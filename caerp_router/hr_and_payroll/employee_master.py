from caerp_db.common.models import EmployeeContactDetails, EmployeeEducationalQualification, EmployeeExperience, EmployeeMaster, EmployeeDocuments,  EmployeeProfessionalQualification, UserBase
from caerp_db.hr_and_payroll.model import HrDocumentMaster
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import AddEmployeeToTeam, EmployeeAddressDetailsSchema, EmployeeDetails, EmployeeDetailsCombinedSchema, EmployeeDocumentResponse,  EmployeeMasterDisplay,EmployeeSalarySchema, EmployeeDocumentsSchema, EmployeeTeamMasterSchema, EmployeeTeamMembersGet, HrViewEmployeeTeamMemberSchema, HrViewEmployeeTeamSchema, SaveEmployeeTeamMaster, UsernameCheckResponse
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetailsGet,EmployeeMasterDisplay,EmployeePresentAddressGet,EmployeePermanentAddressGet,EmployeeContactGet,EmployeeBankAccountGet,EmployeeEmployementGet,EmployeeEmergencyContactGet,EmployeeDependentsGet,EmployeeSalaryGet,EmployeeEducationalQualficationGet,EmployeeExperienceGet,EmployeeDocumentsGet,EmployeeProfessionalQualificationGet,EmployeeSecurityCredentialsGet,EmployeeUserRolesGet
from caerp_db.database import get_db
from caerp_db.hr_and_payroll import db_employee_master
from sqlalchemy.orm import Session
from caerp_auth import oauth2

from typing import List, Optional, Type, Union
from fastapi import APIRouter, Body ,Depends,Request,HTTPException,status,Response, Query, File, UploadFile
from caerp_auth.authentication import authenticate_user
from datetime import date,datetime
from caerp_constants.caerp_constants import RecordActionType, ActionType, ApprovedStatus, ActiveStatus

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
  
