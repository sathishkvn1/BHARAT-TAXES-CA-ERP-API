from fastapi import HTTPException, UploadFile,status,Depends
from caerp_db.office.models import AppHsnSacClasses, AppHsnSacMaster, OffAppointmentVisitDetails, OffAvailableServices, OffServiceFrequency, AppStockKeepingUnitCode, Document_Master, OffServices, ViewOffAvailableServices, ViewOffServices
from sqlalchemy.orm import Session
from caerp_db.hash import Hash
from datetime import date, datetime, timedelta
from sqlalchemy.orm.session import Session
from caerp_schema.office.office_schema import DocumentMasterBase, HsnSacClassesDisplay, HsnSacMasterBase, HsnSacMasterDisplay, OffAvailableServicesDisplay, OffServicesDisplay, ServiceFrequencyDisplay, StockKeepingUnitCodeDisplay
from caerp_db.office.models import ServiceProvider
from caerp_schema.office.office_schema import ServiceProviderBase,ServiceDepartmentBase
from caerp_db.office.models import ServiceDepartments,AppBusinessActivityType,AppBusinessActivityMaster,AppBusinessConstitution
from caerp_schema.office.office_schema import BusinessActivityTypeBase,BusinessActivityMasterBase
from fastapi import HTTPException, status
from caerp_constants.caerp_constants import DeletedStatus,ActionType
from sqlalchemy import and_, between
import pandas as pd
import io
from sqlalchemy.exc import IntegrityError
from caerp_db.office.models import EnquirerType,EnquirerStatus,ServiceProcessingStatus,ConsultancyService,ViewOffConsultancyServices

from caerp_db.common.models import AppEducationalQualificationsMaster
from caerp_schema.office.office_schema import EducationalQualificationsBase,EnquirerTypeBase,OffConsultancyServicesDisplay,EnquirerStatusBase,EnquirerStatusDisplay,ServiceProcessingStatusBase,ServiceProcessingStatusDisplay
from caerp_db.office.models import OffAppointmentMaster, OffAppointmentVisitMaster,OffSourceOfEnquiry,OffAppointmentStatus,OffAppointmentVisitDetailsView, OffAppointmentVisitMasterView
from caerp_schema.office.office_schema import OffAppointmentDetails,OffSourceOfEnquiryBase,OffAppointmentStatusBase,OffAppointmentMasterView

#-------------------------------------document master------------------------------------------------------------------


def save_document(db: Session, document_data: DocumentMasterBase, id: int = 0):
    # Check if a document with the same name already exists and is not deleted
    existing_document = db.query(Document_Master).filter(
        Document_Master.document_name == document_data.document_name,
        Document_Master.is_deleted == "no"
    ).first()

    # If a document with the same name already exists
    if existing_document:
        # If updating and the existing document's ID is different from the ID being updated, or if adding a new document
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A document with the same name already exists.")

    # If creating a new document
    if id == 0:
        new_document = Document_Master(**document_data.dict())
        db.add(new_document)
    # If updating an existing document
    else:
        document = db.query(Document_Master).filter(Document_Master.id == id).first()
        if not document:
            raise HTTPException(status_code=404, detail=f'Document with id {id} not found')

        # Update Document_Master data
        for key, value in document_data.dict().items():
            setattr(document, key, value)

    db.commit()
    db.refresh(new_document if id == 0 else document)
    return new_document if id == 0 else document

#-----------by id-----------------------
def get_document(db: Session, 
                 id: int
                 ):
    document = db.query(Document_Master).filter(Document_Master.id == id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"document with id {id} not found"
        )

    return document
#-----------delete----------------
def delete_document_db(db: Session, id: int):
    document_delete = db.query(Document_Master).filter(Document_Master.id == id).first()

    if document_delete is None:
        raise HTTPException(status_code=404, detail="Document not found")

    document_delete.is_deleted = 'yes'

    db.commit()

    return {"message": "Document deleted successfully"}


#-----------------------------------Service Provider------------------------------------------------------

def save_service_provider(db: Session, service_pro_data: ServiceProviderBase, id: int):
    existing_service_provider = db.query(ServiceProvider).filter(
        ServiceProvider.service_provider == service_pro_data.service_provider,
        ServiceProvider.is_deleted == 'no'
    ).first()
    
    if existing_service_provider:
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A service provider with the same name already exists.")
    
    if id == 0:
        new_service_provider = ServiceProvider(**service_pro_data.dict())
        db.add(new_service_provider)
    else:
        service_provider = db.query(ServiceProvider).filter(ServiceProvider.id == id).first()
        if not service_provider:
            raise HTTPException(status_code=404, detail=f'Service provider with id {id} not found')

        for key, value in service_pro_data.dict().items():
            setattr(service_provider, key, value)

    db.commit()
    db.refresh(new_service_provider if id == 0 else service_provider)
    return new_service_provider if id == 0 else service_provider



#---------by id-------------------

def get_service_provider_id(db: Session, 
                            id: int
                            ):
    
    return db.query(ServiceProvider).filter(ServiceProvider.id == id).first()


#---------delete--------------
def delete_or_undelete_service_provider(db: Session, 
                           id: int,
                           Action: ActionType                           ):
    service_provider_delete = db.query(ServiceProvider).filter(ServiceProvider.id == id).first()

    if service_provider_delete is None:
        raise HTTPException(status_code=404, detail="service provider not found")
    if Action == ActionType.DELETE:
        service_provider_delete.is_deleted = 'yes'
        db.commit()

        return {
        "message": "Service Provider Deleted successfully",
        }
    elif Action == ActionType.UNDELETE:
        service_provider_delete.is_deleted = 'no'
        db.commit()

        return {
        "message": "Service Provider Undeleted successfully",
        }

    

#-----------------------------------Service Department------------------------------------------------------

def save_service_department(db: Session, service_dep_data: ServiceDepartmentBase, id: int):
    existing_service_dep = db.query(ServiceDepartments).filter(
        ServiceDepartments.service_department_name == service_dep_data.service_department_name,
        ServiceDepartments.is_deleted == 'no'
    ).first()
    
    if existing_service_dep:
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A service department with the same name already exists.")
    
    if id == 0:
        new_service_dep = ServiceDepartments(**service_dep_data.dict())
        db.add(new_service_dep)
    else:
        service_dep = db.query(ServiceDepartments).filter(ServiceDepartments.id == id).first()
        if not service_dep:
            raise HTTPException(status_code=404, detail=f'Service department with id {id} not found')

        for key, value in service_dep_data.dict().items():
            setattr(service_dep, key, value)

    db.commit()
    db.refresh(new_service_dep if id == 0 else service_dep)
    return new_service_dep if id == 0 else service_dep



#-----------by id-----------------

