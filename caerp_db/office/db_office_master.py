import logging
from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session
from caerp_constants.caerp_constants import  DeletedStatus, RecordActionType,SearchCriteria

from caerp_db.common.models import Employee
from caerp_db.hash import Hash
from typing import Dict, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm.session import Session
from caerp_db.office.models import OffAppointmentMaster, OffAppointmentPlaceOfBusiness, OffAppointmentRecommendationMaster, OffAppointmentStatus, OffAppointmentVisitMaster,OffAppointmentVisitDetails,OffAppointmentVisitMasterView,OffAppointmentVisitDetailsView,OffAppointmentCancellationReason, OffDocumentDataMaster, OffDocumentDataType, OffServiceDocumentDataDetails, OffServiceDocumentDataMaster, OffServiceGoodsDetails, OffServiceGoodsMaster, OffServiceGoodsPriceMaster, OffServices, OffViewConsultantDetails, OffViewConsultantMaster, OffViewServiceDocumentsDataDetails, OffViewServiceDocumentsDataMaster, OffViewServiceGoodsDetails, OffViewServiceGoodsMaster, OffViewServiceGoodsPriceMaster
from caerp_schema.office.office_schema import AppointmentStatusConstants, OffAppointmentDetails, OffAppointmentMasterViewSchema, OffAppointmentRecommendationMasterCreate, OffAppointmentVisitDetailsViewSchema, OffAppointmentVisitMasterViewSchema, OffDocumentDataMasterBase, OffViewServiceDocumentsDataDetailsDocCategory, OffViewServiceDocumentsDataDetailsSchema, OffViewServiceDocumentsDataMasterSchema, OffViewServiceGoodsDetailsDisplay, OffViewServiceGoodsMasterDisplay, PriceData, PriceHistoryModel, RescheduleOrCancelRequest, ResponseSchema,AppointmentVisitDetailsSchema, SaveServiceDocumentDataMasterRequest, SaveServicesGoodsMasterRequest,  ServiceModel, ServiceModelSchema, ServicePriceHistory, Slot
from typing import Union,List
from sqlalchemy import and_,or_
# from caerp_constants.caerp_constants import SearchCriteria
from fastapi import logger
from sqlalchemy.exc import IntegrityError,OperationalError
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
                # Append new remarks with newline separation
                if field == "remarks":
                    if visit_master.remarks:
                        setattr(visit_master, field, visit_master.remarks + "\n" + value)
                    else:
                        setattr(visit_master, field, value)
                else:
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
                            "bundled_service_goods_id": new_master.id,
                            "created_by": user_id,
                            "created_on": datetime.utcnow()
                        })
                        new_detail = OffServiceGoodsDetails(**new_detail_data)
                        db.add(new_detail)

            db.commit()
            return {"success": True, "message": "Saved successfully", "action": "insert"}

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
                existing_details = db.query(OffServiceGoodsDetails).filter(
                    OffServiceGoodsDetails.bundled_service_goods_id == existing_master.id
                ).all()

                existing_detail_dict = {detail.service_goods_master_id: detail for detail in existing_details}

                incoming_detail_dict = {detail.service_goods_master_id: detail for detail in data.details}

                # Update or add new details
                for detail_data in data.details:
                    detail_data_dict = detail_data.dict()
                    existing_detail = existing_detail_dict.get(detail_data.service_goods_master_id)

                    if existing_detail:
                        for key, value in detail_data_dict.items():
                            setattr(existing_detail, key, value)
                        existing_detail.modified_by = user_id
                        existing_detail.modified_on = datetime.utcnow()
                    else:
                        new_detail_data = detail_data_dict
                        new_detail_data.update({
                            "bundled_service_goods_id": existing_master.id,
                            "created_by": user_id,
                            "created_on": datetime.utcnow()
                        })
                        new_detail = OffServiceGoodsDetails(**new_detail_data)
                        db.add(new_detail)

                # Remove details that are no longer in the update request
                for service_goods_master_id, existing_detail in existing_detail_dict.items():
                    if service_goods_master_id not in incoming_detail_dict:
                        db.delete(existing_detail)

            db.commit()
            return {"success": True, "message": "Updated successfully", "action": "update"}

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

