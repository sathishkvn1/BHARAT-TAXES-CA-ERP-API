from caerp_db.common.models import EmployeeMaster, EmployeeDocuments, EmployeeEmployementDetails, HrDepartmentMaster, HrDesignationMaster, HrEmployeeCategory, EmployeeContactDetails
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetails,EmployeeMasterSchema, EmployeePresentAddressSchema, EmployeePermanentAddressSchema, EmployeeContactSchema, EmployeeBankAccountSchema, EmployeeMasterDisplay, EmployeeEducationalQualficationSchema, EmployeeSalarySchema, EmployeeDocumentsSchema, EmployeeEmployementSchema, EmployeeExperienceSchema, EmployeeEmergencyContactSchema, EmployeeDependentsSchema
from caerp_db.database import get_db
from caerp_db.hr_and_payroll import db_employee_master
from sqlalchemy.orm import Session
from caerp_auth import oauth2
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Union
from fastapi import APIRouter, Body ,Depends,Request,HTTPException,status,Response, Path, Query, File, UploadFile
from caerp_auth.authentication import authenticate_user
from datetime import date,datetime
from caerp_constants.caerp_constants import RecordActionType, ActionType, ApprovedStatus, ActiveStatus
from collections import defaultdict
# from jose import JWTError, jwt


router = APIRouter(
    prefix ='/Employee',
    tags=['Employee']
)


# #save employee master
@router.post('/save_employee_master')
def save_employee_master(
    employee_id: int = 0,
    id: List[int] = Query(None,
    description="ID used for Update"),
    Action: RecordActionType = Query(...),
    employee_profile_component: Optional[str] = Query(None,
    description="Comma-separated list of components to Update",
    title="Components to Update"),
    request: EmployeeDetails = Body(...),
    # request: EmployeeDetails = Depends(),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
  ):

   """
    Creation or updation of Employee Master.
     
    -**Request** : Data needed for creation/updation of Employee Master provided as schema "EmployeeDetails".

    -**employeeid** : Integer parameter, the Employee Master identifier. 
    - If employeeid is 0, it indicates creation of new Employee.
    - If employeeid is not 0, it indicates updation of existing Employee.

    -**id** : Integer parameter, primary key of detail tables to identify Employee profiles.
    -  passed while updating detail tables.

    -**Action** : a dropdown to choose the action to perform. Type of actions are:
    -   INSERT_ONLY - to insert new Employee Master.
    -   UPDATE_ONLY - to update master and detail tables.
    -   INSERT_AND_UPDATE - to insert into detail tables.

    -**employee_profile_component** : a textfield to add components for updating master/detail tables and inserting into detail tables.

    -**db** : database session for adding and updating tables.
   """
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
   auth_info = authenticate_user(token)
   user_id = auth_info["user_id"]

   try:
     result = db_employee_master.save_employee_master(db, request, employee_id, id, user_id, Action, employee_profile_component)

     if Action == RecordActionType.INSERT_ONLY:
       return {
            "success": True,
            "message": "Saved successfully",
            "employee_id" : result
            }
     elif Action == RecordActionType.UPDATE_ONLY or Action == RecordActionType.UPDATE_AND_INSERT:
       return {
            "success": True,
            "message": "Saved /Updated successfully"
         } 
   except Exception as e:    
     raise HTTPException(status_code=500, detail=str(e))
 



@router.post('/upload_document')
def upload_document(
   id: int,
   request: EmployeeDocumentsSchema = Depends(),
   file: UploadFile = File(None),
   db: Session = Depends(get_db),
   token: str = Depends(oauth2.oauth2_scheme)
  ):
  """
  For uploading documents for a particular employee.
     
    -**Request** : Data needed for uploading documents provided as schema "EmployeeDocumentsSchema".

    -**id**      : Integer parameter, employee_documents identifier.
    
    -**file**    : for uploading file/document.

    -**db**      : database session for uploading documentss.
  """ 
  if not token:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
  auth_info = authenticate_user(token)
  user_id = auth_info["user_id"] 

  try:
      db_employee_master.upload_employee_documents(db, request, id, user_id, file)
      return {
            "success": True,
            "message": "Uploaded successfully",
            }                  
  except Exception as e:    
     raise HTTPException(status_code=500, detail=str(e))



#delete employee details by id
@router.delete("/delete_employee_details")
def delete_employee_details_by_id(
    employee_id: int,
    id: Optional[int] = Query(None,
    description="ID used for deleting from detail tables"), 
    Action: ActionType = Query(...),
    employee_profile_component: str = Query(...,
    description="Add profile component",
    title="Component to Delete"),
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2.oauth2_scheme)
  ):
    """
    -**Delete/Undelete employee details by id.**

    -**employeeid** : Integer parameter, the Employee Master identifier.

    -**id** : Integer parameter, primary key of detail tables to identify Employee profiles.
    -  passed while deleting detail tables.

    -**Action** : a dropdown to choose the action to perform. Type of actions are:
    -   DELETE - to delete Employee Master/Employee profiles.
    -   UNDELETE - to undelete Employee Master/Employee profiles.
   """ 
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
      auth_info = authenticate_user(token)
      user_id = auth_info["user_id"]
      db_employee_master.delete_employee_details(db, employee_id, id, user_id, Action, employee_profile_component)
      if Action == ActionType.DELETE:
       return {
            "success": True,
            "message": "Deleted successfully"
         }
      elif Action == ActionType.UNDELETE:
       return {
            "success": True,
            "message": "Undeleted successfully"
         }
    except Exception as e:    
     raise HTTPException(status_code=500, detail=str(e)) 


  


@router.get("/get_employee_details")
def get_employee_details(
    # id: Optional[int] = None, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2.oauth2_scheme),
    category: Optional[Union[str,int]] = Query(None, description="Filter by category"),
    department: Optional[Union[str,int]] = Query(None, description="Filter by department"),
    designation: Optional[Union[str,int]] = Query(None, description="Filter by designation"),
    # status: Optional[ActiveStatus] = Query(None, description="Filter by status (ACTIVE/NOT_ACTIVE/ALL)"),
    approval_status: Optional[ApprovedStatus] = Query(None, description="Filter by approval status (APPROVED/NOT_APPROVED)"),
    is_consultant: Optional[str] = Query(None, description="Filter by consultant status (yes/no)"),
    search: Optional[str] = Query(None, description="Search by employee details")
):
    """
    Retrieve employee details with optional filters and search field.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    employees = db_employee_master.get_employee_master_details(db, approval_status, category, department, designation, is_consultant, search)
       
    if not employees:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No employees found with the given filters")
    
    employee_details = []

    for emp in employees:
       emp_detail = {
                "employee_name": f"{emp.first_name} {emp.middle_name} {emp.last_name}",
                "category" : emp.category_name,
                "department": emp.department_name,
                "designation": emp.designation,
                "contact_number": emp.personal_mobile_number,
                "is_consultant": emp.is_consultant
                # "status": "ACTIVE" if emp_details.is_active else "NOT_ACTIVE"
       }
       employee_details.append(emp_detail)
   
    return employee_details



