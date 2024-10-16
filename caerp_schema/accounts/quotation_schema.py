from enum import Enum
from pydantic import BaseModel
from typing import List,Optional
from datetime import date, datetime
from caerp_schema.office.office_schema import OffWorkOrderMasterSchema,OffViewWorkOrderDetailsSchema,OffViewWorkOrderMasterSchema



class AccQuotationMasterSchema(BaseModel):

    id                      : Optional[int] = None
    financial_year_id       : Optional[int] = None
    work_order_master_id    : Optional[int] = None
    quotation_version       : Optional[int] = None
    quotation_date          : Optional[date] = None
    quotation_number        : Optional[str] = None

    total_offer_amount             : Optional[float] = None
    total_coupon_amount            : Optional[float] = None
    # product_discount_total  : Optional[float] = None
    bill_discount_amount           : Optional[float] = None
    additional_discount_amount     : Optional[float] = None

    grand_total_amount             : Optional[float] = None
    round_off_amount               : Optional[float] = None
    net_amount              : Optional[float] = None
    remarks                 : Optional[str] = None
    quotation_status_id        : Optional[int] = None
    is_final_quotation      : Optional[str] = 'no'
    is_locked                       : Optional[str] = 'no'  
    locked_on                       : Optional[datetime] = None
    locked_by                       : Optional[int] =  None

# class AccQuotationDetailsSchema(BaseModel):

#     id                           : Optional[int] = None
#     quotation_master_id          : Optional[int] = None
#     service_goods_master_id      : Optional[int] = None
#     service_goods_name           : Optional[str] = None
#     hsn_sac_code                 : Optional[str] = None
#     is_main_service              : Optional[str] = 'no'   
#     is_bundle_service            : Optional[str] = 'no'
#     bundle_service_id            : Optional[int] = None
#     service_charge               : Optional[float] = None
#     govt_agency_fee              : Optional[float] = None
#     stamp_duty                   : Optional[float] = None
#     stamp_fee                    : Optional[float] = None
#     quantity                     : Optional[float] = None

#     has_offer                    : Optional[str] = 'no'
#     offer_name                   : Optional[str] = None
#     offer_percentage             : Optional[float] = None
#     offer_amount                 : Optional[float] = None

#     has_coupon                   : Optional[str] = 'no'
#     coupon_code                  : Optional[str] = None
#     coupon_percentage            : Optional[float] = None
#     coupon_amount                : Optional[float] = None

#     discount_percentage          : Optional[float] = None
#     discount_amount              : Optional[float] = None

#     gst_percent                  : Optional[float] = None
#     gst_amount                   : Optional[float] = None
#     taxable_amount               : Optional[float] = None
#     total_amount                 : Optional[float] = None
#     # service_required             : Optional[str] = 'YES'
#     # service_required_date        : Optional[date] = None
#     is_deleted                   : Optional[str] = 'no'



class AccQuotationDetailsSchema(BaseModel):

    id                           : Optional[int] = None
    quotation_master_id          : Optional[int] = None
    service_goods_master_id      : Optional[int] = None
    # service_goods_name           : Optional[str] = None
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
    discount_amount
    additional_discount_percentage   : Optional[float] = None
    additional_discount_amount       : Optional[float] = None
    
    taxable_amount               : Optional[float] = None
    igst_percent                 : Optional[float] = None
    igst_amount                  : Optional[float] = None
    cgst_percent                 : Optional[float] = None
    cgst_amount                  : Optional[float] = None
    sgst_percent                 : Optional[float] = None
    sgst_amount                  : Optional[float] = None
    cess_percent                 : Optional[float] = None
    cess_amount                  : Optional[float] = None
    additional_cess_percent      : Optional[float] = None
    additional_cess_amount       : Optional[float] = None
    total_amount                 : Optional[float] = None
    # service_required             : Optional[str] = 'YES'
    # service_required_date        : Optional[date] = None
    is_deleted                   : Optional[str] = 'no'
    class Config:
        orm_mode = True
        from_attributes = True

