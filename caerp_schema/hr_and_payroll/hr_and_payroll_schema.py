from enum import Enum
from pydantic import BaseModel, validator
from typing import List,Optional, Union,Dict
from datetime import date, datetime, time
from caerp_constants.caerp_constants import BooleanFlag

   
class EmployeeMasterSchema(BaseModel):
    # employee_id            : int
    employee_number        : Optional[str] = None
    first_name             : str
    middle_name            : Optional[str] = None
    last_name              : str
    gender_id              : int
    blood_group            : Optional[str] = None
    marital_status_id      : int
    date_of_birth          : date
    joining_date           : date
    # next_increment_date   : Optional[date] = None
    nationality_id         : int

    class Config:  # Corrected class name to 'Config'
        orm_mode = True


class EmployeeMasterDisplay(BaseModel):
    employee_id            : int
    employee_number        : str
    first_name             : str
    middle_name            : Optional[str] = None
    last_name              : str
    gender_id              : int
    blood_group            : Optional[str] = None
    marital_status_id      : int
    date_of_birth          : date
    joining_date           : date

    nationality_id         : int
    is_approved            : str = 'no'
    approved_by            : int
    approved_on            : datetime

    class Config:  # Corrected class name to 'Config'
        orm_mode = True



class EmployeePresentAddressSchema(BaseModel):
    # employee_id                  : int
    present_house_or_flat_name   : Optional[str] = None
    present_house_flat_or_door_number : Optional[str] = None
    present_road_name            : Optional[str] = None
    present_street_name          : Optional[str] = None
    present_land_mark           : Optional[str] = None
    present_pin_code            : Optional[str] = None
    present_post_office_id      : int
    present_city_id            : int
    present_taluk_id           : int
    present_district_id        : int
    present_state_id           : int
    present_country_id         : int

    remarks                     : Optional[str] = None
   
    class Config:  
        orm_mode = True


class EmployeePresentAddressGet(BaseModel):
    id                          : int
    employee_id                 : int
    present_house_or_flat_name  : Optional[str] = None
    present_house_flat_or_door_number : Optional[str] = None
    present_road_name           : Optional[str] = None
    present_street_name         : Optional[str] = None
    present_land_mark           : Optional[str] = None
    present_pin_code            : Optional[str] = None
    present_post_office_id      : int
    present_city_id             : int
    present_taluk_id            : int
    present_district_id         : int
    present_state_id            : int
    present_country_id          : int
    remarks                     : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True



class EmployeePermanentAddressSchema(BaseModel):
    permanent_house_or_flat_name     : Optional[str] = None
    permanent_house_flat_or_door_number : Optional[str] = None
    permanent_road_name              : Optional[str] = None
    permanent_street_name            : Optional[str] = None
    permanent_land_mark             : Optional[str] = None
    permanent_pin_code              : Optional[str] = None
    permanent_post_office_id        : int
    permanent_city_id               : int
    permanent_taluk_id              : int
    permanent_district_id           : int
    permanent_state_id              : int
    permanent_country_id            : int
    remarks                         : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True



class EmployeePermanentAddressGet(BaseModel):
    id                           : int
    employee_id                  : int
    permanent_house_or_flat_name : Optional[str] = None
    permanent_house_flat_or_door_number : Optional[str] = None
    permanent_road_name          : Optional[str] = None
    permanent_street_name        : Optional[str] = None
    permanent_land_mark          : Optional[str] = None
    permanent_pin_code           : Optional[str] = None
    permanent_post_office_id     : int
    permanent_city_id            : int
    permanent_taluk_id           : int
    permanent_district_id        : int
    permanent_state_id           : int
    permanent_country_id         : int
    remarks                      : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True


class EmployeeContactSchema(BaseModel):
    # employee_id                  : int
    personal_mobile_number       : Optional[str] = None
    personal_whatsapp_number     : Optional[str] = None
    personal_email_id            : Optional[str] = None
    official_mobile_number       : Optional[str] = None
    official_whatsapp_number     : Optional[str] = None
    official_email_id            : Optional[str] = None
    remarks                      : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True



class EmployeeContactGet(BaseModel):
    id                          : int
    employee_id                 : int
    personal_mobile_number      : Optional[str] = None
    personal_whatsapp_number    : Optional[str] = None
    personal_email_id           : Optional[str] = None
    official_mobile_number      : Optional[str] = None
    official_whatsapp_number    : Optional[str] = None
    official_email_id           : Optional[str] = None
    remarks                     : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True


