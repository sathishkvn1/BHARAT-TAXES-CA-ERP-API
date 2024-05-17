# api_library.py

from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union


class DynamicAPI:
    def __init__(self, table_model):
        self.table_model = table_model

    def get_records(self, db: Session, fields: List[str]) -> List[dict]:
        try:
            print("Table Name:", self.table_model.__tablename__)
            print("Fields:", fields)  # Print the provided fields
            # Construct column objects based on the provided field names
            columns = [getattr(self.table_model, field) for field in fields]
            print("Columns:", columns)  # Print the constructed columns
            # Use the constructed columns in the query
            # records = db.query(*columns).all()
            records = db.query(*columns).filter(self.table_model.is_deleted == 'no').all()
            print("Records:", records)  # Print the retrieved records
            # Convert query results to dictionaries
            return [dict(zip(fields, record)) for record in records]
        except Exception as e:
            print("Error:", e)  # Print the exception message
            raise HTTPException(status_code=500, detail=str(e))
        


    def get_record_by_id(self, db: Session, record_id: int, fields: List[str]) -> dict:
        try:
            # Construct column objects based on the provided field names
            columns = [getattr(self.table_model, field) for field in fields]
            # Query the database to get the record filtered by id and select specific fields
            record = db.query(*columns).filter(self.table_model.id == record_id).first()
            if record:
                return dict(zip(fields, record))
            else:
                raise HTTPException(status_code=404, detail="Record not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    
    # def delete_record_by_id(self, db: Session, record_id: int) -> None:
    #     try:
    #         # Find the record by ID
    #         record = db.query(self.table_model).filter(self.table_model.id == record_id).first()
    #         if record:
    #             # Perform soft delete by updating is_deleted to 'yes'
    #             record.is_deleted = 'yes'
    #             db.commit()
    #         else:
    #             raise HTTPException(status_code=404, detail="Record not found")
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

    # def undelete_record_by_id(self, db: Session, record_id: int) -> None:
    #     try:
    #         # Find the record by ID
    #         record = db.query(self.table_model).filter(self.table_model.id == record_id).first()
    #         if record:
    #             # Perform undelete by updating is_deleted to 'no'
    #             record.is_deleted = 'no'
    #             db.commit()
    #         else:
    #             raise HTTPException(status_code=404, detail="Record not found")
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))
        
        


    def delete_records_by_ids(self, db: Session, record_ids: List[int]) -> None:
        try:
            # Find the records by IDs
            records = db.query(self.table_model).filter(self.table_model.id.in_(record_ids)).all()
            if not records:
                raise HTTPException(status_code=404, detail="Records not found")
            for record in records:
                # Perform soft delete by updating is_deleted to 'yes'
                record.is_deleted = 'yes'
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def undelete_records_by_ids(self, db: Session, record_ids: List[int]) -> None:
        try:
            # Find the records by IDs
            records = db.query(self.table_model).filter(self.table_model.id.in_(record_ids)).all()
            if not records:
                raise HTTPException(status_code=404, detail="Records not found")
            for record in records:
                # Perform undelete by updating is_deleted to 'no'
                record.is_deleted = 'no'
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))





    def save_record(self, db: Session, data: dict) -> None:
            """
            Save a record to the database.
            """
            try:
                # Create an instance of the table model with the provided data
                record = self.table_model(**data)
                # Add the record to the session and commit changes
                db.add(record)
                db.commit()
            except Exception as e:
                # Rollback changes if an error occurs
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
    
    