from caerp_db.database import caerp_base
from sqlalchemy import Column, Integer, String,Date,Float,Enum,Time, func


class AccQuotationMaster(caerp_base):
    __tablename__ = 'acc_quotation_master'

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    work_order_master_id    = Column(Integer, nullable=True)
    quotation_version       = Column(Integer, nullable=True)
    quotation_date          = Column(Date, nullable=True)
    quotation_number        = Column(String(50), nullable=True)
    offer_total             = Column(Float, nullable=True)

    coupon_total            = Column(Float, nullable=True)

    product_discount_total  = Column(Float, nullable=True)
    bill_discount           = Column(Float, nullable=True)
    additional_discount     = Column(Float, nullable=True)

    grand_total         = Column(Float, nullable=True)
    round_off           = Column(Float, nullable=True)
    net_amount          = Column(Float, nullable=True)
    remarks             = Column(String(50), nullable=True)
    quotation_status    = Column(Enum('DRAFT', 'ACCEPTED','SENT','REQUESTED REVISION'), nullable=False, default='DRAFT')
    is_final_quotation  = Column(Enum('yes','no'), nullable = False, default='no') 

    created_by          = Column(Integer, nullable=True)
    created_on          = Column(Date, nullable=True)
    modified_by         = Column(Integer, nullable=True)
    modified_on         = Column(Date, nullable=True)
    is_deleted          = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by          = Column(Integer, nullable=True)
    deleted_on          = Column(Date, nullable=True)

class AccQuotationDetails(caerp_base):
    __tablename__ = 'acc_quotation_details'

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    quotation_master_id         = Column(Integer, nullable=True)
    service_goods_master_id     = Column(Integer, nullable=True)
    hsn_sac_code                = Column(String(50), nullable=True)
    is_bundle_service           = Column(Enum('yes', 'no'), nullable=False, default='no')
    bundle_service_id           = Column(Integer, nullable=True)
    service_charge              = Column(Float, nullable=True)
    govt_agency_fee             = Column(Float, nullable=True)
    stamp_duty                  = Column(Float, nullable=True)
    stamp_fee                   = Column(Float, nullable=True)
    quantity                    = Column(Float, nullable=True)

    has_offer                   = Column(Enum('yes', 'no'), nullable=False, default='no')
    offer_name                  = Column(String(50), nullable=True)
    offer_percentage            = Column(Float, nullable=True)
    offer_amount                = Column(Float, nullable=True) 

    has_coupon                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    coupon_code                 = Column(String(50), nullable=True)
    coupon_percentage           = Column(Float, nullable=True)
    coupon_amount               = Column(Float, nullable=True)

    discount_percentage         = Column(Float, nullable=True)
    discount_amount             = Column(Float, nullable=True)

    gst_percent                 = Column(Float, nullable=True)
    gst_amount                  = Column(Float, nullable=True)
    taxable_amount              = Column(Float, nullable=True)
    total_amount                = Column(Float, nullable=True)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    