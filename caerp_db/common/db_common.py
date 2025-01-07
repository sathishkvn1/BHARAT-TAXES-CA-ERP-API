


from datetime import date, datetime
import json
import random
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError

import requests
from sqlalchemy import desc, or_
from caerp_constants.caerp_constants import ActionType
from caerp_db.common import db_otp, db_user
from caerp_db.common.models import  AppViewVillages, CityDB, ConstitutionTypes, CountryDB, CurrencyDB, DistrictDB, EmployeeContactDetails, EmployeeMaster, Gender, MenuStructure, NationalityDB, Notification, PanCard, PostOfficeTypeDB, PostOfficeView, PostalCircleDB, PostalDeliveryStatusDB, PostalDivisionDB, PostalRegionDB, Profession, QueryManagerQuery, QueryView, RoleMenuMapping,  StateDB, TalukDB, UserBase
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException ,status

from caerp_db.database import get_db
from caerp_functions import send_message
from caerp_router.common.common_functions import token_generate
from caerp_schema.common.common_schema import ConstitutionTypeForUpdate, EducationSchema, MenuStructureSchema, NotificationSchema, ProfessionSchemaForUpdate, QueryManagerQuerySchema, QueryManagerViewSchema, RoleMenuMappingSchema, Village, VillageResponse     

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
        official_mobile_no = db.query(EmployeeContactDetails.personal_mobile_number).filter(EmployeeContactDetails.employee_id==user.employee_id).scalar()
        # official_mobile_no = official_mobile_no[0]
    if mobile_no:
        official_mobile_no = mobile_no 
        employee_id = db.query(EmployeeContactDetails.employee_id).filter(EmployeeContactDetails.personal_mobile_number == mobile_no).scalar()
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
    

#-----------------------------------------------------------------------------------------------

def get_query_details(db: Session, id: int):
    # Fetch the main query details
    query_details = db.query(QueryView).filter(QueryView.query_manager_id == id).first()
    
    if not query_details:
        return None

    # Fetch the employee details if resolved_by is present
    employee_details = None
    if query_details.queried_by:
        employee_details = db.query(EmployeeMaster).filter(EmployeeMaster.employee_id == query_details.queried_by).first()
    # Fetch the employee contact details if employee_id is present
    contact_details = None
    if employee_details:
        contact_details = db.query(EmployeeContactDetails).filter(EmployeeContactDetails.employee_id == employee_details.employee_id).first()

    # Fetch the user details if queried_by is present
    user_details = None
    if query_details.queried_by:
        user_details = db.query(UserBase).filter(UserBase.employee_id == query_details.queried_by).first()

    # Combine results
    return {
        "query_details": query_details,
        "employee_name": employee_details.first_name if employee_details else None,
        "employee_id": employee_details.employee_id if employee_details else None,
        "mobile_number": contact_details.personal_mobile_number if contact_details else None,
        "user_name": user_details.user_name if user_details else None,
        "user_id"  : user_details.employee_id if user_details else None
    }
#-------------------------------------------------------------------------------------------

def get_notifications(
        db : Session,
        notification_id : Optional[int] =None,
        display_location : Optional[str] = None
) : 
    query = db.query(Notification).filter(Notification.is_deleted == "no")
    if notification_id :
        query = query.filter(Notification.id == notification_id)
    if display_location:
        query = query.filter(Notification.display_location == display_location)

    # notifications = query.all()
    notifications = query.order_by(desc(Notification.notification_date)).all()
    return notifications


#-------------------------------------------------------------------------------------------

def add_notification(
    notification: NotificationSchema, 
    db: Session = Depends(get_db) ,
    notification_id: Optional[int] = None
    # display_location: Optional[int] = None,
):

    notification_obj = None
    if notification_id :
            notification_obj = db.query(Notification).filter(Notification.id == notification_id, 
                                                          Notification.is_deleted == "no").first()
            if not notification_obj:
                raise HTTPException(status_code=404, detail="Notification not found.")
            # for key, value in notification.dict(exclude_unset=True).items():
            #   setattr(notifications, key, value)
            # notifications.modified_on = datetime.utcnow()

    # elif display_location :
    #         notification_obj = db.query(Notification).filter(Notification.display_location == display_location, 
    #                                                       Notification.is_deleted == "no").first()
    #         if not notification_obj:
    #             raise HTTPException(status_code=404, detail="Notification not found.")
    if notification_obj : 
        for key, value in notification.dict(exclude_unset=True).items():
            setattr(notification_obj, key, value)
        notification_obj.modified_on = datetime.utcnow()
        db.commit()
        db.refresh(notification_obj)
        return  {'success' : True,
                'notificationnid ': notification_obj.id
        } 

    else : 
