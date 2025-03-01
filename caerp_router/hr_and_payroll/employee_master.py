from http import HTTPStatus
from fastapi.responses import JSONResponse
from caerp_db.common.models import AppBankMaster, AppEducationSubjectCourse, AppEducationalLevel, AppEducationalStream, EmployeeContactDetails, EmployeeEducationalQualification, EmployeeExperience, EmployeeMaster, EmployeeDocuments,  EmployeeProfessionalQualification, UserBase
from caerp_db.hr_and_payroll.model import ApplicationMaster, ApplicationRankList, HrDocumentMaster, InterviewSchedule, PrlSalaryComponent, VacancyAnnouncementDetails, VacancyAnnouncementMaster, VacancyDetailsView, VacancyEducationalLevel, VacancyEducationalStream, VacancyEducationalSubjectOrCourse, VacancyMaster, ViewApplicantDetails
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import AddEmployeeToTeam, AnnouncementDetailItem, AnnouncementsListResponse, ApplicantDetails, ApplicantDetailsView, CourseSchema, CreateInterviewPanelRequest, EducationLevelSchema, EducationRequirementSchema, EmployeeAddressDetailsSchema, EmployeeDetails, EmployeeDetailsCombinedSchema, EmployeeDocumentResponse, EmployeeLanguageProficiencyBase,  EmployeeMasterDisplay,EmployeeSalarySchema, EmployeeDocumentsSchema, EmployeeTeamMasterSchema, EmployeeTeamMembersGet, HrViewEmployeeTeamMemberSchema, HrViewEmployeeTeamSchema, InterviewScheduleRequest,  SaveEmployeeTeamMaster, ScheduledCandidate, StreamSchema, VacancyAnnouncements, VacancyCreateSchema, VacancySchema
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetailsGet,EmployeeMasterDisplay,EmployeePresentAddressGet,EmployeePermanentAddressGet,EmployeeContactGet,EmployeeBankAccountGet,EmployeeEmployementGet,EmployeeEmergencyContactGet,EmployeeDependentsGet,EmployeeSalaryGet,EmployeeEducationalQualficationGet,EmployeeExperienceGet,EmployeeDocumentsGet,EmployeeProfessionalQualificationGet,EmployeeSecurityCredentialsGet,EmployeeUserRolesGet
from caerp_db.database import get_db
from caerp_db.hr_and_payroll import db_employee_master
from sqlalchemy.orm import Session
from caerp_auth import oauth2

from typing import Any, List, Optional, Type, Union
from fastapi import APIRouter, Body ,Depends,Request,HTTPException,status,Response, Query, File, UploadFile
from caerp_auth.authentication import authenticate_user
from datetime import date,datetime
from caerp_constants.caerp_constants import RecordActionType, ActionType, ApprovedStatus, ActiveStatus
from sqlalchemy.exc import SQLAlchemyError
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

#--------------------------------------------------------------------------------------------------------------

from sqlalchemy import and_, func, or_, text



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
            "educational_qualification, employee_experience, employee_documents, professional_qualification,language_proficiency.]"
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
                            'employee_salary': [EmployeeSalaryGet(**salary.__dict__) for salary in salary_info]
                        })

                
                if option == "educational_qualification":
                   edu_qual_info = db_employee_master.get_qualification_details(db, employee_id=employee_id)
                   if edu_qual_info:
                        qualifications = [
                            EmployeeEducationalQualficationGet(
                               **qual.__dict__,
                               education_level=education_level,
                               education_stream=education_stream,
                               education_subject_or_course=education_subject_or_course
                            )
                            for qual, education_level, education_stream, education_subject_or_course in edu_qual_info
                        ]
                        
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
                        prof_qualifications = [
                            EmployeeProfessionalQualificationGet(
                               **qual.__dict__, 
                               qualification_name=profession_name  # Add the profession_name to the schema
                            )
                            for qual, profession_name in prof_qual_info
                        ]
                        employee_details.append({
                          'professional_qualification': prof_qualifications
                       })
                
                if option == "language_proficiency":
                    emp_lang_prof_info = db_employee_master.get_employee_language_proficiency_details(db, employee_id=employee_id)
                    if emp_lang_prof_info:
                       
                        employee_details.append({
                          'employee_language_proficiency': emp_lang_prof_info
                       })
                    else:
                        employee_details.append({
                            'employee_language_proficiency': []
                        })
            return employee_details
        else:
            return {"success": False, "message": "Profile component is required to fetch details for a specific employee."}

    
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
                "employee_number": emp.employee_number,
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
                "approval_status": emp.is_approved,
                "is_locked":emp.is_locked,
                "locked_on":emp.locked_on,
                "locked_by":emp.locked_by,
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
# @router.post('/employee_save_update_qualification_and_experience')
# def employee_save_update(
#     employee_id: int,
#     employee_profile_component: Optional[str] = Query(None, description="Comma-separated list of components to Save/Update"),
#     employee_details: EmployeeDetailsCombinedSchema = Body(...),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
#     auth_info = authenticate_user(token)
#     user_id = auth_info["user_id"]

#     try:
#         if not employee_profile_component:
#             raise ValueError("Employee profile component is required")

#         components = employee_profile_component.split(',')

#         # Save or update educational qualifications
#         if 'educational_qualifications' in components and employee_details.educational_qualifications:
#             save_or_update_records(
#                 db, EmployeeEducationalQualification, employee_id, employee_details.educational_qualifications, user_id
#             )

#         # Save or update experiences
#         if 'experiences' in components and employee_details.experiences:
#             save_or_update_records(
#                 db, EmployeeExperience, employee_id, employee_details.experiences, user_id
#             )

#         # Save or update professional qualifications
#         if 'professional_qualifications' in components and employee_details.professional_qualifications:
#             save_or_update_records(
#                 db, EmployeeProfessionalQualification, employee_id, employee_details.professional_qualifications, user_id
#             )

#         return {
#             "success": True,
#             "message": "Employee details saved/updated successfully",
#             "employee_id": employee_id
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post('/employee_save_update_qualification_and_experience')
def employee_save_update(
    employee_id: int,
    employee_profile_component: Optional[str] = Query(
        None,
        description="Comma-separated list of components to Save/Update; values are 'educational_qualifications', 'experiences', 'professional_qualifications'"
    ),
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
        db.rollback()
        return {"success": False, "message": str(e)}
    

#--------------------------------------------------------------------------------------------------------------
from pydantic import BaseModel, ValidationError
from sqlalchemy import insert, update

def save_or_update_records(
    db: Session,
    model_class: Type,
    employee_id: int,
    records: List[BaseModel],
    user_id: int
):
    try:
        # Step 1: Retrieve existing active records
        existing_records = db.query(model_class).filter(
            model_class.employee_id == employee_id,
            model_class.is_deleted == 'no'
        ).all()

        existing_ids = {record.id for record in existing_records}
        incoming_ids = {rec.id for rec in records if rec.id != 0}

        

        # Step 2: Determine IDs to delete
        if incoming_ids:  # Proceed with deletion only if there are incoming IDs
            ids_to_delete = existing_ids - incoming_ids
        else:
            ids_to_delete = set()  # Avoid marking everything for deletion when no valid incoming IDs
        

        # Step 3: Perform deletions
        if ids_to_delete:
            db.query(model_class).filter(
                model_class.id.in_(ids_to_delete)
            ).update({"is_deleted": 'yes'}, synchronize_session=False)

        # Step 4: Insert or update records
        for rec in records:
            record_data = rec.model_dump(exclude_unset=True)
            record_data['employee_id'] = employee_id

            if rec.id == 0:
                # New record insertion
                record_data['created_by'] = user_id
                record_data['created_on'] = datetime.now()
                insert_stmt = insert(model_class).values(**record_data)
                db.execute(insert_stmt)

            else:
                # Update existing record
                print(f"Updating record with id={rec.id} for employee_id={employee_id}")
                existing_record = db.query(model_class).filter(
                    model_class.id == rec.id,
                    model_class.is_deleted == 'no'
                ).first()

                if not existing_record:
                    raise HTTPException(status_code=404, detail=f"Record with id {rec.id} not found.")

                # Apply update
                update_stmt = update(model_class).where(
                    model_class.id == rec.id
                ).values(
                    **record_data,
                    is_deleted='no',  # Ensure the record remains active
                    modified_by=user_id,
                    modified_on=datetime.utcnow()
                )
                db.execute(update_stmt)

        # Commit all changes
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")





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
    salary_data: EmployeeSalarySchema,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):  
    """
    Add or Update Employee Salary Details.

    This endpoint allows you to either add a new salary detail or update an existing one for an employee.

    **Parameters:**

    - `id`: The ID of the salary record to be added or updated. Use `0` to create a new record.

    **Request Body:**

    The request body should be a JSON object containing the employee's salary details with the following keys:

    - `employee_id`: The ID of the employee whose salary details are being added/updated.
    - `component_id`: The ID of the salary component.
    - `calculation_frequency_id`: The frequency at which salary is calculated.
    - `calculation_method_id`: The method used for salary calculation (e.g., FIXED or PERCENTAGE).
    - `amount`: The amount for the salary component (for FIXED method).
    - `percentage_of_component_id`: The ID of the component if percentage-based calculation is used.
    - `percentage`: The percentage for the salary calculation (for PERCENTAGE method).
    - `effective_from_date`: The date when the salary becomes effective.
    - `effective_to_date`: The date when the salary ends (optional).
    - `next_increment_date`: The date for the next salary increment (optional).
    """

    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
        
        auth_info = authenticate_user(token)
        user_id = auth_info.get("user_id")

        message = db_employee_master.save_employee_salary_details(db, id, salary_data, user_id, employee_id)
        
        return message
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#----------------------------------------------------------------------------------------------------------

