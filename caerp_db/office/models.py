
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

class OffAppointmentVisitDetails(caerp_base):
    __tablename__ = 'off_appointment_visit_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_master_id = Column(Integer, nullable=False)
    consultant_id = Column(Integer, nullable=False)
    service_id = Column(Integer, nullable=False)
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
    service_master_id= Column(Integer, nullable=True)
    consultation_fee=Column(Float, nullable=False)
    consultancy_services_igst_rate=Column(Float, nullable=False)
    available_time_from=Column(Time, nullable=False) 
    available_time_to= Column(Time, nullable=True) 
    slot_duration_in_minutes= Column(Integer, nullable=True)
    consultancy_services_effective_from_date= Column(Date, nullable=True)
    consultancy_services_effective_to_date= Column(Date, nullable=True)
    consultancy_services_is_deleted= Column(Enum('yes', 'no'), nullable=False, default='no')
    consultant_id= Column(Integer, nullable=True)
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
    hsn_sac_class = Column(String(100), nullable=False)
    group_id = Column(Integer, nullable=False)
    service_goods_group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    service_goods_sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    service_goods_category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    service_goods_sub_category_name = Column(String(200), nullable=True)
    service_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=False)
    hsn_sac_description = Column(String(2000), nullable=True)
    gst = Column(String(2), nullable=False)
    sku_code_id = Column(Integer, nullable=False)
    stock_keeping_unit_code = Column(String(250), nullable=True)
    is_consultancy_service = Column(Enum('yes', 'no'), nullable=False)
    is_bundled_service = Column(Enum('yes', 'no'), nullable=False)
    service_goods_master_created_by = Column(Integer, nullable=False)
    service_goods_master_created_on = Column(DateTime, nullable=False)
    service_goods_master_modified_by = Column(Integer, nullable=True)
    service_goods_master_modified_on = Column(DateTime, nullable=True)
    service_goods_master_is_deleted = Column(Enum('yes', 'no'), nullable=False)
    service_goods_master_deleted_by = Column(Integer, nullable=True)
    service_goods_master_deleted_on = Column(DateTime, nullable=True)

