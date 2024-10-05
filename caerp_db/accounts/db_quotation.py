from fastapi import HTTPException,Query
from sqlalchemy.orm import Session,aliased
from caerp_db.office.models import CustomerDataDocumentMaster, OffAppointmentVisitDetails, OffAppointmentVisitMasterView, OffConsultantServiceDetails, OffServiceTaskMaster, OffViewServiceGoodsMaster,OffWorkOrderDetails,OffViewServiceGoodsPriceMaster,WorkOrderDetailsView, WorkOrderMasterView,OffWorkOrderMaster
from caerp_schema.office.office_schema import OffWorkOrderMasterSchema,OffViewServiceGoodsPriceMasterSchema,OffViewWorkOrderMasterSchema,ServiceGoodsPriceDetailsSchema,OffViewWorkOrderDetailsSchema,ServiceGoodsPriceResponseSchema, ServiceRequirementSchema
from caerp_schema.accounts.quotation_schema import AccInvoiceResponceSchema, AccProformaInvoiceDetailsSchema, AccProformaInvoiceMasterSchema, AccProformaInvoiceResponceSchema, AccProformaInvoiceShema, AccQuotationMasterSchema,AccQuotationSchema,AccQuotationDetailsSchema,AccQuotationResponseSchema, AccTaxInvoiceDetailsSchema, AccTaxInvoiceMasterSchema, AccTaxInvoiceResponceSchema, AccTaxInvoiceShema
from caerp_db.accounts.models import AccProformaInvoiceDetails, AccProformaInvoiceMaster, AccQuotationMaster,AccQuotationDetails, AccTaxInvoiceDetails, AccTaxInvoiceMaster
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_,or_, func, text
from datetime import date, datetime
from caerp_constants.caerp_constants import EntryPoint
from caerp_functions.send_email import send_email
from caerp_schema.common.common_schema import Email
from sqlalchemy.exc import IntegrityError
from caerp_functions.generate_book_number import generate_book_number, generate_voucher_id
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

