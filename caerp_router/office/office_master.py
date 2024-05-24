from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from sqlalchemy.orm import Session
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import AppointmentStatus, DeletedStatus, RecordActionType,SearchCriteria
from caerp_db.common.models import Employee
from caerp_db.database import get_db
from caerp_db.office import db_office_master
from typing import Union,List,Dict,Any
from caerp_db.office.models import OffAppointmentCancellationReason, OffAppointmentMaster, OffAppointmentStatus, OffAppointmentVisitDetailsView, OffAppointmentVisitMaster, OffViewConsultantDetails, OffViewConsultantMaster
from caerp_schema.office.office_schema import  EmployeeResponse, OffAppointmentDetails, OffViewServiceGoodsMasterDisplay, PriceListResponse,RescheduleOrCancelRequest, ResponseSchema, SaveServicesGoodsMasterRequest, ServiceGoodsPrice, Slot
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
from datetime import date
router = APIRouter(
    tags=['Office Master']
)



#--------------------save_appointment_details-----------------------


@router.post("/save_appointment_details/{id}")
def save_appointment_details(
    id: int,
    appointment_data: List[OffAppointmentDetails], 
    action_type: RecordActionType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
    
):
    """
   - Save or create appointment details for a specific ID.
    - **data**: Data for the visit master, provided as parameters of type OffAppointmentDetails.
    - **id**: An optional integer parameter with a default value of 0, indicating the appointment_details's identifier.
    - **action_type (RecordActionType)**: The action type to be performed, indicating whether to insert or update the appointment details.

    - If appointment_master id is 0, it indicates the creation of a new appointment_details.
    - Returns: The newly created appointment_details as the response.
    - If appointment_master id is not 0, it indicates the update of an existing appointment_details.
    - Returns: The updated appointment_details as the response.
    - If action_type is INSERT_ONLY, the id parameter should be 0.
    - If action_type is UPDATE_ONLY, the id parameter should be greater than 0.
    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        for appointment in appointment_data:
            db_office_master.save_appointment_visit_master(
                db, id, appointment, user_id, action_type
            )

        return {"success": True, "message": "Saved successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
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






#-------------get all-------------------------------------------------------------------------
@router.get("/get_appointments", response_model=Dict[str, List[ResponseSchema]])
def get_and_search_appointments(
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
@router.get('/services/search_service_goods_master', response_model=list[OffViewServiceGoodsMasterDisplay])

def get_all_service_goods_master(
    deleted_status: Optional[DeletedStatus] = Query(None, title="Select deleted status", enum=list(DeletedStatus)),
    service_goods_name: Optional[str] = Query(None, title="Service Name for search (optional)"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get all service goods master
    """
   

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_office_master.get_all_service_goods_master(db, deleted_status, service_goods_name)

