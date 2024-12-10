

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

#----------------------------Amendment-----------------------------------------------------------------------------


@router.post("/duplicate_customer")
def duplicate_customer(customer_id: int, 
                       service_task_id: int,
                       db: Session = Depends(get_db),
                       token: str = Depends(oauth2.oauth2_scheme)):
    """
    Duplicates customer data if certain conditions are met.

    Parameters:
    - customer_id (int): ID of the customer to be duplicated.
    - service_task_id (int): ID of the service task.
    - db (Session): Database session.
    - token (str): Authentication token.

    Returns:
    - JSON response with success status and message.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  

    result = db_gst.duplicate_customer_data(db, customer_id, service_task_id, user_id)

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    
    return {"success": True, "message": "Saved successfully", "id": result["id"]}


#------------------------------------------------------------------------------------------------------------


from typing import Optional

# @router.get("/get_amended_customer_details/{id}", response_model=Optional[CustomerDuplicateSchemaForGet])
# def get_customer(id: int,
#                  db: Session = Depends(get_db),
#                  token: str = Depends(oauth2.oauth2_scheme)):

#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")

#     # Query to join CustomerMaster with CustomerAmendmentHistory
#     query = db.query(CustomerMaster, CustomerAmendmentHistory).join(
#         CustomerAmendmentHistory, CustomerMaster.id == CustomerAmendmentHistory.amendment_id, isouter=True
#     ).filter(
#         CustomerMaster.id == id,
#         CustomerMaster.is_deleted == 'no'
#     )
    
#     # Fetch data
#     result = query.first()

#     if not result:
#         return None  # This will return a 200 response with `null` as the body in JSON format

#     # Unpacking the result tuple
#     customer_master, amendment_history = result

#     # Prepare the response data to match the schema
#     response_data = CustomerDuplicateSchemaForGet(
#         id=customer_master.id,
#         customer_id=customer_master.customer_id,
#         customer_number=customer_master.customer_number,
#         legal_name=customer_master.legal_name,
#         customer_name=customer_master.customer_name,
#         pan_number=customer_master.pan_number,
#         pan_creation_date=customer_master.pan_creation_date,
#         tan_number=customer_master.tan_number,
#         passport_number=customer_master.passport_number,
#         tin_number=customer_master.tin_number,
#         authorized_signatory_name_as_in_pan=customer_master.authorized_signatory_name_as_in_pan,
#         authorized_signatory_pan_number=customer_master.authorized_signatory_pan_number,
#         email_address=customer_master.email_address,
#         mobile_number=customer_master.mobile_number,
#         constitution_id=customer_master.constitution_id,
#         state_id=customer_master.state_id,
#         district_id=customer_master.district_id,
#         is_mother_customer=customer_master.is_mother_customer,
#         is_amendment=customer_master.is_amendment,
#         amendment_date=customer_master.amendment_date,
#         amendment_reason=customer_master.amendment_reason,
#         amendment_status=customer_master.amendment_status,
#         amendment_history=customer_master.amendment_history,
#         effective_from_date=customer_master.effective_from_date,
#         effective_to_date=customer_master.effective_to_date,
#         has_authorized_signatory=customer_master.has_authorized_signatory,
#         has_authorized_representative=customer_master.has_authorized_representative,
#         created_by=customer_master.created_by,
#         created_on=customer_master.created_on,
#         modified_by=customer_master.modified_by,
#         modified_on=customer_master.modified_on,
#         is_deleted=customer_master.is_deleted,
#         deleted_by=customer_master.deleted_by,
#         deleted_on=customer_master.deleted_on,
#         amendment_request_date=amendment_history.amendment_request_date if amendment_history else None,
#         amendment_remarks=amendment_history.amendment_remarks if amendment_history else None
#     )
    
#     # Return the validated response
#     return response_data



@router.get("/get_amended_customer_details", response_model=Optional[CustomerDuplicateSchemaForGet])
def get_customer(
    id: int, 
    service_task_id: Optional[int] = None,  
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    # Query to join CustomerMaster, CustomerAmendmentHistory, app_business_constitution, app_states, and app_districts
    query = db.query(
        CustomerMaster,
        CustomerAmendmentHistory,
        AppBusinessConstitution.business_constitution_name.label("business_constitution_name"),
        StateDB.state_name.label("state_name"),
        DistrictDB.district_name.label("district_name")
    ).join(
        CustomerAmendmentHistory, CustomerMaster.id == CustomerAmendmentHistory.amendment_id, isouter=True
    ).join(
        AppBusinessConstitution, CustomerMaster.constitution_id == AppBusinessConstitution.id, isouter=True
    ).join(
        StateDB, CustomerMaster.state_id == StateDB.id, isouter=True
    ).join(
        DistrictDB, CustomerMaster.district_id == DistrictDB.id, isouter=True
    ).filter(
        CustomerMaster.id == id,
        CustomerMaster.is_deleted == 'no'
    )

    if service_task_id is not None:
        query = query.filter(CustomerMaster.service_task_id == service_task_id)

    # Fetch data
    result = query.first()

    if not result:
        return None  # This will return a 200 response with `null` as the body in JSON format

    # Unpacking the result tuple
    customer_master, amendment_history, business_constitution_name, state_name, district_name = result

    # Prepare the response data to match the schema
    response_data = CustomerDuplicateSchemaForGet(
        id=customer_master.id,
        customer_id=customer_master.customer_id,
        customer_number=customer_master.customer_number,
        legal_name=customer_master.legal_name,
        customer_name=customer_master.customer_name,
        service_task_id=customer_master.service_task_id,
        
        pan_number=customer_master.pan_number,
        pan_creation_date=customer_master.pan_creation_date,
        tan_number=customer_master.tan_number,
        passport_number=customer_master.passport_number,
        tin_number=customer_master.tin_number,
        authorized_signatory_name_as_in_pan=customer_master.authorized_signatory_name_as_in_pan,
        authorized_signatory_pan_number=customer_master.authorized_signatory_pan_number,
        email_address=customer_master.email_address,
        mobile_number=customer_master.mobile_number,
        constitution_id=customer_master.constitution_id,
        business_constitution_name=business_constitution_name,
        state_id=customer_master.state_id,
        state_name=state_name,
        district_id=customer_master.district_id,
        district_name=district_name,
        is_mother_customer=customer_master.is_mother_customer,
        is_amendment=customer_master.is_amendment,
        amendment_date=customer_master.amendment_date,
        amendment_reason=customer_master.amendment_reason,
        amendment_status=customer_master.amendment_status,
        amendment_history=customer_master.amendment_history,
        effective_from_date=customer_master.effective_from_date,
        effective_to_date=customer_master.effective_to_date,
        has_authorized_signatory=customer_master.has_authorized_signatory,
        has_authorized_representative=customer_master.has_authorized_representative,
        amendment_request_date=amendment_history.amendment_request_date if amendment_history else None,
        amendment_remarks=amendment_history.amendment_remarks if amendment_history else None,
        created_by=customer_master.created_by,
        created_on=customer_master.created_on,
        modified_by=customer_master.modified_by,
        modified_on=customer_master.modified_on,
        is_deleted=customer_master.is_deleted,
        deleted_by=customer_master.deleted_by,
        deleted_on=customer_master.deleted_on,
      
    )

    # Return the validated response
    return response_data

#-------------------------------------------------------------------------------------------------------------

@router.post("/save_amended_data")
def save_amendment(
    id: int,
    model_name: str,
    field_name: str,
    new_value,
    date: datetime = datetime.now(),
    # date: datetime =datetime.now().date()
    remarks: str = "",
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    if not field_name:
        raise HTTPException(status_code=400, detail="field_name cannot be null or empty.")
    
    response = db_gst.save_amended_data(db, id, model_name, field_name, new_value, date, remarks)
    return response

#-------------------------------------------------------------------------------------------------------------


# @router.get("/get_active_trade_names")
# def get_active_trade_names(customer_id: int, 
#                            db: Session = Depends(get_db),
#                            token: str = Depends(oauth2.oauth2_scheme)):
    
#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")

#     active_trade_names = db.execute(text("""
#         SELECT *
#         FROM customer_additional_trade_name 
#         WHERE customer_id = :customer_id
#         AND is_deleted = 'no'
#         AND (is_amendment = 'yes' OR amended_parent_id NOT IN (
#             SELECT amended_parent_id
#             FROM customer_additional_trade_name
#             WHERE is_amendment = 'yes'
#         ))
#         ORDER BY id;
#     """), {'customer_id': customer_id}).fetchall()

