from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List
from app.database import SessionLocal, Transaction

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/api/transactions")
async def get_transactions(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    card_scheme: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        Transaction.timestamp,
        func.count(Transaction.id).label("count")
    )

    if card_scheme and card_scheme != "All":
        query = query.filter(Transaction.card_scheme == card_scheme)
    
    if start_time:
        query = query.filter(Transaction.timestamp >= datetime.fromisoformat(start_time))
    if end_time:
        query = query.filter(Transaction.timestamp <= datetime.fromisoformat(end_time))

    # Group by minute for the chart
    # SQLite doesn't have a simple date_trunc, so we'll format the timestamp
    # This is a simplification; for high volume, we might need better aggregation
    results = query.group_by(func.strftime("%Y-%m-%d %H:%M", Transaction.timestamp)).all()
    
    data = []
    for timestamp, count in results:
        data.append({
            "x": timestamp.strftime("%Y-%m-%d %H:%M"),
            "y": count
        })
        
    return data
