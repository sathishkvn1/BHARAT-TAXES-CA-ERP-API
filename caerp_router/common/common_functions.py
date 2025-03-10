from enum import Enum
import json
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status


from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session

from caerp_db.accounts.models import AccProformaInvoiceMaster, AccQuotationMaster, AccTaxInvoiceMaster
from caerp_db.common.models import AppBankAccountType, AppConstitutionStakeholders, AppDesignation, AppEducationSubjectCourse, AppEducationalLevel, AppEducationalStream, AppLanguageProficiency, AppLanguages, AppSkills, BloodGroupDB, BusinessActivity, BusinessActivityMaster, BusinessActivityType, CountryDB, EmployeeDocuments,EmployeeEducationalQualification, EmployeeEmploymentDetails, EmployeeExperience, EmployeeLanguageProficiency, EmployeeMaster, EmployeeProfessionalQualification, Gender,  MaritalStatus, MenuLocation, NationalityDB, Profession, StateDB, UsersRole
from caerp_db.database import get_db
from caerp_db.hr_and_payroll.model import EmployeeTeamMaster, HrDepartmentMaster, HrDesignationMaster, HrDocumentMaster, HrEmployeeCategory, PrlCalculationFrequency, PrlCalculationMethod, PrlSalaryComponent


from caerp_db.office.models import AppBusinessConstitution, AppDayOfWeek, AppHsnSacClasses, AppHsnSacMaster, AppStockKeepingUnitCode, OffAppointmentCancellationReason, OffAppointmentMaster, OffAppointmentStatus, OffAppointmentVisitMaster, OffConsultationMode, OffConsultationTaskMaster, OffConsultationTaskStatus, OffDocumentDataCategory, OffDocumentDataMaster, OffDocumentDataType, OffEnquirerType, OffEnquiryDetails, OffEnquiryMaster, OffEnquiryStatus, OffNatureOfPossession, OffServiceDocumentDataDetails, OffServiceDocumentDataMaster, OffServiceGoodsCategory, OffServiceGoodsGroup, OffServiceGoodsMaster, OffServiceGoodsSubCategory, OffServiceGoodsSubGroup, OffServiceTaskMaster, OffServiceTaskStatus, OffSourceOfEnquiry, OffTaskPriority, OffWorkOrderMaster, OffWorkOrderStatus
from sqlalchemy import update, Table, MetaData
from sqlalchemy.exc import NoResultFound




from caerp_auth import oauth2
from sqlalchemy import inspect
from typing import Optional
from datetime import datetime
from caerp_auth import oauth2
from caerp_auth.authentication import authenticate_user
from typing import List


from caerp_db.services.model import GstOtherAuthorizedRepresentativeResignation, GstReasonToObtainRegistration, GstTypeOfRegistration

router = APIRouter(
    tags=['LIBRARY FUNCTIONS']
)


class ActionType(str, Enum):
    DELETE = 'DELETE'
    UNDELETE = 'UNDELETE'

class LockType(str, Enum):
    LOCK = 'LOCK'
    UNLOCK = 'UNLOCK'

class FetchRecordsRequest(BaseModel):
    search_key_id: int
    search_key_field: str  # Add this line
    fields: List[str] = None


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
    "AccProformaInvoiceMaster":AccProformaInvoiceMaster,
    "EmployeeMaster":EmployeeMaster,
    "OffServiceTaskMaster":OffServiceTaskMaster,
    "OffServiceDocumentDataMaster":OffServiceDocumentDataMaster,
    "OffConsultationTaskMaster":OffConsultationTaskMaster,
    "StateDB":StateDB,
    "CountryDB":CountryDB,
    "AppConstitutionStakeholders":AppConstitutionStakeholders,
    "OffEnquiryDetails":OffEnquiryDetails,
    "OffAppointmentVisitMaster":OffAppointmentVisitMaster,
    "BusinessActivity":BusinessActivity,
    "BusinessActivityMaster":BusinessActivityMaster,
    "GstOtherAuthorizedRepresentativeResignation":GstOtherAuthorizedRepresentativeResignation,
    "AppEducationalLevel":AppEducationalLevel,
    "AppEducationalStream":AppEducationalStream,
    "AppEducationSubjectCourse":AppEducationSubjectCourse,
    "AppBankAccountType":AppBankAccountType,
    "AppLanguageProficiency":AppLanguageProficiency,
    "AppLanguages":AppLanguages,
    "EmployeeLanguageProficiency":EmployeeLanguageProficiency,
    "MenuLocation" : MenuLocation,
    "AppSkills":AppSkills,
  
   
    
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

