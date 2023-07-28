from bson import ObjectId
from pydantic import BaseModel, Field, validator
from typing import Optional, List


class LabelSchema(BaseModel):
    title: str
    color: str

    class Config:
        orm_mode = True


class LabelResponse(BaseModel):
    id: str | ObjectId = Field(default=None, alias="_id")
    title: str
    color: str
    user: str | ObjectId

    @validator('id', 'user')
    def validate_id(cls, value):
        if value == "":
            raise ValueError('field cannot be empty')
        return str(value)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class LabelAssociate(BaseModel):
    note_id: int
    labels: Optional[List[int]]
