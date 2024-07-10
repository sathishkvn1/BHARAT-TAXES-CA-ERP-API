from enum import Enum
from pydantic import BaseModel, constr,validator
from typing import List,Dict,Optional
from typing import Dict, Any,Union
import re
from datetime import date, datetime,time

class AppointmentStatusConstants(str,Enum):
    NEW = "NEW"
    CANCELED = "CANCELED"
    RESCHEDULED = "RESCHEDULED"
    CLOSED = "CLOSED"



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
 
    financial_year_id: Optional[int]
    voucher_number: Optional[str]
    appointment_date : Optional[date]
    appointment_time_from: Optional[str] 
    appointment_time_to: Optional[str]
    source_of_enquiry_id : Optional[int]
    appointment_status_id: Optional[int]
    consultant_id: Optional[int]
    consultation_mode_id: Optional[int]
    consultation_tool_id: Optional[int]
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
    class Config:
        orm_mode = True
        from_attributes = True

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
    from_time: Optional[str] = None
    to_time: Optional[str] = None
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
    appointment_number: Optional[str]
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
    appointment_visit_master_consultation_mode_id: Optional[int]
    appointment_visit_master_consultation_tool_id: Optional[int]
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

class OffViewServiceGoodsDetailsDisplay(BaseModel):
   
    service_goods_master_id: int
    hsn_sac_class_id : int
    hsn_sac_class : str
    group_id : int
    service_master_group_name : Optional[str]
    sub_group_id  : int
    service_master_sub_group_name : Optional[str]
    category_id : int
    service_master_category_name : Optional[str]
    sub_category_id : int
    service_master_sub_category_name : Optional[str]
    service_goods_name: str
    hsn_sac_id : int
    hsn_sac_code : str
    hsn_sac_description : Optional[str]
    sku_code_id : int
    stock_keeping_unit_code : Optional[str]
    has_consultation : str
    is_bundled_service : str
    bundled_service_goods_id : int
    display_order: Optional[int]
    


   



class OffViewServiceGoodsMasterDisplay(BaseModel):
    service_goods_master_id: int
    hsn_sac_class_id: int
    hsn_sac_class: Optional[str]
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
    hsn_sac_code: Optional[str]
    hsn_sac_description: Optional[str]
    gst: str
    sku_code_id: int
    stock_keeping_unit_code: Optional[str]
    has_consultation: str
    is_bundled_service: str
    details: Optional[List[OffViewServiceGoodsDetailsDisplay]] = None
    
    

class OffDocumentDataBase(BaseModel):
    document_data_name :str
    has_expiry : str


    
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
    has_consultation: str
    is_bundled_service: str

class OffServiceGoodsDetailsCreate(BaseModel):
    service_goods_master_id: int
    display_order: int


class SaveServicesGoodsMasterRequest(BaseModel):
    master: List[OffServiceGoodsMasterCreate]
    details: Optional[List[OffServiceGoodsDetailsCreate]] = None
    
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
    id: int
    service_name: str
    configuration_status: Optional[str] = None
    service_type: Optional[str] = None
    bundled_service: Optional[str] = None

class PriceListResponse(BaseModel):
    price_list: List[ServiceGoodsPrice]
    
    



    
class SetPriceModel(BaseModel):
    service_goods_master_id:int
    constitution_id:int
    service_charge: Optional[int]
    govt_agency_fee: Optional[int]
    stamp_duty: Optional[int]
    stamp_fee: Optional[int]
    effective_from_date: Optional[date]
    effective_to_date: Optional[date]

class PriceHistoryModel(BaseModel):
    constitution_id: int
    business_constitution_name: str
    service_charge: Optional[float]
    govt_agency_fee: Optional[float]
    stamp_duty: Optional[float]
    stamp_fee: Optional[float]
    effective_from_date: Optional[date]
    effective_to_date: Optional[date]

class ServiceModel(BaseModel):
    id: int
    service_name: str
    constitution_id: int
    business_constitution_name: str
    business_constitution_code: str
    price_history: List[PriceHistoryModel]
    
class ServiceModelSchema(BaseModel):
    constitution_id: int
    business_constitution_name: str
    service_goods_master_id: int
    service_goods_price_master_id: int
    service_name: str
    business_constitution_code: str
    service_charge: float
    govt_agency_fee: float
    stamp_duty: float
    stamp_fee: float
    price_master_effective_from_date: Optional[date]
    price_master_effective_to_date: Optional[date]

    
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
    id: int
    document_data_name : str  
    data_type: str
    has_expiry : str
      
    
