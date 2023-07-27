from bson import ObjectId
from pydantic import BaseModel, validator, Field, EmailStr
from typing import Optional, List


class NoteSchema(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class NoteResponse(BaseModel):
    id: str | ObjectId = Field(default=None, alias="_id")
    title: str
    description: str
    user: str | ObjectId

    @validator('id', 'user')
    def validate_id(cls, value):
        if value == "":
            raise ValueError('field cannot be empty')
        return str(value)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Collaborator(BaseModel):
    note_id: str
    user_id: Optional[List[str]]
    access: str = 'read_only'

    class Config:
        orm_mode = True
