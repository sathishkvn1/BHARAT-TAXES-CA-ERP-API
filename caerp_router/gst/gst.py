from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Any, List, Optional, Type, Union
from caerp_db.database import get_db
from caerp_db.gst import db_gst
from sqlalchemy.orm import Session
from caerp_auth import oauth2
from typing import Any, List, Optional, Type, Union
from fastapi import APIRouter, Body ,Depends,Request,HTTPException,status,Response, Query, File, UploadFile
from caerp_schema.gst.gst_schema import gstTestSchema, gst2bSchema, gst2aSchema, saleMasterSchema
from datetime import date,datetime
from io import BytesIO
import pandas as pd
import os
import json



router  = APIRouter(
    tags=['Gst']
)




@router.get("/admin_dashboard")
async def get_dashboard():    
    return {"message": "Welcome to the Admin Dashboard"}

@router.post("/check_post")
async def check_post(employee_id: Optional[int] = 0):    
    return {"message": f"Employee id is {employee_id} "}

@router.post("/save_gst_test")
async def save_gst(
    db: Session = Depends(get_db),
    request: gstTestSchema  = Body(...)):
    # print("reached here")
    print(request)
    result = db_gst.save_gst_test(db,request)
    print(result)
    if result:
         return {"message": f"saved successfully {result}"}
    else:
         return {"message": f"save failed "}
    

@router.post("/save_gst_fileupload")
async def save_gst_fileupload(
    db: Session = Depends(get_db),
    file: UploadFile = File(...)):
    #  try:

        file_content = BytesIO(file.file.read())
        df = pd.read_csv(file_content, encoding='utf-8')


        for _, row in df.iterrows():
            data = {
                "id": row[0],
                "name": row[1],
                "gst": row[2],  
                "amount": row[3]
            }
            print(data)
            data_dict = gstTestSchema(**data)
           
            db_gst.save_gst_test(db,data_dict)

    #     return {"message": f"saved successfully"}
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def dateFormat(date):
    date_obj = datetime.strptime(date, "%d-%m-%Y")
    return date_obj.strftime("%Y-%m-%d")

@router.post("/save_gst2b_fileupload")
async def save_gst2b_fileupload(
    db: Session = Depends(get_db),
    file: UploadFile = File(...)):

    file_content = BytesIO(file.file.read())
    json_str = file_content.read().decode('utf-8')  # Convert BytesIO content to string
    df = json.loads(json_str)

    entry_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mon_year = df['data']['rtnprd']
    formatedMonYear = datetime.strptime(mon_year[2:] + "-" + mon_year[:2] + "-01", "%Y-%m-%d").date()

    condition ={"tax_period": formatedMonYear}

    db_gst.delete_gstr2b(db, condition)

    gstin = df['data']['gstin']
    b2bdata = df['data']['docdata'].get('b2b', [])
    b2badata = df['data']['docdata'].get('b2ba', [])
    cdnrdata = df['data']['docdata'].get('cdnr', [])
    cdnadata = df['data']['docdata'].get('cdna', [])

    for record in b2bdata:
        record["type"] = "b2b"

    for record in cdnrdata:
        record["type"] = "cdnr"

    for record in cdnadata:
        record["type"] = "cdna"

    for record in b2badata:
        record["type"] = "b2ba"
    
    mergedData = b2bdata + cdnrdata + cdnadata + b2badata

    for row in mergedData:
        
        trdnm = row['trdnm']
        supprd = row['supprd']
        formatedsupprd = datetime.strptime(supprd[2:] + "-" + supprd[:2] + "-01", "%Y-%m-%d").date()
        ctin = row['ctin']
        type = row['type']
        supfildt = dateFormat(row['supfildt'])

        if type == "b2b":
            inv = row['inv']
        else:
            inv = row['nt']

        for invRow in inv:
                dt = dateFormat(invRow['dt'])
                oidt = dateFormat(invRow['dt'])
                oinum = ntnum = ""
                refund_date = "1900-01-01"
                inum = ""

                if type == "b2ba":
                    oidt = dateFormat(invRow['oidt'])
                    oinum = invRow['oinum']
                elif type == "cdnr":
                    oidt = dt
                    ntnum = invRow['ntnum']
                    refund_date = dt
                elif type == "cdna":
                    oidt = dateFormat(invRow['oidt'])
                    oinum = invRow['oinum']
                else:
                    oidt = dt
                    inum = invRow['inum']
                
                data = {
                "p_g_id" : 0,
                "cfs" : "",
                "type" : type,
                "supplier_name" : trdnm,
                "supplier_tax_period": formatedsupprd,
                "supplier_file_date": supfildt,
                "gstin" : ctin,
                "invoice_date": dt,
                "invoice_number" : inum,
                "applicable_tax_per" : 1,
                "state" : invRow['pos'],
                "reverse_charge" : invRow['rev'],
                "taxable_rate" : 0,
                "taxable_value" : invRow['txval'],
                "iamt" : invRow['igst'],
                "camt" : invRow['cgst'],
                "samt" : invRow['sgst'],
                "csamt" : invRow['cess'],
                "elg" : invRow['itcavl'],
                "tx_i" : 0,
                "tx_c" : 0,
                "tx_s" : 0,
                "tx_cs" : 0,
                "refund_number" : ntnum,
                "refund_date": refund_date,
                "reason" : invRow['rsn'],
                "document_type" : invRow['typ'],
                "p_gst" : "",
                "chksum" : "",
                "flag" : "",
                "cflag" : "",
                "inv_typ" : invRow['typ'],
                "new_entry" : 0,
                "gstr_description" : "",                
                "amd_invoice_number" : oinum,  
                "amd_invoice_date": oidt,
                "tax_period" : formatedMonYear,
                "entry_date" : entry_date
                }
               
                data_dict = gst2bSchema(**data)
                db_gst.save_gstr2b(db,data_dict)
    
    return {"success": True, "message": "GSTR2B file uploaded successfully"}
        
            
