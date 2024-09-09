from datetime import date, datetime, timedelta
from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session

from caerp_db.common.models import DistrictDB, StateDB
from caerp_db.office.models import OffServiceTaskMaster
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerExistingRegistrationDetails, CustomerGSTCasualTaxablePersonDetails, CustomerGSTCompositionOptedPersonDetails, CustomerGSTOtherDetails, CustomerMaster,GstReasonToObtainRegistration,GstTypeOfRegistration
from caerp_schema.services.gst_schema import BusinessDetailsSchema, CustomerRequestSchema



#-------------------------business details--------------------------------------------------------------

def save_business_details(
    db: Session,
    business_details_data: BusinessDetailsSchema,
    task_id: int,  # 0 for insert, non-zero for update
    user_id: int,
    id: int  # 0 for insert (new), non-zero for update
):
    try:
        if id == 0:
            # Insert new CustomerMaster
            customer_master = CustomerMaster(
                **business_details_data.model_dump(exclude_unset=True), 
                created_by=user_id,  # Set created_by field
                created_on=datetime.now()  # Set created_on to current datetime
            )
            db.add(customer_master)
            db.flush()  # Ensure we have the customer_id for further use
        else:
            # Update existing CustomerMaster
            customer_master = db.query(CustomerMaster).filter(CustomerMaster.customer_id == id).first()
            if not customer_master:
                return {"detail": "Customer master not found"}

            # Update fields using the provided data
            for key, value in business_details_data.model_dump(exclude_unset=True).items():
                setattr(customer_master, key, value)
            customer_master.modified_by = user_id  # Set modified_by field
            customer_master.modified_on = datetime.now()  # Set modified_on field

        db.flush()  # Ensure the customer_id is available for task update

        # Update OffServiceTaskMaster with the new customer_id if task_id is provided
        if task_id != 0:
            service_task_master = db.query(OffServiceTaskMaster).filter(OffServiceTaskMaster.id == task_id).first()
            if not service_task_master:
                return {"detail": "Service task not found"}

            # Update the task's customer_id with the current customer_id
            service_task_master.customer_id = customer_master.customer_id
            db.add(service_task_master)

        db.commit()  # Commit transaction

        # Return the customer_id and a success message
        return {"customer_id": customer_master.customer_id, "message": " saved successfully"}

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=500, detail=str(e))






#-------CUSTOMER / BUSINESS DETAILS-------------------------------------------------------------------

