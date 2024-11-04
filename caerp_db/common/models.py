
# from sqlalchemy import Date
from sqlalchemy import Date
from sqlalchemy import Column, Integer, String ,Float,Text, DECIMAL,Time
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import date, datetime 
from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum





class LoginAttempt(caerp_base):
    __tablename__ = "app_login_attempts"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    login_id    = Column(Integer)
    ip          =  Column(String(20), nullable=True)
    when        =  Column(DateTime, nullable=True)

    





class EmailCredentials(caerp_base):
    __tablename__ = "app_email_api_settings"

    id                      = Column(Integer, primary_key=True, index=True)
    SMTP_auth               = Column(Enum('true', 'false'), nullable=False, default='true')
    SMTP_sequre             = Column(Enum('ssl', 'tls'), nullable=False, default='tls')
    SMTP_host               = Column(String(100), nullable=False)
    SMTP_port               = Column(String(5), nullable=False)
    username                = Column(String(100), nullable=False)
    password                = Column(Text, nullable=False)
    email_error_report      = Column(Integer, nullable=False)
    IMAP_host               = Column(String(100), default=None)
    IMAP_port               = Column(String(5), default=None)
    IMAP_username           = Column(String(100), default=None)
    IMAP_mail_box           = Column(String(10), default=None)
    IMAP_path               = Column(String(30), default=None)
    IMAP_server_encoding    = Column(String(15), default=None)
    IMAP_attachement_dir    = Column(String(20), default=None)
    modified_by             = Column(Integer, default=None)
    modified_on             = Column(DateTime, default=None)



class OtpGeneration(caerp_base):
    __tablename__ = "app_sms_email_otp"

    id              = Column(Integer, primary_key=True, index=True)    
    otp             = Column(String(50), nullable=False)
    otp_expire_on   = Column(DateTime, nullable=False)
    created_by          = Column(Integer, default=None)
    created_on          = Column(DateTime, nullable=False, default=func.now())
    modified_by             = Column(Integer, default=None)
    modified_on             = Column(DateTime, default=None)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by          = Column(Integer, default=None)
    deleted_on          = Column(DateTime, default=None)

class MobileCredentials(caerp_base):
    __tablename__ = "app_sms_api_settings"

    id                      = Column(Integer, primary_key=True, index=True)  
    api_url                  = Column(String(500), nullable=False)
    port                    = Column(String(6), nullable=False)
    sender                  = Column(String(6), nullable=False)
    username                = Column(String(250), nullable=False)
    password                = Column(Text, nullable=False)
    entity_id               = Column(String(250), nullable=False)
    delivery_report_status  = Column(Integer, default=None)
    is_active               = Column(Enum('yes', 'no'), nullable=False, default='yes')
    modified_on             = Column(DateTime, default=None)
    modified_by             = Column(Integer, default=None)

class SmsTemplates(caerp_base):
     __tablename__ = "app_sms_templates"

     id                      = Column(Integer, primary_key=True, index=True) 
     sms_category            = Column(Enum('TRANSACTIONAL', 'PROMOTIONAL'), nullable=False, default=None)
     sms_type                = Column(String(100), nullable=False)
     message_template        = Column(String(500), nullable=False)
     template_id             = Column(String(100), nullable=False)
     created_by              = Column(Integer, default=None)
     created_on              = Column(DateTime, nullable=False, default=func.now())
     modified_on             = Column(DateTime, default=None)
     modified_by             = Column(Integer, default=None)
     is_active               = Column(Enum('yes', 'no'), nullable=False, default='yes')





    
# class UserBase(caerp_base):
#     __tablename__ = "users"

