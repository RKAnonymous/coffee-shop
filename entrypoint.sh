#!/usr/bin/env bash
set -e

echo "Waiting for Postgres..."

export PGPASSWORD=${POSTGRES_PASSWORD}

until psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "Postgres is unavailable, sleeping..."
  sleep 2
done

echo "Running migrations..."
alembic upgrade head

# Run the command passed from docker-compose
# Do NOT call entrypoint.sh again here
exec "$@"
