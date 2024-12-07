
from sqlalchemy import Column, Integer, String,BigInteger,Date,Float,Enum,Time, func
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column ,DateTime




class OffAppointmentMaster(caerp_base):
    __tablename__  =  "off_appointment_master"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    full_name 	     = Column(String(200), nullable=False)
    customer_number  =Column(String(100), nullable=True)
    mobile_number    = Column(String(20), nullable=True)
    whatsapp_number  =Column(String(20), nullable=True)
    email_id         = Column(String(50), nullable=True)
    gender_id        = Column(Integer, nullable=True)
    locality         = Column(String(50), nullable=True)
    pin_code         = Column(String(50), nullable=True)
    post_office_id   = Column(Integer, nullable=True)
    taluk_id         = Column(Integer, nullable=True)
    district_id      = Column(Integer, nullable=True)
    state_id         = Column(Integer, nullable=True)
    created_by       = Column(Integer, nullable=True)
    created_on       = Column(Date, nullable=True)
    modified_by      = Column(Integer, nullable=True)
    modified_on      = Column(Date, nullable=True)
    is_deleted       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by       = Column(Integer, nullable=True)
    deleted_on       = Column(Date, nullable=True)
    is_locked        = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on        = Column(Date, nullable=True)
    locked_by        = Column(Integer, nullable=True)



class OffAppointmentVisitMaster(caerp_base):
    __tablename__ = 'off_appointment_visit_master'

    id                         = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id          = Column(Integer, nullable=True)
    appointment_number         = Column(String(50), nullable=True)
    voucher_number             = Column(String(50), nullable=True)
    appointment_master_id      = Column(Integer, nullable=False)
    appointment_date           = Column(Date, nullable=True)
    appointment_time_from      = Column(String(50), nullable=True) 
    appointment_time_to        = Column(String(50), nullable=True)
    source_of_enquiry_id       = Column(Integer, nullable=False)
    appointment_status_id      = Column(Integer, nullable=False)
    consultant_id              = Column(Integer, nullable=False)
    consultation_mode_id       = Column(Integer, nullable=False)
    consultation_tool_id       = Column(Integer, nullable=False)
    gross_amount               = Column(Float, nullable=False)
    discount_percentage        = Column(Float, nullable=False)
    special_discount_percentage= Column(Float, nullable=False)
    special_discount_amount    = Column(Float, nullable=False)
    net_amount                 = Column(Float, nullable=False)
    igst_amount                = Column(Float, nullable=False)
    sgst_amount                = Column(Float, nullable=False)
    cgst_amount                = Column(Float, nullable=False)
    bill_amount                = Column(Float, nullable=False)
    remarks                    = Column(String(1000), nullable=True)
    created_by                 = Column(Integer, nullable=True)
    created_on                 = Column(Date, nullable=True)
    modified_by                = Column(Integer, nullable=True)
    modified_on                = Column(Date, nullable=True)
    is_deleted                 = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                 = Column(Integer, nullable=True)
    deleted_on                 = Column(Date, nullable=True)
    is_locked        = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on        = Column(Date, nullable=True)
    locked_by        = Column(Integer, nullable=True)





class OffAppointmentVisitMasterView(caerp_base):
    __tablename__ = 'off_view_appointment_master'

    appointment_master_id            = Column(Integer,  primary_key=True,nullable=False)
    full_name 	                     = Column(String(200), nullable=False)
    gender_id                        = Column(Integer, nullable=False)
    gender                           = Column(String(50), nullable=False)
    appointment_number               = Column(String(50), nullable=True)
    customer_number                  = Column(String(100), nullable=True)
    mobile_number                    = Column(String(20), nullable=True)
    whatsapp_number                  = Column(String(20), nullable=True)
    email_id                         = Column(String(50), nullable=True)
    locality                         = Column(String(50), nullable=True)
    pin_code                         = Column(String(50), nullable=True)
    post_office_id                   = Column(Integer, nullable=True)
    post_office_name                 = Column(String(255), nullable=True)
    contact_number                   = Column(String(50), nullable=True)
    taluk_id                         = Column(Integer, nullable=True)
    taluk_name                       = Column(String(255), nullable=True)
    district_id                      = Column(Integer, nullable=True)
    district_name                    = Column(String(255), nullable=True)
    state_id                         = Column(Integer, nullable=True)
    state_name                       = Column(String(255), nullable=True)
    state_code                       = Column(Integer, nullable=True)
    gst_registration_name            = Column(String(255), nullable=True)
    created_by                       = Column(Integer, nullable=True)
    created_on                       = Column(Date, nullable=True)
    modified_by                      = Column(Integer, nullable=True)
    modified_on                      = Column(Date, nullable=True)
    is_deleted                       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                       = Column(Integer, nullable=True)
    deleted_on                       = Column(Date, nullable=True)
    is_locked                        = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on                        = Column(Date, nullable=True)
    locked_by                        = Column(Integer, nullable=True)
    visit_master_id                  = Column(Integer, nullable=True)
    financial_year_id                = Column(Integer, nullable=True)
    financial_year                   = Column(String(50), nullable=True)
    voucher_number                   = Column(String(50), nullable=True)
    appointment_date                 = Column(Date, nullable=True)
    appointment_time_from            = Column(String(50), nullable=True)  
    appointment_time_to              = Column(String(50), nullable=True)  
    source_of_enquiry_id             = Column(Integer, nullable=True)
    source                           = Column(String(100), nullable=True)
    appointment_status_id            = Column(Integer, nullable=True)
    appointment_status               = Column(String(100), nullable=True)
    consultant_id                    = Column(Integer)
    consultation_mode_id             = Column(Integer)
    consultation_tool_id             = Column(Integer)
    employee_number                  = Column(String(50), nullable=True)
    first_name                       = Column(String(50), nullable=True)
    middle_name                      = Column(String(50), nullable=True)
    last_name                        = Column(String(50), nullable=True)
    gross_amount                     = Column(Float, nullable=True)
    discount_percentage              = Column(Float, nullable=True)
    special_discount_percentage      = Column(Float, nullable=True)
    special_discount_amount          = Column(Float, nullable=True)
    net_amount                       = Column(Float, nullable=True)
    igst_amount                      = Column(Float, nullable=True)
    sgst_amount                      = Column(Float, nullable=True)
    cgst_amount                      = Column(Float, nullable=True)
    bill_amount                      = Column(Float, nullable=True)
    remarks                          = Column(String(2000), nullable=True)
    



class OffAppointmentVisitDetails(caerp_base):
    __tablename__ = 'off_appointment_visit_details'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    visit_master_id = Column(Integer, nullable=False)
    consultant_id   = Column(Integer, nullable=False)
    service_id      = Column(Integer, nullable=False)
    is_main_service = Column(Enum('yes', 'no'), nullable=False, default='no')
    created_by      = Column(Integer, nullable=True)
    created_on      = Column(Date, nullable=True)
    modified_by     = Column(Integer, nullable=True)
    modified_on     = Column(Date, nullable=True)
    is_deleted      = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by      = Column(Integer, nullable=True)
    deleted_on      = Column(Date, nullable=True)


# class OffAppointmentVisitDetailsView(caerp_base):
#     __tablename__ = 'off_view_appointment_details'

#     visit_details_id                               = Column(Integer, primary_key=True, nullable=False)
#     visit_master_id                                = Column(Integer, nullable=False)
#     appointment_number                             = Column(String(50), nullable=True)
#     financial_year_id                              = Column(Integer, nullable=True)
#     voucher_number                                 = Column(String(50), nullable=True)
#     appointment_master_id                          = Column(Integer, nullable=True)
#     appointment_date                               = Column(Date, nullable=True)
#     appointment_time_from                          = Column(String(50), nullable=False)  
#     appointment_time_to                            = Column(String(50), nullable=True)  
#     source_of_enquiry_id                           = Column(Integer, nullable=True)
#     appointment_status_id                          = Column(Integer, nullable=True)
#     gross_amount                                   = Column(Float, nullable=False)
#     discount_percentage                            = Column(Float, nullable=False)
#     special_discount_percentage                    = Column(Float, nullable=False)
#     special_discount_amount                        = Column(Float, nullable=False)
#     net_amount                                     = Column(Float, nullable=False)
#     igst_amount                                    = Column(Float, nullable=False)
#     sgst_amount                                    = Column(Float, nullable=False)
#     cgst_amount                                    = Column(Float, nullable=False)
#     bill_amount                                    = Column(Float, nullable=False)
#     remarks                                        = Column(String(2000), nullable=False)
#     service_id                                     = Column(Integer, nullable=True)
#     service_goods_name                             = Column(String(500), nullable=False)  
#     consultant_id                                  = Column(Integer, nullable=True)
#     is_main_service                                = Column(Enum('yes', 'no'), nullable=False, default='no')
#     employee_number                                = Column(String(50), nullable=True)
#     first_name                                     = Column(String(50), nullable=True)
#     middle_name                                    = Column(String(50), nullable=True)
#     last_name                                      = Column(String(50), nullable=True)
#     created_by                                     = Column(Integer, nullable=True)
#     created_on                                     = Column(Date, nullable=True)
#     modified_by                                    = Column(Integer, nullable=True)
#     modified_on                                    = Column(Date, nullable=True)
#     is_deleted                                     = Column(Enum('yes', 'no'), nullable=False, default='no')
#     deleted_by                                     = Column(Integer, nullable=True)
#     deleted_on                                     = Column(Date, nullable=True)
    

