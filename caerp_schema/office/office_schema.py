
from pydantic import BaseModel, constr,validator
from typing import List,Dict,Optional
from typing import Dict, Any,Union
import re

from datetime import date, datetime,time



class DocumentMasterBase(BaseModel):
    
    document_name: str
    document_code: Optional[str]

class DocumentBase(BaseModel):
    id: int
    document_name: str
    document_code: Optional[str]
   
class ServiceProviderBase(BaseModel):
   
   
    service_provider :str
    place            :Optional[str]
    address_line_1   :Optional[str]
    email_id         :Optional[str]
    mobile_number    :Optional[str]
    



class ServiceProBase(BaseModel):
   
    id               :int
    service_provider :str
    place            :Optional[str]
    address_line_1   :Optional[str]
    email_id         :Optional[str]
    mobile_number    :Optional[str]
   
class ServiceDepartmentBase(BaseModel):

    service_department_name :str
    department_description  :Optional[str]
    address_line_1          :Optional[str]
    address_line_2          :Optional[str]
    email_id                :Optional[str]
    mobile_number           :Optional[str]
    



class ServiceDepBase(BaseModel):
   
    id                      :int
    service_department_name :str
    department_description  :Optional[str]
    address_line_1          :Optional[str]
    address_line_2          :Optional[str]
    email_id                :Optional[str]
    mobile_number           :Optional[str]
    

class BusinessActivityTypeBase(BaseModel):
    
    business_activity_type: Optional[str]
     

    
class BusinessActivityTypeDisplay(BaseModel):
    id                    : int
    business_activity_type: Optional[str]



class BusinessActivityMasterBase(BaseModel):
    business_activity_type_id:int
    business_activity        : Optional[str]
     

    
# class BusinessActivityMasterDisplay(BaseModel):
#     id                         : int
#     business_activity_type_id  :int
#     business_activity          : Optional[str]


    
    
class BusinessActivityMasterDisplay(BaseModel):
    id: int
    business_activity: Optional[str]
    business_activity_type: Optional[str]


class EducationalQualificationsBase(BaseModel):
   
    qualification     :str
     
class EducationalQualificationsDisplay(BaseModel):
    id                : int
    qualification     :str


class EnquirerTypeBase(BaseModel):
   
    person_type     :Optional[str]

class EnquirerTypeDisplay(BaseModel):
    id                : int
    person_type       :Optional[str]


class EnquirerStatusBase(BaseModel):
   
    status     :Optional[str]


class EnquirerStatusDisplay(BaseModel):
    id         : int
    status     :Optional[str]



class ServiceProcessingStatusBase(BaseModel):
    
    service_processing_status     :Optional[str]


class ServiceProcessingStatusDisplay(BaseModel):
    id                          : int
    service_processing_status   :Optional[str]
    
    #--------------------------------------------------------
class ServiceFrequencyBase(BaseModel):
    id: int
    service_frequency: Optional[str]
     


class ServiceFrequencyDisplay(BaseModel):
   
    service_frequency: Optional[str]
     

class StockKeepingUnitCodeBase(BaseModel):
    id : int
    unit_code : Optional[str]

class StockKeepingUnitCodeDisplay(BaseModel):
   
    unit_code : Optional[str]    
   
       
     
class HsnSacClassesBase(BaseModel):
    id : int
    hsn_sac_class : str
    
class HsnSacClassesDisplay(BaseModel):

    hsn_sac_class :str   

class HsnSacMasterBase(BaseModel):
    id:int
    hsn_sac_class:Optional[str]
    hsn_sac_code:Optional[str]
    hsn_sac_description:Optional[str]
    sku_code: Optional[str]
  



class HsnSacMasterDisplay(BaseModel):
    hsn_sac_class_id: int
    hsn_sac_code: str
    hsn_sac_description: str
    sku_code: str
    

class OffServicesDisplay(BaseModel):
    service_name: Optional[str]
    hsn_sac_id: Optional[int]
    service_provider_id: int
    service_department_id: int
    service_frequency_id: int
    sku_code_id: int
    is_consultancy_service: str
    



class ViewOffServicesDisplay(BaseModel):
    service_master_id: int
    service_name: str
    hsn_sac_id: int
    hsn_sac_code: str
    hsn_sac_description: str
    service_provider_id: int
    service_provider: str
    service_department_id: int
    service_department_name: str
    service_frequency_id: int
    service_frequency: str
    sku_code_id: int
    unit_code: str
    is_consultancy_service: str
    is_deleted: str


