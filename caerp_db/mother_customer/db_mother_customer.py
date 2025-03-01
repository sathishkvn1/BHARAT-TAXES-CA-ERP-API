from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, UploadFile, logger,status,Depends
from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session


from caerp_db.common.models import AppConstitutionStakeholders, AppDesignation, AppViewVillages, BusinessActivity, BusinessActivityMaster, BusinessActivityType, CityDB, CountryDB, DistrictDB, Gender, MaritalStatus, PostOfficeView, StateDB, TalukDB
from caerp_db.office.models import AppBusinessConstitution, AppHsnSacClasses, AppHsnSacMaster, OffNatureOfPossession, OffServiceTaskMaster
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerBusinessPlace, CustomerBusinessPlaceActivity, CustomerBusinessPlaceActivityType, CustomerBusinessPlaceCoreActivity, CustomerExistingRegistrationDetails, CustomerGSTCasualTaxablePersonDetails, CustomerGSTCompositionOptedPersonDetails, CustomerGSTOtherDetails, CustomerGoodsCommoditiesSupplyDetails, CustomerGstStateSpecificInformation, CustomerMaster, CustomerStakeHolder, GstNatureOfPossessionOfPremises, GstOtherAuthorizedRepresentativeResignation,GstReasonToObtainRegistration,GstTypeOfRegistration, GstViewRange, StakeHolderAddress, StakeHolderContactDetails, StakeHolderMaster
from caerp_functions.generate_book_number import generate_book_number
from caerp_schema.mother_customer.mother_customer_schema import MotherCustomerRequestSchema
from caerp_schema.services.gst_schema import  AdditionalTradeNameAmendment, AmendmentDetailsSchema, AmmendStakeHolderMasterSchema, BusinessData, BusinessDetailsSchema, BusinessPlace, CombinedSchema, CustomerBusinessPlaceActivitySchemaForGet, CustomerBusinessPlaceAmendmentSchema, CustomerBusinessPlaceFullAmendmentSchema, CustomerBusinessPlaceSchemaForGet, CustomerDuplicateSchema, CustomerGoodsCommoditiesSupplyDetailsSchema, CustomerGstStateSpecificInformationSchema, CustomerRequestSchema, RangeDetailsSchema, StakeHolderMasterSchema, TradeNameSchema




#------save_mother_customer_details

