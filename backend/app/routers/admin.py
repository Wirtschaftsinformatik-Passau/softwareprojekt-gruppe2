from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime
from app import models, schemas, database, oauth
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Union, List, Any

router = APIRouter(prefix="/admin", tags=["Admin"])


async def check_admin_role(current_user: models.Nutzer) -> None:
    if current_user.rolle != models.Rolle.Admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nur Admins haben Zugriff auf diese Daten")


@router.get("/logOverview", status_code=status.HTTP_200_OK,
            response_model=List[schemas.ChartData])
async def get_log_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> Dict[str, List[Dict[str, Union[str, int]]]]:
    await check_admin_role(current_user)

    log_file_path = Path("logs/server.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    activity_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                date_str = log_entry["timestamp"].split(" ")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                activity_count[date] += 1
            except (IndexError, ValueError):
                continue

    formatted_data = [{"x": date, "y": count} for date, count in activity_count.items()]
    return formatted_data


@router.get("/endpointOverview", status_code=status.HTTP_200_OK, response_model=List[Dict[str, Any]])
async def get_endpoint_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> List[Dict[str, Any]]:
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
                endpoint_activity[endpoint][date] += 1
            except json.JSONDecodeError:
                continue  # Ungültige Zeilen werden automatisch übersprungen

    formatted_data = [{"id": endpoint, "data":
        [{"x": date, "y": count} for date, count in dates.items()]} for endpoint, dates in endpoint_activity.items()]
    return formatted_data


@router.get("/successOverview", status_code=status.HTTP_200_OK,
            response_model=Dict[str, List[Dict[str, Union[str, int]]]])
async def get_success_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> Dict[str, List[Dict[str, Union[str, int]]]]:
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
                continue  # Ungültige Zeilen werden automatisch übersprungen

    success_data = [{"x": date, "y": data['success']} for date, data in success_activity.items()]
    fail_data = [{"x": date, "y": data['fail']} for date, data in success_activity.items()]

    return {"success": success_data, "fail": fail_data}


@router.get("/registrationOverview", status_code=status.HTTP_200_OK, response_model=List[schemas.ChartData])
async def get_registration_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> List[schemas.ChartData]:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    registration_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                if log_entry.get("message") == "User registriert":
                    date_str = log_entry["timestamp"].split(" ")[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")

                    registration_count[date] += 1
            except(IndexError, json.JSONDecodeError):
                continue

    formatted_data = [{"x": date, "y": count} for date, count in registration_count.items()]
    return formatted_data


@router.get("/loginOverview", status_code=status.HTTP_200_OK,
            response_model=List[schemas.ChartData])
async def get_login_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> List[schemas.ChartData]:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    login_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                if log_entry.get("message") == "User eingeloggt":
                    date_str = log_entry["timestamp"].split(" ")[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                    login_count[date] += 1
            except(IndexError, json.JSONDecodeError):
                continue

    formatted_data = [{"x": date, "y": count} for date, count in login_count.items()]
    return formatted_data


@router.get("/userOverview", status_code=status.HTTP_200_OK, response_model=List[schemas.ChartData])
async def get_user_overview(current_user: models.Nutzer = Depends(oauth.get_current_user),
                            db: AsyncSession = Depends(database.get_db_async)) -> List[schemas.ChartData]:
    await check_admin_role(current_user)
    result = await db.execute(
        select(models.Nutzer.rolle, func.count(models.Nutzer.user_id))
        .group_by(models.Nutzer.rolle)
    )
    role_counts = result.all()

    chart_data = [
        schemas.ChartData(x=rolle.name, y=count) for rolle, count in role_counts
    ]

    return chart_data


@router.get("/logs", status_code=status.HTTP_200_OK, response_model=schemas.LogData)
async def get_logs(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> schemas.LogData:
    await check_admin_role(current_user)
    log_file_path = Path("logs/server.log")

    if not log_file_path.exists() or log_file_path.stat().st_size == 0:
        return schemas.LogData(logs=[])

    logs = []
    with open(log_file_path, 'r') as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                logs.append(log_entry)
            except json.JSONDecodeError:
                continue

    return schemas.LogData(logs=logs)

    # User abfragen und zurückgeben
    # stmt = select(models.Nutzer)
    # result = await db.execute(stmt)
    #  users_data = result.scalar().all()
    # users_list = [user.user_id for user in users_data]