class AccQuotationMasterViewSchema(BaseModel):
    quotation_master_id     : Optional[int] = None
    financial_year_id       : Optional[int] = None
    financial_year          : Optional[str] = None
    year_begin_date         : Optional[date] = None
    year_end_date           : Optional[date] = None
    work_order_master_id    : Optional[int] = None
    quotation_version       : Optional[int] = None
    quotation_date          : Optional[date] = None
    quotation_number        : Optional[str] = None
    total_offer_amount             : Optional[float] = None
    total_coupon_amount            : Optional[float] = None

    bill_discount_amount           : Optional[float] = None
    additional_discount_amount     : Optional[float] = None

    grand_total_amount             : Optional[float] = None
    round_off_amount               : Optional[float] = None
    net_amount                     : Optional[float] = None
    quotation_status_id            : Optional[int] = None
    quotation_status                : Optional[str] = None
    is_final_quotation             : Optional[str] = 'no'
    enquiry_master_id           : Optional[int] = None
    enquiry_details_id          : Optional[int] = None
    appointment_master_id       : Optional[int] = None
    visit_master_id             : Optional[int] = None

    work_order_number           : Optional[str] = None
    work_order_date             : Optional[date] = None
    first_name                  : Optional[str] = None
    middle_name                 : Optional[str] = None
    last_name                   : Optional[str] = None
    gender_id                   : Optional[int] = None
    gender                      : Optional[str] = None
    date_of_birth               : Optional[date] = None
    mobile_number               : Optional[str] = None
    whatsapp_number             : Optional[str] = None
    email_id                    : Optional[str] = None
    house_or_building_name      : Optional[str] = None
    road_or_street_name         : Optional[str] = None
    locality                    : Optional[str] = None
    pin_code                    : Optional[str] = None
    post_office_id              : Optional[int] = None
    post_office_name            : Optional[str] = None
    village_id                  : Optional[int] = None
    village_name                : Optional[str] = None
    lsg_type_id                 : Optional[int] = None
    lsg_type                    : Optional[str] = None
    lsg_id                      : Optional[int] = None
    lsg_name                    : Optional[str] = None
    taluk_id                    : Optional[int] = None
    taluk_name                  : Optional[str] = None
    district_id                 : Optional[int] = None
    district_name               : Optional[str] = None
    state_id                    : Optional[int] = None
    state_name                  : Optional[str] = None
    country_id                  : Optional[int] = None
    country_name                : Optional[str] = None
    work_order_remarks          : Optional[str] = None
    contact_person_name         : Optional[str] = None
    contact_person_mobile_number    : Optional[str] = None
    contact_person_whatsapp_number  : Optional[str] = None
    contact_person_email_id         : Optional[str] = None
    work_order_status_id            : Optional[int] = None
    work_order_status               : Optional[str] = None



    # created_by          : Optional[int] = None
    # created_on          : Optional[str] = None
    # modified_by         : Optional[int] = None
    # modified_on         : Optional[str] = None
    # is_deleted          : Optional[str] = 'no'
    # deleted_by          : Optional[int] = None
    # deleted_on          : Optional[str] = None
    is_locked           : Optional[str] = 'no'  
    locked_on          : Optional[date] = None
    locked_by          : Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True

class AccQuotationSchema(BaseModel):
    quotation_master            : AccQuotationMasterSchema
    quotation_details           : List[AccQuotationDetailsSchema]


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

    coupon_total                : Optional[float] = None
    grand_total_amount          : Optional[float]= None
    bill_discount_amount        : Optional[float]= None
    additional_discount_amount  : Optional[float]= None
    advance_amount              : Optional[float]= None
    additional_fee_required     : Optional[float]= None
    round_off_amount            : Optional[float]= None
    net_amount                  : Optional[float]= None
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
    