class OffAppointmentVisitDetailsView(caerp_base):
    __tablename__ = 'off_view_appointment_details'

    visit_details_id                               = Column(Integer, primary_key=True, nullable=False)
    visit_master_id                                = Column(Integer, nullable=False)
    appointment_number                             = Column(String(50), nullable=True)
    financial_year_id                              = Column(Integer, nullable=True)
    financial_year                                 = Column(String(50), nullable=True)
    voucher_number                                 = Column(String(50), nullable=True)
    appointment_master_id                          = Column(Integer, nullable=True)
    appointment_date                               = Column(Date, nullable=True)
    appointment_time_from                          = Column(String(50), nullable=False)  
    appointment_time_to                            = Column(String(50), nullable=True)  
    source_of_enquiry_id                           = Column(Integer, nullable=True)
    source                                         = Column(String(100), nullable=True)
    appointment_status_id                          = Column(Integer, nullable=True)
    appointment_status                             = Column(String(100), nullable=True)
    consultation_mode_id                           = Column(Integer)
    consultation_mode                              = Column(String(50), nullable=True) 
    consultation_tool_id                           = Column(Integer)
    consultation_tool                              = Column(String(50), nullable=True) 
    gross_amount                                   = Column(Float, nullable=False)
    discount_percentage                            = Column(Float, nullable=False)
    special_discount_percentage                    = Column(Float, nullable=False)
    special_discount_amount                        = Column(Float, nullable=False)
    net_amount                                     = Column(Float, nullable=False)
    igst_amount                                    = Column(Float, nullable=False)
    sgst_amount                                    = Column(Float, nullable=False)
    cgst_amount                                    = Column(Float, nullable=False)
    bill_amount                                    = Column(Float, nullable=False)
    remarks                                        = Column(String(2000), nullable=False)
    service_id                                     = Column(Integer, nullable=True)
    service_goods_name                             = Column(String(500), nullable=False)  
    consultant_id                                  = Column(Integer, nullable=True)
    is_main_service                                = Column(Enum('yes', 'no'), nullable=False, default='no')
    employee_number                                = Column(String(50), nullable=True)
    first_name                                     = Column(String(50), nullable=True)
    middle_name                                    = Column(String(50), nullable=True)
    last_name                                      = Column(String(50), nullable=True)
    created_by                                     = Column(Integer, nullable=True)
    created_on                                     = Column(Date, nullable=True)
    modified_by                                    = Column(Integer, nullable=True)
    modified_on                                    = Column(Date, nullable=True)
    is_deleted                                     = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                                     = Column(Integer, nullable=True)
    deleted_on                                     = Column(Date, nullable=True)
    

class OffAppointmentCancellationReason(caerp_base):
    __tablename__ = 'off_appointment_cancellation_reason'

    id                                  = Column(Integer, primary_key=True, autoincrement=True)
    off_appointment_cancellation_reason = Column(String(100), nullable=False)
    is_deleted                          = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class OffAppointmentStatus(caerp_base):
    __tablename__ = 'off_appointment_status'
    id                 = Column(Integer, primary_key=True, autoincrement=True)
    appointment_status = Column(String(100), nullable=False)
    is_deleted         = Column(Enum('yes', 'no'), nullable=False, default='no')
 



#..........................by swathy----------------------------------

class AppHsnSacClasses(caerp_base):
    __tablename__ = 'app_hsn_sac_classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

    
class OffServiceGoodsGroup(caerp_base):
    __tablename__ = 'off_service_goods_group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_classess_id = Column(Integer, nullable=False)
    group_name = Column(String(250), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class OffServiceGoodsSubGroup(caerp_base):
    __tablename__ = 'off_service_goods_sub_group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, nullable=False)
    sub_group_name = Column(String(100), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffServiceGoodsCategory(caerp_base):
    __tablename__ = 'off_service_goods_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_group_id = Column(Integer, nullable=False)
    category_name = Column(String(200), nullable=True)
    gst_category_code = Column(String(20), nullable=True) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffServiceGoodsSubCategory(caerp_base):
    __tablename__ = 'off_service_goods_sub_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    sub_category_name = Column(String(200), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class OffViewServiceGoodsMaster(caerp_base): 
    __tablename__ = 'off_view_service_goods_master'
    
    service_goods_master_id = Column(Integer, primary_key=True, nullable=False)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_class = Column(String(100), nullable=True)
    group_id = Column(Integer, nullable=False)
    service_goods_group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    service_goods_sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    service_goods_category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    service_goods_sub_category_name = Column(String(200), nullable=True)
    service_goods_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=True)
    hsn_sac_description = Column(String(2000), nullable=True)
    gst = Column(String(2), nullable=False)
    sku_code_id = Column(Integer, nullable=False)
    stock_keeping_unit_code = Column(String(250), nullable=True)
    has_consultation = Column(Enum('yes', 'no'), nullable=False)
    is_bundled_service = Column(Enum('yes', 'no'), nullable=False)
    service_goods_master_created_by = Column(Integer, nullable=False)
    service_goods_master_created_on = Column(DateTime, nullable=False)
    service_goods_master_modified_by = Column(Integer, nullable=True)
    service_goods_master_modified_on = Column(DateTime, nullable=True)
    service_goods_master_is_deleted = Column(Enum('yes', 'no'), nullable=False)
    service_goods_master_deleted_by = Column(Integer, nullable=True)
    service_goods_master_deleted_on = Column(DateTime, nullable=True)


class OffServiceGoodsMaster(caerp_base):
    __tablename__  = 'off_service_goods_master'
    id                 = Column(Integer, primary_key=True, index=True)
    hsn_sac_class_id   = Column(Integer, nullable=False)
    group_id           = Column(Integer, nullable=False)
    sub_group_id       = Column(Integer, nullable=False)
    category_id        = Column(Integer, nullable=False)
    sub_category_id    = Column(Integer, nullable=False)
    service_goods_name = Column(String(500), nullable=False)
    hsn_sac_id         = Column(Integer, nullable=False)
    sku_code_id        = Column(Integer, nullable=False)
    has_consultation   = Column(Enum('yes', 'no'), default='no', nullable=False)
    is_bundled_service = Column(Enum('yes', 'no'), default='no', nullable=False)
    created_by         = Column(Integer, nullable=False)
    created_on         = Column(DateTime, nullable=False)
    modified_by        = Column(Integer, nullable=True)
    modified_on        = Column(DateTime, nullable=True)
    is_deleted         = Column(Enum('yes', 'no'), default='no', nullable=False)
    deleted_by         = Column(Integer, nullable=True)
    deleted_on         = Column(DateTime, nullable=True)
    is_locked          = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on          = Column(Date, nullable=True)
    locked_by          = Column(Integer, nullable=True)


class OffServiceGoodsDetails(caerp_base):
        
    __tablename__ = 'off_service_goods_details'
    id = Column(Integer, primary_key=True, index=True)
    service_goods_master_id = Column(Integer, nullable=False)
    bundled_service_goods_id = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True) 
  
  
