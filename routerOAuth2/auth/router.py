from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from .model import Token, User
from .utils import ACCESS_TOKEN_EXPIRE_MINUTES, authenticateUser, quizCompletato, timedelta, createAccessToken, createRefreshToken, utenteCorrenteAttivo, tryRefresh

router = APIRouter()

@router.post("/login", response_model=Token)
async def loginAccessToken(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticateUser(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenziali errate")
    
    access_token = createAccessToken(data={"sub": user.username})
    refresh_token = createRefreshToken(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refreshToken(refresh_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token non valido"
    )
    try:
        payload = tryRefresh(refresh_token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    access_token = createAccessToken(data={"sub": username})
    new_refresh_token = createRefreshToken(data={"sub": username})
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )

@router.get("/users/me/")
async def readUsersMe(
    current_user: Annotated[User, Depends(utenteCorrenteAttivo)],
) -> User:
    return current_user

@router.get("/users/me/quiz")
async def readUsersMe(
    current_user: Annotated[User, Depends(utenteCorrenteAttivo)],
) -> User:
    return current_user.quizsolved

@router.post("/quizCompletato")
async def completatoQuiz( current_user: Annotated[User, Depends(utenteCorrenteAttivo)]):
    quizCompletato(current_user)
    
    
