from fastapi import APIRouter,HTTPException,status
from caerp_auth import oauth2
from caerp_auth.oauth2 import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from fastapi.param_functions import Depends
from caerp_db.database import get_db
from sqlalchemy.orm import Session
from caerp_db.common import db_otp,db_user
import random
from caerp_functions import send_message

router = APIRouter(
    prefix ='/otp',
    tags=['OTP']
)


@router.post("/mobile_otp_verification/{otp}")
def mobile_otp_verification(
    otp: str,
    db:Session = Depends(get_db),
    token :  str = Depends(oauth2.oauth2_scheme)):

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  
    mobile_otp_id = payload.get("mobile_otp_id")
    print("mobile OTP ID : ",mobile_otp_id)
    mobile_otp = db_otp.get_otp_by_id(db, mobile_otp_id)
    
    if mobile_otp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP record not found")
    
    if mobile_otp.otp == otp:
        # update_query = db.query(CustomerRegister).filter(CustomerRegister.id == mobile_otp.created_by).update({CustomerRegister.is_mobile_number_verified: 'yes'})

        # Execute the update query
        # db.commit()
        return {"message": "OTP verified successfully.", "is_verified": True}
    else :
        return { "message": "Invalid  OTP.", "is_verified": False}
 
@router.post("/mobile_resend_otp")
def mobile_resend_otp(   
    db:Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
    ):

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   
    user_id = payload.get("user_id")
    
    user_data = db_user.get_employee_by_id(db, user_id)
    
    mobile_number= user_data.mobile_phone
    mobile_otp_value = random.randint(pow(10,5), pow(10,5+1)-1)  
    new_otp = db_otp.create_otp(db, mobile_otp_value,user_data.employee_id)
    mobile_otp_id = new_otp.id    
    message= f"{mobile_otp_value}is your SECRET One Time Password (OTP) for your mobile registration. Please use this password to complete your transaction. From:BRQ GLOB TECH"
    temp_id= 1607100000000128308
    
    
    try:
        send_message.send_sms_otp(mobile_number,message,temp_id,db)
        data={
                    "mobile_otp_id": mobile_otp_id,                    
                    'user_id'     : user_data.employee_id
                }
        access_token = oauth2.create_access_token(data=data)
        return {'message' : 'Success',
                'access_token': access_token
            }
    #  db_send_sms.send_sms(new_customer.mobile_number,message,temp_id)
    except Exception as e:
        # Handle sms sending failure
        print(f"Failed to send message: {str(e)}")
   
     

   


