from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from caerp_db.common.models import Employee, EmployeeBankDetails, EmployeeContactDetails, EmployeePermanentAddress, EmployeePresentAddress  
from datetime import date,datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetails
from caerp_constants.caerp_constants import DeletedStatus, ActionType, EmployeeActionType
from typing import Union
from sqlalchemy import and_

def save_employee_master(db: Session, request: EmployeeDetails, id: int, user_id: int, Action: ActionType):
    try:
        updated_entities = {}
        if id == 0:
          # new employee master creation
          if Action == EmployeeActionType.INSERT_ONLY:
            data = request.employee_master.dict()
            data["created_by"] = user_id
            result = Employee(**data)
            emp_id = result.employee_id
            db.add(result)
            db.commit()
            db.refresh(result)

            # Get the employee_id of the newly inserted record
            emp_id = result.employee_id

            # Insert into EmployeePresentAddress
            present_address_data = request.present_address.dict()
            present_address_data["employee_id"] = emp_id
            present_address = EmployeePresentAddress(**present_address_data)
            db.add(present_address)

            # Insert into EmployeePermanentAddress
            permanent_address_data = request.permanent_address.dict()
            permanent_address_data["employee_id"] = emp_id
            permanent_address = EmployeePermanentAddress(**permanent_address_data)
            db.add(permanent_address)

            # Insert into EmployeeContactDetails
            contact_details_data = request.contact_details.dict()
            contact_details_data["employee_id"] = emp_id
            contact_details = EmployeeContactDetails(**contact_details_data)
            db.add(contact_details)

            # Insert into EmployeeBankDetails
            bank_details_data = request.bank_details.dict()
            bank_details_data["employee_id"] = emp_id
            bank_details = EmployeeBankDetails(**bank_details_data)
            db.add(bank_details)

            db.commit()
            return result
        else:
          # updating existing employee master
          if Action == EmployeeActionType.UPDATE_ONLY:   
            update_emp = db.query(Employee).filter(Employee.employee_id == id).first()
            if update_emp is None:
                raise HTTPException(status_code=404, detail="Employee not found")
            
            if request.employee_master:
              for field, value in request.employee_master.dict(exclude_unset=True).items():
                setattr(update_emp, field, value)
                update_emp.modified_by = user_id
                update_emp.modified_on = datetime.utcnow()   
              updated_entities['employee_master'] = update_emp 
            
            # updating present address detail table with employee_id
            if request.present_address:            
              update_present_addr = db.query(EmployeePresentAddress).filter(EmployeePresentAddress.employee_id == id).first()
              if update_present_addr is None:
                update_present_addr = EmployeePresentAddress(employee_id = id)
              for field, value in request.present_address.dict(exclude_unset=True).items():
                setattr(update_present_addr, field, value)
              updated_entities['present_address'] = update_present_addr  
            
            # updating permanent address detail table with employee_id
            if request.permanent_address: 
              update_per_addr = db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.employee_id == id).first()
              if update_per_addr is None:
                update_per_addr = EmployeePermanentAddress(employee_id=id)
              for field, value in request.permanent_address.dict(exclude_unset=True).items():
                  setattr(update_per_addr, field, value)
              updated_entities['permanent_address'] = update_per_addr    
            
            # updating contact_details detail table with employee_id
            if request.contact_details:
              update_contact = db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == id).first()
              if update_contact is None:
                update_contact = EmployeeContactDetails(employee_id=id)
              for field, value in request.contact_details.dict(exclude_unset=True).items():
                  setattr(update_contact, field, value)
              updated_entities['contact_details'] = update_contact    
            
            # updating bank_details detail table with employee_id
            if request.bank_details:  
              update_bank = db.query(EmployeeBankDetails).filter(EmployeeBankDetails.employee_id == id).first()
              if update_bank is None:
                update_bank = EmployeeBankDetails(employee_id=id)
              for field, value in request.bank_details.dict(exclude_unset=True).items():
                  setattr(update_bank, field, value)
              updated_entities['bank_details'] = update_bank 
              
            # Commit changes to the database
            db.commit()
            return updated_entities 
          
          # inserting new record to detail tables
          if Action == EmployeeActionType.UPDATE_AND_INSERT:    
            update_emp = db.query(Employee).filter(Employee.employee_id == id).first()
            if update_emp is None:
              raise HTTPException(status_code=404, detail="Employee not found")          
            
            if request.present_address:
              existing_present_address = db.query(EmployeePresentAddress).filter(EmployeePresentAddress.employee_id == id).first()
              if existing_present_address:
                new_effective_from_date = datetime.utcnow()
                existing_present_address.effective_to_date = new_effective_from_date - timedelta(days=1)
                db.add(existing_present_address)

              new_present_address_data = request.present_address.dict(exclude={"effective_to_date"})
              new_present_address_data["employee_id"] = id
              new_present_address_data["effective_from_date"] = new_effective_from_date
              new_present_address = EmployeePresentAddress(**new_present_address_data)
              db.add(new_present_address)

            if request.permanent_address:
              existing_permanent_address = db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.employee_id == id).first()
              if existing_permanent_address:
                new_effective_from_date = datetime.utcnow()
                existing_permanent_address.effective_to_date = new_effective_from_date - timedelta(days=1)
                db.add(existing_permanent_address)

              new_permanent_address_data = request.permanent_address.dict(exclude={"effective_to_date"})
              new_permanent_address_data["employee_id"] = id
              new_permanent_address_data["effective_from_date"] = new_effective_from_date
              new_permanent_address = EmployeePermanentAddress(**new_permanent_address_data)
              db.add(new_permanent_address)  
              
            if request.contact_details:
              existing_contact_details = db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == id).first()
              if existing_contact_details:
                new_effective_from_date = datetime.utcnow()
                existing_contact_details.effective_to_date = new_effective_from_date - timedelta(days=1)
                db.add(existing_contact_details)

              new_contact_details_data = request.contact_details.dict(exclude={"effective_to_date"})
              new_contact_details_data["employee_id"] = id
              new_contact_details_data["effective_from_date"] = new_effective_from_date
              new_contact_details = EmployeeContactDetails(**new_contact_details_data)
              db.add(new_contact_details) 

            if request.bank_details:
              existing_bank_details = db.query(EmployeeBankDetails).filter(EmployeeBankDetails.employee_id == id).first()
              if existing_bank_details:
                new_effective_from_date = datetime.utcnow()
                existing_bank_details.effective_to_date = new_effective_from_date - timedelta(days=1)
                db.add(existing_bank_details)

              new_bank_details_data = request.bank_details.dict(exclude={"effective_to_date"})
              new_bank_details_data["employee_id"] = id
              new_bank_details_data["effective_from_date"] = new_effective_from_date
              new_bank_details = EmployeeBankDetails(**new_bank_details_data)
              db.add(new_bank_details)   
              
              db.commit()
    except SQLAlchemyError as e:
        error_message = f"Failed to save Employee Master: {e}"
        raise HTTPException(status_code=500, detail=error_message)


