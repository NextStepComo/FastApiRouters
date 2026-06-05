from datetime import date
from pydantic import BaseModel, Field, ConfigDict

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    userID: int = Field(alias="userid")
    username: str
    full_name: str
    quizsolved: bool
    date_birth: date

class UserInDB(User):
    hashed_password: str

class registrazioneUser(BaseModel):
  username: str
  full_name: str
  quizsolved: bool
  date_birth: str
  password: str