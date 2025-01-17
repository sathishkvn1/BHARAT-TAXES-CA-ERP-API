
from fastapi import HTTPException, Path,  UploadFile
from sqlalchemy.orm import Session
from caerp_db.common.models import AppDesignation, AppEducationSubjectCourse, AppEducationalLevel, AppEducationalStream, AppLanguageProficiency, AppLanguages, EmployeeLanguageProficiency, EmployeeMaster, Gender, MaritalStatus, NationalityDB, Profession,UserBase,UserRole, EmployeeBankDetails, EmployeeContactDetails, EmployeePermanentAddress, EmployeePresentAddress, EmployeeEducationalQualification, EmployeeEmploymentDetails, EmployeeExperience, EmployeeDocuments, EmployeeDependentsDetails, EmployeeEmergencyContactDetails, EmployeeProfessionalQualification
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import SQLAlchemyError
from caerp_db.hr_and_payroll.model import ApplicantContactDetails, ApplicantEducationalQualification, ApplicantExperience, ApplicantHobby, ApplicantLanguageProficiency, ApplicantMaster, ApplicantPermanentAddress, ApplicantPresentAddress, ApplicantProfessionalQualification, ApplicantSkill, ApplicantSocialMediaProfile, ApplicationMaster, EmployeeSalaryDetails, EmployeeSalaryDetailsView, EmployeeTeamMaster, EmployeeTeamMembers, HrDepartmentMaster, HrDesignationMaster, HrEmployeeCategory, HrViewEmployeeTeamMaster, HrViewEmployeeTeamMembers, InterviewSchedule, VacancyAnnouncementDetails, VacancyAnnouncementMaster, VacancyEducationalLevel, VacancyEducationalQualification, VacancyEducationalStream, VacancyEducationalSubjectOrCourse, VacancyExperience, VacancyLanguageProficiency, VacancyMaster, VacancySkills, ViewApplicantDetails
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import AddEmployeeToTeam, ApplicantContactDetailsResponse, ApplicantDetails, ApplicantDetailsView, ApplicantEducationalQualificationResponse, ApplicantExperienceResponse, ApplicantHobbyResponse, ApplicantLanguageProficiencyResponse, ApplicantMasterResponse, ApplicantPermanentAddressResponse, ApplicantPresentAddressResponse, ApplicantProfessionalQualificationResponse, ApplicantSkillResponse, ApplicantSocialMediaResponse, EmployeeAddressDetailsSchema, EmployeeDetails,EmployeeDocumentsSchema, EmployeeEducationalQualficationSchema, EmployeeLanguageProficiencyBase, EmployeeSalarySchema, EmployeeTeamMasterSchema, EmployeeTeamMembersGet, HrViewEmployeeTeamMasterSchema, HrViewEmployeeTeamMemberSchema, HrViewEmployeeTeamSchema, SaveEmployeeTeamMaster, VacancyAnnouncements, VacancyCreateSchema
from caerp_constants.caerp_constants import RecordActionType, ActionType, ActiveStatus, ApprovedStatus
from typing import Union, List, Optional
from sqlalchemy import and_, func, insert, update , text, or_
from sqlalchemy.sql.operators import is_
from caerp_db.hash import Hash
import os
import shutil
from pathlib import Path 


UPLOAD_EMP_DOCUMENTS = "uploads/employee_documents"

#---------------------------------------------------------------------------------------------------------
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


#---------------------------------------------------------------------------------------------------------
def save_employee_master_new(db: Session, request: EmployeeDetails, id: int, user_id: int, employee_profile_component: Optional[str] = None):
    try:
        if id == 0:
            # Insertion logic
            data = request.employee_master.model_dump()
            data["created_by"] = user_id
            data["is_approved"] = 'yes'
            data["approved_by"] = user_id
            data["approved_on"] = datetime.now()
            data['employee_number'] = get_next_employee_number(db)

            insert_stmt = insert(EmployeeMaster).values(**data)
            result = db.execute(insert_stmt)
            db.commit()
            emp_id = result.lastrowid

            contact_details_data = request.contact_details.model_dump()
            contact_details_data['effective_from_date'] = datetime.now().date()
            contact_details_data['employee_id'] = emp_id

            insert_contact_stmt = insert(EmployeeContactDetails).values(**contact_details_data)
            db.execute(insert_contact_stmt)
            db.commit()

            users_new_dict = request.employee_security_credentials.model_dump()
            log_password = Hash.bcrypt(users_new_dict['login_password'])
            password_reset_date = datetime.now().date() + relativedelta(months=3)

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

            employement_details_data = request.employement_details.model_dump()
            employement_details_data["employee_id"] = emp_id
            employement_details_data['effective_from_date'] = datetime.now().date()
            employement_details_data["created_by"] = user_id
            employement_details_data["approved_by"] = user_id
            employement_details_data["approved_on"] = datetime.now()

            insert_emp_det = insert(EmployeeEmploymentDetails).values(**employement_details_data)
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
                update_data = request.employee_master.model_dump(exclude_unset=True)
                db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == id).update(update_data)
                db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == id).update({
                    "modified_by": user_id,
                    "modified_on": datetime.now()
                })

            # Update contact_details if present in the components
            if 'contact_details' in components and request.contact_details:
                contact_details_data = request.contact_details.model_dump(exclude_unset=True)
                db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == id).update(contact_details_data)

            # Update employement_details if present in the components
            if 'employement_details' in components and request.employement_details:
                employement_details_data = request.employement_details.model_dump(exclude_unset=True)
                db.query(EmployeeEmploymentDetails).filter(EmployeeEmploymentDetails.employee_id == id).update(employement_details_data)

            # You can add more conditions for other components if needed

            db.commit()

            return {
                "success": True,
                "message": "Updated successfully"
            }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

#---------------------------------------------------------------------------------------------------------
def save_employee_master(db: Session, request: EmployeeDetails, employee_id: int, id:  List[int], user_id: int, Action: RecordActionType, employee_profile_component: Optional[str] = None):
   try:
      if Action == RecordActionType.INSERT_ONLY:
        if employee_id != 0:
          raise HTTPException(status_code=400, detail="ID should be 0 for inserting new employee master")
        
        try:    
          data = request.employee_master.model_dump()
          data["created_by"] = user_id
          data["is_approved"] = 'yes'
          data["approved_by"] = user_id
          data["approved_on"] = datetime.now()
          data['employee_number'] = get_next_employee_number(db)

          #  with db.begin():
          insert_stmt = insert(EmployeeMaster).values(**data)
          result = db.execute(insert_stmt)
          db.commit()
    
          emp_id = result.lastrowid         

          contact_details_data = request.contact_details.model_dump()
          contact_details_data['effective_from_date'] = datetime.now().date()
          contact_details_data['employee_id'] = emp_id

          insert_contact_stmt = insert(EmployeeContactDetails).values(**contact_details_data)
          db.execute(insert_contact_stmt)
          db.commit()

          users_new_dict = request.employee_security_credentials.model_dump()
          # Insert into users_new table
          log_password  = Hash.bcrypt(users_new_dict['login_password'])
          password_reset_date = datetime.now().date() + relativedelta(months=3)

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

          employement_details_data = request.employement_details.model_dump()

          employement_details_data["employee_id"] = emp_id
          employement_details_data['effective_from_date'] = datetime.now().date()
          employement_details_data["created_by"] = user_id
          employement_details_data["approved_by"] = user_id
          employement_details_data["approved_on"] = datetime.now()  

          insert_emp_det = insert(EmployeeEmploymentDetails).values(**employement_details_data)
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
          for field, value in request.employee_master.model_dump(exclude_unset=True).items():
            setattr(update_emp, field, value)
            update_emp.modified_by = user_id
            update_emp.modified_on = datetime.now()
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
              update_detail_record(db, EmployeeEmploymentDetails, request.employement_details, id, updated_entities, "employement_details") 
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
              credential_data = request.employee_security_credentials.model_dump()
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
                        "modified_on": datetime.now()
                  }
                  for key, value in user_role_data.items():
                    setattr(existing_roles, key, value)
                  updated_entities['user_roles'] = existing_roles    
                  db.commit()    
                else:
                  user_role_data = {
                          "employee_id": employee_id,
                          "role_id": role_id,
                          "created_on": datetime.now()
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
              insert_detail_record(db, EmployeeEmploymentDetails, request.employement_details, employee_id, user_id) 
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

#---------------------------------------------------------------------------------------------------------
def update_detail_record(db, model, request_data, record_id, updated_entities, entity_name):
  single_id = record_id[0]
  detail_record = db.query(model).filter(model.id == single_id, model.is_deleted == 'no').first()
  if not detail_record:
    raise HTTPException(status_code=404, detail=f"{entity_name} with ID {single_id} not found")
  for field, value in request_data.dict(exclude={"effective_to_date"}).items():
     setattr(detail_record, field, value)
  updated_entities[entity_name] = detail_record
#---------------------------------------------------------------------------------------------------------

def update_multiple_detail_records(db, model, request_data_list, record_ids, updated_entities, entity_name):
    for record_id, request_data in zip(record_ids, request_data_list):
      det_multiple_record = db.query(model).filter(model.id == record_id, model.is_deleted == 'no').first()
      if det_multiple_record is None:
        raise HTTPException(status_code=404, detail=f"{entity_name} with ID {record_id} not found")
      for field, value in request_data.dict(exclude_unset=True).items():
        setattr(det_multiple_record, field, value)
      updated_entities[entity_name] = det_multiple_record

#---------------------------------------------------------------------------------------------------------
def insert_detail_record(db, model, request_data, employee_id, user_id):
   detail_data = request_data.dict()
   
   # Set the effective_from_date to the current date
   current_effective_from_date = datetime.now().date()
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
     detail_data["approved_on"] = datetime.now()  
   new_detail = model(**detail_data)
   db.add(new_detail)


#---------------------------------------------------------------------------------------------------------
def insert_multiple_detail_records(db, model, request_data_list, employee_id, user_id):
   for request_data in request_data_list:
     insert_detail = request_data.dict()
     insert_detail["employee_id"] = employee_id

     if hasattr(model, 'created_by'):
       insert_detail["created_by"] = user_id
     db.add(model(**insert_detail))

 #--------------------------------------------------------------------------------------------------------- 
def upload_employee_documents(db: Session, request: EmployeeDocumentsSchema, employee_id: int, user_id: int, file: UploadFile = None):
    try:
        emp_documents_data = request.model_dump()
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


#-------------------------------------------------------------------------------------------------------------




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
        "employement_details": db.query(EmployeeEmploymentDetails).filter(EmployeeEmploymentDetails.employee_id == employee_id).all(),
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
             item_to_update.deleted_on = datetime.now()

       # Delete the master table entry
       employee_found.is_deleted = 'yes'
       employee_found.deleted_by = user_id
       employee_found.deleted_on = datetime.now()
     else:
       # Delete a specific detail table entry 
       if id is None :
         raise HTTPException(status_code=400, detail="Please provide the ID to delete")
       
       schema_mapping_details = {
        "present_address": db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).first(),
        "permanent_address": db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).first(),
        "contact_details": db.query(EmployeeContactDetails).filter(EmployeeContactDetails.id == id).first(),
        "bank_details": db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).first(),
        "employement_details": db.query(EmployeeEmploymentDetails).filter(EmployeeEmploymentDetails.id == id).first(),
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
         item_to_delete.deleted_on = datetime.now()
     db.commit()  
   elif Action == ActionType.UNDELETE:
     schema_mappings = {
        "employee_master": db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == employee_id).first(),
        "present_address": db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).first(),
        "permanent_address": db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).first(),
        "contact_details": db.query(EmployeeContactDetails).filter(EmployeeContactDetails.id == id).first(),
        "bank_details": db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).first(),
        "employement_details": db.query(EmployeeEmploymentDetails).filter(EmployeeEmploymentDetails.id == id).first(),
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

#---------------------------------------------------------------------------------------------------------


# def search_employee_master_details(
#     db: Session,
#     user_status: Optional[ActiveStatus], 
#     approval_status: Optional[ApprovedStatus], 
#     category: Optional[Union[str,int]] = "ALL",
#     department: Optional[Union[str,int]] = "ALL", 
#     designation: Optional[Union[str,int]] = "ALL", 
#     is_consultant: Optional[str] = "ALL", 
#     search: Optional[str] = None
#     ):
#     query = db.query(
#         EmployeeMaster.employee_id,
#         EmployeeMaster.first_name,
#         EmployeeMaster.middle_name,
#         EmployeeMaster.last_name,
#         EmployeeMaster.gender_id,
#         Gender.gender,
#         EmployeeMaster.nationality_id,
#         NationalityDB.nationality_name, 
#         EmployeeMaster.date_of_birth,
#         EmployeeMaster.blood_group,
#         EmployeeMaster.nationality_id,
#         EmployeeMaster.marital_status_id,
#         MaritalStatus.marital_status, 
#         EmployeeMaster.joining_date,
#         EmployeeEmploymentDetails.employee_category_id,
#         HrEmployeeCategory.category_name,
#         EmployeeEmploymentDetails.department_id,
#         HrDepartmentMaster.department_name,
#         EmployeeEmploymentDetails.designation_id,
#         HrDesignationMaster.designation,
#         EmployeeContactDetails.personal_mobile_number,
#         EmployeeContactDetails.personal_email_id,
#         EmployeeContactDetails.remarks,
#         EmployeeEmploymentDetails.is_consultant,
#         EmployeeMaster.is_approved,
#         UserBase.is_active
#     ).join(
#         EmployeeEmploymentDetails, EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id, isouter=True
  
