from enum import Enum
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from caerp_db.common.models import AppDesignation, BloodGroupDB, BusinessActivityType,EmployeeEducationalQualification, Gender, HrDepartmentMaster, HrDesignationMaster, HrDocumentMaster, HrEmployeeCategory, MaritalStatus, NationalityDB, UsersRole
from caerp_db.database import get_db
from caerp_db.hr_and_payroll.model import PrlCalculationFrequency, PrlCalculationMethod, PrlSalaryComponent
from caerp_db.office import db_office_master

from caerp_db.office.models import AppBusinessConstitution, AppDayOfWeek, AppHsnSacClasses, AppHsnSacMaster, AppStockKeepingUnitCode, OffAppointmentCancellationReason, OffAppointmentMaster, OffAppointmentStatus, OffConsultationMode, OffDocumentDataCategory, OffDocumentDataMaster, OffDocumentDataType, OffEnquirerType, OffEnquiryStatus, OffNatureOfPossession, OffServiceGoodsCategory, OffServiceGoodsGroup, OffServiceGoodsMaster, OffServiceGoodsSubCategory, OffServiceGoodsSubGroup, OffSourceOfEnquiry, OffTaskPriority, OffTaskStatus, OffWorkOrderStatus


from caerp_auth import oauth2

from typing import Optional
from datetime import date

router = APIRouter(
    tags=['LIBRARY FUNCTIONS']
)


class ActionType(str, Enum):
    DELETE = 'DELETE'
    UNDELETE = 'UNDELETE'

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
    "OffTaskStatus":OffTaskStatus,
    "OffServiceGoodsMaster":OffServiceGoodsMaster,
    "OffWorkOrderStatus":OffWorkOrderStatus,
    "BusinessActivityType"       : BusinessActivityType,
    
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


