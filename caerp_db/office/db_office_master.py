from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session
from caerp_db.hash import Hash
from typing import Dict, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm.session import Session
from caerp_db.office.models import OffAppointmentMaster, OffAppointmentVisitMaster,OffAppointmentVisitDetails,OffAppointmentVisitMasterView,OffAppointmentVisitDetailsView
from caerp_schema.office.office_schema import OffAppointmentDetails,ResponseSchema
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
