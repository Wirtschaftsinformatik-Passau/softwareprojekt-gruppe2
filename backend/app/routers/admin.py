from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app import models, schemas, database, config, oauth
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Union, List

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", status_code=status.HTTP_200_OK, response_model=schemas.AdminDashboardResponse)
async def get_admin_dashboard(current_user: models.Nutzer = Depends(oauth.get_current_user),
                              db: AsyncSession = Depends(database.get_db_async)) \
                              -> Dict[str, Union[Dict[str, int], List[str]]]:
    if current_user.rolle != models.Rolle.Admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert")

    # Log Dateien einsheen
    log_file_path = Path("logs/server.log")
    if not log_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log-Datei nicht gefunden")

    activity_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            log_entry = json.loads(line)
            date_str = log_entry["timestamp"].split("T")[0]
            date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
            activity_count[date] += 1

    # User abfragen und zurückgeben
    stmt = select(models.Nutzer)
    result = await db.execute(stmt)
    users_data = result.scalar().all()
    users_list = [user.user_id for user in users_data]

    return {"Log_Daten": dict(activity_count), "users": users_list}
