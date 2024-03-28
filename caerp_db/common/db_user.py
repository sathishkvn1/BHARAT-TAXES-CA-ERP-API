

from caerp_schema.common.common_schema import UserCreateSchema
from caerp_db.common.models import UserBase,Employee
from fastapi import HTTPException , status     
from caerp_db.hash import Hash
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from caerp_constants.caerp_constants import ActiveStatus

def save_user(db: Session,  request: UserCreateSchema, user_id: int):

    if user_id == 0:
        # Add operation
        user_data_dict = request.dict()
        user_data_dict["password"] = Hash.bcrypt(user_data_dict["password"])
        # try:
        new_user = UserBase(**user_data_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
        # except Exception as e:
        #     error_detail = [{
        #         "loc": ["server"],
        #         "msg": "Internal server error",
        #         "type": "internal_server_error"
        #     }]
        #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)
    
    else:
        # Update operation
        user_data = db.query(UserBase).filter(UserBase .id == user_id).first()
        if user_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Category not found")
        user_data_dict = request.dict(exclude_unset=True)
        for key, value in user_data_dict.items():
            setattr(user_data, key, value)
        user_data.modified_by = user_id
        user_data.modified_on = datetime.utcnow()
        
        db.commit()
        db.refresh(user_data)
        return user_data



def get_user_by_mobile(db: Session, mobile: str):
    return db.query(Employee).filter(Employee.mobile_phone == mobile).first()

def get_user_by_id(db: Session, id: int):
    return db.query(UserBase).filter(UserBase.employee_id == id).first()
def get_employee_by_id(db: Session, id: int):
    return db.query(Employee).filter(Employee.employee_id == id).first()
def get_user_by_user_name(db: Session,username: str):    
    return  db.query(UserBase).filter(UserBase.user_name == username).first()
    


def update_user_locked_time(db: Session, username: str):
    
    existing_user = db.query(UserBase).filter(UserBase.user_name == username).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User is not found")

    existing_user.locked_upto = datetime.utcnow()+ timedelta(minutes=15)
   
    try:
        db.commit()  # Commit changes to the database
    except Exception as e:
        db.rollback()  # Rollback changes if an error occurs
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


    return {
        "message": "Update Active Status successfully",

    }





def update_user_active_status(db: Session, active_status: ActiveStatus, username: str):
    existing_user = db.query(UserBase).filter(UserBase.user_name == username).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User is not found")
    if active_status == ActiveStatus.ACTIVE:
        existing_user.is_active = 'yes'
    elif active_status == ActiveStatus.NOT_ACTIVE:
        existing_user.is_active = 'no'    
    
    else:
        raise ValueError("Invalid active_status")
    try:
        db.commit()  # Commit changes to the database
    except Exception as e:
        db.rollback()  # Rollback changes if an error occurs
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


    return {
        "message": "Update Active Status successfully",

    }


# def get_active_user(db: Session, active_status: ActiveStatus):
#     if active_status == ActiveStatus.ACTIVE:
#         return db.query(UserBase).filter(UserBase.is_active == 'yes').all()
#     elif active_status == ActiveStatus.NOT_ACTIVE:
#         return db.query(UserBase).filter(UserBase.is_active == 'no').all()
#     elif active_status == ActiveStatus.ALL:
#         return db.query(UserBase).all()
#     else:
#         raise ValueError("Invalid active_status")