class OffViewServiceGoodsDetails(caerp_base):
    __tablename__ = 'off_view_service_goods_details'

    service_goods_details_id = Column(Integer, primary_key=True, nullable=False)
    service_goods_master_id = Column(Integer, nullable=False)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_class = Column(String(100), nullable=False)
    group_id = Column(Integer, nullable=False)
    service_master_group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    service_master_sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    service_master_category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    service_master_sub_category_name = Column(String(200), nullable=True)
    service_goods_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=False)
    hsn_sac_description = Column(String(2000), nullable=True)
    sku_code_id = Column(Integer, nullable=False)
    stock_keeping_unit_code = Column(String(250), nullable=True)
    has_consultation = Column(Enum('yes', 'no'), nullable=False)
    is_bundled_service = Column(Enum('yes', 'no'), nullable=False)
    bundled_service_goods_id = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=True)
    service_goods_details_created_by = Column(Integer, nullable=False)
    service_goods_details_created_on = Column(DateTime, nullable=False)
    service_goods_details_modified_by = Column(Integer, nullable=True)
    service_goods_details_modified_on = Column(DateTime, nullable=True)
    service_goods_details_is_deleted = Column(Enum('yes', 'no'), nullable=False)
    service_goods_details_deleted_by = Column(Integer, nullable=True)
    service_goods_details_deleted_on = Column(DateTime, nullable=True)


#--------------------

class OffViewServiceGoodsPriceMaster(caerp_base):
    __tablename__ = 'off_view_service_goods_price_master'

    service_goods_price_master_id = Column(Integer, primary_key=True)
    service_goods_master_id = Column(Integer)
    hsn_sac_class_id = Column(Integer)
    hsn_sac_class = Column(String)
    group_id = Column(Integer)
    group_name = Column(String)
    sub_group_id = Column(Integer)
    sub_group_name = Column(String)
    category_id = Column(Integer)
    category_name = Column(String)
    sub_category_id = Column(Integer)
    sub_category_name = Column(String)
    service_goods_name = Column(String)
    hsn_sac_id = Column(Integer)
    hsn_sac_code = Column(String)
    hsn_sac_description = Column(String)
    sku_code_id = Column(Integer)
    unit_code = Column(String)
    has_consultation = Column(Integer)
    # is_consultancy_service = Column(Integer)
    is_bundled_service = Column(Integer)
    services_goods_master_modified_by = Column(Integer)
    services_goods_master_modified_on = Column(DateTime)
    services_goods_master_is_deleted = Column(String)
    services_goods_master_deleted_by = Column(Integer)
    services_goods_master_deleted_on = Column(DateTime)
    constitution_id = Column(Integer)
    business_constitution_name = Column(String)
    business_constitution_code = Column(String)
    business_constitution_description = Column(String)
    pan_code = Column(String)
    service_charge = Column(Float)
    govt_agency_fee = Column(Float)
    stamp_duty = Column(Float)
    stamp_fee = Column(Float)
    effective_from_date = Column(DateTime)
    effective_to_date = Column(DateTime)
    service_goods_price_master_created_by = Column(Integer)
    service_goods_price_master_created_on = Column(DateTime)
    
