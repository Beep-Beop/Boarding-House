from fastapi import FastAPI
from src.routers import boarding_house, rooms, bookings

app = FastAPI(title="Boarding House API", version="1.0.0")

app.include_router(boarding_house.router)
app.include_router(rooms.router)
app.include_router(bookings.router)

@app.get("/")
def root():
    return {"message": "API is Running"}