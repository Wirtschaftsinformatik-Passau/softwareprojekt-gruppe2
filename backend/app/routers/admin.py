from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app import models, schemas, database, oauth
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Union, List

router = APIRouter(prefix="/admin", tags=["Admin"])


async def check_admin_role(current_user: models.Nutzer) -> None:
    if current_user.rolle != models.Rolle.Admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert")


@router.get("/logOverview", status_code=status.HTTP_200_OK, response_model=schemas.AdminDashboardResponse)
async def get_log_overview(current_user: models.Nutzer = Depends(oauth.get_current_user),
                              db: AsyncSession = Depends(database.get_db_async)) \
                              -> Dict[str, Union[Dict[str, int], List[str]]]:
    await check_admin_role(current_user)

    # Log Dateien einsheen
    log_file_path = Path("logs/server_all.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    activity_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                parts = line.split("|")
                timestamp_part = parts[1].strip()
                date_str = timestamp_part.split(" ")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                activity_count[date] += 1
            except (IndexError, ValueError):
                continue

    # User abfragen und zurückgeben
    stmt = select(models.Nutzer)
    result = await db.execute(stmt)
    users_data = result.scalar().all()
    users_list = [user.user_id for user in users_data]

    return {"Log_Daten": dict(activity_count), "users": users_list}


@router.get("/endpointOverview", status_code=status.HTTP_200_OK, response_model=Dict[str, Dict[str, int]])
async def get_endpoint_overview(current_user: models.Nutzer = Depends(oauth.get_current_user))\
                                -> Dict[str, Dict[str, int]]:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=404, detail="Log-Datei nicht gefunden")

    endpoint_activity = defaultdict(Counter)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                date_str = log_entry["timestamp"].split(" ")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                endpoint = log_entry["endpoint"]
                endpoint_activity[date][endpoint] += 1
            except json.JSONDecodeError:
                continue # Ungültige Zeilen werden automatisch übersprungen

    return endpoint_activity


@router.get("/successOverview", status_code=status.HTTP_200_OK, response_model=Dict[str, Dict[str, int]])
async def get_success_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> Dict[str, Dict[str, int]]:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=404, detail="Log-Datei nicht gefunden")

    success_activity = defaultdict(lambda: {'success': 0, 'fail': 0})
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                date_str = log_entry["timestamp"].split(" ")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                success_flag = log_entry["success"]
                if success_flag:
                    success_activity[date]['success'] += 1
                else:
                    success_activity[date]['fail'] += 1
            except json.JSONDecodeError:
                continue # Ungültige Zeilen werden automatisch übersprungen

    return success_activity


@router.get("/registrationOverview", status_code=status.HTTP_200_OK, response_model=Dict[str, int])
async def get_registration_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> Dict[str, int]:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server_all.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    registration_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                parts = line.split("|")
                log_entry = json.loads(parts[2].strip())
                if log_entry.get("msg") == "User registered":
                    date_str = parts[1].strip().split(" ")[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                    registration_count[date] += 1
            except(IndexError, json.JSONDecodeError):
                continue

    return registration_count


@router.get("/loginOverview", status_code=status.HTTP_200_OK, response_model=Dict[str, int])
async def get_login_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> Dict[str, int]:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server_all.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    login_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                parts = line.split("|")
                log_entry = json.loads(parts[2].strip())
                if log_entry.get("msg") == "User logged in":
                    date_str = parts[1].strip().split(" ")[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                    login_count[date] += 1
            except(IndexError, json.JSONDecodeError):
                continue

    return login_count


@router.get("/userOverview", status_code=status.HTTP_200_OK, response_model=Dict[str, int])
async def get_user_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> Dict[str, int]:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server_all.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    role_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                parts = line.split("|")
                log_entry = json.loads(parts[2].strip())
                if log_entry.get("msg") == "User registered":
                    role = log_entry.get("role")
                    role_count[role] += 1
            except(IndexError, json.JSONDecodeError):
                continue

    return role_count