class OffServiceGoodsPriceMaster(caerp_base):
    __tablename__ = 'off_service_goods_price_master'
    
    id = Column(Integer, primary_key=True, index=True)
    service_goods_master_id = Column(Integer,nullable=False)
    constitution_id = Column(Integer, nullable=False)
    service_charge = Column(Float, default=0.00)
    govt_agency_fee = Column(Float, default=0.00)
    stamp_duty = Column(Float, default=0.00)
    stamp_fee = Column(Float, default=0.00)
    effective_from_date = Column(Date, nullable=False)
    effective_to_date = Column(Date, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    
    




class AppStockKeepingUnitCode(caerp_base):
    __tablename__ = 'app_stock_keeping_unit_code'

    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_code = Column(String(250), default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class AppBusinessConstitution(caerp_base):
    __tablename__ = 'app_business_constitution'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_constitution_name = Column(String(100), nullable=False)
    business_constitution_code = Column(String(100), nullable=False)
    description = Column(String(500), default=None)
    pan_code = Column(String(10), default=None)
    display_order = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    


class OffDocumentDataMaster(caerp_base):
    __tablename__ = 'off_document_data_master'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_data_type_id = Column(Integer, nullable=False)
    document_data_name = Column(String(200), nullable=False)
    has_expiry = Column(Enum('yes', 'no'), default='no', nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
class OffDocumentDataType(caerp_base):
    __tablename__ = 'off_document_data_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_data_type = Column(String(200), nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffDocumentDataCategory(caerp_base):
    __tablename__ = 'off_document_data_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(200), nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffNatureOfPossession(caerp_base):
    __tablename__ = 'off_nature_of_possession'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nature_of_possession = Column(String(200), nullable=False) 
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
class OffServiceDocumentDataMaster(caerp_base):
    __tablename__ = 'off_service_document_data_master'
    id                       = Column(Integer, primary_key=True, autoincrement=True)
    service_goods_master_id  = Column(Integer, nullable=False)
    group_id                 = Column(Integer, nullable=False)
    sub_group_id             = Column(Integer, nullable=False)
    category_id              = Column(Integer, nullable=False)
    sub_category_id          = Column(Integer, nullable=False)
    constitution_id          = Column(Integer, nullable=False)
    created_by               = Column(Integer, nullable=False)
    created_on               = Column(DateTime, nullable=False)
    modified_by              = Column(Integer, nullable=True)
    modified_on              = Column(DateTime, nullable=True)
    is_deleted               = Column(Enum('yes', 'no'), default='no', nullable=False)
    deleted_by               = Column(Integer, nullable=True)
    deleted_on               = Column(DateTime, nullable=True)
    is_locked                = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on                = Column(Date, nullable=True)
    locked_by                = Column(Integer, nullable=True)



class OffServiceDocumentDataDetails(caerp_base):
    __tablename__ = 'off_service_document_data_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_data_category_id = Column(Integer, nullable=False)
    service_document_data_master_id = Column(Integer, nullable=False)
    document_data_master_id = Column(Integer, nullable=False)
    nature_of_possession_id = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=False,default=1)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')



class OffViewServiceDocumentsDataDetails(caerp_base):
    __tablename__ = 'off_view_service_documents_data_details'
   
    service_document_data_details_id = Column(Integer, primary_key=True, nullable=False)
    document_data_category_id = Column(Integer, nullable=False)
    document_data_category_category_name = Column(String(200), nullable=False)
    service_document_data_master_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    group_name = Column(String(250))
    sub_group_id = Column(Integer, nullable=False)
    sub_group_name = Column(String(100))
    category_id = Column(Integer, nullable=False)
    category_name = Column(String(200))
    sub_category_id = Column(Integer, nullable=False)
    sub_category_name = Column(String(200))
    constitution_id = Column(Integer, nullable=False)
    business_constitution_name = Column(String(100), nullable=False)
    business_constitution_code = Column(String(100), nullable=False)
    description = Column(String(500))
    document_data_master_id = Column(Integer, nullable=False)
    document_data_type_id = Column(Integer, nullable=False)
    document_data_type = Column(String(200), nullable=False)
    document_data_name = Column(String(200), nullable=False)
    has_expiry = Column(Enum('yes', 'no'), nullable=False)
    nature_of_possession_id = Column(Integer,nullable=True)
    nature_of_possession = Column(String(200), nullable=False)
    display_order = Column(Integer, nullable=False)
    service_document_data_details_is_deleted = Column(Enum('yes', 'no'), nullable=False) 
    
class OffViewServiceDocumentsDataMaster(caerp_base):
    __tablename__ = 'off_view_service_documents_data_master'

    service_document_data_master_id = Column(Integer, primary_key=True)
    service_goods_master_id =Column(Integer, nullable=False)
    service_goods_name = Column(String(500), nullable=False)
    group_id = Column(Integer, nullable=False)
    group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    sub_category_name = Column(String(200), nullable=True)
    constitution_id = Column(Integer, nullable=False)
    business_constitution_name = Column(String(100), nullable=False)
    business_constitution_code = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
   
#--------------------aparna
 

class OffConsultantServiceDetails(caerp_base):
    __tablename__ = "off_consultant_service_details"

    id                              = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id                   = Column(Integer, default=0)
    service_goods_master_id         = Column(Integer,  nullable=False)
    consultation_fee                = Column(Float, nullable=False)
    slot_duration_in_minutes        = Column(Integer, nullable=False)
    effective_from_date             = Column(Date, nullable=False)
    effective_to_date               = Column(Date, default=None)
    created_by                      = Column(Integer, nullable=False)
    created_on                      = Column(DateTime, nullable=False)


class OffConsultantSchedule(caerp_base):
    __tablename__ = "off_consultant_schedule"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer,nullable=False)
    day_of_week_id = Column(Integer,nullable=False)
    consultation_mode_id = Column(Integer, nullable=False)
    morning_start_time = Column(Time, default=None)
    morning_end_time = Column(Time, default=None)
    afternoon_start_time = Column(Time, default=None)
    afternoon_end_time = Column(Time, default=None)
    is_normal_schedule = Column(Enum('yes', 'no'), nullable=False, default='no')
    consultation_date = Column(Date, default=None)
    effective_from_date = Column(Date, default=None)
    effective_to_date = Column(Date, default=None)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_by = Column(Integer, default=None)
    modified_on = Column(DateTime, default=None)


class OffConsultationMode(caerp_base):
    __tablename__ = 'off_consultation_mode'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_mode = Column(String(50), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class AppDayOfWeek(caerp_base):
    __tablename__ = 'app_day_of_week'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    day_short_name = Column(String(4), nullable=False)
    day_long_name = Column(String(10), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class OffEnquiryStatus(caerp_base):
    __tablename__ = 'off_enquiry_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    enquiry_status = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class OffSourceOfEnquiry(caerp_base):
    __tablename__  =  "off_source_of_enquiry"
    
    id      = Column(Integer, primary_key=True, autoincrement=True)
    source 	 = Column(String(100), nullable=False)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')   



class OffEnquirerType(caerp_base):
    __tablename__ = 'off_enquirer_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_type = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
class OffConsultationTool(caerp_base):
    __tablename__ = 'off_consultation_tool'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_mode_id = Column(Integer, nullable=False)
    consultation_tool = Column(String(50), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

#=------------------------Enquiry--------------------



class OffEnquiryMaster(caerp_base): 
    __tablename__ = 'off_enquiry_master'

 	
    id                           = Column(Integer, primary_key=True, autoincrement=True)
    customer_number              = Column(String(100), nullable=True)
    first_name 	                 = Column(String(200), nullable=False)
    middle_name 	             = Column(String(200), nullable=True)
    last_name 	                 = Column(String(200), nullable=True)
    gender_id                    = Column(Integer, nullable=True)
    date_of_birth                = Column(Date, nullable=True)
    mobile_number                = Column(String(20), nullable=True)
    whatsapp_number              = Column(String(20), nullable=True)
    email_id                     = Column(String(50), nullable=True)
    house_or_building_name       = Column(String(100), nullable=True)
    road_or_street_name          = Column(String(100), nullable=True)
    locality                     = Column(String(100), nullable=True)
    pin_code                     = Column(String(50), nullable=True)
    village_id                   = Column(Integer, nullable=True)
    post_office_id               = Column(Integer, nullable=True)
    lsg_type_id                  = Column(Integer, nullable=True)
    lsg_id                       = Column(Integer, nullable=True)
    taluk_id                     = Column(Integer, nullable=True)
    district_id                  = Column(Integer, nullable=True)
    state_id                     = Column(Integer, nullable=True)
    country_id                   = Column(Integer, nullable=True)
    created_by                   = Column(Integer, nullable=True)
    created_on                   = Column(Date, nullable=True)
    modified_by                  = Column(Integer, nullable=True)
    modified_on                  = Column(Date, nullable=True)
    is_deleted                   = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                   = Column(Integer, nullable=True)
    deleted_on                   = Column(Date, nullable=True)
    is_locked                    = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on                    = Column(Date, nullable=True)
    locked_by                    = Column(Integer, nullable=True)


class OffEnquiryDetails(caerp_base):
    __tablename__ = 'off_enquiry_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id = Column(Integer, nullable=True)
    enquiry_master_id = Column(Integer, nullable=False)
    enquiry_date = Column(Date, nullable=True)
    enquiry_number= Column(String(100), nullable=True) 
    source_of_enquiry_id = Column(Integer, nullable=False)
    enquirer_type_id= Column(Integer, nullable=False)
    company_or_business_name= Column(String(100), nullable=True)
    enquiry_status_id=Column(Integer, nullable=False)
    remarks= Column(String(2000), nullable=True)
    created_by = Column(Integer, nullable=True)
    created_on = Column(Date, nullable=True)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(Date, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(Date, nullable=True)
    is_locked               = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on               = Column(Date, nullable=True)
    locked_by               = Column(Integer, nullable=True)


#view
class OffViewEnquiryMaster(caerp_base): 
    __tablename__ = 'off_view_enquiry_master'

 	
    enquiry_master_id       = Column(Integer, primary_key=True, autoincrement=True)
    customer_number         = Column(String(100), nullable=True)
    first_name 	            = Column(String(200), nullable=False)
    middle_name 	        = Column(String(200), nullable=True)
    last_name 	            = Column(String(200), nullable=True)
    gender_id               = Column(Integer, nullable=True)
    gender                  = Column(String(200))
    date_of_birth           = Column(Date, nullable=True)
    mobile_number           = Column(String(20), nullable=True)
    whatsapp_number         = Column(String(20), nullable=True)
    email_id                = Column(String(50), nullable=True)
    house_or_building_name  = Column(String(100), nullable=True)
    road_or_street_name     = Column(String(100), nullable=True)
    locality                = Column(String(100), nullable=True)
    pin_code                = Column(String(50), nullable=True)
    post_office_id          = Column(Integer, nullable=True)
    post_office_name        = Column(String(255), nullable=True)
    village_id              = Column(Integer, nullable=True)
    village_name            = Column(String(255), nullable=True)
    lsg_type_id             = Column(Integer, nullable=True)
    lsg_type                = Column(String(255), nullable=True)
    lsg_id                  = Column(Integer, nullable=True)
    lsg_name                = Column(String(255), nullable=True)
    taluk_id                = Column(Integer, nullable=True)
    taluk_name              = Column(String(255), nullable=True)
    district_id             = Column(Integer, nullable=True)
    district_name           = Column(String(255), nullable=True)
    state_id                = Column(Integer, nullable=True)
    state_name              = Column(String(255), nullable=True)
    country_id              = Column(Integer, nullable=True)
    country_name_english    = Column(String(255), nullable=True)
    country_name_arabic     = Column(String(255), nullable=True)
    created_by              = Column(Integer, nullable=True)
    created_on              = Column(Date, nullable=True)
    modified_by             = Column(Integer, nullable=True)
    modified_on             = Column(Date, nullable=True)
    is_deleted              = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by              = Column(Integer, nullable=True)
    deleted_on              = Column(Date, nullable=True)
    is_locked               = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on               = Column(Date, nullable=True)
    locked_by               = Column(Integer, nullable=True)




class OffViewEnquiryDetails(caerp_base): 
    __tablename__ = 'off_view_enquiry_details'

 	
    enquiry_details_id          = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id           = Column(Integer, nullable=True)
    financial_year              = Column(String(100), nullable=True) 
    enquiry_master_id           = Column(Integer, nullable=False)
    customer_number             =Column(String(100), nullable=True)
    first_name 	                = Column(String(200), nullable=False)
    middle_name 	            = Column(String(200), nullable=True)
    last_name 	                = Column(String(200), nullable=True)
    gender_id                   = Column(Integer, nullable=True)
    gender                      = Column(String(200))
    date_of_birth               =Column(Date, nullable=True)
    mobile_number               = Column(String(20), nullable=True)
    whatsapp_number             =Column(String(20), nullable=True)
    email_id                    = Column(String(50), nullable=True)
    house_or_building_name      =Column(String(100), nullable=True)
    road_or_street_name         =Column(String(100), nullable=True)
    locality                    =Column(String(100), nullable=True)
    pin_code                    =Column(String(50), nullable=True)
    post_office_id              = Column(Integer, nullable=True)
    post_office_name            = Column(String(255), nullable=True)
    lsg_type_id                 = Column(Integer, nullable=True)
    lsg_type                    = Column(String(255), nullable=True)
    lsg_id                      = Column(Integer, nullable=True)
    lsg_name                    = Column(String(255), nullable=True)
    taluk_id                    = Column(Integer, nullable=True)
    taluk_name                  =Column(String(255), nullable=True)
    district_id                 = Column(Integer, nullable=True)
    district_name               =Column(String(255), nullable=True)
    state_id                    = Column(Integer, nullable=True)
    state_name                  =Column(String(255), nullable=True)
    country_id                  = Column(Integer, nullable=True)
    country_name_english        =Column(String(255), nullable=True)
    country_name_arabic         =Column(String(255), nullable=True)
    enquiry_date                = Column(Date, nullable=True)
    enquiry_number              = Column(String(100), nullable=True) 
    source_of_enquiry_id        = Column(Integer, nullable=False)
    source                      =Column(String(255), nullable=True)
    enquirer_type_id            = Column(Integer, nullable=False)
    person_type                 =Column(String(255), nullable=True)
    company_or_business_name    = Column(String(100), nullable=True)
    enquiry_status_id           =Column(Integer, nullable=False)
    enquiry_status              =Column(String(255), nullable=True)
    remarks                     = Column(String(2000), nullable=True)
    created_by                  = Column(Integer, nullable=True)
    created_on                  = Column(Date, nullable=True)
    modified_by                 = Column(Integer, nullable=True)
    modified_on                 = Column(Date, nullable=True)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, nullable=True)
    deleted_on                  = Column(Date, nullable=True)
    
    
class OffTaskPriority(caerp_base):
    __tablename__ = 'off_task_priority'
    id                  = Column(Integer, primary_key=True, autoincrement=True)
    task_priority       = Column(String(100), nullable=True) 
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffConsultationTaskStatus(caerp_base):
    __tablename__ = 'off_consultation_task_status'
    id                  = Column(Integer, primary_key=True, autoincrement=True)
    task_status         = Column(String(100), nullable=True) 
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffServiceTaskStatus(caerp_base):
    __tablename__ = 'off_service_task_status'
    id                  = Column(Integer, primary_key=True, autoincrement=True)
    task_status         = Column(String(100), nullable=True) 
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no') 


  

class OffConsultationTaskMaster(caerp_base):
    __tablename__ = 'off_consultation_task_master'
    id                      = Column(Integer, primary_key=True, autoincrement=True)
    task_date               = Column(Date, nullable=False)
    consultant_id           = Column(Integer, nullable=False)
    appointment_master_id   = Column(Integer, nullable=False)
    visit_master_id         = Column(Integer, nullable=False)
    task_status_id          = Column(Integer, nullable=False)
    task_priority_id        = Column(Integer, nullable=False)
    remarks                 = Column(String(1000), nullable=True)
    created_by              = Column(Integer, nullable=False)
    created_on              = Column(DateTime, nullable=False)
    modified_by             = Column(Integer, nullable=True)
    modified_on             = Column(DateTime, nullable=True)
    is_deleted              = Column(Enum('yes', 'no'), default='no', nullable=False)
    deleted_by              = Column(Integer, nullable=True)
    deleted_on              = Column(DateTime, nullable=True)
    is_locked               = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on               = Column(Date, nullable=True)
    locked_by               = Column(Integer, nullable=True)




class OffConsultationTaskDetails(caerp_base):
    __tablename__ = 'off_consultation_task_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_master_id = Column(Integer,nullable=False)
    service_id = Column(Integer, nullable=False)
    is_main_service = Column(Enum('yes', 'no'), default='no', nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)




class OffViewConsultationTaskMaster(caerp_base):
    __tablename__ = 'off_view_consultation_task_master'
    
    consultation_task_master_id = Column(Integer, primary_key=True)
    task_date = Column(DateTime, nullable=False)
    consultant_id = Column(Integer, nullable=False)
    employee_number = Column(String(50), nullable=False)
    employee_first_name = Column(String(50), nullable=False)
    employee_middle_name = Column(String(50), nullable=True)
    employee_last_name = Column(String(50), nullable=False)
    appointment_master_id = Column(Integer, nullable=False)
    appointee_full_name = Column(String(100), nullable=False)
    appointee_gender_id = Column(Integer, nullable=False)
    appointee_gender = Column(String(20), nullable=False)
    customer_number = Column(String(100), nullable=True)
    legal_name = Column(String(100), nullable=True)
    locality = Column(String(50), nullable=True)
    pin_code = Column(String(50), nullable=True)
    post_office_id = Column(Integer, nullable=True)
    post_office_name = Column(String(255), nullable=True)
    taluk_id = Column(Integer, nullable=True)
    taluk_name = Column(String(50), nullable=True)
    district_id = Column(Integer, nullable=True)
    district_name = Column(String(50), nullable=True)
    state_id = Column(Integer, nullable=True)
    state_name = Column(String(50), nullable=True)
    appointee_mobile_number = Column(String(20), nullable=True)
    appointee_whatsapp_number = Column(String(20), nullable=True)
    appointee_email_id = Column(String(50), nullable=True)
    visit_master_id = Column(Integer, nullable=False)
    visit_master_appointment_time_from = Column(String(20), nullable=False)
    visit_master_appointment_time_to = Column(String(20), nullable=True)
    consultation_mode_id = Column(Integer, nullable=False)
    consultation_mode = Column(String(50), nullable=False)
    consultation_tool_id = Column(Integer, nullable=False)
    consultation_tool = Column(String(50), nullable=False)
    task_status_id = Column(Integer, nullable=False)
    task_status = Column(String(100), nullable=True)
    task_priority_id = Column(Integer, nullable=False)
    task_priority = Column(String(100), nullable=True)
    remarks = Column(String(1000), nullable=True)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)
    consultation_task_details_id = Column(Integer, nullable=True)
    task_master_id = Column(Integer, nullable=True)
    service_id = Column(Integer, nullable=True)
    # consultation_task_details_is_deleted = Column(Enum('yes', 'no'), nullable=True)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_class = Column(String(100), nullable=False)
    has_consultation = Column(Enum('yes', 'no'), nullable=False)
    group_id = Column(Integer, nullable=False)
    group_name = Column(String(250), nullable=True)
    sub_group_id = Column(Integer, nullable=False)
    sub_group_name = Column(String(100), nullable=True)
    category_id = Column(Integer, nullable=False)
    category_name = Column(String(200), nullable=True)
    sub_category_id = Column(Integer, nullable=False)
    sub_category_name = Column(String(200), nullable=True)
    service_goods_name = Column(String(500), nullable=False)
    hsn_sac_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), nullable=False)
    sku_code_id = Column(Integer, nullable=False)
    unit_code = Column(String(250), nullable=True)
    is_bundled_service = Column(Enum('yes', 'no'), nullable=False)
    is_main_service = Column(Enum('yes', 'no'), nullable=True)




class OffOfferCategory(caerp_base):
    __tablename__ ='off_offer_category'

    id              = Column(Integer, primary_key=True, index=True)
    offer_category  = Column(String(100), default=None)
    description     = Column(String(100), default=None)
    is_deleted      = Column(Enum('yes', 'no'), nullable=False, default='no')


class OffOfferMaster(caerp_base):
    __tablename__ = "off_offer_master"

    id                  = Column(Integer, primary_key=True, index=True)
    offer_category_id   = Column(Integer, nullable=False)
    offer_name          = Column(String, nullable=False)
    offer_percentage    = Column(Float, default=0.0)
    effective_from_date = Column(Date, nullable=False)
    effective_to_date   = Column(Date, nullable=False)
    created_by          = Column(Integer, nullable=False)
    created_on          = Column(DateTime, nullable=False, default=func.now())
    modified_by         = Column(Integer, default=None)
    modified_on         = Column(DateTime, default=None)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by          = Column(Integer, default=None)
    deleted_on          = Column(DateTime, default=None)


class OffOfferMasterView(caerp_base):
    __tablename__ = 'off_view_offer_master'

    offer_master_id                  = Column(Integer, primary_key=True, index=True)
    offer_category_id                = Column(Integer, nullable=False)
    offer_category                   = Column(String, nullable=False)
    offer_name                       = Column(String, nullable=False)
    offer_percentage                 = Column(Float, default=0.0)
    offer_master_effective_from_date = Column(Date, nullable=False)
    offer_master_effective_to_date   = Column(Date, nullable=False)
    offer_master_created_by          = Column(Integer, nullable=False)
    offer_master_created_on          = Column(DateTime, nullable=False, default=func.now())
    offer_master_modified_by         = Column(Integer, default=None)
    offer_master_modified_on         = Column(DateTime, default=None)
    offer_master_is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    offer_master_deleted_by          = Column(Integer, default=None)
    offer_master_deleted_on          = Column(DateTime, default=None)


class OffOfferDetails(caerp_base):
    __tablename__ = 'off_offer_details'

    id                      = Column(Integer, primary_key=True, index=True)
    offer_master_id         = Column(Integer, nullable=False)
    service_goods_master_id = Column(Integer, nullable=False)
    created_by              = Column(Integer, nullable=False)
    created_on              = Column(DateTime, nullable=False, default=func.now())
    modified_by             = Column(Integer, default=None)
    modified_on             = Column(DateTime, default=None)
    is_deleted              = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by              = Column(Integer, default=None)
    deleted_on              = Column(DateTime, default=None)

class OffOfferDetailsView(caerp_base):
    __tablename__ = 'off_view_offer_details'

    offer_details_id             = Column(Integer, primary_key=True, index=True) 
    offer_master_id              = Column(Integer, nullable=False)
    offer_category_id            = Column(Integer, nullable=False)
    offer_category               = Column(String, nullable=False)
    offer_name                   = Column(String, nullable=False)
    offer_percentage             = Column(Float, default=0.0)
    offer_amount                 = Column(Float, default=0.0)
    service_goods_master_id      = Column(Integer, nullable=False)
    service_goods_name           = Column(String, nullable=False)
    effective_from_date          = Column(Date, nullable=False)
    effective_to_date            = Column(Date, default=None)
    offer_details_created_by     = Column(Integer, nullable=False)
    offer_details_created_on     = Column(DateTime, nullable=False, default=func.now())
    offer_details_modified_by    = Column(Integer, default=None)
    offer_details_modified_on    = Column(DateTime, default=None)
    offer_details_is_deleted     = Column(Enum('yes', 'no'), nullable=False, default='no')
    offer_details_deleted_by     = Column(Integer, default=None)
    offer_details_deleted_on     = Column(DateTime, default=None)



class OffViewConsultantServiceDetails(caerp_base):
    __tablename__ = 'off_view_consultant_service_details'

    consultant_service_details_id = Column(Integer, primary_key=True)
    consultant_id = Column(Integer)
    employee_number = Column(String)
    first_name = Column(String)
    middle_name = Column(String, nullable=True)
    last_name = Column(String)
    service_goods_master_id = Column(Integer)
    hsn_sac_class_id = Column(Integer)
    hsn_sac_class = Column(String)
    group_id = Column(Integer)
    group_name = Column(String)
    sub_group_id = Column(Integer)
    sub_group_name = Column(String)
    category_id = Column(Integer)
    category_name = Column(String)
    sub_category_id = Column(Integer)
    sub_category_name = Column(String)
    service_goods_name = Column(String)
    hsn_sac_id = Column(Integer)
    hsn_sac_code = Column(String)
    hsn_sac_description = Column(String)
    sku_code_id = Column(Integer)
    unit_code = Column(String)
    has_consultation = Column(Integer)
    is_bundled_service = Column(Integer)
    service_goods_master_modified_by = Column(Integer)
    service_goods_master_modified_on = Column(DateTime)
    service_goods_master_is_deleted = Column(String)
    service_goods_master_deleted_by = Column(Integer)
    service_goods_master_deleted_on = Column(DateTime)
    consultation_fee = Column(Float)
    slot_duration_in_minutes = Column(Integer)
    consultant_details_effective_from_date = Column(DateTime)
    consultant_details_effective_to_date = Column(DateTime, nullable=True)
    consultant_details_created_by = Column(Integer)
    consultant_details_created_on = Column(DateTime)

#-------------------------WORKORDER---------------------------------------


class OffWorkOrderMaster(caerp_base):
    __tablename__ = 'work_order_master'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id       = Column(Integer, nullable=False)
    enquiry_master_id       = Column(Integer, nullable=True)
    appointment_master_id   = Column(Integer, nullable=True)
    visit_master_id         =  Column(Integer, nullable=True)
    customer_id             = Column(Integer, nullable=True)
    enquiry_details_id      = Column(Integer, nullable=True)
    work_order_number       = Column(Integer, nullable=False)
    work_order_date         = Column(Date, nullable=True)
    first_name              = Column(String, nullable=True)
    middle_name             = Column(String, nullable=True)
    last_name               = Column(String, nullable=True)
    gender_id               = Column(Integer, nullable=False)
    date_of_birth           = Column(Date, nullable=False)
    mobile_number           = Column(String, nullable=True)
    whatsapp_number         = Column(String, nullable=True)
    email_id                = Column(String, nullable=True)
    house_or_building_name  = Column(String, nullable=True)
    road_or_street_name     = Column(String, nullable=True)
    locality                = Column(String, nullable=True)
    pin_code                = Column(String, nullable=True)
    post_office_id          = Column(Integer, nullable=False)
    village_id              = Column(Integer, nullable=False)
    lsg_type_id             = Column(Integer, nullable=False)
    lsg_id                  = Column(Integer, nullable=False)
    taluk_id                = Column(Integer, nullable=False)
    district_id             = Column(Integer, nullable=False)
    state_id                = Column(Integer, nullable=False)
    country_id              = Column(Integer, nullable=False)
    remarks                 = Column(String, nullable=True)
    contact_person_name     = Column(String, nullable=True)
    contact_person_mobile_number     = Column(String, nullable=True)
    contact_person_whatsapp_number   = Column(String, nullable=True)
    contact_person_email_id          = Column(String, nullable=True)
    work_order_status_id             = Column(Integer, nullable=False)
    created_by                       = Column(String, nullable=True)
    created_on                       = Column(DateTime, nullable=False)
    modified_by                      = Column(String, nullable=True)
    modified_on                      = Column(DateTime, nullable=True)
    is_deleted                       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                       = Column(String, nullable=True)
    deleted_on                       = Column(DateTime, nullable=True)
    is_locked                        = Column(Enum('yes', 'no'), nullable=False, default='no')  
    locked_on                        = Column(DateTime, nullable=True)
    locked_by                        = Column(String, nullable=True)



class OffWorkOrderDetails(caerp_base):
    __tablename__ = 'work_order_details'
    
    id                      = Column(Integer, primary_key=True, autoincrement=True)
    work_order_master_id    = Column(Integer, nullable=True)
    service_goods_master_id   = Column(Integer, nullable=True)
    constitution_id         = Column(Integer, nullable=True)
    trade_name              = Column(String, nullable=True)
    legal_name             = Column(String, nullable=True)
    business_activity_type_id      = Column(Integer, nullable=True)
    business_activity_master_id   = Column(Integer, nullable=True)
    business_activity_id        = Column(Integer, nullable=True)
    has_branches                = Column(Enum('yes', 'no'), nullable=False, default='no')
    number_of_branches          = Column(Integer, nullable=True)
    has_godowns                 = Column(Enum('yes', 'no'), nullable=False, default='no')
    number_of_godowns           = Column(Integer, nullable=True)
    number_of_directors         = Column(Integer, nullable=True)
    number_of_partners          = Column(Integer, nullable=True)
    number_of_shareholders      = Column(Integer, nullable=True)
    number_of_trustees          = Column(Integer, nullable=True)
    number_of_members           = Column(Integer, nullable=True)
    number_of_authorized_signatory = Column(Integer, nullable=True)
    is_main_service             = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
    bundle_service_id           = Column(Integer, nullable=True)
    is_depended_service         = Column(Enum('yes', 'no'), nullable=False, default='no')
    processing_order            = Column(Integer, nullable=True)
    is_service_required         = Column(Enum('YES', 'NO', 'LATER'), nullable=False, default='YES')
    service_required_date       = Column(Date, nullable=True)
    service_status_id           = Column(Integer, nullable=False)
    file_opened_on              = Column(DateTime, nullable=True)
    file_closed_on              = Column(DateTime, nullable=True)
    rack_number                 = Column(Integer, nullable=True)
    shelf_number                = Column(Integer, nullable=True)
    file_number                 = Column(Integer, nullable=True)
    remarks                     = Column(String, nullable=True)
    created_by                       = Column(String, nullable=False)
    created_on                       = Column(DateTime, nullable=False)
    modified_by                      = Column(String, nullable=True)
    modified_on                      = Column(DateTime, nullable=True)
    is_deleted                       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                       = Column(String, nullable=True)
    deleted_on                       = Column(DateTime, nullable=True)


class OffWorkOrderStatus(caerp_base):
    __tablename__ ='off_work_order_status'

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    work_order_status   = Column(String, nullable=False)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')


class WorkOrderDependancy(caerp_base):
    __tablename__ = 'work_order_dependency'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    work_order_master_id    =  Column(Integer, nullable=False)
    work_order_details_id   =  Column(Integer, nullable=False)
    dependent_on_work_id    =  Column(Integer, nullable=False)
    is_deleted              = Column(Enum('yes', 'no'), nullable=False, default='no')


class WorkOrderMasterView(caerp_base):
    __tablename__ = 'off_view_work_order_master'

    work_order_master_id    = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id       = Column(Integer, nullable=False)
    financial_year          = Column(String, nullable = False)
    enquiry_master_id       = Column(Integer, nullable=True)
    appointment_master_id   = Column(Integer, nullable=True)
    visit_master_id         =  Column(Integer, nullable=True)
    enquiry_details_id      = Column(Integer, nullable=True)
    work_order_number       = Column(String(50), nullable=False)
    work_order_date         = Column(Date, nullable=True)
    customer_id             = Column(Integer, nullable=True)
    first_name              = Column(String, nullable=True)
    middle_name             = Column(String, nullable=True)
    last_name               = Column(String, nullable=True)
    gender_id               = Column(Integer, nullable=False)
    gender                  = Column(String, nullable=True)
    date_of_birth           = Column(Date, nullable=False)
    mobile_number           = Column(String, nullable=True)
    whatsapp_number         = Column(String, nullable=True)
    email_id                = Column(String, nullable=True)
    house_or_building_name  = Column(String, nullable=True)
    road_or_street_name     = Column(String, nullable=True)
    locality                = Column(String, nullable=True)
    pin_code                = Column(String, nullable=True)
    post_office_id          = Column(Integer, nullable=False)
    post_office_name        = Column(String, nullable=True)
    village_id              = Column(Integer, nullable=False)
    village_name            = Column(String, nullable=True)
    lsg_type_id             = Column(Integer, nullable=False)
    lsg_type                = Column(String, nullable=True)
    lsg_id                  = Column(Integer, nullable=False)
    lsg_name                = Column(String, nullable=True)
    taluk_id                = Column(Integer, nullable=False)
    taluk_name              = Column(String, nullable=True)
    district_id             = Column(Integer, nullable=False)
    district_name           = Column(String, nullable=True)
    state_id                = Column(Integer, nullable=False)
    state_name              = Column(String, nullable=True)
    country_id              = Column(Integer, nullable=False)
    country_name            = Column(String, nullable=True)
    remarks                 = Column(String, nullable=True)
    contact_person_name     = Column(String, nullable=True)
    contact_person_mobile_number     = Column(String, nullable=True)
    contact_person_whatsapp_number   = Column(String, nullable=True)
    contact_person_email_id          = Column(String, nullable=True)
    work_order_status_id             = Column(Integer, nullable=False)
    work_order_status                = Column(String, nullable=True)
    created_by                       = Column(String, nullable=True)
    created_on                       = Column(DateTime, nullable=False)
    modified_by                      = Column(String, nullable=True)
    modified_on                      = Column(DateTime, nullable=True)
    is_deleted                       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                       = Column(String, nullable=True)
    deleted_on                       = Column(DateTime, nullable=True)
    is_locked                        = Column(Enum('yes', 'no'), nullable=False, default='no')  
    locked_on                        = Column(DateTime, nullable=True)
    locked_by                        = Column(String, nullable=True)




class WorkOrderDetailsView(caerp_base):
    __tablename__ = 'off_view_work_order_details'
    
    work_order_details_id   = Column(Integer, primary_key=True, autoincrement=True)
    work_order_master_id    = Column(Integer, nullable=True)
    service_goods_master_id   = Column(Integer, nullable=True)
    service_goods_name        = Column(String, nullable=True)
    constitution_id         = Column(Integer, nullable=True)
    business_constitution_name  = Column(String, nullable=True) 
    trade_name              = Column(String, nullable=True)
    legal_name             = Column(String, nullable=True)
    business_activity_type_id      = Column(Integer, nullable=True)
    business_activity_type         = Column(String, nullable=True)
    business_activity_master_id   = Column(Integer, nullable=True)
    business_activity_master    = Column(String, nullable=True)
    business_activity_id        = Column(Integer, nullable=True)
    business_activity           = Column(String, nullable=True)
    has_branches                = Column(Enum('yes', 'no'), nullable=False, default='no')
    number_of_branches          = Column(Integer, nullable=True)
    has_godowns                 = Column(Enum('yes', 'no'), nullable=False, default='no')
    number_of_godowns           = Column(Integer, nullable=True)
    number_of_directors         = Column(Integer, nullable=True)
    number_of_partners          = Column(Integer, nullable=True)
    number_of_shareholders      = Column(Integer, nullable=True)
    number_of_trustees          = Column(Integer, nullable=True)
    number_of_members           = Column(Integer, nullable=True)
    number_of_authorized_signatory = Column(Integer, nullable=True)
    is_main_service             = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
    bundle_service_id           = Column(Integer, nullable=True)
    is_depended_service         = Column(Enum('yes', 'no'), nullable=False, default='no')
    processing_order            = Column(Integer, nullable=True)
    is_service_required            = Column(Enum('YES', 'NO', 'LATER'), nullable=False, default='YES')
    service_required_date       = Column(Date, nullable=True)
    service_status_id           = Column(Integer, nullable=False)
    service_status           = Column(String, nullable=True)
    file_opened_on              = Column(DateTime, nullable=True)
    file_closed_on              = Column(DateTime, nullable=True)
    rack_number                 = Column(Integer, nullable=True)
    shelf_number                = Column(Integer, nullable=True)
    file_number                 = Column(Integer, nullable=True)
    remarks                     = Column(String, nullable=True)
    created_by                       = Column(String, nullable=False)
    created_on                       = Column(DateTime, nullable=False)
    modified_by                      = Column(String, nullable=True)
    modified_on                      = Column(DateTime, nullable=True)
    is_deleted                       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                       = Column(String, nullable=True)
    deleted_on                       = Column(DateTime, nullable=True)

class WorkOrderBusinessPlaceDetails(caerp_base):
    __tablename__ = 'work_order_business_place_details'
    
    id                      = Column(Integer, primary_key=True, autoincrement=True)        
    work_order_details_id   = Column(Integer, nullable=False) 
    business_place_type     = Column(Enum('MAIN OFFICE','GODOWN','BRANCH'), nullable=False, default='MAIN OFFICE')   
    nature_of_possession_id = Column(Integer, nullable=False) 
    business_place_doc_id   = Column(Integer, nullable=False)
    utility_document_id     = Column(Integer, nullable=False)
    is_deleted              = Column(Enum('yes', 'no'), nullable=False, default='no')


class CustomerDataDocumentMaster(caerp_base):
    __tablename__ = 'customer_data_document_master'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    work_order_master_id    = Column(Integer, nullable=False)
    work_order_details_id   = Column(Integer, nullable=False)
    service_task_id         = Column(Integer, nullable=False)
    document_data_category_id = Column(Integer, nullable=False)
    document_data_master_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=True)
    stake_holder_master_id = Column(Integer, nullable=True)
    is_partner_director_proprietor  = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_authorised_sigantory         = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_business_place               = Column(Enum('yes', 'no'), nullable=False, default='no')
    business_place_type_and_name    = Column(String(100), nullable=True)
    stake_holder_role               = Column(String(100), nullable=True)
    signatory_serial_number         = Column(String(100), nullable=True)
    # data = Column(String(1000), nullable=True)
    display_order = Column(Integer, nullable=False, default=1)
    is_document_uploded = Column(Enum('yes', 'no'), nullable=False, default='no')
    uploaded_date = Column(DateTime, nullable=True)
    uploaded_by = Column(Integer, nullable=True)
    valid_from_date = Column(Date, nullable=True)
    valid_to_date = Column(Date, nullable=True)
    remarks = Column(String(1000), nullable=True)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')



