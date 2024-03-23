from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "brdb123"
MYSQL_HOSTNAME = "202.21.38.180"
MYSQL_PORT = "3306"
MYSQL_DATABASE_NAME = "bharat_taxes_ca_erp"


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}:{MYSQL_PORT}/{MYSQL_DATABASE_NAME}"
 
caerp_engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=caerp_engine)


caerp_base = declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()