#     ).join(
#         HrEmployeeCategory, EmployeeEmploymentDetails.employee_category_id == HrEmployeeCategory.id, isouter=True
#     ).join(
#         HrDepartmentMaster, EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id, isouter=True
#     ).join(
#         HrDesignationMaster, EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id, isouter=True
#     ).join(
#        UserBase, EmployeeMaster.employee_id == UserBase.employee_id, isouter = True
#     ).join(
#         EmployeeContactDetails, EmployeeMaster.employee_id == EmployeeContactDetails.employee_id, isouter=True
#     ).join(
#         Gender, EmployeeMaster.gender_id == Gender.id, isouter=True  
#     ).join(
#         NationalityDB, EmployeeMaster.nationality_id == NationalityDB.id, isouter=True  # Added join 
#     ).join(
#         MaritalStatus, EmployeeMaster.marital_status_id == MaritalStatus.id, isouter=True  # Added 
#     )

#     # Applying filters at the end of the join statements
#     if category and category != "ALL":
#       query = query.filter(or_(
#                            HrEmployeeCategory.id == category,
#                            HrEmployeeCategory.category_name == category
#                          ))
#     if department and department != "ALL":
#       query = query.filter(or_(
#                             HrDepartmentMaster.id == department,
#                             HrDepartmentMaster.department_name == department
#                          ))
#     if designation and designation != "ALL":
#       query = query.filter(or_(
#                             HrDesignationMaster.id == designation,
#                             HrDesignationMaster.designation == designation
#                           ))
#     if user_status and user_status != ActiveStatus.ALL:
#       query = query.filter(UserBase.is_active == user_status.value)
#     if approval_status and approval_status != ApprovedStatus.ALL:
#       query = query.filter(EmployeeMaster.is_approved == approval_status.value)
#     if is_consultant and is_consultant != "ALL":
#       query = query.filter(EmployeeEmploymentDetails.is_consultant == is_consultant)
#     if search:
#       search = search.strip()
#       search_term = f"%{search}%"
#       query = query.filter(
#               func.lower(EmployeeMaster.first_name).like(func.lower(search_term)) |
#               func.lower(EmployeeMaster.middle_name).like(func.lower(search_term)) |
#               func.lower(EmployeeMaster.last_name).like(func.lower(search_term)) |
#               func.lower(func.concat(EmployeeMaster.first_name, " ", EmployeeMaster.middle_name, " ", EmployeeMaster.last_name)).like(func.lower(search_term)) |
#               # EmployeeMaster.employee_id.like(search_term) |
#               func.lower(HrEmployeeCategory.category_name).like(func.lower(search_term)) |
#               func.lower(HrDepartmentMaster.department_name).like(func.lower(search_term)) |
#               func.lower(HrDesignationMaster.designation).like(func.lower(search_term)) 
#               # EmployeeContactDetails.personal_mobile_number.like(search_term)
#             )
      
#     # result = query.all()
#     result = query.order_by(EmployeeMaster.first_name.asc()).all()
    
#     return result  


def search_employee_master_details(
    db: Session,
    user_status: Optional[ActiveStatus], 
    approval_status: Optional[ApprovedStatus], 
    category: Optional[Union[str,int]] = "ALL",
    department: Optional[Union[str,int]] = "ALL", 
    designation: Optional[Union[str,int]] = "ALL", 
    is_consultant: Optional[str] = "ALL", 
    search: Optional[str] = None
    ):
    query = db.query(
        EmployeeMaster.employee_id,
        EmployeeMaster.employee_number,
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
        EmployeeMaster.is_locked,
        EmployeeMaster.locked_on ,
        EmployeeMaster.locked_by,
        EmployeeMaster.joining_date,
        EmployeeEmploymentDetails.employee_category_id,
        HrEmployeeCategory.category_name,
        EmployeeEmploymentDetails.department_id,
        HrDepartmentMaster.department_name,
        EmployeeEmploymentDetails.designation_id,
        HrDesignationMaster.designation,
        EmployeeContactDetails.personal_mobile_number,
        EmployeeContactDetails.personal_email_id,
        EmployeeContactDetails.remarks,
        EmployeeEmploymentDetails.is_consultant,
        EmployeeMaster.is_approved,
        UserBase.is_active
    ).join(
        EmployeeEmploymentDetails,
        (EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id) &
        EmployeeEmploymentDetails.effective_to_date.is_(None),
        isouter=True
  
    ).join(
        HrEmployeeCategory, EmployeeEmploymentDetails.employee_category_id == HrEmployeeCategory.id, isouter=True
    ).join(
        HrDepartmentMaster, EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id, isouter=True
    ).join(
        HrDesignationMaster, EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id, isouter=True
    ).join(
       UserBase, EmployeeMaster.employee_id == UserBase.employee_id, isouter = True
    ).join(
        EmployeeContactDetails, 
        (EmployeeMaster.employee_id == EmployeeContactDetails.employee_id) & 
        EmployeeContactDetails.effective_to_date.is_(None),
        isouter=True
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
    if is_consultant and is_consultant != "ALL":
      query = query.filter(EmployeeEmploymentDetails.is_consultant == is_consultant)
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
      
    # result = query.all()
    result = query.order_by(EmployeeMaster.first_name.asc()).all()
    
    return result 


#---------------------------------------------------------------------------------------------------------

def get_employee_master_details(db: Session):
    return db.query(EmployeeMaster).all()


#---------------------------------------------------------------------------------------------------------
def get_present_address_details(db: Session, employee_id: int):
    current_date = date.today()
    return db.query(EmployeePresentAddress).filter(
        EmployeePresentAddress.employee_id == employee_id, 
        EmployeePresentAddress.effective_from_date <= current_date,
        (EmployeePresentAddress.effective_to_date >= current_date) | 
        (EmployeePresentAddress.effective_to_date.is_(None)),
        EmployeePresentAddress.is_deleted == 'no'
    ).all()   

#---------------------------------------------------------------------------------------------------------
def get_permanent_address_details(db: Session ,employee_id: int):
    current_date = date.today()
    return db.query(EmployeePermanentAddress).filter(
        EmployeePermanentAddress.employee_id == employee_id,
        EmployeePermanentAddress.effective_from_date <= current_date,
        (EmployeePermanentAddress.effective_to_date >= current_date) | 
        (EmployeePermanentAddress.effective_to_date.is_(None)),
        EmployeePermanentAddress.is_deleted == 'no'
    ).all()

#---------------------------------------------------------------------------------------------------------

def get_contact_details(db: Session , employee_id: int):
    current_date = date.today()
    return db.query(EmployeeContactDetails).filter(
        EmployeeContactDetails.employee_id == employee_id,
        EmployeeContactDetails.effective_from_date <= current_date,
        (EmployeeContactDetails.effective_to_date >= current_date) | 
        (EmployeeContactDetails.effective_to_date.is_(None)),
        EmployeeContactDetails.is_deleted == 'no'
    ).all()

#---------------------------------------------------------------------------------------------------------    

def get_bank_details(db: Session, employee_id: int):
    current_date = date.today()
    return db.query(EmployeeBankDetails).filter(
        EmployeeBankDetails.employee_id == employee_id,
        EmployeeBankDetails.effective_from_date <= current_date,
        (EmployeeBankDetails.effective_to_date >= current_date) | 
        (EmployeeBankDetails.effective_to_date.is_(None)),
        EmployeeBankDetails.is_deleted == 'no'
    ).all()


#---------------------------------------------------------------------------------------------------------

def get_employment_details(db: Session, employee_id: int):
    current_date = date.today()

    # Join EmployeeEmploymentDetails with HrDepartmentMaster and AppDesignation to fetch department_name and designation_name
    return (
        db.query(
            EmployeeEmploymentDetails,
            HrDepartmentMaster.department_name,  # Fetching department_name
            HrDesignationMaster.designation,      # Fetching designation_name
            HrEmployeeCategory.category_name
        )
        .join(HrDepartmentMaster, EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id)
        .join(HrDesignationMaster, EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id)
        .join(HrEmployeeCategory,EmployeeEmploymentDetails.employee_category_id ==HrEmployeeCategory.id )
        .filter(
            EmployeeEmploymentDetails.employee_id == employee_id,
            EmployeeEmploymentDetails.effective_from_date <= current_date,
            (EmployeeEmploymentDetails.effective_to_date >= current_date) |
            (EmployeeEmploymentDetails.effective_to_date.is_(None)),
            EmployeeEmploymentDetails.is_deleted == 'no'
        )
        .all()
    )

    
#---------------------------------------------------------------------------------------------------------    
def get_salary_details(db: Session,employee_id: int):
    current_date = date.today()
    return db.query(EmployeeSalaryDetails).filter(
        EmployeeSalaryDetails.employee_id == employee_id,
        EmployeeSalaryDetails.effective_from_date <= current_date,
        (EmployeeSalaryDetails.effective_to_date >= current_date) | 
        (EmployeeSalaryDetails.effective_to_date.is_(None)),
        EmployeeSalaryDetails.is_deleted == 'no'
    ).all()
    
#---------------------------------------------------------------------------------------------------------    


def get_qualification_details(db: Session, employee_id: int):
    return (
        db.query(
            EmployeeEducationalQualification,
            AppEducationalLevel.education_level,
            AppEducationalStream.education_stream,
            AppEducationSubjectCourse.subject_or_course_name
        )
        .join(AppEducationalLevel, EmployeeEducationalQualification.education_level_id == AppEducationalLevel.id, isouter=True)
        .join(AppEducationalStream, EmployeeEducationalQualification.education_stream_id == AppEducationalStream.id, isouter=True)
        .join(AppEducationSubjectCourse, EmployeeEducationalQualification.education_subject_or_course_id == AppEducationSubjectCourse.id, isouter=True)
        .filter(
            EmployeeEducationalQualification.employee_id == employee_id,
            EmployeeEducationalQualification.is_deleted == 'no'
        )
        .all()
    )


#---------------------------------------------------------------------------------------------------------
def get_experience_details(db: Session, employee_id: int):
    return db.query(EmployeeExperience).filter(
        EmployeeExperience.employee_id == employee_id,
        EmployeeExperience.is_deleted == 'no'
    ).all()
#---------------------------------------------------------------------------------------------------------
def get_document_details(db: Session, employee_id: int):
    return db.query(EmployeeDocuments).filter(
        EmployeeDocuments.employee_id == employee_id,
        EmployeeDocuments.is_deleted == 'no'
    ).all()

#---------------------------------------------------------------------------------------------------------
def get_emergency_contact_details(db: Session , employee_id: int):
    current_date = date.today()
    return db.query(EmployeeEmergencyContactDetails).filter(
        EmployeeEmergencyContactDetails.employee_id == employee_id,
        EmployeeEmergencyContactDetails.effective_date_from <= current_date,
        (EmployeeEmergencyContactDetails.effective_date_to >= current_date) | 
        (EmployeeEmergencyContactDetails.effective_date_to.is_(None)),
        EmployeeEmergencyContactDetails.is_deleted == 'no'
    ).all()
    
 #---------------------------------------------------------------------------------------------------------   

def get_dependent_details(db: Session , employee_id: int):
    current_date = date.today()
    return db.query(EmployeeDependentsDetails).filter(
        EmployeeDependentsDetails.employee_id == employee_id,
        EmployeeDependentsDetails.effective_date_from <= current_date,
        (EmployeeDependentsDetails.effective_date_to >= current_date) | 
        (EmployeeDependentsDetails.effective_date_to.is_(None)),
        EmployeeDependentsDetails.is_deleted == 'no'
    ).all()
    
#---------------------------------------------------------------------------------------------------------

def get_professional_qualification_details(db: Session, employee_id: int):
    return (
        db.query(
            EmployeeProfessionalQualification,
            Profession.profession_name
        )
        .join(Profession, EmployeeProfessionalQualification.qualification_id == Profession.id)
        .filter(
            EmployeeProfessionalQualification.employee_id == employee_id,
            EmployeeProfessionalQualification.is_deleted == 'no'
        )
        .all()
    )

#---------------------------------------------------------------------------------------------------------
def get_security_credentials(db: Session, employee_id: int):
    return db.query(UserBase).filter(
        UserBase.employee_id == employee_id
    ).all()

#---------------------------------------------------------------------------------------------------------
def get_user_role(db: Session, employee_id: int):
    return db.query(UserRole).filter(
        UserRole.employee_id == employee_id,
        UserRole.is_deleted == 'no'
    ).all()
   

#------------------------------------------------------------------------------------------------------------

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
#------------------------------------------------------------------------------------------------------------


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
            qualification_data = qual.model_dump(exclude_unset=True)
            qualification_data['employee_id'] = employee_id

            if qual.id == 0:
                # Insertion logic
                qualification_data['created_by'] = user_id
                qualification_data['created_on'] = datetime.now()
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
    
#------------------------------------------------------------------------------------------------------------
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
                    data = request.present_address.model_dump()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.now().date(),
                        'created_by': user_id,
                        'created_on': datetime.now(),
                    })
                    
                    existing_address = db.query(EmployeePresentAddress).filter(
                        EmployeePresentAddress.employee_id == employee_id,
                        EmployeePresentAddress.effective_to_date.is_(None),
                        EmployeePresentAddress.is_deleted == 'no'
                    ).first()

                    if existing_address:
                        db.query(EmployeePresentAddress).filter(
                            EmployeePresentAddress.id == existing_address.id
                        ).update({"effective_to_date": datetime.now().date() - timedelta(days=1)})

                    insert_stmt = insert(EmployeePresentAddress).values(**data)
                    db.execute(insert_stmt)
                    db.commit()

                elif component == 'permanent_address' and request.permanent_address:
                    data = request.permanent_address.model_dump()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.now().date(),
                        'created_by': user_id,
                        'created_on': datetime.now(),
                    })

                    existing_address = db.query(EmployeePermanentAddress).filter(
                        EmployeePermanentAddress.employee_id == employee_id,
                        EmployeePermanentAddress.effective_to_date.is_(None),
                        EmployeePermanentAddress.is_deleted == 'no'
                    ).first()

                    if existing_address:
                        db.query(EmployeePermanentAddress).filter(
                            EmployeePermanentAddress.id == existing_address.id
                        ).update({"effective_to_date": datetime.now().date() - timedelta(days=1)})

                    insert_stmt = insert(EmployeePermanentAddress).values(**data)
                    db.execute(insert_stmt)
                    db.commit()

                elif component == 'bank_details' and request.bank_details:
                    data = request.bank_details.model_dump()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.now().date(),
                        'created_by': user_id,
                        'created_on': datetime.now(),
                    })

                    existing_bank = db.query(EmployeeBankDetails).filter(
                        EmployeeBankDetails.employee_id == employee_id,
                        EmployeeBankDetails.effective_to_date.is_(None),
                        EmployeeBankDetails.is_deleted == 'no'
                    ).first()

                    if existing_bank:
                        db.query(EmployeeBankDetails).filter(
                            EmployeeBankDetails.id == existing_bank.id
                        ).update({"effective_to_date": datetime.now().date() - timedelta(days=1)})

                    insert_stmt = insert(EmployeeBankDetails).values(**data)
                    db.execute(insert_stmt)
                    db.commit()

                elif component == 'contact_details' and request.contact_details:
                    data = request.contact_details.model_dump()
                    data.update({
                        'employee_id': employee_id,
                        'effective_from_date': datetime.now().date(),
                        'created_by': user_id,
                        'created_on': datetime.now(),
                    })

                    existing_contact = db.query(EmployeeContactDetails).filter(
                        EmployeeContactDetails.employee_id == employee_id,
                        EmployeeContactDetails.effective_to_date.is_(None),
                        EmployeeContactDetails.is_deleted == 'no'
                    ).first()

                    if existing_contact:
                        db.query(EmployeeContactDetails).filter(
                            EmployeeContactDetails.id == existing_contact.id
                        ).update({"effective_to_date": datetime.now().date() - timedelta(days=1)})

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
                    data = request.present_address.model_dump()
                    record = db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).first()
                    if not record or record.employee_id != employee_id:
                        raise HTTPException(status_code=400, detail="Invalid employee_id for the provided id")

                    db.query(EmployeePresentAddress).filter(EmployeePresentAddress.id == id).update(data)
                    db.commit()

                elif component == 'permanent_address' and request.permanent_address:
                    data = request.permanent_address.model_dump()
                    record = db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).first()
                    if not record or record.employee_id != employee_id:
                        raise HTTPException(status_code=400, detail="Invalid employee_id for the provided id")

                    db.query(EmployeePermanentAddress).filter(EmployeePermanentAddress.id == id).update(data)
                    db.commit()

                elif component == 'bank_details' and request.bank_details:
                    data = request.bank_details.model_dump()
                    record = db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).first()
                    if not record or record.employee_id != employee_id:
                        raise HTTPException(status_code=400, detail="Invalid employee_id for the provided id")

                    db.query(EmployeeBankDetails).filter(EmployeeBankDetails.id == id).update(data)
                    db.commit()

                elif component == 'contact_details' and request.contact_details:
                    data = request.contact_details.model_dump()
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

