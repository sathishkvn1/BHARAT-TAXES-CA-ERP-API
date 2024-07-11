from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import  DeletedStatus, RecordActionType,SearchCriteria
from caerp_db.common.models import  EmployeeContactDetails, EmployeeEmployementDetails, EmployeeMaster, HrDepartmentMaster, HrDesignationMaster
from caerp_db.database import get_db
from caerp_db.office import db_office_master
from typing import Union,List,Dict,Any
from caerp_db.office.models import AppDayOfWeek, AppHsnSacClasses, OffAppointmentCancellationReason, OffAppointmentMaster, OffAppointmentStatus, OffAppointmentVisitDetailsView, OffAppointmentVisitMaster, OffConsultantSchedule, OffConsultantServiceDetails, OffConsultationMode, OffServiceGoodsMaster, OffServiceGoodsPriceMaster, OffViewConsultantDetails, OffViewConsultantMaster
from caerp_schema.office.office_schema import  AppointmentStatusConstants, Bundle, ConsultantEmployee, ConsultantScheduleCreate, ConsultantService, ConsultantServiceDetailsListResponse, ConsultantServiceDetailsResponse, ConsultationModeSchema, ConsultationToolSchema, EmployeeResponse, OffAppointmentDetails, OffConsultationTaskMasterSchema, OffDocumentDataBase, OffDocumentDataMasterBase, OffEnquiryResponseSchema, OffViewConsultationTaskMasterSchema, OffViewEnquiryResponseSchema, OffViewServiceDocumentsDataDetailsDocCategory, OffViewServiceDocumentsDataMasterSchema, OffViewServiceGoodsMasterDisplay, PriceData, PriceHistoryModel, PriceListResponse,RescheduleOrCancelRequest, ResponseSchema, SaveServiceDocumentDataMasterRequest, SaveServicesGoodsMasterRequest, Service_Group, ServiceDocumentsList_Group, ServiceGoodsPrice, ServiceModel, ServiceModelSchema, SetPriceModel, Slot, TimeSlotResponse
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
from datetime import date
from sqlalchemy import text
# from datetime import datetime
from sqlalchemy import select, func,or_
from fastapi.encoders import jsonable_encoder


from sqlalchemy import select, func, and_
router = APIRouter(
    tags=['Office Master']
)



#--------------------save_appointment_details-----------------------

