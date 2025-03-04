from sqlalchemy import ARRAY, Boolean, Date
from sqlalchemy import Column, Integer, String ,Float,Text, DECIMAL,Time
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import date, datetime 
from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum

class PrlSalaryComponent(caerp_base):
    __tablename__ = 'prl_salary_components'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    component_type = Column(Enum('ALLOWANCE', 'DEDUCTION'), nullable=False, default='ALLOWANCE')
    component_name = Column(String(100), default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class PrlCalculationFrequency(caerp_base):
    __tablename__ = 'prl_calculation_frequency'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    frequency = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class PrlCalculationMethod(caerp_base):
    __tablename__ = 'prl_calculation_method'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    calculation_method = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
class EmployeeSalaryDetails(caerp_base):
    __tablename__ = "employee_salary_details"

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    employee_id                 = Column(Integer, nullable=False)
    component_id                = Column(Integer, nullable=False)
    calculation_frequency_id    = Column(Integer, nullable=False)
    calculation_method_id       = Column(Integer, nullable=False)
    amount                      = Column(Float, nullable=False, default=0.0)
    percentage_of_component_id  = Column(Integer, default=None)
    percentage                  = Column(Float, nullable=False, default=0.0)
    effective_from_date         = Column(Date, nullable=False)
    effective_to_date           = Column(Date, default=None)
    next_increment_date         = Column(Date, default=None)
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on                  = Column(DateTime, nullable=False, default=func.now())
    is_approved                 = Column(Enum('yes', 'no'), nullable=False, default='no')
    approved_by                 = Column(Integer, nullable=True)
    approved_on                 = Column(DateTime, nullable=True)
    modified_by                 = Column(Integer, default=None)
    modified_on                 = Column(DateTime, default=None)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, default=None)
    deleted_on                  = Column(DateTime, default=None)


class EmployeeSalaryDetailsView(caerp_base):
    __tablename__ = "hr_view_employee_salary"

    salary_id                          = Column(Integer, primary_key=True)
    employee_id                        = Column(Integer)
    employee_first_name                = Column(String)
    employee_middle_name               = Column(String)
    employee_last_name                 = Column(String)
    component_id                       = Column(Integer)
    salary_component_name              = Column(String)
    salary_component_type              = Column(String)
    calculation_frequency_id           = Column(Integer)
    calculation_frequency_name         = Column(String)
    calculation_method_id              = Column(Integer)
    calculation_method_name            = Column(String)
    amount                             = Column(Float)
    percentage_of_component_id         = Column(Integer)
    percentage_component_name          = Column(String)
    percentage                         = Column(Float)
    effective_from_date                = Column(Date)
    effective_to_date                  = Column(Date)
    next_increment_date                = Column(Date)
    created_by                         = Column(Integer)
    created_on                         = Column(DateTime)
    is_approved                        = Column(Enum('yes', 'no'))
    approved_by                        = Column(Integer)
    approved_on                        = Column(DateTime)
    modified_by                        = Column(Integer)
    modified_on                        = Column(DateTime)
    is_deleted                         = Column(Enum('yes', 'no'))
    deleted_by                         = Column(Integer)
    deleted_on                         = Column(DateTime)
    

#----------------------------EmployeeTeam---------------------------------------------------------------------
class EmployeeTeamMaster(caerp_base):
    __tablename__ = 'employee_team_master'

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    department_id         = Column(Integer, nullable=False)
    team_name             = Column(String(50), nullable=True)
    description           = Column(String(1000), nullable=False)
    effective_from_date   = Column(Date, nullable=False, default=datetime.now().date)
    effective_to_date     = Column(Date, nullable=True)
    created_by            = Column(Integer, nullable=False)
    created_on            = Column(DateTime, nullable=False, default=datetime.now)
    modified_by           = Column(Integer, nullable=True)
    modified_on           = Column(DateTime, nullable=True)
    is_deleted            = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by            = Column(Integer, nullable=True)
    deleted_on            = Column(DateTime, nullable=True)


