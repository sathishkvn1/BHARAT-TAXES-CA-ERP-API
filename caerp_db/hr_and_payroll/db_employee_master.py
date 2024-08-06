
from fastapi import HTTPException, Path, Query, File, UploadFile
from sqlalchemy.orm import Session
from caerp_db.common.models import EmployeeMaster, Gender, MaritalStatus, NationalityDB,UserBase,UserRole, EmployeeBankDetails, EmployeeContactDetails, EmployeePermanentAddress, EmployeePresentAddress, EmployeeEducationalQualification, EmployeeEmployementDetails, EmployeeExperience, EmployeeDocuments, EmployeeDependentsDetails, EmployeeEmergencyContactDetails, EmployeeSalaryDetails, EmployeeProfessionalQualification
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeAddressDetailsSchema, EmployeeDetails,EmployeeDocumentsSchema, EmployeeEducationalQualficationSchema
from caerp_constants.caerp_constants import RecordActionType, ActionType, ActiveStatus, ApprovedStatus
from typing import Union, List, Optional
from sqlalchemy import and_, func, insert, update , text, or_
from sqlalchemy.sql.operators import is_
from caerp_db.common.models import HrDepartmentMaster, HrDesignationMaster, HrEmployeeCategory
from caerp_db.hash import Hash
import os
import shutil
from pathlib import Path 


UPLOAD_EMP_DOCUMENTS = "uploads/employee_documents"


def get_next_employee_number(db: Session) -> str:
    # Get the maximum employee number
    max_employee_number = db.query(func.max(EmployeeMaster.employee_number)).scalar()
    if max_employee_number is None:
        # If there are no employees yet, start with EMP001
        next_employee_number = 100
    else:
        next_employee_number = int(max_employee_number) + 1
        next_employee_number_str = str(next_employee_number)
    return next_employee_number_str



def save_employee_master_new(db: Session, request: EmployeeDetails, id: int, user_id: int, employee_profile_component: Optional[str] = None):
    try:
        if id == 0:
            # Insertion logic
            data = request.employee_master.dict()
            data["created_by"] = user_id
            data["is_approved"] = 'yes'
            data["approved_by"] = user_id
            data["approved_on"] = datetime.utcnow()
            data['employee_number'] = get_next_employee_number(db)

            insert_stmt = insert(EmployeeMaster).values(**data)
            result = db.execute(insert_stmt)
            db.commit()
            emp_id = result.lastrowid

            contact_details_data = request.contact_details.dict()
            contact_details_data['effective_from_date'] = datetime.utcnow().date()
            contact_details_data['employee_id'] = emp_id

            insert_contact_stmt = insert(EmployeeContactDetails).values(**contact_details_data)
            db.execute(insert_contact_stmt)
            db.commit()

            users_new_dict = request.employee_security_credentials.dict()
            log_password = Hash.bcrypt(users_new_dict['login_password'])
            password_reset_date = datetime.utcnow().date() + relativedelta(months=3)

            users_new_data = {
                "employee_id": emp_id,
                "user_name": users_new_dict['user_name'],
                "login_password": log_password,
                "edit_password": log_password,
                "delete_password": log_password,
                "security_password": log_password,
                "is_active": 'yes',
                "password_reset_date": password_reset_date
            }
            insert_user_log_stmt = insert(UserBase).values(**users_new_data)
            db.execute(insert_user_log_stmt)
            db.commit()

            for role_id in request.user_roles.role_id:
                user_role_data = {
                    "employee_id": emp_id,
                    "role_id": role_id
                }
                insert_user_role_stmt = insert(UserRole).values(**user_role_data)
                db.execute(insert_user_role_stmt)
            db.commit()

            employement_details_data = request.employement_details.dict()
            employement_details_data["employee_id"] = emp_id
            employement_details_data['effective_from_date'] = datetime.utcnow().date()
            employement_details_data["created_by"] = user_id
            employement_details_data["approved_by"] = user_id
            employement_details_data["approved_on"] = datetime.utcnow()

            insert_emp_det = insert(EmployeeEmployementDetails).values(**employement_details_data)
            db.execute(insert_emp_det)
            db.commit()

            return emp_id

        else:
            # Update logic based on employee_profile_component
            update_emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == id, EmployeeMaster.is_deleted == 'no').first()
            if not update_emp:
                raise HTTPException(status_code=404, detail="Employee not found")

            if employee_profile_component is None:
                raise ValueError("Employee profile component is required for updation")

            components = employee_profile_component.split(',')

            # Update employee_master if present in the components
            if 'employee_master' in components and request.employee_master:
                update_data = request.employee_master.dict(exclude_unset=True)
                db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == id).update(update_data)
                db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == id).update({
                    "modified_by": user_id,
                    "modified_on": datetime.utcnow()
                })

            # Update contact_details if present in the components
            if 'contact_details' in components and request.contact_details:
                contact_details_data = request.contact_details.dict(exclude_unset=True)
                db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == id).update(contact_details_data)

            # Update employement_details if present in the components
            if 'employement_details' in components and request.employement_details:
                employement_details_data = request.employement_details.dict(exclude_unset=True)
                db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.employee_id == id).update(employement_details_data)

            # You can add more conditions for other components if needed

            db.commit()

            return {
                "success": True,
                "message": "Updated successfully"
            }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


# def save_employee_master_new(db: Session, request: EmployeeDetails, id: int, user_id: int, employee_profile_component: Optional[str] = None):
#     try:
#         if id == 0:
#             # Insertion logic
#             data = request.employee_master.dict()
#             data["created_by"] = user_id
#             data["is_approved"] = 'yes'
#             data["approved_by"] = user_id
#             data["approved_on"] = datetime.utcnow()
#             data['employee_number'] = get_next_employee_number(db)

