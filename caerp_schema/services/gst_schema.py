from enum import Enum
from pydantic import BaseModel, RootModel
from typing import List,Dict,Optional
from typing import Dict, Any,Union
import re
from datetime import date, datetime,time


class BusinessDetailsSchema(BaseModel):
    pan_number                                 : Optional[str]
    pan_creation_date                          : Optional[datetime]
    state_id                                   : Optional[int] 
    district_id                                : Optional[int] 
    legal_name                                 : Optional[str]
    email_address                              : Optional[str]
    mobile_number                              : Optional[str] 
    tan_number                                 : Optional[str] 
    passport_number                            : Optional[str]
    tin_number                                 : Optional[str] 
    authorized_signatory_name_as_in_pan        : Optional[str] 
    authorized_signatory_pan_number            : Optional[str]


#--------------

class TradeNameSchema(BaseModel):
    id        : Optional[int]
    trade_name: str

class CasualTaxablePersonSchema(BaseModel):
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

class CompositionOptionSchema(BaseModel):
    id                                       : Optional[int]
    is_applying_as_composition_taxable_person: str
    option_1                                 : Optional[str]=None
    option_2                                 : Optional[str]=None
    option_3                                 : Optional[str]=None

class ReasonForGSTSchema(BaseModel):
    id                                   : Optional[int]
    reason_to_obtain_gst_registration_id : int
    commencement_of_business_date        : date
    liability_to_register_arises_date    : Optional[date]

class RegistrationSchema(BaseModel):
    id                  : Optional[int]
    registration_type_id: str
    registration_number : str
    registration_date   : date


class AuthorizationSchema(BaseModel):
    constitution_id                : Optional[int]
    has_authorized_signatory       : str
    has_authorized_representative  : str
    is_mother_customer             : str

class CustomerRequestSchema(BaseModel):
    additional_trade_name          : List[TradeNameSchema]
    casual_taxable_person          : CasualTaxablePersonSchema
    option_for_composition         : CompositionOptionSchema
    reason_to_obtain_registration  : ReasonForGSTSchema
    existing_registrations         : List[RegistrationSchema]
    authorization                  : AuthorizationSchema  

#-get

class TradeNameSchema(BaseModel):
    id        : int
    trade_name: str

class CasualTaxablePersonSchema(BaseModel):
    id                                  : int
    is_applying_as_casual_taxable_person: str
    estimated_igst_turnover             : float
    estimated_net_igst_liability        : float
    estimated_cgst_turnover             : float
    estimated_net_cgst_liability        : float
    estimated_sgst_turnover             : float
    estimated_net_sgst_liability        : float
    estimated_cess_turnover             : float
    estimated_net_cess_liability        : float

class OptionForCompositionSchema(BaseModel):
    id                                       : int
    is_applying_as_composition_taxable_person: str
    option_1                                 : Optional[str]
    option_2                                 : Optional[str]
    option_3                                 : Optional[str]

class ReasonToObtainRegistrationSchema(BaseModel):
    reason_to_obtain_gst_registration_id : int
    reason                               : str
    commencement_of_business_date        : date
    liability_to_register_arises_date    : date

class ExistingRegistrationSchema(BaseModel):
    registration_type_id                 : int
    registration_type                    : str
    registration_number                  : str
    registration_date                    : date

class CustomerBusinessDetailsSchema(BaseModel):
    pan_number                               : str
    pan_creation_date                        : date
    state_id                                 : int
    state_name                               : str
    district_id                              : int
    district_name                            : str
    legal_name                               : str
    email_address                            : str
    mobile_number                            : str
    tan_number                               : Optional[str]
    passport_number                          : Optional[str]
    tin_number                               : Optional[str]
    authorised_signatory_name_as_in_pan      : str
    authorised_signatory_pan_number          : str
    constitution_id                          : int
    has_authorized_signatory                 : str
    has_authorized_representative            : str
    is_mother_customer                       : str

class CustomerOtherDetailsSchema(BaseModel):
    additional_trade_name                    : List[TradeNameSchema]
    casual_taxable_person                    : CasualTaxablePersonSchema
    option_for_composition                   : OptionForCompositionSchema
    reason_to_obtain_registration            : ReasonToObtainRegistrationSchema
    existing_registration                    : List[ExistingRegistrationSchema]