class EmployeeTeamMembers(caerp_base):
    __tablename__ = 'employee_team_members'

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    team_master_id        = Column(Integer, nullable=False)
    employee_id           = Column(Integer, nullable=False)
    is_team_leader        = Column(Enum('yes', 'no'), nullable=False, default='no')
    team_leader_id        = Column(Integer, nullable=False)
    effective_from_date   = Column(Date, nullable=False, default=datetime.now().date)
    effective_to_date     = Column(Date, nullable=True)
    created_by            = Column(Integer, nullable=False)
    created_on            = Column(DateTime, nullable=False, default=datetime.now)
    modified_by           = Column(Integer, nullable=True)
    modified_on           = Column(DateTime, nullable=True)
    is_deleted            = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by            = Column(Integer, nullable=True)
    deleted_on            = Column(DateTime, nullable=True)




class HrViewEmployeeTeamMaster(caerp_base):
    __tablename__ = 'hr_view_employee_team_master'

    team_id               = Column(Integer, primary_key=True)
    department_id         = Column(Integer, nullable=False)
    department_name       = Column(String(200))
    team_name             = Column(String(50))
    description           = Column(String(1000), nullable=False)
    effective_from_date   = Column(Date, nullable=False)
    effective_to_date     = Column(Date)

    created_by            = Column(Integer, nullable=False)
    created_on            = Column(DateTime, nullable=False)
    modified_by           = Column(Integer)
    modified_on           = Column(DateTime)
    is_deleted            = Column(Enum('yes', 'no'), nullable=False)
    deleted_by            = Column(Integer)
    deleted_on            = Column(DateTime)
    


class HrViewEmployeeTeamMembers(caerp_base):
    __tablename__ = 'hr_view_employee_team_members'

    team_member_id       = Column(Integer, primary_key=True)
    team_master_id       = Column(Integer, nullable=False)
    team_name            = Column(String(50))
    employee_id          = Column(Integer, nullable=False)
    member_first_name    = Column(String(50), nullable=False)
    member_middle_name   = Column(String(50))
    member_last_name     = Column(String(50), nullable=False)
    department_id        = Column(Integer, nullable=False)
    department_name      = Column(String(200))
    designation_id       = Column(Integer, nullable=False)
    designation          = Column(String(200))
    is_team_leader       = Column(Enum('yes', 'no'), nullable=False)
    team_leader_id       = Column(Integer, nullable=False)
    leader_first_name    = Column(String(50), nullable=False)
    leader_middle_name   = Column(String(50))
    leader_last_name     = Column(String(50), nullable=False)
    effective_from_date  = Column(Date, nullable=False)
    effective_to_date    = Column(Date)
    created_by           = Column(Integer, nullable=False)
    created_on           = Column(DateTime, nullable=False)
    modified_by          = Column(Integer)
    modified_on          = Column(DateTime)
    is_deleted           = Column(Enum('yes', 'no'), nullable=False)
    deleted_by           = Column(Integer)
    deleted_on           = Column(DateTime)

    

    
