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
router = APIRouter(
    tags=['Office Master']
)
#--------------------save_appointment_details-----------------------
@router.post("/save_appointment_details/{id}", response_model=dict)
def save_appointment_details(
    id: int,
    appointment_data: List[OffAppointmentDetails], 
    db: Session = Depends(get_db),
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
    try:
        for appointment in appointment_data:
            # Create appointment visit master for each appointment
            appointment_master, visit_master, visit_details_list = db_office_master.save_appointment_visit_master(
                db, id, appointment, created_by=1  # Pass each individual appointment
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
    db: Session = Depends(get_db)
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

   
    return db_office_master.reschedule_or_cancel_appointment(db, request_data, action, visit_master_id)
    
@router.get("/get/appointment_info")
async def get_appointment_info(type: str = Query(..., description="Type of information to retrieve: cancellation_reasons or status"), db: Session = Depends(get_db)):
    info = db_office_master.get_appointment_info(db, type)
    return {"info": info}





#-----------get_consultancy_services
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


#-----------get all
@router.get("/get_appointments", response_model=dict)
def get_all_appointments(
    id: Optional[int] = None,
    db: Session = Depends(get_db),
    search_criteria: SearchCriteria = Query(None, description="Search criteria"),
    search_value: Union[str, int, None] = None
):
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
        
        # Wrap appointments list in a dictionary
        return {"Appointments": appointments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

###......................test


from api_library.api_library import DynamicAPI





# cancellation_reason_api = DynamicAPI(OffAppointmentCancellationReason)
# status_api = DynamicAPI(OffAppointmentStatus)
    




# @router.get("/get_appointment_info", operation_id="get_appointment_info")
# async def get_appointment_info(
#     fields: str = Query(..., description="Fields to retrieve"),
#     model_name: str = Query(..., description="Model name to fetch data from"),
#     id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Get appointment information based on provided fields, model name, and optional id.
#     """
#     # Convert the fields string to a list of strings
#     fields_list = fields.split(",")  # Split the string by comma to create a list

#     # Choose the appropriate DynamicAPI instance based on the provided model name
#     if model_name == "OffAppointmentCancellationReason":
#         if id is not None:
#             return cancellation_reason_api.get_record_by_id(db, id, fields_list)
#         else:
#             return cancellation_reason_api.get_records(db, fields_list)
#     elif model_name == "OffAppointmentStatus":
#         if id is not None:
#             return status_api.get_record_by_id(db, id, fields_list)
#         else:
#             return status_api.get_records(db, fields_list)
#     else:
#         raise HTTPException(status_code=400, detail="Invalid model name")
    








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



#........................correct one
# # Define your model mappings
# TABLE_MODEL_MAPPING = {
#     "off_appointment_cancellation_reason": OffAppointmentCancellationReason,
#     "off_appointment_status": OffAppointmentStatus,
#     "off_appointment_master": OffAppointmentMaster,
#     # Add more mappings as needed
# }

# # Define a function to get the model class based on the provided model name
# def get_model_by_model_name(model_name: str) -> Type:
#     return TABLE_MODEL_MAPPING.get(model_name)

# # Define your FastAPI endpoint
# @router.get("/test_new/get_info2", operation_id="get_appointment_info")
# async def get_info(
#     fields: str = Query(..., description="Fields to retrieve"),
#     model_name: str = Query(..., description="Model name to fetch data from"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get appointment information based on provided fields and model name.
#     """
#     try:
#         # Convert the fields string to a list of strings
#         fields_list = fields.split(",")  # Split the string by comma to create a list

#         # Print the received request fields and model name for debugging
#         print("Received request with fields:", fields)
#         print("Model name:", model_name)

#         # Get the model class based on the provided model name
#         table_model = get_model_by_model_name(model_name)

#         # Check if the model exists
#         if table_model is None:
#             raise HTTPException(status_code=404, detail="Model not found")

#         # Initialize DynamicAPI instance with the retrieved model
#         dynamic_api = DynamicAPI(table_model)

#         # Fetch records using the DynamicAPI instance
#         return dynamic_api.get_records(db, fields_list)
#     except Exception as e:
#         # Print any exceptions for debugging
#         print("Error:", e)
#         raise HTTPException(status_code=500, detail=str(e))