#--------------------------------------------------------------------------------------------------
def generate_quotation_service_details(
    db: Session,
    work_order_master_id: int,
) -> ServiceGoodsPriceResponseSchema:
    try:
        
        existing_data = db.query(AccQuotationMaster).filter(
            AccQuotationMaster.work_order_master_id == work_order_master_id,
            AccQuotationMaster.is_deleted == 'no'
        ).order_by(AccQuotationMaster.quotation_version.desc()).first()

        if existing_data:
            return {'message': 'Quotation is already exist',
                    'quotation_master_id' : existing_data.id}
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
        quotation_master = AccQuotationMaster(
            work_order_master_id=work_order_master_id,
            quotation_version=1,
            quotation_date=datetime.utcnow().date(),
            quotation_number=generate_book_number('QUOTATION', db),  # Example, generate or fetch actual
            offer_total=0,
            coupon_total=0,
            bill_discount=0,
            additional_discount=0,
            round_off=0,
            net_amount=0,
            grand_total= 0,
            remarks='',
            quotation_status='DRAFT',
            is_final_quotation='no',
            created_by= 1,
            created_on=datetime.utcnow()
        )
        db.add(quotation_master)
        db.flush() 
            
        # Loop through each detail to fetch its price data
        for details in work_order_details_data:
            service_master_id = details.service_goods_master_id
            constitution_id = details.constitution_id
            # Initialize total values for each service
            total_service_charge = 0.0
            total_govt_agency_fee = 0.0
            total_stamp_fee = 0.0
            total_stamp_duty = 0.0
            hsn_sac_code = ''
            quotation_total_amount = 0.0
            product_discount_total = 0.0
            # if details.is_bundle_service == 'no':
            service_goods_price_data = get_service_price_details_by_service_id(db, service_master_id, constitution_id)
            if service_goods_price_data:
                total_service_charge = service_goods_price_data.service_charge
                total_govt_agency_fee = service_goods_price_data.govt_agency_fee
                total_stamp_fee = service_goods_price_data.stamp_fee
                total_stamp_duty = service_goods_price_data.stamp_duty
                hsn_sac_code = service_goods_price_data.hsn_sac_code
            
            if details.is_bundle_service == 'yes':
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
                        hsn_sac_code = sub_service_price_data.hsn_sac_code

            if service_goods_price_data:
                service_goods_price_data.service_charge = total_service_charge
                service_goods_price_data.govt_agency_fee = total_govt_agency_fee
                service_goods_price_data.stamp_duty = total_stamp_duty
                service_goods_price_data.stamp_fee = total_stamp_fee
                service_goods_price_data.hsn_sac_code             = hsn_sac_code

            # Validate and append the work order detail with its price data
            service_data = ServiceGoodsPriceDetailsSchema(
                service=OffViewWorkOrderDetailsSchema.model_validate(details.__dict__),
                prices=service_goods_price_data
            )
            services.append(service_data)
        
        # try:
         # To get the new quotation_master.id

        for service_data in services:
            details = service_data.service
            prices = service_data.prices
            quotation_detail = AccQuotationDetails(
                quotation_master_id=quotation_master.id,
                service_goods_master_id=details.service_goods_master_id,
                hsn_sac_code=hsn_sac_code,
                is_bundle_service=details.is_bundle_service,
                bundle_service_id=details.bundle_service_id,
                service_charge=prices.service_charge,
                # service_charge= total_service_charge,
                # govt_agency_fee = total_govt_agency_fee,
                # stamp_duty = total_stamp_duty,
                # stamp_fee = total_stamp_fee,
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
                gst_percent=10.0,
                gst_amount=0,
                # taxable_amount= total_service_charge - details.offer_amount - details.coupon_amount - details.discount_amount  ,
                # taxable_amount = total_service_charge,
                # total_amount=total_service_charge + total_govt_agency_fee + total_stamp_fee + total_stamp_duty,
                taxable_amount = prices.service_charge,
                total_amount = prices.service_charge + prices.govt_agency_fee + prices.stamp_duty + prices.stamp_fee 
            )
        
            db.add(quotation_detail)
                
            gst_amount = quotation_detail.taxable_amount * (quotation_detail.gst_percent /100)
            quotation_detail.gst_amount = gst_amount
            quotation_detail.total_amount = quotation_detail.total_amount+gst_amount - quotation_detail.discount_amount
            quotation_total_amount += quotation_detail.total_amount 
            product_discount_total +=quotation_detail.discount_amount  
            
        quotation_master.grand_total = quotation_total_amount 
        quotation_master.net_amount = quotation_total_amount - quotation_master.additional_discount
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


#=-------------------------------------------------------------------------------------------


def save_quotation_data(
        request : AccQuotationSchema,
        user_id : int,       
        db : Session ,
        quotation_id : Optional[int]= None
):
    try:

            if quotation_id != 0: 
                
                quotation_data = db.query(AccQuotationMaster).filter(
                    AccQuotationMaster.id == quotation_id,
                    AccQuotationMaster.is_deleted == 'no'
                ).order_by(AccQuotationMaster.quotation_version.desc()).first()


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

                    elif quotation_status in ["DRAFT", "SENT"]:
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
                        return {
                            'message': 'quotation is already accepted ',
                            'quotation_status': quotation_data.quotation_status
                        }
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

#--------------------------------------------------------------------------------------------------
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
        if quotation_status== 'ACCEPTED':
            quotation_data.is_final_quotation  = 'yes'
            
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



