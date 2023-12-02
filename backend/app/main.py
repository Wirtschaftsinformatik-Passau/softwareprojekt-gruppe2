from fastapi import FastAPI
from .routers import users, auth
from .database import Base, engine


app = FastAPI()

@app.get("/")
def hello_world():
    return {"Hello": "World"}

app.include_router(users.router)
app.include_router(auth.router)
