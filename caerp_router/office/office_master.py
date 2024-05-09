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


@router.get("/get_appointments")
def get_appointments(
    appointment_id: Optional[int] = None,
):
    """
    Get appointments based on the specified search criteria.
    """
    try:
        appointment_data = {
            "Appointments": [
                {
                    "appointment_master": {
                        "appointment_master_id": 1,
                        "full_name": "John Doe",
                        "customer_number": "123456",
                        "mobile_number": "9876543210",
                        "whatsapp_number": "9876543210",
                        "email_id": "john@example.com",
                        "locality": "Some locality",
                        "pin_code": "123456",
                        "post_office_id": 1,
                        "post_office_name": "abc",
                        "taluk_id": 2,
                        "taluk_name": "xxx",
                        "district_id": 3,
                        "district_name": 3,
                        "state_id": 4,
                        "state_name": "xxx",
                        # other fields
                        "appointment_visit_master": {
                            "appointment_visit_master_id": 1,
                            "financial_year_id": 1,
                            "voucher_number": "AB1234",
                            "appointment_date": "2024-05-10",
                            "appointment_time_from": "09:00 AM",
                            "appointment_time_to": "10:00 AM",
                            "source_of_enquiry_id": 1,
                            "appointment_status_id": 1,
                            "consultant_id": 1,
                            "first_name": "aaaa",
                            "middle_name": "bbb",
                            "last_name": "ccc",
                            "gross_amount": 100.00,
                            "discount_percentage": 10.00,
                            "discount_amount": 10.00,
                            "special_discount_percentage": 5.00,
                            "special_discount_amount": 5.00,
                            "net_amount": 90.00,
                            "igst_amount": 1.00,
                            "sgst_amount": 2.00,
                            "cgst_amount": 3.00,
                            "bill_amount": 96.00,
                            "remarks": "Appointment visit remarks",
                            "appointment_visit_details": [
                                {
                                    "visit_details_id": 1,
                                    "service_id": 1,
                                    "service_name": "xxx"
                                },
                                {
                                    "visit_details_id": 2,
                                    "service_id": 2,
                                    "service_name": "xxx"
                                },
                                {
                                    "visit_details_id": 3,
                                    "service_id": 3,
                                    "service_name": "xxx"
                                }
                            ]
                        }
                    }
                },
                {
                    "appointment_master": {
                        "appointment_master_id": 2,
                        "full_name": "Ashwathi v",
                        "customer_number": "123456",
                        "mobile_number": "9876543210",
                        "whatsapp_number": "9876543210",
                        "email_id": "john@example.com",
                        "locality": "Some locality",
                        "pin_code": "123456",
                        "post_office_id": 1,
                        "post_office_name": "abc",
                        "taluk_id": 2,
                        "taluk_name": "xxx",
                        "district_id": 3,
                        "district_name": 3,
                        "state_id": 4,
                        "state_name": "xxx",
                        # other fields
                        "appointment_visit_master": {
                            "appointment_visit_master_id": 1,
                            "financial_year_id": 1,
                            "voucher_number": "AB1234",
                            "appointment_date": "2024-05-10",
                            "appointment_time_from": "09:00 AM",
                            "appointment_time_to": "10:00 AM",
                            "source_of_enquiry_id": 1,
                            "appointment_status_id": 1,
                            "consultant_id": 1,
                            "first_name": "aaaa",
                            "middle_name": "bbb",
                            "last_name": "ccc",
                            "gross_amount": 100.00,
                            "discount_percentage": 10.00,
                            "discount_amount": 10.00,
                            "special_discount_percentage": 5.00,
                            "special_discount_amount": 5.00,
                            "net_amount": 90.00,
                            "igst_amount": 1.00,
                            "sgst_amount": 2.00,
                            "cgst_amount": 3.00,
                            "bill_amount": 96.00,
                            "remarks": "Appointment visit remarks",
                            "appointment_visit_details": [
                                {
                                    "visit_details_id": 1,
                                    "service_id": 1,
                                    "service_name": "xxx"
                                },
                                {
                                    "visit_details_id": 2,
                                    "service_id": 2,
                                    "service_name": "xxx"
                                },
                                {
                                    "visit_details_id": 3,
                                    "service_id": 3,
                                    "service_name": "xxx"
                                }
                            ]
                        }
                    }
                }
            ],
            "success": True
        }

        return appointment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/get_consultancy_services')
