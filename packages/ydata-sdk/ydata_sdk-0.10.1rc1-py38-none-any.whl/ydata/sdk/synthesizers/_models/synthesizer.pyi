from .status import Status
from pydantic import BaseModel
from typing import Optional

class Synthesizer(BaseModel):
    uid: Optional[str]
    author: Optional[str]
    name: Optional[str]
    status: Optional[Status]
