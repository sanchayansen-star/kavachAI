FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY kavachai/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY kavachai/ ./kavachai/

# Create data directory for SQLite
RUN mkdir -p /data

# Railway sets PORT dynamically via environment variable
ENV PORT=8000

EXPOSE ${PORT}

CMD uvicorn kavachai.backend.main:app --host 0.0.0.0 --port ${PORT}
