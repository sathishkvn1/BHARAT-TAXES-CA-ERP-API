from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, UploadFile,status,Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from caerp_db.common.models import AppDesignation, AppViewVillages, BusinessActivity, BusinessActivityMaster, BusinessActivityType, CityDB, CountryDB, DistrictDB, Gender, MaritalStatus, PostOfficeView, StateDB, TalukDB
from caerp_db.office.models import AppBusinessConstitution, AppHsnSacClasses, AppHsnSacMaster, OffNatureOfPossession, OffServiceTaskMaster
from caerp_db.services.model import CustomerAdditionalTradeName, CustomerBusinessPlace, CustomerBusinessPlaceActivity, CustomerBusinessPlaceActivityType, CustomerBusinessPlaceCoreActivity, CustomerExistingRegistrationDetails, CustomerGSTCasualTaxablePersonDetails, CustomerGSTCompositionOptedPersonDetails, CustomerGSTOtherDetails, CustomerGoodsCommoditiesSupplyDetails, CustomerGstStateSpecificInformation, CustomerMaster, CustomerStakeHolder,GstReasonToObtainRegistration,GstTypeOfRegistration, GstViewRange, StakeHolderAddress, StakeHolderContactDetails, StakeHolderMaster
from caerp_functions.generate_book_number import generate_book_number
from caerp_schema.services.gst_schema import  BusinessData, BusinessDetailsSchema, BusinessPlace, CustomerGoodsCommoditiesSupplyDetailsSchema, CustomerGstStateSpecificInformationSchema, CustomerRequestSchema, RangeDetailsSchema, StakeHolderMasterSchema, TradeNameSchema



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
                created_by=user_id,  # Set created_by field
                created_on=datetime.now(),  # Set created_on to current datetime
                effective_from_date=datetime.now(),  # Set effective_from_date to current date
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

            customer_master.modified_by = user_id  # Set modified_by field
            customer_master.modified_on = datetime.now()  # Set modified_on field
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


# def save_customer_details(customer_id: int, 
#                           customer_data: CustomerRequestSchema, 
#                           user_id: int, 
#                           db: Session):
#     try:
#         # Handle Additional Trade Names
#         for additional_trade_name in customer_data.additional_trade_name:
#             if additional_trade_name.id == 0:
#                 new_trade_name = CustomerAdditionalTradeName(
#                     customer_id=customer_id,
#                     **additional_trade_name.model_dump(exclude_unset=True),  # Use model_dump to pass fields dynamically
#                     effective_from_date=datetime.now(),  # Set effective_from_date to current date
#                     effective_to_date=None,
#                     created_by=user_id,
#                     created_on=datetime.now()
#                 )
#                 db.add(new_trade_name)
#             else:
#                 existing_trade_name = db.query(CustomerAdditionalTradeName).filter_by(id=additional_trade_name.id).first()
#                 if existing_trade_name:
#                     for key, value in additional_trade_name.model_dump(exclude_unset=True).items():
#                         setattr(existing_trade_name, key, value)
#                     existing_trade_name.effective_from_date=datetime.now()  # Set effective_from_date to current date
#                     existing_trade_name.effective_to_date=None
#                     existing_trade_name.modified_by = user_id
#                     existing_trade_name.modified_on = datetime.now()

#         # Handle Casual Taxable Person Details
#         if customer_data.casual_taxable_person.id == 0:
#             casual_taxable_person = CustomerGSTCasualTaxablePersonDetails(
#                 customer_id=customer_id,
#                 **customer_data.casual_taxable_person.model_dump(exclude_unset=True),
#                 effective_from_date=datetime.now(),  # Set effective_from_date to current date
#                 effective_to_date=None,
#                 created_by=user_id,
#                 created_on=datetime.now()
#             )
#             db.add(casual_taxable_person)
#         else:
#             existing_casual_taxable_person = db.query(CustomerGSTCasualTaxablePersonDetails).filter_by(id=customer_data.casual_taxable_person.id).first()
#             if existing_casual_taxable_person:
#                 for key, value in customer_data.casual_taxable_person.model_dump(exclude_unset=True).items():
#                     setattr(existing_casual_taxable_person, key, value)
#                 existing_casual_taxable_person.effective_from_date=datetime.now()  # Set effective_from_date to current date
#                 existing_casual_taxable_person.effective_to_date=None
#                 existing_casual_taxable_person.modified_by = user_id
#                 existing_casual_taxable_person.modified_on = datetime.now()

