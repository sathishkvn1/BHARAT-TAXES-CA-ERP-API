from enum import Enum
from pydantic import BaseModel, validator
from typing import List,Optional, Union,Dict
from datetime import date, datetime
from caerp_constants.caerp_constants import BooleanFlag


class EmployeeMasterSchema(BaseModel):
    employee_number: str
    first_name: str
    middle_name: str
    last_name: str
    gender_id: int
    date_of_birth: date
    nationality_id: int
    marital_status_id: int
    designation_id: int
    is_consultant: str
    aadhaar_number: Optional[str] = None
    passport_number: Optional[str] = None
    pan_number: Optional[str] = None
    driving_licence_number: Optional[str] = None
    other_id_doc: str
    present_house_or_flat_name: str
    present_house_flat_or_door_number: Optional[str] = None
    present_road_name: Optional[str] = None
    present_street_name: Optional[str] = None
    present_land_mark: Optional[str] = None
    present_pin_code: Optional[str] = None
    present_post_office_id: int
    present_city_id: int
    present_taluk_id: int
    present_district_id: int
    present_state_id: int
    present_country_id: int
    permanent_house_or_flat_name: str
    permanent_house_flat_or_door_number: Optional[str] = None
    permanent_road_name: Optional[str] = None
    permanent_street_name: Optional[str] = None
    permanent_land_mark: Optional[str] = None
    permanent_pin_code: Optional[str] = None
    permanent_post_office_id: int
    permanent_city_id: int
    permanent_taluk_id: int
    permanent_district_id: int
    permanent_state_id: int
    permanent_country_id: int
    home_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    work_phone: Optional[str] = None
    work_email: Optional[str] = None
    private_email: Optional[str] = None
    account_number: Optional[str] = None
    bank_name:  Optional[str] = None
    bank_branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    created_by: int
    created_on: datetime
    # modified_by: Optional[int] = None
    # modified_on: Optional[datetime] = None
    # is_deleted: str = 'no'
    # deleted_by: Optional[int] = None
    # deleted_on: Optional[datetime] = None
    # is_verified: str = 'no'
    # verified_by: Optional[int] = None
    # verified_on: Optional[datetime] = None
    # is_approved: str = 'no'
    # approved_by: Optional[int] = None
    # approved_on: Optional[datetime] = None

               
class EmployeeMasterSchemaForGet(BaseModel):
    employee_id:int
    employee_number: str
    first_name: str
    middle_name: str
    last_name: str
    gender_id: int
    gender: str
    date_of_birth: date
    nationality_id: int
    nationality_name: str
    marital_status_id: int
    marital_status: str
    designation_id: int
    designation: str
    is_consultant: str
    aadhaar_number: Optional[str] = None
    passport_number: Optional[str] = None
    pan_number: Optional[str] = None
    driving_licence_number: Optional[str] = None
    other_id_doc: str
    present_house_or_flat_name: str
    present_house_flat_or_door_number: Optional[str] = None
    present_road_name: Optional[str] = None
    present_street_name: Optional[str] = None
    present_land_mark: Optional[str] = None
    present_pin_code: Optional[str] = None
    present_post_office_id: int
    present_post_office_name: str
    present_city_id: int
    present_city_name: str
    present_taluk_id: int
    present_taluk_name: str
    present_district_id: int
    present_district_name: str
    present_state_id: int
    present_state_name: str
    present_country_id: int
    present_country_name: str
    permanent_house_or_flat_name: str
    permanent_house_flat_or_door_number: Optional[str] = None
    permanent_road_name: Optional[str] = None
    permanent_street_name: Optional[str] = None
    permanent_land_mark: Optional[str] = None
    permanent_pin_code: Optional[str] = None
    permanent_post_office_id: int
    permanent_post_office_name: str
    permanent_city_id: int
    permanent_city_name: str
    permanent_taluk_id: int
    permanent_taluk_name: str
    permanent_district_id: int
    permanent_district_name: str
    permanent_state_id: int
    permanent_state_name: str
    permanent_country_id: int
    permanent_country_name: str
    home_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    work_phone: Optional[str] = None
    work_email: Optional[str] = None
    private_email: Optional[str] = None
    account_number: Optional[str] = None
    bank_name:  Optional[str] = None
    bank_branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    created_by: int
    created_on: datetime
    modified_by: Optional[int] = None
    modified_on: Optional[datetime] = None
    is_deleted: str = 'no'
    deleted_by: Optional[int] = None
    deleted_on: Optional[datetime] = None
    is_verified: str = 'no'
    verified_by: Optional[int] = None
    verified_on: Optional[datetime] = None
    is_approved: str = 'no'
    approved_by: Optional[int] = None
    approved_on: Optional[datetime] = None
    
    class config():
        orm_mode=True

class EmployeePersonalDetailSchema(BaseModel):
    employee_number: str
    first_name: str
    middle_name: str
    last_name: str
    gender_id: int
    date_of_birth: date
    nationality_id: int
    marital_status_id: int
    designation_id: int
    is_consultant: str
    aadhaar_number: Optional[str] = None
    passport_number: Optional[str] = None
    pan_number: Optional[str] = None
    driving_licence_number: Optional[str] = None
    other_id_doc: str

    class config():
        orm_mode=True

class EmployeeAddressDetailSchema(BaseModel):
    present_house_or_flat_name: str
    present_house_flat_or_door_number: Optional[str] = None
    present_road_name: Optional[str] = None
    present_street_name: Optional[str] = None
    present_land_mark: Optional[str] = None
    present_pin_code: Optional[str] = None
    present_post_office_id: int
    present_city_id: int
    present_taluk_id: int
    present_district_id: int
    present_state_id: int
    present_country_id: int
    permanent_house_or_flat_name: str
    permanent_house_flat_or_door_number: Optional[str] = None
    permanent_road_name: Optional[str] = None
    permanent_street_name: Optional[str] = None
    permanent_land_mark: Optional[str] = None
    permanent_pin_code: Optional[str] = None
    permanent_post_office_id: int
    permanent_city_id: int
    permanent_taluk_id: int
    permanent_district_id: int
    permanent_state_id: int
    permanent_country_id: int     

    class config():
        orm_mode=True

class EmployeeContactDetailSchema(BaseModel):
    home_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    work_phone: Optional[str] = None
    work_email: Optional[str] = None
    private_email: Optional[str] = None
  
    class config():
        orm_mode=True

class EmployeeBankAccountDetailSchema(BaseModel):
    account_number: Optional[str] = None
    bank_name:  Optional[str] = None
    bank_branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None

    class config():
        orm_mode=True        


    