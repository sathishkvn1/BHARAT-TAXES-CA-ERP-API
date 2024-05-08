from sqlalchemy import Column, Integer, String,BigInteger,Date,Float,Enum,Time
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column

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

    appointment_master_id = Column(Integer,  primary_key=True,nullable=False)
    full_name 	 = Column(String(200), nullable=False)
    gender_id= Column(Integer, nullable=False)
    customer_number=Column(String(100), nullable=True)
    mobile_number  = Column(String(20), nullable=True)
    whatsapp_number=Column(String(20), nullable=True)
    email_id  = Column(String(50), nullable=True)
    locality=Column(String(50), nullable=True)
    pin_code=Column(String(50), nullable=True)
    appointment_master_post_office_id= Column(Integer, nullable=True)
    post_office_name = Column(String(255), nullable=False)
    contact_number=Column(String(50), nullable=True)
    appointment_master_taluk_id= Column(Integer, nullable=True)
    taluk_name = Column(String(255), nullable=False)
    appointment_master_district_id= Column(Integer, nullable=True)
    district_name= Column(String(255), nullable=False)
    appointment_master_state_id= Column(Integer, nullable=True)
    state_name= Column(String(255), nullable=False)
    state_code= Column(Integer, nullable=True)
    gst_registration_name= Column(String(255), nullable=False)
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
    appointment_time_from= Column(String(50), nullable=False)  
    appointment_time_to= Column(String(50), nullable=True)  
    source_of_enquiry_id= Column(Integer, nullable=True)
    source= Column(String(100), nullable=False)
    appointment_status_id= Column(Integer, nullable=True)
    appointment_status= Column(String(100), nullable=False)
    appointment_visit_master_consultant_id= Column(Integer, nullable=True)
    employee_master_employee_number=Column(String(50), nullable=True)
    employee_master_first_name=Column(String(50), nullable=True)
    employee_master_middle_name=Column(String(50), nullable=True)
    employee_master_last_name=Column(String(50), nullable=True)
    gross_amount=Column(Float, nullable=False)
    discount_percentage=Column(Float, nullable=False)
    special_discount_percentage=Column(Float, nullable=False)
    special_discount_amount=Column(Float, nullable=False)
    net_amount=Column(Float, nullable=False)
    igst_amount=Column(Float, nullable=False)
    sgst_amount=Column(Float, nullable=False)
    cgst_amount=Column(Float, nullable=False)
    bill_amount=Column(Float, nullable=False)
    remarks= Column(String(2000), nullable=False)

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
    available_time_from=Column(String(50), nullable=False) 
    available_time_to= Column(String(50), nullable=True) 
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

