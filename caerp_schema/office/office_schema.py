from enum import Enum
from pydantic import BaseModel, RootModel
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
 
    full_name        : str
    customer_number  : str
    mobile_number    : Optional[str]
    whatsapp_number  : Optional[str]
    email_id         : Optional[str]
    gender_id        : Optional[int]
    locality         : Optional[str]
    pin_code         : Optional[str]
    post_office_id   : Optional[int]
    taluk_id         : Optional[int]
    district_id      : Optional[int]
    state_id         : Optional[int]


class OffAppointmentVisitMasterSchema(BaseModel):
 
    financial_year_id         : Optional[int]
    voucher_number            : Optional[str]
    appointment_date          : Optional[date]
    appointment_time_from     : Optional[str] 
    appointment_time_to       : Optional[str]
    source_of_enquiry_id      : Optional[int]
    appointment_status_id     : Optional[int]
    consultant_id             : Optional[int]
    consultation_mode_id      : Optional[int]
    consultation_tool_id      : Optional[int]
    gross_amount              : Optional[int]
    discount_percentage       : Optional[int]
    special_discount_percentage: Optional[int]
    special_discount_amount    : Optional[int]
    net_amount                 : Optional[int]
    igst_amount                : Optional[int]
    sgst_amount                : Optional[int]
    cgst_amount                : Optional[int]
    bill_amount                : Optional[int]
    remarks                    : Optional[str]
    class Config:
        orm_mode = True
        from_attributes = True




class OffAppointmentVisitDetailsSchema(BaseModel):
  
    service_id     : int
    is_main_service:str
    class Config:
        orm_mode = True
        from_attributes = True


class OffAppointmentDetails(BaseModel):
    appointment_master: OffAppointmentMasterSchema
    visit_master      : OffAppointmentVisitMasterSchema
    visit_details     : List[OffAppointmentVisitDetailsSchema]


class RescheduleOrCancelRequest(BaseModel):
    consultant_id        : Optional[int] = None
    appointment_master_id: Optional[int] = None
    date                 : Optional[str] = None 
    from_time            : Optional[str] = None
    to_time              : Optional[str] = None
    description          : str



    
class OffAppointmentCancellationReasonSchema(BaseModel):
    id                                 :int
    off_appointment_cancellation_reason:str



class OffAppointmentMasterViewSchema(BaseModel):
    appointment_master_id: int
    full_name            : str
    gender_id            : int
    gender               : str
    appointment_number   : Optional[str]
    customer_number      : Optional[str]
    mobile_number        : Optional[str]
    whatsapp_number      : Optional[str]
    email_id             : Optional[str]
    locality             : Optional[str]
    pin_code             : Optional[str]
    post_office_id       : Optional[int]
    post_office_name     : Optional[str]
    contact_number       : Optional[str]
    taluk_id             : Optional[int]
    taluk_name           : Optional[str]
    district_id          : Optional[int]
    district_name        : Optional[str]
    state_id             : Optional[int]
    state_name           : Optional[str]
    state_code           : Optional[int]
    gst_registration_name: Optional[str]
    created_by           : Optional[int]
    created_on           : Optional[date]
    modified_by          : Optional[int]
    modified_on          : Optional[date]
    is_deleted           : str
    deleted_by           : Optional[int]
    deleted_on           : Optional[date]
    is_locked            : str
    locked_on            : Optional[date]
    locked_by            : Optional[int]
    
    class Config:
        orm_mode = True
        from_attributes = True

class OffAppointmentVisitMasterViewSchema(BaseModel):
    visit_master_id           : Optional[int]
    appointment_master_id     : int
    financial_year_id         : Optional[int]
    financial_year            : Optional[str]
    voucher_number            : Optional[str]
    appointment_date          : Optional[date]
    appointment_time_from     : Optional[str]
    appointment_time_to       : Optional[str]
    source_of_enquiry_id      : Optional[int]
    source                    : Optional[str]
    appointment_status_id     : Optional[int]
    appointment_status        : Optional[str]
    consultant_id             : Optional[int]
    consultation_mode_id      : Optional[int]
    consultation_mode         : Optional[str]
    consultation_tool_id      : Optional[int]
    consultation_tool         : Optional[str]
    employee_number           : Optional[str]
    first_name                : Optional[str]
    middle_name               : Optional[str]
    last_name                 : Optional[str]
    gross_amount              : Optional[float]
    discount_percentage       : Optional[float]
    special_discount_percentage: Optional[float]
    special_discount_amount    : Optional[float]
    net_amount                 : Optional[float]
    igst_amount                : Optional[float]
    sgst_amount                : Optional[float]
    cgst_amount                : Optional[float]
    bill_amount                : Optional[float]
    remarks                    : Optional[str]
    is_editable                :Optional[bool]=False
    
    class Config:
        orm_mode = True
        from_attributes = True


class OffAppointmentVisitDetailsViewSchema(BaseModel):
    visit_master_id   : Optional[int]
    visit_details_id  : int
    service_id        : int
    service_goods_name: str
    is_main_service   : str

    class Config:
        orm_mode = True
        from_attributes = True


class ResponseSchema(BaseModel):
    appointment_master: OffAppointmentMasterViewSchema
    visit_master      : OffAppointmentVisitMasterViewSchema
    visit_details     : List[OffAppointmentVisitDetailsViewSchema]
    # is_editable       : Optional[bool] = False


 

#------------------- swathy

class OffViewServiceGoodsDetailsDisplay(BaseModel):
    service_goods_details_id      : int
    service_goods_master_id       : int
    hsn_sac_class_id              : int
    hsn_sac_class                 : str
    group_id                      : int
    service_master_group_name     : Optional[str]
    sub_group_id                  : int
    service_master_sub_group_name : Optional[str]
    category_id                   : int
    service_master_category_name  : Optional[str]
    sub_category_id               : int
    service_master_sub_category_name : Optional[str]
    service_goods_name               : str
    hsn_sac_id                       : int
    hsn_sac_code                     : str
    hsn_sac_description              : Optional[str]
    sku_code_id                      : int
    stock_keeping_unit_code          : Optional[str]
    has_consultation                 : str
    is_bundled_service               : str
    bundled_service_goods_id         : int
    display_order                    : Optional[int]
    
    class Config:
        orm_mode = True
        from_attributes = True

    
   

