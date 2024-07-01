
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

    


# class Employee(caerp_base):
#     __tablename__ = "employee_master"

#     employee_id              = Column(Integer, primary_key=True, autoincrement=True)
#     employee_number          = Column(String(20), nullable=False)
#     first_name               = Column(String(100), nullable=False)
#     middle_name              = Column(String(100), nullable=False)
#     last_name                = Column(String(100), nullable=False)
#     gender_id                = Column(Integer, nullable=False)
#     date_of_birth            = Column(Date, default=None)
#     nationality_id           = Column(Integer, nullable=False)
#     marital_status_id        = Column(Integer, nullable=False)
#     designation_id           = Column(Integer, nullable=False)
#     is_consultant            = Column(Enum('yes', 'no'), nullable=False, default='no')
#     aadhaar_number           = Column(String(50), default=None)
#     passport_number          = Column(String(50), default=None)
#     pan_number               = Column(String(20), default=None)
#     driving_licence_number   = Column(String(50), default=None)
#     other_id_doc             = Column(String(50), default=None)
#     present_house_or_flat_name   = Column(String(100), nullable=False)
#     present_house_flat_or_door_number   = Column(String(100), default=None)
#     present_road_name   = Column(String(100), default=None)
#     present_street_name   = Column(String(100), default=None)
#     present_land_mark      = Column(String(100), default=None)
#     present_pin_code         = Column(String(20), default=None)
#     present_post_office_id   = Column(Integer, nullable=False)
#     present_city_id          = Column(Integer, nullable=False)
#     present_taluk_id         = Column(Integer, nullable=False)
#     present_district_id      = Column(Integer, nullable=False)
#     present_state_id         = Column(Integer, nullable=False)
#     present_country_id       = Column(Integer, nullable=False)
#     permanent_house_or_flat_name = Column(String(100), nullable=False)
#     permanent_house_flat_or_door_number = Column(String(100), default=None)
#     permanent_road_name = Column(String(100), default=None)
#     permanent_street_name = Column(String(100), default=None)
#     permanent_land_mark  = Column(String(100), default=None)
#     permanent_pin_code       = Column(String(20), default=None)
#     permanent_post_office_id = Column(Integer, nullable=False)
#     permanent_city_id        = Column(Integer, nullable=False)
#     permanent_taluk_id       = Column(Integer, nullable=False)
#     permanent_district_id    = Column(Integer, nullable=False)
#     permanent_state_id       = Column(Integer, nullable=False)
#     permanent_country_id     = Column(Integer, nullable=False)
#     home_phone               = Column(String(20), default=None)
#     mobile_phone             = Column(String(20), default=None)
#     whatsapp_number          = Column(String(20), default=None)
#     work_phone               = Column(String(20), default=None)
#     work_email               = Column(String(50), default=None)
#     private_email            = Column(String(50), default=None)
#     account_number           = Column(String(20), default=None)
#     bank_name                = Column(String(50), default=None)
#     bank_branch_name         = Column(String(50), default=None)
#     ifsc_code                = Column(String(20), default=None)
#     created_by               = Column(Integer, nullable=False, default=0)
#     created_on               = Column(DateTime, nullable=False, default=func.now())
#     modified_by              = Column(Integer, default=None)
#     modified_on              = Column(DateTime, default=None)
#     is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')
#     deleted_by               = Column(Integer, default=None)
#     deleted_on               = Column(DateTime, default=None)
#     is_verified              = Column(Enum('yes', 'no'), nullable=False, default='no')
#     verified_by              = Column(Integer, default=None)
#     verified_on              = Column(DateTime, default=None)
#     is_approved              = Column(Enum('yes', 'no'), nullable=False, default='no')
#     approved_by              = Column(Integer, default=None)
#     approved_on              = Column(DateTime, default=None)




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

class UserBaseNew(caerp_base):
    __tablename__ = "users_new"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    employee_id   = Column(Integer, nullable=True)
    user_name    = Column(String(50), nullable=True)
    login_password      = Column(String(200), nullable=True)
    edit_password   = Column(String(200), nullable=True)
    delete_password =  Column(String(200), nullable=True)
    security_password =  Column(String(200), nullable=True)
    is_active     = Column(Enum('yes', 'no'), nullable=False, default='yes')
    is_first_login   = Column(DateTime, default=None)
    locked_upto   = Column(DateTime, default=None)

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
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
class BloodGroupDB(caerp_base):
    __tablename__ = "app_blood_group"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    blood_group = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
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
    
   
   
    
# class QueryView(caerp_base):
#     __tablename__ = 'view_user_queries'

