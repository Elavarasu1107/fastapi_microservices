from pydantic import BaseModel
from typing import Optional, List


class APIResponse(BaseModel):
    message: str
    status: int
    data: dict | Optional[List[dict]]
