
from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from caerp_db.services import db_gst
from caerp_schema.services.gst_schema import BusinessDetailsSchema, CustomerRequestSchema
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, Depends, HTTPException, Header
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
from datetime import date
from caerp_db.database import  get_db
from caerp_auth.authentication import authenticate_user


router = APIRouter(
    prefix ='/gst',
    tags=['GST Services']
)


#--------------business details

@router.post("/save_business_details")
def save_business_details(
    business_details: List[BusinessDetailsSchema], 
    task_id: int,
    id: int,  # 0 for insert, non-zero for update
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save business details. 
    Expects a list of business details to save.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        for details in business_details:
            # Call save_business_details with all required arguments
            result = db_gst.save_business_details(db, details, task_id,user_id, id)
           

        return {"success": True, "message": "Saved successfully"}

    except HTTPException as e:
        raise e
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
        db_gst.handle_customer_details(customer_id, customer_data, db)

        # Commit the changes to the database
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process request: {e}")

    return {"message": "Customer details saved successfully"}

#--------
@router.get("/get_customers/{customer_id}", response_model=dict)
def get_customer_details(customer_id: int, 
                          db: Session = Depends(get_db)):
    """
    get customer details. 
 
    """
    customer_details = db_gst.get_customer_details(db, customer_id)
    
    if customer_details is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer_details