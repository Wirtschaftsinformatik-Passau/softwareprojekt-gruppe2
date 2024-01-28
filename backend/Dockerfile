FROM python:3.10 
COPY app ./app 
COPY logs ./logs 
COPY alembic.ini . 
COPY tose_backend ./tose_backend 
COPY vars/.env ./vars/.env
COPY reqs.txt . 
RUN pip install --no-cache-dir -r reqs.txt
COPY alembic_entrypoint.sh .
RUN chmod 777 alembic_entrypoint.sh

EXPOSE 8000 

ENTRYPOINT ["./alembic_entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

