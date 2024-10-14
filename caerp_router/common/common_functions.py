from enum import Enum
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from caerp_db.accounts.models import AccProformaInvoiceMaster, AccQuotationMaster, AccTaxInvoiceMaster
from caerp_db.common.models import AppDesignation, BloodGroupDB, BusinessActivityType, EmployeeDocuments,EmployeeEducationalQualification, EmployeeEmploymentDetails, EmployeeExperience, EmployeeMaster, EmployeeProfessionalQualification, Gender,  MaritalStatus, NationalityDB, Profession, UsersRole
from caerp_db.database import get_db
from caerp_db.hr_and_payroll.model import EmployeeTeamMaster, HrDepartmentMaster, HrDesignationMaster, HrDocumentMaster, HrEmployeeCategory, PrlCalculationFrequency, PrlCalculationMethod, PrlSalaryComponent
from caerp_db.office import db_office_master

from caerp_db.office.models import AppBusinessConstitution, AppDayOfWeek, AppHsnSacClasses, AppHsnSacMaster, AppStockKeepingUnitCode, OffAppointmentCancellationReason, OffAppointmentMaster, OffAppointmentStatus, OffConsultationMode, OffConsultationTaskStatus, OffDocumentDataCategory, OffDocumentDataMaster, OffDocumentDataType, OffEnquirerType, OffEnquiryMaster, OffEnquiryStatus, OffNatureOfPossession, OffServiceDocumentDataDetails, OffServiceGoodsCategory, OffServiceGoodsGroup, OffServiceGoodsMaster, OffServiceGoodsSubCategory, OffServiceGoodsSubGroup, OffServiceTaskStatus, OffSourceOfEnquiry, OffTaskPriority, OffWorkOrderMaster, OffWorkOrderStatus


from caerp_auth import oauth2
from sqlalchemy import inspect
from typing import Optional
from datetime import datetime
from caerp_auth import oauth2
from caerp_auth.authentication import authenticate_user


from caerp_db.services.model import GstReasonToObtainRegistration, GstTypeOfRegistration

router = APIRouter(
    tags=['LIBRARY FUNCTIONS']
)


class ActionType(str, Enum):
    DELETE = 'DELETE'
    UNDELETE = 'UNDELETE'

class LockType(str, Enum):
    LOCK = 'LOCK'
    UNLOCK = 'UNLOCK'

from api_library.api_library import DynamicAPI

from typing import List, Type