def save_mother_customer_details(
    mother_customer_id: int,
    mother_customer_data: MotherCustomerRequestSchema,
    user_id: int,
    db: Session
):
    try:
        # Retrieve the customer master record
        customer_master = db.query(CustomerMaster).filter(CustomerMaster.customer_id == mother_customer_id).first()

        if not customer_master:
            return []

        # Update or add business details
        business_details = mother_customer_data.mother_customer_business_details
        if business_details.id != 0:
            # Update existing business details if ID is not 0
            business_details_record = db.query(CustomerMaster).filter(CustomerMaster.id == business_details.id).first()
            if business_details_record:
                for key, value in business_details.model_dump(exclude_unset=True).items():
                    setattr(business_details_record, key, value)
                business_details_record.modified_by = user_id
                business_details_record.modified_on = datetime.now()
            else:
                return []
        else:
            # Add new business details if ID is 0
            new_business_details = CustomerMaster(**business_details.model_dump(exclude_unset=True), 
                                                  created_by=user_id, created_on=datetime.now())
            db.add(new_business_details)

        customer_master.modified_by = user_id
        customer_master.modified_on = datetime.now()
        customer_master.is_mother_customer = "yes"

        # Handle Additional Trade Names
        existing_trade_names = {
            trade.id: trade for trade in db.query(CustomerAdditionalTradeName)
            .filter_by(customer_id=mother_customer_id)
            .all()
        }
        incoming_trade_names = {
            trade.id for trade in mother_customer_data.mother_customeradditional_trade_name if trade.id
        }

        # Mark removed trade names as deleted
        for trade_id, trade in existing_trade_names.items():
            if trade_id not in incoming_trade_names:
                trade.is_deleted = "yes"
                trade.deleted_by = user_id
                trade.deleted_on = datetime.now()

        # Update or create new trade names
        for trade in mother_customer_data.mother_customeradditional_trade_name:
            trade_data = trade.model_dump(exclude_unset=True)
            if trade.id != 0:
                # Update existing trade names
                existing_trade = existing_trade_names.get(trade.id)
                if existing_trade:
                    for key, value in trade_data.items():
                        setattr(existing_trade, key, value)
                    existing_trade.is_deleted = "no"
                    existing_trade.modified_by = user_id
                    existing_trade.modified_on = datetime.now()
            else:
                # Add new trade names
                new_trade = CustomerAdditionalTradeName(
                    customer_id=mother_customer_id,
                    additional_trade_name=trade.additional_trade_name,
                    effective_from_date=datetime.now(),
                    created_by=user_id,
                    created_on=datetime.now(),
                )
                db.add(new_trade)

        # Handle Casual Taxable Person details
        if mother_customer_data.mother_customercasual_taxable_person.id != 0:
            # Update existing casual taxable person details
            casual_taxable_person_data = mother_customer_data.mother_customercasual_taxable_person.model_dump(exclude_unset=True)
            existing_casual_taxable_person = db.query(CustomerGSTCasualTaxablePersonDetails).filter_by(id=mother_customer_data.mother_customercasual_taxable_person.id).first()
            if existing_casual_taxable_person:
                for key, value in casual_taxable_person_data.items():
                    setattr(existing_casual_taxable_person, key, value)
                existing_casual_taxable_person.effective_from_date = datetime.now()
                existing_casual_taxable_person.modified_by = user_id
                existing_casual_taxable_person.modified_on = datetime.now()
        else:
            # Add new casual taxable person details
            casual_taxable_person_data = mother_customer_data.mother_customercasual_taxable_person.model_dump(exclude_unset=True)
            new_casual_taxable_person = CustomerGSTCasualTaxablePersonDetails(
                customer_id=mother_customer_id,
                **casual_taxable_person_data,
                effective_from_date=datetime.now(),
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_casual_taxable_person)

        # Handle Composition Option details
        if mother_customer_data.mother_customeroption_for_composition.id != 0:
            # Update existing composition option details
            composition_option_data = mother_customer_data.mother_customeroption_for_composition.model_dump(exclude_unset=True)
            existing_composition_option = db.query(CustomerGSTCompositionOptedPersonDetails).filter_by(id=mother_customer_data.mother_customeroption_for_composition.id).first()
            if existing_composition_option:
                for key, value in composition_option_data.items():
                    setattr(existing_composition_option, key, value)
                existing_composition_option.effective_from_date = datetime.now()
                existing_composition_option.modified_by = user_id
                existing_composition_option.modified_on = datetime.now()
        else:
            # Add new composition option details
            composition_option_data = mother_customer_data.mother_customeroption_for_composition.model_dump(exclude_unset=True)
            new_composition_option = CustomerGSTCompositionOptedPersonDetails(
                customer_id=mother_customer_id,
                **composition_option_data,
                effective_from_date=datetime.now(),
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(new_composition_option)

        # Handle Other GST Details
        if mother_customer_data.mother_customerreason_to_obtain_registration.id == 0:
            # Ensure reason_to_obtain_gst_registration_id is not None if it's required
            reason_to_obtain_gst_registration_id = mother_customer_data.mother_customerreason_to_obtain_registration.reason_to_obtain_gst_registration_id
            if reason_to_obtain_gst_registration_id is None:
                return []

            gst_other_details = CustomerGSTOtherDetails(
                customer_id=mother_customer_id,
                reason_to_obtain_gst_registration_id=reason_to_obtain_gst_registration_id,
                **mother_customer_data.mother_customerreason_to_obtain_registration.model_dump(exclude_unset=True),
                effective_from_date=datetime.now(),
                effective_to_date=None,
                created_by=user_id,
                created_on=datetime.now()
            )
            db.add(gst_other_details)
        else:
            existing_gst_other_details = db.query(CustomerGSTOtherDetails).filter_by(id=mother_customer_data.mother_customerreason_to_obtain_registration.id).first()
            if existing_gst_other_details:
                for key, value in mother_customer_data.mother_customerreason_to_obtain_registration.model_dump(exclude_unset=True).items():
                    setattr(existing_gst_other_details, key, value)
                existing_gst_other_details.effective_from_date = datetime.now()
                existing_gst_other_details.effective_to_date = None
                existing_gst_other_details.modified_by = user_id
                existing_gst_other_details.modified_on = datetime.now()

        existing_registrations = {
            reg.id: reg for reg in db.query(CustomerExistingRegistrationDetails)
            .filter_by(customer_id=mother_customer_id)
            .all()
        }
        incoming_registrations = {
            reg.id for reg in mother_customer_data.mother_customerexisting_registrations if reg.id
        }

        for reg_id, reg in existing_registrations.items():
            if reg_id not in incoming_registrations:
                reg.is_deleted = "yes"
                reg.deleted_by = user_id
                reg.deleted_on = datetime.now()

        for reg in mother_customer_data.mother_customerexisting_registrations:
            reg_data = reg.model_dump(exclude_unset=True)
            if reg.id != 0:
                # Update existing registrations
                existing_reg = existing_registrations.get(reg.id)
                if existing_reg:
                    for key, value in reg_data.items():
                        setattr(existing_reg, key, value)
                    existing_reg.is_deleted = "no"
                    existing_reg.modified_by = user_id
                    existing_reg.modified_on = datetime.now()
            else:
                # Add new registrations
                new_reg = CustomerExistingRegistrationDetails(
                    customer_id=mother_customer_id,
                    **reg_data,
                    effective_from_date=datetime.now(),
                    created_by=user_id,
                    created_on=datetime.now(),
                )
                db.add(new_reg)

        # Commit transaction
        db.commit()
        return {"message": "Mother customer details saved successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


#---------------------


def get_customer_details(db: Session, 
                         mother_customer_id: int, 
                         
                         user_id: int):
    try:
        # Query the main customer record with customer_id and service_task_id
        customer = (
            db.query(CustomerMaster)
            .filter(CustomerMaster.customer_id == mother_customer_id)
            
            .first()
        )
        
        if not customer:
            return []

        # Query related details with customer_id and service_task_id
        additional_trade_names = (
            db.query(CustomerAdditionalTradeName)
            .filter(CustomerAdditionalTradeName.customer_id == mother_customer_id)
           
            .filter(CustomerAdditionalTradeName.is_deleted == "no")
            .filter(
                CustomerAdditionalTradeName.effective_from_date <= datetime.now(),
                CustomerAdditionalTradeName.effective_to_date.is_(None),
            )
            .all()
        )
        
        casual_taxable_person = (
            db.query(CustomerGSTCasualTaxablePersonDetails)
            .filter(CustomerGSTCasualTaxablePersonDetails.customer_id == mother_customer_id)
            
            .filter(
                CustomerGSTCasualTaxablePersonDetails.effective_from_date <= datetime.now(),
                CustomerGSTCasualTaxablePersonDetails.effective_to_date.is_(None),
            )
            .first()
        )
        
        composition_option = (
            db.query(CustomerGSTCompositionOptedPersonDetails)
            .filter(CustomerGSTCompositionOptedPersonDetails.customer_id == mother_customer_id)
            
            .filter(
                CustomerGSTCompositionOptedPersonDetails.effective_from_date <= datetime.now(),
                CustomerGSTCompositionOptedPersonDetails.effective_to_date.is_(None),
            )
            .first()
        )
        
        gst_other_details = (
            db.query(CustomerGSTOtherDetails)
            .filter(CustomerGSTOtherDetails.customer_id == mother_customer_id)
            
            .filter(
                CustomerGSTOtherDetails.effective_from_date <= datetime.now(),
                CustomerGSTOtherDetails.effective_to_date.is_(None),
            )
            .first()
        )
        
        existing_registrations = (
            db.query(CustomerExistingRegistrationDetails)
            .filter(CustomerExistingRegistrationDetails.customer_id == mother_customer_id)
          
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
                "constitution_id": customer.constitution_id,
                "constitution_name": db.query(AppBusinessConstitution.business_constitution_name).filter_by(id=customer.constitution_id).scalar() if customer.constitution_id else None,
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
                    
                    "commencement_of_business_date": gst_other_details.commencement_of_business_date if gst_other_details else None,
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





#------------------save stakeholder

def save_mother_customer_stakeholder_details(
    request: StakeHolderMasterSchema,
    user_id: int,
    db: Session,
    mother_customer_id: int,
   
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
            customer_id=mother_customer_id,
            stake_holder_master_id=stake_holder_master.id
        ).filter(CustomerStakeHolder.effective_to_date == None).first()

        if existing_customer_stakeholder_entry:
            amended_parent_id = existing_customer_stakeholder_entry.id
            existing_customer_stakeholder_entry.effective_to_date = datetime.now() - timedelta(days=1)
            existing_customer_stakeholder_entry.modified_by = user_id
            existing_customer_stakeholder_entry.modified_on = datetime.now()

        customer_stakeholder_entry = CustomerStakeHolder(
            customer_id=mother_customer_id,
            stake_holder_master_id=stake_holder_master.id,
            designation_id=request.customer_stakeholders[0].designation_id,
            contact_details_id=contact_details_id,
            residential_address_id=residential_address_id,
            stake_holder_type=stake_holder_type,
            is_authorized_signatory=is_authorized_signatory,
            is_primary_authorized_signatory=is_primary_authorized_signatory,
            authorized_representative_type=authorized_representative_type,
          
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
    



#-------------------

def get_mother_customer_stakeholder_details(
    db: Session,
    user_id: int,
    mother_customer_id: Optional[int] = None,
    
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
        if mother_customer_id:
            query = query.filter(CustomerStakeHolder.customer_id == mother_customer_id)
        if stake_holder_type:
            query = query.filter(CustomerStakeHolder.stake_holder_type == stake_holder_type)
        if is_authorized_signatory is not None:
            query = query.filter(CustomerStakeHolder.is_authorized_signatory == is_authorized_signatory)
        if is_primary_authorized_signatory is not None:
            query = query.filter(CustomerStakeHolder.is_primary_authorized_signatory == is_primary_authorized_signatory)
        if authorized_representative_type is not None:
            query = query.filter(CustomerStakeHolder.authorized_representative_type == authorized_representative_type)
      

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




#--------------------------

def save_mother_customer_business_place(
    mother_customer_id: int,
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
                        customer_id=mother_customer_id,
                     
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
                    id=id, customer_id=mother_customer_id
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
                .filter_by(customer_id=mother_customer_id, business_place_id=business_place_id)
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
                        customer_id=mother_customer_id,
                        
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
                    customer_id=mother_customer_id,
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
                        customer_id=mother_customer_id,
                     
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
                    customer_id=mother_customer_id,
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
                        customer_id=mother_customer_id,
                        
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

#-------------------------------


def get_mother_customer_business_place(mother_customer_id: int, 
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
            CustomerBusinessPlace.customer_id == mother_customer_id,
          
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
                "office_fax_number"  : bp.office_fax_number,
                "office_whatsapp_number":bp.office_whatsapp_number       
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
    
#-------------------------------------------------------------

def save_mother_customer_goods_commodities_details(
    mother_customer_id: int,
    
    details: List[CustomerGoodsCommoditiesSupplyDetailsSchema],
    db: Session,
    user_id: int
):
    try:
        # Fetch existing records for the customer
        existing_entries = {entry.id: entry for entry in db.query(CustomerGoodsCommoditiesSupplyDetails)
                            .filter_by(customer_id=mother_customer_id).all()}

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
            item_data = item.model_dump(exclude_unset=True)
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
                    customer_id=mother_customer_id,
                    hsn_sac_class_id=item.hsn_sac_class_id,
                    hsn_sac_code_id=item.hsn_sac_code_id,
                    effective_from_date=date.today(),
                    effective_to_date=None,
                   
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
def get_mother_customer_hsn_commodities(mother_customer_id: int,
                                       
                                       user_id: int, 
                                       db: Session):
    try:
        # Query the CustomerGoodsCommoditiesSupplyDetails for the given customer_id
        commodities = (
            db.query(CustomerGoodsCommoditiesSupplyDetails)
            .filter(
                CustomerGoodsCommoditiesSupplyDetails.customer_id == mother_customer_id,
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


def save_mother_customer_gst_state_specific_information(
    id: int,  # 0 for insert, non-zero for update
    mother_customer_id: int,
    
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
                customer_id=mother_customer_id,
                
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

def get_mother_customer_gst_state_specific_information(mother_customer_id: int, 
                                                      db: Session,
                                                      user_id:int) -> List[CustomerGstStateSpecificInformation]:
    try:
        # Query the CustomerGstStateSpecificInformation for the given customer_id
        gst_info_records = (
            db.query(CustomerGstStateSpecificInformation)
            .filter(CustomerGstStateSpecificInformation.customer_id == mother_customer_id,
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


#--------------------------------


def delete_mother_customer_gst_registration_record(
    db: Session,
    user_id: int,
    mother_customer_id,
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
            customer_stakeholders = db.query(CustomerStakeHolder).filter_by(stake_holder_master_id=stakeholder_id, customer_id=mother_customer_id)
            for customer_sh in customer_stakeholders:
                customer_sh.is_deleted = "yes"
                customer_sh.deleted_by = user_id
                customer_sh.deleted_on = datetime.now()

        elif business_place_id:
            # Delete Business Place records with customer_id filter
            business_place = db.query(CustomerBusinessPlace).filter_by(id=business_place_id, customer_id=mother_customer_id).first()
            if not business_place:
                return []
            
            business_place.is_deleted = "yes"
            business_place.deleted_by = user_id
            business_place.deleted_on = datetime.now()

            # Delete related CustomerBusinessPlaceActivity with customer_id filter
            activities = db.query(CustomerBusinessPlaceActivity).filter_by(business_place_id=business_place_id,customer_id=mother_customer_id)
            for activity in activities:
                activity.is_deleted = "yes"
                activity.deleted_by = user_id
                activity.deleted_on = datetime.now()

            # Delete related CustomerBusinessPlaceActivityType with customer_id filter
            activity_types = db.query(CustomerBusinessPlaceActivityType).filter_by(business_place_id=business_place_id, customer_id=mother_customer_id)
            for activity_type in activity_types:
                activity_type.is_deleted = "yes"
                activity_type.deleted_by = user_id
                activity_type.deleted_on = datetime.now()

            # Delete related CustomerBusinessPlaceCoreActivity with customer_id filter
            core_activities = db.query(CustomerBusinessPlaceCoreActivity).filter_by(business_place_id=business_place_id, customer_id=mother_customer_id)
            for core_activity in core_activities:
                core_activity.is_deleted = "yes"
                core_activity.deleted_by = user_id
                core_activity.deleted_on = datetime.now()

        db.commit()
        return {"success": True, "message": "Data deleted successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
