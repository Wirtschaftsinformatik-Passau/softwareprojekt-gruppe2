FROM python:3.10

COPY app ./app
COPY logs ./logs
COPY alembic.ini .
COPY vars/.env.prod ./vars/.env
COPY reqs.txt .

RUN pip install --no-cache-dir -r reqs.txt

RUN alembic upgrade head

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

