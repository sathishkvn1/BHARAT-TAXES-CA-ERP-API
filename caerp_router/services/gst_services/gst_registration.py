
from typing import List, Union
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from caerp_db.services import db_gst
from caerp_schema.services.gst_schema import BusinessDetailsSchema, CustomerRequestSchema, StakeHolderMasterSchema
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, Depends, HTTPException, Header
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
from datetime import date
from caerp_db.database import  get_db
from caerp_auth.authentication import authenticate_user


router = APIRouter(
    prefix="/gst",
    tags=['Gst Services']
)

#--------------business details

@router.post("/save_business_details")
def save_business_details(
    business_details: BusinessDetailsSchema,  # Now a single BusinessDetailsSchema
    task_id: int,
    id: int,  # 0 for insert, non-zero for update
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save business details and update the customer_id in the task master.
    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        # Call save_business_details with the required arguments
        result = db_gst.save_business_details(db, business_details, task_id, user_id, id)

        return {"success": True, "message": "Saved successfully", "customer_id": result["customer_id"]}

   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#--------------

@router.post("/save_customer_details/{customer_id}")
def save_customer_details(customer_id: int, 
                          customer_data: CustomerRequestSchema, 
                          db: Session = Depends(get_db),
                          token: str = Depends(oauth2.oauth2_scheme)
                          ):
    """
    Save customer details. 
 
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    try:
        # Handle customer details with the customer_id
        db_gst.save_customer_details(customer_id, customer_data,user_id,db)

        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

#--------
@router.get("/get_customers/{customer_id}")
def get_customer_details(customer_id: int, 
                          db: Session = Depends(get_db)):
    """
    get customer details. 
 
    """
    customer_details = db_gst.get_customer_details(db, customer_id)
    
    if customer_details is None:
        return []
    
    return customer_details



#----save stakeholder_details--------
@router.post("/save_stake_holder_master")
def save_stake_holder_master(
    request_data: StakeHolderMasterSchema,
    customer_id: int,
    # address_type: str = Query(enum=['RESIDENTIAL', 'PERMANENT', 'PRESENT', 'OFFICE']),
    stakeholder_type: str = Query(enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - 1.Insert Data into stake_holder_master and Capture the ID and Use the captured stake_holder_master_id to insert into the stake_holder_master_id 
        column in the customer_stake_holders table.
    - 2.Insert Data into stake_holder_contact_details and Capture the ID: Use the captured contact_details_id to insert into the contact_details_id column in
        the customer_stake_holders table.
    - 3.Insert Address Data into stake_holder_address and Map the IDs Based on address_type: Based on the address_type, capture the inserted id of the address and store it
        in the corresponding columns of the customer_stake_holders table.
    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    try:
        # Pass customer_id, address_type, and stakeholder_type to the save function
        result = db_gst.save_stakeholder_details(request_data, user_id, db, customer_id, stakeholder_type)
        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#-get stakeholder_details
@router.get("/get_stakeholder_master/{customer_id}")
def get_stakeholder_master(
    customer_id: int,
    stakeholder_type: str = Query(
        ...,
        enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']
    ),
    db: Session = Depends(get_db)
):
    """
    Get the details of a stakeholder by their customer_id and type.

    - customer_id (int): The ID of the customer.
    - stakeholder_type (str): The type of stakeholder to filter by.
    """

    # Call your function to get stakeholder details
    stakeholder_details = db_gst.get_stakeholder_details(db, customer_id, stakeholder_type)

    if not stakeholder_details:
        return []

    return stakeholder_details