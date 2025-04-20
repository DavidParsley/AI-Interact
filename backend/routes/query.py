import os
import re
import requests
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List

from models import get_db, Users, Queries, Conversations
from schemas import CreateQuerySchema, ConversationOutSchema
from auth import get_current_user
from config import FRONTEND_URL

load_dotenv()

router = APIRouter(
    prefix="/query",
    tags=["LLM"]
)

# Environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL")
SITE_URL = FRONTEND_URL
SITE_NAME = "AI Interact"


def clean_response_text(text: str) -> str:
    return re.sub(r"\\boxed\{([^}]*)\}", r"\1", text).strip()


@router.post("/")
def ask_query(
    data: CreateQuerySchema,
    session: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    try:
        conversation_id = data.conversation_id or current_user.active_conversation_id

        if not conversation_id:
            new_convo = Conversations(
                user_id=current_user.id,
                title="New Conversation"
            )
            session.add(new_convo)
            session.commit()
            session.refresh(new_convo)
            conversation_id = new_convo.id

            current_user.active_conversation_id = conversation_id
            session.commit()

        history = session.query(Queries).filter_by(
            user_id=current_user.id,
            conversation_id=conversation_id
        ).order_by(Queries.create_at.asc()).all()

        messages = []
        for q in history:
            messages.append({"role": "user", "content": q.query_text})
            messages.append({"role": "assistant", "content": q.response_text})
        messages.append({"role": "user", "content": data.query_text})

        response = requests.post(
            url=OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": SITE_URL,
                "X-Title": SITE_NAME
            },
            json={
                "model": "deepseek/deepseek-r1-zero:free",
                "messages": messages
            }
        )
        response.raise_for_status()
        raw_response = response.json()["choices"][0]["message"]["content"]
        cleaned_response = clean_response_text(raw_response)

        new_query = Queries(
            user_id=current_user.id,
            conversation_id=conversation_id,
            query_text=data.query_text,
            response_text=cleaned_response
        )
        session.add(new_query)
        session.commit()
        session.refresh(new_query)

        return {
            "query": data.query_text,
            "response": cleaned_response,
            "conversation_id": conversation_id
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    

# Reset conversation (start fresh, reset active_conversation_id)
@router.post("/reset")
def reset_conversation(
    session: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    try:
        new_convo = Conversations(
            user_id=current_user.id,
            title="New Conversation"
        )
        session.add(new_convo)
        session.commit()
        session.refresh(new_convo)

        current_user.active_conversation_id = new_convo.id
        session.commit()

        return {
            "message": "Started a new conversation.",
            "conversation_id": new_convo.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset conversation: {str(e)}")
    

@router.get("/history")
def get_full_history(
    session: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    conversations = (
        session.query(Conversations)
        .filter_by(user_id=current_user.id)
        .order_by(Conversations.updated_at.desc()) 
        .all()
    )

    full_history = []

    for convo in conversations:
        queries = (
            session.query(Queries)
            .filter_by(user_id=current_user.id, conversation_id=convo.id)
            .order_by(Queries.updated_at.desc())  
            .all()
        )

        full_history.append({
            "conversation_id": convo.id,
            "title": convo.title,
            "created_at": convo.created_at,
            "updated_at": convo.updated_at,  
            "queries": [
                {
                    "question": q.query_text,
                    "response": q.response_text,
                    "updated_at": q.updated_at 
                } for q in queries
            ]
        })

    return full_history


# Route to delete a conversation and all associated queries
@router.delete("/conversation/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    session: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    try:
        conversation = session.query(Conversations).filter_by(id=conversation_id, user_id=current_user.id).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

       
        session.delete(conversation)
        session.commit()

        if current_user.active_conversation_id == conversation_id:
            current_user.active_conversation_id = None  # Reset the active conversation
            session.commit()

        return {"message": "Conversation and all related queries deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")