#     id = Column(Integer, primary_key=True)
#     query_id = Column(Integer)
#     query_description=Column(String)
#     query = Column(String)
#     is_deleted = Column(String)
#     queried_by = Column(Integer)
#     query_on = Column(DateTime)
#     is_resolved = Column(String)
#     resolved_by = Column(Integer)
#     resolved_on = Column(DateTime)
#     user_id = Column(Integer)
#     user_name = Column(String)
#     role_id = Column(Integer)
#     role = Column(String)
#     employee_number = Column(String)
#     first_name = Column(String)
#     last_name = Column(String)
#     gender_id = Column(Integer)
#     gender = Column(String)
#     designation_id = Column(Integer)
#     designation = Column(String)
    

# class ConsultancyService(caerp_base):
#     __tablename__ = 'off_consultancy_services'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     service_master_id = Column(Integer, nullable=False)
#     consultant_id = Column(Integer, nullable=False, default=0)
#     consultation_fee = Column(Float)
#     gst_rate = Column(Float)
#     cgst_rate = Column(Float)
#     sgst_rate = Column(Float)
#     cess_rate = Column(Float)
#     discount_percentage = Column(Float)
#     discount_amount = Column(Float)
#     available_time_from = Column(Time, nullable=False)
#     available_time_to = Column(Time, nullable=False)
#     slot_duration_in_minutes = Column(Integer, nullable=False)
#     effective_from_date = Column(Date, nullable=False)
#     effective_to_date = Column(Date, default=None)
#     is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
        
# class AppointmentVisitDetail(caerp_base):
#     __tablename__ = 'off_appointment_visit_details'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     visit_master_id = Column(Integer, ForeignKey('off_enquiry_visit_master.id'), nullable=False)
#     consultancy_service_id = Column(Integer, ForeignKey('off_consultancy_services.id'), nullable=False)
#     consultant_id = Column(Integer, ForeignKey('employee_master.empoyee_id'), nullable=False)
#     appointment_time = Column(Time, nullable=False)
#     service_charge = Column(Float, default=None)
#     gst_percentage = Column(Float, default=None)
#     sgst_percentage = Column(Float, default=None)
#     cgst_percentage = Column(Float, default=None)
#     discount_percentage = Column(Float, default=None)
#     discount_amount = Column(Float, default=None)
#     net_amount = Column(Float, default=None)
#     remarks = Column(String(1000), default=None)
    
 #--------------------------------------------------------
 
# class OffAppointmentDetails(caerp_base):
#     __tablename__ = 'view_off_appointment_details'

#     appointment_visit_details_id = Column(Integer, primary_key=True)
#     appointment_visit_master_id = Column(Integer)
#     appointment_date = Column(Date)
#     appointment_time = Column(Time)
#     consultancy_service_id = Column(Integer)
#     service_name = Column(String)
#     consultant_id = Column(Integer)
#     employee_number = Column(String)
#     first_name = Column(String)
#     middle_name = Column(String)
#     last_name = Column(String)
#     appointment_visit_details_service_charge = Column(Integer)
#     appointment_visit_details_gst_percentage = Column(Integer)
#     appointment_visit_details_sgst_percentage = Column(Integer)
#     appointment_visit_details_cgst_percentage = Column(Integer)
#     appointment_visit_details_discount_percentage = Column(Integer)
#     appointment_visit_details_discount_amount = Column(Integer)
#     appointment_visit_details_net_amount = Column(Integer)
#     appointment_visit_details_remarks = Column(String)
#     appointment_visit_details_created_by = Column(Integer)
#     appointment_visit_details_created_on = Column(DateTime)
#     appointment_visit_details_modified_by = Column(Integer)
#     appointment_visit_details_modified_on = Column(DateTime)
#     appointment_visit_details_is_deleted = Column(String)
#     appointment_visit_details_is_deleted_directly = Column(String)
#     appointment_visit_details_is_deleted_with_master = Column(String)
#     appointment_visit_details_deleted_by = Column(Integer)
#     appointment_visit_details_deleted_on = Column(DateTime)
    
    
# class OffAppointmentMaster(caerp_base):
#     __tablename__ = 'off_appointment_master'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     full_name = Column(String(200), nullable=False)
#     appointment_number = Column(String(100), default=None)
#     enquiry_number = Column(String(100), default=None)
#     customer_number = Column(String(100), default=None)
#     mobile_number = Column(String(20), default=None)
#     email_id = Column(String(50), default=None)
#     created_by = Column(Integer, default=None)
#     created_on = Column(Date, default=None)
#     modified_by = Column(Integer, default=None)
#     modified_on = Column(Date, default=None)
#     is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
#     deleted_by = Column(Integer, default=None)
#     deleted_on = Column(Date, default=None)
    


# class ViewOffAppointmentMaster(caerp_base):
#     __tablename__ = 'view_off_appointment_master'

