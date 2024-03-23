from fastapi import APIRouter,Depends,HTTPException,status
from caerp_schema.common.common_schema import CityDetail, CityResponse, ConstitutionTypeForUpdate, ConstitutionTypeSchemaResponse, CountryCreate, CountryDetail, CurrencyDetail, DistrictDetailByState, DistrictResponse, GenderSchemaResponse, NationalityDetail, PancardSchemaResponse, PostOfficeListResponse, PostOfficeTypeDetail, PostalCircleDetail, PostalDeliveryStatusDetail, PostalDivisionDetail, PostalRegionDetail, ProfessionSchemaForUpdate, ProfessionSchemaResponse, QualificationSchemaForUpdate, QualificationSchemaResponse, StatesByCountry,StateDetail, TalukDetail, TalukResponse, TalukResponseByDistrict
from caerp_db.database import get_db
from sqlalchemy.orm import Session
from caerp_db.common import db_common
from caerp_constants.caerp_constants import ActiveStatus
from typing import List
from caerp_auth import oauth2

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

@router.get("/qualification", response_model=List[QualificationSchemaResponse])
def get_qualification_details(
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
    qualification_details = db_common.get_all_qualification(db)
    return qualification_details


@router.post("/qualification_update/{qualification_id}", response_model=List[QualificationSchemaForUpdate])
def update_qualification_details(        
        qualification_data : QualificationSchemaForUpdate ,
        qualification_id : int ,
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
    new_qualification = db_common.update_qualification(db, qualification_data,qualification_id)
        
    return [new_qualification]


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
