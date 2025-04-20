import os 
import time
import bcrypt
import jwt
from typing import Dict
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from models import Users, get_db, RevokedToken

load_dotenv()

JWT_SECRET = os.getenv("secret")
JWT_ALGORITHM = os.getenv("algorithm")


def token_response(token: str):
    return {
        "access_token": token
    }

def signJWT(user_id: int) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 2400  #(40 minutes) 
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print("DECODED JWT:", decoded_token)
        if decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            print("Token expired")
            return None
    except Exception as e:
        print("JWT Decode error:", str(e))
        return {}

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            
            # 🔸 Check revoked tokens
            db: Session = next(get_db())
            revoked = db.query(RevokedToken).filter_by(token=credentials.credentials).first()
            if revoked:
                raise HTTPException(status_code=403, detail="Token has been revoked.")

            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decodeJWT(jwtoken)
            return payload is not None
        except:
            return False

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_current_user(
    token: str = Depends(JWTBearer()),
    session: Session = Depends(get_db)
):
    payload = decodeJWT(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = session.query(Users).filter_by(id=payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.refresh(user)
    
    return user