#         # Handle Composition Option
#         if customer_data.option_for_composition.id == 0:
#             composition_option = CustomerGSTCompositionOptedPersonDetails(
#                 customer_id=customer_id,
#                 **customer_data.option_for_composition.model_dump(exclude_unset=True),
#                 effective_from_date=datetime.now(),  # Set effective_from_date to current date
#                 effective_to_date=None,
#                 created_by=user_id,
#                 created_on=datetime.now()
#             )
#             db.add(composition_option)
#         else:
#             existing_composition_option = db.query(CustomerGSTCompositionOptedPersonDetails).filter_by(id=customer_data.option_for_composition.id).first()
#             if existing_composition_option:
#                 for key, value in customer_data.option_for_composition.model_dump(exclude_unset=True).items():
#                     setattr(existing_composition_option, key, value)
#                 existing_composition_option.effective_from_date=datetime.now()  # Set effective_from_date to current date
#                 existing_composition_option.effective_to_date=None
#                 existing_composition_option.modified_by = user_id
#                 existing_composition_option.modified_on = datetime.now()

#         # Handle Other GST Details
#         if customer_data.reason_to_obtain_registration.id == 0:
#             gst_other_details = CustomerGSTOtherDetails(
#                 customer_id=customer_id,
#                 **customer_data.reason_to_obtain_registration.model_dump(exclude_unset=True),
#                 effective_from_date=datetime.now(),  # Set effective_from_date to current date
#                 effective_to_date=None,
#                 created_by=user_id,
#                 created_on=datetime.now()
#             )
#             db.add(gst_other_details)
#         else:
#             existing_gst_other_details = db.query(CustomerGSTOtherDetails).filter_by(id=customer_data.reason_to_obtain_registration.id).first()
#             if existing_gst_other_details:
#                 for key, value in customer_data.reason_to_obtain_registration.model_dump(exclude_unset=True).items():
#                     setattr(existing_gst_other_details, key, value)
#                 existing_gst_other_details.effective_from_date=datetime.now()  # Set effective_from_date to current date
#                 existing_gst_other_details.effective_to_date=None
#                 existing_gst_other_details.modified_by = user_id
#                 existing_gst_other_details.modified_on = datetime.now()

#         # Handle Existing Registrations
#         for registration in customer_data.existing_registrations:
#             if registration.id == 0:
#                 new_registration = CustomerExistingRegistrationDetails(
#                     customer_id=customer_id,
#                     **registration.model_dump(exclude_unset=True),
#                     effective_from_date=datetime.now(),  # Set effective_from_date to current date
#                     effective_to_date=None,
#                     created_by=user_id,
#                     created_on=datetime.now()
#                 )
#                 db.add(new_registration)
#             else:
#                 existing_registration = db.query(CustomerExistingRegistrationDetails).filter_by(id=registration.id).first()
#                 if existing_registration:
#                     for key, value in registration.model_dump(exclude_unset=True).items():
#                         setattr(existing_registration, key, value)
#                     existing_registration.effective_from_date=datetime.now()  # Set effective_from_date to current date
#                     existing_registration.effective_to_date=None
#                     existing_registration.modified_by = user_id
#                     existing_registration.modified_on = datetime.now()

#         # Handle Authorization
#         if customer_id >= 0:  # Check if it's an existing customer or a new customer
#             existing_authorization = db.query(CustomerMaster).filter_by(customer_id=customer_id).first()