def get_service_department_id(db: Session, 
                            id: int
                            ):
    
    return db.query(ServiceDepartments).filter(ServiceDepartments.id == id).first()



def delete_or_undelete_service_departments(db: Session, 
                           id: int,
                           Action: ActionType                           
                           ):
    service_dep_delete = db.query(ServiceDepartments).filter(ServiceDepartments.id == id).first()

    if service_dep_delete is None:
        raise HTTPException(status_code=404, detail="Service Departments not found")
    if Action == ActionType.DELETE:
        service_dep_delete.is_deleted = 'yes'
        db.commit()
        return {
        "message": "Service Departments Deleted successfully",
        }

    elif Action == ActionType.UNDELETE: 
        service_dep_delete.is_deleted = 'no'
        db.commit()
        return {
        "message": "Service Departments Undeleted successfully",
        }

#-----------------------------------Business Activity Type------------------------------------------------------

def save_business_activity_type(db: Session, business_activity_type_data: BusinessActivityTypeBase, id: int):
    existing_activity_type = db.query(AppBusinessActivityType).filter(
        AppBusinessActivityType.business_activity_type == business_activity_type_data.business_activity_type,
        AppBusinessActivityType.is_deleted == 'no'
    ).first()
    
    if existing_activity_type:
        if id != 0 or id == 0:
            raise HTTPException(status_code=400, detail="A business activity type with the same name already exists.")
    
    if id == 0:
        new_business_activity_type = AppBusinessActivityType(**business_activity_type_data.dict())
        db.add(new_business_activity_type)
    else:
        business_activity_type = db.query(AppBusinessActivityType).filter(AppBusinessActivityType.id == id).first()
        if not business_activity_type:
            raise HTTPException(status_code=404, detail=f'Business activity type with id {id} not found')

        for key, value in business_activity_type_data.dict().items():
            setattr(business_activity_type, key, value)

    db.commit()
    db.refresh(new_business_activity_type if id == 0 else business_activity_type)
    return new_business_activity_type if id == 0 else business_activity_type


#--------by id-------------

def get_business_activity_type_id(db: Session, 
                            id: int
                            ):
    
    return db.query(AppBusinessActivityType).filter(AppBusinessActivityType.id == id).first()


#---------delete--------------
def delete_business_activity_type(db: Session, 
                           id: int,
                           ):
    business_activity_type_delete = db.query(AppBusinessActivityType).filter(AppBusinessActivityType.id == id).first()

    if business_activity_type_delete is None:
        raise HTTPException(status_code=404, detail="Business Activity Type not found")

    business_activity_type_delete.is_deleted = 'yes'
    

    db.commit()

    return {
        "message": "Business Activity Type Deleted successfully",
    }

#-----------------------------------Business Activity Master------------------------------------------------------

def save_business_activity_master(db: Session, business_activity_master_data: BusinessActivityMasterBase, id: int):
    existing_activity_master = db.query(AppBusinessActivityMaster).filter(
        AppBusinessActivityMaster.business_activity == business_activity_master_data.business_activity,
        AppBusinessActivityMaster.is_deleted == 'no'
    ).first()
    
    if existing_activity_master and (id != 0 or id == 0):
        raise HTTPException(status_code=400, detail="A business activity master with the same name already exists.")
    
    if id == 0:
        new_business_activity_master = AppBusinessActivityMaster(**business_activity_master_data.dict())
        db.add(new_business_activity_master)
    else:
        business_activity_master = db.query(AppBusinessActivityMaster).filter(AppBusinessActivityMaster.id == id).first()
        if not business_activity_master:
            raise HTTPException(status_code=404, detail=f'Business activity master with id {id} not found')

        for key, value in business_activity_master_data.dict().items():
            setattr(business_activity_master, key, value)

    db.commit()
    db.refresh(new_business_activity_master if id == 0 else business_activity_master)
    return new_business_activity_master if id == 0 else business_activity_master



#----by id-----------------

def get_business_activity_master_id(db: Session, id: int):
    query = db.query(
        AppBusinessActivityMaster.id,
        AppBusinessActivityMaster.business_activity,
        AppBusinessActivityType.business_activity_type
    ).join(
        AppBusinessActivityType,
        AppBusinessActivityMaster.business_activity_type_id == AppBusinessActivityType.id
    ).filter(AppBusinessActivityMaster.id == id).first()

    if not query:
        return None

    return {
        "id": query.id,
        "business_activity": query.business_activity,
        "business_activity_type": query.business_activity_type
    }


#---------delete--------------
def delete_business_activity_master(db: Session, 
                           id: int,
                           ):
    business_activity_master_delete = db.query(AppBusinessActivityMaster).filter(AppBusinessActivityMaster.id == id).first()

    if business_activity_master_delete is None:
        raise HTTPException(status_code=404, detail="Business Activity Master not found")

    business_activity_master_delete.is_deleted = 'yes'
    

    db.commit()

    return {
        "message": "Business Activity Master Deleted successfully",
    }

#-----------------------------------Educational Qualifications------------------------------------------------------

def save_educational_qualifications(db: Session, 
                                   educationalqualifications_data: EducationalQualificationsBase, 
                                   id: int):
    existing_educationalqualifications = db.query(AppBusinessActivityMaster).filter(
        AppEducationalQualificationsMaster.qualification == educationalqualifications_data.qualification,
        AppEducationalQualificationsMaster.is_deleted == 'no'
    ).first()
    
    if existing_educationalqualifications and (id != 0 or id == 0):
        raise HTTPException(status_code=400, detail="Educational Qualifications with the same name already exists.")
    
    if id == 0:
        new_educationalqualifications = AppEducationalQualificationsMaster(**educationalqualifications_data.dict())
        db.add(new_educationalqualifications)
    else:
        educational_qualifications = db.query(AppEducationalQualificationsMaster).filter(AppEducationalQualificationsMaster.id == id).first()
        if not educational_qualifications:
            raise HTTPException(status_code=404, detail=f'Educational Qualifications with id {id} not found')

        for key, value in educationalqualifications_data.dict().items():
            setattr(educational_qualifications, key, value)

    db.commit()
    db.refresh(new_educationalqualifications if id == 0 else educational_qualifications)
    return new_educationalqualifications if id == 0 else educational_qualifications

#----by id-----------------

def get_educational_qualifications_id(db: Session, 
                            id: int
                            ):
    
    return db.query(AppEducationalQualificationsMaster).filter(AppEducationalQualificationsMaster.id == id).first()


#---------delete--------------
def delete_educational_qualifications(db: Session, 
                           id: int,
                           ):
    educational_qualifications_delete = db.query(AppEducationalQualificationsMaster).filter(AppEducationalQualificationsMaster.id == id).first()

    if educational_qualifications_delete is None:
        raise HTTPException(status_code=404, detail="Educational Qualifications not found")

    educational_qualifications_delete.is_deleted = 'yes'
    

    db.commit()

    return {
        "message": "Educational Qualifications Deleted successfully",
    }


