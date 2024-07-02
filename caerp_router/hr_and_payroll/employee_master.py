from caerp_db.common.models import EmployeeMaster, EmployeeDocuments, EmployeeEmployementDetails, HrDepartmentMaster, HrDesignationMaster, HrEmployeeCategory, EmployeeContactDetails
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetails, EmployeeMasterSchema, EmployeePresentAddressSchema, EmployeePermanentAddressSchema, EmployeeContactSchema, EmployeeBankAccountSchema, EmployeeMasterDisplay, EmployeeEducationalQualficationSchema, EmployeeSalarySchema, EmployeeDocumentsSchema, EmployeeEmployementSchema, EmployeeExperienceSchema, EmployeeEmergencyContactSchema, EmployeeDependentsSchema
from caerp_db.database import get_db
from caerp_db.hr_and_payroll import db_employee_master
from sqlalchemy.orm import Session
from caerp_auth import oauth2
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
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
  #  print(auth_info)
   user_id = auth_info["user_id"]
   print("USer id .............",user_id)
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




# @router.get("/get_employee_details")
# def get_employee_details(id: Optional[int] = None, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme),
#     include_present_address: bool = Query(False, description="Include present address details"),
#     include_permanent_address: bool = Query(False, description="Include permanent address details"),
#     include_contact_details: bool = Query(False, description="Include contact details"),
#     include_bank_details: bool = Query(False, description="Include bank details"),
#     include_employement_details: bool = Query(False, description="Include employement details"),
#     include_salary_details: bool = Query(False, description="Include salary details"),
#     include_educational_qualification: bool = Query(False, description="Include educational qualification details"),
#     include_experience_details: bool = Query(False, description="Include experience details"),
#     include_documents: bool = Query(False, description="Include employee documents"),
#     include_emergency_contact: bool = Query(False, description="Include emergency contact details"),
#     include_dependent_details: bool = Query(False, description="Include employee dependent details"),
#     ):
#   """
#     -**Retrieve employee master by id.**
#    """
#   if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    

#   employee_details = defaultdict(dict)
  
#   if id is not None:  
#     emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == id).first()
#     if not emp:
#       raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
#       detail = f"Employee with id {id} not found" )
#     employee_details[id]['employee_master'] = EmployeeMasterSchema(
#             **{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()}
#         )
#   else:
#     employees = db_employee_master.get_employee_master_details(db)
#     for emp in employees:
#       employee_details[emp.employee_id]['employee_master'] = EmployeeMasterSchema(
#             **{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()}
#             )
    
#   if include_present_address:
#     present_addresses = db_employee_master.get_present_address_details(db)
#     for present in present_addresses:
#       employee_details[present.employee_id].setdefault('present_address', []).append(
#                 EmployeePresentAddressSchema(**present.__dict__)
#             )
      
#   if include_permanent_address:
#     permanent_addresses = db_employee_master.get_permanent_address_details(db)
#     for permanent in permanent_addresses:
#       employee_details[permanent.employee_id].setdefault('permanent_address', []).append(
#                 EmployeePermanentAddressSchema(**permanent.__dict__)
#             )    
    
#   if include_contact_details:
#     contact_info = db_employee_master.get_contact_details(db)
#     for contact in contact_info:
#      employee_details[contact.employee_id].setdefault('contact_details', []).append(
#              EmployeeContactSchema(**contact.__dict__)
#             )

#   if include_bank_details:
#     bank_info = db_employee_master.get_bank_details(db)
#     for bank in bank_info:
#      employee_details[bank.employee_id].setdefault('bank_details', []).append(
#              EmployeeBankAccountSchema(**bank.__dict__)
#             )
     
#   if include_employement_details:
#     employement_info = db_employee_master.get_employement_details(db)
#     for employement in employement_info:
#      employee_details[employement.employee_id].setdefault('employement_details', []).append(
#              EmployeeEmployementSchema(**employement.__dict__)
#             )   
     
#   if include_salary_details:
#     salary_info = db_employee_master.get_salary_details(db)
#     for salary in salary_info:
#      employee_details[salary.employee_id].setdefault('employee_salary', []).append(
#              EmployeeSalarySchema(**salary.__dict__)
#             )   
     
#   if include_educational_qualification:
#     edu_qual_info = db_employee_master.get_qualification_details(db)
#     for edu_qual in edu_qual_info:
#      employee_details[edu_qual.employee_id].setdefault('educational_qualification', []).append(
#              EmployeeEducationalQualficationSchema(**edu_qual.__dict__)
#             )   

