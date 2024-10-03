from enum import Enum
from pydantic import BaseModel, RootModel
from typing import List,Dict,Optional
from typing import Dict, Any,Union
from datetime import date, datetime,time


class BusinessDetailsSchema(BaseModel):
    pan_number                                 : Optional[str]
    pan_creation_date                          : Optional[date]
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
    id                   : Optional[int]
    additional_trade_name: str

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
    registration_type_id: int
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




#----------stakeholder


class PersonalInformationSchema(BaseModel):
    id                : Optional[int]
    first_name        : str
    middle_name       : Optional[str]
    last_name         : Optional[str]
    fathers_first_name: Optional[str]
    marital_status_id : Optional[int]
    date_of_birth     : Optional[date]
    gender_id         : int
    din_number        : Optional[str]
    is_citizen_of_india: Optional[str]
    pan_number         : Optional[str]
    passport_number    : Optional[str]
    aadhaar_number     : Optional[str]


class ContactDetailsSchema(BaseModel):
    id                               : Optional[int]
    mobile_number                    : Optional[str]
    email_address                    : Optional[str]
    telephone_number_with_std_code   : Optional[str]


class IdentityInformationSchema(BaseModel):
    id            : Optional[int]
    designation_id: Optional[int]


class AddressSchema(BaseModel):
    id             : Optional[int]
    address_type   : str = "RESIDENTIAL" 
    # address_type   : Optional[str]
    pin_code       : Optional[str]
    country_id     : Optional[int]
    state_id       :  Optional[int]
    district_id    : Optional[int]
    city_id        : Optional[int]
    village_id     : Optional[int]
    post_office_id : Optional[int]
    lsg_type_id    : Optional[int]
    lsg_id         : Optional[int]
    locality       : Optional[str]
    road_street_name: Optional[str]
    premises_building_name: Optional[str]
    building_flat_number  : Optional[str]
    floor_number          : Optional[str]
    landmark              : Optional[str]


class StakeHolderMasterSchema(BaseModel):
    personal_information: PersonalInformationSchema
    contact_details     : List[ContactDetailsSchema]
    identity_information: List[IdentityInformationSchema]
    address             : List[AddressSchema]