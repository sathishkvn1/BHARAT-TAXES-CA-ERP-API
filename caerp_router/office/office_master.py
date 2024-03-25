
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,status,Query,Response
from sqlalchemy.orm import Session
from caerp_db.database import get_db
from caerp_db.office import db_office_master
from caerp_db.office.models import ServiceProvider
from caerp_schema.office.office_schema import HsnSacClassesBase, HsnSacClassesDisplay, HsnSacMasterBase, HsnSacMasterDisplay, ServiceFrequencyBase, ServiceFrequencyDisplay, ServiceGenerationModeBase, ServiceGenerationModeDisplay, ServiceOwnerBase, ServiceOwnerDisplay, ServiceProviderBase,ServiceProBase, StockKeepingUnitCodeBase, StockKeepingUnitCodeDisplay
from caerp_db.office.models import ServiceDepartments,Document_Master
from caerp_schema.office.office_schema import ServiceDepartmentBase,ServiceDepBase
from caerp_schema.office.office_schema import DocumentMasterBase,DocumentBase
from caerp_db.office.models import ServiceDepartments,AppBusinessActivityType,AppBusinessActivityMaster
from caerp_schema.office.office_schema import BusinessActivityTypeBase,BusinessActivityTypeDisplay,BusinessActivityMasterBase,BusinessActivityMasterDisplay
from caerp_db.office.models import EnquirerType,EnquirerStatus,ServiceProcessingStatus
from caerp_schema.office.office_schema import EducationalQualificationsBase,EducationalQualificationsDisplay,EnquirerTypeBase,EnquirerTypeDisplay,EnquirerStatusBase,EnquirerStatusDisplay
from caerp_schema.office.office_schema import ServiceProcessingStatusBase,ServiceProcessingStatusDisplay
from caerp_auth import oauth2
from typing import List
from datetime import datetime
from caerp_constants.caerp_constants import DeletedStatus
from caerp_db.common.models import AppEducationalQualificationsMaster


router = APIRouter(
    tags=['Office Master']
)