#--------------------------------------------------------------------------------------------------------
def save_employee_salary_details(
    db: Session,
    id: int,
    salary_data: EmployeeSalarySchema,
    user_id: int,
    employee_id: Optional[int] = None
):  

    # If id is 0, employee_id must be provided
    if id == 0 and not employee_id:
        return {
            "success" :False,
            "message": "Employee ID is required for new salary details."}

    if salary_data.calculation_method_id == 1:  # FIXED
        if salary_data.amount <= 0:
            return {"success" :False,
                "message": "Amount must be non-zero for FIXED calculation method."}
    else:
        if salary_data.percentage <= 0:
            return {"success" :False,
                "message": "Percentage must be non-zero for PERCENTAGE calculation method."}

    try:
        # Query existing salary detail
        existing_salary_detail = db.query(EmployeeSalaryDetails).filter(
            EmployeeSalaryDetails.employee_id == employee_id,
            EmployeeSalaryDetails.component_id == salary_data.component_id,
            EmployeeSalaryDetails.is_deleted == 'no',
            EmployeeSalaryDetails.effective_to_date.is_(None)
        ).first()

        # Update effective_to_date if the new effective_from_date is greater than existing
        if existing_salary_detail:
            if (salary_data.effective_from_date > existing_salary_detail.effective_from_date
                    and salary_data.calculation_frequency_id != 1):
                new_effective_to_date = salary_data.effective_from_date - timedelta(days=1)
                existing_salary_detail.effective_to_date = new_effective_to_date
                existing_salary_detail.modified_by = user_id
                existing_salary_detail.modified_on = datetime.now()

        if id == 0:
            if existing_salary_detail and salary_data.calculation_frequency_id == 1 :
               existing_salary_detail.effective_from_date = salary_data.effective_from_date
               existing_salary_detail.modified_by = user_id
               existing_salary_detail.modified_on = datetime.now()
            else:
            # Insert new salary detail
              new_salary_detail = EmployeeSalaryDetails(
                  employee_id=employee_id,
                  created_by=user_id,
                  created_on=datetime.now(),
                  **salary_data.model_dump(exclude_unset=True)
              )
              db.add(new_salary_detail)
              db.flush()

        else:
            # Update existing salary detail if found
            existing_salary_detail = db.query(EmployeeSalaryDetails).filter(EmployeeSalaryDetails.id == id).first()
            if not existing_salary_detail:
                return []

            # Validation for next_increment_date
            if salary_data.next_increment_date and existing_salary_detail.effective_to_date:
                if salary_data.next_increment_date <= existing_salary_detail.effective_to_date:
                    return {"success" :False,
                            "message": "Next Increment Date must be greater than Effective To Date."}

            for field, value in salary_data.model_dump(exclude_unset=True).items():
                setattr(existing_salary_detail, field, value)
            existing_salary_detail.modified_by = user_id
            existing_salary_detail.modified_on = datetime.now()

        db.commit()
        return {
                "success": True,
                "message": "Updated successfully"
            }


    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    
#-------------------------------------------------------------------------------------------------------
def get_employee_salary_details(db: Session, 
                                employee_id: int,
                                
                                  ):
    try:
        # Query salary details based on provided id and employee_id
        salary_details = db.query(EmployeeSalaryDetailsView).filter(
        
            EmployeeSalaryDetailsView.employee_id == employee_id
        ).all()
        
        # If no records are found, raise an HTTPException
        if not salary_details:
            return []

        return salary_details
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#=============================================EMPLOYEE TEAM MASTER====================================================================

def save_employee_team_master(
    db: Session,
    data: List[EmployeeTeamMasterSchema], 
    user_id: int
):
    not_found_ids = []

    try:
        # Start a transaction
        with db.begin():
            for record in data:
                if record.id == 0:
                    # Insert new master data
                    new_master_data = record.model_dump(exclude_unset=True)
                    new_master_data.update({
                        "created_by": user_id,
                        "created_on": datetime.now()
                    })
                    new_master = EmployeeTeamMaster(**new_master_data)
                    db.add(new_master)
                else:
                    # Update existing master data
                    existing_master = db.query(EmployeeTeamMaster).filter(EmployeeTeamMaster.id == record.id).first()
                    if not existing_master:
                        # Collect IDs of records not found
                        not_found_ids.append(record.id)
                        continue  # Skip to the next record

                    master_update_data = record.model_dump(exclude_unset=True)
                    for key, value in master_update_data.items():
                        setattr(existing_master, key, value)
                    existing_master.modified_by = user_id
                    existing_master.modified_on = datetime.now()

            if not_found_ids:
                # Return a custom response with IDs of records not found
                return {"message": f"Master records with IDs {', '.join(map(str, not_found_ids))} not found"}

            # Commit the transaction
            db.commit()

        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
        # Rollback the transaction in case of an error
        db.rollback()
        raise e


#--------------------------------------------------------------------------------------------------------------

def get_all_employee_team_master(
    db: Session,
    department_id: Union[int, str] = 'ALL',
    team_id: Union[int, str] = 'ALL'
) -> List[HrViewEmployeeTeamSchema]:
    # Initial query to get the team masters
    query = db.query(HrViewEmployeeTeamMaster).filter(HrViewEmployeeTeamMaster.is_deleted == 'no')

    # Filter by department_id if specified
    if department_id != 'ALL':
        query = query.filter(HrViewEmployeeTeamMaster.department_id == department_id)

    # Filter by team_id if specified
    if team_id != 'ALL':
        query = query.filter(HrViewEmployeeTeamMaster.team_id == team_id)

    # Fetch all matching team masters
    team_masters = query.all()

    # Prepare results list
    results = []

    # Iterate over each team master to gather associated team members
    for team_master in team_masters:
        members_query = db.query(HrViewEmployeeTeamMembers).filter(
            HrViewEmployeeTeamMembers.team_master_id == team_master.team_id,
            HrViewEmployeeTeamMembers.is_deleted == 'no'
        )
        members = members_query.all()

        # Map members to HrViewEmployeeTeamMemberSchema
        leaders = [
            HrViewEmployeeTeamMemberSchema(
                team_member_id=member.team_member_id,
                team_leader_id=member.team_leader_id,
                leader_first_name=member.leader_first_name,
                leader_middle_name=member.leader_middle_name,
                leader_last_name=member.leader_last_name,
            )
            for member in members
        ]

        # Create the dictionary for the team master schema
        team_dict = {
            "team_id": team_master.team_id,
            "department_id": team_master.department_id,
            "department_name": team_master.department_name,
            "team_name": team_master.team_name,
            "description": team_master.description,
            "effective_from_date": team_master.effective_from_date,
            "effective_to_date": team_master.effective_to_date,
            "leaders": leaders if leaders else []
        }

        # Append the new schema object to the results list
        results.append(HrViewEmployeeTeamMasterSchema(**team_dict))

    # Return the results as a list of HrViewEmployeeTeamSchema
    return [HrViewEmployeeTeamSchema(teams=results)]


#------------------------------------------------------------------------------------------------------------

def get_all_employee_team_members(
    db: Session,
    team_id: int,
    employee_status: Optional[str] = None,  
) -> List[EmployeeTeamMembersGet]:
    
    
    # Base query with common filters
    query = db.query(HrViewEmployeeTeamMembers).filter(
        HrViewEmployeeTeamMembers.team_master_id == team_id,
        HrViewEmployeeTeamMembers.is_deleted == 'no'
    )

    # Get current date
    current_date = datetime.now().date()

    # Filter by employee status
    if employee_status == "CURRENT_EMPLOYEE":
        query = query.filter(
            HrViewEmployeeTeamMembers.effective_from_date <= current_date,
            (HrViewEmployeeTeamMembers.effective_to_date >= current_date) | 
            (HrViewEmployeeTeamMembers.effective_to_date.is_(None))
        )
    elif employee_status == "OLD_EMPLOYEE":
        query = query.filter(
            HrViewEmployeeTeamMembers.effective_to_date < current_date
        )
    # Add sorting by employee first name in ascending order
    query = query.order_by(HrViewEmployeeTeamMembers.member_first_name.asc())

    # Fetch results
    team_members = query.all()

    # Convert ORM objects to Pydantic models
    team_members_schema = [
        EmployeeTeamMembersGet.from_orm(member) for member in team_members
    ]

    return team_members_schema

#-------------------------------------------------------------------------------------------------------------

def get_team_leaders_by_team_id(db: Session, team_id: int):
    return db.query(
        HrViewEmployeeTeamMembers.team_member_id,
        HrViewEmployeeTeamMembers.team_leader_id,
        HrViewEmployeeTeamMembers.leader_first_name,
        HrViewEmployeeTeamMembers.leader_middle_name,
        HrViewEmployeeTeamMembers.leader_last_name
    ).filter(
        HrViewEmployeeTeamMembers.team_master_id == team_id,
        HrViewEmployeeTeamMembers.is_team_leader == 'yes',
        HrViewEmployeeTeamMembers.is_deleted == 'no'
    ).order_by(
        HrViewEmployeeTeamMembers.leader_first_name.asc()  # Ordering by leader_first_name in ascending order
    ).all()    
   


#------------------------------------------------------------------------------------------------------------


