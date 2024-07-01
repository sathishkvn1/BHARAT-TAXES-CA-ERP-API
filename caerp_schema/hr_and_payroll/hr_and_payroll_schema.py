from enum import Enum
from pydantic import BaseModel, validator
from typing import List,Optional, Union,Dict
from datetime import date, datetime
from caerp_constants.caerp_constants import BooleanFlag


class EmployeeMasterSchema(BaseModel):
   # employee_id : int
   employee_number : Optional[str] = None
   first_name : str
   middle_name : Optional[str] = None
   last_name : str
   gender_id : int
   blood_group : Optional[str] = None
   marital_status_id : int
   date_of_birth : date
   joining_date : date
   next_increment_date : date
   nationality_id : int
    
   class config():
      orm_mode=True
    
class EmployeeMasterSchemaNew(BaseModel):
   # employee_id : int
   employee_number : Optional[str] = None
   first_name : str
   middle_name : Optional[str] = None
   last_name : str
   gender_id : int
   blood_group : Optional[str] = None
   marital_status_id : int
   date_of_birth : date
   joining_date : date
   next_increment_date : date
   nationality_id : int
   # personal_mobile_number : Optional[str] = None
   # personal_email_id : Optional[str] = None
   # user_name: str
   # login_password: str
   # role_ids  :  List[int]
    
   class config():
      orm_mode=True

class EmployeeMasterDisplay(BaseModel):
   employee_id :int
   employee_number : str
   first_name : str
   middle_name : str
   last_name : str
   gender_id : int
   blood_group : str
   marital_status_id : int
   date_of_birth : date
   joining_date : date
   next_increment_date : date
   nationality_id : int
   created_by : int
   created_on : datetime
   is_approved : str = 'no'
   approved_by : int
   approved_on : datetime
   modified_by : Optional[int] = None
   modified_on : Optional[datetime] = None
   is_deleted : str = 'no'
   deleted_by : Optional[int] = None
   deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True



class EmployeePresentAddressSchema(BaseModel):
   # employee_id : int
   present_house_or_flat_name : Optional[str] = None
   present_house_flat_or_door_number : Optional[str] = None
   present_road_name : Optional[str] = None
   present_street_name : Optional[str] = None
   present_land_mark : Optional[str] = None
   present_pin_code : Optional[str] = None
   present_post_office_id : int
   present_city_id : int
   present_taluk_id : int
   present_district_id : int
   present_state_id : int
   present_country_id : int
   effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True



class EmployeePermanentAddressSchema(BaseModel):   
   # employee_id : int    
   permanent_house_or_flat_name : Optional[str] = None
   permanent_house_flat_or_door_number : Optional[str] = None
   permanent_road_name : Optional[str] = None
   permanent_street_name : Optional[str] = None
   permanent_land_mark : Optional[str] = None
   permanent_pin_code : Optional[str] = None
   permanent_post_office_id : int
   permanent_city_id : int
   permanent_taluk_id : int
   permanent_district_id : int
   permanent_state_id : int
   permanent_country_id : int     
   effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True



class EmployeeContactSchema(BaseModel):
   # employee_id : int
   personal_mobile_number : Optional[str] = None
   personal_whatsapp_number : Optional[str] = None
   personal_email_id : Optional[str] = None
   official_mobile_number : Optional[str] = None
   official_whatsapp_number : Optional[str] = None
   official_email_id : Optional[str] = None
   effective_from_date : Optional[date] =None
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None
    
   class config():
      orm_mode=True



class EmployeeBankAccountSchema(BaseModel):
   # employee_id : int
   bank_account_number : Optional[str] = None
   bank_name :  Optional[str] = None
   bank_branch_name : Optional[str] = None
   ifsc_code : Optional[str] = None
   effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True     



class EmployeeEmployementSchema(BaseModel):
   # employee_id : int
   department_id : int
   designation_id : int
   employee_category_id : int
   is_consultant : str = 'no'
   effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_approved : str = 'no'
#    approved_by : int
#    approved_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True



class EmployeeEducationalQualficationSchema(BaseModel):
   # employee_id : int
   qualification_name : Optional[str] = None
   institution : Optional[str] = None
   percentage_or_grade : Optional[str] = None
   month_and_year_of_completion : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True



