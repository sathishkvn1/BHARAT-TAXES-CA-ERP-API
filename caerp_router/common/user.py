from fastapi import APIRouter,Depends,HTTPException,status
from caerp_schema.common.common_schema import UserCreateSchema
from caerp_db.database import get_db
from sqlalchemy.orm import Session
from caerp_db.common import db_user
from caerp_constants.caerp_constants import ActiveStatus
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
    


@router.post('/update_user_active_status')
def update_active_status(
    user_name: str,
    active_status: ActiveStatus = ActiveStatus.ACTIVE,
    db: Session = Depends(get_db)
):

    return db_user.update_user_active_status(db,active_status,user_name)