class EmployeeBankAccountSchema(BaseModel):
    # employee_id                : int
    bank_account_number        : Optional[str] = None
    bank_name                  : Optional[str] = None
    bank_branch_name           : Optional[str] = None
    ifsc_code                  : Optional[str] = None
    remarks                    : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True
  


class EmployeeBankAccountGet(BaseModel):
    id                         : int
    employee_id                : int
    bank_account_number        : Optional[str] = None
    bank_name                  : Optional[str] = None
    bank_branch_name           : Optional[str] = None
    ifsc_code                  : Optional[str] = None
    remarks                    : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True


class EmployeeEmployementSchema(BaseModel):
   
    department_id              : int
    designation_id             : int
    employee_category_id       : int
    is_consultant              : str = 'no'
 
    effective_to_date          : Optional[date] = None
    remarks                    : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True


class EmployeeEmployementGet(BaseModel):
    id                        : int
    employee_id               : int
    department_id             : int
    designation_id            : int
    employee_category_id      : int
    is_consultant             : str = 'no'
    # effective_from_date     : date
    # effective_to_date       : Optional[date] = None
    remarks                   : Optional[str] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True




class EmployeeEducationalQualficationGet(BaseModel):
    id                             : int
    employee_id                    : int
    education_level_id             : int
    education_level                : str
    education_stream_id            : int
    education_stream               : str
    education_subject_or_course_id :int
    education_subject_or_course    : str
    institution                    : str
    percentage_or_grade            : str
    month_and_year_of_completion   : str
    status                         : Optional[str] = None
    remarks                        : Optional[str] = None
    class Config:  
        orm_mode = True



class EmployeeSalarySchema(BaseModel):
       
   component_id              : int
   calculation_frequency_id  : int
   calculation_method_id     : int
   amount                    : float
   percentage_of_component_id: Optional[int] = None
   percentage                : float
   effective_from_date       : date
   effective_to_date         : Optional[date] = None
   next_increment_date       : Optional[date] = None

   class config():
      orm_mode=True


class EmployeeSalaryGet(BaseModel):
    salary_id                  : int
    employee_id                : Optional[int]
    employee_first_name        : Optional[str]
    employee_middle_name       : Optional[str]
    employee_last_name         : Optional[str]
    component_id               : Optional[int]
    salary_component_name      : Optional[str]
    salary_component_type      : Optional[str]
    calculation_frequency_id   : Optional[int]
    calculation_frequency_name : Optional[str]
    calculation_method_id      : Optional[int]
    calculation_method_name    : Optional[str]
    amount                     : Optional[float]
    percentage_of_component_id : Optional[int]
    percentage_component_name  : Optional[str]
    percentage                 : Optional[float]
    effective_from_date        : Optional[date]
    effective_to_date          : Optional[date]
    next_increment_date        : Optional[date]
    
    class Config:
        orm_mode = True



class EmployeeExperienceGet(BaseModel):
    id                     : int
    employee_id            : int
    position_held          : str
    company_name           : str
    company_address        : str
    company_contact_number : str
    company_email          : Optional[str] = None
    position_held          : str
    responsibility         : str
    start_date             : date
    end_date               : Optional[date]
    remarks                : Optional[str] = None
   
    class Config:
        orm_mode           = True


class EmployeeDocumentsSchema(BaseModel):
    document_id      : int
    document_number  : Optional[str] = None
    issue_date       : date
    expiry_date      : Optional[date] = None
    issued_by        : Optional[str] = None
    remarks          : Optional[str] = None

    class Config:  
        orm_mode = True


class EmployeeDocumentsGet(BaseModel):
    id              : int
    employee_id     : int
    document_id     : int
    document_number : Optional[str] = None
    issue_date      : date
    expiry_date     : Optional[date] = None
    issued_by       : Optional[str] = None
    remarks         : Optional[str] = None

    class Config: 
        orm_mode = True



class EmployeeEmergencyContactSchema(BaseModel):
    contact_person_name : Optional[str] = None
    relation_id         : int
    gender_id           : int
    mobile_number       : str
    effective_date_to   : Optional[date] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True