#------------------------------------------SERVICE TASK---------------------------------------------




class OffServiceTaskMaster(caerp_base):
    __tablename__               = 'off_service_task_master'
    id                          = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id           = Column(Integer, nullable=False)
    enquiry_master_id           = Column(Integer, nullable=True)
    enquiry_details_id          = Column(Integer, nullable=True)
    appointment_master_id       = Column(Integer, nullable=True)
    visit_master_id             = Column(Integer, nullable=True)
    
    work_order_master_id        = Column(Integer, nullable=False)
    work_order_details_id       = Column(Integer, nullable=False)
    proforma_invoice_master_id  = Column(Integer, nullable=False)
    proforma_invoice_detail_id  = Column(Integer, nullable = False)
    customer_id                 = Column(Integer, nullable=True)
    task_number                 = Column(String(100), nullable=False)
    allocated_by                = Column(Integer, nullable=False)
    allocated_on                = Column(DateTime, nullable=False)
    department_allocated_on     = Column(DateTime, nullable=False)
    department_allocated_to     = Column(Integer, nullable=False)
    team_allocated_on           = Column(DateTime, nullable=False)
    team_allocated_to           = Column(Integer, nullable=False)
    employee_allocated_on       = Column(DateTime, nullable=False)
    employee_allocated_to       = Column(Integer, nullable=False)
    task_status_id              = Column(Integer, nullable=False)
    task_priority_id            = Column(Integer, nullable=False)
    remarks                     = Column(String(1000), nullable=True)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, nullable=True)
    deleted_on                  = Column(DateTime, nullable=True)
    is_locked                   = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on                   = Column(DateTime, nullable=True)
    locked_by                   = Column(Integer, nullable=True)


