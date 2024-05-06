from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,status,Query,Response
from sqlalchemy.orm import Session
from caerp_auth.authentication import authenticate_user
from caerp_db.database import get_db
from caerp_db.office import db_office_master
from typing import Union,List,Dict,Any
from caerp_schema.office.office_schema import OffAppointmentDetails,ResponseSchema,OffAppointmentMasterView,OffAppointmentMasterSchema
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
router = APIRouter(
    tags=['Office Master']
)
#--------------------save_appointment_details-----------------------

@router.post("/save_appointment_details/{id}", response_model=dict)
def create_appointment_visit_master_endpoint(
    appointment_data: List[OffAppointmentDetails], 
    db: Session = Depends(get_db),
    # token: str = Depends(oauth2.oauth2_scheme)  
):
    """
    Save or create appointment visit_master for a specific ID.
    """
    
    # if not token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
        # Authenticate user if needed
        # auth_info = authenticate_user(token)
        # user_id = auth_info["user_id"]

        for appointment in appointment_data:
            # Create appointment visit master for each appointment
            appointment_master, visit_master, visit_details_list = db_office_master.save_appointment_visit_master(
                db, appointment
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


# @router.post("/reschedule_escalate", response_model=dict)
# def reschedule_escalate_appointment(
#     consultant_id: int,
#     appointment_master_id: int,
#     visit_master_id: int,
#     date: str,
#     time: str,
#     description: str
# ):
#     """
#     Reschedule or escalate appointments.
#     """
#     try:
#         # Perform rescheduling or escalation logic here
#         # For demonstration purposes, let's assume the operation is successful
#         success = True
#         message = "Appointment rescheduled/escalated successfully"

#         # Prepare response
#         response_data = {
#             "success": success,
#             "message": message
#         }
#         return response_data
#     except Exception as e:
#         # If an error occurs, return an error response
#         error_message = str(e)
#         raise HTTPException(status_code=500, detail=error_message)
# @router.post('/cancel_appointment/{visit_master_id}', response_model=dict)
# def cancel_appointment(
#     visit_master_id: int,
#     cancellation_reason: str
# ):
#     """
#     Cancels an existing appointment.
#     """
#     try:
#         # Perform cancellation logic here
#         # For demonstration purposes, let's assume the operation is successful
#         success = True
#         message = "Appointment canceled successfully"

#         # Prepare response
#         response_data = {
#             "success": success,
#             "message": message
#         }
#         return response_data
#     except Exception as e:
#         # If an error occurs, return an error response
#         error_message = str(e)
#         raise HTTPException(status_code=500, detail=error_message)
    


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
                    "consultant_id": 1,
                    "consultant_name": "John Doe",
                    "consultant_email": "john@example.com"
                    # Other consultant details
                },
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