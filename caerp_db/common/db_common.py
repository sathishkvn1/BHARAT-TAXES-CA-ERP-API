


import random
from typing import Optional
from caerp_constants.caerp_constants import ActionType
from caerp_db.common import db_otp, db_user
from caerp_db.common.models import  AppViewVillages, CityDB, ConstitutionTypes, CountryDB, CurrencyDB, DistrictDB, EmployeeContactDetails, Gender, NationalityDB, PanCard, PostOfficeTypeDB, PostOfficeView, PostalCircleDB, PostalDeliveryStatusDB, PostalDivisionDB, PostalRegionDB, Profession, QueryManagerQuery,  StateDB, TalukDB, UserBase
from sqlalchemy.orm import Session
from fastapi import HTTPException ,status

from caerp_functions import send_message
from caerp_schema.common.common_schema import ConstitutionTypeForUpdate, EducationSchema, ProfessionSchemaForUpdate, QueryManagerQuerySchema, Village, VillageResponse     

from caerp_db.common.models import PaymentsMode,PaymentStatus,RefundStatus,RefundReason
from caerp_schema.common.common_schema import PaymentModeSchema,PaymentStatusSchema,RefundStatusSchema,RefundReasonSchema

def get_countries(db: Session):
    return db.query(CountryDB).all()


# def get_states(db: Session):
#     return db.query(StateTestDB).all()



def get_country_by_id(db: Session, country_id: int):
    
    return db.query(CountryDB).filter(CountryDB.id == country_id).first()


def get_states_by_country(db: Session, country_id: int):
    return db.query(StateDB).filter(StateDB.country_id == country_id).all()


def get_state_by_id(db: Session, state_id: int):
    return db.query(StateDB).filter(StateDB.id == state_id).first()

def get_districts_by_state(db: Session, state_id: int):
    return db.query(DistrictDB).filter(DistrictDB.state_id == state_id).all()

def get_district_by_id(db: Session, district_id: int):
    return db.query(DistrictDB).filter(DistrictDB.id == district_id).first()


def get_cities_by_country_and_state(db: Session, country_id: int, state_id: int):
    return db.query(CityDB).filter(
        CityDB.country_id == country_id,
        CityDB.state_id == state_id
    ).all()
    
    

def get_city_by_id(db: Session, city_id: int):
    return db.query(CityDB).filter(CityDB.id == city_id).first()

def get_taluks_by_state(db: Session, state_id: int):
    return db.query(TalukDB).filter(TalukDB.state_id == state_id).all()

def get_taluks_by_district(db: Session, district_id: int):
    return db.query(TalukDB).filter(TalukDB.district_id == district_id).all()

def get_taluk_by_id(db: Session, taluk_id: int):
    return db.query(TalukDB).filter(TalukDB.id == taluk_id).first()

def get_all_currencies(db: Session):
    return db.query(CurrencyDB).all()

def get_currency_by_id(db: Session, currency_id: int):
    return db.query(CurrencyDB).filter(CurrencyDB.id == currency_id).first()


def get_all_nationality(db: Session):
    return db.query(NationalityDB).all()

def get_nationality_by_id(db: Session, nationality_id: int):
    return db.query(NationalityDB).filter(NationalityDB.id == nationality_id).first()

def get_all_post_office_types(db: Session):
    return db.query(PostOfficeTypeDB).all()

def get_post_office_type_by_id(db: Session, id: int):
    return db.query(PostOfficeTypeDB).filter(PostOfficeTypeDB.id == id).first()

def get_all_postal_delivery_statuses(db: Session):
    return db.query(PostalDeliveryStatusDB).all()

def get_postal_delivery_status_by_id(db: Session, id: int):
    return db.query(PostalDeliveryStatusDB).filter(PostalDeliveryStatusDB.id == id).first()

def get_all_postal_circles(db: Session):
    return db.query(PostalCircleDB).all()


def get_postal_circle_by_id(db: Session, id: int):
    return db.query(PostalCircleDB).filter(PostalCircleDB.id == id).first()