#             if existing_authorization:  # Update the existing authorization
#                 for key, value in customer_data.authorization.model_dump(exclude_unset=True).items():
#                     setattr(existing_authorization, key, value)
#                 existing_authorization.effective_from_date = datetime.now()  
#                 existing_authorization.effective_to_date = None 
#                 existing_authorization.modified_by = user_id  
#                 existing_authorization.modified_on = datetime.now()  
#             else:  
#                 new_authorization = CustomerMaster(
#                     customer_id=customer_id,
#                     **customer_data.authorization.model_dump(exclude_unset=True),
#                     effective_from_date=datetime.now(),  
#                     effective_to_date=None,  
#                     created_by=user_id,  
#                     created_on=datetime.now()  
#                 )
#                 db.add(new_authorization)
#         # Commit transaction
#         db.commit()

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
def save_customer_details(customer_id: int, 
                          customer_data: CustomerRequestSchema, 
                          user_id: int, 
                          db: Session):
    try:
        # Handle Additional Trade Names
        for additional_trade_name in customer_data.additional_trade_name:
            if additional_trade_name.id == 0:
                new_trade_name = CustomerAdditionalTradeName(
                    customer_id=customer_id,
                    **additional_trade_name.model_dump(exclude_unset=True),
                    effective_from_date=datetime.now(),
                    effective_to_date=None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                db.add(new_trade_name)
            else:
                existing_trade_name = db.query(CustomerAdditionalTradeName).filter_by(id=additional_trade_name.id).first()
                if existing_trade_name:
                    for key, value in additional_trade_name.model_dump(exclude_unset=True).items():
                        setattr(existing_trade_name, key, value)
                    existing_trade_name.effective_from_date = datetime.now()
                    existing_trade_name.effective_to_date = None
                    existing_trade_name.modified_by = user_id
                    existing_trade_name.modified_on = datetime.now()

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
                    effective_from_date=datetime.now(),
                    effective_to_date=None,
                    created_by=user_id,
                    created_on=datetime.now()
                )
                db.add(new_registration)
            else:
                existing_registration = db.query(CustomerExistingRegistrationDetails).filter_by(id=registration.id).first()
                if existing_registration:
                    for key, value in registration.model_dump(exclude_unset=True).items():
                        setattr(existing_registration, key, value)
                    existing_registration.effective_from_date = datetime.now()
                    existing_registration.effective_to_date = None
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
                         user_id: int, 
                         ):
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
                "customer_number":customer.customer_number,
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
                "authorized_signatory_name_as_in_pan": customer.authorized_signatory_name_as_in_pan,
                "authorized_signatory_pan_number": customer.authorized_signatory_pan_number,
                "constitution_id": customer.constitution_id,
                "constitution_name": db.query(AppBusinessConstitution.business_constitution_name).filter_by(id=customer.constitution_id).scalar() if customer.constitution_id else None,
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
                    "gst_registration_required_from_date":casual_taxable_person.gst_registration_required_from_date if casual_taxable_person else None,
                    "gst_registration_required_to_date":casual_taxable_person.gst_registration_required_to_date if casual_taxable_person else None,
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
    

#------Save stakeholder


# def save_stakeholder_details(request: StakeHolderMasterSchema, 
#                              user_id: int,
#                              db: Session, 
#                              customer_id: int,
#                              stake_holder_type: str):  # Added `stake_holder_type` as a parameter
#     try:
#         # 1. Handle StakeHolderMaster
#         personal_info = request.personal_information
#         if personal_info.id == 0:
#             # Create new StakeHolderMaster
#             stake_holder_master = StakeHolderMaster(
#                 first_name=personal_info.first_name,
#                 middle_name=personal_info.middle_name,
#                 last_name=personal_info.last_name,
#                 fathers_first_name=personal_info.fathers_first_name,
#                 marital_status_id=personal_info.marital_status_id,
#                 date_of_birth=personal_info.date_of_birth,
#                 gender_id=personal_info.gender_id,
#                 din_number=personal_info.din_number,
#                 is_citizen_of_india=personal_info.is_citizen_of_india,
#                 pan_number=personal_info.pan_number,
#                 passport_number=personal_info.passport_number,
#                 aadhaar_number=personal_info.aadhaar_number,
#                 created_by=user_id,  # Set created_by field
#                 created_on=datetime.now()
#             )
#             db.add(stake_holder_master)
#         else:
#             # Update existing StakeHolderMaster
#             stake_holder_master = db.query(StakeHolderMaster).filter_by(id=personal_info.id).first()
#             if stake_holder_master:
#                 stake_holder_master.first_name = personal_info.first_name
#                 stake_holder_master.middle_name = personal_info.middle_name
#                 stake_holder_master.last_name = personal_info.last_name
#                 stake_holder_master.fathers_first_name = personal_info.fathers_first_name
#                 stake_holder_master.marital_status_id = personal_info.marital_status_id
#                 stake_holder_master.date_of_birth = personal_info.date_of_birth
#                 stake_holder_master.gender_id = personal_info.gender_id
#                 stake_holder_master.din_number = personal_info.din_number
#                 stake_holder_master.is_citizen_of_india = personal_info.is_citizen_of_india
#                 stake_holder_master.pan_number = personal_info.pan_number
#                 stake_holder_master.passport_number = personal_info.passport_number
#                 stake_holder_master.aadhaar_number = personal_info.aadhaar_number
#                 stake_holder_master.modified_by = user_id  # Set modified_by field
#                 stake_holder_master.modified_on = datetime.now()
#             else:
#                 return {"detail": "stake_holder_master not found"}

#         db.flush()  # Flush to get `stake_holder_master.id`

