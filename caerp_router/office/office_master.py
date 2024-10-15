import io
import os
from shutil import Error
from fastapi import APIRouter, Body, Depends, HTTPException, Header, UploadFile, File,status,Query,Response
from fastapi.responses import JSONResponse, StreamingResponse
import sqlalchemy
from sqlalchemy.orm import Session
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import  ActionType, ApplyTo, BooleanFlag, DeletedStatus, EntryPoint, RecordActionType,SearchCriteria, Status
from caerp_db.common.models import  AppActivityHistory, EmployeeContactDetails, EmployeeEmploymentDetails, EmployeeMaster
from caerp_db.database import  get_db
from caerp_db.hr_and_payroll.model import EmployeeTeamMaster, HrDepartmentMaster, HrDesignationMaster
from caerp_db.office import db_office_master
from typing import Union,List,Dict,Any
from caerp_db.office.models import AppDayOfWeek , OffConsultantSchedule, OffConsultationMode,  OffServiceGoodsPriceMaster, OffServiceTaskHistory
# from caerp_router.office.crud import call_get_service_details
from caerp_schema.common.common_schema import BusinessActivityMasterSchema, BusinessActivitySchema
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import SaveEmployeeTeamMaster
from caerp_schema.office.office_schema import   AppointmentStatusConstants, BundledServiceData,  ConsultantEmployee, ConsultantScheduleCreate, ConsultantService, ConsultantServiceDetailsListResponse, ConsultantServiceDetailsResponse, ConsultationModeSchema, ConsultationToolSchema, CreateWorkOrderDependancySchema, CreateWorkOrderRequest, CreateWorkOrderSetDtailsRequest, DocumentsSchema, EmployeeResponse, OffAppointmentDetails, OffAppointmentMasterSchema, OffConsultationTaskMasterSchema, OffDocumentDataBase, OffDocumentDataMasterBase, OffEnquiryResponseSchema, OffOfferMasterSchemaResponse, OffServiceTaskHistorySchema, OffServiceTaskMasterSchema, OffViewConsultationTaskMasterSchema, OffViewEnquiryResponseSchema, OffViewServiceDocumentsDataDetailsDocCategory, OffViewServiceDocumentsDataDetailsSchema, OffViewServiceDocumentsDataMasterSchema, OffViewServiceGoodsMasterDisplay, OffViewServiceTaskMasterSchema,  OffViewWorkOrderMasterSchema, PriceData, PriceListResponse,RescheduleOrCancelRequest, ResponseSchema, SaveOfferDetails, SaveServiceDocumentDataMasterRequest, SaveServicesGoodsMasterRequest, Service_Group,  ServiceDocumentsList_Group, ServiceGoodsPrice, ServiceModel, ServiceModelSchema, ServiceRequest, ServiceResponse, ServiceTaskMasterAssign, SetPriceModel,  TimeSlotResponse, UpdateCustomerDataDocumentSchema, WorkOrderDependancySchema
from caerp_auth import oauth2
# from caerp_constants.caerp_constants import SearchCriteria
from typing import Optional
from datetime import date
from sqlalchemy import insert, text,null
# from datetime import datetime
from sqlalchemy import select, func,or_
from fastapi.encoders import jsonable_encoder
from pathlib import Path 

from sqlalchemy import select, func, and_
from collections import defaultdict
from settings import BASE_URL


router = APIRouter(
    tags=['Office Master']
)

UPLOAD_DIR_CONSULTANT_DETAILS       = "uploads/consultant_details"
UPLOAD_WORK_ORDER_DOCUMENTS         ="uploads/work_order_documents"

#--------------------save_appointment_details-------------------------------------------------------
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
@router.get('/get_appointment_details_by_id', response_model=OffAppointmentMasterSchema)
def get_appointment_details_by_id(
    appointment_master_id: int,
    db: Session = Depends(get_db)
):
    results = db_office_master.get_appointment_details(appointment_master_id, db)
    if not results:
        return JSONResponse(status_code=404, content={"message": "No data present"})
    return results
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
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    mobile_number: Optional[str] = None,
    id: Optional[int] = 0,
    search_value: Union[str, int] = "ALL",
    db: Session = Depends(get_db)
):
    """
    Retrieve Appointment based on Parameters.

    Parameters:
    
    - **consultant_id**: consultant ID.
    - **service_id**: service ID.
    - **status_id**: status ID.
    - **effective_from_date**: Effective from date (default: today's date).
    - **effective_to_date**: Effective to date (default: today's date).
    - **search_value**: Search value Can be 'mobile_number', 'email_id', or 'ALL'.
    - **mobile_number**: Search with 'mobile_number' to get the specific details.

    """
    result = db_office_master.get_appointments(
        db,
        consultant_id=consultant_id,
        service_id=service_id,
        status_id=status_id,
        from_date=from_date,
        to_date=to_date,
        mobile_number=mobile_number,
        id=id,
        search_value=search_value
    )
    return {"Appointments": result}



#-------------------------swathy-------------------------------------------------------------------------------



