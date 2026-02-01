FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env .env

# Create cron job for daily sync
RUN apt-get update && apt-get install -y cron && \
    echo "0 0 * * * cd /app && python src/sync_stars.py >> /var/log/cron.log 2>&1" | crontab - && \
    touch /var/log/cron.log

# Run cron in foreground
CMD cron && tail -f /var/log/cron.log