class OffViewServiceGoodsMasterDisplay(BaseModel):
    service_goods_master_id                 : int
    hsn_sac_class_id                        : int
    hsn_sac_class                           : Optional[str]
    group_id                                : int
    service_goods_group_name                : Optional[str]
    sub_group_id                            : int
    service_goods_sub_group_name            : Optional[str]
    category_id                             : int
    service_goods_category_name             : Optional[str]
    sub_category_id                         : int
    service_goods_sub_category_name         : Optional[str]
    service_goods_name                      : str
    hsn_sac_id                              : int
    hsn_sac_code                            : Optional[str]
    hsn_sac_description                     : Optional[str]
    gst                                     : str
    sku_code_id                             : int
    stock_keeping_unit_code                 : Optional[str]
    has_consultation                        : str
    is_bundled_service                      : str
    details                                 : Optional[List[OffViewServiceGoodsDetailsDisplay]] = None
    
    class Config:
        orm_mode = True
        from_attributes = True
        

class OffDocumentDataBase(BaseModel):
    document_data_name      :str
    has_expiry              : str


    
#-----------Aparna
class Slot(BaseModel):
    # Define the fields for a slot
    start_time      : datetime
    end_time        : datetime

class ConsultationRequest(BaseModel):
   
    service_id      : int
    consultant_id   : int
    start_time      : str  
    end_time        : str 



class OffServiceGoodsMasterCreate(BaseModel):
    hsn_sac_class_id        : int
    group_id                : int
    sub_group_id            : int
    category_id             : int
    sub_category_id         : int
    service_goods_name      : str
    hsn_sac_id              : int
    sku_code_id             : int
    has_consultation        : str
    is_bundled_service      : str

class OffServiceGoodsDetailsCreate(BaseModel):
    id                      :int
    service_goods_master_id : int
    display_order           : int


class SaveServicesGoodsMasterRequest(BaseModel):
    master      : List[OffServiceGoodsMasterCreate]
    details     : Optional[List[OffServiceGoodsDetailsCreate]] = None
    



class EmployeeResponse(BaseModel):
    employees       : List[dict]
    


class ServiceGoodsPrice(BaseModel):
    id                      : int
    service_name            : str
    configuration_status    : Optional[str] = None
    service_type            : Optional[str] = None
    bundled_service         : Optional[str] = None

class PriceListResponse(BaseModel):
    price_list              : List[ServiceGoodsPrice]
    
    



    
class SetPriceModel(BaseModel):
    service_goods_master_id             :int
    constitution_id                     :int
    service_charge                      : Optional[int]
    govt_agency_fee                     : Optional[int]
    stamp_duty                          : Optional[int]
    stamp_fee                           : Optional[int]
    effective_from_date                 : Optional[date]
    effective_to_date                   : Optional[date]

class PriceHistoryModel(BaseModel):
    constitution_id                     : int
    business_constitution_name          : str
    service_charge                      : Optional[float]
    govt_agency_fee                     : Optional[float]
    stamp_duty                          : Optional[float]
    stamp_fee                           : Optional[float]
    effective_from_date                 : Optional[date]
    effective_to_date                   : Optional[date]

class ServiceModel(BaseModel):
    id                              : int
    service_name                    : str
    constitution_id                 : int
    business_constitution_name      : str
    business_constitution_code      : str
    price_history                   :   List[PriceHistoryModel]
    
class ServiceModelSchema(BaseModel):
    price_master_id                 : Optional[int] = 0
    constitution_id                 : int
    business_constitution_name      : str
    service_goods_master_id         : int
    service_goods_price_master_id   : int
    service_name                    : str
    business_constitution_code      : str
    service_charge                  : float
    govt_agency_fee                 : float
    stamp_duty                      : float
    stamp_fee                       : float
    effective_from_date             : Optional[date]
    effective_to_date               : Optional[date]




class BundledServiceSchema(BaseModel):
    row_id                              : int
    price_master_id                     : Optional[int] = None
    service_id                          : Optional[int] = None
    service_goods_name                  : Optional[str] = None
    is_bundled_service                  : Optional[str] = None
    constitution_id                     :Optional[int] = None
    business_constitution_name          :Optional[str] = None
    service_charge                      : Optional[float] = None
    govt_agency_fee                     : Optional[float] = None
    stamp_duty                          : Optional[float] = None
    stamp_fee                           : Optional[float] = None
    effective_from_date                 : Optional[str ]=None
    effective_to_date                   : Optional[str ]=None


    class Config:
        orm_mode = True


class BundledServiceResponseSchema(BaseModel):
    service_details                 : List[BundledServiceSchema]


# class BundledServiceResponse(RootModel[List[BundledServiceSchema]]):
#     pass
    
class ServicePriceHistory(BaseModel):
    constitution_id                     : int
    business_constitution_name          : str
    service_charge                      : Optional[float]
    govt_agency_fee                     : Optional[float]
    stamp_duty                          : Optional[float]
    stamp_fee                           : Optional[float]
    effective_from_date                 : Optional[date]
    effective_to_date                   : Optional[date]



class PriceData(BaseModel):
    id                      : Optional[int] = None
    constitution_id         : int
    service_charge          : float
    govt_agency_fee         : float
    stamp_duty              : float
    stamp_fee               : float
    effective_from_date     : date
    effective_to_date       : Optional[date] = None
   
    

class OffDocumentDataMasterBase(BaseModel):
    id                  : int
    document_data_name  : str  
    data_type           : str
    has_expiry          : str
      
    
class Item(BaseModel):
    id                          : int
    service_goods_master_id     : int
    bundled_service_goods_id    : int
    display_order               : int
    service_charge              : float
    govt_agency_fee             : float
    stamp_fee                   : float
    stamp_duty                  : float

class Bundle(BaseModel):
    service_id              : int
    service_name            : str
    service_charge          : float
    govt_agency_fee         : float
    stamp_fee               : float
    stamp_duty              : float
    items                   : List[Item]
    sub_item_total          : Dict[str, float]
    grand_total             : Dict[str, float]
    
    
class OffServiceDocumentDataMasterDisplay(BaseModel):
    service_goods_master_id : int
    group_id                : int
    sub_group_id            : int
    category_id             : int
    sub_category_id         : int
    constitution_id         : int
  
 

class OffServiceDocumentDataDetails(BaseModel):
    id                          : int
    document_data_master_id     : int
    nature_of_possession_id     : int
    display_order               : int
 
