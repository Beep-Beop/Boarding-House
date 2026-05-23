from fastapi import FastAPI
from src.routers import users

app = FastAPI(title="Boarding House API")

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "API is Running"}