def get_quotation_data(
    db: Session,
    status: Optional[str] = 'ALL',
    work_order_master_id: Optional[int] = None,
    quotation_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search_value: Union[str, int] = "ALL"
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

        # Add a join to WorkOrderMasterView with the proper condition
        query = query.join(
            WorkOrderMasterView,
            AccQuotationMaster.work_order_master_id == WorkOrderMasterView.work_order_master_id
        )

        # Apply filters based on provided parameters
        if work_order_master_id:
            query = query.filter(AccQuotationMaster.work_order_master_id == work_order_master_id)
        
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

        # Add condition for search value if it's not 'ALL'
        if search_value != "ALL":
            query = query.filter(
                or_(
                    WorkOrderMasterView.first_name.like(f"%{search_value}%"),
                    WorkOrderMasterView.email_id.like(f"%{search_value}%"),
                    WorkOrderMasterView.mobile_number.like(f"%{search_value}%")
                )
            )

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
            ).distinct().all()

            # Handle the results as tuples
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
            # Fetch all filtered quotations
            quotation_master_list = query.all()

            # Construct response schema for multiple quotations
            quotations_response = []
            for quotation in quotation_master_list:
                work_order_master_data = db.query(WorkOrderMasterView).filter(
                    WorkOrderMasterView.work_order_master_id == quotation.work_order_master_id
                ).first()

                quotation_details_data = db.query(
                    AccQuotationDetails,
                    OffViewServiceGoodsMaster.service_goods_name
                ).join(
                    OffViewServiceGoodsMaster,
                    AccQuotationDetails.service_goods_master_id == OffViewServiceGoodsMaster.service_goods_master_id
                ).filter(
                    AccQuotationDetails.quotation_master_id == quotation.id,
                    AccQuotationDetails.is_deleted == 'no'
                ).distinct().all()

                # Handle the results as tuples
                quotation_details_list = []
                for detail, service_name in quotation_details_data:
                    detail_dict = detail.__dict__.copy()  # Copy to modify
                    detail_dict['service_goods_name'] = service_name
                    quotation_details_list.append(AccQuotationDetailsSchema.model_validate(detail_dict))

                quotations_response.append(AccQuotationResponseSchema(
                    quotation_master=AccQuotationMasterSchema.model_validate(quotation.__dict__),
                    work_order_master=OffViewWorkOrderMasterSchema.model_validate(work_order_master_data.__dict__),
                    quotation_details=quotation_details_list
                ))

            return quotations_response

    except SQLAlchemyError as e:
        # Handle database exceptions
        raise HTTPException(status_code=500, detail=str(e))


