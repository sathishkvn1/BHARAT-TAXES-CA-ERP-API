from fastapi import APIRouter, Depends,HTTPException,status,Query
from sqlalchemy.orm import Session
from caerp_db.database import get_db
from caerp_db.accounts import db_quotation
# from caerp_constants.caerp_constants import EntryPoint
from caerp_schema.accounts.quotation_schema import AccQuotationSchema
from typing import Optional
from datetime import date
from caerp_auth import oauth2
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import EntryPoint

router  = APIRouter(
    tags=['Quotation']
)



@router.get('/generate_quotation_service_details')
def generate_quotation_service_details(
    work_order_master_id: int,
    # work_order_details_id: int,
    # service_goods_master_id : int,
    # constitution_id :int,
    db: Session = Depends(get_db)
):

  result   = db_quotation.generate_quotation_service_details(db,work_order_master_id)
  return result

@router.post('/save_quotation_data')
def save_quotation_data(
        request : AccQuotationSchema,
        quotation_id : Optional[int],
        db : Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    result = db_quotation.save_quotation_data(request,user_id,db,quotation_id)
    return result

@router.post('/update_quotation_status')
def update_quotation_status(
        quotation_id : int,
        quotation_status : str,
        # quotation_version: int,
        db:Session = Depends(get_db)
):
   result = db_quotation.update_quotation_status(quotation_id,quotation_status,db)
   return result

@router.post('/send_proposal')
def send_proposal(
    quotation_id :int,
    work_order_master_id : int,
    db: Session = Depends(get_db)
):
    result = db_quotation.send_proposal(quotation_id,work_order_master_id,db)
    return result

@router.get('/get_quotation_list')
def get_quotqtion_list(
    status: Optional[str]='ALL',
    work_order_master_id : Optional[int] = None,
    quotation_id : Optional[int] = None,
    from_date : Optional[date] = Query(date.today()),
    to_date : Optional[date] =None,
    db: Session = Depends(get_db)
): 
   result = db_quotation.get_quotation_data(db,status,work_order_master_id,quotation_id,from_date,to_date)
   return result