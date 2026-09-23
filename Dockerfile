FROM python:3.12-slim

WORKDIR /app

# Copy dependency definition and install
COPY v2/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application packages
COPY v2 /app/v2

# Configuration
ENV PYTHONPATH=/app
ENV DEMO_MODE=true
ENV PROJECT_ID=qwiklabs-gcp-04-7459370ad109
ENV GOOGLE_GENAI_USE_VERTEXAI=true
ENV GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-04-7459370ad109
ENV GOOGLE_CLOUD_LOCATION=us-east1

EXPOSE 8080

CMD ["sh", "-c", "python3 -m uvicorn v2.backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