#........................fr delete---------------------------------------------------------------------
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
       
#-----------------------------------------------------------------------------------------------------------------

# @router.get("/lock_unlock_record", operation_id="lock_unlock_record")
# async def lock_unlock(
#     model_name: str = Query(..., description="Model name to fetch data from"),
#     id: Optional[int] = Query(None, description="ID of the record to lock/unlock"),
#     action: LockType = Query(..., description="Action to perform (LOCK or UNLOCK)"),
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
#     is_locked = record.is_locked
#     if action == LockType.LOCK:
#         record.is_locked = "yes"
#         record.locked_on = datetime.now()  # Set the current date
#         record.locked_by = user_id         # Set the user ID from the token
#     elif action == LockType.UNLOCK:
#         record.is_locked = "no"
#         record.locked_on = None            # Clear the lock date
#         record.locked_by = None            # Clear the lock user
#     else:
#         raise HTTPException(status_code=400, detail="Invalid action. Use 'LOCK' or 'UNLOCK'.")

#     # Commit the changes
#     db.commit()

#     # Prepare the response data
#     response_data = {
#         "message": f"Record with ID {id} from model {model_name} has been {'locked' if action == LockType.LOCK else 'unlocked'}.",
#         "success": True,
#         "locked":is_locked
#         # "locked": action == LockType.LOCK  # True if locked, False if unlocked
#     }

#     return response_data



@router.get("/lock_unlock_record", operation_id="lock_unlock_record")
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

    # Query the record based on the given ID or employee_id if the model is EmployeeMaster
    if table_model == EmployeeMaster:
        record = db.query(table_model).filter(table_model.employee_id == id).first()
    else:
        record = db.query(table_model).filter(table_model.id == id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Lock/Unlock logic
    is_locked = record.is_locked
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
        "locked": is_locked  # Reflect the lock status before the change
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









def update_column_value(db: Session, table_name: str, row_id: int, field_name: str, value):
    """
    Updates a specific field in a table for a given row.

    :param db: SQLAlchemy Session object.
    :param table_name: Name of the table where the record is to be updated.
    :param row_id: ID of the row to update.
    :param field_name: Name of the field to update.
    :param value: New value to set for the field.
    :return: None
    """
    try:
        # Reflect the table from the database
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=db.bind)
        
        # Check if the table has the field_name as a column
        if field_name not in table.c:
            raise ValueError(f"Field '{field_name}' does not exist in table '{table_name}'.")

        # Build the update query
        stmt = (
            update(table)
            .where(table.c.id == row_id)  # Assuming the primary key column is 'id'
            .values({field_name: value})
        )

        # Execute the update query
        result = db.execute(stmt)
        
        # Commit the changes if the row was successfully updated
        if result.rowcount > 0:
            db.commit()
            # print(f"Successfully updated {field_name} in {table_name} for row with ID {row_id}.")
            return {
                'message': f"Successfully updated {field_name} in {table_name} for row with ID {row_id}.",
                'success': True
            }
        else:
            # print(f"No row found with ID {row_id} in table {table_name}.")
            return {
                'message': f"No row found with ID {row_id} in table {table_name}.",
                'success': False
            }

    except NoResultFound:
        print(f"No row found with ID {row_id} in table {table_name}.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")

from typing import List


def fetch_related_records(
    db: Session,
    model: Type,               # The model to query (e.g., AppState)
    search_key_model: Type,    # The model containing the foreign key (e.g., AppCountry)
    search_key_id: int,        # The ID value of the foreign key used to filter records
    search_key_field: str,     # The name of the foreign key field in the model (e.g., country_id)
    fields: List[str] = None   # Optional list of specific fields to retrieve
) -> List[dict]:
    try:
        # Prepare the query to filter records by joining the search_key_model
        query = (
            db.query(model)
            .join(search_key_model, getattr(model, search_key_field) == search_key_model.id)
            .filter(search_key_model.id == search_key_id)
        )
        print("Generated SQL Query:", str(query))
        
        # If specific fields are provided, select only those fields
        if fields:
            query = query.with_entities(*[getattr(model, field) for field in fields])
        
        # Execute the query and fetch results
        records = query.all()
        
        # Convert query results to dictionaries if fields are specified
        if fields:
            return [dict(zip(fields, record)) for record in records]
        
        # Return the full record if no specific fields are provided
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# @router.post("/fetch-related-records/{model_name}/{search_key_model_name}")
# async def fetch_related_records_endpoint(
#     model_name: str,
#     search_key_model_name: str,
#     request: FetchRecordsRequest,
#     token: str = Depends(oauth2.oauth2_scheme),
#     db: Session = Depends(get_db)
# ):
    
