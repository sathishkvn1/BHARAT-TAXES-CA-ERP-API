
from typing import List, Union
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from sqlalchemy import select
from caerp_db.common.models import BusinessActivity, BusinessActivityMaster, BusinessActivityType
from caerp_db.services import db_gst
from caerp_schema.services.gst_schema import BusinessData, BusinessDetailsSchema, CustomerGoodsCommoditiesSupplyDetailsSchema, CustomerGstStateSpecificInformationSchema, CustomerRequestSchema, StakeHolderMasterSchema
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
    - Save business details and update the customer_id in the task master.
    
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
    - Save customer details. 
 
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
def get_customer_details(
    customer_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Retrieve details of a specific customer based on their ID.

    - param customer_id: ID of the customer to retrieve
    - param db: SQLAlchemy database session
    - param token: OAuth2 token for authentication
    - return: Customer details or raises an HTTPException if not found
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    
    customer_details = db_gst.get_customer_details(db, customer_id,user_id)

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
    stakeholder_type: str = Query(...,enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
                          ):
    """
    Get the details of a stakeholder by their customer_id and type.

    - customer_id (int): The ID of the customer.
    - stakeholder_type (str): The type of stakeholder to filter by.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    

    # Call your function to get stakeholder details
    stakeholder_details = db_gst.get_stakeholder_details(db, customer_id, stakeholder_type,user_id)

    if not stakeholder_details:
        return []

    return stakeholder_details



#-----------------business_activity

@router.get("/get_business-activities/{activity_type_id}")
def get_business_activities(activity_type_id: int, 
                            db: Session = Depends(get_db)):
    # Build the query
    stmt = (
        select(
            BusinessActivityType.business_activity_type,
            BusinessActivityMaster.business_activity,
            BusinessActivity.business_activity.label("activity")
        )
        .join(BusinessActivityMaster, BusinessActivityType.id == BusinessActivityMaster.business_activity_type_id)
        .join(BusinessActivity, BusinessActivityMaster.id == BusinessActivity.activity_master_id)
        .where(
            BusinessActivityType.id == activity_type_id,
            BusinessActivityType.is_deleted == 'no',
            BusinessActivityMaster.is_deleted == 'no',
            BusinessActivity.is_deleted == 'no'
        )
    )

    # Execute the query
    result = db.execute(stmt).all()

    # Check if any results were found
    if not result:
        return []

    # Transform result into a list of dictionaries
    activities = [
        {
            "business_activity_type": row[0],
            "business_activity": row[1],
            "activity": row[2],
        }
        for row in result
    ]

    return {"business_activities": activities}



#--------

@router.post("/save_business_place")
def save_business_place_details(
    id:int,
    customer_id: int,
    business_data: BusinessData,
    type: str = Query(..., enum=['PRINCIPAL_PLACE_ADDRESS', 'ADDITIONAL_PLACE']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - Save business data, including business places and activities, associated with a customer.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    try:
        result = db_gst.save_business_place(customer_id, business_data, db,user_id,id)
        return {"success": True, "message": result["message"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/get_business_place")
def get_business_place(
    customer_id: int,
    type: str = Query(..., enum=['PRINCIPAL_PLACE_ADDRESS', 'ADDITIONAL_PLACE']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
                          ):
    """
    - Retrieve business data based on customer_id and type.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    
    return db_gst.get_business_place(customer_id, type, db,user_id)



#-----------------

@router.get("/get_hsn_sac_data")
def get_hsn_sac_data(
    hsn_sac_class_id:int,
    hsn_sac_code: Optional[str] = None,  
    db: Session = Depends(get_db)  ,
    token: str = Depends(oauth2.oauth2_scheme)
                          ):
    """
    - Fetch data from AppHsnSacMaster based on hsn_sac_class_id and/or hsn_sac_code.
    - param hsn_sac_class_id: ID of the HSN/SAC class (optional)
    - param hsn_sac_code: HSN/SAC code (optional)
    - param db: SQLAlchemy database session
    - return: List of records containing hsn_sac_class, hsn_sac_code, and hsn_sac_description
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    
    return db_gst.get_hsn_sac_data(hsn_sac_class_id, hsn_sac_code, db,user_id)



#--
@router.post("/save_goods_commodities")
def save_goods_commodities(
    id: int,  # New field to handle update or create
    customer_id: int,
    details: CustomerGoodsCommoditiesSupplyDetailsSchema,  # Expecting the schema for details
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - Save Goods Commodities
    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    try:
        return db_gst.save_goods_commodities_details(id, customer_id, details, db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/get_hsn_commodities/{customer_id}")
def get_hsn_commodities(customer_id: int, 
                         db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)
                         ):
    """
    Retrieve HSN/SAC commodities details for a given customer ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  # Retrieve user_id from token

    # Call the function to get commodities, passing the user_id
    commodities = db_gst.get_hsn_commodities_by_customer_id(customer_id, user_id, db)
    return commodities



@router.post("/save-gst-state-info/{id}")
def save_gst_state_info(
    id: int,
    customer_id: int,
    data: CustomerGstStateSpecificInformationSchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
):
    """
    - Save or update GST state-specific information.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    return db_gst.save_customer_gst_state_specific_information(id, customer_id, data, db, user_id)




#--------

@router.get("/get_gst_state_specific_information/{customer_id}", 
            response_model=List[CustomerGstStateSpecificInformationSchema]
            )
def get_gst_state_specific_information(
    customer_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
):
    """
    - Retrieve GST state-specific information for a given customer ID.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  # Optionally track user info

    gst_state_info = db_gst.get_gst_state_specific_information_by_customer_id(customer_id, db,user_id)

    if not gst_state_info:
        return []

    return gst_state_info