#-----------------------------------Enquirer Type------------------------------------------------------

def save_enquirer_type(db: Session, 
                                   enquirer_type_data: EnquirerTypeBase, 
                                   id: int):
    existing_enquirer_type = db.query(EnquirerType).filter(
        EnquirerType.person_type == enquirer_type_data.person_type,
        EnquirerType.is_deleted == 'no'
    ).first()
    
    if existing_enquirer_type and (id != 0 or id == 0):
        raise HTTPException(status_code=400, detail="Enquirer Type with the same name already exists.")
    
    if id == 0:
        new_enquirer_type = EnquirerType(**enquirer_type_data.dict())
        db.add(new_enquirer_type)
    else:
        enquirer_type = db.query(EnquirerType).filter(EnquirerType.id == id).first()
        if not enquirer_type:
            raise HTTPException(status_code=404, detail=f'Enquirer Type with id {id} not found')

        for key, value in enquirer_type_data.dict().items():
            setattr(enquirer_type, key, value)

    db.commit()
    db.refresh(new_enquirer_type if id == 0 else enquirer_type)
    return new_enquirer_type if id == 0 else enquirer_type


#----by id-----------------

def get_enquirer_type_id(db: Session, 
                            id: int
                            ):
    
    return db.query(EnquirerType).filter(EnquirerType.id == id).first()


#---------delete--------------
def delete_enquirer_type(db: Session, 
                           id: int,
                           ):
    enquirer_type_delete = db.query(EnquirerType).filter(EnquirerType.id == id).first()

    if enquirer_type_delete is None:
        raise HTTPException(status_code=404, detail="Enquirer Type not found")

    enquirer_type_delete.is_deleted = 'yes'
    

    db.commit()

    return {
        "message": "Enquirer Type Deleted successfully",
    }



#-----------------------------------Enquirer Status------------------------------------------------------

def save_enquirer_status(db: Session, 
                                   enquirer_status_data: EnquirerStatusBase, 
                                   id: int):
    existing_enquirer_status = db.query(EnquirerStatus).filter(
        EnquirerStatus.status == enquirer_status_data.status,
        EnquirerStatus.is_deleted == 'no'
    ).first()
    
    if existing_enquirer_status and (id != 0 or id == 0):
        raise HTTPException(status_code=400, detail="Enquirer Status with the same name already exists.")
    
    if id == 0:
        new_enquirer_status = EnquirerStatus(**enquirer_status_data.dict())
        db.add(new_enquirer_status)
    else:
        enquirer_status = db.query(EnquirerStatus).filter(EnquirerStatus.id == id).first()
        if not enquirer_status:
            raise HTTPException(status_code=404, detail=f'Enquirer Status with id {id} not found')

        for key, value in enquirer_status_data.dict().items():
            setattr(enquirer_status, key, value)

    db.commit()
    db.refresh(new_enquirer_status if id == 0 else enquirer_status)
    return new_enquirer_status if id == 0 else enquirer_status

#----by id-----------------

def get_enquirer_status_id(db: Session, 
                            id: int
                            ):
    
    return db.query(EnquirerStatus).filter(EnquirerStatus.id == id).first()


#---------delete--------------
def delete_enquirer_status(db: Session, 
                           id: int,
                           ):
    enquirer_status_delete = db.query(EnquirerStatus).filter(EnquirerStatus.id == id).first()

    if enquirer_status_delete is None:
        raise HTTPException(status_code=404, detail="Enquirer status not found")

    enquirer_status_delete.is_deleted = 'yes'
    

    db.commit()

    return {
        "message": "Enquirer Status Deleted successfully",
    }

#-----------------------------------Service Processing Status------------------------------------------------------

def save_service_processing_status(db: Session, 
                                   service_processing_status_data: ServiceProcessingStatusBase, 
                                   id: int):
    existing_service_processing_status = db.query(EnquirerStatus).filter(
        ServiceProcessingStatus.service_processing_status == service_processing_status_data.service_processing_status,
        ServiceProcessingStatus.is_deleted == 'no'
    ).first()
    
    if existing_service_processing_status and (id != 0 or id == 0):
        raise HTTPException(status_code=400, detail="Service Processing Status with the same name already exists.")
    
    if id == 0:
        new_service_processing_status = ServiceProcessingStatus(**service_processing_status_data.dict())
        db.add(new_service_processing_status)
    else:
        service_processing_status = db.query(ServiceProcessingStatus).filter(ServiceProcessingStatus.id == id).first()
        if not service_processing_status:
            raise HTTPException(status_code=404, detail=f'Service Processing Status with id {id} not found')

        for key, value in service_processing_status_data.dict().items():
            setattr(service_processing_status, key, value)

    db.commit()
    db.refresh(new_service_processing_status if id == 0 else service_processing_status)
    return new_service_processing_status if id == 0 else service_processing_status

#----by id-----------------

def get_service_processing_status_id(db: Session, 
                            id: int
                            ):
    
    return db.query(ServiceProcessingStatus).filter(ServiceProcessingStatus.id == id).first()


#---------delete--------------
def delete_or_undelete_service_processing_status(db: Session, 
                           id: int,
                           Action: ActionType                           ):
    service_processing_status_delete = db.query(ServiceProcessingStatus).filter(ServiceProcessingStatus.id == id).first()

    if service_processing_status_delete is None:
        raise HTTPException(status_code=404, detail="Service Processing Status not found")
    if Action == ActionType.DELETE:
      
        service_processing_status_delete.is_deleted = 'yes'
        db.commit()
        return {
        "message": "Service Processing Status Deleted successfully",
        }
    elif Action == ActionType.UNDELETE:  
      
        service_processing_status_delete.is_deleted = 'no'
        db.commit()
        return {
        "message": "Service Processing Status Undeleted successfully",
        }
    
