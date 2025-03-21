

from typing import Any, List, Union
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from sqlalchemy import and_, or_, select, text
from caerp_constants.caerp_constants import AmendmentAction
from caerp_db.common.models import BusinessActivity, BusinessActivityMaster, BusinessActivityType, DistrictDB, StateDB
from caerp_db.office.models import AppBusinessConstitution
from caerp_db.services import db_gst
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerAmendmentHistory, CustomerBusinessPlace, CustomerBusinessPlaceActivity, CustomerMaster, GstViewRange
from caerp_schema.services.gst_schema import AdditionalTradeNameAmendment, AmendmentDetailsSchema, AmmendStakeHolderMasterSchema, BusinessData, BusinessDetailsSchema, CombinedSchema, CustomerAmendmentSchema, CustomerBusinessPlaceAmendmentSchema, CustomerBusinessPlaceFullAmendmentSchema, CustomerBusinessPlacesFullAmendmentSchema, CustomerDuplicateSchemaForGet, CustomerGoodsCommoditiesSupplyDetailsSchema, CustomerGstStateSpecificInformationSchema, CustomerGstStateSpecificInformationSchemaGet, CustomerRequestSchema, RangeDetailsSchema, StakeHolderMasterSchema, SuccessResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, Depends, HTTPException, Header
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
from datetime import date, datetime
from caerp_db.database import  get_db
from caerp_auth.authentication import authenticate_user


router = APIRouter(
    prefix="/gst",
    tags=['Gst Services']
)

#--------------Business Details----------------

