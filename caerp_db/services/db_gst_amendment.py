
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






#-----------------------------------------------------------------------------------------------------------------


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


#-----------------------------------------------------------------------------------------------------------------


def save_amended_data(db: Session, id: int, model_name: str, field_name: str, new_value, date: datetime, remarks: str,user_id:int):
  
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
    record.created_by = user_id  
    record.created_on = datetime.now()

    # Insert record into off_service_task_history table
    db.execute(
        text("""
            INSERT INTO off_service_task_history 
            (service_task_master_id, history_updated_on, history_update_by, history_description)
            VALUES (:service_task_master_id, :history_updated_on, :history_update_by, :history_description)
        """),
        {
            "service_task_master_id": record.service_task_id,  # Use the service_task_id from the record
            "history_updated_on": datetime.now(),
            "history_update_by": user_id,
            "history_description": f"Amendment operation performed on {model_name} table via the Save Amended Data endpoint by user ID {user_id}. Field '{field_name}' changed from '{current_value}' to '{new_value}'."
        }
    )

     # Commit changes
    db.commit()

    return {"success": True, "message": "Amendment saved successfully", "id": id}


#----------------------------------------------------------------------------------------------------


def amend_additional_trade_names_in_db(
    db: Session,
    customer_id: int,
    service_task_id: int,
    amendment_data: AdditionalTradeNameAmendment,
    created_by: int,
    action: AmendmentAction
):
    amendments = amendment_data.amendments
    remarks = amendment_data.remarks
    result = {"added": [], "updated": [], "errors": []}

    try:
        print(f"Checking if service_task_id {service_task_id} exists for customer_id {customer_id}...")
        existing_service_task = db.execute(
            text("""
                SELECT * FROM customer_additional_trade_name 
                WHERE service_task_id = :service_task_id AND customer_id = :customer_id
            """),
            {"service_task_id": service_task_id, "customer_id": customer_id}
        ).fetchone()

        if not existing_service_task:
            print(f"No existing service_task found. Inserting new service task {service_task_id}.")
            for amendment in amendments:
                trade_name = amendment.new_trade_name.strip()
                db.execute(
                    text("""
                        INSERT INTO customer_additional_trade_name 
                        (service_task_id, customer_id, created_by, is_amendment, amendment_action, amendment_status, additional_trade_name, amendment_reason)
                        VALUES (:service_task_id, :customer_id, :created_by, :is_amendment, :amendment_action, :amendment_status, :additional_trade_name, :amendment_reason)
                    """),
                    {
                        "service_task_id": service_task_id,
                        "customer_id": customer_id,
                        "created_by": created_by,
                        "is_amendment": 'yes',
                        "amendment_action": 'ADDED',
                        "amendment_status": 'CREATED',
                        "additional_trade_name": trade_name,
                        "amendment_reason": remarks
                    }
                )
                last_inserted_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
                print(f"Last inserted ID: {last_inserted_id}")
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

        for amendment in amendments:
            trade_name = amendment.new_trade_name.strip()
            effective_from_date = amendment.request_date

            if amendment.id == 0:
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
                            (customer_id, additional_trade_name, created_by, service_task_id, is_amendment, amendment_action, amendment_status, amendment_reason)
                            VALUES (:customer_id, :additional_trade_name, :created_by, :service_task_id, :is_amendment, :amendment_action, :amendment_status, :amendment_reason)
                        """),
                        {
                            "customer_id": customer_id,
                            "additional_trade_name": trade_name,
                            "created_by": created_by,
                            "service_task_id": service_task_id,
                            "is_amendment": 'yes',
                            "amendment_action": 'ADDED',
                            "amendment_status": 'CREATED',
                            "amendment_reason": remarks
                        }
                    )
                    last_inserted_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
                    print(f"Last inserted ID: {last_inserted_id}")
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
                existing_trade_name = db.execute(
                    text("""
                        SELECT effective_from_date FROM customer_additional_trade_name 
                        WHERE id = :id
                    """),
                    {"id": amendment.id}
                ).fetchone()

                if existing_trade_name and existing_trade_name[0]:
                    print(f"Duplicating and updating trade_name {trade_name} for customer_id {customer_id}.")
                    db.execute(
                        text("""
                            INSERT INTO customer_additional_trade_name 
                            (customer_id, additional_trade_name, effective_from_date, effective_to_date, created_by, service_task_id, amended_parent_id, is_amendment, amendment_action, amendment_status, amendment_reason)
                            VALUES (:customer_id, :additional_trade_name, NULL, NULL, :created_by, :service_task_id, :amended_parent_id, :is_amendment, :amendment_action, :amendment_status, :amendment_reason)
                        """),
                        {
                            "customer_id": customer_id,
                            "additional_trade_name": trade_name,
                            "created_by": created_by,
                            "service_task_id": service_task_id,
                            "amended_parent_id": amendment.id,
                            "is_amendment": 'yes',
                            "amendment_action": 'EDITED',
                            "amendment_status": 'CREATED',
                            "amendment_reason": remarks
                        }
                    )
                    result["updated"].append(f"Trade name {trade_name} duplicated and updated for customer {customer_id}.")
                else:
                    print(f"Updating trade_name {trade_name} for customer_id {customer_id} without duplication.")
                    db.execute(
                        text("""
                            UPDATE customer_additional_trade_name
                            SET additional_trade_name = :additional_trade_name,
                                service_task_id = :service_task_id,
                                amendment_reason = :amendment_reason
                            WHERE id = :id
                        """),
                        {
                            "additional_trade_name": trade_name,
                            "service_task_id": service_task_id,
                            "amendment_reason": remarks,
                            "id": amendment.id
                        }
                    )
                    result["updated"].append(f"Trade name {trade_name} updated for customer {customer_id} without duplication.")

        # Insert record into off_service_task_history table
        db.execute(
            text("""
                INSERT INTO off_service_task_history 
                (service_task_master_id, history_updated_on, history_update_by, history_description)
                VALUES (:service_task_master_id, :history_updated_on, :history_update_by, :history_description)
            """),
            {
                "service_task_master_id": service_task_id,
                "history_updated_on": datetime.now(),
                "history_update_by": created_by,
                "history_description": f"Amendment operation performed on customer_additional_trade_name table via the Amend Additional Trade Names page by user ID {created_by}."
            }
        )
        
        db.commit()
        print("Changes committed successfully.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        result["errors"].append(str(e))

    return {"success": True, "message": "Amendments processed successfully", "details": result}

#----------------------------------------------------------------------------------------------------------------

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

            db.execute(
                text("""
                    INSERT INTO off_service_task_history 
                    (service_task_master_id, history_updated_on, history_update_by, history_description)
                    VALUES (:service_task_master_id, :history_updated_on, :history_update_by, :history_description)
                """),
                {
                    "service_task_master_id": service_task_id,
                    "history_updated_on": datetime.now(),
                    "history_update_by": user_id,
                    "history_description": f"Stakeholder of type {stakeholder_type} added for customer ID {customer_id} by user ID {user_id}."
                }
            )

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

#--------------------------------------------------------------------------------------------------------------------
def create_duplicate_business_place(db: Session, original_place: CustomerBusinessPlace, amendment_details: CustomerBusinessPlaceAmendmentSchema, service_task_id: int, id: Optional[int] = None) -> CustomerBusinessPlace:
    # Convert the original place to a schema
    business_place_data = CustomerBusinessPlaceAmendmentSchema.from_orm(original_place)

    # Prepare the data for the new business place
    original_data = business_place_data.dict(exclude_unset=True)
    print(f"Original data: {original_data}")

    # Explicitly create a new dictionary without the 'id' field
    new_place_data = {key: value for key, value in original_data.items() if key != 'id'}
    new_place_data.pop('amendment_date', None)
    new_place_data.pop('amendment_reason', None)
    print(f"Data after removing 'id': {new_place_data}")

    # Create a new business place with 'id' set to None to enable auto-increment
    new_place = CustomerBusinessPlace(
        customer_id=original_place.customer_id,
        **new_place_data,
        effective_from_date=None,
        effective_to_date=None,
        amended_parent_id=original_place.id,
        is_amendment='yes',
        amendment_date=datetime.now(),
        amendment_reason=amendment_details.amendment_reason or "Not provided",
        amendment_status="CREATED",
        amendment_action="EDITED",
        service_task_id=service_task_id
    )

    # Set additional fields from amendment details
    for key, value in amendment_details.dict(exclude_unset=True).items():
        setattr(new_place, key, value)

    print(f"New business place being added: {new_place.__dict__}")

    db.add(new_place)
    db.commit()
    db.refresh(new_place)

    return new_place

def amend_business_place_data(
    db: Session, customer_id: int, service_task_id: int, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, action: AmendmentAction, user_id: int, id: Optional[int] = None
):
    try:
        print(f"Processing amendment for customer_id: {customer_id}, user_id: {user_id}, action: {action}, id: {id}")

        # Ensure 'id' is provided
        if id is None:
            raise HTTPException(status_code=400, detail="Business place ID is required for updates")

        # Fetch the existing place using the provided id
        existing_place = fetch_existing_business_place(db, id)

        # Check if there are changes between the existing place and amendment details
        has_changes = any(
            getattr(existing_place, key, None) != value
            for key, value in amendment_details.business_place[0].dict(exclude_unset=True).items()
        )

        if has_changes:
            if existing_place.effective_from_date:
                print("Changes detected and effective_from_date is present. Creating a duplicate record...")
                new_business_place = create_duplicate_business_place(
                    db, existing_place, amendment_details.business_place[0], service_task_id, id
                )
                description = f"Business place duplicated and updated for customer ID {customer_id} by user ID {user_id}."
            else:
                print("Changes detected but no effective_from_date. Updating the existing record.")
                new_business_place = update_business_place(
                    db, id, amendment_details.business_place[0]
                )
                description = f"Business place updated for customer ID {customer_id} by user ID {user_id}."
        else:
            print("No changes detected. Keeping the existing record.")
            new_business_place = existing_place
            description = f"No changes made to business place for customer ID {customer_id} by user ID {user_id}."

        log_history(db, service_task_id, user_id, description)

        # Handle business activities
        handle_business_activities(db, customer_id, id, new_business_place.id, amendment_details, service_task_id)

        print("Amendment process completed successfully.")
        return {"success": True, "id": new_business_place.id}

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error during amendment: {e}")
        return {"success": False, "message": str(e)}


# Fetch existing business place
def fetch_existing_business_place(db: Session, place_id: int) -> CustomerBusinessPlace:
    existing_place = db.query(CustomerBusinessPlace).filter_by(id=place_id).first()
    if not existing_place:
        raise HTTPException(status_code=404, detail="Business place not found")
    return existing_place

# Update existing business place
def update_business_place(db: Session, place_id: int, amendment_details: CustomerBusinessPlaceAmendmentSchema):
    existing_place = fetch_existing_business_place(db, place_id)
    
    for key, value in amendment_details.dict(exclude_unset=True).items():
        setattr(existing_place, key, value)
    
    existing_place.amendment_date = datetime.now()
    existing_place.amendment_reason = amendment_details.amendment_reason or "Not provided"
    existing_place.amendment_status = "CREATED"
    existing_place.amendment_action = "EDITED"
    
    db.commit()
    return existing_place

# Log history
def log_history(db: Session, service_task_id: int, user_id: int, description: str):
    try:
        print("Inserting log entry into history...")
        db.execute(
            text("""
                INSERT INTO off_service_task_history 
                (service_task_master_id, history_updated_on, history_update_by, history_description)
                VALUES (:service_task_master_id, :history_updated_on, :history_update_by, :history_description)
            """),
            {
                "service_task_master_id": service_task_id,
                "history_updated_on": datetime.now(),
                "history_update_by": user_id,
                "history_description": description
            }
        )
        print("Committing log entry...")
        db.commit()
        print("Log entry committed successfully.")
    except SQLAlchemyError as e:
        print(f"Error inserting log entry: {e}")
        db.rollback()
        raise e

def handle_business_activities(db: Session, customer_id: int, original_place_id: int, new_place_id: int, amendment_details: CustomerBusinessPlaceFullAmendmentSchema, service_task_id: int):
    existing_activities = db.query(CustomerBusinessPlaceActivity).filter_by(business_place_id=original_place_id, customer_id=customer_id).all()
    
    # Step 1: Duplicate existing activities
    duplicated_activities = []
    for activity in existing_activities:
        new_activity = CustomerBusinessPlaceActivity(
            customer_id=activity.customer_id,
            business_place_id=new_place_id,
            business_activity_id=activity.business_activity_id,
            is_amendment='yes',
            amendment_action="EDITED",  # Ensure this is a valid ENUM value
            amendment_date=datetime.now(),
            amendment_reason=activity.amendment_reason,
            effective_from_date=activity.effective_from_date,
            effective_to_date=activity.effective_to_date,
            amended_parent_id=activity.id,
            service_task_id=service_task_id
        )
        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)
        duplicated_activities.append(new_activity)

    # Step 2: Process each activity in the JSON
    activity_ids_in_json = [activity.id for activity in amendment_details.nature_of_business]
    
    for activity in amendment_details.nature_of_business:
        if activity.id == 0:
            # New activity
            new_activity = CustomerBusinessPlaceActivity(
                customer_id=customer_id,
                business_place_id=new_place_id,
                business_activity_id=activity.business_activity_id,
                is_amendment='yes',
                amendment_action="ADDED",  # Ensure this is a valid ENUM value
                amendment_date=activity.amendment_date,
                amendment_reason=activity.amendment_reason,
                service_task_id=service_task_id
            )
            db.add(new_activity)
            db.commit()
        else:
            existing_activity = db.query(CustomerBusinessPlaceActivity).filter_by(id=activity.id, business_place_id=original_place_id, customer_id=customer_id).first()
            if existing_activity:
                if activity.id in activity_ids_in_json:
                    # Duplicate the existing activity
                    new_activity = CustomerBusinessPlaceActivity(
                        customer_id=customer_id,
                        business_place_id=new_place_id,
                        business_activity_id=activity.business_activity_id,
                        is_amendment='yes',
                        amendment_action="EDITED",  # Ensure this is a valid ENUM value
                        amendment_date=activity.amendment_date,
                        amendment_reason=activity.amendment_reason,
                        service_task_id=service_task_id,
                        amended_parent_id=existing_activity.id
                    )
                    db.add(new_activity)
                    db.commit()
                    db.refresh(new_activity)
                else:
                    # Mark activity as deleted
                    if existing_activity.id == existing_activity.amended_parent_id:
                        existing_activity.is_deleted = 'yes'
                    else:
                        existing_activity.amendment_action = "DELETED"  # Ensure this is a valid ENUM value
                    db.commit()

#--------------------------------------------------------------------------------------------------------


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
            # .filter(CustomerBusinessPlace.is_amendment == 'yes')
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
