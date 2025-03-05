from sqlalchemy import Date
from sqlalchemy import Column, Integer, String ,Float,Text, DECIMAL,Time
from sqlalchemy.dialects.mysql import CHAR
from caerp_db.database import caerp_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import date, datetime 
from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum

class PrlSalaryComponent(caerp_base):
    __tablename__ = 'prl_salary_components'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    component_type = Column(Enum('ALLOWANCE', 'DEDUCTION'), nullable=False, default='ALLOWANCE')
    component_name = Column(String(100), default=None)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class PrlCalculationFrequency(caerp_base):
    __tablename__ = 'prl_calculation_frequency'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    frequency = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')

class PrlCalculationMethod(caerp_base):
    __tablename__ = 'prl_calculation_method'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    calculation_method = Column(String(100), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
    
    
    


# class EmployeeSalaryDetail(caerp_base):
#     __tablename__ = 'employee_salary_details'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     employee_id = Column(Integer,  nullable=False)
#     component_id = Column(Integer,  nullable=False)
#     calculation_frequency_id = Column(Integer,  nullable=False)
#     calculation_method_id = Column(Integer, nullable=False)
#     amount = Column(Float, nullable=False, default=0.0)
#     percentage_of_component_id = Column(Integer, nullable=True)
#     percentage = Column(Float, nullable=False, default=0.0)
#     effective_from_date = Column(Date, nullable=False)
#     effective_to_date = Column(Date, nullable=True)
#     next_increment_date = Column(Date, nullable=True)
#     created_by = Column(Integer, nullable=False)
#     created_on = Column(DateTime, nullable=False, default=datetime.utcnow)
#     is_approved = Column(Enum('yes', 'no'), nullable=False, default='no')
#     approved_by = Column(Integer, nullable=False)
#     approved_on = Column(DateTime, nullable=False, default=datetime.utcnow)
#     is_deleted = Column(Enum('yes', 'no'), nullable=False, default='no')
#     deleted_by = Column(Integer, nullable=True)
#     deleted_on = Column(DateTime, nullable=True)


