from sqlalchemy import ARRAY, Boolean, Date
from sqlalchemy import Column, Integer, String ,Float,Text, DECIMAL,Time
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import date, datetime 
from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum

class gstTest(caerp_base):
    __tablename__ = 'gst_test'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), default=None)
    gst = Column(String(100), default=None)
    amount = Column(DECIMAL(15,2), default=None)


class gstr2b(caerp_base):
    __tablename__ = 'purchase_gstr2b'
    p_g_id = Column(Integer, primary_key=True, autoincrement=True)
    cfs = Column(String(5), default=None)
    type = Column(String(10), default=None)
    supplier_name = Column(String(200), default=None)
    supplier_tax_period= Column(Date, default=None)
    supplier_file_date= Column(Date, default=None)
    gstin  = Column(String(50), default=None)
    invoice_date= Column(Date, default=None)
    invoice_number = Column(String(40), default=None)
    applicable_tax_per = Column(DECIMAL(4,2), default=None)
    state = Column(Integer,default=0)
    reverse_charge = Column(String(5), default=None)
    taxable_rate = Column(DECIMAL(6,2), default=None)
    taxable_value = Column(DECIMAL(15,2), default=None)
    iamt = Column(DECIMAL(15,2), default=None)
    camt = Column(DECIMAL(15,2), default=None)
    samt = Column(DECIMAL(15,2), default=None)
    csamt = Column(DECIMAL(15,2), default=None)
    elg  = Column(String(10), default=None)
    tx_i = Column(DECIMAL(15,2), default=None)
    tx_c = Column(DECIMAL(15,2), default=None)
    tx_s = Column(DECIMAL(15,2), default=None)
    tx_cs = Column(DECIMAL(15,2), default=None)
    refund_number = Column(String(40), default=None)
    refund_date= Column(Date, default=None)
    reason = Column(Text, nullable=False)
    document_type = Column(String(5), default=None)
    p_gst = Column(String(5), default=None)
    chksum = Column(Text, nullable=False)
    flag = Column(String(5), default=None)
    cflag = Column(String(5), default=None)
    inv_typ = Column(String(5), default=None)
    new_entry = Column(Integer,default=0)
    gstr_description = Column(Text, nullable=False)
    amd_invoice_number = Column(String(30), default=None)
    amd_invoice_date= Column(Date, default=None)
    tax_period  = Column(DateTime, nullable=True)
    entry_date  = Column(DateTime, nullable=True)