#---------------------------------------------------------------------------------------------------------
@router.post('/save_employee_master_new')
def save_employee_master(
   
    id: int = 0,
    employee_profile_component: Optional[str] = Query(None,        
        description=(
            "Comma-separated list of components to save. Valid options are: " 
            "Valid options are:[ present_address, permanent_address, bank_details, contact_details, "
            "employement_details, emergency_contact_details, dependent_details, employee_salary, "
            "educational_qualification, employee_experience, employee_documents, professional_qualification.]"
        )
    ),
    request: EmployeeDetails = Body(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
): 
    """
    Save or update employee details based on the provided ID and profile components.

    - **id**: The ID of the employee. Set to 0 to create a new employee.
    - **employee_profile_component**: Comma-separated list of components to update. 
   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"]

    try:
        result = db_employee_master.save_employee_master_new(db, request,id, user_id, employee_profile_component)

        if id == 0:
            return {
                "success": True,
                "message": "Saved successfully",
                "employee_id": result
            }
        else:
            return {
                "success": True,
                "message": "Updated successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





#---------------------------------------------------------------------------------------------------------

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


#---------------------------------------------------------------------------------------------------------


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

  
#---------------------------------------------------------------------------------------------------------
from sqlalchemy import func



# @router.get("/get_employee_details with pagination")
# def get_employee_details(
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme),
#     employee_id: Optional[int] = None,
#     employee_profile_component: Optional[str] = Query(
#         None,
#         description=(
#             "Comma-separated list of components to view employee details. "
#             "Valid options are: [present_address, permanent_address, bank_details, contact_details, "
#             "employment_details, emergency_contact_details, dependent_details, employee_salary, "
#             "educational_qualification, employee_experience, employee_documents, professional_qualification.]"
#         )
#     ),
#     category: Optional[Union[str, int]] = Query("ALL", description="Filter by category or 'ALL'"),
#     department: Optional[Union[str, int]] = Query("ALL", description="Filter by department or 'ALL'"),
#     designation: Optional[Union[str, int]] = Query("ALL", description="Filter by designation or 'ALL'"),
#     user_status: Optional[ActiveStatus] = Query("ALL", description="Filter by status (yes/no) or 'ALL'"),
#     approval_status: Optional[ApprovedStatus] = Query("ALL", description="Filter by approval status (yes/no)" or 'ALL'),
#     is_consultant: Optional[str] = Query("ALL", description="Filter by consultant status (yes/no) or ALL"),
#     search: Optional[str] = Query(None, description="Search by employee details"),
#     page: Optional[int] = Query(1, description="Page number"),
#     page_size: Optional[int] = Query(10, description="Number of records per page")
# ):  
#     """
#     Retrieve employee details with optional filters, search, and profile components.

#     - If both **employee_id** and **employee_profile_component** are provided, retrieve details for the specified employee using the given profile components.
#     - If **employee_id** is provided without **employee_profile_component**, return an error indicating the need for profile components.
#     - If neither **employee_id** nor **employee_profile_component** is provided, execute the search logic to retrieve employees based on filters and search criteria.

#     -**employee_id** : Integer parameter, the Employee Master identifier.

#     -**employee_profile_component** : A text field to add components for retrieving employee profiles.
#     - Components: present_address, permanent_address, bank_details, contact_details, employment_details, 
#     emergency_contact_details, dependent_details, employee_salary, educational_qualification, 
#     employee_experience, employee_documents, professional_qualification.

#     -**category** : Retrieve employees with category filter.
#     -**department** : Retrieve employees with department filter.
#     -**designation** : Retrieve employees with designation filter.
#     -**status** : Filter employees by status(yes/no/all).
#     -**approval_status** : Filter employees by approval status(yes/no/all).
#     -**is_consultant** : To check whether the employee is a consultant or not(yes/no/all).
#     -**search** : To search for a particular employee by name, category, department, and designation.
#     """

   
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

#     if employee_id is not None:
#         if employee_profile_component:
#             # Execute profile component logic
#             employee_details = []

#             emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first()
#             if not emp:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with id {employee_id} not found")
#             employee_details.append({
#                 'employee_master': EmployeeMasterDisplay(**{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()})
#             })

#             schema_names = EmployeeDetailsGet.__fields__.keys()
#             schemas_list = employee_profile_component.split(",")
#             valid_options = [option for option in schemas_list if option in schema_names]

#             if not valid_options:
#                 raise HTTPException(status_code=422, detail="Invalid employee profile component")

#             for option in valid_options:
#                 if option == "present_address":
#                     present_addresses = db_employee_master.get_present_address_details(db, employee_id=employee_id)
#                     if present_addresses:
#                         employee_details.append({
#                             'present_address': EmployeePresentAddressGet(**present_addresses[0].__dict__)
#                         })

#                 if option == "permanent_address":
#                     permanent_addresses = db_employee_master.get_permanent_address_details(db, employee_id=employee_id)
#                     if permanent_addresses:
#                         employee_details.append({
#                             'permanent_address': EmployeePermanentAddressGet(**permanent_addresses[0].__dict__)
#                         })

#                 if option == "contact_details":
#                     contact_info = db_employee_master.get_contact_details(db, employee_id=employee_id)
#                     if contact_info:
#                         employee_details.append({
#                             'contact_details': EmployeeContactGet(**contact_info[0].__dict__)
#                         })

#                 if option == "bank_details":
#                     bank_info = db_employee_master.get_bank_details(db, employee_id=employee_id)
#                     if bank_info:
#                         employee_details.append({
#                             'bank_details': EmployeeBankAccountGet(**bank_info[0].__dict__)
#                         })

#                 if option == "employment_details":
#                     employment_info = db_employee_master.get_employment_details(db, employee_id=employee_id)
#                     if employment_info:
#                         employment_details = []
#                         for emp_detail, department_name, designation_name ,category_name in employment_info:
#                             employment_details.append({
#                                    'department_id': emp_detail.department_id,
#                                    'department_name': department_name,
#                                    'designation_id' : emp_detail.designation_id,
#                                    'designation_name': designation_name,
#                                    'employee_category_id' :emp_detail.employee_category_id,
#                                    'category_name' : category_name,
#                                    'is_consultant'   : emp_detail.is_consultant,
#                                    'effective_to_date': emp_detail.effective_to_date,
#                                    'remarks': emp_detail.remarks
#                                 })
              

#                   # Append employment_details to employee_details only once after the loop
#                         employee_details.append({
#                              'employment_details': employment_details
#                         })
 
                
#                 if option == "employee_salary":
#                     salary_info = db_employee_master.get_employee_salary_details(db, employee_id=employee_id)
#                     if salary_info:
#                         employee_details.append({
#                             'employee_salary': EmployeeSalaryGet(**salary_info[0].__dict__)
#                         })

#                 if option == "educational_qualification":
#                     edu_qual_info = db_employee_master.get_qualification_details(db, employee_id=employee_id)
#                     if edu_qual_info:
#                         qualifications = [EmployeeEducationalQualficationGet(**qual.__dict__) for qual in edu_qual_info]
#                         employee_details.append({
#                               'educational_qualification': qualifications
#                         })

#                 if option == "employee_experience":
#                     exp_info = db_employee_master.get_experience_details(db, employee_id=employee_id)
#                     if exp_info:
#                         experiences = [EmployeeExperienceGet(**exp.__dict__) for exp in exp_info]
#                         employee_details.append({
#                             'employee_experience': experiences
#                         })

#                 if option == "employee_documents":
#                     doc_info = db_employee_master.get_document_details(db, employee_id=employee_id)
#                     if doc_info:
#                         documents = [EmployeeDocumentsGet(**doc.__dict__) for doc in doc_info]
#                         employee_details.append({
#                              'employee_documents': documents
#                         })

#                 if option == "emergency_contact_details":
#                     emer_contact = db_employee_master.get_emergency_contact_details(db, employee_id=employee_id)
#                     if emer_contact:
#                         employee_details.append({
#                             'emergency_contact_details': EmployeeEmergencyContactGet(**emer_contact[0].__dict__)
#                         })

#                 if option == "dependent_details":
#                     dep_details = db_employee_master.get_dependent_details(db, employee_id=employee_id)
#                     if dep_details:
#                         employee_details.append({
#                             'dependent_details': EmployeeDependentsGet(**dep_details[0].__dict__)
#                         })

#                 if option == "professional_qualification":
#                     prof_qual_info = db_employee_master.get_professional_qualification_details(db, employee_id=employee_id)
#                     if prof_qual_info:
#                         prof_qualifications = [EmployeeProfessionalQualificationGet(**qual.__dict__) for qual in prof_qual_info]
#                         employee_details.append({
#                                 'professional_qualification': prof_qualifications
#                         })

#                 if option == "employee_security_credentials":
#                     sec_credentials = db_employee_master.get_security_credentials(db, employee_id=employee_id)
#                     if sec_credentials:
#                         credentials = [EmployeeSecurityCredentialsGet(**cred.__dict__) for cred in sec_credentials]
#                         employee_details.append({
#                               'employee_security_credentials': credentials
#                         })

#                 if option == "user_roles":
#                     user_roles = db_employee_master.get_user_role(db, employee_id=employee_id)
#                     if user_roles:
#                         roles = [EmployeeUserRolesGet(**role.__dict__) for role in user_roles]
#                         employee_details.append({
#                                   'user_roles': roles
#                         })

               
#             return employee_details

#         else:
#             # If only employee_id is provided without components
#             raise HTTPException(status_code=400, detail="Profile component is required to fetch details for a specific employee.")

#     else:
#         employees = db_employee_master.search_employee_master_details(
#             db, user_status, approval_status, category, department, designation, is_consultant, search
#         )

#         total_employee_records = len(employees)
#         print("Total employee records:", total_employee_records)

#         # Calculate total pages
#         total_pages = (total_employee_records + page_size - 1) // page_size
#         print("total_pages", total_pages)

#         # Ensure the current page is within valid range
#         if page > total_pages:
#             page = total_pages

#         # Calculate start and end indices for slicing
#         start_index = (page - 1) * page_size
#         end_index = start_index + page_size

#         if not employees:
#             return {
#                 "page": page,
#                 "page_size": page_size,
#                 "total_records": total_employee_records,
#                 "total_pages": total_pages,
#                 "data": []
#             }

#         employee_details = employees[start_index:end_index]

#         response_data = []
#         for emp in employee_details:  # Use sliced data
#             emp_detail = {
#                 "employee_id": emp.employee_id,
#                 "first_name": emp.first_name,
#                 "middle_name": emp.middle_name,
#                 "last_name": emp.last_name,
#                 "employee_name": f"{emp.first_name} {emp.middle_name} {emp.last_name}",
#                 "gender_id": emp.gender_id,
#                 "gender": emp.gender,
#                 "date_of_birth": emp.date_of_birth,
#                 "blood_group": emp.blood_group,
#                 "nationality_id": emp.nationality_id,
#                 "nationality": emp.nationality_name,
#                 "marital_status_id": emp.marital_status_id,
#                 "marital_status": emp.marital_status,
#                 "joining_date": emp.joining_date,
#                 "remarks": emp.remarks,
#                 "category_id": emp.employee_category_id,
#                 "category": emp.category_name,
#                 "department_id": emp.department_id,
#                 "department": emp.department_name,
#                 "designation_id": emp.designation_id,
#                 "designation": emp.designation,
#                 "contact_number": emp.personal_mobile_number,
#                 "email_id": emp.personal_email_id,
#                 "is_consultant": emp.is_consultant,
#                 "user_status": emp.is_active,
#                 "approval_status": emp.is_approved
#             }
#             response_data.append(emp_detail)

#         return {
#             "page": page,
#             "page_size": page_size,
#             "total_records": total_employee_records,
#             "total_pages": total_pages,
#             "data": response_data
#         }

@router.get("/get_employee_details")
def get_employee_details(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
    employee_id: Optional[int] = None,
    employee_profile_component: Optional[str] = Query(
        None,
        description=(
            "Comma-separated list of components to view employee details. "
            "Valid options are: [present_address, permanent_address, bank_details, contact_details, "
            "employment_details, emergency_contact_details, dependent_details, employee_salary, "
            "educational_qualification, employee_experience, employee_documents, professional_qualification.]"
        )
    ),
    category: Optional[Union[str, int]] = Query("ALL", description="Filter by category or 'ALL'"),
    department: Optional[Union[str, int]] = Query("ALL", description="Filter by department or 'ALL'"),
    designation: Optional[Union[str, int]] = Query("ALL", description="Filter by designation or 'ALL'"),
    user_status: Optional[ActiveStatus] = Query("ALL", description="Filter by status (yes/no) or 'ALL'"),
    approval_status: Optional[ApprovedStatus] = Query("ALL", description="Filter by approval status (yes/no) or 'ALL'"),
    is_consultant: Optional[str] = Query("ALL", description="Filter by consultant status (yes/no) or 'ALL'"),
    search: Optional[str] = Query(None, description="Search by employee details"),
):  
    """
    Retrieve employee details with optional filters, search, and profile components.

    - If both **employee_id** and **employee_profile_component** are provided, retrieve details for the specified employee using the given profile components.
    - If **employee_id** is provided without **employee_profile_component**, return an error indicating the need for profile components.
    - If neither **employee_id** nor **employee_profile_component** is provided, execute the search logic to retrieve employees based on filters and search criteria.

    -**employee_id** : Integer parameter, the Employee Master identifier.

    -**employee_profile_component** : A text field to add components for retrieving employee profiles.
    - Components: present_address, permanent_address, bank_details, contact_details, employment_details, 
    emergency_contact_details, dependent_details, employee_salary, educational_qualification, 
    employee_experience, employee_documents, professional_qualification.

    -**category** : Retrieve employees with category filter.
    -**department** : Retrieve employees with department filter.
    -**designation** : Retrieve employees with designation filter.
    -**status** : Filter employees by status(yes/no).
    -**approval_status** : Filter employees by approval status(yes/no).
    -**is_consultant** : To check whether the employee is a consultant or not(yes/no).
    -**search** : To search for a particular employee by name, category, department, and designation.
    """

    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    if employee_id is not None:
        if employee_profile_component:
            employee_details = []
            emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first()
            if not emp:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with id {employee_id} not found")
            
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
                    present_addresses = db_employee_master.get_present_address_details(db, employee_id=employee_id)
                    if present_addresses:
                        employee_details.append({
                            'present_address': EmployeePresentAddressGet(**present_addresses[0].__dict__)
                        })

                if option == "permanent_address":
                    permanent_addresses = db_employee_master.get_permanent_address_details(db, employee_id=employee_id)
                    if permanent_addresses:
                        employee_details.append({
                            'permanent_address': EmployeePermanentAddressGet(**permanent_addresses[0].__dict__)
                        })

                if option == "contact_details":
                    contact_info = db_employee_master.get_contact_details(db, employee_id=employee_id)
                    if contact_info:
                        employee_details.append({
                            'contact_details': EmployeeContactGet(**contact_info[0].__dict__)
                        })

                if option == "bank_details":
                    bank_info = db_employee_master.get_bank_details(db, employee_id=employee_id)
                    if bank_info:
                        employee_details.append({
                            'bank_details': EmployeeBankAccountGet(**bank_info[0].__dict__)
                        })

                if option == "employment_details":
                    employment_info = db_employee_master.get_employment_details(db, employee_id=employee_id)
                    if employment_info:
                        employment_details = []
                        for emp_detail, department_name, designation_name, category_name in employment_info:
                            employment_details.append({
                                'department_id': emp_detail.department_id,
                                'department_name': department_name,
                                'designation_id': emp_detail.designation_id,
                                'designation_name': designation_name,
                                'employee_category_id': emp_detail.employee_category_id,
                                'category_name': category_name,
                                'is_consultant': emp_detail.is_consultant,
                                'effective_to_date': emp_detail.effective_to_date,
                                'remarks': emp_detail.remarks
                            })
              
                        employee_details.append({
                            'employment_details': employment_details
                        })

                if option == "employee_salary":
                    salary_info = db_employee_master.get_employee_salary_details(db, employee_id=employee_id)
                    if salary_info:
                        employee_details.append({
                            'employee_salary': EmployeeSalaryGet(**salary_info[0].__dict__)
                        })

                if option == "educational_qualification":
                    edu_qual_info = db_employee_master.get_qualification_details(db, employee_id=employee_id)
                    if edu_qual_info:
                        qualifications = [EmployeeEducationalQualficationGet(**qual.__dict__) for qual in edu_qual_info]
                        employee_details.append({
                            'educational_qualification': qualifications
                        })

                if option == "employee_experience":
                    exp_info = db_employee_master.get_experience_details(db, employee_id=employee_id)
                    if exp_info:
                        experiences = [EmployeeExperienceGet(**exp.__dict__) for exp in exp_info]
                        employee_details.append({
                            'employee_experience': experiences
                        })

                if option == "employee_documents":
                    doc_info = db_employee_master.get_document_details(db, employee_id=employee_id)
                    if doc_info:
                        documents = [EmployeeDocumentsGet(**doc.__dict__) for doc in doc_info]
                        employee_details.append({
                            'employee_documents': documents
                        })

                if option == "emergency_contact_details":
                    emer_contact = db_employee_master.get_emergency_contact_details(db, employee_id=employee_id)
                    if emer_contact:
                        employee_details.append({
                            'emergency_contact_details': EmployeeEmergencyContactGet(**emer_contact[0].__dict__)
                        })

                if option == "dependent_details":
                    dep_details = db_employee_master.get_dependent_details(db, employee_id=employee_id)
                    if dep_details:
                        employee_details.append({
                            'dependent_details': EmployeeDependentsGet(**dep_details[0].__dict__)
                        })

                if option == "professional_qualification":
                    prof_qual_info = db_employee_master.get_professional_qualification_details(db, employee_id=employee_id)
                    if prof_qual_info:
                        prof_qualifications = [EmployeeProfessionalQualificationGet(**qual.__dict__) for qual in prof_qual_info]
                        employee_details.append({
                            'professional_qualification': prof_qualifications
                        })

            return employee_details

        else:
            raise HTTPException(status_code=400, detail="Profile component is required to fetch details for a specific employee.")
    else:
        employees_query = db_employee_master.search_employee_master_details(
            db, user_status, approval_status, category, department, designation, is_consultant, search
        )

        if not employees_query:
            return []

        employee_details = []
        for emp in employees_query:
            emp_detail = {
                "employee_id": emp.employee_id,
                "first_name": emp.first_name,
                "middle_name": emp.middle_name,
                "last_name": emp.last_name,
                "employee_name": f"{emp.first_name} {emp.middle_name} {emp.last_name}",
                "gender_id": emp.gender_id,
                "gender": emp.gender,
                "date_of_birth": emp.date_of_birth,
                "blood_group": emp.blood_group,
                "nationality_id": emp.nationality_id,
                "nationality": emp.nationality_name,
                "marital_status_id": emp.marital_status_id,
                "marital_status": emp.marital_status,
                "joining_date": emp.joining_date,
                "remarks": emp.remarks,
                "category_id": emp.employee_category_id,
                "category": emp.category_name,
                "department_id": emp.department_id,
                "department": emp.department_name,
                "designation_id": emp.designation_id,
                "designation": emp.designation,
                "contact_number": emp.personal_mobile_number,
                "email_id": emp.personal_email_id,
                "is_consultant": emp.is_consultant,
                "user_status": emp.is_active,
                "approval_status": emp.is_approved
            }
            employee_details.append(emp_detail)

        return employee_details





#---------------------------------------------------------------------------------------------------------


def add_employee_detail(employee_details, employee_id, key, value, db):
    employee = next((emp for emp in employee_details if emp['employee_master'].employee_id == employee_id), None)
    if not employee:
        emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first()
        if emp:
            employee = {'employee_master': EmployeeMasterDisplay(**{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()})}
            employee_details.append(employee)
    if employee:
        employee.setdefault(key, []).append(value)



#--------------------------------------------------------------------------------------------------------------
@router.get('/get_employee_document_details_with_uploads/{employee_id}', response_model=List[EmployeeDocumentResponse])
def get_employee_documents(employee_id: int, db: Session = Depends(get_db),token: str = Depends(oauth2.oauth2_scheme)):

    if not token:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
        query = db.query(
            EmployeeDocuments.id,
            EmployeeDocuments.employee_id,
            EmployeeDocuments.document_id,
            EmployeeDocuments.document_number,
            HrDocumentMaster.document_name,
            EmployeeDocuments.issue_date,
            EmployeeDocuments.expiry_date,
            EmployeeDocuments.issued_by,
            EmployeeDocuments.remarks,
            EmployeeDocuments.is_deleted
        ).join(
            HrDocumentMaster, EmployeeDocuments.document_id == HrDocumentMaster.id
        ).filter(
            EmployeeDocuments.employee_id == employee_id,
            EmployeeDocuments.is_deleted == 'no'
        )

        employee_documents = query.all()

        if not employee_documents:
            raise HTTPException(status_code=404, detail="Employee documents not found")

        response = []
        files_in_directory = os.listdir(UPLOAD_EMP_DOCUMENTS)
       
        for doc in employee_documents:
            document_data = doc._asdict()
            

            # Construct the file name prefix
            filename_prefix = f"{document_data['id']}"
            

            document_url = None

            # Loop through the files in the directory
            for filename in files_in_directory:
                

                if filename.startswith(filename_prefix) :
                    
        
                    
                    document_url = f"{BASE_URL}/hr_and_payroll/Employee/upload_document/{filename}"
                    break
                else:
                    print(f"No match for file: {filename}")  # Debugging: No match

            if not document_url:
                print(f"No document found for ID: {document_data['id']}")  # Debugging: No document found

            # Attach the document URL or keep it as None if not found
            document_data['document'] = document_url
            response.append(EmployeeDocumentResponse(**document_data))

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#--------------------------------------------------------------------------------------------------------------
@router.post('/employee_save_update')
def employee_save_update(
    employee_id: int,
    employee_profile_component: Optional[str] = Query(None, description="Comma-separated list of components to Save/Update"),
    employee_details: EmployeeDetailsCombinedSchema = Body(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"]

    try:
        if not employee_profile_component:
            raise ValueError("Employee profile component is required")

        components = employee_profile_component.split(',')

        # Save or update educational qualifications
        if 'educational_qualifications' in components and employee_details.educational_qualifications:
            db_employee_master.save_or_update_educational_qualifications(
                db, employee_id, employee_details.educational_qualifications, user_id
            )

        # Save or update experiences
        if 'experiences' in components and employee_details.experiences:
            db_employee_master.save_or_update_experiences(
                db, employee_id, employee_details.experiences, user_id
            )

        # Save or update professional qualifications
        if 'professional_qualifications' in components and employee_details.professional_qualifications:
            db_employee_master.save_or_update_professional_qualifications(
                db, employee_id, employee_details.professional_qualifications, user_id
            )

        return {
            "success": True,
            "message": "Employee details saved/updated successfully",
            "employee_id": employee_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#--------------------------------------------------------------------------------------------------------------
@router.post('/employee_save_update_qualification_and_experience')
def employee_save_update(
    employee_id: int,
    employee_profile_component: Optional[str] = Query(None, description="Comma-separated list of components to Save/Update"),
    employee_details: EmployeeDetailsCombinedSchema = Body(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"]

    try:
        if not employee_profile_component:
            raise ValueError("Employee profile component is required")

        components = employee_profile_component.split(',')

        # Save or update educational qualifications
        if 'educational_qualifications' in components and employee_details.educational_qualifications:
            save_or_update_records(
                db, EmployeeEducationalQualification, employee_id, employee_details.educational_qualifications, user_id
            )

        # Save or update experiences
        if 'experiences' in components and employee_details.experiences:
            save_or_update_records(
                db, EmployeeExperience, employee_id, employee_details.experiences, user_id
            )

        # Save or update professional qualifications
        if 'professional_qualifications' in components and employee_details.professional_qualifications:
            save_or_update_records(
                db, EmployeeProfessionalQualification, employee_id, employee_details.professional_qualifications, user_id
            )

        return {
            "success": True,
            "message": "Employee details saved/updated successfully",
            "employee_id": employee_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#--------------------------------------------------------------------------------------------------------------
from pydantic import BaseModel
from sqlalchemy import insert, update


def save_or_update_records(
    db: Session,
    model_class: Type,
    employee_id: int,
    records: List[BaseModel],
    user_id: int
):
    try:
        # Step 1: Retrieve existing records
        existing_records = db.query(model_class).filter(
            model_class.employee_id == employee_id
        ).all()

        # Step 2: Determine which records need to be deleted
        existing_ids = {record.id for record in existing_records}
        incoming_ids = {rec.id for rec in records if rec.id != 0}
        ids_to_delete = existing_ids - incoming_ids

        if ids_to_delete:
            db.query(model_class).filter(
                model_class.id.in_(ids_to_delete)
            ).update({"is_deleted": 'yes'}, synchronize_session=False)

        # Step 3: Insert or update records
        for rec in records:
            record_data = rec.model_dump(exclude_unset=True)
            record_data['employee_id'] = employee_id

            if rec.id == 0:
                # Insertion logic
                record_data['created_by'] = user_id
                record_data['created_on'] = datetime.now()
                insert_stmt = insert(model_class).values(**record_data)
                db.execute(insert_stmt)
            else:
                # Update logic
                existing_record = db.query(model_class).filter(
                    model_class.id == rec.id,
                    model_class.is_deleted == 'no'
                ).first()
                
                if not existing_record:
                    raise HTTPException(status_code=404, detail=f"Record with id {rec.id} not found or already deleted")
                
                update_stmt = update(model_class).where(
                    model_class.id == rec.id
                ).values(
                    **record_data,
                    is_deleted='no',  # Ensure the record is active
                    # modified_by=user_id,
                    # modified_on=datetime.utcnow()
                )
                db.execute(update_stmt)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
#--------------------------------------------------------------------------------------------------------------
@router.post('/update_employee_address_or_bank_details')
def update_employee_address_or_bank_details(
    employee_id: int,
    id: int = Query(0, description="Select 0 for new entries (UPDATE_AND_INSERT) or a non-zero value for updating a specific row (UPDATE_ONLY)."),
    Action: RecordActionType = Query(...,description=("Select UPDATE_AND_INSERT or UPDATE_ONLY") ),
    employee_profile_component: str = Query(...,        
        description=(
            "For UPDATE_AND_INSERT: Comma-separated list of components to save. Valid options are: "
            "[present_address, permanent_address, bank_details,contact_details]. "
            "For UPDATE_ONLY: Only one component can be selected at a time to update."
        )
    ),
    request: EmployeeAddressDetailsSchema = Body(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
):  
    """
    Update or insert employee address and bank details.

    - **employee_id**: Employee ID (required)

    - **id**: ID of the specific address or bank detail to update.
        - Default is 0 for new entries.
        - Non-zero means a particular row ID that needs to be updated.
        - `id = 0` for UPDATE_AND_INSERT.
        - `id` must be non-zero for UPDATE_ONLY.

    - **Action**: Action to perform: UPDATE_AND_INSERT or UPDATE_ONLY (required)

    - **employee_profile_component**: Comma-separated list of components to update 
      (e.g., 'present_address, permanent_address, bank_details,contact_details'). This parameter is required.
     
    - **request**: The request body containing the details to update or insert.

    **Details**:
    - If the `Action` is `UPDATE_AND_INSERT`:
        - Inserts new entries for the specified components.
        - For each specified component, if an existing active entry is found, it updates the `effective_to_date` to the day before the new start date to mark it as inactive.
    - If the `Action` is `UPDATE_ONLY`:
        - Requires a non-zero `id` to update the specific entry for the specified component.
        - Only one component can be updated at a time.
    - The `employee_profile_component` parameter is required to specify which components (present address, permanent address, bank details,contact_details) are to be updated or inserted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"]

    try:
        result = db_employee_master.update_employee_address_or_bank_details(
           db, employee_id, user_id, Action, request, id, employee_profile_component
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#--------------------------------------------------------------------------------------------------------------

@router.post("/save_employee_salary_details/{id}")
def save_employee_salary_details(
    id: int,
    employee_id: int,
    salary_data: EmployeeSalarySchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
) -> Union[dict, List]:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    message = db_employee_master.save_employee_salary_details(db, id, employee_id, salary_data, user_id)
    
    return message

#--------------------------------------------------------------------------------------------------------------


#=============================================EMPLOYEE TEAM MASTER====================================================================


@router.post("/save_employee_team_master")
def save_employee_team_master(
    data: List[EmployeeTeamMasterSchema],  # Now accepting a list of EmployeeTeamMasterSchema objects
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):   
    """
    Save or Update Employee Team Master records.

    This endpoint allows you to create or update multiple employee team master records.

    **Request Body:**

    The request body is a JSON array containing objects with the following keys:

    - **id**: An integer representing the team master record identifier.
      - If `0`, a new record is created.
      - If non-zero, the specified record is updated.
    - **department_id**:  The ID of the department to which the team belongs.
    - **team_name**:  The name of the team.
    - **description**: A description of the team.
    - **effective_from_date**: The date when the team becomes effective.
                               If no date is given, then set it to the current date.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        result = db_employee_master.save_employee_team_master(
            db, data, user_id  
        )
        return {"success": True, "message": result["message"]}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#----------------------------------------------------------------------------------------------------------
@router.get('/get_all_employee_team_master', response_model=List[HrViewEmployeeTeamSchema])
def get_all_employee_team_master(
    department_id: Optional[str] = Query("ALL"),
    team_id: Union[int, str] = Query("ALL"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get all employee team master records based on the provided department and team filters.

    - **department_id**: (Optional) Filter by department ID. If "ALL", return records from all departments.
    - **team_id**: (Optional) Filter by team ID. If "ALL", return records from all teams.
    - **db**: SQLAlchemy database session (injected via dependency).
    - **token**: OAuth2 token for authentication (injected via dependency).

    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    results = db_employee_master.get_all_employee_team_master(
        db, department_id, team_id
    )

    if not results:
        return []

    return results


#-----------------------------------------------------------------------------------------------------------
@router.get('/get_all_employee_team_members', response_model=List[EmployeeTeamMembersGet])
def get_all_employee_team_members(
    team_id:int,
    # employee_status:str,
    employee_status:  Optional[str] = Query("CURRENT_EMPLOYEE", description="Filter by type: 'CURRENT_EMPLOYEE', 'OLD_EMPLOYEE'"),
   
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
   
    """
    Get all employee team members based on the provided team ID and employee status filter.

    - **team_id**: (Required) The ID of the team for which you want to retrieve members.
    - **employee_status**: (Optional) Filter by employee status:
        - "CURRENT_EMPLOYEE": Return only current team members.
        - "OLD_EMPLOYEE": Return only old team members.
    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    

    results = db_employee_master.get_all_employee_team_members(
        db, team_id,employee_status
    )

  
    if not results:
        return []

    
    return results


#----------------------------------------------------------------------------------------------------------

@router.get("/get_team_leaders/{team_id}", response_model=List[HrViewEmployeeTeamMemberSchema])
def get_team_leaders(
    team_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all team leaders by team ID.
    
    - **team_id**: The ID of the team.
    """
    team_leaders = db_employee_master.get_team_leaders_by_team_id(db, team_id)

    if not team_leaders:
        return []

    return team_leaders

#---------------------------------------------------------------------------------------------------------

@router.post("/save_team_members/{team_id}")
def add_employee_to_team(
    team_id: int,
    department_id: int,  
    data: AddEmployeeToTeam, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Add or Update Employees in a Team.

    This endpoint allows you to add new employees to a team or update existing employee details in the team.

    **Path Parameters:**

    - `team_id`: The ID of the team to which employees will be added or updated.
    - `department_id`: The ID of the department from which  employee select.

    **Request Body:**

    The request body should be a JSON object containing a list of team members with the following keys:

    - `id`: The ID of the team member record. Use `0` to create a new record.
            if nonzero,update the specified record
    - `employee_id`: The ID of the employee.
    - `is_team_leader`: Indicates if the employee is a team leader ('yes' or 'no').
    - `team_leader_id`: The ID of the team leader (optional).
    - `effective_from_date`: The date when the team member becomes effective (default current date).

    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
       
        result = db_employee_master.save_team_members(db, team_id, department_id, data, user_id)
        return {"success": True, "message": result.get("message", "Saved successfully")}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#---------------------------------------------------------------------------------------------------

# Define a route
# @router.get("/check_username", response_model=UsernameCheckResponse)

# def check_username(
#     employee_id: int,
#     user_name: str,
#     db: Session = Depends(get_db)
# ) -> Dict[str, bool]:
#     # Check if employee_id is 0 (i.e., new entry) or if it's updating an existing employee
#     if employee_id == 0:
#         # Check if the user_name exists in the database
#         existing_user = db.query(UserBase).filter(UserBase.user_name == user_name).first()
#     else:
#         # Check if the user_name exists but exclude the current employee_id
#         existing_user = db.query(UserBase).filter(
#             UserBase.user_name == user_name,
#             UserBase.employee_id != employee_id
#         ).first()

#     if existing_user:
#         # If a user is found, return false with the appropriate message
#         return {
#             "success": False,
#             "message": "Username exists"
#         }

#     # If no user is found, return success true
#     return {
#         "success": True,
#         "message": "Username is available"
#     }

#------------------------------------------------------------------------


@router.get("/check_username_mobile_and_email")
def check_user_and_mobile(
    employee_id: Optional[int] = None, 
    user_name: Optional[str] = None, 
    personal_mobile_number: Optional[str] = None,
    personal_email_id: Optional[str] = None,  
    personal_whatsapp_number: Optional[str] = None,  
    db: Session = Depends(get_db)
):
    # Check if user_name is provided and not None
    if user_name:
        # Check if the username exists
        username_exists_query = db.query(UserBase).filter(
            UserBase.user_name == user_name
        )

        if employee_id:
            # Exclude the current employee's record while checking for uniqueness
            username_exists_query = username_exists_query.filter(UserBase.employee_id != employee_id)

        username_exists = db.query(username_exists_query.exists()).scalar()

        if username_exists:
            return {
                "success": False,
                "message": "Username exists"
            }
        else:
            return {
                "success": True,
                "message": "Username is available"
            }

    # Check if personal_mobile_number is provided and not None
    if personal_mobile_number:
        # Check if the mobile number exists and is not marked as deleted
        mobile_exists_query = db.query(EmployeeContactDetails).filter(
            EmployeeContactDetails.personal_mobile_number == personal_mobile_number,
            EmployeeContactDetails.is_deleted == 'no'
        )

        if employee_id:
            # Exclude the current employee's record while checking for uniqueness
            mobile_exists_query = mobile_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

        mobile_exists = db.query(mobile_exists_query.exists()).scalar()

        if mobile_exists:
            return {
                "success": False,
                "message": "Mobile number exists"
            }
        else:
            return {
                "success": True,
                "message": "Mobile number is available"
            }

    # Check if personal_email_id is provided and not None
    if personal_email_id:
        # Check if the email exists and is not marked as deleted
        email_exists_query = db.query(EmployeeContactDetails).filter(
            EmployeeContactDetails.personal_email_id == personal_email_id,
            EmployeeContactDetails.is_deleted == 'no'
        )

        if employee_id:
            # Exclude the current employee's record while checking for uniqueness
            email_exists_query = email_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

        email_exists = db.query(email_exists_query.exists()).scalar()

        if email_exists:
            return {
                "success": False,
                "message": "Email exists"
            }
        else:
            return {
                "success": True,
                "message": "Email is available"
            }

    # Check if personal_whatsapp_number is provided and not None
    if personal_whatsapp_number:
        # Check if the WhatsApp number exists and is not marked as deleted
        whatsapp_exists_query = db.query(EmployeeContactDetails).filter(
            EmployeeContactDetails.personal_whatsapp_number == personal_whatsapp_number,
            EmployeeContactDetails.is_deleted == 'no'
        )

        if employee_id:
            # Exclude the current employee's record while checking for uniqueness
            whatsapp_exists_query = whatsapp_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

        whatsapp_exists = db.query(whatsapp_exists_query.exists()).scalar()

        if whatsapp_exists:
            return {
                "success": False,
                "message": "WhatsApp number exists"
            }
        else:
            return {
                "success": True,
                "message": "WhatsApp number is available"
            }

    return {
        "success": False,
        "message": "No valid input provided"
    }

