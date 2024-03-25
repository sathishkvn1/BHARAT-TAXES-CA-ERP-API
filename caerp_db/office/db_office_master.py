from fastapi import HTTPException, UploadFile,status,Depends
from caerp_db.office.models import AppHsnSacClasses, AppHsnSacMaster, AppServiceFrequency, AppServiceGenerationMode, AppServiceOwner, AppStockKeepingUnitCode, Document_Master
from sqlalchemy.orm import Session
from caerp_db.hash import Hash
from datetime import datetime
from sqlalchemy.orm.session import Session
from caerp_schema.office.office_schema import DocumentMasterBase, HsnSacClassesDisplay, HsnSacMasterBase, HsnSacMasterDisplay, ServiceFrequencyDisplay, ServiceGenerationModeDisplay, ServiceOwnerDisplay, StockKeepingUnitCodeDisplay
from caerp_db.office.models import ServiceProvider
from caerp_schema.office.office_schema import ServiceProviderBase,ServiceDepartmentBase
from caerp_db.office.models import ServiceDepartments,AppBusinessActivityType,AppBusinessActivityMaster
from caerp_schema.office.office_schema import BusinessActivityTypeBase,BusinessActivityMasterBase
from fastapi import HTTPException, status
from caerp_constants.caerp_constants import DeletedStatus
from sqlalchemy import and_, between
import pandas as pd
import io
from sqlalchemy.exc import IntegrityError
from caerp_db.office.models import EnquirerType,EnquirerStatus,ServiceProcessingStatus
from caerp_db.common.models import AppEducationalQualificationsMaster
from caerp_schema.office.office_schema import EducationalQualificationsBase,EnquirerTypeBase,EnquirerStatusBase,EnquirerStatusDisplay,ServiceProcessingStatusBase,ServiceProcessingStatusDisplay
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
def delete_service_provider(db: Session, 
                           id: int,
                           ):
    service_provider_delete = db.query(ServiceProvider).filter(ServiceProvider.id == id).first()

    if service_provider_delete is None:
        raise HTTPException(status_code=404, detail="service provider not found")

    service_provider_delete.is_deleted = 'yes'
    

    db.commit()

    return {
        "message": "Service Provider Deleted successfully",
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



def delete_service_departments(db: Session, 
                           id: int,
                           ):
    service_dep_delete = db.query(ServiceDepartments).filter(ServiceDepartments.id == id).first()

    if service_dep_delete is None:
        raise HTTPException(status_code=404, detail="Service Departments not found")

    service_dep_delete.is_deleted = 'yes'
  
 

    db.commit()

    return {
        "message": "Service Departments Deleted successfully",
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
def delete_service_processing_status(db: Session, 
                           id: int,
                           ):
    service_processing_status_delete = db.query(ServiceProcessingStatus).filter(ServiceProcessingStatus.id == id).first()

    if service_processing_status_delete is None:
        raise HTTPException(status_code=404, detail="Service Processing Status not found")

    service_processing_status_delete.is_deleted = 'yes'
    

    db.commit()

    return {
        "message": "Service Processing Status Deleted successfully",
    }
    
#...............................................................................................
def save_service_frequency(db: Session, freq_data: ServiceFrequencyDisplay, id: int):
    # Check if the provided service frequency name already exists in the database
    existing_freq = db.query(AppServiceFrequency).filter(
        AppServiceFrequency.service_frequency == freq_data.service_frequency
    ).filter(AppServiceFrequency.is_deleted == "no").first()
    
    
    if existing_freq:
        # If an existing record with the same name and is_deleted == "no" is found,
        # raise an exception indicating that no creation or update should be done.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service frequency with this name already exists and is active."
        )

    if id == 0:
        # Create
        new_freq = AppServiceFrequency(**freq_data.dict())
        db.add(new_freq)
        db.commit()
        db.refresh(new_freq)
        return new_freq  

    else:
        # Update 
        document = db.query(AppServiceFrequency).filter(AppServiceFrequency.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Frequency with ID {id} not found')
        for key, value in freq_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document


def get_all_service_frequency(db: Session,deleted_status: DeletedStatus):
   
   query = db.query(AppServiceFrequency)

   if deleted_status == DeletedStatus.DELETED:
      query = query.filter(AppServiceFrequency.is_deleted == 'yes')
   elif deleted_status == DeletedStatus.NOT_DELETED:
      query = query.filter(AppServiceFrequency.is_deleted == 'no')
   elif deleted_status == DeletedStatus.ALL:
      pass

   return query.all()


def get_service_frequency_by_id(db: Session, id: int):
     
     return db.query(AppServiceFrequency).filter(AppServiceFrequency.id == id).first()



def delete_service_frequency(db: Session, id:int):
    try:
         # Check if the item exists
        freq= db.query(AppServiceFrequency).filter(AppServiceFrequency.id == id).first()
        if not freq:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"frequency with ID {id} does not exist")

        db.query(AppServiceFrequency).filter(AppServiceFrequency.id == id).update({
            "is_deleted": "yes",
           
        })

        db.commit()
        return "service frequency deleted successfully"

    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)
 #--------------------------------------app_service_owner---------------------------------------------------

