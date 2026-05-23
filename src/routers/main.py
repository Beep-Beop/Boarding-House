from fastapi import FastAPI
from src.routers import boarding_houses, rooms, bookings

app = FastAPI(
    title="Boarding House API",
    version="1.0.0"
)

app.include_router(boarding_houses.router)
app.include_router(rooms.router)
app.include_router(bookings.router)


@app.get("/")
def root():
    return {"message": "API is Running"}