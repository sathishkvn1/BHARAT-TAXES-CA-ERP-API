from caerp_db.common.models import EmployeeMaster, EmployeeDocuments, EmployeeEmployementDetails, HrDepartmentMaster, HrDesignationMaster, HrEmployeeCategory, EmployeeContactDetails
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetails,EmployeeMasterSchema, EmployeePresentAddressSchema, EmployeePermanentAddressSchema, EmployeeContactSchema, EmployeeBankAccountSchema, EmployeeMasterDisplay, EmployeeEducationalQualficationSchema, EmployeeSalarySchema, EmployeeDocumentsSchema, EmployeeEmployementSchema, EmployeeExperienceSchema, EmployeeEmergencyContactSchema, EmployeeDependentsSchema, EmployeeProfessionalQualificationSchema
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetailsGet,EmployeeMasterDisplay,EmployeePresentAddressGet,EmployeePermanentAddressGet,EmployeeContactGet,EmployeeBankAccountGet,EmployeeEmployementGet,EmployeeEmergencyContactGet,EmployeeDependentsGet,EmployeeSalaryGet,EmployeeEducationalQualficationGet,EmployeeExperienceGet,EmployeeDocumentsGet,EmployeeProfessionalQualificationGet,EmployeeSecurityCredentialsGet,EmployeeUserRolesGet
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
import os
from typing import List, Dict
from settings import BASE_URL


router = APIRouter(
    prefix ='/Employee',
    tags=['Employee']
)


UPLOAD_EMP_DOCUMENTS = "uploads/employee_documents"


#save employee master
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
   employee_id: int,
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
      db_employee_master.upload_employee_documents(db, request, employee_id, user_id, file)
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

  