@router.post("/save_gst2a_fileupload")
async def save_gst2a_fileupload(
    db: Session = Depends(get_db),
    file: UploadFile = File(...)):     
    
    file_content = BytesIO(file.file.read())
    json_str = file_content.read().decode('utf-8')  # Convert BytesIO content to string
    df = json.loads(json_str)

    entry_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mon_year = df['fp']
    formatedMonYear = datetime.strptime(mon_year[2:] + "-" + mon_year[:2] + "-01", "%Y-%m-%d").date()

    condition ={"tax_period": formatedMonYear}

    db_gst.delete_gstr2a(db, condition)

    gstin = df['gstin']
    b2bdata = df.get('b2b', [])
    b2badata = df.get('b2ba', [])
    cdnrdata = df.get('cdnr', [])
    cdnadata = df.get('cdna', [])

    for record in b2bdata:
        record["type"] = "b2b"

    for record in cdnrdata:
        record["type"] = "cdn"

    for record in cdnadata:
        record["type"] = "cdna"

    for record in b2badata:
        record["type"] = "b2ba"
    
    mergedData = b2bdata + cdnrdata + cdnadata + b2badata

    for row in mergedData:
        cfs = row['cfs']
        ctin = row['ctin']
        type = row['type']
        
        if type == "b2b":
            inv = row['inv']
        else:
            inv = row['nt']

        for invRow in inv:
            dt = dateFormat(invRow['idt'])
            oidt = dateFormat(invRow['idt'])
            oinum = ntnum = document_type = inv_typ = rsn = ""
            refund_date = "1900-01-01"
            inum = ""
            state = invRow['pos']
            rchrg = invRow['rchrg']
            itms = invRow['itms']

            if type == "b2ba":
                oidt = dateFormat(invRow['oidt'])
                oinum = invRow['oinum']
            elif type == "cdn":
                oidt = dt
                ntnum = invRow['nt_num']
                refund_date  = dateFormat(invRow['nt_dt'])
                document_type =invRow['ntty']
                inv_typ = invRow['inv_typ']
            elif type == "cdna":
                oidt = dateFormat(invRow['oidt'])
                oinum = invRow['oinum']
            else:
                oidt = dt
                inum = invRow['inum']


            for invItem in itms:   
                    data = {
                    "p_g_id" : 0,
                    "cfs" : cfs,
                    "type" : type,
                    "gstin" : ctin,
                    "invoice_date": dt,
                    "invoice_number" : inum,
                    "state" : state,
                    "reverse_charge" : rchrg,
                    "taxable_rate" : invItem['itm_det']['rt'],
                    "taxable_value" : invItem['itm_det']['txval'],
                    "iamt" : invItem['itm_det'].get('iamt', 0.00),
                    "camt" : invItem['itm_det'].get('camt', 0.00),
                    "samt" : invItem['itm_det'].get('samt', 0.00),
                    "csamt" : invItem['itm_det'].get('csamt', 0.00),
                    "elg" : "",
                    "tx_i" : 0,
                    "tx_c" : 0,
                    "tx_s" : 0,
                    "tx_cs" : 0,
                    "refund_number" : ntnum,
                    "refund_date": refund_date,
                    "reason" : rsn,
                    "document_type" : document_type,
                    "p_gst" : "",
                    "chksum" : "",
                    "flag" : "",
                    "cflag" : "",
                    "inv_typ" : inv_typ,
                    "new_entry" : 0,
                    "gstr_description" : "",                
                    "amd_invoice_number" : oinum,  
                    "amd_invoice_date": oidt,
                    "tax_period" : formatedMonYear,
                    "entry_date" : entry_date
                    }
                
                    data_dict = gst2aSchema(**data)
                    db_gst.save_gstr2a(db,data_dict)
    
    return {"success": True, "message": "GSTR2A file uploaded successfully"}