#-------------------------------------------------------------
def generate_profoma_invoice_details(
        db: Session,
        work_order_master_id: int,
        user_id: int):
    try:
        # Check if an invoice already exists
        existing_data = db.query(AccProformaInvoiceMaster).filter(
            AccProformaInvoiceMaster.work_order_master_id == work_order_master_id,
            AccProformaInvoiceMaster.is_deleted == 'no'
        ).first()

        if existing_data:
            return {'message': 'Invoice already exists', 'proforma_invoice_master_id': existing_data.id}

        # Fetch Work Order Master data
        work_order_master_data = db.query(WorkOrderMasterView).filter(
            WorkOrderMasterView.work_order_master_id == work_order_master_id
        ).first()

        if not work_order_master_data:
            raise HTTPException(status_code=404, detail="Work Order Master not found")

        # Fetch Work Order Details data (main services only, where service_required = 'YES')
        work_order_details_data = db.query(WorkOrderDetailsView).filter(
            WorkOrderDetailsView.work_order_master_id == work_order_master_id,
            WorkOrderDetailsView.service_required == 'YES', 
            WorkOrderDetailsView.is_main_service == 'yes',
            WorkOrderDetailsView.is_deleted == 'no'
        ).all()

        if not work_order_details_data:
            raise HTTPException(status_code=404, detail="No work order details found")

        # Fetch Quotation Master data
        quotation_master_data = db.query(AccQuotationMaster).filter(
            AccQuotationMaster.work_order_master_id == work_order_master_id,
            AccQuotationMaster.is_deleted == 'no'
        ).first()

        if not quotation_master_data:
            raise HTTPException(status_code=404, detail="No quotation master data found")

        # Fetch Quotation Details data
        quotation_details_data = db.query(AccQuotationDetails).filter(
            AccQuotationDetails.quotation_master_id == quotation_master_data.id,
            AccQuotationDetails.is_deleted == 'no'
        ).all()

        if not quotation_details_data:
            raise HTTPException(status_code=404, detail="No quotation details found")

        services = []
       
        # Generate new voucher ID and invoice number
        new_voucher_id = generate_voucher_id(db)
        proforma_invoice_number = generate_book_number('INVOICE', db)

        # Create Invoice Master Entry
        proforma_invoice_master = AccProformaInvoiceMaster(
            voucher_id=new_voucher_id,
            service_type='NON_CONSULTATION',
            work_order_master_id=work_order_master_id,
            proforma_invoice_number=proforma_invoice_number,
            proforma_invoice_date=datetime.now(),
            account_head_id=1,
            created_by=user_id,
            created_on=datetime.now(),
            is_deleted='no'
        )

        db.add(proforma_invoice_master)
        db.flush()  # Ensure invoice_master.id is generated

        total_invoice_amount = 0.0
        task_id = None

        # Process each work order detail (only those required) and map it to the quotation details
        for details in work_order_details_data:
            service_document_id = save_customer_data_document_master(db, work_order_master_id, details.work_order_details_id, details.service_goods_master_id, details.constitution_id)
            
            # Filter quotation details based on the service_goods_master_id from the work order
            relevant_quotation_details = [qd for qd in quotation_details_data if qd.service_goods_master_id == details.service_goods_master_id]
            
            for quotation_detail in relevant_quotation_details:
                # Initialize totals
                total_service_charge    = quotation_detail.service_charge
                total_govt_agency_fee   = quotation_detail.govt_agency_fee
                total_stamp_fee         = quotation_detail.stamp_fee
                total_stamp_duty        = quotation_detail.stamp_duty
                total_amount            = quotation_detail.total_amount
                taxable_amount          = quotation_detail.taxable_amount

                # Create Invoice Detail Entry
                invoice_detail = AccProformaInvoiceDetails(
                    proforma_invoice_master_id  =proforma_invoice_master.id,
                    service_goods_master_id     =quotation_detail.service_goods_master_id,
                    is_bundle_service           =quotation_detail.is_bundle_service,
                    bundle_service_id           =quotation_detail.bundle_service_id,
                    service_charge              =total_service_charge,
                    govt_agency_fee             =total_govt_agency_fee,
                    stamp_duty  =total_stamp_duty,
                    stamp_fee   =total_stamp_fee,
                    quantity    =1,  
                    discount_amount = quotation_detail.discount_amount,
                    gst_percent     =quotation_detail.gst_percent,  
                    gst_amount      =quotation_detail.gst_amount,  # To be updated after calculation
                    taxable_amount  =taxable_amount,
                    # total_amount=total_service_charge + total_govt_agency_fee + total_stamp_fee + total_stamp_duty,
                    total_amount    = total_amount,
                    is_deleted      ='no'
                )

                db.add(invoice_detail)
                db.flush()

                total_invoice_amount += invoice_detail.total_amount

                # Calculate GST Amount and update the entry
                gst_amount = invoice_detail.taxable_amount * (invoice_detail.gst_percent / 100)
                invoice_detail.gst_amount = gst_amount
                proforma_invoice_master_id = proforma_invoice_master.id
                proforma_invoice_detail_id = invoice_detail.id
                task_id = save_service_task_details(db, work_order_master_id, details.work_order_details_id, proforma_invoice_master_id,proforma_invoice_detail_id, user_id)
       
        # Update Invoice Master with total amount
        proforma_invoice_master.additional_discount_amount  = quotation_master_data.additional_discount
        proforma_invoice_master.bill_discount_amount        = quotation_master_data.bill_discount
        proforma_invoice_master.round_off_amount            = quotation_master_data.round_off
        
        proforma_invoice_master.grand_total_amount          = total_invoice_amount
        proforma_invoice_master.net_amount                  = total_invoice_amount
        db.commit()

        return {
            'message': 'Success',
            'proforma_invoice_master_id': proforma_invoice_master.id,
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


#----------------------------------------------------------------------------------


def save_service_requirement_status(
        db: Session,
        request: List[ServiceRequirementSchema],
        user_id: int
):                    
    all_later = True  # Flag to check if all services are set to 'LATER'

    for data in request:
        existing_record = db.query(OffWorkOrderDetails).filter(
            OffWorkOrderDetails.id == data.work_order_details_id,
            OffWorkOrderDetails.is_deleted == 'no'
        ).first()

        try:
            if existing_record:
                # Update the existing record with the new data
                existing_record.service_required = data.service_required
                existing_record.service_required_date = data.service_required_date
                existing_record.modified_by = user_id
                existing_record.modified_on = datetime.utcnow()

                db.commit()

                # If any service is NOT set to 'LATER', set the flag to False
                if data.service_required != 'LATER':
                    all_later = False

        except Exception as e:
            db.rollback()
            print(f"Error updating service requirement: {str(e)}")
            return {'message': 'Failed to update service requirements'}

    # After looping, check if all services were set to 'LATER'
    if all_later:
        return {'message': 'No service is required now'}

    return {'message': 'Success'}
#----------------------------------------------------------------------------------------------------------
def save_service_task_details(
        db: Session,
        work_order_master_id: int,
        work_order_details_id: int,
        proforma_invoice_master_id : int,
        proforma_invoice_detail_id: int,
        user_id:int
):
    try: 
        task_number = generate_book_number('TASK',db)
        new_task = OffServiceTaskMaster(
            work_order_master_id=work_order_master_id,
            work_order_details_id=work_order_details_id,
            proforma_invoice_master_id = proforma_invoice_master_id,
            proforma_invoice_detail_id = proforma_invoice_detail_id,    
            task_number=task_number,
            allocated_by=user_id,
            allocated_on=datetime.utcnow(), 
            task_status_id=1, 
            task_priority_id=1, 
            remarks='Initial task creation')
        
        db.add(new_task)
        
        db.commit()
        return new_task.id
    except SQLAlchemyError as e:
        db.rollback()
        # Handle database exceptions
        raise HTTPException(status_code=500, detail=str(e))
   

#----------------------------------------------------------------------------------------------
def save_customer_data_document_master(
        db: Session,
        work_order_master_id: int,
        work_order_details_id: int,
        service_id: int,
        consultation_id: int
):
    # SQL query to fetch document data
    sql = text("""
        SELECT 
            d.*, b.document_data_category_id
        FROM 
            off_service_document_data_master a
        JOIN 
            off_service_document_data_details b ON a.id = b.service_document_data_master_id
        JOIN 
            off_document_data_master d ON b.document_data_master_id = d.id
        WHERE 
            a.service_goods_master_id = :service_id 
            AND a.constitution_id = :consultation_id
    """)

    # Execute the query and fetch results as dictionaries
    result = db.execute(sql, {'service_id': service_id, 'consultation_id': consultation_id}).mappings()

    # Loop through the query results and insert into CustomerDataDocumentMaster
    for row in result:
        # Access columns by name
        document_data_master_id = row['id']  # Assuming 'id' is the column name for document_data_master_id
        document_data_category_id = row['document_data_category_id']

        # Create a new instance of CustomerDataDocumentMaster
        new_document = CustomerDataDocumentMaster(
            work_order_master_id=work_order_master_id,
            work_order_details_id=work_order_details_id,
            document_data_category_id=document_data_category_id,
            document_data_master_id=document_data_master_id,          
            is_deleted='no' 
        )

        db.add(new_document)
   
    db.commit()

    # Optionally, return something or just None
    return {'message' : 'success'}



 


 

def save_profoma_invoice(
        db: Session,
        work_order_master_id: int,
        request: AccProformaInvoiceShema,
        user_id : int
):                    
    
        existing_record = db.query(AccProformaInvoiceMaster).filter(
            AccProformaInvoiceMaster.work_order_master_id == work_order_master_id,
            AccProformaInvoiceMaster.is_deleted == 'no'
        ).first()

        try:
            if existing_record:
                    for key, value in request.proforma_invoice_master.model_dump(exclude_unset=True).items():
                            setattr(existing_record, key, value)
                    existing_record.modified_by = user_id
                    existing_record.modified_on = datetime.utcnow()

            for detail in request.proforma_invoice_details:
                existing_detail = db.query(AccProformaInvoiceDetails).filter(
                    AccProformaInvoiceDetails.id == detail.id,
                    AccProformaInvoiceDetails.proforma_invoice_master_id == existing_record.id,
                    AccProformaInvoiceDetails.is_deleted == 'no'
                ).first()

                if existing_detail:
                    # Update existing details
                    for key, value in detail.model_dump(exclude_unset=True).items():
                        setattr(existing_detail, key, value)
            db.commit()
            return {'message' : 'success'}
        except SQLAlchemyError as e:
            db.rollback()  # Rollback the transaction in case of error
            raise HTTPException(status_code=500, detail=str(e))  # Raise HTTPException with error message
#-------------------------------------------------------------------------------------------------------

def get_demand_notice(
        work_order_master_id: int,
        db: Session
):
    sql = text("""
           SELECT A.*, B.document_data_type FROM off_document_data_master  AS A

            JOIN off_document_data_type AS B ON A.document_data_type_id = B.id

            WHERE A.id IN (

            SELECT document_data_master_id FROM customer_data_document_master WHERE work_order_master_id = :work_order_master_id)
        
            """)
    result = db.execute(sql, {'work_order_master_id': work_order_master_id}).mappings().all()
    
    return result
#-------------------------------------------------------------------------------------------------------------
   
 

def consultation_invoice_generation(
        work_order_master_id: int,
        appointment_id: int,
        db: Session,
        user_id: int
):
    existing_data = db.query(AccTaxInvoiceMaster).filter(
            AccTaxInvoiceMaster.work_order_master_id == work_order_master_id,
            AccTaxInvoiceMaster.is_deleted == 'no'
        ).first()
    if existing_data:
            return {'message': 'invoice is already exist',
                    'invoice_master_id': existing_data.id}
    # Fetch work order data
   
    # Fetch appointment data
    appointment_data = db.query(OffAppointmentVisitMasterView).filter(
        OffAppointmentVisitMasterView.appointment_master_id == appointment_id,
        OffAppointmentVisitMasterView.is_deleted == 'no'
    ).first()
    work_order_data =  db.query(WorkOrderMasterView).filter(
        WorkOrderMasterView.work_order_master_id == work_order_master_id,
        WorkOrderMasterView.appointment_master_id == appointment_id,
        WorkOrderMasterView.is_deleted == 'no'
    ).first()
    visit_master_id = work_order_data.visit_master_id
    consultant_id= appointment_data.consultant_id
    service_data =  db.query(OffAppointmentVisitDetails).filter(
        OffAppointmentVisitDetails.visit_master_id== visit_master_id,
        OffAppointmentVisitDetails.consultant_id== consultant_id,
        OffAppointmentVisitDetails.is_main_service == 'yes'
    ).all()
    # Generate voucher ID and invoice number
    voucher_id = generate_voucher_id(db)
    invoice_number = generate_book_number('INVOICE', db)

    # Create new invoice entry
    new_invoice = AccTaxInvoiceMaster(
        voucher_id=voucher_id,
        service_type='CONSULTATION',
        appointment_master_id=appointment_id,
        visit_master_id = visit_master_id,
        work_order_master_id=work_order_master_id,
        tax_invoice_number=invoice_number,
        tax_invoice_date=date.today(),
        # total_offer_amount = 0.0,
        # total_coupon_amount = 0.0,
        net_amount=0.0,  # To be updated later
        created_by=user_id,
    )
    db.add(new_invoice)
    db.flush()  # To get the new_invoice.id

    # Fetch service data
    # service_data = db.query(WorkOrderDetailsView).filter(
    #     WorkOrderDetailsView.work_order_master_id == work_order_master_id,
    #     WorkOrderDetailsView.service_required == 'yes',
    #     WorkOrderDetailsView.is_deleted == 'no'
    # )

    total_invoice_amount = 0.0

    # Process each service
    for services in service_data:
        total_service_charge = 0.0
        service_goods_master_id = services.service_id
       

        # Fetch consultation fee for the service
        consultation_fee_data = db.query(OffConsultantServiceDetails).filter(
            OffConsultantServiceDetails.consultant_id == appointment_data.consultant_id,
            OffConsultantServiceDetails.service_goods_master_id == service_goods_master_id
        ).first()
        
        if consultation_fee_data:
            total_service_charge += consultation_fee_data.consultation_fee
        else:
            return {
                'message' : 'Please set consultation fee '
            }
   

        # Create new invoice detail
        new_invoice_detail = AccTaxInvoiceDetails(
            tax_invoice_master_id=new_invoice.id,
            service_goods_master_id=service_goods_master_id,
            is_main_service = services.is_main_service,
            is_bundle_service='yes',
            bundle_service_id= None,
            service_charge=total_service_charge,
            taxable_amount = total_service_charge,
            total_amount = total_service_charge
        )
        db.add(new_invoice_detail)

        # Update total invoice amount
        total_invoice_amount += total_service_charge

    # Update total amount in the invoice master record
    new_invoice.net_amount = total_invoice_amount
    new_invoice.grand_total_amount = total_invoice_amount
    # Commit the transaction
    db.commit()

    # Return the generated invoice ID
    if new_invoice.id:
        return {
            'invoice_master_id': new_invoice.id,
            'work_order_master_id': work_order_master_id
        }

#---------------------------------------------------------------------------------------------------

def get_proforma_invoice_details(
    db: Session,
    work_order_master_id: int,
    proforma_invoice_master_id: int
):
    if work_order_master_id:
        if proforma_invoice_master_id:
            # Fetch the invoice master data
            invoice_master_data = db.query(AccProformaInvoiceMaster).filter(
                AccProformaInvoiceMaster.work_order_master_id == work_order_master_id,
                AccProformaInvoiceMaster.id == proforma_invoice_master_id,
                AccProformaInvoiceMaster.is_deleted == 'no'
            ).first()

            # Handle case when invoice master is not found
            if not invoice_master_data:
                raise HTTPException(status_code=404, detail="Invoice Master not found")

            # Fetch the work order master data
            work_order_master_data = db.query(WorkOrderMasterView).filter(
                WorkOrderMasterView.work_order_master_id == work_order_master_id
            ).first()

            # Handle case when work order master data is not found
            if not work_order_master_data:
                raise HTTPException(status_code=404, detail="Work Order Master not found")

            # Fetch the invoice details with the service name from joined table
            invoice_details_data = db.query(
                AccProformaInvoiceDetails,
                OffViewServiceGoodsMaster.service_goods_name
            ).join(
                OffViewServiceGoodsMaster,
                AccProformaInvoiceDetails.service_goods_master_id == OffViewServiceGoodsMaster.service_goods_master_id
            ).filter(
                AccProformaInvoiceDetails.proforma_invoice_master_id == invoice_master_data.id,
                AccProformaInvoiceDetails.is_deleted == 'no'
            ).all()

            # Build the list of invoice details
            invoice_details_list = []
            for detail, service_name in invoice_details_data:
                detail_dict = detail.__dict__.copy()  # Copy the details to modify
                detail_dict['service_goods_name'] = service_name
                invoice_details_list.append(AccProformaInvoiceDetailsSchema.model_validate(detail_dict))

            # Construct response schema
            invoice_response_data = AccProformaInvoiceResponceSchema(
                proforma_invoice_master=AccProformaInvoiceMasterSchema.model_validate(invoice_master_data.__dict__),
                work_order_master=OffViewWorkOrderMasterSchema.model_validate(work_order_master_data.__dict__),
                proforma_invoice_details=invoice_details_list
            )

            return invoice_response_data
        else:
            raise HTTPException(status_code=400, detail="Invoice Master ID is required")
    else:
        raise HTTPException(status_code=400, detail="Work Order Master ID is required")



def get_tax_invoice_details(
    db: Session,
    work_order_master_id: int,
    tax_invoice_master_id: int
):
    if work_order_master_id:
        if tax_invoice_master_id:
            # Fetch the invoice master data
            invoice_master_data = db.query(AccTaxInvoiceMaster).filter(
                AccTaxInvoiceMaster.work_order_master_id == work_order_master_id,
                AccTaxInvoiceMaster.id == tax_invoice_master_id,
                AccTaxInvoiceMaster.is_deleted == 'no'
            ).first()

            # Handle case when invoice master is not found
            if not invoice_master_data:
                raise HTTPException(status_code=404, detail="Invoice Master not found")

            # Fetch the work order master data
            work_order_master_data = db.query(WorkOrderMasterView).filter(
                WorkOrderMasterView.work_order_master_id == work_order_master_id
            ).first()

            # Handle case when work order master data is not found
            if not work_order_master_data:
                raise HTTPException(status_code=404, detail="Work Order Master not found")

            # Fetch the invoice details with the service name from joined table
            invoice_details_data = db.query(
                AccTaxInvoiceDetails,
                OffViewServiceGoodsMaster.service_goods_name
            ).join(
                OffViewServiceGoodsMaster,
                AccTaxInvoiceDetails.service_goods_master_id == OffViewServiceGoodsMaster.service_goods_master_id
            ).filter(
                AccTaxInvoiceDetails.tax_invoice_master_id == invoice_master_data.id,
                AccTaxInvoiceDetails.is_deleted == 'no'
            ).all()

            # Build the list of invoice details
            invoice_details_list = []
            for detail, service_name in invoice_details_data:
                detail_dict = detail.__dict__.copy()  # Copy the details to modify
                detail_dict['service_goods_name'] = service_name
                invoice_details_list.append(AccTaxInvoiceDetailsSchema.model_validate(detail_dict))

            # Construct response schema
            invoice_response_data = AccTaxInvoiceResponceSchema(
                tax_invoice_master=AccTaxInvoiceMasterSchema.model_validate(invoice_master_data.__dict__),
                work_order_master=OffViewWorkOrderMasterSchema.model_validate(work_order_master_data.__dict__),
                tax_invoice_details=invoice_details_list
            )

            return invoice_response_data
        else:
            raise HTTPException(status_code=400, detail="Invoice Master ID is required")
    else:
        raise HTTPException(status_code=400, detail="Work Order Master ID is required")


#---------------------------------------------------------------------------------------------------

def save_tax_invoice(
        db: Session,
        work_order_master_id: int,
        request: AccTaxInvoiceShema,
        user_id : int
):                    
    
        existing_record = db.query(AccTaxInvoiceMaster).filter(
            AccTaxInvoiceMaster.work_order_master_id == work_order_master_id,
            AccTaxInvoiceMaster.is_deleted == 'no'
        ).first()

        try:
            if existing_record:
                    for key, value in request.tax_invoice_master.model_dump(exclude_unset=True).items():
                            setattr(existing_record, key, value)
                    existing_record.modified_by = user_id
                    existing_record.modified_on = datetime.utcnow()

            for detail in request.tax_invoice_details:
                existing_detail = db.query(AccTaxInvoiceDetails).filter(
                    AccTaxInvoiceDetails.id == detail.id,
                    AccTaxInvoiceDetails.tax_invoice_master_id == existing_record.id,
                    AccTaxInvoiceDetails.is_deleted == 'no'
                ).first()

                if existing_detail:
                    # Update existing details
                    for key, value in detail.model_dump(exclude_unset=True).items():
                        setattr(existing_detail, key, value)
            db.commit()
            return {'message' : 'success'}
        except SQLAlchemyError as e:
            db.rollback()  # Rollback the transaction in case of error
            raise HTTPException(status_code=500, detail=str(e))  # Raise HTTPException with error message
 