class OffAvailableServicesDisplay(BaseModel):
    
    service_master_id: int
    is_main_service: str
    main_service_id: int
    purchase_price: Optional[float]= None
    selling_price: Optional[float]= None
    gst_rate: Optional[float]= None
    cgst_rate: Optional[float]= None
    sgst_rate: Optional[float]= None
    cess_rate: Optional[float]= None
    discount_percentage: Optional[float]= None
    discount_amount: Optional[float]= None
    filing_day_from: Optional[int]= None
    filing_day_to: Optional[int]= None
    filing_month_from: Optional[int]= None
    filing_month_to: Optional[int]= None
    department_amount: Optional[float]= None
    days_required_for_processing: Optional[int]= None
    display_order: Optional[int]= None
    effective_from_date: Optional[date]= None
    effective_to_date: Optional[date]= None
    


class ViewOffAvailableServicesDisplay(BaseModel):
    available_services_id: int
    service_master_id: int
    service_name: str
    hsn_sac_id: int
    hsn_sac_description: str
    is_main_service: str
    main_service_id: int
    purchase_price: Optional[float]
    selling_price: Optional[float]
    gst_rate: Optional[float]
    cgst_rate: Optional[float]
    sgst_rate: Optional[float]
    cess_rate: Optional[float]
    discount_percentage: Optional[float]
    discount_amount: Optional[float]
    filing_day_from: Optional[int]
    filing_day_to: Optional[int]
    filing_month_from: Optional[int]
    filing_month_to: Optional[int]
    department_amount: Optional[float]
    days_required_for_processing: Optional[int]
    display_order: Optional[int]
    effective_from_date: Optional[date]
    effective_to_date: Optional[date]
    off_available_services_is_deleted: str
    service_provider_id: int
    service_provider: str
    service_department_id: int
    service_department_name: str
    service_frequency_id: int
    service_frequency: str
    sku_code_id: int
    unit_code: str
    is_consultancy_service: str
    service_master_is_deleted: str
    
    
class OffSourceOfEnquiryBase(BaseModel):
    
    
    source 	 : str
    
class OffSourceOfEnquiryDisplay(BaseModel):
    id        : int
    source 	 : str
    is_deleted     : str


class OffAppointmentStatusBase(BaseModel):
    
    
    appointment_status : Optional[str]
    

class OffAppointmentStatusDisplay(BaseModel):
    id     : int
    appointment_status : Optional[str]
    is_deleted         : str  


class OffAppointmentMaster(BaseModel):
    
    mobile_number: Optional[str]
    email_id: Optional[str]
    full_name: str

class OffAppointmentVisitMaster(BaseModel):
    source_of_enquiry_id: int
    appointment_status_id: int
    appointment_date: date

class OffAppointmentVisitDetails(BaseModel):
    # visit_master_id: int
    consultancy_service_id: int
    consultant_id: int
    appointment_time: time

    

class OffAppointmentDetails(BaseModel):
    appointment_master: OffAppointmentMaster
    visit_master: OffAppointmentVisitMaster
    visit_details: List[OffAppointmentVisitDetails]
#get
class OffAppointmentMasterView(BaseModel):
    
    full_name: str 
    mobile_number: Optional[str]
    email_id: Optional[str]
    class Config:
        orm_mode = True  
