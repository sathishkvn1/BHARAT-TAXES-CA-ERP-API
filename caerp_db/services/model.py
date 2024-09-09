
from sqlalchemy import Column, Integer, String,BigInteger,Date,Float,Enum,Time, func
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column ,DateTime




class CustomerMaster(caerp_base):
    __tablename__                = 'customer_master'

    customer_id                             = Column(Integer, primary_key=True, autoincrement=True)
    customer_number                         = Column(String(100), nullable=True)
    legal_name                              = Column(String(100), nullable=True)
    customer_name                           = Column(String(100), nullable=True)
    pan_number                              = Column(String(20), nullable=True)
    pan_creation_date                       = Column(DateTime, nullable=True)
    tan_number                              = Column(String(20), nullable=True)
    passport_number                         = Column(String(20), nullable=True)
    tin_number                              = Column(String(20), nullable=True)
    authorized_signatory_name_as_in_pan     = Column(String(100), nullable=True)
    authorized_signatory_pan_number         = Column(String(20), nullable=True)
    email_address                           = Column(String(100), nullable=True)
    mobile_number                           = Column(String(20), nullable=True)
    constitution_id                         = Column(Integer, nullable=True)
    state_id                                = Column(Integer, nullable=True)
    district_id                             = Column(Integer, nullable=True)
    is_mother_customer                      = Column(Enum('yes', 'no'), nullable=False, default='no')
    has_authorized_signatory                = Column(Enum('yes', 'no'), nullable=False, default='no')
    has_authorized_representative           = Column(Enum('yes', 'no'), nullable=False, default='no')
    created_by                              = Column(Integer, nullable=True)
    created_on                              = Column(DateTime, nullable=True)
    modified_by                             = Column(Integer, nullable=True)
    modified_on                             = Column(DateTime, nullable=True)
    is_deleted                              = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                              = Column(Integer, nullable=True)
    deleted_on                              = Column(DateTime, nullable=True)


class CustomerAdditionalTradeName(caerp_base):
    __tablename__                = 'customer_additional_trade_name'


    id                                = Column(Integer, primary_key=True, autoincrement=True)
    customer_id                       = Column(Integer, nullable=True)
    additional_trade_name             = Column(String(100), nullable=True)
    is_amendment                      = Column(Enum('yes', 'no'), nullable=False, default='no')
    amendment_status                  = Column(Enum('CREATED','UPLOADED','APPROVED','REJECTED'), nullable=False, default='APPROVED')
    amendment_history                 = Column(String(2000), nullable=True)
    effective_from_date               = Column(DateTime, nullable=True)
    effective_to_date                 = Column(DateTime, nullable=True)
    created_by                        = Column(Integer, nullable=True)
    created_on                        = Column(DateTime, nullable=True)
    modified_by                       = Column(Integer, nullable=True)
    modified_on                       = Column(DateTime, nullable=True)
    is_deleted                        = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                        = Column(Integer, nullable=True)
    deleted_on                        = Column(DateTime, nullable=True)

class CustomerGSTLoginCredentials(caerp_base):
    __tablename__ = 'customer_gst_login_credentials'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    customer_id                 = Column(Integer, nullable=False)
    gst_user_name               = Column(String(100), nullable=True)
    gst_password                = Column(String(100), nullable=True)
    gst_trn_number              = Column(String(100), nullable=True)
    gst_arn_number              = Column(String(100), nullable=True)
    trn_effective_from_date     = Column(DateTime, nullable=False)
    trn_effective_to_date       = Column(DateTime, nullable=True)
    login_effective_from_date   = Column(DateTime, nullable=True)
    login_effective_to_date     = Column(DateTime, nullable=True)
    created_by                  = Column(Integer, nullable=True)
    created_on                  = Column(DateTime, nullable=True)
    modified_by                 = Column(Integer, nullable=True)
    modified_on                 = Column(DateTime, nullable=True)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, nullable=True)
    deleted_on                  = Column(DateTime, nullable=True)



class CustomerGSTCasualTaxablePersonDetails(caerp_base):
    __tablename__ = 'customer_gst_casual_taxable_person_details'

    id                                   = Column(Integer, primary_key=True, autoincrement=True)
    customer_id                          = Column(Integer, nullable=False)
    is_applying_as_casual_taxable_person = Column(Enum('yes', 'no'), nullable=False, default='no')
    gst_registration_required_from_date  = Column(DateTime, nullable=True)
    gst_registration_required_to_date    = Column(DateTime, nullable=True)
    estimated_igst_turnover              = Column(Float, nullable=True)
    estimated_net_igst_liability         = Column(Float, nullable=True)
    estimated_cgst_turnover              = Column(Float, nullable=True)
    estimated_net_cgst_liability         = Column(Float, nullable=True)
    estimated_sgst_turnover              = Column(Float, nullable=True)
    estimated_net_sgst_liability         = Column(Float, nullable=True)
    estimated_cess_turnover              = Column(Float, nullable=True)
    estimated_net_cess_liability         = Column(Float, nullable=True)
    is_amendment                         = Column(Enum('yes', 'no'), nullable=False, default='no')
    amendment_status                     = Column(Enum('CREATED', 'UPLOADED', 'APPROVED', 'REJECTED'), nullable=False, default='APPROVED')
    amendment_history                    = Column(String(2000), nullable=True)
    effective_from_date                  = Column(DateTime, nullable=True)
    effective_to_date                    = Column(DateTime, nullable=True)
    created_by                           = Column(Integer, nullable=True)
    created_on                           = Column(DateTime, nullable=True)
    modified_by                          = Column(Integer, nullable=True)
    modified_on                          = Column(DateTime, nullable=True)
    is_deleted                           = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                           = Column(Integer, nullable=True)
    deleted_on                           = Column(DateTime, nullable=True)