class Item(BaseModel):
    id: int
    service_goods_master_id: int
    bundled_service_goods_id: int
    display_order: int
    service_charge: float
    govt_agency_fee: float
    stamp_fee: float
    stamp_duty: float

class Bundle(BaseModel):
    service_id: int
    service_name: str
    service_charge: float
    govt_agency_fee: float
    stamp_fee: float
    stamp_duty: float
    items: List[Item]
    sub_item_total: Dict[str, float]
    grand_total: Dict[str, float]
    
    
class OffServiceDocumentDataMasterDisplay(BaseModel):
    service_goods_master_id : int
    group_id : int
    sub_group_id : int
    category_id : int
    sub_category_id : int
    constitution_id : int
  
 

class OffServiceDocumentDataDetails(BaseModel):
    #service_document_data_id : int
    document_data_id : int
    nature_of_possession_id : int
    display_order : int
 
class OffServiceDocumentDataRequired(BaseModel):
    document_data_category_id: int
    details: List[OffServiceDocumentDataDetails]
 
class ServiceDocuments(BaseModel):
    personal_doc: Optional[List[OffServiceDocumentDataRequired]] = None
    constitution_doc: Optional[List[OffServiceDocumentDataRequired]] = None
    principal_place_doc: Optional[List[OffServiceDocumentDataRequired]] = None
    utility_doc: Optional[List[OffServiceDocumentDataRequired]] = None
    data_to_be_submitted_doc: Optional[List[OffServiceDocumentDataRequired]] = None

   
class SaveServiceDocumentDataMasterRequest(BaseModel):
    Service: Optional[OffServiceDocumentDataMasterDisplay] = None
    Documents: Optional[List[ServiceDocuments]] = None
    
class OffViewServiceDocumentsDataDetailsSchema(BaseModel):
    service_document_data_details_id: int
    service_document_data_id: int
    constitution_id: int
    business_constitution_name: str
    business_constitution_code: str
    description: Optional[str]
    document_data_id: int
    document_data_type_id: int
    document_data_type: str
    document_data_name: str
    has_expiry: str
    nature_of_possession_id: Optional[int]
    nature_of_possession: str
    display_order: int
    class Config:
        from_attributes = True  
   
class OffViewServiceDocumentsDataDetailsDocCategory(BaseModel):
    document_data_category_id: int
    document_data_category_category_name: str
    details: List[OffViewServiceDocumentsDataDetailsSchema]
    class Config:
        from_attributes = True  
   
class OffViewServiceDocumentsDataMasterSchema(BaseModel):
    service_document_data_master_id: int
    service_goods_master_id : int
    service_goods_name: str
    group_id: int
    group_name: Optional[str]
    sub_group_id: int
    sub_group_name: Optional[str]
    category_id : int
    category_name :Optional[str]
    sub_category_id: int
    sub_category_name: Optional[str]
    constitution_id: int
    business_constitution_name: str
    business_constitution_code: str
    description: Optional[str]
    doc_data_status: Optional[str] = None 
    details: List[OffViewServiceDocumentsDataDetailsDocCategory] = []

    class Config:
        from_attributes = True
        
class OffViewServiceDocumentsDataMasterSchema(BaseModel):
    service_document_data_master_id: int
    service_goods_master_id : int
    service_goods_name: str
    group_id: int
    group_name: Optional[str]
    sub_group_id: int
    sub_group_name: Optional[str]
    category_id : int
    category_name :Optional[str]
    sub_category_id: int
    sub_category_name: Optional[str]
    constitution_id: int
    business_constitution_name: str
    business_constitution_code: str
    description: Optional[str]
    doc_data_status: Optional[str] = None
    details: Optional[List[OffViewServiceDocumentsDataDetailsDocCategory]] = None
   
    class Config:
        from_attributes=True
       
class SubGroup(BaseModel):
    id: int
    sub_group_name: str

class Category(BaseModel):
    id: int
    category_name: str

class SubCategory(BaseModel):
    id: int
    sub_category_name: str
    
class Service_Group(BaseModel):
    id: int
    group_name: str
    

class ServiceDocumentsList_Group(BaseModel):
    group: Optional[Service_Group] =None
    sub_group: Optional[List[SubGroup]] =None
    category:Optional[List[Category]]=None
    sub_category:Optional[List[SubCategory]]=None

class TimeSlotResponse(BaseModel):
    id: int
    consultant_id: int
    day_of_week_id: int
    day_long_name: str
    consultation_mode_id: int
    consultation_mode: str
    morning_start_time: Optional[time]
    morning_end_time: Optional[time]
    afternoon_start_time: Optional[time]
    afternoon_end_time: Optional[time]
    is_normal_schedule: str
    consultation_date: Optional[date]
    effective_from_date: Optional[date]
    effective_to_date: Optional[date]
    created_by: int
    created_on: datetime
    modified_by: Optional[int]
    modified_on: Optional[datetime]
    
   

    class Config:
        orm_mode = True
    
    