#     id            = Column(Integer, primary_key=True, autoincrement=True)
#     employee_id   = Column(Integer, nullable=True)
#     user_name    = Column(String(50), nullable=True)
#     password      = Column(String(200), nullable=True)
#     role_id       = Column(Integer, nullable=True)
#     designation_id=Column(Integer, nullable=True)
#     is_active     = Column(Enum('yes', 'no'), nullable=False, default='yes')
#     locked_upto   = Column(DateTime, default=None)
#     modified_by   = Column(Integer, default=None)
#     modified_on   = Column(DateTime, default=None)

class UserBase(caerp_base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    employee_id   = Column(Integer, nullable=True)
    user_name    = Column(String(50), nullable=True)
    login_password      = Column(String(200), nullable=True)
    edit_password   = Column(String(200), nullable=True)
    delete_password =  Column(String(200), nullable=True)
    security_password =  Column(String(200), nullable=True)
    is_active     = Column(Enum('yes', 'no'), nullable=False, default='yes')
    is_first_login   = Column(Enum('yes', 'no'), nullable=False, default='yes')
    locked_upto   = Column(DateTime, default=None)
    password_reset_date = Column(Date,default=None)

class UserRole(caerp_base):
    __tablename__ = "user_roles"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    employee_id     = Column(Integer, nullable=True)
    role_id         = Column(Integer, nullable=True)
    created_on      = Column(DateTime, nullable=False, default=func.now())
    created_by      = Column(Integer, nullable=True)
    modified_on     = Column(DateTime, default=None)
    modified_by     = Column(Integer, nullable=True)
    is_deleted      = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_on      = Column(DateTime, default=None)
    deleted_by      = Column(Integer, nullable=True)

class UsersRole(caerp_base):
    __tablename__ = "users_role"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    role            = Column(String, nullable=True)
    created_on      = Column(DateTime, nullable=False, default=func.now())
    created_by      = Column(Integer, nullable=True)
    modified_on     = Column(DateTime, default=None)
    modified_by     = Column(Integer, nullable=True)
    is_deleted      = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_on      = Column(DateTime, default=None)
    deleted_by      = Column(Integer, nullable=True)




class CountryDB(caerp_base):
    __tablename__ = "app_countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_name_english        = Column(String(500), nullable=False)
    country_name_arabic         = Column(String(500, collation='utf8mb3_general_ci'), nullable=True)
    iso2_code                   = Column(String(2), nullable=True)
    iso3_code                   = Column(String(3), nullable=True)
    isd_code                    = Column(String(10), nullable=True)
    states                      =relationship("StateDB",back_populates="country")

# class StateDB(caerp_base):
#     __tablename__ = "app_states"
#     id                          = Column(Integer, primary_key=True, autoincrement=True)
#     country_id                  = Column(Integer, ForeignKey('app_countries.id'), nullable=False)
#     state_name                  = Column(String(50), nullable=False)
#     country                     = relationship("CountryDB", back_populates="states")
#     districts                   = relationship("DistrictDB",back_populates="states")
#     is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
#     # post_offices = relationship("PostOfficeView", back_populates="state_name")
class StateDB(caerp_base):
    __tablename__ = "app_states"
    id                          = Column(Integer, primary_key=True, autoincrement=True)
    country_id                  = Column(Integer, ForeignKey('app_countries.id'), nullable=False)
    state_name                  = Column(String(50), nullable=False)
    country                     = relationship("CountryDB", back_populates="states")
    districts                   = relationship("DistrictDB",back_populates="states")
    gst_registration_name       = Column(String(255), nullable=False)
    state_code                  = Column(Integer, nullable=True)
    is_deleted                  = Column(Enum('yes', 'no'), default='no', nullable=False)


class DistrictDB(caerp_base):
    __tablename__ = "app_districts"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    state_id        = Column(Integer, ForeignKey('app_states.id'), nullable=False)
    district_name   = Column(String(50), nullable=False)
    states          = relationship("StateDB", back_populates="districts")
    # post_offices = relationship("PostOfficeView", back_populates="district_name")


class CityDB(caerp_base):
    __tablename__ = "app_cities"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    country_id      = Column(Integer, ForeignKey('app_countries.id'), nullable=False)
    state_id        = Column(Integer, ForeignKey('app_states.id'), nullable=False)
    city_name       = Column(String(50), nullable=False)
    
class TalukDB(caerp_base):
    __tablename__ = "app_taluks"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    district_id     = Column(Integer, nullable=False)
    state_id        = Column(Integer, nullable=False)
    taluk_name      = Column(String(50), nullable=False)
    # post_offices = relationship("PostOfficeView", back_populates="taluk_name")

    
class CurrencyDB(caerp_base):
    __tablename__ = "app_currencies"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    short_name      = Column(String(3), nullable=False)
    long_name       = Column(String(100), nullable=False)
    currency_symbol = Column(String(10), nullable=True)


    
class NationalityDB(caerp_base):
    __tablename__ = "app_nationality"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    nationality_name = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
class BloodGroupDB(caerp_base):
    __tablename__ = "app_blood_group"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    blood_group = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)