class EmployeeEmergencyContactGet(BaseModel):
    id                    : int
    employee_id           : int
    contact_person_name   : Optional[str] = None
    relation_id           : int
    gender_id             : int
    mobile_number         : str
    effective_date_from   : date
    effective_date_to     : Optional[date] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True
    


class EmployeeDependentsSchema(BaseModel):
    dependent_name        : Optional[str] = None
    relation_id           : int
    gender_id             : int
    date_of_birth         : Optional[date] = None
    effective_date_to     : Optional[date] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True


class EmployeeDependentsGet(BaseModel):
    id                    : int
    employee_id           : int
    dependent_name        : Optional[str] = None
    relation_id           : int
    gender_id             : int
    date_of_birth         : Optional[date] = None
    effective_date_from   : date
    effective_date_to     : Optional[date] = None

    class Config:  # Corrected class name to 'Config'
        orm_mode = True

class EmployeeProfessionalQualificationGet(BaseModel):
    id                           : int
    employee_id                  : int
    qualification_id             : int
    qualification_name           : str
    institution                  : Optional[str] = None
    membership_number            : Optional[str] = None
    enrollment_date              : date
    percentage_or_grade          : Optional[str] = None
    month_and_year_of_completion : Optional[str] = None
    status                       : Optional[str] = None
    remarks                      : Optional[str] = None
    
    class Config: 
        orm_mode = True



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
    id                             : Optional[int] = None
    education_level_id             : int
    education_stream_id            : int
    education_subject_or_course_id :int
    institution                    : str
    percentage_or_grade            : str
    month_and_year_of_completion   : str
    status                         :  Optional[str] = None
    remarks                        : Optional[str] = None

    class Config:
        orm_mode = True


class EmployeeExperienceSchema(BaseModel):
    id                     : Optional[int] = None
    position_held          : str
    company_name           : str
    company_address        : str
    company_contact_number : str
    company_email          : Optional[str] = None
    position_held          : str
    responsibility         : str
    start_date             : date
    end_date               : Optional[date]=None
    remarks                : Optional[str] = None
   
    class Config:
        orm_mode           = True



class EmployeeProfessionalQualificationSchema(BaseModel):
    id                           : Optional[int]      = None
    qualification_id             : int
    institution                  : Optional[str] = None
    membership_number            : Optional[str] = None
    enrollment_date              : date
    percentage_or_grade          : Optional[str] = None
    month_and_year_of_completion : Optional[str] = None
    status                       : Optional[str] = None
    remarks                      : Optional[str] = None
    
    class Config:
        orm_mode           = True  



class EmployeeDetailsCombinedSchema(BaseModel):
    educational_qualifications   : Optional[List[EmployeeEducationalQualficationSchema]] = None
    experiences                  : Optional[List[EmployeeExperienceSchema]] = None
    professional_qualifications  : Optional[List[EmployeeProfessionalQualificationSchema]] = None

class EmployeeDetails(BaseModel):
   employee_master            :   Optional[EmployeeMasterSchema]     = None
   present_address            :   Optional[EmployeePresentAddressSchema] = None
   permanent_address          : Optional[EmployeePermanentAddressSchema] = None
   contact_details            :   Optional[EmployeeContactSchema] = None
   bank_details               :      Optional[EmployeeBankAccountSchema] = None
   employement_details        : Optional[EmployeeEmployementSchema] = None
   emergency_contact_details  : Optional[EmployeeEmergencyContactSchema] = None
   dependent_details          : Optional[EmployeeDependentsSchema] = None
   employee_salary            : Optional[EmployeeSalarySchema] = None
   educational_qualification  : List[EmployeeEducationalQualficationSchema] = None
   employee_experience        : List[EmployeeExperienceSchema] = None
   employee_documents         : List[EmployeeDocumentsSchema] = None
   professional_qualification : List[EmployeeProfessionalQualificationSchema] = None
   employee_security_credentials : Optional[EmployeeSecurityCredentials] = None
   user_roles                    : Optional[EmployeeUserRoles] = None


class EmployeeLanguageProficiencyGet(BaseModel):
   
    id                      : int
    employee_id             : int
    language_id             : int
    language                : str
    read_proficiency_id     : int
    read_proficiency_level  : str
    write_proficiency_id    : int
    write_proficiency_level : str
    speak_proficiency_id    : int
    speak_proficiency_level : str
    remarks                 : Optional[str] =None

    class Config:
        orm_mode = True


