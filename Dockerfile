# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set workdir
WORKDIR /app

# Install dependencies + PostgreSQL client
RUN apt update && apt install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
# Expose the port for FastAPI
EXPOSE 8000

# Default command (can override in docker-compose)
ENTRYPOINT ["sh", "./entrypoint.sh"]
