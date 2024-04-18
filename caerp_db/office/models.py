
from sqlalchemy import Column, Integer, String,BigInteger,Date,Float,Enum,Time
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column

class Document_Master(caerp_base):
    __tablename__ = 'off_document_master'
    
    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    document_name = Column(String(100),nullable=False)
    document_code = Column(String(100),nullable=True)
    is_deleted    = Column(Enum('yes', 'no'), default='no', nullable=False)


class ServiceProvider(caerp_base):
    __tablename__ = 'off_service_provider'

    id               = Column(Integer, primary_key=True, autoincrement=True)
    service_provider = Column(String(500), nullable=False)
    place            = Column(String(500), nullable=True)
    address_line_1   = Column(String(500), nullable=True)
    email_id         = Column(String(55), nullable=True)
    mobile_number    = Column(String(500), nullable=True)
    is_deleted       = Column(Enum('yes', 'no'), default='no', nullable=False)


class ServiceDepartments(caerp_base):
    __tablename__ = 'off_service_departments'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    service_department_name = Column(String(500), nullable=False)
    department_description  = Column(String(500), nullable=True)
    address_line_1          = Column(String(500), nullable=True)
    address_line_2          = Column(String(500), nullable=True)
    email_id                = Column(String(500), nullable=True)
    mobile_number           = Column(String(500), nullable=True)
    is_deleted              = Column(Enum('yes', 'no'), default='no', nullable=False)
     


class AppBusinessActivityType(caerp_base):
    __tablename__ = 'app_business_activity_type'

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    business_activity_type = Column(String(100))
    is_deleted             = Column(Enum('yes', 'no'), nullable=False, default='no')

class AppBusinessActivityMaster(caerp_base):
    __tablename__ = 'app_business_activity_master'

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    business_activity_type_id= Column(Integer,nullable=False)
    business_activity        = Column(String(250))
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')

# class AppEducationalQualificationsMaster(caerp_base):
#     __tablename__ = 'app_educational_qualifications'

#     id                       = Column(Integer, primary_key=True, autoincrement=True)
#     qualification            = Column(String(100),nullable=False)
#     is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')


class EnquirerType(caerp_base):
    __tablename__ = 'off_enquirer_type'

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    person_type              = Column(String(100),nullable=True)
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')

class EnquirerStatus(caerp_base):
    __tablename__ = 'off_enquiry_status'

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    status                   = Column(String(100),nullable=True)
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')


class ServiceProcessingStatus(caerp_base):
    __tablename__ = 'off_service_processing_status'

    id                         = Column(Integer, primary_key=True, autoincrement=True)
    service_processing_status  = Column(String(500),nullable=False)
    is_deleted                 = Column(Enum('yes', 'no'), nullable=False, default='no')


#-----------------------------------------------------------------------------------------------------
class OffServiceFrequency(caerp_base):
    __tablename__ = 'off_service_frequency'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_frequency = Column(String(500))
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
   

class AppStockKeepingUnitCode(caerp_base):
    __tablename__ = 'app_stock_keeping_unit_code'

    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_code = Column(String(250))
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    