TABLE_MODEL_MAPPING = {
    "OffAppointmentCancellationReason": OffAppointmentCancellationReason,
    "OffAppointmentStatus": OffAppointmentStatus,
    "OffAppointmentMaster": OffAppointmentMaster,
    "AppHsnSacClasses": AppHsnSacClasses,
    "OffServiceGoodsGroup" : OffServiceGoodsGroup,
    "OffServiceGoodsSubGroup" : OffServiceGoodsSubGroup,
    "OffServiceGoodsCategory":  OffServiceGoodsCategory,
    "OffServiceGoodsSubCategory": OffServiceGoodsSubCategory,
    "AppHsnSacMaster":AppHsnSacMaster,
    "AppStockKeepingUnitCode":AppStockKeepingUnitCode,
    "AppBusinessConstitution":AppBusinessConstitution,
    "OffDocumentDataMaster":OffDocumentDataMaster,
    "OffDocumentDataType":OffDocumentDataType,
    "Gender":Gender,
    "OffDocumentDataCategory":OffDocumentDataCategory,
    "OffNatureOfPossession":OffNatureOfPossession,
    "PrlCalculationFrequency":PrlCalculationFrequency,
    "PrlCalculationMethod":PrlCalculationMethod,
    "PrlSalaryComponent":PrlSalaryComponent,
    "MaritalStatus":MaritalStatus,
    "AppDesignation":AppDesignation,
    "NationalityDB":NationalityDB,
    "BloodGroupDB":BloodGroupDB,
    "HrDocumentMaster":HrDocumentMaster,
    "HrDepartmentMaster":HrDepartmentMaster,
    "HrDesignationMaster":HrDesignationMaster,
    "HrEmployeeCategory":HrEmployeeCategory,
    "EmployeeEducationalQualification":EmployeeEducationalQualification,
    "OffEnquiryStatus":OffEnquiryStatus,
    "OffSourceOfEnquiry":OffSourceOfEnquiry,
    "OffEnquirerType":OffEnquirerType,
    "OffConsultationMode":OffConsultationMode,
    "UsersRole":UsersRole,
    "AppDayOfWeek":AppDayOfWeek,
    "OffTaskPriority":OffTaskPriority,
    "OffConsultationTaskStatus":OffConsultationTaskStatus,
    "OffServiceGoodsMaster":OffServiceGoodsMaster,
    "OffWorkOrderStatus":OffWorkOrderStatus,
    "BusinessActivityType"       : BusinessActivityType,
    "EmployeeProfessionalQualification":EmployeeProfessionalQualification,
    "EmployeeExperience":EmployeeExperience,
    "EmployeeDocuments" :EmployeeDocuments,
    "EmployeeTeamMaster":EmployeeTeamMaster,
    "GstReasonToObtainRegistration":GstReasonToObtainRegistration,
    "GstTypeOfRegistration":GstTypeOfRegistration,
    "OffServiceDocumentDataDetails":OffServiceDocumentDataDetails,
    "Profession":Profession,
    "OffServiceTaskStatus":OffServiceTaskStatus,
    "AccQuotationMaster":AccQuotationMaster,
    "EmployeeEmploymentDetails":EmployeeEmploymentDetails,
    "OffEnquiryMaster":OffEnquiryMaster,
    "OffWorkOrderMaster":OffWorkOrderMaster,
    "AccTaxInvoiceMaster":AccTaxInvoiceMaster,
    "AccProformaInvoiceMaster":AccProformaInvoiceMaster
    
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



@router.get("/get_info", operation_id="get_appointment_info")
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

@router.get("/delete_undelete_by_id", operation_id="modify_records")
async def delete_undelete_by_id(
    model_name: str = Query(..., description="Model name to fetch data from"),
    ids: str = Query(..., description="Comma-separated list of IDs of the records to modify"),
    action: ActionType = Query(..., description="Action to perform (DELETE or UNDELETE)"),
    db: Session = Depends(get_db)
):
    """
    Perform delete or undelete operations on records based on provided model name and IDs.
    """
    # Get the model class based on the provided model name
    table_model = get_model_by_model_name(model_name)

    # Check if the model exists
    if table_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    # Convert the comma-separated string of IDs into a list of integers
    try:
        id_list = [int(id_str) for id_str in ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs must be a comma-separated list of integers")

    # Initialize DynamicAPI instance with the retrieved model
    dynamic_api = DynamicAPI(table_model)

    if action == ActionType.DELETE:
        # Delete the records
        dynamic_api.delete_records_by_ids(db, id_list)
        return {"message": f"Records with IDs {id_list} from model {model_name} have been deleted"}
    elif action == ActionType.UNDELETE:
        # Undelete the records
        dynamic_api.undelete_records_by_ids(db, id_list)
        return {"message": f"Records with IDs {id_list} from model {model_name} have been undeleted"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action type")
       
#--------------------------------------------------------
# @router.post("/lock_unlock", operation_id="lock_unlock_record")
# async def lock_unlock(
#     model_name: str = Query(..., description="Model name to fetch data from"),
#     id: Optional[int] = Query(None, description="ID of the record to lock/unlock"),
#     is_locked: str = Query(..., description="Lock/Unlock status (yes/no)"),
#     token: str = Depends(oauth2.oauth2_scheme),
#     db: Session = Depends(get_db)
# ):
#     """
#     Lock or Unlock a record based on the provided model name and ID.
#     The token is used to extract the user_id for `locked_by`, and the current date is used for `locked_on`.
#     """
#     # Get the model class based on the provided model name
#     table_model = get_model_by_model_name(model_name)

#     # Check if the model exists
#     if table_model is None:
#         raise HTTPException(status_code=404, detail="Model not found")

#     # Retrieve the user info from the token
#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")

#     if user_id is None:
#         raise HTTPException(status_code=401, detail="Invalid user or token")

#     # Query the record based on the given ID
#     record = db.query(table_model).filter(table_model.id == id).first()

#     if not record:
#         raise HTTPException(status_code=404, detail="Record not found")

#     # Lock/Unlock logic
#     if is_locked == "yes":
#         record.is_locked = "yes"
#         record.locked_on = datetime.now()  # Set the current date
#         record.locked_by = user_id         # Set the user ID from the token
#     elif is_locked == "no":
#         record.is_locked = "no"
#         record.locked_on = None            # Clear the lock date
#         record.locked_by = None            # Clear the lock user
#     else:
#         raise HTTPException(status_code=400, detail="Invalid is_locked value. Use 'yes' or 'no'.")

#     # Commit the changes
#     db.commit()

#     return {"message": f"Record with ID {id} from model {model_name} has been {'locked' if is_locked == 'yes' else 'unlocked'}."}

@router.post("/lock_unlock", operation_id="lock_unlock_record")
async def lock_unlock(
    model_name: str = Query(..., description="Model name to fetch data from"),
    id: Optional[int] = Query(None, description="ID of the record to lock/unlock"),
    action: LockType = Query(..., description="Action to perform (LOCK or UNLOCK)"),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Lock or Unlock a record based on the provided model name and ID.
    The token is used to extract the user_id for `locked_by`, and the current date is used for `locked_on`.
    """
    # Get the model class based on the provided model name
    table_model = get_model_by_model_name(model_name)

    # Check if the model exists
    if table_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    # Retrieve the user info from the token
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid user or token")

    # Query the record based on the given ID
    record = db.query(table_model).filter(table_model.id == id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Lock/Unlock logic
    if action == LockType.LOCK:
        record.is_locked = "yes"
        record.locked_on = datetime.now()  # Set the current date
        record.locked_by = user_id         # Set the user ID from the token
    elif action == LockType.UNLOCK:
        record.is_locked = "no"
        record.locked_on = None            # Clear the lock date
        record.locked_by = None            # Clear the lock user
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'LOCK' or 'UNLOCK'.")

    # Commit the changes
    db.commit()

    # Prepare the response data
    response_data = {
        "message": f"Record with ID {id} from model {model_name} has been {'locked' if action == LockType.LOCK else 'unlocked'}.",
        "success": True,
        "locked": action == LockType.LOCK  # True if locked, False if unlocked
    }

    return response_data

#-------------------------------------------------------------------------------------------------
# @router.get("/get_record_with_employee_names")
# async def get_record_with_employee_names(
#     model_name: str = Query(..., description="Model name to fetch data from"),
#     id: int = Query(..., description="ID of the record"),
#     token: str = Depends(oauth2.oauth2_scheme),
#     db: Session = Depends(get_db)
# ):
#     """
#     This endpoint retrieves a record and joins with EmployeeMaster to get the names for created_by, modified_by, and deleted_by.
#     """
#     # Step 1: Get user info from the token (not necessary for fetching but included as per your use case)
#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")

#     # Step 2: Fetch the model dynamically based on model_name
#     model = globals().get(model_name)
#     if not model:
#         raise HTTPException(status_code=404, detail="Model not found")

#     # Step 3: Fetch the record based on ID
#     record = db.query(model).filter(model.id == id).first()
#     if not record:
#         raise HTTPException(status_code=404, detail="Record not found")

#     # Step 4: Fetch employee names for created_by, modified_by, and deleted_by
#     created_by_employee = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == record.created_by).first()
#     modified_by_employee = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == record.modified_by).first()
#     deleted_by_employee = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == record.deleted_by).first()

#     # Step 5: Prepare response with employee names
#     response_data = {
#         "record_id": record.id,
#         "created_by": {
#             "id": record.created_by,
#             "name": f"{created_by_employee.first_name} {created_by_employee.middle_name or ''} {created_by_employee.last_name}" if created_by_employee else None
#         },
#         "modified_by": {
#             "id": record.modified_by,
#             "name": f"{modified_by_employee.first_name} {modified_by_employee.middle_name or ''} {modified_by_employee.last_name}" if modified_by_employee else None
#         },
#         "deleted_by": {
#             "id": record.deleted_by,
#             "name": f"{deleted_by_employee.first_name} {deleted_by_employee.middle_name or ''} {deleted_by_employee.last_name}" if deleted_by_employee else None
#         }
#     }

#     # Return the response with the employee names
#     return response_data




@router.get("/get_record_details_with_employee_names")
async def get_record_with_employee_names(
    model_name: str = Query(..., description="Model name to fetch data from"),
    id: int = Query(..., description="ID of the record"),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    This endpoint retrieves a record and joins with EmployeeMaster to get the names for created_by, modified_by, and deleted_by fields,
    if those fields are present in the model.
    """
    # Step 1: Get user info from the token (not necessary for fetching but included as per your use case)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    # Step 2: Fetch the model dynamically based on model_name
    model = globals().get(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Step 3: Fetch the record based on ID
    record = db.query(model).filter(model.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Step 4: Check which columns exist in the model
    mapper = inspect(model)
    available_columns = {col.key for col in mapper.attrs}
    
    response_data = {"record_id": record.id}

    # Step 5: Get names for each field, if it exists
    if "created_by" in available_columns:
        created_by_employee = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == getattr(record, "created_by")).first()
        response_data["created_by"] = {
            "id": getattr(record, "created_by"),
            "name": f"{created_by_employee.first_name} {created_by_employee.middle_name or ''} {created_by_employee.last_name}" if created_by_employee else None
        }

    if "modified_by" in available_columns:
        modified_by_employee = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == getattr(record, "modified_by")).first()
        response_data["modified_by"] = {
            "id": getattr(record, "modified_by"),
            "name": f"{modified_by_employee.first_name} {modified_by_employee.middle_name or ''} {modified_by_employee.last_name}" if modified_by_employee else None
        }

    if "deleted_by" in available_columns:
        deleted_by_employee = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == getattr(record, "deleted_by")).first()
        response_data["deleted_by"] = {
            "id": getattr(record, "deleted_by"),
            "name": f"{deleted_by_employee.first_name} {deleted_by_employee.middle_name or ''} {deleted_by_employee.last_name}" if deleted_by_employee else None
        }

    # Return the response with the employee names, based on available fields
    return response_data




#-0---------------------------------------------------------------------------------------------------------------------




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
#....................................................................................................


@router.post("/check_duplicate")
async def check_duplicate(
    model_name: str = Query(..., description="Model name to fetch data from"),
    field: str = Query(..., description="Field to check for duplicates"),
    name: str = Query(..., description="Name to check for duplicates"),
    id: int = Query(0, description="ID to exclude from the duplicate check (0 to include all)"),
    db: Session = Depends(get_db)
):
    """
    Search if the entered name already exists in the given table and field.
    """
    try:
        # Retrieve the model from the mapping
        model = TABLE_MODEL_MAPPING.get(model_name)
        
        if not model:
            raise HTTPException(status_code=400, detail="Invalid model name")

        # Initialize DynamicAPI instance with the retrieved model
        dynamic_api = DynamicAPI(model)

        # Check for duplicate
        is_duplicate = dynamic_api.check_duplicate(db, field, name, id)
        if is_duplicate:
            return {"success": True, "message": "Duplicate entry"}
        
    except Exception as e:
        raise HTTPException(status_code=500)


