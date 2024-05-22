from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session
from caerp_constants.caerp_constants import AppointmentStatus, DeletedStatus, RecordActionType,SearchCriteria
from caerp_db.common.models import Employee
from caerp_db.hash import Hash
from typing import Dict, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm.session import Session
from caerp_db.office.models import OffAppointmentMaster, OffAppointmentVisitMaster,OffAppointmentVisitDetails,OffAppointmentVisitMasterView,OffAppointmentVisitDetailsView,OffAppointmentCancellationReason, OffServiceGoodsDetails, OffServiceGoodsMaster, OffServices, OffViewConsultantDetails, OffViewConsultantMaster, OffViewServiceGoodsMaster
from caerp_schema.office.office_schema import OffAppointmentDetails, OffAppointmentMasterViewSchema, OffAppointmentVisitDetailsViewSchema, OffAppointmentVisitMasterViewSchema, RescheduleOrCancelRequest, ResponseSchema,AppointmentVisitDetailsSchema, SaveServicesGoodsMasterRequest, Slot
from typing import Union,List
from sqlalchemy import and_,or_
# from caerp_constants.caerp_constants import SearchCriteria

from sqlalchemy.exc import IntegrityError


def save_appointment_visit_master(
    db: Session,
    appointment_master_id: int,
    appointment_data: OffAppointmentDetails,
    user_id: int,
    action_type: RecordActionType  # Default action is INSERT_ONLY
):
    # Validate action_type and appointment_master_id combination
    if action_type == RecordActionType.INSERT_ONLY and appointment_master_id != 0:
        raise HTTPException(status_code=400, detail="Invalid action: For INSERT_ONLY, appointment_master_id should be 0")
    elif action_type == RecordActionType.UPDATE_ONLY and appointment_master_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid action: For UPDATE_ONLY, appointment_master_id should be greater than 0")

    try:
        if action_type == RecordActionType.INSERT_ONLY:
            appointment_master = OffAppointmentMaster(
                created_by=user_id,
                created_on=datetime.utcnow(),
                **appointment_data.appointment_master.dict(exclude_unset=True)
            )
            db.add(appointment_master)
            db.flush()

            visit_master = OffAppointmentVisitMaster(
                appointment_master_id=appointment_master.id,
                created_by=user_id,
                created_on=datetime.utcnow(),
                **appointment_data.visit_master.dict(exclude_unset=True)
            )
            db.add(visit_master)
            db.flush()

        elif action_type == RecordActionType.UPDATE_ONLY:
            # Fetch existing appointment master record
            appointment_master = db.query(OffAppointmentMaster).filter(OffAppointmentMaster.id == appointment_master_id).first()
            if not appointment_master:
                raise HTTPException(status_code=404, detail="Appointment master not found")

            # Update appointment master fields
            for field, value in appointment_data.appointment_master.dict(exclude_unset=True).items():
                setattr(appointment_master, field, value)
            appointment_master.modified_by = user_id
            appointment_master.modified_on = datetime.utcnow()

            # Fetch existing visit master record
            visit_master = db.query(OffAppointmentVisitMaster).filter(OffAppointmentVisitMaster.appointment_master_id == appointment_master_id).first()
            if not visit_master:
                raise HTTPException(status_code=404, detail="Visit master not found")

            # Update visit master fields
            for field, value in appointment_data.visit_master.dict(exclude_unset=True).items():
                setattr(visit_master, field, value)
            visit_master.modified_by = user_id
            visit_master.modified_on = datetime.utcnow()

        # Update or insert visit details
        for detail_data in appointment_data.visit_details:
            if action_type == RecordActionType.UPDATE_ONLY:
                # Check if the visit detail already exists
                existing_visit_detail = db.query(OffAppointmentVisitDetails).filter(
                    OffAppointmentVisitDetails.visit_master_id == visit_master.id,
                    OffAppointmentVisitDetails.service_id == detail_data.service_id
                ).first()
                if existing_visit_detail:
                    # Update existing visit detail if service ID is different
                    if existing_visit_detail.service_id != detail_data.service_id:
                        existing_visit_detail.service_id = detail_data.service_id
                        existing_visit_detail.modified_by = user_id
                        existing_visit_detail.modified_on = datetime.utcnow()
                else:
                    # Insert new visit detail
                    visit_detail = OffAppointmentVisitDetails(
                        visit_master_id=visit_master.id,
                        consultant_id=visit_master.consultant_id,
                        created_by=user_id,
                        created_on=datetime.utcnow(),
                        **detail_data.dict(exclude_unset=True)
                    )
                    db.add(visit_detail)
            else:
                # Insert new visit detail
                visit_detail = OffAppointmentVisitDetails(
                    visit_master_id=visit_master.id,
                    consultant_id=visit_master.consultant_id,
                    created_by=user_id,
                    created_on=datetime.utcnow(),
                    **detail_data.dict(exclude_unset=True)
                )
                db.add(visit_detail)

        db.commit()

        return {
            "success": True,
            "message": "Saved successfully"
        }

    except IntegrityError as e:
        db.rollback()
        # Check if the error message indicates a duplicate entry violation
        if 'Duplicate entry' in str(e):
            # Return a custom error message indicating the duplicate entry
            raise HTTPException(status_code=400, detail="The selected slot is already booked. Please choose another slot.")
        else:
            # For other IntegrityError cases, raise the exception with the original message
            raise e
    except Exception as e:
        db.rollback()
        raise e


