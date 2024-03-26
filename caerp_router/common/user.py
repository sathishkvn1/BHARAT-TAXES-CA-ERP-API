from fastapi import APIRouter,Depends,HTTPException,status
from caerp_db.common.models import UserBase
from caerp_schema.common.common_schema import UserCreateSchema
from caerp_db.database import get_db
from sqlalchemy.orm import Session
from caerp_db.common import db_user
from caerp_constants.caerp_constants import ActiveStatus
from caerp_auth import oauth2
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