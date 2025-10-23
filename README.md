## Coffee Shop – User Management API

A production-ready FastAPI project implementing full user management, including registration, authentication, email verification, and scheduled cleanup of unverified users using Celery and Redis.
 

### Features

    Features                                       Description
    
    User Registration                   Email, password, optional name/surname, unique email validation.
    
    Authentication (JWT)                Access + Refresh tokens for secure authentication. 
    
    Email Verification                  Users receive verification links via email.
    
    Automatic Cleanup                   Unverified users deleted automatically after a threshold (configurable in .env).
    
    Role Management                     Roles: `user` (default) and `admin` with restricted endpoints.
    
    Permissions                         Dependencies enforce authentication, verification, and admin-only access.
    
    Timezone-aware                      Unified timezone set to **Asia/Tashkent**.
    
    Celery Beat Scheduling              Periodic task for deleting unverified users.
    
    Async Email Sending                 Uses `aiosmtplib` for async SMTP-based mail delivery.


### Tech Stack

    FastAPI               —            high-performance web framework
    SQLAlchemy (Async)    —            ORM for PostgreSQL (or any SQL database)
    Pydantic v2           —            settings & data validation
    JWT (python-jose)     —            authentication tokens
    Celery + Redis        —            background tasks & scheduling
    aiosmtplib            —            async email delivery    
    dotenv                —            environment configuration

### Project Structure
```terminaloutput
app/
├── config.py                  # App configuration & environment settings
├── db.py                      # Async SQLAlchemy DB setup
├── models.py                  # SQLAlchemy models
├── permissions.py             # Auth/role/verification dependencies
├── routers/
│   ├── auth.py                # Auth endpoints (signup, login, refresh, verify)
│   └── users.py               # User management endpoints
├── schemas.py                 # Pydantic models for requests/responses
├── tasks/
│   ├── celery_app.py          # Celery + Beat configuration
│   └── user_tasks.py          # Async email sending & cleanup tasks
├── utils/
│   └── send_email.py          # Async email sending utility
├── views.py                   # Business logic for user operations
└── main.py                    # FastAPI app entry point
```


### Environment Variables
```dotenv
# Postgres
POSTGRES_USER=coffee
POSTGRES_PASSWORD=coffee
POSTGRES_DB=coffee_db
POSTGRES_HOST=postgres

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# App
DATABASE_URL=postgresql+asyncpg://coffee:coffee@postgres:5432/coffee_db
JWT_SECRET_KEY=supersecretkey
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
SMTP_FROM=no-reply@example.com
UNVERIFIED_USER_LIFETIME_MINUTES=2880
TIMEZONE=Asia/Tashkent

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```


### Setup Instructions

#### 1. Clone repo and install dependencies

```bash
git clone https://github.com/yourusername/coffee_shop.git
cd coffee_shop
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Give permission to custom script
```bash
chmod +x barista.sh
```

#### Method 1: Direct installation in the host

#### 3. Run Database migrations
```bash
./barista.sh db:migrate
```

#### 4. Start/Install Redis(for Celery usage)
```bash
sudo service redis-server start
```

#### 5. Start Celery and Celery beat
```bash
./barista.sh celery:worker
./barista.sh celery:beat
```

#### 6. Start app
```bash
./barista.sh app:runserver
```

#### Method 2: Up and run container
#### 7. Run containerized app
```bash
./barista.sh shop:build
```

### Learn more about `barista.sh`
```bash
./barista.sh -h
```

##### Use the script more user-friendly format
```bash
sudo cp barista.sh /usr/local/bin/barista
or
sudo ln -s /full/path/to/barista.sh /usr/local/bin/barista
```

### Possible enhancements

#### Roles and Permissions
Separate Role and Permission tables to have more flexible and robust RBAC system.

```docstring
TABLES
    Role: id, name, permission_id
    Permission: id, name, code
RELATION: 
    Permission -> Role -> User
WHAT IS BETTER:
    Separated Role, Permission tables easy to control
    Flexible access control based on Role
    Easy to manipulate with Permissions
```

### NOT COVERED WITH TEST. TESTS ARE NOT WORKING AS INTENDED!