import random
import re
from fastapi import APIRouter,Depends,HTTPException, WebSocket,status,Query
import httpx
from pydantic import BaseModel
from caerp_auth.authentication import authenticate_user
from caerp_db.common.models import   AppBankMaster, CountryDB,  NationalityDB, QueryManager, QueryManagerQuery,UserBase, UserRegistration
from caerp_schema.common.common_schema import BankMasterBase, CityDetail, CityResponse, ConstitutionTypeForUpdate, ConstitutionTypeSchemaResponse, ConsultancyServiceCreate, CountryCreate, CountryDetail, CurrencyDetail, DistrictDetailByState, DistrictResponse, EducationSchema, GenderSchemaResponse, NationalityDetail, NotificationSchema, PancardSchemaResponse, PostOfficeListResponse, PostOfficeTypeDetail, PostalCircleDetail, PostalDeliveryStatusDetail, PostalDivisionDetail, PostalRegionDetail, ProfessionSchemaForUpdate, ProfessionSchemaResponse, QualificationSchemaResponse, QueryManagerQuerySchema, QueryManagerQuerySchemaForGet, QueryManagerSchema, QueryManagerViewSchema, QueryStatus, QueryViewSchema, StatesByCountry,StateDetail, TalukDetail, TalukResponse, TalukResponseByDistrict, UserRegistrationCreate, VillageResponse

from caerp_db.common.models import PaymentsMode,PaymentStatus,RefundStatus,RefundReason
from caerp_schema.common.common_schema import PaymentModeSchema,PaymentModeSchemaForGet,PaymentStatusSchema,PaymentStatusSchemaForGet,RefundStatusSchema,RefundStatusSchemaForGet,RefundReasonSchema,RefundReasonSchemaForGet
from caerp_db.database import get_db
from sqlalchemy.orm import Session
from caerp_db.common import db_common, db_user
from caerp_constants.caerp_constants import CRUD, ActionType,  DeletedStatus
from typing import List, Optional
from caerp_auth import oauth2
from datetime import date, datetime
from sqlalchemy import text

import io
import os
import wave
import json
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse


router = APIRouter(
    
    tags = ['COMMON FUNCTIONS']
)






