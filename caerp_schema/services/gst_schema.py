from enum import Enum
from pydantic import BaseModel, RootModel,ConfigDict
from typing import List,Dict,Optional
from typing import Dict, Any,Union
from datetime import date, datetime,time

from caerp_constants.caerp_constants import AmendmentAction

class BusinessDetailsSchema(BaseModel):

    financial_year_id                          : Optional[int] = None
    enquiry_master_id                          : Optional[int] = None
    appointment_master_id                      : Optional[int] = None
    visit_master_id                            : Optional[int] = None
    enquiry_details_id                         : Optional[int] = None
    pan_number                                 : Optional[str] = None
    pan_creation_date                          : Optional[date]= None
    state_id                                   : Optional[int] = None
    district_id                                : Optional[int] = None
    legal_name                                 : Optional[str] = None
    customer_name                              : Optional[str] = None
    email_address                              : Optional[str] = None
    mobile_number                              : Optional[str] = None
    tan_number                                 : Optional[str] = None
    passport_number                            : Optional[str] = None
    tin_number                                 : Optional[str] = None
    authorized_signatory_name_as_in_pan        : Optional[str] = None
    authorized_signatory_pan_number            : Optional[str] = None
    constitution_id                            : Optional[int] = None
 
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
    id                    : Optional[int]
    first_name            : str
    middle_name           : Optional[str]
    last_name             : Optional[str]
    fathers_first_name    : Optional[str]=None
    fathers_middle_name   : Optional[str]=None
    fathers_last_name     : Optional[str]=None
    marital_status_id     : Optional[int]
    date_of_birth         : Optional[date]
    gender_id             : int
    din_number            : Optional[str]=None
    is_citizen_of_india   : Optional[str]=None
    pan_number            : Optional[str]
    passport_number       : Optional[str]=None
    aadhaar_number        : Optional[str]
    gst_enrollment_number : Optional[str]=None


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
    # address_type   : str = "RESIDENTIAL" 
    address_type   : Optional[str]
    pin_code       : Optional[str]
    country_id     : Optional[int]
    state_id       : Optional[int]
    district_id    : Optional[int]
    city_id        : Optional[int]
    village_id     : Optional[int]
    post_office_id : Optional[int]
    taluk_id       : Optional[int]
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


class BusinessPlace(BaseModel):
    
    pin_code                  : Optional[str]
    country_id                : Optional[int]
    state_id                  : Optional[int]
    district_id               : Optional[int]
    taluk_id                  : Optional[int]
    city_id                   : Optional[int]
    post_office_id            : Optional[int]
    lsg_type_id               : Optional[int]
    lsg_id                    : Optional[int]
    village_id                : Optional[int]
    locality                  : Optional[str]
    road_street_name          : Optional[str]
    premises_building_name    : Optional[str]
    building_flat_number      : Optional[str]
    floor_number              : Optional[str]
    landmark                  : Optional[str]
    latitude                  : Optional[str]
    longitude                 : Optional[str]
    is_principal_place        : Optional[str]
    business_place_type       : Optional[str]
    nature_of_possession_id   : Optional[int]
    office_email_address      : Optional[str]
    office_mobile_number      : Optional[str]
    office_phone_std_code     : Optional[str]
    office_phone_number       : Optional[str]
    office_fax_std_code       : Optional[str]
    office_fax_number         : Optional[str]



class NatureOfBusiness(BaseModel):
    id: Optional[int]
    business_activity_id: Optional[int]

class BusinessData(BaseModel):
    business_place                  : List[BusinessPlace]
    business_activity_type_id       : int
    business_activity_master_id     : int
    nature_of_business              : List[NatureOfBusiness]


class CustomerGoodsCommoditiesSupplyDetailsSchema(BaseModel):
    id                 :int
    hsn_sac_class_id   :int
    hsn_sac_code_id    :int


class CustomerGstStateSpecificInformationSchema(BaseModel):

    professional_tax_employee_code               :str
    professional_tax_registration_certificate    :str
    state_excise_licence_number                  :str
    excise_licence_holder_name                   :str