#     id = Column(Integer, primary_key=True)
#     full_name = Column(String)
#     appointment_number = Column(String)
#     enquiry_number = Column(String)
#     customer_number = Column(String)
#     mobile_number = Column(String)
#     email_id = Column(String)
#     appointment_master_created_by = Column(Integer)
#     appointment_master_created_on = Column(DateTime)
#     appointment_master_modified_by = Column(Integer)
#     appointment_master_modified_on = Column(DateTime)
#     appointment_master_is_deleted = Column(String)
#     appointment_master_deleted_by = Column(Integer)
#     appointment_master_deleted_on = Column(DateTime)
    
#     appointment_visit_master_id = Column(Integer)
#     appointment_visit_master_appointment_date = Column(Date)
#     appointment_visit_master_source_of_enquiry_id = Column(Integer)
#     source = Column(String)
#     appointment_visit_master_appointment_status_id = Column(Integer)
#     is_paid = Column(Enum('yes', 'no'), nullable=False, default='no')
   
#     appointment_status = Column(String)
#     appointment_visit_master_payment_mode_id = Column(Integer)
#     payment_mode = Column(String)
#     appointment_visit_master_payment_transaction_number = Column(String)
#     appointment_visit_master_payment_status_id = Column(Integer)
#     payment_status = Column(String)
#     appointment_visit_master_payment_date = Column(Date)
#     appointment_visit_master_is_refunded = Column(Enum('yes', 'no'), nullable=False, default='no')
   
#     appointment_visit_master_refund_status_id = Column(Integer)
#     refund_status = Column(String)
#     appointment_visit_master_refund_amount = Column(Float)
#     appointment_visit_master_refund_date = Column(Date)
#     appointment_visit_master_refund_reason_id = Column(Integer)
#     refund_reason = Column(String)
#     appointment_visit_master_refund_transaction_number = Column(String)
#     appointment_visit_master_service_charge = Column(Float)
#     appointment_visit_master_gst_percentage = Column(Float)
#     appointment_visit_master_sgst_percentage = Column(Float)
#     appointment_visit_master_cgst_percentage = Column(Float)
#     appointment_visit_master_discount_percentage = Column(Float)
#     appointment_visit_master_discount_amount = Column(Float)
#     appointment_visit_master_special_discount_percentage = Column(Float)
#     appointment_visit_master_special_discount_amount = Column(Float)
#     appointment_visit_master_net_amount = Column(Float)
#     appointment_visit_master_remarks = Column(String)
#     appointment_visit_master_is_deleted = Column(String)
#     appointment_visit_master_is_deleted_directly = Column(String)
#     appointment_visit_master_is_deleted_with_master = Column(String)
#     appointment_visit_master_deleted_by = Column(Integer)
#     appointment_visit_master_deleted_on = Column(DateTime)
    
    
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
# class Employee(caerp_base):
#     __tablename__ = "employee_master"

#     employee_id           = Column(Integer, primary_key=True, autoincrement=True)
#     employee_number       = Column(String(50), nullable=False)
#     first_name            = Column(String(50), nullable=False)
#     middle_name           = Column(String(50), nullable=False)
#     last_name             = Column(String(50), nullable=False)
#     gender_id             = Column(Integer, nullable=False)
#     date_of_birth         = Column(Date, default=None)
#     nationality_id        = Column(Integer, nullable=False)
#     marital_status_id     = Column(Integer, nullable=False)
#     designation_id        = Column(Integer, nullable=False)
#     is_consultant         = Column(Enum('yes', 'no'), nullable=False, default='no') 
#     effective_from_date   = Column(Date, nullable=False)
#     effective_to_date     = Column(Date, default=None)
#     created_by            = Column(Integer, nullable=False, default=0)
#     created_on            = Column(DateTime, nullable=False, default=func.now())
#     modified_by           = Column(Integer, default=None)
#     modified_on           = Column(DateTime, default=None)
#     is_deleted            = Column(Enum('yes', 'no'), nullable=False, default='no')
#     deleted_by            = Column(Integer, default=None)
#     deleted_on            = Column(DateTime, default=None)


# class EmployeePermanentAddress(caerp_base):
#     __tablename__ = "employee_permanent_address"    

#     id                                  = Column(Integer, primary_key=True, autoincrement=True)
#     employee_id                         = Column(Integer, nullable=False)
#     permanent_house_or_flat_name        = Column(String(50), default=None)
#     permanent_house_flat_or_door_number = Column(String(50), default=None)
#     permanent_road_name                 = Column(String(50), default=None)
#     permanent_street_name               = Column(String(50), default=None)
#     permanent_land_mark                 = Column(String(50), default=None)
#     permanent_pin_code                  = Column(String(20), default=None)
#     permanent_post_office_id            = Column(Integer, nullable=False)
#     permanent_city_id                   = Column(Integer, nullable=False)
#     permanent_taluk_id                  = Column(Integer, nullable=False)
#     permanent_district_id               = Column(Integer, nullable=False)
#     permanent_state_id                  = Column(Integer, nullable=False)
#     permanent_country_id                = Column(Integer, nullable=False)
#     effective_from_date                 = Column(Date, nullable=False)
#     effective_to_date                   = Column(Date, default=None)

