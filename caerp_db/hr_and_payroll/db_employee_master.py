from fastapi import HTTPException,status, Depends
from sqlalchemy.orm import Session
from caerp_db.common.models import Employee, EmployeeMasterView
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeMasterSchema, EmployeeMasterSchemaForGet, EmployeePersonalDetailSchema, EmployeeAddressDetailSchema, EmployeeContactDetailSchema, EmployeeBankAccountDetailSchema
from caerp_db.hash import Hash
from caerp_db.database import get_db
from typing import List,Optional, Union,Dict
from caerp_constants.caerp_constants import DeletedStatus, ActiveStatus, VerifiedStatus, ApprovedStatus
from datetime import date,datetime
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError


def save_employee_master(db: Session, request: EmployeeMasterSchema, id: int, user_id: int):
   try:
      if id == 0:
        data = request.dict()
        data["created_by"] = user_id
        result = Employee(**data)
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
      else:
        updated = db.query(Employee).filter(Employee.employee_id == id).first()
        if updated is None:
          raise HTTPException(status_code=404, detail="Employee not found")
        for field,value in request.dict(exclude_unset = True).items():
           setattr(updated, field, value)
        updated.modified_by = user_id
        updated.modified_on = datetime.utcnow()
        updated.is_verified = 'yes'
        updated.verified_by = user_id
        updated.verified_on = datetime.utcnow()
        updated.is_approved = 'yes'
        updated.approved_by = user_id
        updated.approved_on = datetime.utcnow()
        db.commit()
        db.refresh(updated)
        return updated
   except SQLAlchemyError as e:
        error_message = f"Failed to save Employee Master: {e}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)  
   
#-------------------------------------------------------------------------------------------------------------------

def get_deleted_employees(db: Session, deleted_status: DeletedStatus):
    if deleted_status == DeletedStatus.DELETED:
        return db.query(EmployeeMasterView).filter(EmployeeMasterView.is_deleted == 'yes').all()
    elif deleted_status == DeletedStatus.NOT_DELETED:
        return db.query(EmployeeMasterView).filter(EmployeeMasterView.is_deleted == 'no').all()
    elif deleted_status == DeletedStatus.ALL:
        return db.query(EmployeeMasterView).all()
         
    else:
        # Handle invalid state or raise an error
        raise ValueError("Invalid deleted_status")

#-------------------------------------------------------------------------------------------------------------------

def get_employee(db: Session, id: int):
  emp = db.query(EmployeeMasterView).filter(EmployeeMasterView.employee_id == id).first()
  if not emp:
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
    detail = f"Employee with id {id} not found" )  
  return emp    

#-------------------------------------------------------------------------------------------------------------------

