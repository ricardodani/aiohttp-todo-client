'''
>>> client = TodoAsyncClient()
>>> add_list_response = await client.add_list("My List")
>>> assert add_list_response.status_code == 200
'''


import aiohttp
from typing import Optional, Any
from pydantic import BaseModel, ValidationError
from todoclient.schemas import UserInput, ItemInput, ListInput


POST = 'post'
GET = 'get'
DELETE = 'delete'
PUT = 'put'


class ClientValidationError(Exception):
    pass



class APIResponse(BaseModel):
    status_code: int
    method: str
    data: BaseModel = None
    error_msg: str = None


class AiohttpJsonClient(BaseModel):

    base_url: str
    auth: Optional[Any] = None

    def get_full_url(self, path: str):
        return self.base_url + path

    async def handler(
        self,
        path: str,
        method: str,
        input_data: Optional[dict] = None,
    ) -> APIResponse:

        async with aiohttp.ClientSession(auth=self.auth) as session:

            session_method = getattr(session, method)
            async with session_method(
                self.get_full_url(path),
                **{'json': input_data} if input_data else {}
            ) as resp:
                data = await resp.json()
                return APIResponse(
                    status_code=resp.status,
                    data=data,
                    method=method
                )


class TodoAsyncClient(AiohttpJsonClient):

    base_url: str = 'http://localhost:8000/api/v1'

    async def register_user(
        self, **user_input
    ):
        try:
            user_input = UserInput(**user_input)
        except ValidationError as e:
            raise ClientValidationError(str(e))
        else:
            return await self.handler(
                '/register', POST, user_input.dict()
            )


class AuthenticatedTodoAsyncClient(TodoAsyncClient):

    user: str
    password: str

    @property
    def auth(self):
        return aiohttp.BasicAuth(self.user, self.password)

    async def read_user(self):
        return await self.handler(
            '/__user__', GET
        )

    async def add_list(
        self, **list_input
    ):
        list_input = ListInput(**list_input)
        return await self.handler(
            f'/list', POST, list_input.dict()
        )

    async def view_list(
        self, list_id: int
    ):
        return await self.handler(
            f'/list/{list_id}', GET
        )

    async def add_item(
        self, list_id: int, **item_input
    ):
        item_input = ItemInput(**item_input)
        return await self.handler(
            f'/list/{list_id}', POST, item_input.dict()
       )

    async def delete_list(
        self, list_id: int
    ):
        return await self.handler(
            f'/list/{list_id}', DELETE
        )

    async def update_item(
        self, list_id: int, item_id: int, **item_input
    ):
        item_input = ItemInput(**item_input)
        return await self.handler(
            f'/list/{list_id}/{item_id}', PUT, item_input.dict()
        )

    async def delete_item(
         self, list_id: int, item_id: int
    ):
        return await self.handler(
            f'/list/{list_id}/{item_id}', DELETE
        )