#         # 2. Handle StakeHolderContactDetails
#         for contact_details in request.contact_details:
#             if contact_details.id == 0:
#             # Create new contact details
#                 contact_detail_entry = StakeHolderContactDetails(
#                     stake_holder_id=stake_holder_master.id,
#                     mobile_number=contact_details.mobile_number,
#                     email_address=contact_details.email_address,
#                     telephone_number_with_std_code=contact_details.telephone_number_with_std_code,
#                     effective_from_date=datetime.now(),  # Set effective_from_date to current date
#                     effective_to_date=None,
#                     created_by=user_id,  # Set created_by field
#                     created_on=datetime.now()
#             )
#                 db.add(contact_detail_entry)
#             else:
#             # Update existing contact details
#                 contact_detail_entry = db.query(StakeHolderContactDetails).filter_by(id=contact_details.id).first()
#                 if contact_detail_entry:
#                     contact_detail_entry.mobile_number = contact_details.mobile_number
#                     contact_detail_entry.email_address = contact_details.email_address
#                     contact_detail_entry.telephone_number_with_std_code = contact_details.telephone_number_with_std_code
#                     contact_detail_entry.effective_from_date=datetime.now()  # Set effective_from_date to current date
#                     contact_detail_entry.effective_to_date=None
#                     contact_detail_entry.modified_by = user_id  # Set modified_by field
#                     contact_detail_entry.modified_on = datetime.now()
#                 else:
#                     return {"detail": "contact_detail not found"}

#             db.flush()  # Flush to get `contact_detail_entry.id`

#         # 3. Handle StakeHolderAddress
#         for addr in request.address:
#             if addr.address_type in ['RESIDENTIAL', 'PERMANENT', 'PRESENT', 'OFFICE']:
#                 if addr.id == 0:
#                     # Create new address
#                     address_entry = StakeHolderAddress(
#                         stake_holder_id=stake_holder_master.id,
#                         pin_code=addr.pin_code,
#                         address_type=addr.address_type,
#                         country_id=addr.country_id,
#                         state_id=addr.state_id,
#                         district_id=addr.district_id,
#                         city_id=addr.city_id,
#                         village_id=addr.village_id,
#                         post_office_id=addr.post_office_id,
#                         lsg_type_id=addr.lsg_type_id,
#                         lsg_id=addr.lsg_id,
#                         locality=addr.locality,
#                         road_street_name=addr.road_street_name,
#                         premises_building_name=addr.premises_building_name,
#                         building_flat_number=addr.building_flat_number,
#                         floor_number=addr.floor_number,
#                         landmark=addr.landmark,
#                         effective_from_date=datetime.now(),  # Set effective_from_date to current date
#                         effective_to_date=None,
#                         created_by=user_id,  # Set created_by field
#                         created_on=datetime.now()
#                     )
#                     db.add(address_entry)
#                 else:
#                     # Update existing address
#                     address_entry = db.query(StakeHolderAddress).filter_by(id=addr.id, address_type=addr.address_type).first()
#                     if address_entry:
#                         address_entry.pin_code = addr.pin_code
#                         address_entry.country_id = addr.country_id
#                         address_entry.state_id = addr.state_id
#                         address_entry.district_id = addr.district_id
#                         address_entry.city_id = addr.city_id
#                         address_entry.village_id = addr.village_id
#                         address_entry.post_office_id = addr.post_office_id
#                         address_entry.lsg_type_id = addr.lsg_type_id
#                         address_entry.lsg_id = addr.lsg_id
#                         address_entry.locality = addr.locality
#                         address_entry.road_street_name = addr.road_street_name
#                         address_entry.premises_building_name = addr.premises_building_name
#                         address_entry.building_flat_number = addr.building_flat_number
#                         address_entry.floor_number = addr.floor_number
#                         address_entry.landmark = addr.landmark
#                         address_entry.effective_from_date=datetime.now()  # Set effective_from_date to current date
#                         address_entry.effective_to_date=None
#                         address_entry.modified_by = user_id  # Set modified_by field
#                         address_entry.modified_on = datetime.now()
#                     else:
#                         return {"detail": "address_detail not found"}

#                 db.flush()  # Flush to get `address_entry.id`

#         # 4. Insert into the `customer_stakeholder` table
#         customer_stakeholder_entry = CustomerStakeHolder(
#             customer_id=customer_id,
#             stake_holder_master_id=stake_holder_master.id,
#             designation_id=request.identity_information[0].designation_id,  # Assuming identity_information[0] is valid
#             contact_details_id=contact_detail_entry.id,
#             residential_address_id=address_entry.id,
#             stake_holder_type=stake_holder_type, 
#             effective_from_date=datetime.now(),  # Set effective_from_date to current date
#             effective_to_date=None, # Save the stake_holder_type field
#             created_by=user_id,  # Set created_by field
#             created_on=datetime.now()
#         )
#         db.add(customer_stakeholder_entry)

#         # Commit the transaction
#         db.commit()

#         return {"message": "saved successfully"}

#     except Exception as e:
#         db.rollback()  # Roll back the transaction in case of error
#         raise HTTPException(status_code=500, detail=str(e))


