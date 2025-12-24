from pydantic import BaseModel
from typing import Literal

class Message(BaseModel):
    role: Literal["human", "ai"]
    content: str