class PostOfficeTypeDB(caerp_base):
    __tablename__ = "app_post_office_type"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    office_type = Column(String(50), nullable=False)
    
    
class PostalDeliveryStatusDB(caerp_base):
    __tablename__ = "app_postal_delivery_status"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    delivery_status = Column(String(50), nullable=False)

    
class PostalCircleDB(caerp_base):
    __tablename__ = "app_postal_circle"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    circle_name = Column(String(50), nullable=False)
    regions     = relationship("PostalRegionDB", back_populates="circle")
    divisions   = relationship("PostalDivisionDB", back_populates="circle", cascade="all, delete-orphan")
   

    
    
class PostalRegionDB(caerp_base):
    __tablename__ = "app_postal_region"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    circle_id       = Column(Integer, ForeignKey('app_postal_circle.id'), nullable=False)
    region_name     = Column(String(50), nullable=False)
    circle          = relationship("PostalCircleDB", back_populates="regions")
    divisions       = relationship("PostalDivisionDB", back_populates="region", cascade="all, delete-orphan")
  



class PostalDivisionDB(caerp_base):
    __tablename__ = "app_postal_division"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    circle_id        = Column(Integer, ForeignKey('app_postal_circle.id'), nullable=False)
    region_id        = Column(Integer, ForeignKey('app_postal_region.id'), nullable=False)
    division_name    = Column(String(50), nullable=False)


    circle = relationship("PostalCircleDB", back_populates="divisions")
    region = relationship("PostalRegionDB", back_populates="divisions")
   



class PostOfficeView(caerp_base):
    __tablename__ = "app_view_post_offices"
    id                  = Column(Integer, primary_key=True)
    post_office_name    = Column(String(length=255))
    pin_code            = Column(String(length=10))
    post_office_type_id = Column(Integer)
    office_type         = Column(String(length=255))
    postal_delivery_status_id = Column(Integer)
    delivery_status     = Column(String(length=255))
    postal_division_id  = Column(Integer)
    division_name       = Column(String(length=255))  # Specify length for VARCHAR column
    postal_region_id    = Column(Integer)
    region_name         = Column(String(length=255))
    postal_circle_id    = Column(Integer)
    circle_name         = Column(String(length=255))
    taluk_id            = Column(Integer)
    taluk_name          = Column(String(length=255))
    district_id         = Column(Integer)
    district_name       = Column(String(length=255))
    state_id            = Column(Integer)
    state_name          = Column(String(length=255))
    country_id          =Column(Integer)
    country_name_english = Column(String(length=255))
    contact_number       = Column(String(length=20)) 
    latitude             = Column(String(length=15)) 
    longitude            = Column(String(length=15)) 
    
    
