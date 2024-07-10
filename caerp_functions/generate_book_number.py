from sqlalchemy.orm import Session
from sqlalchemy import func

def generate_book_number(db: Session, column) -> str:
    # Get the maximum number from the specified column in the table
    max_number = db.query(func.max(column)).scalar()
    if max_number is None:
        # If there are no records yet, start with 100 (assuming EMP001, APP001, etc.)
        next_number = 1
    else:
        next_number = int(max_number) + 1
    return str(next_number)
