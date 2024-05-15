from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session
from caerp_constants.caerp_constants import AppointmentStatus, DeletedStatus,SearchCriteria
from caerp_db.hash import Hash
from typing import Dict, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm.session import Session
from caerp_db.office.models import OffAppointmentMaster, OffAppointmentVisitMaster,OffAppointmentVisitDetails,OffAppointmentVisitMasterView,OffAppointmentVisitDetailsView,OffAppointmentCancellationReason, OffServices, OffViewServiceGoodsMaster
from caerp_schema.office.office_schema import OffAppointmentDetails, OffAppointmentMasterViewSchema, OffAppointmentVisitDetailsViewSchema, OffAppointmentVisitMasterViewSchema, RescheduleOrCancelRequest, ResponseSchema,AppointmentVisitDetailsSchema
from typing import Union,List
from sqlalchemy import and_
# from caerp_constants.caerp_constants import SearchCriteria

from sqlalchemy.exc import IntegrityError


def save_appointment_visit_master(
    db: Session,
    appointment_master_id: int,
    appointment_data: OffAppointmentDetails,
    user_id: int
):
    try:
        # Create or update appointment master record
        if appointment_master_id == 0:
            appointment_master = OffAppointmentMaster(
                created_by=user_id,
                created_on=datetime.utcnow(),
                **appointment_data.appointment_master.dict(exclude_unset=True)
            )
            db.add(appointment_master)
            db.flush()  # Flush to generate ID before committing
        else:
            appointment_master = db.query(OffAppointmentMaster).filter(OffAppointmentMaster.id == appointment_master_id).first()
            if appointment_master is None:
                raise HTTPException(status_code=404, detail="Appointment master not found")

            for field, value in appointment_data.appointment_master.dict(exclude_unset=True).items():
                setattr(appointment_master, field, value)
            appointment_master.modified_by = user_id
            appointment_master.modified_on = datetime.utcnow()

        # Create or update visit master record
        if appointment_master_id == 0:
            visit_master = OffAppointmentVisitMaster(
                appointment_master_id=appointment_master.id,
                created_by=user_id,
                created_on=datetime.utcnow(),
                **appointment_data.visit_master.dict(exclude_unset=True)
            )
            db.add(visit_master)
            db.flush()  # Flush to generate ID before committing
        else:
            visit_master = db.query(OffAppointmentVisitMaster).filter(OffAppointmentVisitMaster.appointment_master_id == appointment_master_id).first()
            if visit_master is None:
                raise HTTPException(status_code=404, detail="Visit master not found")

            for field, value in appointment_data.visit_master.dict(exclude_unset=True).items():
                setattr(visit_master, field, value)
            visit_master.modified_by = user_id
            visit_master.modified_on = datetime.utcnow()

        # Create or update visit details records
        visit_details_list = []
        for detail in appointment_data.visit_details:
            visit_detail = OffAppointmentVisitDetails(
                visit_master_id=visit_master.id if appointment_master_id == 0 else visit_master.id,
                consultant_id=visit_master.consultant_id,
                created_by=user_id,
                created_on=datetime.utcnow(),
                **detail.dict(exclude_unset=True)
            )
            db.add(visit_detail)
            visit_details_list.append(visit_detail)

        db.commit()  # Commit all changes to the database

        return appointment_master, visit_master, visit_details_list
    
    except IntegrityError as e:
        db.rollback()
        # Check if the error message indicates a duplicate entry violation
        if 'Duplicate entry' in str(e):
            # Return a custom error message indicating the duplicate entry
            raise HTTPException(status_code=400, detail="Duplicate entry: This appointment already exists.")
        else:
            # For other IntegrityError cases, raise the exception with the original message
            raise e
    except Exception as e:
        db.rollback()
        raise e



def search_appointments(
    db: Session,
    consultant_id: Optional[int] = None,
    service_id: Optional[int] = None,
    status_id: Optional[int] = None,
    effective_from_date: date = date.today(),
    effective_to_date: date = date.today()
) -> List[ResponseSchema]:
    try:
        appointments = []

        # Start building the base query
        query = db.query(OffAppointmentVisitMasterView, OffAppointmentVisitDetailsView)

        # Initialize the search conditions
        search_conditions = []

        # Add conditions based on the provided parameters
        if consultant_id is not None:
            search_conditions.append(OffAppointmentVisitDetailsView.consultant_id == consultant_id)
        elif service_id is not None:
            search_conditions.append(OffAppointmentVisitDetailsView.service_id == service_id)
        elif status_id is not None:
            search_conditions.append(OffAppointmentVisitDetailsView.appointment_status_id == status_id)

        # Add conditions for appointment visit date range
        query = query.filter(
            OffAppointmentVisitDetailsView.appointment_visit_master_appointment_date.between(
                effective_from_date,
                effective_to_date
            )
        )

        # Apply all the search conditions to the query
        if search_conditions:
            query = query.filter(and_(*search_conditions))

        # Execute the query
        query_result = query.all()
        if not query_result:
            # Raise custom exception if no appointments are found
            raise HTTPException(status_code=404, detail="No appointments found")

        # Dictionary to store appointments by ID
        appointment_dict = {}

        # Iterate over query result
        for appointment_master_data, visit_detail_data in query_result:
            appointment_id = appointment_master_data.appointment_master_id

            # If appointment ID is already in the dictionary, append visit detail
            if appointment_id in appointment_dict:
                visit_detail_schema = OffAppointmentVisitDetailsViewSchema(
                    **visit_detail_data.__dict__
                )
                appointment_dict[appointment_id]["visit_details"].append(visit_detail_schema)
            else:
                # Convert appointment_master_data to schema
                appointment_master_schema = OffAppointmentVisitMasterViewSchema(
                    **appointment_master_data.__dict__
                )

                # Convert visit_detail_data to schema
                visit_detail_schema = OffAppointmentVisitDetailsViewSchema(
                    **visit_detail_data.__dict__
                )

                # Create new appointment entry in dictionary
                appointment_dict[appointment_id] = {
                    "appointment_master": appointment_master_schema,
                    "visit_master": appointment_master_schema,  # Assuming appointment_master_schema is what you want for visit_master
                    "visit_details": [visit_detail_schema]
                }

        # Convert dictionary values to list of ResponseSchema objects
        appointments = [ResponseSchema(**appointment_data) for appointment_data in appointment_dict.values()]

        return appointments

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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