def add_employee_to_team(
    db: Session,
    team_id: int,
    department_id :int,
    employee_id: int,
    is_team_leader: str,
    team_leader_id: int,
    effective_from_date: date,
    user_id: int
):
    try:
        # Check if employee already exists in the team and is not marked as deleted
        existing_member = db.query(EmployeeTeamMembers).filter(
            EmployeeTeamMembers.team_master_id == team_id,
            EmployeeTeamMembers.employee_id == employee_id,
            EmployeeTeamMembers.is_deleted == 'no'  # Ensure the record is not deleted
        ).first()

        if existing_member:
            return {"status": "exists", "message": "Employee is already in the team."}

        # Proceed with adding the employee
        new_member = EmployeeTeamMembers(
            team_master_id=team_id,
            employee_id=employee_id,
            is_team_leader=is_team_leader,
            team_leader_id=team_leader_id,
            effective_from_date=effective_from_date,
            created_by=user_id
        )
        db.add(new_member)
        db.commit()

        return {"success": True, "message": "Employee added to team successfully."}
    
    except Exception as e:
        db.rollback()
        raise e
#------------------------------------------------------------------------------------------------------------


def save_team_members(
    db: Session,
    team_id: int,
    department_id: int,  
    data: AddEmployeeToTeam,  
    user_id: int
):
    not_found_ids = []

    try:
        with db.begin():
            for member in data.team_members:  # Access the team_members list from the AddEmployeeToTeam schema
                if member.id == 0:
                    # Insert new team member
                    new_member_data = member.model_dump(exclude_unset=True)
                    new_member_data.update({
                        "team_master_id": team_id,
                        "created_by": user_id,
                        "created_on": datetime.now()
                    })
                    new_member = EmployeeTeamMembers(**new_member_data)
                    db.add(new_member)
                else:
                    # Update existing team member
                    existing_member = db.query(EmployeeTeamMembers).filter(EmployeeTeamMembers.id == member.id).first()
                    if not existing_member:
                        # Collect IDs of records not found
                        not_found_ids.append(member.id)
                        continue  # Skip to the next record

                    member_update_data = member.model_dump(exclude_unset=True)
                    for key, value in member_update_data.items():
                        setattr(existing_member, key, value)
                    existing_member.modified_by = user_id
                    existing_member.modified_on = datetime.now()

            if not_found_ids:
                # Return a custom response with IDs of records not found
                return {"message": f"Team members with IDs {', '.join(map(str, not_found_ids))} not found"}

            # Commit the transaction
            db.commit()

        return {"success": True, "message": "Saved successfully"}

    except Exception as e:
        db.rollback()
        raise e

#------------------------------------------------------------------------------------------------------------



# def search_employee_master_details_test(
#     db: Session,
#     user_status: Optional[ActiveStatus],
#     approval_status: Optional[ApprovedStatus],
#     category: Optional[Union[str,int]] = "ALL",
#     department: Optional[Union[str,int]] = "ALL",
#     designation: Optional[Union[str,int]] = "ALL",
#     is_consultant: Optional[str] = None,
#     search: Optional[str] = None,
#     offset: int = 0,  # Pagination offset
#     page_size: int = 10  # Pagination page size
# ):
#     query = db.query(
#         EmployeeMaster.employee_id,
#         EmployeeMaster.first_name,
#         EmployeeMaster.middle_name,
#         EmployeeMaster.last_name,
#         EmployeeMaster.gender_id,
#         Gender.gender,
#         EmployeeMaster.nationality_id,
#         NationalityDB.nationality_name, 
#         EmployeeMaster.date_of_birth,
#         EmployeeMaster.blood_group,
#         EmployeeMaster.nationality_id,
#         EmployeeMaster.marital_status_id,
#         MaritalStatus.marital_status, 
#         EmployeeMaster.joining_date,
#         EmployeeEmploymentDetails.employee_category_id,
#         HrEmployeeCategory.category_name,
#         EmployeeEmploymentDetails.department_id,
#         HrDepartmentMaster.department_name,
#         EmployeeEmploymentDetails.designation_id,
#         HrDesignationMaster.designation,
#         EmployeeContactDetails.personal_mobile_number,
#         EmployeeContactDetails.personal_email_id,
#         EmployeeContactDetails.remarks,
#         EmployeeEmploymentDetails.is_consultant,
#         EmployeeMaster.is_approved,
#         UserBase.is_active
#     ).join(
#         EmployeeEmploymentDetails, EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id, isouter=True
#     ).join(
#         HrEmployeeCategory, EmployeeEmploymentDetails.employee_category_id == HrEmployeeCategory.id, isouter=True
#     ).join(
#         HrDepartmentMaster, EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id, isouter=True
#     ).join(
#         HrDesignationMaster, EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id, isouter=True
#     ).join(
#         UserBase, EmployeeMaster.employee_id == UserBase.employee_id, isouter=True
#     ).join(
#         EmployeeContactDetails, EmployeeMaster.employee_id == EmployeeContactDetails.employee_id, isouter=True
#     ).join(
#         Gender, EmployeeMaster.gender_id == Gender.id, isouter=True  
#     ).join(
#         NationalityDB, EmployeeMaster.nationality_id == NationalityDB.id, isouter=True
#     ).join(
#         MaritalStatus, EmployeeMaster.marital_status_id == MaritalStatus.id, isouter=True
#     )

#     # Applying filters at the end of the join statements
#     if category and category != "ALL":
#         query = query.filter(or_(
#             HrEmployeeCategory.id == category,
#             HrEmployeeCategory.category_name == category
#         ))
#     if department and department != "ALL":
#         query = query.filter(or_(
#             HrDepartmentMaster.id == department,
#             HrDepartmentMaster.department_name == department
#         ))
#     if designation and designation != "ALL":
#         query = query.filter(or_(
#             HrDesignationMaster.id == designation,
#             HrDesignationMaster.designation == designation
#         ))
#     if user_status and user_status != ActiveStatus.ALL:
#         query = query.filter(UserBase.is_active == user_status.value)
#     if approval_status and approval_status != ApprovedStatus.ALL:
#         query = query.filter(EmployeeMaster.is_approved == approval_status.value)
#     if is_consultant:
#         query = query.filter(EmployeeEmploymentDetails.is_consultant == is_consultant)
#     if search:
#         search = search.strip()
#         search_term = f"%{search}%"
#         query = query.filter(
#             func.lower(EmployeeMaster.first_name).like(func.lower(search_term)) |
#             func.lower(EmployeeMaster.middle_name).like(func.lower(search_term)) |
#             func.lower(EmployeeMaster.last_name).like(func.lower(search_term)) |
#             func.lower(func.concat(EmployeeMaster.first_name, " ", EmployeeMaster.middle_name, " ", EmployeeMaster.last_name)).like(func.lower(search_term)) |
#             func.lower(HrEmployeeCategory.category_name).like(func.lower(search_term)) |
#             func.lower(HrDepartmentMaster.department_name).like(func.lower(search_term)) |
#             func.lower(HrDesignationMaster.designation).like(func.lower(search_term))
#         )
    
#     # Apply pagination before calling .all()
#     query = query.offset(offset).limit(page_size)
    
#     # Execute the query and return results
#     result = query.all()
#     return result

#------------------------------------------------------------------------------------------------------

