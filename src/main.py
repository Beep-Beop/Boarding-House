from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from src.routers import users, photos, social, notifications, auth, search, boarding_house, rooms, bookings, payments, reports, location, amenities, favorites, booking_history, maintenance, viewings, admin_logs
from src.database import engine, SessionLocal
from src import crud
from src.cache import CacheService
from src.dependencies import limiter
from src.logger import logger

app = FastAPI(title="Boarding House API")

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

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
app.include_router(amenities.router)
app.include_router(favorites.router)
app.include_router(booking_history.router)
app.include_router(maintenance.router)
app.include_router(viewings.router)
app.include_router(admin_logs.router)

@app.on_event("startup")
def startup():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning("Database connection failed at startup: %s", e)
    
    app.state.cache = CacheService()

    db = SessionLocal()
    try:
        location_crud = crud.LocationsCRUD(db)
        app.state.cache.set_provinces(location_crud.get_distinct_provinces())
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API is Running"}