#---------------------------------------------------------------------------------------------------------------
def reschedule_or_cancel_appointment(db: Session,
                                     request_data: RescheduleOrCancelRequest,
                                     action: AppointmentStatusConstants, 
                                     visit_master_id: int):
    appointment = db.query(OffAppointmentVisitMaster).filter(OffAppointmentVisitMaster.id == visit_master_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
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
        raise HTTPException(status_code=404, detail=f"Status '{status_name}' not found")
    status_id = status.id

    if action == AppointmentStatusConstants.RESCHEDULED:
        if not request_data.date or not request_data.time:
            raise HTTPException(status_code=400, detail="Date and time are required for rescheduling")
        # Update appointment status to RESCHEDULED and update date and time
        appointment.appointment_status_id = status_id
        appointment.appointment_date = request_data.date
        appointment.appointment_time_from = request_data.time
        if appointment.remarks:
            appointment.remarks += f"\n{request_data.description}"
        else:
            appointment.remarks = request_data.description
        db.commit()
        return {"success": True, "message": "Appointment rescheduled successfully"}
    
    elif action == AppointmentStatusConstants.CANCELED:
        # Update appointment status to CANCELED
        appointment.appointment_status_id = status_id
        if appointment.remarks:
            appointment.remarks += f"\n{request_data.description}"
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



#---service-goods-master-------------------------------------------------------------------------------------

def get_all_service_goods_master(
    db: Session,
    deleted_status: Optional[str] = None,
    name: Optional[str] = None,
    group_id: Union[int, str] = 'ALL',
    sub_group_id: Union[int, str] = 'ALL',
    category_id: Union[int, str] = 'ALL',
    sub_category_id: Union[int, str] = 'ALL'
) -> List[OffViewServiceGoodsMasterDisplay]:
    try:
        # Initialize search conditions
        search_conditions = []

        # Apply filter conditions
        if deleted_status == DeletedStatus.DELETED:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'yes')
        elif deleted_status == DeletedStatus.NOT_DELETED:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_master_is_deleted == 'no')

        if name:
            search_conditions.append(OffViewServiceGoodsMaster.service_goods_name.ilike(f'%{name}%'))

        if group_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.group_id == group_id)

        if sub_group_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.sub_group_id == sub_group_id)

        if category_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.category_id == category_id)

        if sub_category_id != 'ALL':
            search_conditions.append(OffViewServiceGoodsMaster.sub_category_id == sub_category_id)

        # Execute the query with the combined conditions
        query_result = db.query(OffViewServiceGoodsMaster).filter(and_(*search_conditions)).all()

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
            details_dict[detail.bundled_service_goods_id].append(OffViewServiceGoodsDetailsDisplay(**vars(detail)))

        # Convert ORM results to Pydantic models and return
        return [
            OffViewServiceGoodsMasterDisplay(
                **{k: v for k, v in result.__dict__.items() if k != '_sa_instance_state'},
                details=details_dict.get(result.service_goods_master_id, None)
            )
            for result in query_result
        ]

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


 


