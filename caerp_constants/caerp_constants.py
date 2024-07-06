from enum import Enum

class DeletedStatus(str, Enum):
    ALL = "all"
    DELETED = "yes"
    NOT_DELETED = "no"
    
class ActiveStatus(str,Enum):
    ALL         = 'all'
    ACTIVE      = 'yes'
    NOT_ACTIVE  ='no'

class ParameterConstant(str,Enum):
    STATE       ='state_id'
    TALUK       ='taluk_id'
    DISTRICT    = 'district_id'
    COUNTRY     = 'country_id'
    POST_OFFICE = 'post_office_id'
    TYPE        = 'customer_type_id' 
    
class BooleanFlag(str, Enum):
    yes         = "yes"
    no          = "no"

class VerifiedStatus(str, Enum):
    VERIFIED      = 'yes'
    NOT_VERIFIED  = 'no'

 
    
class ActionType(str, Enum):
    DELETE      = 'DELETE'
    UNDELETE    = 'UNDELETE'

class BookingStatus(str, Enum):
    ALL         ='all',
    BOOKED      ="BOOKED",
    AVAILABLE   ="AVAILABLE"
    
class CRUD(str, Enum):
    CREATE      = "create"
    READ        = "read"
    UPDATE      = "update"
    DELETE      = "delete"
 
    
class EmployeeDetails(str, Enum):
    ALL 		        ="ALL"
    EMPLOYEE_MASTER     = "EMPLOYEE_MASTER"
    PRESENT_ADDRESS     = "PRESENT_ADDRESS"
    PERMANENT_ADDRESS   = "PERMANENT_ADDRESS"
    CONTACT_DETAILS     = "CONTACT_DETAILS"
    BANK_DETAILS        = "BANK_DETAILS"


# class AppointmentStatus(str,Enum):
#     NEW = "NEW"
#     CANCELED = "CANCELED"
#     RESCHEDULED = "RESCHEDULED"
#     CLOSED = "CLOSED"

    
class SearchCriteria(str, Enum):
    mobile_number = "mobile_number"
    email_id = "email_id"
    ALL= "ALL"



class EmployeeActionType(str, Enum):
    INSERT_ONLY = 'INSERT_ONLY'    
    UPDATE_ONLY = 'UPDATE_ONLY'
    UPDATE_AND_INSERT = 'UPDATE_AND_INSERT'


class RecordActionType(str, Enum):
    INSERT_ONLY = 'INSERT_ONLY'    
    UPDATE_ONLY = 'UPDATE_ONLY'
    UPDATE_AND_INSERT = 'UPDATE_AND_INSERT'  
    DELETE      = 'DELETE'
    UNDELETE ='UNDELETE'


class ApprovedStatus(str, Enum):
    ALL = 'ALL'
    APPROVED      = 'yes'
    NOT_APPROVED  = 'no'    
    