class EmployeeDetailsGet(BaseModel):
  
   employee_master         :   Optional[EmployeeMasterDisplay] = None
   present_address         :   Optional[EmployeePresentAddressGet] = None
   permanent_address       : Optional[EmployeePermanentAddressGet] = None
   contact_details         :   Optional[EmployeeContactGet] = None
   bank_details            :      Optional[EmployeeBankAccountGet] = None
   employment_details     : Optional[EmployeeEmployementGet] = None
   emergency_contact_details  : Optional[EmployeeEmergencyContactGet] = None
   dependent_details          : Optional[EmployeeDependentsGet] = None
   employee_salary            : Optional[EmployeeSalaryGet] = None
   educational_qualification  : List[EmployeeEducationalQualficationGet] = None
   employee_experience        : List[EmployeeExperienceGet] = None
   employee_documents            : List[EmployeeDocumentsGet] = None
   professional_qualification    : List[EmployeeProfessionalQualificationGet] = None
   employee_security_credentials : Optional[EmployeeSecurityCredentialsGet] = None
   user_roles                    : List[EmployeeUserRolesGet] = None   
   language_proficiency          : List[EmployeeLanguageProficiencyGet] = None 

class EmployeeAddressDetailsSchema(BaseModel):
    present_address        : Optional[EmployeePresentAddressSchema] = None
    permanent_address      : Optional[EmployeePermanentAddressSchema] = None
    bank_details           : Optional[EmployeeBankAccountSchema] = None
    contact_details        : Optional[EmployeeContactSchema] = None


class EmployeeDocumentResponse(BaseModel):
    id               : int
    employee_id      : int
    document_id      : int
    document_name    : str
    document_number  : Optional[str]
    issue_date       : date
    expiry_date      : Optional[date]
    issued_by        : Optional[str]
    remarks          : Optional[str]
    is_deleted       : str
    document         : Optional[str]

    class Config:
        from_attributes = True 

#------------------------------EmployeeTeam--------------------------------------------------------------------
class EmployeeTeamMasterSchema(BaseModel):
    id: Optional[int] = None
    department_id        : int
    team_name            : Optional[str] = None
    description          : str
    effective_from_date  : Optional[date] = None
   
    class Config:
        orm_mode = True

class EmployeeTeamMembersSchema(BaseModel):
    id                  : int
    employee_id         : int
    is_team_leader      : str
    team_leader_id      : Optional[int]
    effective_from_date : Optional[date] = None

    class Config:
        orm_mode = True

class SaveEmployeeTeamMaster(BaseModel):
    master  : EmployeeTeamMasterSchema
    details : List[EmployeeTeamMembersSchema]

class HrViewEmployeeTeamMemberSchema(BaseModel):
    team_member_id: int
    team_leader_id: Optional[int]
    leader_first_name: str
    leader_middle_name: Optional[str]
    leader_last_name: str
  

    class Config:
        orm_mode = True
        from_attributes = True 


class HrViewEmployeeTeamMasterSchema(BaseModel):
    team_id: int
    department_id: int
    department_name: Optional[str]
    team_name: Optional[str]
    description: str
    effective_from_date: date
    effective_to_date: Optional[date]
   #  leaders: List[HrViewEmployeeTeamMemberSchema] 
    leaders: Optional[List[HrViewEmployeeTeamMemberSchema]] = None
    class Config:
        orm_mode = True
        from_attributes = True 



class HrViewEmployeeTeamSchema(BaseModel):
    teams: List[HrViewEmployeeTeamMasterSchema]

    class Config:
        orm_mode = True
        from_attributes = True
        
class EmployeeTeamMembersGet(BaseModel):
    team_member_id      :int
    employee_id         : int
    member_first_name   : str
    member_middle_name  : Optional[str]
    member_last_name    : str
    department_id       : int
    department_name     : Optional[str]
    designation_id      : int
    designation         : Optional[str]
    is_team_leader      : str
    team_leader_id      : Optional[int]
    leader_first_name   : str
    leader_middle_name  : str
    leader_last_name    : str
    effective_from_date : date
    effective_to_date   : Optional[date] = None

    class Config:
        orm_mode = True
        from_attributes = True


class AddEmployeeToTeam(BaseModel):
   team_members: List[EmployeeTeamMembersSchema]
   class Config:
        orm_mode = True
        from_attributes = True 