def save_service_owner(db: Session, owner_data: ServiceOwnerDisplay, id: int):
    
     # Check if the provided service frequency name already exists in the database
    existing_data = db.query(AppServiceOwner).filter(
        AppServiceOwner.service_owner == owner_data.service_owner
    ).filter(AppServiceOwner.is_deleted == "no").first()
    
   
    if existing_data:
        # If an existing record with the same name and is_deleted == "no" is found,
        # raise an exception indicating that no creation or update should be done.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service owner with this name already exists and is active."
        )
    
    if id == 0:
       # Create
        new_owner = AppServiceOwner(** owner_data.dict())
        db.add(new_owner)
        db.commit()
        db.refresh(new_owner)
        return new_owner  

    else:
        # Update 
        document = db.query(AppServiceOwner).filter(AppServiceOwner.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'service owner with id {id} not found')
        for key, value in owner_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document  


def get_all_service_owner(db: Session,deleted_status: DeletedStatus):
   
   query = db.query(AppServiceOwner)

   if deleted_status == DeletedStatus.DELETED:
      query = query.filter(AppServiceFrequency.is_deleted == 'yes')
   elif deleted_status == DeletedStatus.NOT_DELETED:
      query = query.filter(AppServiceFrequency.is_deleted == 'no')
   elif deleted_status == DeletedStatus.ALL:
      pass

   return query.all()


def get_service_owner_by_id(db: Session, id: int):
     
     return db.query(AppServiceOwner).filter(AppServiceOwner.id == id).first()


def delete_service_owner(db: Session, id:int):
    try:
         # Check if the item exists
        owner= db.query(AppServiceOwner).filter(AppServiceOwner.id == id).first()
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"owner with ID {id} does not exist")

        db.query(AppServiceOwner).filter(AppServiceOwner.id == id).update({
            "is_deleted": "yes",
           
        })

        db.commit()
        return "service owner deleted successfully"

    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete  with id {id}: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)

 #--------------------------------------service_generation_mode---------------------------------------------------

def save_service_generation_mode(db: Session, gen_mode_data: ServiceGenerationModeDisplay, id: int):
    
    existing_data = db.query(AppServiceGenerationMode).filter(
        AppServiceGenerationMode.mode == gen_mode_data.mode
    ).filter(AppServiceGenerationMode.is_deleted == "no").first()
    
    if existing_data:
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service mode with this name already exists and is active."
        )
    
    if id == 0:
       # Create
        new_gen_mode = AppServiceGenerationMode(** gen_mode_data.dict())
        db.add(new_gen_mode)
        db.commit()
        db.refresh(new_gen_mode)
        return new_gen_mode  

    else:
        # Update 
        document = db.query(AppServiceGenerationMode).filter(AppServiceGenerationMode.id == id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'service generation mode with id {id} not found')
        for key, value in gen_mode_data.dict().items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)  
        return document  


def get_all_service_generation_mode(db: Session,deleted_status: DeletedStatus):
   
   query = db.query(AppServiceGenerationMode)

   if deleted_status == DeletedStatus.DELETED:
      query = query.filter(AppServiceGenerationMode.is_deleted == 'yes')
   elif deleted_status == DeletedStatus.NOT_DELETED:
      query = query.filter(AppServiceGenerationMode.is_deleted == 'no')
   elif deleted_status == DeletedStatus.ALL:
      pass

   return query.all()

def get_service_generation_mode_by_id(db: Session, id: int):
     
     return db.query(AppServiceGenerationMode).filter(AppServiceGenerationMode.id == id).first()



def delete_service_generation_mode(db: Session, id: int):
    try:
        # Check if the item exists
        service_generation_mode = db.query(AppServiceGenerationMode).filter(AppServiceGenerationMode.id == id).first()
        if not service_generation_mode:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service generation mode with ID {id} does not exist")

        # Update the 'is_deleted' attribute of the service generation mode
        db.query(AppServiceGenerationMode).filter(AppServiceGenerationMode.id == id).update({
            "is_deleted": "yes",
        })

        db.commit()
        return "Service generation mode deleted successfully"

    except Exception as e:
        db.rollback()
        error_message = f"Failed to delete service generation mode with id {id}: {str(e)}"
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'service generation mode with id {id} not found')
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

        # Update the 'is_deleted' 
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














