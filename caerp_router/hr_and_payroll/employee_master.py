from caerp_db.common.models import Employee, EmployeeMasterView
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeMasterSchema, EmployeeMasterSchemaForGet, EmployeePersonalDetailSchema, EmployeeAddressDetailSchema, EmployeeContactDetailSchema, EmployeeBankAccountDetailSchema
from caerp_db.database import get_db
from caerp_db.hr_and_payroll import db_employee_master
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from caerp_db.hash import Hash
from caerp_auth import oauth2
from sqlalchemy.exc import SQLAlchemyError
from typing import List,Optional, Union,Dict
from caerp_constants.caerp_constants import DeletedStatus,ActiveStatus, VerifiedStatus, ApprovedStatus
from fastapi import APIRouter ,Depends,Request,HTTPException,status,UploadFile,File,Response
from caerp_auth.authentication import authenticate_user
from caerp_auth.oauth2 import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt



router = APIRouter(
    prefix ='/Employee',
    tags=['Employee']
)


#save employee master
@router.post('/save_employee_master', response_model= EmployeeMasterSchema)
def save_employee_master(request: EmployeeMasterSchema = Depends(), id: int = 0, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
   """
    Creation or updation of Employee Master.
     
    -**Request** : Data needed for creation/updation provided through schema "EmployeeMasterSchema".

    -**id** : Integer parameter, which is the primary key.
    - If id is 0, it indicates creation of new Employee.
    - If id is not 0, it indicates updation of existing Employee.

    -**db** : database session for adding and updating tables.

    -**Exception** : If any error occurs during the execution of try: block, an exception will be raised.
    - Returns HTTPException with status code = 500 with error details.
   """
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
#    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#    user_id = payload.get("user_id")
   auth_info = authenticate_user(token)
   user_id = auth_info["user_id"]
   try:
      return db_employee_master.save_employee_master(db, request, id, user_id)
   except Exception as e:    
      raise HTTPException(status_code=500, detail=str(e))
  
#-----------------------------------------------------------------------------------------------------------------------------------------------------------   

#get employee status
@router.get("/get_deleted_employees/" , response_model=List[EmployeeMasterSchemaForGet])
async def get_deleted_employees(deleted_status: DeletedStatus = DeletedStatus.NOT_DELETED, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Retrieve employee delete status.**
   """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_employee_master.get_deleted_employees(db, deleted_status)

#----------------------------------------------------------------------------------------------------------------------------------

#read specific employee by id
@router.get("/employee{id}", response_model= EmployeeMasterSchemaForGet)
def get_employee_by_id(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
  """
    -**Retrieve employee details by id.**
   """
  if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
  return  db_employee_master.get_employee(db, id)

#-----------------------------------------------------------------------------------------------------------------------------

#delete specific employee by id
@router.delete("/delete/employee_master/{id}")
def delete_employee_master(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Delete employee details by id.**
   """ 
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    auth_info = authenticate_user(token)
    user_id = auth_info["user_id"]
    return db_employee_master.delete_employee_master(db, id, deleted_by=user_id)

#----------------------------------------------------------------------------------------------------------------------------

@router.get("/get_verified_employees/" , response_model=List[EmployeeMasterSchemaForGet])
def get_verified_employees(verified_status: VerifiedStatus = VerifiedStatus.VERIFIED, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Retrieve employee verified status.**
   """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_employee_master.get_verified_employees(db, verified_status)

#------------------------------------------------------------------------------------------------------------------------

@router.get("/get_approved_employees/" , response_model=List[EmployeeMasterSchemaForGet])
def get_approved_employees(approved_status: ApprovedStatus = ApprovedStatus.APPROVED, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Retrieve employee approved status.**
   """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing") 
    return db_employee_master.get_approved_employees(db, approved_status)
    
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@router.post('/update_employee_personal_details', response_model=EmployeePersonalDetailSchema)
def update_employee_personal_details(request: EmployeePersonalDetailSchema, id: int, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
   """
    -**Update Employee personal details.**
   """   
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   auth_info = authenticate_user(token)
   user_id = auth_info["user_id"]
   try:
      return db_employee_master.update_employee_personal_details(db, request, id, user_id)
   except Exception as e:    
      raise HTTPException(status_code=500, detail=str(e))  
   
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------   

@router.post('/update_employee_address_details', response_model=EmployeeAddressDetailSchema)
def update_employee_address_details(request: EmployeeAddressDetailSchema, id: int, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
   """
    -**Update Employee address details.**
   """ 
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   auth_info = authenticate_user(token)
   user_id = auth_info["user_id"]
   try:
      return db_employee_master.update_employee_address_details(db, request, id, user_id)
   except Exception as e:    
      raise HTTPException(status_code=500, detail=str(e))   
   
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@router.post('/update_employee_contact_details', response_model=EmployeeContactDetailSchema)
def update_employee_contact_details(request: EmployeeContactDetailSchema, id: int, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
   """
    -**Update Employee contact details.**
   """ 
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   auth_info = authenticate_user(token)
   user_id = auth_info["user_id"]
   try:
      return db_employee_master.update_employee_contact_details(db, request, id, user_id)
   except Exception as e:    
      raise HTTPException(status_code=500, detail=str(e))      

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   
@router.post('/update_employee_bank_acc_details', response_model=EmployeeBankAccountDetailSchema)
def update_employee_bank_acc_details(request: EmployeeBankAccountDetailSchema, id: int, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
   """
    -**Update Employee Bank Account details.**
   """ 
   if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   auth_info = authenticate_user(token)
   user_id = auth_info["user_id"]
   try:
      return db_employee_master.update_employee_bank_acc_details(db, request, id, user_id)
   except Exception as e:    
      raise HTTPException(status_code=500, detail=str(e))   
   
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#get consultants
@router.get("/get_consultants/" , response_model=List[EmployeeMasterSchemaForGet])
def get_consultants(db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Retrieve employees who are consultants.**
   """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_employee_master.get_consultants(db)      

#-----------------------------------------------------------------------------------------------------------------------------

#get consultant by id
@router.get("/get_consultant_by_ID/" , response_model=EmployeeMasterSchemaForGet)
def get_consultant_by_id(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Retrieve consultant by id.**
   """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_employee_master.get_consultant_by_id(db, id)