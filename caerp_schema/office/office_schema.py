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
  
    service_id: int
    is_main_service:str
    class Config:
        orm_mode = True
        from_attributes = True

class OffAppointmentDetails(BaseModel):
    appointment_master: OffAppointmentMasterSchema
    visit_master: OffAppointmentVisitMasterSchema
    visit_details: List[OffAppointmentVisitDetailsSchema]


class RescheduleOrCancelRequest(BaseModel):
    consultant_id: Optional[int] = None
    appointment_master_id: Optional[int] = None
    date: Optional[str] = None
    time: Optional[str] = None
    description: str

    
class OffAppointmentCancellationReasonSchema(BaseModel):
    id:int
    off_appointment_cancellation_reason:str

class OffAppointmentMasterViewSchema(BaseModel):
    appointment_master_id: int
    full_name: Optional[str]
    gender_id:Optional[int] 
    customer_number: Optional[str]
    mobile_number: Optional[str] 
    whatsapp_number: Optional[str] 
    email_id: Optional[str] 
    locality: Optional[str] 
    pin_code: Optional[str] 
    appointment_master_post_office_id: Optional[int] 
    post_office_name: Optional[str] 
    appointment_master_taluk_id: Optional[int] 
    taluk_name: Optional[str] 
    appointment_master_district_id: Optional[int] 
    district_name: Optional[str] 
    appointment_master_state_id: Optional[int] 
    state_name: Optional[str] 
    appointment_master_is_deleted: str
    class Config:
        orm_mode = True
        from_attributes = True


class OffAppointmentVisitMasterViewSchema(BaseModel):
    appointment_master_id: int
    full_name: str
    gender_id: int
    customer_number: Optional[str]
    mobile_number: Optional[str]
    whatsapp_number: Optional[str]
    email_id: Optional[str]
    locality: Optional[str]
    pin_code: Optional[str]
    appointment_master_post_office_id: Optional[int]
    post_office_name: Optional[str]
    contact_number: Optional[str]
    appointment_master_taluk_id: Optional[int]
    taluk_name: Optional[str]
    appointment_master_district_id: Optional[int]
    district_name: Optional[str]
    appointment_master_state_id: Optional[int]
    state_name: Optional[str]
    state_code: Optional[int]
    gst_registration_name: Optional[str]
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
    appointment_time_from: Optional[str]
    appointment_time_to: Optional[str]
    source_of_enquiry_id: Optional[int]
    source: Optional[str]
    appointment_status_id: Optional[int]
    appointment_status: Optional[str]
    appointment_visit_master_consultant_id: Optional[int]
    employee_master_employee_number: Optional[str]
    employee_master_first_name: Optional[str]
    employee_master_middle_name: Optional[str]
    employee_master_last_name: Optional[str]
    gross_amount: Optional[float]
    discount_percentage: Optional[float]
    special_discount_percentage: Optional[float]
    special_discount_amount: Optional[float]
    net_amount: Optional[float]
    igst_amount: Optional[float]
    sgst_amount: Optional[float]
    cgst_amount: Optional[float]
    bill_amount: Optional[float]
    remarks: Optional[str]
    class Config:
        orm_mode = True
        from_attributes = True
        
class OffAppointmentVisitDetailsViewSchema(BaseModel):
    
    service_id: Optional[int]
    service_goods_name:str
    appointment_detail_is_main_service:str
    class Config:
        orm_mode = True
        from_attributes = True


class ResponseSchema(BaseModel):
    appointment_master: OffAppointmentMasterViewSchema
    visit_master: OffAppointmentVisitMasterViewSchema
    visit_details: List[OffAppointmentVisitDetailsViewSchema]
    class Config:
        orm_mode = True
        from_attributes = True
        


 
 
class AppointmentVisitDetailsSchema(BaseModel):
    appointment_visit_details_id: int
    visit_master_id: int
    appointment_visit_master_financial_year_id: Optional[int]
    appointment_visit_master_voucher_number: Optional[str]
    appointment_visit_master_appointment_master_id: Optional[int]
    appointment_visit_master_appointment_date: Optional[date]
    appointment_visit_master_appointment_time_from: Optional[str]
    appointment_visit_master_appointment_time_to: Optional[str]
    source_of_enquiry_id: Optional[int]
    appointment_status_id: Optional[int]
    appointment_visit_master_gross_amount: Optional[float]
    appointment_visit_master_discount_percentage: Optional[float]
    special_discount_percentage: Optional[float]
    special_discount_amount: Optional[float]
    appointment_visit_master_net_amount: Optional[float]
    appointment_visit_master_igst_amount: Optional[float]
    appointment_visit_master_sgst_amount: Optional[float]
    appointment_visit_master_cgst_amount: Optional[float]
    appointment_visit_master_bill_amount: Optional[float]
    remarks: str
    service_id: Optional[int]
    service_master_id: Optional[int]
    consultation_fee: Optional[float]
    consultancy_services_igst_rate: Optional[float]
    available_time_from: Optional[time]
    available_time_to: Optional[time]
    slot_duration_in_minutes: Optional[int]
    consultancy_services_effective_from_date: Optional[date]
    consultancy_services_effective_to_date: Optional[date]
    consultancy_services_is_deleted: str
    consultant_id: Optional[int]
    employee_master_employee_number: Optional[str]
    employee_master_first_name: Optional[str]
    employee_master_middle_name: Optional[str]
    employee_master_last_name: Optional[str]
    appointment_visit_details_created_by: Optional[int]
    appointment_visit_details_created_on: Optional[date]
    appointment_visit_details_modified_by: Optional[int]
    appointment_visit_details_modified_on: Optional[date]
    appointment_visit_details_is_deleted: str
    appointment_visit_details_deleted_by: Optional[int]
    appointment_visit_details_deleted_on: Optional[date]   
