from fastapi import FastAPI
from src.routers import users, auth, search

app = FastAPI(title="Boarding House API")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(search.router)

@app.get("/")
def root():
    return {"message": "API is Running"}