class HrDocumentMaster(caerp_base):
    __tablename__ = "hr_document_master"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    document_name = Column(String(100), nullable=False)
    has_expiry = Column(Enum('yes', 'no'), default='no', nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
class HrDepartmentMaster(caerp_base):
    __tablename__ = "hr_department_master"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(200), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
class HrDesignationMaster(caerp_base):
    __tablename__ = "hr_designation_master"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    designation = Column(String(200), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
    
class HrEmployeeCategory(caerp_base):
    __tablename__ = "hr_employee_category"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(200), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    


#------------------------------------------------------------------------------------


class VacancyMaster(caerp_base):
    __tablename__ = 'vacancy_master'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    designation_id           = Column(Integer,nullable=False)
    department_id            = Column(Integer,  nullable=False, default=0)
    created_by              = Column(Integer,  nullable=False, default=0)  
    modified_by             = Column(Integer, nullable=True)
    deleted_by              = Column(Integer,  nullable=True)
    job_description         = Column(String(2000), nullable=False)
    vacancy_count           = Column(Integer, nullable=True, default=None)
    reported_date           = Column(Date, nullable=False)
    announcement_date      = Column(Date, nullable=True, default=None)
    closing_date            = Column(Date, nullable=True, default=None)
    vacancy_status          = Column(Enum('OPEN','ANNOUNCED','CLOSED','RANKLIST_GENERATED','INTERVIEW_SCHEDULED'), nullable=False, default='ON HOLD')
    job_location            = Column(String(200), nullable=True, default=None)
    experience_required     = Column(Enum('yes', 'no'), nullable=True, default='no')
    created_on               = Column(DateTime, nullable=False, default=datetime.utcnow) 
    created_by               = Column(Integer, nullable=False)
    modified_on             = Column(DateTime, nullable=True, default=None)
    modified_by             = Column(String, nullable=False)
    is_deleted              = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_on              = Column(DateTime, nullable=True, default=None)



class VacancySkills(caerp_base):
    __tablename__ = 'vacancy_skills'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_master_id       = Column(Integer, nullable=False)
    skill_id                = Column(Integer, nullable=False)
    weightage               = Column(Float, nullable=False, default=0.0)
    created_by              = Column(Integer, nullable=False, default=0)
    created_on        = Column(DateTime, nullable=False, default=datetime.utcnow) 
    modified_by             = Column(Integer, nullable=True)
    modified_on             = Column(DateTime, nullable=True, default=None)
    is_deleted              = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by              = Column(Integer, nullable=True)
    deleted_on             = Column(DateTime, nullable=True, default=None)



class VacancyLanguageProficiency(caerp_base):
    __tablename__ = 'vacancy_language_proficiency'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_master_id           = Column(Integer, nullable=False)
    language_id                 = Column(Integer, nullable=False)
    language_proficiency_id     = Column(Integer, nullable=False)
    is_read_required            = Column(Enum('yes', 'no'), nullable=False, default='no')
    read_weightage              = Column(Float, nullable=False, default=0.0)
    is_write_required           = Column(Enum('yes', 'no'), nullable=False, default='no')
    write_weightage             = Column(Float, nullable=False, default=0.0)
    is_speak_required           = Column(Enum('yes', 'no'), nullable=False, default='no')
    speak_weightage             = Column(Float, nullable=False, default=0.0)
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on        = Column(DateTime, nullable=False, default=datetime.utcnow) 
    modified_by                 = Column(Integer, nullable=True)
    modified_on                 = Column(DateTime, nullable=True, default=None)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, nullable=True)
    deleted_on                  = Column(DateTime, nullable=True, default=None)




class VacancyEducationalQualification(caerp_base):
    __tablename__ = 'vacancy_educational_qualification'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_master_id           = Column(Integer, nullable=False)
    education_level_id          = Column(Integer, nullable=True, default=None)
    is_any_level                = Column(Enum('yes', 'no'), nullable=False, default='no')
    education_stream_id         = Column(Integer, nullable=True, default=None)
    is_any_stream               = Column(Enum('yes', 'no'), nullable=False, default='no')
    education_subject_or_course_id = Column(Integer, nullable=True, default=None)
    # education_subject_or_course_id = Column(ARRAY(Integer), nullable=False)
    is_any_subject_or_course    = Column(Enum('yes', 'no'), nullable=False, default='no')
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on                  = Column(DateTime, nullable=False, default=datetime.utcnow) 
    modified_by                 = Column(Integer, nullable=True)
    modified_on                 = Column(DateTime, nullable=True, default=None)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, nullable=True)
    deleted_on                  = Column(DateTime, nullable=True, default=None)


class VacancyEducationalLevel(caerp_base):
    __tablename__ = 'vacancy_educational_level'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_master_id           = Column(Integer,  nullable=False)
    education_level_id          = Column(Integer,  nullable=True, default=None)
    is_any_level                = Column(Enum('yes', 'no'), nullable=False, default='no')
    weightage                   = Column(Float, nullable=False, default=0.0)
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on                  = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_by                 = Column(Integer, nullable=True)
    modified_on                 = Column(DateTime, nullable=True, default=None)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, nullable=True)
    deleted_on                  = Column(DateTime, nullable=True, default=None)