#             insert_stmt = insert(EmployeeMaster).values(**data)
#             result = db.execute(insert_stmt)
#             db.commit()
#             emp_id = result.lastrowid

#             contact_details_data = request.contact_details.dict()
#             contact_details_data['effective_from_date'] = datetime.utcnow().date()
#             contact_details_data['employee_id'] = emp_id

#             insert_contact_stmt = insert(EmployeeContactDetails).values(**contact_details_data)
#             db.execute(insert_contact_stmt)
#             db.commit()

#             users_new_dict = request.employee_security_credentials.dict()
#             log_password = Hash.bcrypt(users_new_dict['login_password'])
#             password_reset_date = datetime.utcnow().date() + relativedelta(months=3)

#             users_new_data = {
#                 "employee_id": emp_id,
#                 "user_name": users_new_dict['user_name'],
#                 "login_password": log_password,
#                 "edit_password": log_password,
#                 "delete_password": log_password,
#                 "security_password": log_password,
#                 "is_active": 'yes',
#                 "password_reset_date": password_reset_date
#             }
#             insert_user_log_stmt = insert(UserBase).values(**users_new_data)
#             db.execute(insert_user_log_stmt)
#             db.commit()

#             for role_id in request.user_roles.role_id:
#                 user_role_data = {
#                     "employee_id": emp_id,
#                     "role_id": role_id
#                 }
#                 insert_user_role_stmt = insert(UserRole).values(**user_role_data)
#                 db.execute(insert_user_role_stmt)
#             db.commit()

#             employement_details_data = request.employement_details.dict()
#             employement_details_data["employee_id"] = emp_id
#             employement_details_data['effective_from_date'] = datetime.utcnow().date()
#             employement_details_data["created_by"] = user_id
#             employement_details_data["approved_by"] = user_id
#             employement_details_data["approved_on"] = datetime.utcnow()

#             insert_emp_det = insert(EmployeeEmployementDetails).values(**employement_details_data)
#             db.execute(insert_emp_det)
#             db.commit()

#             return emp_id

#         else:
#             # Update logic based on employee_profile_component
#             update_emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == id, EmployeeMaster.is_deleted == 'no').first()
#             if not update_emp:
#                 raise HTTPException(status_code=404, detail="Employee not found")

#             if employee_profile_component is None:
#                 raise ValueError("Employee profile component is required for updation")

#             components = employee_profile_component.split(',')

#             # Update employee_master if present in the components
#             if 'employee_master' in components and request.employee_master:
#                 update_data = request.employee_master.dict(exclude_unset=True)
#                 db.query(EmployeeMaster).filter(EmployeeMaster.id == id).update(update_data)
#                 db.query(EmployeeMaster).filter(EmployeeMaster.id == id).update({
#                     "modified_by": user_id,
#                     "modified_on": datetime.utcnow()
#                 })

#             # Update contact_details if present in the components
#             if 'contact_details' in components and request.contact_details:
#                 contact_details_data = request.contact_details.dict(exclude_unset=True)
#                 db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == id).update(contact_details_data)

#             # Update employement_details if present in the components
#             if 'employement_details' in components and request.employement_details:
#                 employement_details_data = request.employement_details.dict(exclude_unset=True)
#                 db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.employee_id == id).update(employement_details_data)

#             # You can add more conditions for other components if needed

#             db.commit()

#             return {
#                 "success": True,
#                 "message": "Updated successfully"
#             }

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")