class OffAppointmentVisitMasterViewSchema(BaseModel):
    appointment_master_id: int
    appointment_visit_master_id: int
    full_name: str
    appointment_number: Optional[str]
    enquiry_number: Optional[str]
    customer_number: Optional[str]
    mobile_number: Optional[str]
    email_id: Optional[str]
    appointment_master_created_by: Optional[int]
    appointment_master_created_on: Optional[date]
    appointment_master_modified_by: Optional[int]
    appointment_master_modified_on: Optional[date]
    appointment_master_is_deleted: Optional[str]
    appointment_master_deleted_by: Optional[int]
    appointment_master_deleted_on: Optional[date]
    appointment_visit_master_appointment_date: Optional[date]
    appointment_visit_master_source_of_enquiry_id: Optional[int]
    source: Optional[str]
    appointment_visit_master_appointment_status_id: Optional[int]
    is_paid: Optional[str]
    appointment_status: Optional[str]
    appointment_visit_master_payment_mode_id: Optional[int]
    payment_mode: Optional[str]
    appointment_visit_master_payment_transaction_number: Optional[str]
    appointment_visit_master_payment_status_id: Optional[int]
    payment_status: Optional[str]
    appointment_visit_master_payment_date: Optional[date]
    appointment_visit_master_is_refunded: Optional[str]
    appointment_visit_master_refund_status_id: Optional[int]
    refund_status: Optional[str]
    appointment_visit_master_refund_amount: Optional[int]
    appointment_visit_master_refund_date: Optional[date]
    appointment_visit_master_refund_reason_id: Optional[int]
    refund_reason: Optional[str]
    appointment_visit_master_refund_transaction_number: Optional[str]
    appointment_visit_master_service_charge: Optional[int]
    appointment_visit_master_gst_percentage: Optional[int]
    appointment_visit_master_sgst_percentage: Optional[int]
    appointment_visit_master_cgst_percentage: Optional[int]
    appointment_visit_master_discount_percentage: Optional[int]
    appointment_visit_master_discount_amount: Optional[int]
    appointment_visit_master_special_discount_percentage: Optional[int]
    appointment_visit_master_special_discount_amount: Optional[int]
    appointment_visit_master_net_amount: Optional[int]
    appointment_visit_master_remarks: Optional[str]
    appointment_visit_master_created_by: Optional[int]
    appointment_visit_master_created_on: Optional[date]
    appointment_visit_master_modified_by: Optional[int]
    appointment_visit_master_modified_on: Optional[date]
    appointment_visit_master_is_deleted: Optional[str]
    appointment_visit_master_is_deleted_directly: Optional[str]
    appointment_visit_master_is_deleted_with_master: Optional[str]
    appointment_visit_master_deleted_by: Optional[int]
    appointment_visit_master_deleted_on: Optional[date]

    class Config:
        orm_mode = True
class OffAppointmentVisitDetailsViewGet(BaseModel):
    appointment_visit_details_id: int
    appointment_visit_master_id: Optional[int]
    appointment_master_id: Optional[int]
    appointment_date: Optional[date]
    appointment_time: Optional[time]
    consultancy_service_id: Optional[int]
    service_name: Optional[str]
    consultant_id: Optional[int]
    employee_number: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    appointment_visit_details_service_charge: Optional[int]
    appointment_visit_details_gst_percentage: Optional[int]
    appointment_visit_details_sgst_percentage: Optional[int]
    appointment_visit_details_cgst_percentage: Optional[int]
    appointment_visit_details_discount_percentage: Optional[int]
    appointment_visit_details_discount_amount: Optional[int]
    appointment_visit_details_net_amount: Optional[int]
    appointment_visit_details_remarks: Optional[str]
    appointment_visit_details_created_by: Optional[int]
    appointment_visit_details_created_on: Optional[date]
    appointment_visit_details_modified_by: Optional[int]
    appointment_visit_details_modified_on: Optional[date]
    appointment_visit_details_is_deleted: Optional[str]
    appointment_visit_details_is_deleted_directly: Optional[str]
    appointment_visit_details_is_deleted_with_master: Optional[str]
    appointment_visit_details_deleted_by: Optional[int]
    appointment_visit_details_deleted_on: Optional[date]
    class Config:
        orm_mode = True
        from_attributes = True



class ResponseModel(BaseModel):
    appointment_master: OffAppointmentMasterView
    visit_master: OffAppointmentVisitMasterViewSchema
    visit_details: List[OffAppointmentVisitDetailsViewGet]
    
    
from datetime import time
# Pydantic schema for response with ORM mode enabled
class ConsultancyServiceResponse(BaseModel):
    id: int
    service_master_id: int
    consultant_id: int
    consultation_fee: float
    gst_rate: float
    cgst_rate: float
    sgst_rate: float
    cess_rate: float
    discount_percentage: float
    discount_amount: float
    available_time_from: time
    available_time_to: time
    slot_duration_in_minutes: int
    effective_from_date: date  # Change type to datetime.date
    effective_to_date: Optional[date]  # Change type to Optional[datetime.date]
    is_deleted: str


#------------------18-4-2024----------------------

class BusinessConstitutionBase(BaseModel):

    business_constitution_name: str
    business_constitution_code: str
    description: Optional[str]
    pan_code: Optional[str]
    display_order:int
   

  
class BusinessConstitutionSchema(BaseModel):
    id:int
    business_constitution_name: str
    business_constitution_code: str
    description: Optional[str]
    pan_code: Optional[str]
    display_order:int
    is_deleted: str