def save_stakeholder_details(request: StakeHolderMasterSchema, 
                             user_id: int,
                             db: Session, 
                             customer_id: int,
                             stake_holder_type: str):  # Added `stake_holder_type` as a parameter
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
        for contact_details in request.contact_details:
            if contact_details.id == 0:
                # Create new contact details
                contact_detail_entry = StakeHolderContactDetails(
                    stake_holder_id=stake_holder_master.id,
                    mobile_number=contact_details.mobile_number,
                    email_address=contact_details.email_address,
                    telephone_number_with_std_code=contact_details.telephone_number_with_std_code,
                    effective_from_date=datetime.now(),  # Set effective_from_date to current date
                    effective_to_date=None,
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
                    contact_detail_entry.effective_from_date = datetime.now()  # Set effective_from_date to current date
                    contact_detail_entry.effective_to_date = None
                    contact_detail_entry.modified_by = user_id  # Set modified_by field
                    contact_detail_entry.modified_on = datetime.now()
                else:
                    return {"detail": "contact_detail not found"}

            db.flush()  # Flush to get `contact_detail_entry.id`

        # 3. Handle StakeHolderAddress
        for addr in request.address:
            if addr.address_type in ['RESIDENTIAL', 'PERMANENT', 'PRESENT', 'OFFICE']:
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
                        effective_from_date=datetime.now(),  # Set effective_from_date to current date
                        effective_to_date=None,
                        created_by=user_id,  # Set created_by field
                        created_on=datetime.now()
                    )
                    db.add(address_entry)
                else:
                    # Update existing address
                    address_entry = db.query(StakeHolderAddress).filter_by(id=addr.id).first()  # Removed address_type from filter
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
                        address_entry.effective_from_date = datetime.now()  # Set effective_from_date to current date
                        address_entry.effective_to_date = None
                        address_entry.modified_by = user_id  # Set modified_by field
                        address_entry.modified_on = datetime.now()
                    else:
                        return {"detail": "address_detail not found"}

                db.flush()  # Flush to get `address_entry.id`

        # 4. Check if the `CustomerStakeHolder` entry exists for this `customer_id` and `stake_holder_master_id`
        customer_stakeholder_entry = db.query(CustomerStakeHolder).filter_by(
            customer_id=customer_id,
            stake_holder_master_id=stake_holder_master.id
        ).first()

        if customer_stakeholder_entry:
            # Update existing CustomerStakeHolder
            customer_stakeholder_entry.designation_id = request.identity_information[0].designation_id  # Assuming identity_information[0] is valid
            customer_stakeholder_entry.contact_details_id = contact_detail_entry.id
            customer_stakeholder_entry.residential_address_id = address_entry.id
            customer_stakeholder_entry.stake_holder_type = stake_holder_type
            customer_stakeholder_entry.effective_from_date = datetime.now()  # Set effective_from_date to current date
            customer_stakeholder_entry.modified_by = user_id  # Set modified_by field
            customer_stakeholder_entry.modified_on = datetime.now()
        else:
            # Insert new CustomerStakeHolder
            customer_stakeholder_entry = CustomerStakeHolder(
                customer_id=customer_id,
                stake_holder_master_id=stake_holder_master.id,
                designation_id=request.identity_information[0].designation_id,  # Assuming identity_information[0] is valid
                contact_details_id=contact_detail_entry.id,
                residential_address_id=address_entry.id,
                stake_holder_type=stake_holder_type, 
                effective_from_date=datetime.now(),  # Set effective_from_date to current date
                effective_to_date=None,  # Save the stake_holder_type field
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

#--Get Stakeholder Details

def get_stakeholder_details(db: Session, 
                            customer_id: int, 
                            stakeholder_type: str,
                            user_id: int
                            ):
    try:
        # Fetch records from CustomerStakeHolder based on customer_id
        customer_stakeholders = db.query(CustomerStakeHolder).filter_by(customer_id=customer_id).all()

        if not customer_stakeholders:
            return []

        # Initialize an empty list to hold stakeholder details
        stakeholder_details = []

        for customer_stakeholder in customer_stakeholders:
            # Only process the stakeholder if the type matches
            if customer_stakeholder.stake_holder_type == stakeholder_type:
                # Fetch StakeHolderMaster record based on stake_holder_master_id
                stakeholder = db.query(StakeHolderMaster).filter_by(id=customer_stakeholder.stake_holder_master_id).first()
                
                if not stakeholder:
                    continue  # Skip if no stakeholder found for the given ID

                # Fetch other related details (designation, address, etc.)
                designation = db.query(AppDesignation).filter_by(id=customer_stakeholder.designation_id).first() if customer_stakeholder.designation_id else None
                address = db.query(StakeHolderAddress).filter_by(id=customer_stakeholder.residential_address_id).first() if customer_stakeholder.residential_address_id else None
                contact_details = db.query(StakeHolderContactDetails).filter_by(id=customer_stakeholder.contact_details_id).first() if customer_stakeholder.contact_details_id else None

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
                    } if contact_details else None,
                    "identity_information": {
                        "id": designation.id if designation else None,
                        "designation_id": designation.id if designation else None,
                        "designation": designation.designation if designation else None
                    } if designation else None,
                    "address": {
                        "id": address.id if address else None,
                        "pin_code": address.pin_code if address else None,
                        "address_type":address.address_type if address else None,
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
                        "lsg_type_id": address.lsg_type_id,
                        "lsg_type_name": db.query(AppViewVillages.lsg_type).filter_by(lsg_type_id=address.lsg_type_id).first().lsg_type if address.lsg_type_id else None,
                        "lsg_id": address.lsg_id,
                        "lsg_name": db.query(AppViewVillages.lsg_name).filter_by(lsg_id=address.lsg_id).first().lsg_name if address.lsg_id else None,
                        "locality": address.locality if address else None,
                        "road_street_name": address.road_street_name if address else None,
                        "building_flat_number": address.building_flat_number if address else None,
                        "landmark": address.landmark if address else None
                    } if address else None
                }

                # Append the response to the stakeholder details list
                stakeholder_details.append(response)

        return stakeholder_details if stakeholder_details else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----get activity
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


