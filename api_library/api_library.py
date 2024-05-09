# api_library.py

from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Union


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
            records = db.query(*columns).all()
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