def reschedule_or_cancel_appointment(db: Session, request_data: RescheduleOrCancelRequest, action: AppointmentStatus, visit_master_id: int):
    if action == AppointmentStatus.RESCHEDULED:
        if not request_data.date or not request_data.time:
            raise HTTPException(status_code=400, detail="Date and time are required for rescheduling")
        # Update appointment status to RESCHEDULED (ID: 3) and update date and time
        appointment = db.query(OffAppointmentVisitMaster).filter(OffAppointmentVisitMaster.id == visit_master_id).first()
        if appointment:
            appointment.appointment_status_id = 3  # Assuming 3 is the appointment status ID for RESCHEDULED
            appointment.appointment_date = request_data.date
            appointment.appointment_time_from = request_data.time
            appointment.remarks = request_data.description
            db.commit()
            return {"success": True, "message": "Appointment rescheduled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Appointment not found")
    elif action == AppointmentStatus.CANCELED:
        # Update appointment status to CANCELED (ID: 2)
        appointment = db.query(OffAppointmentVisitMaster).filter(OffAppointmentVisitMaster.id == visit_master_id).first()
        if appointment:
            appointment.appointment_status_id = 2
            appointment.remarks = request_data.description  # Assuming 2 is the appointment status ID for CANCELED
            db.commit()
            return {"success": True, "message": "Appointment canceled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Appointment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
#-------------------------------get_appointment_info
def get_appointment_info(db: Session, type: str) -> List[dict]:
    if type == "cancellation_reasons":
        # Query the database to get unique cancellation reasons
        reasons = db.query(OffAppointmentCancellationReason.id, OffAppointmentCancellationReason.off_appointment_cancellation_reason).filter(
           
        ).distinct().all()
        # Format the reasons into a list of dictionaries
        return [{"id": reason[0], "reason": reason[1]} for reason in reasons]
    elif type == "status":
        # Query the database to get unique appointment statuses
        statuses = db.query(OffAppointmentVisitMasterView.appointment_master_id, OffAppointmentVisitMasterView.appointment_status).distinct().all()
        # Format the statuses into a list of dictionaries
        return [{"appointment_master_id": status[0], "status": status[1]} for status in statuses]
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter. Please specify either 'cancellation_reasons' or 'status'.")



#-------------get_consultancy_services-------------------------------------------------------------------------


#///////////
def get_appointments(
    db: Session,
    search_value: Union[str, int] = "ALL",
    id: Optional[int] = 0,
    consultant_id: Optional[Union[int, str]] = "ALL",
    service_id: Optional[Union[int, str]] = "ALL",
    status_id: Optional[Union[int, str]] = "ALL",
    from_date: Optional[date] = date.today(),
    to_date: Optional[date] = date.today()
) -> List[ResponseSchema]:
    try:
        appointments = []

        # Initialize search conditions
        search_conditions = []

        # Add condition for ID if provided
        if id != 0:
            search_conditions.append(OffAppointmentVisitMasterView.appointment_master_id == id)

        # Add condition for consultant ID
        if consultant_id != "ALL":
            search_conditions.append(OffAppointmentVisitDetailsView.consultant_id == consultant_id)

        # Add condition for service ID
        if service_id != "ALL":
            search_conditions.append(OffAppointmentVisitDetailsView.service_id == service_id)

        # Add condition for status ID
        if status_id != "ALL":
            search_conditions.append(OffAppointmentVisitDetailsView.appointment_status_id == status_id)

        # Add conditions for appointment visit date range
        search_conditions.append(
            OffAppointmentVisitDetailsView.appointment_visit_master_appointment_date.between(from_date, to_date)
        )

        # Add condition for search value if it's not 'ALL'
        if search_value != "ALL":
            # Filter search value from OffAppointmentVisitMasterView
            search_conditions.append(
                or_(
                    OffAppointmentVisitMasterView.mobile_number == search_value,
                    OffAppointmentVisitMasterView.email_id == search_value
                )
            )

        # Execute the query
        query_result = db.query(OffAppointmentVisitDetailsView).join(
            OffAppointmentVisitMasterView,
            OffAppointmentVisitDetailsView.appointment_visit_master_appointment_master_id == OffAppointmentVisitMasterView.appointment_master_id
        ).filter(and_(*search_conditions)).all()

        if not query_result:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Dictionary to store appointments by ID
        appointment_dict = {}

        # Iterate over query result
        for visit_details_data in query_result:
            appointment_id = visit_details_data.appointment_visit_master_appointment_master_id

            # Get the appointment master corresponding to the visit details
            appointment_master_data = db.query(OffAppointmentVisitMasterView).filter_by(
                appointment_master_id=appointment_id
            ).first()

            if appointment_master_data:
                # Convert appointment_master_data to schema
                appointment_master_schema = OffAppointmentVisitMasterViewSchema(
                    **appointment_master_data.__dict__
                )

                # Convert visit_details_data to schema
                visit_details_schema = OffAppointmentVisitDetailsViewSchema(**visit_details_data.__dict__)

                if appointment_id not in appointment_dict:
                    # Create new appointment entry in dictionary
                    appointment_dict[appointment_id] = {
                        "appointment_master": appointment_master_schema,
                        "visit_master": appointment_master_schema,
                        "visit_details": [visit_details_schema]
                    }
                else:
                    # Append visit details to existing entry
                    appointment_dict[appointment_id]["visit_details"].append(visit_details_schema)

        # Convert dictionary values to list of ResponseSchema objects
        appointments = [ResponseSchema(**appointment_data) for appointment_data in appointment_dict.values()]

        return appointments

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#---service-goods-master  swathy---------------------------



#---service-goods-master----------------------------

def get_all_service_goods_master(
    db: Session, 
    deleted_status: Optional[DeletedStatus] = None, 
    name: Optional[str] = None
):
    query = db.query(OffViewServiceGoodsMaster)
     
    if deleted_status == DeletedStatus.DELETED:
         query = query.filter(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'yes')
    elif deleted_status == DeletedStatus.NOT_DELETED:
        query = query.filter(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'no')
    
    # Apply filter based on service name
    if name:
        query = query.filter(OffViewServiceGoodsMaster.service_goods_name.ilike(f'%{name}%'))
    
    return query.all()

#-----------------------

def save_services_goods_master(
    db: Session,
    id: int,
    data: SaveServicesGoodsMasterRequest,
    user_id: int,
    action_type: RecordActionType
):
    if action_type == RecordActionType.INSERT_ONLY and id != 0:
        raise HTTPException(status_code=400, detail="Invalid action: For INSERT_ONLY, id should be 0")
    elif action_type == RecordActionType.UPDATE_ONLY and id <= 0:
        raise HTTPException(status_code=400, detail="Invalid action: For UPDATE_ONLY, id should be greater than 0")

    try:
        if action_type == RecordActionType.INSERT_ONLY:
            for master_data in data.master:
                new_master_data = master_data.dict()
                new_master_data.update({
                    "created_by": user_id,
                    "created_on": datetime.utcnow()
                })
                new_master = OffServiceGoodsMaster(**new_master_data)
                db.add(new_master)
                db.flush()  # Ensure new_master.id is available for details

                if master_data.is_bundled_service == 'yes':
                    for detail_data in data.details:
                        new_detail_data = detail_data.dict()
                        new_detail_data.update({
                            "service_goods_master_id": new_master.id,
                            "created_by": user_id,
                            "created_on": datetime.utcnow()
                        })
                        new_detail = OffServiceGoodsDetails(**new_detail_data)
                        db.add(new_detail)

        elif action_type == RecordActionType.UPDATE_ONLY:
            existing_master = db.query(OffServiceGoodsMaster).filter(OffServiceGoodsMaster.id == id).first()
            if not existing_master:
                raise HTTPException(status_code=404, detail="Master record not found")

            # Use the first item from data.master for update
            master_update_data = data.master[0].dict()
            for key, value in master_update_data.items():
                setattr(existing_master, key, value)
            existing_master.modified_by = user_id
            existing_master.modified_on = datetime.utcnow()

            if existing_master.is_bundled_service == 'yes':
                for detail_data in data.details:
                    existing_detail = db.query(OffServiceGoodsDetails).filter(
                        OffServiceGoodsDetails.service_goods_master_id == existing_master.id,
                        OffServiceGoodsDetails.bundled_service_goods_id == detail_data.bundled_service_goods_id
                    ).first()

                    if existing_detail:
                        for key, value in detail_data.dict().items():
                            setattr(existing_detail, key, value)
                        existing_detail.modified_by = user_id
                        existing_detail.modified_on = datetime.utcnow()
                    else:
                        new_detail_data = detail_data.dict()
                        new_detail_data.update({
                            "service_goods_master_id": existing_master.id,
                            "created_by": user_id,
                            "created_on": datetime.utcnow()
                        })
                        new_detail = OffServiceGoodsDetails(**new_detail_data)
                        db.add(new_detail)

        db.commit()
    except IntegrityError as e:
        db.rollback()
        if 'Duplicate entry' in str(e):
            raise HTTPException(status_code=400, detail="Duplicate entry detected.")
        else:
            raise e
    except Exception as e:
        db.rollback()
        raise e









#-----------Aparna----------------------------------
def save_services_goods_master(
    db: Session,
    id: int,
    data: SaveServicesGoodsMasterRequest,
    user_id: int,
    action_type: RecordActionType
):
    if action_type == RecordActionType.INSERT_ONLY and id != 0:
        raise HTTPException(status_code=400, detail="Invalid action: For INSERT_ONLY, id should be 0")
    elif action_type == RecordActionType.UPDATE_ONLY and id <= 0:
        raise HTTPException(status_code=400, detail="Invalid action: For UPDATE_ONLY, id should be greater than 0")

    try:
        if action_type == RecordActionType.INSERT_ONLY:
            for master_data in data.master:
                new_master_data = master_data.dict()
                new_master_data.update({
                    "created_by": user_id,
                    "created_on": datetime.utcnow()
                })
                new_master = OffServiceGoodsMaster(**new_master_data)
                db.add(new_master)
                db.flush()  # Ensure new_master.id is available for details

                for detail_data in data.details:
                    new_detail_data = detail_data.dict()
                    new_detail_data.update({
                        "service_goods_master_id": new_master.id,
                        "created_by": user_id,
                        "created_on": datetime.utcnow()
                    })
                    new_detail = OffServiceGoodsDetails(**new_detail_data)
                    db.add(new_detail)

        elif action_type == RecordActionType.UPDATE_ONLY:
            existing_master = db.query(OffServiceGoodsMaster).filter(OffServiceGoodsMaster.id == id).first()
            if not existing_master:
                raise HTTPException(status_code=404, detail="Master record not found")

            master_update_data = master_data.dict()
            for key, value in master_update_data.items():
                setattr(existing_master, key, value)
            existing_master.modified_by = user_id
            existing_master.modified_on = datetime.utcnow()

            for detail_data in data.details:
                existing_detail = db.query(OffServiceGoodsDetails).filter(
                    OffServiceGoodsDetails.service_goods_master_id == existing_master.id,
                    OffServiceGoodsDetails.bundled_service_goods_id == detail_data.bundled_service_goods_id
                ).first()

                if existing_detail:
                    for key, value in detail_data.dict().items():
                        setattr(existing_detail, key, value)
                    existing_detail.modified_by = user_id
                    existing_detail.modified_on = datetime.utcnow()
                else:
                    new_detail_data = detail_data.dict()
                    new_detail_data.update({
                        "service_goods_master_id": existing_master.id,
                        "created_by": user_id,
                        "created_on": datetime.utcnow()
                    })
                    new_detail = OffServiceGoodsDetails(**new_detail_data)
                    db.add(new_detail)

        db.commit()
    except IntegrityError as e:
        db.rollback()
        if 'Duplicate entry' in str(e):
            raise HTTPException(status_code=400, detail="Duplicate entry detected.")
        else:
            raise e
    except Exception as e:
        db.rollback()
        raise e

#---------------------------------------------------------------------


def get_consultants(db: Session) -> List[Employee]:
    """
    Fetches all consultants from the database.

    Args:
        db (Session): Database session.

    Returns:
        List[Employee]: List of consultants.
    """
    return db.query(Employee).filter(Employee.is_consultant == 'yes').all()

def get_all_employees(db: Session) -> List[Employee]:
    """
    Fetches all employees (non-consultants) from the database.

    Args:
        db (Session): Database session.

    Returns:
        List[Employee]: List of employees.
    """
    return db.query(Employee).filter(Employee.is_consultant == 'no').all()




def get_all_services(db: Session) -> List[OffViewConsultantDetails]:

    return db.query(OffViewConsultantDetails).all()




def get_consultants_for_service(db: Session, service_id: int) -> List[OffViewConsultantDetails]:
    # Query the database to get consultants for the given service_id
    consultants = db.query(OffViewConsultantDetails).filter(OffViewConsultantDetails.service_goods_master_id == service_id).all()
    return consultants

def get_all_services_by_consultant_id(db: Session, consultant_id: int) -> List[OffViewConsultantDetails]:
    services = db.query(OffViewConsultantDetails).filter(OffViewConsultantDetails.consultant_id == consultant_id).all()
    return services
