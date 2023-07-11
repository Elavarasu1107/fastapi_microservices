from pydantic import BaseModel
from typing import Optional, List


class LabelSchema(BaseModel):
    title: str
    color: str

    class Config:
        orm_mode = True
