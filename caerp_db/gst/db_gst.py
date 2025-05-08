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

def delete_sale(db: Session, request: dict):
    # Step 1: Build dynamic filter conditions
    conditions = [getattr(saleMaster, key) == value for key, value in request.items()]
     # Step 2: Fetch rows that match the condition (to get their IDs)
    rows_to_delete = db.query(saleMaster).filter(and_(*conditions)).all()
    deleted_ids = [row.id for row in rows_to_delete]

    if deleted_ids:
        db.query(saleMaster).filter(saleMaster.id.in_(deleted_ids)).delete(synchronize_session=False)
        db.query(saleDetail).filter(saleDetail.sales_master_id.in_(deleted_ids)).delete(synchronize_session=False)
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

def insertOrGetItemId(db: Session, request: dict):
     # Step 1: Build dynamic filter
    conditions = [getattr(itemMaster, key) == value for key, value in request.items()]
    
    # Step 2: Try to find an existing item
    existing_item = db.query(itemMaster).filter(*conditions).first()

    if existing_item:
        # Step 3: If exists, return its id
        return existing_item.item_id
    else:
        # Step 4: If not exists, insert new item
        sql_stmt = insert(itemMaster).values(**request)
        result = db.execute(sql_stmt)
        db.commit()
        return_id = result.lastrowid
        return return_id
    
def insertOrGetCustomerId(db: Session, request: dict):
     # Step 1: Build dynamic filter
    conditions = [getattr(accountHead, key) == value for key, value in request.items()]
    
    # Step 2: Try to find an existing item
    existing_item = db.query(accountHead).filter(*conditions).first()

    if existing_item:
        # Step 3: If exists, return its id
        return existing_item.account_head_id
    else:
        # Step 4: If not exists, insert new item
        sql_stmt = insert(accountHead).values(**request)
        result = db.execute(sql_stmt)
        db.commit()
        return_id = result.lastrowid
        return return_id
    

def save_purchase_master(db: Session, request: purchaseMaster):
    data = request.model_dump()
    data.pop("id", None)
    sql_stmt = insert(purchaseMaster).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return_id = result.lastrowid
    return return_id

def update_purchase_master(db: Session, request: dict):
    data = request.copy()
    data.pop('id', None)
    sql_stmt = update(purchaseMaster).where(purchaseMaster.id == request['id']).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return

def delete_purchase(db: Session, request: dict):
    # Step 1: Build dynamic filter conditions
    conditions = [getattr(purchaseMaster, key) == value for key, value in request.items()]
     # Step 2: Fetch rows that match the condition (to get their IDs)
    rows_to_delete = db.query(purchaseMaster).filter(and_(*conditions)).all()
    deleted_ids = [row.id for row in rows_to_delete]

    if deleted_ids:
        db.query(purchaseMaster).filter(purchaseMaster.id.in_(deleted_ids)).delete(synchronize_session=False)
        db.query(purchaseDetail).filter(purchaseDetail.sales_master_id.in_(deleted_ids)).delete(synchronize_session=False)
        db.commit()
        return

def save_purchase_detail(db: Session, request: purchaseDetail):
    data = request.model_dump()
    data.pop("id", None)
    sql_stmt = insert(purchaseDetail).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return_id = result.lastrowid
    return return_id

def save_credit_master(db: Session, request: creditMaster):
    data = request.model_dump()
    data.pop("id", None)
    sql_stmt = insert(creditMaster).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return_id = result.lastrowid
    return return_id

def save_credit_detail(db: Session, request: creditDetail):
    data = request.model_dump()
    data.pop("id", None)
    sql_stmt = insert(creditDetail).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return_id = result.lastrowid
    return return_id

def update_credit_master(db: Session, request: dict):
    data = request.copy()
    data.pop('id', None)
    sql_stmt = update(creditMaster).where(creditMaster.id == request['id']).values(**data)
    result = db.execute(sql_stmt)
    db.commit()
    return

def delete_credit(db: Session, request: dict):
    # Step 1: Build dynamic filter conditions
    conditions = [getattr(creditMaster, key) == value for key, value in request.items()]
     # Step 2: Fetch rows that match the condition (to get their IDs)
    rows_to_delete = db.query(creditMaster).filter(and_(*conditions)).all()
    deleted_ids = [row.id for row in rows_to_delete]

    if deleted_ids:
        db.query(creditMaster).filter(creditMaster.id.in_(deleted_ids)).delete(synchronize_session=False)
        db.query(creditDetail).filter(creditDetail.credit_note_master_id.in_(deleted_ids)).delete(synchronize_session=False)
        db.commit()
        return