#------get_consultancy_services
def get_consultancy_services(db: Session):
    return db.query(OffServices).filter(OffServices.is_consultancy_service == "yes").all()


#get all
def get_appointments(
    db: Session,
    search_criteria: Optional[str] = None,
    search_value: Union[str, int, None] = None,
    id: Optional[int] = None
) -> List[ResponseSchema]:
    try:
        appointments = []

        if search_criteria == "ALL":
            # Fetch all appointments and their related details using joins
            query_result = db.query(
                OffAppointmentVisitMasterView,
                OffAppointmentVisitDetailsView
            ).filter(
                OffAppointmentVisitMasterView.appointment_master_id ==
                OffAppointmentVisitDetailsView.appointment_visit_master_appointment_master_id
            ).all()

            if not query_result:
                raise HTTPException(status_code=404, detail="Appointment data not found")

            # Dictionary to store appointments by ID
            appointment_dict = {}

            # Iterate over query result
            for appointment_master_data, visit_detail_data in query_result:
                appointment_id = appointment_master_data.appointment_master_id

                # If appointment ID is already in the dictionary, append visit detail
                if appointment_id in appointment_dict:
                    visit_detail_schema = OffAppointmentVisitDetailsViewSchema(
                        **visit_detail_data.__dict__
                    )
                    appointment_dict[appointment_id]["visit_details"].append(visit_detail_schema)
                else:
                    # Convert appointment_master_data to schema
                    appointment_master_schema = OffAppointmentVisitMasterViewSchema(
                        **appointment_master_data.__dict__
                    )

                    # Convert visit_detail_data to schema
                    visit_detail_schema = OffAppointmentVisitDetailsViewSchema(
                        **visit_detail_data.__dict__
                    )

                    # Create new appointment entry in dictionary
                    appointment_dict[appointment_id] = {
                        "appointment_master": appointment_master_schema,
                        "visit_master": appointment_master_schema,  # Assuming appointment_master_schema is what you want for visit_master
                        "visit_details": [visit_detail_schema]
                    }

            # Convert dictionary values to list of ResponseSchema objects
            appointments = [ResponseSchema(**appointment_data) for appointment_data in appointment_dict.values()]

        elif id is not None:
            # If id is provided, filter appointments by ID
            appointment_master_data = db.query(OffAppointmentVisitMasterView).filter(OffAppointmentVisitMasterView.appointment_master_id == id).first()
            if not appointment_master_data:
                raise HTTPException(status_code=404, detail="Appointment not found")
            
            # Fetch related visit details
            visit_details_data = db.query(OffAppointmentVisitDetailsView).filter(
                OffAppointmentVisitDetailsView.appointment_visit_master_appointment_master_id == id
            ).all()

            # Convert appointment_master_data to schema
            appointment_master_schema = OffAppointmentVisitMasterViewSchema(
                **appointment_master_data.__dict__
            )

            # Convert visit_details_data to schema
            visit_details_schemas = [OffAppointmentVisitDetailsViewSchema(
                **visit_detail.__dict__
            ) for visit_detail in visit_details_data]

            # Create response model
            response_model = ResponseSchema(
                appointment_master=appointment_master_schema,
                visit_master=appointment_master_schema,  # Assuming appointment_master_schema is what you want for visit_master
                visit_details=visit_details_schemas
            )

            appointments.append(response_model)
            
        elif search_criteria in ["email_id", "mobile_number"]:
            # Fetch appointments based on email ID or mobile number
            appointment_visit_details = db.query(OffAppointmentVisitMasterView).filter(
                getattr(OffAppointmentVisitMasterView, search_criteria) == search_value
            ).first()

            if not appointment_visit_details:
                raise HTTPException(status_code=404, detail=f"Appointments not found for the given {search_criteria}")

            # Fetch related visit details
            visit_details_data = db.query(OffAppointmentVisitDetailsView).filter(
                OffAppointmentVisitDetailsView.appointment_visit_master_appointment_master_id ==
                appointment_visit_details.appointment_master_id
            ).all()

            # Convert appointment_visit_details to schema
            appointment_visit_details_schema = OffAppointmentVisitMasterViewSchema(
                **appointment_visit_details.__dict__
            )

            # Convert visit_details_data to schema
            visit_details_schemas = [OffAppointmentVisitDetailsViewSchema(
                **visit_detail.__dict__
            ) for visit_detail in visit_details_data]

            # Create response model
            response_model = ResponseSchema(
                appointment_master=appointment_visit_details_schema,
                visit_master=appointment_visit_details_schema,  # Assuming appointment_visit_details_schema is what you want for visit_master
                visit_details=visit_details_schemas
            )

            appointments.append(response_model)

        return appointments

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#---service-goods-master  swathy---------------------------




def get_all_service_goods_master(db: Session, deleted_status: DeletedStatus):
    query = db.query(OffViewServiceGoodsMaster)
    
    if deleted_status == DeletedStatus.DELETED:
        query = query.filter(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'yes')
    elif deleted_status == DeletedStatus.NOT_DELETED:
        query = query.filter(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'no')
    
    return query.all()