# @router.get("/get_salary_component_by_compons_type")
# def get_salary_component_by_type(

#     component_type: Optional[str] = Query("ALL"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get all salary component names by component_type.
    
#     """
#     component_type = component_type.upper()
    
#     if component_type not in ['ALL', 'ALLOWANCE', 'DEDUCTION']:
#         return {"message": "Invalid component type. Use 'ALL', 'ALLOWANCE', or 'DEDUCTION'."}
    
#     # If 'ALL' is selected, fetch both ALLOWANCE and DEDUCTION components
#     if component_type == 'ALL':
#         components = db.query(PrlSalaryComponent.id, PrlSalaryComponent.component_type,PrlSalaryComponent.component_name).filter(
#             PrlSalaryComponent.is_deleted == 'no'
#         ).all()
#     else:
#         components = db.query(PrlSalaryComponent.id, PrlSalaryComponent.component_type,PrlSalaryComponent.component_name).filter(
#             PrlSalaryComponent.component_type == component_type,
#             PrlSalaryComponent.is_deleted == 'no'
#         ).all()
    
#     # Return components or message if none found
#     if not components:
#         return []
    
#     return [{"id": component.id,
#              "component_type": component.component_type, 
#              "component_name": component.component_name} for component in components]

@router.get("/get_salary_component_by_type")
def get_salary_component_by_type(

    component_type: str = Query(..., enum=['ALL', 'ALLOWANCE', 'DEDUCTION'], description="Select 'ALL', 'ALLOWANCE', or 'DEDUCTION'"),
    db: Session = Depends(get_db)
):
    """
    Get all salary component names by component_type.
    
    """
    component_type = component_type.upper()
    
    # If 'ALL' is selected, fetch both ALLOWANCE and DEDUCTION components
    if component_type == 'ALL':
        components = db.query(PrlSalaryComponent.id, PrlSalaryComponent.component_type,PrlSalaryComponent.component_name).filter(
            PrlSalaryComponent.is_deleted == 'no'
        ).all()
    else:
        components = db.query(PrlSalaryComponent.id, PrlSalaryComponent.component_type,PrlSalaryComponent.component_name).filter(
            PrlSalaryComponent.component_type == component_type,
            PrlSalaryComponent.is_deleted == 'no'
        ).all()
    
    # Return components or message if none found
    if not components:
        return []
    
    return [{"id": component.id,
             "component_type": component.component_type, 
             "component_name": component.component_name} for component in components]


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


#------------------------------------------------------------------------


# @router.get("/check_username_mobile_and_email")
# def check_user_and_mobile(
#     employee_id: Optional[int] = None, 
#     user_name: Optional[str] = None, 
#     personal_mobile_number: Optional[str] = None,
#     personal_email_id: Optional[str] = None,  
#     personal_whatsapp_number: Optional[str] = None,  
#     db: Session = Depends(get_db)
# ):
#     # Check if user_name is provided and not None
#     if user_name:
#         # Check if the username exists
#         username_exists_query = db.query(UserBase).filter(
#             UserBase.user_name == user_name
#         )

#         if employee_id:
#             # Exclude the current employee's record while checking for uniqueness
#             username_exists_query = username_exists_query.filter(UserBase.employee_id != employee_id)

#         username_exists = db.query(username_exists_query.exists()).scalar()

#         if username_exists:
#             return {
#                 "success": False,
#                 "message": "Username exists"
#             }
#         else:
#             return {
#                 "success": True,
#                 "message": "Username is available"
#             }

#     # Check if personal_mobile_number is provided and not None
#     if personal_mobile_number:
#         # Check if the mobile number exists and is not marked as deleted
#         mobile_exists_query = db.query(EmployeeContactDetails).filter(
#             EmployeeContactDetails.personal_mobile_number == personal_mobile_number,
#             EmployeeContactDetails.is_deleted == 'no'
#         )

#         if employee_id:
#             # Exclude the current employee's record while checking for uniqueness
#             mobile_exists_query = mobile_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

#         mobile_exists = db.query(mobile_exists_query.exists()).scalar()

#         if mobile_exists:
#             return {
#                 "success": False,
#                 "message": "Mobile number exists"
#             }
#         else:
#             return {
#                 "success": True,
#                 "message": "Mobile number is available"
#             }

#     # Check if personal_email_id is provided and not None
#     if personal_email_id:
#         # Check if the email exists and is not marked as deleted
#         email_exists_query = db.query(EmployeeContactDetails).filter(
#             EmployeeContactDetails.personal_email_id == personal_email_id,
#             EmployeeContactDetails.is_deleted == 'no'
#         )

#         if employee_id:
#             # Exclude the current employee's record while checking for uniqueness
#             email_exists_query = email_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

#         email_exists = db.query(email_exists_query.exists()).scalar()

#         if email_exists:
#             return {
#                 "success": False,
#                 "message": "Email exists"
#             }
#         else:
#             return {
#                 "success": True,
#                 "message": "Email is available"
#             }

#     # Check if personal_whatsapp_number is provided and not None
#     if personal_whatsapp_number:
#         # Check if the WhatsApp number exists and is not marked as deleted
#         whatsapp_exists_query = db.query(EmployeeContactDetails).filter(
#             EmployeeContactDetails.personal_whatsapp_number == personal_whatsapp_number,
#             EmployeeContactDetails.is_deleted == 'no'
#         )

#         if employee_id:
#             # Exclude the current employee's record while checking for uniqueness
#             whatsapp_exists_query = whatsapp_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

#         whatsapp_exists = db.query(whatsapp_exists_query.exists()).scalar()

#         if whatsapp_exists:
#             return {
#                 "success": False,
#                 "message": "WhatsApp number exists"
#             }
#         else:
#             return {
#                 "success": True,
#                 "message": "WhatsApp number is available"
#             }

#     return {
#         "success": False,
#         "message": "No valid input provided"
#     }



# @router.get("/test1/check_username_mobile_and_email")
# def check_user_and_mobile(
#     employee_id: Optional[int] = None, 
#     user_name: Optional[str] = None, 
#     personal_mobile_number: Optional[str] = None,
#     personal_email_id: Optional[str] = None,  
#     personal_whatsapp_number: Optional[str] = None,  
#     db: Session = Depends(get_db)
# ):
#     result = {"success": True, "messages": []}

#     # Treat "null" (string) as None for each parameter
#     if user_name == "null":
#         user_name = None
#     if personal_mobile_number == "null":
#         personal_mobile_number = None
#     if personal_email_id == "null":
#         personal_email_id = None
#     if personal_whatsapp_number == "null":
#         personal_whatsapp_number = None

#     # Check if user_name is provided and not None
#     if user_name:
#         # Check if the username exists
#         username_exists_query = db.query(UserBase).filter(UserBase.user_name == user_name)

#         if employee_id:
#             # Exclude the current employee's record while checking for uniqueness
#             username_exists_query = username_exists_query.filter(UserBase.employee_id != employee_id)

#         username_exists = db.query(username_exists_query.exists()).scalar()

#         if username_exists:
#             result["success"] = False
#             result["messages"].append("Username exists")
#         else:
#             result["messages"].append("Username is available")

#     # Check if personal_mobile_number is provided and not None
#     if personal_mobile_number:
#         mobile_exists_query = db.query(EmployeeContactDetails).filter(
#             EmployeeContactDetails.personal_mobile_number == personal_mobile_number,
#             EmployeeContactDetails.is_deleted == 'no'
#         )

#         if employee_id:
#             mobile_exists_query = mobile_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

#         mobile_exists = db.query(mobile_exists_query.exists()).scalar()

#         if mobile_exists:
#             result["success"] = False
#             result["messages"].append("Mobile number exists")
#         else:
#             result["messages"].append("Mobile number is available")

#     # Check if personal_email_id is provided and not None
#     if personal_email_id:
#         email_exists_query = db.query(EmployeeContactDetails).filter(
#             EmployeeContactDetails.personal_email_id == personal_email_id,
#             EmployeeContactDetails.is_deleted == 'no'
#         )

#         if employee_id:
#             email_exists_query = email_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

#         email_exists = db.query(email_exists_query.exists()).scalar()

#         if email_exists:
#             result["success"] = False
#             result["messages"].append("Email exists")
#         else:
#             result["messages"].append("Email is available")