class EmployeeLanguageProficiencyBase(BaseModel):
    id                  : Optional[int] =None
    language_id         : int
    read_proficiency_id : int
    write_proficiency_id: int
    speak_proficiency_id: int
    remarks             : Optional[str] =None

    class Config:
        orm_mode = True

#-------------------------------------------------------------------------------
# Schema for Vacancy Experience

class VacancyExperienceSchema(BaseModel):
    id: int = 0
    min_years: int
    max_years: int
    weightage: float

# Schema for Vacancy Skills
class VacancySkillsSchema(BaseModel):
    id: int = 0
    skill_id: int
    weightage: float

class LanguageProficiencySchema(BaseModel):
    id: int = 0 
   
    language_id: int 
    language_proficiency_id: int 
    is_read_required: str = 'no' 
    read_weightage: float = 0.0  
    is_write_required: str = 'no'  
    write_weightage: float = 0.0 
    is_speak_required: str = 'no'  
    speak_weightage: float = 0.0 

    class Config:
        orm_mode = True  


# Main Education Schema
# class VacancyEducationSchema(BaseModel):
#     id: int = 0
#     education_level_id:int
#     is_any_level:str
#     education_stream_id:int
#     is_any_stream:str
#     education_subject_or_course_id:int
#     is_any_subject_or_course:str


# class Course(BaseModel):
#     education_subject_or_course_id: List[int]


class Course(BaseModel):
    education_subject_or_course_id: int


class VacancyEducationSchema(BaseModel):
    id: int = 0
    education_level_id: int
    is_any_level: str
    education_stream_id: int
    is_any_stream: str
    course: List[Course]
    is_any_subject_or_course: str



# Main Vacancy Create Schema

class VacancyCreateSchema(BaseModel):
    id: int = 0  
    department_id: int
    designation_id: int
    vacancy_count: int
    job_description: str
    job_location: str
    reported_date: date  # Use date type for date fields
    announcement_date: date
    closing_date: date
    vacancy_status: str
    experience_required: str
    vacancy_experience: Optional[List[VacancyExperienceSchema]] = None
    skills_required: List[VacancySkillsSchema]
    language_proficiency: List[LanguageProficiencySchema]
    education: Optional[List[VacancyEducationSchema]] = None 
 
 #---------------------------------------------------------------------------------
class AnnouncementDetail(BaseModel):
    id: int = 0
    vacancy_master_id: int

class VacancyAnnouncementMaster(BaseModel):
    id: int = 0
    title: str
    description: str
    announcement_type: str
    closing_date: Optional[date] = None
    announcement_details: Optional[List[AnnouncementDetail]] = None  # Optional and no default empty list

class VacancyAnnouncements(BaseModel):
    vacancy_announcement_master: List[VacancyAnnouncementMaster]


class AnnouncementDetail(BaseModel):
    id: int
    title: str
    announcement_type: str
    announcement_status: str
    created_by: str
    created_on: date
    closing_date: Optional[date] = None

class AnnouncementsListResponse(BaseModel):
    announcements: List[AnnouncementDetail]

#------------------------------------------------------------------------------------


class ApplicantMasterSchema(BaseModel):
    id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: str
    gender_id: int
    blood_group: Optional[str] = None
    marital_status_id: int
    nationality_id: int
    personal_mobile_number: Optional[str] = None
    personal_whatsapp_number: Optional[str] = None
    personal_email_id: Optional[str] = None


class ApplicationMasterSchema(BaseModel):
    id: int
    applicant_id: int
    vacancy_master_id: int
    application_date: date
    application_status: str  
    is_deleted: str  

    class Config:
        orm_mode = True


class ApplicantPresentAddressSchema(BaseModel):
    id: int
    applicant_id:int
    present_house_or_flat_name: Optional[str] = None
    present_house_flat_or_door_number: Optional[str] = None
    present_road_name: Optional[str] = None
    present_street_name: Optional[str] = None
    present_land_mark: Optional[str] = None
    present_pin_code: Optional[str] = None
    present_post_office_id: Optional[int] = None
    present_city_id: Optional[int] = None
    present_taluk_id: Optional[int] = None
    present_district_id: Optional[int] = None
    present_state_id: Optional[int] = None
    present_country_id: Optional[int] = None
    is_permenent_address_same_as_present: Optional[str] = None