def save_business_place(customer_id: int, 
                        data: BusinessData, 
                        db: Session,
                        user_id: int,
                        id: int):
    try:
        # Start transaction
        with db.begin():
            # Check if we're creating a new business place or updating an existing one
            if id == 0:
                # Create new business place
                for business_place in data.business_place:
                    new_business_place = CustomerBusinessPlace(
                        **business_place.model_dump(exclude_unset=True),
                        customer_id=customer_id
                    )
                    db.add(new_business_place)
                    db.flush()  # Get the generated ID after insert
                    business_place_id = new_business_place.id
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
                    business_place_id = existing_business_place.id
                else:
                    raise HTTPException(status_code=404, detail="Business place not found for update.")

            # Process nature_of_business and activity types for the business place
            for nature in data.nature_of_business:
                if nature.id > 0:
                    existing_activity = db.query(CustomerBusinessPlaceActivity).filter_by(
                        id=nature.id,
                        customer_id=customer_id,
                        business_place_id=business_place_id
                    ).first()

                    if existing_activity:
                        existing_activity.business_activity_id = nature.business_activity_id
                else:
                    new_activity = CustomerBusinessPlaceActivity(
                        customer_id=customer_id,
                        business_place_id=business_place_id,
                        business_activity_id=nature.business_activity_id
                    )
                    db.add(new_activity)

            # Handle business activity type
            existing_activity_type = db.query(CustomerBusinessPlaceActivityType).filter_by(
                customer_id=customer_id,
                business_place_id=business_place_id
            ).first()

            if existing_activity_type:
                # Update the existing record
                existing_activity_type.business_activity_type_id = data.business_activity_type_id
            else:
                # Add a new record if none exists
                new_activity_type = CustomerBusinessPlaceActivityType(
                    customer_id=customer_id,
                    business_place_id=business_place_id,
                    business_activity_type_id=data.business_activity_type_id
                )
                db.add(new_activity_type)

            # Handle business activity master
            existing_core_activity = db.query(CustomerBusinessPlaceCoreActivity).filter_by(
                customer_id=customer_id,
                business_place_id=business_place_id
            ).first()

            if existing_core_activity:
                # Update the existing record
                existing_core_activity.business_activity_master_id = data.business_activity_master_id
            else:
                # Add a new record if none exists
                new_core_activity = CustomerBusinessPlaceCoreActivity(
                    customer_id=customer_id,
                    business_place_id=business_place_id,
                    business_activity_master_id=data.business_activity_master_id
                )
                db.add(new_core_activity)

            # Commit the transaction after all operations
            db.commit()

        return {"message": "Data saved successfully"}

    except AttributeError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Attribute Error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#-----get business_place----

