from enum import Enum
from pydantic import BaseModel
from typing import List,Optional
from datetime import date, datetime
from caerp_schema.office.office_schema import OffWorkOrderMasterSchema,OffViewWorkOrderDetailsSchema,OffViewWorkOrderMasterSchema


class AccQuotationMasterSchema(BaseModel):

    id                      : Optional[int] = None
    work_order_master_id    : Optional[int] = None
    quotation_version       : Optional[int] = None
    quotation_date          : Optional[date] = None
    quotation_number        : Optional[str] = None

    offer_total             : Optional[float] = None

    coupon_total            : Optional[float] = None
    # product_discount_total  : Optional[float] = None
    bill_discount           : Optional[float] = None
    additional_discount     : Optional[float] = None

    grand_total             : Optional[float] = None
    round_off               : Optional[float] = None
    net_amount              : Optional[float] = None
    remarks                 : Optional[str] = None
    quotation_status        : Optional[str] = 'DRAFT'
    is_final_quotation      : Optional[str] = 'no'



class AccQuotationDetailsSchema(BaseModel):

    id                           : Optional[int] = None
    quotation_master_id          : Optional[int] = None
    service_goods_master_id      : Optional[int] = None
    service_goods_name           : Optional[str] = None
    hsn_sac_code                 : Optional[str] = None
    is_main_service              : Optional[str] = 'no'   
    is_bundle_service            : Optional[str] = 'no'
    bundle_service_id            : Optional[int] = None
    service_charge               : Optional[float] = None
    govt_agency_fee              : Optional[float] = None
    stamp_duty                   : Optional[float] = None
    stamp_fee                    : Optional[float] = None
    quantity                     : Optional[float] = None

    has_offer                    : Optional[str] = 'no'
    offer_name                   : Optional[str] = None
    offer_percentage             : Optional[float] = None
    offer_amount                 : Optional[float] = None

    has_coupon                   : Optional[str] = 'no'
    coupon_code                  : Optional[str] = None
    coupon_percentage            : Optional[float] = None
    coupon_amount                : Optional[float] = None

    discount_percentage          : Optional[float] = None
    discount_amount              : Optional[float] = None

    gst_percent                  : Optional[float] = None
    gst_amount                   : Optional[float] = None
    taxable_amount               : Optional[float] = None
    total_amount                 : Optional[float] = None
    # service_required             : Optional[str] = 'YES'
    # service_required_date        : Optional[date] = None
    is_deleted                   : Optional[str] = 'no'

class AccQuotationSchema(BaseModel):
    quotation_master            : AccQuotationMasterSchema
    quotation_details           : List[AccQuotationDetailsSchema]

class AccQuotationResponseSchema(BaseModel):
    work_order_master : OffViewWorkOrderMasterSchema
    quotation_master : AccQuotationMasterSchema
    quotation_details : List[AccQuotationDetailsSchema]


class AccProformaInvoiceMasterSchema(BaseModel):

    id                      : Optional[int]= None
    voucher_id              : Optional[int]= None
    service_type            : Optional[str]= 'NON_CONSULTATION'

    appointment_master_id   : Optional[int]= None
    visit_master_id         : Optional[int]= None

    work_order_master_id    : Optional[int]= None

    proforma_invoice_date            : Optional[date]= None
    proforma_invoice_number          : Optional[str]= None
    account_head_id         : Optional[int]= None
    total_offer_amount          : Optional[float]= None

    total_coupon_amount         :  Optional[float]= None


    grand_total_amount           : Optional[float]= None
    bill_discount_amount         : Optional[float]= None
    additional_discount_amount  : Optional[float]= None
    advance_amount              : Optional[float]= None
    round_off_amount            : Optional[float]= None
    net_amount                 : Optional[float]= None
    remarks                     : Optional[str]= None


