

from typing import List, Union
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from sqlalchemy import and_, or_, select, text
from caerp_constants.caerp_constants import AmendmentAction
from caerp_db.common.models import BusinessActivity, BusinessActivityMaster, BusinessActivityType
from caerp_db.services import db_gst
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerAmendmentHistory, CustomerMaster, GstViewRange
from caerp_schema.services.gst_schema import AdditionalTradeNameAmendment, BusinessData, BusinessDetailsSchema, CustomerAmendmentSchema, CustomerDuplicateSchemaForGet, CustomerGoodsCommoditiesSupplyDetailsSchema, CustomerGstStateSpecificInformationSchema, CustomerGstStateSpecificInformationSchemaGet, CustomerRequestSchema, RangeDetailsSchema, StakeHolderMasterSchema
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

    

#--------Get Customer Details---------------
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


#----Save Stakeholder Details--------
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

#------ Get Stakeholder Details-----------------
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
    

#--------- Get Business Place-----------------
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



#-----------------Hsn Sac Data---------------

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



#---------Goods Commodities Supply Details-----------------

@router.post("/save_goods_commodities")
def save_goods_commodities(
    
    customer_id: int,
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
        return db_gst.save_goods_commodities_details(customer_id, details, db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#-------------- Hsn Commodities----------------

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

#-------------Gst State Specific Information---------------
@router.post("/save_gst_state_specific_information/{id}")
def save_gst_state_specific_information(
    id: int,
    customer_id: int,
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

    return db_gst.save_customer_gst_state_specific_information(id, customer_id, data, db, user_id)

#--------Gst State Specific Information
@router.get("/get_gst_state_specific_information/{customer_id}", 
            response_model=List[CustomerGstStateSpecificInformationSchemaGet]
            )
def get_gst_state_specific_information(
    customer_id: int,
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

    gst_state_info = db_gst.get_gst_state_specific_information_by_customer_id(customer_id, db,user_id)

    if not gst_state_info:
        return []

    return gst_state_info




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
        return db_gst.delete_gst_registration_record(db,user_id,customer_id,stakeholder_id, business_place_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------Amendment-----------------------------------------------------------------------------
@router.post("/duplicate_customer")
def duplicate_customer(customer_id: int, 
                       db: Session = Depends(get_db),
                       token: str = Depends(oauth2.oauth2_scheme)):
    
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  

    result = db_gst.duplicate_customer_data(db, customer_id,user_id)

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    
    return {"success": True, "message": "Saved successfully", "id": result["id"]}

#------------------------------------------------------------------------------------------------------------


# @router.get("/get_amended_customer_details/{id}", response_model=CustomerDuplicateSchemaForGet)
# def get_customer(id: int,
#                  db: Session = Depends(get_db),
#                  token: str = Depends(oauth2.oauth2_scheme)):

#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")

#     customer = db.query(CustomerMaster).filter(
#         and_(
#             CustomerMaster.id == id,
#             CustomerMaster.is_amendment == 'yes',
#             CustomerMaster.is_deleted == 'no'
#         )
#     ).first()

#     if not customer:
#         # Returning None when no customer is found
#         # raise HTTPException(status_code=404, detail="Id not found")
#         return None

#     # Return the customer data
#     return customer

from typing import Optional

@router.get("/get_amended_customer_details/{id}", response_model=Optional[CustomerDuplicateSchemaForGet])
def get_customer(id: int,
                 db: Session = Depends(get_db),
                 token: str = Depends(oauth2.oauth2_scheme)):

    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    customer = db.query(CustomerMaster).filter(
        and_(
            CustomerMaster.id == id,
            CustomerMaster.is_amendment == 'yes',
            CustomerMaster.is_deleted == 'no'
        )
    ).first()

    if not customer:
        return None  # This will return a 200 response with `null` as the body in JSON format

    # Return the customer data
    return customer



#--------------------------------------------------------------------------------------------------------------

# @router.post("/amend_legal_name")
# def amend_legal_name(data: CustomerAmendmentSchema, 
#                      customer_id: int,
#                      db: Session = Depends(get_db),
#                      token: str = Depends(oauth2.oauth2_scheme)):
    
#     # Validate token
#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")
    
#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")  

#     # Fetch the original customer data
#     customer = db.query(CustomerMaster).filter(
#         CustomerMaster.customer_id == customer_id,
#         CustomerMaster.is_amendment == 'yes'
#     ).first()
    
#     if not customer:
#         raise HTTPException(status_code=404, detail="Customer not found or amendment not allowed")
    
#     # Save the amendment history
#     amendment_history = CustomerAmendmentHistory(
#         amendment_id=customer.id, 
#         field_name="Legal Name Amendment", 
#         old_value=data.old_value,
#         new_value=data.new_value,
#         amendment_request_date=data.amendment_request_date,
#         amendment_remarks=data.amendment_remarks,
#     )
#     db.add(amendment_history)

#     # Update specific fields in CustomerMaster
#     customer.legal_name = data.new_value  
#     customer.amendment_status = "CREATED"
#     # customer.modified_by = user_id
#     # customer.modified_on = datetime.utcnow()

#     # Commit changes
#     db.commit()
#     db.refresh(customer)

#     return {"success": True, "message": "Legal name amendment saved successfully"}

#---------------------------------------------------------------------------------------------------------------

# @router.post("/amend_district")
# def amend_district(data: CustomerAmendmentSchema, 
#                    customer_id: int,
#                    db: Session = Depends(get_db),
#                    token: str = Depends(oauth2.oauth2_scheme)):
    
#     # Validate token
#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")
    
#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")  

#     # Fetch the original customer data to check if it exists and is amendable
#     customer = db.query(CustomerMaster).filter(
#         CustomerMaster.customer_id == customer_id,
#         CustomerMaster.is_amendment == 'yes'
#     ).first()
    
#     if not customer:
#         raise HTTPException(status_code=404, detail="Customer not found or amendment not allowed")
    
#     # Save the amendment history with the "District Amendment" field name
#     amendment_history = CustomerAmendmentHistory(
#         amendment_id=customer.id, 
#         field_name="District Amendment", 
#         old_value=data.old_value,
#         new_value=data.new_value,
#         amendment_request_date=data.amendment_request_date,
#         # amendment_effective_date=data.amendment_effective_date,
#         amendment_remarks=data.amendment_remarks,
#     )
#     db.add(amendment_history)

  
#     customer.district_id = int(data.new_value) 
#     customer.amendment_status = "CREATED"
#     # customer.modified_by = user_id
#     # customer.modified_on = datetime.utcnow()  

#     # Commit changes to both tables
#     db.commit()
#     db.refresh(customer)

#     return {"success": True, "message": "District amendment saved successfully"}

#---------------------------------------------------------------------------------------------------------
# @router.post("/amend_trade_name")
# def amend_trade_name(data: CustomerAmendmentSchema, 
#                      customer_id: int,
#                      db: Session = Depends(get_db),
#                      token: str = Depends(oauth2.oauth2_scheme)):

#     # Validate token
#     if not token:
#         raise HTTPException(status_code=401, detail="Token is missing")

#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")


#     customer = db.query(CustomerMaster).filter(
#         CustomerMaster.customer_id == customer_id,
#         CustomerMaster.is_amendment == 'yes',
#         CustomerMaster.effective_to_date == None
#     ).first()

#     if not customer:
#         raise HTTPException(status_code=404, detail="Customer not found or amendment not allowed")

#     # Record the amendment history for customer_name (trade_name)
#     amendment_history = CustomerAmendmentHistory(
#         customer_id=customer_id,
#         field_name="Trade Name Amndement",  
#         old_value=customer.customer_name,
#         new_value=data.new_value,
#         modified_by=user_id,
#         modified_on=datetime.utcnow()
#     )
#     db.add(amendment_history)

   
#     customer.customer_name = data.new_value  


#     db.commit()

#     return {"success": True, "message": "Updated successfully"}

#-------------------------------------------------------------------------------------------------------------

@router.post("/save_amended_data")
def save_amendment(
    id: int,
    model_name: str,
    field_name: str,
    new_value,
    date: datetime = datetime.now(),
    remarks: str = "",
    db: Session = Depends(get_db)
):
    
    if not field_name:
        raise HTTPException(status_code=400, detail="field_name cannot be null or empty.")
    
    response = db_gst.save_amended_data(db, id, model_name, field_name, new_value, date, remarks)
    return response

#-------------------------------------------------------------------------------------------------------------


@router.get("/get_active_trade_names")
def get_active_trade_names(customer_id: int, 
                           db: Session = Depends(get_db),
                           token: str = Depends(oauth2.oauth2_scheme)):
    
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    active_trade_names = db.execute(text("""
        SELECT *
        FROM customer_additional_trade_name 
        WHERE customer_id = :customer_id
        AND is_deleted = 'no'
        AND (is_amendment = 'yes' OR amended_parent_id NOT IN (
            SELECT amended_parent_id
            FROM customer_additional_trade_name
            WHERE is_amendment = 'yes'
        ))
        ORDER BY id;
    """), {'customer_id': customer_id}).fetchall()

    if not active_trade_names:
        raise HTTPException(status_code=404, detail="No active trade names found for the specified customer")

    return {
        "success": True,
        "active_trade_names": [
            {
                "id": trade_name.id,
                "amended_parent_id": trade_name.amended_parent_id,
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



@router.post("/amend_additonal_trade_names")
def amend_additonal_trade_names(
    id: int,
    amendments: List[AdditionalTradeNameAmendment],
    action: AmendmentAction,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    
    """
    id:

        If action is ADDED, provide the customer_id for id field.

        Otherwise, provide the row_id of the record to be amended.

        action: The type of amendment. Possible values: ADDED, EDITED, DELETED.

        amendments: A list of amendments.

        {
        "id": 1001,  // customer_id for ADD action, row_id for EDIT or DELETE actions
        "action": "ADDED",  // or "EDITED", "DELETED"
        "amendments": [
            {
            "new_trade_name": "New Trade Name",  // The new or updated trade name
            "request_date": "2024-11-08T04:30:45.156Z",  // The date of the request
            "remarks": "Adding new trade name"  // Any remarks for the amendment
            }
        ]
        }

    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    response = db_gst.amend_additonal_trade_names(db, id, amendments, action, user_id)
    return response
