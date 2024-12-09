
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from sqlalchemy import and_, or_, select, text

from caerp_db.common.models import BusinessActivity, BusinessActivityMaster, BusinessActivityType, DistrictDB, StateDB
from caerp_db.office.models import AppBusinessConstitution
from caerp_db.mother_customer import db_mother_customer
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerAmendmentHistory, CustomerBusinessPlace, CustomerBusinessPlaceActivity, CustomerMaster, GstViewRange
from caerp_schema.mother_customer.mother_customer_schema import MotherCustomerRequestSchema
from caerp_schema.services.gst_schema import AdditionalTradeNameAmendment, AmendmentDetailsSchema, AmmendStakeHolderMasterSchema, BusinessData, BusinessDetailsSchema, CombinedSchema, CustomerAmendmentSchema, CustomerBusinessPlaceAmendmentSchema, CustomerBusinessPlaceFullAmendmentSchema, CustomerBusinessPlacesFullAmendmentSchema, CustomerDuplicateSchemaForGet, CustomerGoodsCommoditiesSupplyDetailsSchema, CustomerGstStateSpecificInformationSchema, CustomerGstStateSpecificInformationSchemaGet, CustomerRequestSchema, RangeDetailsSchema, StakeHolderMasterSchema, SuccessResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, Depends, HTTPException, Header
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import List, Optional
from datetime import date, datetime
from caerp_db.database import  get_db
from caerp_auth.authentication import authenticate_user


router = APIRouter(
    prefix="/gst",
    tags=['Mother Customer']
)




#--------------Save Mother Customer Details----------------