def get_business_place(customer_id: int, 
                       type: str, 
                       db: Session,
                       user_id: int
                       ):
    """
    Fetch business data from the database.
    """
    is_principal_place = 'yes' if type == 'PRINCIPAL_PLACE_ADDRESS' else 'no'

    try:
        # Fetch business places
        business_places = db.query(CustomerBusinessPlace).filter(
            CustomerBusinessPlace.customer_id == customer_id,
            CustomerBusinessPlace.is_principal_place == is_principal_place
        ).all()

        # If no business places found, return an empty list
        if not business_places:
            return []

        # Prepare business places response
        business_places_response = []
        nature_of_business_response = []

        # Iterate over business places
        for bp in business_places:
            # Fetch business activity type and master details
            business_activity_type = db.query(CustomerBusinessPlaceActivityType).filter(
                CustomerBusinessPlaceActivityType.business_place_id == bp.id
            ).first()
            business_activity_master = db.query(CustomerBusinessPlaceCoreActivity).filter(
                CustomerBusinessPlaceCoreActivity.business_place_id == bp.id
            ).first()

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
                "nature_of_possession": db.query(OffNatureOfPossession.nature_of_possession).filter_by(id=bp.nature_of_possession_id).scalar() if bp.nature_of_possession_id else None,
            }

            # Add activity type and master details to the business place data
            if business_activity_type:
                business_place_data.update({
                    "business_activity_type_id": business_activity_type.business_activity_type_id,
                    "business_activity_type_name": db.query(BusinessActivityType).filter(
                        BusinessActivityType.id == business_activity_type.business_activity_type_id
                    ).first().business_activity_type if business_activity_type.business_activity_type_id else None,
                })

            if business_activity_master:
                business_place_data.update({
                    "business_activity_master_id": business_activity_master.business_activity_master_id,
                    "business_activity_master_name": db.query(BusinessActivityMaster).filter(
                        BusinessActivityMaster.id == business_activity_master.business_activity_master_id
                    ).first().business_activity if business_activity_master.business_activity_master_id else None,
                })

            # Append business place data to response
            business_places_response.append(business_place_data)

            # Get business activities
            business_activities = db.query(CustomerBusinessPlaceActivity).filter(
                CustomerBusinessPlaceActivity.business_place_id == bp.id
            ).all()

            # Compile each business activity
            for ba in business_activities:
                activity_data = {
                    "id": ba.id,
                    "business_activity_id": ba.business_activity_id,
                    "business_activity_name": db.query(BusinessActivity).filter(BusinessActivity.id == ba.business_activity_id).first().business_activity if ba.business_activity_id else None
                }
                nature_of_business_response.append(activity_data)

        # Compile final response
        response = {
            "business_places": business_places_response,
            "business_activity_type_id": business_places_response[0].get("business_activity_type_id") if business_places_response else None,
            "business_activity_type_name": business_places_response[0].get("business_activity_type_name") if business_places_response else None,
            "business_activity_master_id": business_places_response[0].get("business_activity_master_id") if business_places_response else None,
            "business_activity_master_name": business_places_response[0].get("business_activity_master_name") if business_places_response else None,
            "nature_of_business": nature_of_business_response
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#-------------Get hsn sac


def get_hsn_sac_data(hsn_sac_class_id: int,
                       hsn_sac_code: str,
                       db: Session,
                       user_id: int
                       ):
    
    try:
        # Base query
        query = db.query(AppHsnSacMaster, AppHsnSacClasses.hsn_sac_class).join(
            AppHsnSacClasses, AppHsnSacMaster.hsn_sac_class_id == AppHsnSacClasses.id
        )

        # Filter based on hsn_sac_class_id and hsn_sac_code
        if hsn_sac_class_id:
            query = query.filter(AppHsnSacMaster.hsn_sac_class_id == hsn_sac_class_id)

        if hsn_sac_code:
            query = query.filter(AppHsnSacMaster.hsn_sac_code == hsn_sac_code)

        # Execute the query
        results = query.all()

        # If no records are found, raise an exception
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

def save_goods_commodities_details(
    id: int,  # 0 for insert, non-zero for update
    customer_id: int,
    details: CustomerGoodsCommoditiesSupplyDetailsSchema,
    db: Session,
    user_id: int  # Optionally track the user making the changes
):
    try:
        # Use model_dump to get the details as a dictionary
        detail_data = details.model_dump(exclude_unset=True)  # Only include set fields

        if id == 0:
            # Create a new entry if ID is 0
            new_entry = CustomerGoodsCommoditiesSupplyDetails(
                customer_id=customer_id,
                hsn_sac_class_id=detail_data['hsn_sac_class_id'],
                hsn_sac_code_id=detail_data['hsn_sac_code_id'],
                effective_from_date=date.today(),  # Set effective_from_date to current date
                effective_to_date=None,              # Set effective_to_date as None
                created_by=user_id,               
                created_on=datetime.now()            
            )
            db.add(new_entry)
            db.commit()  # Commit to save the new entry
            db.refresh(new_entry)  # Refresh to get the updated instance with id

            return {"success": True, "message": "Data saved successfully"}

        else:
            # Fetch the existing record by ID for updating
            existing_entry = db.query(CustomerGoodsCommoditiesSupplyDetails).filter_by(id=id).first()

            if not existing_entry:
                return []

            # Update the existing record fields
            existing_entry.hsn_sac_class_id = detail_data['hsn_sac_class_id']
            existing_entry.hsn_sac_code_id = detail_data['hsn_sac_code_id']
            existing_entry.modified_on = datetime.now() 
            existing_entry.modified_by = user_id  

            db.commit()  # Commit the changes to the database

            return {"success": True, "message": "Data updated successfully"}

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=500, detail=str(e))
    