class OffServiceDocumentDataRequired(BaseModel):
    document_data_category_id   :   int
    details                     : List[OffServiceDocumentDataDetails]
 

class ServiceDocuments(BaseModel):
    personal_doc                : Optional[List[OffServiceDocumentDataRequired]] = None
    constitution_doc            : Optional[List[OffServiceDocumentDataRequired]] = None
    business_place_doc         : Optional[List[OffServiceDocumentDataRequired]] = None
    utility_doc                 : Optional[List[OffServiceDocumentDataRequired]] = None
   
class SaveServiceDocumentDataMasterRequest(BaseModel):
    Service         : Optional[OffServiceDocumentDataMasterDisplay] = None
    Documents       : Optional[List[ServiceDocuments]] = None
    
    
class OffViewServiceDocumentsDataDetailsSchema(BaseModel):
    service_document_data_details_id    : int
    service_document_data_master_id     : int
    constitution_id                     : int
    business_constitution_name          : str
    business_constitution_code          : str
    description                         : Optional[str]
    document_data_master_id             : int
    document_data_type_id               : int
    document_data_type                  : str
    document_data_name                  : str
    has_expiry                          : str
    nature_of_possession_id             : Optional[int]
    nature_of_possession                : Optional[str]
    display_order                       : int
    class Config:
        from_attributes = True  
   

   
class OffViewServiceDocumentsDataDetailsDocCategory(BaseModel):
    document_data_category_id               : int
    document_data_category_category_name    : str
    details                                 : List[OffViewServiceDocumentsDataDetailsSchema]
    class Config:
        from_attributes = True  
   
class OffViewServiceDocumentsDataMasterSchema(BaseModel):
    service_document_data_master_id         : int
    service_goods_master_id                 : int
    service_goods_name                      : str
    group_id                                : int
    group_name                              : Optional[str]
    sub_group_id                            : int
    sub_group_name                          : Optional[str]
    category_id                             : int
    category_name                           :Optional[str]
    sub_category_id                         : int
    sub_category_name                       : Optional[str]
    constitution_id                         : int
    business_constitution_name              : str
    business_constitution_code              : str
    description                             : Optional[str]
    doc_data_status                         : Optional[str] = None 
    details                                 : List[OffViewServiceDocumentsDataDetailsDocCategory] = []

    class Config:
        from_attributes = True
        

       
class SubGroup(BaseModel):
    id              : int
    sub_group_name  : str

class Category(BaseModel):
    id              : int
    category_name   : str

class SubCategory(BaseModel):
    id                  : int
    sub_category_name   : str
    
class Service_Group(BaseModel):
    id                  : int
    group_name          : str
    

class ServiceDocumentsList_Group(BaseModel):
    group           : Optional[Service_Group] =None
    sub_group       : Optional[List[SubGroup]] =None
    category        :Optional[List[Category]]=None
    sub_category    :Optional[List[SubCategory]]=None

class TimeSlotResponse(BaseModel):
    id                  : int
    consultant_id       : int
    day_of_week_id      : int
    day_long_name       : str
    consultation_mode_id: int
    consultation_mode   : str
    morning_start_time  : Optional[time]
    morning_end_time    : Optional[time]
    afternoon_start_time: Optional[time]
    afternoon_end_time  : Optional[time]
    is_normal_schedule  : str
    consultation_date   : Optional[date]
    effective_from_date : Optional[date]
    effective_to_date   : Optional[date]
    created_by          : int
    created_on          : datetime
    modified_by         : Optional[int]
    modified_on         : Optional[datetime]
    
   

    class Config:
        orm_mode = True
    
    
#------------------------------------------------------------------------------------------------
###################CONSULTANTS AND SERVICES####################################################




class ConsultantEmployee(BaseModel):
    employee_id         : int
    first_name          :str
    middle_name         :Optional[str]
    last_name           :str
    # employee_name: str
    employee_number     : str
    personal_email      : str
    official_email      : Optional[str]
    personal_mobile     : str
    official_mobile     : Optional[str]
    department_name     : str
    designation         : Optional[str]
    
class ConsultantService(BaseModel):
    # consultant_id:int
    service_goods_master_id     :Optional[int]=None
    consultation_fee            :float
    slot_duration_in_minutes    :int
    effective_from_date         : date
    effective_to_date           : Optional[date] = None
    
class ConsultantServiceDetailsResponse(BaseModel):
    id                      : int
    consultant_id           : int
    service_goods_master_id: int
    service_goods_name      : str
    consultation_fee        : float
    slot_duration_in_minutes: int
    effective_from_date     : date
    effective_to_date       : Optional[date]

class ConsultantServiceDetailsListResponse(BaseModel):
    services                : List[ConsultantServiceDetailsResponse]



class ConsultantScheduleCreate(BaseModel):
    # consultant_id: int
    day_of_week_id          : Optional[int]=None
    consultation_mode_id    : int
    morning_start_time      : Optional[time] = None
    morning_end_time        : Optional[time] = None
    afternoon_start_time    : Optional[time] = None
    afternoon_end_time      : Optional[time] = None
    is_normal_schedule      : str
    consultation_date       : Optional[date] = None
    effective_from_date     : Optional[date] = None
    effective_to_date       : Optional[date] = None


#------------------------------------------------------------------------------------------------
###################ENQUIRY####################################################
#------------------------------------------------------------------------------------------------
class OffEnquiryMasterSchema(BaseModel):

    customer_number         :Optional[str] 
    first_name              : str
    middle_name             : Optional[str] 
    last_name               : Optional[str] 
    gender_id               : Optional[int]
    date_of_birth           :Optional[date]
    mobile_number           : Optional[str]
    whatsapp_number         : Optional[str]
    email_id                : Optional[str]
    house_or_building_name  : Optional[str]
    road_or_street_name     : Optional[str]
    locality                : Optional[str]
    pin_code                : Optional[str]
    village_id              : Optional[int] 
    post_office_id          : Optional[int]
    lsg_type_id             : Optional[int]
    lsg_id                  :  Optional[int]
    taluk_id                : Optional[int]
    district_id             : Optional[int]
    state_id                : Optional[int]
    country_id              : Optional[int]
    class Config:
        orm_mode = True
        from_attributes = True