#.........................................off_service_frequency......................................................
def save_service_frequency(db: Session, freq_data: ServiceFrequencyDisplay, id: int):
    # Check if the provided service frequency name already exists in the database
    existing_freq = db.query(OffServiceFrequency).filter(
        OffServiceFrequency.service_frequency == freq_data.service_frequency
    ).filter(OffServiceFrequency.is_deleted == "no").first()
    
    
    if existing_freq:
        # If an existing record with the same name and is_deleted == "no" is found,
        # raise an exception indicating that no creation or update should be done.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service frequency with this name already exists and is active."
        )

    if id == 0:
        # Create
        new_freq = OffServiceFrequency(**freq_data.dict())
        db.add(new_freq)
        db.commit()
        db.refresh(new_freq)
        return new_freq  

    else:
        # Update 
        document = db.query(OffServiceFrequency).filter(OffServiceFrequency.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Frequency with ID {id} not found')
        for key, value in freq_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document


def get_all_service_frequency(db: Session,deleted_status: DeletedStatus):
   
   query = db.query(OffServiceFrequency)

   if deleted_status == DeletedStatus.DELETED:
      query = query.filter(OffServiceFrequency.is_deleted == 'yes')
   elif deleted_status == DeletedStatus.NOT_DELETED:
      query = query.filter(OffServiceFrequency.is_deleted == 'no')
   elif deleted_status == DeletedStatus.ALL:
      pass

   return query.all()


def get_service_frequency_by_id(db: Session, id: int):
     
     return db.query(OffServiceFrequency).filter(OffServiceFrequency.id == id).first()



def delete_or_undelete_service_frequency(db: Session, id:int,Action: ActionType):
    try:
         # Check if the item exists
        freq= db.query(OffServiceFrequency).filter(OffServiceFrequency.id == id).first()
        if not freq:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"frequency with ID {id} does not exist")

        if Action == ActionType.DELETE:
      
           db.query(OffServiceFrequency).filter(OffServiceFrequency.id == id).update({
            "is_deleted": "yes" })
           db.commit()
           return "service frequency deleted successfully"

        elif Action == ActionType.UNDELETE:  
           db.query(OffServiceFrequency).filter(OffServiceFrequency.id == id).update({
            "is_deleted": "no"}) 
           db.commit()
           return "service frequency undeleted successfully"

        

    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)

#------------------------------app_stock_keeping_unit_code-----------------------------------------------------

def save_stock_keeping_unit_code(db: Session, unit_code_data: StockKeepingUnitCodeDisplay, id: int):
    
    existing_data = db.query(AppStockKeepingUnitCode).filter(
        AppStockKeepingUnitCode.unit_code == unit_code_data.unit_code
                      ).filter(AppStockKeepingUnitCode.is_deleted == "no").first()
    
    if existing_data:
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unit_code with this name already exists and is active."
        )
    if id == 0:
       # Create
        new_unit_code = AppStockKeepingUnitCode(** unit_code_data.dict())
        db.add(new_unit_code)
        db.commit()
        db.refresh(new_unit_code)
        return new_unit_code  

    else:
        # Update 
        document = db.query(AppStockKeepingUnitCode).filter(AppStockKeepingUnitCode.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'stock keeping unit code  with id {id} not found')
        for key, value in unit_code_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document  


def get_all_stock_keeping_unit_code(db: Session,deleted_status: DeletedStatus):
   
   query = db.query(AppStockKeepingUnitCode)

   if deleted_status == DeletedStatus.DELETED:
      query = query.filter(AppStockKeepingUnitCode.is_deleted == 'yes')
   elif deleted_status == DeletedStatus.NOT_DELETED:
      query = query.filter(AppStockKeepingUnitCode.is_deleted == 'no')
   elif deleted_status == DeletedStatus.ALL:
      pass

   return query.all()

def get_stock_keeping_unit_code_by_id(db: Session, id: int):
     
     return db.query(AppStockKeepingUnitCode).filter(AppStockKeepingUnitCode.id == id).first()



def delete_stock_keeping_unit_code(db: Session, id: int):
    try:
        # Check if the item exists
        unit_code = db.query(AppStockKeepingUnitCode).filter(AppStockKeepingUnitCode.id == id).first()
        if not unit_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock unit code with ID {id} does not exist")

        # Update the 'is_deleted' 
        db.query(AppStockKeepingUnitCode).filter(AppStockKeepingUnitCode.id == id).update({
            "is_deleted": "yes",
        })

        db.commit()
        return "Stock unit code deleted successfully"

    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)

#----------------------------------app_hsn_sac_classes-----------------------------------------------------


def save_hsn_sac_classes(db: Session, hsn_data: HsnSacClassesDisplay, id: int):
    
    existing_data = db.query(AppHsnSacClasses).filter(
        AppHsnSacClasses.hsn_sac_class == hsn_data.hsn_sac_class
                      ).filter(AppHsnSacClasses.is_deleted == "no").first()
    
    if existing_data:
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="hsn_sac_class with this name already exists and is active."
        )

    if id == 0:
       # Create
        new_hsn_class = AppHsnSacClasses(** hsn_data.dict())
        db.add(new_hsn_class)
        db.commit()
        db.refresh(new_hsn_class)
        return new_hsn_class  

    else:
        # Update 
        document = db.query(AppHsnSacClasses).filter(AppHsnSacClasses.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'hsn sac class with id {id} not found')
        for key, value in hsn_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document  


def get_all_hsn_sac_classes(db: Session,deleted_status: DeletedStatus):
   
   query = db.query(AppHsnSacClasses)

   if deleted_status == DeletedStatus.DELETED:
      query = query.filter(AppHsnSacClasses.is_deleted == 'yes')
   elif deleted_status == DeletedStatus.NOT_DELETED:
      query = query.filter(AppHsnSacClasses.is_deleted == 'no')
   elif deleted_status == DeletedStatus.ALL:
      pass

   return query.all()

def get_hsn_sac_class_by_id(db: Session, id: int):
     
     return db.query(AppHsnSacClasses).filter(AppHsnSacClasses.id == id).first()



def delete_hsn_sac_class(db: Session, id: int):
    try:
        # Check if the item exists
        unit_code = db.query(AppHsnSacClasses).filter(AppHsnSacClasses.id == id).first()
        if not unit_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hsn sac class with ID {id} does not exist")

        # Update the 'is_deleted6' 
        db.query(AppHsnSacClasses).filter(AppHsnSacClasses.id == id).update({
            "is_deleted": "yes",
        })

        db.commit()
        return "hsn sac class deleted successfully"

    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)

#----------------------------------------------------app_hsn_sac_master--------------------------------
    
def save_hsn_sac_master(db: Session, hsn_data: HsnSacMasterDisplay, id: int):
    
    
    if id == 0:
       # Create
        new_hsn_sac = AppHsnSacMaster(** hsn_data.dict())
        db.add(new_hsn_sac)
        db.commit()
        db.refresh(new_hsn_sac)
        return new_hsn_sac  

    else:
        # Update 
        document = db.query(AppHsnSacMaster).filter(AppHsnSacMaster.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'hsn sac with id {id} not found')
        for key, value in hsn_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document  