def get_all_postal_regions(db: Session):
    return db.query(PostalRegionDB).all()

def get_postal_regions_by_circle_id(db: Session, circle_id: int):
    return db.query(PostalRegionDB).filter(PostalRegionDB.circle_id == circle_id).all()

def get_postal_region_by_id(db: Session, region_id: int):
    return db.query(PostalRegionDB).filter(PostalRegionDB.id == region_id).first()

def get_all_postal_divisions(db: Session):
    return db.query(PostalDivisionDB).all()

def get_postal_divisions_by_circle_id(db: Session, circle_id: int):
    divisions = db.query(PostalDivisionDB).filter(PostalDivisionDB.circle_id == circle_id).all()
    return divisions


def get_postal_divisions_by_region_id(db: Session, region_id: int):
    return db.query(PostalDivisionDB).filter_by(region_id=region_id).all()

def get_postal_division_by_id(db: Session, division_id: int):
    return db.query(PostalDivisionDB).filter_by(id=division_id).first()


def get_post_offices_by_pincode(db: Session, pincode: str):
    return db.query(PostOfficeView).filter(PostOfficeView.pin_code == pincode).all()

def get_all_gender(db: Session):
    return db.query(Gender).all()

def get_gender_by_id(db: Session, gender_id: int):
    return db.query(Gender).filter(Gender.id == gender_id).first()


def get_all_pan_cards(db: Session):
    return db.query(PanCard).all()

def get_pan_card_by_id(db: Session, pancard_id: int):
    return db.query(PanCard).filter(PanCard.id == pancard_id).first()

def get_pan_card_by_code_type(db: Session, code_type: str):
    return db.query(PanCard).filter(PanCard.pan_card_type_code == code_type).first()








def get_all_constitution(db: Session):
    return db.query(ConstitutionTypes).all()


def update_constitution(db: Session, request: ConstitutionTypeForUpdate, id: int):
    constitution = db.query(ConstitutionTypes).filter(ConstitutionTypes.id == id).first()
    if constitution is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="constitution not found")
    constitution_data_dict = request.dict()
    for key, value in constitution_data_dict.items():
            setattr(constitution, key, value)

    db.commit()
    db.refresh(constitution)
    return constitution


def get_all_profession(db: Session):
    return db.query(Profession).all()

def update_profession(db: Session, request: ProfessionSchemaForUpdate, id: int):
    profession = db.query(Profession).filter(Profession.id == id).first()
    if profession is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profession not found")
    profession_data_dict = request.dict()
    for key, value in profession_data_dict.items():
            setattr(profession, key, value)
    
    db.commit()
    db.refresh(profession)
    return profession



def save_query_manager_queries(db: Session, id: int, data: QueryManagerQuerySchema):
    if id == 0:
        # Add operation
        new_query = QueryManagerQuery(**data.dict())
        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        return {"message": "Query inserted successfully"}
    else:
        # Update operation
        existing_query = db.query(QueryManagerQuery).filter(QueryManagerQuery.id == id).first()
        if existing_query is None:
            raise HTTPException(status_code=404, detail="Query not found")
        
        # Update the existing query with new data
        db.query(QueryManagerQuery).filter(QueryManagerQuery.id == id).update(data.dict())
        db.commit()
        db.refresh(existing_query)
        return {"message": "Query updated successfully"}
    
    
def delete_query_manager_queries(db: Session, id: int):
    result = db.query(QueryManagerQuery).filter(QueryManagerQuery.id == id).first()

    if result is None:
        raise HTTPException(status_code=404, detail="Not found")

    result.is_deleted = 'yes'


    db.commit()

    return {
        "message": "Deleted successfully",
    }


def get_query_manager_query_by_id(db: Session, id: int):
    return db.query(QueryManagerQuery).filter(QueryManagerQuery.id == id).first()


# def get_queries_by_id(db: Session, id: int):
#     return db.query(QueryView).filter(QueryView.id == id).first()

#-----------------------------------------------------------