#------------------------------------------------------------------------------------------------
###################CONSULTANTS AND SERVICES####################################################


    


# class ConsultantEmployee(BaseModel):
#     employee_id: int
#     employee_name: str
#     employee_number: str
#     personal_email: str
#     official_email: str
#     personal_mobile: str
#     official_mobile: str
#     department_name: str
#     designation_name: str



class ConsultantEmployee(BaseModel):
    employee_id: int
    employee_name: str
    employee_number: str
    personal_email: str
    official_email: Optional[str]
    personal_mobile: str
    official_mobile: Optional[str]
    department_name: str
    designation: Optional[str]
    
class ConsultantService(BaseModel):
    # consultant_id:int
    service_goods_master_id:Optional[int]=None
    consultation_fee:float
    slot_duration_in_minutes:int
    effective_from_date: date
    effective_to_date: Optional[date] = None
    
class ConsultantServiceDetailsResponse(BaseModel):
    id: int
    consultant_id: int
    service_goods_master_id: int
    service_goods_name: str
    consultation_fee: float
    slot_duration_in_minutes: int
    effective_from_date: date
    effective_to_date: Optional[date]

class ConsultantServiceDetailsListResponse(BaseModel):
    services: List[ConsultantServiceDetailsResponse]



class ConsultantScheduleCreate(BaseModel):
    # consultant_id: int
    day_of_week_id: Optional[int]=None
    consultation_mode_id: int
    morning_start_time: Optional[time] = None
    morning_end_time: Optional[time] = None
    afternoon_start_time: Optional[time] = None
    afternoon_end_time: Optional[time] = None
    is_normal_schedule: str
    consultation_date: Optional[date] = None
    effective_from_date: Optional[date] = None
    effective_to_date: Optional[date] = None


#------------------------------------------------------------------------------------------------
###################ENQUIRY####################################################
#------------------------------------------------------------------------------------------------
class OffEnquiryMasterSchema(BaseModel):

    customer_number:Optional[str] 
    first_name: str
    middle_name: Optional[str] 
    last_name: Optional[str] 
    gender_id:Optional[int]
    date_of_birth:Optional[date]
    mobile_number: Optional[str]
    whatsapp_number: Optional[str]
    email_id: Optional[str]
    house_or_building_name: Optional[str]
    road_or_street_name: Optional[str]
    locality : Optional[str]
    pin_code : Optional[str]
    village_id  : Optional[int] 
    post_office_id: Optional[int]
    lsg_type_id: Optional[int]
    lsg_id: Optional[int]
    taluk_id: Optional[int]
    district_id: Optional[int]
    state_id: Optional[int]
    country_id: Optional[int]
    class Config:
        orm_mode = True
        from_attributes = True


class OffEnquiryDetailsSchema(BaseModel):
 
    financial_year_id: Optional[int]
    enquiry_number: Optional[str]
    enquiry_date : Optional[date]
    source_of_enquiry_id : Optional[int]
    enquiry_status_id: Optional[int]
    enquirer_type_id: Optional[int]
    company_or_business_name: Optional[str]
    remarks: Optional[str]
    class Config:
        orm_mode = True
        from_attributes = True

class OffEnquiryResponseSchema(BaseModel):
    enquiry_master: OffEnquiryMasterSchema
    enquiry_details: List[OffEnquiryDetailsSchema]
    class Config:
        orm_mode = True
        from_attributes = True

#get
class OffViewEnquiryMasterSchema(BaseModel):
    enquiry_master_id:int
    customer_number:Optional[str] 
    first_name: str
    middle_name: Optional[str] 
    customer_number: Optional[str] 
    first_name 	 : Optional[str] 
    middle_name 	: Optional[str] 
    last_name 	 : Optional[str] 
    gender_id: Optional[int] 
    gender: Optional[str] 
    date_of_birth: Optional[date] 
    mobile_number : Optional[str] 
    whatsapp_number: Optional[str] 
    email_id  : Optional[str] 
    house_or_building_name: Optional[str] 
    road_or_street_name: Optional[str] 
    locality: Optional[str] 
    pin_code: Optional[str] 
    village_id  : Optional[int] 
    village_name:Optional[str] 
    post_office_id: Optional[int] 
    post_office_name : Optional[str] 
    lsg_type_id: Optional[int] 
    lsg_type: Optional[str] 
    lsg_id: Optional[int] 
    lsg_name: Optional[str] 
    taluk_id: Optional[int] 
    taluk_name: Optional[str] 
    district_id: Optional[int] 
    district_name: Optional[str] 
    state_id: Optional[int] 
    state_name: Optional[str] 
    country_id: Optional[int] 
    country_name_english: Optional[str] 
    country_name_arabic: Optional[str] 
    