class OffServiceTaskHistory(caerp_base):
    __tablename__                = 'off_service_task_history'

    id                           = Column(Integer, primary_key=True, autoincrement=True)
    service_task_master_id       = Column(Integer, nullable=False)
    history_updated_on           = Column(DateTime, nullable=False, default=func.now())
    history_update_by            = Column(Integer, nullable=False)
    history_description          = Column(String(1000), nullable=False)



class OffViewServiceTaskMaster(caerp_base):
    __tablename__ = 'off_view_service_task_master'

    task_id                        = Column(Integer, primary_key=True, autoincrement=True)
    work_order_master_id           = Column(Integer, nullable=False)
    work_order_number              = Column(String, nullable=True)
    work_order_date                = Column(Date, nullable=True)
    work_order_details_id          = Column(Integer, nullable=True)
    financial_year_id              = Column(Integer, nullable=False)
    enquiry_master_id              = Column(Integer, nullable=True)
    enquiry_details_id             = Column(Integer, nullable=True)
    appointment_master_id          = Column(Integer, nullable=True)
    visit_master_id                = Column(Integer, nullable=True)
    constitution_id                = Column(Integer, nullable=True)
    trade_name                     = Column(Integer, nullable=True)
    legal_name                    = Column(Integer, nullable=True)
    service_goods_master_id        = Column(Integer, nullable=False)  
    service_goods_name             = Column(String, nullable=False)   
    group_id                       = Column(Integer, nullable=False)  
    group_name                     = Column(String, nullable=False)   
    sub_group_id                   = Column(Integer, nullable=False)  
    sub_group_name                 = Column(String, nullable=False)   
    category_id                    = Column(Integer, nullable=False)  
    category_name                  = Column(String, nullable=False)   
    sub_category_id                = Column(Integer, nullable=False)  
    sub_category_name              = Column(String, nullable=False)   
    customer_id                    = Column(Integer, nullable=True)
    task_number                    = Column(String, nullable=False)
    allocated_by                   = Column(Integer, nullable=False)
    allocated_by_first_name        = Column(String, nullable=False, default="")
    allocated_by_middle_name       = Column(String, nullable=False, default="")
    allocated_by_last_name         = Column(String, nullable=False, default="")
    allocated_on                   = Column(DateTime, nullable=False)
    department_allocated_on        = Column(DateTime, nullable=True)
    department_allocated_to        = Column(Integer, nullable=True)
    department_name                = Column(String, nullable=False, default="")
    team_allocated_on              = Column(DateTime, nullable=True)
    team_allocated_to              = Column(Integer, nullable=True)
    team_name                      = Column(String, nullable=False, default="")
    employee_allocated_on          = Column(DateTime, nullable=True)
    employee_allocated_to          = Column(Integer, nullable=True)
    employee_allocated_first_name  = Column(String, nullable=False, default="")
    employee_allocated_middle_name = Column(String, nullable=False, default="")
    employee_allocated_last_name   = Column(String, nullable=False, default="")
    task_status_id                 = Column(Integer, nullable=True)
    task_status                    = Column(String, nullable=False, default="")
    task_priority_id               = Column(Integer, nullable=True)
    task_priority                  = Column(String, nullable=False, default="")
    remarks                        = Column(String, nullable=True)
    is_deleted                     = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                     = Column(Integer, nullable=True)
    deleted_on                     = Column(DateTime, nullable=True)
    is_locked                      = Column(Enum('yes', 'no'), nullable=False, default='no')
    locked_on                      = Column(DateTime, nullable=True)
    locked_by                      = Column(Integer, nullable=True)


