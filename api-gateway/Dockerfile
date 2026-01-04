# Dockerfile for API Gateway
# Entry point for the microservices architecture

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic-settings \
    neo4j \
    fastmcp==2.12.0

# Copy gateway code
COPY . /app

# Expose port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
