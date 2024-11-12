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
    approved_by                 = Column(Integer, nullable=True)
    approved_on                 = Column(DateTime, nullable=True)
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
    

#----------------------------EmployeeTeam---------------------------------------------------------------------
class EmployeeTeamMaster(caerp_base):
    __tablename__ = 'employee_team_master'

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    department_id         = Column(Integer, nullable=False)
    team_name             = Column(String(50), nullable=True)
    description           = Column(String(1000), nullable=False)
    effective_from_date   = Column(Date, nullable=False, default=datetime.now().date)
    effective_to_date     = Column(Date, nullable=True)
    created_by            = Column(Integer, nullable=False)
    created_on            = Column(DateTime, nullable=False, default=datetime.now)
    modified_by           = Column(Integer, nullable=True)
    modified_on           = Column(DateTime, nullable=True)
    is_deleted            = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by            = Column(Integer, nullable=True)
    deleted_on            = Column(DateTime, nullable=True)


class EmployeeTeamMembers(caerp_base):
    __tablename__ = 'employee_team_members'

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    team_master_id        = Column(Integer, nullable=False)
    employee_id           = Column(Integer, nullable=False)
    is_team_leader        = Column(Enum('yes', 'no'), nullable=False, default='no')
    team_leader_id        = Column(Integer, nullable=False)
    effective_from_date   = Column(Date, nullable=False, default=datetime.now().date)
    effective_to_date     = Column(Date, nullable=True)
    created_by            = Column(Integer, nullable=False)
    created_on            = Column(DateTime, nullable=False, default=datetime.now)
    modified_by           = Column(Integer, nullable=True)
    modified_on           = Column(DateTime, nullable=True)
    is_deleted            = Column(Enum('yes', 'no'), nullable=False, default='no')
    deleted_by            = Column(Integer, nullable=True)
    deleted_on            = Column(DateTime, nullable=True)




class HrViewEmployeeTeamMaster(caerp_base):
    __tablename__ = 'hr_view_employee_team_master'

    team_id               = Column(Integer, primary_key=True)
    department_id         = Column(Integer, nullable=False)
    department_name       = Column(String(200))
    team_name             = Column(String(50))
    description           = Column(String(1000), nullable=False)
    effective_from_date   = Column(Date, nullable=False)
    effective_to_date     = Column(Date)
    created_by            = Column(Integer, nullable=False)
    created_on            = Column(DateTime, nullable=False)
    modified_by           = Column(Integer)
    modified_on           = Column(DateTime)
    is_deleted            = Column(Enum('yes', 'no'), nullable=False)
    deleted_by            = Column(Integer)
    deleted_on            = Column(DateTime)
    


class HrViewEmployeeTeamMembers(caerp_base):
    __tablename__ = 'hr_view_employee_team_members'

    team_member_id       = Column(Integer, primary_key=True)
    team_master_id       = Column(Integer, nullable=False)
    team_name            = Column(String(50))
    employee_id          = Column(Integer, nullable=False)
    member_first_name    = Column(String(50), nullable=False)
    member_middle_name   = Column(String(50))
    member_last_name     = Column(String(50), nullable=False)
    department_id        = Column(Integer, nullable=False)
    department_name      = Column(String(200))
    designation_id       = Column(Integer, nullable=False)
    designation          = Column(String(200))
    is_team_leader       = Column(Enum('yes', 'no'), nullable=False)
    team_leader_id       = Column(Integer, nullable=False)
    leader_first_name    = Column(String(50), nullable=False)
    leader_middle_name   = Column(String(50))
    leader_last_name     = Column(String(50), nullable=False)
    effective_from_date  = Column(Date, nullable=False)
    effective_to_date    = Column(Date)
    created_by           = Column(Integer, nullable=False)
    created_on           = Column(DateTime, nullable=False)
    modified_by          = Column(Integer)
    modified_on          = Column(DateTime)
    is_deleted           = Column(Enum('yes', 'no'), nullable=False)
    deleted_by           = Column(Integer)
    deleted_on           = Column(DateTime)

    

    
class HrDocumentMaster(caerp_base):
    __tablename__ = "hr_document_master"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    document_name = Column(String(100), nullable=False)
    has_expiry = Column(Enum('yes', 'no'), default='no', nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
class HrDepartmentMaster(caerp_base):
    __tablename__ = "hr_department_master"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(200), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
class HrDesignationMaster(caerp_base):
    __tablename__ = "hr_designation_master"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    designation = Column(String(200), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
    
class HrEmployeeCategory(caerp_base):
    __tablename__ = "hr_employee_category"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(200), nullable=False)
    is_deleted = Column(Enum('yes', 'no'), default='no', nullable=False)
    
    