class OffEnquiryDetailsSchema(BaseModel):
    id                      :Optional[int] =None 
    financial_year_id       : Optional[int]
    # enquiry_number: Optional[str]
    enquiry_date            : Optional[date]
    source_of_enquiry_id    : Optional[int]
    enquiry_status_id       : Optional[int]
    enquirer_type_id        : Optional[int]
    company_or_business_name: Optional[str]
    remarks                 : Optional[str]
    class Config:
        orm_mode = True
        from_attributes = True


class OffEnquiryResponseSchema(BaseModel):
    enquiry_master  : OffEnquiryMasterSchema
    enquiry_details : List[OffEnquiryDetailsSchema]

    class Config:
        orm_mode        = True
        from_attributes = True


#get
class OffViewEnquiryMasterSchema(BaseModel):
    enquiry_master_id        : int
    customer_number          : Optional[str]
    first_name               : Optional[str]
    middle_name              : Optional[str]
    last_name                : Optional[str]
    gender_id                : Optional[int]
    gender                   : Optional[str]
    date_of_birth            : Optional[date]
    mobile_number            : Optional[str]
    whatsapp_number          : Optional[str]
    email_id                 : Optional[str]
    house_or_building_name   : Optional[str]
    road_or_street_name      : Optional[str]
    locality                 : Optional[str]
    pin_code                 : Optional[str]
    village_id               : Optional[int]
    village_name             : Optional[str]
    post_office_id           : Optional[int]
    post_office_name         : Optional[str]
    lsg_type_id              : Optional[int]
    lsg_type                 : Optional[str]
    lsg_id                   : Optional[int]
    lsg_name                 : Optional[str]
    taluk_id                 : Optional[int]
    taluk_name               : Optional[str]
    district_id              : Optional[int]
    district_name            : Optional[str]
    state_id                 : Optional[int]
    state_name               : Optional[str]
    country_id               : Optional[int]
    country_name_english     : Optional[str]
    country_name_arabic      : Optional[str]
    is_locked                : str
    locked_on                : Optional[date]
    locked_by                : Optional[int]
    
class OffViewEnquiryDetailsSchema(BaseModel):
    enquiry_details_id      : int
    enquiry_master_id        : int
    financial_year_id       : Optional[int]
    financial_year          : Optional[str]
    enquiry_number          : Optional[str]
    enquiry_date            : Optional[date]
    source_of_enquiry_id    : Optional[int]
    source                  : Optional[str]
    enquiry_status_id       : Optional[int]
    enquiry_status          : Optional[str]
    enquirer_type_id        : Optional[int]
    person_type             : Optional[str]
    company_or_business_name: Optional[str]
    remarks                 : Optional[str]
    is_editable             : Optional[bool] =  False

class OffViewEnquiryResponseSchema(BaseModel):
    enquiry_master  : OffViewEnquiryMasterSchema
    enquiry_details : List[OffViewEnquiryDetailsSchema]
   # is_editable     : Optional[bool] = False

    class Config:
        orm_mode        = True
        from_attributes = True

        
class ConsultationToolSchema(BaseModel):
    id                 : int
    consultation_tool  : str

    class Config:
        orm_mode        = True
        from_attributes = True


class ConsultationModeSchema(BaseModel):
    id                : int
    consultation_mode : str
    is_deleted        : str

    class Config:
        orm_mode        = True
        from_attributes = True

        
        
      
class OffConsultationTaskDetailsSchema(BaseModel):
    # task_master_id: int
    id              : int
    service_id      : int
    is_main_service : str

    class Config:
        orm_mode = True





class OffConsultationTaskMasterSchema(BaseModel):
    task_date            : Optional[date]
    consultant_id        : int
    appointment_master_id: int
    visit_master_id      : int
    task_status_id       : int
    task_priority_id     : int
    remarks              : Optional[str]
    details              : List[OffConsultationTaskDetailsSchema]

    class Config:
        orm_mode = True





class AdditionalServices(BaseModel):
    service_detail_id:int
    service_id: int
    service_name:str




# class OffViewConsultationTaskMasterSchema(BaseModel):
#     consultation_task_master_id           : int
#     task_date                             : datetime
#     consultant_id                         : int
#     employee_number                       : str
#     employee_first_name                   : str
#     employee_middle_name                  : Optional[str]
#     employee_last_name                    : str
#     appointment_master_id                 : int
#     appointee_full_name                   : str
#     appointee_gender_id                   : int
#     appointee_gender                      : str
#     customer_number                       : Optional[str]
#     business_name                         : Optional[str]
#     locality                              : Optional[str]
#     pin_code                              : Optional[str]
#     post_office_id                        : Optional[int]
#     post_office_name                      : Optional[str]
#     taluk_id                              : Optional[int]
#     taluk_name                            : Optional[str]
#     district_id                           : Optional[int]
#     district_name                         : Optional[str]
#     state_id                              : Optional[int]
#     state_name                            : Optional[str]
#     appointee_mobile_number               : Optional[str]
#     appointee_whatsapp_number             : Optional[str]
#     appointee_email_id                    : Optional[str]
#     visit_master_id                       : int
#     visit_master_appointment_time_from    : str
#     visit_master_appointment_time_to      : Optional[str]
#     consultation_mode_id                  : int
#     consultation_mode                     : str
#     consultation_tool_id                  : int
#     consultation_tool                     : str
#     task_status_id                        : int
#     task_status                           : Optional[str]
#     task_priority_id                      : int
#     task_priority                         : Optional[str]
#     remarks                               : Optional[str]
#     consultation_task_details_id          : Optional[int]
#     task_master_id                        : Optional[int]
#     service_id                            : Optional[int]
#     hsn_sac_class_id                      : int
#     hsn_sac_class                         : str
#     hsn_sac_id                            : int
#     hsn_sac_code                          : str
#     group_id                              : int
#     group_name                            : Optional[str]
#     sub_group_id                          : int
#     sub_group_name                        : Optional[str]
#     category_id                           : int
#     category_name                         : Optional[str]
#     sub_category_id                       : int
#     sub_category_name                     : Optional[str]
#     service_goods_name                    : str
#     sku_code_id                           : int
#     unit_code                             : Optional[str]
#     additional_services                   : Optional[List[AdditionalServices]]

