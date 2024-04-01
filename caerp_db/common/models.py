
# from sqlalchemy import Date
from sqlalchemy import Date
from sqlalchemy import Column, Integer, String ,Float,Text, DECIMAL
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import date, datetime 
from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum


    
# class AdminUser(caerp_base):
#     __tablename__ = "app_admin_users"

    # id = Column(Integer, primary_key=True, autoincrement=True)
    # first_name = Column(String(50), nullable=False)
    # last_name = Column(String(50), nullable=False)
    # gender_id = Column(Integer, nullable=False)
    # user_name = Column(String(50), nullable=False, unique=True)
    # password = Column(String(200), nullable=False)
    # role_id = Column(Integer, nullable=False)
    # designation_id = Column(Integer, nullable=False)
    # address_line_1 = Column(String(500), default=None)
    # address_line_2 = Column(String(500), default=None)
    # address_line_3 = Column(String(500), default=None)
    # address_line_4 = Column(String(500), default=None)
    # mobile_number = Column(String(20), default=None)
    # whatsapp_number = Column(String(20), default=None)
    # email_id = Column(String(100), default=None)
    # created_by = Column(Integer, nullable=False, default=0)
    # created_on = Column(DateTime, nullable=False, default=func.now())
    # modified_by = Column(Integer, default=None)
    # modified_on = Column(DateTime, default=None)
    # is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    # deleted_by = Column(Integer, default=None)
    # deleted_on = Column(DateTime, default=None)


class LoginAttempt(caerp_base):
    __tablename__ = "app_login_attempts"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    login_id    = Column(Integer)
    ip          =  Column(String(20), nullable=True)
    when        =  Column(DateTime, nullable=True)

    


class Employee(caerp_base):
    __tablename__ = "employee_master"

    employee_id              = Column(Integer, primary_key=True, autoincrement=True)
    employee_number          = Column(String(20), nullable=False)
    first_name               = Column(String(100), nullable=False)
    middle_name              = Column(String(100), nullable=False)
    last_name                = Column(String(100), nullable=False)
    gender_id                = Column(Integer, nullable=False)
    date_of_birth            = Column(Date, default=None)
    nationality_id           = Column(Integer, nullable=False)
    marital_status_id        = Column(Integer, nullable=False)
    designation_id           = Column(Integer, nullable=False)
    is_consultant            = Column(Enum('yes', 'no'), nullable=False, default='no')
    aadhaar_number           = Column(String(50), default=None)
    passport_number          = Column(String(50), default=None)
    pan_number               = Column(String(20), default=None)
    driving_licence_number   = Column(String(50), default=None)
    other_id_doc             = Column(String(50), default=None)
    present_house_or_flat_name   = Column(String(100), nullable=False)
    present_house_flat_or_door_number   = Column(String(100), default=None)
    present_road_name   = Column(String(100), default=None)
    present_street_name   = Column(String(100), default=None)
    present_land_mark      = Column(String(100), default=None)
    present_pin_code         = Column(String(20), default=None)
    present_post_office_id   = Column(Integer, nullable=False)
    present_city_id          = Column(Integer, nullable=False)
    present_taluk_id         = Column(Integer, nullable=False)
    present_district_id      = Column(Integer, nullable=False)
    present_state_id         = Column(Integer, nullable=False)
    present_country_id       = Column(Integer, nullable=False)
    permanent_house_or_flat_name = Column(String(100), nullable=False)
    permanent_house_flat_or_door_number = Column(String(100), default=None)
    permanent_road_name = Column(String(100), default=None)
    permanent_street_name = Column(String(100), default=None)
    permanent_land_mark  = Column(String(100), default=None)
    permanent_pin_code       = Column(String(20), default=None)
    permanent_post_office_id = Column(Integer, nullable=False)
    permanent_city_id        = Column(Integer, nullable=False)
    permanent_taluk_id       = Column(Integer, nullable=False)
    permanent_district_id    = Column(Integer, nullable=False)
    permanent_state_id       = Column(Integer, nullable=False)
    permanent_country_id     = Column(Integer, nullable=False)
    home_phone               = Column(String(20), default=None)
    mobile_phone             = Column(String(20), default=None)
    whatsapp_number          = Column(String(20), default=None)
    work_phone               = Column(String(20), default=None)
    work_email               = Column(String(50), default=None)
    private_email            = Column(String(50), default=None)
    account_number           = Column(String(20), default=None)
    bank_name                = Column(String(50), default=None)
    bank_branch_name         = Column(String(50), default=None)
    ifsc_code                = Column(String(20), default=None)
    created_by               = Column(Integer, nullable=False, default=0)
    created_on               = Column(DateTime, nullable=False, default=func.now())
    modified_by              = Column(Integer, default=None)
    modified_on              = Column(DateTime, default=None)
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by               = Column(Integer, default=None)
    deleted_on               = Column(DateTime, default=None)
    is_verified              = Column(Enum('yes', 'no'), nullable=False, default='no')
    verified_by              = Column(Integer, default=None)
    verified_on              = Column(DateTime, default=None)
    is_approved              = Column(Enum('yes', 'no'), nullable=False, default='no')
    approved_by              = Column(Integer, default=None)
    approved_on              = Column(DateTime, default=None)