class AccTaxInvoiceMasterViewSchema(BaseModel):
    id: Optional[int] = None
    voucher_id: Optional[int] = None
    tax_invoice_date: Optional[date] = None
    tax_invoice_number: Optional[str] = None
    account_head_id: Optional[int] = None
    service_type: Optional[str] = None
    appointment_master_id: Optional[int] = None
    visit_master_id: Optional[int] = None
    enquiry_master_id: Optional[int] = None
    enquiry_details_id: Optional[int] = None
    work_order_master_id: Optional[int] = None
    financial_year_id: Optional[int] = None
    financial_year: Optional[str] = None
    year_begin_date: Optional[date] = None
    year_end_date: Optional[date] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender_id: Optional[int] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    mobile_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email_id: Optional[str] = None
    house_or_building_name: Optional[str] = None
    road_or_street_name: Optional[str] = None
    locality: Optional[str] = None
    pin_code: Optional[str] = None
    post_office_id: Optional[int] = None
    post_office_name: Optional[str] = None
    village_id: Optional[int] = None
    village_name: Optional[str] = None
    lsg_type_id: Optional[int] = None
    lsg_type: Optional[str] = None
    lsg_id: Optional[int] = None
    lsg_name: Optional[str] = None
    taluk_id: Optional[int] = None
    taluk_name: Optional[str] = None
    district_id: Optional[int] = None
    district_name: Optional[str] = None
    state_id: Optional[int] = None
    state_name: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    contact_person_name: Optional[str] = None
    contact_person_mobile_number: Optional[str] = None
    contact_person_whatsapp_number: Optional[str] = None
    contact_person_email_id: Optional[str] = None
    total_offer_amount: Optional[float] = None
    total_coupon_amount: Optional[float] = None
    bill_discount_amount: Optional[float] = None
    additional_discount_amount: Optional[float] = None
    grand_total_amount: Optional[float] = None
    advance_amount: Optional[float] = None
    additional_fee_amount : Optional[float] =None
    round_off_amount: Optional[float] = None
    net_amount: Optional[float] = None
    tax_invoice_status_id: Optional[int] = None
    tax_invoice_status: Optional[str] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None
    modified_by: Optional[int] = None
    modified_on: Optional[datetime] = None
    is_deleted: Optional[str] = None
    deleted_by: Optional[int] = None
    deleted_on: Optional[datetime] = None
    is_locked: Optional[str] = None
    locked_on: Optional[datetime] = None
    locked_by: Optional[str] = None


class AccTaxInvoiceDetailsViewSchema(BaseModel):
    id: Optional[int] = None
    tax_invoice_master_id: Optional[int] = None
    service_type: Optional[str] = None
    service_goods_master_id: Optional[int] = None
    service_goods_name: Optional[str] = None
    hsn_sac_id: Optional[int] = None
    hsn_sac_code: Optional[str] = None
    sku_code_id: Optional[int] = None
    unit: Optional[str] = None
    is_main_service: Optional[str] = None
    is_bundle_service: Optional[str] = None
    bundle_service_id: Optional[int] = None
    service_charge: Optional[float] = None
    govt_agency_fee: Optional[float] = None
    stamp_duty: Optional[float] = None
    stamp_fee: Optional[float] = None
    quantity: Optional[int] = None
    has_offer: Optional[str] = None
    offer_name: Optional[str] = None
    offer_percentage: Optional[float] = None
    offer_amount: Optional[float] = None
    has_coupon: Optional[str] = None
    coupon_code: Optional[str] = None
    coupon_percentage: Optional[float] = None
    coupon_amount: Optional[float] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    additional_discount_percentage: Optional[float] = None
    additional_discount_amount: Optional[float] = None
    taxable_amount: Optional[float] = None
    igst_percent: Optional[float] = None
    igst_amount: Optional[float] = None
    cgst_percent: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_percent: Optional[float] = None
    sgst_amount: Optional[float] = None
    cess_percent: Optional[float] = None
    cess_amount: Optional[float] = None
    additional_cess_percent: Optional[float] = None
    additional_cess_amount: Optional[float] = None
    total_amount: Optional[float] = None
    is_deleted: Optional[str] = None



class AccTaxInvoiceResponceSchema(BaseModel):
    tax_invoice_master: AccTaxInvoiceMasterViewSchema
    tax_invoice_details: Optional[List[AccTaxInvoiceDetailsViewSchema]]


