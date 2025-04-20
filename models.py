from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, VARCHAR
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy import create_engine

from sqlalchemy.sql import func
from sqlalchemy import DateTime

# connect to  database
engine = create_engine('sqlite:///app.db', echo=True)

# create a session
Session = sessionmaker(bind=engine)

# create an instance of the session
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

# base class for models
Base = declarative_base()


# Users Table
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    create_at = Column(DateTime(), default=datetime.now())

    active_conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=True)


    queries = relationship('Queries', backref='users', cascade='all, delete-orphan')


# Queries Table
class Queries(Base):
    __tablename__ = 'queries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    create_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now(), onupdate=datetime.now())


# Conversations Table
class Conversations(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    queries = relationship('Queries', backref='conversation', cascade='all, delete-orphan')


# Revoked Token Table
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)