class VacancyEducationalStream(caerp_base):
    __tablename__ = 'vacancy_educational_stream'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_master_id           = Column(Integer, nullable=False)
    education_stream_id         = Column(Integer,  nullable=True, default=None)
    is_any_stream               = Column(Enum('yes', 'no'), nullable=False, default='no')
    weightage                   = Column(Float, nullable=False, default=0.0)
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on                  = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_by                 = Column(Integer, nullable=True)
    modified_on                 = Column(DateTime, nullable=True, default=None)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, nullable=True)
    deleted_on                  = Column(DateTime, nullable=True, default=None)




class VacancyEducationalSubjectOrCourse(caerp_base):
    __tablename__ = 'vacancy_educational_subject_or_course'

    id                            = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_master_id             = Column(Integer, nullable=False)
    education_subject_or_course_id = Column(Integer,  nullable=True, default=None)
    is_any_subject_or_course      = Column(Enum('yes', 'no'), nullable=False, default='no')
    weightage                     = Column(Float, nullable=False, default=0.0)
    created_by                    = Column(Integer, nullable=False, default=0)
    created_on                    = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_by                   = Column(Integer, nullable=True)
    modified_on                   = Column(DateTime, nullable=True, default=None)
    is_deleted                    = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                    = Column(Integer, nullable=True)
    deleted_on                    = Column(DateTime, nullable=True, default=None)




# Assuming caerp_base is a subclass of SQLAlchemy's declarative base
class VacancyExperience(caerp_base):
    __tablename__ = 'vacancy_experience'

    id                = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_master_id = Column(Integer, nullable=False)
    min_years         = Column(Integer, nullable=False, default=0)
    max_years         = Column(Integer, nullable=False, default=0)
    weightage         = Column(Float, nullable=False, default=0.0)
    created_by        = Column(Integer, nullable=False, default=0)
    created_on        = Column(DateTime, nullable=False, default=datetime.utcnow)  # Set default to current timestamp
    modified_by       = Column(Integer, nullable=True)
    modified_on       = Column(DateTime, nullable=True, default=None)
    is_deleted        = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by        = Column(Integer, nullable=True)
    deleted_on        = Column(DateTime, nullable=True, default=None)




class VacancyDetailsView(caerp_base):
    __tablename__ = 'view_vacancy_details'

    vacancy_master_id = Column(Integer, primary_key=True)
    department_id = Column(Integer)
    department_name = Column(String)
    designation_id = Column(Integer)
    designation_name = Column(String)
    vacancy_count = Column(Integer)
    job_description = Column(String)
    job_location = Column(String)
    reported_date = Column(Date)
    announcement_date = Column(Date)
    closing_date = Column(Date)
    vacancy_status = Column(String)
    experience_required = Column(String)

    skill_id = Column(Integer)
    skill_name = Column(String)
    skill_weightage = Column(Float)

    language_id = Column(Integer)
    language_name = Column(String)
    language_proficiency_id = Column(Integer)
    proficiency_level = Column(String)
    is_read_required = Column(Enum('yes', 'no', name='yes_no'))
    read_weightage = Column(Float)
    is_write_required = Column(Enum('yes', 'no', name='yes_no'))
    write_weightage = Column(Float)
    is_speak_required = Column(Enum('yes', 'no', name='yes_no'))
    speak_weightage = Column(Float)

    education_level_id = Column(Integer)
    is_any_education_level = Column(Enum('yes', 'no', name='yes_no'))
    education_stream_id = Column(Integer)
    is_any_education_stream = Column(Enum('yes', 'no', name='yes_no'))
    education_subject_or_course_id = Column(Integer)
    is_any_subject_or_course = Column(Enum('yes', 'no', name='yes_no'))

    education_level_name = Column(String)
    education_stream_name = Column(String)
    subject_or_course_name = Column(String)

    min_years = Column(Integer)
    max_years = Column(Integer)
    experience_weightage = Column(Float)

#------------------------------------------------------------------------------------  