class AccProformaInvoiceMasterViewSchema(BaseModel):
    id: Optional[int] = None
    voucher_id: Optional[int] = None
    proforma_invoice_date: Optional[date] = None
    proforma_invoice_number: Optional[str] = None
    account_head_id: Optional[int] = None
    service_type: Optional[str] = None
    appointment_master_id: Optional[int] = None
    visit_master_id: Optional[int] = None
    enquiry_master_id: Optional[int] = None
    enquiry_details_id: Optional[int] = None
    work_order_master_id: Optional[int] = None
    financial_year_id: Optional[int] = None
    financial_year: Optional[str] = None
    year_begin_date: Optional[date] = None
    year_end_date: Optional[date] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender_id: Optional[int] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    mobile_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email_id: Optional[str] = None
    house_or_building_name: Optional[str] = None
    road_or_street_name: Optional[str] = None
    locality: Optional[str] = None
    pin_code: Optional[str] = None
    post_office_id: Optional[int] = None
    post_office_name: Optional[str] = None
    village_id: Optional[int] = None
    village_name: Optional[str] = None
    lsg_type_id: Optional[int] = None
    lsg_type: Optional[str] = None
    lsg_id: Optional[int] = None
    lsg_name: Optional[str] = None
    taluk_id: Optional[int] = None
    taluk_name: Optional[str] = None
    district_id: Optional[int] = None
    district_name: Optional[str] = None
    state_id: Optional[int] = None
    state_name: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    contact_person_name: Optional[str] = None
    contact_person_mobile_number: Optional[str] = None
    contact_person_whatsapp_number: Optional[str] = None
    contact_person_email_id: Optional[str] = None
    total_offer_amount: Optional[float] = None
    total_coupon_amount: Optional[float] = None
    bill_discount_amount: Optional[float] = None
    additional_discount_amount: Optional[float] = None
    grand_total_amount: Optional[float] = None
    advance_amount: Optional[float] = None
    round_off_amount: Optional[float] = None
    net_amount: Optional[float] = None
    proforma_invoice_status_id: Optional[int] = None
    proforma_invoice_status: Optional[str] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None
    modified_by: Optional[int] = None
    modified_on: Optional[datetime] = None
    is_deleted: Optional[str] = None
    deleted_by: Optional[int] = None
    deleted_on: Optional[datetime] = None
    is_locked: Optional[str] = None
    locked_on: Optional[datetime] = None
    locked_by: Optional[str] = None


class AccProformaInvoiceDetailsViewSchema(BaseModel):
    id: Optional[int] = None
    proforma_invoice_master_id: Optional[int] = None
    service_type: Optional[str] = None
    service_goods_master_id: Optional[int] = None
    service_goods_name: Optional[str] = None
    hsn_sac_id: Optional[int] = None
    hsn_sac_code: Optional[str] = None
    sku_code_id: Optional[int] = None
    unit: Optional[str] = None
    is_main_service: Optional[str] = None
    is_bundle_service: Optional[str] = None
    bundle_service_id: Optional[int] = None
    service_charge: Optional[float] = None
    govt_agency_fee: Optional[float] = None
    stamp_duty: Optional[float] = None
    stamp_fee: Optional[float] = None
    quantity: Optional[int] = None
    has_offer: Optional[str] = None
    offer_name: Optional[str] = None
    offer_percentage: Optional[float] = None
    offer_amount: Optional[float] = None
    has_coupon: Optional[str] = None
    coupon_code: Optional[str] = None
    coupon_percentage: Optional[float] = None
    coupon_amount: Optional[float] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    additional_discount_percentage: Optional[float] = None
    additional_discount_amount: Optional[float] = None
    taxable_amount: Optional[float] = None
    igst_percent: Optional[float] = None
    igst_amount: Optional[float] = None
    cgst_percent: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_percent: Optional[float] = None
    sgst_amount: Optional[float] = None
    cess_percent: Optional[float] = None
    cess_amount: Optional[float] = None
    additional_cess_percent: Optional[float] = None
    additional_cess_amount: Optional[float] = None
    total_amount: Optional[float] = None
    is_deleted: Optional[str] = None


class AccProformaInvoiceResponceSchema(BaseModel):
    proforma_invoice_master: AccProformaInvoiceMasterViewSchema
    proforma_invoice_details: Optional[List[AccProformaInvoiceDetailsViewSchema]]


class AccQuotationDetailsViewSchema(BaseModel):
    
    id                          : Optional[int]= None   
    quotation_master_id         : Optional[int]= None    
    quotation_version           : Optional[int]= None
    quotation_date              : Optional[date]= None
    quotation_number            : Optional[str]= None
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
    additional_discount_percentage   : Optional[float] = None
    additional_discount_amount       : Optional[float] = None
    
    taxable_amount               : Optional[float] = None
    igst_percent                 : Optional[float] = None
    igst_amount                  : Optional[float] = None
    cgst_percent                 : Optional[float] = None
    cgst_amount                  : Optional[float] = None
    sgst_percent                 : Optional[float] = None
    sgst_amount                  : Optional[float] = None
    cess_percent                 : Optional[float] = None
    cess_amount                  : Optional[float] = None
    additional_cess_percent      : Optional[float] = None
    additional_cess_amount       : Optional[float] = None
    total_amount                : Optional[float]= None
    is_deleted                  : Optional[str]= None   

    class Config:
        orm_mode = True
        from_attributes = True     


class AccQuotationResponseSchema(BaseModel):
    quotation_master            : AccQuotationMasterViewSchema
    quotation_details           : List[AccQuotationDetailsViewSchema]    