def save_payments_mode(db: Session,
                   payments_mode_data: PaymentModeSchema, 
                   id: int = 0):
    # Check if a PaymentsMode with the same name already exists and is not deleted
    existing_payments_mode = db.query(PaymentsMode).filter(
        PaymentsMode.payment_mode == payments_mode_data.payment_mode,
        PaymentsMode.is_deleted == "no"
    ).first()

    # If a Payments Mode with the same name already exists
    if existing_payments_mode:
        # If updating and the existing PaymentsMode's ID is different from the ID being updated, or if adding a new Payments Mode
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A Payments Mode with the same name already exists.")

    # If creating a new PaymentsMode
    if id == 0:
        new_payment = PaymentsMode(**payments_mode_data.dict())
        db.add(new_payment)
    # If updating an existing Payments Mode
    else:
        payments_mode = db.query(PaymentsMode).filter(PaymentsMode.id == id).first()
        if not payments_mode:
            raise HTTPException(status_code=404, detail=f'Payments Mode with id {id} not found')

        # Update Payments Mode data
        for key, value in payments_mode_data.dict().items():
            setattr(payments_mode, key, value)

    db.commit()
    db.refresh(new_payment if id == 0 else payments_mode)
    return new_payment if id == 0 else payments_mode
#-----------by id-----------------------
def get_payment_mode(db: Session, 
                 id: int
                 ):
    Payments_Mode = db.query(PaymentsMode).filter(PaymentsMode.id == id).first()
    
    if not Payments_Mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payments Mode with id {id} not found"
        )

    return Payments_Mode

#-----------delete----------------
def delete_payments_mode(db: Session, 
                           id: int, 
                           action: ActionType):
    payments_mode = db.query(PaymentsMode).filter(PaymentsMode.id == id).first()
    if payments_mode is None:
        raise HTTPException(status_code=404, detail="Payments Mode not found")
    
    if action == ActionType.DELETE:
        if payments_mode.is_deleted == 'yes':
            raise HTTPException(status_code=400, detail="payments mode  already deleted")
        
        payments_mode.is_deleted = 'yes'
        
    elif action == ActionType.UNDELETE:
        if payments_mode.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="payments_mode not deleted")
        
        payments_mode.is_deleted = 'no'

    
    db.commit()
    return {"success": True, "message": f"Payments Mode {action.value.lower()} successfully"}


    

 
#------------ payment_status-----------------

def save_payment_status(db: Session,
                   payment_status_data: PaymentStatusSchema, 
                   id: int = 0):
    # Check if a payment_status with the same name already exists and is not deleted
    existing_payment_status = db.query(PaymentStatus).filter(
        PaymentStatus.payment_status == payment_status_data.payment_status,
        PaymentStatus.is_deleted == "no"
    ).first()

    # If a Payments Status with the same name already exists
    if existing_payment_status:
        # If updating and the existing Payments Status's ID is different from the ID being updated, or if adding a new Payments Status
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A Payments Status with the same name already exists.")

    # If creating a new Payments Status
    if id == 0:
        new_payment_status = PaymentStatus(**payment_status_data.dict())
        db.add(new_payment_status)
    # If updating an existing Payment Status
    else:
        payment_status = db.query(PaymentStatus).filter(PaymentStatus.id == id).first()
        if not payment_status:
            raise HTTPException(status_code=404, detail=f'Payments Status with id {id} not found')

        # Update Payment Status data
        for key, value in payment_status_data.dict().items():
            setattr(payment_status, key, value)

    db.commit()
    db.refresh(new_payment_status if id == 0 else payment_status)
    return new_payment_status if id == 0 else payment_status
#-----------by id-----------------------
def get_payment_status(db: Session, 
                 id: int
                 ):
    payment_status = db.query(PaymentStatus).filter(PaymentStatus.id == id).first()
    
    if not payment_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment Status with id {id} not found"
        )

    return payment_status
