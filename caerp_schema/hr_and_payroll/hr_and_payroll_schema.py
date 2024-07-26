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
   # next_increment_date : Optional[date] = None
   nationality_id : int
       
   class config():
      orm_mode=True

class EmployeeMasterDisplay(BaseModel):
   
   employee_id :int
   employee_number : str
   first_name : str
   middle_name : Optional[str] = None
   last_name : str
   gender_id : int
   blood_group : Optional[str] = None
   marital_status_id : int
   date_of_birth : date
   joining_date : date
   # next_increment_date : Optional[date] = None
   nationality_id : int
   # created_by : int
   # created_on : datetime
   is_approved : str = 'no'
   approved_by : int
   approved_on : datetime
   # modified_by : Optional[int] = None
   # modified_on : Optional[datetime] = None
   # is_deleted : str = 'no'
   # deleted_by : Optional[int] = None
   # deleted_on : Optional[datetime]

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
   # effective_from_date : date
   # effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True

class EmployeePresentAddressGet(BaseModel):
   id:int
   employee_id : int
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
   # created_by : int
   # created_on : datetime
   is_deleted : str = 'no'
   # deleted_by : Optional[int] = None
   # deleted_on : Optional[datetime] = None

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
   # effective_from_date : date
   # effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True


class EmployeePermanentAddressGet(BaseModel):
   id:int
   employee_id : int    
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
   # created_by : int
   # created_on : datetime
   is_deleted : str = 'no'
   # deleted_by : Optional[int] = None
   # deleted_on : Optional[datetime] = None

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
   # effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None
    
   class config():
      orm_mode=True


class EmployeeContactGet(BaseModel):
   id:int
   employee_id : int
   personal_mobile_number : Optional[str] = None
   personal_whatsapp_number : Optional[str] = None
   personal_email_id : Optional[str] = None
   official_mobile_number : Optional[str] = None
   official_whatsapp_number : Optional[str] = None
   official_email_id : Optional[str] = None
   effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
   # created_by : int
   # created_on : datetime
   is_deleted : str = 'no'
   # deleted_by : Optional[int] = None
   # deleted_on : Optional[datetime] = None
    
   class config():
      orm_mode=True


class EmployeeBankAccountSchema(BaseModel):
   # employee_id : int
   bank_account_number : Optional[str] = None
   bank_name :  Optional[str] = None
   bank_branch_name : Optional[str] = None
   ifsc_code : Optional[str] = None
   # effective_from_date : date
   # effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
#    created_by : int
#    created_on : datetime
#    is_deleted : str = 'no'
#    deleted_by : Optional[int] = None
#    deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True     


class EmployeeBankAccountGet(BaseModel):
   id:int
   employee_id : int
   bank_account_number : Optional[str] = None
   bank_name :  Optional[str] = None
   bank_branch_name : Optional[str] = None
   ifsc_code : Optional[str] = None
   effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None
   # created_by : int
   # created_on : datetime
   is_deleted : str = 'no'
   # deleted_by : Optional[int] = None
   # deleted_on : Optional[datetime] = None

   class config():
      orm_mode=True 


class EmployeeEmployementSchema(BaseModel):
   # employee_id : int
   department_id : int
   designation_id : int
   employee_category_id : int
   is_consultant : str = 'no'
   # effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None


   class config():
      orm_mode=True


class EmployeeEmployementGet(BaseModel):
   id:int
   employee_id : int
   department_id : int
   designation_id : int
   employee_category_id : int
   is_consultant : str = 'no'
   effective_from_date : date
   effective_to_date : Optional[date] = None
   remarks : Optional[str] = None

   class config():
      orm_mode=True



class EmployeeEducationalQualficationGet(BaseModel):
   id:Optional[int]=None,
   employee_id : int
   qualification_name : Optional[str] = None
   institution : Optional[str] = None
   percentage_or_grade : Optional[str] = None
   month_and_year_of_completion : Optional[str] = None   
   is_deleted : str = 'no'


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
   # effective_from_date : date
   effective_to_date : Optional[date] = None
   next_increment_date : Optional[date] = None

   class config():
      orm_mode=True


class EmployeeSalaryGet(BaseModel):
   id:int
   employee_id : int         
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





class EmployeeExperienceGet(BaseModel):
   id:int
   employee_id : int
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
   issued_by : Optional[str] = None
   remarks : Optional[str] = None

   class config():
      orm_mode=True


