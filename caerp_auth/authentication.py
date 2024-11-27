from fastapi import FastAPI,APIRouter, Depends, HTTPException, Header, Request, status
  
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from caerp_db.services.model import CustomerMaster
from caerp_schema.common.common_schema import CustomerLoginRequest, LoginRequest
from sqlalchemy.orm import Session
from caerp_db.database import get_db
from caerp_db.hash import Hash
from caerp_auth import oauth2
# from .oauth2 import create_access_token, get_current_user,oauth2_scheme,SECRET_KEY, ALGORITHM
from .oauth2 import create_access_token,SECRET_KEY, ALGORITHM
from starlette.requests import Request
from sqlalchemy import update
from datetime import datetime,timedelta
from typing import Dict, Union
from jose import JWTError, jwt
import user_agent
from caerp_functions import send_message
from datetime import datetime
from caerp_auth.oauth2 import oauth2_scheme

from sqlalchemy import text
from sqlalchemy.sql import text

import geoip2.database
import geoip2.errors
from caerp_db.database import get_db
from caerp_db.common import models,db_otp,db_user
from caerp_db.common.models import EmployeeMaster, EmployeeContactDetails,OtpGeneration


from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from user_agents import parse
from ua_parser import user_agent_parser
from geoip2 import database, errors
from starlette.requests import Request
from fastapi import Header
import geoip2.database
import os,random
from settings import GEOIP_DATABASE_PATH
from fastapi.responses import JSONResponse




geoip2_reader = geoip2.database.Reader(GEOIP_DATABASE_PATH)
app = FastAPI()
router = APIRouter(
    tags=['Authentication']
)


import logging

logger = logging.getLogger(__name__)


# class MyCustomException(Exception):
#     def __init__(self, status_code: int, detail: str, headers: dict = None):
#         self.status_code = status_code
#         self.detail = detail
#         self.headers = headers

# Exception handler for custom exceptions
# @app.exception_handler(MyCustomException)
# def my_custom_exception_handler(request: Request, exc: MyCustomException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": exc.detail},
#         headers=exc.headers
#     )


