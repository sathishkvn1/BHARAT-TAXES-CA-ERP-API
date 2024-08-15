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
    
    
    
class EmployeeSalaryDetails(caerp_base):
    __tablename__ = "employee_salary_details"

    id                          = Column(Integer, primary_key=True, autoincrement=True)
    employee_id                 = Column(Integer, nullable=False)
    component_id                = Column(Integer, nullable=False)
    calculation_frequency_id    = Column(Integer, nullable=False)
    calculation_method_id       = Column(Integer, nullable=False)
    amount                      = Column(Float, nullable=False, default=0.0)
    percentage_of_component_id  = Column(Integer, default=None)
    percentage                  = Column(Float, nullable=False, default=0.0)
    effective_from_date         = Column(Date, nullable=False)
    effective_to_date           = Column(Date, default=None)
    next_increment_date         = Column(Date, default=None)
    created_by                  = Column(Integer, nullable=False, default=0)
    created_on                  = Column(DateTime, nullable=False, default=func.now())
    is_approved                 = Column(Enum('yes', 'no'), nullable=False, default='no')
    approved_by                 = Column(Integer, nullable=False)
    approved_on                 = Column(DateTime, nullable=False)
    modified_by                 = Column(Integer, default=None)
    modified_on                 = Column(DateTime, default=None)
    is_deleted                  = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by                  = Column(Integer, default=None)
    deleted_on                  = Column(DateTime, default=None)


class EmployeeSalaryDetailsView(caerp_base):
    __tablename__ = "hr_view_employee_salary"

    salary_id                          = Column(Integer, primary_key=True)
    employee_id                        = Column(Integer)
    employee_first_name                = Column(String)
    employee_middle_name               = Column(String)
    employee_last_name                 = Column(String)
    component_id                       = Column(Integer)
    salary_component_name              = Column(String)
    salary_component_type              = Column(String)
    calculation_frequency_id           = Column(Integer)
    calculation_frequency_name         = Column(String)
    calculation_method_id              = Column(Integer)
    calculation_method_name            = Column(String)
    amount                             = Column(Float)
    percentage_of_component_id         = Column(Integer)
    percentage_component_name          = Column(String)
    percentage                         = Column(Float)
    effective_from_date                = Column(Date)
    effective_to_date                  = Column(Date)
    next_increment_date                = Column(Date)
    created_by                         = Column(Integer)
    created_on                         = Column(DateTime)
    is_approved                        = Column(Enum('yes', 'no'))
    approved_by                        = Column(Integer)
    approved_on                        = Column(DateTime)
    modified_by                        = Column(Integer)
    modified_on                        = Column(DateTime)
    is_deleted                         = Column(Enum('yes', 'no'))
    deleted_by                         = Column(Integer)
    deleted_on                         = Column(DateTime)
    