@router.get("/search_employee_details")
def search_employee_details(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2.oauth2_scheme),
    category: Optional[Union[str,int]] = Query("ALL", description="Filter by category"),
    department: Optional[Union[str,int]] = Query("ALL", description="Filter by department"),
    designation: Optional[Union[str,int]] = Query("ALL", description="Filter by designation"),
    user_status: Optional[ActiveStatus] = Query("ALL", description="Filter by status (yes/no)"),
    approval_status: Optional[ApprovedStatus] = Query("ALL", description="Filter by approval status (yes/no)"),
    is_consultant: Optional[str] = Query(None, description="Filter by consultant status (yes/no)"),
    search: Optional[str] = Query(None, description="Search by employee details")
):
    """
    Retrieve employee details with optional filters and search field.

    -**category** : retrieve employees with category filter.
    -**department** : retrieve employees with department filter.
    -**designation** : retrieve employees with designation filter.
    -**status** : filter employees by status(yes/no).
    -**approval_status** : filter employees by approval status(yes/no).
    -**is_consultant** : to check whether the employee is a consultant or not(yes/no).

    -**search** : to search for a particular employee by name, mobile_no, category, department and designation.
        
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    employees = db_employee_master.search_employee_master_details(db, user_status, approval_status, category, department, designation, is_consultant, search)
       
    if not employees:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No employees found with the given filters")
    
    employee_details = []

    for emp in employees:
       emp_detail = {
                "employee_id": emp.employee_id,
                "first_name":emp.first_name,
                "middle_name":emp.middle_name,
                "last_name":emp.last_name,
                "employee_name": f"{emp.first_name} {emp.middle_name} {emp.last_name}",
                "gender": emp.gender, 
                "date_of_birth":emp.date_of_birth,
                "blood_group":emp.blood_group,
                "nationality_id": emp.nationality_id,
                "nationality": emp.nationality_name,
                "marital_status_id": emp.marital_status_id,
                "marital_status": emp.marital_status, 
                "joining_date":emp.joining_date,
                "remarks":emp.remarks,
                
                "category" : emp.category_name,
                "department": emp.department_name,
                "designation": emp.designation,
                "contact_number": emp.personal_mobile_number,
                "email_id":emp.personal_email_id,
                "is_consultant": emp.is_consultant,
                "status": emp.is_active
       }
       employee_details.append(emp_detail)
   
    return employee_details




def add_employee_detail(employee_details, employee_id, key, value, db):
    employee = next((emp for emp in employee_details if emp['employee_master'].employee_id == employee_id), None)
    if not employee:
        emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first()
        if emp:
            employee = {'employee_master': EmployeeMasterDisplay(**{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()})}
            employee_details.append(employee)
    if employee:
        employee.setdefault(key, []).append(value)
    
@router.get("/get_employee_details")
def get_employee_details(employee_id: Optional[int] = None, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme),
    employee_profile_component: Optional[str] = Query(None,
    description="Comma-separated list of components to view employee details")                     
    ):
    """
    -**Retrieve employee master profile by employee_id.**

    -**employee_id** : Integer parameter, the Employee Master identifier.
    - If id is 0, all the employees will be retrieved.

    -**employee_profile_component** : a textfield to add components for retrieving employee profiles. Following are the components:
    - present_address,permanent_address,bank_details,contact_details,employement_details,emergency_contact_details,dependent_details,employee_salary, educational_qualification, employee_experience, employee_documents, professional_qualification
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    employee_details = []

    if employee_profile_component is None: 
        if employee_id is not None:  
            emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first()
            if not emp:
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail = f"Employee with id {employee_id} not found" )
            employee_details.append({
                'employee_master': EmployeeMasterDisplay(**{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()})
            })
        else:
            employees = db_employee_master.get_employee_master_details(db)
            for emp in employees:
                employee_details.append({
                    'employee_master': EmployeeMasterDisplay(**{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()})
                })
        return employee_details    
    else: 
        if employee_id is not None:  
            emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first()
            if not emp:
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail = f"Employee with id {employee_id} not found" )
            employee_details.append({
                'employee_master': EmployeeMasterDisplay(**{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()})
            })
        else:
            employees = db_employee_master.get_employee_master_details(db)
            for emp in employees:
                employee_details.append({
                    'employee_master': EmployeeMasterDisplay(**{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()})
                })
        
        schema_names = EmployeeDetailsGet.__fields__.keys()
        schemas_list = employee_profile_component.split(",")
        valid_options = [option for option in schemas_list if option in schema_names]

        if not valid_options:
            raise HTTPException(status_code=422, detail="Invalid employee profile component")
  
        for option in valid_options:

            if option == "present_address":
                present_addresses = db_employee_master.get_present_address_details(db)
                for present in present_addresses:
                    add_employee_detail(employee_details, present.employee_id, 'present_address', EmployeePresentAddressGet(**present.__dict__),db)
      
            if option == "permanent_address":
                permanent_addresses = db_employee_master.get_permanent_address_details(db)
                for permanent in permanent_addresses:
                    add_employee_detail(employee_details, permanent.employee_id, 'permanent_address', EmployeePermanentAddressGet(**permanent.__dict__),db)    
    
            if option == "contact_details":
                contact_info = db_employee_master.get_contact_details(db)
                for contact in contact_info:
                    add_employee_detail(employee_details, contact.employee_id, 'contact_details', EmployeeContactGet(**contact.__dict__),db)

            if option == "bank_details":
                bank_info = db_employee_master.get_bank_details(db)
                for bank in bank_info:
                    add_employee_detail(employee_details, bank.employee_id, 'bank_details', EmployeeBankAccountGet(**bank.__dict__),db)
     
            if option == "employement_details":
                employement_info = db_employee_master.get_employement_details(db)
                for employement in employement_info:
                    add_employee_detail(employee_details, employement.employee_id, 'employement_details', EmployeeEmployementGet(**employement.__dict__),db)
     
            if option == "employee_salary":
                salary_info = db_employee_master.get_salary_details(db)
                for salary in salary_info:
                    add_employee_detail(employee_details, salary.employee_id, 'employee_salary', EmployeeSalaryGet(**salary.__dict__),db)
     
            if option == "educational_qualification":
                edu_qual_info = db_employee_master.get_qualification_details(db)
                for edu_qual in edu_qual_info:
                    add_employee_detail(employee_details, edu_qual.employee_id, 'educational_qualification', EmployeeEducationalQualficationGet(**edu_qual.__dict__),db)

            if option == "employee_experience":
                exp_info = db_employee_master.get_experience_details(db)
                for exp in exp_info:
                    add_employee_detail(employee_details, exp.employee_id, 'employee_experience', EmployeeExperienceGet(**exp.__dict__),db)

            if option == "employee_documents":
                doc_info = db_employee_master.get_document_details(db)
                for doc in doc_info:
                    add_employee_detail(employee_details, doc.employee_id, 'employee_documents', EmployeeDocumentsGet(**doc.__dict__),db)

            if option == "emergency_contact_details":
                emer_contact = db_employee_master.get_emergency_contact_details(db)
                for emer in emer_contact:
                    add_employee_detail(employee_details, emer.employee_id, 'emergency_contact_details', EmployeeEmergencyContactGet(**emer.__dict__),db)

            if option == "dependent_details":
                dep_details = db_employee_master.get_dependent_details(db)
                for dep in dep_details:
                    add_employee_detail(employee_details, dep.employee_id, 'dependent_details', EmployeeDependentsGet(**dep.__dict__),db)
     
            if option == "professional_qualification":
                prof_qual_info = db_employee_master.get_professional_qualification_details(db)
                for prof_qual in prof_qual_info:
                    add_employee_detail(employee_details, prof_qual.employee_id, 'professional_qualification', EmployeeProfessionalQualificationGet(**prof_qual.__dict__),db)

            if option == "employee_security_credentials":
                sec_credentials = db_employee_master.get_security_credentials(db)
                for sec in sec_credentials:
                    add_employee_detail(employee_details, sec.employee_id, 'employee_security_credentials', EmployeeSecurityCredentialsGet(**sec.__dict__),db)
          
            if option == "user_roles":
                user_role = db_employee_master.get_user_role(db)
                for role in user_role:
                    add_employee_detail(employee_details, role.employee_id, 'user_roles', EmployeeUserRolesGet(**role.__dict__),db)

        if employee_id is not None:
            return next((emp for emp in employee_details if emp['employee_master'].employee_id == employee_id), None)
        else:
            return employee_details




@router.get('/view_documents/{employee_id}', response_model=List[Dict[str, str]])
def view_documents(
    employee_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Fetch uploaded documents for a particular employee.
    
    - **employee_id**: Integer parameter, employee identifier.
    - **db**: Database session.
    - **token**: Authentication token.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"]

    try:
        documents = db.query(EmployeeDocuments).filter(
            EmployeeDocuments.employee_id == employee_id,
            EmployeeDocuments.is_deleted == 'no'
        ).all()

        if not documents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found for the given employee id")

        document_urls = []
        for doc in documents:
          filename_prefix = f"{doc.id}"

          for filename in os.listdir(UPLOAD_EMP_DOCUMENTS):
              if filename.startswith(filename_prefix):
                 document_urls.append({"document": f"{BASE_URL}/Employee/upload_document/{filename}"})
        
        return document_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

