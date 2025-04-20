from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User Section
class CreateUserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johndoe@example.com",
                "password": "1234"
            }
        }

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "password": "1234"
            }
        }

class UpdateUserSchema(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "password": "newpassword"
            }
        }

# Query Section
class CreateQuerySchema(BaseModel):
    query_text: str
    conversation_id: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "query_text": "What is the weather like today?",
                "conversation_id": 1
            }
        }

class UpdateQuerySchema(BaseModel):
    query_text: Optional[str]
    response_text: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "query_text": "What's the capital of France?",
                "response_text": "The capital of France is Paris."
            }
        }


class CreateConversationSchema(BaseModel):
    title: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Chat about AI"
            }
        }

class ConversationOutSchema(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True