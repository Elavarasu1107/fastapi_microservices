from pydantic import BaseModel, EmailStr, Field, validator
from bson.objectid import ObjectId
from .password import set_password
from settings import settings


class RegisterValidation(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    location: str
    is_superuser: str | bool = Field(default="string", alias='superuser_key')

    @validator('password')
    def validate_id(cls, value):
        if value == "":
            raise ValueError('Password cannot be empty')
        return set_password(value)

    @validator('is_superuser')
    def validate_user(cls, value):
        if value == settings.admin_key:
            return True
        if value == '':
            return False
        raise ValueError('Invalid superuser key')


class UserResponse(BaseModel):
    id: str = Field(default=None, alias="_id")
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    location: str
    is_verified: bool = False
    superuser_key: str | bool = Field(default="string", alias='is_superuser')

    @validator('id')
    def validate_id(cls, value):
        if value == "":
            raise ValueError('id cannot be empty')
        return str(value)

    @validator('superuser_key')
    def validate_superuser(cls, value):
        if value == "True":
            return True
        return False

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
