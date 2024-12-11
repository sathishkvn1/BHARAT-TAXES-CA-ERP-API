
from typing import Any, List, Union
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from sqlalchemy import and_, or_, select, text
from caerp_constants.caerp_constants import AmendmentAction
from caerp_db.common.models import BusinessActivity, BusinessActivityMaster, BusinessActivityType, DistrictDB, StateDB
from caerp_db.office.models import AppBusinessConstitution
from caerp_db.services import db_gst, db_gst_amendment
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
    prefix="/gst_amendement",
    tags=['Gst Amendement']
)


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

    result = db_gst_amendment.duplicate_customer_data(db, customer_id, service_task_id, user_id)

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    
    return {"success": True, "message": "Saved successfully", "id": result["id"]}


#----------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------
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
    
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    # Authenticate user and get user_id
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    
    if not field_name:
        raise HTTPException(status_code=400, detail="field_name cannot be null or empty.")
    
    response = db_gst_amendment.save_amended_data(db, id, model_name, field_name, new_value, date, remarks,user_id)
    return response

#----------------------------------------------------------------------------------------------------------



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


#----------------------------------------------------------------------------------------------------------


@router.post("/amend_additional_trade_names")
def amend_additional_trade_names(
    id: int,
    service_task_id: int,
    amendment_data: AdditionalTradeNameAmendment,
    action: AmendmentAction,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
):
    
    """
    {
  "amendments": [
    {
      "id": 198,
      "new_trade_name": "trade1 updated",
      "request_date": "2024-12-09T10:13:08.053Z"
    },
 {
      "id": 199,
      "new_trade_name": "trase2",
      "request_date": "2024-12-09T10:13:08.053Z"
    },
 {
      "id": 0,
      "new_trade_name": "trase3",
      "request_date": "2024-12-09T10:13:08.053Z"
    }
  ],
  "remarks": "saved"
}
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    # Authenticate user and get user_id
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    # Call the database operation
    response = db_gst_amendment.amend_additional_trade_names_in_db(
        db, id, service_task_id, amendment_data, user_id, action
    )
    return response


#--------------------------------------------------------------------------------------------------------------------



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

    response = db_gst_amendment.delete_amendment_business_place(db, id, user_id)
    if not response["success"]:
        raise HTTPException(status_code=400, detail=response["message"])

    return response



#---------------------------------------------------------------------------------------------------------

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
        response = db_gst_amendment.add_stake_holder(db, customer_id,service_task_id, stakeholder_type, request_data, user_id)
    elif action == AmendmentAction.DELETED:
        response = db_gst_amendment.delete_stake_holder(db, id,amendment_details, action, user_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return response


#------------------------------------------------------------------------------------------------------------------------

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
    stakeholder_details = db_gst_amendment.get_stakeholder_master_for_amndement(db, customer_id, stakeholder_type,service_task_id,user_id)

    if not stakeholder_details:
        return []

    return stakeholder_details

#-----------------------------------------------------------------------------------------------------------
@router.post("/amend_business_place")
def amend_business_place(customer_id: int, 
                         service_task_id: int,
                         amendment_details: CustomerBusinessPlaceFullAmendmentSchema,
                         action: AmendmentAction,
                         id: Optional[int] = None,
                         db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)):

    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = db_gst_amendment.amend_business_place_data(db, customer_id, service_task_id, amendment_details, action, user_id, id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"success": True, "message": "Amendment saved successfully", "id": result["id"]}

#----------------------------------------------------------------------------------------------------

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
        combined_data = db_gst_amendment.fetch_combined_data(db, customer_id,service_task_id)
        return combined_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#--------------------------------------------------------------------------------------------------------

@router.post("/amended_additional_business_places")
def amended_additional_business_places(
    customer_id: int, 
    service_task_id: int,
    amendment_details: CustomerBusinessPlacesFullAmendmentSchema,
    action: AmendmentAction,
    db: Session = Depends(get_db),
    id: Optional[int] = None,
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    amendment_details_dict = amendment_details.dict()

    if action == AmendmentAction.ADDED:
        result = db_gst_amendment.add_additional_business_places_and_activities(db, customer_id, service_task_id, amendment_details_dict, user_id)

    elif action == AmendmentAction.EDITED and id:
        result = db_gst_amendment.edit_existing_business_places_and_activities(db, customer_id, service_task_id, id, amendment_details_dict, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {"success": True, "message": "Amendment saved successfully"}