#     # Check if personal_whatsapp_number is provided and not None
#     if personal_whatsapp_number:
#         whatsapp_exists_query = db.query(EmployeeContactDetails).filter(
#             EmployeeContactDetails.personal_whatsapp_number == personal_whatsapp_number,
#             EmployeeContactDetails.is_deleted == 'no'
#         )

#         if employee_id:
#             whatsapp_exists_query = whatsapp_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

#         whatsapp_exists = db.query(whatsapp_exists_query.exists()).scalar()

#         if whatsapp_exists:
#             result["success"] = False
#             result["messages"].append("WhatsApp number exists")
#         else:
#             result["messages"].append("WhatsApp number is available")

#     # If no valid input is provided
#     if not user_name and not personal_mobile_number and not personal_email_id and not personal_whatsapp_number:
#         return {
#             "success": False,
#             "message": "No valid input provided"
#         }

#     return result


@router.get("/check_username_mobile_and_email")
def check_user_and_mobile(
    employee_id: Optional[int] = None, 
    user_name: Optional[str] = "NULL", 
    personal_mobile_number: Optional[str] = "NULL",
    personal_email_id: Optional[str] = "NULL",  
    personal_whatsapp_number: Optional[str] = "NULL",  
    db: Session = Depends(get_db)
):
    result = {"success": True, "messages": []}

 
    if user_name == "NULL":
        user_name = None
    if personal_mobile_number == "NULL":
        personal_mobile_number = None
    if personal_email_id == "NULL":
        personal_email_id = None
    if personal_whatsapp_number == "NULL":
        personal_whatsapp_number = None

    # Check if user_name is provided and not None
    if user_name:
        username_exists_query = db.query(UserBase).filter(UserBase.user_name == user_name)

        if employee_id:
            username_exists_query = username_exists_query.filter(UserBase.employee_id != employee_id)

        username_exists = db.query(username_exists_query.exists()).scalar()

        if username_exists:
            result["success"] = False
            result["messages"].append("Username exists")
        else:
            result["messages"].append("Username is available")

    # Check if personal_mobile_number is provided and not None
    if personal_mobile_number:
        mobile_exists_query = db.query(EmployeeContactDetails).filter(
            EmployeeContactDetails.personal_mobile_number == personal_mobile_number,
            EmployeeContactDetails.is_deleted == 'no'
        )

        if employee_id:
            mobile_exists_query = mobile_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

        mobile_exists = db.query(mobile_exists_query.exists()).scalar()

        if mobile_exists:
            result["success"] = False
            result["messages"].append("Mobile number exists")
        else:
            result["messages"].append("Mobile number is available")

    # Check if personal_email_id is provided and not None
    if personal_email_id:
        email_exists_query = db.query(EmployeeContactDetails).filter(
            EmployeeContactDetails.personal_email_id == personal_email_id,
            EmployeeContactDetails.is_deleted == 'no'
        )

        if employee_id:
            email_exists_query = email_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

        email_exists = db.query(email_exists_query.exists()).scalar()

        if email_exists:
            result["success"] = False
            result["messages"].append("Email exists")
        else:
            result["messages"].append("Email is available")

    # Check if personal_whatsapp_number is provided and not None
    if personal_whatsapp_number:
        whatsapp_exists_query = db.query(EmployeeContactDetails).filter(
            EmployeeContactDetails.personal_whatsapp_number == personal_whatsapp_number,
            EmployeeContactDetails.is_deleted == 'no'
        )

        if employee_id:
            whatsapp_exists_query = whatsapp_exists_query.filter(EmployeeContactDetails.employee_id != employee_id)

        whatsapp_exists = db.query(whatsapp_exists_query.exists()).scalar()

        if whatsapp_exists:
            result["success"] = False
            result["messages"].append("WhatsApp number exists")
        else:
            result["messages"].append("WhatsApp number is available")

    # If no valid input is provided
    if not user_name and not personal_mobile_number and not personal_email_id and not personal_whatsapp_number:
        return {
            "success": False,
            "message": "No valid input provided"
        }

    return result



#--------------------------------------------------------------------------------------------------------


@router.post("/save_employee_language_proficiency/")
def save_employee_language_proficiency(
    data: List[EmployeeLanguageProficiencyBase], 
    employee_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    try:
        # Call the database function to process records
        result = db_employee_master.save_employee_language_proficiency(
            db, employee_id, data, user_id
        )

        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            return {
                "success": False,
                "message": result["message"]
            }
            
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"success": False, "message": str(e)}

#------------------------------------------------------------------------------------------------

# @router.post("/vacancy/create", response_model=dict)
# async def create_vacancy(vacancy_data: VacancyCreateSchema, 
#                          db: Session = Depends(get_db),
#                          token: str = Depends(oauth2.oauth2_scheme)):
#     """
#     Create a new vacancy record and its associated data.
#     Inserts data into vacancy_master and related tables like VacancyExperience, VacancySkills, etc.
#     """
#     # Check if token is provided
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
#     # Authenticate and get user_id from token
#     auth_info = authenticate_user(token)
#     user_id = auth_info.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")

#     try:
#         # Pass user_id (as created_by) along with vacancy data to the save function
#         result = db_employee_master.save_vacancy_data(vacancy_data, db, user_id)
        
#         # Return the response with success message and the generated vacancy_master_id
#         return {"message": "Vacancy created successfully", "vacancy_master_id": result['vacancy_master_id']}
    
#     except Exception as e:
#         # Handle any exceptions and return an HTTP error if something goes wrong
#         raise HTTPException(status_code=500, detail=f"Error while creating vacancy: {str(e)}")
#-------------------------------------------------------------------------------------------------------
# HR

#-------------------------------------------------------------------------------------

@router.post("/save_vacancy_data", response_model=dict)
async def create_vacancy(vacancy_data: VacancyCreateSchema, 
                         db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)):
    """
    Create or Update a Vacancy.

    - **If `id=0`**, inserts a new vacancy.
    - **If `id>0`**, updates the existing vacancy.
    
    **Request Body Example:**
    ```json
    Request body
        {
        "id": 0,
        "department_id": 1,
        "designation_id": 2,
        "vacancy_count": 3,
        "job_description": "Software Engineer Position",
        "job_location": "New York",
        "reported_date": "2025-02-28",
        "announcement_date": "2025-03-01",
        "closing_date": "2025-03-10",
        "vacancy_status": "OPEN",
        "experience_required": "yes",
        "vacancy_experience": [
            {
            "id": 0,
            "min_years": 2,
            "max_years": 5,
            "weightage": 10
            }
        ],
        "skills_required": [
            {
            "id": 0,
            "skill_id": 101,
            "weightage": 20
            }
        ],
        "language_proficiency": [
            {
            "id": 0,
            "language_id": 1,
            "language_proficiency_id": 2,
            "is_read_required": "yes",
            "read_weightage": 10,
            "is_write_required": "yes",
            "write_weightage": 15,
            "is_speak_required": "yes",
            "speak_weightage": 20
            }
        ],
        "education": {
            "levels": [
            {
                "id": 0,
                "education_level_id": 3,
                "weightage": 30,
                "streams": [
                {
                    "id": 0,
                    "education_stream_id": 5,
                    "weightage": 20,
                    "courses": [
                    {
                        "id": 0,
                        "education_subject_or_course_id": 10,
                        "weightage": 15
                    }
                    ]
                }
                ]
            }
            ]
        }
    }
    ```

    **Response:**
    {
  "success": true,
  "message": "Vacancy created successfully",
  "vacancy_master_id": 67
    }
    
    **Errors:**
    - `404 Not Found` if `id > 0` and vacancy does not exist.

    """
    # Check if token is provided
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    # Authenticate and get user_id from token
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")

    try:
        # Pass user_id (as created_by) along with vacancy data to the save function
        result = db_employee_master.save_vacancy_data(vacancy_data, db, user_id)
        
        # Return the response with success message and the generated vacancy_master_id
        return result  # Returning the result which includes success, message, and vacancy_master_id
    
    except Exception as e:
        # Handle any exceptions and return an HTTP error if something goes wrong
        raise HTTPException(status_code=500, detail=f"Error while creating vacancy: {str(e)}")


#-------------------------------------------------------------------------------------


  

# @router.get("/vacancy_details")
# def get_vacancies(
#     department_id: Optional[str] = Query("ALL", description="Filter by department ID (pass 'ALL' for no filter)"),
#     designation_id: Optional[str] = Query("ALL", description="Filter by designation ID (pass 'ALL' for no filter)"),
#     status: str = Query("ALL", description="Filter by vacancy status (OPEN, CLOSED, ALL)"),
#     announcement_date: Optional[str] = Query(None, description="Filter by announcement date (yyyy-mm-dd)"),
#     closing_date: Optional[str] = Query(None, description="Filter by closing date (yyyy-mm-dd)"),
#     vacancy_id: Optional[int] = Query(None, description="Filter by specific vacancy ID"),
#     search: Optional[str] = Query(
#         None,
#         description="Search vacancies by keyword. You can search by department name, designation name, job description, or job location."
#     ),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
#     filters = []