def search_employee_master_details_with_page(
    db: Session,
    user_status: Optional[ActiveStatus],
    approval_status: Optional[ApprovedStatus],
    category: Optional[Union[str,int]] = "ALL",
    department: Optional[Union[str,int]] = "ALL",
    designation: Optional[Union[str,int]] = "ALL",
    is_consultant: Optional[str]= "ALL",
    search: Optional[str] = None,
    offset: int = 0,  # Pagination offset
    page_size: int = 10  # Pagination page size
):
    
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
        EmployeeEmploymentDetails.employee_category_id,
        HrEmployeeCategory.category_name,
        EmployeeEmploymentDetails.department_id,
        HrDepartmentMaster.department_name,
        EmployeeEmploymentDetails.designation_id,
        HrDesignationMaster.designation,
        EmployeeContactDetails.personal_mobile_number,
        EmployeeContactDetails.personal_email_id,
        EmployeeContactDetails.remarks,
        EmployeeEmploymentDetails.is_consultant,
        EmployeeMaster.is_approved,
        UserBase.is_active
    ).join(
        EmployeeEmploymentDetails, EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id, isouter=True
    ).join(
        HrEmployeeCategory, EmployeeEmploymentDetails.employee_category_id == HrEmployeeCategory.id, isouter=True
    ).join(
        HrDepartmentMaster, EmployeeEmploymentDetails.department_id == HrDepartmentMaster.id, isouter=True
    ).join(
        HrDesignationMaster, EmployeeEmploymentDetails.designation_id == HrDesignationMaster.id, isouter=True
    ).join(
        UserBase, EmployeeMaster.employee_id == UserBase.employee_id, isouter=True
    ).join(
        EmployeeContactDetails, EmployeeMaster.employee_id == EmployeeContactDetails.employee_id, isouter=True
    ).join(
        Gender, EmployeeMaster.gender_id == Gender.id, isouter=True  
    ).join(
        NationalityDB, EmployeeMaster.nationality_id == NationalityDB.id, isouter=True
    ).join(
        MaritalStatus, EmployeeMaster.marital_status_id == MaritalStatus.id, isouter=True
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
    if is_consultant and is_consultant != "ALL":
      query = query.filter(EmployeeEmploymentDetails.is_consultant == is_consultant)
    
    if search:
        search = search.strip()
        search_term = f"%{search}%"
        query = query.filter(
            func.lower(EmployeeMaster.first_name).like(func.lower(search_term)) |
            func.lower(EmployeeMaster.middle_name).like(func.lower(search_term)) |
            func.lower(EmployeeMaster.last_name).like(func.lower(search_term)) |
            func.lower(func.concat(EmployeeMaster.first_name, " ", EmployeeMaster.middle_name, " ", EmployeeMaster.last_name)).like(func.lower(search_term)) |
            func.lower(HrEmployeeCategory.category_name).like(func.lower(search_term)) |
            func.lower(HrDepartmentMaster.department_name).like(func.lower(search_term)) |
            func.lower(HrDesignationMaster.designation).like(func.lower(search_term))
        )
    
    # Fix: Ensure order_by() is called before offset() and limit()
    query = query.order_by(EmployeeMaster.first_name.asc())

    # Then apply offset and limit
    query = query.offset(offset).limit(page_size)

    # Execute the query
    result = query.all()

    return result


def get_employee_language_proficiency_details(db: Session, employee_id: int):
    # Fetch employee proficiency details
    emp_lang_prof_info = (
        db.query(
            EmployeeLanguageProficiency.id,
            EmployeeLanguageProficiency.employee_id,
            EmployeeLanguageProficiency.language_id,
            AppLanguages.language,
            EmployeeLanguageProficiency.read_proficiency_id,
            EmployeeLanguageProficiency.write_proficiency_id,
            EmployeeLanguageProficiency.speak_proficiency_id,
            EmployeeLanguageProficiency.remarks
        )
        .join(AppLanguages, EmployeeLanguageProficiency.language_id == AppLanguages.id)
        .filter(
            EmployeeLanguageProficiency.employee_id == employee_id,
            EmployeeLanguageProficiency.is_deleted == 'no'
        )
        .all()
    )

    lang_proficiencies = []

    for prof in emp_lang_prof_info:
        # Fetch the level names for the proficiency IDs
        read_level = (
            db.query(AppLanguageProficiency.proficiency_level)
            .filter(AppLanguageProficiency.id == prof.read_proficiency_id)
            .first()
        )
        write_level = (
            db.query(AppLanguageProficiency.proficiency_level)
            .filter(AppLanguageProficiency.id == prof.write_proficiency_id)
            .first()
        )
        speak_level = (
            db.query(AppLanguageProficiency.proficiency_level)
            .filter(AppLanguageProficiency.id == prof.speak_proficiency_id)
            .first()
        )

        # Add the fetched data to the response list
        lang_proficiencies.append({
            "id": prof.id,
            "employee_id": prof.employee_id,
            "language_id": prof.language_id,
            "language": prof.language,
            "read_proficiency_id": prof.read_proficiency_id,
            "read_proficiency_level": read_level.proficiency_level if read_level else None,
            "write_proficiency_id": prof.write_proficiency_id,
            "write_proficiency_level": write_level.proficiency_level if write_level else None,
            "speak_proficiency_id": prof.speak_proficiency_id,
            "speak_proficiency_level": speak_level.proficiency_level if speak_level else None,
            "remarks": prof.remarks,
        })

    return lang_proficiencies



def save_employee_language_proficiency(
    db: Session,
    employee_id: int,
    data: List[EmployeeLanguageProficiencyBase],
    user_id: int
):
    saved_ids = []
    updated_ids = []
    unavailable_ids = []
   
    try:
         # Fetch all existing rows for the given employee_id
        existing_rows = db.query(EmployeeLanguageProficiency).filter(
            EmployeeLanguageProficiency.employee_id == employee_id,
            EmployeeLanguageProficiency.is_deleted == 'no'
        ).all()

        # Extract IDs from the incoming data
        incoming_ids = {record.id for record in data if record.id != 0}

        # Determine rows to mark as deleted (those not in the incoming data)
        existing_ids = {row.id for row in existing_rows}
        ids_to_delete = existing_ids - incoming_ids

        for record in data:
            if record.id == 0:
                # Create a new record
                new_record_data = record.dict(exclude={"id"})
                new_record_data["employee_id"] = employee_id
                new_record_data["created_by"] = user_id
                new_record_data["created_on"] = datetime.now()

                new_record = EmployeeLanguageProficiency(**new_record_data)
                db.add(new_record)
                db.commit()
                db.refresh(new_record)

                saved_ids.append(new_record.id)

            else:
                # Update an existing record
                existing_record = db.query(EmployeeLanguageProficiency).filter(
                    EmployeeLanguageProficiency.id == record.id,
                    EmployeeLanguageProficiency.is_deleted == 'no'
                ).first()

                if existing_record:
                    update_data = record.dict(exclude={"id"})
                    update_data["modified_by"] = user_id
                    update_data["modified_on"] = datetime.now()

                    for key, value in update_data.items():
                        setattr(existing_record, key, value)

                    db.commit()
                    db.refresh(existing_record)

                    updated_ids.append(existing_record.id)
                else:
                    # If the record does not exist, mark as unavailable
                    unavailable_ids.append(record.id)

        # Mark rows as deleted for unused records
        for id_to_delete in ids_to_delete:
            row_to_delete = db.query(EmployeeLanguageProficiency).filter(
                EmployeeLanguageProficiency.id == id_to_delete
            ).first()
            if row_to_delete:
                row_to_delete.is_deleted = 'yes'
                row_to_delete.deleted_by = user_id
                row_to_delete.deleted_on = datetime.now()

                db.commit()

        # Create response message based on saved and updated records
        if saved_ids or updated_ids:
            response_message = "Saved successfully."
            if unavailable_ids:
                response_message += f" The following records were not available: {', '.join(map(str, unavailable_ids))}."
            return {
                "success": True,
                "message": response_message
            }
        else:
            return {
                "success": False,
                "message": "No records were saved or updated."
            }

    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    

#---------------------------------------------------------------------------------------------------


# def save_vacancy_data(vacancy_data: VacancyCreateSchema, db: Session, created_by: int):
#     try:
#         print("Starting vacancy insert operation")

#         # Prepare data excluding the ID (auto-incremented)
#         vacancy_master_data = vacancy_data.dict(exclude={"vacancy_experience", "skills_required", "language_proficiency", "education", "id"})
#         vacancy_master_data['created_by'] = created_by
#         vacancy_master_data['created_on'] = datetime.utcnow()  # Ensure created_on is set dynamically

#         print(f"Inserting vacancy master data: {vacancy_master_data}")

#         # Insert into VacancyMaster and add it to the session
#         vacancy_master = VacancyMaster(**vacancy_master_data)
#         db.add(vacancy_master)

#         # Flush to generate the ID and sync with the database
#         db.flush()  
#         print(f"Vacancy master inserted with ID: {vacancy_master.id}")

#         # Insert related data (e.g., experience, skills) if they exist
#         if vacancy_data.vacancy_experience:
#             for experience in vacancy_data.vacancy_experience:
#                 if experience.id == 0:  # Check if it's a new entry (id == 0 means new record)
#                     vacancy_experience_data = experience.dict()
#                     vacancy_experience_data['vacancy_master_id'] = vacancy_master.id
#                     vacancy_experience = VacancyExperience(**vacancy_experience_data)
#                     db.add(vacancy_experience)

#         if vacancy_data.skills_required:
#             for skill in vacancy_data.skills_required:
#                 if skill.id == 0:  # Check if it's a new entry (id == 0 means new record)
#                     vacancy_skill_data = skill.dict()
#                     vacancy_skill_data['vacancy_master_id'] = vacancy_master.id
#                     vacancy_skill = VacancySkills(**vacancy_skill_data)
#                     db.add(vacancy_skill)

#         if vacancy_data.language_proficiency:
#             for language in vacancy_data.language_proficiency:
#                 if language.id == 0:  # Check if it's a new entry (id == 0 means new record)
#                     # Remove 'education_level_id' if not part of VacancyLanguageProficiency
#                     language_proficiency_data = language.dict(exclude={"education_level_id"})
#                     language_proficiency_data['vacancy_master_id'] = vacancy_master.id
#                     language_proficiency = VacancyLanguageProficiency(**language_proficiency_data)
#                     db.add(language_proficiency)

#         if vacancy_data.education:
#             for education in vacancy_data.education:
#                 if education.id == 0:  # Check if it's a new entry (id == 0 means new record)
#                     education_data = education.dict()
#                     education_data['vacancy_master_id'] = vacancy_master.id
#                     education = VacancyEducationalQualification(**education_data)
#                     db.add(education)

#         # Commit the session (explicit commit)
#         db.commit()

#         print(f"Vacancy created successfully with ID: {vacancy_master.id}")
#         return {
#             "success": True,  # Success flag
#             "message": "Vacancy created successfully",  # Success message
#             "vacancy_master_id": vacancy_master.id  # ID of the created vacancy
#         }

#     except Exception as e:
#         print(f"Error during vacancy creation: {str(e)}")
#         db.rollback()  # Rollback in case of error
#         return {
#             "success": False,  # Failure flag
#             "message": f"Error while saving vacancy data: {str(e)}"  # Error message
#         }


from datetime import datetime
from sqlalchemy.orm import Session

def save_vacancy_data(vacancy_data: VacancyCreateSchema, db: Session, created_by: int):
    try:
        print("Starting vacancy insert/update operation")

        # Prepare data excluding the ID (auto-incremented)
        vacancy_master_data = vacancy_data.dict(exclude={"vacancy_experience", "skills_required", "language_proficiency", "education", "id"})
        vacancy_master_data['created_by'] = created_by
        vacancy_master_data['created_on'] = datetime.utcnow()  # Ensure created_on is set dynamically

        print(f"Inserting/updating vacancy master data: {vacancy_master_data}")

        # Handle insert or update for VacancyMaster
        if vacancy_data.id == 0:
            # Insert new vacancy master
            vacancy_master = VacancyMaster(**vacancy_master_data)
            db.add(vacancy_master)
            db.flush()  # Flush to generate the ID
            print(f"Vacancy master inserted with ID: {vacancy_master.id}")
        else:
            # Update existing vacancy master by ID
            vacancy_master = db.query(VacancyMaster).filter(VacancyMaster.id == vacancy_data.id).first()
            if not vacancy_master:
                raise Exception(f"Vacancy with ID {vacancy_data.id} not found")
            for key, value in vacancy_master_data.items():
                setattr(vacancy_master, key, value)

        # Insert or update related data (e.g., experience, skills, language proficiency, education)
        
        # Update or insert vacancy experience
        if vacancy_data.vacancy_experience:
            for experience in vacancy_data.vacancy_experience:
                if experience.id == 0:  # New record, insert
                    vacancy_experience_data = experience.dict()
                    vacancy_experience_data['vacancy_master_id'] = vacancy_master.id
                    vacancy_experience = VacancyExperience(**vacancy_experience_data)
                    db.add(vacancy_experience)
                else:  # Existing record, update
                    vacancy_experience = db.query(VacancyExperience).filter(VacancyExperience.id == experience.id).first()
                    if vacancy_experience:
                        for key, value in experience.dict().items():
                            setattr(vacancy_experience, key, value)

        # Update or insert skills required
        if vacancy_data.skills_required:
            for skill in vacancy_data.skills_required:
                if skill.id == 0:  # New record, insert
                    vacancy_skill_data = skill.dict()
                    vacancy_skill_data['vacancy_master_id'] = vacancy_master.id
                    vacancy_skill = VacancySkills(**vacancy_skill_data)
                    db.add(vacancy_skill)
                else:  # Existing record, update
                    vacancy_skill = db.query(VacancySkills).filter(VacancySkills.id == skill.id).first()
                    if vacancy_skill:
                        for key, value in skill.dict().items():
                            setattr(vacancy_skill, key, value)

        # Update or insert language proficiency
        if vacancy_data.language_proficiency:
            for language in vacancy_data.language_proficiency:
                if language.id == 0:  # New record, insert
                    language_proficiency_data = language.dict(exclude={"education_level_id"})
                    language_proficiency_data['vacancy_master_id'] = vacancy_master.id
                    language_proficiency = VacancyLanguageProficiency(**language_proficiency_data)
                    db.add(language_proficiency)
                else:  # Existing record, update
                    language_proficiency = db.query(VacancyLanguageProficiency).filter(VacancyLanguageProficiency.id == language.id).first()
                    if language_proficiency:
                        for key, value in language.dict().items():
                            setattr(language_proficiency, key, value)

        # Update or insert education qualifications
        if vacancy_data.education:
            for education in vacancy_data.education:
                if education.id == 0:  # New record, insert
                    education_data = education.dict()
                    education_data['vacancy_master_id'] = vacancy_master.id
                    education = VacancyEducationalQualification(**education_data)
                    db.add(education)
                else:  # Existing record, update
                    education_record = db.query(VacancyEducationalQualification).filter(VacancyEducationalQualification.id == education.id).first()
                    if education_record:
                        for key, value in education.dict().items():
                            setattr(education_record, key, value)

        # Commit the session (explicit commit)
        db.commit()

        print(f"Vacancy {'updated' if vacancy_data.id else 'created'} successfully with ID: {vacancy_master.id}")
        return {
            "success": True,  # Success flag
            "message": f"Vacancy {'updated' if vacancy_data.id else 'created'} successfully",  # Success message
            "vacancy_master_id": vacancy_master.id  # ID of the created or updated vacancy
        }

    except Exception as e:
        print(f"Error during vacancy creation/update: {str(e)}")
        db.rollback()  # Rollback in case of error
        return {
            "success": False,  # Failure flag
            "message": f"Error while saving vacancy data: {str(e)}"  # Error message
        }

#---------------------------------------------------------------------------------------------------
# def save_vacancy_announcements_to_db(data: VacancyAnnouncements, db: Session, user_id: int):
#     try:
#         for master in data.vacancy_announcement_master:
#             # Insert/update VacancyAnnouncementMaster record
#             master_record = VacancyAnnouncementMaster(
#                 id=master.id if master.id > 0 else None,
#                 title=master.title,
#                 description=master.description,
#                 announcement_type=master.announcement_type,
#                 closing_date=master.closing_date,
#                 created_by=user_id,
#                 created_on=datetime.utcnow(),
#                 is_deleted='no'
#             )
#             db.add(master_record)
#             db.flush()  # Flush to get the master record's ID

#             # Insert/update VacancyAnnouncementDetails records
#             if master.announcement_details:  # Check if announcement_details is not None
#                 for detail in master.announcement_details:
#                     detail_record = VacancyAnnouncementDetails(
#                         id=detail.id if detail.id > 0 else None,
#                         vacancy_announcement_master_id=master_record.id,
#                         vacancy_master_id=detail.vacancy_master_id,
#                         created_by=user_id,
#                         created_on=datetime.utcnow(),
#                         is_deleted='no'
#                     )
#                     db.add(detail_record)

#         db.commit()  # Commit the transaction
#         return {"success": True, "message": "Vacancy announcements saved successfully"}
    
#     except Exception as e:
#         db.rollback()  # Rollback if any error occurs
#         return {"success": False, "message": f"Unexpected error: {str(e)}"}



def save_vacancy_announcements_to_db(data: VacancyAnnouncements, db: Session, user_id: int):
    try:
        for master in data.vacancy_announcement_master:
            if master.id == 0:  # If id is 0, insert new VacancyAnnouncementMaster record
                master_record = VacancyAnnouncementMaster(
                    title=master.title,
                    description=master.description,
                    announcement_type=master.announcement_type,
                    closing_date=master.closing_date,
                    created_by=user_id,
                    created_on=datetime.utcnow(),
                    is_deleted='no'
                )
                db.add(master_record)
                db.flush()  # Ensure ID is generated for the inserted record

            else:  # If id is not 0, update existing VacancyAnnouncementMaster record
                master_record = db.query(VacancyAnnouncementMaster).filter(VacancyAnnouncementMaster.id == master.id).first()
                if master_record:
                    # Update existing record fields
                    master_record.title = master.title
                    master_record.description = master.description
                    master_record.announcement_type = master.announcement_type
                    master_record.closing_date = master.closing_date
                else:
                    raise ValueError(f"VacancyAnnouncementMaster with id {master.id} not found for update.")

            # Handle VacancyAnnouncementDetails insert or update
            if master.announcement_details:
                for detail in master.announcement_details:
                    if detail.id == 0:  # If id is 0, insert new VacancyAnnouncementDetails record
                        detail_record = VacancyAnnouncementDetails(
                            vacancy_announcement_master_id=master_record.id,
                            vacancy_master_id=detail.vacancy_master_id,
                            created_by=user_id,
                            created_on=datetime.utcnow(),
                            is_deleted='no'
                        )
                        db.add(detail_record)

                    else:  # If id is not 0, update existing VacancyAnnouncementDetails record
                        detail_record = db.query(VacancyAnnouncementDetails).filter(VacancyAnnouncementDetails.id == detail.id).first()
                        if detail_record:
                            # Update existing detail record fields
                            detail_record.vacancy_master_id = detail.vacancy_master_id
                        else:
                            raise ValueError(f"VacancyAnnouncementDetails with id {detail.id} not found for update.")

        db.commit()  # Commit the transaction
        return {"success": True, "message": "Vacancy announcements saved successfully"}

    except Exception as e:
        db.rollback()  # Rollback if any error occurs
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

#---------------------------------------------------------------------------------
# def save_applicant(data: ApplicantDetails, db: Session, user_id: int, profile_component: str):
#     try:
#         applicant_id = None
        
#         # Iterate through each profile component and save or update the respective data
#         for component in data.profile_component:
#             if component == "applicant_master":
#                 applicant_data = data.applicant_master.dict()
#                 if applicant_data["id"] == 0:  # Insert new record
#                     new_applicant = ApplicantMaster(
#                         **applicant_data,
#                         # created_by=user_id,
                    
#                     )
#                     db.add(new_applicant)
#                     db.commit()
#                     db.refresh(new_applicant)
#                     applicant_id = new_applicant.id
#                 else:  # Update existing record
#                     # Find existing applicant
#                     existing_applicant = db.query(ApplicantMaster).filter(
#                         ApplicantMaster.id == applicant_data["id"]
#                     ).first()
                    
#                     if existing_applicant:
#                         # Update fields only if present in applicant_data
#                         for key, value in applicant_data.items():
#                             if hasattr(existing_applicant, key) and value is not None:
#                                 setattr(existing_applicant, key, value)
#                         db.commit()
#                         db.refresh(existing_applicant)
#                         applicant_id = existing_applicant.id
#                     else:
#                         raise HTTPException(status_code=404, detail="Applicant master not found for update.")

#             elif component == "applicant_present_address":
#                 if not applicant_id:
#                     raise HTTPException(status_code=400, detail="Applicant master must be saved first.")
#                 address_data = data.applicant_present_address.dict()
#                 if address_data["id"] == 0:  # Insert new record
#                     new_address = ApplicantPresentAddress(
#                         **address_data,
#                         applicant_id=applicant_id,
#                         created_by=user_id,
#                         updated_by=user_id
#                     )
#                     db.add(new_address)
#                     db.commit()
#                     db.refresh(new_address)
#                 else:  # Update existing record
#                     existing_address = db.query(ApplicantPresentAddress).filter(ApplicantPresentAddress.id == address_data["id"]).first()
#                     if existing_address:
#                         for key, value in address_data.items():
#                             setattr(existing_address, key, value)
#                         existing_address.updated_by = user_id
#                         db.commit()
#                         db.refresh(existing_address)

#             elif component == "applicant_permanent_address":
#                 if not applicant_id:
#                     raise HTTPException(status_code=400, detail="Applicant master must be saved first.")
#                 permanent_address_data = data.applicant_permanent_address.dict()
#                 if permanent_address_data["id"] == 0:  # Insert new record
#                     new_permanent_address = ApplicantPermenentAddress(
#                         **permanent_address_data,
#                         applicant_id=applicant_id,
#                         created_by=user_id,
#                         updated_by=user_id
#                     )
#                     db.add(new_permanent_address)
#                     db.commit()
#                     db.refresh(new_permanent_address)
#                 else:  # Update existing record
#                     existing_permanent_address = db.query(ApplicantPermenentAddress).filter(ApplicantPermenentAddress.id == permanent_address_data["id"]).first()
#                     if existing_permanent_address:
#                         for key, value in permanent_address_data.items():
#                             setattr(existing_permanent_address, key, value)
#                         existing_permanent_address.updated_by = user_id
#                         db.commit()
#                         db.refresh(existing_permanent_address)

#             # You can add more components like this

#             else:
#                 raise HTTPException(status_code=400, detail=f"Invalid component: {component}")

#         return {"success": True, "message": "Applicant details saved successfully"}

#     except Exception as e:
#         db.rollback()  # Rollback the transaction in case of failure
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def save_applicant(data: ApplicantDetails,vacancy_master_id:int, db: Session, user_id: int, profile_component: List[str]):
    result = {"success": False, "message": "An error occurred while saving applicant details."}
    
    # Step 1: Process each profile_component
    # Step 1: Process each profile_component
    for component in profile_component:
        if component == "applicant_master":
            # Handling applicant_master component
            applicant_data = data.applicant_master.dict()  # Convert the applicant data to a dictionary
            login_id = 1  # Assuming the login_id is 1 for now

            if applicant_data["id"] == 0:  # Insert new record
                new_applicant = ApplicantMaster(
                    first_name=applicant_data["first_name"],
                    middle_name=applicant_data["middle_name"],
                    last_name=applicant_data["last_name"],
                    date_of_birth=applicant_data["date_of_birth"],
                    gender_id=applicant_data["gender_id"],
                    blood_group=applicant_data["blood_group"],
                    marital_status_id=applicant_data["marital_status_id"],
                    nationality_id=applicant_data["nationality_id"],
                    login_id=login_id 
                    # personal_whatsapp_number=applicant_data["personal_whatsapp_number"],
                    # personal_email_id=applicant_data["personal_email_id"],
                    # login_id=login_id  # Assuming the login_id is 1 for now
                )
                try:
                    db.add(new_applicant)
                    db.commit()
                    db.refresh(new_applicant)
                    applicant_id = new_applicant.applicant_id

                    # Insert into ApplicantContactDetails if data is available
                    contact_data = {
                        "applicant_id": applicant_id,
                        "personal_mobile_number": applicant_data["personal_mobile_number"],
                        "personal_whatsapp_number": applicant_data["personal_whatsapp_number"],
                        "personal_email_id": applicant_data["personal_email_id"],
                    }
                    new_contact = ApplicantContactDetails(**contact_data)
                    db.add(new_contact)
                    db.commit()

                    # If vacancy_master_id is provided, insert into ApplicationMaster
                    if vacancy_master_id:
                        application_data = {
                            "applicant_id": applicant_id,
                            "vacancy_master_id": vacancy_master_id,
                            "application_date": datetime.now(),
                            "application_status": "PENDING",
                           
                        }
                        new_application = ApplicationMaster(**application_data)
                        db.add(new_application)
                        db.commit()

                except Exception as e:
                    db.rollback()  # Rollback if an error occurs
                    raise HTTPException(status_code=500, detail="Error saving applicant: " + str(e))

            else:  # Update existing record
                existing_applicant = db.query(ApplicantMaster).filter(ApplicantMaster.applicant_id == applicant_data["id"]).first()
                # existing_contact_applicant = db.query(ApplicantContactDetails).filter(ApplicantContactDetails.applicant_id == applicant_data["id"]).first()
                if existing_applicant:
                    # Update applicant_master data
                    existing_applicant.first_name = applicant_data["first_name"]
                    existing_applicant.middle_name = applicant_data["middle_name"]
                    existing_applicant.last_name = applicant_data["last_name"]
                    existing_applicant.date_of_birth = applicant_data["date_of_birth"]
                    existing_applicant.gender_id = applicant_data["gender_id"]
                    existing_applicant.blood_group = applicant_data["blood_group"]
                    existing_applicant.marital_status_id = applicant_data["marital_status_id"]
                    existing_applicant.nationality_id = applicant_data["nationality_id"]
                    # existing_contact_applicant.personal_mobile_number = applicant_data["personal_mobile_number"]
                    # existing_contact_applicant.personal_whatsapp_number = applicant_data["personal_whatsapp_number"]
                    # existing_contact_applicant.personal_email_id = applicant_data["personal_email_id"]

                    try:
                        db.commit()
                        db.refresh(existing_applicant)
                        applicant_id = existing_applicant.applicant_id

                        # Update ApplicantContactDetails
                        existing_contact = db.query(ApplicantContactDetails).filter(ApplicantContactDetails.applicant_id == applicant_id).first()
                        if existing_contact:
                            existing_contact.personal_mobile_number = applicant_data["personal_mobile_number"]
                            existing_contact.personal_whatsapp_number = applicant_data["personal_whatsapp_number"]
                            existing_contact.personal_email_id = applicant_data["personal_email_id"]
                            db.commit()
                            db.refresh(existing_contact)

                        # If vacancy_master_id is provided, insert or update ApplicationMaster
                        # if data.vacancy_master_id:
                        #     existing_application = db.query(ApplicationMaster).filter(ApplicationMaster.applicant_id == applicant_id).first()
                        #     if existing_application:
                        #         existing_application.vacancy_master_id = data.vacancy_master_id
                        #         existing_application.application_date = date.today()
                        #         existing_application.application_status = "PENDING"
                        #         db.commit()
                        #         db.refresh(existing_application)
                        #     else:
                        #         application_data = {
                        #             "applicant_id": applicant_id,
                        #             "vacancy_master_id": data.vacancy_master_id,
                        #             "application_date": date.today(),
                        #             "application_status": "PENDING",
                        #             "is_deleted": "no",  # Assuming 'no' as default
                        #         }
                        #         new_application = ApplicationMaster(**application_data)
                        #         db.add(new_application)
                        #         db.commit()

                    except Exception as e:
                        db.rollback()  # Rollback if an error occurs
                        raise HTTPException(status_code=500, detail="Error updating applicant: " + str(e))

                else:
                    raise HTTPException(status_code=404, detail="Applicant master not found for update.")

            return {"success": True, "message": "Applicant details saved successfully", "applicant_id": applicant_id}

        elif component == "applicant_present_address":
            # Handling applicant_present_address component
            present_address_data = data.applicant_present_address.dict()

            if present_address_data["id"] == 0:  # Insert new record
                present_address_data.pop("id", None)
                # Create new address object
                new_address = ApplicantPresentAddress(**present_address_data)
                db.add(new_address)

                try:
                    print("New Address to be inserted:", new_address)  # Log the address object
                    db.commit()  # Commit changes to the database
                    db.refresh(new_address)  # Refresh the instance to reflect the inserted data
                    # return {"success": True, "message": "Saved successfully!"} 
                except Exception as e:
                    db.rollback()  
                    raise HTTPException(status_code=500, detail="Error saving new address: " + str(e))

            else:  # Update existing record
                existing_address = db.query(ApplicantPresentAddress).filter(ApplicantPresentAddress.id == present_address_data["id"]).first()

                if existing_address:
                    for key, value in present_address_data.items():
                        if hasattr(existing_address, key) and value is not None:
                            setattr(existing_address, key, value)

                    try:
                        db.commit()  # Commit changes to the database
                        db.refresh(existing_address)  # Refresh the instance to reflect the updated data
                    except Exception as e:
                        db.rollback()  # Rollback in case of any error during commit
                        raise HTTPException(status_code=500, detail="Error updating address: " + str(e))

                else:
                    raise HTTPException(status_code=404, detail="Applicant present address not found for update.")



        elif component == "applicant_permanent_address":
            # Handling applicant_permanent_address component
            permanent_address_data = data.applicant_permanent_address.dict()

            if permanent_address_data["id"] == 0:  # Insert new record
                permanent_address_data.pop("id", None)
                # Create a new address object with the provided data
                new_address = ApplicantPermanentAddress(**permanent_address_data)
                db.add(new_address)
                
                try:
                    db.commit()
                    db.refresh(new_address)  # Refresh the instance to reflect the inserted data
                    return {"success": True, "message": "Permanent address saved successfully!", "address_id": new_address.id}
                except Exception as e:
                    db.rollback()  # Rollback in case of any error during commit
                    raise HTTPException(status_code=500, detail="Error saving permanent address: " + str(e))

            else:  # Update existing record
                existing_address = db.query(ApplicantPermanentAddress).filter(ApplicantPermanentAddress.id == permanent_address_data["id"]).first()

                if existing_address:
                    # Update the existing address with the new data
                    for key, value in permanent_address_data.items():
                        if hasattr(existing_address, key) and value is not None:
                            setattr(existing_address, key, value)

                    try:
                        db.commit()  # Commit changes to the database
                        db.refresh(existing_address)  # Refresh the instance to reflect the updated data
                        return {"success": True, "message": "Permanent address updated successfully!"}
                    except Exception as e:
                        db.rollback()  # Rollback in case of any error during commit
                        raise HTTPException(status_code=500, detail="Error updating permanent address: " + str(e))

                else:
                    raise HTTPException(status_code=404, detail="Applicant permanent address not found for update.")

        elif component == "applicant_contact_details":
            # Handling applicant_contact_details component
            contact_data = data.applicant_contact_details.dict()
            if contact_data["id"] == 0:  # Insert new record
                contact_data.pop("id", None)
                new_contact = ApplicantContactDetails(**contact_data)
                db.add(new_contact)
                db.commit()
                db.refresh(new_contact)
            else:  # Update existing record
                existing_contact = db.query(ApplicantContactDetails).filter(ApplicantContactDetails.id == contact_data["id"]).first()
                if existing_contact:
                    for key, value in contact_data.items():
                        if hasattr(existing_contact, key) and value is not None:
                            setattr(existing_contact, key, value)
                    db.commit()
                    db.refresh(existing_contact)
                else:
                    raise HTTPException(status_code=404, detail="Applicant contact details not found for update.")
        
        # Continue similarly for other components like 'applicant_educational_qualification', 'applicant_experience', etc.
        elif component == "applicant_educational_qualification":
            for education in data.applicant_educational_qualification:
                education_data = education.dict()
                
                if education_data["id"] == 0:  # Insert new record
                    education_data.pop("id", None)
                    new_education = ApplicantEducationalQualification(**education_data)
                    db.add(new_education)
                    db.commit()  # Commit the changes to the database
                    db.refresh(new_education)  # Refresh to get the latest data after commit
                else:  # Update existing record
                    existing_education = db.query(ApplicantEducationalQualification).filter(ApplicantEducationalQualification.id == education_data["id"]).first()
                    if existing_education:
                        for key, value in education_data.items():
                            if hasattr(existing_education, key) and value is not None:
                                setattr(existing_education, key, value)
                        db.commit()  # Commit the changes to the database
                        db.refresh(existing_education)  # Refresh the updated record
                    else:
                        raise HTTPException(status_code=404, detail="Applicant educational qualification not found for update.")

        elif component == "applicant_professional_qualification":
           # Save or update the applicant's professional qualifications
            for qualification in data.applicant_professional_qualification:
                qualification_data = qualification.dict()

                if qualification_data["id"] == 0:  # Insert new record
                    qualification_data.pop("id", None)
                    new_qualification = ApplicantProfessionalQualification(**qualification_data)
                    db.add(new_qualification)
                    db.commit()
                    db.refresh(new_qualification)  # Refresh the new object to get any default values (e.g., auto-generated fields)
                else:  # Update existing record
                    existing_qualification = db.query(ApplicantProfessionalQualification).filter(
                        ApplicantProfessionalQualification.id == qualification_data["id"]
                    ).first()

                    if existing_qualification:
                        for key, value in qualification_data.items():
                            if hasattr(existing_qualification, key) and value is not None:
                                setattr(existing_qualification, key, value)
                        db.commit()
                        db.refresh(existing_qualification)  # Refresh the updated object
                    else:
                        raise HTTPException(status_code=404, detail="Applicant professional qualification not found for update.")
        
        elif component == "applicant_experience":
            # Save or update the applicant's experience
            for experience in data.applicant_experience:
                experience_data = experience.dict()

                if experience_data["id"] == 0:  # Insert new record
                    experience_data.pop("id", None)
                    new_experience = ApplicantExperience(**experience_data)
                    db.add(new_experience)
                    db.commit()
                    db.refresh(new_experience)  # Refresh the new object to get any default values (e.g., auto-generated fields)
                else:  # Update existing record
                    existing_experience = db.query(ApplicantExperience).filter(
                        ApplicantExperience.id == experience_data["id"]
                    ).first()

                    if existing_experience:
                        for key, value in experience_data.items():
                            if hasattr(existing_experience, key) and value is not None:
                                setattr(existing_experience, key, value)
                        db.commit()
                        db.refresh(existing_experience)  # Refresh the updated object
                    else:
                        raise HTTPException(status_code=404, detail="Applicant experience not found for update.")


        elif component == "applicant_language_proficiency":
            # Save or update the applicant's language proficiency
            for language_proficiency in data.applicant_language_proficiency:
                language_proficiency_data = language_proficiency.dict()

                if language_proficiency_data["id"] == 0:  # Insert new record
                    language_proficiency_data.pop("id", None)
                    new_language_proficiency = ApplicantLanguageProficiency(**language_proficiency_data)
                    db.add(new_language_proficiency)
                    db.commit()
                    db.refresh(new_language_proficiency)  # Refresh the new object to get any default values (e.g., auto-generated fields)
                else:  # Update existing record
                    existing_language_proficiency = db.query(ApplicantLanguageProficiency).filter(
                        ApplicantLanguageProficiency.id == language_proficiency_data["id"]
                    ).first()

                    if existing_language_proficiency:
                        for key, value in language_proficiency_data.items():
                            if hasattr(existing_language_proficiency, key) and value is not None:
                                setattr(existing_language_proficiency, key, value)
                        db.commit()
                        db.refresh(existing_language_proficiency)  # Refresh the updated object
                    else:
                        raise HTTPException(status_code=404, detail="Applicant language proficiency not found for update.")

     
        elif component == "applicant_hobby":
            # Save or update the applicant's hobbies
            for hobby in data.applicant_hobby:
                hobby_data = hobby.dict()

                if hobby_data["id"] == 0:  # Insert new record
                    hobby_data.pop("id", None)  # Remove id field from hobby data
                    new_hobby = ApplicantHobby(**hobby_data)
                    db.add(new_hobby)
                    db.commit()
                    db.refresh(new_hobby)  # Refresh the new object to get any default values (e.g., auto-generated fields)
                else:  # Update existing record
                    existing_hobby = db.query(ApplicantHobby).filter(
                        ApplicantHobby.id == hobby_data["id"]
                    ).first()

                    if existing_hobby:
                        for key, value in hobby_data.items():
                            if hasattr(existing_hobby, key) and value is not None:
                                setattr(existing_hobby, key, value)
                        db.commit()
                        db.refresh(existing_hobby)  # Refresh the updated object
                    else:
                        raise HTTPException(status_code=404, detail="Applicant hobby not found for update.")
        elif component == "applicant_skill":
            # Save or update the applicant's hobbies
            for skill in data.applicant_skill:
                skill_data = skill.dict()

                if skill_data["id"] == 0:  # Insert new record
                    skill_data.pop("id", None)  # Remove id field from hobby data
                    new_skill = ApplicantSkill(**skill_data)
                    db.add(new_skill)
                    db.commit()
                    db.refresh(new_skill)  # Refresh the new object to get auto-generated fields like ID
                else:  # Update existing record
                    existing_skill = db.query(ApplicantSkill).filter(
                        ApplicantSkill.id == skill_data["id"]
                    ).first()

                    if existing_skill:
                        # Update only fields that are present and not None
                        for key, value in skill_data.items():
                            if hasattr(existing_skill, key) and value is not None:
                                setattr(existing_skill, key, value)
                        db.commit()
                        db.refresh(existing_skill)  # Refresh the updated object
                    else:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Applicant skill with ID {skill_data['id']} not found for update."
                        )
                    
        elif component == "applicant_social_media_profile":
            # Save or update the applicant's social media profiles
            for profile in data.applicant_social_media_profile:
                profile_data = profile.dict()

                if profile_data["id"] == 0:  # Insert new record
                    profile_data.pop("id", None)  # Remove id field for a new record
                    new_profile = ApplicantSocialMediaProfile(**profile_data)
                    db.add(new_profile)
                    db.commit()
                    db.refresh(new_profile)  # Refresh to fetch auto-generated fields like ID
                else:  # Update existing record
                    existing_profile = db.query(ApplicantSocialMediaProfile).filter(
                        ApplicantSocialMediaProfile.id == profile_data["id"]
                    ).first()

                    if existing_profile:
                        # Update fields only if they exist and are not None
                        for key, value in profile_data.items():
                            if hasattr(existing_profile, key) and value is not None:
                                setattr(existing_profile, key, value)
                        db.commit()
                        db.refresh(existing_profile)  # Refresh to fetch updated values
                    else:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Applicant social media profile with ID {profile_data['id']} not found for update."
                        )
        


    result["success"] = True
    result["message"] = "Saved successfully."
    return result



