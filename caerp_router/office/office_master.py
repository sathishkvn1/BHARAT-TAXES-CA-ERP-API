from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File,status,Query,Response
from sqlalchemy.orm import Session
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import AppointmentStatus,SearchCriteria
from caerp_db.database import get_db
from caerp_db.office import db_office_master
from typing import Union,List,Dict,Any
from caerp_db.office.models import OffAppointmentCancellationReason, OffAppointmentMaster, OffAppointmentStatus, OffAppointmentVisitDetailsView, OffAppointmentVisitMaster
from caerp_schema.office.office_schema import OffAppointmentDetails, OffServicesDisplay,RescheduleOrCancelRequest, ResponseSchema
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
from datetime import date
router = APIRouter(
    tags=['Office Master']
)



#--------------------save_appointment_details-----------------------


@router.post("/save_appointment_details/{id}", response_model=dict)
def save_appointment_details(
    id: int,
    appointment_data: List[OffAppointmentDetails], 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
   - Save or create appointment details for a specific ID.
   - **data**: Data for the visit master, provided as parameters of type OffAppointmentDetails.
    - **id**: An optional integer parameter with a default value of 0, indicating the appointment_details's identifier.
    
    - If appointment_master id is 0, it indicates the creation of a new appointment_details.
    - Returns: The newly created appointment_details as the response.

    If appointment_master id is not 0, it indicates the update of an existing appointment_details.
    - Returns: The updated appointment_details as the response.

    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    
    try:
        for appointment in appointment_data:
            # Create appointment visit master for each appointment
            db_office_master.save_appointment_visit_master(
                db, id, appointment,user_id  # Pass each individual appointment
            )
        
        # Return success response
        return {"success": True, "message": "Saved successfully"}
    
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# # get all







@router.post("/reschedule_or_cancel")
async def reschedule_or_cancel_appointment(
   
    action: AppointmentStatus,
    visit_master_id: int,
    request_data: RescheduleOrCancelRequest = Depends(),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    
    """
    CANCELLATION PROCESS
    Cancel an appointment.
    
    ### Request Body:
    - **visit_master_id**: The ID of the appointment to be canceled.
    - **description**: The reason for cancellation.

    ### Response:
    - **success**: Indicates whether the cancellation was successful.
  
    RESCHEDULE PROCESS
    Reschedule an appointment.
    
    ### Request Body:
    - **consultant_id**: The ID of the consultant.
    - **appointment_master_id**: The ID of the appointment.
    - **visit_master_id**: The ID of the visit.
    - **date**: The new date for the appointment.
    - **time**: The new time for the appointment.
    - **description**: The reason for rescheduling.

    ### Response:
    - **success**: Indicates whether the rescheduling was successful.
    - **message**: A message indicating the outcome of the reschedule process.

"""

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    return db_office_master.reschedule_or_cancel_appointment(db, request_data, action, visit_master_id)
    
@router.get("/get/appointment_info")
async def get_appointment_info(type: str = Query(..., description="Type of information to retrieve: cancellation_reasons or status"),
                                # token: str = Depends(oauth2.oauth2_scheme),
                                db: Session = Depends(get_db)
                                ):
    """
    Retrieve information about appointment cancellation reasons or statuses.

    Parameters:
    - **type**: Type of information to retrieve. Can be 'cancellation_reasons' or 'status'.

    Response:
    - If 'type' is 'cancellation_reasons', returns a list of cancellation reasons with their IDs.
    - If 'type' is 'status', returns a list of appointment statuses with their IDs.
    """

#-----------get_consultancy_services--------------------------------------------#


@router.get('/get_consultancy_services',response_model=List[OffServicesDisplay])
def get_consultancy_services(
    db: Session = Depends(get_db),
    # token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get consultancy_services
    """
    # if not token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    consultancy_services = db_office_master.get_consultancy_services(db)  
    if not consultancy_services:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"consultancy_services not found" 
        )
    return consultancy_services

#-------------get all-------------------------------------------------------------------------
@router.get("/get_appointments", response_model=Dict[str, List[ResponseSchema]])
def get_all_appointments(
    id: Optional[int] = None,
    # token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
    search_criteria: SearchCriteria = Query(None, description="Search criteria"),
    search_value: Union[str, int, None] = None
):
    """
    Retrieve appointments based on search criteria or appointment ID.

    Parameters:
    - **search_criteria**: Type of search criteria. Can be 'mobile_number', 'email_id', or 'ALL'.
    - **search_value**: Search value corresponding to the search criteria.
    - **id**: Appointment ID.

    Response:
    - If no appointments are found, returns a message indicating no appointments found and success status.
    """
    # if not token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    try:
        if id is not None:
            # If id is provided, filter appointments by ID
            appointments = db_office_master.get_appointments(db, id=id)
        elif search_criteria is not None:
            # If search_criteria is provided, use it with search_value
            appointments = db_office_master.get_appointments(db, search_criteria=search_criteria, search_value=search_value)
        else:
            # If neither id nor search_criteria is provided, return an empty list
            appointments = []
        
        return {"Appointments": appointments}  # Return the dictionary with the key "Appointments"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
#search



@router.get("/search_appointments", response_model=Dict[str, List[ResponseSchema]])
def search_appointments(
    consultant_id: Optional[int] = None,
    service_id: Optional[int] = None,
    status_id: Optional[int] = None,
    effective_from_date: date = Query(date.today()),
    effective_to_date: date = Query(date.today()),
    db: Session = Depends(get_db)
):
    """
    Retrieve appointments based on Parameters.

    Parameters:
    - **consultant_id**: Consultant ID.
    - **service_id**: Service ID.
    - **status_id**: Status ID.
    - **effective_from_date**: Effective from date (default: today's date).
    - **effective_to_date**: Effective to date (default: today's date).
    """
    result = db_office_master.search_appointments(
        db,
        consultant_id=consultant_id,
        service_id=service_id,
        status_id=status_id,
        effective_from_date=effective_from_date,
        effective_to_date=effective_to_date
    )
    return {"appointments": result}


###......................test


from api_library.api_library import DynamicAPI


    


from typing import List, Type

TABLE_MODEL_MAPPING = {
    "OffAppointmentCancellationReason": OffAppointmentCancellationReason,
    "OffAppointmentStatus": OffAppointmentStatus,
    "OffAppointmentMaster": OffAppointmentMaster,
  
}

# Define a function to get the model class based on the provided model name
def get_model_by_model_name(model_name: str) -> Type:
    """
    Get the SQLAlchemy model class corresponding to the provided model name.
    """
    return TABLE_MODEL_MAPPING.get(model_name)

from fastapi import Query

def get_model_by_model_name(model_name: str) -> Type:
    """
    Get the SQLAlchemy model class corresponding to the provided model name.
    """
    return TABLE_MODEL_MAPPING.get(model_name)



@router.get("/test/get_info2", operation_id="get_appointment_info")
async def get_info(
    fields: str = Query(..., description="Fields to retrieve"),
    model_name: str = Query(..., description="Model name to fetch data from"),
    id: Optional[int] = Query(None, description="ID of the record to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get appointment information based on provided fields, model name, and optional ID.
    """
    # Convert the fields string to a list of strings
    fields_list = fields.split(",")  # Split the string by comma to create a list
    
    # Get the model class based on the provided model name
    table_model = get_model_by_model_name(model_name)

    # Check if the model exists
    if table_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    # Initialize DynamicAPI instance with the retrieved model
    dynamic_api = DynamicAPI(table_model)

    if id is not None:
        # Fetch record by ID using the DynamicAPI instance
        return dynamic_api.get_record_by_id(db, id, fields_list)
    else:
        # Fetch records using the DynamicAPI instance
        return dynamic_api.get_records(db, fields_list)

#........................fr delete

@router.get("/test/delete_undelete_by_id", operation_id="delete_undelete_record")
async def get_info(
    model_name: str = Query(..., description="Model name to fetch data from"),
    id: Optional[int] = Query(None, description="ID of the record to retrieve"),
    delete: Optional[str] = Query(None, description="Whether to delete the record ('true' or 'false')"),
    undelete: Optional[str] = Query(None, description="Whether to undelete the record ('true' or 'false')"),
    db: Session = Depends(get_db)
):
    """
    Get appointment information based on provided fields, model name, and optional ID.
    """
    # Convert the fields string to a list of strings
 
    
    # Get the model class based on the provided model name
    table_model = get_model_by_model_name(model_name)

    # Check if the model exists
    if table_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    # Initialize DynamicAPI instance with the retrieved model
    dynamic_api = DynamicAPI(table_model)

    if delete and undelete:
        raise HTTPException(status_code=400, detail="Both delete and undelete cannot be True simultaneously")
    elif delete == 'true':
        # Delete the record
        dynamic_api.delete_record_by_id(db, id)
        return {"message": f"Record with ID {id} from model {model_name} has been deleted"}
    elif undelete == 'true':
        # Undelete the record
        dynamic_api.undelete_record_by_id(db, id)
        return {"message": f"Record with ID {id} from model {model_name} has been undeleted"}
    
    
#--------------------------------------------------------
@router.post("/test/save_record", operation_id="save_record")
async def save_record(
    model_name: str = Query(..., description="Model name to save data to"),
    data: dict = Body(..., description="Data to be saved to the table"),
    db: Session = Depends(get_db)
):
    """
    Save a record to the specified table.
    """
    # Get the model class based on the provided model name
    table_model = get_model_by_model_name(model_name)

    # Check if the model exists
    if table_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    # Extract the appointment_status value from the data dictionary
    appointment_status = data.get("appointment_status")

    # Initialize DynamicAPI instance with the retrieved model
    dynamic_api = DynamicAPI(table_model)

    # Create a dictionary containing the appointment_status
    record_data = {"appointment_status": appointment_status}

    # Call the common function to save the record
    dynamic_api.save_record(db, record_data)

    return {"message": "Record saved successfully"}

#.........................................................

# @router.post("/test/save_recordsss", operation_id="save_record")
# async def save_record(
#     model_name: str = Query(..., description="Model name to save data to"),
#     data: dict = Body(..., description="Data to be saved to the table"),
#     id: Optional[int] = Query(None, description="ID of the record to update. If not provided or 0, insert a new record."),
#     db: Session = Depends(get_db)
# ):
#     """
#     Save a record to the specified table. If ID is provided and nonzero, update an existing record.
#     """
#     # Get the model class based on the provided model name
#     table_model = get_model_by_model_name(model_name)

#     # Check if the model exists
#     if table_model is None:
#         raise HTTPException(status_code=404, detail="Model not found")

#     # Initialize DynamicAPI instance with the retrieved model
#     dynamic_api = DynamicAPI(table_model)

#     if id is not None and id != 0:
#         # Update existing record if ID is provided and nonzero
#         # Check if the record exists
#         existing_record = dynamic_api.get_record_by_id(db, id, [])  # Provide an empty list for fields
#         if existing_record:
#             # Update the existing record
#             dynamic_api.update_record_by_id(db, id, data)
#             return {"message": f"Record with ID {id} from model {model_name} has been updated"}
#         else:
#             raise HTTPException(status_code=404, detail="Record not found")
#     else:
#         # Insert a new record if ID is not provided or 0
#         dynamic_api.save_record(db, data)
#         return {"message": "New record inserted successfully"}

