
from sqlalchemy import Column, Integer, String,BigInteger,Date,Float,Enum,Time
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column ,DateTime


class OffAppointmentMaster(caerp_base):
    __tablename__  =  "off_appointment_master"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    full_name 	 = Column(String(200), nullable=False)
    customer_number=Column(String(100), nullable=True)
    mobile_number  = Column(String(20), nullable=True)
    whatsapp_number=Column(String(20), nullable=True)
    email_id  = Column(String(50), nullable=True)
    gender_id= Column(Integer, nullable=True)
    locality=Column(String(50), nullable=True)
    pin_code=Column(String(50), nullable=True)
    post_office_id= Column(Integer, nullable=True)
    taluk_id= Column(Integer, nullable=True)
    district_id= Column(Integer, nullable=True)
    state_id= Column(Integer, nullable=True)
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
    financial_year_id = Column(Integer, nullable=True)
    voucher_number = Column(String(50), nullable=True)
    appointment_master_id = Column(Integer, nullable=False)
    appointment_date = Column(Date, nullable=True)
    appointment_time_from = Column(String(50), nullable=True) 
    appointment_time_to = Column(String(50), nullable=True)
    source_of_enquiry_id = Column(Integer, nullable=False)
    appointment_status_id = Column(Integer, nullable=False)
    consultant_id = Column(Integer, nullable=False)
    gross_amount = Column(Float, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    special_discount_percentage = Column(Float, nullable=False)
    special_discount_amount = Column(Float, nullable=False)
    net_amount = Column(Float, nullable=False)
    igst_amount = Column(Float, nullable=False)
    sgst_amount = Column(Float, nullable=False)
    cgst_amount = Column(Float, nullable=False)
    bill_amount = Column(Float, nullable=False)
    remarks = Column(String(1000), nullable=True)
    created_by = Column(Integer, nullable=True)
    created_on = Column(Date, nullable=True)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(Date, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(Date, nullable=True)




class OffAppointmentVisitMasterView(caerp_base):
    __tablename__ = 'off_view_appointment_master'

   
    appointment_master_id= Column(Integer,  primary_key=True,nullable=False)
    full_name 	 = Column(String(200), nullable=False)
    gender_id= Column(Integer, nullable=False)
    customer_number=Column(String(100), nullable=True)
    mobile_number  = Column(String(20), nullable=True)
    whatsapp_number=Column(String(20), nullable=True)
    email_id  = Column(String(50), nullable=True)
    locality=Column(String(50), nullable=True)
    pin_code=Column(String(50), nullable=True)
    appointment_master_post_office_id= Column(Integer, nullable=True)
    post_office_name = Column(String(255), nullable=True)
    contact_number=Column(String(50), nullable=True)
    appointment_master_taluk_id= Column(Integer, nullable=True)
    taluk_name = Column(String(255), nullable=True)
    appointment_master_district_id= Column(Integer, nullable=True)
    district_name= Column(String(255), nullable=True)
    appointment_master_state_id= Column(Integer, nullable=True)
    state_name= Column(String(255), nullable=True)
    state_code= Column(Integer, nullable=True)
    gst_registration_name= Column(String(255), nullable=True)
    appointment_master_created_by= Column(Integer, nullable=True)
    appointment_master_created_on= Column(Date, nullable=True)
    appointment_master_modified_by= Column(Integer, nullable=True)
    appointment_master_modified_on= Column(Date, nullable=True)
    appointment_master_is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    appointment_master_deleted_by= Column(Integer, nullable=True)
    appointment_master_deleted_on= Column(Date, nullable=True)
    appointment_visit_master_id= Column(Integer, nullable=True)
    financial_year_id= Column(Integer, nullable=True)
    voucher_number=Column(String(50), nullable=True)
    appointment_date= Column(Date, nullable=True)
    appointment_time_from= Column(String(50), nullable=True)  
    appointment_time_to= Column(String(50), nullable=True)  
    source_of_enquiry_id= Column(Integer, nullable=True)
    source= Column(String(100), nullable=True)
    appointment_status_id= Column(Integer, nullable=True)
    appointment_status= Column(String(100), nullable=True)
    appointment_visit_master_consultant_id= Column(Integer, nullable=True)
    employee_master_employee_number=Column(String(50), nullable=True)
    employee_master_first_name=Column(String(50), nullable=True)
    employee_master_middle_name=Column(String(50), nullable=True)
    employee_master_last_name=Column(String(50), nullable=True)
    gross_amount=Column(Float, nullable=True)
    discount_percentage=Column(Float, nullable=True)
    special_discount_percentage=Column(Float, nullable=True)
    special_discount_amount=Column(Float, nullable=True)
    net_amount=Column(Float, nullable=True)
    igst_amount=Column(Float, nullable=True)
    sgst_amount=Column(Float, nullable=True)
    cgst_amount=Column(Float, nullable=True)
    bill_amount=Column(Float, nullable=True)
    remarks= Column(String(2000), nullable=True)



class OffAppointmentVisitDetails(caerp_base):
    __tablename__ = 'off_appointment_visit_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_master_id = Column(Integer, nullable=False)
    consultant_id = Column(Integer, nullable=False)
    service_id = Column(Integer, nullable=False)
    is_main_service= Column(Enum('yes', 'no'), nullable=False, default='no')
    created_by = Column(Integer, nullable=True)
    created_on = Column(Date, nullable=True)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(Date, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(Date, nullable=True)

class OffAppointmentVisitDetailsView(caerp_base):
    __tablename__ = 'off_view_appointment_details'

    appointment_visit_details_id= Column(Integer, primary_key=True, nullable=False)
    visit_master_id= Column(Integer, nullable=False)
    appointment_visit_master_financial_year_id= Column(Integer, nullable=True)
    appointment_visit_master_voucher_number=Column(String(50), nullable=True)
    appointment_visit_master_appointment_master_id= Column(Integer, nullable=True)
    appointment_visit_master_appointment_date= Column(Date, nullable=True)
    appointment_visit_master_appointment_time_from= Column(String(50), nullable=False)  
    appointment_visit_master_appointment_time_to= Column(String(50), nullable=True)  
    source_of_enquiry_id= Column(Integer, nullable=True)
    appointment_status_id= Column(Integer, nullable=True)
    appointment_visit_master_gross_amount=Column(Float, nullable=False)
    appointment_visit_master_discount_percentage=Column(Float, nullable=False)
    special_discount_percentage=Column(Float, nullable=False)
    special_discount_amount=Column(Float, nullable=False)
    appointment_visit_master_net_amount=Column(Float, nullable=False)
    appointment_visit_master_igst_amount=Column(Float, nullable=False)
    appointment_visit_master_sgst_amount=Column(Float, nullable=False)
    appointment_visit_master_cgst_amount=Column(Float, nullable=False)
    appointment_visit_master_bill_amount=Column(Float, nullable=False)
    remarks= Column(String(2000), nullable=False)
    service_id= Column(Integer, nullable=True)
    service_goods_name= Column(String(500), nullable=False)  
    consultant_id= Column(Integer, nullable=True)
    appointment_detail_is_main_service= Column(Enum('yes', 'no'), nullable=False, default='no')
    employee_master_employee_number=Column(String(50), nullable=True)
    employee_master_first_name=Column(String(50), nullable=True)
    employee_master_middle_name=Column(String(50), nullable=True)
    employee_master_last_name=Column(String(50), nullable=True)
    appointment_visit_details_created_by= Column(Integer, nullable=True)
    appointment_visit_details_created_on= Column(Date, nullable=True)
    appointment_visit_details_modified_by= Column(Integer, nullable=True)
    appointment_visit_details_modified_on= Column(Date, nullable=True)
    appointment_visit_details_is_deleted= Column(Enum('yes', 'no'), nullable=False, default='no')
    appointment_visit_details_deleted_by= Column(Integer, nullable=True)
    appointment_visit_details_deleted_on= Column(Date, nullable=True)
    
class OffAppointmentCancellationReason(caerp_base):
    __tablename__ = 'off_appointment_cancellation_reason'

    id = Column(Integer, primary_key=True, autoincrement=True)
    off_appointment_cancellation_reason = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class OffAppointmentStatus(caerp_base):
    __tablename__ = 'off_appointment_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_status = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
 
class OffServices(caerp_base):
    __tablename__ = 'off_service_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(500), nullable=False)
    is_consultancy_service = Column(Enum('yes', 'no'), nullable=False, default='no')
    has_sub_service= Column(Enum('yes', 'no'), nullable=False, default='no')
    hsn_sac_id = Column(Integer, nullable=False)
    service_provider_id = Column(Integer, nullable=False)
    service_department_id = Column(Integer, nullable=False)
    service_frequency_id = Column(Integer, nullable=False)
    sku_code_id = Column(Integer, nullable=False)
   
    purchase_price = Column(Float, default=None)
    selling_price = Column(Float, default=None)
    igst_rate = Column(Float, default=None)
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
    
    effective_from_date = Column(Date, default=None)
    effective_to_date = Column(Date, default=None)
    created_by = Column(Integer, nullable=True)
    created_on = Column(Date, nullable=True)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(Date, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(Date, nullable=True)

#..........................by swathy 15/5----------------------------------

class AppHsnSacClasses(caerp_base):
    __tablename__ = 'app_hsn_sac_classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

    
class OffServiceGoodsGroup(caerp_base):
    __tablename__ = 'off_service_goods_group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_classess_id = Column(Integer, nullable=False)
    group_name = Column(String(250), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class OffServiceGoodsSubGroup(caerp_base):
    __tablename__ = 'off_service_goods_sub_group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, nullable=False)
    sub_group_name = Column(String(100), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffServiceGoodsCategory(caerp_base):
    __tablename__ = 'off_service_goods_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_group_id = Column(Integer, nullable=False)
    category_name = Column(String(200), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffServiceGoodsSubCategory(caerp_base):
    __tablename__ = 'off_service_goods_sub_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    sub_category_name = Column(String(200), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class OffViewServiceGoodsMaster(caerp_base): 
    __tablename__ = 'off_view_service_goods_master'
    
    service_goods_master_id = Column(Integer, primary_key=True, nullable=False)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_class = Column(String(100), nullable=True)
    group_id = Column(Integer, nullable=False)
    service_goods_group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    service_goods_sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    service_goods_category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    service_goods_sub_category_name = Column(String(200), nullable=True)
    service_goods_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=True)
    hsn_sac_description = Column(String(2000), nullable=True)
    gst = Column(String(2), nullable=False)
    sku_code_id = Column(Integer, nullable=False)
    stock_keeping_unit_code = Column(String(250), nullable=True)
    has_consultation = Column(Enum('yes', 'no'), nullable=False)
    is_bundled_service = Column(Enum('yes', 'no'), nullable=False)
    service_goods_master_created_by = Column(Integer, nullable=False)
    service_goods_master_created_on = Column(DateTime, nullable=False)
    service_goods_master_modified_by = Column(Integer, nullable=True)
    service_goods_master_modified_on = Column(DateTime, nullable=True)
    service_goods_master_is_deleted = Column(Enum('yes', 'no'), nullable=False)
    service_goods_master_deleted_by = Column(Integer, nullable=True)
    service_goods_master_deleted_on = Column(DateTime, nullable=True)

#-------------Aparna...........
class OffConsultantMaster(caerp_base):
    __tablename__ = 'off_consultant_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, nullable=False)
    available_date_from = Column(Date, nullable=False)
    available_date_to = Column(Date, nullable=True)
    available_time_from = Column(Time, nullable=False)
    available_time_to = Column(Time, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_by = Column(Integer, nullable=True, default=None)
    modified_on = Column(DateTime, nullable=True, default=None)

class OffConsultantDetails(caerp_base):
    __tablename__ = 'off_consultant_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, nullable=False)
    service_goods_master_id = Column(Integer, nullable=False)
    consultation_fee = Column(Float, nullable=False)
    slot_duration_in_minutes = Column(Integer, nullable=False)
    effective_from_date = Column(DateTime, nullable=False)
    effective_to_date = Column(DateTime, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    
class OffViewConsultantMaster(caerp_base):
    __tablename__ = 'off_view_consultant_master'

    consultant_master_id = Column(Integer, primary_key=True)
    consultant_id = Column(Integer)
    employee_number = Column(String)
    first_name = Column(String)
    middle_name = Column(String, nullable=True)
    last_name = Column(String)
    consultant_master_available_date_from = Column(Date)
    consultant_master_available_date_to = Column(Date)
    consultant_master_available_time_from = Column(Time)
    consultant_master_available_time_to = Column(Time)
    consultant_master_created_by = Column(Integer)
    consultant_master_created_on = Column(DateTime)
    consultant_master_modified_by = Column(Integer, nullable=True)
    consultant_master_modified_on = Column(DateTime, nullable=True)
    
    
# class OffViewConsultantDetails(caerp_base):
#     __tablename__ = 'off_view_consultant_details'

#     consultant_details_id = Column(Integer, primary_key=True)
#     consultant_id = Column(Integer)
#     employee_number = Column(String)
#     first_name = Column(String)
#     middle_name = Column(String, nullable=True)
#     last_name = Column(String)
#     service_goods_master_id = Column(Integer)
#     hsn_sac_class_id = Column(Integer)
#     hsn_sac_class = Column(String)
#     group_id = Column(Integer)
#     group_name = Column(String)
#     sub_group_id = Column(Integer)
#     sub_group_name = Column(String)
#     category_id = Column(Integer)
#     category_name = Column(String)
#     sub_category_id = Column(Integer)
#     sub_category_name = Column(String)
#     service_name = Column(String)
#     hsn_sac_id = Column(Integer)
#     hsn_sac_code = Column(String)
#     hsn_sac_description = Column(String)
#     sku_code_id = Column(Integer)
#     unit_code = Column(String)
#     is_consultancy_service = Column(Integer)
#     is_bundled_service = Column(Integer)
#     service_goods_master_modified_by = Column(Integer)
#     service_goods_master_modified_on = Column(DateTime)
#     service_goods_master_is_deleted = Column(String)
#     service_goods_master_deleted_by = Column(Integer)
#     service_goods_master_deleted_on = Column(DateTime)
#     consultation_fee = Column(Float)
#     slot_duration_in_minutes = Column(Integer)
#     consultant_details_effective_from_date = Column(DateTime)
#     consultant_details_effective_to_date = Column(DateTime, nullable=True)
#     consultant_details_created_by = Column(Integer)
#     consultant_details_created_on = Column(DateTime)
    
class OffViewConsultantDetails(caerp_base):
    __tablename__ = 'off_view_consultant_details'

    consultant_details_id = Column(Integer, primary_key=True)
    consultant_id = Column(Integer)
    employee_number = Column(String)
    first_name = Column(String)
    middle_name = Column(String, nullable=True)
    last_name = Column(String)
    service_goods_master_id = Column(Integer)
    hsn_sac_class_id = Column(Integer)
    hsn_sac_class = Column(String)
    group_id = Column(Integer)
    group_name = Column(String)
    sub_group_id = Column(Integer)
    sub_group_name = Column(String)
    category_id = Column(Integer)
    category_name = Column(String)
    sub_category_id = Column(Integer)
    sub_category_name = Column(String)
    service_goods_name = Column(String)  
    hsn_sac_id = Column(Integer)
    hsn_sac_code = Column(String)
    hsn_sac_description = Column(String)
    sku_code_id = Column(Integer)
    unit_code = Column(String)
    # is_consultancy_service = Column(Integer)
    has_consultation=Column(Integer)
    is_bundled_service = Column(Integer)
    service_goods_master_modified_by = Column(Integer)
    service_goods_master_modified_on = Column(DateTime)
    service_goods_master_is_deleted = Column(String)
    service_goods_master_deleted_by = Column(Integer)
    service_goods_master_deleted_on = Column(DateTime)
    consultation_fee = Column(Float)
    slot_duration_in_minutes = Column(Integer)
    consultant_details_effective_from_date = Column(DateTime)
    consultant_details_effective_to_date = Column(DateTime, nullable=True)
    consultant_details_created_by = Column(Integer)
    consultant_details_created_on = Column(DateTime)
    
class OffServiceGoodsMaster(caerp_base):
    __tablename__ = 'off_service_goods_master'
    id = Column(Integer, primary_key=True, index=True)
    hsn_sac_class_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    sub_group_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    sub_category_id = Column(Integer, nullable=False)
    service_goods_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    sku_code_id = Column(Integer, nullable=False)
    has_consultation = Column(Enum('yes', 'no'), default='no', nullable=False)
    is_bundled_service = Column(Enum('yes', 'no'), default='no', nullable=False)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)

class OffServiceGoodsDetails(caerp_base):
        
    __tablename__ = 'off_service_goods_details'
    id = Column(Integer, primary_key=True, index=True)
    service_goods_master_id = Column(Integer, nullable=False)
    bundled_service_goods_id = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True) 
  
  
class OffViewServiceGoodsDetails(caerp_base):
    __tablename__ = 'off_view_service_goods_details'

    service_goods_details_id = Column(Integer, primary_key=True, nullable=False)
    service_goods_master_id = Column(Integer, nullable=False)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_class = Column(String(100), nullable=False)
    group_id = Column(Integer, nullable=False)
    service_master_group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    service_master_sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    service_master_category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    service_master_sub_category_name = Column(String(200), nullable=True)
    service_goods_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=False)
    hsn_sac_description = Column(String(2000), nullable=True)
    sku_code_id = Column(Integer, nullable=False)
    stock_keeping_unit_code = Column(String(250), nullable=True)
    has_consultation = Column(Enum('yes', 'no'), nullable=False)
    is_bundled_service = Column(Enum('yes', 'no'), nullable=False)
    bundled_service_goods_id = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=True)
    service_goods_details_created_by = Column(Integer, nullable=False)
    service_goods_details_created_on = Column(DateTime, nullable=False)
    service_goods_details_modified_by = Column(Integer, nullable=True)
    service_goods_details_modified_on = Column(DateTime, nullable=True)
    service_goods_details_is_deleted = Column(Enum('yes', 'no'), nullable=False)
    service_goods_details_deleted_by = Column(Integer, nullable=True)
    service_goods_details_deleted_on = Column(DateTime, nullable=True)


#--------------------

class OffViewServiceGoodsPriceMaster(caerp_base):
    __tablename__ = 'off_view_service_goods_price_master'

    service_goods_price_master_id = Column(Integer, primary_key=True)
    service_goods_master_id = Column(Integer)
    hsn_sac_class_id = Column(Integer)
    hsn_sac_class = Column(String)
    group_id = Column(Integer)
    group_name = Column(String)
    sub_group_id = Column(Integer)
    sub_group_name = Column(String)
    category_id = Column(Integer)
    category_name = Column(String)
    sub_category_id = Column(Integer)
    sub_category_name = Column(String)
    service_goods_name = Column(String)
    hsn_sac_id = Column(Integer)
    hsn_sac_code = Column(String)
    hsn_sac_description = Column(String)
    sku_code_id = Column(Integer)
    unit_code = Column(String)
    has_consultation = Column(Integer)
    # is_consultancy_service = Column(Integer)
    is_bundled_service = Column(Integer)
    services_goods_master_modified_by = Column(Integer)
    services_goods_master_modified_on = Column(DateTime)
    services_goods_master_is_deleted = Column(String)
    services_goods_master_deleted_by = Column(Integer)
    services_goods_master_deleted_on = Column(DateTime)
    constitution_id = Column(Integer)
    business_constitution_name = Column(String)
    business_constitution_code = Column(String)
    business_constitution_description = Column(String)
    pan_code = Column(String)
    service_charge = Column(Float)
    govt_agency_fee = Column(Float)
    stamp_duty = Column(Float)
    stamp_fee = Column(Float)
    effective_from_date = Column(DateTime)
    effective_to_date = Column(DateTime)
    service_goods_price_master_created_by = Column(Integer)
    service_goods_price_master_created_on = Column(DateTime)
    
class OffServiceGoodsPriceMaster(caerp_base):
    __tablename__ = 'off_service_goods_price_master'
    
    id = Column(Integer, primary_key=True, index=True)
    service_goods_master_id = Column(Integer,nullable=False)
    constitution_id = Column(Integer, nullable=False)
    service_charge = Column(Float, default=0.00)
    govt_agency_fee = Column(Float, default=0.00)
    stamp_duty = Column(Float, default=0.00)
    stamp_fee = Column(Float, default=0.00)
    effective_from_date = Column(Date, nullable=False)
    effective_to_date = Column(Date, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    
    

class AppHsnSacMaster(caerp_base):
    __tablename__ = 'app_hsn_sac_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), unique=True, nullable=False)
    hsn_sac_description = Column(String(2000), default=None)
    sku_code = Column(String(20), default=None)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)


class AppStockKeepingUnitCode(caerp_base):
    __tablename__ = 'app_stock_keeping_unit_code'

    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_code = Column(String(250), default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class AppBusinessConstitution(caerp_base):
    __tablename__ = 'app_business_constitution'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_constitution_name = Column(String(100), nullable=False)
    business_constitution_code = Column(String(100), nullable=False)
    description = Column(String(500), default=None)
    pan_code = Column(String(10), default=None)
    display_order = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    


class OffDocumentDataMaster(caerp_base):
    __tablename__ = 'off_document_data_master'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_data_type_id = Column(Integer, nullable=False)
    document_data_name = Column(String(200), nullable=False)
    has_expiry = Column(Enum('yes', 'no'), default='no', nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
class OffDocumentDataType(caerp_base):
    __tablename__ = 'off_document_data_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_data_type = Column(String(200), nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffDocumentDataCategory(caerp_base):
    __tablename__ = 'off_document_data_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(200), nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffNatureOfPossession(caerp_base):
    __tablename__ = 'off_nature_of_possession'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nature_of_possession = Column(String(200), nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
class OffServiceDocumentDataMaster(caerp_base):
    __tablename__ = 'off_service_document_data_master'
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_goods_master_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    sub_group_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    sub_category_id = Column(Integer, nullable=False)
    constitution_id = Column(Integer, nullable=False)
  
 

class OffServiceDocumentDataDetails(caerp_base):
    __tablename__ = 'off_service_document_data_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_data_category_id = Column(Integer, nullable=False)
    service_document_data_id = Column(Integer, nullable=False)
    document_data_id = Column(Integer, nullable=False)
    nature_of_possession_id = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=False,default=1)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')



class OffViewServiceDocumentsDataDetails(caerp_base):
    __tablename__ = 'off_view_service_documents_data_details'
   
    service_document_data_details_id = Column(Integer, primary_key=True, nullable=False)
    document_data_category_id = Column(Integer, nullable=False)
    document_data_category_category_name = Column(String(200), nullable=False)
    service_document_data_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    group_name = Column(String(250))
    sub_group_id = Column(Integer, nullable=False)
    sub_group_name = Column(String(100))
    category_id = Column(Integer, nullable=False)
    category_name = Column(String(200))
    sub_category_id = Column(Integer, nullable=False)
    sub_category_name = Column(String(200))
    constitution_id = Column(Integer, nullable=False)
    business_constitution_name = Column(String(100), nullable=False)
    business_constitution_code = Column(String(100), nullable=False)
    description = Column(String(500))
    document_data_id = Column(Integer, nullable=False)
    document_data_type_id = Column(Integer, nullable=False)
    document_data_type = Column(String(200), nullable=False)
    document_data_name = Column(String(200), nullable=False)
    has_expiry = Column(Enum('yes', 'no'), nullable=False)
    nature_of_possession_id = Column(Integer)
    nature_of_possession = Column(String(200), nullable=False)
    display_order = Column(Integer, nullable=False)
    service_document_data_details_is_deleted = Column(Enum('yes', 'no'), nullable=False) 
    
class OffViewServiceDocumentsDataMaster(caerp_base):
    __tablename__ = 'off_view_service_documents_data_master'

    service_document_data_master_id = Column(Integer, primary_key=True)
    service_goods_master_id =Column(Integer, nullable=False)
    service_goods_name = Column(String(500), nullable=False)
    group_id = Column(Integer, nullable=False)
    group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    sub_category_name = Column(String(200), nullable=True)
    constitution_id = Column(Integer, nullable=False)
    business_constitution_name = Column(String(100), nullable=False)
    business_constitution_code = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
   
#--------------------aparna
class OffAppointmentRecommendationMaster(caerp_base):
    __tablename__ = 'off_appointment_recommendation_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_master_id = Column(Integer, nullable=False)
    visit_master_id = Column(Integer,nullable=False)
    service_goods_master_id = Column(Integer,nullable=False)
    constitution_id = Column(Integer,nullable=False)
    has_branches_or_godowns = Column(Enum('yes', 'no'), nullable=False, default='no')
    number_of_branches_or_godowns = Column(Integer, nullable=False, default=0)
    created_by = Column(Integer, default=None)
    created_on = Column(Date, default=None)
    modified_by = Column(Integer, default=None)
    modified_on = Column(Date, default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, default=None)
    deleted_on = Column(Date, default=None)

class OffAppointmentPlaceOfBusiness(caerp_base):
    __tablename__ = 'off_appointment_place_of_business'

    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_recommendation_master_id = Column(Integer, nullable=False, default='MAIN OFFICE')
    is_main_office = Column(Enum('yes', 'no'), nullable=False, default='no')
    nature_of_possession_id = Column(Integer,  nullable=False)
    utility_document_id = Column(Integer,  nullable=False)
    business_place_type = Column(Enum('MAIN OFFICE', 'GODOWN' ,'BRANCH'), nullable=False, default='no')
    created_by = Column(Integer, default=None)
    created_on = Column(Date, default=None)
    modified_by = Column(Integer, default=None)
    modified_on = Column(Date, default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, default=None)
    deleted_on = Column(Date, default=None)


