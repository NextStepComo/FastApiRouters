from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .model import Token, User
from .utils import ACCESS_TOKEN_EXPIRE_MINUTES, authenticateUser, timedelta, createAccessToken, utenteCorrenteAttivo

router = APIRouter()

@router.post("/login")
async def loginAccessToken(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticateUser(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o Password incorretti",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = createAccessToken(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/")
async def readUsersMe(
    current_user: Annotated[User, Depends(utenteCorrenteAttivo)],
) -> User:
    return current_user
