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

def save_appointment_visit_master(
    db: Session,
    appointment_data: List[OffAppointmentDetails],
    created_by: Optional[int] = None
):
    try:
        # Create or update appointment master record
        appointment_master = OffAppointmentMaster(
            created_by=created_by,
            created_on=datetime.utcnow(),
            **appointment_data.appointment_master.dict(exclude_unset=True)
        )
        db.add(appointment_master)
        db.commit()

        # Refresh the session to get the generated id of the appointment_master
        db.refresh(appointment_master)

        # Create visit master record
        visit_master = OffAppointmentVisitMaster(
            appointment_master_id=appointment_master.id,  # Use the id of the appointment_master
            created_by=created_by,
            created_on=datetime.utcnow(),
            **appointment_data.visit_master.dict(exclude_unset=True)
        )
        db.add(visit_master)
        db.commit()

        # Create or update visit details records
        visit_details_list = []
        for detail in appointment_data.visit_details:
            visit_detail = OffAppointmentVisitDetails(
                visit_master_id=visit_master.id,
                created_by=created_by,
                created_on=datetime.utcnow(),
                **detail.dict(exclude_unset=True)
            )
            db.add(visit_detail)
            visit_details_list.append(visit_detail)

        db.commit()  # Commit all changes to the database

        return appointment_master, visit_master, visit_details_list
    
    except Exception as e:
        raise e

# get by email id

# def get_appointment_visit_by_email(db: Session, email: str) -> Union[dict, HTTPException]:
#     try:
#         # Query the database to check if the email exists
#         appointment_visit_details = db.query(OffAppointmentVisitMasterView).filter(OffAppointmentVisitMasterView.email_id == email).first()

#         # If the email exists, construct and return the success response
#         if appointment_visit_details:
#             return {
#                 "success": True,
#                 "message": "Email already exists",
#                 "details": [OffAppointmentVisitMasterView.from_orm(appointment_visit_details).dict()]
#             }
#         else:
#             # If the email does not exist, return the failure response
#             return {
#                 "success": False,
#                 "message": "Email does not exist"
#             }
#     except Exception as e:
#         # If any error occurs, raise an HTTPException
#         raise HTTPException(status_code=500, detail=str(e))
    

# # get all 


# def get_appointments_by_criteria(db: Session, SearchCriteria: str, search_value: str):
#     if SearchCriteria == "retrieve_appointments":
#         # Retrieve all appointments
#         return db.query(OffAppointmentMaster).all()
#     elif SearchCriteria == "mobile_number":
#         # Search appointments by mobile number
#         return db.query(OffAppointmentMaster).filter_by(mobile_number=search_value).all()
#     elif SearchCriteria == "email_id":
#         # Search appointments by email ID
#         return db.query(OffAppointmentMaster).filter_by(email_id=search_value).all()