#     if not active_trade_names:
#         raise HTTPException(status_code=404, detail="No active trade names found for the specified customer")

#     return {
#         "success": True,
#         "active_trade_names": [
#             {
#                 "id": trade_name.id,
#                 "amended_parent_id": trade_name.amended_parent_id,
#                 "service_task_id":trade_name.service_task,
#                 "additional_trade_name": trade_name.additional_trade_name,
#                 "is_amendment": trade_name.is_amendment,
#                 "amendment_date": trade_name.amendment_date,
#                 "amendment_reason": trade_name.amendment_reason,
#                 "amendment_status": trade_name.amendment_status,
#                 "effective_from_date": trade_name.effective_from_date,
#                 "effective_to_date": trade_name.effective_to_date,
#                 "created_by": trade_name.created_by,
#                 "created_on": trade_name.created_on,
#                 "modified_by": trade_name.modified_by,
#                 "modified_on": trade_name.modified_on
#             } for trade_name in active_trade_names
#         ]
#     }


@router.get("/get_active_trade_names")
def get_active_trade_names(customer_id: int, 
                           service_task_id: int,
                           db: Session = Depends(get_db),
                           token: str = Depends(oauth2.oauth2_scheme)):
    
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    active_trade_names = db.execute(text("""
        SELECT *
        FROM customer_additional_trade_name 
        WHERE customer_id = :customer_id
        AND service_task_id = :service_task_id
        AND is_deleted = 'no'
        AND (is_amendment = 'yes' OR amended_parent_id NOT IN (
            SELECT amended_parent_id
            FROM customer_additional_trade_name
            WHERE is_amendment = 'yes'
        ))
        ORDER BY id;
    """), {'customer_id': customer_id, 'service_task_id': service_task_id}).fetchall()

    if not active_trade_names:
        raise HTTPException(status_code=404, detail="No active trade names found for the specified customer and service task")

    return {
        "success": True,
        "active_trade_names": [
            {
                "id": trade_name.id,
                "amended_parent_id": trade_name.amended_parent_id,
                "service_task_id": trade_name.service_task_id, 
                "additional_trade_name": trade_name.additional_trade_name,
                "is_amendment": trade_name.is_amendment,
                "amendment_date": trade_name.amendment_date,
                "amendment_reason": trade_name.amendment_reason,
                "amendment_status": trade_name.amendment_status,
                "effective_from_date": trade_name.effective_from_date,
                "effective_to_date": trade_name.effective_to_date,
                "created_by": trade_name.created_by,
                "created_on": trade_name.created_on,
                "modified_by": trade_name.modified_by,
                "modified_on": trade_name.modified_on
            } for trade_name in active_trade_names
        ]
    }

