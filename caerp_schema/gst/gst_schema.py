from enum import Enum
from pydantic import BaseModel
from typing import List,Optional, Union,Dict
from datetime import date, datetime
from caerp_constants.caerp_constants import BooleanFlag

class gstTestSchema(BaseModel):
   id   :   Optional[int]
   name :  Optional[str]
   gst  : Optional[str]
   amount :  Optional[float]


class gst2bSchema(BaseModel):
    p_g_id : Optional[int]
    cfs : Optional[str]
    type : Optional[str]
    supplier_name : Optional[str]
    supplier_tax_period: Optional[date]
    supplier_file_date: Optional[date]
    gstin  : Optional[str]
    invoice_date: Optional[date]
    invoice_number : Optional[str]
    applicable_tax_per : Optional[float]
    state : Optional[int]
    reverse_charge : Optional[str]
    taxable_rate : Optional[float]
    taxable_value : Optional[float]
    iamt : Optional[float]
    camt : Optional[float]
    samt : Optional[float]
    csamt : Optional[float]
    elg  : Optional[str]
    tx_i : Optional[float]
    tx_c : Optional[float]
    tx_s : Optional[float]
    tx_cs : Optional[float]
    refund_number : Optional[str]
    refund_date: Optional[date]
    reason : Optional[str]
    document_type : Optional[str]
    p_gst : Optional[str]
    chksum : Optional[str]
    flag : Optional[str]
    cflag : Optional[str]
    inv_typ : Optional[str]
    new_entry : Optional[int]
    gstr_description : Optional[str]
    amd_invoice_number : Optional[str]
    amd_invoice_date: Optional[date]
    tax_period  : Optional[datetime] = None
    entry_date  : Optional[datetime] = None
   