#------------------- swathy

class OffViewServiceGoodsMasterDisplay(BaseModel):

    service_goods_master_id: int
    hsn_sac_class_id: int
    hsn_sac_class: str
    group_id: int
    service_goods_group_name: Optional[str]
    sub_group_id: int
    service_goods_sub_group_name: Optional[str]
    category_id: int
    service_goods_category_name: Optional[str]
    sub_category_id: int
    service_goods_sub_category_name: Optional[str]
    service_goods_name: str
    hsn_sac_id: int
    hsn_sac_code: str
    hsn_sac_description: Optional[str]
    gst: str
    sku_code_id: int
    stock_keeping_unit_code: Optional[str]
    is_consultancy_service: str
    is_bundled_service: str
    service_goods_master_created_by: int
    service_goods_master_created_on: datetime
    service_goods_master_modified_by: Optional[int]
    service_goods_master_modified_on: Optional[datetime]
    service_goods_master_is_deleted: str
    service_goods_master_deleted_by: Optional[int]
    service_goods_master_deleted_on: Optional[datetime]


    
#-----------Aparna
class Slot(BaseModel):
    # Define the fields for a slot
    start_time: datetime
    end_time: datetime

class ConsultationRequest(BaseModel):
   
    service_id: int
    consultant_id: int
    start_time: str  
    end_time: str 

class OffServiceGoodsMasterCreate(BaseModel):
   
    hsn_sac_class_id: int
    group_id: int
    sub_group_id: int
    category_id: int
    sub_category_id: int
    service_goods_name: str
    hsn_sac_id: int
    sku_code_id: int
    is_consultancy_service: str
    is_bundled_service: str



class OffServiceGoodsDetailsCreate(BaseModel):
    service_goods_master_id: int
    display_order: int

class SaveServicesGoodsMasterRequest(BaseModel):
    master: list[OffServiceGoodsMasterCreate]
    details: Optional[list[OffServiceGoodsDetailsCreate]]  = None
    
    
# class Consultant(BaseModel):
#     consultant_id: int
#     first_name: str
#     middle_name: Optional[str] = None
#     last_name: str

# class Service(BaseModel):
#     service_id: int
#     service_name: str

# class ConsultantDetails(BaseModel):
#     consultants: List[Consultant]
#     services: List[Service]
#     service_consultants: Optional[List[Consultant]] = None
    
# class Employee(BaseModel):
#     id: int
#     first_name: str
#     middle_name: Optional[str]
#     last_name: str


class EmployeeResponse(BaseModel):
    employees: List[dict]
    
class ServiceGoodsPrice(BaseModel):
    service_name: str
    configuration_status: Optional[str] = None
    service_type: Optional[str] = None
    bundled_service: Optional[str] = None

class PriceListResponse(BaseModel):
    price_list: List[ServiceGoodsPrice]
    
    
# class ServiceModel(BaseModel):
#     id: int
#     service_name: str

#     constitution_id: int
#     business_constitution_name: str
#     business_constitution_code: str
#     service_charge: Optional[int]  # Changed to Optional[int]
#     govt_agency_fee: Optional[int]  # Changed to Optional[int]
#     stamp_duty: Optional[int]  # Changed to Optional[int]
#     stamp_fee: Optional[int]  # Changed to Optional[int]
#     effective_from_date: Optional[date]
#     effective_to_date: Optional[date]
#     service_description: Optional[str] = None
    
# class PriceHistoryModel(BaseModel):
#     service_charge: Optional[int]
#     govt_agency_fee: Optional[int]
#     stamp_duty: Optional[int]
#     stamp_fee: Optional[int]
#     effective_from_date: Optional[date]
#     effective_to_date: Optional[date]

class PriceHistoryModel(BaseModel):
    service_goods_price_master_id: Optional[int]
    service_charge: Optional[int]
    govt_agency_fee: Optional[int]
    stamp_duty: Optional[int]
    stamp_fee: Optional[int]
    effective_from_date: Optional[date]
    effective_to_date: Optional[date]
    
class SetPriceModel(BaseModel):
    service_goods_master_id:int
    constitution_id:int
    service_charge: Optional[int]
    govt_agency_fee: Optional[int]
    stamp_duty: Optional[int]
    stamp_fee: Optional[int]
    effective_from_date: Optional[date]
    effective_to_date: Optional[date]


class ServiceModel(BaseModel):
    id: int
    service_name: str
    constitution_id: int
    business_constitution_name: str
    business_constitution_code: str
    price_history: List[PriceHistoryModel]

    
    
class ServicePriceHistory(BaseModel):
    constitution_id: int
    business_constitution_name: str
    service_charge: Optional[float]
    govt_agency_fee: Optional[float]
    stamp_duty: Optional[float]
    stamp_fee: Optional[float]
    effective_from_date: Optional[date]
    effective_to_date: Optional[date]
# class ServiceModel(BaseModel):
#     service_name: str
#     price_history: List[ServicePriceHistory]
class PriceData(BaseModel):
    service_goods_master_id: int
    constitution_id: int
    service_charge: float
    govt_agency_fee: float
    stamp_duty: float
    stamp_fee: float
    effective_from_date: date
    effective_to_date: date
    
    
class OffDocumentDataMasterBase(BaseModel):
    document_data_name : str
    has_expiry : str    