#-----------delete----------------
def delete_payment_status(db: Session, 
                           id: int, 
                           action: ActionType):
    payment_status = db.query(PaymentStatus).filter(PaymentStatus.id == id).first()
    if payment_status is None:
        raise HTTPException(status_code=404, detail="Payment Status not found")
    
    if action == ActionType.DELETE:
        if payment_status.is_deleted == 'yes':
            raise HTTPException(status_code=400, detail="Payment Status already deleted")
        
        payment_status.is_deleted = 'yes'
        
    elif action == ActionType.UNDELETE:
        if payment_status.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="Payment Status not deleted")
        
        payment_status.is_deleted = 'no'

    
    db.commit()
    return {"success": True, "message": f"Payment Status {action.value.lower()} successfully"}


    

#------------ refund_status-----------------

def save_refund_status(db: Session,
                   refund_status_data: RefundStatusSchema, 
                   id: int = 0):
    # Check if a refund_status with the same name already exists and is not deleted
    existing_refund_status = db.query(RefundStatus).filter(
        RefundStatus.refund_status == refund_status_data.refund_status,
        RefundStatus.is_deleted == "no"
    ).first()

    # If a Refund Status with the same name already exists
    if existing_refund_status:
        # If updating and the existing refund status's ID is different from the ID being updated, or if adding a new Refund Status
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A Refund Status with the same name already exists.")

    # If creating a new Refund Status
    if id == 0:
        new_refund_status = RefundStatus(**refund_status_data.dict())
        db.add(new_refund_status)
    # If updating an existing Refund Status 
    else:
        refund_status = db.query(RefundStatus).filter(RefundStatus.id == id).first()
        if not refund_status:
            raise HTTPException(status_code=404, detail=f'Refund Status with id {id} not found')

        # Update RefundStatus data
        for key, value in refund_status_data.dict().items():
            setattr(refund_status, key, value)

    db.commit()
    db.refresh(new_refund_status if id == 0 else refund_status)
    return new_refund_status if id == 0 else refund_status
#-----------by id-----------------------
def get_refund_status(db: Session, 
                 id: int
                 ):
    refund_status = db.query(RefundStatus).filter(RefundStatus.id == id).first()
    
    if not refund_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund Status with id {id} not found"
        )

    return refund_status
#-----------delete----------------
def delete_refund_status(db: Session, 
                           id: int, 
                           action: ActionType):
    refund_status = db.query(RefundStatus).filter(RefundStatus.id == id).first()
    if refund_status is None:
        raise HTTPException(status_code=404, detail="Refund Status not found")
    
    if action == ActionType.DELETE:
        if refund_status.is_deleted == 'yes':
            raise HTTPException(status_code=400, detail="Refund Status already deleted")
        
        refund_status.is_deleted = 'yes'
        
    elif action == ActionType.UNDELETE:
        if refund_status.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="Refund Status not deleted")
        
        refund_status.is_deleted = 'no'

    
    db.commit()
    return {"success": True, "message": f"Refund Status {action.value.lower()} successfully"}


#-----------refund_reason-----------------

def save_refund_reason(db: Session,
                   refund_reason_data: RefundReasonSchema, 
                   id: int = 0):
    # Check if a refund_status with the same name already exists and is not deleted
    existing_refund_reason = db.query(RefundStatus).filter(
        RefundReason.refund_reason == refund_reason_data.refund_reason,
        RefundReason.is_deleted == "no"
    ).first()

    # If a Refund Reason with the same name already exists
    if existing_refund_reason:
        # If updating and the existing refund Reason's ID is different from the ID being updated, or if adding a new Refund Reason
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A Refund Reason with the same name already exists.")

    # If creating a new Refund Reason
    if id == 0:
        new_refund_reason = RefundReason(**refund_reason_data.dict())
        db.add(new_refund_reason)
    # If updating an existing Refund Reason 
    else:
        refund_reason = db.query(RefundReason).filter(RefundReason.id == id).first()
        if not refund_reason:
            raise HTTPException(status_code=404, detail=f'Refund Reason with id {id} not found')

        # Update Refund Reason data
        for key, value in refund_reason_data.dict().items():
            setattr(refund_reason, key, value)

    db.commit()
    db.refresh(new_refund_reason if id == 0 else refund_reason)
    return new_refund_reason if id == 0 else refund_reason