def get_all_hsn_sac_master(db: Session,deleted_status: DeletedStatus):
   
    query = db.query(AppHsnSacMaster, AppHsnSacClasses.hsn_sac_class).join(
        AppHsnSacClasses, AppHsnSacMaster.hsn_sac_class_id == AppHsnSacClasses.id)

    if deleted_status == "DELETED":
        hsn_sac = query.filter(AppHsnSacMaster.is_deleted == 'yes').all()
    elif deleted_status == "NOT DELETED":
        hsn_sac = query.filter(AppHsnSacMaster.is_deleted == 'no').all()
    else:
        hsn_sac = query.all()

    # Convert query results to schema objects
    hsn_sac_schema = []
    for hsn_sac_master, hsn_sac_class in hsn_sac:
        hsn_sac_schema.append(
            HsnSacMasterBase(
                id=hsn_sac_master.id,
                hsn_sac_code=hsn_sac_master.hsn_sac_code,
                hsn_sac_description=hsn_sac_master.hsn_sac_description,
                hsn_sac_class=hsn_sac_class,
                sku_code=hsn_sac_master.sku_code,
            )
        )

    return hsn_sac_schema


#----by id-----------------



def get_hsn_sac_by_id(db: Session, id: int):
    query = db.query(
        AppHsnSacMaster.id,
        AppHsnSacMaster.hsn_sac_code,
        AppHsnSacMaster.hsn_sac_description,
        AppHsnSacMaster.sku_code,
        AppHsnSacClasses.hsn_sac_class
    ).join(
        AppHsnSacClasses,
        AppHsnSacMaster.hsn_sac_class_id == AppHsnSacClasses.id  
    ).filter(AppHsnSacMaster.id == id).first()

    if not query:
        return None
    #sku_code = query.sku_code or ""
    return {
        "id": query.id,
        "hsn_sac_code": query.hsn_sac_code,
        "hsn_sac_description": query.hsn_sac_description,
        "sku_code": query.sku_code, 
        "hsn_sac_class": query.hsn_sac_class
    }
  




def delete_hsn_sac_master(db: Session, id: int):
    try:
        # Check if the item exists
        unit_code = db.query(AppHsnSacMaster).filter(AppHsnSacMaster.id == id).first()
        if not unit_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hsn sac with ID {id} does not exist")

        # Update the 'is_deleted' 
        db.query(AppHsnSacMaster).filter(AppHsnSacMaster.id == id).update({
            "is_deleted": "yes",
        })

        db.commit()
        return "hsn sac deleted successfully"

    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)


 


# async def save_csv_to_db(file: UploadFile, db: Session):
#     try:
#         # Read the uploaded file
#         contents = await file.read()

#         # Parse CSV data using pandas
#         try:
#             # Attempt to decode contents as UTF-8
#             df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
#         except UnicodeDecodeError:
#             # If decoding as UTF-8 fails, attempt to decode with errors='replace'
#             decoded_contents = contents.decode('utf-8', errors='replace')
#             df = pd.read_csv(io.StringIO(decoded_contents))

#         # Save DataFrame to the database table
#         try:
#             # Convert DataFrame to dictionary records
#             df_dict = df.where(pd.notnull(df), None).to_dict(orient='records')

#             # Insert data into the database 
#             with db.begin():
#                 for record in df_dict:
#                     # Cleanse each record before inserting
#                     record['hsn_sac_description'] = record['hsn_sac_description'].encode('latin1', 'ignore').decode('utf-8')
#                     # Set sku_code to None if it's null in the CSV file
#                     if pd.isnull(record['sku_code']):
#                         record['sku_code'] = None
#                     db.execute(AppHsnSacMaster.__table__.insert(), record)

#             return {"message": "Data saved successfully"}
#         except IntegrityError as e:
#             # If IntegrityError occurs due to duplicate entry
#             if 'Duplicate entry' in str(e):
#                 raise HTTPException(status_code=400, detail="Error: This data already exists in the table.")
#             else:
#                 raise HTTPException(status_code=500, detail=f"Failed to save data to the database: {str(e)}")
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to save data to the database: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to upload CSV and save to database: {str(e)}")

async def save_csv_to_db(file: UploadFile, db: Session):
    try:
        # Read the uploaded file
        contents = await file.read()

        # Parse CSV data using pandas
        try:
            # Attempt to decode contents as UTF-8
            df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
        except UnicodeDecodeError:
            # If decoding as UTF-8 fails, attempt to decode with errors='replace'
            decoded_contents = contents.decode('utf-8', errors='replace')
            df = pd.read_csv(io.StringIO(decoded_contents))

        # Save DataFrame to the database table
        try:
            # Convert DataFrame to dictionary records
            df_dict = df.where(pd.notnull(df), None).to_dict(orient='records')

            # Insert data into the database 
            with db.begin():
                for record in df_dict:
                    # Cleanse each record before inserting
                    for column in df.columns:
                        if pd.isnull(record[column]):
                            record[column] = None
                    record['hsn_sac_description'] = record['hsn_sac_description'].encode('latin1', 'ignore').decode('utf-8')
                    db.execute(AppHsnSacMaster.__table__.insert(), record)

            return {"message": "Data saved successfully"}
        except IntegrityError as e:
            # If IntegrityError occurs due to duplicate entry
            if 'Duplicate entry' in str(e):
                raise HTTPException(status_code=400, detail="Error: This data already exists in the table.")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to save data to the database: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save data to the database: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload CSV and save to database: {str(e)}")

#.........................................off_services......................................................

def save_off_services(db: Session, details: OffServicesDisplay, id: int):
    
    existing_data = db.query(OffServices).filter(
        OffServices.service_name == details.service_name
                      ).filter(OffServices.is_deleted == "no").first()
    
    if existing_data:
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="service with this name already exists and is active."
        )

    if id == 0:
    
        # Create
        new_service = OffServices(**details.dict())
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        return new_service  

    else:
        # Update 
        service = db.query(OffServices).filter(OffServices.id == id).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id {id} not found")
        for key, value in details.dict().items():
            setattr(service, key, value)

        db.commit()
        db.refresh(service)  
        return service  

def get_all_off_services(db: Session, deleted_status: DeletedStatus):
    query = db.query(ViewOffServices)
    
    if deleted_status == DeletedStatus.DELETED:
        query = query.filter(ViewOffServices.is_deleted == 'yes')
    elif deleted_status == DeletedStatus.NOT_DELETED:
        query = query.filter(ViewOffServices.is_deleted == 'no')
    
    return query.all()

def get_off_service_by_id(db: Session, id: int):
    return db.query(ViewOffServices).filter(ViewOffServices.service_master_id == id).first()

def delete_or_undelete_off_service(db: Session, id: int,Action: ActionType):
    try:
        service = db.query(OffServices).filter(OffServices.id == id).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with ID {id} does not exist")
        if Action == ActionType.DELETE:
           db.query(OffServices).filter(OffServices.id == id).update({
            "is_deleted": "yes",
           })

           db.commit()
           return "service  deleted successfully"
        
        elif Action == ActionType.UNDELETE:  
           db.query(OffServices).filter(OffServices.id == id).update({
            "is_deleted": "no",
           })

           db.commit()
           return "service  undeleted successfully"


    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)
    



