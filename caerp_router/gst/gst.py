from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Any, List, Optional, Type, Union
from caerp_db.database import get_db
from caerp_db.gst import db_gst
from sqlalchemy.orm import Session
from caerp_auth import oauth2
from typing import Any, List, Optional, Type, Union
from fastapi import APIRouter, Body ,Depends,Request,HTTPException,status,Response, Query, File, UploadFile
from caerp_schema.gst.gst_schema import gstTestSchema, gst2bSchema, gst2aSchema, saleMasterSchema, saleDetailsSchema, purchaseMasterSchema, purchaseDetailSchema
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



def taxPeriodFormat(date_str):
    date_str = date_str.title()
    parsed_date = datetime.strptime(date_str, "%b-%Y")
    formatted_date = parsed_date.strftime("%Y-%m-%d")
    return formatted_date

@router.post("/save_sale_fileupload")
async def save_sale_fileupload(
    db: Session = Depends(get_db),
    file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(BytesIO(contents), encoding='utf-8')
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(BytesIO(contents))
        else:
            return {"error": "Unsupported file type. Please upload a CSV or Excel file."}
        
        entry_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        oldinv="xxx"
        firmState="32"
        firmId = 1
        # for general customers
        sub_head_id = 1
        b2c_state = 0
        i = total_cgst = total_sgst = total_igst = total_taxable_amount = total_gross_amount = total_discount_amount = total_cess_amount = grand_total = 0
        for _, row in df.iterrows():
            
                invoice_number = str(row[0])
                invoice_date = dateFormat(row[1])
                customer_name = row[2]
                gstin = str(row[3])
                customerState = gstin[:2]
                ewaybill = str(row[4])
                saletype = row[5]
                invoice_type = row[6]
                reverse_charge = row[7].lower()
                hsn = str(row[8])
                rate = row[9]
                qty = row[10]
                tax = row[11]
                discount = row[12]
                cess = row[13]
                paymode = row[14].upper()
                tax_period = taxPeriodFormat(row[15])
                gross_amount = float(rate) * float(qty)
                taxable_amount = gross_amount - float(discount)
                discount_percentage = float(discount) / float(gross_amount) * 100
                cess_percentage = float(cess) / float(taxable_amount) * 100
                if(firmState == customerState):
                    sgst = cgst = taxable_amount * float(tax) / 200
                    sgst_percentage = cgst_percentage = float(tax) / 2
                    igst = igst_percentage = 0
                else:
                    igst = taxable_amount * float(tax) / 100
                    igst_percentage = tax
                    sgst = cgst = sgst_percentage = cgst_percentage = 0
                
                if(invoice_number != oldinv):
                    if(i>0):
                        updateData ={
                            "id":sale_master_id,
                            "gross_total": total_gross_amount,
                            "discount_amount" : total_discount_amount,
                            "taxable_amount" : total_taxable_amount,
                            "cgst_amount" : total_cgst,
                            "sgst_amount" : total_sgst,
                            "igst_amount" : total_igst,
                            "cess_amount" : total_cess_amount,
                            "total_amount" : grand_total,
                        }
                        db_gst.update_sale_master(db,updateData)

                    deleteSaleConditions ={
                        "invoice_number": invoice_number,
                        "tax_period": tax_period
                    }
                    db_gst.delete_sale(db,deleteSaleConditions)

                    if(invoice_type == "B2B"):
                        customerData ={
                            "account_group_id": 1,
                            "parent_head_id": firmId,
                            "account_head_name": customer_name,
                            "account_head_alternate_name": customer_name,
                            "gstin": gstin,
                        }
                        sub_head_id=db_gst.insertOrGetCustomerId(db,customerData)

                    if(invoice_type == "B2C"):
                        b2c_state = customerState

                    masterData = {
                        "id":0,
                        "voucher_id":1,
                        "head_id":firmId,
                        "sub_head_id":sub_head_id,
                        "invoice_number": invoice_number,
                        "invoice_date": invoice_date,
                        "financial_year_id":0,
                        "payment_mode" : paymode,
                        "transation_id": "",
                        "tax_period" : tax_period,
                        "invoice_type" : invoice_type,
                        "is_amended_invoice" : 0,
                        "amended_invoice_number" : "",
                        "amended_invoice_date" : None,
                        "amended_tax_period" : None,
                        "has_gst_filed" : "no",
                        "gst_filed_date" : None,
                        "transportation_mode" : 0,
                        "transported_date" : None,
                        "vehicle_number" : "",
                        "port_code" : "",
                        "eway_bill_number" : ewaybill,
                        "gross_total" : 0.00,
                        "discount_amount" : 0.00,
                        "taxable_amount" : 0.00,
                        "cgst_amount" : 0.00,
                        "sgst_amount" : 0.00,
                        "igst_amount" : 0.00,
                        "cess_amount" : 0.00,
                        "total_amount" : 0.00,
                        "state_type" : 0,
                        "b2c_state" : b2c_state,
                        "reverse_charge" : reverse_charge,
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

                    
                    data_dict = saleMasterSchema(**masterData)
                    sale_master_id = db_gst.save_sale_master(db,data_dict)
                    oldinv=invoice_number
                    total_cgst = total_sgst = total_igst = total_taxable_amount = total_gross_amount = total_discount_amount = total_cess_amount = grand_total = 0

                itemData ={
                    "item_name":hsn,
                    "item_type":"GOODS",
                    "item_hsn_sac":hsn,
                    "item_gst_tax":float(tax),
                    "item_sku":"NOS",
                }
                item_id=db_gst.insertOrGetItemId(db,itemData)    
                total_amount = (cgst + sgst + igst + taxable_amount +cess)
                detailData={
                    "id":0,
                    "sales_master_id":sale_master_id,
                    "item_master_id":item_id,
                    "hsn_sac_code":hsn,
                    "gst_rate":float(tax),
                    "quantity":qty,
                    "sku_code":"",
                    "unit_rate":float(rate),
                    "gross_amount":gross_amount,
                    "discount_percentage":discount_percentage,
                    "discount_amount":discount,
                    "taxable_amount":taxable_amount,
                    "cgst_percentage":cgst_percentage,
                    "cgst_amount":cgst,
                    "sgst_percentage":sgst_percentage,
                    "sgst_amount":sgst,
                    "igst_percentage":igst_percentage,
                    "igst_amount":igst,
                    "cess_percentage":cess_percentage,
                    "cess_amount":cess,
                    "total_amount":total_amount,
                    "modified_by":0,
                    "modified_on":None,
                    "is_deleted":"no",
                    "deleted_by":0,
                    "deleted_on":None
                }
                total_gross_amount += gross_amount
                total_cgst += cgst
                total_sgst += sgst
                total_igst += igst
                total_taxable_amount += taxable_amount
                total_discount_amount += discount
                total_cess_amount += cess
                grand_total += total_amount

                dataDetail_dict = saleDetailsSchema(**detailData)
                sale_detail_id = db_gst.save_sale_detail(db,dataDetail_dict)
                i+=1
            
        
        updateData ={
            "id":sale_master_id,
            "gross_total": total_gross_amount,
            "discount_amount" : total_discount_amount,
            "taxable_amount" : total_taxable_amount,
            "cgst_amount" : total_cgst,
            "sgst_amount" : total_sgst,
            "igst_amount" : total_igst,
            "cess_amount" : total_cess_amount,
            "total_amount" : grand_total,
        }
        db_gst.update_sale_master(db,updateData)

        return {"message": "File processed successfully" + file_ext}

    except Exception as e:
        return {"error": str(e)}
    




@router.post("/save_purchase_fileupload")
async def save_purchase_fileupload(
    db: Session = Depends(get_db),
    file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(BytesIO(contents), encoding='utf-8')
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(BytesIO(contents))
        else:
            return {"error": "Unsupported file type. Please upload a CSV or Excel file."}
        
        entry_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        oldinv="xxx"
        firmState="32"
        firmId = 1
        # for general customers
        sub_head_id = 1
        b2c_state = 0
        i = total_cgst = total_sgst = total_igst = total_taxable_amount = total_gross_amount = total_discount_amount = total_cess_amount = grand_total = 0
        for _, row in df.iterrows():
            
                invoice_number = str(row[0])
                invoice_date = dateFormat(row[1])
                customer_name = row[2]
                gstin = str(row[3])
                customerState = gstin[:2]
                ewaybill = str(row[4])                
                reverse_charge = row[5].lower()
                hsn = str(row[6])
                rate = row[7]
                qty = row[8]
                tax = row[9]
                discount = row[10]
                cess = row[11]
                paymode = row[12].upper()
                invoice_type = row[13].upper()
                purchase_type = row[14].lower()
                is_composite = row[15].lower()
                tax_period = taxPeriodFormat(row[16])

                gross_amount = float(rate) * float(qty)
                taxable_amount = gross_amount - float(discount)
                discount_percentage = float(discount) / float(gross_amount) * 100
                cess_percentage = float(cess) / float(taxable_amount) * 100
                if(firmState == customerState):
                    sgst = cgst = taxable_amount * float(tax) / 200
                    sgst_percentage = cgst_percentage = float(tax) / 2
                    igst = igst_percentage = 0
                else:
                    igst = taxable_amount * float(tax) / 100
                    igst_percentage = tax
                    sgst = cgst = sgst_percentage = cgst_percentage = 0
                
                if(invoice_number != oldinv):
                    if(i>0):
                        updateData ={
                            "id":purchase_master_id,
                            "gross_total": total_gross_amount,
                            "discount_amount" : total_discount_amount,
                            "taxable_amount" : total_taxable_amount,
                            "cgst_amount" : total_cgst,
                            "sgst_amount" : total_sgst,
                            "igst_amount" : total_igst,
                            "cess_amount" : total_cess_amount,
                            "total_amount" : grand_total,
                        }
                        db_gst.update_purchase_master(db,updateData)

                    deleteSaleConditions ={
                        "invoice_number": invoice_number,
                        "tax_period": tax_period
                    }
                    db_gst.delete_purchase(db,deleteSaleConditions)

                    if(invoice_type == "B2B"):
                        customerData ={
                            "account_group_id": 2,
                            "parent_head_id": firmId,
                            "account_head_name": customer_name,
                            "account_head_alternate_name": customer_name,
                            "gstin": gstin,
                        }
                        sub_head_id=db_gst.insertOrGetCustomerId(db,customerData)

                    if(invoice_type == "B2BUR"):
                        b2c_state = customerState

                    

                    masterData = {
                        "id":0,
                        "voucher_id":1,
                        "head_id":firmId,
                        "sub_head_id":sub_head_id,
                        "invoice_number": invoice_number,
                        "invoice_date": invoice_date,
                        "financial_year_id":0,
                        "tax_period": tax_period,
                        "invoice_type":invoice_type,
                        "is_amended_invoice":0,
                        "amended_invoice_number":"",
                        "amended_invoice_date":None,
                        "amended_tax_period":None,
                        "has_gst_filed":"no",
                        "gst_filed_date":None,
                        "transportation_mode":0,
                        "transported_date":None,
                        "vehicle_number":"",
                        "port_code":"",
                        "eway_bill_number":ewaybill,
                        "payment_mode":paymode,
                        "transation_id":"",
                        "gross_total":0.00,
                        "discount_amount":0.00,
                        "taxable_amount":0.00,
                        "cgst_amount":0.00,
                        "sgst_amount":0.00,
                        "igst_amount":0.00,
                        "cess_amount":0.00,
                        "round_off_amount":0.00,
                        "total_amount":0.00,
                        "state_type":0,
                        "b2c_state":b2c_state,
                        "reverse_charge":reverse_charge,
                        "is_composite":is_composite,
                        "narration":"",
                        "created_by":1,
                        "created_on":entry_date,    
                        "modified_by":None,
                        "modified_on":None,
                        "is_verified":0,
                        "verified_by":None,
                        "is_cancelled":0,
                        "cancelled_by":None,
                        "cancellation_reason":"",
                        "is_deleted":0,
                        "deleted_by":None,
                        "deleted_on":None
                    }

                    
                    data_dict = purchaseMasterSchema(**masterData)
                    purchase_master_id = db_gst.save_purchase_master(db,data_dict)
                    oldinv=invoice_number
                    total_cgst = total_sgst = total_igst = total_taxable_amount = total_gross_amount = total_discount_amount = total_cess_amount = grand_total = 0

                itemData ={
                    "item_name":hsn,
                    "item_type":"GOODS",
                    "item_hsn_sac":hsn,
                    "item_gst_tax":float(tax),
                    "item_sku":"NOS",
                }
                item_id=db_gst.insertOrGetItemId(db,itemData)    
                
                total_amount = (cgst + sgst + igst + taxable_amount +cess)
                detailData={
                    "id":0,
                    "purchase_master_id":purchase_master_id,
                    "item_master_id":item_id,
                    "purchase_type":purchase_type,
                    "itc_type":"yes",
                    "hsn_sac_code":hsn,
                    "gst_rate":float(tax),
                    "quantity":qty,
                    "sku_code":"",
                    "unit_rate":float(rate),
                    "gross_amount":gross_amount,
                    "discount_percentage":discount_percentage,
                    "discount_amount":discount,
                    "taxable_amount":taxable_amount,
                    "cgst_percentage":cgst_percentage,
                    "cgst_amount":cgst,
                    "sgst_percentage":sgst_percentage,
                    "sgst_amount":sgst,
                    "igst_percentage":igst_percentage,
                    "igst_amount":igst,
                    "cess_percentage":cess_percentage,
                    "cess_amount":cess,
                    "total_amount":total_amount,
                    "modified_by":None,
                    "modified_on":None,
                    "is_deleted":0,
                    "deleted_by":None,
                    "deleted_on":None
                }
                total_gross_amount += gross_amount
                total_cgst += cgst
                total_sgst += sgst
                total_igst += igst
                total_taxable_amount += taxable_amount
                total_discount_amount += discount
                total_cess_amount += cess
                grand_total += total_amount

                dataDetail_dict = purchaseDetailSchema(**detailData)
                purchase_detail_id = db_gst.save_purchase_detail(db,dataDetail_dict)
                i+=1
            
        
        updateData ={
            "id":purchase_master_id,
            "gross_total": total_gross_amount,
            "discount_amount" : total_discount_amount,
            "taxable_amount" : total_taxable_amount,
            "cgst_amount" : total_cgst,
            "sgst_amount" : total_sgst,
            "igst_amount" : total_igst,
            "cess_amount" : total_cess_amount,
            "total_amount" : grand_total,
        }
        db_gst.update_purchase_master(db,updateData)

        return {"message": "File processed successfully" + file_ext}

    except Exception as e:
        return {"error": str(e)}