@router.post('/admin-login')
def get_token(
    no_of_attempts: int =0 ,
    request_data: OAuth2PasswordRequestForm = Depends(),
    user_agent: str = Header(None),
    request: Request = None,
    db: Session = Depends(get_db)):
    
    # user = db.query(models.UserBaseNew).filter(models.UserBaseNew.user_name == request_data.username).first()

    user = db.query(models.UserBase).filter(models.UserBase.user_name == request_data.username).first()
    if not user:
        login_attempt = 3 - no_of_attempts
        # detail_message = f'{login_attempt} out of 3 attempts remaining. Username incorrect.'
        detail_message = {
            "message": "Incorrect Username",
            "detail": f"{login_attempt} out of 3 attempts remaining",
            "status": False
        }
        headers = {"X-Error": "Username incorrect."}
        # return {
        #     'detail': detail_message,
        #     'message': 'Username incorrect',
        #     # 'headers': headers
        # }
        # raise  MyCustomException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message, headers=headers)
    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message, headers=headers)
    
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{login_attempt} out of 3 attempts remaining. Username incorrect.', headers={"X-Error": "Username incorrect."})
    # else:
    elif user.locked_upto is not None and datetime.utcnow() < user.locked_upto:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Your account is locked, Please Try ain later')
       
    elif no_of_attempts >= 3 :
            login_attempt =3-no_of_attempts
            db_user.update_user_locked_time(db,request_data.username)
            detail_message = {
            "message": "You are temperarly locked for 5 min.",
            "detail": f"{login_attempt} out of 3 attempts remaining",
            "status": False
            }
            headers = {"X-Error": "you aretemperarly locked for 5 min."}
            raise HTTPException(status_code=403, detail=detail_message, headers=headers)

                # my_custom_exception_handler(name="Incorect Password")
            # raise HTTPException(status_code=403, detail=f"{login_attempt} out of 3 attempts remaining, and you aretemperarly locked for 5 min.")
    elif user.is_active == 'no':        
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Your account is blocked, Please Contact the admin')

    else:
        hashed_password_from_db = user.login_password
        plain_text_password_from_request = request_data.password
        if not Hash.verify(hashed_password_from_db, plain_text_password_from_request):
            
            login_attempt = 3 - no_of_attempts
            # detail_message = f'{login_attempt} out of 3 attempts remaining. Password incorrect.'
            detail_message = {
            "message": "Password incorrect.",
            "detail": f"{login_attempt} out of 3 attempts remaining",
            "status": False
            }
            headers = {"X-Error": "Password incorrect."}

            # return {
            #     'detail': detail_message,
            #     'message': 'Password incorrect'
            # }
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message, headers=headers)

        else:
        # Parse user agent string
            user_agent_info = parse(user_agent)

            # Extract browser information
            browser_type = user_agent_info.browser.family
            browser_version = user_agent_info.browser.version_string

            # Extract operating system information
            operating_system = user_agent_info.os.family
            os_version = user_agent_info.os.version_string

            # Extract user IP address
            user_ip = request.client.host


            # if not user:
            #     login_attempt = 3 - no_of_attempts
            #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{login_attempt} out of 3 attempts remaining.', headers={"X-Error": "Invalid credentials."})
                # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, message=f'{login_attempt} out of 3 attempts remaining.' ,detail='Invalid credentials')
            
            
                # detail_message_with_custom_message = 'Incorrect password.'
                # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message, headers=headers)

            
            
            # Extract referrer from request headers
            referrer = request.headers.get('referer')

            city = None
            region = None
            country = None

            # Lookup geographic location based on IP address
            try:
                response = geoip2_reader.city(user_ip)
                city = response.city.name if response.city.name else ""
                region = response.subdivisions.most_specific.name if response.subdivisions.most_specific.name else ""
                country = response.country.name if response.country.name else ""
                print("response", response)
            
            except geoip2.errors.AddressNotFoundError as e:

                logger.error(f"Address not found for IP {user_ip}: {e}")
                pass  # Handle error if needed
            
            try:
                if user.is_first_login == 'yes':                     
                    update_query = text("UPDATE users SET is_first_login= 'no' WHERE user_name = :user_name ")
                    db.execute(update_query, {'user_name':  request_data.username})
                # Insert login details into app_admin_log table
                result = db.execute(
                text("INSERT INTO users_log (user_id, logged_in_ip, browser_type, browser_family, browser_version, operating_system, os_family, os_version, referrer,location) "
                    "VALUES (:user_id, :logged_in_ip, :browser_type, :browser_family, :browser_version, :operating_system, :os_family, :os_version, :referrer, :city)"),
                {
                    'user_id': user.id,
                    'logged_in_ip': user_ip,
                    'browser_type': browser_type,
                    'browser_family': browser_type,  # Keeping it same as browser_type, you may adjust as needed
                    'browser_version': browser_version,
                    'operating_system': operating_system,
                    'os_family': operating_system,  # Keeping it same as operating_system, you may adjust as needed
                    'os_version': os_version,
                    'referrer': referrer,
                    'city': city,
                    # 'region': region,
                    # 'country': country
                }
            )
                # Retrieve the last inserted ID
                log_id = result.lastrowid
                print("last row id : ",log_id)
                # Commit the transaction
                db.commit()

                employee_data = db.query(models.EmployeeMaster).filter(EmployeeMaster.employee_id == user.employee_id).first()
                
                employee_contact_data =  db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == user.employee_id).first()
                mobile_otp_value = random.randint(pow(10,5), pow(10,5+1)-1)  
                new_otp = db_otp.create_otp(db, mobile_otp_value,user.employee_id)
                mobile_otp_id = new_otp.id    
                # message= f"{mobile_otp_value}is your SECRET One Time Password (OTP) for your mobile registration. Please use this password to complete your transaction. From:BRQ GLOB TECH"
                # temp_id= 1607100000000128308

                sms_type= 'OTP'
                template_data = db_user.get_templates_by_type(db,sms_type)
                temp_id= template_data.template_id
                template_message = template_data.message_template
                replace_values = [ mobile_otp_value, 'mobile registration']
                placeholder = "{#var#}"
                for value in replace_values:
                    template_message = template_message.replace(placeholder, str(value),1)
                             
                
                try:
                    send_message.send_sms_otp(employee_contact_data.personal_mobile_number,template_message,temp_id,db)
                #  db_send_sms.send_sms(new_customer.mobile_number,message,temp_id)
                except Exception as e:
                    # Handle sms sending failure
                    print(f"Failed to send message: {str(e)}")
                mother_customer_data =  db.query(CustomerMaster).filter(
                     CustomerMaster.is_mother_customer== 'yes',
                     CustomerMaster.is_deleted == 'no').first()
                if mother_customer_data: 
                     mother_customer_id = mother_customer_data.customer_id
                # Query the roles associated with the user
                roles = db.query(models.UserRole).filter(
                    models.UserRole.employee_id == user.employee_id,
                    models.UserRole.is_deleted == 'no'
                ).all()
                
                if not roles:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no assigned roles")

                role_ids = [role.role_id for role in roles]
                password_reset_date = user.password_reset_date
                if datetime.today() == password_reset_date:
                     password_reset_status = 'yes'  
                else: 
                     password_reset_status = 'no'   

                    
                # Add the log_id to the data dictionary
                data = {
                    # 'user_id'               : user.employee_id,
                    'user_id'               : user.id,
                    'role_id'               : role_ids,
                    'log_id'                : log_id,
                    'mobile_otp_id'         :mobile_otp_id,
                    'is_password_reset'     : password_reset_status, 
                    'financial_year_id'     : 1,
                    'mother_customer_id'    :  mother_customer_id ,
                    'branch_id'             : 1
                    
                }

                print('data', data)
                access_token = oauth2.create_access_token(data=data)               
            

                # Return a JSON response with the access token and additional information
                return {
                    'access_token': access_token,
                    'token_type': 'bearer'
                }
            except Exception as e:
                # Rollback the transaction
                db.rollback()
                # Raise a more specific HTTPException
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to log in: " + str(e))

                  

def authenticate_user(token: str) -> Dict[str, Union[int, None]]:
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role_id = payload.get("role_id")
        log_id = payload.get("log_id")
        employee_id = payload.get("employee_id")
        financial_year_id = payload.get("financial_year_id")
        mother_customer_id = payload.get('mother_customer_id')
       
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "role_id": role_id ,"log_id": log_id ,"employee_id": employee_id, 
                'financial_year_id':financial_year_id, 'mother_customer_id': mother_customer_id}
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    

@router.post('/admin-logout')
def logout_admin(request: Request, db: Session = Depends(get_db),
                 token: str = Depends(oauth2.oauth2_scheme)):

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token) 
    log_id = auth_info["log_id"]

    # Update logged_out_on field
    db.execute(
        update(models.AdminLog).
        where(models.AdminLog.id == log_id).
        values(logged_out_on=datetime.utcnow())
    )



    # Commit the transaction
    db.commit()

    # Return a response indicating successful logout
    return {'message': 'Logged out successfully'}



