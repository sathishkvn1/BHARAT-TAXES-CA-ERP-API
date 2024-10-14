from caerp_db.database import caerp_base
from sqlalchemy import Column, DateTime, Integer, String,Date,Float,Enum,Time, func




class AccQuotationMaster(caerp_base):
    __tablename__ = 'acc_quotation_master'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id       = Column(Integer, nullable=False)
    work_order_master_id    = Column(Integer, nullable=True)
    quotation_version       = Column(Integer, nullable=True)
    quotation_date          = Column(Date, nullable=True)
    quotation_number        = Column(String(50), nullable=True)
    total_offer_amount             = Column(Float, nullable=True)
    total_coupon_amount            = Column(Float, nullable=True)

    bill_discount_amount           = Column(Float, nullable=True)
    additional_discount_amount     = Column(Float, nullable=True)

    grand_total_amount         = Column(Float, nullable=True)
    round_off_amount           = Column(Float, nullable=True)
    net_amount          = Column(Float, nullable=True)
    remarks             = Column(String(50), nullable=True)
    quotation_status_id    = Column(Integer, nullable=False)
    is_final_quotation  = Column(Enum('yes','no'), nullable = False, default='no') 

    created_by          = Column(Integer, nullable=True)
    created_on          = Column(Date, nullable=True)
    modified_by         = Column(Integer, nullable=True)
    modified_on         = Column(Date, nullable=True)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by          = Column(Integer, nullable=True)
    deleted_on          = Column(Date, nullable=True)
    is_locked           = Column(Enum('yes', 'no'), nullable=False, default='no')  
    locked_on           = Column(DateTime, nullable=True)
    locked_by           = Column(String, nullable=True)


class AccQuotationDetails(caerp_base):
    __tablename__ = 'acc_quotation_details'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    quotation_master_id         = Column(Integer, nullable=True)
    service_goods_master_id     = Column(Integer, nullable=True)
    hsn_sac_code                = Column(String(50), nullable=True)
    is_main_service             = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
    bundle_service_id           = Column(Integer, nullable=True)
    service_charge              = Column(Float, nullable=True)
    govt_agency_fee             = Column(Float, nullable=True)
    stamp_duty                  = Column(Float, nullable=True)
    stamp_fee                   = Column(Float, nullable=True)
    quantity                    = Column(Float, nullable=True)

    has_offer                   = Column(Enum('yes', 'no'), nullable=False, default='no')
    offer_name                  = Column(String(50), nullable=True)
    offer_percentage            = Column(Float, nullable=False,default=0.0)
    offer_amount                = Column(Float, nullable=False,default=0.0) 

    has_coupon                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    coupon_code                 = Column(String(50), nullable=True)
    coupon_percentage           = Column(Float, nullable=True)
    coupon_amount               = Column(Float, nullable=True)

    discount_percentage         = Column(Float, nullable=True)
    discount_amount             = Column(Float, nullable=False,default=0.0)
    additional_discount_percentage      = Column(Float, nullable=False,default=0.0)  
    additional_discount_amount          = Column(Float, nullable=False,default=0.0)
    
    taxable_amount              = Column(Float, nullable=False,default=0.0)
    igst_percent                = Column(Float, nullable=False,default=0.0)
    igst_amount                 = Column(Float, nullable=False,default=0.0)
    cgst_percent                = Column(Float, nullable=False,default=0.0)
    cgst_amount                 = Column(Float, nullable=False,default=0.0)
    sgst_percent                = Column(Float, nullable=False,default=0.0)
    sgst_amount                 = Column(Float, nullable=False,default=0.0)
    cess_percent                = Column(Float, nullable=False,default=0.0)
    cess_amount                 = Column(Float, nullable=False,default=0.0)
    additional_cess_percent     = Column(Float, nullable=False,default=0.0)
    additional_cess_amount      = Column(Float, nullable=False,default=0.0)

    total_amount                = Column(Float, nullable=False,default=0.0)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
     

