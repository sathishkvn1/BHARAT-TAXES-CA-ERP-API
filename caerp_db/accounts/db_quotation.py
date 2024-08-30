from fastapi import HTTPException,Query
from sqlalchemy.orm import Session,aliased
from caerp_db.office.models import OffViewServiceGoodsMaster,OffViewServiceGoodsPriceMaster,WorkOrderDetailsView, WorkOrderMasterView,OffWorkOrderMaster
from caerp_schema.office.office_schema import OffWorkOrderMasterSchema,OffViewServiceGoodsPriceMasterSchema,OffViewWorkOrderMasterSchema,ServiceGoodsPriceDetailsSchema,OffViewWorkOrderDetailsSchema,ServiceGoodsPriceResponseSchema
from caerp_schema.accounts.quotation_schema import AccQuotationMasterSchema,AccQuotationSchema,AccQuotationDetailsSchema,AccQuotationResponseSchema
from caerp_db.accounts.models import AccQuotationMaster,AccQuotationDetails
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_,or_, func
from datetime import date, datetime
from caerp_constants.caerp_constants import EntryPoint
from caerp_functions.send_email import send_email
from caerp_schema.common.common_schema import Email
from sqlalchemy.exc import IntegrityError
from caerp_functions.generate_book_number import generate_book_number
from typing import Optional,Union,List

def get_service_price_details_by_service_id(
        db:Session,
        service_master_id: int,
        constitution_id: int
):
    service_goods_price_data = None
    service_goods_price_details_data = db.query(OffViewServiceGoodsPriceMaster).filter(
                OffViewServiceGoodsPriceMaster.service_goods_master_id == service_master_id,
                OffViewServiceGoodsPriceMaster.constitution_id == constitution_id,
                 or_(
                    OffViewServiceGoodsPriceMaster.effective_to_date.is_(None),
                    OffViewServiceGoodsPriceMaster.effective_to_date > datetime.utcnow().date(),
                ),
                OffViewServiceGoodsPriceMaster.effective_from_date <= datetime.utcnow().date()
            ).first()

    if service_goods_price_details_data:
        # Validate and append the price data
        service_goods_price_data = OffViewServiceGoodsPriceMasterSchema.model_validate(service_goods_price_details_data.__dict__)
    return service_goods_price_data