#     class Config:
#         orm_mode                           = True

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
    legal_name: Optional[str]
    locality: Optional[str]
    pin_code: Optional[str]
    post_office_id: Optional[int]
    post_office_name: Optional[str]
    taluk_id: Optional[int]
    taluk_name: Optional[str]
    district_id: Optional[int]
    district_name: Optional[str]
    state_id: Optional[int]
    state_name: Optional[str]
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
    # consultation_task_details_is_deleted: Optional[str]
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
    # is_bundled_service: str
    # is_main_service: Optional[str]
    additional_services: Optional[List[AdditionalServices]]

    class Config:
        orm_mode = True
    

#-------------------------------------OFFER-------------------------------------------

class  OffOfferCategoryResponse(BaseModel):

    id              : int
    offer_category  : str
    description     : str
    is_deleted      : str


class OffOfferMasterSchema(BaseModel):

    offer_category_id   : int
    offer_name          : str
    offer_percentage    : Optional[float]= None
    effective_from_date : date
    effective_to_date   : date


class OffOfferMasterSchemaResponse(BaseModel):

    id                  : Optional[int] = None
    offer_category_id   : int
    offer_name          : str
    offer_percentage    : Optional[float]= None
    effective_from_date : date
    effective_to_date   : Optional[date] =None   
    created_by          : int
    created_on          : datetime
    modified_by         : Optional[int]
    modified_on         : Optional[datetime]
    is_deleted          : str
    deleted_by          : Optional[int]
    deleted_on          : Optional[datetime]    

class OffOfferDetailsSchema(BaseModel):

    offer_master_id         : Optional[int] = None
    service_goods_master_id : Optional[int] = None


class SaveOfferDetails(BaseModel):

    master: list[OffOfferMasterSchema]
    details: Optional[list[OffOfferDetailsSchema]]=None


#------------------------WORKORDER SCHEMA-----------------------------------
class OffWorkOrderMasterSchema(BaseModel):
 
    id                  : Optional[int] =None
    financial_year_id   : Optional[int] = None
    enquiry_master_id      : Optional[int] =None
    appointment_master_id  : Optional[int] = None
    visit_master_id        : Optional[int] = None
    customer_id            : Optional[int] = None
    enquiry_details_id     : Optional[int] = None
    work_order_number   : Optional[str] = None
    work_order_date     : Optional[date] = None
    first_name          : Optional[str] = None
    middle_name         : Optional[str] = None
    last_name           : Optional[str] = None
    gender_id           : int
    date_of_birth       : Optional[date] = None
    mobile_number       : Optional[str] = None
    whatsapp_number     : Optional[str] = None
    email_id            : Optional[str] = None
    house_or_building_name  : Optional[str] = None
    road_or_street_name     : Optional[str] = None
    locality                : Optional[str] = None
    pin_code                : Optional[str] = None
    post_office_id          : Optional[int] = None
    village_id              : Optional[int] = None
    lsg_type_id             : Optional[int] = None
    lsg_id                  : Optional[int] = None
    taluk_id                : Optional[int] = None
    district_id             : Optional[int] = None
    state_id                : Optional[int] = None
    country_id              : Optional[int] = None
    remarks                 : Optional[str] = None
    contact_person_name     : Optional[str] = None
    contact_person_mobile_number    : Optional[str] = None
    contact_person_whatsapp_number  : Optional[str] = None
    contact_person_email_id         : Optional[str] = None
    work_order_status_id            : Optional[int] = None
    class Config:
        orm_mode = True
        from_attributes = True



class WorkOrderDetailsSchema(BaseModel):
    
    id                        : Optional[int] = None
    work_order_master_id        : Optional[int] = None
    service_goods_master_id     : Optional[int] = None
    # service_goods_name          : Optional[str] = None
    constitution_id             : Optional[int] = None
    trade_name                  : Optional[str] = None
    legal_name                 : Optional[str] = None
    business_activity_type_id          : Optional[int] = None
    business_activity_master_id : Optional[int] = None
    business_activity_id      : Optional[int] = None
    has_branches              : Optional[str] = 'no'
    number_of_branches        : Optional[int] = None
    has_godowns               : Optional[str] = 'no'
    number_of_godowns         : Optional[int] = None
    number_of_directors       : Optional[int] = None
    number_of_partners        : Optional[int] = None
    number_of_shareholders    : Optional[int] = None
    number_of_trustees        : Optional[int] = None
    number_of_members         : Optional[int] = None
    number_of_authorized_signatory : Optional[int] = None
    is_main_service         : Optional[str] ='no'             
    is_bundle_service       : Optional[str] ='no' 
    bundle_service_id       : Optional[int] = None
    is_depended_service     : Optional[str] ='no' 
    processing_order        : Optional[int] = None
    is_service_required        : Optional[str] = 'YES'
    service_required_date   : Optional[date] = None
    service_status_id    : Optional[int] = None
    file_opened_on        : Optional[date] = None
    file_closed_on        : Optional[date] = None
    rack_number           : Optional[int] = None
    shelf_number          : Optional[int] = None
    file_number           : Optional[int] = None
    remarks               : Optional[str] = None
    # depended_on: List['WorkOrderDependancySchema'] = []
    sub_services: List['WorkOrderDetailsSchema'] = []

    class Config:
        orm_mode = True
        from_attributes = True

class WorkOrderDependancySchema(BaseModel):
    id : Optional[int]=None
    work_order_master_id    : int
    work_order_details_id   : int
    dependent_on_work_id    : int
    is_deleted              : Optional[str] ='no'
    service_goods_name      : Optional[str] = None 

    class Config:
        orm_mode = True
        from_attributes = True


class CreateWorkOrderRequest(BaseModel):
    master: OffWorkOrderMasterSchema
    main_service: List[WorkOrderDetailsSchema]