class EmployeeSalarySchema(BaseModel):
   # employee_id : int         
   component_id : int
   calculation_frequency_id : int
   calculation_method_id : int
   amount : float
   percentage_of_component_id : Optional[int] = None
   percentage : float
   effective_from_date : date
   effective_to_date : Optional[date] = None
   next_increment_date : Optional[date] = None

   class config():
      orm_mode=True


class EmployeeExperienceSchema(BaseModel):
   # employee_id : int
   position_held : str
   company_name : str
   responsibilty : str
   start_date : date
   end_date : date

   class config():
      orm_mode=True


class EmployeeDocumentsSchema(BaseModel):
   # employee_id : int
   document_id : int
   document_number : Optional[str] = None
   issue_date : date
   expiry_date : Optional[date] = None
   remarks : Optional[str] = None

   class config():
      orm_mode=True


class EmployeeEmergencyContactSchema(BaseModel):
   # employee_id : int
   contact_person_name : Optional[str] = None
   relation_id : int
   gender_id : int
   mobile_number : str
   effective_date_from : date
   effective_date_to : Optional[date] = None

   class config():
      orm_mode=True


class EmployeeDependentsSchema(BaseModel):
   # employee_id : int
   dependent_name : Optional[str] = None
   relation_id : int
   gender_id : int
   date_of_birth : Optional[date] = None
   effective_date_from : date
   effective_date_to : Optional[date] = None

   class config():
      orm_mode=True

class EmployeeProfessionalQualificationSchema(BaseModel):
   id: Optional[int]
   qualification_id : int
   membership_number : Optional[str] = None
   enrollment_date : date      
   #is_deleted : str = 'no'
      
class EmployeeSecurityCredentials(BaseModel):

    user_name           : str
    login_password      : str
    edit_password       : Optional[str]=None
    delete_password     : Optional[str]=None
    security_password   : Optional[str]=None
   #  role_ids            : List[int]

class EmployeeUserRoles(BaseModel):
    
    role_id            : list[int] 

class EmployeeDetails(BaseModel):
   employee_master :   Optional[EmployeeMasterSchema] = None
   present_address :   Optional[EmployeePresentAddressSchema] = None
   permanent_address : Optional[EmployeePermanentAddressSchema] = None
   contact_details :   Optional[EmployeeContactSchema] = None
   bank_details :      Optional[EmployeeBankAccountSchema] = None
   employement_details : Optional[EmployeeEmployementSchema] = None
   emergency_contact_details : Optional[EmployeeEmergencyContactSchema] = None
   dependent_details : Optional[EmployeeDependentsSchema] = None
   employee_salary : Optional[EmployeeSalarySchema] = None
   educational_qualification : List[EmployeeEducationalQualficationSchema] = None
   employee_experience : List[EmployeeExperienceSchema] = None
   employee_documents : List[EmployeeDocumentsSchema] = None
   professional_qualification : List[EmployeeProfessionalQualificationSchema] = None

   

class EmployeeDetailsNew(BaseModel):
   employee_master :   Optional[EmployeeMasterSchemaNew] = None
   present_address :   Optional[EmployeePresentAddressSchema] = None
   permanent_address : Optional[EmployeePermanentAddressSchema] = None
   contact_details :   Optional[EmployeeContactSchema] = None
   bank_details :      Optional[EmployeeBankAccountSchema] = None
   employement_details : Optional[EmployeeEmployementSchema] = None
   emergency_contact_details : Optional[EmployeeEmergencyContactSchema] = None
   dependent_details : Optional[EmployeeDependentsSchema] = None
   employee_salary : Optional[EmployeeSalarySchema] = None
   educational_qualification : List[EmployeeEducationalQualficationSchema] = None
   employee_experience : List[EmployeeExperienceSchema] = None
   employee_documents : List[EmployeeDocumentsSchema] = None
   professional_qualification : List[EmployeeProfessionalQualificationSchema] = None
   employee_security_credentials: Optional[EmployeeSecurityCredentials]=None
   user_roles: Optional[EmployeeUserRoles]=None