#     db.commit()
#     db.refresh(db_notification)
#     
        new_notification = Notification(**notification.dict(exclude_unset=True))
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        return {'success' : True,
                'new notificationnid ': new_notification.id
        }





def get_queries_by_id(
        db: Session,         
        id: Optional[int]= None, 
        is_resolved : Optional[str] = 'ALL',
        search_value: Optional[str] = "ALL",
        from_date : Optional[date]= None,
        to_date : Optional[date] = None) -> List[QueryManagerViewSchema]:
    today = date.today()
    from_date = from_date or today
    to_date = to_date or today

    query = db.query(QueryView)
    query = query.filter(
        QueryView.query_on >= datetime.combine(from_date, datetime.min.time()),
        QueryView.query_on <= datetime.combine(to_date, datetime.max.time())
    )
    if id :
        query = query.filter(QueryView.query_manager_id == id)
    if is_resolved != 'ALL':
        query = query.filter(QueryView.is_resolved == is_resolved)
   
    if search_value and search_value != "ALL":
        query = query.filter(
            or_(
                QueryView.query.like(f"%{search_value}%"),
                QueryView.query_on.like(f"%{search_value}%")
            )
        )
    results = query.all()
    return [QueryManagerViewSchema.from_orm(result) for result in results]
    


def send_query_resolved_notification(phone, template_name: str, placeholders: list)->dict:
    token = token_generate()
    url = "https://apis.rmlconnect.net/wba/v1/messages"
    payload = {
            "phone": phone,
            "media": {
                "type": "media_template",
                "template_name": template_name,
                "lang_code": "en",
                "body": [{"text": value} for value in placeholders]
            }
        }
    headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"{token}"  # Ensure token is prefixed with Bearer
        }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # print("Request Headers:", headers)
        # print("Request Payload:", json.dumps(payload, indent=4))
        # print('/response ..............',response)
        # response.raise_for_status()  # Raise HTTPError for bad responses
        return {"success": True, "response": response.json()}
    except requests.exceptions.RequestException as e:        
        return {"success": False, "error": str(e), "response": response.text}


#----------------------------------------------------------------------------------------------------------
def create_menu(menus: List[MenuStructureSchema], user_id: int, db: Session = Depends(get_db)):
    processed_menus = []

    for menu in menus:
        # Check if the menu already exists
        existing_menu = db.query(MenuStructure).filter(MenuStructure.id == menu.id).first()

        if existing_menu:
            # Update existing menu
            menu_data = menu.model_dump()  # Convert Pydantic object to dictionary
            menu_data['modified_by'] = user_id
            menu_data['modified_on'] = datetime.now()

            for key, value in menu_data.items():
                if hasattr(existing_menu, key):  # Update only fields that exist in the model
                    setattr(existing_menu, key, value)

            db.commit()
            db.refresh(existing_menu)
            processed_menus.append(existing_menu)  # Add updated menu to the list
        else:
            # Create new menu
            new_menu = MenuStructure(
                **menu.model_dump(),
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_menu)
            db.commit()
            db.refresh(new_menu)
            processed_menus.append(new_menu)  # Add newly created menu to the list

    # Serialize using MenuStructureSchema
    response_menus = [MenuStructureSchema.from_orm(menu) for menu in processed_menus]

    return {"success": True, "menus": response_menus}

#----------------------------------------------------------------------------------------------------------

def build_menu_tree(menu_items, role_menu_mapping, parent_id=0):
    """
    Recursively builds a tree structure for menus.

    Args:
        menu_items: List of all menu items.
        role_menu_mapping: Dictionary with role-specific menu mappings.
        parent_id: Parent menu ID for recursion.

    Returns:
        A list representing the menu tree.
    """
    menu_tree = []
    for item in menu_items:
        if item.parent_id == parent_id:
            # Check if the menu is assigned to the role
            mapping = role_menu_mapping.get(item.id)
            # Build the menu entry
            menu_entry = {
                "id": item.id,
                "menu_name": item.menu_name,
                "parent_id": item.parent_id,
                "has_sub_menu": item.has_sub_menu,
                "display_order": item.display_order,
                "link" : item.link,
                "display_location_id" : item.display_location_id,
                "is_assigned": "yes" if mapping else "no",
                "has_view": item.has_view if hasattr(item, "has_view") else "no",
                "has_edit": item.has_edit if hasattr(item, "has_edit") else "no",
                "has_delete": item.has_delete if hasattr(item, "has_delete") else "no",
                "can_view": mapping.can_view if mapping else "no",
                "can_edit": mapping.can_edit if mapping else "no",
                "can_delete": mapping.can_delete if mapping else "no",
            }
            # Add sub_menus as the last key
            menu_entry["sub_menus"] = build_menu_tree(menu_items, role_menu_mapping, item.id)
            menu_tree.append(menu_entry)
    return menu_tree