class WorkOrderDetailsResponseSchema(BaseModel):
    
    id                        : Optional[int] = None
    work_order_master_id        : Optional[int] = None
    service_id                  : Optional[int] = None
    constitution_id             : Optional[int] = None
    trade_name                  : Optional[str] = None
    legal_name                 : Optional[str] = None
    business_activity_type_id          : Optional[int] = None
    business_activity_master_id : Optional[int] = None
    business_activity_id      : Optional[int] = None
    has_branches              : Optional[str] = 'no'
    number_of_branches        : Optional[int] = None
    has_godowns               : Optional[str] = 'no'
    number_of_godowns         : Optional[int] = None
    number_of_directors       : Optional[int] = None
    number_of_partners        : Optional[int] = None
    number_of_shareholders    : Optional[int] = None
    number_of_trustees        : Optional[int] = None
    number_of_members         : Optional[int] = None
    is_main_service         : Optional[str] ='no'             
    is_bundle_service       : Optional[str] ='no' 
    bundle_service_id       : Optional[int] = None
    is_depended_service     : Optional[str] ='no' 
    processing_order        : Optional[int] = None
    service_required        : Optional[str] = 'NO'
    service_required_date   : Optional[date] = None
    service_status_id    : Optional[int] = None
    file_opened_on        : Optional[date] = None
    file_closed_on        : Optional[date] = None
    rack_number           : Optional[int] = None
    shelf_number          : Optional[int] = None
    file_number           : Optional[int] = None
    remarks               : Optional[str] = None
    depended_on: List['WorkOrderDependancySchema'] = []
    sub_services: List['WorkOrderDetailsSchema'] = []

    class Config:
        orm_mode = True
        from_attributes = True



# class WorkOrderResponseSchema(BaseModel):
#     work_order: OffWorkOrderMasterSchema
#     # service_data: List[WorkOrderDetailsSchema]
#     service_data: List[WorkOrderDetailsResponseSchema]
#     class Config:
#         orm_mode = True
#         from_attributes = True



class  WorkOrderBusinessPlaceDetailsScheema(BaseModel):

    id                      : Optional[int] = None
    work_order_details_id   : Optional[int] = None
    business_place_type     : Optional[str] = 'GODOWN'  
    nature_of_possession_id : Optional[int] = None
    business_place_document_id   : Optional[int] = None
    utility_document_id     : Optional[int] = None
    is_deleted              : Optional[str] = 'no'


class CreateWorkOrderSetDtailsRequest(BaseModel):
    workOrderDetails: WorkOrderDetailsSchema
    businessPlaceDetails: List[WorkOrderBusinessPlaceDetailsScheema]


class OffAppointmentMasterSchema(BaseModel):
 
    id              : Optional[int]
    full_name       : str
    customer_number : str
    mobile_number   : Optional[str]
    whatsapp_number : Optional[str]
    email_id        : Optional[str]
    gender_id       :Optional[int]
    locality        : Optional[str]
    pin_code        : Optional[str]
    post_office_id  : Optional[int]
    taluk_id        : Optional[int]
    district_id     : Optional[int]
    state_id        : Optional[int]

    class Config:
        orm_mode = True
        from_attributes=True



class ServiceDetail(BaseModel):
    row_id              : int
    price_master_id     : int
    service_id          : int
    service_goods_name  : str
    is_bundled_service  : str
    constitution_id     : int
    business_constitution_name  : str
    service_charge              : float
    govt_agency_fee             : float
    stamp_duty                  : float
    stamp_fee                   : float
    effective_from_date         : str
    effective_to_date           : str

class ServiceDetailListResponse(BaseModel):
    data: List[ServiceDetail]

class ServiceRequest(BaseModel):
    service_id: int
    input_date: str



class OffViewWorkOrderMasterSchema(BaseModel):

    work_order_master_id     : Optional[int] =None
    financial_year_id   : Optional[int] = None
    financial_year      :  Optional[str] = None
    enquiry_master_id      : Optional[int] =None
    appointment_master_id  : Optional[int] = None
    visit_master_id        : Optional[int] = None
    enquiry_details_id     : Optional[int] = None
    customer_id             : Optional[int] =None
    work_order_number   : Optional[str] = None
    work_order_date     : Optional[date] = None
    
    first_name          : Optional[str] = None
    middle_name         : Optional[str] = None
    last_name           : Optional[str] = None
    gender_id           : Optional[int] = None
    gender              : Optional[str] = None
    date_of_birth       : Optional[date] = None
    mobile_number       : Optional[str] = None
    whatsapp_number     : Optional[str] = None
    email_id            : Optional[str] = None

    house_or_building_name  : Optional[str] = None
    road_or_street_name     : Optional[str] = None
    locality                : Optional[str] = None
    pin_code                : Optional[str] = None
    post_office_id          : Optional[int] = None
    post_office_name        : Optional[str] = None
    village_id              : Optional[int] = None
    village_name            : Optional[str] = None
    lsg_type_id             : Optional[int] = None
    lsg_type                : Optional[str] = None
    lsg_id                  : Optional[int] = None
    lsg_name                : Optional[str] = None
    taluk_id                : Optional[int] = None
    taluk_name              : Optional[str] = None
    district_id             : Optional[int] = None
    district_name           : Optional[str] = None
    state_id                : Optional[int] = None
    state_name              : Optional[str] = None
    country_id              : Optional[int] = None
    country_name            : Optional[str] = None
    remarks                 : Optional[str] = None

    contact_person_name     : Optional[str] = None
    contact_person_mobile_number    : Optional[str] = None
    contact_person_whatsapp_number  : Optional[str] = None
    contact_person_email_id         : Optional[str] = None
    work_order_status_id            : Optional[int] = None
    work_order_status               : Optional[str] = None
    # is_editable                     : Optional[bool]= False
    class Config:
        orm_mode = True
        from_attributes = True


class WorkOrderViewResponseSchema(BaseModel):
    work_order: OffViewWorkOrderMasterSchema
    is_editable: Optional[bool] =False

    class Config:
        orm_mode = True

class OffViewWorkOrderDetailsSchema(BaseModel):
    
    work_order_details_id       : Optional[int] = None
    work_order_master_id        : Optional[int] = None
    service_goods_master_id     : Optional[int] = None
    service_goods_name          : Optional[str] = None
    constitution_id             : Optional[int] = None
    business_constitution_name  : Optional[str] = None
    trade_name                  : Optional[str] = None
    legal_name                 : Optional[str] = None
    business_activity_type_id   : Optional[int] = None
    business_activity_type      : Optional[str] = None
    business_activity_master_id : Optional[int] = None
    business_activity_master  : Optional[str] = None  
    business_activity_id      : Optional[int] = None
    business_activity         : Optional[str] = None
    has_branches              : Optional[str] = 'no'
    number_of_branches        : Optional[int] = None
    has_godowns               : Optional[str] = 'no'
    number_of_godowns         : Optional[int] = None
    number_of_directors       : Optional[int] = None
    number_of_partners        : Optional[int] = None
    number_of_shareholders    : Optional[int] = None
    number_of_trustees        : Optional[int] = None
    number_of_members         : Optional[int] = None
    is_main_service         : Optional[str] ='no'             
    is_bundle_service       : Optional[str] ='no' 
    bundle_service_id       : Optional[int] = None
    is_depended_service     : Optional[str] ='no' 
    processing_order        : Optional[int] = None
    service_required        : Optional[str] = 'YES'
    service_required_date   : Optional[date] = None
    service_status_id       : Optional[int] = None
    service_status          : Optional[str] = None
    file_opened_on        : Optional[date] = None
    file_closed_on        : Optional[date] = None
    rack_number           : Optional[int] = None
    shelf_number          : Optional[int] = None
    file_number           : Optional[int] = None
    remarks               : Optional[str] = None
    depended_on: List['WorkOrderDependancySchema'] = []
    sub_services: List['OffViewWorkOrderDetailsSchema'] = []

    class Config:
        orm_mode = True
        from_attributes = True




