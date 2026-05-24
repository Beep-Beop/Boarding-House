from fastapi import FastAPI
from src.routers import users, photos, social, notifications

app = FastAPI(title="Boarding House API")

app.include_router(users.router)
app.include_router(photos.router)
app.include_router(social.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"message": "API is Running"}