from pydantic import BaseModel


class LoginCredentials(BaseModel):
    username: str
    password: str


class AuthenticatedUser(BaseModel):
    user_id: str
    username: str