@router.post("/save_sale_fileupload")
async def save_sale_fileupload(
    db: Session = Depends(get_db),
    file: UploadFile = File(...)):
    # try:
        contents = await file.read()
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(BytesIO(contents), encoding='utf-8')
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(BytesIO(contents))
        else:
            return {"error": "Unsupported file type. Please upload a CSV or Excel file."}
        
        entry_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for _, row in df.iterrows():
            
                invoice_number = row[0]
                invoice_date = dateFormat(row[1])
                customer_name = row[2]
                gstin = row[3]
                ewaybill = row[4]
                saletype = row[5]
                invoice_type = row[6]
                reverse_charge = row[7]
                hsn = row[8]
                rate = row[9]
                qty = row[10]
                tax = row[11]
                discount = row[12]
                cess = row[13]
                paymode = row[14].upper()
                tax_period = row[15]

                data = {
                    "id":0,
                    "voucher_id":1,
                    "head_id":2,
                    "sub_head_id":3,
                    "invoice_number": invoice_number,
                    "invoice_date": invoice_date,
                    "financial_year_id":0,
                    "payment_mode" : paymode,
                    "transation_id": "",
                    "tax_period_year" : entry_date,
                    "tax_period_month" : 0,
                    "is_amended_invoice" : 0,
                    "amended_invoice_number" : "",
                    "amended_invoice_date" : None,
                    "amended_tax_period_year" : None,
                    "amended_tax_period_month" : 0,
                    "has_gst_filed" : "no",
                    "gst_filed_date" : None,
                    "transportation_mode" : 0,
                    "transported_date" : None,
                    "vehicle_number" : "",
                    "port_code" : "",
                    "eway_bill_number" : "",
                    "discount_amount" : 0.00,
                    "taxable_amount" : 0.00,
                    "cgst_amount" : 0.00,
                    "sgst_amount" : 0.00,
                    "igst_amount" : 0.00,
                    "cess_amount" : 0.00,
                    "total_amount" : 0.00,
                    "state_type" : 0,
                    "b2c_state" : 0,
                    "reverse_charge" : 0,
                    "narration" : "",
                    "created_by" : 0,
                    "created_on" : entry_date,
                    "modified_by" : 0,
                    "modified_on" : None,
                    "is_verified" : "no",
                    "verified_by" : 0,
                    "is_cancelled" : "no",
                    "cancelled_by" : None,
                    "cancellation_reason" : "",
                    "is_deleted" : "no",
                    "deleted_by" : 0,
                    "deleted_on" : None
                }

                print(data)
                data_dict = saleMasterSchema(**data)
                db_gst.save_sale_master(db,data_dict)

        return {"message": "File processed successfully" + file_ext}

    # except Exception as e:
    #     return {"error 2": str(e)}