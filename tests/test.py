# tests/test_api_async_pg.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db, Base
from app import models
from app.views import create_access_token


TEST_DATABASE_URL = "YOUR_TEST_DB_URL"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest_asyncio.fixture
async def test_user():
    async with AsyncSessionLocal() as session:
        user = models.User(
            email="test@example.com",
            password="hashedpassword",
            role="user",
            is_verified=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

@pytest_asyncio.fixture
async def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

# -----------------------------
# Tests
# -----------------------------
@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    response = await client.post("/auth/signup", json={"email": "new@example.com", "password": "password123"})
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    response = await client.post("/auth/login", json={"email": test_user.email, "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_verify_user(client: AsyncClient):
    response = await client.post("/auth/verify", json={"email": "dummy@example.com", "code": "dummy"})
    assert response.status_code in (200, 400)

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, auth_headers):
    response = await client.post("/auth/refresh", headers=auth_headers)
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()

@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, auth_headers):
    response = await client.get("/users/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, auth_headers, test_user):
    response = await client.get(f"/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == test_user.id

@pytest.mark.asyncio
async def test_patch_user(client: AsyncClient, auth_headers, test_user):
    response = await client.patch(f"/users/{test_user.id}", headers=auth_headers, json={"first_name": "John"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "John"

@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, auth_headers, test_user):
    response = await client.delete(f"/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_set_user_role(client: AsyncClient, auth_headers, test_user):
    response = await client.patch(f"/users/{test_user.id}/role", headers=auth_headers, json={"role": "admin"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
