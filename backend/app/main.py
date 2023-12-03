from fastapi import FastAPI
from routers import users, auth, admin, netzbetreiber
from database import Base, engine

app = FastAPI()



@app.get("/")
def hello_world():
    return {"Hello": "World"}


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(netzbetreiber.router)
