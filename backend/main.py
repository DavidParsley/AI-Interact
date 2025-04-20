from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*']
)

from routes import *
app.include_router(user.router)
app.include_router(query.router)

@app.get('/')
def index():
    return {"message": "Welcome to AI Interact"}