class ApplicantPermanentAddressSchema(BaseModel):
    id: int
    applicant_id:int
    permanent_house_or_flat_name: Optional[str] = None
    permanent_house_flat_or_door_number: Optional[str] = None
    permanent_road_name: Optional[str] = None
    permanent_street_name: Optional[str] = None
    permanent_land_mark: Optional[str] = None
    permanent_pin_code: Optional[str] = None
    permanent_post_office_id: Optional[int] = None
    permanent_city_id: Optional[int] = None
    permanent_taluk_id: Optional[int] = None
    permanent_district_id: Optional[int] = None
    permanent_state_id: Optional[int] = None
    permanent_country_id: Optional[int] = None

class ApplicantContactSchema(BaseModel):
    id: int
    applicant_id:int
    personal_mobile_number: Optional[str] = None
    personal_whatsapp_number: Optional[str] = None
    personal_email_id: Optional[str] = None

class ApplicantEducationalQualficationSchema(BaseModel):
    id: int
    applicant_id:int
    education_level_id: int
    education_stream_id: int
    education_subject_or_course_id: int
    institution: str
    percentage_of_score: float
    month_and_year_of_completion: str
    status: str

class ApplicantProfessionalQualificationSchema(BaseModel):
    id: int
    applicant_id:int
    qualification_id: int
    institution: str
    membership_number: str
    enrollment_date: str
    percentage_of_score: float
    month_and_year_of_completion: str
    status: str

class ApplicantExperienceSchema(BaseModel):
    id: int
    applicant_id:int
    company_name: str
    company_address: str
    company_contact_number: str
    company_email: str
    position_held: str
    responsibility: str
    start_date: str
    end_date: str
    last_salary: float
    reason_for_leaving: str

class ApplicantLanguageProficiencySchema(BaseModel):
    id: int
    applicant_id:int
    applicant_id: int
    language_id: int
    read_proficiency_id: int
    write_proficiency_id: int
    speak_proficiency_id: int

class ApplicantHobbySchema(BaseModel):
    id: int
    applicant_id:int
    applicant_hobby: str
    remarks: Optional[str] = None

class ApplicantSkillSchema(BaseModel):
    id: int
    applicant_id:int
    skill_id: int
    remarks: Optional[str] = None

class ApplicantSocialMediaProfileSchema(BaseModel):
    id: int
    applicant_id:int
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    xhandle: Optional[str] = None
    linked_in: Optional[str] = None

# Combined Applicant Details Schema

# announcement_details: Optional[List[AnnouncementDetail]] = None
class ApplicantDetails(BaseModel):
    applicant_master: Optional[ApplicantMasterSchema] = None
    applicant_present_address: Optional[ApplicantPresentAddressSchema] = None
    applicant_permanent_address: Optional[ApplicantPermanentAddressSchema] = None
    applicant_contact_details: Optional[ApplicantContactSchema] = None
    applicant_educational_qualification: Optional[List[ApplicantEducationalQualficationSchema]] = None
    applicant_professional_qualification:Optional[List[ApplicantProfessionalQualificationSchema]] = None
    applicant_experience: Optional[List[ApplicantExperienceSchema]] = None
    applicant_language_proficiency: Optional[List[ApplicantLanguageProficiencySchema]]= None
    applicant_hobby: Optional[List[ApplicantHobbySchema]] = None
    applicant_skill: Optional[List[ApplicantSkillSchema]]= None
    applicant_social_media_profile: Optional[List[ApplicantSocialMediaProfileSchema]]= None