def generate_quotation_service_details(
    db: Session,
    work_order_master_id: int,
) -> ServiceGoodsPriceResponseSchema:
    try:
        # Fetch master data
        work_order_master_data = db.query(WorkOrderMasterView).filter(
            WorkOrderMasterView.work_order_master_id == work_order_master_id
        ).first()

        work_order_details_data = db.query(WorkOrderDetailsView).filter(
            WorkOrderDetailsView.work_order_master_id == work_order_master_id,
            WorkOrderDetailsView.is_main_service == 'yes',
            WorkOrderDetailsView.is_deleted == 'no'
        ).all()

        services = []
        service_goods_price_data = None

        # Loop through each detail to fetch its price data
        for details in work_order_details_data:
            service_master_id = details.service_goods_master_id
            constitution_id = details.constitution_id

            # Initialize total values for each service
            total_service_charge = 0.0
            total_govt_agency_fee = 0.0
            total_stamp_fee = 0.0
            total_stamp_duty = 0.0

            if details.is_bundle_service == 'no':
                service_goods_price_data = get_service_price_details_by_service_id(db, service_master_id, constitution_id)
                if service_goods_price_data:
                    total_service_charge = service_goods_price_data.service_charge
                    total_govt_agency_fee = service_goods_price_data.govt_agency_fee
                    total_stamp_fee = service_goods_price_data.stamp_fee
                    total_stamp_duty = service_goods_price_data.stamp_duty
            else:
                service_goods_price_data = get_service_price_details_by_service_id(db, service_master_id, constitution_id)
                if service_goods_price_data:
                    total_service_charge = service_goods_price_data.service_charge
                    total_govt_agency_fee = service_goods_price_data.govt_agency_fee
                    total_stamp_fee = service_goods_price_data.stamp_fee
                    total_stamp_duty = service_goods_price_data.stamp_duty

                sub_services = db.query(WorkOrderDetailsView).filter(
                    WorkOrderDetailsView.bundle_service_id == details.work_order_details_id,
                    WorkOrderDetailsView.is_deleted == 'no'
                ).all()

                for sub_service in sub_services:
                    sub_service_price_data = get_service_price_details_by_service_id(db, sub_service.service_goods_master_id, sub_service.constitution_id)
                    if sub_service_price_data:
                        total_service_charge += sub_service_price_data.service_charge
                        total_govt_agency_fee += sub_service_price_data.govt_agency_fee
                        total_stamp_fee += sub_service_price_data.stamp_fee
                        total_stamp_duty += sub_service_price_data.stamp_duty

            if service_goods_price_data:
                service_goods_price_data.service_charge = total_service_charge
                service_goods_price_data.govt_agency_fee = total_govt_agency_fee
                service_goods_price_data.stamp_duty = total_stamp_duty
                service_goods_price_data.stamp_fee = total_stamp_fee

            # Validate and append the work order detail with its price data
            service_data = ServiceGoodsPriceDetailsSchema(
                service=OffViewWorkOrderDetailsSchema.model_validate(details.__dict__),
                prices=service_goods_price_data
            )
            services.append(service_data)

        # try:
            quotation_master = AccQuotationMaster(
                work_order_master_id=work_order_master_id,
                quotation_version=1,
                quotation_date=datetime.utcnow().date(),
                quotation_number=generate_book_number('QUOTATION', db),  # Example, generate or fetch actual
                offer_total=0,
                coupon_total=0,
                product_discount_total=0,
                bill_discount=0,
                additional_discount=0,
                round_off=total_service_charge,
                net_amount=total_service_charge + total_govt_agency_fee + total_stamp_fee + total_stamp_duty,
                grand_total=total_service_charge + total_govt_agency_fee + total_stamp_fee + total_stamp_duty,
                remarks='',
                quotation_status='DRAFT',
                is_final_quotation='no',
                created_by= 1,
                created_on=datetime.utcnow()
            )
            db.add(quotation_master)
            db.flush()  # To get the new quotation_master.id

            for service_data in services:
                details = service_data.service
                prices = service_data.prices

                quotation_detail = AccQuotationDetails(
                    quotation_master_id=quotation_master.id,
                    service_goods_master_id=details.service_goods_master_id,
                    # hsn_sac_code=details.hsn_sac_code,
                    is_bundle_service=details.is_bundle_service,
                    bundle_service_id=details.bundle_service_id,
                    service_charge=prices.service_charge,
                    govt_agency_fee=prices.govt_agency_fee,
                    stamp_duty=prices.stamp_duty,
                    stamp_fee=prices.stamp_fee,
                    quantity=1,
                    offer_percentage = 0.0,
                    offer_amount = 0.0,
                    coupon_percentage = 0.0,
                    coupon_amount = 0.0,
                    discount_percentage = 0.0,
                    discount_amount = 0.0,
                    gst_percent=0.0,
                    gst_amount=0,
                    taxable_amount= 0.0,
                   
                    total_amount=total_service_charge + total_govt_agency_fee + total_stamp_fee + total_stamp_duty,
                )

                db.add(quotation_detail)
            db.commit()
            # return quotation_master.id
            return {"message": "Quotation saved successfully",
                     "quotation_master_id": quotation_master.id,
                     "quotation_detail_id": quotation_detail.id}

     
        # except Exception as e:
        #     db.rollback()
        #     raise HTTPException(status_code=500, detail=f"An unexpected error occurred, {str(e)}")

    except SQLAlchemyError as e:
        db.rollback()
        # Handle database exceptions
        raise HTTPException(status_code=500, detail=str(e))



