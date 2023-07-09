from pydantic import BaseModel, EmailStr


class RegisterValidation(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    location: str


class UserResponse(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    location: str


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