# #-----------------------
def save_service_document_data_master(
    db: Session,
    id: int,
    doc_data: SaveServiceDocumentDataMasterRequest,
    user_id: int,
    action_type: RecordActionType
):
    if action_type == RecordActionType.INSERT_ONLY and id != 0:
        raise HTTPException(status_code=400, detail="Invalid action: For INSERT_ONLY, id should be 0")
    elif action_type == RecordActionType.UPDATE_ONLY and id <= 0:
        raise HTTPException(status_code=400, detail="Invalid action: For UPDATE_ONLY, id should be greater than 0")

    try:
        if action_type == RecordActionType.INSERT_ONLY:
            new_master_data = doc_data.Service.dict()
            new_master = OffServiceDocumentDataMaster(**new_master_data)
            db.add(new_master)
            db.flush()  # Ensure new_master.id is available for details

            if doc_data.Documents:
                for document in doc_data.Documents:
                    if not isinstance(document.details, list):
                        raise HTTPException(status_code=400, detail="Details should be a list")

                    for detail in document.details:
                        new_detail_data = detail.dict()
                        new_detail_data.update({
                            "document_data_category_id": document.document_data_category_id,
                            "service_document_data_id": new_master.id,
                            "is_deleted": 'no'
                        })
                        new_detail = OffServiceDocumentDataDetails(**new_detail_data)
                        db.add(new_detail)

            db.commit()
            return {"success": True, "message": "Saved successfully", "action": "insert"}

        elif action_type == RecordActionType.UPDATE_ONLY:
            existing_master = db.query(OffServiceDocumentDataMaster).filter(OffServiceDocumentDataMaster.id == id).first()
            if not existing_master:
                raise HTTPException(status_code=404, detail="Master record not found")

            for key, value in doc_data.Service.dict().items():
                setattr(existing_master, key, value)

            db.query(OffServiceDocumentDataDetails).filter(OffServiceDocumentDataDetails.service_document_data_id == id).delete()

            if doc_data.Documents:
                for document in doc_data.Documents:
                    if not isinstance(document.details, list):
                        raise HTTPException(status_code=400, detail="Details should be a list")

                    for detail in document.details:
                        new_detail_data = detail.dict()
                        new_detail_data.update({
                            "document_data_category_id": document.document_data_category_id,
                            "service_document_data_id": id
                        })
                        new_detail = OffServiceDocumentDataDetails(**new_detail_data)
                        db.add(new_detail)

            db.commit()
            return {"success": True, "message": "Updated successfully", "action": "update"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
#-------------------------------

def save_off_document_master(
    db: Session,
    id: int,
    data: OffDocumentDataMasterBase,
    type: str,
    action_type: RecordActionType
):
    if action_type == RecordActionType.INSERT_ONLY:
        if id != 0:
            raise HTTPException(status_code=400, detail="Invalid action: For INSERT_ONLY, id should be 0")
    elif action_type == RecordActionType.UPDATE_ONLY:
        if id <= 0:
            raise HTTPException(status_code=400, detail="Invalid action: For UPDATE_ONLY, id should be greater than 0")
    else:
        raise HTTPException(status_code=400, detail="Invalid action type")
    
    try:
        # Retrieve the document type record based on the provided type
        document_type_record = db.query(OffDocumentDataType).filter(
            OffDocumentDataType.document_data_type == type
        ).first()

        if not document_type_record:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        document_data_type_id = document_type_record.id
        
        if action_type == RecordActionType.INSERT_ONLY:
            document_master = OffDocumentDataMaster(
                **data.dict(),
                document_data_type_id=document_data_type_id
            )
            db.add(document_master)
            db.commit()
            db.refresh(document_master)
            return {"success": True, "message": "Saved successfully"}
        elif action_type == RecordActionType.UPDATE_ONLY:
            document = db.query(OffDocumentDataMaster).filter(OffDocumentDataMaster.id == id).first()
            if not document:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with id {id} not found")
            
            # Update the document type if needed
            if document.document_data_type_id != document_data_type_id:
                document.document_data_type_id = document_data_type_id
            
            # Update other fields
            for key, value in data.dict().items():
                setattr(document, key, value)
            
            db.commit()
            db.refresh(document)
            return {"success": True, "message": "Updated successfully"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Integrity error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



#-----------Aparna----------------------------------------------------------------------------------------------



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



#---------------------------------------------------------------------------------------------------------------
def get_all_service(db: Session) -> List[OffViewConsultantDetails]:

    return db.query(OffViewConsultantDetails).all()


#---------------------------------------------------------------------------------------------------------------

def get_consultants_for_service(db: Session, service_id: int) -> List[OffViewConsultantDetails]:
    # Query the database to get consultants for the given service_id
    consultants = db.query(OffViewConsultantDetails).filter(OffViewConsultantDetails.service_goods_master_id == service_id).all()
    return consultants


#---------------------------------------------------------------------------------------------------------------
def get_all_services_by_consultant_id(db: Session, consultant_id: int) -> List[OffViewConsultantDetails]:
    print(f"Running query for consultant ID {consultant_id}")  # Debug print
    services = db.query(OffViewConsultantDetails).filter(OffViewConsultantDetails.consultant_id == consultant_id).all()
    print(f"Query result for consultant ID {consultant_id}: {services}")  # Debug print
    return services


#---------------APARNA------------------------------------------------------------------------------------------
def get_all_services(db: Session) -> List[OffViewServiceGoodsPriceMaster]:
    """
    Fetch all services or goods from the off_view_service_goods_price_master table.
    """
    return db.query(OffViewServiceGoodsPriceMaster).all()

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



# def get_service_data(service_id: int, db: Session) -> List[ServiceModel]:
#     query_result = db.execute("""
#         SELECT
#             a.id AS constitution_id,
#             a.business_constitution_name,
#             a.business_constitution_code,
#             b.id AS service_goods_master_id,
#             b.service_goods_name,
#             c.service_charge,
#             c.govt_agency_fee,
#             c.stamp_duty,
#             c.stamp_fee,
#             c.effective_from_date AS price_master_effective_from_date,
#             c.effective_to_date AS price_master_effective_to_date
#         FROM
#             app_business_constitution AS a
#         LEFT OUTER JOIN
#             off_service_goods_master AS b ON TRUE
#         LEFT OUTER JOIN
#             off_service_goods_price_master AS c ON b.id = c.service_goods_master_id AND a.id = c.constitution_id
#         WHERE
#             b.id = :service_id
#         ORDER BY
#             a.id, b.id;
#     """, {"service_id": service_id}).fetchall()

#     service_data = []
#     for row in query_result:
#         service_data.append(ServiceModel(
#             id=row.constitution_id,
#             service_name=row.service_goods_name,
#             constitution_id=row.constitution_id,
#             business_constitution_name=row.business_constitution_name,
#             business_constitution_code=row.business_constitution_code,
#             service_charge=row.service_charge if row.service_charge is not None else 0,
#             govt_agency_fee=row.govt_agency_fee if row.govt_agency_fee is not None else 0,
#             stamp_duty=row.stamp_duty if row.stamp_duty is not None else 0,
#             stamp_fee=row.stamp_fee if row.stamp_fee is not None else 0,
#             effective_from_date=row.price_master_effective_from_date,
#             effective_to_date=row.price_master_effective_to_date,
#             service_description=None  # Add description if available in the database
#         ))

#     return service_data
#---------------------------------------------------------------------------------------------------------------
# def get_service_data(service_id: int, db: Session) -> List[ServiceModel]:
#     query_result = db.execute("""
#         SELECT
#             a.id AS constitution_id,
#             a.business_constitution_name,
#             a.business_constitution_code,
#             b.id AS service_goods_master_id,
#             COALESCE(c.id, 0) AS service_goods_price_master_id,
#             b.service_goods_name,
#             COALESCE(c.service_charge, 0) AS service_charge,
#             COALESCE(c.govt_agency_fee, 0) AS govt_agency_fee,
#             COALESCE(c.stamp_duty, 0) AS stamp_duty,
#             COALESCE(c.stamp_fee, 0) AS stamp_fee,
#             c.effective_from_date AS price_master_effective_from_date,
#             c.effective_to_date AS price_master_effective_to_date
#         FROM
#             app_business_constitution AS a
#         LEFT OUTER JOIN
#             off_service_goods_master AS b ON TRUE
#         LEFT OUTER JOIN
#             off_service_goods_price_master AS c ON b.id = c.service_goods_master_id 
#                                                  AND a.id = c.constitution_id
#                                                  AND (c.effective_to_date IS NULL OR c.effective_to_date >= CURRENT_DATE)
#                                                  AND c.effective_from_date <= CURRENT_DATE
#         WHERE
#             b.id = :service_id
#         ORDER BY
#             a.id, b.id;
#     """, {"service_id": service_id}).fetchall()

#     service_data_dict = {}
#     for row in query_result:
#         if row.constitution_id not in service_data_dict:
#             service_data_dict[row.constitution_id] = {
#                 "id": row.service_goods_master_id,
#                 "service_name": row.service_goods_name,
#                 "constitution_id": row.constitution_id,
#                 "business_constitution_name": row.business_constitution_name,
#                 "business_constitution_code": row.business_constitution_code,
#                 "price_history": []
#             }
        
#         service_data_dict[row.constitution_id]["price_history"].append({
#             "service_goods_price_master_id": row.service_goods_price_master_id,
#             "service_charge": row.service_charge,
#             "govt_agency_fee": row.govt_agency_fee,
#             "stamp_duty": row.stamp_duty,
#             "stamp_fee": row.stamp_fee,
#             "effective_from_date": row.price_master_effective_from_date,
#             "effective_to_date": row.price_master_effective_to_date
#         })
    
#     service_data = [ServiceModel(**data) for data in service_data_dict.values()]
#     return service_data

def get_service_data(service_id: int, db: Session) -> List[ServiceModelSchema]:
    query_result = db.execute("""
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
            c.effective_from_date AS price_master_effective_from_date,
            c.effective_to_date AS price_master_effective_to_date
        FROM
            app_business_constitution AS a
        LEFT OUTER JOIN
            off_service_goods_master AS b ON TRUE
        LEFT OUTER JOIN
            off_service_goods_price_master AS c ON b.id = c.service_goods_master_id 
                                                 AND a.id = c.constitution_id
                                                 AND (c.effective_to_date IS NULL OR c.effective_to_date >= CURRENT_DATE)
                                                 AND c.effective_from_date <= CURRENT_DATE
        WHERE
            b.id = :service_id
        ORDER BY
            a.id, b.id;
    """, {"service_id": service_id}).fetchall()

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
            price_master_effective_from_date=row.price_master_effective_from_date,
            price_master_effective_to_date=row.price_master_effective_to_date
        ) for row in query_result
    ]
    
    return service_data


