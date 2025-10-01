FROM python:3.11-slim

# Install system deps (ffmpeg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default envs
ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    FLASK_ENV=production

# Expose the port Render will hit
EXPOSE 8080

# Use gunicorn to run Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "reelit.template.main:app"]

