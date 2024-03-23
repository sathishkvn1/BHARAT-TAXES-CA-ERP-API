


from caerp_db.common.models import CityDB, ConstitutionTypes, CountryDB, CurrencyDB, DistrictDB, Gender, NationalityDB, PanCard, PostOfficeTypeDB, PostOfficeView, PostalCircleDB, PostalDeliveryStatusDB, PostalDivisionDB, PostalRegionDB, Profession, Qualification, StateDB, TalukDB
from sqlalchemy.orm import Session
from fastapi import HTTPException ,status

from caerp_schema.common.common_schema import ConstitutionTypeForUpdate, ProfessionSchemaForUpdate, QualificationSchemaForUpdate     

def get_countries(db: Session):
    return db.query(CountryDB).all()



def get_country_by_id(db: Session, country_id: int):
    return db.query(CountryDB).filter(CountryDB.id == country_id).first()


def get_states_by_country(db: Session, country_id: int):
    return db.query(StateDB).filter(StateDB.country_id == country_id).all()


def get_state_by_id(db: Session, state_id: int):
    return db.query(StateDB).filter(StateDB.id == state_id).first()

def get_districts_by_state(db: Session, state_id: int):
    return db.query(DistrictDB).filter(DistrictDB.state_id == state_id).all()

def get_district_by_id(db: Session, district_id: int):
    return db.query(DistrictDB).filter(DistrictDB.id == district_id).first()


def get_cities_by_country_and_state(db: Session, country_id: int, state_id: int):
    return db.query(CityDB).filter(
        CityDB.country_id == country_id,
        CityDB.state_id == state_id
    ).all()
    
    

def get_city_by_id(db: Session, city_id: int):
    return db.query(CityDB).filter(CityDB.id == city_id).first()

def get_taluks_by_state(db: Session, state_id: int):
    return db.query(TalukDB).filter(TalukDB.state_id == state_id).all()

def get_taluks_by_district(db: Session, district_id: int):
    return db.query(TalukDB).filter(TalukDB.district_id == district_id).all()

def get_taluk_by_id(db: Session, taluk_id: int):
    return db.query(TalukDB).filter(TalukDB.id == taluk_id).first()

def get_all_currencies(db: Session):
    return db.query(CurrencyDB).all()

def get_currency_by_id(db: Session, currency_id: int):
    return db.query(CurrencyDB).filter(CurrencyDB.id == currency_id).first()


def get_all_nationality(db: Session):
    return db.query(NationalityDB).all()

def get_nationality_by_id(db: Session, nationality_id: int):
    return db.query(NationalityDB).filter(NationalityDB.id == nationality_id).first()

def get_all_post_office_types(db: Session):
    return db.query(PostOfficeTypeDB).all()

def get_post_office_type_by_id(db: Session, id: int):
    return db.query(PostOfficeTypeDB).filter(PostOfficeTypeDB.id == id).first()

def get_all_postal_delivery_statuses(db: Session):
    return db.query(PostalDeliveryStatusDB).all()

def get_postal_delivery_status_by_id(db: Session, id: int):
    return db.query(PostalDeliveryStatusDB).filter(PostalDeliveryStatusDB.id == id).first()

def get_all_postal_circles(db: Session):
    return db.query(PostalCircleDB).all()


def get_postal_circle_by_id(db: Session, id: int):
    return db.query(PostalCircleDB).filter(PostalCircleDB.id == id).first()

def get_all_postal_regions(db: Session):
    return db.query(PostalRegionDB).all()

def get_postal_regions_by_circle_id(db: Session, circle_id: int):
    return db.query(PostalRegionDB).filter(PostalRegionDB.circle_id == circle_id).all()

def get_postal_region_by_id(db: Session, region_id: int):
    return db.query(PostalRegionDB).filter(PostalRegionDB.id == region_id).first()

def get_all_postal_divisions(db: Session):
    return db.query(PostalDivisionDB).all()

def get_postal_divisions_by_circle_id(db: Session, circle_id: int):
    divisions = db.query(PostalDivisionDB).filter(PostalDivisionDB.circle_id == circle_id).all()
    return divisions


def get_postal_divisions_by_region_id(db: Session, region_id: int):
    return db.query(PostalDivisionDB).filter_by(region_id=region_id).all()

def get_postal_division_by_id(db: Session, division_id: int):
    return db.query(PostalDivisionDB).filter_by(id=division_id).first()


def get_post_offices_by_pincode(db: Session, pincode: str):
    return db.query(PostOfficeView).filter(PostOfficeView.pin_code == pincode).all()

def get_all_gender(db: Session):
    return db.query(Gender).all()

def get_gender_by_id(db: Session, gender_id: int):
    return db.query(Gender).filter(Gender.id == gender_id).first()


def get_all_pan_cards(db: Session):
    return db.query(PanCard).all()

def get_pan_card_by_id(db: Session, pancard_id: int):
    return db.query(PanCard).filter(PanCard.id == pancard_id).first()

def get_pan_card_by_code_type(db: Session, code_type: str):
    return db.query(PanCard).filter(PanCard.pan_card_type_code == code_type).first()


def get_all_qualification(db: Session):
    return db.query(Qualification).all()

def update_qualification(db: Session, request: QualificationSchemaForUpdate, id: int):
    qualification = db.query(Qualification).filter(Qualification.id == id).first()
    if qualification is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Qualification not found")
    qualification_data_dict = request.dict()
    for key, value in qualification_data_dict.items():
            setattr(qualification, key, value)

    db.commit()
    db.refresh(qualification)
    return qualification

def get_all_constitution(db: Session):
    return db.query(ConstitutionTypes).all()


def update_constitution(db: Session, request: ConstitutionTypeForUpdate, id: int):
    constitution = db.query(ConstitutionTypes).filter(ConstitutionTypes.id == id).first()
    if constitution is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="constitution not found")
    constitution_data_dict = request.dict()
    for key, value in constitution_data_dict.items():
            setattr(constitution, key, value)

    db.commit()
    db.refresh(constitution)
    return constitution


def get_all_profession(db: Session):
    return db.query(Profession).all()

def update_profession(db: Session, request: ProfessionSchemaForUpdate, id: int):
    profession = db.query(Profession).filter(Profession.id == id).first()
    if profession is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profession not found")
    profession_data_dict = request.dict()
    for key, value in profession_data_dict.items():
            setattr(profession, key, value)
    
    db.commit()
    db.refresh(profession)
    return profession
