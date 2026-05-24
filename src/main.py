from fastapi import FastAPI
from src.routers import users, photos, social, notifications, auth, search, boarding_house, rooms, bookings

app = FastAPI(title="Boarding House API")

app.include_router(users.router)
app.include_router(boarding_house.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(photos.router)
app.include_router(social.router)
app.include_router(notifications.router)
app.include_router(auth.router)
app.include_router(search.router)

@app.get("/")
def root():
    return {"message": "API is Running"}