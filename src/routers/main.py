from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src import crud, schemas, database, security
from photos import router as photos_router
from social import router as social_router
from notifications import router as notifications_router

app = FastAPI(title="Boarding House Management API", version="1.0")

# Include all routers
app.include_router(photos_router)
app.include_router(social_router)
app.include_router(notifications_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Boarding House API — ready for web integration"}