#---------------------------------------------------------------------------------------------------------------

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
def save_price_data(price_data: PriceData, user_id: int, db: Session):
    new_price = OffServiceGoodsPriceMaster(
        service_goods_master_id=price_data.service_goods_master_id,
        constitution_id=price_data.constitution_id,
        service_charge=price_data.service_charge,
        govt_agency_fee=price_data.govt_agency_fee,
        stamp_duty=price_data.stamp_duty,
        stamp_fee=price_data.stamp_fee,
        effective_from_date=price_data.effective_from_date,
        effective_to_date=price_data.effective_to_date,
        created_by=user_id,
        created_on=datetime.now()
    )
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price
#-------------------------------------------------------------------------------------------------------
def get_all_service_document_data_master(
    db: Session,
    deleted_status: Optional[str] = None,
    name: Optional[str] = None,
    group_id: Union[int, str] = 'ALL',
    sub_group_id: Union[int, str] = 'ALL',
    category_id: Union[int, str] = 'ALL',
    sub_category_id: Union[int, str] = 'ALL',
    constitution_id: Union[int, str] = 'ALL',
    doc_data_status: Optional[str] = None  # New parameter
) -> List[dict]:
    try:
        search_conditions = []

        if deleted_status:
            if deleted_status == 'DELETED':
                search_conditions.append(OffViewServiceDocumentsDataMaster.service_goods_master_is_deleted == 'yes')
            elif deleted_status == 'NOT_DELETED':
                search_conditions.append(OffViewServiceDocumentsDataMaster.service_goods_master_is_deleted == 'no')

        if name:
            search_conditions.append(OffViewServiceDocumentsDataMaster.service_goods_name.ilike(f'%{name}%'))

        if group_id != 'ALL':
            search_conditions.append(OffViewServiceDocumentsDataMaster.group_id == group_id)

        if sub_group_id != 'ALL':
            search_conditions.append(OffViewServiceDocumentsDataMaster.sub_group_id == sub_group_id)

        if category_id != 'ALL':
            search_conditions.append(OffViewServiceDocumentsDataMaster.category_id == category_id)

        if sub_category_id != 'ALL':
            search_conditions.append(OffViewServiceDocumentsDataMaster.sub_category_id == sub_category_id)

        if constitution_id != 'ALL':
            search_conditions.append(OffViewServiceDocumentsDataMaster.constitution_id == constitution_id)

        query = db.query(OffViewServiceDocumentsDataMaster).filter(and_(*search_conditions))

        master_dict = {}
        for master in query.all():
            master_data = OffViewServiceDocumentsDataMasterSchema.from_orm(master).dict()
            details_query = db.query(OffViewServiceDocumentsDataDetails).filter(
                OffViewServiceDocumentsDataDetails.service_document_data_id == master.service_document_data_master_id
            ).all()

            has_details = bool(details_query)
            master_data['doc_data_status'] = 'CONFIGURED' if has_details else 'NOT CONFIGURED'
            
            master_dict[master.service_document_data_master_id] = master_data
            master_dict[master.service_document_data_master_id]["details"] = {}

            for detail in details_query:
                category_id = detail.document_data_category_id
                if category_id not in master_dict[master.service_document_data_master_id]["details"]:
                    master_dict[master.service_document_data_master_id]["details"][category_id] = {
                        "document_data_category_id": detail.document_data_category_id,
                        "document_data_category_category_name": detail.document_data_category_category_name,
                        "details": []
                    }

                master_dict[master.service_document_data_master_id]["details"][category_id]["details"].append(
                    OffViewServiceDocumentsDataDetailsSchema.from_orm(detail)
                )

        results = [
            {**value, "details": list(value["details"].values())}
            for value in master_dict.values()
        ]

        # Apply doc_data_status filter
        if doc_data_status and doc_data_status != 'ALL':
            if doc_data_status == 'CONFIGURED':
                results = [res for res in results if res.get('doc_data_status') == 'CONFIGURED' and res['details']]
            elif doc_data_status == 'NOT CONFIGURED':
                results = [res for res in results if res.get('doc_data_status') == 'NOT CONFIGURED']

        return results

    except Exception as e:
        logging.error(f"Failed to retrieve data from database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#--------------------------------------------------------------------------------------------------------

def get_service_documents_data_details(db: Session, service_id: int, document_category: Optional[str] = None) -> List[OffViewServiceDocumentsDataDetailsDocCategory]:
    try:
        # Query to fetch service_document_data_master_id from master table
        master_query = db.query(OffViewServiceDocumentsDataMaster). \
            filter(OffViewServiceDocumentsDataMaster.service_goods_master_id == service_id). \
            first()

        if not master_query:
            return []  # Return empty list if no master record found for the given service_id

        service_document_data_master_id = master_query.service_document_data_master_id

        # Query to fetch details based on service_document_data_master_id and document_category
        details_query = db.query(OffViewServiceDocumentsDataDetails). \
            filter(OffViewServiceDocumentsDataDetails.service_document_data_id == service_document_data_master_id)

        if document_category:
            details_query = details_query.filter(
                OffViewServiceDocumentsDataDetails.document_data_category_category_name == document_category)

        results = details_query.all()
        
        return results

    except Exception as e:
        logging.error(f"Error fetching service documents details: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching service documents details: {e}")

#-----------------------------------------------------------------------------------------------





from sqlalchemy.orm import Query
def save_off_appointment_recommendation(
    db: Session,
    id: int,
    data: OffAppointmentRecommendationMasterCreate,
    user_id: int,
    action_type: RecordActionType
):
    try:
        if action_type == RecordActionType.INSERT_ONLY:
            if id != 0:
                raise HTTPException(status_code=400, detail="Invalid action: For INSERT_ONLY, id should be 0")

            # Save master data
            appointment_recommendation_master = OffAppointmentRecommendationMaster(
                created_by=user_id,
                created_on=datetime.utcnow(),
                appointment_master_id=data.appointment_master_id,
                visit_master_id=data.visit_master_id,
                service_goods_master_id=data.service_goods_master_id,
                constitution_id=data.constitution_id,
                has_branches_or_godowns=data.has_branches_or_godowns,
                number_of_branches_or_godowns=data.number_of_branches_or_godowns
            )
            db.add(appointment_recommendation_master)
            db.flush()

            # Save detail data
            for place_data in data.places_of_business:
                place_of_business = OffAppointmentPlaceOfBusiness(
                    appointment_recommendation_master_id=appointment_recommendation_master.id,
                    created_by=user_id,
                    created_on=datetime.utcnow(),
                    nature_of_possession_id=place_data.nature_of_possession_id,
                    utility_document_id=place_data.utility_document_id,
                    business_place_type=place_data.business_place_type,
                    is_main_office=place_data.is_main_office
                )
                db.add(place_of_business)

            db.commit()

        elif action_type == RecordActionType.UPDATE_ONLY:
            # Update OffAppointmentRecommendationMaster
            existing_master = db.query(OffAppointmentRecommendationMaster).filter_by(id=id).first()
            if not existing_master:
                raise HTTPException(status_code=404, detail="Existing master record not found")

            # Update master data
            master_update_data = data.dict(exclude={'places_of_business'})
            for key, value in master_update_data.items():
                setattr(existing_master, key, value)
            existing_master.modified_by = user_id
            existing_master.modified_on = datetime.utcnow()

            # Update OffAppointmentPlaceOfBusiness details
            for place_data in data.places_of_business:
                detail = db.query(OffAppointmentPlaceOfBusiness).filter_by(appointment_recommendation_master_id=id).first()
                if not detail:
                    raise HTTPException(status_code=404, detail="Detail not found for the appointment recommendation master")

                for key, value in place_data.dict(exclude_unset=True).items():
                    setattr(detail, key, value)
                detail.modified_by = user_id
                detail.modified_on = datetime.utcnow()

        db.commit()

    except HTTPException as http_error:
        db.rollback()
        raise http_error
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))