@router.get("/country", response_model=List[CountryCreate])
def get_all_countries(db: Session = Depends(get_db),
                      token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve all countries.

    This endpoint retrieves a list of all countries available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[CountryCreate]: A list of countries with their IDs and names.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    countries = db_common.get_countries(db)
    return countries






@router.get("/country/{country_id}", response_model=CountryDetail)
def get_country_by_id(country_id: int,
                      db: Session = Depends(get_db),
                      token: str = Depends(oauth2.oauth2_scheme)):
    
    """
    Retrieve a country by ID.

    This endpoint retrieves a country from the database based on its ID.

    Parameters:
    - `country_id` (path parameter): The unique identifier of the country.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - CountryDetail: Details of the country identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If the country with the specified ID is not found.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    country = db_common.get_country_by_id(db, country_id)
    if country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    return country



@router.get("/states/{country_id}", response_model=StatesByCountry)
def get_states_by_country(country_id: int,
                          db: Session = Depends(get_db),
                          token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve states by country ID.

    This endpoint retrieves all states associated with a specific country based on its ID.

    Parameters:
    - `country_id` (path parameter): The unique identifier of the country.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - StatesByCountry: Details of states belonging to the country identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no states are found for the country with the specified ID.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    states = db_common.get_states_by_country(db, country_id)
    if not states:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No states found for country with ID {country_id}")

    return {"country_id": country_id, "states": states}


@router.get("/state/{state_id}", response_model=StateDetail)
def get_state_by_id(state_id: int,
                    db: Session = Depends(get_db),
                    token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve state by ID.

    This endpoint retrieves a state from the database based on its ID.

    Parameters:
    - `state_id` (path parameter): The unique identifier of the state.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - StateDetail: Details of the state identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no state is found with the specified ID.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    state = db_common.get_state_by_id(db, state_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No state found with ID {state_id}")

    return state


@router.get("/districts/{state_id}", response_model=DistrictDetailByState)
def get_districts_by_state(state_id: int,
                           db: Session = Depends(get_db),
                           token: str = Depends(oauth2.oauth2_scheme)
                           ):
    """
    Retrieve districts by state ID.

    This endpoint retrieves all districts associated with a specific state based on its ID.

    Parameters:
    - `state_id` (path parameter): The unique identifier of the state.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - DistrictDetailByState: Details of districts belonging to the state identified by the provided ID.

    Raises:
    - HTTPException(404): If no districts are found for the state with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    districts = db_common.get_districts_by_state(db, state_id)
    if not districts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No districts found for state with ID {state_id}")

    return {"state_id": state_id, "districts": districts}




@router.get("/district/{district_id}", response_model=DistrictResponse)
def get_district_by_id(district_id: int,
                       db: Session = Depends(get_db),
                       token: str = Depends(oauth2.oauth2_scheme)
                       ):
    """
    Retrieve district by ID.

    This endpoint retrieves a district from the database based on its ID.

    Parameters:
    - `district_id` (path parameter): The unique identifier of the district.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - DistrictResponse: Details of the district identified by the provided ID.

    Raises:
    - HTTPException(404): If no district is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    district = db_common.get_district_by_id(db, district_id)
    if not district:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No district found with ID {district_id}")

    return {"district": district}




@router.get("/cities/{country_id}/{state_id}", response_model=CityResponse)
def get_cities_by_country_and_state(country_id: int,
                                    state_id: int,
                                    db: Session = Depends(get_db),
                                    token: str = Depends(oauth2.oauth2_scheme)
                                    ):
    """
    Retrieve cities by country and state.

    This endpoint retrieves all cities associated with a specific country and state.

    Parameters:
    - `country_id` (path parameter): The unique identifier of the country.
    - `state_id` (path parameter): The unique identifier of the state.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - CityResponse: Details of cities belonging to the specified country and state.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no cities are found for the specified country and state.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    cities = db_common.get_cities_by_country_and_state(db, country_id, state_id)
    if not cities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cities found for country_id={country_id} and state_id={state_id}")
    
    city_details = [{"id": city.id, "city_name": city.city_name} for city in cities]

    return {"country_id": country_id, "state_id": state_id, "cities": city_details}


#--------------------------------------------------------------------------------------------------------------

@router.get("/city/{city_id}", response_model=CityDetail)
def get_city_by_id(city_id: int,
                    db: Session = Depends(get_db),
                    token: str = Depends(oauth2.oauth2_scheme)
                    ):
    """
    Retrieve city by ID.

    This endpoint retrieves a city from the database based on its ID.

    Parameters:
    - `city_id` (path parameter): The unique identifier of the city.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - CityDetail: Details of the city identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no city is found with the specified ID.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    city = db_common.get_city_by_id(db, city_id)
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No city found with ID {city_id}")

    return city


#--------------------------------------------------------------------------------------------------------------


@router.get("/get_taluks/{state_id}", response_model=TalukResponse)
def get_taluks_by_state(state_id: int,
                        db: Session = Depends(get_db),
                        token: str = Depends(oauth2.oauth2_scheme)
                        ):
    """
    Retrieve taluks by state ID.

    This endpoint retrieves all taluks associated with a specific state based on its ID.

    Parameters:
    - `state_id` (path parameter): The unique identifier of the state.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - TalukResponse: Details of taluks belonging to the state identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no taluks are found for the state with the specified ID.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    taluks = db_common.get_taluks_by_state(db, state_id)
    if not taluks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No taluks found for state_id={state_id}")

    taluk_details = [
        TalukDetail(id=taluk.id, district_id=taluk.district_id, state_id=taluk.state_id, taluk_name=taluk.taluk_name)
        for taluk in taluks
    ]

    return TalukResponse(state_id=state_id, taluks=taluk_details)



#--------------------------------------------------------------------------------------------------------------

@router.get("/get_taluks/by_district/{district_id}", response_model=TalukResponseByDistrict)
def get_taluks_by_district(district_id: int,
                           db: Session = Depends(get_db),
                           token: str = Depends(oauth2.oauth2_scheme)
                           ):
    """
    Retrieve taluks by district ID.

    This endpoint retrieves all taluks associated with a specific district based on its ID.

    Parameters:
    - `district_id` (path parameter): The unique identifier of the district.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - TalukResponseByDistrict: Details of taluks belonging to the district identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no taluks are found for the district with the specified ID.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    taluks = db_common.get_taluks_by_district(db, district_id)
    if not taluks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No taluks found for district_id={district_id}")
    
    # Extracting only id and name from each taluk and creating a list of dictionaries
    taluk_details = [{"id": str(taluk.id), "name": taluk.taluk_name} for taluk in taluks]
    
    # Returning the response in the desired format
    return TalukResponseByDistrict(district_id=district_id, taluks=taluk_details)


#--------------------------------------------------------------------------------------------------------------

@router.get("/get_taluks/by_taluk/{taluk_id}", response_model=TalukDetail)
def get_taluk_by_id(taluk_id: int,
                    db: Session = Depends(get_db),
                    token: str = Depends(oauth2.oauth2_scheme)
                    ):
    """
    Retrieve taluk by ID.

    This endpoint retrieves a taluk from the database based on its ID.

    Parameters:
    - `taluk_id` (path parameter): The unique identifier of the taluk.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - TalukDetail: Details of the taluk identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no taluk is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    taluk = db_common.get_taluk_by_id(db, taluk_id)
    if not taluk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No taluk found with ID {taluk_id}")
    return taluk



#--------------------------------------------------------------------------------------------------------------

@router.get("/get_currencies", response_model=List[CurrencyDetail])
async def get_currencies(db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)
                        ):
    """
    Retrieve all currencies.

    This endpoint retrieves details of all currencies available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[CurrencyDetail]: Details of all currencies available.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    currencies = db_common.get_all_currencies(db)
    return currencies

#--------------------------------------------------------------------------------------------------------------
@router.get("/get_currencies/{currency_id}", response_model=CurrencyDetail)
def get_currency_by_id(currency_id: int,
                       db: Session = Depends(get_db),
                       token: str = Depends(oauth2.oauth2_scheme)
                       ):
    """
    Retrieve currency by ID.

    This endpoint retrieves details of a currency based on its ID.

    Parameters:
    - `currency_id` (path parameter): The unique identifier of the currency.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - CurrencyDetail: Details of the currency identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no currency is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    currency = db_common.get_currency_by_id(db, currency_id)
    if not currency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No currency found with ID {currency_id}")
    return currency

#--------------------------------------------------------------------------------------------------------------