def save_employee_master(db: Session, request: EmployeeDetails, employee_id: int, id:  List[int], user_id: int, Action: RecordActionType, employee_profile_component: Optional[str] = None):
   try:
      if Action == RecordActionType.INSERT_ONLY:
        if employee_id != 0:
          raise HTTPException(status_code=400, detail="ID should be 0 for inserting new employee master")
        
        try:    
          data = request.employee_master.dict()
          data["created_by"] = user_id
          data["is_approved"] = 'yes'
          data["approved_by"] = user_id
          data["approved_on"] = datetime.utcnow()
          data['employee_number'] = get_next_employee_number(db)

          #  with db.begin():
          insert_stmt = insert(EmployeeMaster).values(**data)
          result = db.execute(insert_stmt)
          db.commit()
    
          emp_id = result.lastrowid         

          contact_details_data = request.contact_details.dict()
          contact_details_data['effective_from_date'] = datetime.utcnow().date()
          contact_details_data['employee_id'] = emp_id

          insert_contact_stmt = insert(EmployeeContactDetails).values(**contact_details_data)
          db.execute(insert_contact_stmt)
          db.commit()

          users_new_dict = request.employee_security_credentials.dict()
          # Insert into users_new table
          log_password  = Hash.bcrypt(users_new_dict['login_password'])
          password_reset_date = datetime.utcnow().date() + relativedelta(months=3)

          users_new_data = {
              "employee_id": emp_id,
              "user_name": users_new_dict['user_name'],
              "login_password": log_password,  # Ensure this is securely hashed before storage
              "edit_password":  log_password,
              "delete_password": log_password,
              "security_password": log_password,
              "is_active": 'yes',
              "password_reset_date" :password_reset_date
            }
          insert_user_log_stmt = insert(UserBase).values(**users_new_data)
          db.execute(insert_user_log_stmt)
          db.commit()

          for role_id in request.user_roles.role_id :
            user_role_data = {
              "employee_id": emp_id,
              "role_id": role_id
              }
            insert_user_role_stmt = insert(UserRole).values(**user_role_data)
            db.execute(insert_user_role_stmt)
          db.commit()

          employement_details_data = request.employement_details.dict()

          employement_details_data["employee_id"] = emp_id
          employement_details_data['effective_from_date'] = datetime.utcnow().date()
          employement_details_data["created_by"] = user_id
          employement_details_data["approved_by"] = user_id
          employement_details_data["approved_on"] = datetime.utcnow()  

          insert_emp_det = insert(EmployeeEmployementDetails).values(**employement_details_data)
          db.execute(insert_emp_det)
          db.commit()

          return emp_id
        except SQLAlchemyError as e:
          db.rollback()
          raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
      
      
      
      elif Action in {RecordActionType.UPDATE_ONLY, RecordActionType.UPDATE_AND_INSERT}:
        if employee_id <= 0:
          raise HTTPException(status_code=400, detail="Please provide the employee ID to Update")
        
        update_emp = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id, EmployeeMaster.is_deleted == 'no').first()
        if not update_emp:
          raise HTTPException(status_code=404, detail="Employee not found")

        if employee_profile_component is None:
          raise ValueError("Employee profile component is required for updation")

        schema_names = EmployeeDetails.__fields__.keys()
        schemas_list = employee_profile_component.split(",")
        valid_options = [option for option in schemas_list if option in schema_names]

        if not valid_options:
          raise HTTPException(status_code=422, detail="Invalid employee profile component")

        updated_entities = {}

        if "employee_master" in valid_options and request.employee_master:
          for field, value in request.employee_master.dict(exclude_unset=True).items():
            setattr(update_emp, field, value)
            update_emp.modified_by = user_id
            update_emp.modified_on = datetime.utcnow()
          updated_entities['employee_master'] = update_emp

        if Action == RecordActionType.UPDATE_ONLY:
          for option in valid_options:
            if option != "employee_master" and id is None:
              raise HTTPException(status_code=400, detail="Please provide the ID to Update")
            
            if option == "present_address" and request.present_address:
              update_detail_record(db, EmployeePresentAddress, request.present_address, id, updated_entities, "present_address")
            if option == "permanent_address" and request.permanent_address:
              update_detail_record(db, EmployeePermanentAddress, request.permanent_address, id, updated_entities, "permanent_address")  
            if option == "contact_details" and request.contact_details:
              update_detail_record(db, EmployeeContactDetails, request.contact_details, id, updated_entities, "contact_details")
            if option == "bank_details" and request.bank_details:
              update_detail_record(db, EmployeeBankDetails, request.bank_details, id, updated_entities, "bank_details")
            if option == "employement_details" and request.employement_details:
              update_detail_record(db, EmployeeEmployementDetails, request.employement_details, id, updated_entities, "employement_details") 
            if option == "emergency_contact_details" and request.emergency_contact_details:
              update_detail_record(db, EmployeeEmergencyContactDetails, request.emergency_contact_details, id, updated_entities, "emergency_contact_details")
            if option == "dependent_details" and request.dependent_details:
              update_detail_record(db, EmployeeDependentsDetails, request.dependent_details, id, updated_entities, "dependent_details")     
            if option == "educational_qualification" and request.educational_qualification:
              update_multiple_detail_records(db, EmployeeEducationalQualification, request.educational_qualification, id, updated_entities, "educational_qualification")
            if option == "employee_experience" and request.employee_experience:
              update_multiple_detail_records(db, EmployeeExperience, request.employee_experience, id, updated_entities, "employee_experience")
            if option == "employee_documents" and request.employee_documents:
              update_multiple_detail_records(db, EmployeeDocuments, request.employee_documents, id, updated_entities, "employee_documents")
            if option == "professional_qualification" and request.professional_qualification:
              update_multiple_detail_records(db, EmployeeProfessionalQualification, request.professional_qualification, id, updated_entities, "professional_qualification")  
            if option == "employee_security_credentials" and request.employee_security_credentials:
              existing_credential = db.query(UserBase).filter(UserBase.employee_id == employee_id).first()  
              if existing_credential is None:
                raise HTTPException(status_code=404, detail=f"Security credentials with  id {id} not found") 
              credential_data = request.employee_security_credentials.dict()
              # password_reset_date = datetime.utcnow().date() + relativedelta(months=3)
            
              new_credential_data = {
                        "login_password" : Hash.bcrypt(credential_data["login_password"]),
                        "edit_password"   : Hash.bcrypt(credential_data["edit_password"]),
                        "delete_password"   : Hash.bcrypt(credential_data["delete_password"]),
                        "security_password"   : Hash.bcrypt(credential_data["security_password"]),
                        # "password_reset_date" : password_reset_date

               }
              for field, value in new_credential_data.items():
                setattr(existing_credential, field, value)
              updated_entities['security_credentials'] = existing_credential

            if option == "user_roles" and request.user_roles:
              update_query = text(
                "UPDATE user_roles SET is_deleted='yes' "
              "WHERE employee_id = :employee_id "                     
              )
              db.execute(update_query, {'employee_id': employee_id})
              for role_id in request.user_roles.role_id:
                existing_roles = db.query(UserRole).filter(UserRole.employee_id == employee_id,
                                   UserRole.role_id == role_id).first()  
                if existing_roles:
                  user_role_data = {
                      "employee_id": employee_id,
                      "role_id": role_id,
                        "is_deleted" : 'no',
                        "modified_on": datetime.utcnow()
                  }
                  for key, value in user_role_data.items():
                    setattr(existing_roles, key, value)
                  updated_entities['user_roles'] = existing_roles    
                  db.commit()    
                else:
                  user_role_data = {
                          "employee_id": employee_id,
                          "role_id": role_id,
                          "created_on": datetime.utcnow()
                  }
                insert_user_role_stmt = insert(UserRole).values(**user_role_data)
                db.execute(insert_user_role_stmt)
        elif Action == RecordActionType.UPDATE_AND_INSERT:
          for option in valid_options:
            if option == "present_address" and request.present_address:
              insert_detail_record(db, EmployeePresentAddress, request.present_address, employee_id, user_id)
            if option == "permanent_address" and request.permanent_address:
              insert_detail_record(db, EmployeePermanentAddress, request.permanent_address, employee_id, user_id)  
            if option == "contact_details" and request.contact_details:
              insert_detail_record(db, EmployeeContactDetails, request.contact_details, employee_id, user_id)
            if option == "bank_details" and request.bank_details:
              insert_detail_record(db, EmployeeBankDetails, request.bank_details, employee_id, user_id)
            if option == "employement_details" and request.employement_details:
              insert_detail_record(db, EmployeeEmployementDetails, request.employement_details, employee_id, user_id) 
            if option == "emergency_contact_details" and request.emergency_contact_details:
              insert_detail_record(db, EmployeeEmergencyContactDetails, request.emergency_contact_details, employee_id, user_id)   
            if option == "dependent_details" and request.dependent_details:
              insert_detail_record(db, EmployeeDependentsDetails, request.dependent_details, employee_id, user_id)  
            if option == "educational_qualification" and request.educational_qualification:
              insert_multiple_detail_records(db, EmployeeEducationalQualification, request.educational_qualification, employee_id, user_id)
            if option == "employee_experience" and request.employee_experience:
              insert_multiple_detail_records(db, EmployeeExperience, request.employee_experience, employee_id, user_id)
            if option == "professional_qualification" and request.professional_qualification:
              insert_multiple_detail_records(db, EmployeeProfessionalQualification, request.professional_qualification, employee_id, user_id)  

        db.commit()
   except Exception as e:
     db.rollback()
     raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def update_detail_record(db, model, request_data, record_id, updated_entities, entity_name):
  single_id = record_id[0]
  detail_record = db.query(model).filter(model.id == single_id, model.is_deleted == 'no').first()
  if not detail_record:
    raise HTTPException(status_code=404, detail=f"{entity_name} with ID {single_id} not found")
  for field, value in request_data.dict(exclude={"effective_to_date"}).items():
     setattr(detail_record, field, value)
  updated_entities[entity_name] = detail_record

