"""
    This is the main file of the FastAPI application.
    It creates the FastAPI app instance and includes the API routes. 
    It also configures CORS middleware to allow the frontend to
    interact with the API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
