from fastapi import FastAPI, Depends
from logging.config import dictConfig
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, auth, admin, netzbetreiber, haushalte, solarteure, energieberatende
from app.database import Base, engine
from app.oauth import get_current_user
from app.logger import LogConfig
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],  # which origins are allowed
                   allow_credentials=True,
                   allow_methods=["*"],  # which http methods are allowed
                   allow_headers=["*"])  # which headers are allowed

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def start_scheduler():
    """
    Event-Funktion beim Start der Anwendung.
    Startet den Scheduler und fügt einen Cron-Job hinzu, um die Funktion "check_and_create_rechnung"
    von "netzbetreiber" täglich um Mitternacht auszuführen.
    """
    scheduler.start()

    scheduler.add_job(
        netzbetreiber.check_and_create_rechnung,
        trigger=CronTrigger(day="*", hour=0, minute=0)
    )


@app.on_event("shutdown")
async def shutdown_scheduler():
    """
    Event-Funktion beim Herunterfahren der Anwendung.
    Beendet den Scheduler.
    """
    scheduler.shutdown()


@app.get("/")
def test(user_id: dict = Depends(get_current_user)):
    """
    Eine Test-Route, um sicherzustellen, dass die Anwendung funktioniert.

    Args:
        user_id (dict, optional): Benutzer-ID aus dem OAuth-Token.

    Returns:
        dict: Eine einfache JSON-Antwort.
    """
    return {"message": "Hello World"}


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(netzbetreiber.router)
app.include_router(haushalte.router)
app.include_router(solarteure.router)
app.include_router(energieberatende.router)