class WorkOrderResponseSchema(BaseModel):
    work_order: OffViewWorkOrderMasterSchema
    service_data: List[OffViewWorkOrderDetailsSchema]
    is_editable : Optional[bool] = False
    class Config:
        orm_mode = True
        from_attributes = True

class OffViewBusinessPlaceDetailsScheema(BaseModel):

    business_place_id       : Optional[int] = None
    work_order_details_id   : Optional[int] = None
    business_place_type     : Optional[str] = 'GODOWN'  
    nature_of_possession_id : Optional[int] = None
    nature_of_possession    : Optional[str] = None
    business_place_document_id   : Optional[int] = None
    utility_document_id     : Optional[int] = None
    document_data_name      : Optional[str] = None
    is_deleted              : Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True

class WorkOrderSetDetailsResponseSchema(BaseModel):
    workOrderDetails : OffViewWorkOrderDetailsSchema
    pricipalPlaceDetails :OffViewBusinessPlaceDetailsScheema
    
    additionalPlaceDetails : List[OffViewBusinessPlaceDetailsScheema]



class WorkOrderDependancyResponseSchema(BaseModel):
    workOrderDetails : OffViewWorkOrderDetailsSchema
    dipendancies : List[WorkOrderDependancySchema]




class CreateWorkOrderDependancySchema(BaseModel):
    id : Optional[int]=None
    work_order_master_id    : int
    work_order_details_id   : int
    dependent_on_work_id    : int
    is_deleted              : Optional[str] ='no'

    class Config:
        orm_mode = True
        from_attributes = True



class OffViewServiceGoodsPriceMasterSchema(BaseModel):

    service_goods_price_master_id   : Optional[int]
    service_goods_master_id         : Optional[int]
    hsn_sac_class_id                : Optional[int]
    hsn_sac_class                   : Optional[str]
    group_id                        : Optional[int]
    group_name                      : Optional[str]
    sub_group_id                    : Optional[int]
    sub_group_name                  : Optional[str]
    category_id                     : Optional[int]
    category_name                   : Optional[str]
    sub_category_id                 : Optional[int]
    sub_category_name               : Optional[str]
    service_goods_name              : Optional[str]
    hsn_sac_id                      : Optional[int]
    hsn_sac_code                    : Optional[str]
    hsn_sac_description             : Optional[str]
    sku_code_id                     : Optional[int]
    unit_code                        : Optional[str]
    has_consultation                 : Optional[str]
    # is_consultancy_service: Optional[int]
    is_bundled_service               : Optional[str]
    services_goods_master_modified_by   : Optional[int]
    services_goods_master_modified_on   : Optional[datetime]
    services_goods_master_is_deleted    : Optional[str]
    services_goods_master_deleted_by    : Optional[int]
    services_goods_master_deleted_on    : Optional[datetime]
    constitution_id                     : Optional[int]
    business_constitution_name          : Optional[str]
    business_constitution_code          : Optional[str]
    business_constitution_description   : Optional[str]
    pan_code                            : Optional[str]
    service_charge                      : Optional[float]
    govt_agency_fee                     : Optional[float]
    stamp_duty                          : Optional[float]
    stamp_fee                           : Optional[float]
    effective_from_date                 : Optional[date]
    effective_to_date                   : Optional[date]
    service_goods_price_master_created_by   : Optional[int]
    service_goods_price_master_created_on   : Optional[datetime]

    class Config:
        orm_mode = True
        from_attributes = True


class OffServiceGoodsPriceMasterSchema(BaseModel):

    id                          : Optional[int] = None
    service_goods_master_id     : Optional[int] 
    constitution_id             : Optional[int] 
    service_charge              : Optional[float] = 0.00 
    govt_agency_fee             : Optional[float] = 0.00 
    stamp_duty                  : Optional[float] = 0.00 
    stamp_fee                   : Optional[float] = 0.00 
    effective_from_date         : Optional[date] 
    effective_to_date           : Optional[date] 
    # created_by : Optional[int] 
    # created_on 

class ServiceGoodsPriceDetailsSchema(BaseModel):
    service: OffViewWorkOrderDetailsSchema
    prices: OffViewServiceGoodsPriceMasterSchema

class ServiceGoodsPriceResponseSchema(BaseModel):
    workOrderMaster         : OffViewWorkOrderMasterSchema
    workOrderDetails        : List[ServiceGoodsPriceDetailsSchema]


class UpdateCustomerDataDocumentSchema(BaseModel):
    id                  : int
    data                : str
    valid_from_date     : Optional[date] = None
    valid_to_date       : Optional[date] = None

    class Config:
        orm_mode = True
        from_attributes = True


class DocumentsSchema(BaseModel):
    valid_from_date         : Optional[date] = None
    valid_to_date           : Optional[date] = None
    business_place_type_and_name     : Optional[str]  = None
    stake_holder_role           : Optional[str] = None
    signatory_serial_number     : Optional[str] = None
    remarks                     : Optional[str]=None

    class Config:
        orm_mode = True
        from_attributes = True

class OffServiceTaskMasterSchema(BaseModel):
    task_status_id          : int
    # task_priority_id        : int
    remarks                 : Optional[str] = None
    
    class Config:
        orm_mode            :  True



class OffServiceTaskHistorySchema(BaseModel):
    service_task_master_id       : int
    history_updated_date         : date
    history_updated_time         : time
    history_update_by            : int
    history_update_by_first_name : str
    history_update_by_middle_name: str
    history_update_by_last_name  : str
    history_description          : str

    class Config:
        orm_mode              :True



