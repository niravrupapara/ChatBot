from datetime import datetime
from pydantic import BaseModel


class Session(BaseModel):
    session_id: str
    title: str
    created_at: datetime