#------------------------------off_available_services-----------------------------------------------------




def save_off_available_services(db: Session, details: OffAvailableServicesDisplay, id: int):
    # Query existing data
    existing_services  = db.query(OffAvailableServices).filter(
        OffAvailableServices.service_master_id == details.service_master_id,
        OffAvailableServices.is_deleted == "no",
        OffAvailableServices.effective_from_date.isnot(None)
    ).all()
    
    if existing_services:
        existing_from_dates = [service.effective_from_date for service in existing_services]
       #existing_to_dates = [service.effective_to_date for service in existing_services]
        existing_to_dates = [service.effective_to_date for service in existing_services if service.effective_to_date is not None]
        if details.effective_from_date is not None:
       # Check if the provided effective_from_date is greater than all existing from dates
           if any(details.effective_from_date <= date for date in existing_from_dates):
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New effective from date must be greater than all existing from dates")
           if any(details.effective_from_date <= date for date in existing_to_dates):
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="there is an existing  rate in that date range")

         # Iterate over each existing service data
        for existing_data in existing_services:
            if details.effective_from_date != existing_data.effective_from_date and details.effective_from_date is not None:
               if existing_data.effective_to_date is None:
                # Update the corresponding effective_to_date to the new start date
                   existing_data.effective_to_date = details.effective_from_date - timedelta(days=1)

    
    if details.effective_from_date is not None and details.effective_to_date is not None:
       if details.effective_from_date >= details.effective_to_date:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Effective from date must be before effective to date...")


       
    # If id is 0, it means we are creating a new entry
    if id == 0:
        details_data = details.dict()
        new_service = OffAvailableServices(**details_data)
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        return new_service  

    # If id is not 0, we are updating an existing entry
    else:
        service = db.query(OffAvailableServices).filter(OffAvailableServices.id == id).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service with id {id} not found")
        for key, value in details.dict().items():
            setattr(service, key, value)

        db.commit()
        db.refresh(service)  
        return service





def get_all_off_available_services(db: Session, deleted_status: DeletedStatus):
    query = db.query(ViewOffAvailableServices)
    
    if deleted_status == DeletedStatus.DELETED:
        query = query.filter(ViewOffAvailableServices.off_available_services_is_deleted == 'yes')
    elif deleted_status == DeletedStatus.NOT_DELETED:
        query = query.filter(ViewOffAvailableServices.off_available_services_is_deleted == 'no')
    
    return query.all()



def get_off_available_service_by_id(db: Session, id: int):
    return db.query(ViewOffAvailableServices).filter(ViewOffAvailableServices.service_master_id == id).first()

def delete_or_undelete_off_available_service(db: Session, id: int,Action: ActionType):
    try:
        service = db.query(OffAvailableServices).filter(OffAvailableServices.id == id).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with ID {id} does not exist")
        if Action == ActionType.DELETE:
           db.query(OffAvailableServices).filter(OffAvailableServices.id == id).update({
            "is_deleted": "yes",
           })

           db.commit()
           return "service  deleted successfully"
        
        elif Action == ActionType.UNDELETE:  
           db.query(OffAvailableServices).filter(OffAvailableServices.id == id).update({
            "is_deleted": "no",
           })

           db.commit()
           return "service  undeleted successfully"


    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)
    

#----------------------------------------aswathy-----------------------------
#----------------------------------------off_source_of_enquiry---------------------------------------------------




def save_off_source_of_enquiry(db: Session, enq_data: OffSourceOfEnquiryBase, id: int):
    existing_data = db.query(OffSourceOfEnquiry).filter(
        OffSourceOfEnquiry.source == enq_data.source
                      ).filter(OffSourceOfEnquiry.is_deleted == "no").first()
    if existing_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enquiry Source with this name already exists and is active."
        )

    if id == 0:
        # Create
        new_enq_src = OffSourceOfEnquiry(**enq_data.dict())
        db.add(new_enq_src)
        db.commit()
        db.refresh(new_enq_src)
        return new_enq_src  

    else:
        # Update 
        document = db.query(OffSourceOfEnquiry).filter(OffSourceOfEnquiry.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"enquiry source with id {id} not found")
        for key, value in enq_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document  

def get_all_off_source_of_enquiry(db: Session, deleted_status: DeletedStatus):
    query = db.query(OffSourceOfEnquiry)
    
    if deleted_status == DeletedStatus.DELETED:
        query = query.filter(OffSourceOfEnquiry.is_deleted == 'yes')
    elif deleted_status == DeletedStatus.NOT_DELETED:
        query = query.filter(OffSourceOfEnquiry.is_deleted == 'no')
    
    return query.all()

def get_off_source_of_enquiry_by_id(db: Session, id: int):
    return db.query(OffSourceOfEnquiry).filter(OffSourceOfEnquiry.id == id).first()

def delete_off_source_of_enquiry(db: Session, 
                           id: int, 
                           action: ActionType):
    source_of_enquiry = db.query(OffSourceOfEnquiry).filter(OffSourceOfEnquiry.id == id).first()
    if source_of_enquiry is None:
        raise HTTPException(status_code=404, detail="source of enquiry not found")
    
    if action == ActionType.DELETE:
        if source_of_enquiry.is_deleted == 'yes':
            raise HTTPException(status_code=400, detail="source of enquiry already deleted")
        
        source_of_enquiry.is_deleted = 'yes'
        
    elif action == ActionType.UNDELETE:
        if source_of_enquiry.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="source of enquiry not deleted")
        
        source_of_enquiry.is_deleted = 'no'

    
    db.commit()
    return {"success": True, "message": f"source of enquiry {action.value.lower()} successfully"}



#----------------------------off_appointment_status----------------------------------------------------------------

def save_off_appointment(db: Session, appoint_data: OffAppointmentStatusBase, id: int):
    existing_data = db.query(OffAppointmentStatus).filter(
        OffAppointmentStatus.appointment_status == appoint_data.appointment_status
                      ).filter(OffAppointmentStatus.is_deleted == "no").first()
    
    if existing_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment status  with this name already exists and is active."
        )

    if id == 0:
        # Create
        new_status = OffAppointmentStatus(**appoint_data.dict())
        db.add(new_status)
        db.commit()
        db.refresh(new_status)
        return new_status  

    else:
        # Update 
        document = db.query(OffAppointmentStatus).filter(OffAppointmentStatus.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"appointment status with id {id} not found")
        for key, value in appoint_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document  

def get_all_off_appointment(db: Session, deleted_status: DeletedStatus):
    query = db.query(OffAppointmentStatus)
    
    if deleted_status == DeletedStatus.DELETED:
        query = query.filter(OffAppointmentStatus.is_deleted == 'yes')
    elif deleted_status == DeletedStatus.NOT_DELETED:
        query = query.filter(OffAppointmentStatus.is_deleted == 'no')
    
    # Fetch all OffAppointmentMaster objects and populate appointment_status
    return query.all()

