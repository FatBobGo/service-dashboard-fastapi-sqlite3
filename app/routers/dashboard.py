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
    """
    Dependency to get a database session.
    Yields a SQLAlchemy session and closes it after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def dashboard(request: Request):
    """
    Renders the main dashboard HTML template.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/api/transactions")
async def get_transactions(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    card_scheme: Optional[str] = None,
    reject_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetches transaction data for the time series chart.
    
    Args:
        start_time: Filter by start timestamp (ISO format).
        end_time: Filter by end timestamp (ISO format).
        card_scheme: Filter by card scheme (e.g., 'Visa', 'MasterCard').
        reject_code: Filter by reject code (e.g., '0000').
        db: Database session.
        
    Returns:
        List of dictionaries containing 'x' (timestamp) and 'y' (count) for the chart.
    """
    query = db.query(
        Transaction.timestamp,
        func.count(Transaction.id).label("count")
    )

    if card_scheme and card_scheme != "All":
        query = query.filter(Transaction.card_scheme == card_scheme)
    
    if reject_code and reject_code != "All":
        query = query.filter(Transaction.reject_code == reject_code)
    
    if start_time:
        query = query.filter(Transaction.timestamp >= datetime.fromisoformat(start_time))
    if end_time:
        query = query.filter(Transaction.timestamp <= datetime.fromisoformat(end_time))

    # Group by minute for the chart
    results = query.group_by(func.strftime("%Y-%m-%d %H:%M", Transaction.timestamp)).all()
    
    data = []
    for timestamp, count in results:
        data.append({
            "x": timestamp.strftime("%Y-%m-%d %H:%M"),
            "y": count
        })
        
    return data

@router.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Fetches high-level statistics for the dashboard cards.
    
    Returns:
        Dictionary containing total and approved counts for Visa and MasterCard.
    """
    # Total transactions per scheme
    total_visa = db.query(func.count(Transaction.id)).filter(Transaction.card_scheme == "Visa").scalar()
    total_mastercard = db.query(func.count(Transaction.id)).filter(Transaction.card_scheme == "MasterCard").scalar()
    
    # Approved transactions (reject_code = '0000')
    approved_visa = db.query(func.count(Transaction.id)).filter(
        Transaction.card_scheme == "Visa", 
        Transaction.reject_code == "0000"
    ).scalar()
    approved_mastercard = db.query(func.count(Transaction.id)).filter(
        Transaction.card_scheme == "MasterCard", 
        Transaction.reject_code == "0000"
    ).scalar()
    
    return {
        "visa": {
            "total": total_visa or 0,
            "approved": approved_visa or 0
        },
        "mastercard": {
            "total": total_mastercard or 0,
            "approved": approved_mastercard or 0
        }
    }

@router.get("/api/reject_codes")
async def get_reject_codes(db: Session = Depends(get_db)):
    """
    Fetches distinct reject codes and their descriptions for the filter dropdown.
    
    Returns:
        List of dictionaries containing 'code' and 'description'.
    """
    codes = db.query(Transaction.reject_code, Transaction.reject_description).distinct().all()
    return [{"code": code, "description": desc} for code, desc in codes]