# class EmployeePresentAddress(caerp_base):
#     __tablename__ = "employee_present_address"

#     id                                 = Column(Integer, primary_key=True, autoincrement=True)
#     employee_id                        = Column(Integer, nullable=False)
#     present_house_or_flat_name         = Column(String(50), default=None)
#     present_house_flat_or_door_number  = Column(String(50), default=None)
#     present_road_name                  = Column(String(50), default=None)
#     present_street_name                = Column(String(50), default=None)
#     present_land_mark                  = Column(String(50), default=None)
#     present_pin_code                   = Column(String(20), default=None)
#     present_post_office_id             = Column(Integer, nullable=False)
#     present_city_id                    = Column(Integer, nullable=False)
#     present_taluk_id                   = Column(Integer, nullable=False)
#     present_district_id                = Column(Integer, nullable=False)
#     present_state_id                   = Column(Integer, nullable=False)
#     present_country_id                 = Column(Integer, nullable=False)
#     effective_from_date                = Column(Date, nullable=False)
#     effective_to_date                  = Column(Date, default=None)

# class EmployeeContactDetails(caerp_base):
#     __tablename__ = "employee_contact_details"    

#     id                          = Column(Integer, primary_key=True, autoincrement=True)
#     employee_id                 = Column(Integer, nullable=False)
#     personal_mobile_number      = Column(String(15), default=None)
#     personal_whatsapp_number    = Column(String(15), default=None)
#     personal_email_id           = Column(String(50), default=None) 
#     official_mobile_number      = Column(String(15), default=None)
#     official_whatsapp_number    = Column(String(15), default=None)
#     official_email_id           = Column(String(50), default=None)
#     effective_from_date         = Column(Date, nullable=False)
#     effective_to_date           = Column(Date, default=None)

# class EmployeeBankDetails(caerp_base):
#     __tablename__ = "employee_bank_details"    

#     id                     = Column(Integer, primary_key=True, autoincrement=True)
#     employee_id            = Column(Integer, nullable=False)
#     bank_account_number    = Column(String(15), default=None) 
#     bank_name              = Column(String(50), default=None)    
#     bank_branch_name       = Column(String(50), default=None)
#     ifsc_code              = Column(String(15), default=None)
#     effective_from_date    = Column(Date, nullable=False)
#     effective_to_date      = Column(Date, default=None)

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

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, nullable=False)
    bank_account_number = Column(String(15), default=None)
    bank_name = Column(String(50), default=None)
    bank_branch_name = Column(String(50), default=None)
    ifsc_code = Column(String(15), default=None)
    effective_from_date = Column(Date, nullable=False)
    effective_to_date = Column(Date, default=None)
    remarks = Column(String(1000), default=None)
    created_by = Column(Integer, nullable=False, default=0)
    created_on = Column(DateTime, nullable=False, default=func.now())
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, default=None)
    deleted_on = Column(DateTime, default=None)

class EmployeeEmployementDetails(caerp_base):
    __tablename__ = "employee_employement_details"

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
    next_increment_date          = Column(Date, default=None)
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on                  = Column(DateTime, nullable=False, default=func.now())
    is_approved                 = Column(Enum('yes', 'no'), nullable=False, default='no')
    approved_by                 = Column(Integer, nullable=False)
    approved_on                 = Column(DateTime, nullable=False)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, default=None)
    deleted_on                  = Column(DateTime, default=None)



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
    effective_date_from  = Column(Date, nullable=False)
    effective_date_to    = Column(Date, default=None) 
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
    effective_date_from  = Column(Date, nullable=False)
    effective_date_to    = Column(Date, default=None)
    created_by           = Column(Integer, nullable=False, default=0)
    created_on           = Column(DateTime, nullable=False, default=func.now())
    is_deleted           = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by           = Column(Integer, default=None)
    deleted_on           = Column(DateTime, default=None)

class EmployeeProfessionalQualification(caerp_base):
    __tablename__ = "employee_professional_qualifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer,nullable=False)
    qualification_id = Column(Integer,nullable=False)
    membership_number = Column(String(50), default=None)
    enrollment_date = Column(Date, nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
class EmployeeEducationalQualification(caerp_base):
    __tablename__ = "employee_educational_qualification"    

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer,nullable=False)
    qualification_name = Column(String(100), default=None)
    institution = Column(String(100), default=None)
    percentage_or_grade = Column(String(100), default=None)
    month_and_year_of_completion = Column(String(50), default=None)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False, default=func.now())
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, default=None)
    deleted_on = Column(DateTime, default=None)
    
    