@router.post("/save_mother_customer_details")
def save_mother_customer_details(
    mother_customer_data: MotherCustomerRequestSchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save or update mother customer details. 
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    # Extract user and mother customer ID from the token
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    if not mother_customer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mother customer ID not found in token")

    try:
        # Update customer details
        db_mother_customer.save_mother_customer_details(mother_customer_id, mother_customer_data, user_id, db)
        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
       db.rollback()
       print(f"Error: {str(e)}")  # Log the error message for debugging
       raise HTTPException(status_code=500, detail=str(e))

#-------------------------------------------------------------------------------------------------------

@router.get("/get_mother_customer_details")
def get_mother_customer_details(
    
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Retrieve details of a specific customer based on their ID.

    - mother_customer_id =1
    - mother_customer_id = auth_info.get("mother_customer_id")
    - param token: OAuth2 token for authentication
    - return: Customer details or raises an HTTPException if not found
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    if not mother_customer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mother customer ID not found in token")

    
    mother_customer_details = db_mother_customer.get_customer_details(db,mother_customer_id,user_id)

    if mother_customer_details is None:
        return []

    return mother_customer_details


#--------------------

@router.post("/save_mother_customer_stake_holder_master")
def save_mother_customer_stake_holder_master(
    request_data: StakeHolderMasterSchema,
    stake_holder_type: Optional[str] = Query(None, enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']),
    is_authorized_signatory: Optional[str] =None ,  # Added parameter
    is_primary_authorized_signatory: Optional[str] =None,
    authorized_representative_type: Optional[str] = Query(None, enum=['GST_PRACTITIONER', 'OTHER']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - mother_customer_id =1
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
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    try:
        # Pass customer_id, address_type, and stakeholder_type to the save function
        result = db_mother_customer.save_mother_customer_stakeholder_details(request_data, user_id, db, mother_customer_id, stake_holder_type,is_authorized_signatory,is_primary_authorized_signatory,authorized_representative_type)
        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    



#---------------------------
@router.get("/get_mother_customer_stakeholder_master")
def get_mother_customer_stakeholder_master(
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

    - mother_customer_id =1
    - stakeholder_type (str): The type of stakeholder to filter by.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1

    # Call your function to get stakeholder details
    stakeholder_details = db_mother_customer.get_mother_customer_stakeholder_details(db,user_id,mother_customer_id,stake_holder_type,is_authorized_signatory,is_primary_authorized_signatory,authorized_representative_type, search_value=search_value)

    if not stakeholder_details:
        return []

    return stakeholder_details
#---------------------------------------
@router.post("/save_mother_customer_business_place")
def save_mother_customer_business_place(
    id:int,
    business_data: BusinessData,
    type: str = Query(..., enum=['PRINCIPAL_PLACE_ADDRESS', 'ADDITIONAL_PLACE']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - mother_customer_id =1
    - Save business data, including business places and activities, associated with a customer.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    try:
        result = db_mother_customer.save_mother_customer_business_place(mother_customer_id,business_data, db,user_id,id)
        return {"success": True, "message": result["message"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#------------------------------


@router.get("/get_mother_customer_business_place")
def get_mother_customer_business_place(
    type: str = Query(..., enum=['PRINCIPAL_PLACE_ADDRESS', 'ADDITIONAL_PLACE']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
                          ):
    """
    - mother_customer_id =1
    - Retrieve business data based on customer_id and type.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    return db_mother_customer.get_mother_customer_business_place(mother_customer_id, type, db,user_id)

#-----------------------------------------

@router.post("/save_mother_customer_goods_commodities")
def save_mother_customer_goods_commodities(
    details: List[CustomerGoodsCommoditiesSupplyDetailsSchema],  
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - mother_customer_id =1
    - Save Goods Commodities
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    try:
        return db_mother_customer.save_mother_customer_goods_commodities_details(mother_customer_id,details, db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#-------------- Hsn Commodities----------------
#-----------------------------------------------------------------------------------------------------------------
@router.get("/get_mother_customer_hsn_commodities")
def get_mother_customer_hsn_commodities(
                         db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)
                         ):
    """
    - mother_customer_id =1
    - Retrieve HSN/SAC commodities details for a given customer ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  # Retrieve user_id from token
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    # Call the function to get commodities, passing the user_id
    commodities = db_mother_customer.get_mother_customer_hsn_commodities(mother_customer_id,user_id, db)
    return commodities
#--------------------------

@router.post("/save_mother_customer_gst_state_specific_information")
def save_mother_customer_gst_state_specific_information(
    id: int,
    data: CustomerGstStateSpecificInformationSchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - mother_customer_id =1
    - Save or update GST state-specific information.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    return db_mother_customer.save_mother_customer_gst_state_specific_information(id, mother_customer_id,data, db, user_id)

#-------------Gst State Specific Information---------------
@router.post("/save_mother_customer_gst_state_specific_information/{id}")
def save_mother_customer_gst_state_specific_information(
    id: int,
    data: CustomerGstStateSpecificInformationSchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    - mother_customer_id =1
    - Save or update GST state-specific information.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    return db_mother_customer.save_mother_customer_gst_state_specific_information(id, mother_customer_id,data, db, user_id)

#--------Gst State Specific Information
@router.get("/get_mother_customer_gst_state_specific_information", 
            response_model=List[CustomerGstStateSpecificInformationSchemaGet]
            )
def get_mother_customer_gst_state_specific_information(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
     - mother_customer_id =1
    - Retrieve GST state-specific information for a given customer ID.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    gst_state_info = db_mother_customer.get_mother_customer_gst_state_specific_information(mother_customer_id,db,user_id)

    if not gst_state_info:
        return []

    return gst_state_info


#----------------delete_mother_customer_gst_registration_record

@router.delete("/delete_mother_customer_gst_registration_record")
def delete_mother_customer_gst_registration_record(
    stakeholder_id: int = None,
    business_place_id: int = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
     - mother_customer_id =1
    - Deletes a stakeholder or business place based on the provided ID.
    - Either `stakeholder_id` or `business_place_id` must be provided.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    mother_customer_id = auth_info.get("mother_customer_id")
    # mother_customer_id =1
    try:
        return db_mother_customer.delete_mother_customer_gst_registration_record(db,user_id,mother_customer_id,stakeholder_id, business_place_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
