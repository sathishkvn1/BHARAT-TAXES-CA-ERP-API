from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Any, List, Optional, Type, Union
from caerp_db.database import get_db
from caerp_db.gst import db_gst
from sqlalchemy.orm import Session
from caerp_auth import oauth2
from typing import Any, List, Optional, Type, Union
from fastapi import APIRouter, Body ,Depends,Request,HTTPException,status,Response, Query, File, UploadFile
from caerp_schema.gst.gst_schema import gstTestSchema,gst2bSchema
from datetime import date,datetime
from io import BytesIO
import pandas as pd
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
    
        
            
      
        