class AppHsnSacClasses(caerp_base):
    __tablename__ = 'app_hsn_sac_classes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class = Column(String(100),nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class AppHsnSacMaster(caerp_base):
    __tablename__ = 'app_hsn_sac_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=True)
    hsn_sac_description = Column(String(1000), nullable=True)
    sku_code = Column(String(20), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffServices(caerp_base):
    __tablename__ = 'off_service_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    service_provider_id = Column(Integer, nullable=False)
    service_department_id = Column(Integer, nullable=False)
    service_frequency_id = Column(Integer, nullable=False)
    sku_code_id = Column(Integer, nullable=False)
    is_consultancy_service = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class ViewOffServices(caerp_base):
    __tablename__ = 'view_off_service_master'

    service_master_id = Column(Integer, primary_key=True)
    service_name = Column(String(500))
    hsn_sac_id = Column(Integer)
    hsn_sac_code = Column(String(20))
    hsn_sac_description = Column(String(1000))
    service_provider_id = Column(Integer)
    service_provider = Column(String(500))
    service_department_id = Column(Integer)
    service_department_name = Column(String(500))
    service_frequency_id = Column(Integer)
    service_frequency = Column(String(500))
    sku_code_id = Column(Integer)
    unit_code = Column(String(250))
    is_consultancy_service = Column(Enum('yes', 'no'))
    is_deleted = Column(Enum('yes', 'no'))


class OffAvailableServices(caerp_base):
    __tablename__ = 'off_available_services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_master_id = Column(Integer, nullable=False)
    is_main_service = Column(Enum('yes', 'no'), nullable=False, default='yes')
    main_service_id = Column(Integer, default=0)
    purchase_price = Column(Float, default=None)
    selling_price = Column(Float, default=None)
    gst_rate = Column(Float, default=None)
    cgst_rate = Column(Float, default=None)
    sgst_rate = Column(Float, default=None)
    cess_rate = Column(Float, default=None)
    discount_percentage = Column(Float, default=None)
    discount_amount = Column(Float, default=None)
    filing_day_from = Column(Integer, default=None)
    filing_day_to = Column(Integer, default=None)
    filing_month_from = Column(Integer, default=None)
    filing_month_to = Column(Integer, default=None)
    department_amount = Column(Float, default=None)
    days_required_for_processing = Column(Integer, default=None)
    display_order = Column(Integer, default=None)
    effective_from_date = Column(Date, default=None)
    effective_to_date = Column(Date, default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')



class ViewOffAvailableServices(caerp_base):
    __tablename__ = 'view_off_available_services'

    available_services_id = Column(Integer, primary_key=True)
    is_available = Column(String(10),nullable=False, default='yes')
    service_master_id = Column(Integer)
    service_name = Column(String(500))
    hsn_sac_id = Column(Integer)
    hsn_sac_description = Column(String(1000))
    is_main_service = Column(Enum('yes', 'no'))
    main_service_id = Column(Integer)
    purchase_price = Column(Float)
    selling_price = Column(Float)
    gst_rate = Column(Float)
    cgst_rate = Column(Float)
    sgst_rate = Column(Float)
    cess_rate = Column(Float)
    discount_percentage = Column(Float)
    discount_amount = Column(Float)
    filing_day_from = Column(Integer)
    filing_day_to = Column(Integer)
    filing_month_from = Column(Integer)
    filing_month_to = Column(Integer)
    department_amount = Column(Float)
    days_required_for_processing = Column(Integer)
    display_order = Column(Integer)
    effective_from_date = Column(Date)
    effective_to_date = Column(Date)
    off_available_services_is_deleted = Column(Enum('yes', 'no'))
    service_provider_id = Column(Integer)
    service_provider = Column(String(500))
    service_department_id = Column(Integer)
    service_department_name = Column(String(500))
    service_frequency_id = Column(Integer)
    service_frequency = Column(String(500))
    sku_code_id = Column(Integer)
    unit_code = Column(String(250))
    is_consultancy_service = Column(Enum('yes', 'no'))
    service_master_is_deleted = Column(Enum('yes', 'no'))
    
#------------------------------------------------------------------

class OffSourceOfEnquiry(caerp_base):
    __tablename__  =  "off_source_of_enquiry"
    
    id      = Column(Integer, primary_key=True, autoincrement=True)
    source 	 = Column(String(100), nullable=False)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')   


class OffAppointmentStatus(caerp_base):
    __tablename__  =  "off_appointment_status"
    id       = Column(Integer, primary_key=True, autoincrement=True)
    appointment_status 	 = Column(String(100), nullable=True)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')   


class OffAppointmentMaster(caerp_base):
    __tablename__  =  "off_appointment_master"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    full_name 	 = Column(String(200), nullable=False)
    appointment_number=Column(String(100), nullable=True)
    enquiry_number=Column(String(100), nullable=True)
    customer_number=Column(String(100), nullable=True)
    mobile_number  = Column(String(20), nullable=True)
    email_id  = Column(String(50), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')  
    created_by = Column(Integer, nullable=True)
    created_on = Column(Date, nullable=True)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(Date, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(Date, nullable=True)

class OffAppointmentVisitMaster(caerp_base):
    __tablename__ = 'off_appointment_visit_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_master_id = Column(Integer, nullable=False)
    appointment_date = Column(Date, nullable=True)
    source_of_enquiry_id = Column(Integer, nullable=False)
    appointment_status_id = Column(Integer, nullable=False)
    is_paid= Column(Enum('yes', 'no'), nullable=False, default='no')
    payment_mode_id= Column(Integer, nullable=True)
    payment_transaction_number= Column(String(100), nullable=True)
    payment_status_id= Column(Integer, nullable=True)
    payment_date= Column(Date, nullable=True)
    is_refunded= Column(Enum('yes', 'no'), nullable=False, default='no')
    refund_status_id= Column(Integer, nullable=True)
    refund_amount= Column(Float, nullable=True)
    refund_date= Column(Date, nullable=True)
    refund_reason_id= Column(Integer, nullable=True)
    refund_transaction_number= Column(String(100), nullable=True)
    service_charge= Column(Float, nullable=True)
    gst_percentage= Column(Float, nullable=True)
    sgst_percentage= Column(Float, nullable=True)
    cgst_percentage= Column(Float, nullable=True)
    discount_percentage= Column(Float, nullable=True)
    discount_amount= Column(Float, nullable=True)
    special_discount_percentage= Column(Float, nullable=True)
    special_discount_amount= Column(Float, nullable=True)
    net_amount= Column(Float, nullable=True)
    remarks= Column(String(1000), nullable=True)
    created_by = Column(Integer, nullable=True)
    created_on = Column(Date, nullable=True)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(Date, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_deleted_directly= Column(Enum('yes', 'no'), nullable=False, default='no')
    is_deleted_with_master= Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(Date, nullable=True)

class OffAppointmentVisitMasterView(caerp_base):
    __tablename__ = 'view_off_appointment_master'

    appointment_master_id= Column(Integer, primary_key=True)
    appointment_visit_master_id= Column(Integer)
    full_name= Column(String(100))
    appointment_number= Column(String(100))
    enquiry_number= Column(String(100))
    customer_number= Column(String(100))
    mobile_number= Column(String(100))
    email_id= Column(String(100))
    appointment_master_created_by= Column(Integer)
    appointment_master_created_on= Column(Date)
    appointment_master_modified_by= Column(Integer)
    appointment_master_modified_on= Column(Date)
    appointment_master_is_deleted= Column(Enum('yes', 'no'), nullable=False, default='no')
    appointment_master_deleted_by= Column(Integer)
    appointment_master_deleted_on= Column(Date)
    appointment_visit_master_appointment_date= Column(Date)
    appointment_visit_master_source_of_enquiry_id= Column(Integer)
    source= Column(String(100))
    appointment_visit_master_appointment_status_id= Column(Integer)
    is_paid= Column(Enum('yes', 'no'), nullable=False, default='no')
    appointment_status= Column(String(100))
    appointment_visit_master_payment_mode_id= Column(Integer)
    payment_mode= Column(String(100))
    appointment_visit_master_payment_transaction_number= Column(String(100))
    appointment_visit_master_payment_status_id= Column(Integer)
    payment_status= Column(String(100))
    appointment_visit_master_payment_date= Column(Date)
    appointment_visit_master_is_refunded= Column(String(100))
    appointment_visit_master_refund_status_id= Column(Integer)
    refund_status= Column(String(100))
    appointment_visit_master_refund_amount= Column(Integer)
    appointment_visit_master_refund_date= Column(Date)
    appointment_visit_master_refund_reason_id= Column(Integer)
    refund_reason= Column(String(100))
    appointment_visit_master_refund_transaction_number= Column(String(100))
    appointment_visit_master_service_charge= Column(Integer)
    appointment_visit_master_gst_percentage= Column(Integer)
    appointment_visit_master_sgst_percentage= Column(Integer)
    appointment_visit_master_cgst_percentage= Column(Integer)
    appointment_visit_master_discount_percentage= Column(Integer)
    appointment_visit_master_discount_amount= Column(Integer)
    appointment_visit_master_special_discount_percentage= Column(Integer)
    appointment_visit_master_special_discount_amount= Column(Integer)
    appointment_visit_master_net_amount= Column(Integer)
    appointment_visit_master_remarks= Column(String(100))
    appointment_visit_master_created_by= Column(Integer)
    appointment_visit_master_created_on= Column(Date)
    appointment_visit_master_modified_by= Column(Integer)
    appointment_visit_master_modified_on= Column(Date)
    appointment_visit_master_is_deleted=Column(Enum('yes', 'no'), nullable=False, default='no')
    appointment_visit_master_is_deleted_directly=Column(Enum('yes', 'no'), nullable=False, default='no')
    appointment_visit_master_is_deleted_with_master= Column(Enum('yes', 'no'), nullable=False, default='no')
    appointment_visit_master_deleted_by= Column(Integer)
    appointment_visit_master_deleted_on= Column(Date)






    
class OffAppointmentVisitDetails(caerp_base):
    __tablename__ = 'off_appointment_visit_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_master_id = Column(Integer, nullable=False)
    consultancy_service_id = Column(Integer, nullable=False)
    consultant_id = Column(Integer, nullable=False)
    appointment_time = Column(Time, nullable=False)  

    service_charge = Column(Float, nullable=True)
    gst_percentage = Column(Float, nullable=True)
    sgst_percentage = Column(Float, nullable=True)
    cgst_percentage = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    net_amount = Column(Float, nullable=True)
    remarks = Column(String(1000), nullable=True)
    created_by = Column(Integer, nullable=True)
    created_on = Column(Date, nullable=True)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(Date, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_deleted_directly = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_deleted_with_master = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(Date, nullable=True)



class OffAppointmentVisitDetailsView(caerp_base):
    __tablename__ = 'view_off_appointment_details'
    appointment_visit_details_id=Column(Integer, primary_key=True)
    appointment_visit_master_id= Column(Integer)
    appointment_master_id= Column(Integer)
    appointment_date= Column(Date)
    appointment_time= Column(Time)
    consultancy_service_id= Column(Integer)
    service_name= Column(String(100))
    consultant_id= Column(Integer)
    employee_number= Column(String(100))
    first_name= Column(String(100))
    middle_name= Column(String(100))
    last_name= Column(String(100))
    appointment_visit_details_service_charge= Column(Integer)
    appointment_visit_details_gst_percentage= Column(Integer)
    appointment_visit_details_sgst_percentage= Column(Integer)
    appointment_visit_details_cgst_percentage= Column(Integer)
    appointment_visit_details_discount_percentage= Column(Integer)
    appointment_visit_details_discount_amount= Column(Integer)
    appointment_visit_details_net_amount= Column(Integer)
    appointment_visit_details_remarks= Column(String(500))
    appointment_visit_details_created_by= Column(Integer)
    appointment_visit_details_created_on = Column(Date)
    
    appointment_visit_details_modified_by = Column(Integer)
    appointment_visit_details_modified_on = Column(Date)
    appointment_visit_details_is_deleted = Column(Enum('yes', 'no'))
   
    appointment_visit_details_is_deleted_directly= Column(Enum('yes', 'no'))
    appointment_visit_details_is_deleted_with_master= Column(Enum('yes', 'no'))
    appointment_visit_details_deleted_by= Column(Integer)
    appointment_visit_details_deleted_on= Column(Date)


class ConsultancyService(caerp_base):
    __tablename__ = 'off_consultancy_services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_master_id = Column(Integer, nullable=False)
    consultant_id = Column(Integer, nullable=False, default=0)
    consultation_fee = Column(Float)
    gst_rate = Column(Float)
    cgst_rate = Column(Float)
    sgst_rate = Column(Float)
    cess_rate = Column(Float)
    discount_percentage = Column(Float)
    discount_amount = Column(Float)
    available_time_from = Column(Time, nullable=False)
    available_time_to = Column(Time, nullable=False)
    slot_duration_in_minutes = Column(Integer, nullable=False)
    effective_from_date = Column(Date, nullable=False)
    effective_to_date = Column(Date, default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

#--------------------18-4-2024-----------------------------------------

class AppBusinessConstitution(caerp_base):
    __tablename__ = 'app_business_constitution'

    id                         = Column(BigInteger, primary_key=True, autoincrement=True)
    business_constitution_name = Column(String(100),nullable=False)
    business_constitution_code = Column(String(100),nullable=False)
    description                = Column(String(500))
    pan_code                   = Column(String(10))
    display_order              = Column(Integer, nullable=False, default=1)
    is_deleted                 = Column(Enum('yes', 'no'), nullable=False, default='no')
    

    
class ViewOffConsultancyServices(caerp_base):
    __tablename__ = 'view_off_consultancy_services'

    consultancy_service_id = Column(Integer, primary_key=True)
    service_master_id = Column(Integer)
    service_name = Column(String)
    consultant_id = Column(Integer)
    employee_number = Column(Integer)
    consultant_first_name = Column(String)
    consultant_middle_name = Column(String)
    consultant_last_name = Column(String)
    consultation_fee = Column(Float)
    gst_rate = Column(Float)
    cgst_rate = Column(Float)
    sgst_rate = Column(Float)
    cess_rate = Column(Float)
    discount_percentage = Column(Float)
    discount_amount = Column(Float)
    available_time_from = Column(Time)
    available_time_to = Column(Time)
    slot_duration_in_minutes = Column(Integer)
    effective_from_date = Column(Date)
    effective_to_date = Column(Date)
    is_deleted = Column(String)