#--------------------------------------------------------------------------------------------------
class ApplicantDetailsView(BaseModel):
    applicant_id: int
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    
    gender_id: Optional[int]
    gender_name: Optional[str]
    
    blood_group_id: Optional[int]
    blood_group: Optional[str]
   
    marital_status_id: Optional[int]
    marital_status: Optional[str]
 
    nationality_id: Optional[int]
    nationality_name: Optional[str]
    login_id: Optional[int]
    marital_status_id: Optional[int]
    nationality_id: Optional[int]
    applicant_deleted: Optional[bool]
    
    present_address_id: Optional[int]
    present_house_or_flat_name: Optional[str]
    present_house_flat_or_door_number: Optional[str]
    present_road_name: Optional[str]
    present_street_name: Optional[str]
    present_land_mark: Optional[str]
    present_pin_code: Optional[str]
    
    present_post_office_id: Optional[int]
    present_post_office_name: Optional[str]
    present_post_office_pin_code: Optional[str]
    present_post_office_contact: Optional[str]
    present_post_office_latitude: Optional[str]
    present_post_office_longitude: Optional[str]

    present_city_id: Optional[int]
    present_city_name: Optional[str]
    
    present_taluk_id: Optional[int]
    present_taluk_name: Optional[str]
    
    present_district_id: Optional[int]
    present_district_name: Optional[str]
    
    present_state_id: Optional[int]
    present_state_name: Optional[str]
    # present_state_code: Optional[str]
    
    present_country_id: Optional[int]
    present_country_name: Optional[str]
    
    permanent_address_id: Optional[int]
    permanent_house_or_flat_name: Optional[str]
    permanent_house_flat_or_door_number: Optional[str]
    permanent_road_name: Optional[str]
    permanent_street_name: Optional[str]
    permanent_land_mark: Optional[str]
    permanent_pin_code: Optional[str]
    
    permanent_post_office_id: Optional[int]
    permanent_post_office_name: Optional[str]
    permanent_post_office_pin_code: Optional[str]
    permanent_post_office_contact: Optional[str]
    permanent_post_office_latitude: Optional[str]
    permanent_post_office_longitude: Optional[str]

    permanent_city_id: Optional[int]
    permanent_city_name: Optional[str]
    
    permanent_taluk_id: Optional[int]
    permanent_taluk_name: Optional[str]
    
    permanent_district_id: Optional[int]
    permanent_district_name: Optional[str]
    
    permanent_state_id: Optional[int]
    permanent_state_name: Optional[str]
    # permanent_state_code: Optional[str]
    
    permanent_country_id: Optional[int]
    permanent_country_name: Optional[str]

    contact_details_id: Optional[int]
    personal_mobile_number: Optional[str]
    personal_whatsapp_number: Optional[str]
    personal_email_id: Optional[str]
    contact_deleted: Optional[bool]

    
    class Config:
        orm_mode = True 


class ApplicantMasterResponse(BaseModel):
    applicant_id: Optional[int] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender_id: Optional[int] = None
    gender_name: Optional[str] = None
    # blood_group_id: Optional[int] = None
    blood_group: Optional[str] = None
    marital_status_id: Optional[int] = None
    marital_status: Optional[str] = None
    nationality_id: Optional[int] = None
    nationality_name: Optional[str] = None

    class Config:
        orm_mode = True


#--------------------------------------------------------------------------

class ApplicantPresentAddressResponse(BaseModel):
    present_address_id: Optional[int]
    present_house_or_flat_name: Optional[str] = None
    present_house_flat_or_door_number: Optional[str] = None
    present_road_name: Optional[str] = None
    present_street_name: Optional[str] = None
    present_land_mark: Optional[str] = None
    present_pin_code: Optional[str] = None
    is_permenent_address_same_as_present:Optional[str] = None
    present_post_office_id: Optional[int] = None
    present_post_office_name: Optional[str] = None
    present_post_office_pin_code: Optional[str] = None
    present_post_office_contact: Optional[str] = None
    present_city_id: Optional[int] = None
    present_city_name: Optional[str] = None
    present_taluk_id: Optional[int] = None
    present_taluk_name: Optional[str] = None
    present_district_id: Optional[int] = None
    present_district_name: Optional[str] = None
    present_state_id: Optional[int] = None
    present_state_name: Optional[str] = None
    # present_state_code: Optional[str] = None
    present_country_id: Optional[int] = None
    present_country_name: Optional[str] = None

    class Config:
        orm_mode = True




class ApplicantPermanentAddressResponse(BaseModel):
    permanent_address_id: Optional[int]
    permanent_house_or_flat_name: Optional[str] = None
    permanent_house_flat_or_door_number: Optional[str] = None
    permanent_road_name: Optional[str] = None
    permanent_street_name: Optional[str] = None
    permanent_land_mark: Optional[str] = None
    permanent_pin_code: Optional[str] = None

    permanent_post_office_id: Optional[int] = None
    permanent_post_office_name: Optional[str] = None
    permanent_post_office_pin_code: Optional[str] = None
    permanent_post_office_contact: Optional[str] = None
    applicant_id: Optional[int]
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None

    permanent_city_id: Optional[int] = None
    permanent_city_name: Optional[str] = None

    permanent_taluk_id: Optional[int] = None
    permanent_taluk_name: Optional[str] = None

    permanent_district_id: Optional[int] = None
    permanent_district_name: Optional[str] = None

    permanent_state_id: Optional[int] = None
    permanent_state_name: Optional[str] = None
    # present_state_code: Optional[str] = None

    permanent_country_id: Optional[int] = None
    permanent_country_name: Optional[str] = None

    class Config:
        orm_mode = True