def delete_employee_master(db: Session, id: int, deleted_by: int):
    result = db.query(Employee).filter(Employee.employee_id == id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")

    result.is_deleted = 'yes'
    result.deleted_by = deleted_by
    result.deleted_on = datetime.utcnow()

    db.commit()

    return {
        "message": "Deleted successfully",
    }

#---------------------------------------------------------------------------------------------------------------------

def get_verified_employees(db: Session, verified_status: VerifiedStatus):
   if verified_status == VerifiedStatus.VERIFIED:
      return db.query(EmployeeMasterView).filter(
         and_(
            EmployeeMasterView.is_verified == 'yes',
            EmployeeMasterView.is_deleted  == "no"
        )
      ).all()
   elif verified_status == VerifiedStatus.NOT_VERIFIED:
      return db.query(EmployeeMasterView).filter(
         and_(
            EmployeeMasterView.is_verified == 'no',
            EmployeeMasterView.is_deleted  == "no"
        )
      ).all() 
   else:
        # Handle invalid state or raise an error
        raise ValueError("Invalid verified_status")
   
#-----------------------------------------------------------------------------------------------------------------------

def get_approved_employees(db: Session, approved_status: ApprovedStatus):
   if approved_status == ApprovedStatus.APPROVED:
      return db.query(EmployeeMasterView).filter(
         and_(
            EmployeeMasterView.is_approved == 'yes',
            EmployeeMasterView.is_deleted  == "no"
        )
      ).all()
   elif approved_status == ApprovedStatus.NOT_APPROVED:
      return db.query(EmployeeMasterView).filter(
         and_(
            EmployeeMasterView.is_approved == 'no',
            EmployeeMasterView.is_deleted  == "no"
        )
      ).all() 
   else:
        # Handle invalid state or raise an error
        raise ValueError("Invalid approved_status")      
   
#-------------------------------------------------------------------------------------------------------------------

def update_employee_personal_details(db: Session, request: EmployeePersonalDetailSchema, id: int, user_id: int):
   try:   
     update_emp_per_det = db.query(Employee).filter(Employee.employee_id == id).first()
     if update_emp_per_det is None:
        raise HTTPException(status_code=404, detail="Employee not found")
  
     for field,value in request.dict(exclude_unset = True).items():
        setattr(update_emp_per_det, field, value)
     update_emp_per_det.modified_by = user_id
     update_emp_per_det.modified_on = datetime.utcnow()
     db.commit()
     db.refresh(update_emp_per_det)
     return update_emp_per_det
   except SQLAlchemyError as e:
        error_message = f"Failed to update Employee Personal Details: {e}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)
   
#----------------------------------------------------------------------------------------------------------------------

def update_employee_address_details(db: Session, request: EmployeeAddressDetailSchema, id: int, user_id: int):
   try:   
     update_emp_addr_det = db.query(Employee).filter(Employee.employee_id == id).first()
     if update_emp_addr_det is None:
        raise HTTPException(status_code=404, detail="Employee not found")
  
     for field,value in request.dict(exclude_unset = True).items():
        setattr(update_emp_addr_det, field, value)
     update_emp_addr_det.modified_by = user_id
     update_emp_addr_det.modified_on = datetime.utcnow()
     db.commit()
     db.refresh(update_emp_addr_det)
     return update_emp_addr_det
   except SQLAlchemyError as e:
        error_message = f"Failed to update Employee Address Details: {e}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)       
   
#------------------------------------------------------------------------------------------------------------------------

def update_employee_contact_details(db: Session, request: EmployeeContactDetailSchema, id: int, user_id: int):
   try:   
     update_emp_contact_det = db.query(Employee).filter(Employee.employee_id == id).first()
     if update_emp_contact_det is None:
        raise HTTPException(status_code=404, detail="Employee not found")
  
     for field,value in request.dict(exclude_unset = True).items():
        setattr(update_emp_contact_det, field, value)
     update_emp_contact_det.modified_by = user_id
     update_emp_contact_det.modified_on = datetime.utcnow()
     db.commit()
     db.refresh(update_emp_contact_det)
     return update_emp_contact_det
   except SQLAlchemyError as e:
     error_message = f"Failed to update Employee Contact Details: {e}"
     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)      
   
#-----------------------------------------------------------------------------------------------------------------------

def update_employee_bank_acc_details(db: Session, request: EmployeeBankAccountDetailSchema, id: int, user_id: int):
   try:   
     update_emp_bank_acc = db.query(Employee).filter(Employee.employee_id == id).first()
     if update_emp_bank_acc is None:
        raise HTTPException(status_code=404, detail="Employee not found")
  
     for field,value in request.dict(exclude_unset = True).items():
        setattr(update_emp_bank_acc, field, value)
     update_emp_bank_acc.modified_by = user_id
     update_emp_bank_acc.modified_on = datetime.utcnow()
     db.commit()
     db.refresh(update_emp_bank_acc)
     return update_emp_bank_acc
   except SQLAlchemyError as e:
     error_message = f"Failed to update Employee Bank Account Details: {e}"
     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)
   
#-----------------------------------------------------------------------------------------------------------------------

def get_consultants(db: Session):
   is_consult = db.query(EmployeeMasterView).filter(
         and_(
            EmployeeMasterView.is_consultant == 'yes',
            EmployeeMasterView.is_deleted  == "no"
        )
      ).all()
   
   if is_consult is None:
        raise HTTPException(status_code=404, detail="There are no employees who are consultants")
   return is_consult

#----------------------------------------------------------------------------------------------------------------------------

def get_consultant_by_id(db: Session, id: int):
   is_employee_found = db.query(EmployeeMasterView).filter(EmployeeMasterView.employee_id == id).first()
   if is_employee_found is None:
        raise HTTPException(status_code=404, detail="Employee not found")
  
   is_consult_id = db.query(EmployeeMasterView).filter(
         and_(
            EmployeeMasterView.employee_id == id,
            EmployeeMasterView.is_consultant == 'yes',
            EmployeeMasterView.is_deleted  == "no"
        )
      ).first()
   
   if is_consult_id is None:
      raise HTTPException(status_code=404, detail="the particular employee is not a consultant")
   return is_consult_id
