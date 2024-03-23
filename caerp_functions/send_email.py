from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from caerp_schema.common.common_schema import Email,EmailCredentialsSchema
from sqlalchemy.orm import Session
from caerp_db.database import get_db
from caerp_db.common.models import EmailCredentials,OtpGeneration
from datetime import datetime, timedelta
import random



# def send_email(messageTo,subject,messageBody,messageType, db):
def send_email(email: Email, db):
    # Load credentials from a database or configuration file based on messageType
    
    config_res = get_credentials(db, email.messageType)
   
   
    # Set up the email content
    msg = MIMEMultipart()
    msg['From'] = config_res["UserName"]
    msg['To'] = email.messageTo
    msg['Subject'] = email.subject
    msg.attach(MIMEText(email.messageBody, 'html'))
   
    # Set up SMTP connection
    try:
        with smtplib.SMTP(config_res["SMTPHost"], config_res["SMTPPort"]) as server:
            server.ehlo()
            if config_res["SMTPAuth"]:
                server.login(config_res["UserName"], decrypt_password(config_res["Password"]))
            server.send_message(msg)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Define functions to get credentials and decrypt password
def get_credentials(db: Session, message_type: str):
    credentials_dict={}
    # Replace this with your logic to fetch credentials from a database or configuration file
    if message_type == "NO_REPLY":
        
        # Example credentials for demonstration purposes
        email_credentials = db.query(EmailCredentials).filter(EmailCredentials.id == 1).first()

        credentials_dict = {
            "SMTPHost": email_credentials.SMTP_host,
            "SMTPPort": int(email_credentials.SMTP_port),
            "SMTPAuth": bool(email_credentials.SMTP_auth) ,
            "UserName": email_credentials.username,
            "Password": email_credentials.password,
            # Add other fields as needed
        }
 
    
    return credentials_dict 



def decrypt_password(password):
    # Replace this with your logic to decrypt the password
    # For now, returning the password as it is, you should implement the decryption logic here
    password ="mGf*BWw#l,St"
    return password

