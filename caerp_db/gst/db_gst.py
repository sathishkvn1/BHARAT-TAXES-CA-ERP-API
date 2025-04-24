from fastapi import HTTPException, Path,  UploadFile
from sqlalchemy.orm import Session
from caerp_db.gst.model import *
from typing import Union, List, Optional
from sqlalchemy import and_, func, insert, update , text, or_, delete

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

def delete_gstr2b(db: Session, request: dict):
    sql_stmt = delete(gstr2b).where(gstr2b.tax_period == request['tax_period'])
    db.execute(sql_stmt)
    db.commit()
    return

def save_gstr2a(db: Session, request: gstr2a):
        data = request.model_dump()
        data.pop("p_g_id", None)
        sql_stmt = insert(gstr2a).values(**data)
        result = db.execute(sql_stmt)
        db.commit()
        return_id = result.lastrowid
        return return_id

def delete_gstr2a(db: Session, request: dict):
    sql_stmt = delete(gstr2a).where(gstr2a.tax_period == request['tax_period'])
    db.execute(sql_stmt)
    db.commit()
    return


def save_sale_master(db: Session, request: saleMaster):
    data = request.model_dump()
    data.pop("id", None)
    sql_stmt = insert(saleMaster).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return_id = result.lastrowid
    return return_id

def update_sale_master(db: Session, request: dict):
    data = request.copy()
    data.pop('id', None)
    sql_stmt = update(saleMaster).where(saleMaster.id == request['id']).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return

def save_sale_detail(db: Session, request: saleDetail):
    data = request.model_dump()
    data.pop("id", None)
    sql_stmt = insert(saleDetail).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return_id = result.lastrowid
    return return_id