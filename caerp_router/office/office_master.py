from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File,status,Query,Response
from sqlalchemy.orm import Session
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import AppointmentStatus, DeletedStatus,SearchCriteria
from caerp_db.database import get_db
from caerp_db.office import db_office_master
from typing import Union,List,Dict,Any
from caerp_db.office.models import OffAppointmentCancellationReason, OffAppointmentMaster, OffAppointmentStatus, OffAppointmentVisitDetailsView, OffAppointmentVisitMaster
from caerp_schema.office.office_schema import OffAppointmentDetails, OffServicesDisplay, OffViewServiceGoodsMasterDisplay,RescheduleOrCancelRequest, ResponseSchema
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
def search_appointments(
    consultant_id: Optional[str] = "ALL",
    service_id: Optional[str] = "ALL",
    status_id: Optional[str] = "ALL",
    from_date: Optional[date]  = Query(date.today()),
    to_date: Optional[date]  = Query(date.today()),
    # search_criteria: SearchCriteriaConstants = "ALL",
    # id:Optional[int]=0,
    search_value: Union[str, int] = "ALL",
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
    - **search_value**: Search value Can be 'mobile_number', 'email_id', or 'ALL'.
    """
    result = db_office_master.get_appointments(
        db,
        consultant_id=consultant_id,
        service_id=service_id,
        status_id=status_id,
        from_date=from_date,
        to_date=to_date,
       
        # search_criteria=search_criteria,
        search_value=search_value
    )
    return {"Appointments": result}

    


#-------------------------swathy--------------------------------
@router.get('/services/get_all_service_goods_master', response_model=list[OffViewServiceGoodsMasterDisplay])
def get_all_service_goods_master(deleted_status: DeletedStatus =  Query(..., title="Select deleted status"),
  db: Session = Depends(get_db),
      token: str = Depends(oauth2.oauth2_scheme)):
   
    """
    Get all  service goods master
    """
    # Check if deleted_status is a valid option
    if deleted_status not in [DeletedStatus.DELETED, DeletedStatus.NOT_DELETED, DeletedStatus.ALL]:
        raise HTTPException(
            status_code=400,
            detail="Invalid value for 'deleted_status'. Allowed values are 'yes', 'no', and 'all'."
        )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_office_master.get_all_service_goods_master(db,deleted_status)

###......................test


