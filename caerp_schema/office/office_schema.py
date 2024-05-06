from pydantic import BaseModel, constr,validator
from typing import List,Dict,Optional
from typing import Dict, Any,Union
import re

from datetime import date, datetime,time


class OffAppointmentMasterSchema(BaseModel):
    
    full_name: str
    customer_number: str
    mobile_number: Optional[str]
    whatsapp_number: Optional[str]
    email_id: Optional[str]
    locality : Optional[str]
    pin_code : Optional[str]
    post_office_id: Optional[int]
    taluk_id: Optional[int]
    
    district_id: Optional[int]
    state_id: Optional[int]

class OffAppointmentVisitMasterSchema(BaseModel):
    financial_year_id: Optional[int]
    voucher_number: Optional[str]
    # appointment_master_id : int
    appointment_date : Optional[date]
    appointment_time_from: Optional[str] 
    appointment_time_to: Optional[str]
    source_of_enquiry_id : Optional[int]
    appointment_status_id: Optional[int]
    consultant_id: Optional[int]
    gross_amount: Optional[int]
    discount_percentage: Optional[int]
    special_discount_percentage: Optional[int]
    special_discount_amount: Optional[int]
    net_amount : Optional[int]
    igst_amount: Optional[int]
    sgst_amount : Optional[int]
    cgst_amount : Optional[int]
    bill_amount : Optional[int]
    remarks: Optional[str]

class OffAppointmentVisitDetailsSchema(BaseModel):
    
    service_id: int

    

class OffAppointmentDetails(BaseModel):
    appointment_master: OffAppointmentMasterSchema
    visit_master: OffAppointmentVisitMasterSchema
    visit_details: List[OffAppointmentVisitDetailsSchema]

#get
class OffAppointmentMasterView(BaseModel):

    appointment_master_id : int
    full_name: str
    customer_number: str
    mobile_number: Optional[str]
    whatsapp_number: Optional[str]
    email_id: Optional[str]
    locality : Optional[str]
    pin_code : Optional[str]
    post_office_id: Optional[int]
    post_office_name : Optional[str]
    taluk_id: Optional[int]
    taluk_name: Optional[str]
    district_id: Optional[int]
    district_name: Optional[str]
    state_id: Optional[int]
    state_name: Optional[str]
    is_deleted: str

class OffAppointmentVisitMasterView(BaseModel):
    appointment_master_id: int
    full_name: str
    customer_number: Optional[str]
    mobile_number: Optional[str]
    whatsapp_number: Optional[str]
    email_id: Optional[str]
    locality: Optional[str]
    pin_code: Optional[str]
    appointment_master_post_office_id: Optional[int]
    post_office_name: str
    contact_number: Optional[str]
    appointment_master_taluk_id: Optional[int]
    taluk_name: str
    appointment_master_district_id: Optional[int]
    district_name: str
    appointment_master_state_id: Optional[int]
    state_name: str
    state_code: Optional[int]
    gst_registration_name: str
    appointment_master_created_by: Optional[int]
    appointment_master_created_on: Optional[date]
    appointment_master_modified_by: Optional[int]
    appointment_master_modified_on: Optional[date]
    appointment_master_is_deleted: str
    appointment_master_deleted_by: Optional[int]
    appointment_master_deleted_on: Optional[date]
    appointment_visit_master_id: Optional[int]
    financial_year_id: Optional[int]
    voucher_number: Optional[str]
    appointment_date: Optional[date]
    appointment_time_from: time
    appointment_time_to: time
    source_of_enquiry_id: Optional[int]
    source: str
    appointment_status_id: Optional[int]
    appointment_status: str
    appointment_visit_master_consultant_id: Optional[int]
    employee_master_employee_number: Optional[str]
    employee_master_first_name: Optional[str]
    employee_master_middle_name: Optional[str]
    employee_master_last_name: Optional[str]
    gross_amount: float
    discount_percentage: float
    special_discount_percentage: float
    special_discount_amount: float
    net_amount: float
    igst_amount: float
    sgst_amount: float
    cgst_amount: float
    bill_amount: float
    remarks: str
    is_deleted: str

class OffAppointmentVisitDetailsView(BaseModel):
    visit_details_id:int
    service_id :int
    serive_name:str


class ResponseSchema(BaseModel):
    appointment_master: OffAppointmentMasterView
    visit_master: OffAppointmentVisitMasterView
    visit_details: List[OffAppointmentVisitDetailsView]