#   if include_experience_details:
#     exp_info = db_employee_master.get_experience_details(db)
#     for exp in exp_info:
#      employee_details[exp.employee_id].setdefault('employee_experience', []).append(
#              EmployeeExperienceSchema(**exp.__dict__)
#             )   

#   if include_documents:
#     doc_info = db_employee_master.get_document_details(db)
#     for doc in doc_info:
#      employee_details[doc.employee_id].setdefault('employee_documents', []).append(
#              EmployeeDocumentsSchema(**doc.__dict__)
#             ) 

#   if include_emergency_contact:
#     emer_contact = db_employee_master.get_emergency_contact_details(db)
#     for emer in emer_contact:
#      employee_details[emer.employee_id].setdefault('emergency_contact_details', []).append(
#              EmployeeEmergencyContactSchema(**emer.__dict__)
#             )      

#   if include_dependent_details:
#     dep_details = db_employee_master.get_dependent_details(db)
#     for dep in dep_details:
#      employee_details[dep.employee_id].setdefault('dependent_details', []).append(
#              EmployeeDependentsSchema(**dep.__dict__)
#             )   

#   if id is not None:
#     return employee_details.get(id, {})
#   else:
#     return employee_details
  


@router.get("/get_employee_details")
def get_employee_details(
    id: Optional[int] = None, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2.oauth2_scheme),
    category: Optional[str] = Query(None, description="Filter by category"),
    department: Optional[str] = Query(None, description="Filter by department"),
    designation: Optional[str] = Query(None, description="Filter by designation"),
    # status: Optional[ActiveStatus] = Query(None, description="Filter by status (ACTIVE/NOT_ACTIVE/ALL)"),
    approval_status: ApprovedStatus = Query(..., description="Filter by approval status (APPROVED/NOT_APPROVED)"),
    is_consultant: bool = Query(False, description="Filter by consultant status (True/False)")
):
    """
    Retrieve employee details with optional filters and includes.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    employee_details = []
    
    # if id is not None:  
    #     emp, emp_details, category_name, department_name, designation_name, contact_number = db.query(
    #         EmployeeMaster,
    #         EmployeeEmployementDetails,
    #         HrEmployeeCategory.category_name,
    #         HrDepartmentMaster.department_name,
    #         HrDesignationMaster.designation,
    #         EmployeeContactDetails.personal_mobile_number
    #     ).join(
    #         EmployeeEmployementDetails, EmployeeMaster.employee_id == EmployeeEmployementDetails.employee_id
    #     ).join(
    #         HrEmployeeCategory, EmployeeEmployementDetails.employee_category_id == HrEmployeeCategory.id
    #     ).join(
    #         HrDepartmentMaster, EmployeeEmployementDetails.department_id == HrDepartmentMaster.id
    #     ).join(
    #         HrDesignationMaster, EmployeeEmployementDetails.designation_id == HrDesignationMaster.id
    #     ).join(
    #         EmployeeContactDetails, EmployeeMaster.employee_id == EmployeeContactDetails.employee_id
    #     ).filter(EmployeeMaster.employee_id == id).first()
        
    #     if not emp:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with id {id} not found")
        
    #     emp_detail = {
    #         "employee_name": f"{emp.first_name} {emp.middle_name} {emp.last_name}",
    #         "category" : category_name,
    #         "department": department_name,
    #         "designation": designation_name,
    #         "contact_number": contact_number,
    #         "is_consultant": emp_details.is_consultant,
    #         # "status": "ACTIVE" if emp_details.is_active else "NOT_ACTIVE"
    #     }
    #     employee_details.append(emp_detail)
    # else:
    employees = db_employee_master(db, category, department, designation, status, approval_status, is_consultant)
    for emp, emp_details, category_name, department_name, designation_name, contact_number in employees:
       emp_detail = {
                "employee_name": f"{emp.first_name} {emp.middle_name} {emp.last_name}",
                "category" : category_name,
                "department": department_name,
                "designation": designation_name,
                "contact_number": contact_number,
                "is_consultant": emp_details.is_consultant,
                # "status": "ACTIVE" if emp_details.is_active else "NOT_ACTIVE"
            }
       employee_details.append(emp_detail)

    return employee_details



@router.get("/get_user_roles")
def get_user_roles(employee_id: int, db:Session =Depends(get_db)):
  """
    Retrieve roles of an employee.
  """
  return db_employee_master.get_user_roles(db,employee_id)


# get consultants
@router.get("/get_consultants/" , response_model=List[EmployeeEmployementSchema])
def get_consultants(db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Retrieve consultant employees.**
   """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_employee_master.get_consultants(db)