#-----------------------------------------------------------------------------------------------------

def get_all_applicant_detals(db: Session) -> List[ApplicantDetailsView]:
    # Fetch all applicant details from the ViewApplicantDetails view
    applicant_details = db.query(ViewApplicantDetails).all()

    # If no applicant details are found, raise an exception
    if not applicant_details:
        raise HTTPException(status_code=404, detail="No applicant details found")

    # Map the fetched data to the ApplicantDetailsView schema
    return [ApplicantDetailsView(**applicant.__dict__) for applicant in applicant_details]


def get_applicant_master(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantMasterResponse]:
    # Base SQL query to fetch data
    sql_query = text("""
    SELECT 
        a.applicant_id,
        a.first_name,
        a.middle_name,
        a.last_name,
        a.date_of_birth,
        b.id AS gender_id,
        b.gender AS gender_name,
        a.blood_group,
        d.id AS marital_status_id,
        d.marital_status,
        e.id AS nationality_id,
        e.nationality_name
    FROM
        applicant_master a
    LEFT JOIN
        app_gender b ON a.gender_id = b.id
    
    LEFT JOIN
        app_marital_status d ON a.marital_status_id = d.id
    LEFT JOIN
        app_nationality e ON a.nationality_id = e.id
    """)

    # Add filtering for applicant_id if provided
    if applicant_id:
        sql_query = text(f"{sql_query} WHERE a.applicant_id = :applicant_id")

    # Execute the query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No applicant master data found")

    # Convert SQL result rows to Pydantic response models
    applicants = [ApplicantMasterResponse(**dict(row._asdict())) for row in rows]

    return applicants