class AccProformaInvoiceStatus(caerp_base):
    __tablename__ = 'acc_proforma_invoice_status'

    id                              = Column(Integer, primary_key=True, autoincrement=True)
    proforma_invoice_status         = Column(String, nullable=False)
    is_deleted                      = Column(Enum('yes', 'no'), nullable=False, default='no')


class AccVoucherId(caerp_base):
    __tablename__ = 'acc_voucher_id'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    voucher_id           = Column(Integer, nullable=False)



#------------------------------------------------------------------------------
class AccProformaInvoiceMaster(caerp_base):
    __tablename__ = 'acc_proforma_invoice_master'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id           = Column(Integer, nullable=False)
    voucher_id                  = Column(Integer, nullable=False)
    service_type                = Column(Enum('CONSULTATION', 'NON_CONSULTATION', 'GOODS'), nullable=False, default='no' )

    appointment_master_id       = Column(Integer, nullable=True)
    visit_master_id             = Column(Integer, nullable=True)

    work_order_master_id        = Column(Integer, nullable=True)

    proforma_invoice_date       = Column(Date, nullable=True)
    proforma_invoice_number     = Column(String(50), nullable=True)
    account_head_id             = Column(Integer, nullable=True)
    total_offer_amount          = Column(Float, nullable=False,default=0.0)
    total_coupon_amount         = Column(Float, nullable=False,default=0.0)

    grand_total_amount                = Column(Float, nullable=False,default=0.0)
    bill_discount_amount             = Column(Float, nullable=False,default=0.0)
    additional_discount_amount  = Column(Float, nullable=False,default=0.0)
    advance_amount              = Column(Float, nullable=False,default=0.0)
    round_off_amount            = Column(Float, nullable=False,default=0.0)
    net_amount                 = Column(Float, nullable=False,default=0.0)
    remarks                     = Column(String(50), nullable=True)
    proforma_invoice_status_id  = Column(Integer, nullable=False)

    created_by          = Column(Integer, nullable=False)
    created_on          = Column(DateTime, nullable=False, default=func.now())
    modified_by         = Column(Integer, nullable=True)
    modified_on         = Column(Date, nullable=True)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by          = Column(Integer, nullable=True)
    deleted_on          = Column(Date, nullable=True)
    is_locked                        = Column(Enum('yes', 'no'), nullable=False, default='no')  
    locked_on                        = Column(DateTime, nullable=True)
    locked_by                        = Column(String, nullable=True)


# class AccProformaInvoiceDetails(caerp_base):
#     __tablename__ = 'acc_proforma_invoice_details'

#     id                          = Column(Integer, primary_key=True, autoincrement=True)
#     proforma_invoice_master_id  = Column(Integer, nullable=False)
#     service_goods_master_id     = Column(Integer, nullable=False)
#     is_main_service             = Column(Enum('yes', 'no'), nullable=False, default='no')
#     is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
#     bundle_service_id           = Column(Integer, nullable=True)
#     service_charge              = Column(Float, nullable=False, default=0.0)
#     govt_agency_fee             = Column(Float, nullable=False, default=0.0)
#     stamp_duty                  = Column(Float, nullable=False, default=0.0)
#     stamp_fee                   = Column(Float, nullable=False, default=0.0)
#     quantity                    = Column(Integer, nullable=False, default=1.0)

#     has_offer                   = Column(Enum('yes', 'no'), nullable=False, default='no')
#     offer_name                  = Column(String(50), nullable=True)
#     offer_percentage            = Column(Float, nullable=False, default=0.0)
#     offer_amount                = Column(Float, nullable=False, default=0.0)
    
#     has_coupon                  = Column(Enum('yes', 'no'), nullable=False, default='no')
#     coupon_code                 = Column(String(50), nullable=True)
#     coupon_percentage           = Column(Float, nullable=False, default=0.0)
#     coupon_amount               = Column(Float, nullable=False, default=0.0)

