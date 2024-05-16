from enum import Enum
from pydantic import BaseModel, validator
from typing import List,Optional, Union,Dict
from datetime import date, datetime
from caerp_constants.caerp_constants import BooleanFlag


class EmployeeMasterSchema(BaseModel):
    employee_id: int
    employee_number: str
    first_name: str
    middle_name: str
    last_name: str
    gender_id: int
    date_of_birth: date
    nationality_id: int
    marital_status_id: int
    designation_id: int
    is_consultant: Optional[str] = None
    effective_from_date: date
    effective_to_date: Optional[date]

    class config():
        orm_mode=True
         
# class EmployeeMasterUpdate(BaseModel):
#     employee_number: str
#     first_name: str
#     middle_name: str
#     last_name: str
#     gender_id: int
#     date_of_birth: date
#     nationality_id: int
#     marital_status_id: int
#     designation_id: int
#     is_consultant: str
#     effective_from_date: date
#     effective_to_date: Optional[date]    

                
class EmployeeMasterSchemaForGet(BaseModel):
    #employee_id:int
    employee_number: str
    first_name: str
    middle_name: str
    last_name: str
    gender_id: int
    gender: str
    date_of_birth: date
    nationality_id: int
    marital_status_id: int
    designation_id: int
    is_consultant: Optional[str]
    effective_from_date: date
    effective_to_date: Optional[date]
    created_by: int
    created_on: datetime
    modified_by: Optional[int] = None
    modified_on: Optional[datetime] = None
    is_deleted: str = 'no'
    deleted_by: Optional[int] = None
    deleted_on: Optional[datetime] = None

    class config():
        orm_mode=True


class EmployeePresentAddressSchema(BaseModel):
    employee_id: int
    present_house_or_flat_name: Optional[str] = None
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
    effective_from_date: date
    effective_to_date: Optional[date]

    class config():
        orm_mode=True



class EmployeePermanentAddressSchema(BaseModel):   
    employee_id: int    
    permanent_house_or_flat_name: Optional[str] = None
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
    effective_from_date: date
    effective_to_date: Optional[date]

    class config():
        orm_mode=True



class EmployeeContactDetailSchema(BaseModel):
    employee_id: int
    personal_mobile_number: Optional[str] = None
    personal_whatsapp_number: Optional[str] = None
    personal_email_id: Optional[str] = None
    official_mobile_number: Optional[str] = None
    official_whatsapp_number: Optional[str] = None
    official_email_id: Optional[str] = None
    effective_from_date: date
    effective_to_date: Optional[date]
    

    class config():
        orm_mode=True

class EmployeeBankAccountDetailSchema(BaseModel):
    employee_id: int
    bank_account_number: Optional[str] = None
    bank_name:  Optional[str] = None
    bank_branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    effective_from_date: date
    effective_to_date: Optional[date]

    class config():
        orm_mode=True        

class EmployeeDetails(BaseModel):
    employee_master: Optional[EmployeeMasterSchema] = None
    present_address: Optional[EmployeePresentAddressSchema] = None
    permanent_address: Optional[EmployeePermanentAddressSchema] = None
    contact_details: Optional[EmployeeContactDetailSchema] = None
    bank_details: Optional[EmployeeBankAccountDetailSchema] = None