def get_employee_master_details(db: Session):
    return db.query(Employee).all()

def get_present_address_details(db: Session):
    return db.query(EmployeePresentAddress).all()

def get_permanent_address_details(db: Session):
    return db.query(EmployeePermanentAddress).all()

def get_contact_details(db: Session):
    return db.query(EmployeeContactDetails).all()

def get_bank_details(db: Session):
    return db.query(EmployeeBankDetails).all()



def get_consultants(db: Session):
   is_consultant = db.query(Employee).filter(
         and_(
            Employee.is_consultant == 'yes',
            Employee.is_deleted  == "no"
        )
      ).all()
   
   if is_consultant is None:
        raise HTTPException(status_code=404, detail="No consultant employees found")
   return is_consultant




def delete_undelete_employee_master(db: Session, 
                           id: int,
                           Action: ActionType                           
                           ):
    employee_delete = db.query(Employee).filter(Employee.employee_id == id).first()

    if employee_delete is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if Action == ActionType.DELETE:
        employee_delete.is_deleted = 'yes'
        db.commit()
        return {
        "message": "Employee Master Deleted successfully",
        }

    elif Action == ActionType.UNDELETE: 
        employee_delete.is_deleted = 'no'
        db.commit()
        return {
        "message": "Employee Master Undeleted successfully",
        }
