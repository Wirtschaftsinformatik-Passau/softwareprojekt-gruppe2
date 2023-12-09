from fastapi import FastAPI
from logging.config import dictConfig
import logging
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, auth, admin
from .database import Base, engine
from app.logger import LogConfig


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], # which origins are allowed
                   allow_credentials=True,
                   allow_methods=["*"], # which http methods are allowed
                   allow_headers=["*"]) # which headers are allowed


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)