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


class APISuccessResponse(APIResponse):
    data: Optional[Any] = None


class APIErrorResponse(APIResponse):
    error_msg: str = None


class AiohttpJsonClient(BaseModel):

    base_url: str

    def validate_input(self, input_data: dict, model: BaseModel):
        try:
            input_model = model(**input_data)
        except ValidationError as e:
            raise ClientValidationError(str(e))
        else:
            return input_model

    def get_auth(self):
        pass

    def get_full_url(self, path: str):
        return self.base_url + path

    async def handler(
        self,
        path: str,
        method: str,
        input_data: Optional[dict] = None,
    ) -> APIResponse:

        async with aiohttp.ClientSession(auth=self.get_auth()) as session:

            session_method = getattr(session, method)
            async with session_method(
                self.get_full_url(path),
                **{'json': input_data} if input_data else {}
            ) as resp:
                data = await resp.json()
                if 200 <= resp.status < 300:
                    return APISuccessResponse(
                        status_code=resp.status,
                        data=data,
                        method=method
                    )
                else:
                    return APIErrorResponse(
                        status_code=resp.status,
                        error_msg=data['detail'],
                        method=method
                    )



class TodoAsyncClient(AiohttpJsonClient):

    base_url: str = 'http://localhost:8000/api/v1'

    async def register_user(
        self, **user_input
    ):
        user_model = self.validate_input(user_input, UserInput)
        return await self.handler(
            '/register', POST, user_model.dict()
        )


class AuthTodoAsyncClient(TodoAsyncClient):

    user: str
    password: str

    def get_auth(self):
        return aiohttp.BasicAuth(self.user, self.password)

    async def read_user(self):
        return await self.handler(
            '/__user__', GET
        )

    async def add_list(
        self, **list_input
    ):
        list_model = self.validate_input(list_input, ListInput)
        return await self.handler(
            f'/list', POST, list_model.dict()
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
        item_model = self.validate_input(item_input, ItemInput)
        return await self.handler(
            f'/list/{list_id}', POST, item_model.dict()
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
        item_model = self.validate_input(item_input, ItemInput)
        return await self.handler(
            f'/list/{list_id}/{item_id}', PUT, item_model.dict()
        )

    async def delete_item(
         self, list_id: int, item_id: int
    ):
        return await self.handler(
            f'/list/{list_id}/{item_id}', DELETE
        )
