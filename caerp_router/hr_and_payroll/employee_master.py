from caerp_db.common.models import Employee
from caerp_schema.hr_and_payroll.hr_and_payroll_schema import EmployeeDetails, EmployeeMasterSchema, EmployeePresentAddressSchema, EmployeePermanentAddressSchema, EmployeeContactDetailSchema, EmployeeBankAccountDetailSchema, EmployeeMasterSchemaForGet
from caerp_db.database import get_db
from caerp_db.hr_and_payroll import db_employee_master
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from caerp_db.hash import Hash
from caerp_auth import oauth2
from sqlalchemy.exc import SQLAlchemyError
from typing import List,Optional, Union,Dict
from caerp_constants.caerp_constants import DeletedStatus,ActiveStatus, VerifiedStatus, ApprovedStatus
from fastapi import APIRouter, Body ,Depends,Request,HTTPException,status,UploadFile,File,Response, Path, Query
from caerp_auth.authentication import authenticate_user
from caerp_auth.oauth2 import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from datetime import date,datetime
from caerp_constants.caerp_constants import DeletedStatus,ActionType, EmployeeActionType
from collections import defaultdict

router = APIRouter(
    prefix ='/Employee',
    tags=['Employee']
)


# #save employee master
@router.post('/save_employee_master', response_model=EmployeeDetails)
def save_employee_master(
        id: int = 0,
        Action: EmployeeActionType = Query(...),
        request: EmployeeDetails = Body(...),
        db: Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)):

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
    
   auth_info = authenticate_user(token)
   user_id = auth_info["user_id"]
   try:
     db_employee_master.save_employee_master(db, request, id, user_id, Action)
     return {
            "success": True,
            "message": "Saved /Updated successfully"
    }
   except Exception as e:    
      raise HTTPException(status_code=500, detail=str(e))
   


@router.get("/get_employee_details")
def get_employee_details(id: Optional[int] = None, db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme),
    # include_master: bool = Query(False, description="Include employee master details"),
    include_present_address: bool = Query(False, description="Include present address details"),
    include_permanent_address: bool = Query(False, description="Include permanent address details"),
    include_contact_details: bool = Query(False, description="Include contact details"),
    include_bank_details: bool = Query(False, description="Include bank details"),
    ):
  """
    -**Retrieve employee master by id.**
   """
  if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    

  employee_details = defaultdict(dict)
    
  employees = db_employee_master.get_employee_master_details(db)
  for emp in employees:
    employee_details[emp.employee_id]['employee_master'] = EmployeeMasterSchema(
            **{k: v.isoformat() if isinstance(v, date) else v for k, v in emp.__dict__.items()}
            )
    
  if include_present_address:
    present_addresses = db_employee_master.get_present_address_details(db)
    for present in present_addresses:
      employee_details[present.employee_id].setdefault('present_address', []).append(
                EmployeePresentAddressSchema(**present.__dict__)
            )
      
  if include_permanent_address:
    permanent_addresses = db_employee_master.get_permanent_address_details(db)
    for permanent in permanent_addresses:
      employee_details[permanent.employee_id].setdefault('permanent_address', []).append(
                EmployeePermanentAddressSchema(**permanent.__dict__)
            )    
    
  if include_contact_details:
    contact_info = db_employee_master.get_contact_details(db)
    for contact in contact_info:
     employee_details[contact.employee_id].setdefault('contact_details', []).append(
             EmployeeContactDetailSchema(**contact.__dict__)
            )

  if include_bank_details:
    bank_info = db_employee_master.get_bank_details(db)
    for bank in bank_info:
     employee_details[bank.employee_id].setdefault('bank_details', []).append(
             EmployeeBankAccountDetailSchema(**bank.__dict__)
            )
     
  if id is not None:
    return employee_details.get(id, {})
  else:
    return employee_details
  

#get consultants
@router.get("/get_consultants/" , response_model=List[EmployeeMasterSchema])
def get_consultants(db: Session = Depends(get_db), token: str = Depends(oauth2.oauth2_scheme)):
    """
    -**Retrieve employees who are consultants.**
   """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_employee_master.get_consultants(db)



@router.delete("/employee/delete/undelete/{id}")
def delete_employee_master(
    id: int,
    Action: ActionType = Query(..., title="Select delete or undelete"),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete employee master by employee_id.
    Set the 'is_deleted' flag to 'yes' to mark the employee master as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_employee_master.delete_undelete_employee_master(db, id, Action)  