# class AppHsnSacTaxMaster(caerp_base):
#     __tablename__ = 'app_hsn_sac_tax_master'

#     id                   = Column(Integer, primary_key=True, autoincrement=True)
#     hsn_sac_id           = Column(Integer, nullable=False)
#     gst_rate             = Column(Float, nullable=True)
#     cess_rate            = Column(Float, nullable=True)
#     additional_cess_rate = Column(Float, nullable=True)
#     effective_from_date  = Column(Date, nullable=True)
#     effective_to_date    = Column(Date, nullable=True)
#     is_deleted           = Column(Enum('yes', 'no'), default='no', nullable=False)



class AppHsnSacMaster(caerp_base):
    __tablename__ = 'app_hsn_sac_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_class_id = Column(Integer, nullable=False)
    hsn_sac_code = Column(String(20), unique=True, nullable=False)
    hsn_sac_description = Column(String(2000), default=None)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)



class AppHsnSacTaxMaster(caerp_base):
    __tablename__ = 'app_hsn_sac_tax_master'

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    hsn_sac_id           = Column(Integer, nullable=False)
    gst_rate             = Column(Float, nullable=True)
    cess_rate            = Column(Float, nullable=True)
    additional_cess_rate = Column(Float, nullable=True)
    effective_from_date  = Column(Date, nullable=True)
    effective_to_date    = Column(Date, nullable=True)
    is_deleted           = Column(Enum('yes', 'no'), default='no', nullable=False)



