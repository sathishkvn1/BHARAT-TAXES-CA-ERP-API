from sqlalchemy.orm import Session
from sqlalchemy import func
from caerp_constants.caerp_constants import BookType
from caerp_db.common.models import BookNumber
from caerp_db.accounts.models import AccVoucherId
from fastapi import  HTTPException
from sqlalchemy.exc import SQLAlchemyError

# def generate_book_number(db: Session, column) -> str:
#     # Get the maximum number from the specified column in the table
#     max_number = db.query(func.max(column)).scalar()
#     if max_number is None:
#         # If there are no records yet, start with 100 (assuming EMP001, APP001, etc.)
#         next_number = 1
#     else:
#         next_number = int(max_number) + 1
#     return str(next_number)


def generate_book_number(book_type:BookType,financial_year_id,customer_id,db:Session  ):
        """
        Generate a book number based on the book type.

        Parameters:
        - book_type (BookType): The type of the book (e.g., BookType.INVOICE, BookType.WORK_ORDER)
        - financial_year_id (int): The ID of the financial year.
        - customer_id (int): The ID of the customer.
        - db (Session): The database session.

        Returns:
        - str: The generated book number.
        """
    # Fetch the existing record to get the prefix and current maximum book number
        book_record = db.query(BookNumber).filter(
            BookNumber.financial_year_id == financial_year_id,
            BookNumber.customer_id == customer_id,
            BookNumber.book_type == book_type.value,
            BookNumber.is_active == 'yes'
        ).first()
        
        # Get the prefix from the record, if it exists
        if book_record:
            prefix = book_record.book_prefix
            current_number = book_record.book_number
        else:
            # Handle the case where no record exists (e.g., default prefix)
            prefix = ''  # Or set a default prefix if necessary
            current_number = 0

        # Calculate the new book number
        new_number = current_number + 1
        new_book_number = f'{prefix}{new_number}'

        # Update or insert the record with the new book number
        if book_record:
            book_record.book_number = new_number
        else:
            # Create a new record with the generated book number and existing prefix
            book_record = BookNumber(
                financial_year_id=financial_year_id,
                customer_id=customer_id,
                book_type=book_type,
                book_prefix=prefix,
                book_number=new_number,
                is_active='yes'
            )
            db.add(book_record)

        db.commit()  # Commit the update or insert operation

        return new_book_number


def generate_voucher_id(db:Session):
     
    last_voucher = db.query(AccVoucherId).filter(AccVoucherId.id == 1).first()
    new_voucher_id = last_voucher.voucher_id + 1
    last_voucher.voucher_id = new_voucher_id
    db.add(last_voucher)
    db.flush()

    return new_voucher_id