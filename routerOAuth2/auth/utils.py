from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
import psycopg2
from psycopg2.extras import RealDictCursor

from routerOAuth2.auth.model import Token, TokenData, User, UserInDB

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

connection = psycopg2.connect(
    database="nextStepDB",
    user="postgres",
    password="password",
    host="localhost",
    port=5432
)

def getUserFromDB(username: str) -> UserInDB | None:
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    SQLquery = "SELECT * FROM usersDB WHERE username = %s;"
    cursor.execute(SQLquery, (username,))
    user_row = cursor.fetchone()
    cursor.close()
    
    if user_row:
        return UserInDB(**user_row)
    return None

def verifyPassword(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def authenticateUser(username: str, password: str) -> UserInDB | None:
    user = getUserFromDB(username)
    if user is None:
        return None
    if not verifyPassword(password, user.hashed_password):
        return None
    return user

def createAccessToken(data: dict, expires_delta: timedelta | None = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def utenteCorrente(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossibile validare le credenziali",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
        
    user = getUserFromDB(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def utenteCorrenteAttivo(current_user: Annotated[User, Depends(utenteCorrente)]) -> User:
    return current_user

def createRefreshToken(data: dict):
    return createAccessToken(
        data, 
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

def tryRefresh(refresh_token : str):
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

def quizCompletato(current_user: User):
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    SQLquery = "UPDATE usersDB SET quizsolved = true WHERE username = %s;"
    cursor.execute(SQLquery, (current_user.username,))
    connection.commit()
    cursor.close()