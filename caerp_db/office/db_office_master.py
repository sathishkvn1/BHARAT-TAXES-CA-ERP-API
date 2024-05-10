from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session
from caerp_constants.caerp_constants import AppointmentStatus,SearchCriteria
from caerp_db.hash import Hash
from typing import Dict, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm.session import Session
from caerp_db.office.models import OffAppointmentMaster, OffAppointmentVisitMaster,OffAppointmentVisitDetails,OffAppointmentVisitMasterView,OffAppointmentVisitDetailsView,OffAppointmentCancellationReason, OffServices
from caerp_schema.office.office_schema import OffAppointmentDetails, OffAppointmentMasterViewSchema, OffAppointmentVisitDetailsViewSchema, OffAppointmentVisitMasterViewSchema, RescheduleOrCancelRequest, ResponseSchema
from typing import Union,List
# from caerp_constants.caerp_constants import SearchCriteria

from sqlalchemy.exc import IntegrityError
def save_appointment_visit_master(
    db: Session,
    appointment_master_id: int,
    appointment_data: OffAppointmentDetails,
    created_by: Optional[int] = None
):
    try:
        # Create or update appointment master record
        if appointment_master_id == 0:
            appointment_master = OffAppointmentMaster(
                created_by=created_by,
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
            appointment_master.modified_by = created_by
            appointment_master.modified_on = datetime.utcnow()

        # Create or update visit master record
        if appointment_master_id == 0:
            visit_master = OffAppointmentVisitMaster(
                appointment_master_id=appointment_master.id,
                created_by=created_by,
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
            visit_master.modified_by = created_by
            visit_master.modified_on = datetime.utcnow()

        # Create or update visit details records
        visit_details_list = []
        for detail in appointment_data.visit_details:
            visit_detail = OffAppointmentVisitDetails(
                visit_master_id=visit_master.id if appointment_master_id == 0 else visit_master.id,
                consultant_id=visit_master.consultant_id,
                created_by=created_by,
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
# # get all 




def get_appointments(
    db: Session,
    search_criteria: Optional[SearchCriteria] = None,
    search_value: Union[str, int, None] = None,
    id: Optional[int] = None,
) -> Union[List[ResponseSchema], ResponseSchema]:
    try:
        appointments = []

        if search_criteria == SearchCriteria.ALL:
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

            for appointment_master_data, visit_master_data in query_result:
                # Convert database models to Pydantic schemas
                appointment_master_schema = OffAppointmentMasterViewSchema.from_orm(appointment_master_data)
                visit_master_schema = OffAppointmentVisitMasterViewSchema.from_orm(visit_master_data)

                # Filter visit details for the current visit master ID
                visit_master_id = visit_master_data.appointment_visit_master_appointment_master_id
                visit_details_schema = [
                    OffAppointmentVisitDetailsViewSchema.from_orm(data)
                    for _, data in query_result
                    if data.appointment_visit_master_appointment_master_id == visit_master_id
                ]

                # Construct appointment data
                appointment_data = ResponseSchema(
                    appointment_master=appointment_master_schema,
                    visit_master=visit_master_schema,
                    visit_details=visit_details_schema
                )

                # Add appointment data to the list of appointments
                appointments.append(appointment_data)

            return appointments

        elif search_criteria == SearchCriteria.email_id:
            # Fetch appointments based on email ID
            appointment_visit_details = db.query(OffAppointmentVisitMasterView).filter(
                OffAppointmentVisitMasterView.email_id == search_value
            ).first()

            if appointment_visit_details:
                # Fetch related details from OffAppointmentVisitDetailsView
                visit_details_data = db.query(OffAppointmentVisitDetailsView).filter(
                    OffAppointmentVisitDetailsView.appointment_visit_master_appointment_master_id ==
                    appointment_visit_details.appointment_master_id
                ).all()

                appointment_master_schema = OffAppointmentMasterViewSchema.from_orm(appointment_visit_details)
                visit_master_schema = OffAppointmentVisitMasterViewSchema.from_orm(appointment_visit_details)

                # Construct visit details schema
                visit_details_schema = [
                    OffAppointmentVisitDetailsViewSchema.from_orm(data)
                    for data in visit_details_data
                ]

                # Construct appointment data
                appointment_data = ResponseSchema(
                    appointment_master=appointment_master_schema,
                    visit_master=visit_master_schema,
                    visit_details=visit_details_schema
                )

                return [appointment_data]
            else:
                raise HTTPException(status_code=404, detail="Appointments not found for the given email ID")

        elif search_criteria == SearchCriteria.mobile_number:
            # Fetch appointments based on mobile number
            appointment_visit_details = db.query(OffAppointmentVisitMasterView).filter(
                OffAppointmentVisitMasterView.mobile_number == search_value
            ).first()

            if appointment_visit_details:
                # Fetch related details from OffAppointmentVisitDetailsView
                visit_details_data = db.query(OffAppointmentVisitDetailsView).filter(
                    OffAppointmentVisitDetailsView.appointment_visit_master_appointment_master_id ==
                    appointment_visit_details.appointment_master_id
                ).all()

                appointment_master_schema = OffAppointmentMasterViewSchema.from_orm(appointment_visit_details)
                visit_master_schema = OffAppointmentVisitMasterViewSchema.from_orm(appointment_visit_details)

                # Construct visit details schema
                visit_details_schema = [
                    OffAppointmentVisitDetailsViewSchema.from_orm(data)
                    for data in visit_details_data
                ]

                # Construct appointment data
                appointment_data = ResponseSchema(
                    appointment_master=appointment_master_schema,
                    visit_master=visit_master_schema,
                    visit_details=visit_details_schema
                )

                return [appointment_data]
            else:
                raise HTTPException(status_code=404, detail="Appointments not found for the given mobile number")

        elif id is not None:
            # Fetch appointments based on ID
            query_result = db.query(
                OffAppointmentVisitMasterView,
                OffAppointmentVisitDetailsView
            ).filter(
                OffAppointmentVisitMasterView.appointment_master_id == id,
                OffAppointmentVisitMasterView.appointment_master_id == OffAppointmentVisitDetailsView.appointment_visit_master_appointment_master_id
            ).first()

            if query_result:
                appointment_master_data, visit_details_data = query_result

                appointment_master_schema = OffAppointmentMasterViewSchema.from_orm(appointment_master_data)
                visit_master_schema = OffAppointmentVisitMasterViewSchema.from_orm(appointment_master_data)
                if isinstance(visit_details_data, list):
                    visit_details_schema = [
                        OffAppointmentVisitDetailsViewSchema.from_orm(data)
                        for data in visit_details_data
                    ]
                else:
                    # If visit_details_data is not iterable, convert it to a list
                    visit_details_schema = [OffAppointmentVisitDetailsViewSchema.from_orm(visit_details_data)]

                appointment_data = ResponseSchema(
                    appointment_master=appointment_master_schema,
                    visit_master=visit_master_schema,
                    visit_details=visit_details_schema
                )
                return [appointment_data]
            else:
                raise HTTPException(status_code=404, detail="Appointment data not found")

    except HTTPException:
        raise  # Re-raise HTTPExceptions to maintain their original status codes and details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))