class EmployeeMasterView(caerp_base):
    __tablename__ = "view_employee_master"
    employee_id              = Column(Integer, primary_key=True, autoincrement=True)
    employee_number          = Column(String(20), nullable=False)
    first_name               = Column(String(100), nullable=False)
    middle_name              = Column(String(100), nullable=False)
    last_name                = Column(String(100), nullable=False)
    gender_id                = Column(Integer, nullable=False)
    gender                   = Column(String(15), nullable=False)
    date_of_birth            = Column(Date, default=None)
    nationality_id           = Column(Integer, nullable=False)
    nationality_name         = Column(String(50), nullable=False)
    marital_status_id        = Column(Integer, nullable=False)
    marital_status           = Column(String(30), nullable=False)
    designation_id           = Column(Integer, nullable=False)
    designation              = Column(String(50), nullable=False)
    is_consultant            = Column(Enum('yes', 'no'), nullable=False, default='no')
    aadhaar_number           = Column(String(50), default=None)
    passport_number          = Column(String(50), default=None)
    pan_number               = Column(String(20), default=None)
    driving_licence_number   = Column(String(50), default=None)
    other_id_doc             = Column(String(50), default=None)
    present_house_or_flat_name   = Column(String(100), nullable=False)
    present_house_flat_or_door_number   = Column(String(100), default=None)
    present_road_name   = Column(String(100), default=None)
    present_street_name   = Column(String(100), default=None)
    present_land_mark      = Column(String(100), default=None)
    present_pin_code         = Column(String(20), default=None)
    present_post_office_id   = Column(Integer, nullable=False)
    present_post_office_name = Column(String(250), nullable=False)
    present_city_id          = Column(Integer, nullable=False)
    present_city_name        = Column(String(50), nullable=False)
    present_taluk_id         = Column(Integer, nullable=False)
    present_taluk_name       = Column(String(50), nullable=False)
    present_district_id      = Column(Integer, nullable=False)
    present_district_name    = Column(String(50), nullable=False)
    present_state_id         = Column(Integer, nullable=False)
    present_state_name       = Column(String(50), nullable=False)
    present_country_id       = Column(Integer, nullable=False)
    present_country_name     = Column(String(300), nullable=False)
    permanent_house_or_flat_name = Column(String(100), nullable=False)
    permanent_house_flat_or_door_number = Column(String(100), default=None)
    permanent_road_name = Column(String(100), default=None)
    permanent_street_name = Column(String(100), default=None)
    permanent_land_mark  = Column(String(100), default=None)
    permanent_pin_code       = Column(String(20), default=None)
    permanent_post_office_id = Column(Integer, nullable=False)
    permanent_post_office_name = Column(String(250), nullable=False)
    permanent_city_id        = Column(Integer, nullable=False)
    permanent_city_name      = Column(String(50), nullable=False)
    permanent_taluk_id       = Column(Integer, nullable=False)
    permanent_taluk_name     = Column(String(50), nullable=False)
    permanent_district_id    = Column(Integer, nullable=False)
    permanent_district_name  = Column(String(50), nullable=False)
    permanent_state_id       = Column(Integer, nullable=False)
    permanent_state_name     = Column(String(50), nullable=False)
    permanent_country_id     = Column(Integer, nullable=False)
    permanent_country_name   = Column(String(300), nullable=False)
    home_phone               = Column(String(20), default=None)
    mobile_phone             = Column(String(20), default=None)
    whatsapp_number          = Column(String(20), default=None)
    work_phone               = Column(String(20), default=None)
    work_email               = Column(String(50), default=None)
    private_email            = Column(String(50), default=None)
    account_number           = Column(String(20), default=None)
    bank_name                = Column(String(50), default=None)
    bank_branch_name         = Column(String(50), default=None)
    ifsc_code                = Column(String(20), default=None)
    created_by               = Column(Integer, nullable=False, default=0)
    created_on               = Column(DateTime, nullable=False, default=func.now())
    modified_by              = Column(Integer, default=None)
    modified_on              = Column(DateTime, default=None)
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by               = Column(Integer, default=None)
    deleted_on               = Column(DateTime, default=None)
    is_verified              = Column(Enum('yes', 'no'), nullable=False, default='no')
    verified_by              = Column(Integer, default=None)
    verified_on              = Column(DateTime, default=None)
    is_approved              = Column(Enum('yes', 'no'), nullable=False, default='no')
    approved_by              = Column(Integer, default=None)
    approved_on              = Column(DateTime, default=None)

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





    
class UserBase(caerp_base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    employee_id   = Column(Integer, nullable=True)
    user_name    = Column(String(50), nullable=True)
    password      = Column(String(200), nullable=True)
    role_id       = Column(Integer, nullable=True)
    designation_id=Column(Integer, nullable=True)
    is_active     = Column(Enum('yes', 'no'), nullable=False, default='yes')
    locked_upto   = Column(DateTime, default=None)
    modified_by   = Column(Integer, default=None)
    modified_on   = Column(DateTime, default=None)

class CountryDB(caerp_base):
    __tablename__ = "app_countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_name_english        = Column(String(500), nullable=False)
    country_name_arabic         = Column(String(500, collation='utf8mb3_general_ci'), nullable=True)
    iso2_code                   = Column(String(2), nullable=True)
    iso3_code                   = Column(String(3), nullable=True)
    isd_code                    = Column(String(10), nullable=True)
    states                      =relationship("StateDB",back_populates="country")

class StateDB(caerp_base):
    __tablename__ = "app_states"
    id                          = Column(Integer, primary_key=True, autoincrement=True)
    country_id                  = Column(Integer, ForeignKey('app_countries.id'), nullable=False)
    state_name                  = Column(String(50), nullable=False)
    country                     = relationship("CountryDB", back_populates="states")
    districts                   = relationship("DistrictDB",back_populates="states")
    # post_offices = relationship("PostOfficeView", back_populates="state_name")


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
    
   
   
    
class QueryView(caerp_base):
    __tablename__ = 'view_user_queries'

    id = Column(Integer, primary_key=True)
    query_id = Column(Integer)
    query_description=Column(String)
    query = Column(String)
    is_deleted = Column(String)
    queried_by = Column(Integer)
    query_on = Column(DateTime)
    is_resolved = Column(String)
    resolved_by = Column(Integer)
    resolved_on = Column(DateTime)
    user_id = Column(Integer)
    user_name = Column(String)
    role_id = Column(Integer)
    role = Column(String)
    employee_number = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    gender_id = Column(Integer)
    gender = Column(String)
    designation_id = Column(Integer)
    designation = Column(String)
    
