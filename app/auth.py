from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.database import get_users_collection, get_admins_collection, get_agents_collection

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token security
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user_type: str = payload.get("type")
    
    if email is None or user_type is None:
        raise credentials_exception
    
    if user_type == "user":
        users_collection = get_users_collection()
        user = await users_collection.find_one({"email": email})
        if user is None:
            raise credentials_exception
        return {"user": user, "type": "user"}
    
    raise credentials_exception

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user_type: str = payload.get("type")
    
    if email is None or user_type != "admin":
        raise credentials_exception
    
    admins_collection = get_admins_collection()
    admin = await admins_collection.find_one({"email": email})
    
    if admin is None:
        raise credentials_exception
    
    return {"admin": admin, "type": "admin"}

async def get_current_agent(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Agent authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user_type: str = payload.get("type")
    
    if email is None or user_type != "agent":
        raise credentials_exception
    
    agents_collection = get_agents_collection()
    agent = await agents_collection.find_one({"email": email})
    
    if agent is None or not agent.get("approved", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent not approved"
        )
    
    return {"agent": agent, "type": "agent"}