@router.get("/get_nationality", response_model=List[NationalityDetail])
async def get_all_nationalities(db: Session = Depends(get_db),
                                token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve all nationalities.

    This endpoint retrieves details of all nationalities available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[NationalityDetail]: Details of all nationalities available.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    nationalities = db_common.get_all_nationality(db) 
    return nationalities



#--------------------------------------------------------------------------------------------------------------

@router.get("/get_nationality/{nationality_id}", response_model=NationalityDetail)
async def get_nationality_by_id(nationality_id: int,
                                db: Session = Depends(get_db),
                                token: str = Depends(oauth2.oauth2_scheme)
                                ):
    """
    Retrieve nationality by ID.

    This endpoint retrieves a nationality from the database based on its ID.

    Parameters:
    - `nationality_id` (path parameter): The unique identifier of the nationality.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - NationalityDetail: Details of the nationality identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no nationality is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    nationality = db_common.get_nationality_by_id(db, nationality_id)
    if nationality is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nationality not found")
    return nationality


#--------------------------------------------------------------------------------------------------------------

@router.get("/get_post_office_types", response_model=List[PostOfficeTypeDetail])
async def get_all_post_office_types(db: Session = Depends(get_db),
                                    token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve all post office types.

    This endpoint retrieves details of all post office types available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[PostOfficeTypeDetail]: Details of all post office types available.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    post_office_types = db_common.get_all_post_office_types(db)
    return post_office_types

#--------------------------------------------------------------------------------------------------------------


@router.get("/get_post_office_type/{id}", response_model=PostOfficeTypeDetail)
async def get_post_office_type(id: int, db: Session = Depends(get_db),
                               token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve post office type by ID.

    This endpoint retrieves details of a specific post office type based on its ID.

    Parameters:
    - `id` (path parameter): The unique identifier of the post office type.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - PostOfficeTypeDetail: Details of the post office type identified by the provided ID.

    Raises:
    - HTTPException(404): If no post office type is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    post_office_type = db_common.get_post_office_type_by_id(db, id)
    if not post_office_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post office type with ID {id} not found")
    return post_office_type


#--------------------------------------------------------------------------------------------------------------

@router.get("/get_postal_delivery_status", response_model=List[PostalDeliveryStatusDetail])
async def get_all_postal_delivery_status(db: Session = Depends(get_db),
                                         token: str = Depends(oauth2.oauth2_scheme)
                                         ):
    """
    Retrieve all postal delivery statuses.

    This endpoint retrieves details of all postal delivery statuses available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[PostalDeliveryStatusDetail]: Details of all postal delivery statuses available.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    delivery_statuses = db_common.get_all_postal_delivery_statuses(db)
    return delivery_statuses


#--------------------------------------------------------------------------------------------------------------

@router.get("/get_postal_delivery_status/{id}", response_model=PostalDeliveryStatusDetail)
async def get_postal_delivery_status_by_id(id: int, db: Session = Depends(get_db),
                                      token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve postal delivery status by ID.

    This endpoint retrieves details of a specific postal delivery status based on its ID.

    Parameters:
    - `id` (path parameter): The unique identifier of the postal delivery status.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - PostalDeliveryStatusDetail: Details of the postal delivery status identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no postal delivery status is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    delivery_status = db_common.get_postal_delivery_status_by_id(db, id)
    if not delivery_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Delivery status with ID {id} not found")
    return delivery_status


#--------------------------------------------------------------------------------------------------------------

@router.get("/get_postal_circles", response_model=List[PostalCircleDetail])
async def get_all_postal_circles(db: Session = Depends(get_db),
                                  token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve all postal circles.

    This endpoint retrieves details of all postal circles available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.


    Returns:
    - List[PostalCircleDetail]: Details of all postal circles available.
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    postal_circles = db_common.get_all_postal_circles(db)
    return postal_circles


#--------------------------------------------------------------------------------------------------------------


@router.get("/get_postal_circles/{id}", response_model=PostalCircleDetail)
async def get_postal_circle(id: int, db: Session = Depends(get_db),
                             token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve postal circle by ID.

    This endpoint retrieves details of a specific postal circle based on its ID.

    Parameters:
    - `id` (path parameter): The unique identifier of the postal circle.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - PostalCircleDetail: Details of the postal circle identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no postal circle is found with the specified ID.
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    postal_circle = db_common.get_postal_circle_by_id(db, id)
    if not postal_circle:
        raise HTTPException(status_code=404, detail=f"Postal Circle with {id} not found")
    return postal_circle


#--------------------------------------------------------------------------------------------------------------

@router.get("/get_postal_regions", response_model=List[PostalRegionDetail])
async def get_all_postal_regions(db: Session = Depends(get_db),
                                 token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve all postal regions.

    This endpoint retrieves details of all postal regions available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[PostalRegionDetail]: Details of all postal regions available.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    postal_regions = db_common.get_all_postal_regions(db)
    return postal_regions



@router.get("/get_postal_regions/{circle_id}", response_model=List[PostalRegionDetail])
async def get_postal_regions_by_circle_id(circle_id: int, db: Session = Depends(get_db),
                                          token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve postal regions by postal circle ID.

    This endpoint retrieves details of postal regions associated with a specific postal circle based on its ID.

    Parameters:
    - `circle_id` (path parameter): The unique identifier of the postal circle.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[PostalRegionDetail]: Details of postal regions associated with the postal circle identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no postal regions are found for the postal circle with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    postal_regions = db_common.get_postal_regions_by_circle_id(db, circle_id)
    if not postal_regions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No postal regions found for postal circle with ID {circle_id}")
    return postal_regions



@router.get("/get_postal_region/{region_id}", response_model=PostalRegionDetail)
async def get_postal_region(region_id: int, db: Session = Depends(get_db),
                            token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve postal region by ID.

    This endpoint retrieves details of a specific postal region based on its ID.

    Parameters:
    - `region_id` (path parameter): The unique identifier of the postal region.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - PostalRegionDetail: Details of the postal region identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no postal region is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    postal_region = db_common.get_postal_region_by_id(db, region_id)
    if not postal_region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Postal Region with ID {region_id} not found")
    return postal_region


@router.get("/get_all_postal_divisions", response_model=List[PostalDivisionDetail])
async def get_all_postal_divisions(db: Session = Depends(get_db),
                                   token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve all postal divisions.

    This endpoint retrieves details of all postal divisions available in the database.

    Parameters:
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[PostalDivisionDetail]: Details of all postal divisions available.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    divisions = db_common.get_all_postal_divisions(db)
    return divisions


@router.get("/get_postal_divisions/by_circle_id/{circle_id}", response_model=List[PostalDivisionDetail])
async def get_postal_divisions_by_circle_id(circle_id: int, db: Session = Depends(get_db),
                                            token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve postal divisions by circle ID.

    This endpoint retrieves details of postal divisions associated with a specific circle based on its ID.

    Parameters:
    - `circle_id` (path parameter): The unique identifier of the circle.
    - `db` (optional): SQLAlchemy database session. If not provided, a new session will be created.
    - `token` (required): Authentication token.

    Returns:
    - List[PostalDivisionDetail]: Details of postal divisions associated with the circle identified by the provided ID.

    Raises:
    - HTTPException(401): If the authentication token is missing.
    - HTTPException(404): If no circle is found with the specified ID.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    circle = db_common.get_postal_divisions_by_circle_id(db, circle_id)
    if not circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Circle with ID {circle_id} not found")
    return circle



@router.get("/get_postal_divisions/by_region_id/{region_id}", response_model=List[PostalDivisionDetail])
async def get_postal_divisions_by_region(region_id: int, db: Session = Depends(get_db),
                                         token: str = Depends(oauth2.oauth2_scheme)):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    region = db_common.get_postal_divisions_by_region_id(db, region_id=region_id)
    if not region:
        raise HTTPException(status_code=404, detail=f"Region with {region_id} not found")
    return region


@router.get("/get_postal_divisions/{division_id}", response_model=PostalDivisionDetail)
async def get_postal_division_by_id(division_id: int, db: Session = Depends(get_db),
                                    token: str = Depends(oauth2.oauth2_scheme)):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    division = db_common.get_postal_division_by_id(db, division_id=division_id)
    if not division:
        raise HTTPException(status_code=404, detail=f"Division with {division_id} not found")
    return division


@router.get('/get_post_offices_by_pincode/{pincode}', response_model=PostOfficeListResponse)
def get_post_offices_by_pin_code(
    pincode: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
   
):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    post_office_details = db_common.get_post_offices_by_pincode(db, pincode)

    if not post_office_details:
        raise HTTPException(status_code=404, detail="No post offices found for the given pincode")

    common_details = [
        {
            "pincode": pincode,
            "taluk": {"id": post_office_details[0].taluk_id, "name": post_office_details[0].taluk_name},
            "division": {"id": post_office_details[0].postal_division_id, "name": post_office_details[0].division_name},
            "region": {"id": post_office_details[0].postal_region_id, "name": post_office_details[0].region_name},
            "postalcircle": {"id": post_office_details[0].postal_circle_id, "name": post_office_details[0].circle_name},
            "district": {"id": post_office_details[0].district_id, "name": post_office_details[0].district_name},
            "state": {"id": post_office_details[0].state_id, "name": post_office_details[0].state_name},
            "country": {"id": post_office_details[0].country_id, "name": post_office_details[0].country_name_english},
            "post_offices": [{"id": po.id, "name": po.post_office_name} for po in post_office_details],
        }
    ]

    return {"pincode_details": common_details}


@router.get("/gender", response_model=List[GenderSchemaResponse])
def get_gender_details(db: Session = Depends(get_db),
                       token: str = Depends(oauth2.oauth2_scheme)):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    
    gender_details = db_common.get_all_gender(db)
    return [{"gender": gender_details}]


@router.get("/gender/{gender_id}", response_model=GenderSchemaResponse)
def get_gender_by_id(gender_id: int, db: Session = Depends(get_db),
                     token: str = Depends(oauth2.oauth2_scheme)):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    gender_detail = db_common.get_gender_by_id(db, gender_id)
    if gender_detail is None:
        raise HTTPException(status_code=404, detail="Gender not found")
    return {"gender": [gender_detail]}

@router.get("/pan_card_types", response_model=List[PancardSchemaResponse])
def get_pan_card_details(db: Session = Depends(get_db),
                         token: str = Depends(oauth2.oauth2_scheme)
     
    ):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

 
    pan_card_details = db_common.get_all_pan_cards(db)
    return pan_card_details


@router.get("/pan_card_types/{pancard_id}", response_model=PancardSchemaResponse)
def get_pan_card_by_id(
        pancard_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)
    ):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    pan_card_detail = db_common.get_pan_card_by_id(db, pancard_id)
    if pan_card_detail is None:
        raise HTTPException(status_code=404, detail="Pan card not found")
    # return {"pan card": [pan_card_detail]}
    return pan_card_detail


@router.get("/pan_card_types/{code_type}", response_model=PancardSchemaResponse)
def get_pan_card_by_card_type(
        code_type: str, 
        db: Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)
    ):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    pan_card_detail = db_common.get_pan_card_by_code_type(db, code_type)
    if pan_card_detail is None:
        raise HTTPException(status_code=404, detail="Pan card not found")
    return pan_card_detail



    

from caerp_auth.oauth2 import SECRET_KEY, ALGORITHM

from fastapi import HTTPException, status
from jose import jwt, JWTError


def verify_token(token: str):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        # Token is invalid
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")





    





@router.get("/constitution", response_model=List[ConstitutionTypeSchemaResponse])
def get_constitution_details(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)   
    ):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
     # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    constitution_details = db_common.get_all_constitution(db)
    return constitution_details

@router.post("/constitution_update/{constitution_id}", response_model=List[ConstitutionTypeForUpdate])
def update_constitution_details(        
        constitution_data : ConstitutionTypeForUpdate ,
        constitution_id : int ,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)
    ):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
   
    new_constitution = db_common.update_constitution(db, constitution_data,constitution_id)
        
    return [new_constitution]


@router.get("/profession", response_model=List[ProfessionSchemaResponse])
def get_profession_details(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)

    ):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    profession_details = db_common.get_all_profession(db)
    return profession_details


@router.post("/profession_update/{profession_id}", response_model=List[ProfessionSchemaForUpdate])
def update_profession_details(        
        profession_data : ProfessionSchemaForUpdate ,
        profession_id : int ,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)
    ):
    """
    Parameters:
    - `token` (required): Authentication token.
    """
    # Check authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    new_profession = db_common.update_profession(db, profession_data,profession_id)
        
    return [new_profession]


@router.post("/save/query_manager_queries/{id}", response_model=dict)
def save_query_manager_queries(
    data: QueryManagerQuerySchema,
    id: int = 0,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    return db_common.save_query_manager_queries(db, id, data)


@router.delete("/delete/query_manager_queries/{id}")
def delete_query_manager_queries(
                    
                     id: int,
                     db: Session = Depends(get_db),
                     token: str = Depends(oauth2.oauth2_scheme)):
    
    
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")


    
    return db_common.delete_query_manager_queries(db, id)


@router.get("/query_manager_queries/{id}", response_model=QueryManagerQuerySchemaForGet)
def get_query_manager_query_by_id(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    query = db_common.get_query_manager_query_by_id(db, id)
    if query is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")

    return query


@router.get("/get_all_query_manager_queries/" , response_model=List[QueryManagerQuerySchemaForGet])
async def get_all_query_manager_queries(deleted_status: DeletedStatus = DeletedStatus.NOT_DELETED,
                              db: Session = Depends(get_db),
                             ):
    return get_all_query_manager_queries(db, deleted_status)



def get_all_query_manager_queries(db: Session, deleted_status: DeletedStatus):
    if deleted_status == DeletedStatus.DELETED:
        return db.query(QueryManagerQuery).filter(QueryManagerQuery.is_deleted == 'yes').all()
    elif deleted_status == DeletedStatus.NOT_DELETED:
        return db.query(QueryManagerQuery).filter(QueryManagerQuery.is_deleted == 'no').all()
    elif deleted_status == DeletedStatus.ALL:
        return db.query(QueryManagerQuery).all()
    else:
       
        raise ValueError("Invalid deleted_status")
    
    
@router.post("/resolve/query_manager/{query_manager_id}")
def resolve_query_manager(
    query_manager_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    resolved_by = auth_info["user_id"]
    
    # Retrieve the QueryManager record
    query_manager = db.query(QueryManager).filter(QueryManager.id == query_manager_id).first()
    if query_manager is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query Manager not found")

    # Check if the query is already resolved
    if query_manager.is_resolved == 'yes':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query is already resolved")

    # Update the query_manager record to mark it as resolved
    query_manager.is_resolved = 'yes'
    query_manager.resolved_by = resolved_by
    query_manager.resolved_on = datetime.now()

    # Commit the changes to the database
    db.commit()

    return {"message": "Query resolved successfully", "query_manager": query_manager}

		


@router.get("/get_usernames_with_names_and_ids", response_model=List[dict])
def get_usernames_with_names_and_ids(db: Session = Depends(get_db)):
    try:
        # SQL query using SQLAlchemy text() function
        query = text(
            "SELECT users.id, users.user_name, "
            "CONCAT_WS(' ', "
            "employee_master.first_name, "
            "COALESCE(employee_master.middle_name, ''), "
            "employee_master.last_name"
            ") AS full_name "
            "FROM users "
            "LEFT JOIN employee_master ON users.employee_id = employee_master.employee_id;"
        )
        result = db.execute(query)

        # List to store formatted data
        formatted_data = []

        # Iterate over query results and format data
        for row in result:
            formatted_data.append(dict(row))

        return formatted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------ -----------------

@router.post('/save_Payments_mode/{id}', response_model=PaymentModeSchema)
def save_payments_mode(
    data: PaymentModeSchema,
    id: int = 0,  # Default value of 0 for id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a Payments mode.

    - **data**: Data for the Payments mode, provided as parameters of type PaymentModeSchema.
    - **id**: An optional integer parameter with a default value of 0, indicating the Payments mode's identifier.
    
    - If Payments mode id is 0, it indicates the creation of a new Payments mode.
    - Returns: The newly created Payments mode as the response.

    If Payments mode id is not 0, it indicates the update of an existing Payments mode.
    - Returns: The updated Payments mode as the response.

    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_common.save_payments_mode (db, data, id)
    
#------All-----------------  
@router.get('/payments_mode/all', response_model=list[PaymentModeSchemaForGet])
def get_all_payments_mode(deleted_status: DeletedStatus = Query(DeletedStatus.ALL),
                          token: str = Depends(oauth2.oauth2_scheme),
                          db: Session = Depends(get_db)
                          ):
    """                       
    Get payments_mode from the database based on status.

    - **status**: Query parameter to filter payments_mode by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    if deleted_status == DeletedStatus.DELETED:
        return db.query(PaymentsMode).filter(PaymentsMode.is_deleted == 'yes').all()
    elif deleted_status == DeletedStatus.NOT_DELETED:
        return db.query(PaymentsMode).filter(PaymentsMode.is_deleted == 'no').all()
    elif deleted_status == DeletedStatus.ALL:
        return db.query(PaymentsMode).all()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid deleted_status")
#-----------by id----------------------

@router.get('/get/Payments_mode/{id}', response_model=PaymentModeSchemaForGet)
def get_payments_mode_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get Payments mode by Payments_mode id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    payments_mode = db_common.get_payment_mode(db, id)
    if not payments_mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"payments mode with id {id} not found"
        )
    return payments_mode
#-----delete------
@router.delete("/payments_mode/delete/{id}")
def delete_payments_mode(
    id: int,
    action_type: ActionType,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
   
    
    return db_common.delete_payments_mode(db, id, action_type)


    

#------------6/4/2024 Payments_Status -----------------

@router.post('/get/save_payment_status/{id}', response_model=PaymentStatusSchema)
def save_payment_status(
    data: PaymentStatusSchema,
    id: int = 0,  # Default value of 0 for id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a payment status

    - **data**: Data for the payment_status, provided as parameters of type PaymentStatusSchema.
    - **id**: An optional integer parameter with a default value of 0, indicating the payment_status's identifier.
    
    - If payment_status id is 0, it indicates the creation of a new payment_status.
    - Returns: The newly created payment_status as the response.

    If payment_status id is not 0, it indicates the update of an existing payment_status.
    - Returns: The updated payment_status as the response.

    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_common.save_payment_status (db, data, id)
    
#-----------------------  

@router.get('/payment_status/all', response_model=list[PaymentStatusSchemaForGet])
def get_all_payment_status(deleted_status: DeletedStatus = Query(DeletedStatus.ALL),
                          token: str = Depends(oauth2.oauth2_scheme),
                          db: Session = Depends(get_db)
                          ):
    """                       
    Get payment_status from the database based on status.

    - **status**: Query parameter to filter payment_status by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    if deleted_status == DeletedStatus.DELETED:
        return db.query(PaymentStatus).filter(PaymentStatus.is_deleted == 'yes').all()
    elif deleted_status == DeletedStatus.NOT_DELETED:
        return db.query(PaymentStatus).filter(PaymentStatus.is_deleted == 'no').all()
    elif deleted_status == DeletedStatus.ALL:
        return db.query(PaymentStatus).all()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid deleted_status")

#---------------------------------

@router.get('/get/payment_status/{id}', response_model=PaymentStatusSchemaForGet)
def get_payments_status_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get payment status by payment_status id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    payment_status = db_common.get_payment_status(db, id)
    if not payment_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"payments status with id {id} not found"
        )
    return payment_status
#-----delete------
@router.delete("/payment_status/delete/{id}")
def delete_payment_status(
    id: int,
    action_type: ActionType,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
   
    
    return db_common.delete_payment_status(db, id, action_type)


    

#-----------------------------

@router.post('/get/save_refund_status/{id}', response_model=RefundStatusSchema)
def save_refund_status(
    data: RefundStatusSchema,
    id: int = 0,  # Default value of 0 for id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a Refund Status

    - **data**: Data for the Refund Status, provided as parameters of type RefundStatusSchema.
    - **id**: An optional integer parameter with a default value of 0, indicating the refund_status's identifier.
    
    - If Refund Status id is 0, it indicates the creation of a new Refund Status.
    - Returns: The newly created Refund Status as the response.

    If Refund Status id is not 0, it indicates the update of an existing Refund Status.
    - Returns: The updated Refund Status as the response.

    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_common.save_refund_status (db, data, id)
    
#------All-----------------  

@router.get('/refund_status/all', response_model=list[RefundStatusSchemaForGet])
def get_all_refund_status(deleted_status: DeletedStatus = Query(DeletedStatus.ALL),
                          token: str = Depends(oauth2.oauth2_scheme),
                          db: Session = Depends(get_db)
                          ):
    """                       
    Get refund_status from the database based on status.

    - **status**: Query parameter to filter refund_status by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    if deleted_status == DeletedStatus.DELETED:
        return db.query(RefundStatus).filter(RefundStatus.is_deleted == 'yes').all()
    elif deleted_status == DeletedStatus.NOT_DELETED:
        return db.query(RefundStatus).filter(RefundStatus.is_deleted == 'no').all()
    elif deleted_status == DeletedStatus.ALL:
        return db.query(RefundStatus).all()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid deleted_status")

#-----------by id----------------------

@router.get('/get/refund_status/{id}', response_model=RefundStatusSchemaForGet)
def get_refund_status_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get refund status by refund_status id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    refund_status = db_common.get_refund_status(db, id)
    if not refund_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"refund status  with id {id} not found"
        )
    return refund_status
#-----delete------
@router.delete("/refund_status/delete/{id}")
def delete_refund_status(
    id: int,
    action_type: ActionType,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
   
    
    return db_common.delete_refund_status(db, id, action_type)


#------------8/4/2024 refund reason -----------------

@router.post('/save_refund_reason/{id}', response_model=RefundReasonSchema)
def save_refund_reason(
    data: RefundReasonSchema,
    id: int = 0,  # Default value of 0 for id
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Handles the creation or update of a Refund Reason

    - **data**: Data for the Refund Reason, provided as parameters of type RefundReasonSchema.
    - **id**: An optional integer parameter with a default value of 0, indicating the Refund Reason's identifier.
    
    - If Refund Reason id is 0, it indicates the creation of a new Refund Reason.
    - Returns: The newly created Refund Reason as the response.

    If Refund Reason id is not 0, it indicates the update of an existing Refund Reason.
    - Returns: The updated Refund Reason as the response.

    
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    return db_common.save_refund_reason (db, data, id)
    
#------All-----------------  


@router.get('/refund_reason/all', response_model=list[RefundReasonSchemaForGet])
def get_all_refund_status(deleted_status: DeletedStatus = Query(DeletedStatus.ALL),
                          token: str = Depends(oauth2.oauth2_scheme),
                          db: Session = Depends(get_db)
                          ):
    """                       
    Get refund_reason from the database based on status.

    - **status**: Query parameter to filter refund_reason by status (ALL/DELETED/NOT DELETED).
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    if deleted_status == DeletedStatus.DELETED:
        return db.query(RefundReason).filter(RefundReason.is_deleted == 'yes').all()
    elif deleted_status == DeletedStatus.NOT_DELETED:
        return db.query(RefundReason).filter(RefundReason.is_deleted == 'no').all()
    elif deleted_status == DeletedStatus.ALL:
        return db.query(RefundReason).all()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid deleted_status")

    

#-----------by id----------------------

@router.get('/get/refund_reason/{id}', response_model=RefundReasonSchemaForGet)
def get_refund_reason_by_id(id: int, 
                    token: str = Depends(oauth2.oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
     - Get refund status by refund_reason id.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    refund_reason = db_common.get_refund_reason(db, id)
    if not refund_reason:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"refund reason with id {id} not found"
        )
    return refund_reason
#-----delete------
@router.delete("/refund_reason/delete/{id}")
def delete_refund_reason(
    id: int,
    action_type: ActionType,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
   
    
    return db_common.delete_refund_reason(db, id, action_type)




#----------------------------------------------------------------------------




@router.post("/nationalities/{crud_operation}")
def crud_nationality(crud_operation: CRUD, nationality_id: int = None, nationality_name: str = None, db: Session = Depends(get_db)):
    if crud_operation == CRUD.CREATE:
        nationality = NationalityDB(nationality_name=nationality_name)
        db.add(nationality)
        db.commit()
        db.refresh(nationality)
        return nationality
    elif crud_operation == CRUD.READ:
        nationality = db.query(NationalityDB).filter(NationalityDB.id == nationality_id).first()
        if not nationality:
            raise HTTPException(status_code=404, detail="Nationality not found")
        return nationality
    elif crud_operation == CRUD.UPDATE:
        nationality = db.query(NationalityDB).filter(NationalityDB.id == nationality_id).first()
        if not nationality:
            raise HTTPException(status_code=404, detail="Nationality not found")
        nationality.nationality_name = nationality_name
        db.commit()
        db.refresh(nationality)
        return {"message": "Nationality updated successfully"}
    elif crud_operation == CRUD.DELETE:
        nationality = db.query(NationalityDB).filter(NationalityDB.id == nationality_id).first()
        if not nationality:
            raise HTTPException(status_code=404, detail="Nationality not found")
        db.delete(nationality)
        db.commit()
        return {"message": "Nationality deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid CRUD operation")
    

@router.get("/get/villages_by_pincode/", response_model=VillageResponse)
def get_villages(pincode: str, db: Session = Depends(get_db)):
    return db_common.get_villages_data(db, pincode)

#-------------------------------------------------------------------------------

@router.get("/get_bank_details/{ifsc_code}", response_model=List[BankMasterBase])
def get_bank_details_by_ifsc_code(
    ifsc_code: str, 
    db: Session = Depends(get_db)
   
):
    """
    Retrieve all bank details by the given IFSC code.
    """
   
    # Query the bank details based on the IFSC code and not deleted status
    bank_details = db.query(AppBankMaster).filter(
        AppBankMaster.ifsc_code == ifsc_code,
        AppBankMaster.is_deleted == 'no'
    ).all()

    # If no records are found, raise a 404 error with a custom message
    if not bank_details:
        return []
    return bank_details


#-----------------------------------------------------------------------

@router.post('/save/send_query_manager_otp')
def send_query_manager_otp(
    input_value: str,  # Single input parameter
    db: Session = Depends(get_db)
):  
    # Determine the type of input
    if re.match(r'^\S+@\S+\.\S+$', input_value):  # Simple email regex
        input_type = "email"
        mobile_no = None
        email_id = input_value
        user_name = None
    elif input_value.isdigit() and len(input_value) in [10, 12]:  # Mobile number
        input_type = "mobile"
        mobile_no = input_value
        email_id = None
        user_name = None
    else:  # Assume it's a username
        input_type = "username"
        mobile_no = None
        email_id = None
        user_name = input_value

    # Call the database function with the determined input type
    result = db_common.send_query_manager_otp(
        db, 
        mobile_no=mobile_no, 
        email_id=email_id, 
        user_name=user_name
    )

    return {
        "input_type": input_type,
        "result": result
    }
    

#-----------------------------------------------------------------------
@router.post("/save/query_manager/")
def save_query_manager(
    data: QueryManagerSchema,
    db: Session = Depends(get_db),
    # token: str = Depends(oauth2.oauth2_scheme)
):
    # if not token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    


    # Retrieve the user_id based on the provided username
    # user = db.query(UserBase).filter(UserBase.user_name == data.queried_by).first()
    # if user is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Create a new QueryManager record
    new_query_manager = QueryManager(
        query_id=data.query_id,
        queried_by=data.user_id, 
        query_on=datetime.now(),
        query_description=data.query_description 
      
    )

    # Save the new record
    db.add(new_query_manager)
    db.commit()
    db.refresh(new_query_manager)

    return {"message": "Query inserted successfully", "query_manager": new_query_manager}



#-----------------------------------------------------------------------
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# @router.post("/register")
# async def register(user: UserRegistrationCreate, db: Session = Depends(get_db)):
#     # Check if user already exists
#     db_user = db.query(UserRegistration).filter(UserRegistration.username == user.username).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
    
#     # Hash the password
#     hashed_password = pwd_context.hash(user.password)

#     # Create a new user object
#     new_user = UserRegistration(
#         username=user.username,
#         password=hashed_password,
#         latitude=user.latitude,
#         longitude=user.longitude
#     )

#     # Add the new user to the session and commit
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return {"message": "User registered successfully!", "user_id": new_user.id}



@router.post('/send_resolved_notification')
def send_resolved_notification(
    query_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    quer_details = db_common.get_query_details(db, query_id)
    
    if not quer_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query details not found")

    mobile_no = quer_details["mobile_number"]
    employee_name = quer_details["employee_name"]
    user_name = quer_details["user_name"]
    user_id     = quer_details["user_id"]
    employee_id = quer_details["employee_id"]

    if not mobile_no:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number is missing for the resolved employee")
    random_no = random.randint(pow(10,4), pow(10,4+1)-1)
    password = f'{user_name}@{random_no}'
    phone_number = f'+91{mobile_no}'
    template = "query1"
    placeholders = [employee_name, user_name, password]
    
    password_reset_result = db_user.user_password_reset(db, user_id, password)  
    if password_reset_result:
        result = db_common.send_query_resolved_notification(phone_number, template, placeholders)

    if result["success"]:
        return {
            "success": True,
            "response": result["response"]
        }
    else:
        return {
            "success": False,
            "response": result["error"]
        }

#-------------------------------------------------------------------------------------
@router.get("/notifications/", response_model=List[NotificationSchema])
def get_notifications(
    notification_id : Optional[int] = None,
    display_location : Optional[str] = None,
    db: Session = Depends(get_db),
    # token: str = Depends(oauth2.oauth2_scheme)
):
    # if not token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    # auth_info = authenticate_user(token)
    # user_id = auth_info.get("user_id")
    result = db_common.get_notifications(db,notification_id,display_location)
    return result
    

#-------------------------------------------------------------------------------------

@router.post("/notifications/")
def add_notification(    
    notification: NotificationSchema, 
    db: Session = Depends(get_db) ,
    notification_id: Optional[int] = None,
    # display_location: Optional[int] = None,
    token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    result = db_common.add_notification(notification,db, notification_id)
    return result




@router.get("/queries", response_model=List[QueryManagerViewSchema])
def get_queries(id: Optional[int] =None,
                      search_value: Optional[str] = "ALL",
                      is_resolved : Optional[str] = 'ALL',
                      from_date     : Optional[date] = None,
                      to_date       : Optional[date] =None,
                      db: Session = Depends(get_db),
                      token: str = Depends(oauth2.oauth2_scheme)):
    """
    Retrieve a list of queries based on the provided parameters.

    Parameters:
        id (Optional[int]): 
            The unique identifier of a specific query. 
            If provided, returns the query matching this ID.
        
        search_value (Optional[str], default="ALL"): 
            A search term to filter queries (e.g., query description or content). 
            Use "ALL" for no filtering.

        is_resolved (Optional[str], default="ALL"): 
            Filter queries by resolution status. 
            "yes" for resolved queries and "no" for unresolved queries.

        db (Session): 
            The database session used to fetch query data. 
            Injected automatically using FastAPI dependencies.

        token (str): 
            The authorization token required for authentication. 
            Missing or invalid tokens will result in an HTTP 401 error.

    Returns:
        List[QueryManagerViewSchema]: 
            A list of queries matching the specified filters.

    Raises:
        HTTPException: 
            - 401 Unauthorized if the token is missing.
            - 404 Not Found if no queries match the provided criteria.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    query = db_common.get_queries_by_id(db, id,is_resolved ,search_value,from_date, to_date)
    if query is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return query

