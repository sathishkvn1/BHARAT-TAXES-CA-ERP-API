from datetime import date, datetime, timedelta
from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy.orm import Session

from caerp_db.common.models import AppDesignation, AppViewVillages, CityDB, CountryDB, DistrictDB, Gender, MaritalStatus, StateDB
from caerp_db.office.models import OffServiceTaskMaster
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerExistingRegistrationDetails, CustomerGSTCasualTaxablePersonDetails, CustomerGSTCompositionOptedPersonDetails, CustomerGSTOtherDetails, CustomerMaster, CustomerStakeHolder,GstReasonToObtainRegistration,GstTypeOfRegistration, StakeHolderAddress, StakeHolderContactDetails, StakeHolderMaster
from caerp_schema.services.gst_schema import BusinessDetailsSchema, CustomerRequestSchema, StakeHolderMasterSchema



#-------------------------business details


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


#-------CUSTOMER / BUSINESS DETAILS

def save_customer_details(customer_id: int, 
                          customer_data: CustomerRequestSchema, 
                          user_id: int,
                          db: Session):
    try:
        # Handle Additional Trade Names
        for trade_name in customer_data.additional_trade_name:
            if trade_name.id == 0:
                new_trade_name = CustomerAdditionalTradeName(
                    customer_id=customer_id,
                    additional_trade_name=trade_name.trade_name,
                    created_by=user_id,  # Set created_by field
                    created_on=datetime.now() 
                )
                db.add(new_trade_name)
            else:
                existing_trade_name = db.query(CustomerAdditionalTradeName).filter_by(id=trade_name.id).first()
                if existing_trade_name:
                    existing_trade_name.additional_trade_name = trade_name.trade_name
                    existing_trade_name.modified_by = user_id  # Set modified_by field
                    existing_trade_name.modified_on = datetime.now() 
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
                estimated_net_cess_liability=customer_data.casual_taxable_person.estimated_net_cess_liability,
                created_by=user_id,  # Set created_by field
                created_on=datetime.now() 
            )
            db.add(casual_taxable_person)
        else:
            existing_casual_taxable_person = db.query(CustomerGSTCasualTaxablePersonDetails).filter_by(id=customer_data.casual_taxable_person.id).first()
            if existing_casual_taxable_person:
                existing_casual_taxable_person.is_applying_as_casual_taxable_person = customer_data.casual_taxable_person.is_applying_as_casual_taxable_person
                existing_casual_taxable_person.estimated_igst_turnover = customer_data.casual_taxable_person.estimated_igst_turnover
                existing_casual_taxable_person.estimated_net_igst_liability = customer_data.casual_taxable_person.estimated_net_igst_liability
                existing_casual_taxable_person.estimated_cgst_turnover = customer_data.casual_taxable_person.estimated_igst_turnover
                existing_casual_taxable_person.estimated_net_cgst_liability = customer_data.casual_taxable_person.estimated_net_igst_liability
                existing_casual_taxable_person.estimated_sgst_turnover = customer_data.casual_taxable_person.estimated_igst_turnover
                existing_casual_taxable_person.estimated_net_sgst_liability = customer_data.casual_taxable_person.estimated_net_igst_liability
                existing_casual_taxable_person.estimated_cess_turnover = customer_data.casual_taxable_person.estimated_igst_turnover
                existing_casual_taxable_person.estimated_net_cess_liability = customer_data.casual_taxable_person.estimated_net_igst_liability
                existing_casual_taxable_person.modified_by = user_id  # Set modified_by field
                existing_casual_taxable_person.modified_on = datetime.now() 
    
        # Handle Composition Option
        if customer_data.option_for_composition.id == 0:
            composition_option = CustomerGSTCompositionOptedPersonDetails(
                customer_id=customer_id,
                is_applying_as_composition_taxable_person=customer_data.option_for_composition.is_applying_as_composition_taxable_person,
                option_1=customer_data.option_for_composition.option_1,
                option_2=customer_data.option_for_composition.option_2,
                option_3=customer_data.option_for_composition.option_3,
                created_by=user_id,  # Set created_by field
                created_on=datetime.now() 
            )
            db.add(composition_option)
        else:
            existing_composition_option = db.query(CustomerGSTCompositionOptedPersonDetails).filter_by(id=customer_data.option_for_composition.id).first()
            if existing_composition_option:
                existing_composition_option.is_applying_as_composition_taxable_person = customer_data.option_for_composition.is_applying_as_composition_taxable_person
                existing_composition_option.option_1 = customer_data.option_for_composition.option_1
                existing_composition_option.option_2 = customer_data.option_for_composition.option_2
                existing_composition_option.option_3 = customer_data.option_for_composition.option_3
                existing_composition_option.modified_by = user_id  # Set modified_by field
                existing_composition_option.modified_on = datetime.now() 
    
        # Handle Other GST Details
        if customer_data.reason_to_obtain_registration.id == 0:
            gst_other_details = CustomerGSTOtherDetails(
                customer_id=customer_id,
                reason_to_obtain_gst_registration_id=customer_data.reason_to_obtain_registration.reason_to_obtain_gst_registration_id,
                commencement_of_business_date=customer_data.reason_to_obtain_registration.commencement_of_business_date,
                liability_to_register_arises_date=customer_data.reason_to_obtain_registration.liability_to_register_arises_date,
                created_by=user_id,  # Set created_by field
                created_on=datetime.now()
            )
            db.add(gst_other_details)
        else:
            existing_gst_other_details = db.query(CustomerGSTOtherDetails).filter_by(id=customer_data.reason_to_obtain_registration.id).first()
            if existing_gst_other_details:
                existing_gst_other_details.reason_to_obtain_gst_registration_id = customer_data.reason_to_obtain_registration.reason_to_obtain_gst_registration_id
                existing_gst_other_details.commencement_of_business_date = customer_data.reason_to_obtain_registration.commencement_of_business_date
                existing_gst_other_details.liability_to_register_arises_date = customer_data.reason_to_obtain_registration.liability_to_register_arises_date
                existing_gst_other_details.modified_by = user_id  # Set modified_by field
                existing_gst_other_details.modified_on = datetime.now() 
    
        # Handle Existing Registrations
        for registration in customer_data.existing_registrations:
            if registration.id == 0:
                new_registration = CustomerExistingRegistrationDetails(
                    customer_id=customer_id,
                    registration_type_id=registration.registration_type_id,
                    registration_number=registration.registration_number,
                    registration_date=registration.registration_date,
                    created_by=user_id,  # Set created_by field
                    created_on=datetime.now()
                )
                db.add(new_registration)
            else:
                existing_registration = db.query(CustomerExistingRegistrationDetails).filter_by(id=registration.id).first()
                if existing_registration:
                    existing_registration.registration_type_id = registration.registration_type_id
                    existing_registration.registration_number = registration.registration_number
                    existing_registration.registration_date = registration.registration_date
                    existing_registration.modified_by = user_id  # Set modified_by field
                    existing_registration.modified_on = datetime.now() 
    
        # Handle Authorization
        if customer_id == 0:  # New Customer Authorization
            new_authorization = CustomerMaster(
                customer_id=customer_id,
                constitution_id=customer_data.authorization.constitution_id,
                has_authorized_signatory=customer_data.authorization.has_authorized_signatory,
                has_authorized_representative=customer_data.authorization.has_authorized_representative,
                is_mother_customer=customer_data.authorization.is_mother_customer,
                created_by=user_id,  # Set created_by field
                created_on=datetime.now()
            )
            db.add(new_authorization)
        else:
            existing_authorization = db.query(CustomerMaster).filter_by(customer_id=customer_id).first()
            if existing_authorization:
                existing_authorization.constitution_id = customer_data.authorization.constitution_id
                existing_authorization.has_authorized_signatory = customer_data.authorization.has_authorized_signatory
                existing_authorization.has_authorized_representative = customer_data.authorization.has_authorized_representative
                existing_authorization.is_mother_customer = customer_data.authorization.is_mother_customer
                existing_authorization.modified_by = user_id  # Set modified_by field
                existing_authorization.modified_on = datetime.now() 
    
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
            return []

        # Query related details
        additional_trade_names = db.query(CustomerAdditionalTradeName).filter_by(customer_id=customer_id).all()
        casual_taxable_person = db.query(CustomerGSTCasualTaxablePersonDetails).filter_by(customer_id=customer_id).first()
        composition_option = db.query(CustomerGSTCompositionOptedPersonDetails).filter_by(customer_id=customer_id).first()
        gst_other_details = db.query(CustomerGSTOtherDetails).filter_by(customer_id=customer_id).first()
        existing_registrations = db.query(CustomerExistingRegistrationDetails).filter_by(customer_id=customer_id).all()

        # Assemble response data
        response = {
            "customer_business_details": {
                "id": customer.customer_id,
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
                    "reason_to_obtain_gst_registration_id": gst_other_details.reason_to_obtain_gst_registration_id if gst_other_details and gst_other_details.reason_to_obtain_gst_registration_id is not None else None,
                     "reason_to_obtain_gst_registration_name": db.query(GstReasonToObtainRegistration.reason)
                                                .filter_by(id=gst_other_details.reason_to_obtain_gst_registration_id)
                                                .scalar() if gst_other_details and gst_other_details.reason_to_obtain_gst_registration_id else None,
    "commencement_of_business_date": gst_other_details.commencement_of_business_date if gst_other_details else None,
    "liability_to_register_arises_date": gst_other_details.liability_to_register_arises_date if gst_other_details else None
                },
                "existing_registrations": [
                    {
                        "id": reg.id if existing_registrations else None,
                        "registration_type_id": reg.registration_type_id if reg.registration_type_id is not None else None, 
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
    

    #-save stskeholder


def save_stakeholder_details(request: StakeHolderMasterSchema, 
                             user_id: int,
                             db: Session, 
                             customer_id: int):
    try:
        # 1. Handle StakeHolderMaster
        personal_info = request.personal_information
        if personal_info.id == 0:
            # Create new StakeHolderMaster
            stake_holder_master = StakeHolderMaster(
                first_name=personal_info.first_name,
                middle_name=personal_info.middle_name,
                last_name=personal_info.last_name,
                fathers_first_name=personal_info.fathers_first_name,
                marital_status_id=personal_info.marital_status_id,
                date_of_birth=personal_info.date_of_birth,
                gender_id=personal_info.gender_id,
                din_number=personal_info.din_number,
                is_citizen_of_india=personal_info.is_citizen_of_india,
                pan_number=personal_info.pan_number,
                passport_number=personal_info.passport_number,
                aadhaar_number=personal_info.aadhaar_number,
                created_by=user_id,  # Set created_by field
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
                stake_holder_master.marital_status_id = personal_info.marital_status_id
                stake_holder_master.date_of_birth = personal_info.date_of_birth
                stake_holder_master.gender_id = personal_info.gender_id
                stake_holder_master.din_number = personal_info.din_number
                stake_holder_master.is_citizen_of_india = personal_info.is_citizen_of_india
                stake_holder_master.pan_number = personal_info.pan_number
                stake_holder_master.passport_number = personal_info.passport_number
                stake_holder_master.aadhaar_number = personal_info.aadhaar_number
                stake_holder_master.modified_by = user_id  # Set modified_by field
                stake_holder_master.modified_on = datetime.now()
            else:
                return {"detail": "stake_holder_master not found"}

        db.flush()  # Flush to get `stake_holder_master.id`

        # 2. Handle StakeHolderContactDetails
        contact_details = request.contact_details
        if contact_details.id == 0:
            # Create new contact details
            contact_detail_entry = StakeHolderContactDetails(
                stake_holder_id=stake_holder_master.id,
                mobile_number=contact_details.mobile_number,
                email_address=contact_details.email_address,
                telephone_number_with_std_code=contact_details.telephone_number_with_std_code,
                created_by=user_id,  # Set created_by field
                created_on=datetime.now()
            )
            db.add(contact_detail_entry)
        else:
            # Update existing contact details
            contact_detail_entry = db.query(StakeHolderContactDetails).filter_by(id=contact_details.id).first()
            if contact_detail_entry:
                contact_detail_entry.mobile_number = contact_details.mobile_number
                contact_detail_entry.email_address = contact_details.email_address
                contact_detail_entry.telephone_number_with_std_code = contact_details.telephone_number_with_std_code
                contact_detail_entry.modified_by = user_id  # Set modified_by field
                contact_detail_entry.modified_on = datetime.now()
            else:
                return {"detail": "contact_detail not found"}

        db.flush()  # Flush to get `contact_detail_entry.id`

        # 3. Handle StakeHolderAddress
        for addr in request.address:
            if addr.address_type == "RESIDENTIAL":
                if addr.id == 0:
                    # Create new address
                    address_entry = StakeHolderAddress(
                        stake_holder_id=stake_holder_master.id,
                        pin_code=addr.pin_code,
                        address_type=addr.address_type,
                        country_id=addr.country_id,
                        state_id=addr.state_id,
                        district_id=addr.district_id,
                        city_id=addr.city_id,
                        village_id=addr.village_id,
                        post_office_id=addr.post_office_id,
                        lsg_type_id=addr.lsg_type_id,
                        lsg_id=addr.lsg_id,
                        locality=addr.locality,
                        road_street_name=addr.road_street_name,
                        premises_building_name=addr.premises_building_name,
                        building_flat_number=addr.building_flat_number,
                        floor_number=addr.floor_number,
                        landmark=addr.landmark,
                        created_by=user_id,  # Set created_by field
                        created_on=datetime.now()
                    )
                    db.add(address_entry)
                else:
                    # Update existing address
                    address_entry = db.query(StakeHolderAddress).filter_by(id=addr.id).first()
                    if address_entry:
                        address_entry.pin_code = addr.pin_code
                        address_entry.country_id = addr.country_id
                        address_entry.state_id = addr.state_id
                        address_entry.district_id = addr.district_id
                        address_entry.city_id = addr.city_id
                        address_entry.village_id = addr.village_id
                        address_entry.post_office_id = addr.post_office_id
                        address_entry.lsg_type_id = addr.lsg_type_id
                        address_entry.lsg_id = addr.lsg_id
                        address_entry.locality = addr.locality
                        address_entry.road_street_name = addr.road_street_name
                        address_entry.premises_building_name = addr.premises_building_name
                        address_entry.building_flat_number = addr.building_flat_number
                        address_entry.floor_number = addr.floor_number
                        address_entry.landmark = addr.landmark
                        address_entry.modified_by = user_id  # Set modified_by field
                        address_entry.modified_on = datetime.now()
                    else:
                        return {"detail": "address_detail not found"}

                db.flush()  # Flush to get `address_entry.id`

        # 4. Insert into the `customer_stakeholder` table
        customer_stakeholder_entry = CustomerStakeHolder(
            customer_id=customer_id,
            stake_holder_master_id=stake_holder_master.id,
            designation_id=request.identity_information[0].designation_id,  # Assuming identity_information[0] is valid
            contact_details_id=contact_detail_entry.id,
            residential_address_id=address_entry.id,
            created_by=user_id,  # Set created_by field
            created_on=datetime.now()
        )
        db.add(customer_stakeholder_entry)

        # Commit the transaction
        db.commit()

        return {"message": "saved successfully"}

    except Exception as e:
        db.rollback()  # Roll back the transaction in case of error
        raise HTTPException(status_code=500, detail=str(e))

#-get
def get_stakeholder_details(db: Session, 
                            customer_id: int):
    try:
        # Fetch records from CustomerStakeHolder based on customer_id
        customer_stakeholders = db.query(CustomerStakeHolder).filter_by(customer_id=customer_id).all()

        if not customer_stakeholders:
            return []

        # Initialize an empty list to hold stakeholder details
        stakeholder_details = []

        for customer_stakeholder in customer_stakeholders:
            # Fetch StakeHolderMaster record based on stake_holder_master_id
            stakeholder = db.query(StakeHolderMaster).filter_by(id=customer_stakeholder.stake_holder_master_id).first()
            
            if not stakeholder:
                continue

            # Fetch designation details
            designation = db.query(AppDesignation).filter_by(id=customer_stakeholder.designation_id).first() if customer_stakeholder.designation_id else None

            # Fetch address details
            address = db.query(StakeHolderAddress).filter_by(id=customer_stakeholder.residential_address_id).first() if customer_stakeholder.residential_address_id else None

            # Fetch contact details
            contact_details = db.query(StakeHolderContactDetails).filter_by(id=customer_stakeholder.contact_details_id).first() if customer_stakeholder.contact_details_id else None

            # Assemble response data for each stakeholder
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
                    "marital_status": db.query(MaritalStatus.marital_status).filter_by(id=stakeholder.marital_status_id).scalar() if stakeholder.marital_status_id else None,
                    "date_of_birth": stakeholder.date_of_birth,
                    "gender_id": stakeholder.gender_id,
                    "gender": db.query(Gender.gender).filter_by(id=stakeholder.gender_id).scalar() if stakeholder.gender_id else None,
                    "din_number": stakeholder.din_number,
                    "is_citizen_of_india": stakeholder.is_citizen_of_india,
                    "pan_number": stakeholder.pan_number,
                    "passport_number": stakeholder.passport_number,
                    "aadhaar_number": stakeholder.aadhaar_number
                },
                "contact_details": {
                    "id": contact_details.id if contact_details else None,
                    "mobile_number": contact_details.mobile_number if contact_details else None,
                    "email_address": contact_details.email_address if contact_details else None,
                    "telephone_number_with_std_code": contact_details.telephone_number_with_std_code if contact_details else None
                } if contact_details else {},
                "identity_information": [
                    {
                        "id": designation.id if designation else 0,
                        "designation_id": designation.id if designation else None,
                        "designation": designation.designation if designation else None
                    }
                ] if designation else [],
                "address": [
                    {
                        "id": address.id if address else None,
                        "pin_code": address.pin_code if address else None,
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
                        "lsg_type_id": address.lsg_type_id if address else None,
                        "lsg_type": db.query(AppViewVillages.lsg_type).filter_by(app_village_id=address.lsg_type_id).scalar() if address and address.lsg_type_id else None,
                        "lsg_id": address.lsg_id if address else None,
                        "lsg": db.query(AppViewVillages.lsg_name).filter_by(app_village_id=address.lsg_id).scalar() if address and address.lsg_id else None,
                        "locality": address.locality if address else None,
                        "road_street_name": address.road_street_name if address else None,
                        "premises_building_name": address.premises_building_name if address else None,
                        "building_flat_number": address.building_flat_number if address else None,
                        "floor_number": address.floor_number if address else None,
                        "landmark": address.landmark if address else None
                    }
                ] if address else []
            }

            # Append the response for this stakeholder to the list
            stakeholder_details.append(response)

        return stakeholder_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))