class CustomerGSTCompositionOptedPersonDetails(caerp_base):
    __tablename__ = 'customer_gst_composition_opted_person_details'

    id                                        = Column(Integer, primary_key=True, autoincrement=True)
    customer_id                               = Column(Integer, nullable=False)
    is_applying_as_composition_taxable_person = Column(Enum('yes', 'no'), nullable=False, default='no')
    option_1                                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    option_2                                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    option_3                                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_amendment                              = Column(Enum('yes', 'no'), nullable=False, default='no')
    amendment_status                          = Column(Enum('CREATED', 'UPLOADED', 'APPROVED', 'REJECTED'), nullable=False, default='APPROVED')
    amendment_history                         = Column(String(2000), nullable=True)
    effective_from_date                       = Column(DateTime, nullable=True)
    effective_to_date                         = Column(DateTime, nullable=True)
    created_by                                = Column(Integer, nullable=True)
    created_on                                = Column(DateTime, nullable=True)
    modified_by                               = Column(Integer, nullable=True)
    modified_on                               = Column(DateTime, nullable=True)
    is_deleted                                = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                                = Column(Integer, nullable=True)
    deleted_on                                = Column(DateTime, nullable=True)


class CustomerGSTOtherDetails(caerp_base):
    __tablename__ = 'customer_gst_other_details'

    id                                   = Column(Integer, primary_key=True, autoincrement=True)
    customer_id                          = Column(Integer, nullable=False)
    reason_to_obtain_gst_registration_id = Column(Integer, nullable=False)
    commencement_of_business_date        = Column(DateTime, nullable=False)
    liability_to_register_arises_date    = Column(DateTime, nullable=True)
    is_amendment                         = Column(Enum('yes', 'no'), nullable=False, default='no')
    amendment_status                     = Column(Enum('CREATED', 'UPLOADED', 'APPROVED', 'REJECTED'), nullable=False, default='APPROVED')
    amendment_history                    = Column(String(2000), nullable=True)
    effective_from_date                  = Column(DateTime, nullable=True)
    effective_to_date                    = Column(DateTime, nullable=True)
    created_by                           = Column(Integer, nullable=True)
    created_on                           = Column(DateTime, nullable=True)
    modified_by                          = Column(Integer, nullable=True)
    modified_on                          = Column(DateTime, nullable=True)
    is_deleted                           = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                           = Column(Integer, nullable=True)
    deleted_on                           = Column(DateTime, nullable=True)


class CustomerExistingRegistrationDetails(caerp_base):
    __tablename__ = 'customer_existing_registration_details'

    id                               = Column(Integer, primary_key=True, autoincrement=True)
    customer_id                      = Column(Integer, nullable=False)
    registration_type_id             = Column(Integer, nullable=False)
    other_registration               = Column(String(100), nullable=True)
    registration_number              = Column(String(100), nullable=False)
    registration_date                = Column(DateTime, nullable=False)
    is_amendment                     = Column(Enum('yes', 'no'), nullable=False, default='no')
    amendment_status                 = Column(Enum('CREATED', 'UPLOADED', 'APPROVED', 'REJECTED'), nullable=False, default='APPROVED')
    amendment_history                = Column(String(2000), nullable=True)
    effective_from_date              = Column(DateTime, nullable=True)
    effective_to_date                = Column(DateTime, nullable=True)
    created_by                       = Column(Integer, nullable=True)
    created_on                       = Column(DateTime, nullable=True)
    modified_by                      = Column(Integer, nullable=True)
    modified_on                      = Column(DateTime, nullable=True)
    is_deleted                       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                       = Column(Integer, nullable=True)
    deleted_on                       = Column(DateTime, nullable=True)


class CustomerDocuments(caerp_base):
    __tablename__ = 'customer_documents'

    id                               = Column(Integer, primary_key=True, autoincrement=True)
    customer_master_id               = Column(Integer, nullable=False)
    document_id                      = Column(Integer, nullable=False)
    document_type                    = Column(Enum('AUTHORIZED_SIGNATORY_DOC', 'AUTHORIZED_REPRESENTATIVE_DOC', 'BUSINESS_PLACE_DOC', 'STAKE_HOLDER_DOC'), nullable=False)
    is_amendment                     = Column(Enum('yes', 'no'), nullable=False, default='no')
    amendment_status                 = Column(Enum('CREATED', 'UPLOADED', 'APPROVED', 'REJECTED'), nullable=False, default='APPROVED')
    amendment_history                = Column(String(2000), nullable=True)
    effective_from_date              = Column(Date, nullable=True)
    effective_to_date                = Column(Date, nullable=True)
    created_by                       = Column(Integer, nullable=True)
    created_on                       = Column(Date, nullable=True)
    modified_by                      = Column(Integer, nullable=True)
    modified_on                      = Column(Date, nullable=True)
    is_deleted                       = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                       = Column(Integer, nullable=True)
    deleted_on                       = Column(Date, nullable=True)


#------
class GstReasonToObtainRegistration(caerp_base):
    __tablename__ = 'gst_reason_to_obtain_registration'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    reason_code = Column(String(10), nullable=False)
    reason      = Column(String(100), nullable=False)
    is_deleted  = Column(Enum('yes', 'no'), nullable=False, default='no')


class GstTypeOfRegistration(caerp_base):
    __tablename__ = 'gst_type_of_registration'

    id                        = Column(Integer, primary_key=True, autoincrement=True)
    type_of_registration_code = Column(String(10), nullable=False)
    type_of_registration      = Column(String(200), nullable=False)
    is_deleted                = Column(Enum('yes', 'no'), nullable=False, default='no')