@router.post("/save_business_details")
def save_business_details(
    business_details: BusinessDetailsSchema,  # Now a single BusinessDetailsSchema
    id: int,  # 0 for insert, non-zero for update
    task_id: Optional[int] = None,  # Optional task_id, default is None
    is_mother_customer: Optional[str] = "no",  # Optional is_mother_customer param, default to 'no'
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - Save business details and update the customer_id in the task master (if task_id provided).
    - Optionally, indicate if this customer is a 'mother customer' (is_mother_customer).
    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        # Call save_business_details with the required arguments
        result = db_gst.save_business_details(db, business_details, task_id, user_id, id, is_mother_customer)

        return {"success": True, "message": "Saved successfully", "customer_id": result["customer_id"], "customer_number": result["customer_number"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#--------------Save Customer Details----------------

@router.post("/save_customer_details/{customer_id}")
def save_customer_details(customer_id: int, 
                          service_task_id: int,
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
        db_gst.save_customer_details(customer_id, service_task_id,customer_data,user_id,db)

        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#--------Get Customer Details---------------
@router.get("/get_customers/{customer_id}")
def get_customer_details(
    customer_id: int,
    service_task_id: int,
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

    
    customer_details = db_gst.get_customer_details(db, customer_id,service_task_id,user_id)

    if customer_details is None:
        return []

    return customer_details


#----Save Stakeholder Details--------
@router.post("/save_stake_holder_master")
def save_stake_holder_master(
    request_data: StakeHolderMasterSchema,
    customer_id: int,
    service_task_id: int,
    stake_holder_type: Optional[str] = Query(None, enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']),
    is_authorized_signatory: Optional[str] =None ,  # Added parameter
    is_primary_authorized_signatory: Optional[str] =None,
    authorized_representative_type: Optional[str] = Query(None, enum=['GST_PRACTITIONER', 'OTHER']),
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
        result = db_gst.save_stakeholder_details(request_data, user_id, db, customer_id,service_task_id, stake_holder_type,is_authorized_signatory,is_primary_authorized_signatory,authorized_representative_type)
        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


#------ Get Stakeholder Details---------------------------------------------------------------------------
@router.get("/get_stakeholder_master")
def get_stakeholder_master(
    customer_id: Optional[int] = None,  # Optional customer_id
    service_task_id:  Optional[int] = None,
    stake_holder_type: Optional[str] = Query(None, enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']),  # Optional stakeholder_type
    search_value: Optional[str] = None, 
    is_authorized_signatory: Optional[str] = None,
    is_primary_authorized_signatory: Optional[str] = None, 
    authorized_representative_type: Optional[str] = Query(None, enum=['GST_PRACTITIONER', 'OTHER']),# Optional search value parameter
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
    stakeholder_details = db_gst.get_stakeholder_details(db,user_id, customer_id,service_task_id, stake_holder_type,is_authorized_signatory,is_primary_authorized_signatory,authorized_representative_type, search_value=search_value)

    if not stakeholder_details:
        return []

    return stakeholder_details

#-----------------Business Activity-----------------

@router.get("/get_business_activities")
def get_business_activities(
    activity_type_id: Optional[int] = Query(None),
    business_activity_master_id: Optional[int] = Query(None),
    
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get business activities based on the provided filters.

    - This endpoint retrieves business activities based on the given parameters. 
    - You can filter the results by `activity_type_id` and/or `business_activity_master_id`.

    Parameters:
    - **activity_type_id** (Optional[int]): 
       - The ID of the business activity type to filter results. 
       - When provided, only business activities associated with this ID will be returned. 
       - If no activities then return [].
        
    - **business_activity_master_id** (Optional[int]): 
       - The ID of the business activity master to filter results. 
       - When provided, this will return the specific business activity master data. 
       - If not provided, and `activity_type_id` is given, a list of unique business activities will be returned.
       - If no activities then return [].
    
    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    return db_gst.fetch_business_activities(db, activity_type_id, business_activity_master_id,user_id)

#--------Save Business Place--------------
@router.post("/save_business_place")
def save_business_place_details(
    id:int,
    customer_id: int,
    service_task_id: int,
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
        result = db_gst.save_business_place(customer_id,service_task_id,type,business_data, db,user_id,id)
        return {"success": True, "message": result["message"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


#--------- Get Business Place-----------------
@router.get("/get_business_place")
def get_business_place(
    customer_id: int,
    service_task_id: int,
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
    
    return db_gst.get_business_place(customer_id,service_task_id, type, db,user_id)
#-----------------Hsn Sac Data---------------------------------------------------------------------------

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



#---------Goods Commodities Supply Details--------------------------------------------------------------------
@router.post("/save_goods_commodities")
def save_goods_commodities(
    
    customer_id: int,
    service_task_id: int,
    details: List[CustomerGoodsCommoditiesSupplyDetailsSchema],  
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
        return db_gst.save_goods_commodities_details(customer_id,service_task_id, details, db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#-------------- Hsn Commodities----------------
#-----------------------------------------------------------------------------------------------------------------

@router.get("/get_hsn_commodities/{customer_id}")
def get_hsn_commodities(customer_id: int, 
                        service_task_id: int,
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
    commodities = db_gst.get_hsn_commodities_by_customer_id(customer_id,service_task_id, user_id, db)
    return commodities

#-------------Gst State Specific Information---------------
@router.post("/save_gst_state_specific_information/{id}")
def save_gst_state_specific_information(
    id: int,
    customer_id: int,
    service_task_id: int,
    data: CustomerGstStateSpecificInformationSchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - Save or update GST state-specific information.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    return db_gst.save_customer_gst_state_specific_information(id, customer_id,service_task_id, data, db, user_id)

#--------Gst State Specific Information
@router.get("/get_gst_state_specific_information/{customer_id}", 
            response_model=List[CustomerGstStateSpecificInformationSchemaGet]
            )
def get_gst_state_specific_information(
    customer_id: int,
    service_task_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - Retrieve GST state-specific information for a given customer ID.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  

    gst_state_info = db_gst.get_gst_state_specific_information_by_customer_id(customer_id, service_task_id,db,user_id)

    if not gst_state_info:
        return []

    return gst_state_info



#-----------------------------------------------------------------------------------------------------------------


#----jurisdiction
@router.get("/range_details/{pin}/", response_model=List[RangeDetailsSchema])
async def get_range_details(pin: str, 
                            db: Session = Depends(get_db),
                            token: str = Depends(oauth2.oauth2_scheme)
                            ):
    
    """
    - Get Range,Division,Commissionerate,Zone by Pincode
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id") 
    details = db_gst.get_details_by_pin(db, pin,user_id)
    if details:
        return details  # Return the list directly
    else:
        return []
    
#----------------------------------------------------------------------------------------------------------
@router.delete("/delete_gst_registration_record")
def delete_gst_registration_record(
    customer_id:int,
    service_task_id: int,
    stakeholder_id: int = None,
    business_place_id: int = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - Deletes a stakeholder or business place based on the provided ID.
    - Either `stakeholder_id` or `business_place_id` must be provided.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    try:
        return db_gst.delete_gst_registration_record(db,user_id,customer_id,service_task_id,stakeholder_id, business_place_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


