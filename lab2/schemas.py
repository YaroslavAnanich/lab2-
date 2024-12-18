from pydantic import BaseModel


class UserLoginSchem(BaseModel):
    name: str
    password: str


class UserAddSchem(UserLoginSchem):
    role: str


class UserDbSchem(UserAddSchem):
    id: int


class UserDelSchem(BaseModel):
    id: int


class UserVisitSchem(BaseModel):
    visit: int


class PostAddSchem(BaseModel):
    title: str
    body: str
    addition: str


class PostDbSchem(PostAddSchem):
    id: int


class PostDelSchem(BaseModel):
    id: int