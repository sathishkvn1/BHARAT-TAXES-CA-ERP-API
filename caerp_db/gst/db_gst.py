from fastapi import HTTPException, Path,  UploadFile
from sqlalchemy.orm import Session
from caerp_db.gst.model import *
from typing import Union, List, Optional
from sqlalchemy import and_, func, insert, update , text, or_

def save_gst_test(db: Session, request: gstTest):
    data = request.model_dump()
    
    if request.id == 0: 
        data.pop("id", None)
        sql_stmt = insert(gstTest).values(**data)
        result = db.execute(sql_stmt)
        db.commit()
        return_id = result.lastrowid
    else: 
        sql_stmt = update(gstTest).where(gstTest.id == request.id).values(**data)
        db.execute(sql_stmt)
        db.commit()
        return_id = request.id
            
    return return_id


def save_gstr2b(db: Session, request: gstr2b):
        data = request.model_dump()
        data.pop("p_g_id", None)
        sql_stmt = insert(gstr2b).values(**data)
        result = db.execute(sql_stmt)
        db.commit()
        return_id = result.lastrowid
        return return_id