#-------------------------------------------------------------------------------------------------------------



@router.post("/amend_additional_trade_names")
def amend_additional_trade_names(
    id: int,
    service_task_id: int,
    amendments: List[AdditionalTradeNameAmendment],
    action: AmendmentAction,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
):
    """
        Amend additional trade names for a customer.

        Parameters:
            id (int): If action is ADDED, provide the customer_id. 
            service_task_id (int): The ID of the service task.
            amendments (List[AdditionalTradeNameAmendment]): A list of amendments containing trade name details.
            action (AmendmentAction): The type of amendment. Possible values: ADDED, EDITED, DELETED.
            db (Session): Database session.
            token (str): Authentication token.

        Returns:
            dict: Response indicating the success or failure of the amendment process.

        Example:
        {
            "id": 1001,  # customer_id for ADD action, 
            "service_task_id": 100,
            "amendments": [
                { 
                    "id":0
                    "new_trade_name": "New Trade Name",  # The new or updated trade name
                    "request_date": "2024-11-08T04:30:45.156Z",  # The date of the request
                    "remarks": "Adding new trade name"  # Any remarks for the amendment
                },
                { 
                    "id":0
                    "new_trade_name": "New Trade Name1",  # The new or updated trade name
                    "request_date": "2024-11-08T04:30:45.156Z",  # The date of the request
                    "remarks": "Adding new trade name"  # Any remarks for the amendment
                },
                { 
                    "id":10
                    "new_trade_name": "New Trade Name1 updated",  # The new or updated trade name
                    "request_date": "2024-11-08T04:30:45.156Z",  # The date of the request
                    "remarks": "Adding new trade name"  # Any remarks for the amendment
                }
            ],
            
        }
        """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    # Authenticate user and get user_id
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    # Call the database operation
    response = db_gst.amend_additional_trade_names_in_db(
        db, id, service_task_id, amendments, user_id, action
    )
    return response







