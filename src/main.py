from fastapi import FastAPI
from sqlalchemy import text
from src.routers import users, photos, social, notifications, auth, search, boarding_house, rooms, bookings, payments, reports, location
from src.database import engine, SessionLocal
from src import crud, state

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
app.include_router(payments.router)
app.include_router(reports.router)
app.include_router(location.router)

@app.on_event("startup")
def startup():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    db = SessionLocal()
    try:
        location_crud = crud.LocationsCRUD(db)
        state.province_cache.extend(location_crud.get_distinct_provinces())
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API is Running"}