#     discount_percentage         = Column(Float, nullable=False, default=0.0)
#     discount_amount             = Column(Float, nullable=False, default=0.0)

#     additional_discount_percentage      = Column(Float, nullable=False,default=0.0)  
#     additional_discount_amount          = Column(Float, nullable=False,default=0.0)
    
#     taxable_amount              = Column(Float, nullable=False,default=0.0)
#     igst_percent                = Column(Float, nullable=False,default=0.0)
#     igst_amount                 = Column(Float, nullable=False,default=0.0)
#     cgst_percent                = Column(Float, nullable=False,default=0.0)
#     cgst_amount                 = Column(Float, nullable=False,default=0.0)
#     sgst_percent                = Column(Float, nullable=False,default=0.0)
#     sgst_amount                 = Column(Float, nullable=False,default=0.0)
#     cess_percent                = Column(Float, nullable=False,default=0.0)
#     cess_amount                 = Column(Float, nullable=False,default=0.0)
#     additional_cess_percent     = Column(Float, nullable=False,default=0.0)
#     additional_cess_amount      = Column(Float, nullable=False,default=0.0)

#     total_amount                = Column(Float, nullable=False, default=0.0)
#     is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')


class AccProformaInvoiceDetails(caerp_base):
    __tablename__ = 'acc_proforma_invoice_details'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    proforma_invoice_master_id  = Column(Integer, nullable=False)
    service_goods_master_id     = Column(Integer, nullable=False)
    hsn_sac_code                = Column(String(50), nullable=True)
    is_main_service             = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
    bundle_service_id           = Column(Integer, nullable=True)
    service_charge              = Column(Float, nullable=False, default=0.0)
    govt_agency_fee             = Column(Float, nullable=False, default=0.0)
    stamp_duty                  = Column(Float, nullable=False, default=0.0)
    stamp_fee                   = Column(Float, nullable=False, default=0.0)
    quantity                    = Column(Integer, nullable=False, default=1.0)

    has_offer                   = Column(Enum('yes', 'no'), nullable=False, default='no')
    offer_name                  = Column(String(50), nullable=True)
    offer_percentage            = Column(Float, nullable=False, default=0.0)
    offer_amount                = Column(Float, nullable=False, default=0.0)
    
    has_coupon                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    coupon_code                 = Column(String(50), nullable=True)
    coupon_percentage           = Column(Float, nullable=False, default=0.0)
    coupon_amount               = Column(Float, nullable=False, default=0.0)

    discount_percentage         = Column(Float, nullable=False, default=0.0)
    discount_amount             = Column(Float, nullable=False, default=0.0)

    additional_discount_percentage      = Column(Float, nullable=False,default=0.0)  
    additional_discount_amount          = Column(Float, nullable=False,default=0.0)
    
    taxable_amount              = Column(Float, nullable=False,default=0.0)
    igst_percent                = Column(Float, nullable=False,default=0.0)
    igst_amount                 = Column(Float, nullable=False,default=0.0)
    cgst_percent                = Column(Float, nullable=False,default=0.0)
    cgst_amount                 = Column(Float, nullable=False,default=0.0)
    sgst_percent                = Column(Float, nullable=False,default=0.0)
    sgst_amount                 = Column(Float, nullable=False,default=0.0)
    cess_percent                = Column(Float, nullable=False,default=0.0)
    cess_amount                 = Column(Float, nullable=False,default=0.0)
    additional_cess_percent     = Column(Float, nullable=False,default=0.0)
    additional_cess_amount      = Column(Float, nullable=False,default=0.0)

    total_amount                = Column(Float, nullable=False, default=0.0)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')