class Gender(caerp_base):
    __tablename__ = "app_gender"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    gender      = Column(String(20), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
class MaritalStatus(caerp_base):
    __tablename__ = "app_marital_status"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    marital_status      = Column(String(20), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
    
class AppDesignation(caerp_base):
    __tablename__ = "app_designation"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    designation      = Column(String(50), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
    
class PanCard(caerp_base):
    __tablename__   =   "app_pan_card_types"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    pan_card_type_code	= Column(String(1), nullable=False)
    pan_card_type	    = Column(String(100), nullable=False)
    
class AppEducationalQualificationsMaster(caerp_base):
    __tablename__   =   "app_educational_qualifications"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    qualification	    = Column(String(50), nullable=False)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class ConstitutionTypes(caerp_base):
    __tablename__   =   "app_constitution_types"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    constitution_type	 = Column(String(50), nullable=False)

class Profession(caerp_base):
    __tablename__  =  "app_profession"
    
    id                   = Column(Integer, primary_key=True, autoincrement=True)
    profession_name 	 = Column(String(100), nullable=False)
    profession_code      = Column(String(100), nullable=False)
    created_on      = Column(DateTime, nullable=False, default=func.now())
    created_by      = Column(Integer, nullable=True)
    modified_on     = Column(DateTime, default=None)
    modified_by     = Column(Integer, nullable=True)
    is_deleted      = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_on      = Column(DateTime, default=None)
    deleted_by      = Column(Integer, nullable=True)




class QueryManagerQuery(caerp_base):
    __tablename__ = "app_query_manager_queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(500), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class QueryManager(caerp_base):
    __tablename__ = "app_query_manager"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, nullable=False)
    query_description = Column(String(2000), default=None)
    queried_by = Column(Integer,  nullable=False)
    query_on = Column(DateTime, nullable=False)
    is_resolved = Column(Enum('yes', 'no'), nullable=False, default='no')
    resolved_by = Column(Integer,nullable=True )
    resolved_on = Column(DateTime, nullable=False, default=func.now())
    
   

#--------------------------------------------------------
class PaymentsMode(caerp_base):
    __tablename__ = 'app_payments_mode'

    id = Column(Integer, primary_key=True)
    payment_mode= Column(String(500), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class PaymentStatus(caerp_base):
    __tablename__ = 'app_payment_status'

    id = Column(Integer, primary_key=True)
    payment_status= Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class RefundStatus(caerp_base):
    __tablename__ = 'app_refund_status'

    id = Column(Integer, primary_key=True)
    refund_status= Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class RefundReason(caerp_base):
    __tablename__ = 'app_refund_reason'

    id = Column(Integer, primary_key=True)
    refund_reason= Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    



#--------------------------------Aparna--------------------------------------------------------------


#--------------------------------vipin--------------------------------------------------------------
class EmployeeMaster(caerp_base):
    __tablename__ = "employee_master"

    employee_id          = Column(Integer, primary_key=True, autoincrement=True)
    employee_number      = Column(String(50), nullable=False)
    first_name           = Column(String(50), nullable=False)
    middle_name          = Column(String(50), nullable=False)
    last_name            = Column(String(50), nullable=False)
    gender_id            = Column(Integer, nullable=False)
    blood_group          = Column(String(5), default=None)
    marital_status_id    = Column(Integer, nullable=False)
    date_of_birth        = Column(Date, nullable=False)
    joining_date         = Column(Date, nullable=False)
    next_increment_date  = Column(Date, nullable=False)
    nationality_id       = Column(Integer, nullable=False)
    created_by           = Column(Integer, nullable=False, default=0)
    created_on           = Column(DateTime, nullable=False, default=func.now())
    is_approved          = Column(Enum('yes', 'no'), nullable=False, default='no')
    approved_by          = Column(Integer, nullable=False)
    approved_on          = Column(DateTime, nullable=False)
    modified_by          = Column(Integer, default=None)
    modified_on          = Column(DateTime, default=None)
    is_deleted           = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by           = Column(Integer, default=None)
    deleted_on           = Column(DateTime, default=None)
    is_locked            = Column(Enum('yes', 'no'), nullable=False, default='no')  
    locked_on            = Column(DateTime, nullable=True)
    locked_by            = Column(String, nullable=True)



class EmployeePermanentAddress(caerp_base):
    __tablename__ = "employee_permanent_address"    

    id                                  = Column(Integer, primary_key=True, autoincrement=True)
    employee_id                         = Column(Integer, nullable=False)
    permanent_house_or_flat_name        = Column(String(50), default=None)
    permanent_house_flat_or_door_number = Column(String(50), default=None)
    permanent_road_name                 = Column(String(50), default=None)
    permanent_street_name               = Column(String(50), default=None)
    permanent_land_mark                 = Column(String(50), default=None)
    permanent_pin_code                  = Column(String(20), default=None)
    permanent_post_office_id            = Column(Integer, nullable=False)
    permanent_city_id                   = Column(Integer, nullable=False)
    permanent_taluk_id                  = Column(Integer, nullable=False)
    permanent_district_id               = Column(Integer, nullable=False)
    permanent_state_id                  = Column(Integer, nullable=False)
    permanent_country_id                = Column(Integer, nullable=False)
    effective_from_date                 = Column(Date, nullable=False)
    effective_to_date                   = Column(Date, default=None)
    remarks                             = Column(String(1000), default=None)
    created_by                          = Column(Integer, nullable=False, default=0)
    created_on                          = Column(DateTime, nullable=False, default=func.now())
    is_deleted                          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                          = Column(Integer, default=None)
    deleted_on                          = Column(DateTime, default=None)



class EmployeePresentAddress(caerp_base):
    __tablename__ = "employee_present_address"

    id                                 = Column(Integer, primary_key=True, autoincrement=True)
    employee_id                        = Column(Integer, nullable=False)
    present_house_or_flat_name         = Column(String(50), default=None)
    present_house_flat_or_door_number  = Column(String(50), default=None)
    present_road_name                  = Column(String(50), default=None)
    present_street_name                = Column(String(50), default=None)
    present_land_mark                  = Column(String(50), default=None)
    present_pin_code                   = Column(String(20), default=None)
    present_post_office_id             = Column(Integer, nullable=False)
    present_city_id                    = Column(Integer, nullable=False)
    present_taluk_id                   = Column(Integer, nullable=False)
    present_district_id                = Column(Integer, nullable=False)
    present_state_id                   = Column(Integer, nullable=False)
    present_country_id                 = Column(Integer, nullable=False)
    effective_from_date                = Column(Date, nullable=False)
    effective_to_date                  = Column(Date, default=None)
    remarks                            = Column(String(1000), default=None)
    created_by                         = Column(Integer, nullable=False, default=0)
    created_on                         = Column(DateTime, nullable=False, default=func.now())
    is_deleted                         = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                         = Column(Integer, default=None)
    deleted_on                         = Column(DateTime, default=None)



class EmployeeContactDetails(caerp_base):
    __tablename__ = "employee_contact_details"    

    id                        = Column(Integer, primary_key=True, autoincrement=True)
    employee_id               = Column(Integer, nullable=False)
    personal_mobile_number    = Column(String(15), default=None)
    personal_whatsapp_number  = Column(String(15), default=None)
    personal_email_id         = Column(String(50), default=None) 
    official_mobile_number    = Column(String(15), default=None)
    official_whatsapp_number  = Column(String(15), default=None)
    official_email_id         = Column(String(50), default=None)
    effective_from_date       = Column(Date, nullable=False)
    effective_to_date         = Column(Date, default=None)
    remarks                   = Column(String(1000), default=None)
    created_by                = Column(Integer, nullable=False, default=0)
    created_on                = Column(DateTime, nullable=False, default=func.now())
    is_deleted                = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                = Column(Integer, default=None)
    deleted_on                = Column(DateTime, default=None)


class EmployeeBankDetails(caerp_base):
    __tablename__ = "employee_bank_details"

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    employee_id                 = Column(Integer, nullable=False)
    bank_account_number         = Column(String(15), default=None)
    bank_name                   = Column(String(50), default=None)
    bank_branch_name            = Column(String(50), default=None)
    ifsc_code                   = Column(String(15), default=None)
    effective_from_date         = Column(Date, nullable=False)
    effective_to_date           = Column(Date, default=None)
    remarks                     = Column(String(1000), default=None)
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on                  = Column(DateTime, nullable=False, default=func.now())
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, default=None)
    deleted_on                  = Column(DateTime, default=None)

class EmployeeEmploymentDetails(caerp_base):
    __tablename__ = "employee_employment_details"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    employee_id           = Column(Integer, nullable=False)
    department_id         = Column(Integer, nullable=False)
    designation_id        = Column(Integer, nullable=False)
    employee_category_id  = Column(Integer, nullable=False)
    is_consultant         = Column(Enum('yes', 'no'), nullable=False, default='no')
    effective_from_date   = Column(Date, nullable=False)
    effective_to_date     = Column(Date, default=None)
    remarks               = Column(String(1000), default=None) 
    created_by            = Column(Integer, nullable=False, default=0)
    created_on            = Column(DateTime, nullable=False, default=func.now())
    is_approved           = Column(Enum('yes', 'no'), nullable=False, default='no')
    approved_by           = Column(Integer, nullable=False)
    approved_on           = Column(DateTime, nullable=False)
    is_deleted            = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by            = Column(Integer, default=None)
    deleted_on            = Column(DateTime, default=None)





class EmployeeExperience(caerp_base):
    __tablename__ = "employee_experience"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    employee_id     = Column(Integer, nullable=False) 
    position_held   = Column(String(100), nullable=False)
    company_name    = Column(String(100), nullable=False)
    responsibilty   = Column(String(2000), nullable=False)  
    start_date      = Column(Date, nullable=False)
    end_date        = Column(Date, nullable=False)    
    created_by      = Column(Integer, nullable=False, default=0)
    created_on      = Column(DateTime, nullable=False, default=func.now())
    is_deleted      = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by      = Column(Integer, default=None)
    deleted_on      = Column(DateTime, default=None)



class EmployeeDocuments(caerp_base):
    __tablename__ = "employee_documents"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    employee_id      = Column(Integer, nullable=False)
    document_id      = Column(Integer, nullable=False)
    document_number  = Column(String(100), default=None)
    issue_date       = Column(Date, nullable=False)
    expiry_date      = Column(Date, default=None)
    issued_by        = Column(String(100), default=None)
    remarks          = Column(String(500), default=None)
    created_by       = Column(Integer, nullable=False, default=0)
    created_on       = Column(DateTime, nullable=False, default=func.now())
    is_deleted       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by       = Column(Integer, default=None)
    deleted_on       = Column(DateTime, default=None)


class EmployeeEmergencyContactDetails(caerp_base):
    __tablename__ = "employee_emergency_contact_details"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    employee_id          = Column(Integer, nullable=False)
    contact_person_name  = Column(String(100), default=None)
    relation_id          = Column(Integer, nullable=False)
    gender_id            = Column(Integer, nullable=False)
    mobile_number        = Column(String(100), nullable=False)
    effective_from_date = Column(Date, nullable=False)
    effective_to_date   = Column(Date, default=None) 
    created_by           = Column(Integer, nullable=False, default=0)
    created_on           = Column(DateTime, nullable=False, default=func.now())
    is_deleted           = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by           = Column(Integer, default=None)
    deleted_on           = Column(DateTime, default=None)


class EmployeeDependentsDetails(caerp_base):
    __tablename__ = "employee_dependents_details"    

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    employee_id          = Column(Integer, nullable=False)
    dependent_name       = Column(String(100), default=None)
    relation_id          = Column(Integer, nullable=False)
    gender_id            = Column(Integer, nullable=False)
    date_of_birth        = Column(Date, default=None)
    effective_from_date  = Column(Date, nullable=False)
    effective_to_date    = Column(Date, default=None)
    created_by           = Column(Integer, nullable=False, default=0)
    created_on           = Column(DateTime, nullable=False, default=func.now())
    is_deleted           = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by           = Column(Integer, default=None)
    deleted_on           = Column(DateTime, default=None)

class EmployeeProfessionalQualification(caerp_base):
    __tablename__ = "employee_professional_qualifications"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    employee_id          = Column(Integer,nullable=False)
    qualification_id     = Column(Integer,nullable=False)
    membership_number    = Column(String(50), default=None)
    enrollment_date      = Column(Date, nullable=False)
    created_by           = Column(Integer, nullable=False, default=0)
    created_on           = Column(DateTime, nullable=False, default=func.now())
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
class EmployeeEducationalQualification(caerp_base):
    __tablename__ = "employee_educational_qualification"    

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    employee_id                 = Column(Integer,nullable=False)
    qualification_name          = Column(String(100), default=None)
    institution                 = Column(String(100), default=None)
    percentage_or_grade         = Column(String(100), default=None)
    month_and_year_of_completion = Column(String(50), default=None)
    created_by                  = Column(Integer, nullable=False)
    created_on                  = Column(DateTime, nullable=False, default=func.now())
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, default=None)
    deleted_on                  = Column(DateTime, default=None)
    
class AppViewVillages(caerp_base):
    __tablename__ = "app_view_villages"
    
    app_village_id          = Column(Integer, primary_key=True, index=True)
    village_name            = Column(String)
    village_code            = Column(String)
    post_office_name        = Column(String)
    pincode                 = Column(String)
    lsg_id                  = Column(Integer)
    lsg_name                = Column(String)
    lsg_code                = Column(String)
    lsg_type_id             = Column(Integer)
    lsg_type                = Column(String)
    lsg_sub_type_id         = Column(Integer)
    lsg_sub_type            = Column(String)
    block_id                = Column(Integer)
    block_code              = Column(String)
    block_name              = Column(String)
    taluk_id                = Column(Integer)
    taluk_name              = Column(String)
    taluk_code              = Column(String)

    


class BusinessActivityType(caerp_base):
    __tablename__ = 'app_business_activity_type'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    business_activity_type      = Column(String, nullable=False)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')


class BusinessActivityMaster(caerp_base):
    __tablename__ = 'app_business_activity_master'


    id                                   = Column(Integer, primary_key=True, autoincrement=True)
    business_activity_type_id            = Column(Integer,nullable=False)
    business_activity             = Column(String, nullable=False)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')

class BusinessActivity(caerp_base):
    __tablename__ = 'app_business_activity'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    activity_master_id            = Column(Integer,nullable=False)
    business_activity           = Column(String, nullable=False)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')



class BookNumber(caerp_base):
    __tablename__ = 'acc_book_numbers'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id           = Column(Integer, nullable=False)
    customer_id                 = Column(Integer, nullable=False)
    book_type                   = Column(String, nullable=False)
    book_prefix                 = Column(String, nullable=True)
    book_number                 = Column(Integer, nullable=False, default= 0)
    is_active                   = Column(Enum('yes', 'no'), nullable=False, default='no')


class AppActivityHistory(caerp_base):
    __tablename__ = 'app_activity_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_taken_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    action_taken_by = Column(Integer, ForeignKey('employee_master.employee_id'), nullable=False)
    action_type = Column(Enum('INSERT', 'UPDATE', 'DELETE', 'SELECT'), nullable=False)
    db_table_name = Column(String(50), nullable=False)
    action_query = Column(Text, nullable=False)





class AppConstitutionStakeholders(caerp_base):
    __tablename__ = 'app_constitution_stakeholders'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    constitution_id            = Column(Integer,nullable=False)
    stakeholder                      = Column(String, nullable=False)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