class EmployeeDocumentsGet(BaseModel):
   id:int
   employee_id : int
   document_id : int
   document_number : Optional[str] = None
   issue_date : date
   expiry_date : Optional[date] = None
   issued_by : Optional[str] = None
   remarks : Optional[str] = None

   class config():
      orm_mode=True



class EmployeeEmergencyContactSchema(BaseModel):
   # employee_id : int
   contact_person_name : Optional[str] = None
   relation_id : int
   gender_id : int
   mobile_number : str
   # effective_date_from : date
   effective_date_to : Optional[date] = None

   class config():
      orm_mode=True



class EmployeeEmergencyContactGet(BaseModel):
   id:int
   employee_id : int
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
   # effective_date_from : date
   effective_date_to : Optional[date] = None

   class config():
      orm_mode=True


class EmployeeDependentsGet(BaseModel):
   id:int
   employee_id : int
   dependent_name : Optional[str] = None
   relation_id : int
   gender_id : int
   date_of_birth : Optional[date] = None
   effective_date_from : date
   effective_date_to : Optional[date] = None

   class config():
      orm_mode=True      


  
         

class EmployeeProfessionalQualificationGet(BaseModel):
   id:int
   employee_id : int
   qualification_id : int
   membership_number : Optional[str] = None
   enrollment_date : date      
  


class EmployeeSecurityCredentials(BaseModel):
    user_name           : str
    login_password      : str
    edit_password       : Optional[str]=None
    delete_password     : Optional[str]=None
    security_password   : Optional[str]=None
   #  role_ids            : List[int]

class EmployeeSecurityCredentialsGet(BaseModel):
    id:int
    employee_id         : int  
    user_name           : str
    login_password      : str
    edit_password       : Optional[str]=None
    delete_password     : Optional[str]=None
    security_password   : Optional[str]=None
   #  role_ids            : List[int]   



class EmployeeUserRoles(BaseModel):
   role_id            : list[int] 


class EmployeeUserRolesGet(BaseModel):
   id:int
   employee_id        : int
   role_id            : int



class EmployeeEducationalQualficationSchema(BaseModel):
    id: Optional[int] = None
    qualification_name: Optional[str] = None
    institution: Optional[str] = None
    percentage_or_grade: Optional[str] = None
    month_and_year_of_completion: Optional[str] = None

    class Config:
        orm_mode = True

class EmployeeExperienceSchema(BaseModel):
    id: Optional[int] = None
    position_held: str
    company_name: str
    responsibilty: str
    start_date: date
    end_date: date

    class Config:
        orm_mode = True

class EmployeeProfessionalQualificationSchema(BaseModel):
    id: Optional[int] = None
    qualification_id: int
    membership_number: Optional[str] = None
    enrollment_date: date

class EmployeeDetailsCombinedSchema(BaseModel):
    educational_qualifications: Optional[List[EmployeeEducationalQualficationSchema]] = None
    experiences: Optional[List[EmployeeExperienceSchema]] = None
    professional_qualifications: Optional[List[EmployeeProfessionalQualificationSchema]] = None

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
   employee_security_credentials: Optional[EmployeeSecurityCredentials] = None
   user_roles: Optional[EmployeeUserRoles] = None


class EmployeeDetailsGet(BaseModel):
   employee_master :   Optional[EmployeeMasterDisplay] = None
   present_address :   Optional[EmployeePresentAddressGet] = None
   permanent_address : Optional[EmployeePermanentAddressGet] = None
   contact_details :   Optional[EmployeeContactGet] = None
   bank_details :      Optional[EmployeeBankAccountGet] = None
   employement_details : Optional[EmployeeEmployementGet] = None
   emergency_contact_details : Optional[EmployeeEmergencyContactGet] = None
   dependent_details : Optional[EmployeeDependentsGet] = None
   employee_salary : Optional[EmployeeSalaryGet] = None
   educational_qualification : List[EmployeeEducationalQualficationGet] = None
   employee_experience : List[EmployeeExperienceGet] = None
   employee_documents : List[EmployeeDocumentsGet] = None
   professional_qualification : List[EmployeeProfessionalQualificationGet] = None
   employee_security_credentials: Optional[EmployeeSecurityCredentialsGet] = None
   user_roles: List[EmployeeUserRolesGet] = None   


class EmployeeAddressDetailsSchema(BaseModel):
   present_address: Optional[List[EmployeePresentAddressSchema]] = None
   permanent_address: Optional[List[EmployeePermanentAddressSchema]] = None
   bank_details: Optional[List[EmployeeBankAccountSchema]] = None
