from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str
    username: str