#----------------------------------------------------------------------------------------------------------

def get_menu_structure(role_id : int,
                      db: Session):
    menus = db.query(MenuStructure).filter(MenuStructure.is_deleted == "no").order_by(MenuStructure.display_order).all()
    # Fetch role menu mappings if role_id is provided
    role_menu_mapping = {}
    if role_id:
        mappings = db.query(RoleMenuMapping).filter(RoleMenuMapping.role_id == role_id).all()
        role_menu_mapping = {mapping.menu_id: mapping for mapping in mappings}
    # Build the menu tree
    menu_tree = build_menu_tree(menus, role_menu_mapping)

    return {"menuData": menu_tree}

#----------------------------------------------------------------------------------------------------------



def save_role_menu_permission(
        db: Session,
        role_id : int,
        datas: List[RoleMenuMappingSchema],
        user_id: int
):
    processed_data = []  # Initialize as a list

    try:
        for data in datas:
            # Check if the record exists for the role and menu
            existing_data = db.query(RoleMenuMapping).filter(
                RoleMenuMapping.role_id == role_id,
                RoleMenuMapping.menu_id == data.menu_id,
                RoleMenuMapping.is_deleted == 'no'
            ).first()

            if existing_data:
                # Update existing record
                updating_data = data.model_dump()  # Convert Pydantic object to dictionary
                updating_data['modified_by'] = user_id
                updating_data['modified_on'] = datetime.now()

                for key, value in updating_data.items():
                    if hasattr(existing_data, key):  # Update only fields that exist in the model
                        setattr(existing_data, key, value)

                db.commit()
                db.refresh(existing_data)
                processed_data.append({
                    "id": existing_data.id,
                    "message": "Updated successfully"
                })  # Add updated record ID and message to the list
            else:
                # Create a new record
                new_mapping = RoleMenuMapping(
                    **data.model_dump(),
                    role_id = role_id,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                db.add(new_mapping)
                db.commit()
                db.refresh(new_mapping)
                processed_data.append({
                    "id": new_mapping.id,
                    "message": "Created successfully"
                })  # Add newly created record ID and message to the list

        return {"success": True, "data": processed_data}

    except SQLAlchemyError as e:
        # Rollback any uncommitted changes
        db.rollback()
        # Log the error if needed and return failure response
        return {
            "success": False,
            "error": f"Database error occurred: {str(e)}"
        }

    except Exception as e:
        # Handle any other unexpected exceptions
        db.rollback()
        return {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }

#-----------------------------------------------------------------------------------------------


def delete_menu_recursively(db: Session, menu_id: int, user_id: int):
    try:
        # Fetch the menu by ID
        menu = db.query(MenuStructure).filter(MenuStructure.id == menu_id, MenuStructure.is_deleted == 'no').first()

        if not menu:
            return {"success": False, "message": "Menu not found or already deleted"}

        # Find all submenus (child menus)
        submenus = db.query(MenuStructure).filter(MenuStructure.parent_id == menu_id, MenuStructure.is_deleted == 'no').all()

        # Recursively delete all submenus
        for submenu in submenus:
            delete_menu_recursively(db, submenu.id, user_id)

        # After all submenus are deleted, delete the menu itself
        menu.is_deleted = 'yes'
        menu.deleted_by = user_id
        menu.deleted_on = datetime.now()

        db.commit()

        return {"success": True, "message": f"Menu with ID {menu_id} and all its submenus deleted successfully"}

    except SQLAlchemyError as e:
        # Rollback if there is a database error
        db.rollback()
        return {"success": False, "message": f"Database error occurred: {str(e)}"}

    except Exception as e:
        # Handle any other unexpected errors
        db.rollback()
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}
  


























