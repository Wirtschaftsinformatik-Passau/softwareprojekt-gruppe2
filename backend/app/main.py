from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, auth
from .database import Base, engine


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], # which origins are allowed
                   allow_credentials=True,
                   allow_methods=["*"], # which http methods are allowed
                   allow_headers=["*"]) # which headers are allowed


@app.get("/")
def hello_world():
    return {"Hello": "World"}

app.include_router(users.router)
app.include_router(auth.router)