class AccTaxInvoiceStatus(caerp_base):
    __tablename__ = 'acc_tax_invoice_status'

    id                         = Column(Integer, primary_key=True, autoincrement=True)
    tax_invoice_status         = Column(String, nullable=False)
    is_deleted                 = Column(Enum('yes', 'no'), nullable=False, default='no')



class AccTaxInvoiceMaster(caerp_base):
    __tablename__ = 'acc_tax_invoice_master'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id           = Column(Integer, nullable=False)
    voucher_id                  = Column(Integer, nullable=False)
    service_type                = Column(Enum('CONSULTATION', 'NON_CONSULTATION', 'GOODS'), nullable=False, default='no' )

    appointment_master_id       = Column(Integer, nullable=True)
    visit_master_id             = Column(Integer, nullable=True)

    work_order_master_id        = Column(Integer, nullable=True)

    tax_invoice_date            = Column(Date, nullable=True)
    tax_invoice_number          = Column(String(50), nullable=True)
    account_head_id             = Column(Integer, nullable=True)
    total_offer_amount          = Column(Float, nullable=False,default=0.0)

    total_coupon_amount         = Column(Float, nullable=False,default=0.0)


    grand_total_amount          = Column(Float, nullable=False,default=0.0)
    bill_discount_amount        = Column(Float, nullable=False,default=0.0)
    additional_discount_amount  = Column(Float, nullable=False,default=0.0)
    advance_amount              = Column(Float, nullable=False,default=0.0)
    additional_fee_amount       = Column(Float, nullable=False,default=0.0)
    round_off_amount            = Column(Float, nullable=False,default=0.0)
    net_amount                  = Column(Float, nullable=False,default=0.0)
    remarks                     = Column(String(50), nullable=True)
    tax_invoice_status_id       = Column(String, nullable= False)

    created_by          = Column(Integer, nullable=False)
    created_on          = Column(DateTime, nullable=False, default=func.now())
    modified_by         = Column(Integer, nullable=True)
    modified_on         = Column(Date, nullable=True)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by          = Column(Integer, nullable=True)
    deleted_on          = Column(Date, nullable=True)
    is_locked                        = Column(Enum('yes', 'no'), nullable=False, default='no')  
    locked_on                        = Column(DateTime, nullable=True)
    locked_by                        = Column(String, nullable=True)



# class AccTaxInvoiceDetails(caerp_base):
#     __tablename__ = 'acc_tax_invoice_details'

#     id                          = Column(Integer, primary_key=True, autoincrement=True)
#     tax_invoice_master_id  = Column(Integer, nullable=False)
#     service_goods_master_id     = Column(Integer, nullable=False)
#     is_main_service             = Column(Enum('yes', 'no'), nullable=False, default='no')
#     is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
#     bundle_service_id           = Column(Integer, nullable=True)
#     service_charge              = Column(Float, nullable=False, default=0.0)
#     govt_agency_fee             = Column(Float, nullable=False, default=0.0)
#     stamp_duty                  = Column(Float, nullable=False, default=0.0)
#     stamp_fee                   = Column(Float, nullable=False, default=0.0)
#     quantity                    = Column(Integer, nullable=False, default=1.0)

#     has_offer                   = Column(Enum('yes', 'no'), nullable=False, default='no')
#     offer_name                  = Column(String(50), nullable=True)
#     offer_percentage            = Column(Float, nullable=False, default=0.0)
#     offer_amount                = Column(Float, nullable=False, default=0.0)

#     has_coupon                  = Column(Enum('yes', 'no'), nullable=False, default='no')
#     coupon_code                 = Column(String(50), nullable=True)
#     coupon_percentage           = Column(Float, nullable=False, default=0.0)
#     coupon_amount               = Column(Float, nullable=False, default=0.0)

#     discount_percentage         = Column(Float, nullable=False, default=0.0)
#     discount_amount             = Column(Float, nullable=False, default=0.0)
#     additional_discount_percentage      = Column(Float, nullable=False,default=0.0)  
#     additional_discount_amount          = Column(Float, nullable=False,default=0.0)
    
