from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)


class SessionResponse(BaseModel):
    session_id: str
    display_name: str
    token: str
    expires_in_minutes: int