#----------------------------------document_master------------------------------------------------------------------------------------
@router.post('/save_document_master/{id}', response_model=DocumentMasterBase)
def save_document(
    document_data: DocumentMasterBase,
    id: int = 0,  # Default value of 0 for id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a document.

    - **document_data**: Data for the document, provided as parameters of type DocumentMasterBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the documents's identifier.
    
    - If document_id is 0, it indicates the creation of a new document.
    - Returns: The newly created document as the response.

    If document_id is not 0, it indicates the update of an existing document.
    - Returns: The updated document as the response.

    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.save_document (db, document_data, id)
    
    

 #------All-----------------  


@router.get('/document_master/all', response_model=list[DocumentBase])
def get_all_document(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get documents from the database based on status.

    - **status**: Query parameter to filter documents by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        documents = db.query(Document_Master).filter(Document_Master.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        documents = db.query(Document_Master).filter(Document_Master.is_deleted == 'no').all()
    else:
        documents = db.query(Document_Master).all()

    return documents

#-----------by id----------------------

@router.get('/document/{id}', response_model=DocumentBase)
def get_document_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get document by document id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    document = db_office_master.get_document(db, id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"document with id {id} not found"
        )
    return document

#------------delete----------------------
@router.delete("/document/delete/{id}")
def delete_document(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete document by document_id.
    Set the 'is_deleted' flag to 'yes' to mark the document as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_document_db(db, id)

#-----------------------------service provider---------------------------------------------------------------------

 
@router.post('/services/service_provider/{id}', response_model=ServiceProviderBase)
def save_service_provider(
    service_provider_data: ServiceProviderBase,
    id: int = 0,  # Default value of 0 for service_provider_id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a service_provider.

    - **service_provider_data**: Data for the service_provider, provided as parameters of type ServiceProviderBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the service_provider's identifier.
    
    - If service_provider_id is 0, it indicates the creation of a new service_provider.
    - Returns: The newly created service_provider as the response.

    If service_provider_id is not 0, it indicates the update of an existing service_provider.
    - Returns: The updated service_provider as the response.


    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    return db_office_master.save_service_provider (db, service_provider_data, id)
    
    

#-----------all------------------------

@router.get('/services/service_provider/all', response_model=list[ServiceProBase])
def get_all_service_provider(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get service_provider from the database based on status.

    - **status**: Query parameter to filter service_provider by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        service_provider = db.query(ServiceProvider).filter(ServiceProvider.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        service_provider = db.query(ServiceProvider).filter(ServiceProvider.is_deleted == 'no').all()
    else:
        service_provider = db.query(ServiceProvider).all()

    return service_provider

#---------by id------------------------
@router.get('/services/service_provider_by_id/{id}', response_model=ServiceProBase)
def service_provider_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get service_provider by service_provider id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    service_provider = db_office_master.get_service_provider_id(db, id)
    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"service_provider with id {id} not found"
        )
    return service_provider
#-----delete----------------------------
@router.delete("/services/service_provider/delete/{id}")
def delete_service_provider(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete service_provider by service_provider_id.
    Set the 'is_deleted' flag to 'yes' to mark the service_provider as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_service_provider(db, id)


#-----------------------------service departments---------------------------------------------------------------------


@router.post('/services/service_departments/{id}', response_model=ServiceDepartmentBase)
def save_service_departments(
    service_departments_data: ServiceDepartmentBase,
    id: int = 0,  # Default value of 0 for service_departments_id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a service_departments.

    - **service_departments_data**: Data for the service_departments, provided as parameters of type ServiceDepartmentBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the service_departments's identifier.
    
    - If service_departments_id is 0, it indicates the creation of a new service_departments.
    - Returns: The newly created service_departments as the response.

    If service_departments_id is not 0, it indicates the update of an existing service_departments.
    - Returns: The updated service_departments as the response.

   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
  
    return db_office_master.save_service_department (db, service_departments_data, id)
   
    



@router.get('/services/service_departments/all', response_model=list[ServiceDepBase])
def get_all_service_departments(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get service_departments from the database based on status.

    - **status**: Query parameter to filter service_departments by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        service_departments = db.query(ServiceDepartments).filter(ServiceDepartments.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        service_departments = db.query(ServiceDepartments).filter(ServiceDepartments.is_deleted == 'no').all()
    else:
        service_departments = db.query(ServiceDepartments).all()

    return service_departments


@router.get('/services/service_departments/{id}', response_model=ServiceDepBase)
def service_departments_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get service_departments by service_departments id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    service_departments = db_office_master.get_service_department_id(db, id)
    if not service_departments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"service_departments with id {id} not found"
        )
    return service_departments



@router.delete("/services/service_departments/delete/{id}")
def delete_service_departments(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete service_departments by service_departments_id.
    Set the 'is_deleted' flag to 'yes' to mark the service_departments as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_service_departments(db, id)


#-----------------------------Business Activity Type----------------------------------------------------------------------

@router.post('/services/business_activity_type/{id}', response_model=BusinessActivityTypeBase)
def save_business_activity_type(
    business_activity_type_data: BusinessActivityTypeBase,
    id: int = 0,  # Default value of 0 for business_activity_type id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a business_activity_type.

    - **business_activity_type_data**: Data for the business_activity_type, provided as parameters of type BusinessActivityTypeBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the business_activity_type's identifier.
    
    - If _business_activity_type id is 0, it indicates the creation of a new _business_activity_type.
    - Returns: The newly created business_activity_type as the response.

    If _business_activity_type id is not 0, it indicates the update of an existing _business_activity_type.
    - Returns: The updated business_activity_type as the response.

   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    return db_office_master.save_business_activity_type (db, business_activity_type_data, id)
 
    

#-------all----------

@router.get('/services/business_activity_type/all', response_model=list[BusinessActivityTypeDisplay])
def get_all_business_activity_type(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get business_activity_type from the database based on status.

    - **status**: Query parameter to filter business_activity_type by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        business_activity_type = db.query(AppBusinessActivityType).filter(AppBusinessActivityType.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        business_activity_type = db.query(AppBusinessActivityType).filter(AppBusinessActivityType.is_deleted == 'no').all()
    else:
        business_activity_type = db.query(AppBusinessActivityType).all()

    return business_activity_type

#-----------by id-----------------
@router.get('/services/business_activity_type/{id}', response_model=BusinessActivityTypeDisplay)
def business_activity_type_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get business_activity_type by business_activity_type id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    business_activity_type = db_office_master.get_business_activity_type_id(db, id)
    if not business_activity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"business activity type with id {id} not found"
        )
    return business_activity_type

#-----------delete-------------------

@router.delete("/services/business_activity_type/delete/{id}")
def delete_business_activity_type(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete business_activity_type by business_activity_type id.
    Set the 'is_deleted' flag to 'yes' to mark the business_activity_type as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_business_activity_type(db, id)



#-----------------------------Business Activity Master----------------------------------------------------------------------


@router.post('/services/business_activity_master/{id}', response_model=BusinessActivityMasterBase)
def save_business_activity_master(
    business_activity_master_data: BusinessActivityMasterBase,
    id: int = 0,  # Default value of 0 for _business_activity_master id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a business_activity_master.

    - **service_departments_data**: Data for the business_activity_master, provided as parameters of type BusinessActivityMasterBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the business_activity_master's identifier.
    
    - If business_activity_master id is 0, it indicates the creation of a new business_activity_master.
    - Returns: The newly created business_activity_master as the response.

    If business_activity_master id is not 0, it indicates the update of an existing business_activity_master.
    - Returns: The updated business_activity_master as the response.

   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
  
    return db_office_master.save_business_activity_master (db, business_activity_master_data, id)
    
    

#-------all----------

@router.get('/services/business_activity_master/all', response_model=list[BusinessActivityMasterDisplay])
def get_all_business_activity_master(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get business_activity_master from the database based on status.

    - **status**: Query parameter to filter business_activity_master by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    query = db.query(AppBusinessActivityMaster, AppBusinessActivityType.business_activity_type).join(
        AppBusinessActivityType, AppBusinessActivityMaster.business_activity_type_id == AppBusinessActivityType.id)

    if is_status == "DELETED":
        business_activity_master = query.filter(AppBusinessActivityMaster.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        business_activity_master = query.filter(AppBusinessActivityMaster.is_deleted == 'no').all()
    else:
        business_activity_master = query.all()

    # Extract the required fields from the query result
    result = [
        BusinessActivityMasterDisplay(
            id=item[0].id,
            business_activity=item[0].business_activity,
            business_activity_type=item[1]
        ) for item in business_activity_master
    ]

    return result
#-----------by id-----------------
@router.get('/services/business_activity_master/{id}', response_model=BusinessActivityMasterDisplay)
def business_activity_master_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get business_activity_master by business_activity_master id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    business_activity_master = db_office_master.get_business_activity_master_id(db, id)
    if not business_activity_master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"business activity master with id {id} not found"
        )
    return business_activity_master

#-----------delete-------------------

@router.delete("/services/business_activity_master/delete/{id}")
def delete_business_activity_master(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete business_activity_master by business_activity_master id.
    Set the 'is_deleted' flag to 'yes' to mark the business_activity_master as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_business_activity_master(db, id)

#-----------------------------Educational Qualifications Master----------------------------------------------------------------------

@router.post('/educational_qualifications/{id}', response_model=EducationalQualificationsBase)
def save_educational_qualifications(
    educationalqualifications_data: EducationalQualificationsBase,
    id: int = 0,  # Default value of 0 for EducationalQualifications id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a educationalqualifications.

    - **educational qualifications_data**: Data for the educationalqualifications, provided as parameters of type EducationalQualificationsBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the educational qualifications's identifier.
    
    - If educational qualifications id is 0, it indicates the creation of a new educationalqualifications.
    - Returns: The newly created educationalqualifications as the response.

    If educational qualifications id is not 0, it indicates the update of an existing educational qualifications.
    - Returns: The updated educational qualifications as the response.

   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
  
    return db_office_master.save_educational_qualifications (db, educationalqualifications_data, id)
    
    

#-------all----------

@router.get('/educational_qualifications/all', response_model=list[EducationalQualificationsDisplay])
def get_all_educational_qualifications(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get educational qualifications from the database based on status.

    - **status**: Query parameter to filter educational qualifications by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        educational_qualifications = db.query(AppEducationalQualificationsMaster).filter(AppEducationalQualificationsMaster.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        educational_qualifications = db.query(AppEducationalQualificationsMaster).filter(AppEducationalQualificationsMaster.is_deleted == 'no').all()
    else:
        educational_qualifications = db.query(AppEducationalQualificationsMaster).all()

    return educational_qualifications

#-----------by id-----------------
@router.get('/educational_qualifications/{id}', response_model=EducationalQualificationsDisplay)
def educational_qualifications_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get educational qualifications by educational qualifications id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    educationalqualifications = db_office_master.get_educational_qualifications_id(db, id)
    if not educationalqualifications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"business activity master with id {id} not found"
        )
    return educationalqualifications

#-----------delete-------------------

@router.delete("/educational_qualifications/delete/{id}")
def delete_educational_qualifications(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete educational qualifications by educational qualifications id.
    Set the 'is_deleted' flag to 'yes' to mark the educationalqualifications as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_educational_qualifications(db, id)

#-----------------------------Enquirer Type----------------------------------------------------------------------

@router.post('/enquiry/enquirer_type/{id}', response_model=EnquirerTypeBase)
def save_enquirer_type(
    enquirer_type_data: EnquirerTypeBase,
    id: int = 0,  # Default value of 0 for enquirer_type id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a enquirer_type.

    - **enquirer_type_data**: Data for the enquirer_type, provided as parameters of type EnquirerTypeBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the enquirer_type's identifier.
    
    - If enquirer_type id is 0, it indicates the creation of a new enquirer_type.
    - Returns: The newly created enquirer_type as the response.

    If enquirer_type id is not 0, it indicates the update of an existing enquirer_type.
    - Returns: The updated enquirer_type as the response.

   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
  
    return db_office_master.save_enquirer_type (db, enquirer_type_data, id)
    
    

#-------all----------

@router.get('/enquiry/enquirer_type/all', response_model=list[EnquirerTypeDisplay])
def get_all_enquirer_type(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get enquirer type from the database based on status.

    - **status**: Query parameter to filter enquirer type by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        enquirer_type = db.query(EnquirerType).filter(EnquirerType.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        enquirer_type = db.query(EnquirerType).filter(EnquirerType.is_deleted == 'no').all()
    else:
        enquirer_type = db.query(EnquirerType).all()

    return enquirer_type

#-----------by id-----------------
@router.get('/enquiry/enquirer_type/{id}', response_model=EnquirerTypeDisplay)
def enquirer_type_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get enquirer type by enquirer type id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    enquirer_type = db_office_master.get_enquirer_type_id(db, id)
    if not enquirer_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"enquirer type with id {id} not found"
        )
    return enquirer_type

#-----------delete-------------------

@router.delete("/enquiry/enquirer_type/delete/{id}")
def delete_enquirer_type(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete enquirer_type by enquirer_type id.
    Set the 'is_deleted' flag to 'yes' to mark the enquirer_type as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_enquirer_type(db, id)

#-----------------------------Enquirer Status----------------------------------------------------------------------

@router.post('/enquiry/enquirer_status/{id}', response_model=EnquirerStatusBase)
def save_enquirer_status(
    enquirer_status_data: EnquirerStatusBase,
    id: int = 0,  # Default value of 0 for enquirer_status id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a enquirer_status.

    - **enquirer_status_data**: Data for the enquirer_status, provided as parameters of type EnquirerStatusBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the enquirer_status's identifier.
    
    - If enquirer_status id is 0, it indicates the creation of a new enquirer_status.
    - Returns: The newly created enquirer_status as the response.

    If enquirer_status id is not 0, it indicates the update of an existing enquirer_status.
    - Returns: The updated enquirer_status as the response.

   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
  
    return db_office_master.save_enquirer_status(db, enquirer_status_data, id)
    
    

#-------all----------

@router.get('/enquiry/enquirer_status/all', response_model=list[EnquirerStatusDisplay])
def get_all_enquirer_status(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get enquirer status from the database based on status.

    - **status**: Query parameter to filter enquirer status by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        enquirer_status = db.query(EnquirerStatus).filter(EnquirerStatus.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        enquirer_status = db.query(EnquirerStatus).filter(EnquirerStatus.is_deleted == 'no').all()
    else:
        enquirer_status = db.query(EnquirerStatus).all()

    return enquirer_status

#-----------by id-----------------
@router.get('/enquiry/enquirer_status/{id}', response_model=EnquirerStatusDisplay)
def enquirer_status_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get enquirer status by enquirer status id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    enquirer_status = db_office_master.get_enquirer_status_id(db, id)
    if not enquirer_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"enquirer status with id {id} not found"
        )
    return enquirer_status

#-----------delete-------------------

@router.delete("/enquiry/enquirer_status/delete/{id}")
def delete_enquirer_status(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete enquirer_status by enquirer_status id.
    Set the 'is_deleted' flag to 'yes' to mark the enquirer_status as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_enquirer_status(db, id)

#-----------------------------Service Processing Status----------------------------------------------------------------------

@router.post('/service/service_processing_status/{id}', response_model=ServiceProcessingStatusBase)
def save_service_processing_status(
   service_processing_status_data: ServiceProcessingStatusBase,
    id: int = 0,  # Default value of 0 for service_processing_status id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a service_processing_status.

    - **service_processing_status_data**: Data for the service_processing_status, provided as parameters of type ServiceProcessingStatusBase.
    - **id**: An optional integer parameter with a default value of 0, indicating the service_processing_status's identifier.
    
    - If service_processing_status id is 0, it indicates the creation of a new service_processing_status.
    - Returns: The newly created service_processing_status as the response.

    If service_processing_status id is not 0, it indicates the update of an existing service_processing_status.
    - Returns: The updated service_processing_status as the response.

   
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
  
    return db_office_master.save_service_processing_status(db, service_processing_status_data, id)
    
    

#-------all----------

@router.get('/service/service_processing_status/all', response_model=list[ServiceProcessingStatusDisplay])
def get_all_service_processing_status(
    is_status: str = Query("ALL", enum=["ALL", "DELETED", "NOT DELETED"]),
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    """
    Get service processing status from the database based on status.

    - **status**: Query parameter to filter service processing status by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    if is_status == "DELETED":
        service_processing_status = db.query(ServiceProcessingStatus).filter(ServiceProcessingStatus.is_deleted == 'yes').all()
    elif is_status == "NOT DELETED":
        service_processing_status = db.query(ServiceProcessingStatus).filter(ServiceProcessingStatus.is_deleted == 'no').all()
    else:
        service_processing_status = db.query(ServiceProcessingStatus).all()

    return service_processing_status

#-----------by id-----------------
@router.get('/service/service_processing_status/{id}', response_model=ServiceProcessingStatusDisplay)
def service_processing_status_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get service processing status by service processing status id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    service_processing_status = db_office_master.get_service_processing_status_id(db, id)
    if not service_processing_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"service processing status with id {id} not found"
        )
    return service_processing_status

#-----------delete-------------------

@router.delete("/service/service_processing_status/delete/{id}")
def delete_service_processing_status(
    id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete service_processing_status by service_processing_status id.
    Set the 'is_deleted' flag to 'yes' to mark the service_processing_status as deleted.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.delete_service_processing_status(db, id)

#--------------------------------------------------------------------------------
@router.post('/services/save_service_frequency/{ID}', response_model=ServiceFrequencyDisplay)
def save_service_frequency(
    ID: int,
    freq_data: ServiceFrequencyDisplay,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save  or Create service frequency for a specific ID.
    """
    if not token:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
         return db_office_master.save_service_frequency(db, freq_data, ID)
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
       
@router.get('/services/service_frequency', response_model=list[ServiceFrequencyBase])
def get_all_service_frequency(deleted_status: DeletedStatus =  Query(..., title="Select deleted status"),
  db: Session = Depends(get_db),
      token: str = Depends(oauth2.oauth2_scheme)):
   
    """
    Get all  service frequency.
    """
    # Check if deleted_status is a valid option
    if deleted_status not in [DeletedStatus.DELETED, DeletedStatus.NOT_DELETED, DeletedStatus.ALL]:
        raise HTTPException(
            status_code=400,
            detail="Invalid value for 'deleted_status'. Allowed values are 'yes', 'no', and 'all'."
        )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_office_master.get_all_service_frequency(db,deleted_status)


@router.get('/services/service_frequency/{id}', response_model=ServiceFrequencyBase)
def get_service_frequency_by_id(ID: int,db: Session = Depends(get_db),
                                  token: str = Depends(oauth2.oauth2_scheme)):
                   
    """
    Get service frequency by ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    document = db_office_master.get_service_frequency_by_id(db,ID)  
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"frequency  with id {ID} not found" 
        )
    return document

@router.delete('/service_frequency/{id}')
def delete_service_frequency(id: int, db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)):
    """
    Delete service frequency  for specific ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    message =db_office_master.delete_service_frequency(db, id)
    
    return {"message": message}
#-------------------------------------------------ServiceOwner-------------------------------------------------------



@router.post('/services/save_service_owner/{ID}', response_model=ServiceOwnerDisplay)
def save_service_owner(
    ID: int,
    owner_data: ServiceOwnerDisplay,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save  or Create service owner for a specific ID.
    """
    if not token:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
         return db_office_master.save_service_owner(db, owner_data, ID)
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
       
@router.get('/services/service_owner', response_model=list[ServiceOwnerBase])
def get_all_service_owner(deleted_status: DeletedStatus =  Query(..., title="Select deleted status"),
  db: Session = Depends(get_db),
      token: str = Depends(oauth2.oauth2_scheme)):
   
    """
    Get all  service owners.
    """
    # Check if deleted_status is a valid option
    if deleted_status not in [DeletedStatus.DELETED, DeletedStatus.NOT_DELETED, DeletedStatus.ALL]:
        raise HTTPException(
            status_code=400,
            detail="Invalid value for 'deleted_status'. Allowed values are 'yes', 'no', and 'all'."
        )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_office_master.get_all_service_owner(db,deleted_status)


@router.get('/services/service_owner/{id}', response_model=ServiceOwnerBase)
def get_service_owner_by_id(ID: int,db: Session = Depends(get_db),
                                  token: str = Depends(oauth2.oauth2_scheme)):
                   
    """
    Get service owner by ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    document = db_office_master.get_service_owner_by_id(db,ID)  
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"service owner  with id {ID} not found" 
        )
    return document



@router.delete('/services/service_owner/{id}')
def delete_service_owner(id: int, db: Session = Depends(get_db),
                        token: str = Depends(oauth2.oauth2_scheme) ):
    """
    Delete service owner  for specific ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    message = db_office_master.delete_service_owner(db, id)
    
    return {"message": message}

#--------------------------------------------app_service_generation_mode---------------------------------------------------------




@router.post('/save_service_generation_mode/{id}', response_model=ServiceGenerationModeDisplay)
def save_service_generation_mode(
    ID: int,
    gen_mode_data: ServiceGenerationModeDisplay,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save  or Create service_generation_mode for a specific ID.
    """
    if not token:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
         return db_office_master.save_service_generation_mode(db, gen_mode_data, ID)
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
       
@router.get('/service_generation_mode', response_model=list[ServiceGenerationModeBase])
def get_all_service_generation_mode(deleted_status: DeletedStatus =  Query(..., title="Select deleted status"),
  db: Session = Depends(get_db),
      token: str = Depends(oauth2.oauth2_scheme)):
   
    """
    Get all  service_generation_modes  as all,deleted.not deleted.
    """
    # Check if deleted_status is a valid option
    if deleted_status not in [DeletedStatus.DELETED, DeletedStatus.NOT_DELETED, DeletedStatus.ALL]:
        raise HTTPException(
            status_code=400,
            detail="Invalid value for 'deleted_status'. Allowed values are 'yes', 'no', and 'all'."
        )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_office_master.get_all_service_generation_mode(db,deleted_status)


@router.get('/service_generation_mode/{id}', response_model=ServiceGenerationModeBase)
def get_service_generation_mode_by_id(id: int,db: Session = Depends(get_db),
                                  token: str = Depends(oauth2.oauth2_scheme)):
                   
    """
    Get service_generation_mode by ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    document = db_office_master.get_service_generation_mode_by_id(db,id )  
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"service owner  with id {id} not found" 
        )
    return document


@router.delete('/service_generation_mode/{id}')
def delete_service_generation_mode(id: int, db: Session = Depends(get_db),
                        token: str = Depends(oauth2.oauth2_scheme) ):
    """
    Delete service generation mode for specific ID. Set is_deleted to 'yes'.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    message = db_office_master.delete_service_generation_mode(db, id)
    
    return {"message": message}
#------------------------------------------------app_stock_keeping_unit_code-------------------------------------------------------------------------



@router.post('/save_stock_keeping_unit_code/{id}', response_model=StockKeepingUnitCodeDisplay)
def save_stock_keeping_unit_code(
    ID: int,
    unit_code_data: StockKeepingUnitCodeDisplay,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save  or Create stock keeping unit code for a specific ID.
    """
    if not token:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    try:
         return db_office_master.save_stock_keeping_unit_code(db, unit_code_data, ID)
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
       
@router.get('/stock_keeping_unit_code', response_model=list[StockKeepingUnitCodeBase])
def get_all_stock_keeping_unit_code(deleted_status: DeletedStatus =  Query(..., title="Select deleted status"),
  db: Session = Depends(get_db),
      token: str = Depends(oauth2.oauth2_scheme)):
   
    """
    Get all  stock_keeping_unit_code  as all,deleted.not deleted.
    """
    # Check if deleted_status is a valid option
    if deleted_status not in [DeletedStatus.DELETED, DeletedStatus.NOT_DELETED, DeletedStatus.ALL]:
        raise HTTPException(
            status_code=400,
            detail="Invalid value for 'deleted_status'. Allowed values are 'yes', 'no', and 'all'."
        )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return db_office_master.get_all_stock_keeping_unit_code(db,deleted_status)


@router.get('/stock_keeping_unit_code/{id}', response_model=StockKeepingUnitCodeBase)
def get_stock_keeping_unit_code_by_id(id: int,db: Session = Depends(get_db),
                                  token: str = Depends(oauth2.oauth2_scheme)):
                   
    """
    Get stock keeping unit code by ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    document = db_office_master.get_stock_keeping_unit_code_by_id(db,id )  
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"stock keeping unit code with id {id} not found" 
        )
    return document


@router.delete('/stock_keeping_unit_code/{id}')
def delete_stock_keeping_unit_code(id: int, db: Session = Depends(get_db),
                        token: str = Depends(oauth2.oauth2_scheme) ):
    """
    Delete stock keeping unit code for specific ID. Set is_deleted to 'yes'.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    message = db_office_master.delete_stock_keeping_unit_code(db, id)
    

    return {"message": message}

#-----------------------------------app_hsn_sac_classes---------------------------------------------------------



@router.post('/save_hsn_sac_classes/{id}', response_model=HsnSacClassesDisplay)
def save_hsn_sac_classes(
    id: int,
    hsn_data: HsnSacClassesDisplay,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save or create HSN/SAC class for a specific ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    try:
        return db_office_master.save_hsn_sac_classes(db, hsn_data, id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save HSN/SAC class: {str(e)}")

@router.get('/hsn_sac_classes', response_model=list[HsnSacClassesBase])
def get_all_hsn_sac_classes(
    deleted_status: DeletedStatus = Query(..., title="Select deleted status"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get all HSN/SAC classes based on the provided deleted status.
    """
    # Check if deleted_status is a valid option
    if deleted_status not in [DeletedStatus.DELETED, DeletedStatus.NOT_DELETED, DeletedStatus.ALL]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid value for 'deleted_status'. Allowed values are 'yes', 'no', and 'all'."
        )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.get_all_hsn_sac_classes(db, deleted_status)

@router.get('/hsn_sac_classes/{id}', response_model=HsnSacClassesBase)
def get_hsn_sac_class_by_id(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get HSN/SAC class by ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    document = db_office_master.get_hsn_sac_class_by_id(db, id)  
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HSN/SAC class with id {id} not found" 
        )
    return document

@router.delete('/hsn_sac_classes/{id}')
def delete_hsn_sac_class(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Delete HSN/SAC class for specific ID. Set is_deleted to 'yes'.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    message = db_office_master.delete_hsn_sac_class(db, id)
    return {"message": message}

#-----------HsnSacMaster---------------------------------------


@router.post('/save_hsn_sac/{id}', response_model=HsnSacMasterDisplay)
def save_hsn_sac_master(
    id: int,
    hsn_data: HsnSacMasterDisplay,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Save or create HSN/SAC for a specific ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    try:
        return db_office_master.save_hsn_sac_master(db, hsn_data, id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save HSN/SAC : {str(e)}")

@router.get('/hsn_sac_master', response_model=list[HsnSacMasterBase])
def get_all_hsn_sac_master(
    deleted_status: DeletedStatus = Query(..., title="Select deleted status"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get all HSN/SAC  based on the provided deleted status.
    """
    # Check if deleted_status is a valid option
    if deleted_status not in [DeletedStatus.DELETED, DeletedStatus.NOT_DELETED, DeletedStatus.ALL]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid value for 'deleted_status'. Allowed values are 'yes', 'no', and 'all'."
        )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_office_master.get_all_hsn_sac_master(db, deleted_status)

@router.get('/hsn_sac/{id}', response_model=HsnSacMasterBase)
def get_hsn_sac_by_id(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Get HSN/SAC  by ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    document = db_office_master.get_hsn_sac_by_id(db, id)  
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HSN/SAC class with id {id} not found" 
        )
    return document

@router.delete('/hsn_sac_master/{id}')
def delete_hsn_sac(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
    Delete HSN/SAC  for specific ID. Set is_deleted to 'yes'.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    message = db_office_master.delete_hsn_sac_master(db, id)
    return {"message": message}


# @router.post("/hsn_sac_master_with_file/")
# async def upload_hsn_sac_master_with_file(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_scheme)
# ):
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

#     result = await db_office_master.save_csv_to_db(file, db)
#     return result
 

@router.post("/hsn_sac_master_with_file/")
async def upload_hsn_sac_master_with_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    result = await db_office_master.save_csv_to_db(file, db)
    return result