#----------------get Hsn Commodities Supply Details
def get_hsn_commodities_by_customer_id(customer_id: int,
                                        user_id: int, 
                                        db: Session):
    try:
        # Query the CustomerGoodsCommoditiesSupplyDetails for the given customer_id
        commodities = (
            db.query(CustomerGoodsCommoditiesSupplyDetails)
            .filter(CustomerGoodsCommoditiesSupplyDetails.customer_id == customer_id)
            .all()
        )

        if not commodities:
            return []  # Return an empty list if no commodities found

        response = []
        for commodity in commodities:
            # Fetching hsn_sac_class from AppHsnSacClasses based on hsn_sac_class_id
            hsn_class_details = ( 
                db.query(AppHsnSacClasses)
                .filter(AppHsnSacClasses.id == commodity.hsn_sac_class_id)
                .first()
            )

            # Fetching hsn_sac_code and hsn_sac_description from AppHsnSacMaster based on hsn_sac_code_id
            hsn_details = (
                db.query(AppHsnSacMaster)
                .filter(AppHsnSacMaster.id == commodity.hsn_sac_code_id)
                .first()
            )

            if hsn_class_details and hsn_details:
                response.append({
                    "hsn_sac_class_id": hsn_class_details.id,
                    "hsn_sac_class": hsn_class_details.hsn_sac_class,  
                    "hsn_sac_code_id": hsn_details.id,
                    "hsn_sac_code": hsn_details.hsn_sac_code,
                    "hsn_sac_description": hsn_details.hsn_sac_description,
                })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#----- save Customer Gst State Specific Information


def save_customer_gst_state_specific_information(
    id: int,  # 0 for insert, non-zero for update
    customer_id: int,
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
                **detail_data,
                created_by=user_id,
                created_on=datetime.now()  # Set created_on to current datetime
            )
            db.add(new_entry)
            db.commit()  # Commit to save the new entry
            db.refresh(new_entry)  # Refresh to get the updated instance with id

            return {"success": True, "message": "New GST state-specific information saved successfully"}

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

            return {"success": True, "message": "GST state-specific information updated successfully"}

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=500, detail=str(e))
    

#----------get Customer Gst State Specific Information

def get_gst_state_specific_information_by_customer_id(customer_id: int, 
                                                      db: Session,
                                                      user_id:int) -> List[CustomerGstStateSpecificInformation]:
    try:
        # Query the CustomerGstStateSpecificInformation for the given customer_id
        gst_info_records = (
            db.query(CustomerGstStateSpecificInformation)
            .filter(CustomerGstStateSpecificInformation.customer_id == customer_id, 
                    CustomerGstStateSpecificInformation.is_deleted == 'no')  # Optionally filter out deleted records
            .all()
        )

        if not gst_info_records:
            return []  # Return an empty list if no records found

        return gst_info_records

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




#-------jurisdicition




def get_details_by_pin(db: Session, pin: str,user_id:int) -> List[RangeDetailsSchema]:
    try:
        # Query the view where jurisdiction contains the PIN or pin matches the PIN
        range_details = db.query(GstViewRange).filter(
            or_(
                GstViewRange.jurisdiction.contains(pin),
                GstViewRange.pin == pin
            )
        ).all()  # Fetch all matching records

        if range_details:
            # Manually create RangeDetailsSchema instances from SQLAlchemy model attributes
            range_info_list = [
                RangeDetailsSchema(
                    Range_id=range_detail.range_id,
                    Range=range_detail.range_name,
                    Division_id=range_detail.division_id,
                    Division=range_detail.division_name,
                    Commissionerate_id=range_detail.commissionerate_id,
                    Commissionerate=range_detail.commissionerate_name,
                    Zone_id=range_detail.zone_id,
                    Zone=range_detail.zone_name,
                    State_id=range_detail.state_id,
                    State=range_detail.state_name,
                    District_id=range_detail.district_id,
                    District=range_detail.district_name,
                    Country_id=range_detail.country_id,
                    Country=range_detail.country_name_english
                )
                for range_detail in range_details
            ]
            return range_info_list  # Return list of matching range details
        else:
            return []  # Return an empty list if no results are found
            
    except Exception as e:
        # Properly handle exceptions and provide useful feedback
        raise HTTPException(status_code=500, detail=f"Error occurred while fetching details: {str(e)}")