class OffViewServiceTaskMasterSchema(BaseModel):
    task_id                        : int
    work_order_master_id           : int
    work_order_number              : Optional[str] 
    work_order_date                : Optional[date] 
    work_order_details_id          : Optional[int] = None
    financial_year_id              : Optional[int] = None
    enquiry_master_id              : Optional[int] = None
    enquiry_details_id             : Optional[int] = None
    appointment_master_id          : Optional[int] = None
    visit_master_id                : Optional[int] = None
    constitution_id                : int
    trade_name                      : Optional[str] = None     
    legal_name                     : Optional[str] = None 
    service_goods_master_id        : int  
    service_goods_name             : str   
    group_id                       : int   
    group_name                     : Optional[str] = None   
    sub_group_id                   : int   
    sub_group_name                 : Optional[str] = None      
    category_id                    : int   
    category_name                  : Optional[str] = None      
    sub_category_id                : int   
    sub_category_name              : Optional[str] = None   
    customer_id                    : Optional[int] = None
    task_number                    : str
    allocated_by                   : int
    allocated_by_first_name        : Optional[str] = ""
    allocated_by_middle_name       : Optional[str] = ""
    allocated_by_last_name         : Optional[str] = ""
    allocated_on                   : datetime
    department_allocated_on        : Optional[datetime] = None
    department_allocated_to        : Optional[int] = None
    department_name                : Optional[str] = ""
    team_allocated_on              : Optional[datetime] = None
    team_allocated_to              : Optional[int] = None
    team_name                      : Optional[str] = ""
    employee_allocated_on          : Optional[datetime] = None
    employee_allocated_to          : Optional[int] = None
    employee_allocated_first_name  : Optional[str] = ""
    employee_allocated_middle_name : Optional[str] = ""
    employee_allocated_last_name   : Optional[str] = ""
    task_status_id                 : Optional[int] = None
    task_status                    : Optional[str] = ""
    task_priority_id               : Optional[int] = None
    task_priority                  : Optional[str] = ""
    remarks                        : Optional[str] = ""
    is_locked                      : str
    locked_on                      : Optional[date]
    locked_by                      : Optional[int]

    class Config:
        orm_mode = True


class ServiceTaskMasterAssign(BaseModel):  
    department_id  : int
    team_id        : Optional[int] = None                   
    employee_id    : Optional[int] = None                
    remarks        : Optional[str] = None                 

    class Config:
        orm_mode                   : True




class ServiceRequirementSchema(BaseModel):
    work_order_details_id           : int
    service_required                : Optional[str] = 'YES'
    service_required_date           : Optional[date] = None


class ServiceTaskMasterSchema(BaseModel):

    id                      : Optional[int] = None
    work_order_master_id    : Optional[int] = None
    work_order_details_id   : Optional[int] = None
    customer_id             : Optional[int] = None
    task_number             : Optional[str] = None
    allocated_by            : Optional[int] = None
    allocated_on            : Optional[datetime] = None
    department_allocated_on : Optional[datetime] = None
    department_allocated_to : Optional[int] = None
    team_allocated_on       : Optional[datetime] = None
    team_allocated_to       : Optional[int] = None
    employee_allocated_on   : Optional[datetime] = None
    employee_allocated_to   : Optional[int] = None
    task_status_id          : Optional[int] = None
    task_priority_id        : Optional[int] = None
    remarks                 : Optional[str] = None


#-----------------------------------
# class BundlePriceResponse(BaseModel):
#     constitution_id: int
#     total_service_charge: float
#     total_govt_agency_fee: float
#     total_stamp_duty: float
#     total_stamp_fee: float
#     service_goods_name: str
#     is_bundled_service: str
#     business_constitution_name: str
#     effective_from_date: Optional[str]
#     effective_to_date: Optional[str]




# class BundlePriceResponse(BaseModel):
#     constitution_id: int
#     total_service_charge: float
#     total_govt_agency_fee: float
#     total_stamp_duty: float
#     total_stamp_fee: float
#     service_goods_name: str
#     is_bundled_service: str
#     business_constitution_name: str
#     effective_from_date: Optional[str]
#     effective_to_date: Optional[str]
#     row_id: int

class BundledServiceData(BaseModel):
    # row_id: int 
    total_service_charge: float
    total_govt_agency_fee: float
    total_stamp_duty: float
    total_stamp_fee: float
    service_goods_name: Optional[str]
    is_bundled_service: Optional[str]
    constitution_id: Optional[int]
    business_constitution_name: Optional[str]
    effective_from_date: Optional[str]
    effective_to_date: Optional[str]

# Main service response model
class ServiceResponse(BaseModel):
    aggregated_data: Dict[int, BundledServiceData]


# class ServiceResponse(BaseModel):
#     data: List[BundlePriceResponse]
#     aggregated_data: List[BundlePriceResponse] 

class AppViewHsnSacMasterSchema(BaseModel):
    hsn_sac_master_id     : int
    hsn_sac_class_id      : int
    hsn_sac_class         : str
    hsn_sac_id            : int
    hsn_sac_code          : str
    hsn_sac_description   : Optional[str]
    gst_rate              : Optional[float]
    cess_rate             : Optional[float]
    additional_cess_rate  : Optional[float]
    effective_from_date   : Optional[date]
    effective_to_date     : Optional[date]
    is_deleted            : str
    tax_master_id         : int

    class Config:
        orm_mode = True



class CustomerEnquiryAppointmentDetailsSchema(BaseModel):
    id:int
    source: Optional[str]
    enquiry_master_id: Optional[str]
    appointment_master_id: Optional[str]
    legal_name: Optional[str]
    customer_id: Optional[str]
    customer_number: Optional[str]
    customer_name: Optional[str]
    mobile_number: Optional[str]
    whatsapp_number: Optional[str]
    email_id: Optional[str]
    address: Optional[str]
    pin_code: Optional[str] 
    post_office_id: Optional[int]
    post_office_name: Optional[str]
    village_id: Optional[str]  
    village_name: Optional[str]
    lsg_type_id: Optional[str] 
    lsg_type: Optional[str]
    lsg_id: Optional[str]  
    lsg_name: Optional[str]
    taluk_id: Optional[int]
    taluk_name: Optional[str]
    district_id: Optional[int]
    district_name: Optional[str]
    state_id: Optional[int]
    state_name: Optional[str]

    class Config:
        orm_mode = True