from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from caerp_db.database import get_db
from sqlalchemy.orm import Session
# from caerp_db import db_admin
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows, OAuthFlowPassword


SECRET_KEY = "da30300a84b6fa144a20702bd15acac18ff3954aa67e72b485d59df5e27fb5d3"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(self, token_url: str, user_type: str):
        super().__init__(tokenUrl=token_url)
        self.user_type = user_type

    def __call__(self, request: Request) -> str:
        # Custom logic here if needed
        return super().__call__(request)

# For admin login
# custom_oauth2_scheme_admin = CustomOAuth2PasswordBearer(token_url="/admin-login", user_type="admin")

# For client login
custom_oauth2_scheme_client = CustomOAuth2PasswordBearer(token_url="/client-login", user_type="client")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin-login")

# custom_oauth2_scheme_admin
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt






# def get_current_user(token:str =Depends(oauth2_scheme),db: Session = Depends(get_db)):
#     credential_exception= HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail= 'could not validate credential',
#         headers={"WWW-Authenticate":"Bearer"}
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
#         username: str=payload.get("sub")
#         if username is None:
#             raise credential_exception
#     except JWTError :
#         raise credential_exception
#     user= db_admin.get_user_by_username(db , username)

#     if user is None:
#         raise credential_exception
#     return user