def save_quotation_data(
        request : AccQuotationSchema,
        user_id : int,       
        db : Session ,
        quotation_id : Optional[int]= None
):
    try:

            if quotation_id != 0: 
                quotation_data = db.query(AccQuotationMaster).filter(
                    AccQuotationMaster.id == quotation_id
                ).first()

                if quotation_data:
                    quotation_status = quotation_data.quotation_status
                    if quotation_status=='REQUESTED REVISION':
                        new_quotation_master = AccQuotationMaster(
                                quotation_version=quotation_data.quotation_version + 1,
                                # quotation_number=quotation_data.quotation_number,  # Retain the same quotation number
                                # quotation_date=quotation_data.quotation_date,  # Retain the same quotation date
                                quotation_status="DRAFT",  # Set the status to "DRAFT"
                                created_by=user_id,
                                created_on=datetime.utcnow(),
                                **request.quotation_master.dict(exclude_unset=True)
                            )
                        db.add(new_quotation_master)
                        db.flush()
                        for detail in request.quotation_details:
                    
                            quotation_detail = AccQuotationDetails(
                                quotation_master_id=new_quotation_master.id,
                                **detail.model_dump(exclude_unset=True)
                            )
                            db.add(quotation_detail)
                        db.commit()
                        return {"message": "Quotation saved successfully", "quotation_master_id": new_quotation_master.id}

                    elif quotation_status == "DRAFT":
                    # Update the existing quotation master
                        for key, value in request.quotation_master.model_dump(exclude_unset=True).items():
                            setattr(quotation_data, key, value)
                        quotation_data.modified_by = user_id
                        quotation_data.modified_on = datetime.utcnow()

                        # Update existing quotation details
                        for detail in request.quotation_details:
                            existing_detail = db.query(AccQuotationDetails).filter(
                                AccQuotationDetails.id == detail.id
                            ).first()

                            if existing_detail:
                                # Update existing detail
                                for key, value in detail.dict(exclude_unset=True).items():
                                    setattr(existing_detail, key, value)
                                existing_detail.modified_by = user_id
                                existing_detail.modified_on = datetime.utcnow()
                            else:
                                # Insert new detail if it does not exist
                                new_detail = AccQuotationDetails(
                                    quotation_master_id=quotation_data.id,
                                    **detail.model_dump(exclude_unset=True)
                                )
                                db.add(new_detail)

                        db.commit()
                        return {"message": "Quotation updated successfully", "quotation_master_id": quotation_data.id}

            else:
                raise HTTPException(status_code=404, detail="Quotation not found")


                # else:
                #     raise HTTPException(status_code=404, detail="Quotation not found")
        # with db.begin():
            if quotation_id == 0  :
                quotation_number  = generate_book_number('QUOTATION',db)
                quotation_master = AccQuotationMaster(
                    quotation_version = 1,
                    quotation_number = quotation_number,
                    quotation_date = datetime.utcnow().date(),
                    created_by=user_id,
                    created_on=datetime.utcnow(),
                    **request.quotation_master.dict(exclude_unset=True)
                )
                db.add(quotation_master)
                db.flush()
                # if isinstance(request.quotation_details, list):
                for detail in request.quotation_details:
                    # Ensure each detail is an instance of AccQuotationDetailsSchema
                    # if isinstance(detail, AccQuotationDetailsSchema):
                        quotation_detail = AccQuotationDetails(
                            quotation_master_id=quotation_master.id,
                            **detail.dict(exclude_unset=True)
                        )
                        db.add(quotation_detail)
                # else:
                #     raise HTTPException(status_code=400, detail="Quotation details should be a list.")

            db.commit()
            return {"message": "Quotation saved successfully", "quotation_master_id": quotation_master.id}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error occurred,{ str(e)}")

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error occurred, {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred,{ str(e)}")


def update_quotation_status(
        quotation_id : int,
        quotation_status : str,
        # quotation_version: int,
        db:Session
):
    quotation_data = db.query(AccQuotationMaster).filter(AccQuotationMaster.id == quotation_id).first()
    if quotation_data:
        quotation_data.quotation_status = quotation_status
        quotation_data.modified_on = datetime.utcnow()
            
            # Commit the changes to the database
        db.commit()
        return {'message': 'Quotation status updated successfully',
                'success': True}
            
    else:
        return {'message': 'please provide a valid quotqtion id',
                'success': False}
    
def send_proposal(
        quotation_id: int,
        work_order_master_id: int,
        db:Session):
    work_order_master_data = db.query(WorkOrderMasterView).filter(
        WorkOrderMasterView.work_order_master_id == work_order_master_id).first()
    
    email = Email(
        messageTo = work_order_master_data.email_id,
        subject=  "Quotation verification",
        messageBody = f"This is for compleating your quotation",
        messageType= "NO_REPLY"
    )
    result = send_email(email,db)
    return result


# def get_quotation_data(
#     db: Session,
#     status: Optional[str] = 'ALL',
#     work_order_master_id : Optional[int] = None,
#     quotation_id: Optional[int] = None,
#     from_date: Optional[date] = Query(date.today()),
#     to_date: Optional[date] = None
# ) -> Union[AccQuotationResponseSchema, List[AccQuotationResponseSchema]]:
#     try:
#         latest_version_subquery = (
#             db.query(
#                 AccQuotationMaster.work_order_master_id,
#                 func.max(AccQuotationMaster.quotation_version).label("latest_version")
#             )
#             .group_by(AccQuotationMaster.work_order_master_id)
#             .subquery()
#         )

#         # Alias for AccQuotationMaster to join ith the subquery
#         latest_version_alias = aliased(AccQuotationMaster, latest_version_subquery)

#         # Main query to get the latest version records
#         query = db.query(AccQuotationMaster).join(
#             latest_version_subquery,
#             (AccQuotationMaster.work_order_master_id == latest_version_subquery.c.work_order_master_id) &
#             (AccQuotationMaster.quotation_version == latest_version_subquery.c.latest_version)
#         )
#         if work_order_master_id:
#             query = query.filter(AccQuotationMaster.work_order_master_id== work_order_master_id)
#         # Apply filters based on provided parameters
#         if quotation_id:
#             query = query.filter(AccQuotationMaster.id == quotation_id)
#             quotation_data = query.group_by(AccQuotationMaster.work_order_master_id).first()
            
#             if not quotation_data:
#                 return {"message": "Quotation not found."}
            
#             # Fetch related work order and details
#             work_order_master_data = db.query(WorkOrderMasterView).filter(
#                 WorkOrderMasterView.work_order_master_id == quotation_data.work_order_master_id
#             ).first()
            
#             # Fetch quotation details
#             # quotation_details_data = db.query(AccQuotationDetails).filter(
#             #     AccQuotationDetails.quotation_master_id == quotation_data.id,
#             #     AccQuotationDetails.is_deleted == 'no'
#             # ).all()
#             quotation_details_data = db.query(
#                 AccQuotationDetails,
#                 OffViewServiceGoodsMaster.service_goods_name
#             ).join(
#                 OffViewServiceGoodsMaster,  # Joining with the alias defined
#                 AccQuotationDetails.service_goods_master_id == OffViewServiceGoodsMaster.service_goods_master_id
#             ).filter(
#                 AccQuotationDetails.quotation_master_id == quotation_data.id,
#                 AccQuotationDetails.is_deleted == 'no'
#             ).all()
#             # print('Query Statement', query)
#             print('quotation_details_data', quotation_details_data)
#             # Construct response schema for a single quotation
#             quotation_service_price_data = AccQuotationResponseSchema(
#                 quotation_master=AccQuotationMasterSchema.model_validate(quotation_data.__dict__),
#                 work_order_master=OffWorkOrderMasterSchema.model_validate(work_order_master_data.__dict__),
#                 quotation_details=[AccQuotationDetailsSchema.model_validate(detail.__dict__) for detail in quotation_details_data]
#             )
            
#             return quotation_service_price_data
#         else:
#             if status != 'ALL':
#                 query = query.filter(AccQuotationMaster.quotation_status == status)
            
#             if from_date and to_date:
#                 query = query.filter(
#                     AccQuotationMaster.quotation_date >= from_date,
#                     AccQuotationMaster.quotation_date <= to_date
#                 )
#             elif from_date:
#                 query = query.filter(AccQuotationMaster.quotation_date >= from_date)
#             elif to_date:
#                 query = query.filter(AccQuotationMaster.quotation_date <= to_date)

#             # Fetch all filtered quotations
#             quotation_master_list = query.all()
           
#             # Construct response schema for multiple quotations
#             quotations_response = []
#             for quotation in quotation_master_list:
#                 work_order_master_data = db.query(WorkOrderMasterView).filter(
#                     WorkOrderMasterView.work_order_master_id == quotation.work_order_master_id
#                 ).first()
                
#                 quotation_details_data = db.query(AccQuotationDetails).filter(
#                     AccQuotationDetails.quotation_master_id == quotation.id,
#                     AccQuotationDetails.is_deleted == 'no'
#                 ).all()
                
#                 # Add each quotation's data to the response list
#                 quotations_response.append(AccQuotationResponseSchema(
#                     quotation_master=AccQuotationMasterSchema.model_validate(quotation.__dict__),
#                     work_order_master=OffWorkOrderMasterSchema.model_validate(work_order_master_data.__dict__),
#                     quotation_details=[AccQuotationDetailsSchema.model_validate(detail.__dict__) for detail in quotation_details_data]
#                 ))

#             return quotations_response

#     except SQLAlchemyError as e:
#         # Handle database exceptions
#         raise HTTPException(status_code=500, detail=str(e))

def get_quotation_data(
    db: Session,
    status: Optional[str] = 'ALL',
    work_order_master_id: Optional[int] = None,
    quotation_id: Optional[int] = None,
    from_date: Optional[date] = Query(date.today()),
    to_date: Optional[date] = None
) -> Union[AccQuotationResponseSchema, List[AccQuotationResponseSchema]]:
    try:
        latest_version_subquery = (
            db.query(
                AccQuotationMaster.work_order_master_id,
                func.max(AccQuotationMaster.quotation_version).label("latest_version")
            )
            .group_by(AccQuotationMaster.work_order_master_id)
            .subquery()
        )

        # Main query to get the latest version records
        query = db.query(AccQuotationMaster).join(
            latest_version_subquery,
            (AccQuotationMaster.work_order_master_id == latest_version_subquery.c.work_order_master_id) &
            (AccQuotationMaster.quotation_version == latest_version_subquery.c.latest_version)
        )
        if work_order_master_id:
            query = query.filter(AccQuotationMaster.work_order_master_id == work_order_master_id)
        # Apply filters based on provided parameters
        if quotation_id:
            query = query.filter(AccQuotationMaster.id == quotation_id)
            quotation_data = query.group_by(AccQuotationMaster.work_order_master_id).first()
            
            if not quotation_data:
                return {"message": "Quotation not found."}
            
            # Fetch related work order and details
            work_order_master_data = db.query(WorkOrderMasterView).filter(
                WorkOrderMasterView.work_order_master_id == quotation_data.work_order_master_id
            ).first()
            
            # Fetch quotation details with the join to get service names
            quotation_details_data = db.query(
                AccQuotationDetails,
                OffViewServiceGoodsMaster.service_goods_name
            ).join(
                OffViewServiceGoodsMaster,
                AccQuotationDetails.service_goods_master_id == OffViewServiceGoodsMaster.service_goods_master_id
            ).filter(
                AccQuotationDetails.quotation_master_id == quotation_data.id,
                AccQuotationDetails.is_deleted == 'no'
            ).all()

            # Correctly handle the results as tuples
            quotation_details_list = []
            for detail, service_name in quotation_details_data:
                detail_dict = detail.__dict__.copy()  # Copy to modify
                detail_dict['service_goods_name'] = service_name
                quotation_details_list.append(AccQuotationDetailsSchema.model_validate(detail_dict))

            # Construct response schema for a single quotation
            quotation_service_price_data = AccQuotationResponseSchema(
                quotation_master=AccQuotationMasterSchema.model_validate(quotation_data.__dict__),
                work_order_master=OffViewWorkOrderMasterSchema.model_validate(work_order_master_data.__dict__),
                quotation_details=quotation_details_list
            )
            
            return quotation_service_price_data
        else:
            if status != 'ALL':
                query = query.filter(AccQuotationMaster.quotation_status == status)
            
            if from_date and to_date:
                query = query.filter(
                    AccQuotationMaster.quotation_date >= from_date,
                    AccQuotationMaster.quotation_date <= to_date
                )
            elif from_date:
                query = query.filter(AccQuotationMaster.quotation_date >= from_date)
            elif to_date:
                query = query.filter(AccQuotationMaster.quotation_date <= to_date)

            # Fetch all filtered quotations
            quotation_master_list = query.all()
           
            # Construct response schema for multiple quotations
            quotations_response = []
            for quotation in quotation_master_list:
                work_order_master_data = db.query(WorkOrderMasterView).filter(
                    WorkOrderMasterView.work_order_master_id == quotation.work_order_master_id
                ).first()
                
                # quotation_details_data = db.query(AccQuotationDetails).filter(
                #     AccQuotationDetails.quotation_master_id == quotation.id,
                #     AccQuotationDetails.is_deleted == 'no'
                # ).all()
                quotation_details_data = db.query(
                AccQuotationDetails,
                    OffViewServiceGoodsMaster.service_goods_name
                ).join(
                    OffViewServiceGoodsMaster,
                    AccQuotationDetails.service_goods_master_id == OffViewServiceGoodsMaster.service_goods_master_id
                ).filter(
                    AccQuotationDetails.quotation_master_id == quotation.id,
                    AccQuotationDetails.is_deleted == 'no'
                ).all()

                # Correctly handle the results as tuples
                quotation_details_list = []
                for detail, service_name in quotation_details_data:
                    detail_dict = detail.__dict__.copy()  # Copy to modify
                    detail_dict['service_goods_name'] = service_name
                    quotation_details_list.append(AccQuotationDetailsSchema.model_validate(detail_dict))

                
                # Add each quotation's data to the response list
                quotations_response.append(AccQuotationResponseSchema(
                    quotation_master=AccQuotationMasterSchema.model_validate(quotation.__dict__),
                    work_order_master=OffViewWorkOrderMasterSchema.model_validate(work_order_master_data.__dict__),
                    # quotation_details=[AccQuotationDetailsSchema.model_validate(detail.__dict__) for detail in quotation_details_data]
                    quotation_details = quotation_details_list
                ))

            return quotations_response

    except SQLAlchemyError as e:
        # Handle database exceptions
        raise HTTPException(status_code=500, detail=str(e))