def handle_customer_details(customer_id: int, customer_data: CustomerRequestSchema, db: Session):
    try:
        # Handle Additional Trade Names
        for trade_name in customer_data.additional_trade_name:
            if trade_name.id == 0:
                new_trade_name = CustomerAdditionalTradeName(
                    customer_id=customer_id,
                    additional_trade_name=trade_name.trade_name
                )
                db.add(new_trade_name)
            else:
                existing_trade_name = db.query(CustomerAdditionalTradeName).filter_by(id=trade_name.id).first()
                if existing_trade_name:
                    existing_trade_name.additional_trade_name = trade_name.trade_name

        # Handle Casual Taxable Person Details
        if customer_data.casual_taxable_person.id == 0:
            casual_taxable_person = CustomerGSTCasualTaxablePersonDetails(
                customer_id=customer_id,
                is_applying_as_casual_taxable_person=customer_data.casual_taxable_person.is_applying_as_casual_taxable_person,
                estimated_igst_turnover=customer_data.casual_taxable_person.estimated_igst_turnover,
                estimated_net_igst_liability=customer_data.casual_taxable_person.estimated_net_igst_liability,
                estimated_cgst_turnover=customer_data.casual_taxable_person.estimated_cgst_turnover,
                estimated_net_cgst_liability=customer_data.casual_taxable_person.estimated_net_cgst_liability,
                estimated_sgst_turnover=customer_data.casual_taxable_person.estimated_sgst_turnover,
                estimated_net_sgst_liability=customer_data.casual_taxable_person.estimated_net_sgst_liability,
                estimated_cess_turnover=customer_data.casual_taxable_person.estimated_cess_turnover,
                estimated_net_cess_liability=customer_data.casual_taxable_person.estimated_net_cess_liability
            )
            db.add(casual_taxable_person)
        else:
            existing_casual_taxable_person = db.query(CustomerGSTCasualTaxablePersonDetails).filter_by(id=customer_data.casual_taxable_person.id).first()
            if existing_casual_taxable_person:
                existing_casual_taxable_person.is_applying_as_casual_taxable_person = customer_data.casual_taxable_person.is_applying_as_casual_taxable_person
                existing_casual_taxable_person.estimated_igst_turnover = customer_data.casual_taxable_person.estimated_igst_turnover
                existing_casual_taxable_person.estimated_net_igst_liability = customer_data.casual_taxable_person.estimated_net_igst_liability
                # Update other fields similarly

        # Handle Composition Option
        if customer_data.option_for_composition.id == 0:
            composition_option = CustomerGSTCompositionOptedPersonDetails(
                customer_id=customer_id,
                is_applying_as_composition_taxable_person=customer_data.option_for_composition.is_applying_as_composition_taxable_person,
                option_1=customer_data.option_for_composition.option_1,
                option_2=customer_data.option_for_composition.option_2,
                option_3=customer_data.option_for_composition.option_3
            )
            db.add(composition_option)
        else:
            existing_composition_option = db.query(CustomerGSTCompositionOptedPersonDetails).filter_by(id=customer_data.option_for_composition.id).first()
            if existing_composition_option:
                existing_composition_option.is_applying_as_composition_taxable_person = customer_data.option_for_composition.is_applying_as_composition_taxable_person
                existing_composition_option.option_1 = customer_data.option_for_composition.option_1
                existing_composition_option.option_2 = customer_data.option_for_composition.option_2
                existing_composition_option.option_3 = customer_data.option_for_composition.option_3

        # Handle Other GST Details
        if customer_data.reason_to_obtain_registration.id == 0:
            gst_other_details = CustomerGSTOtherDetails(
                customer_id=customer_id,
                reason_to_obtain_gst_registration_id=customer_data.reason_to_obtain_registration.reason_to_obtain_gst_registration_id,
                commencement_of_business_date=customer_data.reason_to_obtain_registration.commencement_of_business_date,
                liability_to_register_arises_date=customer_data.reason_to_obtain_registration.liability_to_register_arises_date
            )
            db.add(gst_other_details)
        else:
            existing_gst_other_details = db.query(CustomerGSTOtherDetails).filter_by(id=customer_data.reason_to_obtain_registration.id).first()
            if existing_gst_other_details:
                existing_gst_other_details.reason_to_obtain_gst_registration_id = customer_data.reason_to_obtain_registration.reason_to_obtain_gst_registration_id
                existing_gst_other_details.commencement_of_business_date = customer_data.reason_to_obtain_registration.commencement_of_business_date

        # Handle Existing Registrations
        for registration in customer_data.existing_registrations:
            if registration.id == 0:
                new_registration = CustomerExistingRegistrationDetails(
                    customer_id=customer_id,
                    registration_type_id=registration.registration_type_id,
                    registration_number=registration.registration_number,
                    registration_date=registration.registration_date
                )
                db.add(new_registration)
            else:
                existing_registration = db.query(CustomerExistingRegistrationDetails).filter_by(id=registration.id).first()
                if existing_registration:
                    existing_registration.registration_type_id = registration.registration_type_id
                    existing_registration.registration_number = registration.registration_number
                    existing_registration.registration_date = registration.registration_date

        # Handle Authorization
        if customer_id == 0:  # New Customer Authorization
            new_authorization = CustomerMaster(
                customer_id=customer_id,
                constitution_id=customer_data.authorization.constitution_id,
                has_authorized_signatory=customer_data.authorization.has_authorized_signatory,
                has_authorized_representative=customer_data.authorization.has_authorized_representative,
                is_mother_customer=customer_data.authorization.is_mother_customer
            )
            db.add(new_authorization)
        else:
            existing_authorization = db.query(CustomerMaster).filter_by(customer_id=customer_id).first()
            if existing_authorization:
                existing_authorization.constitution_id = customer_data.authorization.constitution_id
                existing_authorization.has_authorized_signatory = customer_data.authorization.has_authorized_signatory
                existing_authorization.has_authorized_representative = customer_data.authorization.has_authorized_representative
                existing_authorization.is_mother_customer = customer_data.authorization.is_mother_customer

        # Commit transaction
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


