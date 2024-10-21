import logging
import os
import shutil
from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session
from caerp_constants.caerp_constants import  ApplyTo, BooleanFlag, DeletedStatus, EntryPoint, RecordActionType, Status
from sqlalchemy.exc import SQLAlchemyError
# from caerp_db.common.models import Employee
from caerp_db.common.models import  BusinessActivity, BusinessActivityMaster, EmployeeEmploymentDetails, EmployeeMaster
from caerp_db.hash import Hash
from typing import Any, Dict, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm.session import Session
from caerp_db.office.models import AppDayOfWeek, CustomerDataDocumentMaster, OffAppointmentMaster, OffAppointmentStatus, OffAppointmentVisitMaster,OffAppointmentVisitDetails,OffAppointmentVisitMasterView,OffAppointmentVisitDetailsView,OffAppointmentCancellationReason, OffConsultantSchedule, OffConsultantServiceDetails, OffConsultationMode, OffConsultationTaskDetails, OffConsultationTaskMaster, OffConsultationTool, OffDocumentDataMaster, OffDocumentDataType, OffEnquiryDetails, OffEnquiryMaster, OffOfferDetails, OffOfferMaster, OffServiceDocumentDataDetails, OffServiceDocumentDataMaster, OffServiceGoodsCategory, OffServiceGoodsDetails, OffServiceGoodsGroup, OffServiceGoodsMaster, OffServiceGoodsPriceMaster, OffServiceGoodsSubCategory, OffServiceGoodsSubGroup, OffServiceTaskHistory, OffServiceTaskMaster,OffViewConsultantServiceDetails, OffViewConsultationTaskMaster, OffViewEnquiryDetails, OffViewEnquiryMaster, OffViewServiceDocumentsDataDetails, OffViewServiceDocumentsDataMaster, OffViewServiceGoodsDetails, OffViewServiceGoodsMaster, OffViewServiceGoodsPriceMaster, OffViewServiceTaskMaster, OffViewWorkOrderBusinessPlaceDetails, OffWorkOrderDetails, OffWorkOrderMaster, WorkOrderBusinessPlaceDetails, WorkOrderDependancy, WorkOrderDetailsView, WorkOrderMasterView
from caerp_functions.generate_book_number import generate_book_number

from caerp_router.common.common_functions import update_column_value
from caerp_schema.common.common_schema import BusinessActivityMasterSchema, BusinessActivitySchema
from caerp_schema.office.office_schema import AdditionalServices, AppointmentStatusConstants, Category, ConsultantScheduleCreate, ConsultantService, ConsultationModeSchema, ConsultationToolSchema, CreateWorkOrderDependancySchema, CreateWorkOrderRequest, CreateWorkOrderSetDtailsRequest, DocumentsSchema, OffAppointmentDetails, OffAppointmentMasterViewSchema,OffAppointmentVisitDetailsViewSchema, OffAppointmentVisitMasterViewSchema, OffConsultationTaskMasterSchema, OffDocumentDataMasterBase, OffEnquiryDetailsSchema, OffEnquiryMasterSchema, OffEnquiryResponseSchema, OffServiceTaskMasterSchema, OffViewBusinessPlaceDetailsScheema, OffViewConsultationTaskMasterSchema, OffViewEnquiryDetailsSchema, OffViewEnquiryMasterSchema, OffViewEnquiryResponseSchema, OffViewServiceDocumentsDataDetailsDocCategory, OffViewServiceDocumentsDataDetailsSchema, OffViewServiceDocumentsDataMasterSchema, OffViewServiceGoodsDetailsDisplay, OffViewServiceGoodsMasterDisplay, OffViewServiceTaskMasterSchema, OffViewWorkOrderDetailsSchema, OffViewWorkOrderMasterSchema, OffWorkOrderMasterSchema, PriceData, PriceHistoryModel, RescheduleOrCancelRequest, ResponseSchema, SaveOfferDetails, SaveServiceDocumentDataMasterRequest, SaveServicesGoodsMasterRequest, Service_Group, ServiceDocumentsList_Group,  ServiceModel, ServiceModelSchema, ServicePriceHistory, ServiceTaskMasterAssign, Slot, SubCategory, SubGroup, UpdateCustomerDataDocumentSchema, WorkOrderDependancyResponseSchema, WorkOrderDependancySchema,  WorkOrderResponseSchema, WorkOrderSetDetailsResponseSchema
from typing import Union,List
from sqlalchemy import and_, insert,or_, func
from pathlib import Path 
# from caerp_constants.caerp_constants import SearchCriteria
from fastapi import logger
from sqlalchemy.exc import IntegrityError,OperationalError
from sqlalchemy.exc import IntegrityError

UPLOAD_WORK_ORDER_DOCUMENTS         ="uploads/work_order_documents"
#------------------------------------------------------------------------------------------------------------
# def save_appointment_visit_master(
#     db: Session,
#     appointment_master_id: int,
#     appointment_data: OffAppointmentDetails,
#     user_id: int
# ):
#     try:
#         # Manually begin the transaction
#         db.begin()

#         if appointment_master_id == 0:
#             # Insert operation
#             appointment_number = generate_book_number('APPOINTMENT', db)
#             appointment_master = OffAppointmentMaster(
#                 created_by=user_id,
#                 created_on=datetime.now(),
#                 **appointment_data.appointment_master.model_dump(exclude_unset=True)
#             )
#             db.add(appointment_master)
#             db.flush()  # Ensure changes are flushed to the database

#             visit_master = OffAppointmentVisitMaster(
#                 appointment_master_id=appointment_master.id,
#                 appointment_number=appointment_number,
#                 created_by=user_id,
#                 created_on=datetime.now(),
#                 **appointment_data.visit_master.model_dump(exclude_unset=True)
#             )
#             db.add(visit_master)
#             db.flush()

#             visit_details_list = []
#             for detail_data in appointment_data.visit_details:
#                 visit_detail = OffAppointmentVisitDetails(
#                     visit_master_id=visit_master.id,
#                     consultant_id=visit_master.consultant_id,
#                     created_by=user_id,
#                     created_on=datetime.now(),
#                     **detail_data.model_dump(exclude_unset=True)
#                 )
#                 db.add(visit_detail)
#                 visit_details_list.append(visit_detail)

#         elif appointment_master_id > 0:
#             # Update operation
#             appointment_master = db.query(OffAppointmentMaster).filter(
#                 OffAppointmentMaster.id == appointment_master_id).first()
#             if not appointment_master:
#                 return {"detail":"Appointment master not found"}

#             for field, value in appointment_data.appointment_master.model_dump(exclude_unset=True).items():
#                 setattr(appointment_master, field, value)
#             appointment_master.modified_by = user_id
#             appointment_master.modified_on = datetime.now()

#             visit_master = db.query(OffAppointmentVisitMaster).filter(
#                 OffAppointmentVisitMaster.appointment_master_id == appointment_master_id).first()
#             if not visit_master:
#                 return {"detail":"Visit master not found"}

#             for field, value in appointment_data.visit_master.model_dump(exclude_unset=True).items():
#                 if field == "remarks":
#                     if visit_master.remarks:
#                         setattr(visit_master, field, visit_master.remarks + "**" + value)
#                     else:
#                         setattr(visit_master, field, value)
#                 else:
#                     setattr(visit_master, field, value)
#             visit_master.modified_by = user_id
#             visit_master.modified_on = datetime.now()

#             existing_details = db.query(OffAppointmentVisitDetails).filter(
#                 OffAppointmentVisitDetails.visit_master_id == visit_master.id).all()

#             existing_details_dict = {detail.service_id: detail for detail in existing_details}

#             for detail in existing_details:
#                 detail.is_deleted = "yes"
#                 detail.deleted_by = user_id
#                 detail.deleted_on = datetime.now()
#                 detail.modified_by = user_id
#                 detail.modified_on = datetime.now()

#             visit_details_list = []
#             for detail_data in appointment_data.visit_details:
#                 detail_data_dict = detail_data.model_dump(exclude_unset=True)
#                 service_id = detail_data_dict.get("service_id")

#                 if service_id in existing_details_dict:
#                     existing_detail = existing_details_dict[service_id]
#                     for key, value in detail_data_dict.items():
#                         setattr(existing_detail, key, value)
#                     existing_detail.is_deleted = "no"
#                     existing_detail.deleted_by = None
#                     existing_detail.deleted_on = None
#                     existing_detail.modified_by = user_id
#                     existing_detail.modified_on = datetime.now()
#                     visit_details_list.append(existing_detail)
#                 else:
#                     visit_detail = OffAppointmentVisitDetails(
#                         visit_master_id=visit_master.id,
#                         consultant_id=visit_master.consultant_id,
#                         created_by=user_id,
#                         created_on=datetime.now(),
#                         **detail_data_dict
#                     )
#                     db.add(visit_detail)
#                     visit_details_list.append(visit_detail)

#         # Commit the transaction
#         db.commit()

#         # Return response outside of the transaction block
#         return {
#             "appointment_master": appointment_master,
#             "visit_master": visit_master,
#             "visit_details": visit_details_list
#         }

#     except IntegrityError as e:
#         db.rollback()
#         if 'Duplicate entry' in str(e):
#             raise HTTPException(status_code=400, detail="The selected slot is already booked. Please choose another slot.")
#         else:
#             raise e
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))

# def save_appointment_visit_master(
#     db: Session,
#     appointment_master_id: int,
#     appointment_data: OffAppointmentDetails,
#     user_id: int
# ):
#     visit_details_list = []  # Initialize visit_details_list at the start
#     new_visit_master = None  # Initialize new_visit_master
#     existing_visit_master = None  # Initialize existing_visit_master

#     try:
#         # Manually begin the transaction
#         db.begin()

#         if appointment_master_id == 0:
#             # Insert operation for new appointment
#             appointment_number = generate_book_number('APPOINTMENT', db)
#             appointment_master = OffAppointmentMaster(
#                 created_by=user_id,
#                 created_on=datetime.now(),
#                 **appointment_data.appointment_master.model_dump(exclude_unset=True)
#             )
#             db.add(appointment_master)
#             db.flush()  # Ensure changes are flushed to the database

#             visit_master = OffAppointmentVisitMaster(
#                 appointment_master_id=appointment_master.id,
#                 appointment_number=appointment_number,
#                 created_by=user_id,
#                 created_on=datetime.now(),
#                 **appointment_data.visit_master.model_dump(exclude_unset=True)
#             )
#             db.add(visit_master)
#             db.flush()  # Flush to get the ID of the new visit master

#             # Add new visit details
#             for detail_data in appointment_data.visit_details:
#                 visit_detail = OffAppointmentVisitDetails(
#                     visit_master_id=visit_master.id,  # Use the new visit master ID
#                     consultant_id=visit_master.consultant_id,
#                     created_by=user_id,
#                     created_on=datetime.now(),
#                     **detail_data.model_dump(exclude_unset=True)
#                 )
#                 db.add(visit_detail)
#                 visit_details_list.append(visit_detail)

#         elif appointment_master_id > 0:
#             # Update operation for existing appointment
#             appointment_master = db.query(OffAppointmentMaster).filter(
#                 OffAppointmentMaster.id == appointment_master_id).first()
#             if not appointment_master:
#                 return {"detail": "Appointment master not found"}

#             # Update appointment master fields
#             for field, value in appointment_data.appointment_master.model_dump(exclude_unset=True).items():
#                 setattr(appointment_master, field, value)
#             appointment_master.modified_by = user_id
#             appointment_master.modified_on = datetime.now()

#             # Check existing visit master for the same date and consultant ID
#             existing_visit_master = db.query(OffAppointmentVisitMaster).filter(
#                 OffAppointmentVisitMaster.appointment_master_id == appointment_master_id,
#                 OffAppointmentVisitMaster.appointment_date == appointment_data.visit_master.appointment_date,
#                 OffAppointmentVisitMaster.consultant_id == appointment_data.visit_master.consultant_id
#             ).first()

#             if existing_visit_master:
#                 # Update existing visit master
#                 for field, value in appointment_data.visit_master.model_dump(exclude_unset=True).items():
#                     if field == "remarks":
#                         if existing_visit_master.remarks:
#                             # Append new remarks to existing remarks with separator
#                             setattr(existing_visit_master, field, existing_visit_master.remarks + "**" + value)
#                         else:
#                             setattr(existing_visit_master, field, value)
#                     else:
#                         setattr(existing_visit_master, field, value)
                
#                 existing_visit_master.modified_by = user_id
#                 existing_visit_master.modified_on = datetime.now()

#                 # Handle visit details: update existing or add new
#                 existing_details = db.query(OffAppointmentVisitDetails).filter(
#                     OffAppointmentVisitDetails.visit_master_id == existing_visit_master.id).all()

#                 existing_details_dict = {detail.service_id: detail for detail in existing_details}

#                 for detail in existing_details:
#                     detail.is_deleted = "yes"
#                     detail.deleted_by = user_id
#                     detail.deleted_on = datetime.now()
#                     detail.modified_by = user_id
#                     detail.modified_on = datetime.now()

#                 for detail_data in appointment_data.visit_details:
#                     detail_data_dict = detail_data.model_dump(exclude_unset=True)
#                     service_id = detail_data_dict.get("service_id")

#                     if service_id in existing_details_dict:
#                         existing_detail = existing_details_dict[service_id]
#                         for key, value in detail_data_dict.items():
#                             setattr(existing_detail, key, value)
#                         existing_detail.is_deleted = "no"
#                         existing_detail.deleted_by = None
#                         existing_detail.deleted_on = None
#                         existing_detail.modified_by = user_id
#                         existing_detail.modified_on = datetime.now()
#                     else:
#                         # If service_id is not found, create a new visit detail
#                         visit_detail = OffAppointmentVisitDetails(
#                             visit_master_id=existing_visit_master.id,
#                             consultant_id=existing_visit_master.consultant_id,
#                             created_by=user_id,
#                             created_on=datetime.now(),
#                             **detail_data_dict
#                         )
#                         db.add(visit_detail)
#                         visit_details_list.append(visit_detail)

#             else:
#                 # Create new visit master for a different date or consultant ID
#                 new_visit_master = OffAppointmentVisitMaster(
#                     appointment_master_id=appointment_master.id,
#                     appointment_number=generate_book_number('APPOINTMENT', db),
#                     created_by=user_id,
#                     created_on=datetime.now(),
#                     **appointment_data.visit_master.model_dump(exclude_unset=True)
#                 )
#                 db.add(new_visit_master)
#                 db.flush()  # Flush to get the ID of the new visit master

#                 # Add new visit details with the new visit master ID
#                 for detail_data in appointment_data.visit_details:
#                     visit_detail = OffAppointmentVisitDetails(
#                         visit_master_id=new_visit_master.id,  # Use the new visit master ID
#                         consultant_id=new_visit_master.consultant_id,
#                         created_by=user_id,
#                         created_on=datetime.now(),
#                         **detail_data.model_dump(exclude_unset=True)
#                     )
#                     db.add(visit_detail)
#                     visit_details_list.append(visit_detail)

#         # Commit the transaction
#         db.commit()

#         # Return response outside of the transaction block
#         return {
#             "appointment_master": appointment_master,
#             "visit_master": existing_visit_master if existing_visit_master else new_visit_master,
#             "visit_details": visit_details_list  # Return the list of visit details
#         }

#     except IntegrityError as e:
#         db.rollback()
#         if 'Duplicate entry' in str(e):
#             raise HTTPException(status_code=400, detail="The selected slot is already booked. Please choose another slot.")
#         else:
#             raise e
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))



def save_appointment_visit_master(
    db: Session,
    appointment_master_id: int,
    appointment_data: OffAppointmentDetails,
    user_id: int
):
    visit_details_list = []  # Initialize visit_details_list at the start
    new_visit_master = None  # Initialize new_visit_master
    existing_visit_master = None  # Initialize existing_visit_master
    financial_year_id = 1
    customer_id = 1
    try:
        # Manually begin the transaction
        db.begin()

        if appointment_master_id == 0:
            
            # Insert operation for new appointment
            appointment_number = generate_book_number('APPOINTMENT',financial_year_id,customer_id, db)
            appointment_master = OffAppointmentMaster(
                created_by=user_id,
                created_on=datetime.now(),
                **appointment_data.appointment_master.model_dump(exclude_unset=True)
            )
            db.add(appointment_master)
            db.flush()  # Ensure changes are flushed to the database

            visit_master = OffAppointmentVisitMaster(
                appointment_master_id=appointment_master.id,
                appointment_number=appointment_number,
                created_by=user_id,
                created_on=datetime.now(),
                **appointment_data.visit_master.model_dump(exclude_unset=True)
            )
            db.add(visit_master)
            db.flush()  # Flush to get the ID of the new visit master

            # Add new visit details
            for detail_data in appointment_data.visit_details:
                visit_detail = OffAppointmentVisitDetails(
                    visit_master_id=visit_master.id,  # Use the new visit master ID
                    consultant_id=visit_master.consultant_id,
                    created_by=user_id,
                    created_on=datetime.now(),
                    **detail_data.model_dump(exclude_unset=True)
                )
                db.add(visit_detail)
                visit_details_list.append(visit_detail)

        elif appointment_master_id > 0:
            # Update operation for existing appointment
            appointment_master = db.query(OffAppointmentMaster).filter(
                OffAppointmentMaster.id == appointment_master_id).first()
            if not appointment_master:
                return {"detail": "Appointment master not found"}

            # Update appointment master fields
            for field, value in appointment_data.appointment_master.model_dump(exclude_unset=True).items():
                setattr(appointment_master, field, value)
            appointment_master.modified_by = user_id
            appointment_master.modified_on = datetime.now()

            # Check existing visit master for the same date and consultant ID
            existing_visit_master = db.query(OffAppointmentVisitMaster).filter(
                OffAppointmentVisitMaster.appointment_master_id == appointment_master_id,
                OffAppointmentVisitMaster.appointment_date == appointment_data.visit_master.appointment_date,
                OffAppointmentVisitMaster.consultant_id == appointment_data.visit_master.consultant_id
            ).first()

            if existing_visit_master:
                # Update existing visit master
                for field, value in appointment_data.visit_master.model_dump(exclude_unset=True).items():
                    if field == "remarks":
                        if existing_visit_master.remarks:
                            # Append new remarks to existing remarks with separator
                            setattr(existing_visit_master, field, existing_visit_master.remarks + "**" + value)
                        else:
                            setattr(existing_visit_master, field, value)
                    else:
                        setattr(existing_visit_master, field, value)
                
                existing_visit_master.modified_by = user_id
                existing_visit_master.modified_on = datetime.now()

                # Handle visit details: update existing or add new
                existing_details = db.query(OffAppointmentVisitDetails).filter(
                    OffAppointmentVisitDetails.visit_master_id == existing_visit_master.id).all()

                existing_details_dict = {detail.service_id: detail for detail in existing_details}

                for detail in existing_details:
                    detail.is_deleted = "yes"
                    detail.deleted_by = user_id
                    detail.deleted_on = datetime.now()
                    detail.modified_by = user_id
                    detail.modified_on = datetime.now()

                for detail_data in appointment_data.visit_details:
                    detail_data_dict = detail_data.model_dump(exclude_unset=True)
                    service_id = detail_data_dict.get("service_id")

                    if service_id in existing_details_dict:
                        existing_detail = existing_details_dict[service_id]
                        for key, value in detail_data_dict.items():
                            setattr(existing_detail, key, value)
                        existing_detail.is_deleted = "no"
                        existing_detail.deleted_by = None
                        existing_detail.deleted_on = None
                        existing_detail.modified_by = user_id
                        existing_detail.modified_on = datetime.now()
                    else:
                        # If service_id is not found, create a new visit detail
                        visit_detail = OffAppointmentVisitDetails(
                            visit_master_id=existing_visit_master.id,
                            consultant_id=existing_visit_master.consultant_id,
                            created_by=user_id,
                            created_on=datetime.now(),
                            **detail_data_dict
                        )
                        db.add(visit_detail)
                        visit_details_list.append(visit_detail)

            else:
                # Create new visit master for a different date or consultant ID
                new_visit_master = OffAppointmentVisitMaster(
                    appointment_master_id=appointment_master.id,
                    appointment_number=generate_book_number('APPOINTMENT',financial_year_id,customer_id, db),
                    created_by=user_id,
                    created_on=datetime.now(),
                    **appointment_data.visit_master.model_dump(exclude_unset=True)
                )
                db.add(new_visit_master)
                db.flush()  # Flush to get the ID of the new visit master

                # Add new visit details with the new visit master ID
                for detail_data in appointment_data.visit_details:
                    visit_detail = OffAppointmentVisitDetails(
                        visit_master_id=new_visit_master.id,  # Use the new visit master ID
                        consultant_id=new_visit_master.consultant_id,
                        created_by=user_id,
                        created_on=datetime.now(),
                        **detail_data.model_dump(exclude_unset=True)
                    )
                    db.add(visit_detail)
                    visit_details_list.append(visit_detail)

        # Commit the transaction
        db.commit()

        # Return response outside of the transaction block
        return {
            "appointment_master": appointment_master,
            "visit_master": existing_visit_master if existing_visit_master else new_visit_master,
            "visit_details": visit_details_list  # Return the list of visit details
        }

    except IntegrityError as e:
        db.rollback()
        if 'Duplicate entry' in str(e):
            raise HTTPException(status_code=400, detail="The selected slot is already booked. Please choose another slot.")
        else:
            raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#------------------------------------------------------------------------------------------------------------
#///////////////////////////////////////////////////
def get_appointment_details(appointment_id :int , db:Session):
    data =db.query(OffAppointmentMaster).filter(OffAppointmentMaster.id == appointment_id).first()
    return data

#######--SERVICE_GOODS-MASTER--#############################################################

def save_services_goods_master(
    db: Session,
    id: int,
    data: SaveServicesGoodsMasterRequest,
    user_id: int
):
    try:
        if id == 0:
            for master_data in data.master:
                new_master_data = master_data.model_dump()
                new_master_data.update({
                    "created_by": user_id,
                    "created_on": datetime.now()
                })
                new_master = OffServiceGoodsMaster(**new_master_data)
                db.add(new_master)
                db.flush()  # Ensure new_master.id is available for details

                if master_data.is_bundled_service == 'yes':
                    for detail_data in data.details:
                        new_detail_data = detail_data.model_dump()
                        new_detail_data.update({
                            "bundled_service_goods_id": new_master.id,
                            "created_by": user_id,
                            "created_on": datetime.now()
                        })
                        new_detail = OffServiceGoodsDetails(**new_detail_data)
                        db.add(new_detail)

            db.commit()
            return {"success": True, "message": "Saved successfully", "action": "insert"}

        else:
            existing_master = db.query(OffServiceGoodsMaster).filter(OffServiceGoodsMaster.id == id).first()
            if not existing_master:
                # raise HTTPException(status_code=404, detail="Master record not found")
                return {"message":" master record not found"}
                
            master_update_data = data.master[0].model_dump()
            for key, value in master_update_data.items():
                setattr(existing_master, key, value)
            existing_master.modified_by = user_id
            existing_master.modified_on = datetime.now()

            if existing_master.is_bundled_service == 'yes':
                existing_details = db.query(OffServiceGoodsDetails).filter(
                    OffServiceGoodsDetails.bundled_service_goods_id == existing_master.id
                ).all()

                existing_detail_dict = {detail.service_goods_master_id: detail for detail in existing_details}
                incoming_detail_dict = {detail.service_goods_master_id: detail for detail in data.details}

                for detail_data in data.details:
                    detail_data_dict = detail_data.model_dump()
                    existing_detail = existing_detail_dict.get(detail_data.service_goods_master_id)

                    if existing_detail:
                        for key, value in detail_data_dict.items():
                            setattr(existing_detail, key, value)
                        existing_detail.modified_by = user_id
                        existing_detail.modified_on = datetime.now()
                    else:
                        new_detail_data = detail_data_dict
                        new_detail_data.update({
                            "bundled_service_goods_id": existing_master.id,
                            "created_by": user_id,
                            "created_on": datetime.now()
                        })
                        new_detail = OffServiceGoodsDetails(**new_detail_data)
                        db.add(new_detail)

                for service_goods_master_id, existing_detail in existing_detail_dict.items():
                    if service_goods_master_id not in incoming_detail_dict:
                        
                        existing_detail.is_deleted = "yes"
                        existing_detail.deleted_by = user_id
                        existing_detail.deleted_on = datetime.now()
                        


            db.commit()
            return {"success": True, "message": "Updated successfully", "action": "update"}

    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database connection error.")
    except Exception as e:
        db.rollback()
        raise e
#--------------------------------------------------------------------------------------------------------

def reschedule_or_cancel_appointment(db: Session,
                                     request_data: RescheduleOrCancelRequest,
                                     action: AppointmentStatusConstants, 
                                     visit_master_id: int):
    appointment = db.query(OffAppointmentVisitMaster).filter(OffAppointmentVisitMaster.id == visit_master_id).first()
    
    if not appointment:
        return {"message": "Appointment not found"}
    
    # Fetch the status ID based on the action
    status_name = ""
    if action == AppointmentStatusConstants.RESCHEDULED:
        status_name = "RESCHEDULED"
    elif action == AppointmentStatusConstants.CANCELED:
        status_name = "CANCELED"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    status = db.query(OffAppointmentStatus).filter(OffAppointmentStatus.appointment_status == status_name).first()
    
    if not status:
        return {"message": f"Status '{status_name}' not found"}
    
    status_id = status.id

    # Handle Rescheduling
    if action == AppointmentStatusConstants.RESCHEDULED:
        if not request_data.date or not request_data.from_time or not request_data.to_time:
            return {"message": "Date and time are required for rescheduling"} 
        
        # Update appointment status and details in OffAppointmentVisitMaster
        appointment.appointment_status_id = status_id
        appointment.consultant_id = request_data.consultant_id
        appointment.appointment_date = request_data.date
        appointment.appointment_time_from = request_data.from_time
        appointment.appointment_time_to = request_data.to_time
        
        # Update remarks with the provided description
        if appointment.remarks:
            appointment.remarks += f"**{request_data.description}"
        else:
            appointment.remarks = request_data.description

        # Fetch and update the consultant ID in OffAppointmentVisitDetails
        appointment_details = db.query(OffAppointmentVisitDetails).filter(OffAppointmentVisitDetails.visit_master_id == visit_master_id).all()

        for detail in appointment_details:
            detail.consultant_id = request_data.consultant_id
        
        db.commit()
        return {"success": True, "message": "Appointment rescheduled successfully"}
    
    # Handle Canceling
    elif action == AppointmentStatusConstants.CANCELED:
        # Update appointment status to CANCELED
        appointment.appointment_status_id = status_id
        
        # Update remarks with the provided description
        if appointment.remarks:
            appointment.remarks += f"**{request_data.description}"
        else:
            appointment.remarks = request_data.description
        
        db.commit()
        return {"success": True, "message": "Appointment canceled successfully"}
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



#-------------get_consultancy_services-------------------------------------------------------------------
def get_appointments(
    db: Session,
    search_value: Union[str, int] = "ALL",
    id: Optional[int] = 0,
    consultant_id: Optional[Union[int, str]] = "ALL",
    service_id: Optional[Union[int, str]] = "ALL",
    status_id: Optional[Union[int, str]] = "ALL",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    mobile_number: Optional[str] = None
) -> List[ResponseSchema]:
    try:
        # Prepare search conditions
        search_conditions = []

        # Mobile number filter
        if mobile_number:
            search_conditions.append(OffAppointmentVisitMasterView.mobile_number == mobile_number)
        else:
            # Date range filter
            if from_date and to_date:
                search_conditions.append(OffAppointmentVisitMasterView.appointment_date.between(from_date, to_date))
            if id != 0:
                search_conditions.append(OffAppointmentVisitMasterView.appointment_master_id == id)
            if consultant_id != "ALL":
                search_conditions.append(OffAppointmentVisitMasterView.consultant_id == consultant_id)
            if status_id != "ALL":
                search_conditions.append(OffAppointmentVisitMasterView.appointment_status_id == status_id)
            if search_value != "ALL":
                search_conditions.append(
                    or_(
                        OffAppointmentVisitMasterView.mobile_number.like(f"%{search_value}%"),
                        OffAppointmentVisitMasterView.email_id.like(f"%{search_value}%")
                    )
                )

        # Main query to fetch visit details along with their associated appointment masters
        main_service_query = db.query(
            OffAppointmentVisitMasterView,
            OffAppointmentVisitDetailsView
        ).join(
            OffAppointmentVisitDetailsView,
            OffAppointmentVisitDetailsView.visit_master_id == OffAppointmentVisitMasterView.visit_master_id
        ).filter(
            *search_conditions,
            OffAppointmentVisitDetailsView.is_deleted == "no"
        )

        if service_id != "ALL":
            main_service_query = main_service_query.filter(OffAppointmentVisitDetailsView.service_id == service_id)

        # Order by appointment date (descending) and full name (ascending)
        main_service_query = main_service_query.order_by(
            OffAppointmentVisitMasterView.appointment_date.desc(),
            OffAppointmentVisitMasterView.full_name.asc()
        )

        # Execute the query to fetch all relevant results
        main_service_results = main_service_query.all()

        # Organize appointments
        appointments = {}
        
        for appointment_master, visit_details in main_service_results:
            # Extract data from appointment master
            appointment_master_data = {
                column.name: getattr(appointment_master, column.name)
                for column in appointment_master.__table__.columns
            }
            appointment_master_schema = OffAppointmentMasterViewSchema(**appointment_master_data)

            # Create the visit master schema from visit details
            visit_master_data = {
                column.name: getattr(visit_details, column.name)
                for column in visit_details.__table__.columns
            }
            visit_master_schema = OffAppointmentVisitMasterViewSchema(**visit_master_data)

            # Create visit detail schema using the OffAppointmentVisitDetailsViewSchema
            visit_detail_schema = OffAppointmentVisitDetailsViewSchema(
                visit_master_id=visit_details.visit_master_id, 
                visit_details_id=visit_details.visit_details_id,
                service_id=visit_details.service_id,
                service_goods_name=visit_details.service_goods_name,
                is_main_service=visit_details.is_main_service  # Ensure is_main_service is provided
            )

            # Group by visit master ID
            if visit_master_schema.visit_master_id not in appointments:
                appointments[visit_master_schema.visit_master_id] = ResponseSchema(
                    appointment_master=appointment_master_schema,
                    visit_master=visit_master_schema,
                    visit_details=[visit_detail_schema]  # Initialize visit details list
                )
            else:
                appointments[visit_master_schema.visit_master_id].visit_details.append(visit_detail_schema)

        return list(appointments.values())  # Return the list of grouped appointments

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#---service-goods-master  swathy---------------------------





#---service-goods-master-------------------------------------------------------------------------------------


# def get_all_service_goods_master(
#     db: Session,
#     deleted_status: Optional[str] = None,
#     name: Optional[str] = None,
#     service_goods_type: Union[int, str] = 'ALL', 
#     group_id: Union[int, str] = 'ALL',
#     sub_group_id: Union[int, str] = 'ALL',
#     category_id: Union[int, str] = 'ALL',
#     sub_category_id: Union[int, str] = 'ALL'
# ) -> List[OffViewServiceGoodsMasterDisplay]:
#     try:
#         # Initialize search conditions
#         search_conditions = []

#         # Apply filter conditions
#         if deleted_status == DeletedStatus.DELETED:
#             search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'yes')
#         elif deleted_status == DeletedStatus.NOT_DELETED:
#             search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'no')

#         if name:
#             search_conditions.append(OffViewServiceGoodsMaster.service_goods_name.ilike(f'%{name}%'))
        
#         if service_goods_type != 'ALL':
#             search_conditions.append(OffViewServiceGoodsMaster.hsn_sac_class_id == service_goods_type)

#         if group_id != 'ALL':
#             search_conditions.append(OffViewServiceGoodsMaster.group_id == group_id)

#         if sub_group_id != 'ALL':
#             search_conditions.append(OffViewServiceGoodsMaster.sub_group_id == sub_group_id)

#         if category_id != 'ALL':
#             search_conditions.append(OffViewServiceGoodsMaster.category_id == category_id)

#         if sub_category_id != 'ALL':
#             search_conditions.append(OffViewServiceGoodsMaster.sub_category_id == sub_category_id)

#         # Execute the query with the combined conditions
#         query_result = db.query(OffViewServiceGoodsMaster).filter(and_(*search_conditions)).all()

#         # Check if no data is found
#         if not query_result:
#             return []

#         # Fetching details for bundled service_goods_master_ids
#         master_ids = [result.service_goods_master_id for result in query_result if result.is_bundled_service == "yes"]
#         details = db.query(OffViewServiceGoodsDetails).filter(OffViewServiceGoodsDetails.bundled_service_goods_id.in_(master_ids)).all()

#         # Create a dictionary of details
#         details_dict = {}
#         for detail in details:
#             if detail.bundled_service_goods_id not in details_dict:
#                 details_dict[detail.bundled_service_goods_id] = []
#             details_dict[detail.bundled_service_goods_id].append(OffViewServiceGoodsDetailsDisplay(**vars(detail)))

#         # Convert ORM results to Pydantic models and return
#         return [
#             OffViewServiceGoodsMasterDisplay(
#                 **{k: v for k, v in result.__dict__.items() if k != '_sa_instance_state'},
#                 details=details_dict.get(result.service_goods_master_id, None)
#             )
#             for result in query_result
#         ]

#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
#------------------------------------------------------------------------------------------------------------
from time import time
def get_all_service_goods_master(
    db: Session,
    deleted_status: Optional[str] = None,
    name: Optional[str] = None,
    service_goods_type: Union[int, str] = 'ALL', 
    group_id: Union[int, str] = 'ALL',
    sub_group_id: Union[int, str] = 'ALL',
    category_id: Union[int, str] = 'ALL',
    sub_category_id: Union[int, str] = 'ALL'
) -> List[OffViewServiceGoodsMasterDisplay]:
    start_time = time()  # Capture start time

    try:
        search_conditions = []

        if deleted_status == DeletedStatus.DELETED:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'yes')
        elif deleted_status == DeletedStatus.NOT_DELETED:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'no')

        if name:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_name.ilike(f'%{name}%'))
        
        if service_goods_type != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.hsn_sac_class_id == service_goods_type)

        if group_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.group_id == group_id)

        if sub_group_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.sub_group_id == sub_group_id)

        if category_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.category_id == category_id)

        if sub_category_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.sub_category_id == sub_category_id)

        query_start = time()  # Capture query start time
        query_result = db.query(OffViewServiceGoodsMaster).filter(and_(*search_conditions)).all()
        query_duration = time() - query_start  # Capture query duration

        if not query_result:
            return []

        master_ids = [result.service_goods_master_id for result in query_result if result.is_bundled_service == "yes"]
        details = db.query(OffViewServiceGoodsDetails).filter(OffViewServiceGoodsDetails.bundled_service_goods_id.in_(master_ids)).all()

        details_dict = {}
        for detail in details:
            if detail.bundled_service_goods_id not in details_dict:
                details_dict[detail.bundled_service_goods_id] = []
            details_dict[detail.bundled_service_goods_id].append(OffViewServiceGoodsDetailsDisplay(**vars(detail)))

        result = [
            OffViewServiceGoodsMasterDisplay(
                **{k: v for k, v in result.__dict__.items() if k != '_sa_instance_state'},
                details=details_dict.get(result.service_goods_master_id, None)
            )
            for result in query_result
        ]

        end_time = time()  # Capture end time
        total_duration = end_time - start_time
        print(f"Total duration for get_all_service_goods_master function: {total_duration:.2f} seconds")
        print(f"Query duration: {query_duration:.2f} seconds")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


#------------------------------------------------------------------------------------------------------------
def get_all_service_goods_master_test(
    db: Session,
    deleted_status: Optional[str] = None,
    name: Optional[str] = None,
    service_goods_type: Union[int, str] = 'ALL', 
    group_id: Union[int, str] = 'ALL',
    sub_group_id: Union[int, str] = 'ALL',
    category_id: Union[int, str] = 'ALL',
    sub_category_id: Union[int, str] = 'ALL'
) -> List[OffViewServiceGoodsMasterDisplay]:
    start_time = time()

    try:
        search_conditions = []

        

        if sub_category_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.sub_category_id == sub_category_id)
        elif category_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.category_id == category_id)
        elif sub_group_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.sub_group_id == sub_group_id)
        elif group_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.group_id == group_id)
        elif service_goods_type!='ALL':
           search_conditions.append(OffViewServiceGoodsMaster.hsn_sac_class_id == service_goods_type)

        
        if deleted_status == DeletedStatus.DELETED:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'yes')
        elif deleted_status == DeletedStatus.NOT_DELETED:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'no')

        if name:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_name.ilike(f'%{name}%'))
        

        query_start = time()
        query_result = db.query(OffViewServiceGoodsMaster).filter(and_(*search_conditions)).all()
        query_duration = time() - query_start

        if not query_result:
            return []

        master_ids = [result.service_goods_master_id for result in query_result if result.is_bundled_service == "yes"]
        details = db.query(OffViewServiceGoodsDetails).filter(OffViewServiceGoodsDetails.bundled_service_goods_id.in_(master_ids)).all()

        details_dict = {}
        for detail in details:
            if detail.bundled_service_goods_id not in details_dict:
                details_dict[detail.bundled_service_goods_id] = []
            details_dict[detail.bundled_service_goods_id].append(OffViewServiceGoodsDetailsDisplay(**vars(detail)))

        result = [
            OffViewServiceGoodsMasterDisplay(
                **{k: v for k, v in result.__dict__.items() if k != '_sa_instance_state'},
                details=details_dict.get(result.service_goods_master_id, None)
            )
            for result in query_result
        ]

        end_time = time()
        total_duration = end_time - start_time
        print(f"Total duration for get_all_service_goods_master_test function: {total_duration:.2f} seconds")
        print(f"Query duration: {query_duration:.2f} seconds")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


#--------------------------------------------------------------------------------------------------------------

def search_off_document_data_master(
    db: Session, 
    document_type: Optional[str] = None,   
    name: Optional[str] = None
):
    # Perform an explicit join between OffDocumentDataMaster and OffDocumentDataType
    query = db.query(
        OffDocumentDataMaster.id,
        OffDocumentDataMaster.document_data_name,
        OffDocumentDataMaster.has_expiry,
        OffDocumentDataType.document_data_type.label('data_type')  # Add the data_type field
    ).join(
        OffDocumentDataType,
        OffDocumentDataMaster.document_data_type_id == OffDocumentDataType.id
    )
    
    # Filter based on the document_data_type
    if document_type:
        if document_type == "DOCUMENT":
            query = query.filter(OffDocumentDataType.document_data_type == "DOCUMENT")
        elif document_type == "DATA":
            query = query.filter(OffDocumentDataType.document_data_type == "DATA")
    
    # Apply filter based on document name
    if name:
        query = query.filter(OffDocumentDataMaster.document_data_name.ilike(f'%{name}%'))
    
    return query.all()


 

#------------------------------------------------------------------------------------------------------------
def save_service_document_data_master(
    db: Session,
    id: int,
    doc_data: SaveServiceDocumentDataMasterRequest,
    user_id: int
):
    try:
        if id == 0:
            # Create a new master and insert details
            new_master_data = doc_data.Service.model_dump()
            new_master_data.update({
                    "created_by": user_id,
                    "created_on": datetime.now()
                })
            new_master = OffServiceDocumentDataMaster(**new_master_data)
            db.add(new_master)
            db.flush()  # Ensure new_master.id is available for details

            if doc_data.Documents:
                for document_group in doc_data.Documents:
                    document_dict = document_group.model_dump()
                    for doc_type, docs in document_dict.items():
                        if docs:
                            if not isinstance(docs, list):
                                raise HTTPException(status_code=400, detail=f"{doc_type} should be a list")
                            for doc in docs:
                                if not isinstance(doc['details'], list):
                                    raise HTTPException(status_code=400, detail="Details should be a list")
                                for detail in doc['details']:
                                    if detail['id'] != 0:
                                        raise HTTPException(
                                            status_code=400,
                                            detail=f"Cannot insert detail with non-zero ID for new master: {detail['id']}"
                                        )
                                    new_detail_data = detail
                                    new_detail_data.update({
                                        "document_data_category_id": doc['document_data_category_id'],
                                        "service_document_data_master_id": new_master.id,
                                        "is_deleted": 'no'
                                    })
                                    new_detail = OffServiceDocumentDataDetails(**new_detail_data)
                                    db.add(new_detail)

            db.commit()
            return {"success": True, "message": "Saved successfully", "action": "insert"}

        else:
            existing_master = db.query(OffServiceDocumentDataMaster).filter(OffServiceDocumentDataMaster.id == id).first()
            if not existing_master:
                # raise HTTPException(status_code=404, detail="Master record not found")
                return {"message":" master record not found"}
            
            # Save master data
            for key, value in doc_data.Service.model_dump().items():
                setattr(existing_master, key, value)
                existing_master.modified_by = user_id
                existing_master.modified_on = datetime.now()  
            if doc_data.Documents:
                # Mark existing details as deleted
                db.query(OffServiceDocumentDataDetails).filter(
                    OffServiceDocumentDataDetails.service_document_data_master_id == id
                ).update({"is_deleted": "yes"})

                for document_group in doc_data.Documents:
                    document_dict = document_group.model_dump()
                    for doc_type, docs in document_dict.items():
                        if docs:
                            if not isinstance(docs, list):
                                raise HTTPException(status_code=400, detail=f"{doc_type} should be a list")
                            for doc in docs:
                                if not isinstance(doc['details'], list):
                                    raise HTTPException(status_code=400, detail="Details should be a list")
                                for detail in doc['details']:
                                    if detail['id'] == 0:
                                        # Add new detail
                                        new_detail_data = detail
                                        new_detail_data.update({
                                            "document_data_category_id": doc['document_data_category_id'],
                                            "service_document_data_master_id": id,
                                            "is_deleted": 'no'
                                        })
                                        new_detail = OffServiceDocumentDataDetails(**new_detail_data)
                                        db.add(new_detail)
                                    else:
                                        # Update existing detail
                                        existing_detail = db.query(OffServiceDocumentDataDetails).filter(
                                            OffServiceDocumentDataDetails.id == detail['id']
                                        ).first()
                                        if existing_detail:
                                            for key, value in detail.items():
                                                setattr(existing_detail, key, value)
                                            existing_detail.document_data_category_id = doc['document_data_category_id']
                                            existing_detail.service_document_data_master_id = id
                                            existing_detail.is_deleted = 'no'
                                        else:
                                            raise HTTPException(
                                                status_code=400,
                                                detail=f"Detail with ID {detail['id']} does not exist"
                                            )

            db.commit()
            return {"success": True, "message": "Updated successfully", "action": "update"}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))




#------------------------------------------------------------------------------------------------------------


def fetch_available_and_unavailable_dates_and_slots(
    consultant_id: Optional[int],
    consultation_mode_id: Optional[int],
    db: Session,
    check_date: Optional[date] = None,
    service_goods_master_id: Optional[int] = None,
    appointment_id: Optional[int] = None
) -> Dict[str, Any]:
    
    def generate_time_slots(start_time: time, end_time: time, slot_duration: int, consultant_id: int, check_date: date, appointment_id: Optional[int]) -> List[Dict[str, str]]:
        available_slots = []
        current_time = datetime.combine(check_date, start_time)
        end_time = datetime.combine(check_date, end_time)

        while current_time + timedelta(minutes=slot_duration) <= end_time:
            next_time = current_time + timedelta(minutes=slot_duration)

            is_fully_covered = db.query(OffAppointmentVisitMaster).join(
                OffAppointmentVisitMasterView,
                OffAppointmentVisitMaster.id == OffAppointmentVisitMasterView.visit_master_id
            ).filter(
                OffAppointmentVisitMaster.consultant_id == consultant_id,
                OffAppointmentVisitMaster.appointment_date == check_date,
                OffAppointmentVisitMaster.appointment_time_from <= current_time.time(),
                OffAppointmentVisitMaster.appointment_time_to > current_time.time(),
                OffAppointmentVisitMasterView.appointment_status != AppointmentStatusConstants.CANCELED.name,
                OffAppointmentVisitMaster.appointment_master_id != appointment_id
            ).first()

            if not is_fully_covered:
                available_slots.append({
                    'start_time': current_time.strftime("%H:%M"),
                    'end_time': next_time.strftime("%H:%M"),
                })

            current_time = next_time

        return available_slots

    try:
        # Check for service duration based on service_goods_master_id
        if service_goods_master_id:
            service_detail = db.query(OffConsultantServiceDetails).filter(
                OffConsultantServiceDetails.consultant_id == consultant_id,
                OffConsultantServiceDetails.service_goods_master_id == service_goods_master_id,
                OffConsultantServiceDetails.effective_from_date <= check_date,
                or_(
                    OffConsultantServiceDetails.effective_to_date >= check_date,
                    OffConsultantServiceDetails.effective_to_date.is_(None)
                )
            ).first()

            if not service_detail or service_detail.slot_duration_in_minutes is None:
                return {'message': "Booking Closed"}  # No duration found

            slot_duration = service_detail.slot_duration_in_minutes

        if check_date:
            # Check for special schedules (non-normal)
            special_schedule = db.query(OffConsultantSchedule).filter(
                OffConsultantSchedule.consultant_id == consultant_id,
                OffConsultantSchedule.consultation_mode_id == consultation_mode_id,
                OffConsultantSchedule.is_normal_schedule == 'no',
                OffConsultantSchedule.consultation_date == check_date
            ).first()

            if special_schedule:
                available_slots = []
                time_slots = [
                    (special_schedule.morning_start_time, special_schedule.morning_end_time),
                    (special_schedule.afternoon_start_time, special_schedule.afternoon_end_time)
                ]

                for morning_start, morning_end in time_slots:
                    if morning_start and morning_end:
                        available_slots.extend(generate_time_slots(morning_start, morning_end, slot_duration, consultant_id, check_date, appointment_id))

                if available_slots:
                    return {'available_slots': available_slots}
                else:
                    return {'message': "No available slots for the specified date."}

            # If no special schedule, check for normal schedules
            normal_schedule = db.query(OffConsultantSchedule).filter(
                OffConsultantSchedule.consultant_id == consultant_id,
                OffConsultantSchedule.consultation_mode_id == consultation_mode_id,
                OffConsultantSchedule.is_normal_schedule == 'yes',
                OffConsultantSchedule.effective_from_date <= check_date,
                or_(
                    OffConsultantSchedule.effective_to_date.is_(None),
                    OffConsultantSchedule.effective_to_date >= check_date
                ),
                OffConsultantSchedule.day_of_week_id == (check_date.weekday() + 1) % 7 + 1
            ).first()

            if normal_schedule:
                # Check for overlapping non-normal schedules
                overlapping_schedule = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.consultation_mode_id == consultation_mode_id,
                    OffConsultantSchedule.is_normal_schedule == 'no',
                    OffConsultantSchedule.consultation_date == check_date,
                    OffConsultantSchedule.day_of_week_id == (check_date.weekday() + 1) % 7 + 1
                ).all()

                if overlapping_schedule:
                    return {'available_slots': []}

                # Generate available slots based on normal schedules
                available_slots = []
                time_slots = [
                    (normal_schedule.morning_start_time, normal_schedule.morning_end_time),
                    (normal_schedule.afternoon_start_time, normal_schedule.afternoon_end_time)
                ]

                for morning_start, morning_end in time_slots:
                    if morning_start and morning_end:
                        available_slots.extend(generate_time_slots(morning_start, morning_end, slot_duration, consultant_id, check_date, appointment_id))

                return {'available_slots': available_slots} if available_slots else {'message': "No available slots for the specified date."}

            # If neither normal nor special schedule found
            return {'message': "No schedule available for the given date."}

        else:
            # Handle date range logic for fetching available and unavailable dates
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=30)

            available_dates = set()
            unavailable_dates = set()

            current_date = start_date
            while current_date <= end_date:
                # Check for special schedules first
                special_schedule = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.consultation_mode_id == consultation_mode_id,
                    OffConsultantSchedule.is_normal_schedule == 'no',
                    OffConsultantSchedule.consultation_date == current_date
                ).first()

                if special_schedule:
                    available_dates.add(current_date)
                else:
                    # Check for normal schedules
                    normal_schedule = db.query(OffConsultantSchedule).filter(
                        OffConsultantSchedule.consultant_id == consultant_id,
                        OffConsultantSchedule.consultation_mode_id == consultation_mode_id,
                        OffConsultantSchedule.is_normal_schedule == 'yes',
                        OffConsultantSchedule.effective_from_date <= current_date,
                        or_(
                            OffConsultantSchedule.effective_to_date.is_(None),
                            OffConsultantSchedule.effective_to_date >= current_date
                        ),
                        OffConsultantSchedule.day_of_week_id == (current_date.weekday() + 1) % 7 + 1
                    ).first()

                    if normal_schedule:
                        overlapping_schedule = db.query(OffConsultantSchedule).filter(
                            OffConsultantSchedule.consultant_id == consultant_id,
                            OffConsultantSchedule.consultation_mode_id == consultation_mode_id,
                            OffConsultantSchedule.is_normal_schedule == 'no',
                            OffConsultantSchedule.consultation_date == current_date,
                            OffConsultantSchedule.day_of_week_id == (current_date.weekday() + 1) % 7 + 1
                        ).all()

                        if overlapping_schedule:
                            unavailable_dates.add(current_date)
                        else:
                            available_dates.add(current_date)
                    else:
                        unavailable_dates.add(current_date)

                current_date += timedelta(days=1)

            # Ensure that available and unavailable dates are non-null, returning message if none
            if not available_dates and not unavailable_dates:
                return {'message': "No available or unavailable dates in the specified range."}

            # Handle special date conflicts with other consultation modes
            for available_date in available_dates.copy():
                current_special_schedule = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.is_normal_schedule == 'no',
                    OffConsultantSchedule.consultation_date == available_date,
                    OffConsultantSchedule.consultation_mode_id == consultation_mode_id
                ).first()
                other_special_schedules = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.is_normal_schedule == 'no',
                    OffConsultantSchedule.consultation_date == available_date
                ).filter(OffConsultantSchedule.consultation_mode_id != consultation_mode_id).all()
                if current_special_schedule and other_special_schedules:
                         # If both modes have special schedules, keep the date as available
                  continue
                if other_special_schedules:
                    available_dates.remove(available_date)
                    unavailable_dates.add(available_date)
            
            sorted_available_dates = sorted(list(available_dates))
            sorted_unavailable_dates = sorted(list(unavailable_dates))

            return {
                'available_dates': sorted_available_dates,
                'unavailable_dates': sorted_unavailable_dates
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error occurred: {str(e)}")

#------------------------------------------------------------------------------------------------------------

def save_off_document_master(
    db: Session,
    id: int,
    data: OffDocumentDataMasterBase,
    type: str
):
    
    try:
        # Retrieve the document type record based on the provided type
        document_type_record = db.query(OffDocumentDataType).filter(
            OffDocumentDataType.document_data_type == type
        ).first()

        if not document_type_record:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        document_data_type_id = document_type_record.id
        
        if id == 0:
            document_master = OffDocumentDataMaster(
                **data.model_dump(),
                document_data_type_id=document_data_type_id
            )
            db.add(document_master)
            db.commit()
            db.refresh(document_master)
            return {"success": True, "message": "Saved successfully"}
        
        else:
            document = db.query(OffDocumentDataMaster).filter(OffDocumentDataMaster.id == id).first()
            if not document:
                # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with id {id} not found")
                return {"success": True, "message": "Document with the given ID was not found"}

            # Update the document type if needed
            if document.document_data_type_id != document_data_type_id:
                document.document_data_type_id = document_data_type_id
            
            # Update other fields
            for key, value in data.model_dump().items():
                setattr(document, key, value)
            
            db.commit()
            db.refresh(document)
            return {"success": True, "message": "Updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



#-----------Aparna----------------------------------------------------------------------------------------------

from sqlalchemy.sql import text
# def get_consultants(db: Session):
#     sql = text("""
#     SELECT 
  
#         em.employee_id,
#         em.first_name,
#         em.middle_name,
#         em.last_name
#     FROM 
#         employee_master em
#     INNER JOIN 
#         employee_employement_details eed
#     ON 
#         em.employee_id = eed.employee_id
#     WHERE 
#         eed.is_consultant = 'yes'
#         AND eed.effective_from_date <= CURDATE()
#         AND eed.effective_to_date IS NULL OR eed.effective_to_date >= CURDATE()
        
#         AND em.is_deleted = 'no'
#         AND eed.is_deleted = 'no';
#     """)
#     result = db.execute(sql)
#     return result.fetchall()

def get_consultants(db: Session):
    sql = text("""
    SELECT 
  
        em.employee_id,
        em.first_name,
        em.middle_name,
        em.last_name
    FROM 
        employee_master em
    INNER JOIN 
        employee_employment_details eed
    ON 
        em.employee_id = eed.employee_id
    WHERE 
        eed.is_consultant = 'yes'
        AND eed.effective_from_date <= CURDATE()
        AND eed.effective_to_date IS NULL OR eed.effective_to_date >= CURDATE()
        
        AND em.is_deleted = 'no'
        AND eed.is_deleted = 'no'
               ORDER BY 
        em.first_name, em.middle_name, em.last_name;
    """)
    result = db.execute(sql)
    return result.fetchall()


#------------------------------------------------------------------------------------------------------------



def get_all_non_consultant_employees(db: Session):
    query = (
        db.query(EmployeeMaster)
        .join(EmployeeEmploymentDetails, EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id)
        .filter(
            EmployeeEmploymentDetails.is_consultant == 'no',
            EmployeeMaster.is_deleted == 'no',
            EmployeeEmploymentDetails.is_deleted == 'no'
        )
    )
    return query.all()


#------------------------------------------------------------------------------------------------------------

def get_all_non_consultant_employees(db: Session):
    query = (
        db.query(EmployeeMaster)
        .join(EmployeeEmploymentDetails, EmployeeMaster.employee_id == EmployeeEmploymentDetails.employee_id)
        .filter(
            EmployeeEmploymentDetails.is_consultant == 'no',
            EmployeeMaster.is_deleted == 'no',
            EmployeeEmploymentDetails.is_deleted == 'no'
        )
    )
    return query.all()

#---------------------------------------------------------------------------------------------------------------
# def get_all_service(db: Session) -> List[OffViewConsultantDetails]:

#     return db.query(OffViewConsultantDetails).all()


def get_all_service(db: Session) -> List[Dict[str, any]]:
    """
    Fetch all services from the off_service_goods_master table.
    """
    services = db.query(OffServiceGoodsMaster).filter(
        and_(
            OffServiceGoodsMaster.is_deleted == 'no',
            OffServiceGoodsMaster.has_consultation == 'yes'
        )
    ).all()
    
    services_data = [{"id": service.id, "name": service.service_goods_name} for service in services]
    return services_data
#---------------------------------------------------------------------------------------------------------------



# def get_consultants_for_service(db: Session, service_id: int) -> List[OffViewConsultantServiceDetails]:
#     # Query the database to get consultants for the given service_id
#     consultants = db.query(OffViewConsultantServiceDetails).filter(OffViewConsultantServiceDetails.service_goods_master_id == service_id).all()
#     return consultants

def get_consultants_for_service(db: Session, service_id: int) -> List[OffViewConsultantServiceDetails]:
    """
    Query the database to get consultants for the given service_id
    where `consultant_details_effective_to_date` is either NULL or greater than the current date.
    """
    # Query the database with the condition on `consultant_details_effective_to_date`

    consultants = (
        db.query(OffViewConsultantServiceDetails)
        .filter(
            OffViewConsultantServiceDetails.service_goods_master_id == service_id,
            or_(
                OffViewConsultantServiceDetails.consultant_details_effective_to_date.is_(None),
                OffViewConsultantServiceDetails.consultant_details_effective_to_date > func.now()
            )
        )
        .all()
    )
    
    return consultants

#---------------------------------------------------------------------------------------------------------------
# def get_all_services_by_consultant_id(db: Session, consultant_id: int) -> List[OffViewConsultantServiceDetails]:
    
#     services = db.query(OffViewConsultantServiceDetails).filter(OffViewConsultantServiceDetails.consultant_id == consultant_id).all()
   
#     return services

def get_all_services_by_consultant_id(db: Session, consultant_id: int) -> List[OffViewConsultantServiceDetails]:
    services = db.query(OffViewConsultantServiceDetails).filter(
        OffViewConsultantServiceDetails.consultant_id == consultant_id,
        or_(
            OffViewConsultantServiceDetails.consultant_details_effective_to_date.is_(None),
            OffViewConsultantServiceDetails.consultant_details_effective_to_date > func.now()
        )
    ).all()

    return services

#---------------APARNA------------------------------------------------------------------------------------------
def get_all_services(db: Session) -> List[OffViewServiceGoodsPriceMaster]:
    """
    Fetch all services or goods from the off_view_service_goods_price_master table.
    """
    return db.query(OffViewServiceGoodsPriceMaster).all()
#------------------------------------------------------------------------------------------------------------
def get_services_filtered(db: Session, 
                          service_type: Optional[str] = None, 
                          search: Optional[str] = None) -> List[OffViewServiceGoodsPriceMaster]:
    """
    Fetch services or goods filtered by service type and search term.
    """
    query = db.query(OffViewServiceGoodsPriceMaster)
    
    # Apply filters based on provided query parameters
    if service_type == "GOODS":
        query = query.filter(OffViewServiceGoodsPriceMaster.hsn_sac_class_id == 1)
    elif service_type == "SERVICE":
        query = query.filter(OffViewServiceGoodsPriceMaster.hsn_sac_class_id == 2)
    
    if search:
        query = query.filter(OffViewServiceGoodsPriceMaster.service_goods_name.ilike(f"%{search}%"))
    
    return query.all()

#---------------------------------------------------------------------------------------------------------------



def get_service_data(service_id: int, rate_status: Optional[str], db: Session) -> List[ServiceModelSchema]:
    query_date = datetime.now().date()

    query = text("""
        WITH ranked_prices AS (
            SELECT
                a.id AS constitution_id,
                a.business_constitution_name,
                a.business_constitution_code,
                b.id AS service_goods_master_id,
                COALESCE(c.id, 0) AS service_goods_price_master_id,
                b.service_goods_name,
                COALESCE(c.service_charge, 0) AS service_charge,
                COALESCE(c.govt_agency_fee, 0) AS govt_agency_fee,
                COALESCE(c.stamp_duty, 0) AS stamp_duty,
                COALESCE(c.stamp_fee, 0) AS stamp_fee,
                COALESCE(c.id, 0) AS price_master_id,
                c.effective_from_date AS effective_from_date,
                c.effective_to_date AS effective_to_date,
                CASE
                    WHEN c.effective_from_date <= :query_date AND (c.effective_to_date IS NULL OR c.effective_to_date >= :query_date) THEN 'CURRENT'
                    WHEN c.effective_from_date > :query_date THEN 'UPCOMING'
                    ELSE 'PREVIOUS'
                END AS rate_status,
                ROW_NUMBER() OVER (PARTITION BY a.id ORDER BY 
                    CASE 
                        WHEN c.effective_from_date <= :query_date AND (c.effective_to_date IS NULL OR c.effective_to_date >= :query_date) THEN 1
                        WHEN c.effective_from_date > :query_date THEN 2
                        ELSE 3 
                    END, c.effective_from_date DESC) AS rn
            FROM
                app_business_constitution AS a
            LEFT OUTER JOIN
                off_service_goods_master AS b ON TRUE
            LEFT OUTER JOIN
                off_service_goods_price_master AS c ON b.id = c.service_goods_master_id 
                                                     AND a.id = c.constitution_id
            WHERE
                b.id = :service_id
        )
        SELECT * FROM ranked_prices
        WHERE rn = 1 
          AND (:rate_status IS NULL 
              OR (rate_status = 'CURRENT' AND effective_from_date <= :query_date AND (effective_to_date IS NULL OR effective_to_date >= :query_date))
              OR (rate_status = 'UPCOMING' AND effective_from_date > :query_date)
              OR (rate_status = 'PREVIOUS' AND effective_to_date IS NOT NULL AND effective_to_date < :query_date))
        ORDER BY constitution_id;
    """)

    query_result = db.execute(query, {"service_id": service_id, "query_date": query_date, "rate_status": rate_status}).fetchall()

    service_data = [
        ServiceModelSchema(
            constitution_id=row.constitution_id,
            business_constitution_name=row.business_constitution_name,
            service_goods_master_id=row.service_goods_master_id,
            service_goods_price_master_id=row.service_goods_price_master_id,
            service_name=row.service_goods_name,
            business_constitution_code=row.business_constitution_code,
            service_charge=row.service_charge,
            govt_agency_fee=row.govt_agency_fee,
            stamp_duty=row.stamp_duty,
            stamp_fee=row.stamp_fee,
            effective_from_date=row.effective_from_date,
            effective_to_date=row.effective_to_date,
            price_master_id=row.price_master_id,
            rate_status=row.rate_status
        ) for row in query_result
    ]
    
    return service_data


#---------------------------------------------------------------------------------------------------------------
def get_bundled_service_data(service_id: int, db: Session):
    query = """
    WITH recent_prices AS (
        SELECT
            a.id AS constitution_id,
            a.business_constitution_name,
            a.business_constitution_code,
            b.id AS service_goods_master_id,
            COALESCE(c.id, 0) AS service_goods_price_master_id,
            b.service_goods_name,
            COALESCE(c.service_charge, 0) AS service_charge,
            COALESCE(c.govt_agency_fee, 0) AS govt_agency_fee,
            COALESCE(c.stamp_duty, 0) AS stamp_duty,
            COALESCE(c.stamp_fee, 0) AS stamp_fee,
            COALESCE(c.id, 0) AS price_master_id,
            c.effective_from_date AS effective_from_date,
            c.effective_to_date AS effective_to_date,
            ROW_NUMBER() OVER (PARTITION BY a.id, b.id ORDER BY c.effective_from_date DESC) AS rn
        FROM
            app_business_constitution AS a
        LEFT OUTER JOIN
            off_service_goods_master AS b ON TRUE
        LEFT OUTER JOIN
            off_service_goods_price_master AS c ON b.id = c.service_goods_master_id 
                                                 AND a.id = c.constitution_id
        WHERE
            b.id = :service_id
            AND b.is_bundled_service = 'yes'
    ),
    duplicate_constitutions AS (
        SELECT
            rp.*,
            ROW_NUMBER() OVER (ORDER BY rp.constitution_id, rp.service_goods_master_id) * 2 - 1 AS row_id
        FROM
            recent_prices rp
        WHERE
            rp.rn = 1
        UNION ALL
        SELECT
            rp.*,
            ROW_NUMBER() OVER (ORDER BY rp.constitution_id, rp.service_goods_master_id) * 2 AS row_id
        FROM
            recent_prices rp
        WHERE
            rp.rn = 1
    )
    SELECT
        row_id,
        constitution_id,
        business_constitution_name,
        business_constitution_code,
        service_goods_master_id,
        service_goods_price_master_id,
        service_goods_name,
        service_charge,
        govt_agency_fee,
        stamp_duty,
        stamp_fee,
        price_master_id,
        effective_from_date,
        effective_to_date
    FROM
        duplicate_constitutions
    ORDER BY
        row_id;
    """

    result = db.execute(text(query), {"service_id": service_id})
    rows = result.fetchall()

    # Convert rows to list of dicts manually
    columns = result.keys()  # Get the column names
    service_data = [dict(zip(columns, row)) for row in rows]
    
    return service_data



#----------------------------------------------------------------------------------------------------------
def get_price_history(service_id: int, db: Session) -> List[ServiceModel]:
    query_result = db.execute("""
        SELECT
            a.id AS constitution_id,
            a.business_constitution_name,
            b.service_goods_name,
            c.service_charge,
            c.govt_agency_fee,
            c.stamp_duty,
            c.stamp_fee,
            c.effective_from_date AS price_master_effective_from_date,
            c.effective_to_date AS price_master_effective_to_date
        FROM
            app_business_constitution AS a
        LEFT OUTER JOIN
            off_service_goods_price_master AS c ON a.id = c.constitution_id
        LEFT OUTER JOIN
            off_service_goods_master AS b ON b.id = c.service_goods_master_id
        WHERE
            b.id = :service_id
        ORDER BY
            a.id, c.effective_from_date DESC;
    """, {"service_id": service_id}).fetchall()

    if not query_result:
        return []

    service_name = query_result[0].service_goods_name
    service_models = []
    for row in query_result:
        price_history = PriceHistoryModel(
            constitution_id=row.constitution_id,
            business_constitution_name=row.business_constitution_name,
            service_charge=row.service_charge,
            govt_agency_fee=row.govt_agency_fee,
            stamp_duty=row.stamp_duty,
            stamp_fee=row.stamp_fee,
            effective_from_date=row.price_master_effective_from_date,
            effective_to_date=row.price_master_effective_to_date
        )
        service_models.append(ServiceModel(
            id=row.constitution_id,  # Assuming constitution_id is used as id
            service_name=service_name,
            constitution_id=row.constitution_id,
            business_constitution_name=row.business_constitution_name,
            business_constitution_code="",  # You might need to provide this value
            price_history=[price_history]
        ))
    return service_models
   
#--------------------------------------------------------------------------------------------------------------   


# def save_price_data(data: PriceData, service_goods_master_id: int, user_id: int, db: Session):
#     try:
#         current_date = datetime.now().date()
#         # Fetch the existing record if it exists
#         existing_record = db.query(OffServiceGoodsPriceMaster).filter(
#             OffServiceGoodsPriceMaster.id == data.id
#         ).first()

#         if data.id == 0:
#             # Insert new record
#             new_record = OffServiceGoodsPriceMaster(
#                 service_goods_master_id=service_goods_master_id,
#                 constitution_id=data.constitution_id,
#                 service_charge=data.service_charge,
#                 govt_agency_fee=data.govt_agency_fee,
#                 stamp_duty=data.stamp_duty,
#                 stamp_fee=data.stamp_fee,
#                 effective_from_date=data.effective_from_date,
#                 effective_to_date=data.effective_to_date if data.effective_to_date else None,
#                 # effective_to_date=data.effective_to_date,
#                 effective_to_date=None,
#                 created_by=user_id,
#                 created_on=datetime.now()
#             )
#             db.add(new_record)
        
#         elif existing_record:
#             if data.effective_from_date > current_date:
#                 # Update effective_to_date of the existing record
#                 if existing_record.effective_to_date is None or existing_record.effective_to_date >= current_date:
#                     existing_record.effective_to_date = data.effective_from_date - timedelta(days=1)
#                     db.add(existing_record)

#                 # Insert new record
#                 new_record = OffServiceGoodsPriceMaster(
#                     service_goods_master_id=service_goods_master_id,
#                     constitution_id=data.constitution_id,
#                     service_charge=data.service_charge,
#                     govt_agency_fee=data.govt_agency_fee,
#                     stamp_duty=data.stamp_duty,
#                     stamp_fee=data.stamp_fee,
#                     effective_from_date=data.effective_from_date,
#                     # effective_to_date=None,
#                     effective_to_date=data.effective_to_date if data.effective_to_date else None,
#                     created_by=user_id,
#                     created_on=datetime.now()
#                 )
#                 db.add(new_record)
            
#             else:
#                 # Update existing record with new data
#                 existing_record.service_charge = data.service_charge
#                 existing_record.govt_agency_fee = data.govt_agency_fee
#                 existing_record.stamp_duty = data.stamp_duty
#                 existing_record.stamp_fee = data.stamp_fee
#                 existing_record.effective_from_date = data.effective_from_date
#                 existing_record.effective_to_date = data.effective_to_date if data.effective_to_date else existing_record.effective_to_date
#                 db.add(existing_record)

#         db.commit()

#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Duplicate entry error occurred. Please check the data and try again.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))

#------------------------------------------------------------------------------------------------------------
def save_price_data(data: PriceData, service_goods_master_id: int, user_id: int, db: Session):
    try:
        current_date = datetime.now().date()
        # Fetch the existing record if it exists
        existing_record = db.query(OffServiceGoodsPriceMaster).filter(
            OffServiceGoodsPriceMaster.id == data.id
        ).first()

        if data.id == 0:
            # Insert new record
            new_record = OffServiceGoodsPriceMaster(
                service_goods_master_id=service_goods_master_id,
                constitution_id=data.constitution_id,
                service_charge=data.service_charge,
                govt_agency_fee=data.govt_agency_fee,
                stamp_duty=data.stamp_duty,
                stamp_fee=data.stamp_fee,
                effective_from_date=data.effective_from_date,
                effective_to_date=data.effective_to_date if data.effective_to_date else None,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_record)
        
        elif existing_record:
            if data.effective_from_date > current_date:
                # Update effective_to_date of the existing record
                if existing_record.effective_to_date is None or existing_record.effective_to_date >= current_date:
                    existing_record.effective_to_date = data.effective_from_date - timedelta(days=1)
                    db.add(existing_record)

                # Insert new record
                new_record = OffServiceGoodsPriceMaster(
                    service_goods_master_id=service_goods_master_id,
                    constitution_id=data.constitution_id,
                    service_charge=data.service_charge,
                    govt_agency_fee=data.govt_agency_fee,
                    stamp_duty=data.stamp_duty,
                    stamp_fee=data.stamp_fee,
                    effective_from_date=data.effective_from_date,
                    effective_to_date=data.effective_to_date if data.effective_to_date else None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                db.add(new_record)
            
            else:
                # Update existing record with new data
                existing_record.constitution_id = data.constitution_id
                existing_record.service_charge = data.service_charge
                existing_record.govt_agency_fee = data.govt_agency_fee
                existing_record.stamp_duty = data.stamp_duty
                existing_record.stamp_fee = data.stamp_fee
                existing_record.effective_from_date = data.effective_from_date
                existing_record.effective_to_date = data.effective_to_date if data.effective_to_date else existing_record.effective_to_date
                db.add(existing_record)

        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate entry error occurred. Please check the data and try again.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

#------------------------------------------------------------------------------------------------------------

# def get_service_documents_data_details(db: Session, service_document_data_master_id: int, document_category: Optional[str] = None) -> List[OffViewServiceDocumentsDataDetailsDocCategory]:
#     try:
#         # Query to fetch all records from master table for the given service_id
#         master_queries = db.query(OffViewServiceDocumentsDataMaster). \
#             filter(OffViewServiceDocumentsDataMaster.service_document_data_master_id == service_document_data_master_id). \
#             all()

#         if not master_queries:
#             return []  # Return empty list if no master record found for the given service_id

#         # Collect all service_document_data_master_id
#         service_document_data_master_ids = [master.service_document_data_master_id for master in master_queries]

#         # Query to fetch details based on the collected service_document_data_master_ids and optional document_category
#         details_query = db.query(OffViewServiceDocumentsDataDetails). \
#             filter(OffViewServiceDocumentsDataDetails.service_document_data_master_id.in_(service_document_data_master_ids))

#         if document_category:
#             details_query = details_query.filter(
#                 OffViewServiceDocumentsDataDetails.document_data_category_category_name == document_category)

#         results = details_query.all()
        
#         return results

#     except Exception as e:
#         # logging.error(f"Error fetching service documents details: {e}")
#         raise HTTPException(status_code=500, detail=f"Error fetching service documents details: {e}")


def get_service_documents_data_details(
    db: Session,
    service_document_data_master_id: Optional[int] = None,
    service_id: Optional[int] = None,
    constitution_id: Optional[int] = None,
    document_category: Optional[str] = "ALL",
    nature_of_possession_id: Optional[int] = None,
) -> List[OffViewServiceDocumentsDataDetails]:
    try:

        query = db.query(OffViewServiceDocumentsDataDetails).join(
            OffServiceDocumentDataMaster,
            OffViewServiceDocumentsDataDetails.service_document_data_master_id == OffServiceDocumentDataMaster.id
        ).filter(
            OffViewServiceDocumentsDataDetails.service_document_data_details_is_deleted == 'no'  
        )


        
        # Conditional filters based on provided arguments
        if service_document_data_master_id is not None:
            query = query.filter(
                OffServiceDocumentDataMaster.id == service_document_data_master_id
            )

        if constitution_id is not None:
            query = query.filter(OffServiceDocumentDataMaster.constitution_id == constitution_id)

        if service_id is not None:
            query = query.filter(OffServiceDocumentDataMaster.service_goods_master_id == service_id)

        if document_category !='ALL':
            query = query.filter(
                OffViewServiceDocumentsDataDetails.document_data_category_category_name == document_category
            )

        if nature_of_possession_id is not None and document_category == 'PRINCIPAL PLACE DOC':
            query = query.filter(
                OffViewServiceDocumentsDataDetails.nature_of_possession_id == nature_of_possession_id
            )

        # Return the filtered or non-filtered result set
        return query.all()

    except Exception as e:
        raise Exception(f"Error fetching service documents details: {e}")


# def get_service_documents_data_details(
#     db: Session,
#     service_document_data_master_id: Optional[int] = None,
#     service_id: Optional[int] = None,
#     constitution_id: Optional[int] = None,
#     document_category: Optional[str] = "ALL",
#     nature_of_possession_id: Optional[int] = None,
# ) -> List[OffViewServiceDocumentsDataDetails]:
#     try:
#         # query = db.query(OffViewServiceDocumentsDataDetails).join(
#         #     OffServiceDocumentDataMaster,
#         #     OffViewServiceDocumentsDataDetails.service_document_data_master_id == OffServiceDocumentDataMaster.id
#         # ).filter(
#         #     OffViewServiceDocumentsDataDetails.service_document_data_details_is_deleted == 'no'
#         # )

#         query = db.query(OffViewServiceDocumentsDataDetails).join(
#             OffServiceDocumentDataMaster,
#             OffViewServiceDocumentsDataDetails.service_document_data_master_id == OffServiceDocumentDataMaster.id
#         )

#         # Add the is_deleted filter
#         query = query.filter(
#             OffViewServiceDocumentsDataDetails.service_document_data_details_is_deleted == 'no'  # Correct field for is_deleted check
#         )


#         # Conditional filters based on provided arguments
#         if service_document_data_master_id is not None:
#             query = query.filter(
#                 OffServiceDocumentDataMaster.id == service_document_data_master_id
#             )
            
#         if constitution_id is not None:
#             query = query.filter(OffServiceDocumentDataMaster.constitution_id == constitution_id)

#         if service_id is not None:
#             query = query.filter(OffServiceDocumentDataMaster.service_goods_master_id == service_id)

#         if document_category != 'ALL':
#             query = query.filter(
#                 OffViewServiceDocumentsDataDetails.document_data_category_category_name == document_category
#             )

#         if nature_of_possession_id is not None and document_category == 'PRINCIPAL PLACE DOC':
#             query = query.filter(
#                 OffViewServiceDocumentsDataDetails.nature_of_possession_id == nature_of_possession_id
#             )

#         # Print the SQL query
#         print(str(query.statement))

#         # Return the filtered or non-filtered result set
#         return query.all()

#     except Exception as e:
#         raise Exception(f"Error fetching service documents details: {e}")



#---------------------------------------------------------------------------------------------
def get_service_documents_list_by_group_category(
    db: Session,
    group_id: Optional[int] = None,
    sub_group_id: Optional[int] = None,
    category_id: Optional[int] = None
) -> Union[List[ServiceDocumentsList_Group], List[Service_Group]]:
 
    try:
        results = []
        
        if group_id is None and sub_group_id is None and category_id is None or group_id == 0:  # If all are None or group_id is 0
            return _get_all_groups(db)  
         
        if group_id is not None:
            group = db.query(OffServiceGoodsGroup).filter_by(id=group_id, is_deleted='no').first()
            if not group:
                return []

            sub_groups = db.query(OffServiceGoodsSubGroup).filter_by(group_id=group_id, is_deleted='no').all()
            sub_group_ids = [SubGroup(id=sub_group.id, sub_group_name=sub_group.sub_group_name or "") for sub_group in sub_groups]

            category_ids = []
            for sub_group in sub_groups:
                categories = db.query(OffServiceGoodsCategory).filter_by(sub_group_id=sub_group.id, is_deleted='no').all()
                category_ids.extend([Category(id=category.id, category_name=category.category_name or "") for category in categories])

            sub_category_ids = []
            for category in category_ids:
                sub_categories = db.query(OffServiceGoodsSubCategory).filter_by(category_id=category.id, is_deleted='no').all()
                sub_category_ids.extend([SubCategory(id=sub_category.id, sub_category_name=sub_category.sub_category_name or "") for sub_category in sub_categories])

            results.append(ServiceDocumentsList_Group(
                group=Service_Group(id=group.id, group_name=group.group_name or ""),
                sub_group=sub_group_ids,
                category=category_ids,
                sub_category=sub_category_ids
            ))

        if sub_group_id is not None:
            sub_group = db.query(OffServiceGoodsSubGroup).filter_by(id=sub_group_id, is_deleted='no').first()
            if not sub_group:
                return []

            categories = db.query(OffServiceGoodsCategory).filter_by(sub_group_id=sub_group_id, is_deleted='no').all()
            category_ids = [Category(id=category.id, category_name=category.category_name or "") for category in categories]

            sub_category_ids = []
            for category in categories:
                sub_categories = db.query(OffServiceGoodsSubCategory).filter_by(category_id=category.id, is_deleted='no').all()
                sub_category_ids.extend([SubCategory(id=sub_category.id, sub_category_name=sub_category.sub_category_name or "") for sub_category in sub_categories])

            results.append(ServiceDocumentsList_Group(
                # group=None,
                sub_group=[SubGroup(id=sub_group.id, sub_group_name=sub_group.sub_group_name or "")],
                category=category_ids,
                sub_category=sub_category_ids
            ))

        if category_id is not None:
            category = db.query(OffServiceGoodsCategory).filter_by(id=category_id, is_deleted='no').first()
            if not category:
                return []

            sub_categories = db.query(OffServiceGoodsSubCategory).filter_by(category_id=category.id, is_deleted='no').all()
            sub_category_ids = [SubCategory(id=sub_category.id, sub_category_name=sub_category.sub_category_name or "") for sub_category in sub_categories]

            results.append(ServiceDocumentsList_Group(
                # group=None,
                # sub_group=None,
                 category=[Category(id=category.id, category_name=category.category_name or "")],
                 sub_category=sub_category_ids
            ))

        return results

    except Exception as e:
        raise e
        
#------------------------------------------------------------------------------------------------------------

def _get_all_groups(db: Session) -> List[Service_Group]:
    groups = db.query(OffServiceGoodsGroup).filter_by(is_deleted='no').all()
    return [Service_Group(id=group.id, group_name=group.group_name or "") for group in groups]


#------------------------------------------------------------------------------------------------------------

def save_consultant_service_details_db(
    data: ConsultantService,
    consultant_id: Optional[int],
    service_id: Optional[int],
    user_id: int,
    action_type: RecordActionType,
    db: Session,
    id: Optional[int] = None
):
    try:
        if action_type == RecordActionType.UPDATE_AND_INSERT:
            if consultant_id is None or service_id is None:
                raise ValueError("consultant_id and service_id are required for UPDATE_AND_INSERT")
            
            # Check if there is an existing active record
            existing_record = db.query(OffConsultantServiceDetails).filter(
                OffConsultantServiceDetails.consultant_id == consultant_id,
                OffConsultantServiceDetails.service_goods_master_id == service_id,
                OffConsultantServiceDetails.effective_to_date.is_(None)
            ).first()
            
            if existing_record:
                # Update existing record's effective_to_date if it's None
                existing_record.effective_to_date = data.effective_from_date - timedelta(days=1)
                existing_record.modified_by = user_id
                existing_record.modified_on = datetime.now()
                db.commit()
            
                # Insert a new record
            new_record_data = {
                    "service_goods_master_id": service_id,
                    "consultation_fee": data.consultation_fee,
                    "slot_duration_in_minutes": data.slot_duration_in_minutes,
                    "effective_from_date": data.effective_from_date,
                    "effective_to_date": None, 
                    "consultant_id": consultant_id,
                    "created_by": user_id,
                    "created_on": datetime.now()
                }

            new_record = OffConsultantServiceDetails(**new_record_data)
            db.add(new_record)
            db.commit()
        
        elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
            # Find the existing record by id
            existing_record = db.query(OffConsultantServiceDetails).filter(OffConsultantServiceDetails.id == id).first()
            
            if existing_record:
                # Log the existing record before update
                print(f"Existing record before update: {existing_record.__dict__}")
                
                # Update existing record with new data
                for key, value in data.model_dump().items():
                    if value is not None:
                        setattr(existing_record, key, value)
                
                existing_record.modified_by = user_id
                existing_record.modified_on = datetime.now()
                db.commit()

                # Log the existing record after update
                print(f"Existing record after update: {existing_record.__dict__}")

            else:
                raise ValueError(f"Record with ID {id} not found.")
        
        else:
            raise ValueError("Invalid action type or ID provided.")
    
    except Exception as e:
        # db.rollback()
        raise e




#------------------------------------------------------------------------------------------------------------
# from datetime import timedelta
# def save_consultant_schedule(
#     schedule_data: ConsultantScheduleCreate,
#     consultant_id: Optional[int],
#     user_id: int,
#     id: Optional[int],
#     action_type: RecordActionType,
#     db: Session
# ):
#     try:
#         schedule_dict = schedule_data.model_dump()

#         if schedule_data.is_normal_schedule == "no":
#             if not schedule_data.consultation_date:
#                 raise ValueError("For 'is_normal_schedule' no, 'consultation_date' must be provided.")
            
#             # Remove effective_from_date if present
#             schedule_dict.pop("effective_from_date", None)
            
#             # Assign day_of_week_id using SQL query
#             day_of_week_query = f"SELECT DAYOFWEEK('{schedule_data.consultation_date}')"
           
#             print(" day_of_week_query", day_of_week_query)
#             day_of_week_id = db.execute(day_of_week_query).fetchone()[0]
#             print(" Day of Week ID", day_of_week_id)
            
            
#             # Assign day_of_week_id to schedule_dict
#             schedule_dict['day_of_week_id'] = day_of_week_id
        
#         if action_type == RecordActionType.UPDATE_AND_INSERT:
#             if consultant_id is None:
#                 raise ValueError("consultant_id is required for UPDATE_AND_INSERT")
               
            
#             schedule_dict['consultant_id'] = consultant_id

#             # Query existing active schedule
#             existing_schedule = db.query(OffConsultantSchedule).filter(
#                 OffConsultantSchedule.consultant_id == consultant_id,
#                 OffConsultantSchedule.day_of_week_id == schedule_dict['day_of_week_id'],
#                 OffConsultantSchedule.consultation_mode_id == schedule_dict['consultation_mode_id'],
#                 OffConsultantSchedule.effective_to_date.is_(None)
#             ).first()
#             print("Ecccccccccc",existing_schedule)

#             if existing_schedule:
#                 # print("haiii")
#                 # Calculate new effective_to_date
                

#                 new_effective_to_date = schedule_dict['effective_from_date'] - timedelta(days=1)

#                 # Update existing schedule
#                 existing_schedule.effective_to_date = new_effective_to_date
#                 existing_schedule.modified_by = user_id
#                 existing_schedule.modified_on = datetime.now()
#                 db.commit()

#             # Create new schedule
#             new_schedule = OffConsultantSchedule(**schedule_dict, created_by=user_id, created_on=datetime.now())
#             db.add(new_schedule)
#             db.commit()
#             return True

#         elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
#             # Handle UPDATE_ONLY case
#             existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()
#             if existing_schedule:
#                 for key, value in schedule_dict.items():
#                     setattr(existing_schedule, key, value)
#                 existing_schedule.modified_by = user_id
#                 existing_schedule.modified_on = datetime.now()
#                 db.commit()
#                 return True
#             else:
#                 raise ValueError(f"Schedule with ID {id} not found.")
        
#         else:
#             raise ValueError("Invalid action type or ID provided.")

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))


# def save_consultant_schedule(
#     schedule_data: ConsultantScheduleCreate,
#     consultant_id: Optional[int],
#     user_id: int,
#     id: Optional[int],
#     action_type: RecordActionType,
#     db: Session
# ):
#     try:
#         # Convert schedule_data to dictionary format for processing
#         schedule_dict = schedule_data.model_dump()
#         print("schedule_dict",schedule_dict)

#         # Handle special schedules (`is_normal_schedule == "no"`)
#         if schedule_data.is_normal_schedule == "no":
#             if not schedule_data.consultation_date:
#                 raise ValueError("For 'is_normal_schedule' no, 'consultation_date' must be provided.")
            
#             # Remove `effective_from_date` as it's not needed in special schedules
#             schedule_dict.pop("effective_from_date", None)

#             # Assign `day_of_week_id` using SQL query based on `consultation_date`
#             day_of_week_query = f"SELECT DAYOFWEEK('{schedule_data.consultation_date}')"
#             day_of_week_id = db.execute(day_of_week_query).fetchone()[0]
#             schedule_dict['day_of_week_id'] = day_of_week_id

#             # Directly insert the new schedule for the consultant
#             new_schedule = OffConsultantSchedule(**schedule_dict, consultant_id=consultant_id, created_by=user_id, created_on=datetime.now())
#             db.add(new_schedule)
#             db.commit()
#             return True

#         elif schedule_data.is_normal_schedule == "yes" and action_type == RecordActionType.UPDATE_AND_INSERT:
#             if consultant_id is None:
#                 raise ValueError("consultant_id is required for UPDATE_AND_INSERT")

#             # Ensure `effective_from_date` is provided
#             effective_from_date = schedule_dict.get('effective_from_date')
#             if not effective_from_date:
#                 raise ValueError("effective_from_date is required for UPDATE_AND_INSERT when is_normal_schedule is 'yes'.")

#             # Query for the existing schedule (active record)
#             existing_schedule = db.query(OffConsultantSchedule).filter(
#                 OffConsultantSchedule.consultant_id == consultant_id,
#                 OffConsultantSchedule.day_of_week_id == schedule_dict['day_of_week_id'],
#                 OffConsultantSchedule.consultation_mode_id == schedule_dict['consultation_mode_id'],
#                 OffConsultantSchedule.effective_to_date.is_(None)
#             ).first()

#             # If an active schedule exists, update its `effective_to_date`
#             if existing_schedule:
#                 new_effective_to_date = effective_from_date - timedelta(days=1)
#                 print("new_effective_to_date",new_effective_to_date)
#                 existing_schedule.effective_to_date = new_effective_to_date
#                 existing_schedule.modified_by = user_id
#                 existing_schedule.modified_on = datetime.now()
#                 db.commit()  # Commit the update for the existing schedule

#             # Insert the new schedule
#             new_schedule = OffConsultantSchedule(**schedule_dict, consultant_id=consultant_id, created_by=user_id, created_on=datetime.now())
#             db.add(new_schedule)
#             db.commit()
#             return True

#         elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
#             # Handle the update of an existing schedule based on the provided ID
#             existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()
#             if existing_schedule:
#                 for key, value in schedule_dict.items():
#                     setattr(existing_schedule, key, value)
#                 existing_schedule.modified_by = user_id
#                 existing_schedule.modified_on = datetime.now()
#                 db.commit()
#                 return True
#             else:
#                 raise ValueError(f"Schedule with ID {id} not found.")

#         else:
#             raise ValueError("Invalid action type or ID provided.")

#     except Exception as e:
#         db.rollback()  # Rollback changes in case of an error
#         raise HTTPException(status_code=400, detail=str(e))


# def save_consultant_schedule(
#     schedule_data: ConsultantScheduleCreate,
#     consultant_id: Optional[int],
#     user_id: int,
#     id: Optional[int],
#     action_type: RecordActionType,
#     db: Session
# ):
#     try:
#         # Convert schedule_data to dictionary format for processing
#         schedule_dict = schedule_data.model_dump()
#         print("schedule_dict", schedule_dict)

#         # Handle special schedules (`is_normal_schedule == "no"`)
#         if schedule_data.is_normal_schedule == "no":
#             if not schedule_data.consultation_date:
#                 raise ValueError("For 'is_normal_schedule' no, 'consultation_date' must be provided.")

#             # Remove `effective_from_date` as it's not needed in special schedules
#             schedule_dict.pop("effective_from_date", None)

#             # Assign `day_of_week_id` using SQL query based on `consultation_date`
#             day_of_week_query = text(f"SELECT DAYOFWEEK('{schedule_data.consultation_date}')")
#             day_of_week_id = db.execute(day_of_week_query).fetchone()[0]
#             schedule_dict['day_of_week_id'] = day_of_week_id

#             # Handle `INSERT_ONLY` action type
#             if action_type == RecordActionType.INSERT_ONLY:
#                 if consultant_id is None:
#                     raise ValueError("consultant_id is required for INSERT_ONLY")

#                 # Check if the record already exists to avoid duplicates
#                 existing_schedule = db.query(OffConsultantSchedule).filter(
#                     OffConsultantSchedule.consultant_id == consultant_id,
#                     OffConsultantSchedule.consultation_date == schedule_data.consultation_date,
#                     OffConsultantSchedule.consultation_mode_id == schedule_data.consultation_mode_id
#                 ).first()

#                 if existing_schedule:
#                     raise ValueError("A schedule for this consultant on this date already exists.")

#                 # Insert the new schedule
#                 new_schedule = OffConsultantSchedule(
#                     **schedule_dict, 
#                     consultant_id=consultant_id, 
#                     created_by=user_id, 
#                     created_on=datetime.now()
#                 )
#                 db.add(new_schedule)
#                 db.commit()
#                 return True

#             # Handle `UPDATE_ONLY` action type
#             elif action_type == RecordActionType.UPDATE_ONLY:
              
#                 if id is None:
#                     raise ValueError("ID is required for UPDATE_ONLY")
                
#                 # Fetch the existing schedule based on the provided ID
#                 existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()

#                 if not existing_schedule:
#                     raise ValueError(f"Schedule with ID {id} not found.")

#                 # Update only the fields that are provided in the schedule_dict
#                 for key, value in schedule_dict.items():
#                     setattr(existing_schedule, key, value)

#                 # Update the modification metadata
#                 existing_schedule.modified_by = user_id
#                 existing_schedule.modified_on = datetime.now()
                
#                 # Commit the update to the existing schedule
#                 db.commit()
#                 return True

#             else:
#                 raise ValueError("Invalid action type for special schedules (is_normal_schedule = 'no').")

#         # Handle normal schedules (`is_normal_schedule == "yes"`) and `UPDATE_AND_INSERT`
#         elif schedule_data.is_normal_schedule == "yes" and action_type == RecordActionType.UPDATE_AND_INSERT:
#             if consultant_id is None:
#                 raise ValueError("consultant_id is required for UPDATE_AND_INSERT")

#             # Ensure `effective_from_date` is provided
#             effective_from_date = schedule_dict.get('effective_from_date')
#             if not effective_from_date:
#                 raise ValueError("effective_from_date is required for UPDATE_AND_INSERT when is_normal_schedule is 'yes'.")

#             # Query for the existing schedule (active record)
#             existing_schedule = db.query(OffConsultantSchedule).filter(
#                 OffConsultantSchedule.consultant_id == consultant_id,
#                 OffConsultantSchedule.day_of_week_id == schedule_dict['day_of_week_id'],
#                 OffConsultantSchedule.consultation_mode_id == schedule_dict['consultation_mode_id'],
#                 OffConsultantSchedule.effective_to_date.is_(None)
#             ).first()

#             # If an active schedule exists, update its `effective_to_date`
#             if existing_schedule:
#                 new_effective_to_date = effective_from_date - timedelta(days=1)
#                 existing_schedule.effective_to_date = new_effective_to_date
#                 existing_schedule.modified_by = user_id
#                 existing_schedule.modified_on = datetime.now()
#                 db.commit()  # Commit the update for the existing schedule

#             # Insert the new schedule
#             new_schedule = OffConsultantSchedule(
#                 **schedule_dict, 
#                 consultant_id=consultant_id, 
#                 created_by=user_id, 
#                 created_on=datetime.now()
#             )
#             db.add(new_schedule)
#             db.commit()
#             return True
        
#         elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
#             # Handle the update of an existing schedule based on the provided ID
#             existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()
#             if existing_schedule:
#                 for key, value in schedule_dict.items():
#                     setattr(existing_schedule, key, value)
#                 existing_schedule.modified_by = user_id
#                 existing_schedule.modified_on = datetime.now()
#                 db.commit()
#                 return True
#             else:
#                 raise ValueError(f"Schedule with ID {id} not found.")
        


#         else:
#             raise ValueError("Invalid action type or ID provided.")

#     except Exception as e:
#         db.rollback()  # Rollback changes in case of an error
#         raise HTTPException(status_code=400, detail=str(e))


def save_consultant_schedule(
    schedule_data: ConsultantScheduleCreate,
    consultant_id: Optional[int],
    user_id: int,
    id: Optional[int],
    action_type: RecordActionType,
    db: Session
):
    try:
        # Convert schedule_data to dictionary format for processing
        schedule_dict = schedule_data.model_dump()
        print("schedule_dict", schedule_dict)

        # Handle special schedules (`is_normal_schedule == "no"`)
        if schedule_data.is_normal_schedule == "no":
            if not schedule_data.consultation_date:
                raise ValueError("For 'is_normal_schedule' no, 'consultation_date' must be provided.")
            
            # Remove `effective_from_date` as it's not needed in special schedules
            schedule_dict.pop("effective_from_date", None)

            # Assign `day_of_week_id` using SQL query based on `consultation_date`
            # day_of_week_query = f"SELECT DAYOFWEEK('{schedule_data.consultation_date}')"
            day_of_week_query = text(f"SELECT DAYOFWEEK('{schedule_data.consultation_date}')")
            day_of_week_id = db.execute(day_of_week_query).fetchone()[0]
            schedule_dict['day_of_week_id'] = day_of_week_id

            # INSERT ONLY logic
            if action_type == RecordActionType.INSERT_ONLY:
                if consultant_id is None:
                    raise ValueError("consultant_id is required for INSERT_ONLY")
                
                # Check if the record already exists to avoid duplicates
                existing_schedule = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.consultation_date == schedule_data.consultation_date,
                    OffConsultantSchedule.consultation_mode_id == schedule_data.consultation_mode_id
                ).first()

                if existing_schedule:
                    raise ValueError("A schedule for this consultant on this date already exists.")

                # Insert the new schedule
                new_schedule = OffConsultantSchedule(
                    **schedule_dict, 
                    consultant_id=consultant_id, 
                    created_by=user_id, 
                    created_on=datetime.now()
                )
                db.add(new_schedule)
                db.commit()
                return True

            # UPDATE ONLY logic
            elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
                # Fetch the existing schedule based on the provided ID
                existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()

                if not existing_schedule:
                    raise ValueError(f"Schedule with ID {id} not found.")

                # Update only the fields that are provided in the schedule_dict
                for key, value in schedule_dict.items():
                    setattr(existing_schedule, key, value)

                # Update the modification metadata
                existing_schedule.modified_by = user_id
                existing_schedule.modified_on = datetime.now()
                
                # Commit the update to the existing schedule
                db.commit()
                return True

            else:
                raise ValueError("Invalid action type for special schedules (is_normal_schedule = 'no').")

        # Handle normal schedules (`is_normal_schedule == "yes"`)
        elif schedule_data.is_normal_schedule == "yes":
            if action_type == RecordActionType.UPDATE_AND_INSERT:
                if consultant_id is None:
                    raise ValueError("consultant_id is required for UPDATE_AND_INSERT")

                # Ensure `effective_from_date` is provided
                effective_from_date = schedule_dict.get('effective_from_date')
                if not effective_from_date:
                    raise ValueError("effective_from_date is required for UPDATE_AND_INSERT when is_normal_schedule is 'yes'.")

                # Query for the existing schedule (active record)
                existing_schedule = db.query(OffConsultantSchedule).filter(
                    OffConsultantSchedule.consultant_id == consultant_id,
                    OffConsultantSchedule.day_of_week_id == schedule_dict['day_of_week_id'],
                    OffConsultantSchedule.consultation_mode_id == schedule_dict['consultation_mode_id'],
                    OffConsultantSchedule.effective_to_date.is_(None)
                ).first()

                # If an active schedule exists, update its `effective_to_date`
                if existing_schedule:
                    new_effective_to_date = effective_from_date - timedelta(days=1)
                    print("new_effective_to_date", new_effective_to_date)
                    existing_schedule.effective_to_date = new_effective_to_date
                    existing_schedule.modified_by = user_id
                    existing_schedule.modified_on = datetime.now()
                    db.commit()  # Commit the update for the existing schedule

                # Insert the new schedule
                new_schedule = OffConsultantSchedule(
                    **schedule_dict, 
                    consultant_id=consultant_id, 
                    created_by=user_id, 
                    created_on=datetime.now()
                )
                db.add(new_schedule)
                db.commit()
                return True

            # UPDATE ONLY logic for normal schedule
            elif action_type == RecordActionType.UPDATE_ONLY and id is not None:
                # Handle the update of an existing schedule based on the provided ID
                existing_schedule = db.query(OffConsultantSchedule).filter(OffConsultantSchedule.id == id).first()
                if existing_schedule:
                    for key, value in schedule_dict.items():
                        setattr(existing_schedule, key, value)
                    existing_schedule.modified_by = user_id
                    existing_schedule.modified_on = datetime.now()
                    db.commit()
                    return True
                else:
                    raise ValueError(f"Schedule with ID {id} not found.")

            else:
                raise ValueError("Invalid action type for normal schedules (is_normal_schedule = 'yes').")

        else:
            raise ValueError("Invalid schedule type or action type provided.")

    except Exception as e:
        db.rollback()  # Rollback changes in case of an error
        raise HTTPException(status_code=400, detail=str(e))



#-------------- TASK #------------------------------------------------------------------------------------------------------------



def save_off_consultation_task_master(
    db: Session,
    id: int,
    data: OffConsultationTaskMasterSchema,
    user_id: int
):
    try:
        if id == 0:
            # Insert new task master
            new_task_master = OffConsultationTaskMaster(
                created_by=user_id,
                created_on=datetime.now(),
                **data.model_dump(exclude={'details'})
            )
            db.add(new_task_master)
            db.commit()  # Commit to get new_task_master.id
            db.refresh(new_task_master)  # Refresh to get the updated id

            # Insert task details
            for detail in data.details:
                new_detail = OffConsultationTaskDetails(
                    task_master_id=new_task_master.id,
                    **detail.model_dump()
                )
                db.add(new_detail)

            db.commit()
            return {"message": "Created successfully"}

        else:
            # Update existing task master
            existing_task_master = db.query(OffConsultationTaskMaster).filter(OffConsultationTaskMaster.id == id).first()
            if not existing_task_master:
                # raise HTTPException(status_code=404, detail="Task master record not found")
                return {"message":" master record not found"}

            for key, value in data.model_dump(exclude={'details'}).items():
                setattr(existing_task_master, key, value)
            existing_task_master.modified_by = user_id
            existing_task_master.modified_on = datetime.now()

            # Delete existing task details by setting is_deleted='yes' and updating fields
            existing_details = db.query(OffConsultationTaskDetails).filter(OffConsultationTaskDetails.task_master_id == id).all()
            for detail in existing_details:
                detail.is_deleted = 'yes'
                # detail.deleted_by = user_id
                # detail.deleted_on = datetime.now()
                db.add(detail)

            # Insert updated task details
            for detail in data.details:
                if detail.id:
                    # Update existing detail
                    existing_detail = db.query(OffConsultationTaskDetails).filter(OffConsultationTaskDetails.id == detail.id).first()
                    if existing_detail:
                        for key, value in detail.model_dump().items():
                            setattr(existing_detail, key, value)
                        # existing_detail.modified_by = user_id
                        # existing_detail.modified_on = datetime.now()
                        existing_detail.is_deleted = 'no'
                    else:
                        # raise HTTPException(status_code=404, detail=f"Detail with id {detail.id} not found")
                        return {"message":" detail  with given id  not found"}
                else:
                    # Insert new detail
                    new_detail = OffConsultationTaskDetails(
                        task_master_id=id,
                        **detail.model_dump(),
                        # created_by=user_id,
                        # created_on=datetime.now()
                    )
                    db.add(new_detail)

            db.commit()
            return {"message": "Updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))




#-------------------------------------------------------------------------------------------


# def get_all_consultation_task_master_details(
#     db: Session,
#     service_id: Union[int, str] = 'ALL',
#     task_status: Union[int, str] = 'ALL',
#     consultation_mode: Union[int, str] = 'ALL',
#     tool: Union[int, str] = 'ALL',
#     consultant_id: Union[int, str] = 'ALL',
#     from_date: Optional[date] = None,
#     to_date: Optional[date] = None  
# ) -> List[OffViewConsultationTaskMasterSchema]:
#     search_conditions = [OffViewConsultationTaskMaster.is_deleted == 'no']

#     if service_id != 'ALL':
#         search_conditions.append(OffViewConsultationTaskMaster.service_id == service_id)

#     if task_status != 'ALL':
#         search_conditions.append(OffViewConsultationTaskMaster.task_status_id == task_status)

#     if consultation_mode != 'ALL':
#         search_conditions.append(OffViewConsultationTaskMaster.consultation_mode_id == consultation_mode)

#     if tool != 'ALL':
#         search_conditions.append(OffViewConsultationTaskMaster.consultation_tool_id == tool)

#     if consultant_id != 'ALL':
#         search_conditions.append(OffViewConsultationTaskMaster.consultant_id == consultant_id)

#     if from_date is not None:
#         search_conditions.append(func.date(OffViewConsultationTaskMaster.task_date) >= from_date)
        
#     if to_date is not None:
#         search_conditions.append(func.date(OffViewConsultationTaskMaster.task_date) <= to_date)

#     # Query all tasks from the view
#     tasks_query = db.query(OffViewConsultationTaskMaster).filter(and_(*search_conditions)).all()
    
#     # Query the additional services
#     additional_services_query = db.query(
#         OffConsultationTaskDetails.id,
#         OffConsultationTaskDetails.task_master_id,
#         OffConsultationTaskDetails.service_id,
#         OffViewServiceGoodsMaster.service_goods_name
#     ).join(
#         OffViewServiceGoodsMaster,
#         OffViewServiceGoodsMaster.service_goods_master_id == OffConsultationTaskDetails.service_id
#     ).filter(
#         OffConsultationTaskDetails.is_main_service == 'no',
#         OffConsultationTaskDetails.is_deleted == 'no'
#     ).all()

#     # Create a dictionary to store the additional services by task_master_id
#     additional_services_dict = {}
#     for service_detail_id, task_master_id, service_id, service_goods_name in additional_services_query:
#         if task_master_id not in additional_services_dict:
#             additional_services_dict[task_master_id] = []
#         additional_services_dict[task_master_id].append(
#             AdditionalServices(
#                 service_detail_id=service_detail_id,
#                 service_id=service_id,
#                 service_name=service_goods_name
#             )
#         )

#     # Merge the results
#     task_master_details = []
   
#     for task in tasks_query:
        
#         task_dict = task.__dict__.copy()
#         task_dict["additional_services"] = additional_services_dict.get(task.consultation_task_master_id, [])
#         task_master_details.append(OffViewConsultationTaskMasterSchema(**task_dict))

#     return task_master_details


def get_all_consultation_task_master_details(
    db: Session,
    service_id: Union[int, str] = 'ALL',
    task_status: Union[int, str] = 'ALL',
    consultation_mode: Union[int, str] = 'ALL',
    tool: Union[int, str] = 'ALL',
    consultant_id: Union[int, str] = 'ALL',
    from_date: Optional[date] = None,
    to_date: Optional[date] = None  
) -> List[OffViewConsultationTaskMasterSchema]:
    search_conditions = [OffViewConsultationTaskMaster.is_deleted == 'no']

    if service_id != 'ALL':
        search_conditions.append(OffViewConsultationTaskMaster.service_id == service_id)

    if task_status != 'ALL':
        search_conditions.append(OffViewConsultationTaskMaster.task_status_id == task_status)

    if consultation_mode != 'ALL':
        search_conditions.append(OffViewConsultationTaskMaster.consultation_mode_id == consultation_mode)

    if tool != 'ALL':
        search_conditions.append(OffViewConsultationTaskMaster.consultation_tool_id == tool)

    if consultant_id != 'ALL':
        search_conditions.append(OffViewConsultationTaskMaster.consultant_id == consultant_id)

    if from_date is not None:
        search_conditions.append(func.date(OffViewConsultationTaskMaster.task_date) >= from_date)
        
    if to_date is not None:
        search_conditions.append(func.date(OffViewConsultationTaskMaster.task_date) <= to_date)

    # Query all tasks from the view with ordering by task_date descending
    tasks_query = db.query(OffViewConsultationTaskMaster)\
                    .filter(and_(*search_conditions))\
                    .order_by(OffViewConsultationTaskMaster.task_date.desc())\
                    .all()

    # Query the additional services
    additional_services_query = db.query(
        OffConsultationTaskDetails.id,
        OffConsultationTaskDetails.task_master_id,
        OffConsultationTaskDetails.service_id,
        OffViewServiceGoodsMaster.service_goods_name
    ).join(
        OffViewServiceGoodsMaster,
        OffViewServiceGoodsMaster.service_goods_master_id == OffConsultationTaskDetails.service_id
    ).filter(
        OffConsultationTaskDetails.is_main_service == 'no',
        OffConsultationTaskDetails.is_deleted == 'no'
    ).all()

    # Create a dictionary to store the additional services by task_master_id
    additional_services_dict = {}
    for service_detail_id, task_master_id, service_id, service_goods_name in additional_services_query:
        if task_master_id not in additional_services_dict:
            additional_services_dict[task_master_id] = []
        additional_services_dict[task_master_id].append(
            AdditionalServices(
                service_detail_id=service_detail_id,
                service_id=service_id,
                service_name=service_goods_name
            )
        )

    # Merge the results
    task_master_details = []
   
    for task in tasks_query:
        task_dict = task.__dict__.copy()
        task_dict["additional_services"] = additional_services_dict.get(task.consultation_task_master_id, [])
        task_master_details.append(OffViewConsultationTaskMasterSchema(**task_dict))

    return task_master_details




#------------------------------------------------------------------------------------------------
###################ENQUIRY####################################################
#------------------------------------------------------------------------------------------------

# def save_enquiry_master(
#     db: Session,
#     enquiry_master_id: int,
#     enquiry_data: OffEnquiryResponseSchema,
#     user_id: int
# ) -> Dict[str, Union[Dict, List[Dict]]]:
#     try:
#         # Begin the transaction
#         db.begin()

#         if enquiry_master_id == 0:
#             # Insert new enquiry master record
#             enquiry_master = OffEnquiryMaster(
#                 created_by=user_id,
#                 created_on=datetime.now(),
#                 **enquiry_data.enquiry_master.model_dump(exclude_unset=True)
#             )
#             db.add(enquiry_master)
#             db.flush()  # Ensure the ID is generated

#             # Insert related enquiry details
#             enquiry_details_list = []
#             for detail_data in enquiry_data.enquiry_details:
#                 enquiry_number = generate_book_number('ENQUIRY', db)
#                 enquiry_detail = OffEnquiryDetails(
#                     enquiry_master_id=enquiry_master.id,
#                     enquiry_number=enquiry_number,
#                     created_by=user_id,
#                     created_on=datetime.now(),
#                     **detail_data.model_dump(exclude_unset=True)
#                 )
#                 db.add(enquiry_detail)
#                 enquiry_details_list.append(enquiry_detail)

#         elif enquiry_master_id > 0:
#             # Fetch existing enquiry master record
#             enquiry_master = db.query(OffEnquiryMaster).filter_by(id=enquiry_master_id).first()
#             if not enquiry_master:
#                 return {"detail":"Enquiry master not found"}

#             # Update enquiry master
#             enquiry_master_data = enquiry_data.enquiry_master.model_dump(exclude_unset=True)
#             for field, value in enquiry_master_data.items():
#                 setattr(enquiry_master, field, value)
#             enquiry_master.modified_by = user_id
#             enquiry_master.modified_on = datetime.now()

#             # Process enquiry details
#             enquiry_details_list = []
#             for detail_data in enquiry_data.enquiry_details:
#                 detail_data_dict = detail_data.model_dump(exclude_unset=True)
#                 detail_id = detail_data_dict.get("id")

#                 if detail_id:
#                     # Update existing detail if ID is provided
#                     existing_detail = db.query(OffEnquiryDetails).filter_by(id=detail_id, enquiry_master_id=enquiry_master_id).first()
#                     if existing_detail:
#                         for key, value in detail_data_dict.items():
#                             if key == "remarks" and existing_detail.remarks:
#                                 setattr(existing_detail, key, existing_detail.remarks + "\n" + value)
#                             else:
#                                 setattr(existing_detail, key, value)
#                         existing_detail.modified_by = user_id
#                         existing_detail.modified_on = datetime.now()
#                         enquiry_details_list.append(existing_detail)
#                     else:
#                         return {"detail":"Enquiry details not found"}
#                 else:
#                     # Check for existing detail or insert new one
#                     existing_detail = db.query(OffEnquiryDetails).filter_by(
#                         enquiry_master_id=enquiry_master_id,
#                         enquiry_date=detail_data_dict.get("enquiry_date")
#                     ).first()

#                     if existing_detail:
#                         for key, value in detail_data_dict.items():
#                             if key == "remarks" and existing_detail.remarks:
#                                 setattr(existing_detail, key, existing_detail.remarks + "\n" + value)
#                             else:
#                                 setattr(existing_detail, key, value)
#                         existing_detail.modified_by = user_id
#                         existing_detail.modified_on = datetime.now()
#                         enquiry_details_list.append(existing_detail)
#                     else:
#                         enquiry_number = generate_book_number('ENQUIRY', db)
#                         new_enquiry_detail = OffEnquiryDetails(
#                             enquiry_master_id=enquiry_master.id,
#                             enquiry_number=enquiry_number,
#                             created_by=user_id,
#                             created_on=datetime.now(),
#                             **detail_data_dict
#                         )
#                         db.add(new_enquiry_detail)
#                         enquiry_details_list.append(new_enquiry_detail)

#         # Commit the transaction
#         db.commit()

#         # Convert to dictionaries for response
#         enquiry_master_schema = {column.name: getattr(enquiry_master, column.name) for column in OffEnquiryMaster.__table__.columns}
#         enquiry_details_schema = [{column.name: getattr(detail, column.name) for column in OffEnquiryDetails.__table__.columns} for detail in enquiry_details_list]

#         return {
#             "enquiry_master": enquiry_master_schema,
#             "enquiry_details": enquiry_details_schema
#         }

#     except IntegrityError as e:
#         db.rollback()
#         if 'Duplicate entry' in str(e):
#             raise HTTPException(status_code=400, detail="Duplicate entry detected.")
#         else:
#             raise e
    
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))

def save_enquiry_master(
    db: Session,
    enquiry_master_id: int,
    enquiry_data: OffEnquiryResponseSchema,
    user_id: int
) -> Dict[str, Union[Dict, List[Dict]]]:
    financial_year_id = 1
    customer_id = 1
    
    try:
        # Begin the transaction
        db.begin()

        if enquiry_master_id == 0:
            # Insert new enquiry master record
            enquiry_master = OffEnquiryMaster(
                created_by=user_id,
                created_on=datetime.now(),
                **enquiry_data.enquiry_master.model_dump(exclude_unset=True)
            )
            db.add(enquiry_master)
            db.flush()  # Ensure the ID is generated

            # Insert related enquiry details
            enquiry_details_list = []
            for detail_data in enquiry_data.enquiry_details:
    
                enquiry_number = generate_book_number('ENQUIRY',financial_year_id,customer_id, db)
                enquiry_detail = OffEnquiryDetails(
                    enquiry_master_id=enquiry_master.id,
                    enquiry_number=enquiry_number,
                    created_by=user_id,
                    created_on=datetime.now(),
                    **detail_data.model_dump(exclude_unset=True)
                )
                db.add(enquiry_detail)
                enquiry_details_list.append(enquiry_detail)

        elif enquiry_master_id > 0:
            # Fetch existing enquiry master record
            enquiry_master = db.query(OffEnquiryMaster).filter_by(id=enquiry_master_id).first()
            if not enquiry_master:
                return {"detail":"Enquiry master not found"}

            # Update enquiry master
            enquiry_master_data = enquiry_data.enquiry_master.model_dump(exclude_unset=True)
            for field, value in enquiry_master_data.items():
                setattr(enquiry_master, field, value)
            enquiry_master.modified_by = user_id
            enquiry_master.modified_on = datetime.now()

            # Process enquiry details
            enquiry_details_list = []
            for detail_data in enquiry_data.enquiry_details:
                detail_data_dict = detail_data.model_dump(exclude_unset=True)
                detail_id = detail_data_dict.get("id")

                if detail_id:
                    # Update existing detail if ID is provided
                    existing_detail = db.query(OffEnquiryDetails).filter_by(id=detail_id, enquiry_master_id=enquiry_master_id).first()
                    if existing_detail:
                        for key, value in detail_data_dict.items():
                            if key == "remarks" and existing_detail.remarks:
                                setattr(existing_detail, key, existing_detail.remarks + "\n" + value)
                            else:
                                setattr(existing_detail, key, value)
                        existing_detail.modified_by = user_id
                        existing_detail.modified_on = datetime.now()
                        enquiry_details_list.append(existing_detail)
                    else:
                        return {"detail":"Enquiry details not found"}
                else:
                    # Check for existing detail or insert new one
                    existing_detail = db.query(OffEnquiryDetails).filter_by(
                        enquiry_master_id=enquiry_master_id,
                        enquiry_date=detail_data_dict.get("enquiry_date")
                    ).first()

                    if existing_detail:
                        for key, value in detail_data_dict.items():
                            if key == "remarks" and existing_detail.remarks:
                                setattr(existing_detail, key, existing_detail.remarks + "\n" + value)
                            else:
                                setattr(existing_detail, key, value)
                        existing_detail.modified_by = user_id
                        existing_detail.modified_on = datetime.now()
                        enquiry_details_list.append(existing_detail)
                    else:
                        enquiry_number = generate_book_number('ENQUIRY', financial_year_id, customer_id,db)
                        new_enquiry_detail = OffEnquiryDetails(
                            enquiry_master_id=enquiry_master.id,
                            enquiry_number=enquiry_number,
                            created_by=user_id,
                            created_on=datetime.now(),
                            **detail_data_dict
                        )
                        db.add(new_enquiry_detail)
                        enquiry_details_list.append(new_enquiry_detail)

        # Commit the transaction
        db.commit()

        # Convert to dictionaries for response
        enquiry_master_schema = {column.name: getattr(enquiry_master, column.name) for column in OffEnquiryMaster.__table__.columns}
        enquiry_details_schema = [{column.name: getattr(detail, column.name) for column in OffEnquiryDetails.__table__.columns} for detail in enquiry_details_list]

        return {
            "enquiry_master": enquiry_master_schema,
            "enquiry_details": enquiry_details_schema
        }

    except IntegrityError as e:
        db.rollback()
        if 'Duplicate entry' in str(e):
            raise HTTPException(status_code=400, detail="Duplicate entry detected.")
        else:
            raise e
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



#-------------------------------------------------------------------------------------------------------------
def get_enquiries(
    db: Session,
    search_value: Union[str, int] = "ALL",
    status_id: Optional[str] = "ALL",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    mobile_number: Optional[str] = None,
    email_id: Optional[str] = None
) -> List[OffViewEnquiryResponseSchema]:
    try:
        # Initialize search conditions
        search_conditions = [OffViewEnquiryDetails.is_deleted == "no"]
        
        # Add conditions for enquiry date range if provided
        if from_date and to_date:
            search_conditions.append(OffViewEnquiryDetails.enquiry_date.between(from_date, to_date))
        elif from_date:
            search_conditions.append(OffViewEnquiryDetails.enquiry_date >= from_date)
        elif to_date:
            search_conditions.append(OffViewEnquiryDetails.enquiry_date <= to_date)

        # Add condition for status ID if provided
        if status_id != "ALL":
            search_conditions.append(OffViewEnquiryDetails.enquiry_status_id == status_id)

        # Add condition for search value if it's not 'ALL'
        if search_value != "ALL":
            search_conditions.append(
                or_(
                    OffViewEnquiryMaster.mobile_number.like(f"%{search_value}%"),
                    OffViewEnquiryMaster.email_id.like(f"%{search_value}%")
                )
            )

        # Add condition for mobile number if provided
        if mobile_number:
            search_conditions.append(OffViewEnquiryMaster.mobile_number == mobile_number)
        if email_id:
            search_conditions.append(OffViewEnquiryMaster.email_id == email_id)

        # Execute the query
        # query_result = db.query(OffViewEnquiryDetails).join(
        #     OffViewEnquiryMaster,
        #     OffViewEnquiryDetails.enquiry_master_id == OffViewEnquiryMaster.enquiry_master_id
        # ).filter(and_(*search_conditions)).all()
        query_result = db.query(OffViewEnquiryDetails).join(
            OffViewEnquiryMaster,
            OffViewEnquiryDetails.enquiry_master_id == OffViewEnquiryMaster.enquiry_master_id
        ).filter(and_(*search_conditions)).order_by(
            OffViewEnquiryDetails.enquiry_date.desc(),  # Order by enquiry_date descending
            OffViewEnquiryMaster.first_name.asc()        # Order by full_name ascending
        ).all()
        if not query_result:
            return []

        # Dictionary to store enquiries by ID
        enquiry_dict = {}

        # Iterate over query result
        for enquiry_details_data in query_result:
            enquiry_id = enquiry_details_data.enquiry_master_id

            # Get the enquiry master corresponding to the enquiry details
            enquiry_master_data = db.query(OffViewEnquiryMaster).filter_by(
                enquiry_master_id=enquiry_id
            ).first()

            if enquiry_master_data:
                # Convert enquiry_master_data to schema
                enquiry_master_schema = OffViewEnquiryMasterSchema(
                    **enquiry_master_data.__dict__
                )

                # Convert enquiry_details_data to schema
                enquiry_details_schema = OffViewEnquiryDetailsSchema(**enquiry_details_data.__dict__)

                if enquiry_id not in enquiry_dict:
                    # Create new enquiry entry in dictionary
                    enquiry_dict[enquiry_id] = {
                        "enquiry_master": enquiry_master_schema,
                        "enquiry_details": [enquiry_details_schema]
                    }
                else:
                    # Append enquiry details to existing entry
                    enquiry_dict[enquiry_id]["enquiry_details"].append(enquiry_details_schema)

        # Convert dictionary values to list of OffViewEnquiryResponseSchema objects
        enquiries = [OffViewEnquiryResponseSchema(**enquiry_data) for enquiry_data in enquiry_dict.values()]

        return enquiries

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#------------------------------------------------------------------------------------------------
    # WORK ORDER
#------------------------------------------------------------------------------------------------

def get_all_services_from_service_master(
    db: Session,
    service_type: str,
    has_consultation: str
) -> List[OffViewServiceGoodsMasterDisplay]:
    try:
       
         # Initialize query with additional filter conditions
        query = db.query(OffViewServiceGoodsMaster).filter(
            OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'no',
            OffViewServiceGoodsMaster.hsn_sac_class_id == 2
        )
        # Apply filter conditions
        if service_type != "ALL":
            if service_type == "SINGLE SERVICE":
                query = query.filter(OffViewServiceGoodsMaster.is_bundled_service == 'no')
            elif service_type == "BUNDLE SERVICE":
                query = query.filter(OffViewServiceGoodsMaster.is_bundled_service == 'yes')

        if has_consultation != "ALL":
            if has_consultation == "Yes":
                query = query.filter(OffViewServiceGoodsMaster.has_consultation == 'yes')
            elif has_consultation == "No":
                query = query.filter(OffViewServiceGoodsMaster.has_consultation == 'no')

        # Execute the query
        query_result = query.all()

        # Check if no data is found
        if not query_result:
            return []

        # Fetching details for bundled service_goods_master_ids
        master_ids = [result.service_goods_master_id for result in query_result if result.is_bundled_service == "yes"]
        details = db.query(OffViewServiceGoodsDetails).filter(OffViewServiceGoodsDetails.bundled_service_goods_id.in_(master_ids)).all()

        # Create a dictionary of details
        details_dict = {}
        for detail in details:
            if detail.bundled_service_goods_id not in details_dict:
                details_dict[detail.bundled_service_goods_id] = []
            details_dict[detail.bundled_service_goods_id].append(OffViewServiceGoodsDetailsDisplay.from_orm(detail))

        # Convert ORM results to Pydantic models and return
        return [
            OffViewServiceGoodsMasterDisplay(
                **result.__dict__,
                details=details_dict.get(result.service_goods_master_id, None)
            )
            for result in query_result
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
#--------------------
def get_consultation_tools(db: Session, mode_id: int = 0):
    if mode_id == 0:
        # Fetch all consultation modes that are not deleted
        consultation_modes = db.query(OffConsultationMode).filter(OffConsultationMode.is_deleted == "no").all()
        
        
        # Convert SQLAlchemy models to Pydantic models
        return [ConsultationModeSchema.from_orm(mode) for mode in consultation_modes]
    else:
        # Fetch consultation tools for a specific mode_id that are not deleted
        tools = db.query(OffConsultationTool).filter(
            OffConsultationTool.consultation_mode_id == mode_id,
            OffConsultationTool.is_deleted == "no"
        ).all()
        
        # Convert SQLAlchemy models to Pydantic models
        tools_schema = [ConsultationToolSchema.from_orm(tool) for tool in tools]
        return tools_schema


#-------------------------OFFER---------------------------------------------------------------------------------
def save_office_offer_details(
    db: Session,
    id: int,
    data: SaveOfferDetails,
    user_id: int,
    action_type: RecordActionType,
    apply_to: ApplyTo
):
    if action_type == RecordActionType.INSERT_ONLY and id != 0:
       raise HTTPException(status_code=400, detail="Invalid action: For INSERT_ONLY, id should be 0")
    elif action_type == RecordActionType.UPDATE_ONLY and id <= 0:
        raise HTTPException(status_code=400, detail="Invalid action: For UPDATE_ONLY, id should be greater than 0")

    try:
        if action_type == RecordActionType.INSERT_ONLY:
          for master_data in data.master:
             new_master_data = master_data.model_dump()
             new_master_data.update({
                 "created_by": user_id,
                 "created_on": datetime.now()
               })
             new_master = OffOfferMaster(**new_master_data)
             db.add(new_master)
             db.flush()  # Ensure new_master.id is available for details

          if apply_to == ApplyTo.SELECTED :    
             for detail_data in data.details:
                new_detail_data = detail_data.model_dump()

                service_goods_master_id = new_detail_data.get("service_goods_master_id")

                # Check if the service is deleted
                service = db.query(OffServiceGoodsMaster).filter(OffServiceGoodsMaster.id == service_goods_master_id).first()
                if service and service.is_deleted == 'yes':
                   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot give offers for a deleted service")

                new_detail_data.update({
                    "offer_master_id": new_master.id,
                    "created_by": user_id,
                    "created_on": datetime.now()
                  })
                new_detail = OffOfferDetails(**new_detail_data)
                db.add(new_detail)
          else:
                details = db.query(OffServiceGoodsMaster.id).filter(OffServiceGoodsMaster.is_deleted == 'no').all()
                for detail_data in details:
                   new_detail_data = {
                     "offer_master_id": new_master.id,
                     "service_goods_master_id": detail_data[0],
                     "created_by": user_id,
                     "created_on": datetime.now()
                    }
                   new_detail = OffOfferDetails(**new_detail_data)
                   db.add(new_detail)
        elif action_type == RecordActionType.UPDATE_ONLY:
          existing_master = db.query(OffOfferMaster).filter(OffOfferMaster.id == id).first()
          if not existing_master:
            raise HTTPException(status_code=400, detail="Master record not found")

          # Use the first item from data.master for update
          master_update_data = data.master[0].model_dump()
          for key, value in master_update_data.items():
             setattr(existing_master, key, value)
          existing_master.modified_by = user_id
          existing_master.modified_on = datetime.now()
            
          existing_details = db.query(OffOfferDetails).filter(OffOfferDetails.offer_master_id == id).all()    
          for det in existing_details:
              det.is_deleted = 'yes'
              det.deleted_by = user_id
              det.deleted_on = datetime.now()

          if apply_to == ApplyTo.SELECTED :    
            for detail_data in data.details:
              new_detail_data = detail_data.model_dump()

              service_goods_master_id = new_detail_data.get("service_goods_master_id")

              # Check if the product is deleted
              service = db.query(OffServiceGoodsMaster).filter(OffServiceGoodsMaster.id == service_goods_master_id).first()
              if service and service.is_deleted == 'yes':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot give offers for a deleted service")
              new_detail_data.update({
                 "offer_master_id": id,
                 "created_by": user_id,
                 "created_on": datetime.now()
                })
              new_detail = OffOfferDetails(**new_detail_data)
              db.add(new_detail)
          else:
             details = db.query(OffServiceGoodsMaster.id).filter(OffServiceGoodsMaster.is_deleted == 'no').all()
             for detail_data in details:
                new_detail_data = {
                  "offer_master_id": id,
                  "service_goods_master_id": detail_data[0],
                  "created_by": user_id,
                  "created_on": datetime.now()
                 }
                new_detail = OffOfferDetails(**new_detail_data)
                db.add(new_detail)

        db.commit()
    except IntegrityError as e:
       db.rollback()
       logger.error("IntegrityError: %s", str(e))
       if 'Duplicate entry' in str(e):
         raise HTTPException(status_code=400, detail="Duplicate entry detected.")
       else:
         raise e
    except OperationalError as e:
       db.rollback()
       logger.error("OperationalError: %s", str(e))
       raise HTTPException(status_code=500, detail="Database connection error.")
    except Exception as e:
       db.rollback()
       logger.error("Exception: %s", str(e))
       raise e

#------------------------------------------------------------------------------------------------------------
def get_all_offer_list(
                        db : Session,
                        category_id : Optional[int]=None,
                        offer_master_id : Optional[int]=None ,
                        operator : Optional[Status] = None 
                        
                        ):
    try:
        current_date = datetime.today()
        query = db.query(OffOfferMaster).filter(OffOfferMaster.is_deleted == 'no')
        
        if category_id:
            query = query.filter(OffOfferMaster.offer_category_id == category_id)
        
        if offer_master_id:
            query = query.filter(OffOfferMaster.id == offer_master_id)
        
        if operator:
            if operator == Status.CURRENT:
                query = query.filter(
                    OffOfferMaster.effective_from_date <= current_date,
                    OffOfferMaster.effective_to_date >= current_date
                )
            elif operator == Status.UPCOMMING:
                query = query.filter(OffOfferMaster.effective_from_date > current_date)
            elif operator == Status.EXPIRED:
                query = query.filter(OffOfferMaster.effective_to_date < current_date)
        
        offer_master_data = query.all()
        # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
        return offer_master_data
    except Exception as e:
        print("Error:", e)  # Print the exception message for debugging
        raise HTTPException(status_code=500, detail=str(e))
    

#------------------------------------------------------------------------------------------------------------
def delete_offer_master(db, offer_master_id,action_type,deleted_by):
    existing_offer = db.query(OffOfferMaster).filter(OffOfferMaster.id == offer_master_id).first()

    if existing_offer is None:
        # raise HTTPException(status_code=404, detail="Offer  not found")
        return {"message":" Offer not found"}
    
    
    if(action_type== 'DELETE'):
       existing_offer.is_deleted = 'yes'
       existing_offer.deleted_by = deleted_by
       existing_offer.deleted_on = datetime.now()
            
            
       db.query(OffOfferDetails).filter(OffOfferDetails.offer_master_id == offer_master_id).update({
             OffOfferDetails.is_deleted: 'yes',                
             OffOfferDetails.deleted_by: deleted_by,
             OffOfferDetails.deleted_on: datetime.now()
          }, synchronize_session=False)
        
       db.commit()

       return {
            "message": "Offer marked as deleted successfully",
            }
    if(action_type == 'UNDELETE'):
       existing_offer.is_deleted = 'no'
       existing_offer.deleted_by = None
       existing_offer.deleted_on = None
       db.commit()

       return {
            "message": "Offer marked as Undeleted successfully",
            }


#------------------WORKORDER---------------------------------------------------------------------------
def get_work_order_details( 
                           db: Session,                            
                           entry_point: EntryPoint,
                           id: int,
                           visit_master_id : Optional[int]= None,
                           enquiry_details_id : Optional[int]= None,
                           work_order_details_id : Optional[int] = None,
                           ) -> List[Dict]:

    if entry_point == 'WORK_ORDER':
            try:
                data = []
                query = db.query(WorkOrderMasterView).filter(
                    WorkOrderMasterView.is_deleted == 'no',
                    WorkOrderMasterView.work_order_master_id == id)
                
                work_order_master_data = query.first()
                if not work_order_master_data:
                    return {
                        'message': "Work order not found",
                    }
                query = db.query(WorkOrderDetailsView).filter(
                        WorkOrderDetailsView.work_order_master_id == id,
                        WorkOrderDetailsView.is_main_service == 'yes',
                        WorkOrderDetailsView.is_deleted == 'no')
                if work_order_details_id :
                    query = query.filter(
                        
                        WorkOrderDetailsView.work_order_details_id == work_order_details_id)
                work_order_details_data = query.all()
                
                service_data = []

                for detail in work_order_details_data:
                    detail_data = OffViewWorkOrderDetailsSchema.model_validate(detail)
                    
                    if detail.is_depended_service == 'yes':
                        detail_data.depended_on = get_dependencies(db, detail.work_order_details_id)
                    if detail.is_bundle_service == 'yes':
                        sub_services = db.query(WorkOrderDetailsView).filter(
                            WorkOrderDetailsView.bundle_service_id == detail.work_order_details_id,
                            WorkOrderDetailsView.is_deleted == 'no'
                        ).all()

                        sub_service_data = []
                        for sub_service in sub_services:
                            sub_service_detail = OffViewWorkOrderDetailsSchema.model_validate(sub_service)
                            
                            if sub_service.is_depended_service == 'yes':
                                sub_service_detail.depended_on = get_dependencies(db, sub_service.work_order_details_id)
                            
                            sub_service_data.append(sub_service_detail)
                            detail_data.sub_services = sub_service_data
                        # detail_data.sub_services = sub_service_data

                    service_data.append(detail_data)  # Append only once for each service

                work_order_data = WorkOrderResponseSchema(
                    work_order=OffViewWorkOrderMasterSchema.model_validate(work_order_master_data),
                    service_data=service_data
                )
                
                data.append(work_order_data.dict())  # Convert to dictionary format if required
                return data

            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=str(e))
        
    elif entry_point == 'CONSULTATION':
        
            
            if visit_master_id is None:
                # raise ValueError("visit master id is required for CONSULTATION entry point")
                return {
                    'message ': "visit master id is required for CONSULTATION entry point",
                    'Success' : 'false'
                }
            existing_data = db.query(OffWorkOrderMaster).filter(
                OffWorkOrderMaster.appointment_master_id == id,
                OffWorkOrderMaster.visit_master_id == visit_master_id
            ).first()
            if existing_data :
                return {
                    'message': 'work_order already exist',
                    'work_order_master_id':existing_data.id
                }
            # appointment_data = db.query(OffAppointmentMaster).filter(OffAppointmentMaster.id == id).first()
            visit_data       = db.query(OffAppointmentVisitMasterView).filter(
                OffAppointmentVisitMasterView.appointment_master_id == id,
                OffAppointmentVisitMasterView.visit_master_id==visit_master_id).first()   
            if  not visit_data:
                return {
                    'message': "Consultation or visit data not found",
                }
            full_name = visit_data.full_name.split()
            first_name = full_name[0] if len(full_name) > 0 else ""
            middle_name = full_name[1] if len(full_name) > 2 else ""
            last_name = full_name[-1] if len(full_name) > 1 else ""

            # Transforming the data
            transformed_data = {
                # "work_order_master_id" : visit_data.,
                "financial_year_id":visit_data.financial_year_id,
                "financial_year" : visit_data.financial_year,
                "appointment_master_id": visit_data.appointment_master_id,
                "visit_master_id": visit_master_id,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "gender_id": visit_data.gender_id,
                "gender" : visit_data.gender,
                "mobile_number": visit_data.mobile_number,
                "whatsapp_number":visit_data.whatsapp_number,
                "email_id":visit_data.email_id,
                "locality":visit_data.locality,
                "pin_code":visit_data.pin_code,
                "post_office_id":visit_data.post_office_id,
                "post_office_name": visit_data.post_office_name,
                "taluk_id":visit_data.taluk_id,
                "taluk_name": visit_data.taluk_name,
                "district_id":visit_data.district_id,
                "district_name":visit_data.district_name,
                "state_id":visit_data.state_id,
                "state_name": visit_data.state_name,
                "customer_number": visit_data.customer_number

            }

            data = WorkOrderResponseSchema(
                work_order=transformed_data,

                # work_order=OffAppointmentMasterSchema.model_validate(transformed_data),
                service_data=[]
            )
    elif entry_point == 'ENQUIRY':
        if id is None:
                return {
                    'message ': "ID is required for ENQUIRY entry point",
                    'Success' : 'false'
                }
                # raise HTTPException(status_code=400, detail="ID is required for ENQUIRY entry point")
        elif enquiry_details_id is None:
            return {
                    'message ': "enquiry_details_id is required for ENQUIRY entry point",
                    'Success' : 'false'
                }
        existing_data = db.query(OffWorkOrderMaster).filter(
            OffWorkOrderMaster.enquiry_master_id == id,
            OffWorkOrderMaster.enquiry_details_id == enquiry_details_id
        ).first()
        if existing_data :
            return {
                'message': 'work_order already exist',
                'work_order_master_id':existing_data.id
            }
            # raise HTTPException(status_code=400, detail="enquiry_details_id is required for ENQUIRY entry point")        
        enquiry_master_data = db.query(OffViewEnquiryMaster).filter(
            OffViewEnquiryMaster.is_deleted == 'no',
            OffViewEnquiryMaster.enquiry_master_id == id).first()
        enquiry_detail_data = db.query(OffViewEnquiryDetails).filter(
            OffViewEnquiryDetails.is_deleted == 'no',
            OffViewEnquiryDetails.enquiry_master_id == id,
            OffViewEnquiryDetails.enquiry_details_id == enquiry_details_id
            ).first()
        if not enquiry_master_data or not enquiry_detail_data:
                return {
                    'message': "Enquiry master or Enquiry details  data not found"
                }
        
        work_order_data = OffViewWorkOrderMasterSchema(
            **enquiry_master_data.__dict__,
            # work_order_master_id =enquiry_master_data.enquiry_master_id,
            enquiry_details_id=enquiry_detail_data.enquiry_details_id,
            financial_year_id=enquiry_detail_data.financial_year_id,
            financial_year= enquiry_detail_data.financial_year,
            country_name = enquiry_detail_data.country_name_english

        )
        # data = enquiry_master_data
        data = WorkOrderResponseSchema(
            work_order= work_order_data,
            service_data=[]
        )
    else:
            return {
                'message': 'Invalid entry point',
                'Success': 'false'
            }
            # raise ValueError("Invalid entry point")
    # if data:

    return data
#------------------------------------------------------------------------------------------------------------
def get_work_order_list(
    db: Session,
    search_value: Union[str, int] = "ALL",
    work_order_number: Optional[int] = None,
    status_id:  Optional[Union[int, str]] = "ALL",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) :
   
        try:
            
            # Initialize search conditions
            search_conditions = [WorkOrderMasterView.is_deleted == "no"]
            
            # Add conditions for enquiry date range if provided
            if from_date and to_date:
                search_conditions.append(WorkOrderMasterView.work_order_date.between(from_date, to_date))
            elif from_date:
                search_conditions.append(WorkOrderMasterView.work_order_date >= from_date)
            elif to_date:
                search_conditions.append(WorkOrderMasterView.work_order_date <= to_date)
            
            if work_order_number != None:
                search_conditions.append(WorkOrderMasterView.work_order_number == work_order_number)
            
            # Add condition for status ID if provided
            if status_id !='ALL':
                search_conditions.append(WorkOrderMasterView.work_order_status_id == status_id)

            # Add condition for search value if it's not 'ALL'
            if search_value != "ALL":
                search_conditions.append(
                    or_(
                        WorkOrderMasterView.mobile_number.like(f"%{search_value}%"),
                        WorkOrderMasterView.email_id.like(f"%{search_value}%")
                    )
                )
            
            # Execute the query
            query_result = db.query(WorkOrderMasterView).filter(and_(*search_conditions)).all()

            # if not query_result:
            #     raise HTTPException(status_code=404, detail="Work_order not found")

           

            return query_result

        except HTTPException as http_error:
            raise http_error
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
         
            # except HTTPException as http_error:
            # raise http_error
#------------------------------------------------------------------------------------------------------------

def get_business_activity_master_by_type_id(
        db: Session,
        type_id: Optional[int] = None
) -> List[BusinessActivityMasterSchema]:
    
    if type_id is None:
        business_activities = db.query(BusinessActivityMaster).filter(BusinessActivityMaster.is_deleted == 'no').all()
    else:
        business_activities = db.query(BusinessActivityMaster).filter(
            BusinessActivityMaster.is_deleted == 'no',
            BusinessActivityMaster.business_activity_type_id == type_id).all()
        
    return business_activities  
#---------------------------------------------------------------------------------------------------------

def get_dependencies(db: Session,detail_id):
    dependencies = db.query(WorkOrderDependancy.id,
        WorkOrderDependancy.work_order_master_id,
        WorkOrderDependancy.work_order_details_id,
        WorkOrderDependancy.dependent_on_work_id,
        WorkOrderDependancy.is_deleted,
        OffViewServiceGoodsMaster.service_goods_name).join(
        OffViewServiceGoodsMaster,
        WorkOrderDependancy.dependent_on_work_id == OffViewServiceGoodsMaster.service_goods_master_id
    ).filter(
        WorkOrderDependancy.work_order_details_id == detail_id,
        WorkOrderDependancy.is_deleted == 'no'
    ).all()
    # return [WorkOrderDependancySchema.model_validate(dep) for dep in dependencies]
    return [WorkOrderDependancySchema(
                id=dep.id,
                work_order_master_id=dep.work_order_master_id,
                work_order_details_id=dep.work_order_details_id,
                dependent_on_work_id=dep.dependent_on_work_id,
                is_deleted=dep.is_deleted,
                service_goods_name=dep.service_goods_name  # Populate the service_goods_name
            )
            for dep in dependencies]

#-------------------------------------------------------------------------------------------------------\
def get_business_activity_by_master_id(
        db: Session,
        master_id: Optional[int] =None
) -> List[BusinessActivitySchema]:
        
        if master_id is None:
            business_activities = db.query(BusinessActivity).filter(BusinessActivity.is_deleted == 'no').all()

        else:
            business_activities = db.query(BusinessActivity).filter(
                BusinessActivity.is_deleted == 'no',
                BusinessActivity.activity_master_id == master_id).all()
        return business_activities
   

#----------------------------------------------------------------------------------------------------

def save_work_order(
    request: CreateWorkOrderRequest,
    db: Session,
    user_id: int,
    financial_year_id: int,
    customer_id : int,
    work_order_master_id: Optional[int] = 0
):
    if work_order_master_id == 0:
        try:
           
            work_order_number = generate_book_number('WORK_ORDER',financial_year_id,customer_id, db)
            enquiry_details_id = request.master.enquiry_details_id
            master_data = request.master.model_dump()
            master_data['created_on'] = datetime.now()
            master_data['created_by'] = user_id
            master_data['work_order_number'] = work_order_number
            master_data['work_order_date'] = datetime.now()
            master = OffWorkOrderMaster(**master_data)
            db.add(master)
            db.flush()
            
            for main_detail in request.main_service:
                detail_data = main_detail.model_dump()
                detail_data['work_order_master_id'] = master.id
                detail_data['created_by'] = user_id
                detail_data['created_on'] = datetime.now()
                
                # Remove sub_services before creating the main work order detail
                sub_services = detail_data.pop('sub_services', [])
                
                work_order_detail = OffWorkOrderDetails(**detail_data)
                db.add(work_order_detail)
                db.flush()
                for sub_detail in sub_services:
                    sub_detail_data = sub_detail  # Already a dictionary
                    sub_detail_data['work_order_master_id'] = master.id
                    sub_detail_data['created_by'] = user_id
                    sub_detail_data['created_on'] = datetime.now()
                    sub_detail_data['bundle_service_id'] = work_order_detail.id

                    # Remove sub_services from sub_detail_data if present
                    sub_detail_data.pop('sub_services', None)
                    
                    work_order_sub_detail = OffWorkOrderDetails(**sub_detail_data)
                    db.add(work_order_sub_detail)

            db.commit()
            if enquiry_details_id:
                 update_column_value(db,'off_enquiry_details',enquiry_details_id,'enquiry_status_id',2)

            return {"message": "Work order created successfully", 
                    "work_order_master_id": master.id,
                    "work_order_number":master.work_order_number,
                    "work_order_date": master.work_order_date,
                      "success": "success"}

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"An error occurred while creating the work order, {str(e)}")

    else:
        try:
            master = db.query(OffWorkOrderMaster).filter(
                OffWorkOrderMaster.id == work_order_master_id
            ).first()

            if not master:
                return {
                    'message': 'Work order master not found'
                }

            master_data = request.master.model_dump()  # Use .dict() for Pydantic models
            for key, value in master_data.items():
                if key != "id":
                    setattr(master, key, value)

            master.modified_on = datetime.now()
            master.modified_by = user_id

            db.commit()
            db.flush()

            existing_detail_ids = {
                detail.id for detail in db.query(OffWorkOrderDetails.id).filter(
                    OffWorkOrderDetails.work_order_master_id == work_order_master_id
                ).all()
            }
            provided_detail_ids = {detail.id for detail in request.main_service if detail.id}
            
            # Update existing records or add new ones
            for detail in request.main_service:
                sub_services = detail.sub_services if hasattr(detail, 'sub_services') else []
                provided_detail_ids.update(sub_detail.id for sub_detail in sub_services if sub_detail.id)

                if detail.id and detail.id in existing_detail_ids:
                    work_order_detail = db.query(OffWorkOrderDetails).filter(
                        OffWorkOrderDetails.id == detail.id,
                        OffWorkOrderDetails.work_order_master_id == work_order_master_id
                    ).first()

                    if not work_order_detail:
                        return {
                            'message': f"Work order detail with id {detail.id} not found"
                        }

                    detail_data = detail.model_dump()  # Use .dict() for Pydantic models
                    for key, value in detail_data.items():
                        if key != "id":
                            setattr(work_order_detail, key, value)
                    work_order_detail.is_deleted = 'no'
                    work_order_detail.modified_on = datetime.now()
                    work_order_detail.modified_by = user_id

                    # Handle sub-details for existing records
                    for sub_detail in sub_services:
                        if sub_detail.id in existing_detail_ids:
                            work_order_sub_detail = db.query(OffWorkOrderDetails).filter(
                                OffWorkOrderDetails.id == sub_detail.id,
                                OffWorkOrderDetails.work_order_master_id == work_order_master_id
                            ).first()

                            if not work_order_sub_detail:
                                return {
                                    'message': f"Work order sub-detail with id {sub_detail.id} not found"
                                }

                            sub_detail_data = sub_detail.dict()  # Use .dict() for Pydantic models
                            for key, value in sub_detail_data.items():
                                if key != "id":
                                    setattr(work_order_sub_detail, key, value)

                            work_order_sub_detail.modified_on = datetime.now()
                            work_order_sub_detail.modified_by = user_id
                            work_order_sub_detail.is_deleted = 'no'
                else:
                    detail_data = detail.model_dump()  # Use .dict() for Pydantic models
                    detail_data['work_order_master_id'] = master.id
                    detail_data['created_by'] = user_id
                    detail_data['created_on'] = datetime.now()
                    
                    # Remove sub_services before creating the detail
                    sub_services = detail_data.pop('sub_services', [])
                    
                    work_order_detail = OffWorkOrderDetails(**detail_data)
                    db.add(work_order_detail)
                    db.flush()

                    for sub_detail in sub_services:
                        sub_detail_data = sub_detail  # Already a dictionary
                        sub_detail_data['work_order_master_id'] = master.id
                        sub_detail_data['created_by'] = user_id
                        sub_detail_data['created_on'] = datetime.now()
                        sub_detail_data['bundle_service_id'] = work_order_detail.id

                        # Remove sub_services from sub_detail_data if present
                        sub_detail_data.pop('sub_services', None)

                        work_order_sub_detail = OffWorkOrderDetails(**sub_detail_data)
                        db.add(work_order_sub_detail)

            # Set is_details = 'yes' for existing records not in the provided details list
            for existing_id in existing_detail_ids - provided_detail_ids:
               
                work_order_detail = db.query(OffWorkOrderDetails).filter(
                    OffWorkOrderDetails.id == existing_id
                ).first()

                if work_order_detail.is_main_service == 'yes' or work_order_detail.is_bundle_service == 'yes':
                    sub_services = db.query(OffWorkOrderDetails).filter(
                        OffWorkOrderDetails.bundle_service_id == work_order_detail.id
                    ).all()

                    if sub_services:  # Check if sub_services is not empty
                        for service in sub_services:
                            service.bundle_service_id = None
                            service.modified_on = datetime.now()
                            service.modified_by = user_id
                            db.add(service)  # Add to the session

                depended_services = db.query(WorkOrderDependancy).filter(
                    WorkOrderDependancy.dependent_on_work_id == work_order_detail.id
                ).all()
                for depended_service in depended_services:
                    depended_service.is_deleted = 'yes'
                    db.add(depended_service)

                work_order_detail.is_deleted = 'yes'
                work_order_detail.modified_on = datetime.now()
                work_order_detail.modified_by = user_id
                db.add(work_order_detail)  # Add to the session

            db.commit()  # Commit all changes at once

            return {"message": "Work order updated successfully", 
                    "work_order_master_id": master.id,
                    "work_order_number":master.work_order_number,
                    "work_order_date": master.work_order_date,
                    "success": "success"}

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


#-------------------------------------------------------------------------------------------------------------
def get_utility_document_by_nature_of_possession(
        service_id: int,
        constitution_id: int,
        nature_of_possession_id: int,
        db: Session 
)->List[OffViewServiceDocumentsDataDetailsSchema]:
    try:
        # Extract service_document_master_id
        service_document_master_id_row = db.query(OffServiceDocumentDataMaster.id).filter(
            OffServiceDocumentDataMaster.service_goods_master_id == service_id,
            OffServiceDocumentDataMaster.constitution_id == constitution_id
        ).first()
        # print("service_document_master data ---- ",service_document_master_id_row)
        # Check if service_document_master_id_row is None
        if service_document_master_id_row is None:
            return []

        # Extract the actual ID from the row
        service_document_master_id = service_document_master_id_row.id
        # Fetch service document details
        service_document_details_data = db.query(OffViewServiceDocumentsDataDetails).filter(
            OffViewServiceDocumentsDataDetails.service_document_data_master_id == service_document_master_id,
            OffViewServiceDocumentsDataDetails.nature_of_possession_id == nature_of_possession_id
        ).all()

        if service_document_details_data:
            return service_document_details_data
        else:
            return []

    except SQLAlchemyError as e:
        return {"error": str(e)}

    except Exception as e:
        return {"error": str(e)}


#---------------------------------------------------------------------------------------------------------------

