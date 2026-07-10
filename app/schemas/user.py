from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


class UserRead(BaseUser[int]):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass
