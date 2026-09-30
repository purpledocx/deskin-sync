from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.exc import  SQLAlchemyError

from app.database import engine


from app.routers import auth_router, booking_router, space_router

"""----------------------APP-SETTINGS----------------------"""
app = FastAPI(
    title="DeskIn SmartDesk API",
    version="0.1.0"
)

app.include_router(booking_router)
app.include_router(auth_router)
app.include_router(space_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""----------------------ROUTES----------------------"""
@app.get("/health")
def health_check():
    return {"status": "ok", "project": "DeskIn SmartDesk"}

@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )