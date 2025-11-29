import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal, Transaction

scheduler = BackgroundScheduler()

def generate_random_transaction():
    schemes = ["Visa", "MasterCard"]
    reject_codes = [
        ("0000", "approved"),
        ("0001", "invalid card status"),
        ("0002", "invalid card expiry date"),
        ("0004", "invalid CVV2"),
    ]
    
    scheme = random.choice(schemes)
    code, desc = random.choice(reject_codes)
    now = datetime.now()
    
    return Transaction(
        card_scheme=scheme,
        transaction_date=now.strftime("%Y%m%d"),
        transaction_time=now.strftime("%H%M%S"),
        reject_code=code,
        reject_description=desc,
        timestamp=now
    )

def ingest_data():
    session = SessionLocal()
    try:
        # Simulate receiving 1-5 transactions
        for _ in range(random.randint(1, 5)):
            txn = generate_random_transaction()
            session.add(txn)
        session.commit()
        print(f"Ingested data at {datetime.now()}")
    except Exception as e:
        print(f"Error ingesting data: {e}")
    finally:
        session.close()

def start_scheduler():
    scheduler.add_job(ingest_data, 'interval', seconds=10)
    scheduler.start()
