from pydantic import BaseModel


class UserInput(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str


class ListInput(BaseModel):
    list_name: str


class ItemInput(BaseModel):
    todo_item_name: str