class VacancyAnnouncementMaster(caerp_base):
    __tablename__ = 'vacancy_announcement_master'

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    title                = Column(String(2000), nullable=False)
    description          = Column(String(2000), nullable=False)
   
    announcement_type    = Column(Enum('SPECIAL', 'GENERAL'), nullable=False, default='GENERAL')
    announcement_status  = Column(Enum('ACTIVE', 'INACTIVE'), nullable=False, default='ACTIVE')
    closing_date         = Column(Date, nullable=True, default=None)
    created_by           = Column(Integer, nullable=False, default=0)
    created_on        = Column(DateTime, nullable=False, default=datetime.utcnow) 
    modified_by          = Column(Integer, nullable=True)
    modified_on          = Column(DateTime, nullable=True, default=None)
    is_deleted           = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by           = Column(Integer, nullable=True)
    deleted_on           = Column(DateTime, nullable=True, default=None)


#------------------------------------------------------------------------------------

class VacancyAnnouncementDetails(caerp_base):
    __tablename__ = 'vacancy_announcement_details'

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_announcement_master_id = Column(Integer, nullable=False)
    vacancy_master_id       = Column(Integer, nullable=False)
    created_by             = Column(Integer, nullable=False, default=0)
    created_on             = Column(DateTime, nullable=False, default='CURRENT_TIMESTAMP')
    modified_by            = Column(Integer, nullable=True)
    modified_on            = Column(DateTime, nullable=True, default=None)
    is_deleted             = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by             = Column(Integer, nullable=True)
    deleted_on             = Column(DateTime, nullable=True, default=None)

