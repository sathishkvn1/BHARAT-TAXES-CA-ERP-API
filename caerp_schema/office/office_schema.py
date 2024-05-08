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
    gender_id:Optional[int]
    locality : Optional[str]
    pin_code : Optional[str]
    post_office_id: Optional[int]
    taluk_id: Optional[int]
    district_id: Optional[int]
    state_id: Optional[int]

class OffAppointmentVisitMasterSchema(BaseModel):
    # id: Optional[int]
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
    # consultant_id : int
    service_id: int

    

class OffAppointmentDetails(BaseModel):
    appointment_master: OffAppointmentMasterSchema
    visit_master: OffAppointmentVisitMasterSchema
    visit_details: List[OffAppointmentVisitDetailsSchema]


class RescheduleOrCancelRequest(BaseModel):
    consultant_id: Optional[int]
    appointment_master_id: Optional[int]
    date: Optional[date]
    time: Optional[str]
    description: str 

class OffAppointmentCancellationReasonSchema(BaseModel):
    id:int
    off_appointment_cancellation_reason:str