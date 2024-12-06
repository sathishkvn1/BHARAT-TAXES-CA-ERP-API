from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from fastapi import HTTPException, UploadFile, logger,status,Depends
from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from caerp_constants.caerp_constants import AmendmentAction
from caerp_db.common.models import AppConstitutionStakeholders, AppDesignation, AppViewVillages, BusinessActivity, BusinessActivityMaster, BusinessActivityType, CityDB, CountryDB, DistrictDB, Gender, MaritalStatus, PostOfficeView, StateDB, TalukDB
from caerp_db.office.models import AppBusinessConstitution, AppHsnSacClasses, AppHsnSacMaster, OffNatureOfPossession, OffServiceTaskMaster
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerAmendmentHistory, CustomerBusinessPlace, CustomerBusinessPlaceActivity, CustomerBusinessPlaceActivityType, CustomerBusinessPlaceCoreActivity, CustomerExistingRegistrationDetails, CustomerGSTCasualTaxablePersonDetails, CustomerGSTCompositionOptedPersonDetails, CustomerGSTOtherDetails, CustomerGoodsCommoditiesSupplyDetails, CustomerGstStateSpecificInformation, CustomerMaster, CustomerStakeHolder, GstNatureOfPossessionOfPremises, GstOtherAuthorizedRepresentativeResignation,GstReasonToObtainRegistration,GstTypeOfRegistration, GstViewRange, StakeHolderAddress, StakeHolderContactDetails, StakeHolderMaster
from caerp_functions.generate_book_number import generate_book_number
from caerp_schema.services.gst_schema import  AdditionalTradeNameAmendment, AmendmentDetailsSchema, AmmendStakeHolderMasterSchema, BusinessData, BusinessDetailsSchema, BusinessPlace, CombinedSchema, CustomerBusinessPlaceActivitySchemaForGet, CustomerBusinessPlaceAmendmentSchema, CustomerBusinessPlaceFullAmendmentSchema, CustomerBusinessPlaceSchemaForGet, CustomerDuplicateSchema, CustomerGoodsCommoditiesSupplyDetailsSchema, CustomerGstStateSpecificInformationSchema, CustomerRequestSchema, RangeDetailsSchema, StakeHolderMasterSchema, TradeNameSchema



#-------------------------business details
def save_business_details(
    db: Session,
    business_details_data: BusinessDetailsSchema,
    task_id: Optional[int],  # task_id is now optional
    user_id: int,
    id: int,  # 0 for insert (new), non-zero for update
    is_mother_customer: Optional[str] = "no"  # Optional parameter, default is 'no'
):
    financial_year_id = 1
    customer_id = 1
    try:
        is_mother_customer_value = "yes" if is_mother_customer.lower() == "yes" else "no"
        if id == 0:
            # Insert new CustomerMaster
            customer_number = generate_book_number('CUSTOMER', financial_year_id, customer_id, db)
            customer_master = CustomerMaster(
                **business_details_data.model_dump(exclude_unset=True),
                customer_number=customer_number,   
                service_task_id=task_id,
                registration_status="CREATED",
                created_by=user_id,  
                created_on=datetime.now(),  
                effective_from_date=datetime.now(), 
                effective_to_date=None,
                is_mother_customer=is_mother_customer_value
            )
            db.add(customer_master)
            db.flush()  # Generate the `id` for the new customer_master

            # Set customer_id equal to auto-generated id
            customer_master.customer_id = customer_master.id
            db.add(customer_master)  # Re-add the customer to update customer_id
            db.flush()

        else:
            # Update existing CustomerMaster
            customer_master = db.query(CustomerMaster).filter(CustomerMaster.customer_id == id).first()
            if not customer_master:
                return {"detail": "Customer master not found"}

            # Update fields using the provided data
            for key, value in business_details_data.model_dump(exclude_unset=True).items():
                setattr(customer_master, key, value)

            customer_master.modified_by = user_id  
            customer_master.modified_on = datetime.now()  
            customer_master.is_mother_customer = is_mother_customer_value
            # Update `is_mother_customer` if provided
            

        db.flush()

        # Update OffServiceTaskMaster with the new customer_id if task_id is provided
        if task_id:
            service_task_master = db.query(OffServiceTaskMaster).filter(OffServiceTaskMaster.id == task_id).first()
            if not service_task_master:
                return {"detail": "Service task not found"}

            # Update the task's customer_id
            service_task_master.customer_id = customer_master.customer_id
            db.add(service_task_master)

        db.commit()  # Commit transaction

        return {"customer_id": customer_master.customer_id,"customer_number": customer_master.customer_number, "message": "Customer details saved successfully"}

    except Exception as e:
        db.rollback()  # Rollback transaction in case of error
        raise HTTPException(status_code=500, detail=str(e))