#-----------by id-----------------------
def get_refund_reason(db: Session, 
                 id: int
                 ):
    refund_reason = db.query(RefundReason).filter(RefundReason.id == id).first()
    
    if not refund_reason:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund Reason with id {id} not found"
        )

    return refund_reason

#-----------delete----------------
def delete_refund_reason(db: Session, 
                           id: int, 
                           action: ActionType):
    refund_reason = db.query(RefundReason).filter(RefundReason.id == id).first()
    if refund_reason is None:
        raise HTTPException(status_code=404, detail="Refund Reason not found")
    
    if action == ActionType.DELETE:
        if refund_reason.is_deleted == 'yes':
            raise HTTPException(status_code=400, detail="Refund Reason already deleted")
        
        refund_reason.is_deleted = 'yes'
        
    elif action == ActionType.UNDELETE:
        if refund_reason.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="Refund Reason not deleted")
        
        refund_reason.is_deleted = 'no'

    
    db.commit()
    return {"success": True, "message": f"Refund Reason {action.value.lower()} successfully"}



def get_villages_data(db: Session, pincode: str) -> VillageResponse:
    result = db.query(AppViewVillages).filter(AppViewVillages.pincode == pincode).all()

    if not result:
        raise HTTPException(status_code=404, detail="No villages found for the given pincode")

    villages = []
    block = None
    taluk = None
  

    for row in result:
        try:
            village_name = str(row.village_name) if row.village_name is not None else ""
            villages.append(
                Village(
                    id=row.app_village_id,
                    village_name=village_name,
                    lsg_type=row.lsg_type,
                    lsg_type_id=row.lsg_type_id,
                    lsg_sub_type=row.lsg_sub_type,
                    lsg_sub_type_id=row.lsg_sub_type_id,
                    lsg_name=row.lsg_name,
                    lsg_id=row.lsg_id
                )
            )
            if block is None:
                block = {"name": row.block_name, "id": row.block_id}
            if taluk is None:
                taluk = {"name": row.taluk_name, "id": row.taluk_id}
            # if district is None:
            #     district = {"name": row.district_name, "id": row.district_id}

        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue

    return VillageResponse(
        villages=villages,
        block=block,
        taluk=taluk,
        district="",
        state="kerala",
        country="India"
    )


#-------------------------------------------------------------------------------------------------
def send_query_manager_otp(
        db : Session,
        mobile_no: Optional[str]=None,
        email_id : Optional[str]=None,
        user_name : Optional[str]=None,
        ):
# if email_id: 

    # else:
    if user_name :
        user = db.query(UserBase).filter(UserBase.user_name == user_name).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        employee_id = user.employee_id
        official_mobile_no = db.query(EmployeeContactDetails.official_mobile_number).filter(EmployeeContactDetails.employee_id==user.employee_id).scalar()
        # official_mobile_no = official_mobile_no[0]
    if mobile_no:
        official_mobile_no = mobile_no 
        employee_id = db.query(EmployeeContactDetails.employee_id).filter(EmployeeContactDetails.official_mobile_number == mobile_no).scalar()
        # employee_id = employee_id[0]
        if employee_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
     
    mobile_otp_value = random.randint(pow(10,5), pow(10,5+1)-1)  
    new_otp = db_otp.create_otp(db, mobile_otp_value,employee_id)
    mobile_otp_id = new_otp.id    
    
    sms_type= 'OTP'
    template_data = db_user.get_templates_by_type(db,sms_type)
    temp_id= template_data.template_id
    template_message = template_data.message_template
    replace_values = [ mobile_otp_value, 'mobile registration']
    placeholder = "{#var#}"
    for value in replace_values:
        template_message = template_message.replace(placeholder, str(value),1)
                    
    
    try:
       
        result = send_message.send_sms_otp(official_mobile_no,template_message,temp_id,db)
        return {
        "success" :True,
        'mobile_otp_id' : mobile_otp_id,
        'user_id' : employee_id
            }
    except Exception as e:
                # Handle sms sending failure
                print(f"Failed to send message: {str(e)}")
    





































