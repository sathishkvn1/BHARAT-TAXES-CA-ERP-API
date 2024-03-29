from fastapi import APIRouter,Depends,HTTPException,status
from caerp_db.common.models import UserBase
from caerp_schema.common.common_schema import UserCreateSchema
from caerp_db.database import get_db
from sqlalchemy.orm import Session
from caerp_db.common import db_user,db_otp
from caerp_db.hr_and_payroll import db_employee_master
from caerp_constants.caerp_constants import ActiveStatus

from caerp_auth import oauth2

from caerp_functions import send_message
from caerp_auth import oauth2
from jose import JWTError, jwt
from caerp_auth.oauth2 import create_access_token,SECRET_KEY, ALGORITHM
import random
from caerp_db.hash import Hash

router = APIRouter(
    prefix ='/user',
    tags = ['USER']
)



@router.post('/add/users', response_model=UserCreateSchema)
def create_user(
    user_data: UserCreateSchema=Depends(),
    user_id :  int =0,
    db: Session = Depends(get_db),
    
):
    
        new_user = db_user.save_user(db, user_data, user_id)
        
        return new_user
    



@router.get('/check_username/{username}', response_model=str)
def check_username_availability(
    username: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    # Check authorization
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    user = db.query(UserBase).filter(UserBase.user_name == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists. Please try another name.")
    else:
        return "Username available."



@router.post('/update_user_active_status')
def update_active_status(
    user_name: str,
    active_status: ActiveStatus = ActiveStatus.ACTIVE,
    db: Session = Depends(get_db)
):

    return db_user.update_user_active_status(db,active_status,user_name)



@router.post('/forgot_password')
def forgot_password(
    user_name: str,
    db:Session = Depends(get_db)
):
    try:
        user = db_user.get_user_by_user_name(db,user_name) 
        
    except Exception as e:
                # Handle sms sending failure
                print(f"Failed to send message: {str(e)}")

    # user = db.user.get_user_by_id(db,user_id) 
    if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" Please Check your user name")
    else:
        if user.role_id == 1:
            employee_data = db_employee_master.get_employee_master_by_id(db, user.employee_id)
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
                send_message.send_sms_otp(employee_data.mobile_phone,template_message,temp_id,db)
                data = {
                    'user_id': user.employee_id,
                    'role_id': user.role_id,
                    'mobile_otp_id':mobile_otp_id
                    
                }
                
                access_token = oauth2.create_access_token(data=data)

                # Return a JSON response with the access token and additional information
                return {
                    'access_token': access_token,
                    'token_type': 'bearer'
                }


        # #  db_send_sms.send_sms(new_customer.mobile_number,message,temp_id)
            except Exception as e:
                # Handle sms sending failure
                print(f"Failed to send message: {str(e)}")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" Only an ADMIN or Super Admin can change their password.")
 
 
@router.get("/password_reset")
def password_reset(
                     password: str,

                     db: Session = Depends(get_db),
                    token: str = Depends(oauth2.oauth2_scheme)
                    ):
    
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   
    user_id = payload.get("user_id")
   
    return db_user.user_password_reset(db, user_id, password)       
           