#-------CUSTOMER / BUSINESS DETAILS
def save_customer_details(customer_id: int, 
                          service_task_id: Optional[int],
                          customer_data: CustomerRequestSchema, 
                          user_id: int, 
                          db: Session):
    try:
        for additional_trade_name in customer_data.additional_trade_name:
            if additional_trade_name.id == 0:
                # Create a new trade name record
                
                new_trade_name = CustomerAdditionalTradeName(
                    customer_id=customer_id,
                    additional_trade_name=additional_trade_name.additional_trade_name,
                    service_task_id=service_task_id,
                    effective_from_date=datetime.now(),
                    effective_to_date=None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                
                db.add(new_trade_name)
                db.flush()  # Flush to get the generated ID without committing

                # Get the generated ID for the newly inserted record
                new_record_id = new_trade_name.id
                
                # If the trade name is an amendment, update the amended_parent_id
            
                new_trade_name.amended_parent_id = new_record_id  
            else:
                trade_entries = {entry.id: entry for entry in db.query(CustomerAdditionalTradeName)
                         .filter_by(customer_id=customer_id).all()}

                incoming_trade_ids = {trade_name.id for trade_name in customer_data.additional_trade_name if trade_name.id != 0}

                for entry_id, existing_trade in trade_entries.items():
                    if entry_id not in incoming_trade_ids:
                        existing_trade.is_deleted = "yes"
                        existing_trade.deleted_by = user_id
                        existing_trade.deleted_on = datetime.now()
                        existing_trade.modified_by = user_id
                        existing_trade.modified_on = datetime.now()

                for additional_trade_name in customer_data.additional_trade_name:
                    trade_data = additional_trade_name.model_dump(exclude_unset=True)
                    entry_id = trade_data.get("id")

                    if entry_id in trade_entries:
                        existing_trade = trade_entries[entry_id]
                        for key, value in trade_data.items():
                            setattr(existing_trade, key, value)
                        existing_trade.is_deleted = "no"
                        existing_trade.deleted_by = None
                        existing_trade.deleted_on = None
                        existing_trade.modified_by = user_id
                        existing_trade.modified_on = datetime.now()
        # Handle Casual Taxable Person Details
        if customer_data.casual_taxable_person.is_applying_as_casual_taxable_person == "no":
            # When is_applying_as_casual_taxable_person is "no", set other fields to None
            casual_taxable_person_data = {
                "id": customer_data.casual_taxable_person.id,
                "is_applying_as_casual_taxable_person": customer_data.casual_taxable_person.is_applying_as_casual_taxable_person,
                "gst_registration_required_from_date": None,
                "gst_registration_required_to_date": None,
                "estimated_igst_turnover": None,
                "estimated_net_igst_liability": None,
                "estimated_cgst_turnover": None,
                "estimated_net_cgst_liability": None,
                "estimated_sgst_turnover": None,
                "estimated_net_sgst_liability": None,
                "estimated_cess_turnover": None,
                "estimated_net_cess_liability": None
            }
        else:
            # Use the actual values when the person is applying as a casual taxable person
            casual_taxable_person_data = customer_data.casual_taxable_person.model_dump(exclude_unset=True)

        if customer_data.casual_taxable_person.id == 0:
            casual_taxable_person = CustomerGSTCasualTaxablePersonDetails(
                customer_id=customer_id,
                **casual_taxable_person_data,
                service_task_id=service_task_id,
                effective_from_date=datetime.now(),
                effective_to_date=None,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(casual_taxable_person)
        else:
            existing_casual_taxable_person = db.query(CustomerGSTCasualTaxablePersonDetails).filter_by(id=customer_data.casual_taxable_person.id).first()
            if existing_casual_taxable_person:
                for key, value in casual_taxable_person_data.items():
                    setattr(existing_casual_taxable_person, key, value)
                existing_casual_taxable_person.effective_from_date = datetime.now()
                existing_casual_taxable_person.effective_to_date = None
                existing_casual_taxable_person.modified_by = user_id
                existing_casual_taxable_person.modified_on = datetime.now()

        # Handle Composition Option
        if customer_data.option_for_composition.is_applying_as_composition_taxable_person == "no":
            # When is_applying_as_composition_taxable_person is "no", set other fields to None
            composition_option_data = {
                "id": customer_data.option_for_composition.id,
                "is_applying_as_composition_taxable_person": customer_data.option_for_composition.is_applying_as_composition_taxable_person,
                "option_1": "no",
                "option_2": "no",
                "option_3": "no"
            }
        else:
            # Use the actual values when applying as a composition taxable person
            composition_option_data = customer_data.option_for_composition.model_dump(exclude_unset=True)

        if customer_data.option_for_composition.id == 0:
            composition_option = CustomerGSTCompositionOptedPersonDetails(
                customer_id=customer_id,
                **composition_option_data,
                service_task_id=service_task_id,
                effective_from_date=datetime.now(),
                effective_to_date=None,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(composition_option)
        else:
            existing_composition_option = db.query(CustomerGSTCompositionOptedPersonDetails).filter_by(id=customer_data.option_for_composition.id).first()
            if existing_composition_option:
                for key, value in composition_option_data.items():
                    setattr(existing_composition_option, key, value)
                existing_composition_option.effective_from_date = datetime.now()
                existing_composition_option.effective_to_date = None
                existing_composition_option.modified_by = user_id
                existing_composition_option.modified_on = datetime.now()

        # Handle Other GST Details
        if customer_data.reason_to_obtain_registration.id == 0:
            gst_other_details = CustomerGSTOtherDetails(
                customer_id=customer_id,
                **customer_data.reason_to_obtain_registration.model_dump(exclude_unset=True),
                service_task_id=service_task_id,
                effective_from_date=datetime.now(),
                effective_to_date=None,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(gst_other_details)
        else:
            existing_gst_other_details = db.query(CustomerGSTOtherDetails).filter_by(id=customer_data.reason_to_obtain_registration.id).first()
            if existing_gst_other_details:
                for key, value in customer_data.reason_to_obtain_registration.model_dump(exclude_unset=True).items():
                    setattr(existing_gst_other_details, key, value)
                existing_gst_other_details.effective_from_date = datetime.now()
                existing_gst_other_details.effective_to_date = None
                existing_gst_other_details.modified_by = user_id
                existing_gst_other_details.modified_on = datetime.now()

        # Handle Existing Registrations
        for registration in customer_data.existing_registrations:
            if registration.id == 0:
                new_registration = CustomerExistingRegistrationDetails(
                    customer_id=customer_id,
                    **registration.model_dump(exclude_unset=True),
                    service_task_id=service_task_id,
                    effective_from_date=datetime.now(),
                    effective_to_date=None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                db.add(new_registration)
            else:
                registration_entries = {entry.id: entry for entry in db.query(CustomerExistingRegistrationDetails)
                                .filter_by(customer_id=customer_id).all()}

                incoming_registration_ids = {registration.id for registration in customer_data.existing_registrations if registration.id != 0}

                for entry_id, existing_registration in registration_entries.items():
                    if entry_id not in incoming_registration_ids:
                        existing_registration.is_deleted = "yes"
                        existing_registration.deleted_by = user_id
                        existing_registration.deleted_on = datetime.now()
                        existing_registration.modified_by = user_id
                        existing_registration.modified_on = datetime.now()

                for registration in customer_data.existing_registrations:
                    registration_data = registration.model_dump(exclude_unset=True)
                    entry_id = registration_data.get("id")

                    if entry_id in registration_entries:
                        existing_registration = registration_entries[entry_id]
                        for key, value in registration_data.items():
                            setattr(existing_registration, key, value)
                        existing_registration.is_deleted = "no"
                        existing_registration.deleted_by = None
                        existing_registration.deleted_on = None
                        existing_registration.modified_by = user_id
                        existing_registration.modified_on = datetime.now()
        # Handle Authorization
        if customer_id >= 0:
            existing_authorization = db.query(CustomerMaster).filter_by(customer_id=customer_id).first()

            if existing_authorization:
                for key, value in customer_data.authorization.model_dump(exclude_unset=True).items():
                    setattr(existing_authorization, key, value)
                existing_authorization.effective_from_date = datetime.now()
                existing_authorization.effective_to_date = None
                existing_authorization.modified_by = user_id
                existing_authorization.modified_on = datetime.now()
            else:
                new_authorization = CustomerMaster(
                    customer_id=customer_id,
                    **customer_data.authorization.model_dump(exclude_unset=True),
                    effective_from_date=datetime.now(),
                    effective_to_date=None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                db.add(new_authorization)

        # Commit transaction
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#-get''
def get_customer_details(db: Session, 
                         customer_id: int, 
                         service_task_id: Optional[int], 
                         user_id: int):
    try:
        # Query the main customer record with customer_id and service_task_id
        customer = (
            db.query(CustomerMaster)
            .filter(CustomerMaster.customer_id == customer_id)
            .filter(CustomerMaster.service_task_id == service_task_id)
            .first()
        )
        
        if not customer:
            return []

        # Query related details with customer_id and service_task_id
        additional_trade_names = (
            db.query(CustomerAdditionalTradeName)
            .filter(CustomerAdditionalTradeName.customer_id == customer_id)
            .filter(CustomerAdditionalTradeName.service_task_id == service_task_id)
            .filter(CustomerAdditionalTradeName.is_deleted == "no")
            .filter(
                CustomerAdditionalTradeName.effective_from_date <= datetime.now(),
                CustomerAdditionalTradeName.effective_to_date.is_(None),
            )
            .all()
        )
        
        casual_taxable_person = (
            db.query(CustomerGSTCasualTaxablePersonDetails)
            .filter(CustomerGSTCasualTaxablePersonDetails.customer_id == customer_id)
            .filter(CustomerGSTCasualTaxablePersonDetails.service_task_id == service_task_id)
            .filter(
                CustomerGSTCasualTaxablePersonDetails.effective_from_date <= datetime.now(),
                CustomerGSTCasualTaxablePersonDetails.effective_to_date.is_(None),
            )
            .first()
        )
        
        composition_option = (
            db.query(CustomerGSTCompositionOptedPersonDetails)
            .filter(CustomerGSTCompositionOptedPersonDetails.customer_id == customer_id)
            .filter(CustomerGSTCompositionOptedPersonDetails.service_task_id == service_task_id)
            .filter(
                CustomerGSTCompositionOptedPersonDetails.effective_from_date <= datetime.now(),
                CustomerGSTCompositionOptedPersonDetails.effective_to_date.is_(None),
            )
            .first()
        )
        
        gst_other_details = (
            db.query(CustomerGSTOtherDetails)
            .filter(CustomerGSTOtherDetails.customer_id == customer_id)
            .filter(CustomerGSTOtherDetails.service_task_id == service_task_id)
            .filter(
                CustomerGSTOtherDetails.effective_from_date <= datetime.now(),
                CustomerGSTOtherDetails.effective_to_date.is_(None),
            )
            .first()
        )
        
        existing_registrations = (
            db.query(CustomerExistingRegistrationDetails)
            .filter(CustomerExistingRegistrationDetails.customer_id == customer_id)
            .filter(CustomerExistingRegistrationDetails.service_task_id == service_task_id)
            .filter(CustomerExistingRegistrationDetails.is_deleted == "no")
            .filter(
                CustomerExistingRegistrationDetails.effective_from_date <= datetime.now(),
                CustomerExistingRegistrationDetails.effective_to_date.is_(None),
            )
            .all()
        )

        # Assemble response data
        response = {
            "customer_business_details": {
                "id": customer.customer_id,
                "customer_number": customer.customer_number,
                "pan_number": customer.pan_number,
                "pan_creation_date": customer.pan_creation_date,
                "state_id": customer.state_id,
                "state_code": db.query(StateDB.state_code).filter_by(id=customer.state_id).scalar() if customer.state_id else None,
                "state_name": db.query(StateDB.state_name).filter_by(id=customer.state_id).scalar() if customer.state_id else None,
                "district_id": customer.district_id,
                "district_name": db.query(DistrictDB.district_name).filter_by(id=customer.district_id).scalar() if customer.district_id else None,
                "district_code": db.query(DistrictDB.gst_district_code).filter_by(id=customer.district_id).scalar() if customer.district_id else None,
                "legal_name": customer.legal_name,
                "trade_name": customer.customer_name,
                "email_address": customer.email_address,
                "mobile_number": customer.mobile_number,
                "tan_number": customer.tan_number,
                "passport_number": customer.passport_number,
                "tin_number": customer.tin_number,
                "authorized_signatory_name_as_in_pan": customer.authorized_signatory_name_as_in_pan,
                "authorized_signatory_pan_number": customer.authorized_signatory_pan_number,
                "constitution_id": customer.constitution_id,
                "constitution_name": db.query(AppBusinessConstitution.business_constitution_name).filter_by(id=customer.constitution_id).scalar() if customer.constitution_id else None,
                "business_constitution_code": db.query(AppBusinessConstitution.business_constitution_code).filter_by(id=customer.constitution_id).scalar() if customer.constitution_id else None,
                "has_authorized_signatory": customer.has_authorized_signatory,
                "has_authorized_representative": customer.has_authorized_representative,
                "is_mother_customer": customer.is_mother_customer,
                "registration_status":customer.registration_status
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
                    "gst_registration_required_from_date": casual_taxable_person.gst_registration_required_from_date if casual_taxable_person else None,
                    "gst_registration_required_to_date": casual_taxable_person.gst_registration_required_to_date if casual_taxable_person else None,
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
                    "reason_to_obtain_gst_registration_id": gst_other_details.reason_to_obtain_gst_registration_id if gst_other_details and gst_other_details.reason_to_obtain_gst_registration_id is not None else None,
                    "reason_to_obtain_gst_registration_name": db.query(GstReasonToObtainRegistration.reason)
                                                .filter_by(id=gst_other_details.reason_to_obtain_gst_registration_id)
                                                .scalar() if gst_other_details and gst_other_details.reason_to_obtain_gst_registration_id else None,
                    "reason_to_obtain_gst_registration_code": db.query(GstReasonToObtainRegistration.reason_code)
                                                .filter_by(id=gst_other_details.reason_to_obtain_gst_registration_id)
                                                .scalar() if gst_other_details and gst_other_details.reason_to_obtain_gst_registration_id else None,
                    "commencement_of_business_date": gst_other_details.commencement_of_business_date if gst_other_details else None,
                    "liability_to_register_arises_date": gst_other_details.liability_to_register_arises_date if gst_other_details else None
                },
                "existing_registrations": [
                    {
                        "id": reg.id,
                        "registration_type_id": reg.registration_type_id if reg.registration_type_id is not None else None, 
                        "registration_type": db.query(GstTypeOfRegistration.type_of_registration).filter_by(id=reg.registration_type_id).scalar() if reg.registration_type_id else None,
                        "registration_type_code": db.query(GstTypeOfRegistration.type_of_registration_code).filter_by(id=reg.registration_type_id).scalar() if reg.registration_type_id else None,
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

#------Save stakeholder

def save_stakeholder_details(
    request: StakeHolderMasterSchema,
    user_id: int,
    db: Session,
    customer_id: int,
    service_task_id: int,
    stake_holder_type: Optional[str] = None,
    is_authorized_signatory: Optional[str] = None,
    is_primary_authorized_signatory: Optional[str] = None,
    authorized_representative_type: Optional[str] = None
):
    try:
        # Handle StakeHolderMaster
        personal_info = request.personal_information
        identity_info = request.identity_information

        if personal_info.id == 0:
            # Create new StakeHolderMaster
            stake_holder_master = StakeHolderMaster(
                first_name=personal_info.first_name,
                middle_name=personal_info.middle_name,
                last_name=personal_info.last_name,
                fathers_first_name=personal_info.fathers_first_name,
                fathers_middle_name=personal_info.fathers_middle_name,
                fathers_last_name=personal_info.fathers_last_name,
                marital_status_id=personal_info.marital_status_id,
                date_of_birth=personal_info.date_of_birth,
                gender_id=personal_info.gender_id,
                din_number=identity_info.din_number,
                is_citizen_of_india=identity_info.is_citizen_of_india,
                pan_number=identity_info.pan_number,
                passport_number=identity_info.passport_number,
                aadhaar_number=identity_info.aadhaar_number,
                gst_enrollment_number=identity_info.gst_enrollment_number,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(stake_holder_master)
        else:
            # Update existing StakeHolderMaster
            stake_holder_master = db.query(StakeHolderMaster).filter_by(id=personal_info.id).first()
            if stake_holder_master:
                stake_holder_master.first_name = personal_info.first_name
                stake_holder_master.middle_name = personal_info.middle_name
                stake_holder_master.last_name = personal_info.last_name
                stake_holder_master.fathers_first_name = personal_info.fathers_first_name
                stake_holder_master.fathers_middle_name = personal_info.fathers_middle_name
                stake_holder_master.fathers_last_name = personal_info.fathers_last_name
                stake_holder_master.marital_status_id = personal_info.marital_status_id
                stake_holder_master.date_of_birth = personal_info.date_of_birth
                stake_holder_master.gender_id = personal_info.gender_id
                stake_holder_master.din_number = identity_info.din_number
                stake_holder_master.is_citizen_of_india = identity_info.is_citizen_of_india
                stake_holder_master.pan_number = identity_info.pan_number
                stake_holder_master.passport_number = identity_info.passport_number
                stake_holder_master.aadhaar_number = identity_info.aadhaar_number
                stake_holder_master.gst_enrollment_number = identity_info.gst_enrollment_number
                stake_holder_master.modified_by = user_id
                stake_holder_master.modified_on = datetime.now()
            else:
                return {"detail": "StakeHolderMaster not found"}

        db.flush()  # Flush to get stake_holder_master.id

        # Handle StakeHolderContactDetails
        
        for contact_details in request.contact_details:
            existing_contact = db.query(StakeHolderContactDetails).filter(
                StakeHolderContactDetails.stake_holder_id == stake_holder_master.id,
                StakeHolderContactDetails.effective_to_date == None  # Only active entries
            ).first()

            if existing_contact:
                has_changes = any(
                    getattr(existing_contact, field, None) != getattr(contact_details, field, None)
                    for field in vars(contact_details)
                    if field != "id" and hasattr(existing_contact, field)
                )
                contact_details_id = existing_contact.id
                if has_changes:
                    existing_contact.effective_to_date = datetime.now() - timedelta(days=1)
                    existing_contact.modified_by = user_id
                    existing_contact.modified_on = datetime.now()

                    new_contact = StakeHolderContactDetails(
                        stake_holder_id=stake_holder_master.id,
                        effective_from_date=datetime.now(),
                        effective_to_date=None,
                        created_by=user_id,
                        created_on=datetime.now()
                    )
                    for field in vars(contact_details):
                        if field != "id" and hasattr(new_contact, field):
                            setattr(new_contact, field, getattr(contact_details, field))
                    db.add(new_contact)
                    db.flush()
                    contact_details_id = new_contact.id
            else:
                new_contact = StakeHolderContactDetails(
                    stake_holder_id=stake_holder_master.id,
                    effective_from_date=datetime.now(),
                    effective_to_date=None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                for field in vars(contact_details):
                    if field != "id" and hasattr(new_contact, field):
                        setattr(new_contact, field, getattr(contact_details, field))
                db.add(new_contact)
                db.flush()
                contact_details_id = new_contact.id

        # Handle StakeHolderAddress
        
        for addr in request.address:
            existing_address = db.query(StakeHolderAddress).filter(
                StakeHolderAddress.stake_holder_id == stake_holder_master.id,
                StakeHolderAddress.effective_to_date == None  # Only active entries
            ).first()

            if existing_address:
                has_changes = any(
                    getattr(existing_address, field, None) != getattr(addr, field, None)
                    for field in vars(addr)
                    if field != "id" and hasattr(existing_address, field)
                )
                residential_address_id = existing_address.id
                
                if has_changes:
                    existing_address.effective_to_date = datetime.now() - timedelta(days=1)
                    existing_address.modified_by = user_id
                    existing_address.modified_on = datetime.now()
                    
                    new_address = StakeHolderAddress(
                        stake_holder_id=stake_holder_master.id,
                        effective_from_date=datetime.now(),
                        effective_to_date=None,
                        created_by=user_id,
                        created_on=datetime.now()
                    )
                    for field in vars(addr):
                        if field != "id" and hasattr(new_address, field):
                            setattr(new_address, field, getattr(addr, field))
                    db.add(new_address)
                    db.flush()
                    residential_address_id = new_address.id
            else:
                new_address = StakeHolderAddress(
                    stake_holder_id=stake_holder_master.id,
                    effective_from_date=datetime.now(),
                    effective_to_date=None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                for field in vars(addr):
                    if field != "id" and hasattr(new_address, field):
                        setattr(new_address, field, getattr(addr, field))
                db.add(new_address)
                db.flush()
                residential_address_id = new_address.id

        # Handle CustomerStakeHolder
        amended_parent_id = None
        existing_customer_stakeholder_entry = db.query(CustomerStakeHolder).filter_by(
            customer_id=customer_id,
            stake_holder_master_id=stake_holder_master.id
        ).filter(CustomerStakeHolder.effective_to_date == None).first()

        if existing_customer_stakeholder_entry:
            amended_parent_id = existing_customer_stakeholder_entry.id
            existing_customer_stakeholder_entry.effective_to_date = datetime.now() - timedelta(days=1)
            existing_customer_stakeholder_entry.modified_by = user_id
            existing_customer_stakeholder_entry.modified_on = datetime.now()

        customer_stakeholder_entry = CustomerStakeHolder(
            customer_id=customer_id,
            stake_holder_master_id=stake_holder_master.id,
            designation_id=request.customer_stakeholders[0].designation_id,
            contact_details_id=contact_details_id,
            residential_address_id=residential_address_id,
            stake_holder_type=stake_holder_type,
            is_authorized_signatory=is_authorized_signatory,
            is_primary_authorized_signatory=is_primary_authorized_signatory,
            authorized_representative_type=authorized_representative_type,
            service_task_id=service_task_id,
            effective_from_date=datetime.now(),
            effective_to_date=None,
            
            created_by=user_id,
            created_on=datetime.now()
        )
        db.add(customer_stakeholder_entry)
        db.flush()
        new_record_id = customer_stakeholder_entry.id
        customer_stakeholder_entry.amended_parent_id = new_record_id  
        db.commit()
        return {"detail": "Stakeholder details saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#-----------------------------------------------------------------------------------------------------------------
def get_stakeholder_details(
    db: Session,
    user_id: int,
    customer_id: Optional[int] = None,
    service_task_id: Optional[int] = None,
    stake_holder_type: Optional[str] = None,
    is_authorized_signatory: Optional[str] = None,
    is_primary_authorized_signatory: Optional[str] = None,
    authorized_representative_type: Optional[str] = None,
    search_value: Optional[str] = None
):
    try:
        # Step 1: Query StakeHolderContactDetails based on search_value
        matching_contact_ids = []
        if search_value:
            # Build query to search by mobile_number or email_address
            matching_contacts = db.query(StakeHolderContactDetails).filter(
                StakeHolderContactDetails.is_deleted == 'no',
                StakeHolderContactDetails.effective_from_date <= datetime.now(),
                StakeHolderContactDetails.effective_to_date.is_(None),
                or_(
                    StakeHolderContactDetails.mobile_number == search_value) |
                   (StakeHolderContactDetails.email_address == search_value)
            ).all()

            # Extract contact IDs for filtering
            matching_contact_ids = [contact.id for contact in matching_contacts]

        # Step 2: Query CustomerStakeHolder with filters
        query = db.query(CustomerStakeHolder).filter(
            CustomerStakeHolder.is_deleted == 'no',
            CustomerStakeHolder.effective_from_date <= datetime.now(),
            (CustomerStakeHolder.effective_to_date.is_(None)) )
    

        # Apply filters dynamically
        if matching_contact_ids:
            query = query.filter(CustomerStakeHolder.contact_details_id.in_(matching_contact_ids))
        if customer_id:
            query = query.filter(CustomerStakeHolder.customer_id == customer_id)
        if stake_holder_type:
            query = query.filter(CustomerStakeHolder.stake_holder_type == stake_holder_type)
        if is_authorized_signatory is not None:
            query = query.filter(CustomerStakeHolder.is_authorized_signatory == is_authorized_signatory)
        if is_primary_authorized_signatory is not None:
            query = query.filter(CustomerStakeHolder.is_primary_authorized_signatory == is_primary_authorized_signatory)
        if authorized_representative_type is not None:
            query = query.filter(CustomerStakeHolder.authorized_representative_type == authorized_representative_type)
        if service_task_id:
            query = query.filter(CustomerStakeHolder.service_task_id == service_task_id)

        # Fetch all matching stakeholders
        stakeholders = query.all()

        # Step 3: Assemble stakeholder details
        stakeholder_details = []
        for stakeholder in stakeholders:
            stakeholder_master = db.query(StakeHolderMaster).filter_by(
                id=stakeholder.stake_holder_master_id,
                is_deleted='no'
            ).first()
            if not stakeholder_master:
                return []

            # Fetch related data
            contact_details = db.query(StakeHolderContactDetails).filter(
                StakeHolderContactDetails.id == stakeholder.contact_details_id,
                StakeHolderContactDetails.is_deleted == 'no'
            ).first()

            address = db.query(StakeHolderAddress).filter(
                StakeHolderAddress.id == stakeholder.residential_address_id,
                StakeHolderAddress.is_deleted == 'no'
            ).first()

            # Fetch designation based on stakeholder type
            designation = None
            designation_code = None
            if stake_holder_type in ['PROMOTER_PARTNER_DIRECTOR', 'AUTHORIZED_SIGNATORY'] or stake_holder_type is None:
                designation = db.query(AppConstitutionStakeholders).filter(
                    AppConstitutionStakeholders.id == stakeholder.designation_id,
                    AppConstitutionStakeholders.is_deleted == 'no'
                ).first()
                if designation:
                    designation_name = designation.stakeholder
            elif stake_holder_type == 'AUTHORIZED_REPRESENTATIVE'or stake_holder_type is None:
                designation = db.query(GstOtherAuthorizedRepresentativeResignation).filter(
                    GstOtherAuthorizedRepresentativeResignation.id == stakeholder.designation_id,
                    GstOtherAuthorizedRepresentativeResignation.is_deleted == 'no'
                ).first()
                if designation:
                    designation_name = designation.designation  
                    designation_code = designation.designation_code 
            # Prepare response data
            stakeholder_details.append({
                "personal_information": {
                    "id": stakeholder_master.id,
                    "first_name": stakeholder_master.first_name,
                    "middle_name": stakeholder_master.middle_name,
                    "last_name": stakeholder_master.last_name,
                    "fathers_first_name": stakeholder_master.fathers_first_name,
                    "fathers_middle_name": stakeholder_master.fathers_middle_name,
                    "fathers_last_name": stakeholder_master.fathers_last_name,
                    "marital_status_id": stakeholder_master.marital_status_id,
                    "marital_status": db.query(MaritalStatus.marital_status).filter_by(
                        id=stakeholder_master.marital_status_id
                    ).scalar(),
                    "date_of_birth": stakeholder_master.date_of_birth,
                    "gender_id": stakeholder_master.gender_id,
                    "gender": db.query(Gender.gender).filter_by(
                        id=stakeholder_master.gender_id
                    ).scalar()
                },
                "identity_information": {
                    "id": stakeholder_master.id,
                    "din_number": stakeholder_master.din_number,
                    "is_citizen_of_india": stakeholder_master.is_citizen_of_india,
                    "pan_number": stakeholder_master.pan_number,
                    "passport_number": stakeholder_master.passport_number,
                    "aadhaar_number": stakeholder_master.aadhaar_number,
                    "gst_enrollment_number": stakeholder_master.gst_enrollment_number
                },
                "customer_stakeholders": {
                    "id": stakeholder.id,
                    "designation_id": designation.id if designation else None,
                    "designation": designation_name,
                    "designation_code": designation_code,
                    "stake_holder_type": stakeholder.stake_holder_type,
                    "is_authorized_signatory": stakeholder.is_authorized_signatory,
                    "is_primary_authorized_signatory": stakeholder.is_primary_authorized_signatory,
                    "authorized_representative_type": stakeholder.authorized_representative_type
                },
                "contact_details": {
                    "id": contact_details.id if contact_details else None,
                    "mobile_number": contact_details.mobile_number if contact_details else None,
                    "email_address": contact_details.email_address if contact_details else None,
                    "telephone_number_with_std_code": contact_details.telephone_number_with_std_code if contact_details else None
                },
                "address": {
                        "id": address.id if address else None,
                        "pin_code": address.pin_code if address else None,
                        "address_type": address.address_type if address else None,
                        "country_id": address.country_id if address else None,
                        "country_name": db.query(CountryDB.country_name_english).filter_by(id=address.country_id).scalar() if address and address.country_id else None,
                        "state_id": address.state_id if address else None,
                        "state_name": db.query(StateDB.state_name).filter_by(id=address.state_id).scalar() if address and address.state_id else None,
                        "district_id": address.district_id if address else None,
                        "district_name": db.query(DistrictDB.district_name).filter_by(id=address.district_id).scalar() if address and address.district_id else None,
                        "district_code": db.query(DistrictDB.gst_district_code).filter_by(id=address.district_id).scalar() if address and address.district_id else None,
                        "city_id": address.city_id if address else None,
                        "city_name": db.query(CityDB.city_name).filter_by(id=address.city_id).scalar() if address and address.city_id else None,
                        "village_id": address.village_id if address else None,
                        "village_name": db.query(AppViewVillages.village_name).filter_by(app_village_id=address.village_id).scalar() if address and address.village_id else None,
                        "post_office_id": address.post_office_id if address else None,
                        "post_office_name": db.query(PostOfficeView.post_office_name).filter_by(id=address.post_office_id).scalar() if address and address.post_office_id else None,
                        "taluk_id": address.taluk_id if address else None,
                        "taluk_name": db.query(TalukDB.taluk_name).filter_by(id=address.taluk_id).scalar() if address and address.taluk_id else None,
                        "lsg_type_id": address.lsg_type_id if address and address.lsg_type_id else None,
                        "lsg_type_name": (db.query(AppViewVillages.lsg_type)
                        .filter_by(lsg_type_id=address.lsg_type_id)
                           .first().lsg_type if address and address.lsg_type_id else None),
                        "lsg_id": address.lsg_id if address and address.lsg_id else None,
                        "lsg_name": (db.query(AppViewVillages.lsg_name)
                        .filter_by(lsg_id=address.lsg_id)
                        .first().lsg_name if address and address.lsg_id else None),
                        "locality": address.locality if address else None,
                        "road_street_name": address.road_street_name if address else None,
                        "premises_building_name": address.premises_building_name if address else None,
                        "building_flat_number": address.building_flat_number if address else None,
                        "floor_number": address.floor_number if address else None,
                        "landmark": address.landmark if address else None
                    }
            })
        
        return stakeholder_details
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#----get activity--------------------------------------------------------------------------------------------------
def fetch_business_activities(
    db: Session, 
    activity_type_id: Optional[int], 
    business_activity_master_id: Optional[int],
    user_id: int
) -> Dict[str, Any]:
    # Base query with joins
    stmt = (
        select(
            BusinessActivityType.id.label("business_activity_type_id"),
            BusinessActivityType.business_activity_type,
            BusinessActivityMaster.id.label("business_activity_master_id"),
            BusinessActivityMaster.business_activity,
            BusinessActivity.id.label("activity_id"),
            BusinessActivity.business_activity.label("activity")
        )
        .join(BusinessActivityMaster, BusinessActivityType.id == BusinessActivityMaster.business_activity_type_id)
        .join(BusinessActivity, BusinessActivityMaster.id == BusinessActivity.activity_master_id)
        .where(
            BusinessActivityType.is_deleted == 'no',
            BusinessActivityMaster.is_deleted == 'no',
            BusinessActivity.is_deleted == 'no'
        )
    )

    # Apply filters conditionally
    if activity_type_id:
        stmt = stmt.where(BusinessActivityType.id == activity_type_id)
    if business_activity_master_id:
        stmt = stmt.where(BusinessActivityMaster.id == business_activity_master_id)

    # Execute the query
    result = db.execute(stmt).all()

    # Return empty list if no results found
    if not result:
        return {"business_activities": []}

    # Check if only activity_type_id is provided
    if activity_type_id and not business_activity_master_id:
        # Simplified response with only business_activity_master_id and business_activity fields
        business_activities = [
            {
                "business_activity_master_id": row[2],
                "business_activity": row[3]
            }
            for row in result
        ]
        # Remove duplicates if any
        unique_business_activities = []
        seen_ids = set()
        for activity in business_activities:
            if activity["business_activity_master_id"] not in seen_ids:
                unique_business_activities.append(activity)
                seen_ids.add(activity["business_activity_master_id"])

        return {"business_activities": unique_business_activities}

    # Check if only business_activity_master_id is provided
    if business_activity_master_id and not activity_type_id:
        # Return only the activities related to the business_activity_master_id
        activities = [
            {
                "activity_id": row[4],
                "activity": row[5]
            }
            for row in result
            if row[2] == business_activity_master_id  # Filter by business_activity_master_id
        ]
        return {"activities": activities}

    # If both parameters are provided, return filtered activities
    activities_dict = {}
    for row in result:
        business_activity_master_id = row[2]
        if business_activity_master_id not in activities_dict:
            activities_dict[business_activity_master_id] = {
                "business_activity_master_id": business_activity_master_id,
                "business_activity": row[3],
                "activities": []
            }
        
        activities_dict[business_activity_master_id]["activities"].append({
            "activity_id": row[4],
            "activity": row[5]
        })

    # Convert dictionary to list for the final response
    activities = list(activities_dict.values())

    return {"business_activities": activities}



#----------------Save Business Place----------

#-----------------------------------------------------------------------------------------------------------------
def save_business_place(
    customer_id: int,
    service_task_id: int, 
    data: BusinessData,
    db: Session,
    user_id: int,
    id: int
):
    try:
        # Start transaction
        with db.begin():
            # Check if creating a new business place or updating an existing one
            if id == 0:
                # Create new business place
                for business_place in data.business_place:
                    new_business_place = CustomerBusinessPlace(
                        **business_place.model_dump(exclude_unset=True),
                        customer_id=customer_id,
                        service_task_id=service_task_id,
                        effective_from_date=datetime.now(),
                        effective_to_date=None,
                        created_by=user_id,
                        created_on=datetime.now(),
                    )
                    db.add(new_business_place)
                    db.flush()  # Get the generated ID after insert
                    business_place_id = new_business_place.id
                    new_business_place.amended_parent_id = business_place_id
            else:
                # Update existing business place with id != 0
                existing_business_place = db.query(CustomerBusinessPlace).filter_by(
                    id=id, customer_id=customer_id
                ).first()

                if existing_business_place:
                    for business_place in data.business_place:
                        # Update each attribute of the existing business place
                        for key, value in business_place.model_dump(exclude_unset=True).items():
                            setattr(existing_business_place, key, value)
                    existing_business_place.effective_from_date = datetime.now()
                    existing_business_place.effective_to_date = None
                    existing_business_place.modified_by = user_id
                    existing_business_place.modified_on = datetime.now()
                    business_place_id = existing_business_place.id
                else:
                    return {"message": "Business place not found for update."}

            # Process nature_of_business activities for the business place
            existing_activities = {
                activity.id: activity
                for activity in db.query(CustomerBusinessPlaceActivity)
                .filter_by(customer_id=customer_id, business_place_id=business_place_id)
                .all()
            }

            # Collect incoming service IDs to check against existing ones for deletions
            incoming_activity_ids = {nature.id for nature in data.nature_of_business if nature.id != 0}

            # Mark activities as deleted if they are not in the incoming data
            for activity_id, existing_activity in existing_activities.items():
                if activity_id not in incoming_activity_ids:
                    existing_activity.is_deleted = "yes"
                    existing_activity.deleted_by = user_id
                    existing_activity.deleted_on = datetime.now()
                    existing_activity.modified_by = user_id
                    existing_activity.modified_on = datetime.now()

            # Process each incoming nature_of_business item
            for nature in data.nature_of_business:
                nature_data = nature.model_dump(exclude_unset=True)
                activity_id = nature_data.get("id")

                if activity_id in existing_activities:
                    # Update existing activity
                    existing_activity = existing_activities[activity_id]
                    for key, value in nature_data.items():
                        setattr(existing_activity, key, value)
                    existing_activity.is_deleted = "no"
                    existing_activity.deleted_by = None
                    existing_activity.deleted_on = None
                    existing_activity.modified_by = user_id
                    existing_activity.modified_on = datetime.now()
                else:
                    # Insert new activity if it does not exist in existing_activities
                    new_activity = CustomerBusinessPlaceActivity(
                        customer_id=customer_id,
                        service_task_id=service_task_id,
                        effective_from_date=datetime.now(),
                        effective_to_date=None,
                        created_by=user_id,
                        created_on=datetime.now(),
                        business_place_id=business_place_id,
                        business_activity_id=nature.business_activity_id,
                    )
                    db.add(new_activity)
                    db.flush()  # Get the generated ID after insert
                    activity_id = new_activity.id
                    new_activity.amended_parent_id = activity_id
            # Handle business activity type
            if data.business_activity_type_id is not None:
                existing_activity_type = db.query(CustomerBusinessPlaceActivityType).filter_by(
                    customer_id=customer_id,
                    business_place_id=business_place_id,
                ).first()

                if existing_activity_type:
                    # Update the existing record
                    existing_activity_type.business_activity_type_id = data.business_activity_type_id
                    existing_activity_type.effective_from_date = datetime.now()
                    existing_activity_type.effective_to_date = None
                    existing_activity_type.modified_by = user_id
                    existing_activity_type.modified_on = datetime.now()
                else:
                    # Add a new record if none exists
                    new_activity_type = CustomerBusinessPlaceActivityType(
                        customer_id=customer_id,
                        service_task_id=service_task_id,
                        effective_from_date=datetime.now(),
                        effective_to_date=None,
                        created_by=user_id,
                        created_on=datetime.now(),
                        business_place_id=business_place_id,
                        business_activity_type_id=data.business_activity_type_id,
                    )
                    db.add(new_activity_type)

            # Handle business activity master
            if data.business_activity_master_id is not None:
                existing_core_activity = db.query(CustomerBusinessPlaceCoreActivity).filter_by(
                    customer_id=customer_id,
                    business_place_id=business_place_id,
                ).first()

                if existing_core_activity:
                    # Update the existing record
                    existing_core_activity.business_activity_master_id = data.business_activity_master_id
                    existing_core_activity.effective_from_date = datetime.now()
                    existing_core_activity.effective_to_date = None
                    existing_core_activity.modified_by = user_id
                    existing_core_activity.modified_on = datetime.now()
                else:
                    # Add a new record if none exists
                    new_core_activity = CustomerBusinessPlaceCoreActivity(
                        customer_id=customer_id,
                        service_task_id=service_task_id,
                        effective_from_date=datetime.now(),
                        effective_to_date=None,
                        created_by=user_id,
                        created_on=datetime.now(),
                        business_place_id=business_place_id,
                        business_activity_master_id=data.business_activity_master_id,
                    )
                    db.add(new_core_activity)

            # Commit the transaction after all operations
            db.commit()

        return {"message": "Data saved successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



#-----get business_place----

def get_business_place(customer_id: int, 
                       service_task_id: int, 
                       type: str, 
                       db: Session,
                       user_id: int):
    """
    Fetch business data from the database.
    """
    is_principal_place = 'yes' if type == 'PRINCIPAL_PLACE_ADDRESS' else 'no'

    try:
        # Fetch business places based on customer ID and address type
        business_places = db.query(CustomerBusinessPlace).filter(
            CustomerBusinessPlace.customer_id == customer_id,
            CustomerBusinessPlace.service_task_id == service_task_id,
            CustomerBusinessPlace.is_deleted == 'no',
            CustomerBusinessPlace.is_principal_place == is_principal_place,
            CustomerBusinessPlace.effective_from_date <= datetime.now(),
            or_(CustomerBusinessPlace.effective_to_date.is_(None))
        ).all()

        # If no business places found, return an empty list
        if not business_places:
            return {"business_places": []}

        # Prepare final response array
        response = []

        # Iterate over business places
        for bp in business_places:
            # Fetch business activity type and master details
            business_activity_type = (
                db.query(CustomerBusinessPlaceActivityType)
                .join(CustomerBusinessPlace, CustomerBusinessPlaceActivityType.business_place_id == CustomerBusinessPlace.id)
                .filter(
                    CustomerBusinessPlaceActivityType.business_place_id == bp.id,
                    CustomerBusinessPlaceActivityType.is_deleted == 'no',
                    CustomerBusinessPlaceActivityType.effective_from_date <= datetime.now(),
                    or_(CustomerBusinessPlaceActivityType.effective_to_date.is_(None))
                )
                .first()
            )

            business_activity_master = (
                db.query(CustomerBusinessPlaceCoreActivity)
                .join(CustomerBusinessPlace, CustomerBusinessPlaceCoreActivity.business_place_id == CustomerBusinessPlace.id)
                .filter(
                    CustomerBusinessPlaceCoreActivity.business_place_id == bp.id,
                    CustomerBusinessPlaceCoreActivity.is_deleted == 'no',
                    CustomerBusinessPlaceCoreActivity.effective_from_date <= datetime.now(),
                    or_(CustomerBusinessPlaceCoreActivity.effective_to_date.is_(None))
                )
                .first()
            )


            # Prepare the business place data
            business_place_data = {
                "id": bp.id,
                "pin_code": bp.pin_code,
                "country_id": bp.country_id,
                "country_name": db.query(CountryDB.country_name_english).filter_by(id=bp.country_id).scalar() if bp.country_id else None,
                "state_id": bp.state_id,
                "state_name": db.query(StateDB.state_name).filter_by(id=bp.state_id).scalar() if bp.state_id else None,
                "district_id": bp.district_id,
                "district_name": db.query(DistrictDB.district_name).filter_by(id=bp.district_id).scalar() if bp.district_id else None,
                "taluk_id": bp.taluk_id,
                "taluk_name": db.query(TalukDB.taluk_name).filter_by(id=bp.taluk_id).scalar() if bp.taluk_id else None,
                "city_id": bp.city_id,
                "city_name": db.query(CityDB.city_name).filter_by(id=bp.city_id).scalar() if bp.city_id else None,
                "post_office_id": bp.post_office_id if bp else None,
                "post_office_name": db.query(PostOfficeView.post_office_name).filter_by(id=bp.post_office_id).scalar() if bp and bp.post_office_id else None,
                "village_id": bp.village_id,
                "village_name": db.query(AppViewVillages.village_name).filter_by(app_village_id=bp.village_id).scalar() if bp.village_id else None,
                "lsg_type_id": bp.lsg_type_id,
                "lsg_type_name": db.query(AppViewVillages.lsg_type).filter_by(lsg_type_id=bp.lsg_type_id).first().lsg_type if bp.lsg_type_id else None,
                "lsg_id": bp.lsg_id,
                "lsg_name": db.query(AppViewVillages.lsg_name).filter_by(lsg_id=bp.lsg_id).first().lsg_name if bp.lsg_id else None,
                "locality": bp.locality,
                "road_street_name": bp.road_street_name,
                "premises_building_name": bp.premises_building_name,
                "building_flat_number": bp.building_flat_number,
                "floor_number": bp.floor_number,
                "landmark": bp.landmark,
                "latitude": bp.latitude,
                "longitude": bp.longitude,
                "is_principal_place": bp.is_principal_place,
                "business_place_type": bp.business_place_type,
                "nature_of_possession_id": bp.nature_of_possession_id,
                "nature_of_possession": db.query(GstNatureOfPossessionOfPremises.possession_type).filter_by(id=bp.nature_of_possession_id).scalar() if bp.nature_of_possession_id else None,
                "nature_of_possession_code": db.query(GstNatureOfPossessionOfPremises.possession_code).filter_by(id=bp.nature_of_possession_id).scalar() if bp.nature_of_possession_id else None,
                "office_email_address": bp.office_email_address,     
                "office_mobile_number": bp.office_mobile_number,      
                "office_phone_std_code" : bp.office_phone_std_code,   
                "office_phone_number" : bp.office_phone_number,     
                "office_fax_std_code"  : bp.office_fax_std_code,    
                "office_fax_number"  : bp.office_fax_number      
            }

            # Add business activity type and master details to the business place data
            if business_activity_type:
                activity_type_data = db.query(BusinessActivityType).filter(
                    BusinessActivityType.id == business_activity_type.business_activity_type_id
                ).first()
                business_place_data['business_activity_type_id'] = business_activity_type.business_activity_type_id
                business_place_data['business_activity_type_name'] = activity_type_data.business_activity_type if activity_type_data else None

            if business_activity_master:
                activity_master_data = db.query(BusinessActivityMaster).filter(
                    BusinessActivityMaster.id == business_activity_master.business_activity_master_id
                ).first()
                business_place_data['business_activity_master_id'] = business_activity_master.business_activity_master_id
                business_place_data['business_activity_master_name'] = activity_master_data.business_activity if activity_master_data else None

            # Get nature of business activities
            nature_of_business_response = []
            business_activities = db.query(CustomerBusinessPlaceActivity).filter(
                CustomerBusinessPlaceActivity.business_place_id == bp.id,
                CustomerBusinessPlaceActivity.is_deleted == "no",
                CustomerBusinessPlaceActivity.effective_from_date <= datetime.now(),
                or_(CustomerBusinessPlaceActivity.effective_to_date.is_(None))
            ).all()

            for ba in business_activities:
                activity_data = {
                    "id": ba.id,
                    "business_activity_id": ba.business_activity_id,
                    "business_activity_name": db.query(BusinessActivity).filter(BusinessActivity.id == ba.business_activity_id).first().business_activity if ba.business_activity_id else None,
                    "business_activity_code": db.query(BusinessActivity).filter(BusinessActivity.id == ba.business_activity_id).first().gst_business_activity_code if ba.business_activity_id else None
                }
                nature_of_business_response.append(activity_data)

            # Add nature of business to the business place data
            business_place_data['nature_of_business'] = nature_of_business_response

            # Append the complete business place data to the response
            response.append(business_place_data)

        return {"business_places": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#-------------Get hsn sac
#-----------------------------------------------------------------------------------------------------------------
def get_hsn_sac_data(
    hsn_sac_class_id: int,
    hsn_sac_code: str,
    db: Session,
    user_id: int
):
    try:
        # Base query
        query = db.query(AppHsnSacMaster, AppHsnSacClasses.hsn_sac_class).join(
            AppHsnSacClasses, AppHsnSacMaster.hsn_sac_class_id == AppHsnSacClasses.id
        )

        # Filter based on hsn_sac_class_id
        if hsn_sac_class_id:
            query = query.filter(AppHsnSacMaster.hsn_sac_class_id == hsn_sac_class_id)

        # Check if hsn_sac_code should be exact or use a starts-with match
        if hsn_sac_code:
            # Use starts-with filter by appending "%" to the end of the hsn_sac_code
            query = query.filter(AppHsnSacMaster.hsn_sac_code.like(f"{hsn_sac_code}%"))

        # Execute the query
        results = query.all()

        # If no records are found, return an empty list
        if not results:
            return []

        # Format the results for the response
        response = [
            {
                "hsn_sac_class": result.hsn_sac_class,
                "hsn_sac_code_id": result.AppHsnSacMaster.id,
                "hsn_sac_code": result.AppHsnSacMaster.hsn_sac_code,
                "hsn_sac_description": result.AppHsnSacMaster.hsn_sac_description,
            }
            for result in results
        ]

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#-------------Goods Commodities Supply Details----------

#-----------------------------------------------------------------------------------------------------------------

def save_goods_commodities_details(
    customer_id: int,
    service_task_id: int, 
    details: List[CustomerGoodsCommoditiesSupplyDetailsSchema],
    db: Session,
    user_id: int
):
    try:
        # Fetch existing records for the customer
        existing_entries = {entry.id: entry for entry in db.query(CustomerGoodsCommoditiesSupplyDetails)
                            .filter_by(customer_id=customer_id).all()}

        # Collect IDs of incoming records to identify which records to keep as active
        incoming_ids = {item.id for item in details if item.id != 0}

        # Mark existing records as deleted if they are not in the incoming data
        for entry_id, existing_entry in existing_entries.items():
            if entry_id not in incoming_ids:
                existing_entry.is_deleted = "yes"
                existing_entry.deleted_by = user_id
                existing_entry.deleted_on = datetime.now()
                existing_entry.modified_by = user_id
                existing_entry.modified_on = datetime.now()

        # Process each item in the incoming details list
        for item in details:
            item_data = item.dict(exclude_unset=True)
            entry_id = item_data.get("id")

            if entry_id in existing_entries:
                # Update existing entry
                existing_entry = existing_entries[entry_id]
                for key, value in item_data.items():
                    setattr(existing_entry, key, value)
                existing_entry.is_deleted = "no"
                existing_entry.deleted_by = None
                existing_entry.deleted_on = None
                existing_entry.modified_by = user_id
                existing_entry.modified_on = datetime.now()

            else:
                # Create a new entry if ID is 0 or not found in existing entries
                new_entry = CustomerGoodsCommoditiesSupplyDetails(
                    customer_id=customer_id,
                    hsn_sac_class_id=item.hsn_sac_class_id,
                    hsn_sac_code_id=item.hsn_sac_code_id,
                    effective_from_date=date.today(),
                    effective_to_date=None,
                    service_task_id=service_task_id,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                db.add(new_entry)
                db.commit()  # Commit to save the new entry
                db.refresh(new_entry)  # Refresh to get the updated instance with id

        db.commit()  # Final commit after processing all records

        return {"success": True, "message": "Data saved successfully"}

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=500, detail=str(e))


#----- save Customer Gst State Specific Information
def get_hsn_commodities_by_customer_id(customer_id: int,
                                       service_task_id: int,  
                                       user_id: int, 
                                       db: Session):
    try:
        # Query the CustomerGoodsCommoditiesSupplyDetails for the given customer_id
        commodities = (
            db.query(CustomerGoodsCommoditiesSupplyDetails)
            .filter(
                CustomerGoodsCommoditiesSupplyDetails.customer_id == customer_id,
                CustomerGoodsCommoditiesSupplyDetails.service_task_id == service_task_id,
                CustomerGoodsCommoditiesSupplyDetails.is_deleted == "no",
                CustomerGoodsCommoditiesSupplyDetails.effective_from_date <= datetime.now(),
                or_(CustomerGoodsCommoditiesSupplyDetails.effective_to_date.is_(None))
                    
            )
            .all()  # Use .all() to retrieve multiple commodities
        )

        if not commodities:
            return []  # Return an empty list if no commodities are found

        response = []
        for commodity in commodities:
            # Fetch hsn_sac_class from AppHsnSacClasses based on hsn_sac_class_id
            hsn_class_details = (
                db.query(AppHsnSacClasses)
                .filter(AppHsnSacClasses.id == commodity.hsn_sac_class_id)
                .first()
            )

            # Fetch hsn_sac_code and hsn_sac_description from AppHsnSacMaster based on hsn_sac_code_id
            hsn_details = (
                db.query(AppHsnSacMaster)
                .filter(AppHsnSacMaster.id == commodity.hsn_sac_code_id)
                .first()
            )

            if hsn_class_details and hsn_details:
                response.append({
                    "id":commodity.id,
                    "hsn_sac_class_id": hsn_class_details.id,
                    "hsn_sac_class": hsn_class_details.hsn_sac_class,  
                    "hsn_sac_code_id": hsn_details.id,
                    "hsn_sac_code": hsn_details.hsn_sac_code,
                    "hsn_sac_description": hsn_details.hsn_sac_description,
                })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#-----------------------------------------------------------------------------------------------------------------


def save_customer_gst_state_specific_information(
    id: int,  # 0 for insert, non-zero for update
    customer_id: int,
    service_task_id: int,  
    data: CustomerGstStateSpecificInformationSchema,
    db: Session,
    user_id: int  # Optionally track the user making the changes
):
    try:
        # Use model_dump to get the details as a dictionary
        detail_data = data.model_dump(exclude_unset=True)  # Only include set fields

        if id == 0:
            # Create a new entry if ID is 0
            new_entry = CustomerGstStateSpecificInformation(
                customer_id=customer_id,
                service_task_id=service_task_id,
                **detail_data,
                created_by=user_id,
                created_on=datetime.now(),
                effective_from_date=datetime.now(),  # Set effective_from_date to current date
                effective_to_date=None # Set created_on to current datetime
            )
            db.add(new_entry)
            db.commit()  # Commit to save the new entry
            db.refresh(new_entry)  # Refresh to get the updated instance with id

            return {"success": True, "message": "Data saved successfully"}

        else:
            # Fetch the existing record by ID for updating
            existing_entry = db.query(CustomerGstStateSpecificInformation).filter_by(id=id).first()

            if not existing_entry:
                return []

            # Update the existing record fields
            for key, value in detail_data.items():
                setattr(existing_entry, key, value)

            existing_entry.modified_on = datetime.now()  
            existing_entry.modified_by = user_id  

            db.commit()  # Commit the changes to the database

            return {"success": True, "message": "Data updated successfully"}

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=500, detail=str(e))

#----------get Customer Gst State Specific Information

def get_gst_state_specific_information_by_customer_id(customer_id: int, 
                                                      service_task_id: int, 
                                                      db: Session,
                                                      user_id:int) -> List[CustomerGstStateSpecificInformation]:
    try:
        # Query the CustomerGstStateSpecificInformation for the given customer_id
        gst_info_records = (
            db.query(CustomerGstStateSpecificInformation)
            .filter(CustomerGstStateSpecificInformation.customer_id == customer_id,
                    CustomerGstStateSpecificInformation.service_task_id == service_task_id,
                CustomerGstStateSpecificInformation.effective_from_date <= datetime.now(),
                or_(CustomerGstStateSpecificInformation.effective_to_date.is_(None))
                    
            )
            .all()  
        )
        if not gst_info_records:
            return []  # Return an empty list if no records found

        return gst_info_records

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#-----------------------------------------------------------------------------------------------------------------

def get_details_by_pin(db: Session, pin: str, user_id: int) -> List[RangeDetailsSchema]:
    try:
        # Query the view where jurisdiction contains the PIN or pin matches the PIN
        range_details = db.query(GstViewRange).filter(
            or_(
                GstViewRange.jurisdiction.contains(pin),
                GstViewRange.pin == pin
            )
        ).all()

        # Return an empty list if no matching records are found
        if not range_details:
            return []

        # Create a list of RangeDetailsSchema instances using ** unpacking
        range_info_list = [
            RangeDetailsSchema(**{key: getattr(range_detail, key) for key in RangeDetailsSchema.__annotations__.keys()})
            for range_detail in range_details
        ]

        return range_info_list

    except Exception as e:
        # Properly handle exceptions and provide useful feedback
        raise HTTPException(status_code=500, detail=f"Error occurred while fetching details: {str(e)}")

#-----------------------------------------------------------------------------------------------------------------
def delete_gst_registration_record(
    db: Session,
    user_id: int,
    customer_id: int,
    service_task_id: int,
    stakeholder_id: Optional[int] = None,
    business_place_id: Optional[int] = None
):
    if not stakeholder_id and not business_place_id:
        return []

    try:
        if stakeholder_id:
            # # Delete Stakeholder records with customer_id filter
            stakeholder = db.query(StakeHolderMaster).filter_by(id=stakeholder_id).first()
            if not stakeholder:
                return []
            
            

            # Delete related CustomerStakeHolder with customer_id filter
            customer_stakeholders = db.query(CustomerStakeHolder).filter_by(stake_holder_master_id=stakeholder_id, customer_id=customer_id,service_task_id=service_task_id)
            for customer_sh in customer_stakeholders:
                customer_sh.is_deleted = "yes"
                customer_sh.deleted_by = user_id
                customer_sh.deleted_on = datetime.now()

        elif business_place_id:
            # Delete Business Place records with customer_id filter
            business_place = db.query(CustomerBusinessPlace).filter_by(id=business_place_id, customer_id=customer_id,service_task_id=service_task_id).first()
            if not business_place:
                return []
            
            business_place.is_deleted = "yes"
            business_place.deleted_by = user_id
            business_place.deleted_on = datetime.now()

            # Delete related CustomerBusinessPlaceActivity with customer_id filter
            activities = db.query(CustomerBusinessPlaceActivity).filter_by(business_place_id=business_place_id,customer_id=customer_id,service_task_id=service_task_id)
            for activity in activities:
                activity.is_deleted = "yes"
                activity.deleted_by = user_id
                activity.deleted_on = datetime.now()

            # Delete related CustomerBusinessPlaceActivityType with customer_id filter
            activity_types = db.query(CustomerBusinessPlaceActivityType).filter_by(business_place_id=business_place_id, customer_id=customer_id,service_task_id=service_task_id)
            for activity_type in activity_types:
                activity_type.is_deleted = "yes"
                activity_type.deleted_by = user_id
                activity_type.deleted_on = datetime.now()

            # Delete related CustomerBusinessPlaceCoreActivity with customer_id filter
            core_activities = db.query(CustomerBusinessPlaceCoreActivity).filter_by(business_place_id=business_place_id, customer_id=customer_id,service_task_id=service_task_id)
            for core_activity in core_activities:
                core_activity.is_deleted = "yes"
                core_activity.deleted_by = user_id
                core_activity.deleted_on = datetime.now()

        db.commit()
        return {"success": True, "message": "Data deleted successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------------------------------------------------------------------------------------------


# def duplicate_customer_data(db: Session, customer_id: int, service_task_id: int, user_id: int):
#     try:
#         # Fetch the active customer data for the given customer_id
#         current_date = datetime.now().date()
#         original_customer = db.query(CustomerMaster).filter(
#             CustomerMaster.customer_id == customer_id,
#             CustomerMaster.effective_from_date <= current_date,
#             (CustomerMaster.effective_to_date.is_(None) | (CustomerMaster.effective_to_date >= current_date))
#         ).first()

#         if not original_customer:
#             return {"success": False, "message": "Active customer not found"}

#         # Check if service_task_id is present
#         if original_customer.service_task_id == service_task_id:
#             # Return the existing record ID if service_task_id is present
#             return {"success": True, "message": "Service task has already started", "id": original_customer.id}

#         # Use model_validate instead of from_orm
#         customer_data = CustomerDuplicateSchema.model_validate(original_customer)

#         # Create a new CustomerMaster instance from the schema data
#         new_customer = CustomerMaster(
#             customer_id=original_customer.customer_id,
#             **customer_data.model_dump(exclude_unset=True)
#         )

#         # new_customer.is_amendment = 'yes'
#         new_customer.effective_from_date = None
#         new_customer.effective_to_date = None
#         new_customer.created_by = user_id  
#         new_customer.created_on = datetime.now()  
#         new_customer.service_task_id = service_task_id

#         # Add and commit the new entry
#         db.add(new_customer)
#         db.commit()
#         db.refresh(new_customer)

#         return {"success": True,
#                 #  "message": "Saved successfully", 
#                  "id": new_customer.id}

#     except SQLAlchemyError as e:
#         db.rollback()
#         return {"success": False, "message": f"Error duplicating customer: {str(e)}"}

def duplicate_customer_data(db: Session, customer_id: int, service_task_id: int, user_id: int):
    try:
        print(f"Starting duplication for customer_id: {customer_id}, service_task_id: {service_task_id}, user_id: {user_id}")

        # Fetch the active customer data for the given customer_id
        current_date = datetime.now().date()
        original_customer = db.query(CustomerMaster).filter(
            CustomerMaster.customer_id == customer_id,
            CustomerMaster.effective_from_date <= current_date,
            (CustomerMaster.effective_to_date.is_(None) | (CustomerMaster.effective_to_date >= current_date))
        ).first()

        print(f"Fetched original customer: {original_customer}")

        if not original_customer:
            print("No active customer found")
            return {"success": False, "message": "Active customer not found"}

        print(f"Original customer service_task_id: {original_customer.service_task_id}")

        # Check if the service_task_id is already present for the customer
        existing_customer_with_service_task = db.query(CustomerMaster).filter(
            CustomerMaster.customer_id == customer_id,
            CustomerMaster.service_task_id == service_task_id
        ).first()

        if existing_customer_with_service_task:
            # If service_task_id is already present, return the existing row ID
            print(f"Service task ID {service_task_id} already exists for customer {customer_id}")
            return {"success": True, "message": "Service task has already started", "id": existing_customer_with_service_task.id}

        # Use model_validate instead of from_orm
        customer_data = CustomerDuplicateSchema.model_validate(original_customer)
        print(f"Customer data for duplication: {customer_data}")

        # Create a new CustomerMaster instance from the schema data
        new_customer = CustomerMaster(
            customer_id=original_customer.customer_id,
            **customer_data.model_dump(exclude_unset=True)
        )

        new_customer.effective_from_date = None
        new_customer.effective_to_date = None
        new_customer.created_by = user_id  
        new_customer.created_on = datetime.now()
        new_customer.service_task_id = service_task_id  # Update service_task_id
        new_customer.amendment_status="CREATED"

        # Add and commit the new entry
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        print(f"Duplicated customer with new ID: {new_customer.id}")

        return {"success": True, "id": new_customer.id}

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error duplicating customer: {str(e)}")
        return {"success": False, "message": f"Error duplicating customer: {str(e)}"}

#------------------Amendment---------------------------------------------------------------------
def amend_customer_data(
    db: Session, 
    customer_id: int, 
    new_legal_name: str, 
    amendment_reason: str,
    amendment_remarks: str,
    user_id: int
):
    try:
        # Fetch the existing customer data
        original_customer = db.query(CustomerMaster).filter(CustomerMaster.customer_id == customer_id).first()

        if not original_customer:
            return {"success": False, "message": "Customer not found"}
        
        # Prepare amendment data for customer_amendment_history
        amendment_entry = CustomerAmendmentHistory(
            amendment_id=original_customer.id,  # Foreign key to customer_master
            field_name="Legal Name",
            old_value=original_customer.legal_name,
            new_value=new_legal_name,
            amendment_request_date=date.today(),
            amendment_effective_date=None,  # Set as needed
            amendment_remarks=amendment_remarks
        )

        # Update the customer_master table with amendment details
        original_customer.legal_name = new_legal_name
        original_customer.amendment_date = datetime.now()
        original_customer.amendment_reason = amendment_reason
        original_customer.amendment_status = "Pending"  # Update based on your logic
        original_customer.amendment_history = f"Amendment by user {user_id} on {datetime.now().strftime('%Y-%m-%d')}"

        # Add amendment entry to history and update customer_master
        db.add(amendment_entry)
        db.commit()
        db.refresh(original_customer)

        return {"success": True, "message": "Customer amended successfully", "customer_id": original_customer.customer_id}

    except SQLAlchemyError as e:
        db.rollback()
        return {"success": False, "message": f"Error amending customer: {str(e)}"}
#-----------------------------------------------------------------------------------------------------------------------
# def save_amended_data(db: Session, id: int, model_name: str, field_name: str, new_value, date: datetime, remarks: str):
#     # Map model names to actual model classes
#     model_mapping = {
#         "CustomerMaster": CustomerMaster,
      
#     }

#     # Get the model class based on model_name
#     model_class = model_mapping.get(model_name)
#     if not model_class:
#         raise HTTPException(status_code=400, detail=f"Model {model_name} not found.")

#     # Step 1: Get the current data from the master table for the specified field
#     record = db.query(model_class).filter_by(id=id).first()
#     if not record:
#         raise HTTPException(status_code=404, detail="Record not found.")

#     # Use reflection to get the current value of the specified field
#     current_value = getattr(record, field_name, None)
#     if current_value is None:
#         raise HTTPException(status_code=400, detail=f"Field {field_name} not found in {model_name}.")


#     history_entry = CustomerAmendmentHistory(
#         amendment_id=id,
#         old_value=current_value,
#         new_value=new_value,
#         amendment_request_date=date,
#         amendment_remarks=remarks
#     )
#     db.add(history_entry)
    
#     # Step 3: Update the master table for the specified field
#     setattr(record, field_name, new_value)
#     db.commit()

#     return {"success": True, "message": "Amendment saved successfully", "id": id}

#-----------------------------------------------------------------------------------------------------------

def save_amended_data(db: Session, id: int, model_name: str, field_name: str, new_value, date: datetime, remarks: str):
  
    model_mapping = {
        "CustomerMaster": CustomerMaster,
    }

    model_class = model_mapping.get(model_name)
    if not model_class:
        raise HTTPException(status_code=400, detail=f"Model {model_name} not found.")

 
    record = db.query(model_class).filter_by(id=id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    # Check that field_name exists in the model
    if not hasattr(record, field_name):
        raise HTTPException(status_code=400, detail=f"Field {field_name} not found in {model_name}.")

    # Use reflection to get the current value of the specified field
    current_value = getattr(record, field_name, None)

    if current_value is None:
        current_value = "" 

  
    history_entry = CustomerAmendmentHistory(
        amendment_id=id,
        field_name=field_name, 
        old_value=current_value,
        new_value=new_value,
        amendment_request_date=date,
        amendment_remarks=remarks
    )
    db.add(history_entry)
    
    # Step 3: Update the master table for the specified field
    setattr(record, field_name, new_value)
    record.amendment_status = 'CREATED'
    db.commit()

    return {"success": True, "message": "Amendment saved successfully", "id": id}

#----------------------------------------------------------------------------------------------------------------

# def edit_trade_names(db: Session, original_id: int, amendments: List[AdditionalTradeNameAmendment], user_id: int):
#     # Retrieve the original record
#     original_record = db.query(CustomerAdditionalTradeName).filter_by(id=original_id).first()
#     if not original_record:
#         raise HTTPException(status_code=404, detail=f"Original record with id {original_id} not found")

#     for amendment in amendments:
#         # Capture the existing value
#         old_value = original_record.additional_trade_name

#         # Log the amendment in CustomerAmendmentHistory
#         history_entry = CustomerAmendmentHistory(
#             amendment_id=original_id,
#             field_name="additional_trade_name",
#             old_value=old_value,
#             new_value=amendment.new_trade_name,
#             amendment_request_date=amendment.request_date,
#             amendment_remarks=amendment.remarks
#         )
#         db.add(history_entry)

#         # Add a new row in CustomerAdditionalTradeName for the amendment
#         trade_name_entry = CustomerAdditionalTradeName(
#             customer_id=original_record.customer_id,
#             additional_trade_name=amendment.new_trade_name,
#             is_amendment='yes',
#             amendment_date=amendment.request_date,
#             amendment_reason=amendment.remarks,
#             amendment_status='PENDING',
#             amended_parent_id=original_id,
#             created_by=user_id,
#             created_on=datetime.now()
#         )
#         db.add(trade_name_entry)

#     db.commit()
#     return {"success": True, "message": "Trade name amendments requested successfully"}

#--------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------



# def amend_additional_trade_names_in_db(
#     db: Session,
#     customer_id: int,
#     service_task_id: int,
#     amendments: List[AdditionalTradeNameAmendment],
#     created_by: int,
#     action: AmendmentAction
# ):
#     result = {"added": [], "updated": [], "errors": []}

#     try:
#         # Step 1: Check if the service_task_id exists for the customer
#         print(f"Checking if service_task_id {service_task_id} exists for customer_id {customer_id}...")
#         existing_service_task = db.execute(
#             text("""
#                 SELECT * FROM customer_additional_trade_name 
#                 WHERE service_task_id = :service_task_id AND customer_id = :customer_id
#             """),
#             {"service_task_id": service_task_id, "customer_id": customer_id}
#         ).fetchone()

#         if not existing_service_task:
#             # If no existing service_task_id, insert it into the table
#             print(f"No existing service_task found. Inserting new service task {service_task_id}.")
#             for amendment in amendments:
#                 trade_name = amendment.new_trade_name.strip()
#                 db.execute(
#                     text("""
#                         INSERT INTO customer_additional_trade_name 
#                         (service_task_id, customer_id, created_by, is_amendment, amendment_action, amendment_status, additional_trade_name)
#                         VALUES (:service_task_id, :customer_id, :created_by, :is_amendment, :amendment_action, :amendment_status, :additional_trade_name)
#                     """),
#                     {
#                         "service_task_id": service_task_id,
#                         "customer_id": customer_id,
#                         "created_by": created_by,
#                         "is_amendment": 'yes',  
#                         "amendment_action": 'ADDED',  
#                         "amendment_status": 'CREATED', 
#                         "additional_trade_name": trade_name  
#                     }
#                 )
#                 # Fetch the last inserted id for setting `amended_parent_id`
#                 last_inserted_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
#                 # Update the `amended_parent_id` for the newly inserted row
#                 db.execute(
#                     text("""
#                         UPDATE customer_additional_trade_name
#                         SET amended_parent_id = :amended_parent_id
#                         WHERE id = :id
#                     """),
#                     {
#                         "amended_parent_id": last_inserted_id,
#                         "id": last_inserted_id
#                     }
#                 )
#                 result["added"].append(f"Service task {service_task_id} added with trade name {trade_name}")

#         # Step 2: Process amendments for additional trade names
#         for amendment in amendments:
#             trade_name = amendment.new_trade_name.strip()
#             effective_from_date = amendment.request_date

#             if amendment.id == 0:
#                 # Case 1: Insert new trade name record only if it does not already exist
#                 print(f"Inserting new trade_name {trade_name} for customer_id {customer_id}.")
#                 existing_trade_name = db.execute(
#                     text("""
#                         SELECT * FROM customer_additional_trade_name 
#                         WHERE customer_id = :customer_id AND additional_trade_name = :additional_trade_name
#                     """),
#                     {"customer_id": customer_id, "additional_trade_name": trade_name}
#                 ).fetchone()

#                 if not existing_trade_name:
#                     db.execute(
#                         text("""
#                             INSERT INTO customer_additional_trade_name 
#                             (customer_id, additional_trade_name,  created_by, service_task_id)
#                             VALUES (:customer_id, :additional_trade_name, :created_by, :service_task_id)
#                         """),
#                         {
#                             "customer_id": customer_id,
#                             "additional_trade_name": trade_name,
#                             # "effective_from_date": effective_from_date,
#                             "created_by": created_by,
#                             "service_task_id": service_task_id
#                         }
#                     )
#                     # Fetch the last inserted id for setting `amended_parent_id`
#                     last_inserted_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
#                     # Update the `amended_parent_id` for the newly inserted row
#                     db.execute(
#                         text("""
#                             UPDATE customer_additional_trade_name
#                             SET amended_parent_id = :amended_parent_id
#                             WHERE id = :id
#                         """),
#                         {
#                             "amended_parent_id": last_inserted_id,
#                             "id": last_inserted_id
#                         }
#                     )
#                     result["added"].append(f"Trade name {trade_name} added for customer {customer_id}.")
#                 else:
#                     result["errors"].append(f"Trade name {trade_name} already exists for customer {customer_id}.")

#             else:
#                 # Check if effective_from_date exists for the given id
#                 existing_trade_name = db.execute(
#                     text("""
#                         SELECT effective_from_date FROM customer_additional_trade_name 
#                         WHERE id = :id
#                     """),
#                     {"id": amendment.id}
#                 ).fetchone()

#                 if existing_trade_name and existing_trade_name[0]:
#                     # Case 2: Duplicate the row with amendment_parent_id as the row we are updating
#                     print(f"Duplicating and updating trade_name {trade_name} for customer_id {customer_id}.")
#                     db.execute(
#                         text("""
#                             INSERT INTO customer_additional_trade_name 
#                             (customer_id, additional_trade_name, effective_from_date, effective_to_date, created_by, service_task_id, amended_parent_id, is_amendment, amendment_action, amendment_status)
#                             VALUES (:customer_id, :additional_trade_name, NULL, NULL, :created_by, :service_task_id, :amended_parent_id, :is_amendment, :amendment_action, :amendment_status)
#                         """),
#                         {
#                             "customer_id": customer_id,
#                             "additional_trade_name": trade_name,
#                             "created_by": created_by,
#                             "service_task_id": service_task_id,
#                             "amended_parent_id": amendment.id,
#                             "is_amendment": 'yes',
#                             "amendment_action": 'EDITED',
#                             "amendment_status": 'CREATED'
#                         }
#                     )
#                     result["updated"].append(f"Trade name {trade_name} duplicated and updated for customer {customer_id}.")
#                 else:
#                     # Case 3: Update the existing row without duplication
#                     print(f"Updating trade_name {trade_name} for customer_id {customer_id} without duplication.")
#                     db.execute(
#                         text("""
#                             UPDATE customer_additional_trade_name
#                             SET additional_trade_name = :additional_trade_name,
                                
#                                 service_task_id = :service_task_id
#                             WHERE id = :id
#                         """),
#                         {
#                             "additional_trade_name": trade_name,
                            
#                             "service_task_id": service_task_id,
#                             "id": amendment.id
#                         }
#                     )
#                     result["updated"].append(f"Trade name {trade_name} updated for customer {customer_id} without duplication.")

#         # Commit the changes after all operations
#         db.commit()
#         print("Changes committed successfully.")
#     except Exception as e:
#         db.rollback()
#         print(f"An error occurred: {e}")
#         result["errors"].append(str(e))

#     return {"success": True, "message": "Amendments processed successfully", "details": result}


def amend_additional_trade_names_in_db(
    db: Session,
    customer_id: int,
    service_task_id: int,
    amendments: List[AdditionalTradeNameAmendment],
    created_by: int,
    action: AmendmentAction
):
    result = {"added": [], "updated": [], "errors": []}

    try:
        # Step 1: Check if the service_task_id exists for the customer
        print(f"Checking if service_task_id {service_task_id} exists for customer_id {customer_id}...")
        existing_service_task = db.execute(
            text("""
                SELECT * FROM customer_additional_trade_name 
                WHERE service_task_id = :service_task_id AND customer_id = :customer_id
            """),
            {"service_task_id": service_task_id, "customer_id": customer_id}
        ).fetchone()

        if not existing_service_task:
            # If no existing service_task_id, insert it into the table
            print(f"No existing service_task found. Inserting new service task {service_task_id}.")
            for amendment in amendments:
                trade_name = amendment.new_trade_name.strip()
                db.execute(
                    text("""
                        INSERT INTO customer_additional_trade_name 
                        (service_task_id, customer_id, created_by, is_amendment, amendment_action, amendment_status, additional_trade_name)
                        VALUES (:service_task_id, :customer_id, :created_by, :is_amendment, :amendment_action, :amendment_status, :additional_trade_name)
                    """),
                    {
                        "service_task_id": service_task_id,
                        "customer_id": customer_id,
                        "created_by": created_by,
                        "is_amendment": 'yes',  
                        "amendment_action": 'ADDED',  
                        "amendment_status": 'CREATED', 
                        "additional_trade_name": trade_name  
                    }
                )
                # Fetch the last inserted id for setting `amended_parent_id`
                last_inserted_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
                # Update the `amended_parent_id` for the newly inserted row
                db.execute(
                    text("""
                        UPDATE customer_additional_trade_name
                        SET amended_parent_id = :amended_parent_id
                        WHERE id = :id
                    """),
                    {
                        "amended_parent_id": last_inserted_id,
                        "id": last_inserted_id
                    }
                )
                result["added"].append(f"Service task {service_task_id} added with trade name {trade_name}")

        # Step 2: Process amendments for additional trade names
        for amendment in amendments:
            trade_name = amendment.new_trade_name.strip()
            effective_from_date = amendment.request_date

            if amendment.id == 0:
                # Case 1: Insert new trade name record only if it does not already exist
                print(f"Inserting new trade_name {trade_name} for customer_id {customer_id}.")
                existing_trade_name = db.execute(
                    text("""
                        SELECT * FROM customer_additional_trade_name 
                        WHERE customer_id = :customer_id AND additional_trade_name = :additional_trade_name
                    """),
                    {"customer_id": customer_id, "additional_trade_name": trade_name}
                ).fetchone()

                if not existing_trade_name:
                    db.execute(
                        text("""
                            INSERT INTO customer_additional_trade_name 
                            (customer_id, additional_trade_name, created_by, service_task_id, is_amendment, amendment_action, amendment_status)
                            VALUES (:customer_id, :additional_trade_name, :created_by, :service_task_id, :is_amendment, :amendment_action, :amendment_status)
                        """),
                        {
                            "customer_id": customer_id,
                            "additional_trade_name": trade_name,
                            "created_by": created_by,
                            "service_task_id": service_task_id,
                            "is_amendment": 'yes',
                            "amendment_action": 'ADDED',
                            "amendment_status": 'CREATED'
                        }
                    )
                    # Fetch the last inserted id for setting `amended_parent_id`
                    last_inserted_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
                    # Update the `amended_parent_id` for the newly inserted row
                    db.execute(
                        text("""
                            UPDATE customer_additional_trade_name
                            SET amended_parent_id = :amended_parent_id
                            WHERE id = :id
                        """),
                        {
                            "amended_parent_id": last_inserted_id,
                            "id": last_inserted_id
                        }
                    )
                    result["added"].append(f"Trade name {trade_name} added for customer {customer_id}.")
                else:
                    result["errors"].append(f"Trade name {trade_name} already exists for customer {customer_id}.")

            else:
                # Check if effective_from_date exists for the given id
                existing_trade_name = db.execute(
                    text("""
                        SELECT effective_from_date FROM customer_additional_trade_name 
                        WHERE id = :id
                    """),
                    {"id": amendment.id}
                ).fetchone()

                if existing_trade_name and existing_trade_name[0]:
                    # Case 2: Duplicate the row with amendment_parent_id as the row we are updating
                    print(f"Duplicating and updating trade_name {trade_name} for customer_id {customer_id}.")
                    db.execute(
                        text("""
                            INSERT INTO customer_additional_trade_name 
                            (customer_id, additional_trade_name, effective_from_date, effective_to_date, created_by, service_task_id, amended_parent_id, is_amendment, amendment_action, amendment_status)
                            VALUES (:customer_id, :additional_trade_name, NULL, NULL, :created_by, :service_task_id, :amended_parent_id, :is_amendment, :amendment_action, :amendment_status)
                        """),
                        {
                            "customer_id": customer_id,
                            "additional_trade_name": trade_name,
                            "created_by": created_by,
                            "service_task_id": service_task_id,
                            "amended_parent_id": amendment.id,
                            "is_amendment": 'yes',
                            "amendment_action": 'EDITED',
                            "amendment_status": 'CREATED'
                        }
                    )
                    result["updated"].append(f"Trade name {trade_name} duplicated and updated for customer {customer_id}.")
                else:
                    # Case 3: Update the existing row without duplication
                    print(f"Updating trade_name {trade_name} for customer_id {customer_id} without duplication.")
                    db.execute(
                        text("""
                            UPDATE customer_additional_trade_name
                            SET additional_trade_name = :additional_trade_name,
                                service_task_id = :service_task_id
                            WHERE id = :id
                        """),
                        {
                            "additional_trade_name": trade_name,
                            "service_task_id": service_task_id,
                            "id": amendment.id
                        }
                    )
                    result["updated"].append(f"Trade name {trade_name} updated for customer {customer_id} without duplication.")

        # Commit the changes after all operations
        db.commit()
        print("Changes committed successfully.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        result["errors"].append(str(e))

    return {"success": True, "message": "Amendments processed successfully", "details": result}



# -------------------------------------------------------------------------------------------------------------

def delete_amendment_business_place(db: Session, id: int, user_id: int):
    try:
        # Fetch the amendment record based on id
        amendment_record = db.execute(
            text("""
                SELECT id, amended_parent_id FROM customer_additional_trade_name 
                WHERE id = :id
            """),
            {"id": id}
        ).fetchone()

        if not amendment_record:
            print("Record not found")
            return {"success": False, "message": "Record not found"}

        print(f"Fetched amendment_record: {amendment_record}")

        if amendment_record[0] == amendment_record[1]:  # id === amended_parent_id
            # Case 1: id and amended_parent_id are the same
            print("Case 1: id and amended_parent_id are the same")
            db.execute(
                text("""
                    UPDATE customer_additional_trade_name
                    SET is_deleted = 'yes'
                    WHERE id = :id
                """),
                {"id": id}
            )
            db.commit()
            return {"success": True, "message": "Record marked as deleted"}
        else:
            # Case 2: id and amended_parent_id are not the same
            print("Case 2: id and amended_parent_id are not the same")
            db.execute(
                text("""
                    UPDATE customer_additional_trade_name
                    SET amendment_action = 'DELETED'
                    WHERE id = :id
                """),
                {"id": id}
            )
            db.commit()
            return {"success": True, "message": "Amendment marked as deleted"}

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        return {"success": False, "message": str(e)}




#---------------------------------------------------------------------------------------------------------------



def add_stake_holder(db: Session, customer_id: int, service_task_id: int, stakeholder_type: str, request_data: AmmendStakeHolderMasterSchema, user_id: int):
    try:
        # Check for existing stakeholder
        existing_stakeholder = db.query(StakeHolderMaster).filter_by(
            first_name=request_data.personal_information.first_name,
            middle_name=request_data.personal_information.middle_name,
            last_name=request_data.personal_information.last_name,
            fathers_first_name=request_data.personal_information.fathers_first_name,
            fathers_middle_name=request_data.personal_information.fathers_middle_name,
            fathers_last_name=request_data.personal_information.fathers_last_name,
            marital_status_id=request_data.personal_information.marital_status_id,
            gender_id=request_data.personal_information.gender_id,
            din_number=request_data.personal_information.din_number,
            is_citizen_of_india=request_data.personal_information.is_citizen_of_india,
            passport_number=request_data.personal_information.passport_number,
            aadhaar_number=request_data.personal_information.aadhaar_number,
            date_of_birth=request_data.personal_information.date_of_birth,
            pan_number=request_data.personal_information.pan_number
        ).first()

        if existing_stakeholder:
            stake_holder_id = existing_stakeholder.id
        else:
            # Insert data into StakeHolderMaster
            new_stake_holder = StakeHolderMaster(
                first_name=request_data.personal_information.first_name,
                middle_name=request_data.personal_information.middle_name,
                last_name=request_data.personal_information.last_name,
                fathers_first_name=request_data.personal_information.fathers_first_name,
                fathers_middle_name=request_data.personal_information.fathers_middle_name,
                fathers_last_name=request_data.personal_information.fathers_last_name,
                marital_status_id=request_data.personal_information.marital_status_id,
                date_of_birth=request_data.personal_information.date_of_birth,
                gender_id=request_data.personal_information.gender_id,
                din_number=request_data.personal_information.din_number,
                is_citizen_of_india=request_data.personal_information.is_citizen_of_india,
                pan_number=request_data.personal_information.pan_number,
                passport_number=request_data.personal_information.passport_number,
                aadhaar_number=request_data.personal_information.aadhaar_number,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_stake_holder)
            db.commit()
            db.refresh(new_stake_holder)
            stake_holder_id = new_stake_holder.id

        # Check for existing address
        existing_address = db.query(StakeHolderAddress).filter_by(
            pin_code=request_data.address[0].pin_code,
            country_id=request_data.address[0].country_id,
            state_id=request_data.address[0].state_id,
            district_id=request_data.address[0].district_id,
            city_id=request_data.address[0].city_id,
            village_id=request_data.address[0].village_id,
            post_office_id=request_data.address[0].post_office_id,
            taluk_id=request_data.address[0].taluk_id,
            lsg_type_id=request_data.address[0].lsg_type_id,
            lsg_id=request_data.address[0].lsg_id,
            locality=request_data.address[0].locality,
            road_street_name=request_data.address[0].road_street_name,
            premises_building_name=request_data.address[0].premises_building_name,
            building_flat_number=request_data.address[0].building_flat_number,
            floor_number=request_data.address[0].floor_number,
            landmark=request_data.address[0].landmark
        ).first()

        if existing_address:
            permanent_address_id = existing_address.id
        else:
            # Insert data into StakeHolderAddress
            new_address = StakeHolderAddress(
                stake_holder_id=stake_holder_id,
                address_type='PERMANENT',
                pin_code=request_data.address[0].pin_code,
                country_id=request_data.address[0].country_id,
                state_id=request_data.address[0].state_id,
                district_id=request_data.address[0].district_id,
                city_id=request_data.address[0].city_id,
                village_id=request_data.address[0].village_id,
                post_office_id=request_data.address[0].post_office_id,
                taluk_id=request_data.address[0].taluk_id,
                lsg_type_id=request_data.address[0].lsg_type_id,
                lsg_id=request_data.address[0].lsg_id,
                locality=request_data.address[0].locality,
                road_street_name=request_data.address[0].road_street_name,
                premises_building_name=request_data.address[0].premises_building_name,
                building_flat_number=request_data.address[0].building_flat_number,
                floor_number=request_data.address[0].floor_number,
                landmark=request_data.address[0].landmark,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_address)
            db.commit()
            db.refresh(new_address)
            permanent_address_id = new_address.id

        # Check for existing contact details
        existing_contact_details = db.query(StakeHolderContactDetails).filter_by(
            mobile_number=request_data.contact_details[0].mobile_number,
            email_address=request_data.contact_details[0].email_address,
            telephone_number_with_std_code=request_data.contact_details[0].telephone_number_with_std_code
        ).first()

        if existing_contact_details:
            contact_details_id = existing_contact_details.id
        else:
            # Insert data into StakeHolderContactDetails
            new_contact_details = StakeHolderContactDetails(
                stake_holder_id=stake_holder_id,
                mobile_number=request_data.contact_details[0].mobile_number,
                email_address=request_data.contact_details[0].email_address,
                telephone_number_with_std_code=request_data.contact_details[0].telephone_number_with_std_code,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_contact_details)
            db.commit()
            db.refresh(new_contact_details)
            contact_details_id = new_contact_details.id

        # Check if CustomerStakeHolder already exists with customer_id, service_task_id, and stakeholder_type
        existing_customer_stake_holder = db.query(CustomerStakeHolder).filter_by(
            customer_id=customer_id,
            service_task_id=service_task_id,
            stake_holder_type=stakeholder_type
        ).first()

        if existing_customer_stake_holder:
            # Update existing CustomerStakeHolder with the new stake_holder_id, contact_details_id, and permanent_address_id
            existing_customer_stake_holder.stake_holder_master_id = stake_holder_id
            existing_customer_stake_holder.contact_details_id = contact_details_id
            existing_customer_stake_holder.permanent_address_id = permanent_address_id
            existing_customer_stake_holder.designation_id = request_data.personal_information.designation_id
            db.commit()
            return {"success": True, "message": "Stakeholder updated successfully", "id": existing_customer_stake_holder.id}
        else:
            # Insert data into CustomerStakeHolder
            new_customer_stake_holder = CustomerStakeHolder(
                customer_id=customer_id,
                service_task_id=service_task_id,
                stake_holder_master_id=stake_holder_id,
                stake_holder_type=stakeholder_type,
                designation_id=request_data.personal_information.designation_id,
                contact_details_id=contact_details_id,
                permanent_address_id=permanent_address_id,
                official_mobile_number=request_data.contact_details[0].mobile_number,
                official_email_address=request_data.contact_details[0].email_address,
                is_amendment='yes',
                amendment_date=datetime.now(),
                amendment_reason='Adding new stakeholder',
                amendment_status='CREATED',
                amendment_action='ADDED',
                effective_from_date=None,
                effective_to_date=None,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_customer_stake_holder)
            db.commit()
            db.refresh(new_customer_stake_holder)

            # Update the amended_parent_id to be the same as id 
            new_customer_stake_holder.amended_parent_id = new_customer_stake_holder.id 
            db.commit()

            return {"success": True, "message": "Stakeholder added successfully", "id": new_customer_stake_holder.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------------------------------------------------------------------------------------------

def delete_stake_holder(db: Session, id: int, amendment_details: AmendmentDetailsSchema, action: AmendmentAction, user_id: int):
    try:
        existing_stake_holder = db.query(CustomerStakeHolder).filter(CustomerStakeHolder.id == id).first()
        if not existing_stake_holder:
            raise HTTPException(status_code=404, detail="Stakeholder not found")

        # Duplicate the existing row
        new_stake_holder = CustomerStakeHolder(
            customer_id=existing_stake_holder.customer_id,
            stake_holder_master_id=existing_stake_holder.stake_holder_master_id,
            stake_holder_type=existing_stake_holder.stake_holder_type,
            designation_id=existing_stake_holder.designation_id,
            official_position_id=existing_stake_holder.official_position_id,
            is_authorized_signatory=existing_stake_holder.is_authorized_signatory,
            is_primary_authorized_signatory=existing_stake_holder.is_primary_authorized_signatory,
            contact_details_id=existing_stake_holder.contact_details_id,
            permanent_address_id=existing_stake_holder.permanent_address_id,
            official_mobile_number=existing_stake_holder.official_mobile_number,
            official_email_address=existing_stake_holder.official_email_address,
            is_amendment='yes',
            amendment_date=amendment_details.date,
            amendment_reason=amendment_details.reason,
            amendment_status='CREATED',
            amendment_action=action.value,
            # effective_from_date=existing_stake_holder.effective_from_date,
            # effective_to_date=existing_stake_holder.effective_to_date,
            created_by=user_id,
            created_on=datetime.now(),
            amended_parent_id=existing_stake_holder.id 
        )

        db.add(new_stake_holder)
        db.commit()
        db.refresh(new_stake_holder)

        return {"success": True, "message": "Stakeholder marked for deletion successfully", "id": new_stake_holder.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#------------------------------------------------------------------------------------------------------------


def get_stakeholder_master_for_amndement(db: Session, 
                            customer_id: int, 
                            
                            stakeholder_type: str,
                            service_task_id:int,
                            user_id: int):
    try:
        # Fetch records from CustomerStakeHolder based on customer_id
        customer_stakeholders = db.query(CustomerStakeHolder).filter_by(
            customer_id=customer_id,
            service_task_id=service_task_id,
              is_deleted='no',is_amendment='yes').all()

        
        if not customer_stakeholders:
            return []

        # Initialize an empty list to hold stakeholder details
        stakeholder_details = []
        
        for customer_stakeholder in customer_stakeholders:
            # Check if the stakeholder type matches and effective date conditions are satisfied
            if customer_stakeholder.stake_holder_type == stakeholder_type :
                # and 
                # customer_stakeholder.effective_from_date is not None and
                # customer_stakeholder.effective_from_date <= datetime.now().date() and
                # customer_stakeholder.effective_to_date is None):
                
                # Fetch StakeHolderMaster record
                stakeholder = (
                    db.query(StakeHolderMaster)
                    .filter_by(id=customer_stakeholder.stake_holder_master_id)
                    .filter(StakeHolderMaster.is_deleted == 'no')  # Assuming is_deleted is a column
                    .first()
                )
                if not stakeholder:
                    return []

                # Fetch StakeHolderAddress record based on residential_address_id
                address = (
                    db.query(StakeHolderAddress)
                    .filter_by(id=customer_stakeholder.permanent_address_id)
                    # .filter(StakeHolderAddress.effective_from_date <= datetime.now().date())
                    # .filter(StakeHolderAddress.effective_to_date.is_(None))
                     
                    .first() if customer_stakeholder.permanent_address_id else None
                )

                # Fetch designation
                designation = (
                    db.query(AppConstitutionStakeholders)
                    .filter_by(id=customer_stakeholder.designation_id)
                    .filter(AppConstitutionStakeholders.is_deleted == 'no')  # Assuming AppDesignation has an is_deleted column
                    .first() if customer_stakeholder.designation_id else None
                )


                # Fetch StakeHolderContactDetails
                contact_details = (
                    db.query(StakeHolderContactDetails)
                    .filter_by(id=customer_stakeholder.contact_details_id)
                    # .filter(StakeHolderContactDetails.effective_from_date <= datetime.now().date())
                    # .filter(StakeHolderContactDetails.effective_to_date.is_(None))
                    .filter(StakeHolderContactDetails.is_deleted == 'no')  # Filter by is_deleted
                    .first() if customer_stakeholder.contact_details_id else None
                )

                # Assemble the response for the stakeholder
                response = {
                    "personal_information": {
                    "id": stakeholder.id,
                    "first_name": stakeholder.first_name,
                    "middle_name": stakeholder.middle_name,
                    "last_name": stakeholder.last_name,
                    "fathers_first_name": stakeholder.fathers_first_name,
                    "fathers_middle_name": stakeholder.fathers_middle_name,
                    "fathers_last_name": stakeholder.fathers_last_name,
                    "marital_status_id": stakeholder.marital_status_id,
                    "marital_status": db.query(MaritalStatus.marital_status).filter_by(
                        id=stakeholder.marital_status_id
                    ).scalar(),
                    "date_of_birth": stakeholder.date_of_birth,
                    "gender_id": stakeholder.gender_id,
                    "gender": db.query(Gender.gender).filter_by(
                        id=stakeholder.gender_id
                    ).scalar()
                },
                    "identity_information": {
                    "id": stakeholder.id,
                    "din_number": stakeholder.din_number,
                    "is_citizen_of_india": stakeholder.is_citizen_of_india,
                    "pan_number": stakeholder.pan_number,
                    "passport_number": stakeholder.passport_number,
                    "aadhaar_number": stakeholder.aadhaar_number,
                    "gst_enrollment_number": stakeholder.gst_enrollment_number
                },
                    "customer_stakeholders": {
                    "id": stakeholder.id,
                    "designation_id": designation.id if designation else None,
                    "designation": designation.stakeholder if designation else None,
                },
                    "contact_details": {
                    "id": contact_details.id if contact_details else None,
                    "mobile_number": contact_details.mobile_number if contact_details else None,
                    "email_address": contact_details.email_address if contact_details else None,
                    "telephone_number_with_std_code": contact_details.telephone_number_with_std_code if contact_details else None
                },
                    "address": {
                        "id": address.id if address else None,
                        "pin_code": address.pin_code if address else None,
                        "address_type": address.address_type if address else None,
                        "country_id": address.country_id if address else None,
                        "country_name": db.query(CountryDB.country_name_english).filter_by(id=address.country_id).scalar() if address and address.country_id else None,
                        "state_id": address.state_id if address else None,
                        "state_name": db.query(StateDB.state_name).filter_by(id=address.state_id).scalar() if address and address.state_id else None,
                        "district_id": address.district_id if address else None,
                        "district_name": db.query(DistrictDB.district_name).filter_by(id=address.district_id).scalar() if address and address.district_id else None,
                        "city_id": address.city_id if address else None,
                        "city_name": db.query(CityDB.city_name).filter_by(id=address.city_id).scalar() if address and address.city_id else None,
                        "village_id": address.village_id if address else None,
                        "village_name": db.query(AppViewVillages.village_name).filter_by(app_village_id=address.village_id).scalar() if address and address.village_id else None,
                        "post_office_id": address.post_office_id if address else None,
                        "post_office_name": db.query(PostOfficeView.post_office_name).filter_by(id=address.post_office_id).scalar() if address and address.post_office_id else None,
                        "taluk_id": address.taluk_id,
                        "taluk_name": db.query(TalukDB.taluk_name).filter_by(id=address.taluk_id).scalar() if address and address.taluk_id else None,
                        "lsg_type_id": address.lsg_type_id,
                        "lsg_type_name": db.query(AppViewVillages.lsg_type).filter_by(lsg_type_id=address.lsg_type_id).first().lsg_type if address.lsg_type_id else None,
                        "lsg_id": address.lsg_id if address and address.lsg_id else None,
                        "lsg_name": (db.query(AppViewVillages.lsg_name)
                        .filter_by(lsg_id=address.lsg_id)
                        .first().lsg_name if address and address.lsg_id else None),
                        "locality": address.locality if address else None,
                        "road_street_name": address.road_street_name if address else None,
                        "premises_building_name": address.premises_building_name if address else None,
                        "building_flat_number": address.building_flat_number if address else None,
                        "floor_number": address.floor_number if address else None,
                        "landmark": address.landmark if address else None
                    } if address else None
                }

                # Append the response to the stakeholder details list
                stakeholder_details.append(response)

        return stakeholder_details if stakeholder_details else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#-------------------------------------------------------------------------------------------

# def amend_business_place_data(db: Session, customer_id: int, service_task_id: int, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, action: AmendmentAction, user_id: int):
#     try:
#         print(f"Starting amend_business_place_data for customer_id: {customer_id}, user_id: {user_id}, action: {action}")

#         original_business_place = None
#         original_business_place_id = None

#         # Step 1: Check if service_task_id is present
#         print(f"Checking for existing task with customer_id: {customer_id} and service_task_id: {service_task_id}")
#         existing_task = db.query(CustomerBusinessPlace).filter_by(
#             customer_id=customer_id,
#             service_task_id=service_task_id
#         ).first()

#         if existing_task:
#             print(f"Task already started for customer_id: {customer_id} and service_task_id: {service_task_id}")

#             # Log the ID before any updates
#             original_business_place_id = existing_task.amended_parent_id or existing_task.id
#             print(f"Original business place ID before update: {original_business_place_id}")

#             if existing_task.effective_from_date:
#                 # Duplicate the existing task to a new record
#                 print("Existing task has an effective_from_date. Duplicating to create new record.")
#                 business_place_data = CustomerBusinessPlaceAmendmentSchema.from_orm(existing_task)
#                 new_business_place = CustomerBusinessPlace(
#                     customer_id=existing_task.customer_id,
#                     **business_place_data.dict(exclude_unset=True)
#                 )

#                 # Set effective dates to NULL and update status
#                 print("Setting effective dates to NULL and updating status.")
#                 new_business_place.effective_from_date = None
#                 new_business_place.effective_to_date = None
#                 new_business_place.amended_parent_id = existing_task.id
             
#                 new_business_place.is_amendment = 'yes'
#                 new_business_place.amendment_date = datetime.now()
#                 new_business_place.amendment_reason = amendment_details.business_place[0].amendment_reason or "Not provided"
#                 new_business_place.amendment_status = "CREATED"
#                 new_business_place.amendment_action = "EDITED"
#                 new_business_place.service_task_id = service_task_id

#                 # Apply amendments
#                 for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
#                     if hasattr(new_business_place, key):
#                         setattr(new_business_place, key, value)

#                 # Add to the session and commit
#                 db.add(new_business_place)
#                 db.commit()
#                 db.refresh(new_business_place)

#                 print(f"New business place created with ID: {new_business_place.id}")

#             else:
#                 # Update the existing task directly
#                 print("No effective_from_date found. Updating the existing task.")
#                 new_business_place = existing_task
#                 for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
#                     if hasattr(new_business_place, key):
#                         setattr(new_business_place, key, value)

#                 new_business_place.amendment_date = datetime.now()
#                 new_business_place.amendment_reason = amendment_details.business_place[0].amendment_reason or "Not provided"
#                 new_business_place.amendment_status = "CREATED"
#                 new_business_place.amendment_action = "EDITED"
#                 new_business_place.service_task_id = service_task_id

#                 db.commit()
#                 db.refresh(new_business_place)

#                 print(f"Existing business place updated with ID: {new_business_place.id}")

#         else:
#             # Fetch active business place with is_principal_place=no
#             print("No existing task found. Fetching active business place with is_principal_place='no'.")
#             current_date = datetime.now().date()
#             original_business_place = db.query(CustomerBusinessPlace).filter(
#                 CustomerBusinessPlace.customer_id == customer_id,
#                 CustomerBusinessPlace.effective_from_date <= current_date,
#                 CustomerBusinessPlace.is_principal_place == 'yes',
#                 ((CustomerBusinessPlace.effective_to_date.is_(None)) | 
#                  (CustomerBusinessPlace.effective_to_date >= current_date))
#             ).first()

#             if not original_business_place:
#                 print(f"No active business place found for customer_id: {customer_id}")
#                 return {"success": False, "message": "Active business place not found"}

#             original_business_place_id = original_business_place.id
#             print(f"Fetched original business place ID: {original_business_place_id}")

#             # Step 2: Duplicate and create new business place
#             print("Duplicating original business place to create a new one.")
#             business_place_data = CustomerBusinessPlaceAmendmentSchema.from_orm(original_business_place)
#             print(f"Business place data from ORM: {business_place_data}")

#             new_business_place = CustomerBusinessPlace(
#                 customer_id=original_business_place.customer_id,
#                 **business_place_data.dict(exclude_unset=True)
#             )

#             # Setting effective dates and amendment info
#             print("Setting effective dates and amendment information.")
#             new_business_place.effective_from_date = None
#             new_business_place.effective_to_date = None
#             new_business_place.amended_parent_id = original_business_place.id
#             new_business_place.is_amendment = 'yes'
#             new_business_place.amendment_date = datetime.now()
#             new_business_place.amendment_reason = amendment_details.business_place[0].amendment_reason or "Not provided"
#             new_business_place.amendment_status = "CREATED"
#             new_business_place.amendment_action = "EDITED"
#             new_business_place.service_task_id = service_task_id

#             # Apply amendments
#             for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
#                 if hasattr(new_business_place, key):
#                     setattr(new_business_place, key, value)

#             db.add(new_business_place)
#             db.commit()
#             db.refresh(new_business_place)

#             print(f"New business place created with ID: {new_business_place.id}")

#         # Step 3: Fetch and handle customer_business_place_activity using original_business_place_id
#         print(f"Using original business place ID for fetching activities: {original_business_place_id}")
#         current_activity_ids = {nature.business_activity_id for nature in amendment_details.nature_of_business}
#         print(f"Current activity IDs from amendment details: {current_activity_ids}")

#         # Fetch existing activities for the original business place
#         existing_activities = db.query(CustomerBusinessPlaceActivity).filter_by(
#             business_place_id=original_business_place_id,
#             customer_id=customer_id
#         ).all()
#         print(f"Fetched existing activities: {[activity.id for activity in existing_activities]}")

#         existing_activity_ids = {activity.business_activity_id for activity in existing_activities}
#         print(f"Existing activity IDs: {existing_activity_ids}")

#         duplicated_activities = []
        
#         # Case 1 and Case 2: Duplicate existing activities
#         for activity in existing_activities:
#             new_entry = CustomerBusinessPlaceActivity(
#                 customer_id=activity.customer_id,
#                 business_place_id=new_business_place.id,
#                 business_activity_id=activity.business_activity_id,
#                 amended_parent_id=activity.id,
#                 is_amendment='yes',
#                 amendment_action="EDITED",  # Set to EDITED when duplicating
#                 amendment_date=datetime.now(),
#                 amendment_reason=activity.amendment_reason,
#                 service_task_id=service_task_id
#             )
#             db.add(new_entry)
#             db.commit()
#             db.refresh(new_entry)
#             duplicated_activities.append(new_entry)
#             print(f"Duplicated entry with new ID: {new_entry.id}")

#         # Case 3: Add new activities from the amendment details
#         for nature in amendment_details.nature_of_business:
#             if nature.business_activity_id not in existing_activity_ids:
#                 new_entry = CustomerBusinessPlaceActivity(
#                     customer_id=customer_id,
#                     business_place_id=new_business_place.id,
#                     business_activity_id=nature.business_activity_id,
#                     amended_parent_id=None,
#                     is_amendment='yes',
#                     amendment_action="ADDED",  # Set to ADDED for new activities
#                     amendment_date=nature.amendment_date or datetime.now(),
#                     amendment_reason=nature.amendment_reason or "Not provided",
#                     service_task_id=service_task_id
#                 )
#                 db.add(new_entry)
#                 db.commit()
#                 db.refresh(new_entry)
#                 new_entry.amended_parent_id = new_entry.id  # Set amended_parent_id to the new entry's ID
#                 db.commit()
#                 db.refresh(new_entry)
#                 duplicated_activities.append(new_entry)
#                 print(f"Added new entry for business_activity_id: {nature.business_activity_id} with amended_parent_id: {new_entry.amended_parent_id}")

#         # Case 4: Mark activities as deleted if not present in the amendment details
#         for activity in existing_activities:
#             print("1111##############################")
#             if activity.business_activity_id not in current_activity_ids:
#                 if activity.id == activity.amended_parent_id:
#                     activity.is_deleted = 'yes'
#                     db.commit()
#                     print(f"Marked activity with ID: {activity.id} as deleted (is_deleted set to 'yes')")

#                 else:
#                     print("2222#################################")
#                     activity.amendment_action = "DELETED"
#                     db.commit()
#                     print(f"Marked activity with ID: {activity.id} as deleted (amendment_action set to 'DELETED')")

#             else:
#                 print(f"Activity with ID: {activity.id} is still present in the amendment details, not marked for deletion.")        
#         db.commit()
               
#         print(f"Marked activity with ID: {activity.id} as deleted")

#         return {"success": True, "id": new_business_place.id}

#     except SQLAlchemyError as e:
#         db.rollback()
#         print(f"Error occurred during amendment process: {e}")
#         return {"success": False, "message": str(e)}


# def amend_business_place_data(db: Session, customer_id: int, service_task_id: int, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, action: AmendmentAction, user_id: int):
#     try:
#         print(f"Starting amend_business_place_data for customer_id: {customer_id}, user_id: {user_id}, action: {action}")

#         original_business_place = None
#         original_business_place_id = None

#         # Step 1: Check if service_task_id is present
#         print(f"Checking for existing task with customer_id: {customer_id} and service_task_id: {service_task_id}")
#         existing_task = db.query(CustomerBusinessPlace).filter_by(
#             customer_id=customer_id,
#             service_task_id=service_task_id
#         ).first()

#         if existing_task:
#             print(f"Task already started for customer_id: {customer_id} and service_task_id: {service_task_id}")

#             # Log the ID before any updates
#             original_business_place_id = existing_task.amended_parent_id or existing_task.id
#             print(f"Original business place ID before update: {original_business_place_id}")

#             if existing_task.effective_from_date:
#                 # Duplicate the existing task to a new record
#                 print("Existing task has an effective_from_date. Duplicating to create new record.")
#                 business_place_data = CustomerBusinessPlaceAmendmentSchema.from_orm(existing_task)
#                 new_business_place = CustomerBusinessPlace(
#                     customer_id=existing_task.customer_id,
#                     **business_place_data.dict(exclude_unset=True)
#                 )

#                 # Set effective dates to NULL and update status
#                 print("Setting effective dates to NULL and updating status.")
#                 new_business_place.effective_from_date = None
#                 new_business_place.effective_to_date = None
#                 new_business_place.amended_parent_id = existing_task.id
             
#                 new_business_place.is_amendment = 'yes'
#                 new_business_place.amendment_date = datetime.now()
#                 new_business_place.amendment_reason = amendment_details.business_place[0].amendment_reason or "Not provided"
#                 new_business_place.amendment_status = "CREATED"
#                 new_business_place.amendment_action = "EDITED"
#                 new_business_place.service_task_id = service_task_id

#                 # Apply amendments
#                 for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
#                     if hasattr(new_business_place, key):
#                         setattr(new_business_place, key, value)

#                 # Add to the session and commit
#                 db.add(new_business_place)
#                 db.commit()
#                 db.refresh(new_business_place)

#                 print(f"New business place created with ID: {new_business_place.id}")

#             else:
#                 # Update the existing task directly
#                 print("No effective_from_date found. Updating the existing task.")
#                 new_business_place = existing_task
#                 for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
#                     if hasattr(new_business_place, key):
#                         setattr(new_business_place, key, value)

#                 new_business_place.amendment_date = datetime.now()
#                 new_business_place.amendment_reason = amendment_details.business_place[0].amendment_reason or "Not provided"
#                 new_business_place.amendment_status = "CREATED"
#                 new_business_place.amendment_action = "EDITED"
#                 new_business_place.service_task_id = service_task_id

#                 db.commit()
#                 db.refresh(new_business_place)

#                 print(f"Existing business place updated with ID: {new_business_place.id}")

#         else:
#             # Fetch active business place with is_principal_place=no
#             print("No existing task found. Fetching active business place with is_principal_place='no'.")
#             current_date = datetime.now().date()
#             original_business_place = db.query(CustomerBusinessPlace).filter(
#                 CustomerBusinessPlace.customer_id == customer_id,
#                 CustomerBusinessPlace.effective_from_date <= current_date,
#                 CustomerBusinessPlace.is_principal_place == 'yes',
#                 ((CustomerBusinessPlace.effective_to_date.is_(None)) | 
#                  (CustomerBusinessPlace.effective_to_date >= current_date))
#             ).first()

#             if not original_business_place:
#                 print(f"No active business place found for customer_id: {customer_id}")
#                 return {"success": False, "message": "Active business place not found"}

#             original_business_place_id = original_business_place.id
#             print(f"Fetched original business place ID: {original_business_place_id}")

#             # Step 2: Duplicate and create new business place
#             print("Duplicating original business place to create a new one.")
#             business_place_data = CustomerBusinessPlaceAmendmentSchema.from_orm(original_business_place)
#             print(f"Business place data from ORM: {business_place_data}")

#             new_business_place = CustomerBusinessPlace(
#                 customer_id=original_business_place.customer_id,
#                 **business_place_data.dict(exclude_unset=True)
#             )

#             # Setting effective dates and amendment info
#             print("Setting effective dates and amendment information.")
#             new_business_place.effective_from_date = None
#             new_business_place.effective_to_date = None
#             new_business_place.amended_parent_id = original_business_place.id
#             new_business_place.is_amendment = 'yes'
#             new_business_place.amendment_date = datetime.now()
#             new_business_place.amendment_reason = amendment_details.business_place[0].amendment_reason or "Not provided"
#             new_business_place.amendment_status = "CREATED"
#             new_business_place.amendment_action = "EDITED"
#             new_business_place.service_task_id = service_task_id

#             # Apply amendments
#             for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
#                 if hasattr(new_business_place, key):
#                     setattr(new_business_place, key, value)

#             db.add(new_business_place)
#             db.commit()
#             db.refresh(new_business_place)

#             print(f"New business place created with ID: {new_business_place.id}")

#         # Step 3: Fetch and handle customer_business_place_activity using original_business_place_id
#         print(f"Using original business place ID for fetching activities: {original_business_place_id}")
#         current_activity_ids = {nature.business_activity_id for nature in amendment_details.nature_of_business}
#         print(f"Current activity IDs from amendment details: {current_activity_ids}")

#         # Fetch existing activities for the original business place
#         existing_activities = db.query(CustomerBusinessPlaceActivity).filter_by(
#             business_place_id=original_business_place_id,
#             customer_id=customer_id
#         ).all()
#         print(f"Fetched existing activities: {[activity.id for activity in existing_activities]}")

#         existing_activity_ids = {activity.business_activity_id for activity in existing_activities}
#         print(f"Existing activity IDs: {existing_activity_ids}")

#         duplicated_activities = []
        
#         # Case 1 and Case 2: Duplicate existing activities
#         for activity in existing_activities:
#             new_entry = CustomerBusinessPlaceActivity(
#                 customer_id=activity.customer_id,
#                 business_place_id=new_business_place.id,
#                 business_activity_id=activity.business_activity_id,
#                 amended_parent_id=activity.id,
#                 is_amendment='yes',
#                 amendment_action="EDITED",  # Set to EDITED when duplicating
#                 amendment_date=datetime.now(),
#                 amendment_reason=activity.amendment_reason,
#                 service_task_id=service_task_id
#             )
#             db.add(new_entry)
#             db.commit()
#             db.refresh(new_entry)
#             duplicated_activities.append(new_entry)
#             print(f"Duplicated entry with new ID: {new_entry.id}")

#         # Case 3: Add new activities from the amendment details
#         for nature in amendment_details.nature_of_business:
#             if nature.business_activity_id not in existing_activity_ids:
#                 new_entry = CustomerBusinessPlaceActivity(
#                     customer_id=customer_id,
#                     business_place_id=new_business_place.id,
#                     business_activity_id=nature.business_activity_id,
#                     amended_parent_id=None,
#                     is_amendment='yes',
#                     amendment_action="ADDED",  # Set to ADDED for new activities
#                     amendment_date=nature.amendment_date or datetime.now(),
#                     amendment_reason=nature.amendment_reason or "Not provided",
#                     service_task_id=service_task_id
#                 )
#                 db.add(new_entry)
#                 db.commit()
#                 db.refresh(new_entry)
#                 new_entry.amended_parent_id = new_entry.id  # Set amended_parent_id to the new entry's ID
#                 db.commit()
#                 db.refresh(new_entry)
#                 duplicated_activities.append(new_entry)
#                 print(f"Added new entry for business_activity_id: {nature.business_activity_id} with amended_parent_id: {new_entry.amended_parent_id}")

#         # Case 4: Mark activities as deleted if not present in the amendment details
       

       
       
#         # Case 4: Mark activities as deleted if not present in the amendment details
#         for activity in existing_activities:
#             print("##############################")
            
#             print(f"Checking activity with ID: {activity.id}, amended_parent_id: {activity.amended_parent_id}, business_activity_id: {activity.business_activity_id}")

#             # Case when activity should be deleted
#             if activity.business_activity_id not in current_activity_ids:
#                 print(f"Activity with ID {activity.id} (business_activity_id: {activity.business_activity_id}) is not in current_activity_ids and should be marked for deletion.")
                
#                 # If it's a duplicated/amended activity, mark it as deleted
#                 if activity.id != activity.amended_parent_id:
#                     print("*********************************")
#                     activity.amendment_action = "DELETED"
#                     print(f"Marked amended activity with ID: {activity.id} as deleted (amendment_action set to 'DELETED')")

#                 # If it's the original activity (amended parent), mark it as deleted
#                 elif activity.id == activity.amended_parent_id and activity.is_amendment == 'yes':
#                     print("222222222222222222222222222222")
#                     activity.is_deleted = 'yes'
#                     print(f"Marked original activity with ID: {activity.id} as deleted (is_deleted set to 'yes')")
#             else:
#                 # Activity is still present in the amendment details, not marked for deletion
#                 print(f"Activity with ID: {activity.id} is still present in the amendment details, not marked for deletion.")
            
#             db.commit()

#         print("Successfully marked activities for deletion where needed.")
#         return {"success": True, "id": new_business_place.id}

#     except SQLAlchemyError as e:
#         db.rollback()
#         print(f"Error occurred during amendment process: {e}")
#         return {"success": False, "message": str(e)}
    
def amend_business_place_data(
    db: Session, customer_id: int, service_task_id: int, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, action: AmendmentAction, user_id: int
):
    try:
        print(f"Processing amendment for customer_id: {customer_id}, user_id: {user_id}, action: {action}")

        # Step 1: Validate and initialize
        existing_task = db.query(CustomerBusinessPlace).filter_by(
            customer_id=customer_id, service_task_id=service_task_id
        ).first()

        if existing_task:
            print(f"Found existing task with ID: {existing_task.id}")
            original_business_place_id = existing_task.amended_parent_id or existing_task.id
            print(f"original_business_place_id: {original_business_place_id}")

            if existing_task.effective_from_date:
                print("Existing task has an effective_from_date. Checking for changes...")

                # Check if there are changes between the existing task and amendment details
                has_changes = any(
                    getattr(existing_task, key) != value
                    for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items()
                )

                if has_changes:
                    print("Changes detected. Creating a duplicate record...")
                    new_business_place = create_duplicate_business_place(
                        db, existing_task, amendment_details, service_task_id
                    )
                else:
                    print("No changes detected. Skipping duplication and keeping the existing record.")
                    new_business_place = existing_task
            else:
                print("Existing task has no effective_from_date. Updating the existing record.")
                update_business_place(existing_task, amendment_details, service_task_id)
                new_business_place = existing_task
        else:
            print("No task found. Fetching original business place.")
            original_business_place = get_active_business_place(db, customer_id)
            if not original_business_place:
                return {"success": False, "message": "Active business place not found"}

            # Create a duplicate of the original business place if no existing task
            new_business_place = create_duplicate_business_place(db, original_business_place, amendment_details, service_task_id)
            original_business_place_id = original_business_place.id

        # Step 2: Handle business activities
        handle_business_activities(
            db, customer_id, original_business_place_id, new_business_place.id, amendment_details, service_task_id
        )

        print("Amendment process completed successfully.")
        return {"success": True, "id": new_business_place.id}

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error during amendment: {e}")
        return {"success": False, "message": str(e)}

# Helper functions
def get_active_business_place(db: Session, customer_id: int) -> CustomerBusinessPlace:
    current_date = datetime.now().date()
    return db.query(CustomerBusinessPlace).filter(
        CustomerBusinessPlace.customer_id == customer_id,
        CustomerBusinessPlace.effective_from_date <= current_date,
        CustomerBusinessPlace.is_principal_place == 'yes',
        ((CustomerBusinessPlace.effective_to_date.is_(None)) |
         (CustomerBusinessPlace.effective_to_date >= current_date))
    ).first()




def update_business_place(existing_place: CustomerBusinessPlace, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, service_task_id: int):
    for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
        setattr(existing_place, key, value)
    existing_place.amendment_date = datetime.now()
    existing_place.amendment_reason = amendment_details.business_place[0].amendment_reason or "Not provided"
    existing_place.amendment_status = "CREATED"
    existing_place.amendment_action = "EDITED"
    existing_place.service_task_id = service_task_id


def create_duplicate_business_place(db: Session, original_place: CustomerBusinessPlace, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, service_task_id: int) -> CustomerBusinessPlace:
    # Convert the original place to a schema
    business_place_data = CustomerBusinessPlaceAmendmentSchema.from_orm(original_place)

    # Prepare the data for the new business place
    new_place_data = business_place_data.dict(exclude_unset=True)

    # Remove 'amendment_date' and 'amendment_reason' from new_place_data to avoid conflicts
    new_place_data.pop('amendment_date', None)
    new_place_data.pop('amendment_reason', None)

    # Create a new business place
    new_place = CustomerBusinessPlace(
        customer_id=original_place.customer_id,
        **new_place_data,  # Use the remaining attributes from the original place
        effective_from_date=None,
        effective_to_date=None,
        amended_parent_id=original_place.id,
        is_amendment='yes',
        amendment_date=datetime.now(),  # Set the amendment date explicitly
        amendment_reason=amendment_details.business_place[0].amendment_reason or "Not provided",
        amendment_status="CREATED",
        amendment_action="EDITED",
        service_task_id=service_task_id
    )

    # Set additional fields from amendment details
    for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items():
        setattr(new_place, key, value)

    # Commit the new business place to the database
    db.add(new_place)
    db.commit()
    db.refresh(new_place)

    return new_place


def mark_activities_as_deleted(db: Session, existing_activities: List[CustomerBusinessPlaceActivity], current_activity_ids: Set[int]) -> None:
    for activity in existing_activities:
        if activity.business_activity_id not in current_activity_ids:
            if activity.id != activity.amended_parent_id:
                activity.amendment_action = "DELETED"
            elif activity.id == activity.amended_parent_id and activity.is_amendment == 'yes':
                activity.is_deleted = 'yes'
            db.commit()



def handle_business_activities(db: Session, customer_id: int, original_place_id: int, new_place_id: int, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, service_task_id: int):
    current_activity_ids = {nature.business_activity_id for nature in amendment_details.nature_of_business}

    # Fetch existing activities
    existing_activities = get_existing_activities(db, customer_id, original_place_id)
    existing_activity_ids = {activity.business_activity_id for activity in existing_activities}

    # Duplicate existing activities
    duplicated_activities = duplicate_existing_activities(db, existing_activities, new_place_id, service_task_id)

    # Add new activities
    add_new_activities(db, customer_id, new_place_id, amendment_details, existing_activity_ids, service_task_id)

    # Mark duplicated activities as deleted
    mark_activities_as_deleted(db, duplicated_activities, current_activity_ids)

def get_existing_activities(db: Session, customer_id: int, original_place_id: int) -> List[CustomerBusinessPlaceActivity]:
    print(f"Fetching existing activities for customer_id: {customer_id}, original_place_id: {original_place_id}")
    existing_activities = db.query(CustomerBusinessPlaceActivity).filter_by(
        business_place_id=original_place_id, customer_id=customer_id
    ).all()
    print(f"Fetched existing activities: {existing_activities}")
    return existing_activities

def duplicate_existing_activities(db: Session, existing_activities: List[CustomerBusinessPlaceActivity], new_place_id: int, service_task_id: int) -> List[CustomerBusinessPlaceActivity]:
    duplicated_activities = []
    for activity in existing_activities:
        print(f"Duplicating activity with ID: {activity.id}, business_activity_id: {activity.business_activity_id}")
        
        new_entry = CustomerBusinessPlaceActivity(
            customer_id=activity.customer_id,
            business_place_id=new_place_id,
            business_activity_id=activity.business_activity_id,
            amended_parent_id=activity.id,
            is_amendment='yes',
            amendment_action="EDITED",
            amendment_date=datetime.now(),
            amendment_reason=activity.amendment_reason,
            service_task_id=service_task_id
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        print(f"Created new duplicated entry with ID: {new_entry.id}, business_activity_id: {new_entry.business_activity_id}")
        duplicated_activities.append(new_entry)
    
    return duplicated_activities

def add_new_activities(db: Session, customer_id: int, new_place_id: int, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, existing_activity_ids: Set[int], service_task_id: int) -> None:
    for nature in amendment_details.nature_of_business:
        if nature.business_activity_id not in existing_activity_ids:
            print(f"Adding new activity with business_activity_id: {nature.business_activity_id}")
            
            new_entry = CustomerBusinessPlaceActivity(
                customer_id=customer_id,
                business_place_id=new_place_id,
                business_activity_id=nature.business_activity_id,
                is_amendment='yes',
                amendment_action="ADDED",
                amendment_date=datetime.now(),
                amendment_reason=nature.amendment_reason or "Not provided",
                service_task_id=service_task_id
            )
            
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)

            # Set amended_parent_id to the new entry's ID
            new_entry.amended_parent_id = new_entry.id
            db.commit()
            db.refresh(new_entry)
            
            print(f"Added new entry with ID: {new_entry.id}, business_activity_id: {new_entry.business_activity_id}, amended_parent_id: {new_entry.amended_parent_id}")

def mark_activities_as_deleted(db: Session, duplicated_activities: List[CustomerBusinessPlaceActivity], current_activity_ids: Set[int]) -> None:
    for activity in duplicated_activities:
        print("#####################")
        print(f"Checking duplicated activity with ID: {activity.id}, business_activity_id: {activity.business_activity_id}, amended_parent_id: {activity.amended_parent_id}")

        if activity.business_activity_id not in current_activity_ids:
            print(f"Activity with business_activity_id: {activity.business_activity_id} not in current_activity_ids. Marking for deletion.")

            if activity.id == activity.amended_parent_id:
                # Mark the original activity as deleted
                activity.is_deleted = 'yes'
                print(f"Marked original activity with ID: {activity.id} as deleted (is_deleted set to 'yes')")
            elif activity.id != activity.amended_parent_id:
                print("$$$$$$$$$$$$$$$$$$$$$$$$")
                # Mark the duplicated/amended activity with amendment_action = DELETED
                activity.amendment_action = "DELETED"
                print(f"Marked duplicated activity with ID: {activity.id} as deleted (amendment_action set to 'DELETED')")
            
            db.commit()
        else:
            print(f"Activity with business_activity_id: {activity.business_activity_id} is present in current_activity_ids. Not marking for deletion.")

#----------------------------------------------------------------------------------------------


# def fetch_combined_data(db: Session, customer_id: Optional[int] = None) -> List[CombinedSchema]:
#     try:
#         print(f"Fetching combined data for customer_id: {customer_id}")

#         # Fetch amended business place data along with customer, state, district, and city details
#         print("Fetching amended business place data with customer, state, district, and city details")
#         amended_business_places = (
#             db.query(
#                 CustomerBusinessPlace,
#                 CustomerMaster.customer_name,
#                 CustomerMaster.legal_name,
#                 StateDB.state_name,
#                 DistrictDB.district_name,
#                 CityDB.city_name
#             )
#             .join(CustomerMaster, CustomerBusinessPlace.customer_id == CustomerMaster.id)
#             .join(StateDB, CustomerBusinessPlace.state_id == StateDB.id)
#             .join(DistrictDB, CustomerBusinessPlace.district_id == DistrictDB.id)
#             .join(CityDB, CustomerBusinessPlace.city_id == CityDB.id)
#             .filter(
#                 CustomerBusinessPlace.customer_id == customer_id,
#                 CustomerBusinessPlace.is_amendment == 'yes'
#             )
#             .all()
#         )
#         print(f"Amended business places fetched: {amended_business_places}")

#         if not amended_business_places:
#             print("No amended business places found")
#             return []

#         # Extract original business place IDs from the amended records using a traditional loop
#         original_business_place_ids = []
#         amended_business_place_ids = []
#         for bp, customer_name, legal_name, state_name, district_name, city_name in amended_business_places:
#             if bp.amended_parent_id:
#                 original_business_place_ids.append(bp.amended_parent_id)
#             amended_business_place_ids.append(bp.id)  # Also gather amended business place ids here
#         print(f"Original business place IDs: {original_business_place_ids}")
#         print(f"Amended business place IDs: {amended_business_place_ids}")

#         # Fetch activities for both original and amended business places
#         print("Fetching activities for business places")
#         activities = (
#             db.query(
#                 CustomerBusinessPlaceActivity,
#                 BusinessActivity.gst_business_activity_code,
#                 BusinessActivity.business_activity
#             )
#             .join(BusinessActivity, CustomerBusinessPlaceActivity.business_activity_id == BusinessActivity.id)
#             .filter(
#                 CustomerBusinessPlaceActivity.business_place_id.in_(original_business_place_ids + amended_business_place_ids),
#                 CustomerBusinessPlaceActivity.is_amendment == 'yes'
#             )
#             .all()
#         )
#         print(f"Activities fetched: {activities}")

#         # Combine data
#         print("Combining business place and activity data")
#         combined_data = []
#         for business_place, customer_name, legal_name, state_name, district_name, city_name in amended_business_places:
#             business_place_data = CustomerBusinessPlaceSchemaForGet.from_orm(business_place).dict()
#             business_place_data['customer_name'] = customer_name
#             business_place_data['legal_name'] = legal_name
#             business_place_data['state_name'] = state_name
#             business_place_data['district_name'] = district_name
#             business_place_data['city_name'] = city_name

#             activity_data = [
#                 {
#                     **CustomerBusinessPlaceActivitySchemaForGet.from_orm(activity).dict(),
#                     "gst_business_activity_code": gst_business_activity_code,
#                     "business_activity": business_activity
#                 }
#                 for activity, gst_business_activity_code, business_activity in activities
#                 if activity.business_place_id in (business_place.id, business_place.amended_parent_id)
#             ]

#             combined_entry = {
#                 "business_place": business_place_data,
#                 "activity": activity_data
#             }
#             combined_data.append(combined_entry)
#             print(f"Combined entry added: {combined_entry}")

#         print("Combined data fetching complete")
#         return combined_data

#     except SQLAlchemyError as e:
#         print(f"SQLAlchemy error: {str(e)}")
#         raise

def fetch_combined_data(db: Session, customer_id: Optional[int] = None, service_task_id: Optional[int] = None) -> List[CombinedSchema]:
    try:
        print(f"Fetching combined data for customer_id: {customer_id}, service_task_id: {service_task_id}")

        # Fetch amended business place data along with customer, state, district, and city details
        print("Fetching amended business place data with customer, state, district, and city details")
        query = (
            db.query(
                CustomerBusinessPlace,
                CustomerMaster.customer_name,
                CustomerMaster.legal_name,
                StateDB.state_name,
                DistrictDB.district_name,
                CityDB.city_name
            )
            .join(CustomerMaster, CustomerBusinessPlace.customer_id == CustomerMaster.id)
            .join(StateDB, CustomerBusinessPlace.state_id == StateDB.id)
            .join(DistrictDB, CustomerBusinessPlace.district_id == DistrictDB.id)
            .join(CityDB, CustomerBusinessPlace.city_id == CityDB.id)
            .filter(CustomerBusinessPlace.is_amendment == 'yes')
        )
        
        if customer_id is not None:
            query = query.filter(CustomerBusinessPlace.customer_id == customer_id)
        
        if service_task_id is not None:
            query = query.filter(CustomerBusinessPlace.service_task_id == service_task_id)
        
        amended_business_places = query.all()

        print(f"Amended business places fetched: {amended_business_places}")

        if not amended_business_places:
            print("No amended business places found")
            return []

        # Extract original business place IDs from the amended records using a traditional loop
        original_business_place_ids = []
        amended_business_place_ids = []
        for bp, customer_name, legal_name, state_name, district_name, city_name in amended_business_places:
            if bp.amended_parent_id:
                original_business_place_ids.append(bp.amended_parent_id)
            amended_business_place_ids.append(bp.id)  # Also gather amended business place ids here
        print(f"Original business place IDs: {original_business_place_ids}")
        print(f"Amended business place IDs: {amended_business_place_ids}")

        # Fetch activities for both original and amended business places
        print("Fetching activities for business places")
        activity_query = (
            db.query(
                CustomerBusinessPlaceActivity,
                BusinessActivity.gst_business_activity_code,
                BusinessActivity.business_activity
            )
            .join(BusinessActivity, CustomerBusinessPlaceActivity.business_activity_id == BusinessActivity.id)
            .filter(
                CustomerBusinessPlaceActivity.business_place_id.in_(original_business_place_ids + amended_business_place_ids),
                CustomerBusinessPlaceActivity.is_amendment == 'yes'
            )
        )

        if service_task_id is not None:
            activity_query = activity_query.filter(CustomerBusinessPlaceActivity.service_task_id == service_task_id)

        activities = activity_query.all()
        print(f"Activities fetched: {activities}")

        # Combine data
        print("Combining business place and activity data")
        combined_data = []
        for business_place, customer_name, legal_name, state_name, district_name, city_name in amended_business_places:
            business_place_data = CustomerBusinessPlaceSchemaForGet.from_orm(business_place).dict()
            business_place_data['customer_name'] = customer_name
            business_place_data['legal_name'] = legal_name
            business_place_data['state_name'] = state_name
            business_place_data['district_name'] = district_name
            business_place_data['city_name'] = city_name

            activity_data = [
                {
                    **CustomerBusinessPlaceActivitySchemaForGet.from_orm(activity).dict(),
                    "gst_business_activity_code": gst_business_activity_code,
                    "business_activity": business_activity
                }
                for activity, gst_business_activity_code, business_activity in activities
                if activity.business_place_id in (business_place.id, business_place.amended_parent_id)
            ]

            combined_entry = {
                "business_place": business_place_data,
                "activity": activity_data
            }
            combined_data.append(combined_entry)
            print(f"Combined entry added: {combined_entry}")

        print("Combined data fetching complete")
        return combined_data

    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        raise

#------------------------------------------------------------------------------------------------------------

# def save_additional_business_places_and_activities(db: Session, customer_id: int, service_task_id: int, amendment_details: dict, action: AmendmentAction, user_id: int):
#     try:
#         parsed_data = amendment_details
#         business_place_ids = []

#         if action == AmendmentAction.ADDED:
#             # Case: Adding new business places and activities
#             print("Adding new business places and activities")
#             for business_place_data in parsed_data["business_place"]:
#                 print(f"Processing business place data: {business_place_data}")

#                 # Extract and remove nature_of_business to handle it separately
#                 nature_of_business_data = business_place_data.pop("nature_of_business", [])

#                 # Check if service_task_id already exists for this customer in CustomerBusinessPlace
#                 existing_business_place = db.query(CustomerBusinessPlace).filter_by(
#                     customer_id=customer_id,
#                     service_task_id=service_task_id,
#                     pin_code=business_place_data["pin_code"],
#                     country_id=business_place_data["country_id"],
#                     state_id=business_place_data["state_id"],
#                     district_id=business_place_data["district_id"],
#                     taluk_id=business_place_data["taluk_id"],
#                     city_id=business_place_data["city_id"]
#                 ).first()

#                 if existing_business_place:
#                     print(f"Using existing business place with ID: {existing_business_place.id}")
#                     new_business_place = existing_business_place
#                 else:
#                     print(f"Creating new business place for service_task_id: {service_task_id}")
#                     new_business_place = CustomerBusinessPlace(
#                         **business_place_data,
#                         customer_id=customer_id,
#                         service_task_id=service_task_id,
#                         is_principal_place="no",
#                         is_amendment="yes",
#                         amendment_action="ADDED",
#                         amendment_status="CREATED",
#                         created_by=user_id,
#                         created_on=datetime.now()
#                     )
#                     db.add(new_business_place)
#                     db.commit()
#                     db.refresh(new_business_place)

#                     # Set amended_parent_id to the same value as id
#                     new_business_place.amended_parent_id = new_business_place.id
#                     db.commit()
#                     db.refresh(new_business_place)

#                 business_place_ids.append(new_business_place.id)
#                 print(f"Business place processed with ID: {new_business_place.id}")

#                 # Saving nature of business for the current business place
#                 for activity_data in nature_of_business_data:
#                     print(f"Processing activity data: {activity_data} for business_place_id: {new_business_place.id}")

#                     # Check if service_task_id already exists for this customer and business activity
#                     existing_activity = db.query(CustomerBusinessPlaceActivity).filter_by(
#                         customer_id=customer_id,
#                         service_task_id=service_task_id,
#                         business_activity_id=activity_data["business_activity_id"]
#                     ).first()

#                     if existing_activity:
#                         print(f"Using existing activity with ID: {existing_activity.id}")
#                         new_activity = existing_activity
#                     else:
#                         print(f"Creating new activity for service_task_id: {service_task_id}")
#                         new_activity = CustomerBusinessPlaceActivity(
#                             **activity_data,
#                             customer_id=customer_id,
#                             business_place_id=new_business_place.id,
#                             service_task_id=service_task_id,  # Ensure service_task_id is set
#                             is_amendment="yes",
#                             amendment_action="ADDED",
#                             amendment_status="CREATED",
#                             created_by=user_id,
#                             created_on=datetime.now()
#                         )
#                         db.add(new_activity)
#                         db.commit()
#                         db.refresh(new_activity)

#                         # Set amended_parent_id to the same value as id for the new activity
#                         new_activity.amended_parent_id = new_activity.id
#                         db.commit()
#                         db.refresh(new_activity)

#                     print(f"Business activity processed with ID: {new_activity.id}")


#         elif action == AmendmentAction.EDITED:
#             # Case: Editing existing business places and activities
#             print("Editing existing business places and activities")

#             for business_place_data in parsed_data["business_place"]:
#                 print(f"Processing business place data for editing: {business_place_data}")

#                 # Extract and remove nature_of_business to handle it separately
#                 nature_of_business_data = business_place_data.pop("nature_of_business", [])

#                 existing_place = db.query(CustomerBusinessPlace).filter_by(
#                     customer_id=customer_id,
#                     service_task_id=service_task_id,
#                     pin_code=business_place_data["pin_code"],
#                     country_id=business_place_data["country_id"],
#                     state_id=business_place_data["state_id"],
#                     district_id=business_place_data["district_id"],
#                     taluk_id=business_place_data["taluk_id"],
#                     city_id=business_place_data["city_id"]
#                 ).first()
#                 print("Existing Place:", existing_place)

#                 if existing_place:
#                     print(f"Found existing place: {existing_place.id}")
#                     # Duplicate the existing place with is_amendment = 'yes'
#                     amended_place = CustomerBusinessPlace(
#                         **business_place_data,
#                         customer_id=customer_id,
#                         service_task_id=service_task_id,
#                         amended_parent_id=existing_place.id,  # Set amended_parent_id to the ID of the place being amended
#                         is_principal_place="no",
#                         is_amendment="yes",
#                         amendment_action="EDITED",
#                         created_by=user_id,
#                         created_on=datetime.now()
#                     )
#                     db.add(amended_place)
#                     db.commit()
#                     db.refresh(amended_place)

#                     business_place_ids.append(amended_place.id)
#                     print(f"Amended business place saved: {amended_place.id}")

#                     # Fetch and duplicate existing activities for the amended place
#                     existing_activities = db.query(CustomerBusinessPlaceActivity).filter_by(
#                         business_place_id=existing_place.id
#                     ).all()
#                     print(f"Found existing activities: {existing_activities}")
                    
#                     duplicated_activities = []
#                     for activity in existing_activities:
#                         # Duplicate the existing activity
#                         activity_dict = activity.__dict__.copy()
#                         activity_dict.pop('_sa_instance_state', None)  # Remove SQLAlchemy state
#                         activity_dict.pop('id', None)  # Remove ID to avoid conflicts

#                         # Ensure all required fields are set
#                         activity_dict['business_place_id'] = amended_place.id  # Update to new business place ID
#                         activity_dict['is_amendment'] = 'yes'
#                         activity_dict['amendment_action'] = 'EDITED'
#                         activity_dict['created_by'] = user_id  # Ensure created_by is set correctly
#                         activity_dict['created_on'] = datetime.now()  # Ensure created_on is set correctly
#                         activity_dict['customer_id'] = customer_id  # Ensure customer_id is set correctly
#                         activity_dict['service_task_id'] = service_task_id  # Ensure service_task_id is set correctly
#                         activity_dict['amended_parent_id'] = activity.id  # Link back to the original activity

#                         # Set missing fields to default values if necessary
#                         activity_dict.setdefault('business_activity_id', activity.business_activity_id)
#                         activity_dict.setdefault('amendment_date', activity.amendment_date)
#                         activity_dict.setdefault('amendment_reason', activity.amendment_reason)
#                         activity_dict.setdefault('amendment_status', activity.amendment_status)
#                         activity_dict.setdefault('is_deleted', 'no')

#                         # Create a new duplicated activity
#                         duplicated_activity = CustomerBusinessPlaceActivity(
#                             **activity_dict
#                         )
#                         db.add(duplicated_activity)
#                         db.commit()
#                         db.refresh(duplicated_activity)

#                         duplicated_activities.append(duplicated_activity)
#                         print(f"Duplicated activity saved: {duplicated_activity.id}")

#                     # Compare duplicated activities with the amendment JSON
#                     amendment_activity_ids = {activity_data["business_activity_id"] for activity_data in nature_of_business_data}
#                     existing_activity_ids = {activity.business_activity_id for activity in duplicated_activities}

#                     # Handle activities in the JSON
#                     for activity_data in nature_of_business_data:
#                         print(f"Processing activity data: {activity_data} for amended_place_id: {amended_place.id}")

#                         if activity_data["business_activity_id"] in existing_activity_ids:
#                             # If activity exists and remains unchanged, no action needed
#                             existing_activity = db.query(CustomerBusinessPlaceActivity).filter_by(
#                                 business_place_id=amended_place.id,
#                                 business_activity_id=activity_data["business_activity_id"]
#                             ).first()
                            
#                             if existing_activity.amendment_reason == activity_data["amendment_reason"]:
#                                 print(f"Activity {existing_activity.business_activity_id} remains unchanged.")
#                                 continue
#                             else:
#                                 # Mark as EDITED if activity details have changed
#                                 existing_activity.amendment_action = 'EDITED'
#                                 existing_activity.amendment_reason = activity_data["amendment_reason"]
#                                 db.commit()
#                                 print(f"Updated activity {existing_activity.business_activity_id} to EDITED.")
#                         else:
#                             # Add new activities
#                             print(f"Adding new activity: {activity_data['business_activity_id']}")
#                             new_activity = CustomerBusinessPlaceActivity(
#                                 **activity_data,
#                                 customer_id=customer_id,
#                                 business_place_id=amended_place.id,
#                                 service_task_id=service_task_id,
#                                 is_amendment="yes",
#                                 amendment_action="ADDED",
#                                 created_by=user_id,
#                                 created_on=datetime.now()
#                             )
#                             db.add(new_activity)
#                             db.commit()
#                             db.refresh(new_activity)

#                             # Set amended_parent_id to the same value as id for the new activity
#                             new_activity.amended_parent_id = new_activity.id
#                             db.commit()
#                             db.refresh(new_activity)

#                             print(f"New business activity saved: {new_activity.id}")

#                     # Marking activities as DELETED if not in JSON
#                     for duplicated_activity in duplicated_activities:
#                         if duplicated_activity.business_activity_id not in amendment_activity_ids:
#                             print(f"Marking activity as DELETED: {duplicated_activity.id}")
#                             duplicated_activity.is_deleted = "yes"
#                             duplicated_activity.amendment_action = "DELETED"
#                             db.commit()
#                             print(f"Business activity marked as DELETED: {duplicated_activity.id}")

#         return {"success": True, "message": "Business places and activities saved successfully"}

#     except SQLAlchemyError as e:
#         db.rollback()
#         print(f"SQLAlchemy error: {str(e)}")
#         return {"success": False, "message": "Failed to save business places and activities"}

#     except ValueError as e:
#         print(f"Validation error: {str(e)}")
#         return {"success": False, "message": str(e)}

#     except Exception as e:
#         db.rollback()
#         print(f"Error: {str(e)}")
#         return {"success": False, "message": "An unexpected error occurred"}

#---------------------------------------------------------------------------------------------------------------
def add_additional_business_places_and_activities(
    db: Session, customer_id: int, service_task_id: int, parsed_data: Dict, user_id: int
) -> Dict[str, Any]:
    business_place_ids = []

    print("Adding additional business places and activities")

    for business_place_data in parsed_data["business_place"]:
        print(f"Processing business place data: {business_place_data}")

        nature_of_business_data = business_place_data.pop("nature_of_business", [])

        existing_business_place = db.query(CustomerBusinessPlace).filter_by(
            customer_id=customer_id,
            service_task_id=service_task_id,
            pin_code=business_place_data["pin_code"],
            country_id=business_place_data["country_id"],
            state_id=business_place_data["state_id"],
            district_id=business_place_data["district_id"],
            city_id=business_place_data["city_id"],
            village_id=business_place_data["village_id"],
            taluk_id=business_place_data["taluk_id"],
            post_office_id=business_place_data["post_office_id"],
            lsg_type_id=business_place_data["lsg_type_id"],
            lsg_id=business_place_data["lsg_id"],
            locality=business_place_data["locality"],
            road_street_name=business_place_data["road_street_name"],
            premises_building_name=business_place_data["premises_building_name"],
            building_flat_number=business_place_data["building_flat_number"],
            floor_number=business_place_data["floor_number"],
            landmark=business_place_data["landmark"],
            latitude=business_place_data["latitude"],
            longitude=business_place_data["longitude"],
            office_email_address=business_place_data["office_email_address"],
            office_mobile_number=business_place_data["office_mobile_number"],
            office_phone_std_code=business_place_data["office_phone_std_code"],
            office_phone_number=business_place_data["office_phone_number"],
            office_fax_std_code=business_place_data["office_fax_std_code"],
            office_fax_number=business_place_data["office_fax_number"],
        ).first()

        if existing_business_place:
            print(f"Using existing business place with ID: {existing_business_place.id}")
            new_business_place = existing_business_place
        else:
            print(f"Creating new business place for service_task_id: {service_task_id}")
            new_business_place = CustomerBusinessPlace(
                **business_place_data,
                customer_id=customer_id,
                service_task_id=service_task_id,
                is_principal_place="yes",
                is_amendment="yes",
                amendment_action="ADDED",
                amendment_status="CREATED",
                created_by=user_id,
                created_on=datetime.now(),
            )
            db.add(new_business_place)
            db.commit()
            db.refresh(new_business_place)

            new_business_place.amended_parent_id = new_business_place.id
            db.commit()
            db.refresh(new_business_place)

        business_place_ids.append(new_business_place.id)
        print(f"Business place processed with ID: {new_business_place.id}")

        for activity_data in nature_of_business_data:
            print(f"Processing activity data: {activity_data} for business_place_id: {new_business_place.id}")

            existing_activity = db.query(CustomerBusinessPlaceActivity).filter_by(
                customer_id=customer_id,
                service_task_id=service_task_id,
                business_activity_id=activity_data["business_activity_id"],
            ).first()

            if existing_activity:
                print(f"Using existing activity with ID: {existing_activity.id}")
                new_activity = existing_activity
            else:
                print(f"Creating new activity for service_task_id: {service_task_id}")
                new_activity = CustomerBusinessPlaceActivity(
                    **activity_data,
                    customer_id=customer_id,
                    business_place_id=new_business_place.id,
                    service_task_id=service_task_id,
                    is_amendment="yes",
                    amendment_action="ADDED",
                    amendment_status="CREATED",
                    created_by=user_id,
                    created_on=datetime.now(),
                )
                db.add(new_activity)
                db.commit()
                db.refresh(new_activity)

                new_activity.amended_parent_id = new_activity.id
                db.commit()
                db.refresh(new_activity)

            print(f"Business activity processed with ID: {new_activity.id}")

    return {"success": True, "ids": business_place_ids}

########################################################################################################
                            # update_additional_business_place
#########################################################################################################
def fetch_existing_place(db: Session, row_id: int) -> CustomerBusinessPlace:
    existing_place = db.query(CustomerBusinessPlace).filter_by(id=row_id).first()
    if not existing_place:
        raise ValueError(f"Business place with ID {row_id} not found")
    return existing_place


def has_changes(existing_place: CustomerBusinessPlace, new_data: dict) -> bool:
    for key, value in new_data.items():
        if getattr(existing_place, key) != value:
            return True
    return False

def duplicate_if_needed(db: Session, existing_place: CustomerBusinessPlace, business_place_data: dict, user_id: int) -> CustomerBusinessPlace:
    # Logging incoming data for debugging
    print(f"Incoming business place data: {business_place_data}")
    
    valid_keys = {c.name for c in CustomerBusinessPlace.__table__.columns}
    filtered_business_place_data = {k: v for k, v in business_place_data.items() if k in valid_keys}
    
    # Logging filtered data for debugging
    print(f"Filtered business place data: {filtered_business_place_data}")

    # Ensure all required fields are present
    required_fields = [
        'pin_code', 'country_id', 'state_id', 'district_id', 'taluk_id', 'city_id',
        'post_office_id', 'lsg_type_id', 'lsg_id', 'village_id', 'locality', 'road_street_name',
        'premises_building_name', 'building_flat_number', 'floor_number', 'landmark',
        'latitude', 'longitude', 'office_email_address', 'office_mobile_number',
        'office_phone_std_code', 'office_phone_number', 'office_fax_std_code', 'office_fax_number'
    ]
    
    for field in required_fields:
        if field not in filtered_business_place_data:
            raise ValueError(f"Missing required field: {field}")

    # Check if there are changes
    if not has_changes(existing_place, filtered_business_place_data):
        print(f"No changes detected for business place ID: {existing_place.id}. No update or duplication needed.")
        return existing_place

    # Duplicate if there's an effective_from_date
    if existing_place.effective_from_date:
        print(f"Duplicating existing place with ID: {existing_place.id}")
        amended_place = CustomerBusinessPlace(
            amended_parent_id=existing_place.id,
            customer_id=existing_place.customer_id,
            service_task_id=existing_place.service_task_id,
            pin_code=filtered_business_place_data.get('pin_code'),
            country_id=filtered_business_place_data.get('country_id'),
            state_id=filtered_business_place_data.get('state_id'),
            district_id=filtered_business_place_data.get('district_id'),
            taluk_id=filtered_business_place_data.get('taluk_id'),
            city_id=filtered_business_place_data.get('city_id'),
            post_office_id=filtered_business_place_data.get('post_office_id'),
            lsg_type_id=filtered_business_place_data.get('lsg_type_id'),
            lsg_id=filtered_business_place_data.get('lsg_id'),
            village_id=filtered_business_place_data.get('village_id'),
            locality=filtered_business_place_data.get('locality'),
            road_street_name=filtered_business_place_data.get('road_street_name'),
            premises_building_name=filtered_business_place_data.get('premises_building_name'),
            building_flat_number=filtered_business_place_data.get('building_flat_number'),
            floor_number=filtered_business_place_data.get('floor_number'),
            landmark=filtered_business_place_data.get('landmark'),
            latitude=filtered_business_place_data.get('latitude'),
            longitude=filtered_business_place_data.get('longitude'),
            office_email_address=filtered_business_place_data.get('office_email_address'),
            office_mobile_number=filtered_business_place_data.get('office_mobile_number'),
            office_phone_std_code=filtered_business_place_data.get('office_phone_std_code'),
            office_phone_number=filtered_business_place_data.get('office_phone_number'),
            office_fax_std_code=filtered_business_place_data.get('office_fax_std_code'),
            office_fax_number=filtered_business_place_data.get('office_fax_number'),
            is_principal_place="yes",
            business_place_type=filtered_business_place_data.get('business_place_type', "HEAD OFFICE"),  # Defaulting to HEAD OFFICE
            nature_of_possession_id=filtered_business_place_data.get('nature_of_possession_id'),
            is_amendment="yes",
            amendment_action="EDITED",
            amendment_status="CREATED",
            created_by=user_id,
            created_on=datetime.now()
        )
        db.add(amended_place)
        db.commit()
        db.refresh(amended_place)
        return amended_place
    else:
        return update_existing_place(db, existing_place, filtered_business_place_data, user_id)


def update_existing_place(db: Session, existing_place: CustomerBusinessPlace, business_place_data: dict, user_id: int) -> CustomerBusinessPlace:
    valid_keys = {c.name for c in CustomerBusinessPlace.__table__.columns}
    filtered_business_place_data = {k: v for k, v in business_place_data.items() if k in valid_keys}

    # Logging filtered data for debugging
    print(f"Filtered business place data: {filtered_business_place_data}")

    # Ensure all required fields are present
    required_fields = [
        'pin_code', 'country_id', 'state_id', 'district_id', 'taluk_id', 'city_id',
        'post_office_id', 'lsg_type_id', 'lsg_id', 'village_id', 'locality', 'road_street_name',
        'premises_building_name', 'building_flat_number', 'floor_number', 'landmark',
        'latitude', 'longitude', 'office_email_address', 'office_mobile_number',
        'office_phone_std_code', 'office_phone_number', 'office_fax_std_code', 'office_fax_number'
    ]
    
    for field in required_fields:
        if field not in filtered_business_place_data:
            raise ValueError(f"Missing required field: {field}")

    print(f"Updating existing place with ID: {existing_place.id}")
    for key, value in filtered_business_place_data.items():
        setattr(existing_place, key, value)
    
    # Set amendment details
    existing_place.amendment_action = "EDITED"
    existing_place.amendment_status = "CREATED"
    existing_place.modified_by = user_id
    existing_place.modified_on = datetime.now()
    
    # Commit and refresh
    db.commit()
    db.refresh(existing_place)
    return existing_place



def get_existing_activitiess(db: Session, customer_id: int, original_place_id: int) -> List[CustomerBusinessPlaceActivity]:
    print(f"Fetching existing activities for customer_id: {customer_id}, original_place_id: {original_place_id}")
    existing_activities = db.query(CustomerBusinessPlaceActivity).filter_by(
        business_place_id=original_place_id, customer_id=customer_id
    ).all()
    print(f"Fetched existing activities: {existing_activities}")
    return existing_activities


def fetch_and_duplicate_activities(db: Session, customer_id: int, original_place_id: int, amended_place_id: int, user_id: int) -> List[CustomerBusinessPlaceActivity]:
    existing_activities = get_existing_activities(db, customer_id, original_place_id)
    print(f"Found existing activities: {existing_activities}")

    duplicated_activities = []
    for activity in existing_activities:
        print(f"Duplicating activity with ID: {activity.id}")
        activity_dict = activity.__dict__.copy()
        activity_dict.pop('_sa_instance_state', None)
        activity_dict.pop('id', None)

        activity_dict['business_place_id'] = amended_place_id
        activity_dict['amended_parent_id'] = activity.id
        activity_dict['customer_id'] = customer_id
        activity_dict['is_amendment'] = 'yes'
        activity_dict['amendment_action'] = 'EDITED'
        activity_dict['created_by'] = user_id
        activity_dict['created_on'] = datetime.now()

        duplicated_activity = CustomerBusinessPlaceActivity(**activity_dict)
        db.add(duplicated_activity)
        db.commit()
        db.refresh(duplicated_activity)

        duplicated_activities.append(duplicated_activity)
        print(f"Duplicated activity saved: {duplicated_activity.id}")

    print(f"Total duplicated activities: {len(duplicated_activities)}")
    return duplicated_activities


def process_activities(db: Session, duplicated_activities: List[CustomerBusinessPlaceActivity], nature_of_business_data: list, user_id: int, amended_place_id: int, customer_id: int, service_task_id: int):
    # Logging inputs
    print(f"Duplicated Activities: {duplicated_activities}")
    print(f"Nature of Business Data: {nature_of_business_data}")
    print(f"User ID: {user_id}")
    print(f"Amended Place ID: {amended_place_id}")
    print(f"Customer ID: {customer_id}")
    print(f"Service Task ID: {service_task_id}")

    # Extract current activity IDs and print them
    current_activity_ids = {activity_data["business_activity_id"] for activity_data in nature_of_business_data}
    print(f"Current Activity IDs: {current_activity_ids}")

    for duplicated_activity in duplicated_activities:
        if duplicated_activity.business_activity_id not in current_activity_ids:
            if duplicated_activity.id == duplicated_activity.amended_parent_id:
                duplicated_activity.is_deleted = "yes"
                duplicated_activity.modified_by = user_id
                duplicated_activity.modified_on = datetime.now()
                db.commit()
                print(f"Marked activity as DELETED with is_deleted=yes: {duplicated_activity.id}")
            else:
                duplicated_activity.amendment_action = "DELETED"
                duplicated_activity.modified_by = user_id
                duplicated_activity.modified_on = datetime.now()
                db.commit()
                print(f"Marked activity as DELETED with amendment_action=DELETED: {duplicated_activity.id}")
        else:
            nature_of_business_data_item = next(item for item in nature_of_business_data if item["business_activity_id"] == duplicated_activity.business_activity_id)
            if duplicated_activity.amendment_reason == nature_of_business_data_item["amendment_reason"]:
                print(f"Activity {duplicated_activity.business_activity_id} remains unchanged.")
            else:
                duplicated_activity.amendment_action = 'EDITED'
                duplicated_activity.amendment_reason = nature_of_business_data_item["amendment_reason"]
                duplicated_activity.modified_by = user_id
                duplicated_activity.modified_on = datetime.now()
                db.commit()
                print(f"Updated activity {duplicated_activity.business_activity_id} to EDITED.")

    for activity_data in nature_of_business_data:
        if not activity_data.get("business_activity_id"):
            raise ValueError("Missing required field: business_activity_id")

        if activity_data.get("id", 0) == 0:
            add_new_activity(db, activity_data, customer_id, amended_place_id, service_task_id, user_id)
        else:
            print(f"Updating existing activity: {activity_data['business_activity_id']}")
            existing_activity = db.query(CustomerBusinessPlaceActivity).filter_by(id=activity_data["id"]).first()
            if existing_activity:
                for key, value in activity_data.items():
                    if key != 'id':
                        setattr(existing_activity, key, value)
                existing_activity.customer_id = customer_id
                existing_activity.is_amendment = "no"  # Ensure original activity is not marked as amendment
                existing_activity.amendment_action = "EDITED"
                existing_activity.modified_by = user_id
                existing_activity.modified_on = datetime.now()
                db.commit()
                print(f"Updated existing activity: {existing_activity.id}")


def add_new_activity(db: Session, activity_data: dict, customer_id: int, amended_place_id: int, service_task_id: int, user_id: int):
    print(f"Adding new activity: {activity_data['business_activity_id']}")
    new_activity = CustomerBusinessPlaceActivity(
        **activity_data,
        customer_id=customer_id,
        business_place_id=amended_place_id,
        service_task_id=service_task_id,
        is_amendment="yes",
        amendment_action="ADDED",
        amendment_status="CREATED",
        created_by=user_id,
        created_on=datetime.now()
    )
    try:
        print("Activity data to be inserted:", new_activity)
        db.add(new_activity)
        db.commit()
        print("After commit")

        # Directly query the database to verify the new activity exists
        inserted_activity = db.query(CustomerBusinessPlaceActivity).filter_by(
            customer_id=customer_id,
            business_place_id=amended_place_id,
            service_task_id=service_task_id,
            business_activity_id=activity_data['business_activity_id'],
            created_by=user_id
        ).order_by(CustomerBusinessPlaceActivity.id.desc()).first()

        if not inserted_activity:
            raise Exception("Inserted activity not found in the database")
        
        new_id = inserted_activity.id
        print(f"New ID is: {new_id}")

        # Use a fresh transaction to update amended_parent_id
        db.query(CustomerBusinessPlaceActivity).filter(CustomerBusinessPlaceActivity.id == new_id).update({"amended_parent_id": new_id})
        db.commit()
        print("After updating amended_parent_id")

        # Fetch and print the updated activity for verification
        updated_activity = db.query(CustomerBusinessPlaceActivity).filter(CustomerBusinessPlaceActivity.id == new_id).first()
        if updated_activity is None:
            raise Exception("Failed to update amended_parent_id")
        print(f"Updated business activity: {updated_activity.id}, amended_parent_id set to {updated_activity.amended_parent_id}")

    except Exception as e:
        db.rollback()
        print(f"Error adding new activity: {e}")

def edit_existing_business_places_and_activities(
    db: Session, customer_id: int, service_task_id: int, row_id: int, parsed_data: Dict, user_id: int
) -> Dict[str, Any]:
    business_place_data_list = parsed_data.get("business_place", [])
    if not business_place_data_list:
        raise ValueError("No business place data provided")

    business_place_data = business_place_data_list[0]  # Assuming there is only one business place to process
    nature_of_business_data = business_place_data.pop("nature_of_business", [])

    existing_place = fetch_existing_place(db, row_id)
    amended_place = duplicate_if_needed(db, existing_place, business_place_data, user_id)

    duplicated_activities = fetch_and_duplicate_activities(db, customer_id, existing_place.id, amended_place.id, user_id)
    print(f"Duplicated activities: {duplicated_activities}")
    process_activities(db, duplicated_activities, nature_of_business_data, user_id, amended_place.id, customer_id, service_task_id)

    return {"success": True, "id": amended_place.id}


# def add_new_activity(db: Session, activity_data: dict, customer_id: int, amended_place_id: int, service_task_id: int, user_id: int):
#     print(f"Adding new activity: {activity_data['business_activity_id']}")
#     new_activity = CustomerBusinessPlaceActivity(
#         **activity_data,
#         customer_id=customer_id,
#         business_place_id=amended_place_id,
#         service_task_id=service_task_id,
#         is_amendment="yes",
#         amendment_action="ADDED",
#         amendment_status="CREATED",
#         created_by=user_id,
#         created_on=datetime.now()
#     )
#     try:
#         print("Activity data to be inserted:", new_activity)
#         db.add(new_activity)
#         db.commit()
#         print("After commit")

#         # Refresh the session to ensure the instance is in sync
#         db.refresh(new_activity)
#         new_id = new_activity.id
#         print(f"New ID is: {new_id}")

#         if new_id is None:
#             raise Exception("Failed to insert new activity")
        
#         # Verifying if the new activity actually exists
#         inserted_activity = db.query(CustomerBusinessPlaceActivity).filter(CustomerBusinessPlaceActivity.id == new_id).first()
#         if inserted_activity is None:
#             raise Exception("Inserted activity not found in the database")

#         # Update the amended_parent_id
#         db.query(CustomerBusinessPlaceActivity).filter(CustomerBusinessPlaceActivity.id == new_id).update({"amended_parent_id": new_id})
#         db.commit()
#         print("After updating amended_parent_id")

#         # Fetch and print the updated activity for verification
#         updated_activity = db.query(CustomerBusinessPlaceActivity).filter(CustomerBusinessPlaceActivity.id == new_id).first()
#         if updated_activity is None:
#             raise Exception("Failed to update amended_parent_id")
#         print(f"Updated business activity: {updated_activity.id}, amended_parent_id set to {updated_activity.amended_parent_id}")

#     except Exception as e:
#         db.rollback()
#         print(f"Error adding new activity: {e}")

# def edit_existing_business_places_and_activities(
#     db: Session, customer_id: int, service_task_id: int, row_id: int, parsed_data: Dict, user_id: int
# ) -> Dict[str, Any]:
#     business_place_data_list = parsed_data.get("business_place", [])
#     if not business_place_data_list:
#         raise ValueError("No business place data provided")

#     business_place_data = business_place_data_list[0]  # Assuming there is only one business place to process
#     nature_of_business_data = business_place_data.pop("nature_of_business", [])

#     existing_place = fetch_existing_place(db, row_id)
#     amended_place = duplicate_if_needed(db, existing_place, business_place_data, user_id)

#     duplicated_activities = fetch_and_duplicate_activities(db, customer_id, existing_place.id, amended_place.id, user_id)
#     print(f"Duplicated activities: {duplicated_activities}")
#     process_activities(db, duplicated_activities, nature_of_business_data, user_id, amended_place.id, customer_id, service_task_id)

#     return {"success": True, "id": amended_place.id}