#     if department_id and department_id != "ALL":
#         filters.append(VacancyDetailsView.department_id == int(department_id))

#     if designation_id and designation_id != "ALL":
#         filters.append(VacancyDetailsView.designation_id == int(designation_id))

#     if status and status != "ALL":
#         filters.append(VacancyDetailsView.vacancy_status == status)

#     if announcement_date:
#         filters.append(VacancyDetailsView.announcement_date == announcement_date)

#     if closing_date:
#         filters.append(VacancyDetailsView.closing_date == closing_date)

#     vacancies_query = db.query(VacancyDetailsView).filter(and_(*filters))

#     if search:
#         search_filter = or_(
#             VacancyDetailsView.department_name.ilike(f"%{search}%"),
#             VacancyDetailsView.designation_name.ilike(f"%{search}%"),
#             VacancyDetailsView.job_description.ilike(f"%{search}%"),
#             VacancyDetailsView.job_location.ilike(f"%{search}%")
#         )
#         vacancies_query = vacancies_query.filter(search_filter)

#     if vacancy_id:
#         vacancy_details = db_employee_master.get_vacancy_details_by_id(db, vacancy_id)
#         if vacancy_details:
#             return vacancy_details
#         else:
#             return {"vacancies": []}

#     vacancies = vacancies_query.all()

#     return {
#         "vacancies": [
#             {
#                 "vacancy_master_id": vacancy.vacancy_master_id,
#                 "department_id": vacancy.department_id,
#                 "department_name": vacancy.department_name,
#                 "designation_id": vacancy.designation_id,
#                 "designation_name": vacancy.designation_name,
#                 "vacancy_count": vacancy.vacancy_count,
#                 "job_description": vacancy.job_description,
#                 "job_location": vacancy.job_location,
#                 "reported_date": vacancy.reported_date,
#                 "announcement_date": vacancy.announcement_date,
#                 "closing_date": vacancy.closing_date,
#                 "vacancy_status": vacancy.vacancy_status,
#                 "experience_required": vacancy.experience_required,
#                 "skill_id": vacancy.skill_id,
#                 "skill_name": vacancy.skill_name,
#                 "skill_weightage": vacancy.skill_weightage,
#                 "language_id": vacancy.language_id,
#                 "language_name": vacancy.language_name,
#                 "language_proficiency_id": vacancy.language_proficiency_id,
#                 "proficiency_level": vacancy.proficiency_level,
#                 "is_read_required": vacancy.is_read_required,
#                 "read_weightage": vacancy.read_weightage,
#                 "is_write_required": vacancy.is_write_required,
#                 "write_weightage": vacancy.write_weightage,
#                 "is_speak_required": vacancy.is_speak_required,
#                 "speak_weightage": vacancy.speak_weightage,
#                 "education_level_id": vacancy.education_level_id,
#                 "is_any_education_level": vacancy.is_any_education_level,
#                 "education_stream_id": vacancy.education_stream_id,
#                 "is_any_education_stream": vacancy.is_any_education_stream,
#                 "education_subject_or_course_id": vacancy.education_subject_or_course_id,
#                 "is_any_subject_or_course": vacancy.is_any_subject_or_course,
#                 "education_level_name": vacancy.education_level_name,
#                 "education_stream_name": vacancy.education_stream_name,
#                 "subject_or_course_name": vacancy.subject_or_course_name,
#                 "min_years": vacancy.min_years,
#                 "max_years": vacancy.max_years,
#                 "experience_weightage": vacancy.experience_weightage,
#             }
#             for vacancy in vacancies
#         ]
#     }