#     taxable_amount              = Column(Float, nullable=False,default=0.0)
#     igst_percent                = Column(Float, nullable=False,default=0.0)
#     igst_amount                 = Column(Float, nullable=False,default=0.0)
#     cgst_percent                = Column(Float, nullable=False,default=0.0)
#     cgst_amount                 = Column(Float, nullable=False,default=0.0)
#     sgst_percent                = Column(Float, nullable=False,default=0.0)
#     sgst_amount                 = Column(Float, nullable=False,default=0.0)
#     cess_percent                = Column(Float, nullable=False,default=0.0)
#     cess_amount                 = Column(Float, nullable=False,default=0.0)
#     additional_cess_percent     = Column(Float, nullable=False,default=0.0)
#     additional_cess_amount      = Column(Float, nullable=False,default=0.0)
#     total_amount                = Column(Float, nullable=False, default=0.0)
#     is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')

class AccTaxInvoiceDetails(caerp_base):
    __tablename__ = 'acc_tax_invoice_details'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    tax_invoice_master_id  = Column(Integer, nullable=False)
    service_goods_master_id     = Column(Integer, nullable=False)
    hsn_sac_code                = Column(String(50), nullable=True)
    is_main_service             = Column(Enum('yes', 'no'), nullable=False, default='no')
    is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
    bundle_service_id           = Column(Integer, nullable=True)
    service_charge              = Column(Float, nullable=False, default=0.0)
    govt_agency_fee             = Column(Float, nullable=False, default=0.0)
    stamp_duty                  = Column(Float, nullable=False, default=0.0)
    stamp_fee                   = Column(Float, nullable=False, default=0.0)
    quantity                    = Column(Integer, nullable=False, default=1.0)

    has_offer                   = Column(Enum('yes', 'no'), nullable=False, default='no')
    offer_name                  = Column(String(50), nullable=True)
    offer_percentage            = Column(Float, nullable=False, default=0.0)
    offer_amount                = Column(Float, nullable=False, default=0.0)

    has_coupon                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    coupon_code                 = Column(String(50), nullable=True)
    coupon_percentage           = Column(Float, nullable=False, default=0.0)
    coupon_amount               = Column(Float, nullable=False, default=0.0)

    discount_percentage         = Column(Float, nullable=False, default=0.0)
    discount_amount             = Column(Float, nullable=False, default=0.0)
    additional_discount_percentage      = Column(Float, nullable=False,default=0.0)  
    additional_discount_amount          = Column(Float, nullable=False,default=0.0)
    
    taxable_amount              = Column(Float, nullable=False,default=0.0)
    igst_percent                = Column(Float, nullable=False,default=0.0)
    igst_amount                 = Column(Float, nullable=False,default=0.0)
    cgst_percent                = Column(Float, nullable=False,default=0.0)
    cgst_amount                 = Column(Float, nullable=False,default=0.0)
    sgst_percent                = Column(Float, nullable=False,default=0.0)
    sgst_amount                 = Column(Float, nullable=False,default=0.0)
    cess_percent                = Column(Float, nullable=False,default=0.0)
    cess_amount                 = Column(Float, nullable=False,default=0.0)
    additional_cess_percent     = Column(Float, nullable=False,default=0.0)
    additional_cess_amount      = Column(Float, nullable=False,default=0.0)
    total_amount                = Column(Float, nullable=False, default=0.0)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')



class AccQuotationStatus(caerp_base):
    __tablename__ = 'acc_quotation_status'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    quotation_status            = Column(String, nullable=False)
    is_deleted                   = Column(Enum('yes', 'no'), nullable=False, default='no')