class ApplicantContactDetailsResponse(BaseModel):
    contact_details_id: int
    personal_mobile_number: Optional[str]
    personal_whatsapp_number: Optional[str]
    personal_email_id: Optional[str]
    contact_deleted: str  # Assuming it's an ENUM('yes', 'no')

    applicant_id: int
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]




class ApplicantEducationalQualificationResponse(BaseModel):
    qualification_id: int
    institution: str
    percentage_of_score: float
    month_and_year_of_completion: str
    qualification_status: str
    qualification_deleted: str
    education_level_id: int
    education_level: str
    education_stream_id: Optional[int]  # Optional if it can be None
    education_stream: Optional[str]  # Optional if it can be None
    education_subject_or_course_id: Optional[int]  # Optional if it can be None
    education_subject_or_course: Optional[str]
    # subject_or_course_name: Optional[str]  # Optional if it can be None
    first_name: str
    middle_name: Optional[str]  # Optional if it can be None
    last_name: str

    class Config:
        orm_mode = True



class ApplicantProfessionalQualificationResponse(BaseModel):
    id: int
    applicant_id: int
    qualification_id: int
    institution: Optional[str] = None
    membership_number: Optional[str] = None
    enrollment_date:  Optional[date] = None
    percentage_of_score: Optional[float] = None
    month_and_year_of_completion: Optional[str] = None
    status: str
    is_deleted: str
    profession_name: str 
    applicant_id: int 
    first_name: str
    middle_name: Optional[str]  # Optional if it can be None
    last_name: str

    class Config:
        orm_mode = True



class ApplicantExperienceResponse(BaseModel):
    id: int
    applicant_id: int
    company_name: str
    company_address: str
    company_contact_number: str
    company_email: Optional[str] = None
    position_held: str
    responsibility: str
    start_date: date
    end_date: Optional[date] = None
    last_salary: float
    reason_for_leaving: str
    is_deleted: str
    first_name: str
    middle_name: Optional[str]
    last_name: str

    class Config:
        orm_mode = True




class ApplicantLanguageProficiencyResponse(BaseModel):
    id: int
    language_id:int
    language: str
    read_proficiency_id:int
    read_proficiency: Optional[str] = None
    write_proficiency_id:int
    write_proficiency: Optional[str] = None
    speak_proficiency_id:int
    speak_proficiency: Optional[str] = None
    is_deleted: str
    applicant_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str

    class Config:
        orm_mode = True



class ApplicantHobbyResponse(BaseModel):
    id: int
    
    applicant_hobby: str
    remarks: Optional[str] = None
    applicant_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str

    class Config:
        orm_mode = True




class ApplicantSkillResponse(BaseModel):
    id: int
    
    skill_id: int
    skill: str
    remarks: Optional[str] = None
    applicant_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str

    class Config:
        orm_mode = True



class ApplicantSocialMediaResponse(BaseModel):
    id: int
    applicant_id: int
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    xhandle: Optional[str] = None
    linked_in: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str



class InterviewScheduleRequest(BaseModel):
    id: Optional[int] = 0  # id is optional, and default is 0 for insert
    applicant_id: int
    vacancy_id: int
    interview_panel_id: int
    interview_date: date
    interview_time: time
    location: str
    interview_status: str = "SCHEDULED"  # Default value for interview status
    remarks: Optional[str] = None  # Optional field for remarks


class InterviewSchedulesResponse(BaseModel):
    schedules: List[InterviewScheduleRequest]


#-----------offer letter schema----------------

class InterviewPanelMasterSchema(BaseModel):
    id: Optional[int] = None
    interview_date_from: date
    interview_date_to: date
    interview_time_from: time
    interview_time_to: time
    panel_description: str
    location: str

class InterviewPanelMemberSchema(BaseModel):
    id: Optional[int] = None
    interviewer_id: int
    remarks: Optional[str] = None

class CreateInterviewPanelRequest(BaseModel):
    master: InterviewPanelMasterSchema
    members: List[InterviewPanelMemberSchema]