#----------------------------------------------------------------------------------------

def applicant_present_address(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantPresentAddressResponse]:
    
    sql_query = text("""
        SELECT 
        -- Table f: applicant_present_address
        f.id AS present_address_id,
        f.present_house_or_flat_name,
        f.present_house_flat_or_door_number,
        f.present_road_name,
        f.present_street_name,
        f.present_land_mark,
        f.present_pin_code,
       f.is_permenent_address_same_as_present,              
    
        -- Table g: app_post_offices (Present Address)
        g.id AS present_post_office_id,
        g.post_office_name AS present_post_office_name,
        g.pin_code AS present_post_office_pin_code,
        g.contact_number AS present_post_office_contact,
        g.latitude AS present_post_office_latitude,
        g.longitude AS present_post_office_longitude,

        -- Table h: app_cities (Present Address)
        h.id AS present_city_id,
        h.city_name AS present_city_name,

        -- Table i: app_taluks (Present Address)
        i.id AS present_taluk_id,
        i.taluk_name AS present_taluk_name,

        -- Table j: app_districts (Present Address)
        j.id AS present_district_id,
        j.district_name AS present_district_name,

        -- Table k: app_states (Present Address)
        k.id AS present_state_id,
        k.state_name AS present_state_name,
        

        -- Table l: app_countries (Present Address)
        l.id AS present_country_id,
        l.country_name_english AS present_country_name
    FROM 
        applicant_master a
    -- Join applicant_present_address to get the present address details
    LEFT JOIN
        applicant_present_address f ON a.applicant_id = f.applicant_id  

    -- Join other related tables to fetch present address information
    LEFT JOIN
        app_post_offices g ON f.present_post_office_id = g.id
    LEFT JOIN
        app_cities h ON f.present_city_id = h.id
    LEFT JOIN
        app_taluks i ON f.present_taluk_id = i.id
    LEFT JOIN
        app_districts j ON f.present_district_id = j.id
    LEFT JOIN
        app_states k ON f.present_state_id = k.id
    LEFT JOIN
        app_countries l ON f.present_country_id = l.id


    """)

    # Add filtering for applicant_id if provided
    if applicant_id:
        sql_query = text(f"{sql_query} WHERE a.applicant_id = :applicant_id")

    # Execute the query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No applicant master data found")

    # Convert SQL result rows to Pydantic response models
    applicants_address = [ApplicantPresentAddressResponse(**dict(row._asdict())) for row in rows]

    return applicants_address

#---------------------------------------------------------------------------------------------------
# def applicant_permanent_address(
#     db: Session, applicant_id: Optional[int] = None
# ) -> List[ApplicantPermanentAddressResponse]:
#     # SQL query to fetch the data
#     sql_query = text("""
#         SELECT 
#             -- Table f: applicant_permanent_address (Permanent Address)
#             f.id AS permanent_address_id,
#             f.permanent_house_or_flat_name,
#             f.permanent_house_flat_or_door_number,
#             f.permanent_road_name,
#             f.permanent_street_name,
#             f.permanent_land_mark,
#             f.permanent_pin_code,
            
#             -- Table g: app_post_offices (Permanent Address - Post office details)
#             g.id AS permanent_post_office_id,
#             g.post_office_name AS permanent_post_office_name,
#             g.pin_code AS permanent_post_office_pin_code,
#             g.contact_number AS permanent_post_office_contact,

#             -- Table h: app_cities (Permanent Address - City details)
#             h.id AS permanent_city_id,
#             h.city_name AS permanent_city_name,

#             -- Table i: app_taluks (Permanent Address - Taluk details)
#             i.id AS permanent_taluk_id,
#             i.taluk_name AS permanent_taluk_name,

#             -- Table j: app_districts (Permanent Address - District details)
#             j.id AS permanent_district_id,
#             j.district_name AS permanent_district_name,

#             -- Table k: app_states (Permanent Address - State details)
#             k.id AS permanent_state_id,
#             k.state_name AS permanent_state_name,

#             -- Table l: app_countries (Permanent Address - Country details)
#             l.id AS permanent_country_id,
#             l.country_name_english AS permanent_country_name,

#             -- Table a: applicant_master (Applicant details)
#             a.applicant_id,
#             a.first_name AS applicant_first_name,
#             a.middle_name AS applicant_middle_name,
#             a.last_name AS applicant_last_name
#         FROM 
#             applicant_permanent_address f
#         LEFT JOIN
#             applicant_master a ON f.applicant_id = a.applicant_id
#         LEFT JOIN
#             app_post_offices g ON f.permanent_post_office_id = g.id
#         LEFT JOIN
#             app_cities h ON f.permanent_city_id = h.id
#         LEFT JOIN
#             app_taluks i ON f.permanent_taluk_id = i.id
#         LEFT JOIN
#             app_districts j ON f.permanent_district_id = j.id
#         LEFT JOIN
#             app_states k ON f.permanent_state_id = k.id
#         LEFT JOIN
#             app_countries l ON f.permanent_country_id = l.id
#     """)

#     # Add filtering for applicant_id if provided
#     if applicant_id:
#         sql_query = text(f"{sql_query} WHERE a.applicant_id = :applicant_id")

#     # Execute the query with parameters
#     params = {"applicant_id": applicant_id} if applicant_id else {}
#     result = db.execute(sql_query, params)

#     rows = result.fetchall()