#---------------------------------------------------------------------------------------------------------------
@router.post("/save_appointment_details/{id}")
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
                db, id, appointment, user_id
            )

        return {"success": True, "message": "Saved successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
# # get all




#---------------------------------------------------------------------------------------------------------------
@router.post("/reschedule_or_cancel")
async def reschedule_or_cancel_appointment(
   
    action: AppointmentStatusConstants,
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
    
    
    info = db_office_master.get_appointment_info(db, type)
    return {"info": info}

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

    


#-------------------------swathy-------------------------------------------------------------------------------

@router.get('/services/get_all_service_goods_master', response_model=Union[List[OffViewServiceGoodsMasterDisplay], dict])
def get_all_service_goods_master(
    deleted_status: Optional[DeletedStatus] = Query(None, title="Select deleted status", enum=list(DeletedStatus)),
    service_goods_name: Optional[str] = Query(None),
    group_id: Union[int, str] = Query("ALL"),
    sub_group_id: Union[int, str] = Query("ALL"),
    category_id: Union[int, str] = Query("ALL"),
    sub_category_id: Union[int, str] = Query("ALL"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get all service goods master
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    results = db_office_master.get_all_service_goods_master(
        db, deleted_status, service_goods_name, group_id, sub_group_id, category_id, sub_category_id
    )

    # Check if no data is found
    if not results:
        return {"message": "No data present"}

    # Remove the "details" field if there are no details available
    for result in results:
        if result.is_bundled_service == "no" or not result.details:
            delattr(result, "details")

    return results




#--------------------------------------------------------------------------------------------------------

@router.post("/services/save_services_goods_master/{id}")
def save_services_goods_master(
    id: int,
    data: List[SaveServicesGoodsMasterRequest], 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):  
    """
    Save or update service and goods master records.

    This endpoint allows the user to save or update records in the service and goods master table.
    If the `id` is 0, it will insert new records; otherwise, it will update the existing records with the specified `id`.

    - **id**: The ID of the master record. Use 0 for new records.
    - **data**: A list of `SaveServicesGoodsMasterRequest` objects containing the master and detail data to be saved or updated.
    
    **Returns**:
    - A JSON object indicating the success status and a message detailing the action performed (insert or update).

    """  
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        result_message = ""
        for service in data:
            result = db_office_master.save_services_goods_master(
                db, id, service, user_id
            )
            result_message = result["message"]
        
        return {"success": True, "message": result_message}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#-------------------------------------------------------------------------------------------------------
@router.post("/services/save_off_document_master/{id}")
def save_off_document_master(
    id: int,
    data: OffDocumentDataBase, 
    document_type: str = Query(enum=["DOCUMENT", "DATA"]),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    try:
        result = db_office_master.save_off_document_master(
            db, id, data, document_type
        )
        
        # Return the message from the database function

        if result["success"]:
          
            return {"success": True, "message":result["message"]}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#-------------------------------------------------------------------------------------------------------

@router.get('/services/search_off_document_data_master', response_model=List[OffDocumentDataMasterBase])
def search_off_document_data_master(
    type:  Optional[str] = Query(None, description="Filter by type: 'ALL', 'DOCUMENT', 'DATA'"),
                                #   enum=["ALL", "DOCUMENT", "DATA"]),
    document_name: Optional[str] = Query(None, title="Document Name for search"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    
    """
    Search document names from off document master
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
       
    documents = db_office_master.search_off_document_data_master(db, type, document_name)
    if not documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return documents




#-------------------------------------------------------------------------------------------------------
@router.post("/services/save_service_document_data_master/{id}")
def save_service_document_data_master(
    id: int,
    data: List[SaveServiceDocumentDataMasterRequest], 
    service_document_master_id: Optional[int] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save service document data master.

    Parameters:
    - **id**: The ID of the service document data master record. This parameter is required and should be an integer.
    - **data**: A list of `SaveServiceDocumentDataMasterRequest` objects containing the service document data to be saved.
    - **service_document_master_id**: An optional query parameter that specifies the master ID if only details need to be inserted.
    - **db**: A database session dependency injected by FastAPI.
    - **token**: An authentication token dependency injected by FastAPI using OAuth2.

    Returns:
    - A success message after processing all service document data.
    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
 #   user_id = auth_info.get("user_id")

    try:
        result_message = ""
        for service in data:
            result = db_office_master.save_service_document_data_master(
                db, id, service, service_document_master_id
            )
            result_message = result["message"]
        
        return {"success": True, "message": result_message}
    
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
#---------------------------------------------------------------------------------------------------------------
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

#--------------------------------------------------------------------------------------------------------
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

#---------------------------------------------------------------------------------------------------------------


# @router.get("/consultants_and_services/")
# def get_consultants_and_services(
#     category: Optional[str] = Query(None, description="Selection category: 'consultant', 'all'"),
#     # category: str = Query(..., description="Selection category: 'consultant', 'all'"),
#     service_id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     if category == "consultant":
#         # Fetch consultants from the database
#         consultants = db_office_master.get_consultants(db)
#         # Convert consultants to a list of dictionaries
#         consultants_data = [{"id": consultant.employee_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
#         return EmployeeResponse(employees=consultants_data)

#     elif category == "all":
#         # Fetch all employees from the database
#         employees = db_office_master.get_all_non_consultant_employees(db)
#         # Convert employees to a list of dictionaries
#         employees_data = [{"id": employee.employee_id, "first_name": employee.first_name, "middle_name": employee.middle_name, "last_name": employee.last_name} for employee in employees]
#         return EmployeeResponse(employees=employees_data)
    
#     # elif service_id is not None and service_id != 0:
        
#     #     # Fetch consultants for the given service_id from off_view_consultant_details table
#     #     consultants = db_office_master.get_consultants_for_service(db, service_id)
#     #     # Convert consultants to a list of dictionaries
#     #     consultants_data = [{"id": consultant.consultant_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
#     #     return {"consultants": consultants_data}
    
#     else service_id = 0:
#         # Fetch all services from off_view_consultant_details table
#         services = db_office_master.get_all_service(db)
#         # Convert services to a list of dictionaries
#         services_data = [{"id": service.service_goods_master_id, "name": service.service_goods_name} for service in services]
#         return {"services": services_data}

@router.get("/consultants_and_services/")
def get_consultants_and_services(
    category: Optional[str] = Query(None, description="Selection category: 'consultant', 'all'"),
    service_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve consultants, non-consultant employees, or all services based on the provided category.

    Parameters:
    - category (str, optional): Selection category ('consultant', 'all').
    - service_id (int, optional): Identifier for filtering services by ID.

    Returns:
    - EmployeeResponse or dict: Depending on the category:
        - For 'consultant': JSON response containing a list of consultants.
        - For 'all': JSON response containing a list of non-consultant employees.
        - Otherwise: JSON response containing all services available.
    """
    if category == "consultant":
        # Fetch consultants from the database
        consultants = db_office_master.get_consultants(db)
        # Convert consultants to a list of dictionaries
        consultants_data = [{"id": consultant.employee_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
        return EmployeeResponse(employees=consultants_data)

    elif category == "all":
        # Fetch all employees from the database
        employees = db_office_master.get_all_non_consultant_employees(db)
        # Convert employees to a list of dictionaries
        employees_data = [{"id": employee.employee_id, "first_name": employee.first_name, "middle_name": employee.middle_name, "last_name": employee.last_name} for employee in employees]
        return EmployeeResponse(employees=employees_data)

    # elif service_id is not None and service_id != 0:
    #     # Fetch consultants for the given service_id from off_view_consultant_details table
    #     consultants = db_office_master.get_consultants_for_service(db, service_id)
    #     # Convert consultants to a list of dictionaries
    #     consultants_data = [{"id": consultant.consultant_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
    #     return {"consultants": consultants_data}
    
    else:
        # Fetch all services from off_view_consultant_details table
        services = db_office_master.get_all_service(db)
        # Ensure services is a list of dictionaries
        services_data = services  # Assuming get_all_service returns a list of dictionaries already
        return {"services": services_data}

#--------------------------------------------------------------------------------------------------------

@router.get("/get_consultants/")
def get_consultants(
    id: Optional[int] = None,
    service_id: Optional[int] = Query(None, description="ID of the service to retrieve consultants for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve consultants. 
    - Retrieve all consultants by setting id=0.
    - Retrieve consultants for a specific service by providing a valid service_id.
    """
    if service_id is not None and service_id != 0:
        consultants = db_office_master.get_consultants_for_service(db, service_id)
        if not consultants:
            raise HTTPException(status_code=404, detail="No consultants found for the given service ID")
        
        consultants_data = [
            {
                "id": consultant.consultant_id,
                "first_name": consultant.first_name,
                "middle_name": consultant.middle_name,
                "last_name": consultant.last_name
            } for consultant in consultants
        ]
        return {"service_id": service_id, "consultants": consultants_data}
    
    elif id == 0:
        consultants = db_office_master.get_consultants(db)
        if not consultants:
            raise HTTPException(status_code=404, detail="No consultants found")
        
        consultants_data = [
            {
                "id": consultant.employee_id,
                "first_name": consultant.first_name,
                "middle_name": consultant.middle_name,
                "last_name": consultant.last_name
            } for consultant in consultants
        ]
        return EmployeeResponse(employees=consultants_data)
    
    else:
        raise HTTPException(status_code=400, detail="Invalid request parameters")
#--------------------------------------------------------------------------------------------------------
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





#--------------------------------------------------------------------------------------------------------------
@router.get("/get_price_list/", response_model=PriceListResponse)
def get_price_list(
    service_type: Optional[str] = Query(None, description="Filter by type: 'ALL', 'GOODS', 'SERVICE'"),
    configuration_status: Optional[str] = Query(None, description="Filter by configuration status: 'ALL', 'CONFIGURED', 'NOTCONFIGURED'"),
    search: Optional[str] = Query(None, description="Search by service name"),
    db: Session = Depends(get_db)
):
    print(f"Received request with service_type: {service_type}, configuration_status: {configuration_status}, search: {search}")  # Debug print

    base_query = select([
        OffServiceGoodsMaster.id,
        OffServiceGoodsMaster.hsn_sac_class_id,
        AppHsnSacClasses.hsn_sac_class,
        OffServiceGoodsMaster.service_goods_name,
        OffServiceGoodsMaster.is_bundled_service,
        func.count(OffServiceGoodsPriceMaster.service_goods_master_id).label("configured_count")
    ]).select_from(
        OffServiceGoodsMaster.__table__.outerjoin(AppHsnSacClasses, OffServiceGoodsMaster.hsn_sac_class_id == AppHsnSacClasses.id)
        .outerjoin(OffServiceGoodsPriceMaster, OffServiceGoodsMaster.id == OffServiceGoodsPriceMaster.service_goods_master_id)
    ).group_by(
        OffServiceGoodsMaster.id
    ).order_by(
        OffServiceGoodsMaster.hsn_sac_class_id.desc(),
        OffServiceGoodsMaster.service_goods_name
    )

    conditions = []

    if service_type == "GOODS":
        conditions.append(OffServiceGoodsMaster.hsn_sac_class_id == 1)
    elif service_type == "SERVICE":
        conditions.append(OffServiceGoodsMaster.hsn_sac_class_id == 2)

    if configuration_status == "CONFIGURED":
        having_condition = func.count(OffServiceGoodsPriceMaster.service_goods_master_id) >= 1
    elif configuration_status == "NOTCONFIGURED":
        having_condition = func.count(OffServiceGoodsPriceMaster.service_goods_master_id) == 0

    if search:
        conditions.append(OffServiceGoodsMaster.service_goods_name.ilike(f"%{search}%"))

    if conditions:
        base_query = base_query.where(and_(*conditions))

    if configuration_status and configuration_status != "ALL":
        base_query = base_query.having(having_condition)

    results = db.execute(base_query).fetchall()
    services_data = [
        ServiceGoodsPrice(
            id=item.id,
            service_name=item.service_goods_name,
            service_type=item.hsn_sac_class,
            configuration_status="Configured" if item.configured_count >= 1 else "Not Configured",
            bundled_service="BUNDLED" if item.is_bundled_service == "yes" else "SINGLE",
        ) for item in results
    ]

    if not services_data:
        raise HTTPException(status_code=404, detail="No services found matching the criteria")

    return PriceListResponse(price_list=services_data)


# @router.get("/get_service_data/",response_model=List[ServiceModel])
# def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
#                               db: Session = Depends(get_db)):
#     # Call the function to get service data based on service_id
#     service_data = db_office_master.get_service_data(service_id, db)
#     return service_data

#---------------------------------------------------------------------------------------------------------------
# @router.get("/get_service_data/", response_model=List[ServiceModel])
# def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
#                               db: Session = Depends(get_db)):
#     # Call the function to get service data based on service_id
#     service_data = db_office_master.get_service_data(service_id, db)
#     return service_data



@router.get("/get_service_data/", response_model=List[ServiceModelSchema])
def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
                              db: Session = Depends(get_db)):
    # Call the function to get service data based on service_id
    service_data =db_office_master.get_service_data(service_id, db)
    return service_data
#---------------------------------------------------------------------------------------------------------------
@router.get("/get_price_history/", response_model=List[ServiceModel])
def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
                              db: Session = Depends(get_db)):
    service_data = db_office_master.get_price_history(service_id, db)
    if not service_data:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_data

#-------------------------------------------------------------------------------  
@router.post("/save_service_price/")
def save_service_price_endpoint(price_data: List[PriceData], 
                                id: int,
                                db: Session = Depends(get_db),
                                token: str = Depends(oauth2.oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    try:
        for data in price_data:
            db_office_master.save_price_data(data, user_id, db)
        return {"detail": "Price data saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#---------------------------------------------------------------------------------------------------------------
 



import datetime
@router.post("/add_price/", response_model=dict)
def add_price_to_service(
                        new_price: SetPriceModel,
                        service_id: int = Header(..., description="Service ID"),
                        db: Session = Depends(get_db),
                        token: str = Depends(oauth2.oauth2_scheme)):
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    
    try:
        # Retrieve the service's pricing history
        service = db.query(OffServiceGoodsPriceMaster).filter(OffServiceGoodsPriceMaster.id == service_id).first()

        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        # Set the current timestamp for the created_on field
        created_on = datetime.datetime.now()

        # Convert new_price to OffServiceGoodsPriceMaster model
        new_price_db = OffServiceGoodsPriceMaster(**new_price.dict(), created_by=user_id, created_on=created_on)

        # Check if there is an existing price entry
        existing_price = db.query(OffServiceGoodsPriceMaster).filter(
            OffServiceGoodsPriceMaster.service_goods_master_id == service_id,
            OffServiceGoodsPriceMaster.effective_to_date == None
        ).first()

        # If an existing price entry is found
        if existing_price:
            # Update the effective_to_date of the previous price entry
            existing_price.effective_to_date = new_price_db.effective_from_date - timedelta(days=1)

        # Insert the new price entry into the database
        db.add(new_price_db)
        db.commit()

        return {"success": True, "message": "Price added successfully"}

    except Exception as e:
        return {"success": False, "message": str(e)}
    



# @router.get("/get_bundle_price_list/{bundle_id}", response_model=Bundle)
# def get_bundled_service(bundle_id: int, db: Session = Depends(get_db)):
#     # Execute SQL query to fetch bundled service and items details
#     query = text("""
#         SELECT
#             a.id AS bundle_id,
#             a.service_goods_name AS service_name,
#             b.id AS goods_price_master_id,
#             b.service_goods_master_id,
#             b.constitution_id,
#             b.service_charge AS bundle_service_charge,
#             b.govt_agency_fee AS bundle_govt_agency_fee,
#             b.stamp_duty AS bundle_stamp_duty,
#             b.stamp_fee AS bundle_stamp_fee,
#             c.id AS service_goods_details_id,
#             c.service_goods_master_id AS item_id,
#             c.bundled_service_goods_id,
#             c.display_order,
#             a.service_goods_name AS item_name,
#             MAX(d.service_charge) AS item_service_charge,
#             MAX(d.govt_agency_fee) AS item_govt_agency_fee,
#             MAX(d.stamp_fee) AS item_stamp_fee,
#             MAX(d.stamp_duty) AS item_stamp_duty
#         FROM
#             off_service_goods_master AS a
#         JOIN
#             off_service_goods_price_master AS b ON a.id = b.service_goods_master_id
#         JOIN
#             off_service_goods_details AS c ON a.id = c.bundled_service_goods_id
#         JOIN
#             off_service_goods_price_master AS d ON c.service_goods_master_id = d.service_goods_master_id
#         WHERE
#             a.is_bundled_service = 'yes'
#             AND a.id = :bundle_id
#         GROUP BY
#             bundle_id, service_name, goods_price_master_id, service_goods_master_id, constitution_id, bundle_service_charge, bundle_govt_agency_fee, bundle_stamp_duty, bundle_stamp_fee, service_goods_details_id, item_id, bundled_service_goods_id, display_order, item_name
#     """)
#     query_result = db.execute(query, {"bundle_id": bundle_id}).fetchall()
    
#     # Check if bundled service exists
#     if not query_result:
#         raise HTTPException(status_code=404, detail="Bundled service not found")
    
#     # Process query result to organize it into the desired structure
#     bundle_data = {}
#     bundle_data['service_id'] = query_result[0]['bundle_id']
#     bundle_data['service_name'] = query_result[0]['service_name']
#     bundle_data['service_charge'] = query_result[0]['bundle_service_charge']
#     bundle_data['govt_agency_fee'] = query_result[0]['bundle_govt_agency_fee']
#     bundle_data['stamp_fee'] = query_result[0]['bundle_stamp_fee']
#     bundle_data['stamp_duty'] = query_result[0]['bundle_stamp_duty']

#     items = []
#     sub_item_total = {
#         'service_charge': 0,
#         'govt_agency_fee': 0,
#         'stamp_fee': 0,
#         'stamp_duty': 0
#     }
#     total_item_charge = {
#         'service_charge': 0,
#         'govt_agency_fee': 0,
#         'stamp_fee': 0,
#         'stamp_duty': 0
#     }

#     for row in query_result:
#         item = {
#             'id': row['service_goods_details_id'],
#             'name': row['item_name'],
#             'service_goods_master_id': row['item_id'],
#             'bundled_service_goods_id': row['bundled_service_goods_id'],
#             'display_order': row['display_order'],
#             'service_charge': row['item_service_charge'],
#             'govt_agency_fee': row['item_govt_agency_fee'],
#             'stamp_fee': row['item_stamp_fee'],
#             'stamp_duty': row['item_stamp_duty']
#         }
#         items.append(item)
        
#         # Summing item-specific details
#         total_item_charge['service_charge'] += row['item_service_charge']
#         total_item_charge['govt_agency_fee'] += row['item_govt_agency_fee']
#         total_item_charge['stamp_fee'] += row['item_stamp_fee']
#         total_item_charge['stamp_duty'] += row['item_stamp_duty']

#     # Update sub_item_total with the sum of all item charges
#     sub_item_total['service_charge'] = total_item_charge['service_charge']
#     sub_item_total['govt_agency_fee'] = total_item_charge['govt_agency_fee']
#     sub_item_total['stamp_fee'] = total_item_charge['stamp_fee']
#     sub_item_total['stamp_duty'] = total_item_charge['stamp_duty']

#     bundle_data['items'] = items

#     # Calculate grand total
#     grand_total = {
#         'service_charge': bundle_data['service_charge'] + sub_item_total['service_charge'],
#         'govt_agency_fee': bundle_data['govt_agency_fee'] + sub_item_total['govt_agency_fee'],
#         'stamp_fee': bundle_data['stamp_fee'] + sub_item_total['stamp_fee'],
#         'stamp_duty': bundle_data['stamp_duty'] + sub_item_total['stamp_duty']
#     }

#     # Update sub_item_total and grand_total in the bundle
#     bundle_data['sub_item_total'] = sub_item_total
#     bundle_data['grand_total'] = grand_total

#     # Return the bundle data
#     return bundle_data

@router.get("/get_bundle_price_list/{bundle_id}", response_model=Bundle)
def get_bundled_service(bundle_id: int, db: Session = Depends(get_db)):
    # Execute SQL query to fetch bundled service and items details
    query = text("""
        SELECT DISTINCT
            a.id AS bundle_id,
            a.service_goods_name AS service_name,
            b.id AS goods_price_master_id,
            b.service_goods_master_id,
            b.constitution_id,
            b.service_charge AS bundle_service_charge,
            b.govt_agency_fee AS bundle_govt_agency_fee,
            b.stamp_duty AS bundle_stamp_duty,
            b.stamp_fee AS bundle_stamp_fee,
            c.id AS service_goods_details_id,
            c.service_goods_master_id AS item_id,
            c.bundled_service_goods_id,
            c.display_order,
            a.service_goods_name AS item_name,
            SUM(b.service_charge) AS total_item_service_charge,
            SUM(b.govt_agency_fee) AS total_item_govt_agency_fee,
            SUM(b.stamp_fee) AS total_item_stamp_fee,
            SUM(b.stamp_duty) AS total_item_stamp_duty
        FROM
            off_service_goods_master AS a
        JOIN
            off_service_goods_price_master AS b ON a.id = b.service_goods_master_id
            AND (b.effective_from_date <= :current_date AND b.effective_to_date >= :current_date) -- Filter based on effective date range
        JOIN
            off_service_goods_details AS c ON a.id = c.bundled_service_goods_id
        WHERE
            a.is_bundled_service = 'yes'
            AND a.id = :bundle_id
        GROUP BY
            bundle_id, service_name, goods_price_master_id, service_goods_master_id, constitution_id, bundle_service_charge, bundle_govt_agency_fee, bundle_stamp_duty, bundle_stamp_fee, service_goods_details_id, item_id, bundled_service_goods_id, display_order, item_name
    """)
    query_result = db.execute(
        query, {"bundle_id": bundle_id, "current_date": datetime.now()}
    ).fetchall()

    # Check if bundled service exists
    if not query_result:
        raise HTTPException(status_code=404, detail="Bundled service not found")

    # Process query result to organize it into the desired structure
    bundle_data = {}
    bundle_data["service_id"] = query_result[0]["bundle_id"]
    bundle_data["service_name"] = query_result[0]["service_name"]
    bundle_data["service_charge"] = query_result[0]["bundle_service_charge"]
    bundle_data["govt_agency_fee"] = query_result[0]["bundle_govt_agency_fee"]
    bundle_data["stamp_fee"] = query_result[0]["bundle_stamp_fee"]
    bundle_data["stamp_duty"] = query_result[0]["bundle_stamp_duty"]

    items = []
    sub_item_total = {
        "service_charge": 0,
        "govt_agency_fee": 0,
        "stamp_fee": 0,
        "stamp_duty": 0,
    }
    total_item_charge = {
        "service_charge": 0,
        "govt_agency_fee": 0,
        "stamp_fee": 0,
        "stamp_duty": 0,
    }

    for row in query_result:
        item = {
            "id": row["service_goods_details_id"],
            "name": row["item_name"],
            "service_goods_master_id": row["item_id"],
            "bundled_service_goods_id": row["bundled_service_goods_id"],
            "display_order": row["display_order"],
            "service_charge": row["item_service_charge"],
            "govt_agency_fee": row["item_govt_agency_fee"],
            "stamp_fee": row["item_stamp_fee"],
            "stamp_duty": row["item_stamp_duty"],
        }
        items.append(item)

        # Summing item-specific details
        total_item_charge["service_charge"] += row["item_service_charge"]
        total_item_charge["govt_agency_fee"] += row["item_govt_agency_fee"]
        total_item_charge["stamp_fee"] += row["item_stamp_fee"]
        total_item_charge["stamp_duty"] += row["item_stamp_duty"]

    # Update sub_item_total with the sum of all item charges
    sub_item_total["service_charge"] = total_item_charge["service_charge"]
    sub_item_total["govt_agency_fee"] = total_item_charge["govt_agency_fee"]
    sub_item_total["stamp_fee"] = total_item_charge["stamp_fee"]
    sub_item_total["stamp_duty"] = total_item_charge["stamp_duty"]

    bundle_data["items"] = items

    # Calculate grand total
    grand_total = {
        "service_charge": bundle_data["service_charge"] + sub_item_total["service_charge"],
        "govt_agency_fee": bundle_data["govt_agency_fee"] + sub_item_total["govt_agency_fee"],
        "stamp_fee": bundle_data["stamp_fee"] + sub_item_total["stamp_fee"],
        "stamp_duty": bundle_data["stamp_duty"] + sub_item_total["stamp_duty"],
    }

    # Update sub_item_total and grand_total in the bundle
    bundle_data["sub_item_total"] = sub_item_total
    bundle_data["grand_total"] = grand_total

    # Return the bundle data
    return bundle_data


@router.get("/test/get_bundle_price_list/{bundle_id}", response_model=Bundle)
def get_bundled_service(bundle_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            a.id AS bundle_id,
            a.service_goods_name AS service_name,
            b.id AS goods_price_master_id,
            b.service_goods_master_id,
            b.constitution_id,
            b.service_charge AS bundle_service_charge,
            b.govt_agency_fee AS bundle_govt_agency_fee,
            b.stamp_duty AS bundle_stamp_duty,
            b.stamp_fee AS bundle_stamp_fee,
            c.id AS service_goods_details_id,
            c.service_goods_master_id AS item_id,
            c.bundled_service_goods_id,
            c.display_order,
            d.service_goods_name AS item_name,
            SUM(e.service_charge) AS total_item_service_charge,
            SUM(e.govt_agency_fee) AS total_item_govt_agency_fee,
            SUM(e.stamp_fee) AS total_item_stamp_fee,
            SUM(e.stamp_duty) AS total_item_stamp_duty
        FROM
            off_service_goods_master AS a
        JOIN
            off_service_goods_price_master AS b ON a.id = b.service_goods_master_id
        JOIN
            off_service_goods_details AS c ON a.id = c.bundled_service_goods_id
        JOIN
            off_service_goods_master AS d ON c.service_goods_master_id = d.id
        JOIN
            off_service_goods_price_master AS e ON d.id = e.service_goods_master_id
            AND (e.effective_from_date <= :current_date AND e.effective_to_date >= :current_date)
        WHERE
            a.is_bundled_service = 'yes'
            AND a.id = :bundle_id
        GROUP BY
            bundle_id, service_name, goods_price_master_id, service_goods_master_id, constitution_id, bundle_service_charge, bundle_govt_agency_fee, bundle_stamp_duty, bundle_stamp_fee, service_goods_details_id, item_id, bundled_service_goods_id, display_order, item_name
        ORDER BY
            c.display_order;
    """)

    query_result = db.execute(
        query, {"bundle_id": bundle_id, "current_date": datetime.now()}
    ).fetchall()

    if not query_result:
        raise HTTPException(status_code=404, detail="Bundled service not found")

    bundle_data = {
        "service_id": query_result[0]["bundle_id"],
        "service_name": query_result[0]["service_name"],
        "service_charge": query_result[0]["bundle_service_charge"],
        "govt_agency_fee": query_result[0]["bundle_govt_agency_fee"],
        "stamp_fee": query_result[0]["bundle_stamp_fee"],
        "stamp_duty": query_result[0]["bundle_stamp_duty"],
    }

    items = []
    sub_item_total = {"service_charge": 0, "govt_agency_fee": 0, "stamp_fee": 0, "stamp_duty": 0}
    total_item_charge = {"service_charge": 0, "govt_agency_fee": 0, "stamp_fee": 0, "stamp_duty": 0}

    for row in query_result:
        item = {
            "id": row["service_goods_details_id"],
            "name": row["item_name"],
            "service_goods_master_id": row["item_id"],
            "bundled_service_goods_id": row["bundled_service_goods_id"],
            "display_order": row["display_order"],
            "service_charge": row["total_item_service_charge"],
            "govt_agency_fee": row["total_item_govt_agency_fee"],
            "stamp_fee": row["total_item_stamp_fee"],
            "stamp_duty": row["total_item_stamp_duty"],
        }
        items.append(item)

        total_item_charge["service_charge"] += row["total_item_service_charge"]
        total_item_charge["govt_agency_fee"] += row["total_item_govt_agency_fee"]
        total_item_charge["stamp_fee"] += row["total_item_stamp_fee"]
        total_item_charge["stamp_duty"] += row["total_item_stamp_duty"]

    sub_item_total["service_charge"] = total_item_charge["service_charge"]
    sub_item_total["govt_agency_fee"] = total_item_charge["govt_agency_fee"]
    sub_item_total["stamp_fee"] = total_item_charge["stamp_fee"]
    sub_item_total["stamp_duty"] = total_item_charge["stamp_duty"]

    bundle_data["items"] = items

    grand_total = {
        "service_charge": bundle_data["service_charge"] + sub_item_total["service_charge"],
        "govt_agency_fee": bundle_data["govt_agency_fee"] + sub_item_total["govt_agency_fee"],
        "stamp_fee": bundle_data["stamp_fee"] + sub_item_total["stamp_fee"],
        "stamp_duty": bundle_data["stamp_duty"] + sub_item_total["stamp_duty"],
    }

    bundle_data["sub_item_total"] = sub_item_total
    bundle_data["grand_total"] = grand_total

    return bundle_data


#---------------------------------------------------------------------------------------
@router.get('/services/get_all_service_document_data_master', response_model=Union[List[OffViewServiceDocumentsDataMasterSchema], dict])
def get_all_service_document_data_master(
    db: Session = Depends(get_db),
    name: Optional[str] = None,
    group_id: Union[int, str] = Query('ALL'),
    sub_group_id: Union[int, str] = Query('ALL'),
    category_id: Union[int, str] = Query('ALL'),
    sub_category_id: Union[int, str] = Query('ALL'),
    constitution_id: Union[int, str] = Query('ALL'),
    doc_data_status: Optional[str] = Query(None, description="Filter by type: 'CONFIGURED', 'NOT CONFIGURED'"),
    token: str = Depends(oauth2.oauth2_scheme)
) -> Union[List[OffViewServiceDocumentsDataMasterSchema], Dict[str, Any]]:
    
    
    """
    Allows users to search and filter service document data master records by the following criteria:
    
    - **name**: Search for records that contain the provided name as a substring.
    
    - **group_id**: Filter records by group ID. Use 'ALL' to include all group IDs.
    
    - **sub_group_id**: Filter records by sub-group ID. Use 'ALL' to include all sub-group IDs.
    
    - **category_id**: Filter records by category ID. Use 'ALL' to include all category IDs.
    
    - **sub_category_id**: Filter records by sub-category ID. Use 'ALL' to include all sub-category IDs.
    
    - **constitution_id**: Filter records by constitution ID. Use 'ALL' to include all constitution IDs.
    
    - **doc_data_status**: Filter by document data status. Possible values are:
      - 'CONFIGURED'
      - 'NOT CONFIGURED'

    Returns:
        - A list of service document data master records matching the specified filters.
        - If no records are found, a message indicating that no data is present.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    try:
        results = db_office_master.get_all_service_document_data_master(
            db, name, group_id, sub_group_id, category_id, sub_category_id, constitution_id, doc_data_status
        )

        if not results:
            return {"message": "No data present"}
        
        # Remove 'details' attribute if doc_data_status is 'NOT CONFIGURED'
        for result in results:
            if result.get("doc_data_status") == "NOT CONFIGURED" and "details" in result:
                del result["details"]

        # Ensure the response is correctly encoded as JSON
        return JSONResponse(content=jsonable_encoder(results), status_code=200)
        #return results

    except Exception as e:
       # logging.error(f"Error fetching service document data master: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
#-----------------------------------------------------------------------------------------
@router.get('/services/get_service_documents_list_by_group_category', response_model=Union[List[ServiceDocumentsList_Group], List[Service_Group]])
def get_service_documents_list_by_group_category(
    group_id: Optional[int] = None,
    sub_group_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of service documents filtered by group, sub-group, and category.

    Parameters:
    - **group_id**: Optional query parameter to filter documents by group ID.
    - **sub_group_id**: Optional query parameter to filter documents by sub-group ID.
    - **category_id**: Optional query parameter to filter documents by category ID.
      If all arguments are null or group_id == 0, then get all groups.

    Returns:
    - A list of filtered service documents that match the provided criteria.
    - If no matching documents are found, returns a 404 status code with a message "No data found".
    - If an internal server error occurs, returns a 500 status code with a message "Internal Server Error".
    """
    try:
        results = db_office_master.get_service_documents_list_by_group_category(
            db, group_id, sub_group_id, category_id)
            
        if not results:
            return JSONResponse(status_code=404, content={"message": "No data found"})
        
        # If the results are a list of Service_Group objects
        if isinstance(results[0], Service_Group):
            return JSONResponse(status_code=200, content={"group": [result.dict() for result in results]})

        # Filter out null fields from each ServiceDocumentsList_Group object
        filtered_results = [
            {k: v for k, v in result.dict().items() if v is not None}
            for result in results
        ]

        # Ensure the response is a list of dictionaries matching the schema
        return JSONResponse(status_code=200, content=filtered_results)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




#---------------------------------------------------------------------------------------
@router.get('/services/get_service_documents_data_details', response_model=List[OffViewServiceDocumentsDataDetailsDocCategory])
def get_service_documents_data_details(
    service_id: int,
    document_category: Optional[str] = Query(None, title="Select document category", 
                                            enum=['PERSONAL DOC', 'CONSTITUTION DOC', 'PRINCIPAL PLACE DOC', 'UTILITY DOC', 'DATA TO BE SUBMITTED']),         
    db: Session = Depends(get_db)
):
    """
    Retrieve service document details based on specified criteria.

    Parameters:
    - **service_id**: Required parameter to filter by service ID.
    - **document_category**: Optional parameter to filter by document category.
    - Return a list of documents details with the selected category for the specified service_id.
    
    Possible values for `document_category` include:
    - 'PERSONAL DOC'
    - 'CONSTITUTION DOC'
    - 'PRINCIPAL PLACE DOC'
    - 'UTILITY DOC'
    - 'DATA TO BE SUBMITTED'

    Returns:
    - Returns all document details for the specified service_id and 'document_category'.
    - If no records are found, return {'message': 'No data found'}.
    """
    try:
        results = db_office_master.get_service_documents_data_details(db, service_id, document_category)

        if not results:
            return JSONResponse(status_code=404, content={"message": "No data found"})

        # Group the results by document category
        grouped_results = {}
        for result in results:
            if result.document_data_category_id not in grouped_results:
                grouped_results[result.document_data_category_id] = {
                    "document_data_category_id": result.document_data_category_id,
                    "document_data_category_category_name": result.document_data_category_category_name,
                    "details": []
                }
            grouped_results[result.document_data_category_id]["details"].append(result)

        # Convert grouped_results dict to List[OffViewServiceDocumentsDataDetailsDocCategory]
        final_results = list(grouped_results.values())

        return final_results

    except Exception as e:
        # logging.error(f"Error fetching service documents details: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





#------------------------------------------------------------------------------------------------
###################CONSULTANTS AND SERVICES####################################################
#------------------------------------------------------------------------------------------------

from datetime import datetime

@router.get("/consultant_employees", response_model=List[ConsultantEmployee])
def get_consultant_employees(
    db: Session = Depends(get_db),
    search_query: str = Query(None, description="Search query to filter consultant employees")
):
    current_date = datetime.utcnow().date()
    query = db.query(
        EmployeeMaster.employee_id,
        func.concat(EmployeeMaster.first_name, ' ', EmployeeMaster.middle_name, ' ', EmployeeMaster.last_name).label('employee_name'),
        EmployeeMaster.employee_number,
        EmployeeContactDetails.personal_email_id.label('personal_email'),
        EmployeeContactDetails.official_email_id.label('official_email'),
        EmployeeContactDetails.personal_mobile_number.label('personal_mobile'),
        EmployeeContactDetails.official_mobile_number.label('official_mobile'),
        HrDepartmentMaster.department_name,
        HrDesignationMaster.designation
    ).join(
        EmployeeEmployementDetails,
        EmployeeMaster.employee_id == EmployeeEmployementDetails.employee_id
    ).join(
        EmployeeContactDetails,
        EmployeeMaster.employee_id == EmployeeContactDetails.employee_id
    ).join(
        HrDepartmentMaster,
        EmployeeEmployementDetails.department_id == HrDepartmentMaster.id
    ).join(
        HrDesignationMaster,
        EmployeeEmployementDetails.designation_id == HrDesignationMaster.id
    ).filter(
        EmployeeEmployementDetails.is_consultant == 'yes',
        EmployeeEmployementDetails.effective_from_date <= current_date,
        (EmployeeEmployementDetails.effective_to_date == None) | (EmployeeEmployementDetails.effective_to_date >= current_date),
        EmployeeMaster.is_deleted == 'no',
        EmployeeEmployementDetails.is_deleted == 'no',
        EmployeeContactDetails.is_deleted == 'no'
    )

    if search_query:
        search_filter = (
            EmployeeMaster.first_name.ilike(f"%{search_query}%") |
            EmployeeMaster.middle_name.ilike(f"%{search_query}%") |
            EmployeeMaster.last_name.ilike(f"%{search_query}%") |
            EmployeeMaster.employee_number.ilike(f"%{search_query}%") |
            EmployeeContactDetails.personal_email_id.ilike(f"%{search_query}%") |
            EmployeeContactDetails.official_email_id.ilike(f"%{search_query}%") |
            EmployeeContactDetails.personal_mobile_number.ilike(f"%{search_query}%") |
            EmployeeContactDetails.official_mobile_number.ilike(f"%{search_query}%")
        )
        query = query.filter(search_filter)

    return query.all()





@router.post("/save_consultant_service_details/")
def save_consultant_service_details(
    data: List[ConsultantService],
    action_type: RecordActionType,
    consultant_id: Optional[int] = None,
    service_id: Optional[int] = None,
    id: Optional[int] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save or update consultant service details.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    
    try:
        for item in data:
            db_office_master.save_consultant_service_details_db(
                item, consultant_id, service_id, user_id, action_type, db, id
            )
        
        return {"success": True, "detail": "Saved successfully"}
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

     
#------------------------------------------------------------------------------------------------
@router.get("/get_service_details_by_consultant/", response_model=ConsultantServiceDetailsListResponse)
def get_service_details_by_consultant(
    consultant_id: int = Header(..., description="Consultant ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve the currently active consultant service details.
    """
    current_date = datetime.now().date()


    query = """
    SELECT
        a.id,
        a.consultant_id,
        a.service_goods_master_id,
        b.service_goods_name,
        a.consultation_fee,
        a.slot_duration_in_minutes,
        a.effective_from_date,
        a.effective_to_date
    FROM 
        off_consultant_service_details AS a
    JOIN 
        off_service_goods_master AS b ON a.service_goods_master_id = b.id
    WHERE 
        a.consultant_id = :consultant_id
        AND a.effective_from_date <= CURDATE()
        AND (a.effective_to_date IS NULL OR a.effective_to_date >= CURDATE());
    """

    result = db.execute(text(query), {"consultant_id": consultant_id}).fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="No active records found")

    services = [
        ConsultantServiceDetailsResponse(
            id=row.id,
            consultant_id=row.consultant_id,
            service_goods_master_id=row.service_goods_master_id,
            service_goods_name=row.service_goods_name,
            consultation_fee=row.consultation_fee,
            slot_duration_in_minutes=row.slot_duration_in_minutes,
            effective_from_date=row.effective_from_date,
            effective_to_date=row.effective_to_date
        )
        for row in result
    ]

    return ConsultantServiceDetailsListResponse(services=services)
#------------------------------------------------------------------------------------------------

# @router.post("/save_consultant_schedule/")
# def save_consultant_schedule(
#     schedules: List[ConsultantScheduleCreate], 
#     action_type: RecordActionType,
#     id: Optional[int] = None,
#     consultant_id: Optional[int] = None,  # Make consultant_id optional
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")
    
#     try:
#         for data in schedules:
#             db_office_master.save_consultant_schedule(data, consultant_id, user_id, id, action_type, db)
        
#         return {"success": True, "detail": "Saved successfully"}
    
#     except Exception as e:
#         print(f"Error in endpoint: {e}")
#         raise HTTPException(status_code=400, detail=str(e))



@router.post("/save_consultant_schedule/")
def save_consultant_schedule(
    schedules: List[ConsultantScheduleCreate], 
    action_type: RecordActionType,
    id: Optional[int] = None,
    consultant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    
    try:
        for data in schedules:
            db_office_master.save_consultant_schedule(data, consultant_id, user_id, id, action_type, db)
        
        return {"success": True, "detail": "Saved successfully"}
    
    except Exception as e:
        print(f"Error in endpoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    
    
    
        
from fastapi import Query
@router.get("/get_time_slots/", response_model=List[TimeSlotResponse])
def get_time_slots(
    slot: str = Query(..., description="Type of time slots to fetch: 'NORMAL' or 'SPECIAL'"),
    consultant_id: int = Header(..., description="Consultant ID"),
    db: Session = Depends(get_db)
):
    try:
        slot = slot.upper()  # Convert slot to uppercase for comparison

        if slot == 'NORMAL':
            # Retrieve Normal Time Slots
            time_slots = db.query(
                OffConsultantSchedule,
                AppDayOfWeek.day_long_name,
                OffConsultationMode.consultation_mode
            ).join(
                AppDayOfWeek, OffConsultantSchedule.day_of_week_id == AppDayOfWeek.id
            ).join(
                OffConsultationMode, OffConsultantSchedule.consultation_mode_id == OffConsultationMode.id
            ).filter(
                OffConsultantSchedule.is_normal_schedule == 'yes',
                OffConsultantSchedule.consultant_id == consultant_id,
                OffConsultantSchedule.effective_from_date <= datetime.utcnow().date(),
                or_(
                    OffConsultantSchedule.effective_to_date >= datetime.utcnow().date(),
                    OffConsultantSchedule.effective_to_date.is_(None)
                )
            ).all()
        elif slot == 'SPECIAL':
            # Retrieve Special Time Slots
            time_slots = db.query(
                OffConsultantSchedule,
                AppDayOfWeek.day_long_name,
                OffConsultationMode.consultation_mode
            ).join(
                AppDayOfWeek, OffConsultantSchedule.day_of_week_id == AppDayOfWeek.id
            ).join(
                OffConsultationMode, OffConsultantSchedule.consultation_mode_id == OffConsultationMode.id
            ).filter(
                OffConsultantSchedule.is_normal_schedule == 'no',
                OffConsultantSchedule.consultant_id == consultant_id
            ).all()
        else:
            raise HTTPException(status_code=400, detail="Invalid slot type. Please specify 'NORMAL' or 'SPECIAL'.")

        result = []
        for slot, day_long_name, consultation_mode in time_slots:
            slot_dict = slot.__dict__.copy()
            slot_dict['day_long_name'] = day_long_name
            slot_dict['consultation_mode'] = consultation_mode
            result.append(TimeSlotResponse(**slot_dict))

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#------------------------------------------------------------------------------------------------
###################ENQUIRY####################################################
#------------------------------------------------------------------------------------------------
@router.post("/enquiry/save_enquiry_details/{id}")
def save_enquiry_details(
    id: int,
    enquiry_data: OffEnquiryResponseSchema,
    
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
   - Save or create enquiry details for a specific ID.
    - **enquiry_data**: Data for the enquiry master and details, provided as parameters of type OffEnquiryResponseSchema.
    - **id**: An optional integer parameter with a default value of 0, indicating the enquiry master's identifier.
    
    - If enquiry_master id is 0, it indicates the creation of a new enquiry.
    - Returns: The newly created enquiry details as the response.
    - If enquiry_master id is not 0, it indicates the update of an existing enquiry.
    - Returns: The updated enquiry details as the response.
    
    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        result = db_office_master.save_enquiry_master(
            db, id, enquiry_data, user_id
        )

        return {"success": True, "message": "Saved successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/enquiry/get_enquiries", response_model=List[OffViewEnquiryResponseSchema])
def get_and_search_enquiries(
    search_value: Union[str, int] = "ALL",
    status_id: Optional[str] = "ALL",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve Enquiry based on Parameters.

    Parameters:
    - **search_value**: Search value Can be 'mobile_number',and other are default 
    - **status_id**: Status ID.
    - **effective_from_date**: Effective from date (default: today's date).
    - **effective_to_date**: Effective to date (default: today's date).
    - **search_value**: Search value Can be 'mobile_number', 'email_id', or 'ALL'.
    """
    return db_office_master.get_enquiries(
        db,
        search_value=search_value,
        status_id=status_id,
        from_date=from_date,
        to_date=to_date
    )



@router.get("/get/consultation_tools/{mode_id}", response_model=Union[List[ConsultationModeSchema], List[ConsultationToolSchema]])
def get_consultation_modes_with_tools(
    mode_id: int = 0,
    db: Session = Depends(get_db)
):
    result = db_office_master.get_consultation_tools(db, mode_id)
    if mode_id != 0 and not result:
        raise HTTPException(status_code=404, detail=f"Consultation tools for mode id {mode_id} not found")
    return result


#-----------------------------------------------------------------------------------------------------
#    TASK LIST

#-------------------------------------------------------------------------------------------------------
@router.post("/services/save_off_consultation_task_master/{id}")
def save_off_consultation_task_master(
    id: int,
    data: OffConsultationTaskMasterSchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save or update consultation task master and its details.

    Parameters:
    - **id**: ID of the task master. Should be 0 for insert and greater than 0 for update.
    - **data**: OffConsultationTaskMasterSchema containing task master and its details.
    
    Returns:
    - Success message indicating the operation (save/update) was successful.
    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        result = db_office_master.save_off_consultation_task_master(
            db, id, data, user_id
        )

        return {"success": True, "message": result["message"]}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
#-----------------------------------------------------------------------------------------

@router.get('/services/get_all_consultation_task_master_details', response_model=Union[List[OffViewConsultationTaskMasterSchema], dict])
def get_all_consultation_task_master_details(
    db: Session = Depends(get_db),
    service_id: Union[int, str] = Query("ALL"),
    task_status: Union[int, str] = Query("ALL"),
    consultation_mode: Union[int, str] = Query("ALL"),
    tool: Union[int, str] = Query("ALL"),
    consultant_id: Union[int, str] = Query("ALL"),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    token: str = Depends(oauth2.oauth2_scheme)
) -> Union[List[OffViewConsultationTaskMasterSchema], dict]:
    """
    Retrieve consultation task master details with optional filters.
    
    - `service_id`: Filter by service_id or 'ALL' for all services.
    - `task_status`: Filter by task status or 'ALL' for all statuses.
    - `consultation_mode`: Filter by consultation mode or 'ALL' for all modes.
    - `tool`: Filter by consultation tool or 'ALL' for all tools.
    - `consultant_id`: Filter by consultant ID or 'ALL' for all consultants.
    - `from_date`: Optional. Filter tasks from this date onwards.(default None)
    - `to_date`: Optional. Filter tasks up to this date.(default None)
    
    """
    
    try:
        if not token:
            raise HTTPException(status_code=401, detail="Token is missing")

        results = db_office_master.get_all_consultation_task_master_details(
            db, service_id, task_status, consultation_mode, tool, consultant_id, from_date, to_date
        )

        if not results:
            return {"message": "No data present"}
        
        # Filter out null fields and convert datetime objects to strings
        filtered_results = [
            {
                attribute_name: value.isoformat() if isinstance(value, datetime) else value 
                for attribute_name, value in result.dict().items() if value not in [None, [], {}]
            }
            for result in results
        ]

        return JSONResponse(status_code=200, content=filtered_results)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

#--------------------------------------------------------------------------------------------
# WORK ORDER


#--------------------------------------------------------------------------------------------


@router.get('/services/get_all_services', response_model=Union[List[OffViewServiceGoodsMasterDisplay], dict])
def get_all_services(
    service_type: str = Query(enum=["ALL", "SINGLE SERVICE", "BUNDLE SERVICE"]),
    has_consultation: str = Query(enum=["ALL", "Yes", "No"]),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get all services from service_goods_master with the search  filters
     

    - `service_type` (str): Type of the service. Can be 'ALL', 'SINGLE SERVICE', or 'BUNDLE SERVICE'.
          Filter services based on whether they are single services or bundled services.
    - `service_has_consultant` (str): Specifies if the service has a consultant. Can be 'ALL', 'Yes', or 'No'.
          Filter services based on whether they have a consultant.
        
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    results = db_office_master.get_all_services_from_service_master(
        db, service_type, has_consultation
    )

    # Check if no data is found
    if not results:
        return {"message": "No data present"}

    # Remove the "details" field if there are no details available
    for result in results:
        if result.is_bundled_service == "no" or not result.details:
            delattr(result, "details")

    return results

