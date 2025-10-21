from fastapi import FastAPI
from .routers import auth, users

app = FastAPI(title="Coffee Shop API")

app.include_router(auth.router)
app.include_router(users.router)