class AccProformaInvoiceDetailsSchema(BaseModel):

    id                           : Optional[int]= None
    proforma_invoice_master_id           : Optional[int]= None
    service_goods_master_id     : Optional[int]= None
    service_goods_name          : Optional[str] =None
    is_main_service             : Optional[str] = 'no'
    is_bundle_service           : Optional[str]= 'no'
    bundle_service_id           : Optional[int]= None
    service_charge              : Optional[float]= None
    govt_agency_fee             : Optional[float]= None
    stamp_duty                  : Optional[float]= None
    stamp_fee                   : Optional[float]= None
    quantity                    : Optional[int]= None

    offer_master_id             : Optional[int]= None
    offer_name                  : Optional[str]= None
    offer_percentage            : Optional[float]= None
    offer_amount                : Optional[float]= None

    discount_percentage         : Optional[float]= None
    discount_amount             : Optional[float]= None

    gst_percent                 : Optional[float]= None
    gst_amount                  : Optional[float]= None
    taxable_amount              : Optional[float]= None
    total_amount                : Optional[float]= None
    is_deleted                  : Optional[str]= None

# class AccProformaInvoiceShema(BaseModel):
#     invoice_master          : AccProformaInvoiceMasterSchema
#     invoice_details         : List[AccProformaInvoiceDetailsSchema]

class AccProformaInvoiceShema(BaseModel):
    proforma_invoice_master : AccProformaInvoiceMasterSchema
    proforma_invoice_details : List[AccProformaInvoiceDetailsSchema]


class AccInvoiceResponceSchema(BaseModel):
    work_order_master       : OffViewWorkOrderMasterSchema
    invoice_master          : AccProformaInvoiceMasterSchema
    invoice_details         : List[AccProformaInvoiceDetailsSchema]


class AccProformaInvoiceResponceSchema(BaseModel):
    work_order_master : OffViewWorkOrderMasterSchema
    proforma_invoice_master : AccProformaInvoiceMasterSchema
    proforma_invoice_details : List[AccProformaInvoiceDetailsSchema]
    

#----------------------------------------------------------------------------



class AccTaxInvoiceMasterSchema(BaseModel):

    id                      : Optional[int]= None
    voucher_id              : Optional[int]= None
    service_type            : Optional[str]= 'NON_CONSULTATION'

    appointment_master_id   : Optional[int]= None
    visit_master_id         : Optional[int]= None

    work_order_master_id    : Optional[int]= None

    tax_invoice_date            : Optional[date]= None
    tax_invoice_number          : Optional[str]= None
    account_head_id         : Optional[int]= None
    offer_total             : Optional[float] = None

    coupon_total            : Optional[float] = None
    grand_total_amount            : Optional[float]= None
    bill_discount_amount         : Optional[float]= None
    additional_discount_amount  : Optional[float]= None
    advance_amount              : Optional[float]= None
    round_off_amount            : Optional[float]= None
    net_amount                 : Optional[float]= None
    remarks                     : Optional[str]= None

class AccTaxInvoiceDetailsSchema(BaseModel):

    id                           : Optional[int]= None
    tax_invoice_master_id           : Optional[int]= None
    service_goods_master_id     : Optional[int]= None
    service_goods_name          : Optional[str] =None
    is_main_service             : Optional[str] = 'no'
    is_bundle_service           : Optional[str]= 'no'
    bundle_service_id           : Optional[int]= None
    service_charge              : Optional[float]= None
    govt_agency_fee             : Optional[float]= None
    stamp_duty                  : Optional[float]= None
    stamp_fee                   : Optional[float]= None
    quantity                    : Optional[int]= None

    offer_master_id             : Optional[int]= None
    offer_name                  : Optional[str]= None
    offer_percentage            : Optional[float]= None
    offer_amount                : Optional[float]= None

    has_coupon                   : Optional[str] = 'no'
    coupon_code                  : Optional[str] = None
    coupon_percentage            : Optional[float] = None
    coupon_amount                : Optional[float] = None

    discount_percentage         : Optional[float]= None
    discount_amount             : Optional[float]= None

    gst_percent                 : Optional[float]= None
    gst_amount                  : Optional[float]= None
    taxable_amount              : Optional[float]= None
    total_amount                : Optional[float]= None
    is_deleted                  : Optional[str]= None

class AccTaxInvoiceShema(BaseModel):
    tax_invoice_master : AccTaxInvoiceMasterSchema
    tax_invoice_details : List[AccTaxInvoiceDetailsSchema]
class AccTaxInvoiceResponceSchema(BaseModel):
    work_order_master : OffViewWorkOrderMasterSchema
    tax_invoice_master : AccTaxInvoiceMasterSchema
    tax_invoice_details : List[AccTaxInvoiceDetailsSchema]
    