#     if not rows:
#         raise HTTPException(status_code=404, detail="No applicant permanent address data found")

#     # Convert SQL result rows to Pydantic response models
#     applicants_address = [ApplicantPermanentAddressResponse(**dict(row._asdict())) for row in rows]

#     return applicants_address


def applicant_permanent_address(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantPermanentAddressResponse]:
    sql_query = text("""
    SELECT 
        -- Table f: applicant_permanent_address (Permanent Address)
        f.id AS permanent_address_id,
        f.permanent_house_or_flat_name,
        f.permanent_house_flat_or_door_number,
        f.permanent_road_name,
        f.permanent_street_name,
        f.permanent_land_mark,
        f.permanent_pin_code,
        
        -- Table g: app_post_offices (Permanent Address - Post office details)
        g.id AS permanent_post_office_id,
        g.post_office_name AS permanent_post_office_name,
        g.pin_code AS permanent_post_office_pin_code,
        g.contact_number AS permanent_post_office_contact,

        -- Table h: app_cities (Permanent Address - City details)
        h.id AS permanent_city_id,
        h.city_name AS permanent_city_name,

        -- Table i: app_taluks (Permanent Address - Taluk details)
        i.id AS permanent_taluk_id,
        i.taluk_name AS permanent_taluk_name,

        -- Table j: app_districts (Permanent Address - District details)
        j.id AS permanent_district_id,
        j.district_name AS permanent_district_name,

        -- Table k: app_states (Permanent Address - State details)
        k.id AS permanent_state_id,
        k.state_name AS permanent_state_name,

        -- Table l: app_countries (Permanent Address - Country details)
        l.id AS permanent_country_id,
        l.country_name_english AS permanent_country_name,

        -- Table a: applicant_master (Applicant details)
        a.applicant_id,
        a.first_name AS first_name,
        a.middle_name AS middle_name,
        a.last_name AS last_name

    FROM 
        applicant_permanent_address f

    -- Join applicant_master to get applicant details
    LEFT JOIN
        applicant_master a ON f.applicant_id = a.applicant_id

    -- Join other related tables to fetch permanent address information
    LEFT JOIN
        app_post_offices g ON f.permanent_post_office_id = g.id
    LEFT JOIN
        app_cities h ON f.permanent_city_id = h.id
    LEFT JOIN
        app_taluks i ON f.permanent_taluk_id = i.id
    LEFT JOIN
        app_districts j ON f.permanent_district_id = j.id
    LEFT JOIN
        app_states k ON f.permanent_state_id = k.id
    LEFT JOIN
        app_countries l ON f.permanent_country_id = l.id
    """)

    # Add filtering for applicant_id if provided
    if applicant_id:
        sql_query = text(f"{sql_query} WHERE a.applicant_id = :applicant_id")
    
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No permanent address data found")

    # Convert SQLAlchemy row objects to Pydantic models
    permanent_addresses = [
        ApplicantPermanentAddressResponse(**dict(row._asdict())) for row in rows
    ]

    return permanent_addresses


#---------------------------------------------------------------------------------------------------


def get_applicant_contact_details(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantContactDetailsResponse]:
    sql_query = text("""
        SELECT 
            -- Table a: applicant_contact_details
            a.id AS contact_details_id,
            a.personal_mobile_number,
            a.personal_whatsapp_number,
            a.personal_email_id,
            a.is_deleted AS contact_deleted,

            -- Table b: applicant_master
            b.applicant_id,
            b.first_name AS first_name,
            b.middle_name AS middle_name,
            b.last_name AS last_name

        FROM 
            applicant_contact_details a

        -- Join applicant_master to get applicant details
        LEFT JOIN
            applicant_master b ON b.applicant_id = a.applicant_id
    """)

    # Add filtering for applicant_id if provided
    if applicant_id:
        sql_query = text(f"{sql_query} WHERE b.applicant_id = :applicant_id")

    # Execute query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No contact details found for the applicant")

    # Convert rows to response schema
    contact_details = [
        ApplicantContactDetailsResponse(**dict(row._asdict())) for row in rows
    ]

    return contact_details
#--------------------------------------------------------------------------------

def get_applicant_educational_qualifications(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantEducationalQualificationResponse]:
    sql_query = text("""
        SELECT
            eq.id AS qualification_id,
            eq.institution,
            eq.percentage_of_score,
            eq.month_and_year_of_completion,
            eq.status AS qualification_status,
            eq.is_deleted AS qualification_deleted,
            el.id AS education_level_id,
            el.education_level,
            es.id AS education_stream_id,
            es.education_stream,
            sc.id AS education_subject_or_course_id,
            sc.subject_or_course_name,
            am.first_name,
            am.middle_name,
            am.last_name
        FROM
            applicant_educational_qualification eq
        LEFT JOIN
            app_education_level el ON eq.education_level_id = el.id
        LEFT JOIN
            app_education_stream es ON eq.education_stream_id = es.id
        LEFT JOIN
            app_education_subject_or_course sc ON eq.education_subject_or_course_id = sc.id
        LEFT JOIN
            applicant_master am ON eq.applicant_id = am.applicant_id
        WHERE
            eq.is_deleted = 'no'
    """)

    # Add filtering for applicant_id if provided
    if applicant_id:
        sql_query = text(f"{sql_query} AND eq.applicant_id = :applicant_id")

    # Execute query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No educational qualifications found for the applicant")

    # Convert rows to response schema
    educational_details = [
        ApplicantEducationalQualificationResponse(**dict(row._asdict())) for row in rows
    ]

    return educational_details

#---------------------------------------------------------------------------------------------------

def get_applicant_professional_qualifications(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantProfessionalQualificationResponse]:
    sql_query = text("""
        SELECT
            apq.id,
            apq.applicant_id,
            apq.qualification_id,
            apq.institution,
            apq.membership_number,
            apq.enrollment_date,
            apq.percentage_of_score,
            apq.month_and_year_of_completion,
            apq.status,
            apq.is_deleted,
            ap.profession_name,
            am.first_name,
            am.middle_name,
            am.last_name
        FROM
            applicant_professional_qualifications apq
        LEFT JOIN
            app_profession ap ON apq.qualification_id = ap.id
        LEFT JOIN
            applicant_master am ON apq.applicant_id = am.applicant_id
        WHERE
            apq.applicant_id = :applicant_id AND apq.is_deleted = 'no';
    """)

    # Execute query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No professional qualifications found for the applicant")

    # Convert rows to response schema
    qualifications = [
        ApplicantProfessionalQualificationResponse(**dict(row._asdict())) for row in rows
    ]

    return qualifications

#-----------------------------------------------------------------------------------------------



def get_applicant_experience(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantExperienceResponse]:
    sql_query = text("""
        SELECT
            ae.id,
            ae.applicant_id,
            ae.company_name,
            ae.company_address,
            ae.company_contact_number,
            ae.company_email,
            ae.position_held,
            ae.responsibility,
            ae.start_date,
            ae.end_date,
            ae.last_salary,
            ae.reason_for_leaving,
            ae.is_deleted,
            am.first_name,
            am.middle_name,
            am.last_name
        FROM
            applicant_experience ae
        LEFT JOIN
            applicant_master am ON ae.applicant_id = am.applicant_id
        WHERE
            ae.applicant_id = :applicant_id AND ae.is_deleted = 'no';
    """)

    # Execute query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No experience found for the applicant")

    # Convert rows to response schema
    experience_data = [
        ApplicantExperienceResponse(**dict(row._asdict())) for row in rows
    ]

    return experience_data

#-------------------------------------------------------------------------------------------------------


def get_applicant_language_proficiency(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantLanguageProficiencyResponse]:
    sql_query = text("""
        SELECT
            alp.id,
            alp.applicant_id,
            al.language,
            r_proficiency.proficiency_level AS read_proficiency,
            w_proficiency.proficiency_level AS write_proficiency,
            s_proficiency.proficiency_level AS speak_proficiency,
            alp.is_deleted,
            am.first_name,
            am.middle_name,
            am.last_name
        FROM
            applicant_language_proficiency alp
        LEFT JOIN
            app_languages al ON alp.language_id = al.id
        LEFT JOIN
            app_language_proficiency r_proficiency ON alp.read_proficiency_id = r_proficiency.id
        LEFT JOIN
            app_language_proficiency w_proficiency ON alp.write_proficiency_id = w_proficiency.id
        LEFT JOIN
            app_language_proficiency s_proficiency ON alp.speak_proficiency_id = s_proficiency.id
        LEFT JOIN
            applicant_master am ON alp.applicant_id = am.applicant_id
        WHERE
            alp.applicant_id = :applicant_id AND alp.is_deleted = 'no';
    """)

    # Execute query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No language proficiency data found for the applicant")

    # Convert rows to response schema
    language_proficiency_data = [
        ApplicantLanguageProficiencyResponse(**dict(row._asdict())) for row in rows
    ]

    return language_proficiency_data

#-----------------------------------------------------------------------------------------------


def get_applicant_hobbies(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantHobbyResponse]:
    sql_query = text("""
        SELECT
            ah.id,
            ah.applicant_id,
            ah.applicant_hobby,
            ah.remarks,
            am.first_name,
            am.middle_name,
            am.last_name
        FROM
            applicant_hobby ah
        LEFT JOIN
            applicant_master am ON ah.applicant_id = am.applicant_id
        WHERE
            ah.applicant_id = :applicant_id;
    """)

    # Execute query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No hobbies found for the applicant")

    # Convert rows to response schema
    hobbies = [
        ApplicantHobbyResponse(**dict(row._asdict())) for row in rows
    ]

    return hobbies

#----------------------------------------------------------------------------------------------


def get_applicant_skills(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantSkillResponse]:
    # SQL query to fetch skills along with applicant data
    sql_query = text("""
       SELECT
            app_skill.id,
            app_skill.applicant_id,
            app_skill.skill_id,
            s.skill,
            app_skill.remarks,
            am.first_name,
            am.middle_name,
            am.last_name
        FROM
            applicant_skill app_skill
        LEFT JOIN
            app_skills s ON app_skill.skill_id = s.id
        LEFT JOIN
            applicant_master am ON app_skill.applicant_id = am.applicant_id
        WHERE
            app_skill.is_deleted = 'no'
            AND (app_skill.applicant_id = :applicant_id);  
    """)

    # Execute query with parameters
    params = {"applicant_id": applicant_id} if applicant_id else {}
    result = db.execute(sql_query, params)

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No skills found for the applicant")

    # Convert rows to response schema
    skills = [
        ApplicantSkillResponse(**dict(row._asdict())) for row in rows
    ]

    return skills

#---------------------------------------------------------------------------------------------
def get_applicant_social_media_profiles(
    db: Session, applicant_id: Optional[int] = None
) -> List[ApplicantSocialMediaResponse]:
    
    sql_query = text("""
       SELECT
            asm.id,
            asm.applicant_id,
            asm.facebook,
            asm.youtube,
            asm.xhandle,
            asm.linked_in,
            am.first_name,
            am.middle_name,
            am.last_name
        FROM
            applicant_social_media_profile asm
        LEFT JOIN
            applicant_master am ON asm.applicant_id = am.applicant_id
        WHERE
            asm.is_deleted = 'no'
            AND ( asm.applicant_id = :applicant_id);  
    """)

    # Parameters for the query
    params = {"applicant_id": applicant_id} if applicant_id else {}

    # Execute the query
    result = db.execute(sql_query, params)

    # Fetch all results
    rows = result.fetchall()

    # Check if no results were found
    if not rows:
        raise HTTPException(status_code=404, detail="No social media profiles found for the applicant")

    # Convert query results into response schema
    social_media_profiles = [
        ApplicantSocialMediaResponse(**dict(row._asdict())) for row in rows
    ]

    return social_media_profiles
#-------------------------------------------------------------------------
from sqlalchemy.exc import SQLAlchemyError
def save_schedule(schedule, db: Session):
    try:
        # Check if it's an insert or update
        if schedule.id == 0:  # Insert new schedule
            # Create a new InterviewSchedule instance without the id field (let DB auto-generate it)
            new_schedule = InterviewSchedule(**schedule.dict(exclude_unset=True, exclude={"id"}))  # Exclude id field
            
            # Add the new schedule to the session
            db.add(new_schedule)
            
            # Commit the session to save the new schedule
            db.commit()
            
            # Refresh to get the updated instance with auto-generated fields like id
            db.refresh(new_schedule)
            
            return new_schedule
        
        else:  # Update existing schedule
            # Fetch the existing schedule by id
            existing_schedule = db.query(InterviewSchedule).filter(InterviewSchedule.id == schedule.id).first()
            
            if existing_schedule:
                # Update the fields with the new data
                for key, value in schedule.dict(exclude_unset=True).items():
                    if hasattr(existing_schedule, key) and value is not None:
                        setattr(existing_schedule, key, value)
                
                # Commit the session to save the changes
                db.commit()
                
                # Refresh to get the updated instance
                db.refresh(existing_schedule)
                
                return existing_schedule
            else:
                # If no schedule is found, raise an exception
                raise Exception(f"Interview schedule with id {schedule.id} not found.")
    
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of a database error
        raise Exception(f"Error saving schedule: {str(e)}")
    except Exception as e:
        db.rollback()  # Rollback in case of a non-SQLAlchemy error
        raise Exception(f"Error: {str(e)}")
#----------------------------------------------------------------------------------------------------------