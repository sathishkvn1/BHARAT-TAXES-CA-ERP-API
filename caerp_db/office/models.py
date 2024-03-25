
from sqlalchemy import Column, Integer, String,BigInteger,Date,Float,Enum
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column

class Document_Master(caerp_base):
    __tablename__ = 'off_document_master'
    
    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    document_name = Column(String(100),nullable=False)
    document_code = Column(String(100),nullable=True)
    is_deleted    = Column(Enum('yes', 'no'), default='no', nullable=False)


class ServiceProvider(caerp_base):
    __tablename__ = 'app_service_provider'

    id               = Column(Integer, primary_key=True, autoincrement=True)
    service_provider = Column(String(500), nullable=False)
    place            = Column(String(500), nullable=True)
    address_line_1   = Column(String(500), nullable=True)
    email_id         = Column(String(55), nullable=True)
    mobile_number    = Column(String(500), nullable=True)
    is_deleted       = Column(Enum('yes', 'no'), default='no', nullable=False)


class ServiceDepartments(caerp_base):
    __tablename__ = 'app_service_departments'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    service_department_name = Column(String(500), nullable=False)
    department_description  = Column(String(500), nullable=True)
    address_line_1          = Column(String(500), nullable=True)
    address_line_2          = Column(String(500), nullable=True)
    email_id                = Column(String(500), nullable=True)
    mobile_number           = Column(String(500), nullable=True)
    is_deleted              = Column(Enum('yes', 'no'), default='no', nullable=False)
     


class AppBusinessActivityType(caerp_base):
    __tablename__ = 'app_business_activity_type'

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    business_activity_type = Column(String(100))
    is_deleted             = Column(Enum('yes', 'no'), nullable=False, default='no')

class AppBusinessActivityMaster(caerp_base):
    __tablename__ = 'app_business_activity_master'

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    business_activity_type_id= Column(Integer,nullable=False)
    business_activity        = Column(String(250))
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')

# class AppEducationalQualificationsMaster(caerp_base):
#     __tablename__ = 'app_educational_qualifications'

#     id                       = Column(Integer, primary_key=True, autoincrement=True)
#     qualification            = Column(String(100),nullable=False)
#     is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')


class EnquirerType(caerp_base):
    __tablename__ = 'off_enquirer_type'

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    person_type              = Column(String(100),nullable=True)
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')

class EnquirerStatus(caerp_base):
    __tablename__ = 'off_enquiry_status'

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    status                   = Column(String(100),nullable=True)
    is_deleted               = Column(Enum('yes', 'no'), nullable=False, default='no')


class ServiceProcessingStatus(caerp_base):
    __tablename__ = 'off_service_processing_status'

    id                         = Column(Integer, primary_key=True, autoincrement=True)
    service_processing_status  = Column(String(500),nullable=False)
    is_deleted                 = Column(Enum('yes', 'no'), nullable=False, default='no')


#-----------------------------------------------------------------------------------------------------
class AppServiceFrequency(caerp_base):
    __tablename__ = 'app_service_frequency'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_frequency = Column(String(500))
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
   

    
class AppServiceOwner(caerp_base):
    __tablename__ = 'app_service_owner'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_owner = Column(String(100))
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')



class AppServiceGenerationMode(caerp_base):
    __tablename__ = 'app_service_generation_mode'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mode = Column(String(250))
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')



class AppStockKeepingUnitCode(caerp_base):
    __tablename__ = 'app_stock_keeping_unit_code'

    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_code = Column(String(250))
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    

class AppHsnSacClasses(caerp_base):
    __tablename__ = 'app_hsn_sac_classes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class = Column(String(100),nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class AppHsnSacMaster(caerp_base):
    __tablename__ = 'app_hsn_sac_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=True)
    hsn_sac_description = Column(String(1000), nullable=True)
    sku_code = Column(String(20), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
