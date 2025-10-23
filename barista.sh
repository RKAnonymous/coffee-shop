#!/bin/bash

# -----------------------------
# barista.sh - manage DB, Celery, Uvicorn & Docker
# -----------------------------
# Usage:
# barista db:makemigrations "message"    -> create Alembic revision
# barista db:migrate                     -> upgrade DB to latest head
# barista celery:worker [force]          -> start Celery worker (optionally force kill existing)
# barista celery:beat [force]            -> start Celery beat (optionally force kill existing)
# barista uvicorn [port]                 -> start Uvicorn app (default port 8000)
# barista shop:up                        -> docker-compose up
# barista shop:down                      -> docker-compose down
# barista shop:build                      -> docker-compose build
# barista shop:rebuild                    -> docker-compose build --no-cache & up -d
# -----------------------------

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

ACTION=$1
MESSAGE=$2

# ----------- ALEMBIC FUNCTIONS -----------
create_makemigrations() {
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    MSG=${MESSAGE:-"auto_update_$TIMESTAMP"}
    echo -e "${GREEN}Creating Alembic migration: $MSG${NC}"
    alembic revision --autogenerate -m "$MSG"
}

run_migrate() {
    echo -e "${GREEN}Upgrading database to latest head...${NC}"
    alembic upgrade head
    echo -e "${GREEN}Database migrated successfully!${NC}"
}

# ----------- CELERY FUNCTIONS -----------
start_celery_worker() {
    FORCE=$1
    if [ "$FORCE" = "force" ]; then
        echo -e "${RED}Force stopping existing Celery workers...${NC}"
        pkill -f "celery.*worker" || true
    fi
    echo -e "${GREEN}Starting Celery worker in background...${NC}"
    celery -A app.tasks.celery_app worker --loglevel=info &
    echo -e "${GREEN}Celery worker started.${NC}"
}

stop_celery_worker() {
    echo -e "${RED}Stopping Celery worker...${NC}"
    pkill -f "celery.*worker" || true
}

start_celery_beat() {
    FORCE=$1
    if [ "$FORCE" = "force" ]; then
        echo -e "${RED}Force stopping existing Celery beat...${NC}"
        pkill -f "celery.*beat" || true
        echo -e "${RED}Removing old celerybeat-schedule files...${NC}"
        rm -f celerybeat-schedule celerybeat-schedule.db
    fi
    echo -e "${GREEN}Starting Celery beat in background...${NC}"
    celery -A app.tasks.celery_app beat --loglevel=info &
    echo -e "${GREEN}Celery beat started.${NC}"
}

stop_celery_beat() {
    echo -e "${RED}Stopping Celery beat...${NC}"
    pkill -f "celery.*beat" || true
    rm -f celerybeat-schedule celerybeat-schedule.db
}

restart_celery_worker() {
    stop_celery_worker
    start_celery_worker "force"
}

restart_celery_beat() {
    stop_celery_beat
    start_celery_beat "force"
}

# ----------- DEV SERVER FUNCTION -----------
start_server() {
    PORT=${MESSAGE:-8000}
    echo -e "${GREEN}Starting Uvicorn on port $PORT...${NC}"
    uvicorn app.main:app --reload --port $PORT &
    echo -e "${GREEN}Uvicorn started.${NC}"
}

# ----------- DOCKER COMPOSE FUNCTIONS -----------
docker_up() {
    echo -e "${GREEN}Bringing up Docker containers...${NC}"
    docker compose up -d
}

docker_down() {
    echo -e "${RED}Stopping Docker containers...${NC}"
    docker compose down
}

docker_build() {
    echo -e "${GREEN}Building Docker images...${NC}"
    docker compose up --build -d
}

docker_rebuild() {
    echo -e "${RED}Force rebuilding Docker images (no cache) and starting containers...${NC}"
    docker compose build --no-cache
    docker compose up -d
}

docker_logs() {
    echo -e "${GREEN}Attaching to Docker logs...${NC}"
    docker compose logs -f
}

# ----------- MAIN SCRIPT -----------
case $ACTION in
    db:makemigrations)
        create_makemigrations
        ;;
    db:migrate)
        run_migrate
        ;;
    celery:worker)
        start_celery_worker $MESSAGE
        ;;
    celery:worker:stop)
        stop_celery_worker
        ;;
    celery:worker:restart)
        restart_celery_worker
        ;;
    celery:beat)
        start_celery_beat $MESSAGE
        ;;
    celery:beat:stop)
        stop_celery_beat
        ;;
    celery:beat:restart)
        restart_celery_beat
        ;;
    app:runserver)
        start_server
        ;;
    compose:up)
        docker_up
        ;;
    compose:down)
        docker_down
        ;;
    compose:build)
        docker_build
        ;;
    compose:rebuild)
        docker_rebuild
        ;;
    compose:logs)
        docker_logs
        ;;
    *)
        echo -e "${RED}Usage:${NC} "
        echo -e "  barista db:makemigrations \"optional message\" -> Create Alembic migration"
        echo -e "  barista db:migrate                           -> Upgrade DB to latest head"
        echo -e "  barista celery:worker [force]                -> Start Celery worker (force restart optional)"
        echo -e "  barista celery:worker:stop                   -> Stop Celery worker"
        echo -e "  barista celery:worker:restart                -> Restart Celery worker"
        echo -e "  barista celery:beat [force]                  -> Start Celery beat (force restart optional)"
        echo -e "  barista celery:beat:stop                     -> Stop Celery beat"
        echo -e "  barista celery:beat:restart                  -> Restart Celery beat"
        echo -e "  barista runserver [port]                     -> Start Uvicorn server (default 8000)"
        echo -e "  barista compose:up                              -> Start docker containers"
        echo -e "  barista compose:down                            -> Stop docker containers"
        echo -e "  barista compose:build                           -> Build docker containers"
        echo -e "  barista compose:rebuild                         -> Rebuild docker containers"
        echo -e "  barista compose:logs                            -> attach to Docker logs"
        exit 1
        ;;
esac