def save_work_order_service_details(
    db: Session,
    request: CreateWorkOrderSetDtailsRequest,
    work_order_details_id: int,
    user_id: int
):

    try:
        if work_order_details_id == 0:
            return {'message': 'Error, please provide work order details id'}

        # Fetch work order details
        work_order_details = db.query(OffWorkOrderDetails).filter(
            OffWorkOrderDetails.id == work_order_details_id
        ).first()

        if not work_order_details:
            return {'message': 'Work order details not found'}
        else:
            # Update work order details
            detail_data_dict = request.workOrderDetails.model_dump()
            for key, value in detail_data_dict.items():
                if key == "remarks" and work_order_details.remarks:
                    setattr(work_order_details, key, work_order_details.remarks + "\n" + value)
                elif key != "id": 
                    setattr(work_order_details, key, value)

            # Update the modified_on field
            work_order_details.modified_on = datetime.utcnow()

        db.commit()
        db.flush()

        # Fetch existing business place details for this work order detail
        existing_business_place_details = db.query(WorkOrderBusinessPlaceDetails).filter(
            WorkOrderBusinessPlaceDetails.work_order_details_id == work_order_details_id
        ).all()

        # Track incoming business place detail IDs
        incoming_ids = set(detail.id for detail in request.businessPlaceDetails if detail.id and detail.id != 0)

        # Process business place details
        for detail in request.businessPlaceDetails:
            detail_data = detail.model_dump()
            if detail_data.get("id") and detail_data["id"] != 0:
                # Update existing business place details
                business_place_detail = db.query(WorkOrderBusinessPlaceDetails).filter(
                    WorkOrderBusinessPlaceDetails.id == detail_data["id"]
                ).first()

                if not business_place_detail:
                    return {
                        'message': 'Business place details not found',
                        'Success': 'false'
                    }
                
                for key, value in detail_data.items():
                    if key != "id": 
                        setattr(business_place_detail, key, value)

            else:
                # Insert a new business place detail
                work_order_business_place = WorkOrderBusinessPlaceDetails(**detail_data)
                db.add(work_order_business_place)
            # if detail_data.get('utility_document_id'):
            #     new_document = CustomerDataDocumentMaster(
            #         work_order_master_id=work_order_details.work_order_master_id,
            #         work_order_details_id=work_order_details_id,
            #         document_data_category_id=3,  # Assuming '3' is for PRINCIPAL PLACE DOC
            #         document_data_master_id=detail_data['utility_document_id'],
            #         is_deleted='no'
            #     )
            #     db.add(new_document)
            #         # print('new_document',new_document.id)
            # db.commit()
        # Set is_deleted to 'yes' for any existing business place details not in the incoming request
        for existing_detail in existing_business_place_details:
            if existing_detail.id not in incoming_ids:
                existing_detail.is_deleted = 'yes'

        db.commit()
        
          # Step: Update sub-services' constitution if the main service is a bundle
        if work_order_details.is_bundle_service == 'yes' and work_order_details.is_main_service == 'yes':
            # Fetch all sub-services with the same bundle_service_id
            
            sub_services = db.query(OffWorkOrderDetails).filter(
                OffWorkOrderDetails.bundle_service_id == work_order_details.id,
                OffWorkOrderDetails.is_main_service == 'no' ,
                OffWorkOrderDetails.is_deleted=='no' # Ensure we are updating only sub-services
            ).all()

            # Update constitution for each sub-service
            for sub_service in sub_services:
                sub_service.constitution_id = work_order_details.constitution_id

            db.commit()
        
        return {"message": "Work order set details saved successfully"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


#-------------------------------------------------------------------------------------------------
def get_work_order_service_details(
        db: Session,
        id: int
) -> List[Dict]:
    try:
        data = []

        # Query for work order details
        work_order_details_data = db.query(WorkOrderDetailsView).filter(
            WorkOrderDetailsView.is_deleted == 'no',
            WorkOrderDetailsView.work_order_details_id == id
        ).first()
        if not work_order_details_data:
            return []

        # Query for principal place data (Main Office)
        princypal_place_data = db.query(OffViewWorkOrderBusinessPlaceDetails).filter(
            OffViewWorkOrderBusinessPlaceDetails.work_order_details_id == id,
            OffViewWorkOrderBusinessPlaceDetails.is_deleted == 'no',
            OffViewWorkOrderBusinessPlaceDetails.business_place_type == 'Main Office'
        ).first()

        if princypal_place_data is None or princypal_place_data == []:
            princypal_place_data == []

        # Query for all business place details
        business_place_details_data = db.query(OffViewWorkOrderBusinessPlaceDetails).filter(
            OffViewWorkOrderBusinessPlaceDetails.work_order_details_id == id,
            OffViewWorkOrderBusinessPlaceDetails.is_deleted == 'no',
            OffViewWorkOrderBusinessPlaceDetails.business_place_type != 'Main Office'
        ).all()

        if business_place_details_data is None or business_place_details_data == []:
            business_place_details_data == []

        # Ensure principalPlaceDetails is always provided
        work_order_business_place_data = WorkOrderSetDetailsResponseSchema(
            workOrderDetails=OffViewWorkOrderDetailsSchema.model_validate(work_order_details_data),
            pricipalPlaceDetails=OffViewBusinessPlaceDetailsScheema.model_validate(princypal_place_data) if princypal_place_data else {},
            additionalPlaceDetails=[OffViewBusinessPlaceDetailsScheema.model_validate(detail) for detail in business_place_details_data] if business_place_details_data else [] 
        )


        data.append(work_order_business_place_data.model_dump())  # Convert the response schema to a dictionary
        return data

    except SQLAlchemyError as e:
        # Handle database exceptions
        raise HTTPException(status_code=500, detail=str(e))
     
#-------------------------------------------------------------------------------------------------------

def get_work_order_dependancy_service_details(
        db:Session ,
        work_order_details_id : int,
        work_order_master_id: int,
        is_main_service  = BooleanFlag

) :
   try: 
    # print("service data ================",is_main_service)
    existing_row =  db.query(WorkOrderDetailsView).filter(
        WorkOrderDetailsView.work_order_master_id == work_order_master_id,
        WorkOrderDetailsView.work_order_details_id == work_order_details_id,
         WorkOrderDetailsView.is_deleted == 'no',
         WorkOrderDetailsView.is_main_service == is_main_service).all()
    if not existing_row : 
         return {
        'message': 'No record found for the given work order master ID and work order details ID.'
    }
    if is_main_service == BooleanFlag.yes:
        service_data = db.query(WorkOrderDetailsView).filter(
            WorkOrderDetailsView.work_order_master_id == work_order_master_id,
            WorkOrderDetailsView.work_order_details_id != work_order_details_id,
            WorkOrderDetailsView.is_main_service =='yes',
            WorkOrderDetailsView.is_deleted == 'no'
        ).all()
        # print("service data ================",service_data)
        # return service_data
    else:
        query = db.query(WorkOrderDetailsView).filter(
            WorkOrderDetailsView.work_order_master_id == work_order_master_id,
            # WorkOrderDetailsView.bundle_service_id == work_order_details_id,
            WorkOrderDetailsView.work_order_details_id != work_order_details_id,
            WorkOrderDetailsView.is_main_service=='no',
            WorkOrderDetailsView.is_deleted == 'no'
        )
        print(str(query.statement.compile(compile_kwargs={"literal_binds": True})))
        service_data = query.all()
        # print("service data ================",service_data)
    result = [
            {
                'work_order_details_id': service.work_order_details_id,
                'service_goods_master_id': service.service_goods_master_id,
                'service_goods_name': service.service_goods_name
            }
            for service in service_data
        ]
    return result
   except SQLAlchemyError as e:
        # Handle database exceptions
        raise HTTPException(status_code=500, detail=str(e))
    
#------------------------------------------------------------------------------------------------------------
def get_work_order_dependancy_by_work_order_details_id(
        db: Session,
        work_order_details_id: int
) -> List[Dict]:
    try:
        data = []

        # Query for work order details
        work_order_details_data = db.query(WorkOrderDetailsView).filter(
            WorkOrderDetailsView.is_deleted == 'no',
            WorkOrderDetailsView.work_order_details_id == work_order_details_id  # Corrected variable name
        ).first()

        if not work_order_details_data:
            raise HTTPException(status_code=404, detail="Service not found")  # Raising an exception for consistency

        # Query for work order dependencies
        
        dependancy_details_data= get_dependencies(db,work_order_details_id)
        # Create response object
        work_order_dependancy_data = WorkOrderDependancyResponseSchema(
            workOrderDetails=OffViewWorkOrderDetailsSchema.model_validate(work_order_details_data),
            dipendancies=[WorkOrderDependancySchema.model_validate(detail) for detail in dependancy_details_data]
        )

        data.append(work_order_dependancy_data.model_dump())  # Convert the response schema to a dictionary
        return data

    except SQLAlchemyError as e:
        # Handle database exceptions
        raise HTTPException(status_code=500, detail=str(e))
  

#--------------------------------------------------------------------------------------------------------------

# def update_customer_data_documents(
#     update_data: List[UpdateCustomerDataDocumentSchema],
#     db: Session
# ):
#     try:
#         for data in update_data:
#             record = db.query(CustomerDataDocumentMaster).filter(
#                 CustomerDataDocumentMaster.id == data.id,
#                 CustomerDataDocumentMaster.is_deleted == 'no'
#             ).first()

#             if not record:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail=f"Record with id {data.id} not found."
#                 )

#             # Update fields
#             record.data = data.data
#             record.valid_from_date = data.valid_from_date if data.valid_from_date is not None else None
#             record.valid_to_date = data.valid_to_date if data.valid_to_date is not None else None

#             db.commit()
#             db.refresh(record)
        
#         return True  # Indicating success

#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def update_customer_data_documents(
    update_data: List[UpdateCustomerDataDocumentSchema],
    db: Session
) -> bool:
    try:
        for data in update_data:
            record = db.query(CustomerDataDocumentMaster).filter(
                CustomerDataDocumentMaster.id == data.id,
                CustomerDataDocumentMaster.is_deleted == 'no'
            ).first()

            if not record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Record with id {data.id} not found."
                )

            # Update the data field
            record.data = data.data
            
            # Update the dates based on the provided data model_fields_set
            if 'valid_from_date' in data.__fields_set__: 
                
                record.valid_from_date = data.valid_from_date  # Set to NULL if null is provided
            if 'valid_to_date' in data.__fields_set__:
                record.valid_to_date = data.valid_to_date  # Set to NULL if null is provided

            db.commit()
            db.refresh(record)
        
        return True  # Indicating success

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

#----------------------------------------------------------------------------------------------------------------------
def upload_documents(db: Session, 
                     request: DocumentsSchema,
                       id: int, 
                       user_id: int, 
                       file: UploadFile = None):
    try:
        # Update the document record
        document_data = request.dict()  # Assuming request is a Pydantic model
        document = db.query(CustomerDataDocumentMaster).filter_by(id=id).first()

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        document.valid_from_date = request.valid_from_date
        document.valid_to_date = request.valid_to_date
        document.remarks = request.remarks
        document.uploaded_date = datetime.now()
        document.uploaded_by = user_id
        document.is_document_uploded = 'yes'
        
        db.commit()
        db.refresh(document)

        # Handle file upload
        if file:
            # Extract original file name and extension
            original_file_name = Path(file.filename).stem
            file_extension = Path(file.filename).suffix

            # Construct file name and path
            # file_name = f"{id}_{original_file_name}{file_extension}"
            file_name = f"{id}{file_extension}"
            file_path = os.path.join(UPLOAD_WORK_ORDER_DOCUMENTS, file_name)

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        return document

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload the file: {str(e)}")
    
#---------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------



def update_service_task(
    db: Session, 
    task_id: int, 
    task_data: OffServiceTaskMasterSchema,
    user_id: int):
    # Fetch the existing task
    task = db.query(OffServiceTaskMaster).filter(OffServiceTaskMaster.id == task_id, OffServiceTaskMaster.is_deleted == 'no').first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Update the task details
    task.task_status_id = task_data.task_status_id
    task.remarks = task_data.remarks
   
    
    # Insert into the service task history table
    task_history = OffServiceTaskHistory(
        service_task_master_id=task.id,
        history_updated_on=datetime.now(),
        history_update_by=user_id,
        history_description=task_data.remarks
    )

    db.add(task_history)  # Add the history record to the session
    db.commit()           # Commit all changes (both task update and history insert)
    db.refresh(task)     

    return task

#-----------------------------------------------------------------


def get_all_service_task_list(
    db: Session,
    task_no: Optional[str] = None,
    department_id: Union[int, str] = "ALL",
    team_id: Union[int, str] = "ALL",
    employee_id: Union[int, str] = "ALL",
    status_id: Union[int, str] = "ALL",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List[OffViewServiceTaskMasterSchema]:

    query = db.query(OffViewServiceTaskMaster)

    if task_no:
        query = query.filter(OffViewServiceTaskMaster.task_number.ilike(f"%{task_no}%"))
    
    if department_id != "ALL":
        query = query.filter(OffViewServiceTaskMaster.department_allocated_to == department_id)
    
    if team_id != "ALL":
        query = query.filter(OffViewServiceTaskMaster.team_allocated_to == team_id)
    
    if employee_id != "ALL":
        query = query.filter(OffViewServiceTaskMaster.employee_allocated_to == employee_id)
    
    if status_id != "ALL":
        query = query.filter(OffViewServiceTaskMaster.task_status_id == status_id)
    
    if from_date:
        query = query.filter(func.date(OffViewServiceTaskMaster.allocated_on) >= from_date)
    
    if to_date:
        query = query.filter(func.date(OffViewServiceTaskMaster.allocated_on) <= to_date)

    # Ensure that is_deleted is not equal to 'yes'
    query = query.filter(OffViewServiceTaskMaster.is_deleted == 'no')
    
    results = query.all()

    for task in results:
        task.employee_allocated_first_name = task.employee_allocated_first_name or ""
        task.employee_allocated_middle_name = task.employee_allocated_middle_name or ""
        task.employee_allocated_last_name = task.employee_allocated_last_name or ""
        task.team_name = task.team_name or ""
        task.department_name = task.department_name or ""
        task.task_status = task.task_status or ""
        task.task_priority = task.task_priority or ""
        task.allocated_by_first_name = task.allocated_by_first_name or ""
        task.allocated_by_middle_name = task.allocated_by_middle_name or ""
        task.allocated_by_last_name = task.allocated_by_last_name or ""
        task.remarks = task.remarks or ""
         

    return results




# def get_all_service_task_list(
#     db: Session,
#     task_no: Optional[str] = None,
#     department_id: Union[int, str] = "ALL",
#     team_id: Union[int, str] = "ALL",
#     employee_id: Union[int, str] = "ALL",
#     status_id: Union[int, str] = "ALL",
#     from_date: Optional[date] = None,
#     to_date: Optional[date] = None
# ) -> List[OffViewServiceTaskMasterSchema]:

#     query = db.query(OffViewServiceTaskMaster)

#     if task_no:
#         query = query.filter(OffViewServiceTaskMaster.task_number.ilike(f"%{task_no}%"))
    
#     if department_id != "ALL":
#         query = query.filter(OffViewServiceTaskMaster.department_allocated_to == department_id)
    
#     if team_id != "ALL":
#         query = query.filter(OffViewServiceTaskMaster.team_allocated_to == team_id)
    
#     if employee_id != "ALL":
#         query = query.filter(OffViewServiceTaskMaster.employee_allocated_to == employee_id)
    
#     if status_id != "ALL":
#         query = query.filter(OffViewServiceTaskMaster.task_status_id == status_id)
    
#     if from_date:
#         query = query.filter(func.date(OffViewServiceTaskMaster.allocated_on) >= from_date)
    
#     if to_date:
#         query = query.filter(func.date(OffViewServiceTaskMaster.allocated_on) <= to_date)

#     # Ensure that is_deleted is not equal to 'yes'
#     query = query.filter(OffViewServiceTaskMaster.is_deleted == 'no')
    
#     results = query.all()

#     # Convert SQLAlchemy model instances to Pydantic schema
#     tasks = []
#     for task in results:
#         task.employee_allocated_first_name = task.employee_allocated_first_name or ""
#         task.employee_allocated_middle_name = task.employee_allocated_middle_name or ""
#         task.employee_allocated_last_name = task.employee_allocated_last_name or ""
#         task.team_name = task.team_name or ""
#         task.department_name = task.department_name or ""
#         task.task_status = task.task_status or ""
#         task.task_priority = task.task_priority or ""
#         task.allocated_by_first_name = task.allocated_by_first_name or ""
#         task.allocated_by_middle_name = task.allocated_by_middle_name or ""
#         task.allocated_by_last_name = task.allocated_by_last_name or ""
#         task.remarks = task.remarks or ""

#         # Append the converted Pydantic schema
#         tasks.append(OffViewServiceTaskMasterSchema.from_orm(task))

#     return tasks


#----------------------------------------------------------------------------

def assign_reassign_service_task(
    db: Session,
    task_id: int,
    assign_to: str,
    task_data: ServiceTaskMasterAssign,
    user_id: int
):
   
    
    # Retrieve the task from the database
    task = (db.query(OffServiceTaskMaster)
    .filter(OffServiceTaskMaster.id == task_id,OffServiceTaskMaster.is_deleted == 'no').first())

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Update the task based on the assignment type
    if assign_to == "DEPARTMENT":
        task.department_allocated_to = task_data.department_id
        task.team_allocated_to = None
        task.employee_allocated_to = None
    elif assign_to == "TEAM":
        task.department_allocated_to = task_data.department_id
        task.team_allocated_to = task_data.team_id
        task.employee_allocated_to = None
    elif assign_to == "EMPLOYEE":
        task.department_allocated_to = task_data.department_id
        task.team_allocated_to = task_data.team_id
        task.employee_allocated_to = task_data.employee_id

    # Update remarks, modified_by, and modified_on fields
    task.remarks = task_data.remarks
    
    
    # Insert into the ServiceTaskHistory table
    history_entry = OffServiceTaskHistory(
        service_task_master_id=task.id,
        history_updated_on=datetime.now(),
        history_update_by=user_id,
        history_description=task_data.remarks
    )
    db.add(history_entry)

    db.commit()

#----------------------------------------------------------------------------------------------
def get_sub_services_by_bundled_id(db: Session, bundled_service_goods_id: int):
    sub_services = (
        db.query(
            OffServiceGoodsDetails.id,
            OffServiceGoodsDetails.service_goods_master_id,
            OffServiceGoodsMaster.service_goods_name,
            OffServiceGoodsMaster.is_bundled_service
        )
        .join(OffServiceGoodsMaster, OffServiceGoodsDetails.service_goods_master_id == OffServiceGoodsMaster.id)
        .filter(OffServiceGoodsDetails.bundled_service_goods_id == bundled_service_goods_id)
        .filter(OffServiceGoodsDetails.is_deleted == 'no')
        .all()
    )
    
    # Constructing the response format
    response = [
        {
            "id": service_id,
            "service_goods_master_id":service_goods_master_id,
            "service_name": service_name,
            "is_bundled_service": is_bundled_service
        }
        for service_id,service_goods_master_id, service_name, is_bundled_service in sub_services
    ]
    
    return response

#---------------------------------------------------------------------------------------------------
def save_work_order_dependancies( 
         depended_works: List[CreateWorkOrderDependancySchema],
         action_type : RecordActionType,
         db: Session ,
         
):
    try:
            results = []   
        # with db.begin():
            if action_type == RecordActionType.INSERT_ONLY:

                
                # Save new records
                for work_order_dependancy in depended_works:
                    previouse_records = db.query(WorkOrderDependancy).filter(
                        WorkOrderDependancy.dependent_on_work_id == work_order_dependancy.dependent_on_work_id,
                        WorkOrderDependancy.work_order_details_id == work_order_dependancy.work_order_details_id,
                        WorkOrderDependancy.is_deleted == 'yes'
                    ).all()
                    if previouse_records:
                        for record in previouse_records:
                            record.is_deleted = 'no'
                            db.add(record)
                            db.commit()
                        db.refresh(record)
                        results.append(record.id)
                        
                    else:
                        new_record = WorkOrderDependancy(**work_order_dependancy.model_dump(exclude={"id"}))
                        db.add(new_record)
                        db.commit()
                        db.refresh(new_record)
                        results.append(new_record.id)

                        work_order_details = db.query(OffWorkOrderDetails).filter(
                            OffWorkOrderDetails.id == work_order_dependancy.work_order_details_id
                        ).first()
                        
                        if work_order_details:
                            work_order_details.is_depended_service = 'yes'
                            db.commit()
            elif action_type == RecordActionType.UPDATE_AND_INSERT:
            # Update existing records
                existing_records = db.query(WorkOrderDependancy).filter(
                    WorkOrderDependancy.work_order_details_id == depended_works[0].work_order_details_id,
                    WorkOrderDependancy.is_deleted == 'no'
                ).all()

                existing_ids = {record.id for record in existing_records}
                incoming_ids = {work_order_dependancy.id for work_order_dependancy in depended_works if work_order_dependancy.id}

                # Mark records as deleted if they are not in the incoming list
                records_to_delete = existing_ids - incoming_ids
                if records_to_delete:
                    db.query(WorkOrderDependancy).filter(
                        WorkOrderDependancy.id.in_(records_to_delete)
                    ).update({'is_deleted': 'yes'}, synchronize_session=False)
                    db.commit()

                # Update existing records or add new ones
                for work_order_dependancy in depended_works:
                    if work_order_dependancy.id and work_order_dependancy.id != 0:
                        existing_record = db.query(WorkOrderDependancy).filter(
                            WorkOrderDependancy.id == work_order_dependancy.id
                        ).first()

                        if not existing_record:
                            return {
                                'message': f"Work order dependency with id {work_order_dependancy.id} not found",
                                'Success': 'false'
                            }

                        for key, value in work_order_dependancy.model_dump(exclude_unset=True).items():
                            setattr(existing_record, key, value)
                        
                        db.commit()
                        db.refresh(existing_record)
                        results.append(existing_record.id)

                    else:
                        # Add new dependency
                        new_record = WorkOrderDependancy(**work_order_dependancy.model_dump(exclude={"id"}))
                        db.add(new_record)
                        db.commit()
                        db.refresh(new_record)
                        results.append(new_record.id)

                        work_order_details = db.query(OffWorkOrderDetails).filter(
                            OffWorkOrderDetails.id == work_order_dependancy.work_order_details_id
                        ).first()

                        if work_order_details:
                            work_order_details.is_depended_service = 'yes'
                            db.commit()

         
    except SQLAlchemyError as e:
        db.rollback()  # Rollback the transaction in case of error
        raise HTTPException(status_code=500, detail="Failed to save or update work order dependencies. Error: " + str(e))
    return {
        'message': 'Successfully Saved' if results else 'No Records Processed',
        'Success': 'true' if results else 'false',
        'record_ids': results
    }
    # return results




# Function to save consultant schedule

 