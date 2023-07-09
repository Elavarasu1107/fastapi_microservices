from pydantic import BaseModel
from typing import Optional, List


class NoteSchema(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class Collaborator(BaseModel):
    note_id: int
    user_id: Optional[List[int]]

    class Config:
        orm_mode = True