@router.get("/vacancy_details")
def get_vacancies(
    department_id: Optional[str] = Query("ALL", description="Filter by department ID (pass 'ALL' for no filter)"),
    designation_id: Optional[str] = Query("ALL", description="Filter by designation ID (pass 'ALL' for no filter)"),
    status: str = Query("ALL", description="Filter by vacancy status (OPEN, ANNOUNCED, CLOSED, RANKLIST_GENERATED, INTERVIEW_SCHEDULED, ALL)"),
    announcement_date: Optional[str] = Query(None, description="Filter by announcement date (yyyy-mm-dd)"),
    closing_date: Optional[str] = Query(None, description="Filter by closing date (yyyy-mm-dd)"),
    vacancy_id: Optional[int] = Query(None, description="Filter by specific vacancy ID"),
    search: Optional[str] = Query(
        None,
        description="Search vacancies by keyword. You can search by department name, designation name, job description, or job location."
    ),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token is missing")

    filters = []

    # Apply status filter only if it's not "ALL"
    if status and status != "ALL":
        # filters.append(VacancyDetailsView.vacancy_status == status)
        filters.append(func.trim(func.lower(VacancyDetailsView.vacancy_status)) == status.lower())

    if department_id and department_id != "ALL":
        filters.append(VacancyDetailsView.department_id == int(department_id))

    if designation_id and designation_id != "ALL":
        filters.append(VacancyDetailsView.designation_id == int(designation_id))

    if announcement_date:
        filters.append(VacancyDetailsView.announcement_date == announcement_date)

    if closing_date:
        filters.append(VacancyDetailsView.closing_date == closing_date)

    # Handle vacancy_id filter separately
    if vacancy_id:
        vacancy_details = db_employee_master.get_vacancy_details_by_id(db, vacancy_id)
        return {"vacancies": vacancy_details if vacancy_details else []}

    # Apply filters only if there are any
    vacancies_query = db.query(VacancyDetailsView)
    if filters:
        vacancies_query = vacancies_query.filter(and_(*filters))

    if search:
        search_filter = or_(
            VacancyDetailsView.department_name.ilike(f"%{search}%"),
            VacancyDetailsView.designation_name.ilike(f"%{search}%"),
            VacancyDetailsView.job_description.ilike(f"%{search}%"),
            VacancyDetailsView.job_location.ilike(f"%{search}%")
        )
        vacancies_query = vacancies_query.filter(search_filter)

    vacancies = vacancies_query.all()

    # Return an empty list if no vacancies are found
    if not vacancies:
        return {"vacancies": []}

    return {
        "vacancies": [
            {
                "vacancy_master_id": vacancy.vacancy_master_id,
                "department_id": vacancy.department_id,
                "department_name": vacancy.department_name,
                "designation_id": vacancy.designation_id,
                "designation_name": vacancy.designation_name,
                "vacancy_count": vacancy.vacancy_count,
                "job_description": vacancy.job_description,
                "job_location": vacancy.job_location,
                "reported_date": vacancy.reported_date,
                "announcement_date": vacancy.announcement_date,
                "closing_date": vacancy.closing_date,
                "vacancy_status": vacancy.vacancy_status,
                "experience_required": vacancy.experience_required,
                "skill_id": vacancy.skill_id,
                "skill_name": vacancy.skill_name,
                "skill_weightage": vacancy.skill_weightage,
                "language_id": vacancy.language_id,
                "language_name": vacancy.language_name,
                "language_proficiency_id": vacancy.language_proficiency_id,
                "proficiency_level": vacancy.proficiency_level,
                "is_read_required": vacancy.is_read_required,
                "read_weightage": vacancy.read_weightage,
                "is_write_required": vacancy.is_write_required,
                "write_weightage": vacancy.write_weightage,
                "is_speak_required": vacancy.is_speak_required,
                "speak_weightage": vacancy.speak_weightage,
                "education_level_id": vacancy.education_level_id,
                "is_any_education_level": vacancy.is_any_education_level,
                "education_stream_id": vacancy.education_stream_id,
                "is_any_education_stream": vacancy.is_any_education_stream,
                "education_subject_or_course_id": vacancy.education_subject_or_course_id,
                "is_any_subject_or_course": vacancy.is_any_subject_or_course,
                "education_level_name": vacancy.education_level_name,
                "education_stream_name": vacancy.education_stream_name,
                "subject_or_course_name": vacancy.subject_or_course_name,
                "min_years": vacancy.min_years,
                "max_years": vacancy.max_years,
                "experience_weightage": vacancy.experience_weightage,
            }
            for vacancy in vacancies
        ]
    }

#-------------------------------------------------------------------------------------------------------------
@router.post("/save_vacancy_announcements/")
async def save_vacancy_announcements(
    data: VacancyAnnouncements,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    
    """
    Save Vacancy Announcements API

    Endpoint:
        POST /save_vacancy_announcements/

    Description:
        This endpoint is used to create or update vacancy announcements.
        When a vacancy is announced, the vacancy_master table's status should be updated to "ANNOUNCED".

    Request Body Example:
        {
        "vacancy_announcement_master": [
            {
            "id": 0,
            "title": "Software Engineer Hiring",
            "description": "We are hiring for the position of Software Engineer with experience in Python and React.",
            "announcement_type": "GENERAL",
            "closing_date": "2025-03-10",
            "announcement_details": [
                {
                "id": 0,
                "vacancy_master_id": 67
                },
                {
                "id": 0,
                "vacancy_master_id": 66
                }
            ]
            }
        ]
        }

    Request Parameters:
        vacancy_announcement_master (Array)    : List of vacancy announcements.
        ├── id (Integer)                       : Use 0 for a new record, otherwise provide the existing announcement ID for updates.
        ├── title (String)                      : Title of the vacancy announcement.
        ├── description (String)                : Description of the announcement.
        ├── announcement_type (Enum)            : Type of announcement. Allowed values: ["SPECIAL", "GENERAL"].
        ├── closing_date (String)               : Closing date in "YYYY-MM-DD" format.
        ├── announcement_details (Array)        : List of associated vacancies.
            ├── id (Integer)                    : Use 0 for new vacancy details, otherwise provide an existing ID.
            ├── vacancy_master_id (Integer)      : The ID of the vacancy from vacancy_master.

    Response Example:
        Success Response:
        {
        "success": true,
        "message": "Vacancy announcements saved successfully"
        }

        Error Responses:
        Invalid Announcement Type:
        {
        "detail": "Invalid announcement_type. Allowed values are ['SPECIAL', 'GENERAL']."
        }

        Missing Required Fields:
        {
        "detail": "Field 'title' is required."
        }

        Database Error:
        {
        "success": false,
        "message": "Unexpected error: VacancyAnnouncementMaster with id 5 not found for update."
        }

    Additional Notes:
        - announcement_type must be either "SPECIAL" or "GENERAL".
        - If id = 0, a new announcement is created.
        - If id > 0, the existing announcement will be updated.
        - Upon announcement, the vacancy_master table status should be updated to "ANNOUNCED".
        - API expects a valid authentication token in the request.
    """

    
    
    # Step 1: Validate the token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    # Step 2: Authenticate the user (you can modify as per your authentication mechanism)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    # Step 3: Save the vacancy announcements to the DB
    result = db_employee_master.save_vacancy_announcements_to_db(data, db, user_id)

    # Step 4: Return the result based on success or failure
    if result["success"]:
        return {"success": True, "message": "Vacancy announcements saved successfully"}
    else:
        raise HTTPException(status_code=500, detail=result["message"])
    
#-------------------------------------------------------------------------------------------------------


# @router.get("/announcements_list", response_model=AnnouncementsListResponse)
# async def get_announcements(
#     announcement_type: Optional[str] = Query("ALL", enum=["ALL", "GENERAL", "SPECIAL"]),
#     announcement_status: Optional[str] = Query("ALL", enum=["ALL", "ACTIVE", "INACTIVE"]),
#     status: Optional[str] = None,
#     announcement_date: Optional[str] = None,
#     closing_date: Optional[str] = None,
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
    
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
#     filters = []

#     if announcement_date:
#         try:
#             announcement_date = datetime.strptime(announcement_date, "%Y-%m-%d").date()
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid format for announcement_date. Use YYYY-MM-DD")

#     if closing_date:
#         try:
#             closing_date = datetime.strptime(closing_date, "%Y-%m-%d").date()
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid format for closing_date. Use YYYY-MM-DD")

#     if announcement_type != "ALL":
#         filters.append(VacancyAnnouncementMaster.announcement_type == announcement_type)

#     if announcement_status != "ALL":
#         filters.append(VacancyAnnouncementMaster.announcement_status == announcement_status)

#     if status:
#         filters.append(VacancyAnnouncementMaster.is_deleted == status)

#     if closing_date:
#         filters.append(VacancyAnnouncementMaster.closing_date == closing_date)

#     # Query with Joins
#     announcements = (
#         db.query(
#             VacancyAnnouncementMaster,
#             VacancyMaster.id.label("vacancy_master_id"),
#             VacancyMaster.job_description.label("vacancy_name"),  # Get job description as vacancy name
#             EmployeeMaster.first_name,
#             EmployeeMaster.middle_name,
#             EmployeeMaster.last_name,
#         )
#         .join(VacancyAnnouncementDetails, VacancyAnnouncementDetails.vacancy_announcement_master_id == VacancyAnnouncementMaster.id, isouter=True)
#         .join(VacancyMaster, VacancyMaster.id == VacancyAnnouncementDetails.vacancy_master_id, isouter=True)
#         .join(EmployeeMaster, EmployeeMaster.employee_id == VacancyAnnouncementMaster.created_by, isouter=True)
#         .filter(*filters)
#         .all()
#     )

#     result = []
#     for announcement, vacancy_master_id, vacancy_name, first_name, middle_name, last_name in announcements:
#         details = db.query(VacancyAnnouncementDetails).filter(
#             VacancyAnnouncementDetails.vacancy_announcement_master_id == announcement.id
#         ).all()

#         announcement_details = [
#             {
#                 "id": detail.id,
#                 "vacancy_master_id": detail.vacancy_master_id,
#                 # "vacancy_name": vacancy_name,  # Add vacancy name
#             }
#             for detail in details
#         ]

#         # Combine first name, middle name, and last name for full name
#         full_name = " ".join(filter(None, [first_name, middle_name, last_name]))

#         result.append({
#             "id": announcement.id,
#             "title": announcement.title,
#             "announcement_type": announcement.announcement_type,
#             "description": announcement.description,
#             "announcement_status": announcement.announcement_status,
#             "created_by": full_name, 
#             "first_name": first_name,
#             "middle_name": middle_name,
#             "last_name": last_name,
#             "created_on": announcement.created_on.date(),
#             "closing_date": announcement.closing_date,
#             "announcement_details": announcement_details,
#         })

#     return {"announcements": result}

@router.get("/announcements_list")
async def get_announcements(
    announcement_type: Optional[str] = Query("ALL", enum=["ALL", "GENERAL", "SPECIAL"]),
    announcement_status: Optional[str] = Query("ALL", enum=["ALL", "ACTIVE", "INACTIVE"]),
    status: Optional[str] = None,
    announcement_date: Optional[str] = None,
    closing_date: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    filters = []

    if announcement_date:
        try:
            announcement_date = datetime.strptime(announcement_date, "%Y-%m-%d").date()
            filters.append(VacancyAnnouncementMaster.created_on == announcement_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid format for announcement_date. Use YYYY-MM-DD")

    if closing_date:
        try:
            closing_date = datetime.strptime(closing_date, "%Y-%m-%d").date()
            filters.append(VacancyAnnouncementMaster.closing_date == closing_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid format for closing_date. Use YYYY-MM-DD")

    if announcement_type != "ALL":
        filters.append(VacancyAnnouncementMaster.announcement_type == announcement_type)

    if announcement_status != "ALL":
        filters.append(VacancyAnnouncementMaster.announcement_status == announcement_status)

    if status:
        filters.append(VacancyAnnouncementMaster.is_deleted == status)

    # Query with necessary joins (removing VacancyMaster join since `vacancy_name` is not needed)
    announcements = (
        db.query(
            VacancyAnnouncementMaster,
            EmployeeMaster.first_name,
            EmployeeMaster.middle_name,
            EmployeeMaster.last_name
        )
        .join(EmployeeMaster, EmployeeMaster.employee_id == VacancyAnnouncementMaster.created_by, isouter=True)
        .filter(*filters)
        .all()
    )

    # Dictionary to store unique announcements
    result_dict = {}

    for announcement, first_name, middle_name, last_name in announcements:
        announcement_id = announcement.id

        # Full name creation
        full_name = " ".join(filter(None, [first_name, middle_name, last_name]))

        # If announcement is not already added, initialize it
        if announcement_id not in result_dict:
            result_dict[announcement_id] = {
                "id": announcement.id,
                "title": announcement.title,
                "announcement_type": announcement.announcement_type,
                "description": announcement.description,
                "announcement_status": announcement.announcement_status,
                "created_by": full_name,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "created_on": announcement.created_on.strftime("%Y-%m-%d"),
                "closing_date": announcement.closing_date.strftime("%Y-%m-%d"),
                "announcement_details": []  # Empty list for details
            }

        # Fetch announcement details
        details = db.query(VacancyAnnouncementDetails).filter(
            VacancyAnnouncementDetails.vacancy_announcement_master_id == announcement_id
        ).all()

        for detail in details:
            result_dict[announcement_id]["announcement_details"].append({
                "id": detail.id,
                "vacancy_master_id": detail.vacancy_master_id,
            })

    # Convert dictionary values to list for response
    result = list(result_dict.values())

    return {"announcements": result}




#-------------------------------------------------------------------------------------------------------------------

@router.post("/save_applicant/")
async def save_applicant(

    data: ApplicantDetails, 
    vacancy_master_id: Optional[int] = None, 
    profile_component: List[str] = Query(...),  # Receiving the list of components to save
    db: Session = Depends(get_db),  # Dependency for the DB session
    token: str = Depends(oauth2.oauth2_scheme)  # OAuth2 token for authentication
):
    # Step 1: Validate the token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    # Step 2: Authenticate the user
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")

    # Step 3: Save the applicant data to the DB by passing profile_component
    result = db_employee_master.save_applicant(data,vacancy_master_id, db, user_id, profile_component)

    # Step 4: Return the result based on success or failure
    if result["success"]:
        return {
            "success": True,
            "message": "Saved successfully",
            "applicant_id": result.get("applicant_id")  
        }
    else:
        raise HTTPException(status_code=500, detail=result["message"])


#------------------------------------------------------------------------------------------




@router.get("/get_applicant_details/", response_model=Dict[str, Any])
def get_applicant_details(
    applicant_id: Optional[int] = None,
    profile_component: Optional[str] = None,
    vacancy_master_id: Optional[int] = None, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """Fetch applicant details based on provided parameters.
    For selecting profile_component can provode any on the below component to 
    give the specific details of each component
    applicant_master
    applicant_present_address
    applicant_permanent_address
    applicant_contact_details
    applicant_educational_qualification
    applicant_professional_qualification
    applicant_experience
    applicant_language_proficiency
    applicant_hobby
    applicant_skill
    applicant_social_media_profile
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    profile_data = {}

    if applicant_id is None and profile_component is None and vacancy_master_id is None:
        # Fetch all applicant details
        applicant_details = db_employee_master.get_all_applicant_detals(db)  # Fixed typo
        if not applicant_details:
            raise HTTPException(status_code=404, detail="No data found for applicant details")
        profile_data["applicant_details"] = [ApplicantDetailsView(**applicant.__dict__) for applicant in applicant_details]

    elif vacancy_master_id is not None:
        # Fetch applicants by vacancy_master_id
        applicant_details = db_employee_master.get_applicants_by_vacancy(db, vacancy_master_id)
        if not applicant_details:
            raise HTTPException(status_code=404, detail="No applicants found for the given vacancy")
        profile_data["applicants_by_vacancy"] = [dict(row._mapping) for row in applicant_details]

    elif applicant_id is not None and profile_component is None:
        # Fetch all details for a specific applicant
        applicant_details = db_employee_master.get_applicant_master(db, applicant_id)
        if not applicant_details:
            raise HTTPException(status_code=404, detail="No applicant found with the given ID")
        profile_data["applicant_master"] = applicant_details

    elif applicant_id is not None and profile_component is not None:
        # Fetch specific profile component details for a given applicant
        component_map = {
            "applicant_master": db_employee_master.get_applicant_master,
            "applicant_present_address": db_employee_master.applicant_present_address,
            "applicant_permanent_address": db_employee_master.applicant_permanent_address,
            "applicant_contact_details": db_employee_master.get_applicant_contact_details,
            "applicant_educational_qualification": db_employee_master.get_applicant_educational_qualifications,
            "applicant_professional_qualifications": db_employee_master.get_applicant_professional_qualifications,
            "applicant_experience": db_employee_master.get_applicant_experience,
            "applicant_language_proficiency": db_employee_master.get_applicant_language_proficiency,
            "applicant_hobby": db_employee_master.get_applicant_hobbies,
            "applicant_skill": db_employee_master.get_applicant_skills,
            "applicant_social_media_profile": db_employee_master.get_applicant_social_media_profiles
        }

        if profile_component not in component_map:
            raise HTTPException(status_code=400, detail=f"Invalid profile component: {profile_component}")

        profile_data[profile_component] = component_map[profile_component](db, applicant_id)

    if not profile_data:
        raise HTTPException(status_code=404, detail="No data found for the given parameters")

    return profile_data



#----------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------
def fetch_skills_scores(vacancy_id: int, db: Session):
    query = text("""
        SELECT 
            a.applicant_id,
            a.first_name,
            a.middle_name,
            a.last_name,
            SUM(DISTINCT vs.weightage) AS skill_score
        FROM 
            applicant_master a
        JOIN 
            applicant_skill aps ON a.applicant_id = aps.applicant_id
        JOIN 
            vacancy_skills vs ON aps.skill_id = vs.skill_id AND vs.vacancy_master_id = :vacancy_id
        WHERE 
            aps.is_deleted = 'no' AND vs.is_deleted = 'no'
        GROUP BY 
            a.applicant_id, a.first_name, a.middle_name, a.last_name;
    """)
    return db.execute(query, {"vacancy_id": vacancy_id}).fetchall()


def fetch_experience_scores(vacancy_id: int, db: Session):
    query = text("""
    SELECT 
        a.applicant_id,
        a.first_name,
        a.middle_name,
        a.last_name,
        SUM(CASE 
            WHEN (DATEDIFF(COALESCE(ae.end_date, NOW()), ae.start_date) / 365) <= 2 THEN 10
            WHEN (DATEDIFF(COALESCE(ae.end_date, NOW()), ae.start_date) / 365) <= 3 THEN 15
            WHEN (DATEDIFF(COALESCE(ae.end_date, NOW()), ae.start_date) / 365) <= 5 THEN 20
            WHEN (DATEDIFF(COALESCE(ae.end_date, NOW()), ae.start_date) / 365) <= 10 THEN 30
            WHEN (DATEDIFF(COALESCE(ae.end_date, NOW()), ae.start_date) / 365) > 10 THEN 40
            ELSE 0 
        END) AS experience_score
    FROM 
        applicant_master a
    JOIN 
        application_master am ON a.applicant_id = am.applicant_id
    LEFT JOIN 
        applicant_experience ae ON a.applicant_id = ae.applicant_id
    WHERE 
        am.vacancy_master_id = :vacancy_id
        AND am.is_deleted = 'no'
        AND (ae.is_deleted = 'no' OR ae.is_deleted IS NULL)
    GROUP BY 
        a.applicant_id, a.first_name, a.middle_name, a.last_name;
    """)
    try:
        result = db.execute(query, {"vacancy_id": vacancy_id}).fetchall()
        experience_data = {
            (row[0], row[1], row[2], row[3]): float(row[4]) if row[4] is not None else 0.0
            for row in result
        }
        return experience_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching experience scores: {str(e)}")

#------------------------------------------------------------------------------------------------
def fetch_qualification_scores(vacancy_id: int, db: Session):
    query = text("""
    SELECT 
        a.applicant_id,
        a.first_name,
        a.middle_name,
        a.last_name,
        SUM(
            CASE 
                WHEN vel.education_level_id = ae.education_level_id THEN vel.weightage ELSE 0 
            END + 
            CASE 
                WHEN ves.education_stream_id = ae.education_stream_id THEN ves.weightage ELSE 0 
            END + 
            CASE 
                WHEN vesc.education_subject_or_course_id = ae.education_subject_or_course_id THEN vesc.weightage ELSE 0 
            END
        ) AS qualification_score
    FROM 
        applicant_educational_qualification ae
    LEFT JOIN 
        applicant_master a ON ae.applicant_id = a.applicant_id
    LEFT JOIN 
        application_master am ON a.applicant_id = am.applicant_id
    LEFT JOIN 
        vacancy_educational_level vel ON vel.vacancy_master_id = am.vacancy_master_id AND vel.education_level_id = ae.education_level_id
    LEFT JOIN 
        vacancy_educational_stream ves ON ves.vacancy_master_id = am.vacancy_master_id AND ves.education_stream_id = ae.education_stream_id
    LEFT JOIN 
        vacancy_educational_subject_or_course vesc ON vesc.vacancy_master_id = am.vacancy_master_id AND vesc.education_subject_or_course_id = ae.education_subject_or_course_id
    WHERE 
        ae.is_deleted = 'no' AND am.vacancy_master_id = :vacancy_id
    GROUP BY 
        a.applicant_id, a.first_name, a.middle_name, a.last_name;
    """)
    try:
        result = db.execute(query, {"vacancy_id": vacancy_id}).fetchall()
        qualification_data = {
            (row[0], row[1], row[2], row[3]): float(row[4]) if row[4] is not None else 0.0
            for row in result
        }
        return qualification_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching qualification scores: {str(e)}")

#----------------------------------------------------------------------------------------------------------
def fetch_language_proficiency_scores(vacancy_id: int, db: Session):
    query = text("""
    SELECT 
        a.applicant_id,
        a.first_name,
        a.middle_name,
        a.last_name,
        SUM(
            CASE
                WHEN vlp.is_read_required = 'yes' AND alp.read_proficiency_id = vlp.language_proficiency_id THEN vlp.read_weightage ELSE 0
            END +
            CASE
                WHEN vlp.is_write_required = 'yes' AND alp.write_proficiency_id = vlp.language_proficiency_id THEN vlp.write_weightage ELSE 0
            END +
            CASE
                WHEN vlp.is_speak_required = 'yes' AND alp.speak_proficiency_id = vlp.language_proficiency_id THEN vlp.speak_weightage ELSE 0
            END
        ) AS language_proficiency_score
    FROM 
        applicant_language_proficiency alp
    LEFT JOIN 
        applicant_master a ON alp.applicant_id = a.applicant_id
    LEFT JOIN 
        application_master am ON alp.applicant_id = am.applicant_id
    LEFT JOIN 
        vacancy_language_proficiency vlp ON vlp.vacancy_master_id = am.vacancy_master_id AND vlp.language_id = alp.language_id
    WHERE 
        alp.is_deleted = 'no' AND am.vacancy_master_id = :vacancy_id
    GROUP BY 
        a.applicant_id, a.first_name, a.middle_name, a.last_name;
    """)
    try:
        result = db.execute(query, {"vacancy_id": vacancy_id}).fetchall()
        language_proficiency_data = {
            (row[0], row[1], row[2], row[3]): float(row[4]) if row[4] is not None else 0.0
            for row in result
        }
        return language_proficiency_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching language proficiency scores: {str(e)}")


#----------------------------------------------------------------------------------------------------------

def calculate_total_scores(vacancy_id: int, db: Session):
    # Fetch individual components
    skills = fetch_skills_scores(vacancy_id, db)
    experience = fetch_experience_scores(vacancy_id, db)
    qualification = fetch_qualification_scores(vacancy_id, db)
    language_proficiency = fetch_language_proficiency_scores(vacancy_id, db)

    # Initialize a list to store applicant score objects
    applicant_scores = []

    # Merge skill scores
    for row in skills:
        applicant_id, first_name, middle_name, last_name, skill_score = row
        applicant = next((a for a in applicant_scores if a["applicant_id"] == applicant_id), None)
        if not applicant:
            applicant = {
                "applicant_id": applicant_id,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "skill_score": 0,
                "experience_score": 0,
                "qualification_score": 0,
                "language_proficiency_score": 0
            }
            applicant_scores.append(applicant)
        applicant["skill_score"] = skill_score

    # Merge experience scores
    for (applicant_id, first_name, middle_name, last_name), experience_score in experience.items():
        applicant = next((a for a in applicant_scores if a["applicant_id"] == applicant_id), None)
        if not applicant:
            applicant = {
                "applicant_id": applicant_id,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "skill_score": 0,
                "experience_score": 0,
                "qualification_score": 0,
                "language_proficiency_score": 0
            }
            applicant_scores.append(applicant)
        applicant["experience_score"] = experience_score

    # Merge qualification /education scores
    for (applicant_id, first_name, middle_name, last_name), qualification_score in qualification.items():
        applicant = next((a for a in applicant_scores if a["applicant_id"] == applicant_id), None)
        if not applicant:
            applicant = {
                "applicant_id": applicant_id,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "skill_score": 0,
                "experience_score": 0,
                "qualification_score": 0,
                "language_proficiency_score": 0
            }
            applicant_scores.append(applicant)
        applicant["qualification_score"] = qualification_score

    # Merge language proficiency scores
    for (applicant_id, first_name, middle_name, last_name), language_proficiency_score in language_proficiency.items():
        applicant = next((a for a in applicant_scores if a["applicant_id"] == applicant_id), None)
        if not applicant:
            applicant = {
                "applicant_id": applicant_id,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "skill_score": 0,
                "experience_score": 0,
                "qualification_score": 0,
                "language_proficiency_score": 0
            }
            applicant_scores.append(applicant)
        applicant["language_proficiency_score"] = language_proficiency_score

    # Calculate the total score for each applicant
    for applicant in applicant_scores:
        total_score = (applicant["skill_score"] + applicant["experience_score"] + 
                       applicant["qualification_score"] + applicant["language_proficiency_score"])
        applicant["total_score"] = total_score

    # Filter out applicants with no score data (if needed)
    applicant_scores = [applicant for applicant in applicant_scores if applicant["total_score"] > 0]

    return {
        "success": "true",
        "data": applicant_scores  # Return data as a list, not a dictionary with IDs
    }

#------------------------------------------------------------------------------------------------


@router.get("/ranked-applicants")
def get_ranked_applicants(
    vacancy_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme),
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    try:
        # Fetch applicants and calculate scores
        ranked_applicants = calculate_total_scores(vacancy_id, db)

        # Ensure the response is a list before sorting
        if isinstance(ranked_applicants, dict):
            ranked_applicants = ranked_applicants.get("data", [])

        # Sort by total_score in descending order
        ranked_applicants = sorted(ranked_applicants, key=lambda x: x["total_score"], reverse=True)

        # Assign ranks and insert into `application_rank_list`
        for idx, applicant in enumerate(ranked_applicants, start=1):
            applicant["rank"] = idx  # Add rank to response

            # Prepare record for insertion
            rank_entry = ApplicationRankList(
                applicant_id=applicant["applicant_id"],
                vacancy_master_id=vacancy_id,
                education_score=applicant.get("qualification_score", 0.0),
                professional_score=0.0,  # Modify based on actual calculation
                experience_score=applicant.get("experience_score", 0.0),
                language_score=applicant.get("language_proficiency_score", 0.0),
                skill_score=applicant.get("skill_score", 0.0),
                interview_score=0.0,  # Modify if applicable
                rank_number=idx,
                total_score=applicant["total_score"],
                # status="Pending",  # Modify based on business logic
                is_deleted="no"
            )

            # Check if the record already exists
            existing_record = db.query(ApplicationRankList).filter_by(
                applicant_id=applicant["applicant_id"],
                vacancy_master_id=vacancy_id
            ).first()

            if existing_record:
                # Update existing record
                existing_record.education_score = rank_entry.education_score
                existing_record.professional_score = rank_entry.professional_score
                existing_record.experience_score = rank_entry.experience_score
                existing_record.language_score = rank_entry.language_score
                existing_record.skill_score = rank_entry.skill_score
                existing_record.interview_score = rank_entry.interview_score
                existing_record.rank_number = rank_entry.rank_number
                existing_record.total_score = rank_entry.total_score
                # existing_record.status = rank_entry.status
            else:
                # Insert new record
                db.add(rank_entry)

        # Update vacancy_status in vacancy_master
        vacancy_record = db.query(VacancyMaster).filter(VacancyMaster.id == vacancy_id).first()

        if vacancy_record:
            vacancy_record.vacancy_status = "RANKLIST_GENERATED"

        # Commit changes to database
        db.commit()

        return {"success": "true", "data": ranked_applicants}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#------------------------------------------------------------------------------------------------
# @router.post("/save_interview_schedule/")
# async def save_interview_schedule(
#     schedules: List[InterviewScheduleRequest],  # List of interview schedules to save
#     db: Session = Depends(get_db),  # Database session dependency
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
#     try:
#         saved_schedules = []
#         for schedule in schedules:
#             # Delegating insert or update logic to save_schedule function
#             saved_schedule = db_employee_master.save_schedule(schedule, db)
#             # Manually convert the SQLAlchemy object to a dictionary
#             saved_schedule_dict = {
#                 "id": saved_schedule.id,
#                 "applicant_id": saved_schedule.applicant_id,
#                 "vacancy_id": saved_schedule.vacancy_id,
#                 "interview_panel_id": saved_schedule.interview_panel_id,
#                 "interview_date": saved_schedule.interview_date,
#                 "interview_time": saved_schedule.interview_time,
#                 "location": saved_schedule.location,
#                 "interview_status": saved_schedule.interview_status,
#                 "remarks": saved_schedule.remarks
#             }
           
#             # Convert dictionary to InterviewScheduleRequest
#             saved_schedules.append(InterviewScheduleRequest(**saved_schedule_dict))
        
#         return {"success": "true", "message": "Schedules saved successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
#-----------------------------------------------------------------------------------------------------
@router.post("/save_interview_panel")
def save_interview_panel_endpoint(
    request: CreateInterviewPanelRequest, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
        # Call the service to save the interview panel data
        response = db_employee_master.save_interview_panel(db, request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while saving the data.")
    
    
# -----------------------------------------------------------------------------------------------------


@router.get("/vacancy_details_for_education/{vacancy_id}")
def get_vacancy_details(vacancy_id: int, 
                        db: Session = Depends(get_db),
                        token: str = Depends(oauth2.oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    # Fetch education levels, streams, and courses for the given vacancy_id
    education_levels = db.query(VacancyEducationalLevel).filter(
        VacancyEducationalLevel.vacancy_master_id == vacancy_id,
        VacancyEducationalLevel.is_deleted == "no"
    ).all()

    education_streams = db.query(VacancyEducationalStream).filter(
        VacancyEducationalStream.vacancy_master_id == vacancy_id,
        VacancyEducationalStream.is_deleted == "no"
    ).all()

    # Assuming we have the correct attribute names for `VacancyEducationalSubjectOrCourse`
    education_courses = db.query(VacancyEducationalSubjectOrCourse).filter(
        VacancyEducationalSubjectOrCourse.vacancy_master_id == vacancy_id,
        VacancyEducationalSubjectOrCourse.is_deleted == "no"
    ).all()

    # Fetch names for levels, streams, and courses
    level_names = db.query(AppEducationalLevel).all()
    stream_names = db.query(AppEducationalStream).all()
    course_names = db.query(AppEducationSubjectCourse).all()

    level_name_dict = {level.id: level.education_level for level in level_names}
    stream_name_dict = {stream.id: stream.education_stream for stream in stream_names}
    course_name_dict = {course.id: course.subject_or_course_name for course in course_names}

    # Step 1: Organize streams by education_level_id using the correct relationship
    stream_dict = {}
    for stream in education_streams:
        education_level_id = db.query(AppEducationalStream.education_level_id).filter(
            AppEducationalStream.id == stream.education_stream_id).scalar()
        stream_dict.setdefault(education_level_id, []).append({
            "id": stream.id,
            "education_stream_id": stream.education_stream_id,
            "education_stream_name": stream_name_dict.get(stream.education_stream_id, ""),
            "weightage": stream.weightage or 0.0,
            "courses": []
        })

    # Step 2: Assign courses to the correct streams
    for course in education_courses:
        education_stream_id = db.query(AppEducationSubjectCourse.education_stream_id).filter(
            AppEducationSubjectCourse.id == course.education_subject_or_course_id).scalar()
        for stream_list in stream_dict.values():
            for stream in stream_list:
                if education_stream_id == stream["education_stream_id"]:
                    stream["courses"].append({
                        "id": course.id,
                        "education_subject_or_course_id": course.education_subject_or_course_id or 0,
                        "education_subject_or_course_name": course_name_dict.get(course.education_subject_or_course_id, ""),
                        "weightage": course.weightage or 0.0
                    })

    # Step 3: Organize education levels with nested streams
    education_data = []
    for level in education_levels:
        education_data.append({
            "id": level.id,
            "education_level_id": level.education_level_id,
            "education_level_name": level_name_dict.get(level.education_level_id, ""),
            "weightage": level.weightage or 0.0,
            "streams": stream_dict.get(level.education_level_id, [])
        })

    # Step 4: Construct the response as a plain dictionary
    response_data = {
        "id": vacancy_id,
        "education": {
            "levels": education_data
        }
    }

    return response_data


#----------------------------------------------------------------------------------------------


@router.post("/save_interview_schedule/")
def save_schedule(request: InterviewScheduleRequest, 
                  db: Session = Depends(get_db),
                  token: str = Depends(oauth2.oauth2_scheme)):
    """
    Save or update interview schedules.

    This endpoint allows users to create new interview schedules or update existing ones 
    for a given vacancy. It also performs a soft delete for schedules that are missing 
    from the request.

    ### Request Body:
    ```json
    {
      "schedules": [
        {
          "id": 0,
          "applicant_id": 100,
          "vacancy_id": 50,
          "interview_panel_id": 1,
          "interview_date": "2025-02-19T07:51:26.050Z",
          "interview_time": "2025-02-19T07:51:26.050Z",
          "location": "kochi",
          "remarks": "SSSS"
        }
      ]
    }
    ```

    ### Request Parameters:
    - `id` (int): `0` for new records, otherwise the existing schedule ID.
    - `applicant_id` (int): ID of the applicant being scheduled.
    - `vacancy_id` (int, required): The vacancy ID for which the interview is scheduled.
    - `interview_panel_id` (int): The ID of the interview panel.
    - `interview_date` (str, ISO 8601 format): The date of the interview.
    - `interview_time` (str, ISO 8601 format): The time of the interview.
    - `location` (str): The location where the interview will take place.
    - `remarks` (str, optional): Additional notes for the interview.

    ### Response:
    - **Success** (`200 OK`):
    ```json
    {
      "success": "true",
      "message": "Interview schedules saved successfully"
    }
    ```
    - **Failure** (`400 Bad Request` / `500 Internal Server Error`):
    ```json
    {
      "success": "false",
      "message": "Error: <detailed error message>"
    }
    ```

    ### Logic:
    - If `id = 0`, a new schedule is inserted.
    - If `id > 0`, an existing schedule is updated.
    - Any existing schedules in the database that are not in the request are marked as deleted (`is_deleted = "yes"`).

    ### Errors:
    - Returns `"Vacancy ID is required"` if no schedules are provided.
    - Returns `"Error: <detailed message>"` if any unexpected database or server error occurs.

    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    try:
        # Step 1: Validate Vacancy ID
        vacancy_id = request.schedules[0].vacancy_id if request.schedules else None
        if not vacancy_id:
            raise HTTPException(status_code=400, detail="Vacancy ID is required")

        # Step 2: Fetch Existing Schedules for Vacancy
        existing_schedules = db.query(InterviewSchedule).filter(
            InterviewSchedule.vacancy_id == vacancy_id,
            InterviewSchedule.is_deleted == "no"
        ).all()

        # Step 3: Create a lookup dictionary {applicant_id -> existing schedule}
        existing_schedule_map = {s.applicant_id: s for s in existing_schedules}

        # Step 4: Extract applicant IDs from the request
        new_applicant_ids = {schedule.applicant_id for schedule in request.schedules}

        # Step 5: Insert or Update Logic
        for schedule in request.schedules:
            if schedule.id == 0:
                # 🟢 Insert New Record
                new_schedule = InterviewSchedule(
                    applicant_id=schedule.applicant_id,
                    vacancy_id=schedule.vacancy_id,
                    interview_panel_id=schedule.interview_panel_id,
                    interview_date=schedule.interview_date,
                    interview_time=schedule.interview_time,
                    location=schedule.location,
                    interview_status="SCHEDULED",
                    remarks=schedule.remarks,
                    is_deleted="no",
                )
                db.add(new_schedule)
                db.flush()  # Ensure ID is generated
                db.refresh(new_schedule)  # Refresh the object with DB values

            else:
                # 🟡 Update Existing Record
                existing_schedule = db.query(InterviewSchedule).filter(
                    InterviewSchedule.id == schedule.id
                ).first()
                
                if existing_schedule:
                    existing_schedule.interview_panel_id = schedule.interview_panel_id
                    existing_schedule.interview_date = schedule.interview_date
                    existing_schedule.interview_time = schedule.interview_time
                    existing_schedule.location = schedule.location
                    existing_schedule.interview_status = "RESCHEDULED"  # Fixed Typo
                    existing_schedule.remarks = schedule.remarks

        # Step 6: Mark Missing Applicants as Deleted (Soft Delete)
        for applicant_id, schedule in existing_schedule_map.items():
            if applicant_id not in new_applicant_ids:
                schedule.is_deleted = "yes"

        # Step 7: Commit Changes
        db.commit()
        return {"success": "true", "message": "Interview schedules saved successfully"}

    except Exception as e:
        db.rollback()
        return {"success": "false", "message": f"Error: {str(e)}"}

#--------------------------------------------------------------------------------------------------
# Query	Join Type	Purpose
# Scheduled Applicants	INNER JOIN	Only returns applicants who have interviews scheduled
# Not Scheduled Applicants	LEFT JOIN with WHERE isch.applicant_id IS NULL	Returns applicants who do NOT have interviews scheduled




#--------------------------------------------------------------------------------------------------

@router.get("/get_applicants_status/{vacancy_id}")
def get_applicants_status(vacancy_id: int, 
                          db: Session = Depends(get_db),
                          token: str = Depends(oauth2.oauth2_scheme)):
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    # Applicants whose interviews are scheduled
    scheduled_applicants = db.execute(text("""
        SELECT ar.*, 
               am.first_name, 
               am.middle_name, 
               am.last_name
        FROM application_rank_list ar
        INNER JOIN interview_schedule isch 
            ON ar.applicant_id = isch.applicant_id 
            AND ar.vacancy_master_id = isch.vacancy_id
            AND isch.is_deleted = 'no'
        INNER JOIN applicant_master am 
            ON ar.applicant_id = am.applicant_id
        WHERE ar.vacancy_master_id = :vacancy_id
        AND am.is_deleted = 'no'
    """), {"vacancy_id": vacancy_id}).mappings().all()

    # Applicants whose interviews are NOT scheduled
    not_scheduled_applicants = db.execute(text("""
        SELECT ar.*, 
               am.first_name, 
               am.middle_name, 
               am.last_name
        FROM application_rank_list ar
        LEFT JOIN interview_schedule isch 
            ON ar.applicant_id = isch.applicant_id 
            AND ar.vacancy_master_id = isch.vacancy_id
            AND isch.is_deleted = 'no'
        INNER JOIN applicant_master am 
            ON ar.applicant_id = am.applicant_id
        WHERE ar.vacancy_master_id = :vacancy_id
        AND isch.applicant_id IS NULL
        AND am.is_deleted = 'no'
    """), {"vacancy_id": vacancy_id}).mappings().all()

    return {
        "scheduled_applicants": list(scheduled_applicants),  
        "not_scheduled_applicants": list(not_scheduled_applicants)
    }

#--------------------------------------------------------------------------------------------------



@router.get("/get_scheduled_candidates/{vacancy_id}", response_model=List[ScheduledCandidate])
def get_scheduled_candidates_endpoint(vacancy_id: int, db: Session = Depends(get_db)):
    candidates = db_employee_master.get_scheduled_candidates(db, vacancy_id)
    return candidates 