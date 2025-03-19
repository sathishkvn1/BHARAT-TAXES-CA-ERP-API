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
    gstin = df['data']['gstin']
    b2bdata = df['data']['docdata']['b2b']
    cdnrdata = df['data']['docdata']['cdnr']
    
    final_data = []
    for row in b2bdata:
        inv = row['inv']
        trdnm = row['trdnm']
        supprd = row['supprd']
        formatedsupprd = datetime.strptime(supprd[2:] + "-" + supprd[:2] + "-01", "%Y-%m-%d").date()
        ctin = row['ctin']
        supfildt = dateFormat(row['supfildt'])

        for invRow in inv:
                dt = dateFormat(invRow['dt'])
                val = invRow['val']
                txval = invRow['txval']
                typ = invRow['typ']
                rsn = invRow['rsn']

                data = {
                "p_g_id" : 0,
                "cfs" : "",
                "type" : "b2b",
                "supplier_name" : trdnm,
                "supplier_tax_period": formatedsupprd,
                "supplier_file_date": supfildt,
                "gstin" : ctin,
                "invoice_date": dt,
                "invoice_number" : invRow['inum'],
                "applicable_tax_per" : 1,
                "state" : invRow['pos'],
                "reverse_charge" : invRow['rev'],
                "taxable_rate" : 0,
                "taxable_value" : 0,
                "iamt" : invRow['igst'],
                "camt" : invRow['cgst'],
                "samt" : invRow['sgst'],
                "csamt" : invRow['cess'],
                "elg" : invRow['itcavl'],
                "tx_i" : 0,
                "tx_c" : 0,
                "tx_s" : 0,
                "tx_cs" : 0,
                "refund_number" : "",
                "refund_date": '2025-03-19',
                "reason" : "",
                "document_type" : "",
                "p_gst" : "",
                "chksum" : "",
                "flag" : "",
                "cflag" : "",
                "inv_typ" : "",
                "new_entry" : 0,
                "gstr_description" : "",                
                "amd_invoice_number" : "",
                "amd_invoice_date": '2025-03-19',
                "tax_period" : formatedMonYear,
                "entry_date" : entry_date
                }
               
                data_dict = gst2bSchema(**data)
                db_gst.save_gstr2b(db,data_dict)
    
        
            
      
        