def update_multiple_detail_records(db, model, request_data_list, record_ids, updated_entities, entity_name):
    for record_id, request_data in zip(record_ids, request_data_list):
      det_multiple_record = db.query(model).filter(model.id == record_id, model.is_deleted == 'no').first()
      if det_multiple_record is None:
        raise HTTPException(status_code=404, detail=f"{entity_name} with ID {record_id} not found")
      for field, value in request_data.dict(exclude_unset=True).items():
        setattr(det_multiple_record, field, value)
      updated_entities[entity_name] = det_multiple_record


def insert_detail_record(db, model, request_data, employee_id, user_id):
   detail_data = request_data.dict()
   
   # Set the effective_from_date to the current date
   current_effective_from_date = datetime.utcnow().date()
   detail_data["effective_from_date"] = current_effective_from_date

   existing_detail = db.query(model).filter(model.employee_id == employee_id, model.is_deleted == 'no', model.effective_to_date.is_(None)).first()
   if existing_detail:
     effective_to_date = current_effective_from_date - timedelta(days=1)

     # Check if effective_to_date is less than effective_from_date
     if effective_to_date < existing_detail.effective_from_date:
       raise HTTPException(status_code=400, detail="The calculated effective_to_date is less than the existing effective_from_date.")
     db.execute(
            update(model)
            .where(
                model.employee_id == existing_detail.employee_id,
                model.effective_to_date.is_(None)
            )
            .values(effective_to_date=effective_to_date))
   
   detail_data["employee_id"] = employee_id
   detail_data["created_by"] = user_id

   if hasattr(model, 'approved_by'):
     detail_data["approved_by"] = user_id
   if hasattr(model, 'approved_on'):
     detail_data["approved_on"] = datetime.utcnow()  
   new_detail = model(**detail_data)
   db.add(new_detail)

def insert_multiple_detail_records(db, model, request_data_list, employee_id, user_id):
   for request_data in request_data_list:
     insert_detail = request_data.dict()
     insert_detail["employee_id"] = employee_id

     if hasattr(model, 'created_by'):
       insert_detail["created_by"] = user_id
     db.add(model(**insert_detail))

  


# def upload_employee_documents(db: Session, request: EmployeeDocumentsSchema, employee_id: int, user_id: int, file: UploadFile = None):
#     try:
#         emp_documents_data = request.dict()
#         emp_documents_data["employee_id"] = employee_id
#         emp_documents_data["created_by"] = user_id
#         result = EmployeeDocuments(**emp_documents_data)
#         db.add(result)
#         db.commit()
#         db.refresh(result)
#         # Handle file upload
#         if file:
          
#             file_path = os.path.join(UPLOAD_EMP_DOCUMENTS, str(result.id))

#             os.makedirs(os.path.dirname(file_path), exist_ok=True)
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
#             db.commit()
#         return result
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Failed to upload the file: {str(e)}")



