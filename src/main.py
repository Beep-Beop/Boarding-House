from fastapi import FastAPI
from .boarding_house import router as boarding_house_router
from .rooms import router as rooms_router
from .bookings import router as bookings_router

app = FastAPI(title="Boarding House API", version="1.0.0")

app.include_router(boarding_house_router)
app.include_router(rooms_router)
app.include_router(bookings_router)

@app.get("/")
def root():
    return {"message": "API is Running"}