class OffViewEnquiryDetailsSchema(BaseModel):
    financial_year_id: Optional[int]
    financial_year: Optional[str]
    enquiry_number: Optional[str]
    enquiry_date : Optional[date]
    source_of_enquiry_id : Optional[int]
    source: Optional[str]
    enquiry_status_id: Optional[int]
    enquiry_status: Optional[str]
    enquirer_type_id: Optional[int]
    person_type: Optional[str]
    company_or_business_name: Optional[str]
    remarks: Optional[str]


class OffViewEnquiryResponseSchema(BaseModel):
    enquiry_master: OffViewEnquiryMasterSchema
    enquiry_details: List[OffViewEnquiryDetailsSchema]
    class Config:
        orm_mode = True
        from_attributes = True
        
        
class ConsultationToolSchema(BaseModel):
    id: int
    consultation_tool: str


    class Config:
        orm_mode = True
        from_attributes = True

class ConsultationModeSchema(BaseModel):
    id: int
    consultation_mode: str
    is_deleted: str
    
    class Config:
        orm_mode = True
        from_attributes = True
       
        
        
class OffConsultationTaskDetailsSchema(BaseModel):
   # task_master_id: int
    service_id: int
    is_main_service: str

    class Config:
        orm_mode = True


class OffConsultationTaskMasterSchema(BaseModel):
    task_date: Optional[datetime]
    consultant_id: int
    appointment_master_id: int
    visit_master_id : int
    task_status_id: int
    task_priority_id: int
    remarks: Optional[str]
    details: List[OffConsultationTaskDetailsSchema]

    class Config:
        orm_mode = True

class AdditionalServices(BaseModel):
    service_id: int
    service_name:str

class OffViewConsultationTaskMasterSchema(BaseModel):
    consultation_task_master_id: int
    task_date: datetime
    consultant_id: int
    employee_number: str
    employee_first_name: str
    employee_middle_name: Optional[str]
    employee_last_name: str
    appointment_master_id: int
    appointee_full_name: str
    appointee_gender_id: int
    appointee_gender: str
    customer_number: Optional[str]
    business_name: Optional[str]
    appointee_mobile_number: Optional[str]
    appointee_whatsapp_number: Optional[str]
    appointee_email_id: Optional[str]
    visit_master_id: int
    visit_master_appointment_time_from: str
    visit_master_appointment_time_to: Optional[str]
    consultation_mode_id: int
    consultation_mode: str
    consultation_tool_id: int
    consultation_tool: str
    task_status_id: int
    task_status: Optional[str]
    task_priority_id: int
    task_priority: Optional[str]
    remarks: Optional[str]
    consultation_task_details_id: Optional[int]
    task_master_id: Optional[int]
    service_id: Optional[int]
    hsn_sac_class_id: int
    hsn_sac_class: str
    hsn_sac_id: int
    hsn_sac_code: str
   # has_consultation: str
    group_id: int
    group_name: Optional[str]
    sub_group_id: int
    sub_group_name: Optional[str]
    category_id: int
    category_name: Optional[str]
    sub_category_id: int
    sub_category_name: Optional[str]
    service_goods_name: str
    sku_code_id: int
    unit_code: Optional[str]
    #is_bundled_service: str
    is_main_service: Optional[str]
    additional_services:Optional[List[AdditionalServices]]

    class Config:
        orm_mode = True

       

#----------------------------------------------
       
# class DocumentDetail(BaseModel):
#     document_data_id: int
#     nature_of_possession_id: int
#     display_order: int

# class DocumentCategory(BaseModel):
#     document_data_category_id: int
#     details: List[DocumentDetail]

# class ServiceDocuments(BaseModel):
#     personal_doc: Optional[List[DocumentCategory]] = None
#     constitution_doc: Optional[List[DocumentCategory]] = None
#     principal_place_doc: Optional[List[DocumentCategory]] = None
#     utility_doc: Optional[List[DocumentCategory]] = None
#     data_to_be_submitted_doc: Optional[List[DocumentCategory]] = None

# class Service(BaseModel):
#     service_goods_master_id: int
#     group_id: int
#     sub_group_id: int
#     category_id: int
#     sub_category_id: int
#     constitution_id: int

# class ServiceDocumentRequest(BaseModel):
#     service: Service
#     documents: ServiceDocuments