@router.delete("/delete_amendment_business_place/{id}", response_model=dict)
def delete_amendment_business_place_endpoint(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
) -> Any:
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    # Assume there's a function to extract user info from the token
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    response = db_gst.delete_amendment_business_place(db, id, user_id)
    if not response["success"]:
        raise HTTPException(status_code=400, detail=response["message"])

    return response

#---------------------------------------------------------------------------------------------------------





#---------------------------------------------------------------------------------------------

# @router.get("/get_active_stake_holders")
# def get_active_stake_holders(customer_id: int, 
#                              db: Session = Depends(get_db),
#                              token: str = Depends(oauth2.oauth2_scheme)):
#     """
#     Get Active Stake Holders

#     This endpoint retrieves active stakeholders for a given customer.

#     Parameters:
#     - customer_id: The ID of the customer.

#     Returns:
#     - JSON response with active stakeholders.
#     """
#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")

#     active_stake_holders = db.execute(text("""
#         SELECT *
#         FROM customer_stake_holders
#         WHERE customer_id = :customer_id
#         AND is_deleted = 'no'
#         AND (is_amendment = 'yes' OR amended_parent_id NOT IN (
#             SELECT amended_parent_id
#             FROM customer_stake_holders
#             WHERE is_amendment = 'yes'
#         ))
#         ORDER BY id;
#     """), {'customer_id': customer_id}).fetchall()

#     if not active_stake_holders:
#         raise HTTPException(status_code=404, detail="No active stakeholders found for the specified customer")

#     return {
#         "success": True,
#         "active_stake_holders": [
#             {
#                 "id": stake_holder.id,
#                 "amended_parent_id": stake_holder.amended_parent_id,
#                 "customer_id": stake_holder.customer_id,
#                 "stake_holder_master_id": stake_holder.stake_holder_master_id,
#                 "stake_holder_type": stake_holder.stake_holder_type,
#                 "designation_id": stake_holder.designation_id,
#                 "official_position_id": stake_holder.official_position_id,
#                 "is_authorized_signatory": stake_holder.is_authorized_signatory,
#                 "contact_details_id": stake_holder.contact_details_id,
#                 "present_address_id": stake_holder.present_address_id,
#                 "permanent_address_id": stake_holder.permanent_address_id,
#                 "residential_address_id": stake_holder.residential_address_id,
#                 "official_address_id": stake_holder.official_address_id,
#                 "official_mobile_number": stake_holder.official_mobile_number,
#                 "official_email_address": stake_holder.official_email_address,
#                 "is_amendment": stake_holder.is_amendment,
#                 "amendment_date": stake_holder.amendment_date,
#                 "amendment_reason": stake_holder.amendment_reason,
#                 "amendment_status": stake_holder.amendment_status,
#                 "effective_from_date": stake_holder.effective_from_date,
#                 "effective_to_date": stake_holder.effective_to_date,
#                 "created_by": stake_holder.created_by,
#                 "created_on": stake_holder.created_on,
#                 "modified_by": stake_holder.modified_by,
#                 "modified_on": stake_holder.modified_on,
#                 "is_deleted": stake_holder.is_deleted,
#                 "deleted_by": stake_holder.deleted_by,
#                 "deleted_on": stake_holder.deleted_on
#             } for stake_holder in active_stake_holders
#         ]
#     }

