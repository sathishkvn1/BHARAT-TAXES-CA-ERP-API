from pydantic import BaseModel, RootModel,ConfigDict
from typing import List,Dict,Optional
from typing import Dict, Any,Union
from datetime import date, datetime,time



class MotherCustomerBusinessDetailsSchema(BaseModel):

    id                                         : int
    legal_name                                 : Optional[str] 
    customer_name                              : Optional[str] 
    state_id                                   : Optional[int] 
    district_id                                : Optional[int] 
    email_address                              : Optional[str] 
    mobile_number                              : Optional[str] 
    pan_number                                 : Optional[str] 
    pan_creation_date                          : Optional[date]
 
#--------------

class MotherCustomerTradeNameSchema(BaseModel):
    id                   : Optional[int]
    additional_trade_name: str

class MotherCustomerCasualTaxablePersonSchema(BaseModel):
    id                                  : Optional[int]
    is_applying_as_casual_taxable_person: str
    gst_registration_required_from_date : Optional[date]=None
    gst_registration_required_to_date   : Optional[date]=None
    estimated_igst_turnover             : Optional[float]=None
    estimated_net_igst_liability        : Optional[float]=None
    estimated_cgst_turnover             : Optional[float]=None
    estimated_net_cgst_liability        : Optional[float]=None
    estimated_sgst_turnover             : Optional[float]=None
    estimated_net_sgst_liability        : Optional[float]=None
    estimated_cess_turnover             : Optional[float]=None
    estimated_net_cess_liability        : Optional[float]=None

class MotherCustomerCompositionOptionSchema(BaseModel):
    id                                       : Optional[int]
    is_applying_as_composition_taxable_person: str
    option_1                                 : Optional[str]=None
    option_2                                 : Optional[str]=None
    option_3                                 : Optional[str]=None

class MotherCustomerReasonForGSTSchema(BaseModel):
    id                                   : Optional[int]
    commencement_of_business_date        : date
    
class MotherCustomerRegistrationSchema(BaseModel):
    id                  : Optional[int]
    registration_type_id: int
    registration_number : str
    registration_date   : date


class MotherCustomerRequestSchema(BaseModel):
    mother_customer_business_details                  : MotherCustomerBusinessDetailsSchema
    mother_customeradditional_trade_name              : List[MotherCustomerTradeNameSchema]
    mother_customercasual_taxable_person              : MotherCustomerCasualTaxablePersonSchema
    mother_customeroption_for_composition             : MotherCustomerCompositionOptionSchema
    mother_customerreason_to_obtain_registration      : MotherCustomerReasonForGSTSchema
    mother_customerexisting_registrations             : List[MotherCustomerRegistrationSchema]
    