#-get''
def get_customer_details(db: Session, customer_id: int):
    try:
        # Query the main customer record
        customer = db.query(CustomerMaster).filter_by(customer_id=customer_id).first()
        
        if not customer:
            return {"detail":"customer not found"}

        # Query related details
        additional_trade_names = db.query(CustomerAdditionalTradeName).filter_by(customer_id=customer_id).all()
        casual_taxable_person = db.query(CustomerGSTCasualTaxablePersonDetails).filter_by(customer_id=customer_id).first()
        composition_option = db.query(CustomerGSTCompositionOptedPersonDetails).filter_by(customer_id=customer_id).first()
        gst_other_details = db.query(CustomerGSTOtherDetails).filter_by(customer_id=customer_id).first()
        existing_registrations = db.query(CustomerExistingRegistrationDetails).filter_by(customer_id=customer_id).all()

        # Assemble response data
        response = {
            "customer_business_details": {
                "pan_number": customer.pan_number,
                "pan_creation_date": customer.pan_creation_date,
                "state_id": customer.state_id,
                "state_name": db.query(StateDB.state_name).filter_by(id=customer.state_id).scalar() if customer.state_id else None,
                "district_id": customer.district_id,
                "district_name": db.query(DistrictDB.district_name).filter_by(id=customer.district_id).scalar() if customer.district_id else None,
                "legal_name": customer.legal_name,
                "email_address": customer.email_address,
                "mobile_number": customer.mobile_number,
                "tan_number": customer.tan_number,
                "passport_number": customer.passport_number,
                "tin_number": customer.tin_number,
                "authorised_signatory_name_as_in_pan": customer.authorized_signatory_name_as_in_pan,
                "authorised_signatory_pan_number": customer.authorized_signatory_pan_number,
                "constitution_id": customer.constitution_id,
                "has_authorized_signatory": customer.has_authorized_signatory,
                "has_authorized_representative": customer.has_authorized_representative,
                "is_mother_customer": customer.is_mother_customer
            },
            "customer_other_details": {
                "additional_trade_name": [
                    {
                        "id": trade.id,
                        "trade_name": trade.additional_trade_name
                    }
                    for trade in additional_trade_names
                ],
                "casual_taxable_person": {
                    "id": casual_taxable_person.id if casual_taxable_person else None,
                    "is_applying_as_casual_taxable_person": casual_taxable_person.is_applying_as_casual_taxable_person if casual_taxable_person else None,
                    "estimated_igst_turnover": casual_taxable_person.estimated_igst_turnover if casual_taxable_person else None,
                    "estimated_net_igst_liability": casual_taxable_person.estimated_net_igst_liability if casual_taxable_person else None,
                    "estimated_cgst_turnover": casual_taxable_person.estimated_cgst_turnover if casual_taxable_person else None,
                    "estimated_net_cgst_liability": casual_taxable_person.estimated_net_cgst_liability if casual_taxable_person else None,
                    "estimated_sgst_turnover": casual_taxable_person.estimated_sgst_turnover if casual_taxable_person else None,
                    "estimated_net_sgst_liability": casual_taxable_person.estimated_net_sgst_liability if casual_taxable_person else None,
                    "estimated_cess_turnover": casual_taxable_person.estimated_cess_turnover if casual_taxable_person else None,
                    "estimated_net_cess_liability": casual_taxable_person.estimated_net_cess_liability if casual_taxable_person else None
                },
                "option_for_composition": {
                    "id": composition_option.id if composition_option else None,
                    "is_applying_as_composition_taxable_person": composition_option.is_applying_as_composition_taxable_person if composition_option else None,
                    "option_1": composition_option.option_1 if composition_option else None,
                    "option_2": composition_option.option_2 if composition_option else None,
                    "option_3": composition_option.option_3 if composition_option else None
                },
                "reason_to_obtain_registration": {
                    "id": gst_other_details.id if gst_other_details else None,
                    "reason_to_obtain_gst_registration_id": gst_other_details.reason_to_obtain_gst_registration_id if gst_other_details else None,
                     "reason_to_obtain_gst_registration_name": db.query(GstReasonToObtainRegistration.reason).filter_by(id=gst_other_details.reason_to_obtain_gst_registration_id).scalar() if gst_other_details.reason_to_obtain_gst_registration_id else None,
                    "commencement_of_business_date": gst_other_details.commencement_of_business_date if gst_other_details else None,
                    "liability_to_register_arises_date": gst_other_details.liability_to_register_arises_date if gst_other_details else None
                },
                "existing_registrations": [
                    {
                        "registration_type_id": reg.registration_type_id,
                        "registration_type": db.query(GstTypeOfRegistration.type_of_registration).filter_by(id=reg.registration_type_id).scalar() if reg.registration_type_id else None,
                        "registration_number": reg.registration_number,
                        "registration_date": reg.registration_date
                    }
                    for reg in existing_registrations
                ]
            }
        }
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