#-jurisdition

class RangeDetailsSchema(BaseModel):
    address              : str
    phone                : str
    range_id             : int
    range_name           : str
    range_code           : str
    division_id          : int
    division_name        : str
    division_code        : str
    commissionerate_id   : int
    commissionerate_name : str
    commissionerate_code : str
    zone_id              : int
    zone_name            : str
    zone_code            : str
    state_id             : int
    state_name           : str
    district_id          : int
    district_name        : str
    country_id           :int
    country_name_english :str
    class Config:
        orm_mode = True

# class CustomerDuplicateSchema(BaseModel):
   
#     customer_number: Optional[str]
#     legal_name: Optional[str]
#     customer_name: Optional[str]
#     pan_number: Optional[str]
#     pan_creation_date: Optional[date]
#     tan_number: Optional[str]
#     passport_number: Optional[str]
#     tin_number: Optional[str]
#     authorized_signatory_name_as_in_pan: Optional[str]
#     authorized_signatory_pan_number: Optional[str]
#     email_address: Optional[str]
#     mobile_number: Optional[str]
#     constitution_id: Optional[int]
#     state_id: Optional[int]
#     district_id: Optional[int]
#     is_mother_customer: str
#     is_amendment: str
#     amendment_date: Optional[date]
#     amendment_reason: Optional[str]
#     amendment_status: str
#     amendment_history: Optional[str]
#     effective_from_date: Optional[date]
#     effective_to_date: Optional[date]
#     has_authorized_signatory: str
#     has_authorized_representative: str
#     created_by: Optional[int]
#     created_on: Optional[datetime]
#     modified_by: Optional[int]
#     modified_on: Optional[datetime]
#     is_deleted: str
#     deleted_by: Optional[int]
#     deleted_on: Optional[datetime]
    
#     model_config = ConfigDict(from_attributes=True)

class CustomerDuplicateSchema(BaseModel):
    customer_number                         : Optional[str]
    legal_name                              : Optional[str]
    customer_name                           :Optional[str]
    pan_number                              : Optional[str]
    pan_creation_date                       : Optional[date]
    tan_number                              : Optional[str]
    passport_number                         : Optional[str]
    tin_number                              : Optional[str]
    authorized_signatory_name_as_in_pan     : Optional[str]
    authorized_signatory_pan_number         : Optional[str]
    email_address                           : Optional[str]
    mobile_number                           : Optional[str]
    constitution_id                         : Optional[int]
    state_id                                : Optional[int]
    district_id                             : Optional[int]
    is_mother_customer                      : str
    is_amendment                            : str
    amendment_date                          : Optional[date]
    amendment_reason                        : Optional[str]
    amendment_status                        : Optional[str] 
    amendment_history                       : Optional[str]
    effective_from_date                     : Optional[date]
    effective_to_date                       : Optional[date]
    has_authorized_signatory                : str
    has_authorized_representative           : str

    model_config = ConfigDict(from_attributes=True)


class CustomerDuplicateSchemaForGet(BaseModel):
    id                                      :int
    customer_id                             :int
    customer_number                         : Optional[str]
    legal_name                              : Optional[str]
    customer_name                           : Optional[str]
    pan_number                              : Optional[str]
    pan_creation_date                       : Optional[date]
    tan_number                              : Optional[str]
    passport_number                         : Optional[str]
    tin_number                              : Optional[str]
    authorized_signatory_name_as_in_pan     : Optional[str]
    authorized_signatory_pan_number         : Optional[str]
    email_address                           : Optional[str]
    mobile_number                           : Optional[str]
    constitution_id                         : Optional[int]
    business_constitution_name              : Optional[str]
    state_id                                : Optional[int]
    state_name                              : Optional[str]           
    district_id                             : Optional[int]
    district_name                           : Optional[str]
    is_mother_customer                      : str
    is_amendment                            :str
    amendment_date                          : Optional[date]
    amendment_reason                        : Optional[str]
    amendment_status                        : str
    amendment_history                       : Optional[str]
    effective_from_date                     : Optional[date]
    effective_to_date                       : Optional[date]
    has_authorized_signatory                : str
    has_authorized_representative           : str
    amendment_request_date                  : Optional[date]  
    amendment_remarks                       : Optional[str]  
    created_by                              : Optional[int]
    created_on                              : Optional[datetime]
    modified_by                             : Optional[int]
    modified_on                             : Optional[datetime]
    is_deleted                              : str
    deleted_by                              : Optional[int]
    deleted_on                              : Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)



