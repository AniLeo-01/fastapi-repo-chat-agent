FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn pydantic-settings neo4j

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