#-----------------------------------------------------------------------------------
class ApplicantMaster(caerp_base):
    __tablename__ = "applicant_master"

    applicant_id = Column(Integer, primary_key=True, autoincrement=True)
    login_id = Column(Integer, nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    gender_id = Column(Integer, nullable=False)
    blood_group = Column(String(5),  nullable=True)
    marital_status_id = Column(Integer, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    nationality_id = Column(Integer,  nullable=False)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")

#--------------------------------------------------------------------------------------------

class ApplicantPresentAddress(caerp_base):
    __tablename__ = "applicant_present_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    present_house_or_flat_name = Column(String(50), nullable=True)
    present_house_flat_or_door_number = Column(String(50), nullable=True)
    present_road_name = Column(String(50), nullable=True)
    present_street_name = Column(String(50), nullable=True)
    present_land_mark = Column(String(50), nullable=True)
    present_pin_code = Column(String(50), nullable=True)
    present_post_office_id = Column(Integer, nullable=False, default=0)
    present_city_id = Column(Integer, nullable=False, default=0)
    present_taluk_id = Column(Integer, nullable=False, default=0)
    present_district_id = Column(Integer, nullable=False, default=0)
    present_state_id = Column(Integer, nullable=False, default=0)
    present_country_id = Column(Integer, nullable=False, default=0)
    is_permenent_address_same_as_present = Column(Enum("yes", "no"), nullable=False, default="no")
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")

#--------------------------------------------------------------------------------------------
class ApplicantPermanentAddress(caerp_base):
    __tablename__ = "applicant_permanent_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    permanent_house_or_flat_name = Column(String(50), nullable=True)
    permanent_house_flat_or_door_number = Column(String(50), nullable=True)
    permanent_road_name = Column(String(50), nullable=True)
    permanent_street_name = Column(String(50), nullable=True)
    permanent_land_mark = Column(String(50), nullable=True)
    permanent_pin_code = Column(String(50), nullable=True)
    permanent_post_office_id = Column(Integer, nullable=False, default=0)
    permanent_city_id = Column(Integer, nullable=False, default=0)
    permanent_taluk_id = Column(Integer, nullable=False, default=0)
    permanent_district_id = Column(Integer, nullable=False, default=0)
    permanent_state_id = Column(Integer, nullable=False, default=0)
    permanent_country_id = Column(Integer, nullable=False, default=0)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")

#--------------------------------------------------------------------------------------------

class ApplicantContactDetails(caerp_base):
    __tablename__ = "applicant_contact_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    personal_mobile_number = Column(String(15), nullable=True)
    personal_whatsapp_number = Column(String(15), nullable=True)
    personal_email_id = Column(String(50), nullable=True)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")
#--------------------------------------------------------------------------------------------
class ApplicantEducationalQualification(caerp_base):
    __tablename__ = "applicant_educational_qualification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    education_level_id = Column(Integer, nullable=False)
    education_stream_id = Column(Integer, nullable=False)
    education_subject_or_course_id = Column(Integer, nullable=False)
    institution = Column(String(100), nullable=False)
    percentage_of_score = Column(Float, nullable=False)
    month_and_year_of_completion = Column(String(50), nullable=False)
    status = Column(Enum("PURSUING", "COMPLETED", "RESULT AWAITING"), default="COMPLETED")
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")
#------------------------------------------------------------------------------------------------

class ApplicantProfessionalQualification(caerp_base):
    __tablename__ = "applicant_professional_qualifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    qualification_id = Column(Integer, nullable=False)
    institution = Column(String(100), nullable=True)
    membership_number = Column(String(100), nullable=True)
    enrollment_date = Column(Date, nullable=False)
    percentage_of_score = Column(Float, nullable=False)
    month_and_year_of_completion = Column(String(50), nullable=True)
    status = Column(Enum("PURSUING", "COMPLETED", "RESULT AWAITING"), default="COMPLETED")
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")

#---------------------------------------------------------------------------------------------------
class ApplicantExperience(caerp_base):
    __tablename__ = "applicant_experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    company_name = Column(String(100), nullable=False)
    company_address = Column(String(100), nullable=False)
    company_contact_number = Column(String(100), nullable=False)
    company_email = Column(String(100), nullable=True)
    position_held = Column(String(100), nullable=False)
    responsibility = Column(String(2000), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    last_salary = Column(Float, nullable=False, default=0.0)
    reason_for_leaving = Column(String(100), nullable=False)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")

#-----------------------------------------------------------------------------------------
class ApplicantLanguageProficiency(caerp_base):
    __tablename__ = "applicant_language_proficiency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    language_id = Column(Integer, nullable=False)
    read_proficiency_id = Column(Integer, nullable=False)
    write_proficiency_id = Column(Integer, nullable=False)
    speak_proficiency_id = Column(Integer, nullable=False)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")
#-----------------------------------------------------------------------------------------
class ApplicantHobby(caerp_base):
    __tablename__ = "applicant_hobby"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    applicant_hobby = Column(String(50), nullable=False)
    remarks = Column(String(500), nullable=True, default=None)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")
#-----------------------------------------------------------------------------------------
class ApplicantSkill(caerp_base):
    __tablename__ = "applicant_skill"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    skill_id = Column(Integer, nullable=False)
    remarks = Column(String(500), nullable=True, default=None)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")
#-----------------------------------------------------------------------------------------
class ApplicantSocialMediaProfile(caerp_base):
    __tablename__ = "applicant_social_media_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    facebook = Column(String(100), nullable=True, default=None)
    youtube = Column(String(100), nullable=True, default=None)
    xhandle = Column(String(100), nullable=True, default=None)
    linked_in = Column(String(100), nullable=True, default=None)
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")

#---------------------------------------------------------------------------------------------------

class ViewApplicantDetails(caerp_base):
    __tablename__ = 'view_applicant_details'
    applicant_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
   
    gender_id = Column(Integer)
    gender_name = Column(String)
   
    blood_group_id = Column(Integer)
    blood_group = Column(String)
   
    marital_status_id = Column(Integer)
    marital_status = Column(String)
   
    nationality_id = Column(Integer)
    nationality_name = Column(String)
    
    login_id = Column(Integer)
    marital_status_id = Column(Integer)
    nationality_id = Column(Integer)
    applicant_deleted = Column(Boolean)
    
    present_address_id = Column(Integer)
    present_house_or_flat_name = Column(String)
    present_house_flat_or_door_number = Column(String)
    present_road_name = Column(String)
    present_street_name = Column(String)
    present_land_mark = Column(String)
    present_pin_code = Column(String)
    
    present_post_office_id = Column(Integer)
    present_post_office_name = Column(String)
    present_post_office_pin_code = Column(String)
    present_post_office_contact = Column(String)
    present_post_office_latitude = Column(String)
    present_post_office_longitude = Column(String)

    present_city_id = Column(Integer)
    present_city_name = Column(String)
    
    present_taluk_id = Column(Integer)
    present_taluk_name = Column(String)
    
    present_district_id = Column(Integer)
    present_district_name = Column(String)
    
    present_state_id = Column(Integer)
    present_state_name = Column(String)
    present_state_code = Column(String, nullable=True)  
    
    present_country_id = Column(Integer)
    present_country_name = Column(String)
    
    permanent_address_id = Column(Integer)
    permanent_house_or_flat_name = Column(String)
    permanent_house_flat_or_door_number = Column(String)
    permanent_road_name = Column(String)
    permanent_street_name = Column(String)
    permanent_land_mark = Column(String)
    permanent_pin_code = Column(String)
    
    permanent_post_office_id = Column(Integer)
    permanent_post_office_name = Column(String)
    permanent_post_office_pin_code = Column(String)
    permanent_post_office_contact = Column(String)
    permanent_post_office_latitude = Column(String)
    permanent_post_office_longitude = Column(String)

    permanent_city_id = Column(Integer)
    permanent_city_name = Column(String)
    
    permanent_taluk_id = Column(Integer)
    permanent_taluk_name = Column(String)
   
    permanent_district_id = Column(Integer)
    permanent_district_name = Column(String)
    
    permanent_state_id = Column(Integer)
    permanent_state_name = Column(String)
    permanent_state_code = Column(String, nullable=True) 
    
    permanent_country_id = Column(Integer)
    permanent_country_name = Column(String)

    contact_details_id = Column(Integer)
    personal_mobile_number = Column(String)
    personal_whatsapp_number = Column(String)
    personal_email_id = Column(String)
    contact_deleted = Column(Boolean)



#------------------------------------------------------------------------------------------------
class ApplicationMaster(caerp_base):
    __tablename__ = "application_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=False)
    vacancy_master_id = Column(Integer, ForeignKey("vacancy_master.id"), nullable=False)
    application_date = Column(Date, nullable=False)
    application_status = Column(Enum("PENDING", "SHORT LISTED", "REJECTED"), nullable=False, default="PENDING")
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")



class InterviewSchedule(caerp_base):
    __tablename__ = 'interview_schedule'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    applicant_id = Column(Integer,  nullable=False)
    vacancy_id = Column(Integer, nullable=False)
    interview_panel_id = Column(Integer,  nullable=False)
    interview_date = Column(Date, nullable=False)
    interview_time = Column(Time, nullable=False)
    location = Column(String(100), nullable=False)
    interview_status = Column(Enum('SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED', name='status_enum'), default='SCHEDULED', nullable=False)
    remarks = Column(String(1000), default=None)
    is_deleted = Column(Enum('yes', 'no', name='yes_no_enum'), default='no', nullable=False)


class InterviewPanelMaster(caerp_base):
    __tablename__ = "interview_panel_master"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_date_from = Column(Date, nullable=False)
    interview_date_to = Column(Date, nullable=False)
    interview_time_from = Column(Time, nullable=False)
    interview_time_to = Column(Time, nullable=False)
    panel_description = Column(String(1000), nullable=False)
    location = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')



class InterviewPanelMembers(caerp_base):
    __tablename__ = "interview_panel_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_panel_master_id = Column(Integer, nullable=False)
    interviewer_id = Column(Integer,  nullable=False)
    remarks = Column(String(250), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

 

class ApplicationRankList(caerp_base):
    __tablename__ = "application_rank_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer,  nullable=False)
    vacancy_master_id = Column(Integer,  nullable=False)
    
    education_score = Column(Float, nullable=False, default=0.0)
    professional_score = Column(Float, nullable=False, default=0.0)
    experience_score = Column(Float, nullable=False, default=0.0)
    language_score = Column(Float, nullable=False, default=0.0)
    skill_score = Column(Float, nullable=False, default=0.0)
    interview_score = Column(Float, nullable=False, default=0.0)

    rank_number = Column(Integer, nullable=False, default=0)
    total_score = Column(Float, nullable=False, default=0.0)

    # status = Column(Enum("Pending", "Selected", "Rejected"), default="Pending")
    is_deleted = Column(Enum("yes", "no"), nullable=False, default="no")