class CustomerGstStateSpecificInformationSchemaGet(BaseModel):
    id                                           :int
    professional_tax_employee_code               :str
    professional_tax_registration_certificate    :str
    state_excise_licence_number                  :str
    excise_licence_holder_name                   :str


class CustomerAmendmentSchema(BaseModel):
   
    old_value               : str
    new_value               : str
    amendment_remarks       : str
    amendment_request_date  : date
    # amendment_effective_date: Optional[date] = None

    class Config:
        orm_mode = True


class AdditionalTradeNameAmendment(BaseModel):
    
    new_trade_name          : str
    request_date            : datetime
    remarks                 : str

#----------------------------------------------------------


class AmmendPersonalInformationSchema(BaseModel):
    id:Optional[int]
    first_name: str
    middle_name: Optional[str]
    last_name: Optional[str]
    fathers_first_name: Optional[str] = None
    fathers_middle_name: Optional[str] = None
    fathers_last_name: Optional[str] = None
    marital_status_id: Optional[int]
    date_of_birth: Optional[date]
    gender_id: int
    din_number: Optional[str] = None
    is_citizen_of_india: Optional[str] = None
    pan_number: Optional[str]
    passport_number: Optional[str] = None
    aadhaar_number: Optional[str]
    designation_id:Optional[int]

class AmmendContactDetailsSchema(BaseModel):
    id:Optional[int]
    mobile_number: Optional[str]
    email_address: Optional[str]
    telephone_number_with_std_code: Optional[str]

class AmmendAddressSchema(BaseModel):
    id:Optional[int]
    address_type: Optional[str]
    pin_code: Optional[str]
    country_id: Optional[int]
    state_id: Optional[int]
    district_id: Optional[int]
    city_id: Optional[int]
    village_id: Optional[int]
    post_office_id: Optional[int]
    taluk_id: Optional[int]
    lsg_type_id: Optional[int]
    lsg_id: Optional[int]
    locality: Optional[str]
    road_street_name: Optional[str]
    premises_building_name: Optional[str]
    building_flat_number: Optional[str]
    floor_number: Optional[str]
    landmark: Optional[str]

class AmmendStakeHolderMasterSchema(BaseModel):
    personal_information: AmmendPersonalInformationSchema
    contact_details: List[AmmendContactDetailsSchema]
    address: List[AmmendAddressSchema]

    class Config:
        orm_mode = True



class AmendmentDetailsSchema(BaseModel):
    
    reason: str
    date: datetime


class CustomerBusinessPlaceAmendmentSchema(BaseModel):
    pin_code: str
    country_id: int
    state_id: int
    district_id: int
    taluk_id:int
    city_id: int
    post_office_id:int
    lsg_type_id:int
    lsg_id:int
    village_id:int
    locality: Optional[str] = None
    road_street_name: Optional[str] = None
    premises_building_name: str
    building_flat_number: str
    floor_number: Optional[str] = None
    landmark: Optional[str] = None
    latitude: str
    longitude: str
    office_email_address: Optional[str] = None
    office_mobile_number: Optional[str] = None
    office_phone_std_code: Optional[str] = None
    office_phone_number: Optional[str] = None
    office_fax_std_code: Optional[str] = None
    office_fax_number: Optional[str] = None

    amendment_date: Optional[date] = None  # New field added
    amendment_reason: Optional[str] = None  # New field added

    class Config:
        orm_mode = True
        from_attributes = True