def get_consultancy_services(
    

):
   
    consultancy_services =  [
    {
        "id": 1,
        "service_name": "Consulting Service",
        "is_consultancy_service": "yes"
    },
     {
        "id": 2,
        "service_name": "Consulting Service1",
        "is_consultancy_service": "yes"
    },
]
    return consultancy_services
@router.get('/get_services_by_consultant')
def get_services_by_consultant(
    consultant_id:int=None
   
):
   if consultant_id is not None:
    consultant=   [
    {
        "consultant_id": 123,
        "services": [
            {
                "id": 1,
                "service_name": "Service 1"
            },
            {
                "id": 2,
                "service_name": "Service 2"
            }
        ]
    }
    
]

    return consultant


    


@router.get('/get_consultants_by_service')
def get_consultants_by_service(service_id: int = None):
    """
    Get consultants by service ID.
    """
    if service_id is not None:
        # Replace this example data with your actual data retrieval logic
        service = {
            "service_id": 123,
            "service_name": "Service Name",
            "consultants": [
                {
                    "consultant_id": 2,
                    "consultant_name": "Jane Smith",
                    "consultant_email": "jane@example.com"
                    # Other consultant details
                },
                # More consultant entries as needed
            ]
        }
        return service
    else:
        # Return an empty dictionary or handle the case when service_id is not provided
        return {}
    

@router.get('/get_appointment_cancellation_reasons', response_model=dict)
def get_appointment_cancellation_reasons():
    """
    Get appointment cancellation reasons.
    """
    reasons = [
        {"id": 1, "reason": "Reason 1"},
        {"id": 2, "reason": "Reason 2"},
        {"id": 3, "reason": "Reason 3"}
        # Add more reasons as needed
    ]
    response_data = {"reasons": reasons}
    return response_data

#  """
#     CANCELLATION PROCESS
#     Cancel an appointment.
    
#     ### Request Body:
#     - **visit_master_id**: The ID of the appointment to be canceled.
#     - **description**: The reason for cancellation.

#     ### Response:
#     - **success**: Indicates whether the cancellation was successful.
  
#     RESCHEDULE PROCESS
#     Reschedule an appointment.
    
#     ### Request Body:
#     - **consultant_id**: The ID of the consultant.
#     - **appointment_master_id**: The ID of the appointment.
#     - **visit_master_id**: The ID of the visit.
#     - **date**: The new date for the appointment.
#     - **time**: The new time for the appointment.
#     - **description**: The reason for rescheduling.

#     ### Response:
#     - **success**: Indicates whether the rescheduling was successful.
#     - **message**: A message indicating the outcome of the reschedule process.

# """

@router.post("/reschedule_or_cancel")
async def reschedule_or_cancel_appointment(
   
    action: AppointmentStatus,
    visit_master_id: int,
    request_data: RescheduleOrCancelRequest = Depends(),
    db: Session = Depends(get_db)
):
   
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
@router.get("/get_appointments", response_model=List[ResponseSchema])
def get_all_appointments(
    id: Optional[int] = None,
    db: Session = Depends(get_db),
    search_criteria: SearchCriteria = Query(None, description="Search criteria"),
    search_value: Union[str, int, None] = None
):
    if search_criteria is None and id is not None:
        # Use "retrieve_appointments" criteria if search_criteria is not provided but id is given
        search_criteria = SearchCriteria.retrieve_appointments

    # Call the consolidated get_appointments function
    appointments = db_office_master.get_appointments(db, search_criteria, search_value)
    return appointments

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