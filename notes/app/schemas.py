from bson import ObjectId
from pydantic import BaseModel, validator, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


class NoteSchema(BaseModel):
    title: str
    description: str
    reminder: Optional[datetime]

    class Config:
        orm_mode = True


class NoteResponse(BaseModel):
    id: str | ObjectId = Field(default=None, alias="_id")
    title: str
    description: str
    reminder: str | datetime = None
    # collaborators: dict | List[str] = Field(default=[])
    # labels: dict | List[str] = Field(default=[])

    @validator('id')
    def validate_id(cls, value):
        if value == "":
            raise ValueError('field cannot be empty')
        return str(value)

    # @validator('collaborators')
    # def validate_collaborator(cls, value):
    #     if value:
    #         return [i[1].get('username') for i in value.values()]
    #     return value

    # @validator('labels')
    # def validate_label(cls, value):
    #     print(value)
    #     if value:
    #         return [i[1].get('title') for i in value.values()]
    #     return []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Collaborator(BaseModel):
    note_id: str
    user_id: Optional[List[str]]
    grant_access: bool = False

    class Config:
        orm_mode = True


class LabelAssociate(BaseModel):
    note_id: str
    labels: Optional[List[str]]