#     """
#     model_name (string): The name of the primary model to query .
#     search_key_model_name (string): The name of the model that contains the foreign key referenced by the primary model.
#     Example: AppBusinessConstitution (this model does not contain a foreign key; instead, the foreign key exists in AppConstitutionStakeholders, referencing AppBusinessConstitution).
#     search_key_id:This is the ID of the record in the related (foreign key) model that you want to filter by. It represents a specific instance of that model.
#     search_key_field: Defines which field in your model you will use to join with the foreign key model.

#     eg-
#    model_name: AppConstitutionStakeholders
#    search_key_model_name :  AppBusinessConstitution

#     {
#     "search_key_id": 2,
#     "search_key_field": "constitution_id",
#     "fields": [
#         "id","stakeholder" 
#     ]
#     }
#     """

#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
#     # Check if the model names exist in the mapping
#     model = TABLE_MODEL_MAPPING.get(model_name)
#     search_key_model = TABLE_MODEL_MAPPING.get(search_key_model_name)

#     if not model or not search_key_model:
#         raise HTTPException(status_code=400, detail="Invalid model names provided.")

#     # Call the common function with the mapped models
#     records = fetch_related_records(
#         db=db,
#         model=model,
#         search_key_model=search_key_model,
#         search_key_id=request.search_key_id,
#         search_key_field=request.search_key_field,  # Use the field from the request
#         fields=request.fields
#     )

#     return records


@router.post("/fetch-related-records/{model_name}/{search_key_model_name}")
async def fetch_related_records_endpoint(
    model_name: str,
    search_key_model_name: str,
    request: FetchRecordsRequest,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Fetch related records based on the primary and foreign key models.

    Parameters:
    - model_name (string): The name of the primary model to query.
    - search_key_model_name (string): The name of the model that contains the foreign key referenced by the primary model.
      Example: AppBusinessConstitution (this model does not contain a foreign key; instead, the foreign key exists in AppConstitutionStakeholders, referencing AppBusinessConstitution).
    - request (FetchRecordsRequest): The request body containing parameters to filter the records.

    Request Body Example:

    model_name: AppConstitutionStakeholders
    search_key_model_name:AppBusinessConstitution
    {
        "search_key_id": 2,
        "search_key_field": "constitution_id",
        "fields": [
            "id", "stakeholder"
        ]
    }

    - search_key_id (int): The ID of the record in the related (foreign key) model that you want to filter by. It represents a specific instance of that model.
    - search_key_field (string): Defines which field in your model you will use to join with the foreign key model.

    Returns:
    - List[dict]: A list of dictionaries containing the filtered records from the primary model based on the provided foreign key criteria.

    Raises:
    - HTTPException: If the token is missing or if invalid model names are provided.
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    # Check if the model names exist in the mapping
    model = TABLE_MODEL_MAPPING.get(model_name)
    search_key_model = TABLE_MODEL_MAPPING.get(search_key_model_name)

    if not model or not search_key_model:
        raise HTTPException(status_code=400, detail="Invalid model names provided.")

    # Call the common function with the mapped models
    records = fetch_related_records(
        db=db,
        model=model,
        search_key_model=search_key_model,
        search_key_id=request.search_key_id,
        search_key_field=request.search_key_field,  # Use the field from the request
        fields=request.fields
    )

    return records




def token_generate() -> str:
    """Generate an authentication token."""
    url = "https://apis.rmlconnect.net/auth/v1/login/"
    payload = {
        "username": "Brqglob",  # Replace with your actual username
        "password": "Brg@678in"  # Replace with your actual password
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        jwt_auth = data.get('JWTAUTH')
        if not jwt_auth: 
            raise ValueError("Token not found in response")
        return jwt_auth
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise
    except ValueError as e:
        print(f"Error: {e}")
        raise
