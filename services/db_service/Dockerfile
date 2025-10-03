# services/db_service/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt
COPY services/common ./common
RUN pip install -e ./common

COPY services/db_service/src ./src
COPY services/db_service/main.py .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]