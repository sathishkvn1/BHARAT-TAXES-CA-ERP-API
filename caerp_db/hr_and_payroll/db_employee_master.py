from fastapi import HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from caerp_db.common.models import EmployeeMaster, EmployeeBankDetails, EmployeeContactDetails, EmployeePermanentAddress, EmployeePresentAddress, UserBase, EmployeeEducationalQualification, EmployeeEmployementDetails, EmployeeExperience, EmployeeDocuments, EmployeeDependentsDetails, EmployeeEmergencyContactDetails, EmployeeSalaryDetails, EmployeeProfessionalQualification
from datetime import date,datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetails, EmployeeDocumentsSchema
from caerp_constants.caerp_constants import RecordActionType, ActionType
from typing import Union, List, Optional
from sqlalchemy import and_, func, insert
import os
import shutil


UPLOAD_EMP_DOCUMENTS = "uploads/employee_documents"

def save_employee_master(db: Session, request: EmployeeDetails, employeeid: int, id: int, user_id: int, Action: RecordActionType, schemas_to_add: Optional[str] = None):
  try:
    if (employeeid > 0 or employeeid < 0) and Action == RecordActionType.INSERT_ONLY:
      raise HTTPException(status_code=400, detail="ID should be 0 for inserting new employee master")
    
    if (employeeid <= 0 or employeeid is None) and (Action == RecordActionType.UPDATE_ONLY or Action == RecordActionType.UPDATE_AND_INSERT):
      raise HTTPException(status_code=400, detail="Please provide the employee ID to Update")
            
    updated_entities = {}
    # new employee master creation
    if employeeid == 0: 
      if Action == RecordActionType.INSERT_ONLY:
        # Check if employee number already exists
        existing_employee = db.query(EmployeeMaster).filter(EmployeeMaster.employee_number == request.employee_master.employee_number).first()
        if existing_employee:
          raise HTTPException(status_code=400, detail="employee number exists! Please give a different number")
      
        data = request.employee_master.dict()
      
        data["created_by"] = user_id
        # data["created_on"] = datetime.utcnow()
        data["approved_by"] = user_id
        data["approved_on"] = datetime.utcnow()
        result = EmployeeMaster(**data)
        db.add(result)
        db.commit()
        # db.refresh(result)      
    else:
      # updating existing employee master
      if Action == RecordActionType.UPDATE_ONLY:   
        update_emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employeeid).first()
        if update_emp is None:
          raise HTTPException(status_code=404, detail="Employee not found")
                
        if schemas_to_add is None:
          raise ValueError("schemas_to_add is required for updation")
      
        schema_names = EmployeeDetails.__fields__.keys()
        schemas_list = schemas_to_add.split(",")
        valid_options = [option for option in schemas_list if option in schema_names]
        
        if not valid_options:
          raise HTTPException(status_code=422, detail="Invalid selection")

        for option in valid_options: 
          if id is None and option != "employee_master":
            raise HTTPException(status_code=400, detail="Please provide the ID to Update") 

          if option == "employee_master" and request.employee_master:
            for field, value in request.employee_master.dict(exclude_unset=True).items():
              setattr(update_emp, field, value)
              update_emp.modified_by = user_id
              update_emp.modified_on = datetime.utcnow()   
            updated_entities['employee_master'] = update_emp 

          # updating present address detail table
          if option == "present_address" and request.present_address:  
            update_present_addr = db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).first()
            if update_present_addr is None:
              raise HTTPException(status_code=404, detail=f"present address with employee id {id} not found")
            for field, value in request.present_address.dict(exclude={"effective_from_date"}).items():
              setattr(update_present_addr, field, value)
            updated_entities['present_address'] = update_present_addr  

          # updating permanent address detail table
          if option == "permanent_address" and request.permanent_address: 
            update_per_addr = db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).first()
            if update_per_addr is None:
              raise HTTPException(status_code=404, detail=f"permanent address with employee id {id} not found")
            for field, value in request.permanent_address.dict(exclude={"effective_from_date"}).items():
              # update_per_addr.employee_id = id
              setattr(update_per_addr, field, value)
            updated_entities['permanent_address'] = update_per_addr

          # updating contact_details detail table
          if option == "contact_details" and request.contact_details:
            update_contact = db.query(EmployeeContactDetails).filter(EmployeeContactDetails.id == id).first()
            if update_contact is None:
              raise HTTPException(status_code=404, detail=f"contact details with employee id {id} not found")
            for field, value in request.contact_details.dict(exclude={"effective_from_date"}).items():
              # update_contact.employee_id = id
              setattr(update_contact, field, value)
            updated_entities['contact_details'] = update_contact

          # updating bank_details detail table
          if option == "bank_details" and request.bank_details: 
            update_bank = db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).first()
            if update_bank is None:
              raise HTTPException(status_code=404, detail=f"bank details with employee id {id} not found")
            for field, value in request.bank_details.dict(exclude={"effective_from_date"}).items():
              # update_bank.employee_id = id
              setattr(update_bank, field, value)
            updated_entities['bank_details'] = update_bank

          # updating educational qualification
          if option == "educational_qualification" and request.educational_qualification:
            update_qualification = db.query(EmployeeEducationalQualification).filter(EmployeeEducationalQualification.id == id).first()   
            if update_qualification is None:
              raise HTTPException(status_code=404, detail=f"educational qualification details with employee id {id} not found") 
            for edu_qual in request.educational_qualification:
              for field, value in edu_qual.dict(exclude={"effective_from_date"}).items():
                setattr(update_qualification, field, value)
              updated_entities['educational_qualification'] = update_qualification

          # updating employement details
          if option == "employement_details" and request.employement_details:
            update_employement = db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.id == id).first()  
            if update_employement is None:
              raise HTTPException(status_code=404, detail=f"employement details with employee id {id} not found") 
            for field, value in request.employement_details.dict(exclude={"effective_from_date"}).items():
              setattr(update_employement, field, value)
            updated_entities['employement_details'] = update_employement

          # updating salary details
          if option == "employee_salary" and request.employee_salary:
            update_salary = db.query(EmployeeSalaryDetails).filter(EmployeeSalaryDetails.id == id).first()  
            if update_salary is None:
              raise HTTPException(status_code=404, detail=f"salary details with employee id {id} not found") 
            for field, value in request.employee_salary.dict(exclude={"effective_from_date"}).items():
              setattr(update_salary, field, value)
            updated_entities['employee_salary'] = update_salary 

          # updating employee experience details 
          if option == "employee_experience" and request.employee_experience:
            update_experience = db.query(EmployeeExperience).filter(EmployeeExperience.id == id).first()  
            if update_experience is None:
              raise HTTPException(status_code=404, detail=f"experience details with employee id {id} not found")
            for emp_exp in request.employee_experience: 
              for field, value in emp_exp.dict(exclude={"effective_from_date"}).items():
                setattr(update_experience, field, value)
              updated_entities['employee_experience'] = update_experience

          # updating employee emergency contact details
          if option == "emergency_contact_details" and request.emergency_contact_details:
            update_emergency_contact = db.query(EmployeeEmergencyContactDetails).filter(EmployeeEmergencyContactDetails.id == id).first()  
            if update_emergency_contact is None:
              raise HTTPException(status_code=404, detail=f"emergency contact details with employee id {id} not found") 
            for field, value in request.emergency_contact_details.dict(exclude={"effective_from_date"}).items():
              setattr(update_emergency_contact, field, value)
            updated_entities['emergency_contact_details'] = update_emergency_contact  

          # updating employee dependent details
          if option == "dependent_details" and request.dependent_details:
            update_dependents = db.query(EmployeeDependentsDetails).filter(EmployeeDependentsDetails.id == id).first()  
            if update_dependents is None:
              raise HTTPException(status_code=404, detail=f"dependent details with employee id {id} not found") 
            for field, value in request.dependent_details.dict(exclude={"effective_from_date"}).items():
              setattr(update_dependents, field, value)
            updated_entities['dependent_details'] = update_dependents   

          # updating employee professional qualification
          if option == "professional_qualification" and request.professional_qualification:
            update_pro_qual = db.query(EmployeeProfessionalQualification).filter(EmployeeProfessionalQualification.id == id).first()  
            if update_pro_qual is None:
              raise HTTPException(status_code=404, detail=f"professional qualification details with employee id {id} not found")
            for pro_qual in request.professional_qualification: 
              for field, value in pro_qual.dict(exclude={"effective_from_date"}).items():
                setattr(update_pro_qual, field, value)
              updated_entities['professional_qualification'] = update_pro_qual    
         
        db.commit() 
        # return updated_entities
      
      # inserting new record to detail tables
      elif Action == RecordActionType.UPDATE_AND_INSERT:  
        update_emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employeeid).first()
        if update_emp is None:
          raise HTTPException(status_code=404, detail="Employee not found")          

        if schemas_to_add is None:
          raise ValueError("schemas_to_add is required for updation")
      
        schema_names = EmployeeDetails.__fields__.keys()
        schemas_list = schemas_to_add.split(",")
        valid_options = [option for option in schemas_list if option in schema_names]
        
        if not valid_options:
          raise HTTPException(status_code=422, detail="Invalid selection")
        
        for option in valid_options:
          new_effective_from_date = datetime.utcnow()

          if option == "present_address" and request.present_address:
            existing_present_address = db.query(EmployeePresentAddress).filter(EmployeePresentAddress.employee_id == employeeid).first()
            if existing_present_address:
              existing_present_address.effective_to_date = new_effective_from_date - timedelta(days=1)
              db.add(existing_present_address)
            
            new_present_address_data = request.present_address.dict()

            new_present_address_data["employee_id"] = employeeid
            new_present_address_data["created_by"] = user_id
            new_present_address_data["effective_from_date"] = new_effective_from_date
            new_present_address = EmployeePresentAddress(**new_present_address_data)
            db.add(new_present_address)
              
          if option == "permanent_address" and request.permanent_address:
            existing_permanent_address = db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.employee_id == employeeid).first()
            if existing_permanent_address:
              existing_permanent_address.effective_to_date = new_effective_from_date - timedelta(days=1)
              db.add(existing_permanent_address)

            new_permanent_address_data = request.permanent_address.dict()

            new_permanent_address_data["employee_id"] = employeeid
            new_permanent_address_data["created_by"] = user_id
            new_permanent_address_data["effective_from_date"] = new_effective_from_date
            new_permanent_address = EmployeePermanentAddress(**new_permanent_address_data)
            db.add(new_permanent_address)  
             
          if option == "contact_details" and request.contact_details:
            existing_contact_details = db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == employeeid).first()
            if existing_contact_details:
              existing_contact_details.effective_to_date = new_effective_from_date - timedelta(days=1)
              db.add(existing_contact_details)

            new_contact_details_data = request.contact_details.dict()
            
            new_contact_details_data["employee_id"] = employeeid
            new_contact_details_data["created_by"] = user_id
            new_contact_details_data["effective_from_date"] = new_effective_from_date
            new_contact_details = EmployeeContactDetails(**new_contact_details_data)
            db.add(new_contact_details) 

          if option == "bank_details" and request.bank_details:
            existing_bank_details = db.query(EmployeeBankDetails).filter(EmployeeBankDetails.employee_id == employeeid).first()
            if existing_bank_details:
              existing_bank_details.effective_to_date = new_effective_from_date - timedelta(days=1)
              db.add(existing_bank_details)

            new_bank_details_data = request.bank_details.dict()
            
            new_bank_details_data["employee_id"] = employeeid
            new_bank_details_data["created_by"] = user_id
            new_bank_details_data["effective_from_date"] = new_effective_from_date
            new_bank_details = EmployeeBankDetails(**new_bank_details_data)
            db.add(new_bank_details) 

          if option == "employement_details" and request.employement_details:
            existing_emp_details = db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.employee_id == employeeid).first()
            if existing_emp_details:
              existing_emp_details.effective_to_date = new_effective_from_date - timedelta(days=1)
              db.add(existing_emp_details)

            new_emp_details_data = request.employement_details.dict()

            new_emp_details_data["employee_id"] = employeeid
            new_emp_details_data["created_by"] = user_id
            new_emp_details_data["effective_from_date"] = new_effective_from_date
            new_emp_details = EmployeeEmployementDetails(**new_emp_details_data)
            db.add(new_emp_details)  

          if option == "employee_salary" and request.employee_salary:
            
            new_salary_details_data = request.employee_salary.dict()

            if new_salary_details_data.get('calculation_frequency_id') == 1:
              # Ensure effective_to_date is provided
              if not request.employee_salary.effective_to_date:
                raise HTTPException(status_code=400, detail="Effective to date is required for ONE_TIME frequency")

              # Ensure effective_to_date falls within the same month as effective_from_date
              if request.employee_salary.effective_to_date.month != request.employee_salary.effective_from_date.month:
                raise HTTPException(status_code=400, detail="Effective to date should fall within the same month as effective from date for ONE_TIME frequency")

              # Check if the component is available for the next month
              existing_record = db.query(EmployeeSalaryDetails).filter(
                 and_(
                      EmployeeSalaryDetails.employee_id == employeeid,
                      EmployeeSalaryDetails.component_id == request.employee_salary.component_id,
                      EmployeeSalaryDetails.effective_to_date > new_effective_from_date
                      )
                   ).first()

              if existing_record:
                raise HTTPException(status_code=400, detail="Salary component is already set for a future month")
            else:
              existing_salary_details = db.query(EmployeeSalaryDetails).filter(EmployeeSalaryDetails.employee_id == employeeid).first()
              if existing_salary_details:
                existing_salary_details.effective_to_date = new_effective_from_date - timedelta(days=1)
                db.add(existing_salary_details)  

            # Check calculation method and validate amount or percentage accordingly
            if new_salary_details_data.get('calculation_method_id') == 1 and request.employee_salary.amount == 0.0:
              raise HTTPException(status_code=400, detail="Amount cannot be zero for FIXED calculation method") 

            if new_salary_details_data.get('calculation_method_id') == 2 and request.employee_salary.percentage == 0.0:
              raise HTTPException(status_code=400, detail="Percentage cannot be zero for PERCENTAGE calculation method") 
          
            new_salary_details_data["employee_id"] = employeeid
            new_salary_details_data["created_by"] = user_id
            new_salary_details_data["effective_from_date"] = new_effective_from_date
            new_salary_details = EmployeeSalaryDetails(**new_salary_details_data)
            db.add(new_salary_details)  
          
          if option == "emergency_contact_details" and request.emergency_contact_details:
            exist_emergency_con_details = db.query(EmployeeEmergencyContactDetails).filter(EmployeeEmergencyContactDetails.employee_id == employeeid).first()
            if exist_emergency_con_details:
              exist_emergency_con_details.effective_date_to = new_effective_from_date - timedelta(days=1)
              db.add(exist_emergency_con_details)

            new_emergency_contact_data = request.emergency_contact_details.dict()

            new_emergency_contact_data["employee_id"] = employeeid
            new_emergency_contact_data["created_by"] = user_id
            new_emergency_contact_data["effective_date_from"] = new_effective_from_date
            new_emergency_contact = EmployeeEmergencyContactDetails(**new_emergency_contact_data)
            db.add(new_emergency_contact)

          if option == "dependent_details" and request.dependent_details:
            existing_dep_details = db.query(EmployeeDependentsDetails).filter(EmployeeDependentsDetails.employee_id == employeeid).first()
            if existing_dep_details:
              existing_dep_details.effective_date_to = new_effective_from_date - timedelta(days=1)
              db.add(existing_dep_details)

            new_dependent_data = request.dependent_details.dict()

            new_dependent_data["employee_id"] = employeeid
            new_dependent_data["created_by"] = user_id
            new_dependent_data["effective_date_from"] = new_effective_from_date
            new_dependent = EmployeeDependentsDetails(**new_dependent_data)
            db.add(new_dependent)  

          if option == "educational_qualification" and request.educational_qualification:
            for edu_qual in request.educational_qualification:
              edu_qualification_data = edu_qual.dict()
              edu_qualification_data["employee_id"] = employeeid
              edu_qualification_data["created_by"] = user_id
              db.add(EmployeeEducationalQualification(**edu_qualification_data))   

          if option == "employee_experience" and request.employee_experience:
            for emp_exp in request.employee_experience:
              emp_experience_data = emp_exp.dict()
              emp_experience_data["employee_id"] = employeeid
              emp_experience_data["created_by"] = user_id
              db.add(EmployeeExperience(**emp_experience_data))

          if option == "professional_qualification" and request.professional_qualification:
            for pro_qual in request.professional_qualification:
              pro_qual_data = pro_qual.dict()
              pro_qual_data["employee_id"] = employeeid
              pro_qual_data["created_by"] = user_id
              db.add(EmployeeProfessionalQualification(**pro_qual_data))    

        db.commit()
      
  except Exception as e:
     db.rollback()
     raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")   
  