def upload_employee_documents(db: Session, request: EmployeeDocumentsSchema, employee_id: int, user_id: int, file: UploadFile = None):
    try:
        emp_documents_data = request.dict()
        emp_documents_data["employee_id"] = employee_id
        emp_documents_data["created_by"] = user_id

        result = EmployeeDocuments(**emp_documents_data)
        db.add(result)
        db.commit()
        db.refresh(result)

        # Handle file upload
        if file:
            # Extract file extension
            file_extension = Path(file.filename).suffix

            # Construct file path with the extension
            file_path = os.path.join(UPLOAD_EMP_DOCUMENTS, f"{result.id}{file_extension}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the file with the extension
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
 
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload the file: {str(e)}")







def delete_employee_details(db: Session, employee_id: int, id: int, user_id: int, Action: ActionType, employee_profile_component: str):
   employee_found = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first()
   if employee_found is None:
          raise HTTPException(status_code=404, detail=f"Employee with id {id} not found")
   
   if employee_profile_component is None:
     raise ValueError("Employee profile component is required for updation")

   schema_names = EmployeeDetails.__fields__.keys()
   schemas_list = employee_profile_component.split(",")
   valid_options = [option for option in schemas_list if option in schema_names]

   if not valid_options:
     raise HTTPException(status_code=422, detail="Invalid employee profile component")

   if Action == ActionType.DELETE:
     schema_mappings = {
        "employee_master": db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).all(),
        "present_address": db.query(EmployeePresentAddress).filter(EmployeePresentAddress.employee_id == employee_id).all(),
        "permanent_address": db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.employee_id == employee_id).all(),
        "contact_details": db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == employee_id).all(),
        "bank_details": db.query(EmployeeBankDetails).filter(EmployeeBankDetails.employee_id == employee_id).all(),
        "employement_details": db.query(EmployeeEmployementDetails).filter(EmployeeEmployementDetails.employee_id == employee_id).all(),
        "emergency_contact_details": db.query(EmployeeEmergencyContactDetails).filter(EmployeeEmergencyContactDetails.employee_id == employee_id).all(),
        "dependent_details": db.query(EmployeeDependentsDetails).filter(EmployeeDependentsDetails.employee_id == employee_id).all(),
        "employee_salary":  db.query(EmployeeSalaryDetails).filter(EmployeeSalaryDetails.employee_id == employee_id).all(),
        "educational_qualification": db.query(EmployeeEducationalQualification).filter(EmployeeEducationalQualification.employee_id == employee_id).all(),
        "employee_experience": db.query(EmployeeExperience).filter(EmployeeExperience.employee_id == employee_id).all(),
        "employee_documents": db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employee_id).all(),
        "professional_qualification": db.query(EmployeeProfessionalQualification).filter(EmployeeProfessionalQualification.employee_id == employee_id).all()
        }
     
     if employee_profile_component == "employee_master":
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

       item_to_delete = schema_mapping_details.get(employee_profile_component)
       if item_to_delete:
         item_to_delete.is_deleted = 'yes'
         item_to_delete.deleted_by = user_id
         item_to_delete.deleted_on = datetime.utcnow()
     db.commit()  
   elif Action == ActionType.UNDELETE:
     schema_mappings = {
        "employee_master": db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first(),
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

     item_to_undelete = schema_mappings.get(employee_profile_component)
     if item_to_undelete:
       item_to_undelete.is_deleted = 'no'
      #  item_to_undelete.deleted_by = user_id
      #  item_to_undelete.deleted_on = datetime.utcnow()
       db.commit()
    #  else:
    #    raise HTTPException(status_code=400, detail=f"Invalid profile component: {employee_profile_component}")   



def search_employee_master_details(db: Session, user_status: Optional[ActiveStatus], approval_status: Optional[ApprovedStatus], category: Optional[Union[str,int]] = "ALL", department: Optional[Union[str,int]] = "ALL", designation: Optional[Union[str,int]] = "ALL", is_consultant: Optional[str] = None, search: Optional[str] = None):
    query = db.query(
        EmployeeMaster.employee_id,
        EmployeeMaster.first_name,
        EmployeeMaster.middle_name,
        EmployeeMaster.last_name,
        EmployeeMaster.gender_id,
        Gender.gender,
        EmployeeMaster.nationality_id,
        NationalityDB.nationality_name, 
        EmployeeMaster.date_of_birth,
        EmployeeMaster.blood_group,
        EmployeeMaster.nationality_id,
        EmployeeMaster.marital_status_id,
        MaritalStatus.marital_status, 
        EmployeeMaster.joining_date,
        EmployeeEmployementDetails.employee_category_id,
        HrEmployeeCategory.category_name,
        EmployeeEmployementDetails.department_id,
        HrDepartmentMaster.department_name,
        EmployeeEmployementDetails.designation_id,
        HrDesignationMaster.designation,
        EmployeeContactDetails.personal_mobile_number,
        EmployeeContactDetails.personal_email_id,
        EmployeeContactDetails.remarks,
        EmployeeEmployementDetails.is_consultant,
        EmployeeMaster.is_approved,
        UserBase.is_active
    ).join(
        EmployeeEmployementDetails, EmployeeMaster.employee_id == EmployeeEmployementDetails.employee_id, isouter=True
  
    ).join(
        HrEmployeeCategory, EmployeeEmployementDetails.employee_category_id == HrEmployeeCategory.id, isouter=True
    ).join(
        HrDepartmentMaster, EmployeeEmployementDetails.department_id == HrDepartmentMaster.id, isouter=True
    ).join(
        HrDesignationMaster, EmployeeEmployementDetails.designation_id == HrDesignationMaster.id, isouter=True
    ).join(
       UserBase, EmployeeMaster.employee_id == UserBase.employee_id, isouter = True
    ).join(
        EmployeeContactDetails, EmployeeMaster.employee_id == EmployeeContactDetails.employee_id, isouter=True
    ).join(
        Gender, EmployeeMaster.gender_id == Gender.id, isouter=True  
    ).join(
        NationalityDB, EmployeeMaster.nationality_id == NationalityDB.id, isouter=True  # Added join 
    ).join(
        MaritalStatus, EmployeeMaster.marital_status_id == MaritalStatus.id, isouter=True  # Added 
    )

    # Applying filters at the end of the join statements
    if category and category != "ALL":
      query = query.filter(or_(
                           HrEmployeeCategory.id == category,
                           HrEmployeeCategory.category_name == category
                         ))
    if department and department != "ALL":
      query = query.filter(or_(
                            HrDepartmentMaster.id == department,
                            HrDepartmentMaster.department_name == department
                         ))
    if designation and designation != "ALL":
      query = query.filter(or_(
                            HrDesignationMaster.id == designation,
                            HrDesignationMaster.designation == designation
                          ))
    if user_status and user_status != ActiveStatus.ALL:
      query = query.filter(UserBase.is_active == user_status.value)
    if approval_status and approval_status != ApprovedStatus.ALL:
      query = query.filter(EmployeeMaster.is_approved == approval_status.value)
    if is_consultant:
      query = query.filter(EmployeeEmployementDetails.is_consultant == is_consultant)
    if search:
      search = search.strip()
      search_term = f"%{search}%"
      query = query.filter(
              func.lower(EmployeeMaster.first_name).like(func.lower(search_term)) |
              func.lower(EmployeeMaster.middle_name).like(func.lower(search_term)) |
              func.lower(EmployeeMaster.last_name).like(func.lower(search_term)) |
              func.lower(func.concat(EmployeeMaster.first_name, " ", EmployeeMaster.middle_name, " ", EmployeeMaster.last_name)).like(func.lower(search_term)) |
              # EmployeeMaster.employee_id.like(search_term) |
              func.lower(HrEmployeeCategory.category_name).like(func.lower(search_term)) |
              func.lower(HrDepartmentMaster.department_name).like(func.lower(search_term)) |
              func.lower(HrDesignationMaster.designation).like(func.lower(search_term)) 
              # EmployeeContactDetails.personal_mobile_number.like(search_term)
            )
      
    result = query.all()    
    return result  



def get_employee_master_details(db: Session):
    return db.query(EmployeeMaster).all()



def get_present_address_details(db: Session, employee_id: int):
    current_date = date.today()
    return db.query(EmployeePresentAddress).filter(
        EmployeePresentAddress.employee_id == employee_id, 
        EmployeePresentAddress.effective_from_date <= current_date,
        (EmployeePresentAddress.effective_to_date >= current_date) | 
        (EmployeePresentAddress.effective_to_date.is_(None)),
        EmployeePresentAddress.is_deleted == 'no'
    ).all()   


def get_permanent_address_details(db: Session ,employee_id: int):
    current_date = date.today()
    return db.query(EmployeePermanentAddress).filter(
        EmployeePermanentAddress.employee_id == employee_id,
        EmployeePermanentAddress.effective_from_date <= current_date,
        (EmployeePermanentAddress.effective_to_date >= current_date) | 
        (EmployeePermanentAddress.effective_to_date.is_(None)),
        EmployeePermanentAddress.is_deleted == 'no'
    ).all()


# def get_permanent_address_details(db: Session):
    # return db.query(EmployeePermanentAddress).all()

def get_contact_details(db: Session , employee_id: int):
    current_date = date.today()
    return db.query(EmployeeContactDetails).filter(
        EmployeeContactDetails.employee_id == employee_id,
        EmployeeContactDetails.effective_from_date <= current_date,
        (EmployeeContactDetails.effective_to_date >= current_date) | 
        (EmployeeContactDetails.effective_to_date.is_(None)),
        EmployeeContactDetails.is_deleted == 'no'
    ).all()

    

def get_bank_details(db: Session, employee_id: int):
    current_date = date.today()
    return db.query(EmployeeBankDetails).filter(
        EmployeeBankDetails.employee_id == employee_id,
        EmployeeBankDetails.effective_from_date <= current_date,
        (EmployeeBankDetails.effective_to_date >= current_date) | 
        (EmployeeBankDetails.effective_to_date.is_(None)),
        EmployeeBankDetails.is_deleted == 'no'
    ).all()



def get_employement_details(db: Session, employee_id: int):
    current_date = date.today()
    return db.query(EmployeeEmployementDetails).filter(
        EmployeeEmployementDetails.employee_id == employee_id,
        EmployeeEmployementDetails.effective_from_date <= current_date,
        (EmployeeEmployementDetails.effective_to_date >= current_date) | 
        (EmployeeEmployementDetails.effective_to_date.is_(None)),
        EmployeeEmployementDetails.is_deleted == 'no'
    ).all()
    
    
def get_salary_details(db: Session,employee_id: int):
    current_date = date.today()
    return db.query(EmployeeSalaryDetails).filter(
        EmployeeSalaryDetails.employee_id == employee_id,
        EmployeeSalaryDetails.effective_from_date <= current_date,
        (EmployeeSalaryDetails.effective_to_date >= current_date) | 
        (EmployeeSalaryDetails.effective_to_date.is_(None)),
        EmployeeSalaryDetails.is_deleted == 'no'
    ).all()
    
    


def get_qualification_details(db: Session, employee_id: int):
    return db.query(EmployeeEducationalQualification).filter(
        EmployeeEducationalQualification.employee_id == employee_id,
        EmployeeEducationalQualification.is_deleted == 'no'
    ).all()


def get_experience_details(db: Session, employee_id: int):
    return db.query(EmployeeExperience).filter(
        EmployeeExperience.employee_id == employee_id,
        EmployeeExperience.is_deleted == 'no'
    ).all()

def get_document_details(db: Session, employee_id: int):
    return db.query(EmployeeDocuments).filter(
        EmployeeDocuments.employee_id == employee_id,
        EmployeeDocuments.is_deleted == 'no'
    ).all()

def get_emergency_contact_details(db: Session , employee_id: int):
    current_date = date.today()
    return db.query(EmployeeEmergencyContactDetails).filter(
        EmployeeEmergencyContactDetails.employee_id == employee_id,
        EmployeeEmergencyContactDetails.effective_date_from <= current_date,
        (EmployeeEmergencyContactDetails.effective_date_to >= current_date) | 
        (EmployeeEmergencyContactDetails.effective_date_to.is_(None)),
        EmployeeEmergencyContactDetails.is_deleted == 'no'
    ).all()
    
    

def get_dependent_details(db: Session , employee_id: int):
    current_date = date.today()
    return db.query(EmployeeDependentsDetails).filter(
        EmployeeDependentsDetails.employee_id == employee_id,
        EmployeeDependentsDetails.effective_date_from <= current_date,
        (EmployeeDependentsDetails.effective_date_to >= current_date) | 
        (EmployeeDependentsDetails.effective_date_to.is_(None)),
        EmployeeDependentsDetails.is_deleted == 'no'
    ).all()
    

def get_professional_qualification_details(db: Session, employee_id: int):
    return db.query(EmployeeProfessionalQualification).filter(
        EmployeeProfessionalQualification.employee_id == employee_id,
        EmployeeProfessionalQualification.is_deleted == 'no'
    ).all()


def get_security_credentials(db: Session, employee_id: int):
    return db.query(UserBase).filter(
        UserBase.employee_id == employee_id
    ).all()


def get_user_role(db: Session, employee_id: int):
    return db.query(UserRole).filter(
        UserRole.employee_id == employee_id,
        UserRole.is_deleted == 'no'
    ).all()
   







def get_user_roles(db: Session, employee_id: Optional[int]=None)->  List[UserRole]:  
    # if employee_id is None:
    #   users_role = db.query(UsersRole).filter(UsersRole.is_deleted == 'no').all()
  
    user_roles_data =  db.query(UserRole).filter(UserRole.employee_id == employee_id,
                          UserRole.is_deleted=='no').all()
   
    result = {
            "customer_id": employee_id,
            "Roles": [
                {
                    "id"     : user_roles.id,
                    "role_id": user_roles.role_id,                    
                    "is_deleted"        : user_roles.is_deleted
                } for user_roles in user_roles_data
            ]
        }
  
    return result


# def save_or_update_educational_qualifications(db: Session, employee_id: int, qualifications: List[EmployeeEducationalQualficationSchema], user_id: int):
#     try:
#         for qual in qualifications:
#             if qual.id == 0:
#                 # Insertion logic
#                 qualification_data = qual.dict()
#                 qualification_data['employee_id'] = employee_id
#                 qualification_data['created_by'] = user_id
#                 qualification_data['created_on'] = datetime.utcnow()
#                 insert_stmt = insert(EmployeeEducationalQualification).values(**qualification_data)
#                 db.execute(insert_stmt)
#             else:
#                 # Update logic
#                 update_stmt = update(EmployeeEducationalQualification).where(EmployeeEducationalQualification.id == qual.id).values(
#                     qualification_name=qual.qualification_name,
#                     institution=qual.institution,
#                     percentage_or_grade=qual.percentage_or_grade,
#                     month_and_year_of_completion=qual.month_and_year_of_completion,
#                     modified_by=user_id,
#                     modified_on=datetime.utcnow()
#                 )
#                 db.execute(update_stmt)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")



def save_or_update_educational_qualifications(
    db: Session, employee_id: int, qualifications: List[EmployeeEducationalQualficationSchema], user_id: int
):
    try:
        # Step 1: Retrieve existing records
        existing_records = db.query(EmployeeEducationalQualification).filter(
            EmployeeEducationalQualification.employee_id == employee_id
        ).all()

        # Step 2: Determine which records need to be deleted
        existing_ids = {record.id for record in existing_records}
        incoming_ids = {qual.id for qual in qualifications if qual.id != 0}
        ids_to_delete = existing_ids - incoming_ids

        if ids_to_delete:
            db.query(EmployeeEducationalQualification).filter(
                EmployeeEducationalQualification.id.in_(ids_to_delete)
            ).update({"is_deleted": 'yes'}, synchronize_session=False)

        # Step 3: Insert or update records
        for qual in qualifications:
            qualification_data = qual.dict(exclude_unset=True)
            qualification_data['employee_id'] = employee_id

            if qual.id == 0:
                # Insertion logic
                qualification_data['created_by'] = user_id
                qualification_data['created_on'] = datetime.utcnow()
                insert_stmt = insert(EmployeeEducationalQualification).values(**qualification_data)
                db.execute(insert_stmt)
            else:
                # Update logic
                existing_record = db.query(EmployeeEducationalQualification).filter(
                    EmployeeEducationalQualification.id == qual.id,
                    EmployeeEducationalQualification.is_deleted == 'no'
                ).first()
                
                if not existing_record:
                    raise HTTPException(status_code=404, detail=f"Record with id {qual.id} not found or already deleted")
                
                update_stmt = update(EmployeeEducationalQualification).where(
                    EmployeeEducationalQualification.id == qual.id
                ).values(
                    qualification_name=qual.qualification_name,
                    institution=qual.institution,
                    percentage_or_grade=qual.percentage_or_grade,
                    month_and_year_of_completion=qual.month_and_year_of_completion,
                    is_deleted='no',  # Ensure the record is active
                    # modified_by=user_id,
                    # modified_on=datetime.utcnow()
                )
                db.execute(update_stmt)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    



def update_employee_address_or_bank_details(
    db: Session,
    employee_id: int,
    user_id: int,
    Action: RecordActionType,
    request: EmployeeAddressDetailsSchema,
    id: int = 0,
    employee_profile_component: str = None
):
    try:
        if not employee_profile_component:
            raise ValueError("Employee profile component is required for updating")

        components = employee_profile_component.split(',')

        # Validate that the request matches the components specified
        if ('present_address' in components and not request.present_address) or \
           ('permanent_address' in components and not request.permanent_address) or \
           ('bank_details' in components and not request.bank_details) or \
           ('contact_details' in components and not request.contact_details):
            raise HTTPException(status_code=400, detail="Provided request data does not match the specified components")

        if Action == RecordActionType.UPDATE_AND_INSERT:
            for component in components:
                if component == 'present_address' and request.present_address:
                    data = request.present_address.dict()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.utcnow().date(),
                        'created_by': user_id,
                        'created_on': datetime.utcnow(),
                    })
                    
                    existing_address = db.query(EmployeePresentAddress).filter(
                        EmployeePresentAddress.employee_id == employee_id,
                        EmployeePresentAddress.effective_to_date.is_(None),
                        EmployeePresentAddress.is_deleted == 'no'
                    ).first()

                    if existing_address:
                        db.query(EmployeePresentAddress).filter(
                            EmployeePresentAddress.id == existing_address.id
                        ).update({"effective_to_date": datetime.utcnow().date() - timedelta(days=1)})

                    insert_stmt = insert(EmployeePresentAddress).values(**data)
                    db.execute(insert_stmt)
                    db.commit()

                elif component == 'permanent_address' and request.permanent_address:
                    data = request.permanent_address.dict()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.utcnow().date(),
                        'created_by': user_id,
                        'created_on': datetime.utcnow(),
                    })

                    existing_address = db.query(EmployeePermanentAddress).filter(
                        EmployeePermanentAddress.employee_id == employee_id,
                        EmployeePermanentAddress.effective_to_date.is_(None),
                        EmployeePermanentAddress.is_deleted == 'no'
                    ).first()

                    if existing_address:
                        db.query(EmployeePermanentAddress).filter(
                            EmployeePermanentAddress.id == existing_address.id
                        ).update({"effective_to_date": datetime.utcnow().date() - timedelta(days=1)})

                    insert_stmt = insert(EmployeePermanentAddress).values(**data)
                    db.execute(insert_stmt)
                    db.commit()

                elif component == 'bank_details' and request.bank_details:
                    data = request.bank_details.dict()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.utcnow().date(),
                        'created_by': user_id,
                        'created_on': datetime.utcnow(),
                    })

                    existing_bank = db.query(EmployeeBankDetails).filter(
                        EmployeeBankDetails.employee_id == employee_id,
                        EmployeeBankDetails.effective_to_date.is_(None),
                        EmployeeBankDetails.is_deleted == 'no'
                    ).first()

                    if existing_bank:
                        db.query(EmployeeBankDetails).filter(
                            EmployeeBankDetails.id == existing_bank.id
                        ).update({"effective_to_date": datetime.utcnow().date() - timedelta(days=1)})

                    insert_stmt = insert(EmployeeBankDetails).values(**data)
                    db.execute(insert_stmt)
                    db.commit()

                elif component == 'contact_details' and request.contact_details:
                    data = request.contact_details.dict()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.utcnow().date(),
                        'created_by': user_id,
                        'created_on': datetime.utcnow(),
                    })

                    existing_contact = db.query(EmployeeContactDetails).filter(
                        EmployeeContactDetails.employee_id == employee_id,
                        EmployeeContactDetails.effective_to_date.is_(None),
                        EmployeeContactDetails.is_deleted == 'no'
                    ).first()

                    if existing_contact:
                        db.query(EmployeeContactDetails).filter(
                            EmployeeContactDetails.id == existing_contact.id
                        ).update({"effective_to_date": datetime.utcnow().date() - timedelta(days=1)})

                    insert_stmt = insert(EmployeeContactDetails).values(**data)
                    db.execute(insert_stmt)
                    db.commit()

            return {
                "success": True,
                "message": "Saved successfully"
            }

        elif Action == RecordActionType.UPDATE_ONLY:
            for component in components:
                if component == 'present_address' and request.present_address:
                    data = request.present_address.dict()
                    record = db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).first()
                    if not record or record.employee_id != employee_id:
                        raise HTTPException(status_code=400, detail="Invalid employee_id for the provided id")

                    db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).update(data)
                    db.commit()

                elif component == 'permanent_address' and request.permanent_address:
                    data = request.permanent_address.dict()
                    record = db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).first()
                    if not record or record.employee_id != employee_id:
                        raise HTTPException(status_code=400, detail="Invalid employee_id for the provided id")

                    db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).update(data)
                    db.commit()

                elif component == 'bank_details' and request.bank_details:
                    data = request.bank_details.dict()
                    record = db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).first()
                    if not record or record.employee_id != employee_id:
                        raise HTTPException(status_code=400, detail="Invalid employee_id for the provided id")

                    db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).update(data)
                    db.commit()

                elif component == 'contact_details' and request.contact_details:
                    data = request.contact_details.dict()
                    record = db.query(EmployeeContactDetails).filter(EmployeeContactDetails.id == id).first()
                    if not record or record.employee_id != employee_id:
                        raise HTTPException(status_code=400, detail="Invalid employee_id for the provided id")

                    db.query(EmployeeContactDetails).filter(EmployeeContactDetails.id == id).update(data)
                    db.commit()

            return {
                "success": True,
                "message": "Updated successfully"
            }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