from time import time
@router.get('/services/get_all_service_goods_master', response_model=Union[List[OffViewServiceGoodsMasterDisplay], dict])
def get_all_service_goods_master(
    deleted_status: Optional[DeletedStatus] = Query(None, title="Select deleted status", enum=list(DeletedStatus)),
    service_goods_name: Optional[str] = Query(None),
    service_goods_type: Union[int, str] = Query("ALL", description="Filter by hsn_sac_class_id. Use 1 for goods, 2 for services, or 'ALL' for both."),
    group_id: Union[int, str] = Query("ALL"),
    sub_group_id: Union[int, str] = Query("ALL"),
    category_id: Union[int, str] = Query("ALL"),
    sub_category_id: Union[int, str] = Query("ALL"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get all service goods master
    This endpoint retrieves a list of service goods masters based on the provided filters.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    start_time = time()  # Capture start time

    results = db_office_master.get_all_service_goods_master(
        db, deleted_status, service_goods_name, service_goods_type, group_id, sub_group_id, category_id, sub_category_id
    )

    end_time = time()  # Capture end time
    total_duration = end_time - start_time
    print(f"Total duration for fetching service goods master: {total_duration:.2f} seconds")

    if not results:
        return []

    for result in results:
        if result.is_bundled_service == "no" or not result.details:
            delattr(result, "details")

    return results



#------------------------------------------------------------------------------------------------------------



@router.get('/services/get_all_service_goods_master_test', response_model=Union[List[OffViewServiceGoodsMasterDisplay], dict])
def get_all_service_goods_master_test(
    deleted_status: Optional[DeletedStatus] = Query(None, title="Select deleted status", enum=list(DeletedStatus)),
    service_goods_name: Optional[str] = Query(None),
    service_goods_type: Union[int, str] = Query("ALL", description="Filter by hsn_sac_class_id. Use 1 for goods, 2 for services, or 'ALL' for both."),
    group_id: Union[int, str] = Query("ALL"),
    sub_group_id: Union[int, str] = Query("ALL"),
    category_id: Union[int, str] = Query("ALL"),
    sub_category_id: Union[int, str] = Query("ALL"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    start_time = time()

    results = db_office_master.get_all_service_goods_master_test(
        db,deleted_status, service_goods_name, service_goods_type, group_id, sub_group_id, category_id, sub_category_id
    )

    end_time = time()
    total_duration = end_time - start_time
    print(f"Total duration for fetching service goods master: {total_duration:.2f} seconds")

    if not results:
        return {"message": "No data present"}

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

#----------------------------------------------------------------------------------------------------
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
        return []
    return documents

#-------------------------------------------------------------------------------------------------------
@router.post("/services/save_service_document_data_master/{id}")
def save_service_document_data_master(
    id: int,
    data: List[SaveServiceDocumentDataMasterRequest], 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save service document data master.

    Parameters:
    - **id**: The ID of the service document data master record. This parameter is required and should be an integer.
    - **data**: A list of `SaveServiceDocumentDataMasterRequest` objects containing the service document data to be saved.
    - **db**: A database session dependency injected by FastAPI.
    - **token**: An authentication token dependency injected by FastAPI using OAuth2.

    Returns:
    - A success message after processing all service document data.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    # user_id = auth_info.get("user_id")

    try:
        result_message = ""
        for service in data:
            result = db_office_master.save_service_document_data_master(
                db, id, service
            )
            result_message = result["message"]
        
        return {"success": True, "message": result_message}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#---------------------------------------------------------------------------------------------------------------
from datetime import datetime, timedelta



# @router.get("/get_consultant_schedule")
# def get_consultant_schedule(
#     consultant_id: int,
#     consultation_mode_id: int,
#     db: Session = Depends(get_db),
#     check_date: Optional[date] = None,
#     service_goods_master_id: Optional[int] = None,
#     appointment_id: Optional[int] = None
# ):
#     """
# #### Parameters:

# - `consultant_id` (int, required): The ID of the consultant whose schedule is to be fetched.
# - `consultation_mode_id` (int, required): The ID of the consultation mode.
# - `db` (Session, required): The database session, provided by the dependency injection.
# - `check_date` (date, optional): The specific date to check the schedule for. If not provided, the endpoint will fetch the schedule for the next 10 days.
# - `service_goods_master_id` (int, optional): The ID of the service or goods master to get slot duration.

# #### Response:
# The endpoint returns a JSON object containing either available slots or messages about unavailable dates. The response format varies depending on whether `check_date` is provided or not.

# 1. **When All parameters are provided**:
#     - **Available slots found**: Returns a list of available time slots.
#     - **No available slots**: Returns a message indicating no available slots for the specified date.

# 2. **When `check_date` and `service_goods_master_id`  is not provided**:
#     - **Unavailable dates**: Returns a list of unavailable dates within the next 10 days.
#     - **Available dates**: Returns a list of available dates within the next 10 days.
# """

#     return db_office_master.fetch_available_and_unavailable_dates_and_slots(
#         consultant_id=consultant_id,
#         consultation_mode_id=consultation_mode_id,
#         db=db,
#         check_date=check_date,
#         service_goods_master_id=service_goods_master_id,
#         appointment_id=appointment_id
#     )



@router.get("/get_consultant_schedule")
def get_consultant_schedule(
    consultant_id: int,
    consultation_mode_id: int,
    db: Session = Depends(get_db),
    check_date: Optional[date] = None,
    service_goods_master_id: Optional[int] = None,
    appointment_id: Optional[int] = None
):
    """
#### Parameters:

- `consultant_id` (int, required): The ID of the consultant whose schedule is to be fetched.
- `consultation_mode_id` (int, required): The ID of the consultation mode.
- `db` (Session, required): The database session, provided by the dependency injection.
- `check_date` (date, optional): The specific date to check the schedule for. If not provided, the endpoint will fetch the schedule for the next 10 days.
- `service_goods_master_id` (int, optional): The ID of the service or goods master to get slot duration.

#### Response:
The endpoint returns a JSON object containing either available slots or messages about unavailable dates. The response format varies depending on whether `check_date` is provided or not.

1. **When All parameters are provided**:
    - **Available slots found**: Returns a list of available time slots.
    - **No available slots**: Returns a message indicating no available slots for the specified date.

2. **When `check_date` and `service_goods_master_id`  is not provided**:
    - **Unavailable dates**: Returns a list of unavailable dates within the next 10 days.
    - **Available dates**: Returns a list of available dates within the next 10 days.
"""

    return db_office_master.fetch_available_and_unavailable_dates_and_slots(
        consultant_id=consultant_id,
        consultation_mode_id=consultation_mode_id,
        db=db,
        check_date=check_date,
        service_goods_master_id=service_goods_master_id,
        appointment_id=appointment_id
    )

#---------------------------------------------------------------------------------------------------------------




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

    elif service_id is not None and service_id != 0:
        # Fetch consultants for the given service_id from off_view_consultant_details table
        consultants = db_office_master.get_consultants_for_service(db, service_id)
        # Convert consultants to a list of dictionaries
        consultants_data = [{"id": consultant.consultant_id, "first_name": consultant.first_name, "middle_name": consultant.middle_name, "last_name": consultant.last_name} for consultant in consultants]
        return {"consultants": consultants_data}
    
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
    # print(f"Received request with service_id: {service_id}, consultant_id: {consultant_id}")  # Debug print

    if service_id == 0:
        # Fetch all services from off_view_consultant_details table
        services = db_office_master.get_all_services(db)
        # Convert services to a list of dictionaries
        services_data = [{"id": service.service_goods_master_id, "name": service.service_goods_name} for service in services]
        # print(f"Retrieved all services: {services_data}")  # Debug print
        return {"services": services_data}

    elif consultant_id is not None and consultant_id != 0:
        # print(f"Checking consultant_id: {consultant_id}")  # Debug print
        # Fetch services for the given consultant_id from off_view_consultant_details table
        services = db_office_master.get_all_services_by_consultant_id(db, consultant_id)
        # print(f"Retrieved services for consultant ID {consultant_id}: {services}")  # Debug print
        if not services:
            raise HTTPException(status_code=404, detail=f"No services found for consultant ID {consultant_id}")
        # Convert services to a list of dictionaries
        services_data = [{"id": service.service_goods_master_id, "name": service.service_goods_name} for service in services]
        # print(f"Filtered services data: {services_data}")  # Debug print
        return {"consultant_id": consultant_id, "services": services_data}

    else:
        raise HTTPException(status_code=400, detail="Invalid request. Provide a valid service ID or consultant ID.")

#--------------------------------------------------------------------------------------------------------------

@router.get("/get_price_list/", response_model=PriceListResponse)
def get_price_list(
    service_type: Optional[str] = Query(None, description="Filter by type: 'ALL', 'GOODS', 'SERVICE'"),
    configuration_status: Optional[str] = Query(None, description="Filter by configuration status: 'ALL', 'CONFIGURED', 'NOT CONFIGURED'"),
    search: Optional[str] = Query(None, description="Search by service name"),
    db: Session = Depends(get_db)
):
    print(f"Received request with service_type: {service_type}, configuration_status: {configuration_status}, search: {search}")  # Debug print

    # Define the base SQL query
    sql_query = """
    SELECT
        off_service_goods_master.id,
        off_service_goods_master.hsn_sac_class_id,
        app_hsn_sac_classes.hsn_sac_class,
        off_service_goods_master.service_goods_name,
        off_service_goods_master.is_bundled_service,
        COUNT(off_service_goods_price_master.service_goods_master_id) AS configured_count
    FROM
        off_service_goods_master
    LEFT JOIN
        app_hsn_sac_classes
    ON
        off_service_goods_master.hsn_sac_class_id = app_hsn_sac_classes.id
    LEFT JOIN
        off_service_goods_price_master
    ON
        off_service_goods_master.id = off_service_goods_price_master.service_goods_master_id
    WHERE
        1=1
    """

    # Add service_type filter
    if service_type == "GOODS":
        sql_query += " AND off_service_goods_master.hsn_sac_class_id = 1"
    elif service_type == "SERVICE":
        sql_query += " AND off_service_goods_master.hsn_sac_class_id = 2"

    # Add search filter
    if search:
        sql_query += " AND off_service_goods_master.service_goods_name LIKE :search"

    # Add grouping
    sql_query += """
    GROUP BY
        off_service_goods_master.id,
        app_hsn_sac_classes.hsn_sac_class,
        off_service_goods_master.service_goods_name,
        off_service_goods_master.is_bundled_service
    """

    # Add configuration_status filter
    if configuration_status == "CONFIGURED":
        sql_query += " HAVING COUNT(off_service_goods_price_master.service_goods_master_id) >= 1"
    elif configuration_status == "NOT CONFIGURED":
        sql_query += " HAVING COUNT(off_service_goods_price_master.service_goods_master_id) = 0"
    elif configuration_status == "ALL" or not configuration_status:
        # No specific HAVING condition for ALL or if not provided
        pass

    # Add ordering
    sql_query += """
    ORDER BY
        off_service_goods_master.hsn_sac_class_id DESC,
        off_service_goods_master.service_goods_name;
    """

    # Execute the query
    params = {"search": f"%{search}%"} if search else {}
    results = db.execute(text(sql_query), params).fetchall()

    # Map the results to the response model
    services_data = [
        ServiceGoodsPrice(
            id=row.id,
            service_name=row.service_goods_name,
            service_type=row.hsn_sac_class,
            configuration_status="Configured" if row.configured_count >= 1 else "Not Configured",
            bundled_service="BUNDLED" if row.is_bundled_service == "yes" else "SINGLE",
        ) for row in results
    ]

    if not services_data:
        raise HTTPException(status_code=404, detail="No services found matching the criteria")

    return PriceListResponse(price_list=services_data)

#---------------------------------------------------------------------------------------------------------------
# @router.get("/get_service_data/", response_model=List[ServiceModel])
# def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
#                               db: Session = Depends(get_db)):
#     # Call the function to get service data based on service_id
#     service_data = db_office_master.get_service_data(service_id, db)
#     return service_data



# @router.get("/get_service_data/", response_model=List[ServiceModelSchema])
# def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
#                               db: Session = Depends(get_db)):
#     # Call the function to get service data based on service_id
#     service_data = db_office_master.get_service_data(service_id, db)
#     return service_data


#-------------------------------------------------------------------------------------------------------
# @router.get("/get_service_data/", response_model=List[ServiceModelSchema])
# def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
#                               db: Session = Depends(get_db)):
#     # Call the function to get service data based on service_id
#     service_data = db_office_master.get_service_data(service_id, db)
#     return service_data

# def get_service_data(service_id: int, db: Session) -> List[ServiceModelSchema]:
#     query = text("""
#         SELECT
#             a.id AS constitution_id,
#             a.business_constitution_name,
#             a.business_constitution_code,
#             b.id AS service_goods_master_id,
#             COALESCE(c.id, 0) AS service_goods_price_master_id,
#             b.service_goods_name,
#             COALESCE(c.service_charge, 0) AS service_charge,
#             COALESCE(c.govt_agency_fee, 0) AS govt_agency_fee,
#             COALESCE(c.stamp_duty, 0) AS stamp_duty,
#             COALESCE(c.stamp_fee, 0) AS stamp_fee,
#             COALESCE(c.id, 0) AS price_master_id,
           
#             c.effective_from_date AS effective_from_date,
#             c.effective_to_date AS effective_to_date
#         FROM
#             app_business_constitution AS a
#         LEFT OUTER JOIN
#             off_service_goods_master AS b ON TRUE
#         LEFT OUTER JOIN
#             off_service_goods_price_master AS c ON b.id = c.service_goods_master_id 
#                                                  AND a.id = c.constitution_id
#                                                  AND (c.effective_to_date IS NULL OR c.effective_to_date >= CURRENT_DATE)
#                                                  AND c.effective_from_date <= CURRENT_DATE
#         WHERE
#             b.id = :service_id
#         ORDER BY
#             a.id, b.id;
#     """)

#     query_result = db.execute(query, {"service_id": service_id}).fetchall()

#     service_data = [
#         ServiceModelSchema(
           
#             constitution_id=row.constitution_id,
#             business_constitution_name=row.business_constitution_name,
#             service_goods_master_id=row.service_goods_master_id,
#             service_goods_price_master_id=row.service_goods_price_master_id,
#             service_name=row.service_goods_name,
#             business_constitution_code=row.business_constitution_code,
#             service_charge=row.service_charge,
#             govt_agency_fee=row.govt_agency_fee,
#             stamp_duty=row.stamp_duty,
#             stamp_fee=row.stamp_fee,
#             effective_from_date=row.effective_from_date,
#             effective_to_date=row.effective_to_date,
#             price_master_id=row.price_master_id
#         ) for row in query_result
#     ]
    
#     return service_data



#------------------------------------------------------------------------------------------------------------
@router.get("/get_service_data/", response_model=List[ServiceModelSchema])
def get_service_data_endpoint(
    service_id: int = Query(..., description="Service ID"),
    rate_status: Optional[str] = Query(None, description="Rate status: CURRENT, UPCOMING, or PREVIOUS"),
    db: Session = Depends(get_db)
):
    # Call the function to get service data based on service_id, optional rate_status, and the current date
    service_data = db_office_master.get_service_data(service_id, rate_status, db)
    return service_data

#---------------------------------------------------------------------------------------------------------------
@router.get("/get_price_history/", response_model=List[ServiceModel])
def get_service_data_endpoint(service_id: int = Header(..., description="Service ID"), 
                              db: Session = Depends(get_db)):
    service_data = db_office_master.get_price_history(service_id, db)
    if not service_data:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_data
#-----------------------------------------------------------------------------------------------------------  
@router.post("/save_service_price/")
def save_service_price_endpoint(price_data: List[PriceData], 
                                service_goods_master_id: int,
                                db: Session = Depends(get_db),
                                token: str = Depends(oauth2.oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    
    try:
        for data in price_data:
            db_office_master.save_price_data(data, service_goods_master_id, user_id, db)
        
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
            return []
        
        # If the results are a list of Service_Group objects
        if isinstance(results[0], Service_Group):
            return JSONResponse(status_code=200, content={"group": [result.model_dump() for result in results]})

        # Filter out null fields from each ServiceDocumentsList_Group object
        filtered_results = [
            {k: v for k, v in result.model_dump().items() if v is not None}
            for result in results
        ]

        # Ensure the response is a list of dictionaries matching the schema
        return JSONResponse(status_code=200, content=filtered_results)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# #---------------------------------------------------------------------------------------
# @router.get('/services/get_service_documents_data_details', response_model=List[OffViewServiceDocumentsDataDetailsDocCategory])
# def get_service_documents_data_details(
#     service_document_data_master_id: int,
#     document_category: Optional[str] = Query(None, title="Select document category", 
#                                             enum=['PERSONAL DOC', 'CONSTITUTION DOC', 'PRINCIPAL PLACE DOC', 'UTILITY DOC', 'DATA TO BE SUBMITTED']),         
#     db: Session = Depends(get_db)
# ):
#     """
#     Retrieve service document details based on specified criteria.

#     Parameters:
#     - **service_id**: Required parameter to filter by service ID.
#     - **document_category**: Optional parameter to filter by document category.
#     - Return a list of documents details with the selected category for the specified service_id.
    
#     Possible values for `document_category` include:
#     - 'PERSONAL DOC'
#     - 'CONSTITUTION DOC'
#     - 'PRINCIPAL PLACE DOC'
#     - 'UTILITY DOC'
#     - 'DATA TO BE SUBMITTED'

#     Returns:
#     - Returns all document details for the specified service_id and 'document_category'.
#     - If no records are found, return {'message': 'No data found'}.
#     """
#     try:
#         results = db_office_master.get_service_documents_data_details(db, service_document_data_master_id, document_category)

#         if not results:
#             return []

#         # Group the results by document category
#         grouped_results = {}
#         for result in results:
#             if result.document_data_category_id not in grouped_results:
#                 grouped_results[result.document_data_category_id] = {
#                     "document_data_category_id": result.document_data_category_id,
#                     "document_data_category_category_name": result.document_data_category_category_name,
#                     "details": []
#                 }
#             grouped_results[result.document_data_category_id]["details"].append(result)

#         # Convert grouped_results dict to List[OffViewServiceDocumentsDataDetailsDocCategory]
#         final_results = list(grouped_results.values())

#         return final_results

#     except Exception as e:
#         # logging.error(f"Error fetching service documents details: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
    
#  #-------------------------------------------------------------------------------------------------------------   





@router.get('/services/get_service_documents_data_details', response_model=List[OffViewServiceDocumentsDataDetailsDocCategory])
def get_service_documents_data_details(
    service_document_data_master_id: Optional[int] = Query(None, title="Service Document Data Master ID"),
    service_id: Optional[int] = Query(None, title="Service ID"),
    constitution_id: Optional[int] = Query(None, title="Constitution ID"),
    document_category: Optional[str] = Query("ALL", title="Select document category", 
                                             enum=['ALL','PERSONAL DOC', 'CONSTITUTION DOC', 'PRINCIPAL PLACE DOC', 'UTILITY DOC', 'DATA TO BE SUBMITTED']),
    nature_of_possession_id: Optional[int] = Query(None, title="Nature of Possession ID", 
                                                   description="Only relevant if 'PRINCIPAL PLACE DOC' is selected."),
    db: Session = Depends(get_db)
):
    """
   
    Retrieve service document details based on various filter criteria.

    This endpoint allows users to fetch service document details by specifying optional filters such as 
    service document data master ID, constitution ID, service ID, document category, and nature of possession ID. 

    - **document_category** (Optional[str], default="ALL"): The category of the document to filter the results.
     Categories include 'PERSONAL DOC', 'CONSTITUTION DOC', 'PRINCIPAL PLACE DOC', 'UTILITY DOC', 
     and 'DATA TO BE SUBMITTED'. If 'ALL' is selected, documents from all categories will be retrieved.

    - **nature_of_possession_id** (Optional[int]): The ID representing the nature of possession.
    This filter is only relevant when 'PRINCIPAL PLACE DOC' is selected as the document category.
  
    """
    try:
        results = db_office_master.get_service_documents_data_details(
            db,
            service_document_data_master_id,
            service_id,
            constitution_id,
            document_category,
            nature_of_possession_id,
        )

        if not results:
            return []

        # Group results by document category
        grouped_results = {}
        for result in results:
            if result.document_data_category_id not in grouped_results:
                grouped_results[result.document_data_category_id] = {
                    "document_data_category_id": result.document_data_category_id,
                    "document_data_category_category_name": result.document_data_category_category_name,
                    "details": []
                }
            grouped_results[result.document_data_category_id]["details"].append(result)

        return list(grouped_results.values())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching service documents details: {e}")




# @router.get("/services/get_all_service_document_data_master")
# def get_all_service_document_data_master(
#     db: Session = Depends(get_db),
#     search: Optional[str] = None,
#     service_id: Union[int, str] = 'ALL',
#     group_id: Union[int, str] = 'ALL',
#     sub_group_id: Union[int, str] = 'ALL',
#     category_id: Union[int, str] = 'ALL',
#     sub_category_id: Union[int, str] = 'ALL',
#     constitution_id: Union[int, str] = 'ALL',
#     doc_data_status: Optional[str] = Query('ALL', description="Filter by type: 'CONFIGURED', 'NOT CONFIGURED'"),
# ) -> List[dict]:
#     try:
       

#         search_conditions = []

#         if search:
#             search_like = f'%{search}%'
#             search_conditions.append(
#                 or_(
#                     text("g.service_goods_name LIKE :search"),
#                     text("b.group_name LIKE :search"),
#                     text("d.category_name LIKE :search"),
#                     text("c.sub_group_name LIKE :search"),
#                     text("e.sub_category_name LIKE :search"),
#                     text("f.business_constitution_name LIKE :search")
#                 )
#             )

#         if service_id != 'ALL':
#             search_conditions.append(text("g.id = :service_id"))
        
#         if group_id != 'ALL':
#             search_conditions.append(text("g.group_id = :group_id"))
        
#         if sub_group_id != 'ALL':
#             search_conditions.append(text("g.sub_group_id = :sub_group_id"))
        
#         if category_id != 'ALL':
#             search_conditions.append(text("g.category_id = :category_id"))
        
#         if sub_category_id != 'ALL':
#             search_conditions.append(text("g.sub_category_id = :sub_category_id"))
        
#         if constitution_id != 'ALL':
#             search_conditions.append(text("f.id = :constitution_id"))
        
#         if doc_data_status != 'ALL':
#             if doc_data_status == "CONFIGURED":
#                 # search_conditions.append(text("a.id IS NOT NULL"))
#                 search_conditions.append(text("a.id IS NOT NULL AND d.is_deleted = 'no'"))
#             elif doc_data_status == "NOT CONFIGURED":
#                 # search_conditions.append(text("a.id IS NULL"))
#                 search_conditions.append(text("a.id IS NULL OR (a.id IS NOT NULL AND d.is_deleted = 'yes')"))
    

#         base_query = """
#         SELECT
#             ROW_NUMBER() OVER (ORDER BY g.service_goods_name, f.business_constitution_name) AS unique_id,
#             a.id AS service_document_data_master_id,
#             g.id AS service_goods_master_id,
#             g.service_goods_name,
#             f.id AS constitution_id,
#             f.business_constitution_name,
#             b.id AS group_id,
#             b.group_name,
#             c.id AS sub_group_id,
#             c.sub_group_name,
#             d.id AS category_id,
#             d.category_name,
#             e.id AS sub_category_id,
#             e.sub_category_name,
            
#             CASE
#                   WHEN a.id IS NOT NULL AND EXISTS (
#                       SELECT 1
#                       FROM off_service_document_data_details AS dd
#                       WHERE dd.service_document_data_master_id = a.id
#                       AND dd.is_deleted = 'no'
#                   ) THEN 'Configured'
#                   ELSE 'Not Configured'
#             END AS document_status
#         FROM 
#             off_service_goods_master AS g
#         CROSS JOIN app_business_constitution AS f
#         LEFT JOIN off_service_document_data_master AS a 
#             ON g.id = a.service_goods_master_id 
#             AND f.id = a.constitution_id
#         LEFT JOIN off_service_goods_group AS b ON g.group_id = b.id
#         LEFT JOIN off_service_goods_sub_group AS c ON g.sub_group_id = c.id
#         LEFT JOIN off_service_goods_category AS d ON g.category_id = d.id
#         LEFT JOIN off_service_goods_sub_category AS e ON g.sub_category_id = e.id
#         """

#         if search_conditions:
#             base_query += " WHERE " + " AND ".join(str(cond) for cond in search_conditions)
        
#         base_query += " ORDER BY g.service_goods_name, f.display_order"

       

#         query = text(base_query)

#         params = {
#             'search': f'%{search}%' if search else None,
#             'service_id': service_id if service_id != 'ALL' else None,
#             'group_id': group_id if group_id != 'ALL' else None,
#             'sub_group_id': sub_group_id if sub_group_id != 'ALL' else None,
#             'category_id': category_id if category_id != 'ALL' else None,
#             'sub_category_id': sub_category_id if sub_category_id != 'ALL' else None,
#             'constitution_id': constitution_id if constitution_id != 'ALL' else None
#         }

     

#         result = db.execute(query, params)
#         rows = result.fetchall()

#         # Log keys and rows for debugging
       
#         if not rows:
#             return []

#         service_document_data_master = []
#         for row in rows:
#             service_document_data_master.append({
#                 "unique_id": row.unique_id,
#                 "service_goods_master_id": row.service_goods_master_id,
#                 "service_goods_name": row.service_goods_name,
#                 "service_document_data_master_id": row.service_document_data_master_id,  # Ensure this matches the alias in your SQL query
#                 "group_id": row.group_id,
#                 "group_name": row.group_name,
#                 "sub_group_id": row.sub_group_id,
#                 "sub_group_name": row.sub_group_name,
#                 "category_id": row.category_id,
#                 "category_name": row.category_name,
#                 "sub_category_id": row.sub_category_id,
#                 "sub_category_name": row.sub_category_name,
#                 "constitution_id": row.constitution_id,
#                 "business_constitution_name": row.business_constitution_name,
#                 # "business_constitution_code": row.business_constitution_code,
#                 # "description": row.description,
#                 "status": row.document_status
#             })

#         return service_document_data_master

#     except HTTPException as e:
#         raise e
#     except Exception as e:
       
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/services/get_all_service_document_data_master")
def get_all_service_document_data_master(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    service_id: Union[int, str] = 'ALL',
    group_id: Union[int, str] = 'ALL',
    sub_group_id: Union[int, str] = 'ALL',
    category_id: Union[int, str] = 'ALL',
    sub_category_id: Union[int, str] = 'ALL',
    constitution_id: Union[int, str] = 'ALL',
    doc_data_status: Optional[str] = Query('ALL', description="Filter by type: 'CONFIGURED', 'NOT CONFIGURED'"),
) -> List[dict]:
    try:
       

        search_conditions = []

        if search:
            search_like = f'%{search}%'
            search_conditions.append(
                or_(
                    text("g.service_goods_name LIKE :search"),
                    text("b.group_name LIKE :search"),
                    text("d.category_name LIKE :search"),
                    text("c.sub_group_name LIKE :search"),
                    text("e.sub_category_name LIKE :search"),
                    text("f.business_constitution_name LIKE :search")
                )
            )

        if service_id != 'ALL':
            search_conditions.append(text("g.id = :service_id"))
        
        if group_id != 'ALL':
            search_conditions.append(text("g.group_id = :group_id"))
        
        if sub_group_id != 'ALL':
            search_conditions.append(text("g.sub_group_id = :sub_group_id"))
        
        if category_id != 'ALL':
            search_conditions.append(text("g.category_id = :category_id"))
        
        if sub_category_id != 'ALL':
            search_conditions.append(text("g.sub_category_id = :sub_category_id"))
        
        if constitution_id != 'ALL':
            search_conditions.append(text("f.id = :constitution_id"))
        
        if doc_data_status != 'ALL':
            if doc_data_status == "CONFIGURED":
                search_conditions.append(text(
                "a.id IS NOT NULL AND EXISTS ("
                "SELECT 1 FROM off_service_document_data_details dd "
                "WHERE dd.service_document_data_master_id = a.id "
                "AND dd.is_deleted = 'no')"
                 ))

        # For Not Configured: No valid master or all details are deleted (is_deleted = 'yes')
            elif doc_data_status == "NOT CONFIGURED":
                search_conditions.append(text(
                "(a.id IS NULL OR NOT EXISTS ("
                "SELECT 1 FROM off_service_document_data_details dd "
                "WHERE dd.service_document_data_master_id = a.id "
                "AND dd.is_deleted = 'no'))"
                 ))
            

        base_query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY g.service_goods_name, f.business_constitution_name) AS unique_id,
            a.id AS service_document_data_master_id,
            g.id AS service_goods_master_id,
            g.service_goods_name,
            f.id AS constitution_id,
            f.business_constitution_name,
            b.id AS group_id,
            b.group_name,
            c.id AS sub_group_id,
            c.sub_group_name,
            d.id AS category_id,
            d.category_name,
            e.id AS sub_category_id,
            e.sub_category_name,
            
            CASE
                  WHEN a.id IS NOT NULL AND EXISTS (
                      SELECT 1
                      FROM off_service_document_data_details AS dd
                      WHERE dd.service_document_data_master_id = a.id
                      AND dd.is_deleted = 'no'
                  ) THEN 'Configured'
                  ELSE 'Not Configured'
            END AS document_status
        FROM 
            off_service_goods_master AS g
        CROSS JOIN app_business_constitution AS f
        LEFT JOIN off_service_document_data_master AS a 
            ON g.id = a.service_goods_master_id 
            AND f.id = a.constitution_id
        LEFT JOIN off_service_goods_group AS b ON g.group_id = b.id
        LEFT JOIN off_service_goods_sub_group AS c ON g.sub_group_id = c.id
        LEFT JOIN off_service_goods_category AS d ON g.category_id = d.id
        LEFT JOIN off_service_goods_sub_category AS e ON g.sub_category_id = e.id
        """

        if search_conditions:
            base_query += " WHERE " + " AND ".join(str(cond) for cond in search_conditions)
        
        base_query += " ORDER BY g.service_goods_name, f.display_order"

       

        query = text(base_query)

        params = {
            'search': f'%{search}%' if search else None,
            'service_id': service_id if service_id != 'ALL' else None,
            'group_id': group_id if group_id != 'ALL' else None,
            'sub_group_id': sub_group_id if sub_group_id != 'ALL' else None,
            'category_id': category_id if category_id != 'ALL' else None,
            'sub_category_id': sub_category_id if sub_category_id != 'ALL' else None,
            'constitution_id': constitution_id if constitution_id != 'ALL' else None
        }

     

        result = db.execute(query, params)
        rows = result.fetchall()

        # Log keys and rows for debugging
       
        if not rows:
            return []

        service_document_data_master = []
        for row in rows:
            service_document_data_master.append({
                "unique_id": row.unique_id,
                "service_goods_master_id": row.service_goods_master_id,
                "service_goods_name": row.service_goods_name,
                "service_document_data_master_id": row.service_document_data_master_id,  # Ensure this matches the alias in your SQL query
                "group_id": row.group_id,
                "group_name": row.group_name,
                "sub_group_id": row.sub_group_id,
                "sub_group_name": row.sub_group_name,
                "category_id": row.category_id,
                "category_name": row.category_name,
                "sub_category_id": row.sub_category_id,
                "sub_category_name": row.sub_category_name,
                "constitution_id": row.constitution_id,
                "business_constitution_name": row.business_constitution_name,
                # "business_constitution_code": row.business_constitution_code,
                # "description": row.description,
                "status": row.document_status
            })

        return service_document_data_master

    except HTTPException as e:
        raise e
    except Exception as e:
       
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#------------------------------------------------------------------------------------------------
###################CONSULTANTS AND SERVICES####################################################
#------------------------------------------------------------------------------------------------

from datetime import datetime

# @router.get("/consultant_employees", response_model=List[ConsultantEmployee])
# def get_consultant_employees(
#     db: Session = Depends(get_db),
#     search_query: str = Query(None, description="Search query to filter consultant employees")
# ):
#     current_date = datetime.utcnow().date()
#     query = db.query(
#         EmployeeMaster.employee_id,
#         EmployeeMaster.first_name,
#         EmployeeMaster.middle_name,
#          EmployeeMaster.last_name,
#         # func.concat(EmployeeMaster.first_name, ' ', EmployeeMaster.middle_name, ' ', EmployeeMaster.last_name).label('employee_name'),
#         EmployeeMaster.employee_number,
#         EmployeeContactDetails.personal_email_id.label('personal_email'),
#         EmployeeContactDetails.official_email_id.label('official_email'),
#         EmployeeContactDetails.personal_mobile_number.label('personal_mobile'),
#         EmployeeContactDetails.official_mobile_number.label('official_mobile'),
#         HrDepartmentMaster.department_name,
#         HrDesignationMaster.designation
#     ).join(
#         EmployeeEmploymentDetails,
#         EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id
#     ).join(
#         EmployeeContactDetails,
#         EmployeeMaster.employee_id == EmployeeContactDetails.employee_id
#     ).join(
#         HrDepartmentMaster,
#         EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id
#     ).join(
#         HrDesignationMaster,
#         EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id
#     ).filter(
#         EmployeeEmploymentDetails.is_consultant == 'yes',
#         EmployeeEmploymentDetails.effective_from_date <= current_date,
#         (EmployeeEmploymentDetails.effective_to_date == None) | (EmployeeEmploymentDetails.effective_to_date >= current_date),
#         EmployeeMaster.is_deleted == 'no',
#         EmployeeEmploymentDetails.is_deleted == 'no',
#         EmployeeContactDetails.is_deleted == 'no'
#     )

#     if search_query:
#         search_filter = (
#             EmployeeMaster.first_name.ilike(f"%{search_query}%") |
#             EmployeeMaster.middle_name.ilike(f"%{search_query}%") |
#             EmployeeMaster.last_name.ilike(f"%{search_query}%") |
#             EmployeeMaster.employee_number.ilike(f"%{search_query}%") |
#             EmployeeContactDetails.personal_email_id.ilike(f"%{search_query}%") |
#             EmployeeContactDetails.official_email_id.ilike(f"%{search_query}%") |
#             EmployeeContactDetails.personal_mobile_number.ilike(f"%{search_query}%") |
#             EmployeeContactDetails.official_mobile_number.ilike(f"%{search_query}%")
#         )
#         query = query.filter(search_filter)

#     return query.all()


@router.get("/consultant_employees", response_model=List[ConsultantEmployee])
def get_consultant_employees(
    db: Session = Depends(get_db),
    search_query: str = Query(None, description="Search query to filter consultant employees")
):
    current_date = datetime.utcnow().date()
    
    # Initial query with necessary joins
    query = db.query(
        EmployeeMaster.employee_id,
        EmployeeMaster.first_name,
        EmployeeMaster.middle_name,
        EmployeeMaster.last_name,
        EmployeeMaster.employee_number,
        EmployeeContactDetails.personal_email_id.label('personal_email'),
        EmployeeContactDetails.official_email_id.label('official_email'),
        EmployeeContactDetails.personal_mobile_number.label('personal_mobile'),
        EmployeeContactDetails.official_mobile_number.label('official_mobile'),
        HrDepartmentMaster.department_name,
        HrDesignationMaster.designation
    ).join(
        EmployeeEmploymentDetails,
        EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id
    ).join(
        EmployeeContactDetails,
        EmployeeMaster.employee_id == EmployeeContactDetails.employee_id
    ).join(
        HrDepartmentMaster,
        EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id
    ).join(
        HrDesignationMaster,
        EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id
    ).filter(
        EmployeeEmploymentDetails.is_consultant == 'yes',
        EmployeeEmploymentDetails.effective_from_date <= current_date,
        (EmployeeEmploymentDetails.effective_to_date == None) | (EmployeeEmploymentDetails.effective_to_date >= current_date),
        EmployeeContactDetails.effective_from_date <= current_date,
        (EmployeeContactDetails.effective_to_date == None) | (EmployeeContactDetails.effective_to_date >= current_date),
        EmployeeMaster.is_deleted == 'no',
        EmployeeEmploymentDetails.is_deleted == 'no',
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


#-------------------------------------------------------------------------------------------------------------

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
    To save give action_type =Update and Insert
    id:0
    consultant_id:1
    service_id:88
    these data should be given
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

        result = []
        # raise HTTPException(status_code=404, detail="No active records found")

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



#-------------------------------------------------------------------------------------------------------------

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

    
 #-------------------------------------------------------------------------------------------------------------   
    
        
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


#-------------------------------------------------------------------------------------------------------------

@router.get("/enquiry/get_enquiries", response_model=List[OffViewEnquiryResponseSchema])
def get_and_search_enquiries(
    search_value: Union[str, int] = "ALL",
    status_id: Optional[str] = "ALL",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    mobile_number: Optional[str] = None,
    email_id: Optional[str] = None,
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
    - **mobile_number**: Search with 'mobile_number' to get the specific details.
    - **email_id**: Search with 'email_id' to get the specific details.
    """
    return db_office_master.get_enquiries(
        db,
        search_value=search_value,
        status_id=status_id,
        from_date=from_date,
        to_date=to_date,
        mobile_number=mobile_number,
        email_id=email_id
    )

#------------------------------------------------------------------------------------------------------------

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

# @router.get('/services/get_all_consultation_task_master_details', response_model=Union[List[OffViewConsultationTaskMasterSchema], dict])
# def get_all_consultation_task_master_details(
#     db: Session = Depends(get_db),
#     service_id: Union[int, str] = Query("ALL"),
#     task_status: Union[int, str] = Query("ALL"),
#     consultation_mode: Union[int, str] = Query("ALL"),
#     tool: Union[int, str] = Query("ALL"),
#     consultant_id: Union[int, str] = Query("ALL"),
#     from_date: Optional[date] = None,
#     to_date: Optional[date] = None,
#     token: str = Depends(oauth2.oauth2_scheme)
# ) -> Union[List[OffViewConsultationTaskMasterSchema], dict]:
#     """
#     Retrieve consultation task master details with optional filters.
    
#     - `service_id`: Filter by service_id or 'ALL' for all services.
#     - `task_status`: Filter by task status or 'ALL' for all statuses.
#     - `consultation_mode`: Filter by consultation mode or 'ALL' for all modes.
#     - `tool`: Filter by consultation tool or 'ALL' for all tools.
#     - `consultant_id`: Filter by consultant ID or 'ALL' for all consultants.
#     - `from_date`: Optional. Filter tasks from this date onwards.(default None)
#     - `to_date`: Optional. Filter tasks up to this date.(default None)
    
#     """
    
#     try:
#         if not token:
#             raise HTTPException(status_code=401, detail="Token is missing")

#         results = db_office_master.get_all_consultation_task_master_details(
#             db, service_id, task_status, consultation_mode, tool, consultant_id, from_date, to_date
#         )

#         if not results:
#             return []
        
#         # Filter out null fields and convert datetime objects to strings
#         filtered_results = [
#             {
#                 attribute_name: value.isoformat() if isinstance(value, datetime) else value 
#                 for attribute_name, value in result.service_id().items() if value not in [None, [], {}]
#             }
#             for result in results
#         ]

#         return JSONResponse(status_code=200, content=filtered_results)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")

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
            return []
        
        # # Filter out null fields and convert datetime objects to strings
        # filtered_results = [
        #     {
        #         attribute_name: value.isoformat() if isinstance(value, datetime) else value 
        #         for attribute_name, value in result.dict().items() if value not in [None, [], {}]
        #     }
        #     for result in results
        # ]

        # return JSONResponse(status_code=200, content=filtered_results)
        return results
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
        return []

    # Remove the "details" field if there are no details available
    for result in results:
        if result.is_bundled_service == "no" or not result.details:
            delattr(result, "details")

    return results



#-------------------------------------OFFER-------------------------------------------------------
@router.post("/save_offer_details")
def save_office_offer_details(
    
    data: List[SaveOfferDetails], 
    action_type: RecordActionType,
    apply_to : ApplyTo,
    id: Optional[int] = 0 ,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)

):
    """
    Endpoint to save or update offer details in the office offer master table and office offer details table.

    Parameters:
    - data (List[SaveOfferDetails]): The list of offer data to save or update. This data contains both master data and details.
    - action_type (RecordActionType): The action to perform. Use INSERT_ONLY to add new rows or UPDATE_ONLY to update existing rows.
    - apply_to (ApplyTo): Determines the scope of application. Use ALL to apply to all services, otherwise use SELECT for selected services.
    - id (Optional[int]): The ID of the offer master to update. Required for updating an existing offer master data. Default value is 0.
    - db (Session): The database session dependency.
    - token (str): The authorization token dependency.

    Returns:
    - JSON response with the status of the operation.
    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        for offer_master in data:
            db_office_master.save_office_offer_details(
                db, id, offer_master, user_id, action_type, apply_to
            )
        return {"success": True, "message": "Saved successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#-------------------------------------------------------------------------------------------------------------

@router.get("/get_all_offer_list", response_model=List[OffOfferMasterSchemaResponse])
def get_all_offer_list(
    category_id: Optional[int] = None,
    offer_master_id: Optional[int]=None,
    offers : Status = Status.CURRENT, # date filter parameter, 
    db: Session = Depends(get_db)
):
    offer_list= db_office_master.get_all_offer_list(db,category_id,offer_master_id,offers)
    return offer_list

#-------------------------------------------------------------------------------------------------------------

@router.delete("/delete_offer_master")
def delete_offer_master(
     offer_master_id: int,
     action_type: ActionType = ActionType.UNDELETE,
     db: Session = Depends(get_db),
     token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"]
        
    return db_office_master.delete_offer_master(db, offer_master_id,action_type,deleted_by=user_id)


#--------------------------------------------------------------------

from fpdf import FPDF

class PDFWithFooter(FPDF):
    def __init__(self):
        super().__init__()
        self.alias_nb_pages()

    def header(self):
        # Add company logo
        logo_path = r"C:\logo\logo.png"  # Update this path
        self.image(logo_path, x=10, y=8, w=20, h=20)
        
        # Add company name
        self.set_font("Arial", 'B', size=20)
        self.cell(0, 10, txt="BRQ ASSOCIATES", ln=True, align='C')
        
        # Add a line break
        self.ln(10)
        
        # Add a horizontal line
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        
        # Add a line break
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        page_number = f'Page {self.page_no()} of {{nb}}'
        self.cell(0, 10, page_number, 0, 0, 'C')

#-------------------------------------------------------------------------------------------------------------
def generate_consultant_employees_pdf(employee_list: List[ConsultantEmployee], file_path: str):
    # pdf = FPDF()
      
    pdf = PDFWithFooter()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    
    # Add invoice details
    pdf.cell(100, 10, txt="Invoice Date: 2023-07-24", ln=True)
    pdf.cell(100, 10, txt="Due Date: 2023-08-24", ln=True)
    pdf.cell(100, 10, txt="Invoice Number: 12345", ln=True)
    
    # Add a line break
    pdf.ln(10)
    
    # Add a horizontal line
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    
    # Add a line break
    pdf.ln(10)
    
    # Set font for table headers
    pdf.set_font("Arial", 'B', size=10)
    
    # Table headers
    pdf.set_fill_color(200, 220, 255)  # Light blue fill color
    pdf.cell(10, 10, txt="ID", border=1, fill=True)
    pdf.cell(40, 10, txt="Name", border=1, fill=True)
    pdf.cell(25, 10, txt="Number", border=1, fill=True)
    pdf.cell(40, 10, txt="Personal Email", border=1, fill=True)
    pdf.cell(40, 10, txt="Official Email", border=1, fill=True)
    # pdf.cell(25, 10, txt="Department", border=1, fill=True)
    # pdf.cell(25, 10, txt="Designation", border=1, fill=True)
    pdf.ln()
    
    # Set font for table rows
    pdf.set_font("Arial", size=10)
    
    # Table rows
    for employee in employee_list:
        pdf.cell(10, 10, txt=str(employee.employee_id), border=1)
        pdf.cell(40, 10, txt=f"{employee.first_name} {employee.middle_name} {employee.last_name}", border=1)
        pdf.cell(25, 10, txt=employee.employee_number, border=1)
        pdf.cell(40, 10, txt=employee.personal_email, border=1)
        pdf.cell(40, 10, txt=employee.official_email or 'N/A', border=1)
        # pdf.cell(25, 10, txt=employee.department_name, border=1)
        # pdf.cell(25, 10, txt=employee.designation or 'N/A', border=1)
        pdf.ln()
    
    pdf.output(file_path)
    return open(file_path, "rb")

#-------------------------------------------------------------------------------------------------------------

@router.get("/consultant_employees/pdf")
def get_consultant_employees_pdf(
    db: Session = Depends(get_db),
    search_query: str = Query(None, description="Search query to filter consultant employees")
):
    current_date = datetime.utcnow().date()
    query = db.query(
        EmployeeMaster.employee_id,
        EmployeeMaster.first_name,
        # EmployeeMaster.middle_name,
        # EmployeeMaster.last_name,
        func.coalesce(EmployeeMaster.middle_name, '').label('middle_name'),  
        func.coalesce(EmployeeMaster.last_name, '').label('last_name'),
        EmployeeMaster.employee_number,
        EmployeeContactDetails.personal_email_id.label('personal_email'),
        EmployeeContactDetails.official_email_id.label('official_email'),
        EmployeeContactDetails.personal_mobile_number.label('personal_mobile'),
        EmployeeContactDetails.official_mobile_number.label('official_mobile'),
        HrDepartmentMaster.department_name,
        HrDesignationMaster.designation
    ).join(
        EmployeeEmploymentDetails,
        EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id
    ).join(
        EmployeeContactDetails,
        EmployeeMaster.employee_id == EmployeeContactDetails.employee_id
    ).join(
        HrDepartmentMaster,
        EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id
    ).join(
        HrDesignationMaster,
        EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id
    ).filter(
        EmployeeEmploymentDetails.is_consultant == 'yes',
        EmployeeEmploymentDetails.effective_from_date <= current_date,
        (EmployeeEmploymentDetails.effective_to_date == None) | (EmployeeEmploymentDetails.effective_to_date >= current_date),
        EmployeeMaster.is_deleted == 'no',
        EmployeeEmploymentDetails.is_deleted == 'no',
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

    employees = query.all()

    if not employees:
        raise HTTPException(status_code=404, detail="No consultant employees found")

    # Convert query results to list of ConsultantEmployee models
    employee_list = [
        ConsultantEmployee(
            employee_id=e.employee_id,
            first_name=e.first_name,
            middle_name=e.middle_name,
            last_name=e.last_name,
            employee_number=e.employee_number,
            personal_email=e.personal_email,
            official_email=e.official_email,
            personal_mobile=e.personal_mobile,
            official_mobile=e.official_mobile,
            department_name=e.department_name,
            designation=e.designation
        )
        for e in employees
    ]

    # Define the file path to save the PDF using the correct path separator
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    print("base_dir",base_dir)
    file_path = f"{UPLOAD_DIR_CONSULTANT_DETAILS}/consultant_employees.pdf"
    # file_path = os.path.join(base_dir, UPLOAD_DIR_CONSULTANT_DETAILS, "consultant_employees.pdf")
    print("file_path",file_path)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Generate and save the PDF
    pdf_buffer = generate_consultant_employees_pdf(employee_list, file_path)
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=consultant_employees.pdf"})



#--------------------------------------------------------------------------------------
from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import StreamingResponse
import os
from datetime import datetime
import pdfkit



TEMPLATE_CONSULTANT_DETAILS = "C:/BHARAT-TAXES-CA-ERP-API/templates/employee.html"
UPLOAD_DIR_CONSULTANT_DETAILS = "uploads/consultant_details"



def generate_consultant_employees_pdf_template(employee_list, file_path):
    # Load the template environment
    template_dir = os.path.dirname(TEMPLATE_CONSULTANT_DETAILS)
    template_name = os.path.basename(TEMPLATE_CONSULTANT_DETAILS)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    
    # Render the template with data
    html_content = template.render(employees=employee_list)
    
    # Configuration for pdfkit
    wkhtmltopdf_path = 'C:/wkhtmltox/wkhtmltopdf/bin/wkhtmltopdf.exe'
    if not os.path.isfile(wkhtmltopdf_path):
        raise FileNotFoundError(f'wkhtmltopdf executable not found at path: {wkhtmltopdf_path}')
    
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    
    # PDF options
    options = {
        'footer-center': 'Page [page] of [topage]',
        'footer-font-size': '8',
        'margin-bottom': '20mm',
        'no-outline': None
    }
    
    try:
        # Convert HTML to PDF
        pdfkit.from_string(html_content, file_path, configuration=config, options=options)
    except Exception as e:
        raise RuntimeError(f'Error generating PDF: {e}')
    
    return open(file_path, "rb")

#-------------------------------------------------------------------------------------------------------------

@router.get("/template/consultant_employees/pdf")
def get_consultant_employees_pdf(
    db: Session = Depends(get_db),
    search_query: str = Query(None, description="Search query to filter consultant employees")
):
    current_date = datetime.utcnow().date()
    query = db.query(
        EmployeeMaster.employee_id,
        EmployeeMaster.first_name,
        EmployeeMaster.middle_name,
        EmployeeMaster.last_name,
        EmployeeMaster.employee_number,
        EmployeeContactDetails.personal_email_id.label('personal_email'),
        EmployeeContactDetails.official_email_id.label('official_email'),
        EmployeeContactDetails.personal_mobile_number.label('personal_mobile'),
        EmployeeContactDetails.official_mobile_number.label('official_mobile'),
        HrDepartmentMaster.department_name,
        HrDesignationMaster.designation
    ).join(
        EmployeeEmploymentDetails,
        EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id
    ).join(
        EmployeeContactDetails,
        EmployeeMaster.employee_id == EmployeeContactDetails.employee_id
    ).join(
        HrDepartmentMaster,
        EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id
    ).join(
        HrDesignationMaster,
        EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id
    ).filter(
        EmployeeEmploymentDetails.is_consultant == 'yes',
        EmployeeEmploymentDetails.effective_from_date <= current_date,
        (EmployeeEmploymentDetails.effective_to_date == None) | (EmployeeEmploymentDetails.effective_to_date >= current_date),
        EmployeeMaster.is_deleted == 'no',
        EmployeeEmploymentDetails.is_deleted == 'no',
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

    employees = query.all()

    if not employees:
        raise HTTPException(status_code=404, detail="No consultant employees found")

    employee_list = [
        ConsultantEmployee(
            employee_id=e.employee_id,
            first_name=e.first_name,
            middle_name=e.middle_name,
            last_name=e.last_name,
            employee_number=e.employee_number,
            personal_email=e.personal_email,
            official_email=e.official_email,
            personal_mobile=e.personal_mobile,
            official_mobile=e.official_mobile,
            department_name=e.department_name,
            designation=e.designation
        )
        for e in employees
    ]

    file_path = os.path.join(UPLOAD_DIR_CONSULTANT_DETAILS, "consultant_employees.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    pdf_buffer = generate_consultant_employees_pdf_template(employee_list, file_path)
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=consultant_employees.pdf"})


#-------------------------------------------------------------------------------------------------------------


    
import mysql.connector
from mysql.connector import Error

def call_stored_procedure(service_id, input_date):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            user="root",
            password="brdb123",
            host="202.21.38.180",
            port="3306",
            database="bharat_taxes_ca_erp"
        )
        cursor = connection.cursor(dictionary=True)
        
        # Call the stored procedure
        cursor.callproc('GetServiceDetails', [service_id, input_date])
        
        # Fetch results
        results = []
        for result_set in cursor.stored_results():
            results.extend(result_set.fetchall())
        
        return results
    
    except Error as e:
        print(f"Error: {e}")
        raise
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Example call
# results = call_stored_procedure(1, '2024-01-01')
# print("Resultcccccccc",results)
#------------------------------------------------------------------------------------------------------------
@router.get("/get_bundle_price_list")
def get_bundle_price_list(request: ServiceRequest=Depends()):
    """
    Query Parameters:
    service_id (int, required): The unique identifier of the service for which the bundle price details are requested.
    input_date (string, optional): The date for which the price details should be retrieved, formatted as YYYY-MM-DD.
    """
    results = call_stored_procedure(request.service_id, request.input_date)
    return {"data": results}




#------------------------------------------------------------------------------------------------------------
@router.get("/get_bundled_price_history", response_model=ServiceResponse)
def get_bundle_price_list(service_id: int, input_date: Optional[str] = None):
    # Call stored procedure or some other DB fetching logic
    results = call_stored_procedure(service_id, input_date)

    # Initialize a dictionary to hold aggregated data
    aggregated_data = defaultdict(lambda: {
        "total_service_charge": 0,
        "total_govt_agency_fee": 0,
        "total_stamp_duty": 0,
        "total_stamp_fee": 0,
        "service_goods_name": None,
        "is_bundled_service": None,
        "constitution_id": None,
        "business_constitution_name": None,
        "effective_from_date": None,
        "effective_to_date": None
    })

    # Iterate over the results and aggregate values
    for item in results:
        constitution_id = item['constitution_id']

        # Aggregate values
        aggregated_data[constitution_id]['total_service_charge'] += item['service_charge']
        aggregated_data[constitution_id]['total_govt_agency_fee'] += item['govt_agency_fee']
        aggregated_data[constitution_id]['total_stamp_duty'] += item['stamp_duty']
        aggregated_data[constitution_id]['total_stamp_fee'] += item['stamp_fee']

        
        aggregated_data[constitution_id]['service_goods_name'] = item['service_goods_name']
        aggregated_data[constitution_id]['is_bundled_service'] = item['is_bundled_service']
        aggregated_data[constitution_id]['constitution_id'] = constitution_id
        aggregated_data[constitution_id]['business_constitution_name'] = item['business_constitution_name']

        # Convert date fields to ISO format strings
        aggregated_data[constitution_id]['effective_from_date'] = item['effective_from_date'].isoformat() if item['effective_from_date'] else None
        aggregated_data[constitution_id]['effective_to_date'] = item['effective_to_date'].isoformat() if item['effective_to_date'] else None

    # Convert the defaultdict to a regular dict
    aggregated_data = dict(aggregated_data)

    # Return the response with aggregated data
    if not aggregated_data:
        raise HTTPException(status_code=404, detail="No data found for the given service ID")

    # Match the response to the expected format of ServiceResponse
    return {"aggregated_data": aggregated_data}




####################################WORKORDER####################################

#-------------------------------------------------------------------------------------------------------------
@router.get('/get_work_order_details')
def get_work_order_details(
    
    entry_point : EntryPoint,
    id          : int,
    visit_master_id : Optional[int] = None,
    enquiry_details_id : Optional[int]= None,
    work_order_details_id: Optional[int] = None,
    db: Session = Depends(get_db),
    token : str = Depends(oauth2.oauth2_scheme)
):
    """
    To retrieves work order details based on the specified entry point and associated IDs. 
    
    The entry points can be `WORK_ORDER`, `CONSULTATION`, or `ENQUIRY`. The behavior of this endpoint 
    depends on the value of `entry_point` and includes different parameters based on the entry point type.

    Parameters: 
        
        - entry_point (required, query parameter): Specifies the type of entry point for the query.   
          It can be `WORK_ORDER`, `CONSULTATION`, or `ENQUIRY`.  
        - id (required, query parameter): The ID associated with the entry point. 

          - If `entry_point` is `WORK_ORDER`, `id` should be the `work_order_master_id`. 
          - If `entry_point` is `CONSULTATION`, `id` should be the `appointment_master_id`. 
          - If `entry_point` is `ENQUIRY`, `id` should be the `enquiry_master_id`. 

        - visit_master_id (optional, query parameter): Required when the `entry_point` is `CONSULTATION`. 
        - enquiry_details_id (optional, query parameter): Required when the `entry_point` is `ENQUIRY`.
        - work_order_details_id (optional) : required when the edit option is selected

    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")


    results = db_office_master.get_work_order_details(db,entry_point,id,visit_master_id,enquiry_details_id,work_order_details_id)
    
    return results




#------------------------------------------------------------------------------------------------------------


@router.get('/get_work_order_list', response_model=List[OffViewWorkOrderMasterSchema])
def get_work_order_list(
    
   
    work_order_number 	    : Optional[str]= None,
    search_value            :  Union[str, int] = "ALL",

    work_order_from_date  	: Optional[date]= None,
    work_order_to_date  	: Optional[date]= None,
    work_order_status_id 	: Optional[Union[int, str]] = "ALL",
    # mobile_number  	    : Optional[str]= None,
    # email_id            : Optional[str]= None,
    db: Session = Depends(get_db),
    token : str = Depends(oauth2.oauth2_scheme)
):
    """
    Retrieve a list of work orders based on the provided filter criteria.

    Parameters:
    - search_value (Union[str, int], optional): The search value to filter work orders. It can be a email id or a mobile number.
    - work_order_from_date (date, optional): The start date to filter work orders.
    - work_order_to_date (date, optional): The end date to filter work orders.
    - work_order_status_id (int, optional): The status ID to filter work orders.

    Returns:
    - List[OffViewWorkOrderMasterSchema]: A list of work orders matching the filter criteria.

    Responses:
    - 200: Successful retrieval of the work order list.
    - 404: No data present based on the filter criteria.
    """
    results = db_office_master.get_work_order_list(
         db,search_value,work_order_number,work_order_status_id,work_order_from_date,work_order_to_date)
    
    return results


#-------------------------------------------------------------------------------------------------------------
@router.get('/get_business_activity_master_by_type_id', response_model=List[BusinessActivityMasterSchema])
def get_business_activity_master_by_type_id(
    activity_type_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    business_activities = db_office_master.get_business_activity_master_by_type_id(db, activity_type_id)
    return business_activities
#-------------------------------------------------------------------------------------------------------------
@router.get('/get_business_activity_by_master_id', response_model=List[BusinessActivitySchema])
def get_business_activity_by_master_id(
    activity_master_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    business_activities = db_office_master.get_business_activity_by_master_id(db, activity_master_id)
    return business_activities
#----------------------------------------------------------------------------------------------------------
@router.get('/get_utility_document_by_nature_of_possession', response_model=List[OffViewServiceDocumentsDataDetailsSchema])
def get_utility_document_by_nature_of_possession(
        service_id: int,
        constitution_id: int,
        nature_of_possession : int,
        db:Session = Depends(get_db)
):
    return db_office_master.get_utility_document_by_nature_of_possession(service_id,constitution_id,nature_of_possession,db)
#------------------------------------------------------------------------------------------------------------
@router.post('/save_work_order')
def save_work_order(
    request: CreateWorkOrderRequest,
    db: Session = Depends(get_db),
    work_order_master_id:Optional[int] =0,
    token: str = Depends(oauth2.oauth2_scheme)
):
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   auth_info = authenticate_user(token)
   user_id = auth_info.get("user_id")
   financial_year_id   =  auth_info.get("financial_year_id") 
   customer_id         =  auth_info.get("mother_customer_id") 
   
   return db_office_master.save_work_order(request, db, user_id,financial_year_id,customer_id,work_order_master_id)


#---------------------------------------------------------------------------------------------------------
@router.post('/save_work_order_service_details')
def save_work_order_service_details(
    request: CreateWorkOrderSetDtailsRequest,
    work_order_details_id:int,
    # business_place_details_id:Optional[int] = 0,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)

):
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   auth_info = authenticate_user(token)
   user_id = auth_info.get("user_id")
   
   return db_office_master.save_work_order_service_details( db,request,work_order_details_id,user_id)

#---------------------------------------------------------------------------------------------------------
@router.get('/get_work_order_service_details')
def get_work_order_service_details(
    work_order_detail_id: int,
    db:Session = Depends(get_db)
):
    
    result  = db_office_master.get_work_order_service_details(db,work_order_detail_id)
    return result
#-----------------------------------------------------------------------------------------------------------
@router.get('/get_work_order_dependancy_service_details')
def get_work_order_dependancy_service_details(
    work_order_master_id : int,
    work_order_details_id : int,
    is_main_service : BooleanFlag,
    db: Session = Depends(get_db)
) :
    """
    Get work order dependency services.  
    Parameters: 
       - work_order_master_id (int): ID of the work order master. 
       - work_order_details_id (int): ID of the current work order details. 
       - is_main_service (BooleanFlag): Indicates if the service is the main service ('yes' or 'no'). 
       - db (Session): Database session dependency.
    Returns:
        List[OffViewWorkOrderDetailsSchema]: List of dependent work order services.
    """
    
    result = db_office_master.get_work_order_dependancy_service_details(db,work_order_details_id,work_order_master_id,is_main_service)
   
    return result

#-----------------------------------------------------------------------------------------------------------

@router.post('/save_work_order_dependancies')
def save_work_order_dependancies(
    depended_works: List[CreateWorkOrderDependancySchema],
    record_action : RecordActionType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save or update work order dependencies based on the action type.

    - depended_works: List of `CreateWorkOrderDependancySchema` objects representing the dependencies to be saved or updated.
    - record_action: Specifies whether to insert new records or update existing ones. Can be `'INSERT_ONLY'` or `'UPDATE_AND_INSERT'`.
    - db: Database session dependency.

    **Returns**:
    - A dictionary with a success message, success status, and list of processed record IDs.
    - In case of error, raises an HTTPException with the appropriate status code.
    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    # auth_info = authenticate_user(token)
    # user_id = auth_info.get("user_id")

    result = db_office_master.save_work_order_dependancies(depended_works, record_action,db)
    
    return result

#--------------------------------------------------------------------------------------------------------------
@router.get('/get_work_order_dependancy_by_work_order_details_id')
def get_work_order_dependancy_by_work_order_details_id(
    work_order_details_id: int,
    db: Session=Depends(get_db)
):
    result = db_office_master.get_work_order_dependancy_by_work_order_details_id(db,work_order_details_id)
    return result

#--------------------------------------------------------------------------------------------------------------


#-------------------------------SERVICE TASK-------------------------------------------------------------------------------

@router.get('/services/get_all_service_task_list', response_model=List[OffViewServiceTaskMasterSchema])
def get_all_service_task_list(
    db: Session = Depends(get_db),
    task_no: Optional[str] = None,
    department_id: Union[int, str] = Query("ALL"),
    team_id: Union[int, str] = Query("ALL"),
    employee_id: Union[int, str] = Query("ALL"),
    status_id: Union[int, str] = Query("ALL"),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    token: str = Depends(oauth2.oauth2_scheme)
) -> List[OffViewServiceTaskMasterSchema]:
    """
    Retrieve a list of service tasks based on various filters.

    Parameters:
    - task_no (str): The task number to search for (partial match).
    - department_id (int or str): The department ID to filter by, or "ALL" for no filtering.
    - team_id (int or str): The team ID to filter by, or "ALL" for no filtering.
    - employee_id (int or str): The employee ID to filter by, or "ALL" for no filtering.
    - status_id (int or str): The status ID to filter by, or "ALL" for no filtering.
    - from_date (date): The start date for filtering tasks.
    - to_date (date): The end date for filtering tasks.
    - token (str): The OAuth2 token for authentication.

    Returns:
    - A list of service tasks that match the given filters.
    """

    # Authenticate the user using the provided token.
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    # Call the database function to retrieve the filtered task list.
    service_tasks = db_office_master.get_all_service_task_list(
        db, task_no, department_id, team_id, employee_id, status_id, from_date, to_date
    )

    return service_tasks




#---------------------------------------------------------------------------------------------

@router.post("/update_service_task/{id}")
def update_service_task(
    id: int,
    task_data: OffServiceTaskMasterSchema, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Updates an existing service task and inserts a history record for the update.
    
    Parameters:
    - id (int): The ID of the service task to update.
    - task_data (OffServiceTaskMasterSchema): The data to update the service task with.
    
    Returns:
    - A success message if the update is successful.
    """

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")  # Extract the user ID from the authentication info

    try:
        db_office_master.update_service_task( db, id, task_data, user_id)

        # Return a success message after the update is completed.
        return {"success": True, "message": "Updated successfully"}
    
    except HTTPException as e:
        # If an HTTPException occurs, re-raise it to be handled by FastAPI's error handling.
        raise e

#----------------------------------------------------------------------------------------------------------------------------

@router.get('/services/get_service_task_history/{task_id}', response_model=List[OffServiceTaskHistorySchema])
def get_service_task_history(
    task_id: int,
    db: Session = Depends(get_db)
) -> List[OffServiceTaskHistorySchema]:
    """
    Retrieve all history entries for a given service_task_master_id.

    Parameters:
    - task_id (int): The ID of the service task master.

    Returns:
    - A list of service task history records.
    """

    # Query the database for all history entries with the given task_id
    history_details = db.query(
        OffServiceTaskHistory,
        EmployeeMaster.first_name.label('history_update_by_first_name'),
        EmployeeMaster.middle_name.label('history_update_by_middle_name'),
        EmployeeMaster.last_name.label('history_update_by_last_name')
    ).join(
        EmployeeMaster, OffServiceTaskHistory.history_update_by == EmployeeMaster.employee_id
    ).filter(
        OffServiceTaskHistory.service_task_master_id == task_id
    ).all()

    # If no history details found, return an empty list
    if not history_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No history found for this service task")

    # Convert the SQLAlchemy query results to the Pydantic schema
    result = []
    for history, first_name, middle_name, last_name in history_details:
        history_data = OffServiceTaskHistorySchema(
            service_task_master_id=history.service_task_master_id,
            # history_updated_on=history.history_updated_on,
            history_updated_date=history.history_updated_on.date(),
            history_updated_time=history.history_updated_on.time(),
            history_update_by=history.history_update_by,
            history_update_by_first_name=first_name,
            history_update_by_middle_name=middle_name,
            history_update_by_last_name=last_name,
            history_description=history.history_description
        )
        result.append(history_data)

    return result






#------------------------------------------------------------------------------------------------------

@router.get('/teams/get_by_department/{department_id}')
def get_teams_by_department(
    department_id: int,
    db: Session = Depends(get_db)
    # token: str = Depends(oauth2.oauth2_scheme)
) -> List[dict]:
    """
    Retrieve all teams associated with a given department_id.

    Parameters:
    - department_id (int): The ID of the department.

    Returns:
    - A list of dictionaries representing teams associated with the department.
    """
    
    teams = db.query(EmployeeTeamMaster).filter(
        EmployeeTeamMaster.department_id == department_id,
        EmployeeTeamMaster.is_deleted == 'no'
    ).all()

    # If no teams found, return an empty list
    if not teams:
        return []
    
    # Convert the result to a list of dictionaries
    teams_list = [
        {
            "team_id": team.id,
            "team_name": team.team_name
           
        }
        for team in teams
    ]
    
    return teams_list



#------------------------------------------------------------------------------------------------------------------

#-------------------------------SERVICE TASK-------------------------------------------------------------------------------
@router.post('/services/assign_reassign_service_task')
def assign_reassign_service_task(
    task_data: ServiceTaskMasterAssign,
    task_id: int,
    assign_to: str = Query(enum=["DEPARTMENT", "TEAM", "EMPLOYEE"],description="Select to assign: DEPARTMENT,TEAM or EMPLOYEE"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Assign or reassign a service task to a department, team, or employee.

    Parameters:
    - task_id (int): The ID of the task to be assigned or reassigned.
    - assign_to (str): Specifies whether to assign to a "DEPARTMENT", "TEAM", or "EMPLOYEE".
    - task_data (ServiceTaskMasterAssign): The data for assignment, including department, team, and employee IDs.
       If 'DEPARTMENT' is selected, 'TEAM' and 'EMPLOYEE' fields must be null.
       If 'TEAM' is selected, 'DEPARTMENT' field must benot  null, but 'EMPLOYEE' is null.
       If 'EMPLOYEE' is selected, both 'DEPARTMENT' and 'TEAM' fields must be not null.
    Returns:
    - A success message if the assignment is successful.
    """

    # Token verification
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    if not auth_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or authentication failed")

    # Update the service task assignment in the master table
    try:
        db_office_master.assign_reassign_service_task(db, task_id, assign_to, task_data, user_id)
        return {"success": True, "message": "Task assigned/reassigned successfully"}
    except HTTPException as e:
        raise e



#--------------------------------------------------------------------------------------------------------------

@router.post('/update_customer_data_document')
def update_customer_data_document(
    update_data: List[UpdateCustomerDataDocumentSchema],
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Endpoint to update customer data document master records.
    
    Updates records in the `customer_data_document_master` table based on the provided data.

    **Parameters:**
    - `update_data`: List of `UpdateCustomerDataDocumentSchema` objects containing update information.
        - `id`: The ID of the record to update (required).
        - `data`: The new data value (required).
        - `valid_from_date`: Optional. The new start date of validity. Set to `null` to remove the date or omit the field to retain the existing date.
        - `valid_to_date`: Optional. The new end date of validity. Set to `null` to remove the date or omit the field to retain the existing date.
    - `db`: The SQLAlchemy database session (required).
    - `token`: OAuth2 token for authorization (required).

    **Request Examples:**

    1. **Updating a Record with New Dates:**
       ```json
      [
        {
            "id": 4,
            "data": "pan",
            "valid_from_date": "2024-08-28",
            "valid_to_date": "2024-12-30"
        },
        {
            "id": 5,
            "data": "voter card",
            "valid_from_date": "2024-08-28",
            "valid_to_date": "2024-12-30"
        }
    ]
       ```

    2. **Removing Dates (Setting to `null`):**
       ```json
       [
         {
           "id": 4,
           "data": "data4",
           "valid_from_date": null,
           "valid_to_date": null
         }
       ]
       ```

    3. **Updating a Record Without Changing Dates:**
       ```json
       [
        {
            "id": 4,
            "data": "pan",
            "valid_from_date": "2024-08-28",
            "valid_to_date": "2024-12-30"
        },
        {
            "id": 5,
            "data": "voter card",
            "valid_from_date": "2024-08-28",
            "valid_to_date": "2024-12-30"
        },
        {
            "id": 6,
            "data": "aahar ",
            "valid_from_date": null,
            "valid_to_date": null
        }
    ]
       ```

    **Returns:**
    - A JSON object with a success status and a message:
      ```json
      {
        "success": true,
        "message": "Records successfully updated"
      }
      ```

    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    try:
        # Try to update the records
        success = db_office_master.update_customer_data_documents(update_data, db)
        return {
            "success": success,
            "message": "Records successfully updated" if success else "Failed to update records"
        }
    except HTTPException as e:
        # If a specific exception is raised, handle it
        return {
            "success": False,
            "message": str(e.detail)
        }
    except Exception as e:
        # Catch any other exceptions and handle them
        return {
            "success": False,
            "message": str(e)
        }
    
#------------------------------------------------------------------------------------------------------

# @router.get("/get_documents_and_data")
# def get_documents(
#     type: Optional[str] = Query(None, description="Filter by type: 'DOCUMENT', 'DATA'"),
#     db: Session = Depends(get_db)
# ) -> List[Dict[str, Any]]:
    
#     """  Fetches a list of documents and data records based on an optional filter type.
#     **Parameters:**

#     - **type** (Optional, `str`): Filter the results by document data type. The value should be either `'DOCUMENT'` or `'DATA'`.
#     """
#     sql_query = text("""
#     SELECT
#         a.id,
#         a.work_order_master_id,
#         a.work_order_details_id,
#         a.document_data_category_id,
#         b.category_name,
#         a.document_data_master_id,
#         c.document_data_name,
#         d.id AS document_data_type_id, 
#         d.document_data_type, 
#         c.has_expiry,
#         a.customer_id,
#         a.stake_holder_master_id,
#         a.data,
#         a.display_order,
#         a.is_document_uploded,
#         a.uploaded_date,
#         a.uploaded_by,
#         a.valid_from_date,
#         a.valid_to_date,
#         a.remarks,
#         a.is_deleted
#     FROM
#         customer_data_document_master a
#     LEFT JOIN
#         off_document_data_category b ON a.document_data_category_id = b.id
#     LEFT JOIN
#         off_document_data_master c ON a.document_data_master_id = c.id
#     LEFT JOIN
#         off_document_data_type d ON c.document_data_type_id = d.id 
#     WHERE
#         a.is_deleted = 'no'
#     AND 
#         (:type IS NULL OR d.document_data_type = :type)
#     """)

#     try:
#         result = db.execute(sql_query, {"type": type})
#         # Convert results to a list of dictionaries
#         results_list = [dict(zip(result.keys(), row)) for row in result.fetchall()]
#         return results_list
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/get_documents_and_data")
def get_documents(
    work_order_master_id: int,  # Required parameter
    type: Optional[str] = Query(None, description="Filter by type: 'DOCUMENT', 'DATA'"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    
    """
    Fetches a list of documents and data records based on work_order_master_id and an optional filter type.
    
    **Parameters:**

    - **work_order_master_id** (int): Filter the results by the work order master ID.
    - **type** (Optional, `str`): Further filter the results by document data type. The value should be either `'DOCUMENT'` or `'DATA'`.
    """

    sql_query = text("""
    SELECT
        a.id,
        a.work_order_master_id,
        a.work_order_details_id,
        a.document_data_category_id,
        b.category_name,
        a.document_data_master_id,
        c.document_data_name,
        d.id AS document_data_type_id, 
        d.document_data_type, 
        c.has_expiry,
        a.customer_id,
        a.stake_holder_master_id,
        a.data,
        a.display_order,
        a.is_document_uploded,
        a.uploaded_date,
        a.uploaded_by,
        a.valid_from_date,
        a.valid_to_date,
        a.remarks,
        a.is_deleted
    FROM
        customer_data_document_master a
    LEFT JOIN
        off_document_data_category b ON a.document_data_category_id = b.id
    LEFT JOIN
        off_document_data_master c ON a.document_data_master_id = c.id
    LEFT JOIN
        off_document_data_type d ON c.document_data_type_id = d.id 
    WHERE
        a.is_deleted = 'no'
    AND 
        a.work_order_master_id = :work_order_master_id
    AND 
        (:type IS NULL OR d.document_data_type = :type)
    """)

    try:
        result = db.execute(sql_query, {"work_order_master_id": work_order_master_id, "type": type})
        # Convert results to a list of dictionaries
        results_list = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        return results_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#-------------------------------------------------------------------------------------------------------
@router.post('/upload_document/{id}')
def upload_document(
   id: int,
   request: DocumentsSchema = Depends(),
   db: Session = Depends(get_db),
   token: str = Depends(oauth2.oauth2_scheme),
   file: UploadFile = File(None)

):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"] 

    try:
        updated_document = db_office_master.upload_documents(db, request, id, user_id, file)
        return {
            "success": True,
            "message": "Uploaded  successfully",
            # "file_url": updated_document.file_url  # Return file URL if needed
        }                  
    except Exception as e:    
        raise HTTPException(status_code=500, detail=str(e))

#-----------------------------------------------------------------------------------------------------
@router.get("/get_upload_document/{id}", response_model=dict)
def get_upload_document(id: int):
    # Search for a file that starts with the given ID and has any extension
    file_path = None
    for file in Path(UPLOAD_WORK_ORDER_DOCUMENTS).glob(f"{id}.*"):
        if file.is_file():
            file_path = file
            break

    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")

    
    return {"photo_url": f"{BASE_URL}/office/upload_document/{file_path.name}"}


#---------------------------------------------------------------------------------------------------
@router.get("/get_sub_services_by_bundled_id/{bundled_service_goods_id}")
def get_bundled_service(bundled_service_goods_id: int, db: Session = Depends(get_db)):
    sub_services = db_office_master.get_sub_services_by_bundled_id(db, bundled_service_goods_id)
    
    return {"bundled_service_goods_id": bundled_service_goods_id, "services": sub_services}

#------------------------------------------------------------------------------------------------------
@router.get("/get_dependent_services")
def get_dependent_services(
    work_order_details_id: int,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Fetches a list of dependent services for a given work_order_details_id.

    **Parameters:**

    - **work_order_details_id** (int): The ID of the work order detail to check for dependencies.

    **Returns:**
    - List of dependent services with their details.
    """
    try:
        # Step 1: Check if the work_order_details_id is a dependent service in work_order_details table
        dependent_service_check_query = text("""
        SELECT is_depended_service 
        FROM work_order_details 
        WHERE id = :work_order_details_id 
        AND is_deleted = 'no'
        """)
        result = db.execute(dependent_service_check_query, {"work_order_details_id": work_order_details_id}).fetchone()
        
        if not result or result[0] != 'yes':
            return []  # Return empty list if it's not a dependent service or doesn't exist

        # Step 2: Fetch dependent service IDs from the work_order_dependency table
        dependency_query = text("""
        SELECT dependent_on_work_id 
        FROM work_order_dependency 
        WHERE work_order_details_id = :work_order_details_id 
        AND is_deleted = 'no'
        """)
        dependent_ids = db.execute(dependency_query, {"work_order_details_id": work_order_details_id}).fetchall()
        
        dependent_ids = [row[0] for row in dependent_ids]

        if not dependent_ids:
            return []

        # Step 3: Fetch the dependent service details from the off_view_work_order_details view
        # Convert the tuple of IDs into a comma-separated string for the SQL query
        dependent_ids_str = ','.join(map(str, dependent_ids))

        dependent_services_query = text(f"""
        SELECT 
            work_order_details_id,
            service_goods_name,
            trade_name,
            leagal_name,
            service_status
        FROM off_view_work_order_details
        WHERE work_order_details_id IN ({dependent_ids_str})
        """)
        result = db.execute(dependent_services_query).fetchall()

        # print("result...............",result)

        # Convert results to a list of dictionaries
        results_list = [
            {
                "work_order_details_id": row[0],
                "service_goods_name": row[1],
                "trade_name": row[2],
                "leagal_name": row[3],
                "service_status":row[4]
            }
            for row in result
        ]

        return results_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#-------------------------------------------------------------------------------------------------------------
# test








# def call_stored_procedure(service_id: int, input_date: Optional[str] = None):
#     connection = None
#     cursor = None
#     try:
#         connection = mysql.connector.connect(
#             user="root",
#             password="brdb123",  # Consider using environment variables
#             host="202.21.38.180",
#             port="3306",
#             database="bharat_taxes_ca_erp"
#         )
#         cursor = connection.cursor(dictionary=True)

#         # Call the stored procedure
#         cursor.callproc('GetServiceDetails', [service_id, input_date])

#         # Fetch results from stored procedure
#         results = []
#         for result_set in cursor.stored_results():
#             results.extend(result_set.fetchall())

#         return results

#     except Error as e:
#         print(f"Error: {e}")  # Consider logging instead of printing
#         raise

#     finally:
#         if cursor:
#             cursor.close()
#         if connection:
#             connection.close()

# @router.get("/test/get_bundle_price_list", response_model=ServiceResponse)
# def get_bundle_price_list(service_id: int, input_date: Optional[str] = None):
#     # Call stored procedure or some other DB fetching logic
#     results = call_stored_procedure(service_id, input_date)

#     # Initialize a dictionary to hold aggregated data
#     aggregated_data = defaultdict(lambda: {
#         "total_service_charge": 0,
#         "total_govt_agency_fee": 0,
#         "total_stamp_duty": 0,
#         "total_stamp_fee": 0,
#         "service_goods_name": None,
#         "is_bundled_service": None,
#         "constitution_id": None,
#         "business_constitution_name": None,
#         "effective_from_date": None,
#         "effective_to_date": None
#     })

#     # Iterate over the results and aggregate values
#     for item in results:
#         constitution_id = item['constitution_id']

#         # Aggregate values
#         aggregated_data[constitution_id]['total_service_charge'] += item['service_charge']
#         aggregated_data[constitution_id]['total_govt_agency_fee'] += item['govt_agency_fee']
#         aggregated_data[constitution_id]['total_stamp_duty'] += item['stamp_duty']
#         aggregated_data[constitution_id]['total_stamp_fee'] += item['stamp_fee']

#         # Set other fields (assuming they are the same across all items with the same constitution_id)
#         aggregated_data[constitution_id]['service_goods_name'] = item['service_goods_name']
#         aggregated_data[constitution_id]['is_bundled_service'] = item['is_bundled_service']
#         aggregated_data[constitution_id]['constitution_id'] = constitution_id
#         aggregated_data[constitution_id]['business_constitution_name'] = item['business_constitution_name']

#         # Convert date fields to ISO format strings
#         aggregated_data[constitution_id]['effective_from_date'] = item['effective_from_date'].isoformat() if item['effective_from_date'] else None
#         aggregated_data[constitution_id]['effective_to_date'] = item['effective_to_date'].isoformat() if item['effective_to_date'] else None

#     # Convert the defaultdict to a regular dict
#     aggregated_data = dict(aggregated_data)

#     # Return the response with aggregated data
#     if not aggregated_data:
#         raise HTTPException(status_code=404, detail="No data found for the given service ID")

#     # Match the response to the expected format of ServiceResponse
#     return {"aggregated_data": aggregated_data}



def log_activity(db: Session, user_id: int, action_type: str, db_table_name: str, action_query: str):
    try:
        # Create a new activity history record
        activity_history = AppActivityHistory(
            action_taken_on=datetime.utcnow(),
            action_taken_by=user_id,
            action_type=action_type,
            db_table_name=db_table_name,
            action_query=action_query
        )
        
        # Add the new record to the session and commit
        db.add(activity_history)
        db.commit()
    except Exception as e:
        db.rollback()  # Rollback in case of error
        print(f"Error logging activity: {str(e)}")  # Log the error as needed

@router.post("/test/save_consultant_schedule/")
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
            save_consultant_schedule_detail_test(data, consultant_id, user_id, id, action_type, db)
        
        return {"success": True, "detail": "Saved successfully"}
    
    except Exception as e:
        print(f"Error in endpoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    

def save_consultant_schedule_detail_test(
    schedule_data: ConsultantScheduleCreate,
    consultant_id: Optional[int],
    user_id: int,
    id: Optional[int],
    action_type: RecordActionType,
    db: Session
):
    try:
        # Convert schedule_data to dictionary format for processing
        schedule_dict = schedule_data.model_dump()
        print("schedule_dict", schedule_dict)

        # Handle special schedules (`is_normal_schedule == "no"`)
        if schedule_data.is_normal_schedule == "no":
            if not schedule_data.consultation_date:
                raise ValueError("For 'is_normal_schedule' no, 'consultation_date' must be provided.")
            
            # Remove `effective_from_date` as it's not needed in special schedules
            schedule_dict.pop("effective_from_date", None)

            # Assign `day_of_week_id` using SQL query based on `consultation_date`
            day_of_week_query = text(f"SELECT DAYOFWEEK('{schedule_data.consultation_date}')")
            day_of_week_id = db.execute(day_of_week_query).fetchone()[0]
            schedule_dict['day_of_week_id'] = day_of_week_id

            # INSERT ONLY logic
            if action_type == RecordActionType.INSERT_ONLY:
                if consultant_id is None:
                    raise ValueError("consultant_id is required for INSERT_ONLY")
                
                # Check if the record already exists to avoid duplicates
                existing_schedule = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.consultation_date == schedule_data.consultation_date,
                    OffConsultantSchedule.consultation_mode_id == schedule_data.consultation_mode_id
                ).first()

               
                if existing_schedule:
                    raise ValueError("A schedule for this consultant on this date already exists.")

                # Insert the new schedule
                new_schedule = OffConsultantSchedule(
                    **schedule_dict, 
                    consultant_id=consultant_id, 
                    created_by=user_id, 
                    created_on=datetime.now()
                )

                stmt = insert(OffConsultantSchedule).values(
                **schedule_dict, 
                consultant_id=consultant_id, 
                created_by=user_id, 
                created_on=datetime.now()
            )

            # Compile the statement to get the raw SQL
                action_query = str(stmt.compile(compile_kwargs={"literal_binds": True}))
                print("action_query:", action_query)
                action_type = action_query.split()[0]  # This will give you the first word
                print("action_type:", action_type)  #


                
                db.add(new_schedule)
                db.commit()

                # Log activity
                log_activity(
                    db=db,
                    user_id=user_id,
                    action_type=action_type,
                    db_table_name="OffConsultantSchedule",
                    action_query=action_query
                )

                return True

            # UPDATE ONLY logic
            elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
                # Fetch the existing schedule based on the provided ID
                existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()

                if not existing_schedule:
                    raise ValueError(f"Schedule with ID {id} not found.")

                # Update only the fields that are provided in the schedule_dict
                for key, value in schedule_dict.items():
                    setattr(existing_schedule, key, value)

                # Update the modification metadata
                existing_schedule.modified_by = user_id
                existing_schedule.modified_on = datetime.now()
                
                # Commit the update to the existing schedule
                db.commit()

                # Log activity
                log_activity(
                    db=db,
                    user_id=user_id,
                    action_type="UPDATE",
                    db_table_name="OffConsultantSchedule",
                    action_query=str(db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id))  # Log the SQL query
                )

                return True

            else:
                raise ValueError("Invalid action type for special schedules (is_normal_schedule = 'no').")

        # Handle normal schedules (`is_normal_schedule == "yes"`)
        elif schedule_data.is_normal_schedule == "yes":
            if action_type == RecordActionType.UPDATE_AND_INSERT:
                if consultant_id is None:
                    raise ValueError("consultant_id is required for UPDATE_AND_INSERT")

                # Ensure `effective_from_date` is provided
                effective_from_date = schedule_dict.get('effective_from_date')
                if not effective_from_date:
                    raise ValueError("effective_from_date is required for UPDATE_AND_INSERT when is_normal_schedule is 'yes'.")

                # Query for the existing schedule (active record)
                existing_schedule_query = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.day_of_week_id == schedule_dict['day_of_week_id'],
                    OffConsultantSchedule.consultation_mode_id == schedule_dict['consultation_mode_id'],
                    OffConsultantSchedule.effective_to_date.is_(None)
                )
                existing_schedule = existing_schedule_query.first()

                # If an active schedule exists, update its `effective_to_date`
                if existing_schedule:
                    new_effective_to_date = effective_from_date - timedelta(days=1)
                    existing_schedule.effective_to_date = new_effective_to_date
                    existing_schedule.modified_by = user_id
                    existing_schedule.modified_on = datetime.now()
                    db.commit()  # Commit the update for the existing schedule

                    # Log activity for existing schedule update
                    log_activity(
                        db=db,
                        user_id=user_id,
                        action_type="UPDATE",
                        db_table_name="OffConsultantSchedule",
                        action_query=str(existing_schedule_query)  # Log the SQL query
                    )

                # Insert the new schedule
                new_schedule = OffConsultantSchedule(
                    **schedule_dict, 
                    consultant_id=consultant_id, 
                    created_by=user_id, 
                    created_on=datetime.now()
                )
                db.add(new_schedule)
                db.commit()

                # Log activity for new schedule insertion
                log_activity(
                    db=db,
                    user_id=user_id,
                    action_type="INSERT",
                    db_table_name="OffConsultantSchedule",
                    action_query=f"Inserted new schedule for consultant ID {consultant_id}: {schedule_dict}"
                )

                return True

            # UPDATE ONLY logic for normal schedule
            elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
                # Handle the update of an existing schedule based on the provided ID
                existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()
                if existing_schedule:
                    for key, value in schedule_dict.items():
                        setattr(existing_schedule, key, value)
                    existing_schedule.modified_by = user_id
                    existing_schedule.modified_on = datetime.now()
                    db.commit()

                    # Log activity for updating an existing schedule
                    log_activity(
                        db=db,
                        user_id=user_id,
                        action_type="UPDATE",
                        db_table_name="OffConsultantSchedule",
                        action_query=str(db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id))  # Log the SQL query
                    )

                    return True
                else:
                    raise ValueError(f"Schedule with ID {id} not found.")

            else:
                raise ValueError("Invalid action type for normal schedules (is_normal_schedule = 'yes').")

        else:
            raise ValueError("Invalid schedule type or action type provided.")

    except Exception as e:
        db.rollback()  # Rollback changes in case of an error
        raise HTTPException(status_code=400, detail=str(e))