def upload_employee_documents(db: Session, request: EmployeeDocumentsSchema, id: int, user_id: int, file: UploadFile = None):
  try: 
    emp_documents_data = request.dict()
    emp_documents_data["employee_id"] = id
    emp_documents_data["created_by"] = user_id
    
    result = EmployeeDocuments(**emp_documents_data)
    db.add(result)
    db.commit() 
    db.refresh(result)

    # Handle file upload
    if file:
        file_path = os.path.join(UPLOAD_EMP_DOCUMENTS, f"{result.id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # result.document_number = file_path
        db.commit()
    # return result         
  except Exception as e:
     db.rollback()
     raise HTTPException(status_code=500, detail=f"Failed to upload the file: {str(e)}") 



def get_employee_master_details(db: Session):
    return db.query(EmployeeMaster).all()

def get_present_address_details(db: Session):
    return db.query(EmployeePresentAddress).all()

def get_permanent_address_details(db: Session):
    return db.query(EmployeePermanentAddress).all()

def get_contact_details(db: Session):
    return db.query(EmployeeContactDetails).all()

def get_bank_details(db: Session):
    return db.query(EmployeeBankDetails).all()

def get_employement_details(db: Session):
    return db.query(EmployeeEmployementDetails).all()

def get_salary_details(db: Session):
    return db.query(EmployeeSalaryDetails).all()

def get_qualification_details(db: Session):
    return db.query(EmployeeEducationalQualification).all()

def get_experience_details(db: Session):
    return db.query(EmployeeExperience).all()

def get_document_details(db: Session):
    return db.query(EmployeeDocuments).all()

def get_emergency_contact_details(db: Session):
    return db.query(EmployeeEmergencyContactDetails).all()

def get_dependent_details(db: Session):
    return db.query(EmployeeDependentsDetails).all()



def get_consultants(db: Session):
   is_consultant = db.query(EmployeeEmployementDetails).filter(
         and_(
            EmployeeEmployementDetails.is_consultant == 'yes',
            EmployeeEmployementDetails.is_deleted  == "no"
        )
      ).all()
   
   if is_consultant is None:
        raise HTTPException(status_code=404, detail="No consultant employees found")
   return is_consultant



def delete_employee_details(db: Session, employeeid: int, id: int, user_id: int, Action: ActionType, schema_to_delete: str):
   employee_found = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employeeid).first()
   if employee_found is None:
          raise HTTPException(status_code=404, detail=f"Employee with id {id} not found")
   
   if Action == ActionType.DELETE:
     schema_mappings = {
        "employee_master": db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employeeid).all(),
        "present_address": db.query(EmployeePresentAddress).filter(EmployeePresentAddress.employee_id == employeeid).all(),
        "permanent_address": db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.employee_id == employeeid).all(),
        "contact_details": db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == employeeid).all(),
        "bank_details": db.query(EmployeeBankDetails).filter(EmployeeBankDetails.employee_id == employeeid).all(),
        "employement_details": db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.employee_id == employeeid).all(),
        "emergency_contact_details": db.query(EmployeeEmergencyContactDetails).filter(EmployeeEmergencyContactDetails.employee_id == employeeid).all(),
        "dependent_details": db.query(EmployeeDependentsDetails).filter(EmployeeDependentsDetails.employee_id == employeeid).all(),
        "employee_salary":  db.query(EmployeeSalaryDetails).filter(EmployeeSalaryDetails.employee_id == employeeid).all(),
        "educational_qualification": db.query(EmployeeEducationalQualification).filter(EmployeeEducationalQualification.employee_id == employeeid).all(),
        "employee_experience": db.query(EmployeeExperience).filter(EmployeeExperience.employee_id == employeeid).all(),
        "employee_documents": db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employeeid).all(),
        "professional_qualification": db.query(EmployeeProfessionalQualification).filter(EmployeeProfessionalQualification.employee_id == employeeid).all()
        }
     
     if schema_to_delete == "employee_master":
       # Delete all related detail table entries
       for table_name, query_results in schema_mappings.items():
         if table_name != "employee_master" and query_results:
           for item_to_update in query_results:
             item_to_update.is_deleted = 'yes'
             item_to_update.deleted_by = user_id
             item_to_update.deleted_on = datetime.utcnow()

       # Delete the master table entry
       employee_found.is_deleted = 'yes'
       employee_found.deleted_by = user_id
       employee_found.deleted_on = datetime.utcnow()
     else:
       # Delete a specific detail table entry 
       if id is None :
         raise HTTPException(status_code=400, detail="Please provide the ID to delete")
       
       schema_mapping_details = {
        "present_address": db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).first(),
        "permanent_address": db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).first(),
        "contact_details": db.query(EmployeeContactDetails).filter(EmployeeContactDetails.id == id).first(),
        "bank_details": db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).first(),
        "employement_details": db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.id == id).first(),
        "emergency_contact_details": db.query(EmployeeEmergencyContactDetails).filter(EmployeeEmergencyContactDetails.id == id).first(),
        "dependent_details": db.query(EmployeeDependentsDetails).filter(EmployeeDependentsDetails.id == id).first(),
        "employee_salary":  db.query(EmployeeSalaryDetails).filter(EmployeeSalaryDetails.id == id).first(),
        "educational_qualification": db.query(EmployeeEducationalQualification).filter(EmployeeEducationalQualification.id == id).first(),
        "employee_experience": db.query(EmployeeExperience).filter(EmployeeExperience.id == id).first(),
        "employee_documents": db.query(EmployeeDocuments).filter(EmployeeDocuments.id == id).first(),
        "professional_qualification": db.query(EmployeeProfessionalQualification).filter(EmployeeProfessionalQualification.id == id).first()
        }

       item_to_delete = schema_mapping_details.get(schema_to_delete)
       if item_to_delete:
         item_to_delete.is_deleted = 'yes'
         item_to_delete.deleted_by = user_id
         item_to_delete.deleted_on = datetime.utcnow()
       else:
         raise HTTPException(status_code=400, detail=f"Invalid schema_to_delete: {schema_to_delete}")
     db.commit()  
   elif Action == ActionType.UNDELETE:
     schema_mappings = {
        "employee_master": db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employeeid).first(),
        "present_address": db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).first(),
        "permanent_address": db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).first(),
        "contact_details": db.query(EmployeeContactDetails).filter(EmployeeContactDetails.id == id).first(),
        "bank_details": db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).first(),
        "employement_details": db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.id == id).first(),
        "emergency_contact_details": db.query(EmployeeEmergencyContactDetails).filter(EmployeeEmergencyContactDetails.id == id).first(),
        "dependent_details": db.query(EmployeeDependentsDetails).filter(EmployeeDependentsDetails.id == id).first(),
        "employee_salary":  db.query(EmployeeSalaryDetails).filter(EmployeeSalaryDetails.id == id).first(),
        "educational_qualification": db.query(EmployeeEducationalQualification).filter(EmployeeEducationalQualification.id == id).first(),
        "employee_experience": db.query(EmployeeExperience).filter(EmployeeExperience.id == id).first(),
        "employee_documents": db.query(EmployeeDocuments).filter(EmployeeDocuments.id == id).first(),
        "professional_qualification": db.query(EmployeeProfessionalQualification).filter(EmployeeProfessionalQualification.id == id).first()
        }

     item_to_undelete = schema_mappings.get(schema_to_delete)
     if item_to_undelete:
       item_to_undelete.is_deleted = 'no'
      #  item_to_undelete.deleted_by = user_id
      #  item_to_undelete.deleted_on = datetime.utcnow()
       db.commit()
     else:
       raise HTTPException(status_code=400, detail=f"Invalid schema_to_undelete: {schema_to_delete}")    

