from pydantic import BaseModel
from typing import List,Dict,Optional
from typing import Dict, Any,Union
from datetime import date
from datetime import date, datetime



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
     

class ServiceOwnerBase(BaseModel):
    id: int
    service_owner: Optional[str]
     

    
class ServiceOwnerDisplay(BaseModel):

    service_owner: Optional[str]
    


class ServiceGenerationModeBase(BaseModel):
    id : int
    mode : Optional[str]
   

class ServiceGenerationModeDisplay(BaseModel):
   
    mode : Optional[str]

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
    