def get_off_appointment_status_by_id(db: Session, id: int):
    return db.query(OffAppointmentStatus).filter(OffAppointmentStatus.id == id).first()

def delete_off_appointment_status(db: Session, 
                           id: int, 
                           action: ActionType):
    appointment_status = db.query(OffAppointmentStatus).filter(OffAppointmentStatus.id == id).first()
    if appointment_status is None:
        raise HTTPException(status_code=404, detail="appointment status not found")
    
    if action == ActionType.DELETE:
        if appointment_status.is_deleted == 'yes':
            raise HTTPException(status_code=400, detail="appointment status already deleted")
        
        appointment_status.is_deleted = 'yes'
        
    elif action == ActionType.UNDELETE:
        if appointment_status.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="appointment status not deleted")
        
        appointment_status.is_deleted = 'no'

    
    db.commit()
    return {"success": True, "message": f"appointment status {action.value.lower()} successfully"}

#-------------------create_appointment_visit_master--------------


def create_appointment_visit_master(db: Session, appointment_data: OffAppointmentDetails):
    try:
        # Check if an existing appointment master with the same mobile number exists
        existing_appointment_master = db.query(OffAppointmentMaster).filter_by(mobile_number=appointment_data.appointment_master.mobile_number).first()

        if existing_appointment_master:
            # Update existing appointment master with new data
            existing_appointment_master.full_name = appointment_data.appointment_master.full_name
            existing_appointment_master.email_id = appointment_data.appointment_master.email_id
            # existing_appointment_master.modified_by = user_id
            existing_appointment_master.modified_on = datetime.utcnow()
            appointment_master = existing_appointment_master
        else:
            # Create a new appointment master record
            appointment_master = OffAppointmentMaster(
                full_name=appointment_data.appointment_master.full_name,
                mobile_number=appointment_data.appointment_master.mobile_number,
                email_id=appointment_data.appointment_master.email_id,
                # created_by=user_id,
                created_on=datetime.utcnow()
            )
            db.add(appointment_master)
        
        db.commit()
        
        # Check if an existing visit master with the same appointment master ID and date exists
        existing_visit_master = db.query(OffAppointmentVisitMaster).filter_by(appointment_master_id=appointment_master.id, appointment_date=appointment_data.visit_master.appointment_date).first()

        if existing_visit_master:
            # Update existing visit master with new data
            existing_visit_master.source_of_enquiry_id = appointment_data.visit_master.source_of_enquiry_id
            existing_visit_master.appointment_status_id = appointment_data.visit_master.appointment_status_id
            # existing_visit_master.modified_by = user_id
            existing_visit_master.modified_on = datetime.utcnow()
            visit_master = existing_visit_master
        else:
            # Create a new visit master record
            visit_master = OffAppointmentVisitMaster(
                appointment_master_id=appointment_master.id,
                source_of_enquiry_id=appointment_data.visit_master.source_of_enquiry_id,
                appointment_status_id=appointment_data.visit_master.appointment_status_id,
                appointment_date=appointment_data.visit_master.appointment_date,
                # created_by=user_id,
                created_on=datetime.utcnow()
            )
            db.add(visit_master)
        
        db.commit()
        
        # Create or update visit details records
        visit_details_list = []
        for detail in appointment_data.visit_details:
            # Check if the visit detail already exists
            existing_visit_detail = db.query(OffAppointmentVisitDetails).filter_by(
                visit_master_id=visit_master.id,
                consultancy_service_id=detail.consultancy_service_id,
                consultant_id=detail.consultant_id,
                appointment_time = detail.appointment_time,
                
                is_deleted='no'
            ).first()

            if existing_visit_detail:
                # Update existing visit detail
                # existing_visit_detail.modified_by = user_id
                existing_visit_detail.modified_on = datetime.utcnow()
                existing_visit_detail.field_to_update = detail.field_to_update
                db.commit()
                visit_detail = existing_visit_detail
            else:
                # Create new visit detail
                visit_detail = OffAppointmentVisitDetails(
                    visit_master_id=visit_master.id,
                    consultancy_service_id=detail.consultancy_service_id,
                    consultant_id=detail.consultant_id,
                    
                    appointment_time = detail.appointment_time,
                    # created_by=user_id,
                    created_on=datetime.utcnow(),
                    # modified_by=user_id,
                    modified_on=datetime.utcnow()
                )
                db.add(visit_detail)

            visit_details_list.append(visit_detail)

        db.commit()  # Commit all changes to the database

        return appointment_master, visit_master, visit_details_list
    except Exception as e:
        # Raise HTTPException with status code 500 for any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

#get

def get_appointment_visit_by_id(db: Session,appointment_master_id: int):
    try:
        # Fetch appointment details
        appointment_data = db.query(OffAppointmentVisitDetailsView).filter(OffAppointmentVisitDetailsView.appointment_master_id == appointment_master_id).all()
        if not appointment_data:
            raise HTTPException(status_code=404, detail="Appointment data not found")

        # Fetch visit master details
        appointment_visit_data = db.query(OffAppointmentVisitMasterView).filter(OffAppointmentVisitMasterView.appointment_master_id == appointment_master_id).first()
        if not appointment_visit_data:
            raise HTTPException(status_code=404, detail="Visit master data not found")

        # Convert visit master details to dictionary
        visit_master = appointment_visit_data.__dict__
        visit_master["appointment_visit_master_appointment_date"] = str(visit_master["appointment_visit_master_appointment_date"])

        # Construct appointment master data
        appointment_master_data = {
            "id": visit_master.get("id"),
            "full_name": visit_master.get("full_name"),
            "mobile_number": visit_master.get("mobile_number"),
            "email_id": visit_master.get("email_id")
        }
        appointment_master = OffAppointmentMasterView(**appointment_master_data)

        # Extract appointment ID from visit master
        appointment_id = visit_master.get("id")

        # Add appointment_id to visit_master
        visit_master["appointment_id"] = appointment_id

        # Convert appointment details to a list of dictionaries
        visit_details = [record.__dict__ for record in appointment_data]

        return {
            "appointment_master": appointment_master,
            "visit_master": visit_master,
            "visit_details": visit_details
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



#-----------delete appointment_master----------------
from caerp_constants.caerp_constants import DeletedStatus,ActionType
def delete_appointment_master(db: Session, 
                           id: int, 
                           action: ActionType,
                           deleted_by:int):
    appointment_master = db.query(OffAppointmentMaster).filter(OffAppointmentMaster.id == id).first()
    if appointment_master is None:
        raise HTTPException(status_code=404, detail="Appointment master not found")
    
    if action == ActionType.DELETE:
        if appointment_master.is_deleted == 'yes':
            raise HTTPException(status_code=400, detail="Appointment master already deleted")
        
        appointment_master.is_deleted = 'yes'
        appointment_master.deleted_by = deleted_by
        appointment_master.deleted_on = datetime.utcnow()
        
        
    elif action == ActionType.UNDELETE:
        if appointment_master.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="Appointment master not deleted")
        
        appointment_master.is_deleted = 'no'
        appointment_master.deleted_by = None
        appointment_master.deleted_on = None
        
        
    db.commit()
    return {"success": True, "message": f"Appointment master {action.value.lower()} successfully"}