#------------------------------------------------------------------------------------------------

@router.post("/amend_stake_holders")
def amend_stake_holders(
    
    customer_id: int,
    service_task_id: int,
    action: AmendmentAction,
    request_data: Optional[AmmendStakeHolderMasterSchema] = None,
    amendment_details: Optional[AmendmentDetailsSchema] = None,
    id: Optional[int] = None,
    stakeholder_type: str = Query(..., enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Amend Stake Holders

    Parameters:
    - request_data: The stakeholder data to be added or amended.
    - customer_id: The ID of the customer.
    - id: If action is ADDED, provide the customer_id for the id field. Otherwise, provide the row_id of the record to be amended.
    - action: The type of amendment. Possible values: ADDED, DELETED.
    - stakeholder_type: The type of stakeholder.

    Returns:
    - JSON response with success status and message.


    {
  "amendment_details": {
    "reason": "marked for deletion",
    "date": "2024-11-16T05:38:22.572Z"
  }
}
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if action == AmendmentAction.ADDED:
        response = db_gst.add_stake_holder(db, customer_id,service_task_id, stakeholder_type, request_data, user_id)
    elif action == AmendmentAction.DELETED:
        response = db_gst.delete_stake_holder(db, id,amendment_details, action, user_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return response
#----------------------------------------------------------------------------------------------------------

# @router.get("/get_stakeholder_master_for_amndement/{customer_id}")
# def get_stakeholder_master(
#     customer_id: int,
#     service_task_id: int,
#     stakeholder_type: str = Query(..., enum=['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY', 'AUTHORIZED_REPRESENTATIVE']),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
#     """
#     Get the details of a stakeholder by their customer_id and type.

#     - customer_id (int): The ID of the customer.
#     - service_task_id (int): The ID of the service task.
#     - stakeholder_type (str): The type of stakeholder to filter by.
#     """
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")
    
#     # Print the input parameters for debugging
#     print(f"Received parameters: customer_id={customer_id}, service_task_id={service_task_id}, stakeholder_type={stakeholder_type}")

#     # Call your function to get stakeholder details
#     stakeholder_details = db_gst.get_stakeholder_master_for_amndement(db, customer_id, service_task_id, stakeholder_type, user_id)

#     if not stakeholder_details:
#         return []

#     return stakeholder_details


@router.get("/get_stakeholder_master_for_amndement/{customer_id}")
def get_stakeholder_master(
    customer_id: int,
    service_task_id:int,
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
    stakeholder_details = db_gst.get_stakeholder_master_for_amndement(db, customer_id, stakeholder_type,service_task_id,user_id)

    if not stakeholder_details:
        return []

    return stakeholder_details

#------------------------------------------------------------------------------------------------------------

@router.post("/amend_business_place")
def amend_business_place(customer_id: int, 
                         service_task_id: int,
                         amendment_details: CustomerBusinessPlaceFullAmendmentSchema,
                         action: AmendmentAction,
                         db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)):
    
    """
        Amend Business Place

        This endpoint is used to amend the details of a business place and its associated activities for a specified customer.

        Parameters:
        - **customer_id** (int): The ID of the customer whose business place is to be amended.
        - **service_task_id** (int): The ID of the service task associated with the amendment.
        - **amendment_details** (CustomerBusinessPlaceFullAmendmentSchema): The details of the amendment for the business place and nature of business.
        - **action** (AmendmentAction): The type of amendment. Possible values: ADDED, EDITED, DELETED.
        - **token** (str): The authentication token.

        Request Body Example:
        ```json
        {
            "business_place": [
                {
                    "pin_code": "110001",
                    "country_id": 1,
                    "state_id": 2,
                    "district_id": 3,
                    "taluk_id": 4,
                    "city_id": 5,
                    "post_office_id": 6,
                    "lsg_type_id": 7,
                    "lsg_id": 8,
                    "village_id": 9,
                    "locality": "Connaught Place",
                    "road_street_name": "Janpath Lane",
                    "premises_building_name": "Janpath Tower",
                    "building_flat_number": "101",
                    "floor_number": "1",
                    "landmark": "Near Palika Bazar",
                    "latitude": "28.6345",
                    "longitude": "77.2190",
                    "office_email_address": "office@example.com",
                    "office_mobile_number": "9876543210",
                    "office_phone_std_code": "011",
                    "office_phone_number": "12345678",
                    "office_fax_std_code": "011",
                    "office_fax_number": "87654321",
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Expansion of business"
                }
            ],
            "nature_of_business": [
                {
                    "business_activity_id": 1,
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Added new service offering"
                },
                {
                    "business_activity_id": 3,
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Added new service offering"
                },
                {
                    "business_activity_id": 2,
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Updated product range"
                }
            ]
        }
        ```

        Returns:
        - **200 OK**: Amendment saved successfully.
        - **401 Unauthorized**: Token is missing or invalid.
        - **400 Bad Request**: If there is an issue with saving the amendment.
        
        Example Response:
        ```json
        {
            "success": True,
            "message": "Amendment saved successfully",
            "id": 123
        }
        ```
        """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = db_gst.amend_business_place_data(db, customer_id,service_task_id, amendment_details, action, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"success": True, "message": "Amendment saved successfully", "id": result["id"]}


#-----------------------------------------------------------------------------------------------------


@router.get("/get_amended_business_place", response_model=List[CombinedSchema])
def get_amended_business_place(
    customer_id: Optional[int] = None, 
    service_task_id: Optional[int] = None,
    # business_place_id: Optional[int] = None, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        combined_data = db_gst.fetch_combined_data(db, customer_id,service_task_id)
        return combined_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#---------------------------------------------------------------------------------------------

# @router.post("/amended_additional_business_places")
# def amended_additional_business_places(
#     customer_id: int, 
#     amendment_details: CustomerBusinessPlaceFullAmendmentSchema,
#     action: AmendmentAction,
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")

#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")

#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     # Convert Pydantic model to dictionary
#     amendment_details_dict = amendment_details.dict()

#     result = db_gst.save_additional_business_places_and_activities(db, customer_id, amendment_details_dict, action, user_id)

#     if not result["success"]:
#         raise HTTPException(status_code=400, detail=result["message"])
    
#     return {"success": True, "message": "Amendment saved successfully", "id": result.get("id")}


@router.post("/amended_additional_business_places")
def amended_additional_business_places(
    customer_id: int, 
    service_task_id: int,  # Include service_task_id
    amendment_details: CustomerBusinessPlacesFullAmendmentSchema,
    action: AmendmentAction,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
            Amend Additional Business Places

            This endpoint is used to amend the details of additional business places and their associated activities for a specified customer.

            Parameters:
            - customer_id (int): The ID of the customer.
            - service_task_id (int): The ID of the service task.
            - amendment_details (CustomerBusinessPlacesFullAmendmentSchema): The details of the amendment for the business place and nature of business.
            - action (AmendmentAction): The type of amendment. Possible values: ADDED, EDITED, DELETED.
            - token (str): The authentication token.

            Returns:
            - JSON response with success status and message.

            {
        "business_place": [
            {
            "pin_code": "110001",
            "country_id": 1,
            "state_id": 2,
            "district_id": 3,
            "taluk_id": 4,
            "city_id": 5,
            "post_office_id": 6,
            "lsg_type_id": 7,
            "lsg_id": 8,
            "village_id": 9,
            "locality": "Connaught Place",
            "road_street_name": "Janpath Lane",
            "premises_building_name": "Janpath Tower",
            "building_flat_number": "101",
            "floor_number": "1",
            "landmark": "Near Palika Bazar",
            "latitude": "28.6345",
            "longitude": "77.2190",
            "office_email_address": "office@example.com",
            "office_mobile_number": "9876543210",
            "office_phone_std_code": "011",
            "office_phone_number": "12345678",
            "office_fax_std_code": "011",
            "office_fax_number": "87654321",
            "amendment_date": "2024-11-26",
            "amendment_reason": "Expansion of business",
            "nature_of_business": [
                {
                "business_activity_id": 1,
                "amendment_date": "2024-11-26",
                "amendment_reason": "Added new service offering"
                },
                {
                "business_activity_id": 2,
                "amendment_date": "2024-11-26",
                "amendment_reason": "Updated product range"
                }
            ]
            },
            {
            "pin_code": "560001",
            "country_id": 1,
            "state_id": 2,
            "district_id": 4,
            "taluk_id": 5,
            "city_id": 6,
            "post_office_id": 7,
            "lsg_type_id": 8,
            "lsg_id": 9,
            "village_id": 10,
            "locality": "MG Road",
            "road_street_name": "Brigade Road",
            "premises_building_name": "Brigade Tower",
            "building_flat_number": "201",
            "floor_number": "2",
            "landmark": "Opposite to Metro Station",
            "latitude": "12.9716",
            "longitude": "77.5946",
            "office_email_address": "branch@example.com",
            "office_mobile_number": "9876543200",
            "office_phone_std_code": "080",
            "office_phone_number": "23456789",
            "office_fax_std_code": "080",
            "office_fax_number": "87654320",
            "amendment_date": "2024-11-26",
            "amendment_reason": "New branch setup",
            "nature_of_business": [
                {
                "business_activity_id": 3,
                "amendment_date": "2024-11-26",
                "amendment_reason": "New activity for branch"
                },
                {
                "business_activity_id": 4,
                "amendment_date": "2024-11-26",
                "amendment_reason": "Expanded service offerings"
                }
            ]
            }
        ]
        }

   """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Convert Pydantic model to dictionary
    amendment_details_dict = amendment_details.dict()

    result = db_gst.save_additional_business_places_and_activities(db, customer_id, service_task_id, amendment_details_dict, action, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"success": True, "message": "Amendment saved successfully", "id": result.get("id")}

#--------------------------------------------------------------------------------------------------------------

@router.get("/get_additional_business_places_and_activities")
def get_business_places_and_activities(customer_id: int, service_task_id: int, db: Session = Depends(get_db)):
    try:
        # Fetch all business places for the given customer and service task
        business_places = db.query(CustomerBusinessPlace).filter_by(
            customer_id=customer_id,
            service_task_id=service_task_id
        ).all()

        if not business_places:
            raise HTTPException(status_code=404, detail="Business places not found")

        # Prepare the result dictionary
        result = {
            "customer_id": customer_id,
            "service_task_id": service_task_id,
            "business_places": []
        }

        # Iterate through each business place and fetch their activities
        for business_place in business_places:
            business_place_data = {
                "business_place_id": business_place.id,
                "pin_code": business_place.pin_code,
                "country_id": business_place.country_id,
                "state_id": business_place.state_id,
                "district_id": business_place.district_id,
                "taluk_id": business_place.taluk_id,
                "city_id": business_place.city_id,
                "post_office_id": business_place.post_office_id,
                "lsg_type_id": business_place.lsg_type_id,
                "lsg_id": business_place.lsg_id,
                "village_id": business_place.village_id,
                "locality": business_place.locality,
                "road_street_name": business_place.road_street_name,
                "premises_building_name": business_place.premises_building_name,
                "building_flat_number": business_place.building_flat_number,
                "floor_number": business_place.floor_number,
                "landmark": business_place.landmark,
                "latitude": business_place.latitude,
                "longitude": business_place.longitude,
                "office_email_address": business_place.office_email_address,
                "office_mobile_number": business_place.office_mobile_number,
                "office_phone_std_code": business_place.office_phone_std_code,
                "office_phone_number": business_place.office_phone_number,
                "office_fax_std_code": business_place.office_fax_std_code,
                "office_fax_number": business_place.office_fax_number,
                "amendment_date": business_place.amendment_date,
                "amendment_reason": business_place.amendment_reason,
                "nature_of_business": []
            }

            # Fetch all activities for the current business place
            activities = db.query(CustomerBusinessPlaceActivity).filter_by(
                business_place_id=business_place.id
            ).all()

            # Add activities to the business place data
            for activity in activities:
                activity_data = {
                    "business_activity_id": activity.business_activity_id,
                    "amendment_date": activity.amendment_date,
                    "amendment_reason": activity.amendment_reason,
                    "amendment_status": activity.amendment_status,
                    "amendment_action": activity.amendment_action,
                    "is_deleted": activity.is_deleted
                }
                business_place_data["nature_of_business"].append(activity_data)

            result["business_places"].append(business_place_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch business places and activities: {str(e)}")

#--------------------------


@router.post("/amend_business_place")
def amend_business_place(customer_id: int, 
                         service_task_id: int,
                         amendment_details: CustomerBusinessPlaceFullAmendmentSchema,
                         action: AmendmentAction,
                         db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)):
    
    """
        Amend Business Place

        This endpoint is used to amend the details of a business place and its associated activities for a specified customer.

        Parameters:
        - **customer_id** (int): The ID of the customer whose business place is to be amended.
        - **service_task_id** (int): The ID of the service task associated with the amendment.
        - **amendment_details** (CustomerBusinessPlaceFullAmendmentSchema): The details of the amendment for the business place and nature of business.
        - **action** (AmendmentAction): The type of amendment. Possible values: ADDED, EDITED, DELETED.
        - **token** (str): The authentication token.

        Request Body Example:
        ```json
        {
            "business_place": [
                {
                    "pin_code": "110001",
                    "country_id": 1,
                    "state_id": 2,
                    "district_id": 3,
                    "taluk_id": 4,
                    "city_id": 5,
                    "post_office_id": 6,
                    "lsg_type_id": 7,
                    "lsg_id": 8,
                    "village_id": 9,
                    "locality": "Connaught Place",
                    "road_street_name": "Janpath Lane",
                    "premises_building_name": "Janpath Tower",
                    "building_flat_number": "101",
                    "floor_number": "1",
                    "landmark": "Near Palika Bazar",
                    "latitude": "28.6345",
                    "longitude": "77.2190",
                    "office_email_address": "office@example.com",
                    "office_mobile_number": "9876543210",
                    "office_phone_std_code": "011",
                    "office_phone_number": "12345678",
                    "office_fax_std_code": "011",
                    "office_fax_number": "87654321",
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Expansion of business"
                }
            ],
            "nature_of_business": [
                {
                    "business_activity_id": 1,
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Added new service offering"
                },
                {
                    "business_activity_id": 3,
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Added new service offering"
                },
                {
                    "business_activity_id": 2,
                    "amendment_date": "2024-11-26",
                    "amendment_reason": "Updated product range"
                }
            ]
        }
        ```

        Returns:
        - **200 OK**: Amendment saved successfully.
        - **401 Unauthorized**: Token is missing or invalid.
        - **400 Bad Request**: If there is an issue with saving the amendment.
        
        Example Response:
        ```json
        {
            "success": True,
            "message": "Amendment saved successfully",
            "id": 123
        }
        ```
        """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = db_gst.amend_business_place_data(db, customer_id,service_task_id, amendment_details, action, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"success": True, "message": "Amendment saved successfully", "id": result["id"]}




