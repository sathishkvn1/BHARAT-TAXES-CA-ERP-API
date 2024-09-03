from sqlalchemy.orm import Session
from sqlalchemy import func
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

def generate_book_number(book_type,db:Session  ):
        """
        Generate a book number based on the book type.

        Parameters:
        - book_type (str): The type of the book ('INVOICE', 'WORK_ORDER', 'QUOTATION', 'ENQUIRY')
        - db (Session): The database session.

        Returns:
        - str: The generated book number.
        """
    
        # book_number = db.query(BookNumber.invoice_number).filter(BookNumber.invoice_prefix == 'INV')
        book_number  = db.query(BookNumber).first()
        if not book_number:
            raise HTTPException(status_code=404, detail="Book number not found")
        prefix =''
        number = 0
        if book_type == 'INVOICE':
            book_number.invoice_number += 1
            prefix = book_number.invoice_number_prefix
            number = book_number.invoice_number
        if book_type == 'WORK_ORDER':
            book_number.work_order_number +=1
            prefix = book_number.work_order_number_prefix
            number = book_number.work_order_number
        if book_type == 'QUOTATION':
            book_number.quotation_number +=1
            prefix = book_number.quotation_number_prefix
            number = book_number.quotation_number
        if book_type == 'ENQUIRY':
            book_number.enquiry_number +=1
            prefix = book_number.enquiry_number_prefix
            number = book_number.enquiry_number
        if book_type == 'APPOINTMENT':
            book_number.appointment_number +=1
            prefix = book_number.appointment_number_prefix
            number = book_number.appointment_number
        if book_type == 'TASK':
            book_number.task_number +=1
            prefix = book_number.task_number_prefix
            number = book_number.task_number
        if book_type == 'PAYMENT':
            book_number.payment_voucher_number +=1
            prefix = book_number.payment_voucher_number_prefix
            number = book_number.payment_voucher_number
        if book_type == 'RECEIPT':
            book_number.receipt_voucher_number +=1
            prefix = book_number.receipt_voucher_number_prefix
            number = book_number.receipt_voucher_number
        if book_type == 'CREDIT':
            book_number.credit_note_number +=1
            prefix = book_number.credit_note_number_prefix
            number = book_number.credit_note_number
        if book_type == 'DEBIT':
            book_number.debit_note_number +=1
            prefix = book_number.debit_note_number_prefix
            number = book_number.debit_note_number
        
        if book_type == 'JOURNAL':
            book_number.journal_voucher_number +=1
            prefix = book_number.journal_voucher_number_prefix
            number = book_number.journal_voucher_number

        if book_type == 'CUSTOMER':
            book_number.customer_number +=1
            prefix = book_number.customer_number_prefix
            number = book_number.customer_number
        if book_type == 'FILE':
            book_number.file_number +=1
            prefix = book_number.file_number_prefix
            number = book_number.file_number

        new_book_number  = f'{prefix}{number}'    
        # new_invoice_number = generate_number(book_number.invoice_prefix, book_number.invoice_number)
        # db.commit()
        try:
            db.commit()  # Ensure the incremented number is committed to the database
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An error occurred while generating the book number")
    
        # db.flush()
        return new_book_number

def generate_voucher_id(db:Session):
     
    last_voucher = db.query(AccVoucherId).filter(AccVoucherId.id == 1).first()
    new_voucher_id = last_voucher.voucher_id + 1
    last_voucher.voucher_id = new_voucher_id
    db.add(last_voucher)
    db.flush()

    return new_voucher_id