@router.post("/services/save_services_goods_master{id}")
def save_services_goods_master(
    id: int,
    data: List[SaveServicesGoodsMasterRequest], 
    action_type: RecordActionType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
    
):
   

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        for service in data:
            db_office_master.save_services_goods_master(
                db, id, service, user_id, action_type
            )

        return {"success": True, "message": "Saved successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



###......................test

# @router.get("/generate_consultation_slots/", response_model=List[Slot])
# def generate_consultation_slots(request: ConsultationRequest=Depends(), db: Session = Depends(get_db)):
#     # Step 1: Get Service and Consultants
#     service, consultants = db_office_master.get_service_and_consultants_by_service(db, request.service_id)
#     print("Service:", service)
#     print("Consultants:", consultants)
#     if not service:
#         raise HTTPException(status_code=404, detail="Service not found")
#     if not consultants:
#         raise HTTPException(status_code=404, detail="No consultants available for this service")

#     # Step 2: Check Consultant Availability
#     available_consultants = []
#     for consultant_id in consultants:
#         is_available = db_office_master.check_consultant_availability(db, consultant_id, request.start_time, request.end_time)
#         if is_available:
#             available_consultants.append(consultant_id)
    
#     if not available_consultants:
#         raise HTTPException(status_code=404, detail="No available consultants for the selected time")

#     # Step 3: Generate Slots
#     slots = []
#     for consultant_id in available_consultants:
#         slots.extend(db_office_master.generate_slots(db, request.service_id, consultant_id, request.start_time, request.end_time))
    
#     return slots
from datetime import datetime, timedelta


# @router.get("/get_availability/", response_model=List[dict])
async def get_availability(
    consultant_id: int,
    service_id: int,
    date: date ,
    db: Session = Depends(get_db)
):
    # Check if date is provided
    if not date:
        raise HTTPException(status_code=400, detail="Date header is missing")

    # Query to join OffViewConsultantMaster and OffViewConsultantDetails
    availability_query = (
        db.query(OffViewConsultantMaster, OffViewConsultantDetails)
        .join(OffViewConsultantDetails,OffViewConsultantMaster.consultant_id ==OffViewConsultantDetails.consultant_id)
        .filter(
           OffViewConsultantMaster.consultant_id == consultant_id,
            OffViewConsultantMaster.consultant_master_available_date_from <= date,
            (OffViewConsultantMaster.consultant_master_available_date_to == None) |
            (OffViewConsultantMaster.consultant_master_available_date_to >= date),
           OffViewConsultantDetails.service_goods_master_id == service_id
        )
    )

    # Execute the query
    availability_data = availability_query.first()

    # Check if availability data is found
    if not availability_data:
        raise HTTPException(status_code=404, detail="Consultant or service not available on this date")

    # Extract consultant and service details
    consultant_master, consultant_details = availability_data

    # Calculate available time slots
    start_time = datetime.combine(date, consultant_master.consultant_master_available_time_from)
    end_time = datetime.combine(date, consultant_master.consultant_master_available_time_to)
    slot_duration = timedelta(minutes=consultant_details.slot_duration_in_minutes)

    available_slots = []
    while start_time + slot_duration <= end_time:
        available_slots.append({
            "start_time": start_time.time().strftime('%H:%M'),
            "end_time": (start_time + slot_duration).time().strftime('%H:%M')
        })
        start_time += slot_duration

    return available_slots



@router.get("/get_availability/")
async def check_availability(
    consultant_id: int,
    service_id: int,
    check_date: date,
    db: Session = Depends(get_db)
):
    # Call the get_availability endpoint to retrieve available slots
    available_slots = await get_availability(consultant_id, service_id, check_date, db)
    
    # Filter out booked slots
    available_slots = filter_booked_slots(available_slots, consultant_id, check_date, db)
    
    # Return the filtered available slots
    return available_slots

def filter_booked_slots(available_slots, consultant_id, check_date, db):
    # Query booked slots from OffAppointmentVisitMaster for the specified consultant and date
    booked_slots_query = (
        db.query(OffAppointmentVisitMaster)
        .filter(
           OffAppointmentVisitMaster.consultant_id == consultant_id,
           OffAppointmentVisitMaster.appointment_date == check_date
        )
    )
    
    # Extract booked slots
    booked_slots = [(slot.appointment_time_from, slot.appointment_time_to) for slot in booked_slots_query.all()]
    
    # Filter out booked slots from available slots
    available_slots = [slot for slot in available_slots if (slot['start_time'], slot['end_time']) not in booked_slots]
    
    return available_slots

#---------------------


@router.post("/services/save_services_goods_master{id}")
def save_services_goods_master(
    id: int,
    data: List[SaveServicesGoodsMasterRequest], 
    action_type: RecordActionType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
    
):
   

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        for service in data:
            db_office_master.save_services_goods_master(
                db, id, service, user_id, action_type
            )

        return {"success": True, "message": "Saved successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#///////////////////////////////////////////////

@router.get("/consultants_and_services/")
def get_consultants_and_services(
    category: Optional[str] = Query(None, description="Selection category: 'consultant', 'all'"),
    # category: str = Query(..., description="Selection category: 'consultant', 'all'"),
    service_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if category == "consultant":
        # Fetch consultants from the database
        consultants = db_office_master.get_consultants(db)
        # Convert consultants to a list of dictionaries
        consultants_data = [{"id": consultant.employee_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
        return EmployeeResponse(employees=consultants_data)

    elif category == "all":
        # Fetch all employees from the database
        employees = db_office_master.get_all_employees(db)
        # Convert employees to a list of dictionaries
        employees_data = [{"id": employee.employee_id, "first_name": employee.first_name, "middle_name": employee.middle_name, "last_name": employee.last_name} for employee in employees]
        return EmployeeResponse(employees=employees_data)
    
    elif service_id is not None and service_id != 0:
        # Fetch consultants for the given service_id from off_view_consultant_details table
        consultants = db_office_master.get_consultants_for_service(db, service_id)
        # Convert consultants to a list of dictionaries
        consultants_data = [{"id": consultant.consultant_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
        return {"consultants": consultants_data}
    
    else:
        # Fetch all services from off_view_consultant_details table
        services = db_office_master.get_all_services(db)
        # Convert services to a list of dictionaries
        services_data = [{"id": service.service_goods_master_id, "name": service.service_goods_name} for service in services]
        return {"services": services_data}


@router.get("/get_consultants/")
def get_consultants(
    id: Optional[int] = None,
    service_id: Optional[int] = Query(None, description="ID of the service to retrieve consultants for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all consultants by setting id=0.
    Retrieve consultants for a specific service by providing a valid service_id.
    """
    if service_id is not None and service_id != 0:
        # Fetch consultants for the given service_id from off_view_consultant_details table
        consultants = db_office_master.get_consultants_for_service(db, service_id)
        # Convert consultants to a list of dictionaries
        consultants_data = [{"id": consultant.consultant_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
        return {"service_id": service_id, "consultants": consultants_data}
    elif id==0:
        consultants = db_office_master.get_consultants(db)
        consultants_data = [{"id": consultant.employee_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
        return EmployeeResponse(employees=consultants_data)

    else:
        raise HTTPException(status_code=400, detail="Invalid service ID")



@router.get("/get_consultation_services/")
def get_consultation_services(
    service_id: Optional[int] = Query(None, description="ID of the service to retrieve consultants for"),
    consultant_id: Optional[int] = Query(None, description="ID of the consultant to retrieve services for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all services by setting service_id=0.
    Retrieve services for a specific consultant by providing a valid consultant_id.
    """
    print(f"Received request with service_id: {service_id}, consultant_id: {consultant_id}")  # Debug print

    if service_id == 0:
        # Fetch all services from off_view_consultant_details table
        services = db_office_master.get_all_services(db)
        # Convert services to a list of dictionaries
        services_data = [{"id": service.service_goods_master_id, "name": service.service_goods_name} for service in services]
        print(f"Retrieved all services: {services_data}")  # Debug print
        return {"services": services_data}

    elif consultant_id is not None and consultant_id != 0:
        print(f"Checking consultant_id: {consultant_id}")  # Debug print
        # Fetch services for the given consultant_id from off_view_consultant_details table
        services = db_office_master.get_all_services_by_consultant_id(db, consultant_id)
        print(f"Retrieved services for consultant ID {consultant_id}: {services}")  # Debug print
        if not services:
            raise HTTPException(status_code=404, detail=f"No services found for consultant ID {consultant_id}")
        # Convert services to a list of dictionaries
        services_data = [{"id": service.service_goods_master_id, "name": service.service_goods_name} for service in services]
        print(f"Filtered services data: {services_data}")  # Debug print
        return {"consultant_id": consultant_id, "services": services_data}

    else:
        raise HTTPException(status_code=400, detail="Invalid request. Provide a valid service ID or consultant ID.")


#..........................................................



# @router.get("/get_price_list/", response_model=PriceListResponse)
# def get_price_list(
#     service_type: Optional[str] = Query(None, description="Filter by type: 'ALL', 'GOODS', 'SERVICE'"),
    
#     search: Optional[str] = Query(None, description="Search by service name"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Fetches a list of services or goods with their configuration status, service type, and rate status.
#     """
#     print(f"Received request with service_type: {service_type}, search: {search}")  # Debug print

#     if service_type == "ALL" and search is None:
#         services = db_office_master.get_all_services(db)
#     else:
#         services = db_office_master.get_services_filtered(db, service_type, search)
    
#     if not services:
#         raise HTTPException(status_code=404, detail="No services found matching the criteria")
    
#     services_data = [
#         ServiceGoodsPrice(
#             service_name=item.service_goods_name,
#             # configuration_status="CONFIGURED" if not item.services_goods_master_is_deleted else "NOT CONFIGURED",
#             service_type=item.hsn_sac_class,
#             # service_type="BUNDLE" if item.is_bundled_service else "SINGLE",
#             # rate_status="CONFIGURED" if not item.services_goods_master_is_deleted else "NOT CONFIGURED"
#         ) for item in services
#     ]
    
#     return PriceListResponse(price_list=services_data)


from sqlalchemy import text
from fastapi import HTTPException

@router.get("/get_price_list/", response_model=PriceListResponse)
def get_price_list(
    service_type: Optional[str] = Query(None, description="Filter by type: 'ALL', 'GOODS', 'SERVICE'"),
    configuration_status: Optional[str] = Query(None, description="Filter by configuration status: 'ALL', 'CONFIGURED', 'NOTCONFIGURED'"),
    search: Optional[str] = Query(None, description="Search by service name"),
    db: Session = Depends(get_db)
):
    """
    Fetches a list of services or goods with their configuration status, service type, and rate status.
    """
    print(f"Received request with service_type: {service_type}, search: {search}")  # Debug print

    if service_type == "ALL" and  configuration_status == "ALL" and search is None:
        query = text("""
            SELECT 
                a.id, 
                a.hsn_sac_class_id,
                b.hsn_sac_class,
                a.service_goods_name,
                a.is_bundled_service,
                c.id AS price_master_id,
                CASE 
                    WHEN COUNT(c.service_goods_master_id) >= 1 
                    THEN 'Configured' 
                    ELSE 'Not Configured' 
                END AS configuration_status
            FROM 
                off_service_goods_master AS a
            INNER JOIN 
                app_hsn_sac_classes AS b ON a.hsn_sac_class_id = b.id
            LEFT JOIN 
                off_service_goods_price_master AS c ON a.id = c.service_goods_master_id
            GROUP BY 
                a.id
            ORDER BY  a.hsn_sac_class_id DESC, a.service_goods_name ;
        """)
   

    results = db.execute(query)
    services_data = [
        ServiceGoodsPrice(
            service_name=item.service_goods_name,
            service_type=item.hsn_sac_class,
            bundled_service=item.is_bundled_service,
        ) for item in results.fetchall()
    ]

    if not services_data:
        raise HTTPException(status_code=404, detail="No services found matching the criteria")

    return PriceListResponse(price_list=services_data)


