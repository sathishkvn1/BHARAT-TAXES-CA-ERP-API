from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from caerp_db.common.models import OtpGeneration
from datetime import datetime,timedelta

def get_otp_by_id(db: Session,otp_id:str):
    return db.query(OtpGeneration).filter(OtpGeneration.id == otp_id).first()


def create_otp(db: Session, otp_value: str, user_id: int):
    current_time = datetime.utcnow()

    # Calculate OTP expiry time (30 minutes from current time)
    expiry_time = current_time + timedelta(minutes=30)

    # Create a new instance of OtpGeneration
    new_otp = OtpGeneration(
        otp=otp_value,
        created_on=current_time,
        created_by=user_id,
        otp_expire_on=expiry_time,
    )
    print("new otp", new_otp)
    # Add the new OTP to the database session
    db.add(new_otp)
    # Commit the changes to the database
    db.commit()
    # Refresh the new OTP object to reflect any changes made during the commit
    db.refresh(new_otp)

    # Return the newly created OTP object
    return new_otp




def query_mobile_otp_verification(otp,mobile_otp_id, db):

    mobile_otp = get_otp_by_id(db, mobile_otp_id)
    
    if mobile_otp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP record not found")
    
    if mobile_otp.otp == otp:
        
        return {"message": "OTP verified successfully.", "is_verified": True}
    else :
        return { "message": "Invalid  OTP.", "is_verified": False}