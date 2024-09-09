from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware 
from caerp_auth import authentication
from caerp_router.common import user,otp_process,common,common_functions
from caerp_router.office import office_master
from caerp_router.services.gst_services import gst_registration

from caerp_router.accounts import quotation
from caerp_router.hr_and_payroll import employee_master
from caerp_functions import captcha
from caerp_db.database import caerp_base, caerp_engine
from fastapi.staticfiles import StaticFiles

# from caerp_router.accounts im
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# import redis

caerp_base.metadata.create_all(bind=caerp_engine)

app = FastAPI(
    debug=True,
    title="Main Application API",
    description="""
        Welcome to the Main Application API! Here, you can find documentation for various endpoints related to different modules.

        ## Documentation Links:
        - [Office Module](/office/docs): Documentation for endpoints related to the login related functions.
        - [Common Module](/common/docs): Documentation for endpoints related to the common process.
        - [Hr and Payroll Module](/hr_and_payroll/docs): Documentation for endpoints related to the  hr_and_payroll process.
        - [Accounts Module](/accounts/docs): Documentation for endpoints related to the  accounts related process.
       """
)



# @app.on_event("startup")
# async def startup():
#     # Initialize cache
#     redis_client = redis.Redis.from_url("redis://localhost:6379")
#     FastAPICache.init(RedisBackend(redis_client), prefix="cache")

# @app.on_event("shutdown")
# async def shutdown():
#     await FastAPICache.clear()

  
app_common=FastAPI(debug=True)
app_office=FastAPI(debug=True)
hr_and_payroll=FastAPI(debug=True)
accounts=FastAPI(debug=True)
gst_services=FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SessionMiddleware, secret_key="da30300a84b6fa144a20702bd15acac18ff3954aa67e72b485d59df5e27fb5d3")

try:
    caerp_engine.connect()
    print("Database connection established.")
except Exception as e:
    print(f"Error connecting to the database: {e}")


# instance of the APIRouter class.

app.include_router(authentication.router)

# # for common module
app_common.include_router(authentication.router)
app_common.include_router(common.router)
app_common.include_router(common_functions.router)
app_common.include_router(otp_process.router)
app_common.include_router(user.router)
app_common.include_router(captcha.router)
# # for office module
app_office.include_router(authentication.router)
app_office.include_router(office_master.router)
# # for hr_and_payroll module
hr_and_payroll.include_router(authentication.router)
hr_and_payroll.include_router(employee_master.router)

# for accounts module
accounts.include_router(authentication.router)
accounts.include_router(quotation.router)


# for gst service
gst_services.include_router(authentication.router)
gst_services.include_router(gst_registration.router) 

app.mount("/common", app_common, name="common")
app.mount("/office", app_office, name="office")
app.mount("/hr_and_payroll", hr_and_payroll, name="hr_and_payroll")
app.mount("/accounts/",accounts,name="accounts")
app.mount("/services/",gst_services,name="services")

app_common.mount("/captcha/generate_captcha", StaticFiles(directory="uploads/captcha_modified_images"), name="captcha_images")
# app_office.mount("/upload_document", StaticFiles(directory="uploads/work_order_documents"), name="documents")
app_office.mount("/upload_document", StaticFiles(directory="uploads/work_order_documents"), name="office_documents")
hr_and_payroll.mount("/Employee/upload_document", StaticFiles(directory="uploads/employee_documents"), name="documents")



















