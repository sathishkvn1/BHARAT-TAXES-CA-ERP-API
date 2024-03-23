import requests
from fastapi import FastAPI, HTTPException, APIRouter
import http.client
import random
from sqlalchemy.orm import Session
from caerp_db.common.models import MobileCredentials
from urllib.parse import urlparse


def send_sms_otp(mobile_no, message, temp_id,db):

    config_res = get_sms_credentials(db)
    # print(config_res)
    
    sms_username = config_res["username"]
    sms_password = decrypt_password(config_res["password"])
    sms_sender_id = config_res["sender"]
    sms_url = config_res["api_url"]    
    entity_id = config_res["entity_id"]
    
    parsed_url = urlparse(sms_url)
    hostname = parsed_url.netloc
   
    temp_id = temp_id
    payload = f"username={sms_username}&password={sms_password}&type=0&dlr=0&destination={mobile_no}&source={sms_sender_id}&message={message}&entityid={entity_id}&tempid={temp_id}"
    
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    try:
        conn = http.client.HTTPConnection(hostname)
        conn.request("POST", "/bulksms/bulksms", payload, headers)
        response = conn.getresponse()
        
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail=f"Failed to send SMS: {response.reason}")
        
        return response.read().decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")
    finally:
        conn.close()



# Define functions to get credentials and decrypt password
def get_sms_credentials(db: Session):
    credentials_dict={}
        
        # Example credentials for demonstration purposes
    mobile_credentials = db.query(MobileCredentials).filter(MobileCredentials.id == 1).first()

    credentials_dict = {
            "api_url"       : mobile_credentials.api_url,
            "port"          : mobile_credentials.port,
            "sender"        : mobile_credentials.sender ,
            "username"      : mobile_credentials.username,
            "password"      : mobile_credentials.password,
            "entity_id"      : mobile_credentials.entity_id,
            "delivery_report_status": mobile_credentials.delivery_report_status
            # Add other fields as needed
        }
 
    
    return credentials_dict 

def decrypt_password(password):
    # Replace this with your logic to decrypt the password
    # For now, returning the password as it is, you should implement the decryption logic here
    password ="BRQglob1"
    return password