class AppViewHsnSacMaster(caerp_base):
    __tablename__ = 'app_view_hsn_sac_master'
    hsn_sac_master_id      = Column(Integer, primary_key=True)
    hsn_sac_class_id       = Column(Integer, nullable=False)
    hsn_sac_class          = Column(String(100), nullable=False)
    hsn_sac_id             = Column(Integer, nullable=False)
    hsn_sac_code           = Column(String(20), nullable=False)
    hsn_sac_description    = Column(String(2000), nullable=True)
    gst_rate               = Column(Float, default=0.0)
    cess_rate              = Column(Float, default=0.0)
    additional_cess_rate   = Column(Float, default=0.0)
    effective_from_date    = Column(Date, nullable=True)
    effective_to_date      = Column(Date, nullable=True)
    is_deleted             = Column(Enum('yes', 'no'), nullable=False)
    tax_master_id          = Column(Integer, nullable=False)
    



class OffViewCustomerEnquiryAppointmentDetails(caerp_base):
    __tablename__ = "off_view_customer_enquiry_appointment_details"
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False) 
    enquiry_master_id = Column(String(11), nullable=True)
    appointment_master_id = Column(String(11), nullable=True)
    legal_name = Column(String(302), nullable=True)
    customer_id = Column(String(100), nullable=True)
    customer_number = Column(String(100), nullable=True)
    customer_name = Column(String(100), nullable=True)
    mobile_number = Column(String(100), nullable=True)
    whatsapp_number = Column(String(100), nullable=True)
    email_id = Column(String(100), nullable=True)
    address = Column(String(201), nullable=True)
    pin_code = Column(String(50), nullable=True) 
    post_office_id = Column(Integer, nullable=True)
    post_office_name = Column(String(255), nullable=True)
    village_id = Column(String(11), nullable=True) 
    village_name = Column(String(500), nullable=True)
    lsg_type_id = Column(String(11), nullable=True)  
    lsg_type = Column(String(500), nullable=True)
    lsg_id = Column(String(11), nullable=True) 
    lsg_name = Column(String(1000), nullable=True)
    taluk_id = Column(Integer, nullable=True)
    taluk_name = Column(String(50), nullable=True)
    district_id = Column(Integer, nullable=True)
    district_name = Column(String(50), nullable=True)
    state_id = Column(Integer, nullable=True)
    state_name = Column(String(50), nullable=True)

  