class AccQuotationMasterView(caerp_base):
    __tablename__ = 'off_view_quotation_master'

    quotation_master_id     = Column(Integer, primary_key=True, autoincrement=True)
    financial_year_id       = Column(Integer, nullable=False)
    financial_year          = Column(String(50), nullable=True)
    year_begin_date         = Column(Date, nullable=True)
    year_end_date           = Column(Date, nullable=True)
    work_order_master_id    = Column(Integer, nullable=True)
    quotation_version       = Column(Integer, nullable=True)
    quotation_date          = Column(Date, nullable=True)
    quotation_number        = Column(String(50), nullable=True)
    total_offer_amount             = Column(Float, nullable=True)
    total_coupon_amount            = Column(Float, nullable=True)

    bill_discount_amount           = Column(Float, nullable=True)
    additional_discount_amount     = Column(Float, nullable=True)

    grand_total_amount             = Column(Float, nullable=True)
    round_off_amount               = Column(Float, nullable=True)
    net_amount                     = Column(Float, nullable=True)
    quotation_status_id            = Column(Integer, nullable=False)
    quotation_status               = Column(String(50), nullable= False)
    is_final_quotation             = Column(Enum('yes','no'), nullable = False, default='no') 
    enquiry_master_id           = Column(Integer, nullable=True)
    enquiry_details_id          = Column(Integer, nullable=True)
    appointment_master_id       = Column(Integer, nullable=True)
    visit_master_id             = Column(Integer, nullable=True)

    work_order_number           = Column(String(100),nullable=True)
    work_order_date             = Column(Date, nullable=True)
    first_name                  = Column(String(100),nullable=False)
    middle_name                 = Column(String(100),nullable=False)
    last_name                   = Column(String(100),nullable=False)
    gender_id                   = Column(Integer, nullable=False)
    gender                      = Column(Date, nullable=False)
    date_of_birth               = Column(String(100),nullable=False)
    mobile_number               = Column(String(100),nullable=True)
    whatsapp_number             = Column(String(100),nullable=True)
    email_id                    = Column(String(100),nullable=True)
    house_or_building_name      = Column(String(100),nullable=True)
    road_or_street_name         = Column(String(100),nullable=True)
    locality                    = Column(String(100),nullable=True)
    pin_code                    = Column(String(100),nullable=True)
    post_office_id              = Column(Integer, nullable=True)
    post_office_name            = Column(String(100),nullable=True)
    village_id                  = Column(Integer, nullable=True)
    village_name                = Column(String(100),nullable=True)
    lsg_type_id                 = Column(Integer, nullable=True)
    lsg_type                    = Column(String(100),nullable=True)
    lsg_id                      = Column(Integer, nullable=True)
    lsg_name                    = Column(String(100),nullable=True)
    taluk_id                    = Column(Integer, nullable=True)
    taluk_name                  = Column(String(100),nullable=True)
    district_id                 = Column(Integer, nullable=True)
    district_name               = Column(String(100),nullable=True)
    state_id                    = Column(Integer, nullable=True)
    state_name                  = Column(String(100),nullable=True)
    country_id                  = Column(Integer, nullable=True)
    country_name                = Column(String(100),nullable=True)
    work_order_remarks          = Column(String(100),nullable=True)
    contact_person_name         = Column(String(100),nullable=True)
    contact_person_mobile_number    = Column(String(100),nullable=True)
    contact_person_whatsapp_number  = Column(String(100),nullable=True)
    contact_person_email_id         = Column(String(100), nullable=True)
    work_order_status_id            = Column(Integer, nullable=True)
    work_order_status               = Column(String(100), nullable=True)



    created_by          = Column(Integer, nullable=True)
    created_on          = Column(Date, nullable=True)
    modified_by         = Column(Integer, nullable=True)
    modified_on         = Column(Date, nullable=True)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by          = Column(Integer, nullable=True)
    deleted_on          = Column(Date, nullable=True)
    is_locked           = Column(Enum('yes', 'no'), nullable=False, default='no')  
    locked_on           = Column(DateTime, nullable=True)
    locked_by           = Column(String(100), nullable=True)