#-----------delete appointment_visit_master----------------

def delete_appointment_visit_master(db: Session, 
                           id: int, 
                           action: ActionType,
                           deleted_by:int
                           ):
    appointment_visit_master = db.query(OffAppointmentVisitMaster).filter(OffAppointmentVisitMaster.id == id).first()
    if appointment_visit_master is None:
        raise HTTPException(status_code=404, detail="appointment visit master not found")
    
    if action == ActionType.DELETE:
        if appointment_visit_master.is_deleted == 'yes':

            raise HTTPException(status_code=400, detail="appointment visit master already deleted")
        
        appointment_visit_master.is_deleted = 'yes'
        appointment_visit_master.is_deleted_directly = 'yes'
        appointment_visit_master.is_deleted_with_master = 'no'
        appointment_visit_master.deleted_by = deleted_by
        appointment_visit_master.deleted_on = datetime.utcnow()
        
    elif action == ActionType.UNDELETE:
        if appointment_visit_master.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="appointment visit  master not deleted")
        
        appointment_visit_master.is_deleted = 'no'
        appointment_visit_master.is_deleted_directly = 'no'
        appointment_visit_master.is_deleted_with_master = 'no'
        appointment_visit_master.deleted_by = None
        appointment_visit_master.deleted_on = None

    
    db.commit()
    return {"success": True, "message": f"appointment visit master {action.value.lower()} successfully"}

#-----------delete appointment_visit_details----------------

def delete_appointment_visit_details(db: Session, 
                           id: int, 
                           action: ActionType,
                           deleted_by:int
                           ):
    appointment_visit_details = db.query(OffAppointmentVisitDetails).filter(OffAppointmentVisitDetails.id == id).first()
    if appointment_visit_details is None:
        raise HTTPException(status_code=404, detail="appointment visit details not found")
    
    if action == ActionType.DELETE:
        if appointment_visit_details.is_deleted == 'yes':

            raise HTTPException(status_code=400, detail="appointment visit details already deleted")
        
        appointment_visit_details.is_deleted = 'yes'
        appointment_visit_details.is_deleted_directly = 'yes'
        appointment_visit_details.is_deleted_with_master = 'no'
        appointment_visit_details.deleted_by = deleted_by
        appointment_visit_details.deleted_on = datetime.utcnow()

        
    elif action == ActionType.UNDELETE:
        if appointment_visit_details.is_deleted == 'no':
            raise HTTPException(status_code=400, detail="appointment visit  master not deleted")
        
        appointment_visit_details.is_deleted = 'no'
        appointment_visit_details.is_deleted_directly = 'no'
        appointment_visit_details.is_deleted_with_master = 'no'
        appointment_visit_details.deleted_by = None
        appointment_visit_details.deleted_on = None

    
    db.commit()
    return {"success": True, "message": f"appointment visit master {action.value.lower()} successfully"}


#-------get all bussiness constitution
def get_all_business_constitution(db: Session, deleted_status: DeletedStatus):
    query = db.query(AppBusinessConstitution)
    
    if deleted_status == DeletedStatus.DELETED:
        query = query.filter(AppBusinessConstitution.is_deleted == 'yes')
    elif deleted_status == DeletedStatus.NOT_DELETED:
        query = query.filter(AppBusinessConstitution.is_deleted == 'no')
    
    return query.all()


def save_off_consultancy_services(db: Session, details: OffConsultancyServicesDisplay, id: int):
    
    existing_services  = db.query(ConsultancyService).filter(
        ConsultancyService.service_master_id == details.service_master_id,
        ConsultancyService.is_deleted == "no",
        ConsultancyService.effective_from_date.isnot(None),
        ConsultancyService.consultant_id == details.consultant_id
    ).all()
    
    if existing_services:
        existing_from_dates = [service.effective_from_date for service in existing_services]
       #existing_to_dates = [service.effective_to_date for service in existing_services]
        existing_to_dates = [service.effective_to_date for service in existing_services if service.effective_to_date is not None]
        if details.effective_from_date is not None:
       # Check if the provided effective_from_date is greater than all existing from dates
           if any(details.effective_from_date <= date for date in existing_from_dates):
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New effective from date must be greater than all existing from dates")
           if any(details.effective_from_date <= date for date in existing_to_dates):
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="there is an existing  rate in that date range")

         # Iterate over each existing service data
        for existing_data in existing_services:
            if details.effective_from_date != existing_data.effective_from_date and details.effective_from_date is not None:
               if existing_data.effective_to_date is None:
                # Update the corresponding effective_to_date to the new start date
                   existing_data.effective_to_date = details.effective_from_date - timedelta(days=1)

    
    if details.effective_from_date is not None and details.effective_to_date is not None:
       if details.effective_from_date >= details.effective_to_date:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Effective from date must be before effective to date...")


       
    # If id is 0,creating a new entry
    if id == 0:
        details_data = details.dict()
        new_service = ConsultancyService(**details_data)
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        return new_service  

    # If id is not 0,  updating an existing entry
    else:
        service = db.query(ConsultancyService).filter(ConsultancyService.id == id).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service with id {id} not found")
        for key, value in details.dict().items():
            setattr(service, key, value)

        db.commit()
        db.refresh(service)  
        return service



def get_services_by_consultant_id(db: Session, consultant_id: int, date_param: date = date.today()):
    return db.query(ViewOffConsultancyServices).filter(
        ViewOffConsultancyServices.consultant_id == consultant_id,
        ViewOffConsultancyServices.effective_from_date <= date_param,
        (ViewOffConsultancyServices.effective_to_date >= date_param) |
        (ViewOffConsultancyServices.effective_to_date == None)  
    ).all()



def get_consultants_by_service_id(db: Session, service_master_id: int, date_param: date = date.today()):
    return db.query(ViewOffConsultancyServices).filter(
        ViewOffConsultancyServices.service_master_id == service_master_id,
        ViewOffConsultancyServices.effective_from_date <= date_param,
        (ViewOffConsultancyServices.effective_to_date >= date_param) |
        (ViewOffConsultancyServices.effective_to_date == None)  
    ).all()













