
import json
from fastapi import FastAPI, HTTPException, APIRouter, Depends
from httpcore import TimeoutException
from pydantic import BaseModel
from requests import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uuid
import time
from datetime import date, datetime
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import StaleElementReferenceException
from sqlalchemy import text
from caerp_auth import oauth2
from caerp_auth.authentication import authenticate_user
from caerp_db.database import get_db
from caerp_db.services.db_gst import get_business_place, get_customer_details, get_gst_state_specific_information_by_customer_id, get_hsn_commodities_by_customer_id, get_stakeholder_details
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

router = APIRouter(tags=['GST Registration AutoFill'])

# Dictionary to store WebDriver instances by session ID
webdriver_sessions = {}

class BusinessDetails(BaseModel):

    trade_name: str
    add_trade_name: str
    constitution: str
    f_first_name: str
    f_middle_name: str
    f_last_name: str
    date_of_birth: date
    mobile: str
    email: str
    gender:str
    pin_code : str

class RegistrationData(BaseModel):
    registration_type : str
   
def get_browser_name(user_id,log_id,db):

    result = db.execute(
        text("SELECT browser_type, browser_family, browser_version "
            "FROM users_log "
            "WHERE id = :log_id AND user_id = :user_id"),
        {'log_id': log_id, 'user_id': user_id}
    )

    # Fetch the result
    browser_details = result.fetchone()
    # Execute the query with parameters
    # result = db.execute(query, {'log_id': log_id, 'user_id': user_id})
   
    if browser_details is None:
        print(f"No browser details found for log_id={log_id} and user_id={user_id}.")
        return None
    else: 
        browser_name = browser_details[0]
        return browser_name
    
    

def get_driver(browser_name):
    browser_name = browser_name.lower()  # Normalize input
    if browser_name == "chrome":
        return webdriver.Chrome(service=ChromeService())
    elif browser_name == "firefox":
        return webdriver.Firefox(service=FirefoxService())
    elif browser_name == "edge":
        return webdriver.Edge(service=EdgeService())
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    
def get_driver_session(session_id: str):
    # Retrieve the WebDriver instance for the session ID
    if session_id in webdriver_sessions:
        return webdriver_sessions[session_id]
    else:
        raise HTTPException(status_code=404, detail="Session not found")

def otp_page(driver, entry_point= 'temp_reg'):
    
    print('inside function')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'mobile_otp')))
        # print("OTP page loaded, waiting for manual OTP input...")

    otp_input = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.ID, 'mobile_otp'))
    )

    expected_otp_length = 6
    WebDriverWait(driver, 120).until(
        lambda driver: len(otp_input.get_attribute('value')) == expected_otp_length
    )
    if entry_point == 'temp_reg':
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'email-otp')))
            # print("OTP page loaded, waiting for manual OTP input...")

        email_otp_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, 'email-otp'))
        )

        # expected_otp_length = 6
        WebDriverWait(driver, 120).until(
            lambda driver: len(email_otp_input.get_attribute('value')) == expected_otp_length
        )

    submit_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(text(), "Proceed")]'))
    )
    submit_button.click()


def enter_text_field(driver, element_id, text_value):
    """
    Clears an input field and enters text if the field is enabled.
    
    :param driver: The Selenium WebDriver instance.
    :param element_id: The ID of the element to interact with.
    :param text_value: The text to enter into the input field.
    """
    try:
        field = driver.find_element(By.ID, element_id)
        if field.is_enabled():
            field.clear()
            field.send_keys(text_value)
        #     print(f"Entered '{text_value}' into field with ID '{element_id}'. Current text: {field.get_attribute('value')}")
        # else:
        #     print(f"Field with ID '{element_id}' is not enabled.")
    except Exception as e:
        print(f"An error occurred with field ID '{element_id}': {e}")
    

@router.post("/gst_registration")
def gst_registration(
        request : RegistrationData,
        customer_id: int,
        service_task_id:int,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)
        ): 
    session_id = str(uuid.uuid4())
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    log_id = auth_info.get("log_id")
     

    browser_name = get_browser_name(user_id,log_id,db)
   
    # driver     = webdriver.Chrome()
    driver      = get_driver(browser_name)
    webdriver_sessions[session_id] = driver

    
    try:
        # customer_id = 43
        customer_details = get_customer_details(db,customer_id,service_task_id, user_id)
        legal_name      = customer_details['customer_business_details']['legal_name']
        mobile_number   = customer_details['customer_business_details']['mobile_number']
        email           = customer_details['customer_business_details']['email_address']
        pan_number      = customer_details['customer_business_details']['pan_number']
        tin_number      = customer_details['customer_business_details']['tin_number']
        name_authorized_signatory   = customer_details['customer_business_details']['authorized_signatory_name_as_in_pan']
        pan_number_authorised_signatory = customer_details['customer_business_details']['authorized_signatory_pan_number']
        district_code  = customer_details['customer_business_details']['district_code']
        state_code     = customer_details['customer_business_details']['state_code']
        # tan_number = 'WUISGGFH'
        tan_number      = customer_details['customer_business_details']['tan_number']

        
        # print('customer_ id', customer_details['customer_business_details']['state_id'])
        # Load login page and fill login details (similar to the code you have)
        driver.get("https://reg.gst.gov.in/registration/")
        WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.ID, 'applnType')))
        application_type_field = Select(driver.find_element(By.ID, 'applnType'))
        application_type_field.select_by_value(request.registration_type)
        if request.registration_type != 'REGOI':
        # application_type_field.select_by_visible_text()
            WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.ID, 'applnState')))
            state_field = Select(driver.find_element(By.ID, 'applnState'))
            state_field.select_by_value(str(state_code))	
            if request.registration_type != 'APLTD' and request.registration_type != 'APLTC':
                WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID, 'applnDistr')))
                district_field = Select(driver.find_element(By.ID, 'applnDistr'))
                district_field.select_by_value(district_code)	
        # legal_name_field = driver.find_element(By.ID, 'bnm')
        # driver.execute_script("arguments[0].scrollIntoView(true);", legal_name_field)
        # legal_name_field.clear()
        # legal_name_field.send_keys(legal_name)	
        enter_text_field(driver,'bnm',legal_name)
        if request.registration_type == 'APLTD' :

            if pan_number:
                radio_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="radio" and @value="P" and @id="pt"]'))
                )
                driver.execute_script("arguments[0].click();", radio_button)

            else:   
                radio_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="radio" and @value="T" and @id="radiopass"]'))
                )
                driver.execute_script("arguments[0].click();", radio_button)
                # pan_field = driver.find_element(By.ID, 'pan_card')
                # pan_field = WebDriverWait(driver, 10).until(
                #         EC.presence_of_element_located((By.XPATH, '//input[@type="text" and @placeholder="Enter Tax Deduction Account Number (TAN)"  and @id="pan_card"]'))
                #     )
                # driver.execute_script("arguments[0].scrollIntoView(true);", pan_field)
                # pan_field.clear()
                # pan_field.send_keys('EFSD124')	
                # pass_number_field = driver.find_element(By.ID, 'pp_number')
                # if pass_number_field:
                #     pass_number_field.clear()
                #     pass_number_field.send_keys(pan_number)
        

        if request.registration_type == 'APLNR':
            if pan_number:
                radio_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="radio" and @value="P" and @id="radiopan"]'))
                )
                driver.execute_script("arguments[0].click();", radio_button)

            elif tin_number:
                
                radio_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="radio" and @value="P" and @id="radiotin"]'))
                )
                driver.execute_script("arguments[0].click();", radio_button)
                enter_text_field(driver,'taxid',pan_number)
                
                # tax_id_number_field = driver.find_element(By.ID, 'taxid')
                # if tax_id_number_field:
                #     tax_id_number_field.clear()
                #     tax_id_number_field.send_keys(pan_number)

            else:             
                radio_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="radio" and @value="S" and @id="radiopass" ]'))
                )
                driver.execute_script("arguments[0].click();", radio_button)
        if request.registration_type == 'APLNR' or request.registration_type == 'APLUN'  or request.registration_type == 'APLEM' or request.registration_type == 'APLOT' or request.registration_type == 'REGOI'  :
            print('inside loooppp====')
            if request.registration_type != 'REGOI':
                pass_number_field = driver.find_element(By.ID, 'pp_number')
                if pass_number_field:
                    pass_number_field.clear()
                    pass_number_field.send_keys(pan_number)
                           
                           
            
            auth_name_field = driver.find_element(By.ID, 'auth_name')
            driver.execute_script("arguments[0].scrollIntoView(true);", auth_name_field)
            auth_name_field.clear()
            auth_name_field.send_keys(name_authorized_signatory)
            
            pan_card_field = driver.find_element(By.ID, 'pan_card2')
            pan_card_field.clear()
            pan_card_field.send_keys(pan_number_authorised_signatory)	


        pan_field = driver.find_element(By.ID, 'pan_card')
        
        driver.execute_script("arguments[0].scrollIntoView(true);", pan_field)
        pan_field.clear()
        if pan_number:
            pan_field.send_keys(pan_number)	
        else : 
            pan_field.send_keys(tan_number)	

        enter_text_field(driver, 'email',email)
        enter_text_field(driver, 'mobile',mobile_number)
       
        if request.registration_type == 'REGOI':
            enter_text_field(driver, 'taxid',pan_number)           
            
            check_box_field = driver.find_element(By.XPATH, '//label[@for="ar_ind"]')
    # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", check_box_field)
            check_box_field.click()

            enter_text_field(driver,'arname',legal_name)
            enter_text_field(driver,'arpan',pan_number)
            enter_text_field(driver,'aremail',email)
            enter_text_field(driver,'armobile',mobile_number)         
            

        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@type="button" and @ng-click="play()"]'))
        )
        driver.execute_script("arguments[0].click();", button)

        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, 'captcha')))

        captcha_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, 'captcha'))
        )
        expected_captcha_length =6
        # Wait for manual captcha entry
        WebDriverWait(driver, 120).until(
            lambda driver: len(captcha_input.get_attribute('value')) == expected_captcha_length
        )
        time.sleep(5)

        proceed_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(text(), "Proceed")]'))
        )
        driver.execute_script("arguments[0].click();", proceed_button)              

        otp_page(driver)

    except Exception as e:
        driver.quit()
        del webdriver_sessions[session_id]
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/start_gst_login")
def start_gst_login(
     trn_no: str,
     customer_id : int,
     db : Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
     ):
    session_id = str(uuid.uuid4())
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    log_id = auth_info.get("log_id")
    browser_name = get_browser_name(user_id,log_id,db)
    # driver = webdriver.Chrome()
    driver      = get_driver(browser_name)

    webdriver_sessions[session_id] = driver
    
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    try:
        # Load login page and fill login details (similar to the code you have)
        driver.get("https://reg.gst.gov.in/registration/")
        
        # customer_details = get_customer_details(db,customer_id, user_id)
     
        # Select the radio button
        second_radio_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="radio" and @value="T" and @id="radiotrn"]'))
        )
        driver.execute_script("arguments[0].click();", second_radio_button)

        trn_no_field = driver.find_element(By.ID, 'trnno')
        driver.execute_script("arguments[0].scrollIntoView(true);", trn_no_field)
        trn_no_field.clear()
        trn_no_field.send_keys(trn_no)
        
        # Audio CAPTCHA
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@type="button" and @ng-click="play()"]'))
        )
        driver.execute_script("arguments[0].click();", button)

        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, 'captchatrn')))

        captcha_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, 'captchatrn'))
        )
        expected_captcha_length =6
        # Wait for manual captcha entry
        WebDriverWait(driver, 120).until(
            lambda driver: len(captcha_input.get_attribute('value')) == expected_captcha_length
        )
        time.sleep(5)

        proceed_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(text(), "Proceed")]'))
        )
        driver.execute_script("arguments[0].click();", proceed_button)
        # otp_page(driver)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'mobile_otp')))
        # print("OTP page loaded, waiting for manual OTP input...")

        otp_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, 'mobile_otp'))
        )

        expected_otp_length = 6
        WebDriverWait(driver, 120).until(
            lambda driver: len(otp_input.get_attribute('value')) == expected_otp_length
        )

        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(text(), "Proceed")]'))
        )
        submit_button.click()

        WebDriverWait(driver, 50).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'dimmer-holder'))
        )

        edit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='button'  and @title='Edit']"))
        )
        edit_button.click()
        
        # Add any necessary wait or logic for completing the login
        # Store the session state, cookies if needed for further steps

        return {"session_id": session_id,
                'user_id': user_id,
                'customer_id': customer_id,
                "message": "Login page filled successfully. Proceed to OTP entry."}
    
    except Exception as e:
        driver.quit()
        del webdriver_sessions[session_id]
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fill_business_details")
def fill_business_details(session_id: str,
                            customer_id :int ,
                            service_task_id : int,
                            # business_details: BusinessDetails,
                            db: Session = Depends(get_db),
                            token: str = Depends(oauth2.oauth2_scheme)
):
    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    # is_composition =customer_details['customer_other_details']['casual_taxable_person']['is_applying_as_casual_taxable_person']

    customer_details = get_customer_details(db,customer_id, service_task_id ,user_id)
    trade_name                  = customer_details['customer_business_details']['trade_name']
    business_constitution_code  = customer_details['customer_business_details']['business_constitution_code']
    is_composition              = customer_details['customer_other_details']['option_for_composition']['is_applying_as_composition_taxable_person']
    is_casual                   = customer_details['customer_other_details']['casual_taxable_person']['is_applying_as_casual_taxable_person']
    gst_registration_required_from_date = customer_details['customer_other_details']['casual_taxable_person']['gst_registration_required_from_date']
    gst_registration_required_to_date   = customer_details['customer_other_details']['casual_taxable_person']['gst_registration_required_to_date']
    if gst_registration_required_from_date:
        from_date_str = gst_registration_required_from_date.strftime("%d/%m/%Y")
    if gst_registration_required_to_date:
        to_date_str = gst_registration_required_to_date.strftime("%d/%m/%Y")

    integrated_tax      = customer_details['customer_other_details']['casual_taxable_person']['estimated_igst_turnover']
    central_tax         = customer_details['customer_other_details']['casual_taxable_person']['estimated_cgst_turnover']
    state_tax           = customer_details['customer_other_details']['casual_taxable_person']['estimated_sgst_turnover']
    cess_value          = customer_details['customer_other_details']['casual_taxable_person']['estimated_cess_turnover']

    integrated_liability_tax      = customer_details['customer_other_details']['casual_taxable_person']['estimated_net_igst_liability']
    central_liability_tax         = customer_details['customer_other_details']['casual_taxable_person']['estimated_net_cgst_liability']
    state_liability_tax           = customer_details['customer_other_details']['casual_taxable_person']['estimated_net_sgst_liability']
    cess_liability_value          = customer_details['customer_other_details']['casual_taxable_person']['estimated_net_cess_liability']
    reason_to_obtain_registration = customer_details['customer_other_details']['reason_to_obtain_registration']['reason_to_obtain_gst_registration_code']
    
    commencement_date             = customer_details['customer_other_details']['reason_to_obtain_registration']['commencement_of_business_date']
    liability_to_register_arises_date = customer_details['customer_other_details']['reason_to_obtain_registration']['liability_to_register_arises_date']

    # commencement_formatted = datetime.strptime(commencement_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    # liability_formatted = datetime.strptime(liability_to_register_arises_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    commencement_formatted = commencement_date.strftime("%d/%m/%Y")
    liability_formatted     = liability_to_register_arises_date.strftime("%d/%m/%Y")
    
    try:
        # Assuming the previous endpoint has logged in, continue to fill the next page
        WebDriverWait(driver, 300).until(EC.url_contains('business'))
        
        enter_text_field(driver,'trdnm',trade_name)
       
        WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.ID, 'bd_ConstBuss')))
        const_field = Select(driver.find_element(By.ID, 'bd_ConstBuss'))
        const_field.select_by_value(business_constitution_code)  
        if is_composition == 'no':
            casual_button = driver.find_element(By.XPATH, '//label[@for="casual"]')
            composition_button = driver.find_element(By.XPATH, '//label[@for="composition"]')
            if composition_button.is_selected():
                composition_button.click()            
          
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", casual_button)
            casual_button.click()
            if from_date_str:
                date_from_field = WebDriverWait(driver, 50).until(
                    EC.visibility_of_element_located((By.ID, "prdt"))
                )
    #             # Clear any pre-filled data and enter the new date
                date_from_field.clear()
                date_from_field.send_keys(from_date_str)
            date_to_field = WebDriverWait(driver, 50).until(
                EC.visibility_of_element_located((By.ID, "prdto"))
            )
            if to_date_str:
                WebDriverWait(driver, 50).until(lambda d: date_to_field.is_enabled())

                # Clear any pre-filled data and enter the new date only if it's enabled
                if date_to_field.is_enabled():
                    date_to_field.clear()
                    date_to_field.send_keys(to_date_str)
            integrated_tax_field = driver.find_element(By.ID, 'est ')
            driver.execute_script("arguments[0].scrollIntoView(true);", integrated_tax_field)
            integrated_tax_field.clear()
            integrated_tax_field.send_keys(integrated_tax)
            enter_text_field(driver, 'libest ',integrated_liability_tax)
            enter_text_field(driver, 'cgst ',central_tax)
            enter_text_field(driver, 'libcgst ',central_liability_tax)
            enter_text_field(driver, 'sgst ',state_tax)
            enter_text_field(driver, 'libsgst ',state_liability_tax)
            enter_text_field(driver, 'cess ',cess_value)
            enter_text_field(driver, 'libcess ',cess_liability_value)
           
        if is_composition == 'yes':
            casual_button = driver.find_element(By.XPATH, '//label[@for="casual"]')

            if casual_button.is_selected():
                casual_button.click()
            composition_button = driver.find_element(By.XPATH, '//label[@for="composition"]')

            driver.execute_script("arguments[0].scrollIntoView(true);", composition_button)
            # composition_button.click()
            # if not composition_button.is_selected():
            composition_button.click()

            check_box1 = WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.ID, 'bd_ck_mgnag'))
            )
            # Check the checkbox if it is present
            if not check_box1.is_selected():
                check_box1.click()

            # driver.execute_script("arguments[0].scrollIntoView(true);", check_box1)
            check_box2 = driver.find_element(By.ID,'bd_ck_smrcp')
            driver.execute_script("arguments[0].scrollIntoView(true);", check_box2)
            if not check_box2.is_selected():
                check_box2.click()
            check_box3 = driver.find_element(By.ID,'bd_ck_others')
            driver.execute_script("arguments[0].scrollIntoView(true);", check_box3)
            if not check_box3.is_selected():
                check_box3.click()
            check_box4 = driver.find_element(By.ID,'cdec')
            if not check_box4.is_selected():
                check_box4.click()

        WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.ID, 'bd_rsl')))
        reason_field = Select(driver.find_element(By.ID, 'bd_rsl'))
        reason_field.select_by_value(reason_to_obtain_registration)

        # commencement_date = driver.find_element(By.ID, 'bd_cmbz')
        # driver.execute_script("arguments[0].value = '08/10/2024';", commencement_date)
        date_to_enter = "09/10/2024"  # Replace with your desired date in "DD/MM/YYYY" format
        date_to_enter = commencement_formatted
        try:
            # Wait for the date field to be visible
            date_field = WebDriverWait(driver, 50).until(
                EC.visibility_of_element_located((By.ID, "bd_cmbz"))
            )
            # Clear any pre-filled data and enter the new date
            date_field.clear()
            date_field.send_keys(date_to_enter)
        except Exception as e:
            print(f"Error filling the date: {e}")
        liability_date = driver.find_element(By.ID, 'lib')
        driver.execute_script(f"arguments[0].value = '{liability_formatted}';", liability_date)
        existing_registrations = customer_details['customer_other_details']['existing_registrations']
        for registration in existing_registrations:
            existing_registration_number = registration['registration_number']
            existing_registration_code = registration['registration_type_code']
            existing_registration_date  = registration['registration_date']
            formated_date = existing_registration_date.strftime("%d/%m/%Y")
            WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.ID, 'exty')))
            type_field = Select(driver.find_element(By.ID, 'exty'))
            type_field.select_by_value(existing_registration_code)
            enter_text_field(driver, 'exno', existing_registration_number)
            # exdt
            existing_reg_date_field = WebDriverWait(driver, 50).until(
                EC.visibility_of_element_located((By.ID, "exdt"))
            )
            # Clear any pre-filled data and enter the new date
            existing_reg_date_field.clear()
            existing_reg_date_field.send_keys(formated_date)
            # addexist
            add_button = driver.find_element(By.XPATH, "//button[@title='Add' and @name='addexist']")
            add_button.click()
        
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, 'tr_upload')))
        
        # Locate the file input field
        file_input = driver.find_element(By.ID, 'tr_upload')  # Use the appropriate locator

        file_path = r'C:\BHARAT-TAXES-CA-ERP-API\uploads\invoice\aiwa licence.pdf'

        # Send the file path to the input element to upload it automatically
        file_input.send_keys(file_path)


        time.sleep(5)
        
        const_field = Select(driver.find_element(By.ID, 'bd_ConstBuss'))
        # const_field.select_by_value(business_details.constitution)
        const_field.select_by_value(business_constitution_code)

        submit_button = driver.find_element(By.XPATH, "//button[@title='Save & Continue']")
        submit_button.click()
        if is_composition == 'yes':
            WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Confirmation')]")))

            # Locate the checkbox by its ID and check if it’s already selected
            checkbox = driver.find_element(By.ID, 'comp_decl')
            if not checkbox.is_selected():
                checkbox.click()  # Click to select it
                
            confirm_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='CONFIRM']"))
            )
            confirm_button.click()  
        
        # Complete additional business details as required
        return {"message": "Business details filled successfully",
                'session_id': session_id}

    except Exception as e:
        driver.quit()
        del webdriver_sessions[session_id]
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill-promoters-directors-details")
def fill_promoters_directors_details(session_id: str, 
                        customer_id :int ,
                        service_task_id : int,
                        business_details: BusinessDetails,
                        db: Session = Depends(get_db),
                        token: str = Depends(oauth2.oauth2_scheme)):
    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    promoters_details = get_stakeholder_details(db,customer_id, service_task_id,'PROMOTER_PARTNER_DIRECTOR',user_id)

    # for person in promoters_details:
    for index, person in enumerate(promoters_details):
        first_name      = person['personal_information']['first_name']
        middle_name     = person['personal_information']['middle_name']
        last_name       = person['personal_information']['last_name']
        f_first_name    = person["personal_information"]["fathers_first_name"]
        f_middle_name   = person["personal_information"]["fathers_middle_name"]
        f_last_name     = person["personal_information"]["fathers_last_name"]
        locality_name   = person["address"]["locality"]
        pin_code        = person["address"]["pin_code"]
        floor_number    = person["address"]["floor_number"]
        land_mark        = person["address"]["landmark"]
        building_flat_number = person["address"]["building_flat_number"]
        road_street_name     = person["address"]["road_street_name"]
        building_name        = person["address"]["premises_building_name"]
        email                = person["contact_details"]["email_address"]
        mobile_number        = person["contact_details"]["mobile_number"]
        date_of_birth        = person["personal_information"]["date_of_birth"]  
        gender               = person["personal_information"]["gender"]
        telephone_no_std_code = person["contact_details"]["telephone_number_with_std_code"]
        pan_number            = person["personal_information"]["pan_number"]
        passport_number       = person["personal_information"]["passport_number"]

        WebDriverWait(driver, 300).until(EC.url_contains('promoters'))
        first_name_field = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.ID, "fnm"))
        )
        enter_text_field(driver, 'fnm', first_name)
        enter_text_field(driver,'pd_mname',middle_name)
        enter_text_field(driver,'pd_lname',last_name)
        fathers_name = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.ID, "ffname"))
        )
        enter_text_field(driver, 'ffname',f_first_name )
        enter_text_field(driver, 'pd_fmname',f_middle_name )
        enter_text_field(driver, 'pd_flname',f_last_name )

        date_of_birth_field = driver.find_element(By.ID,'dob')
        date_to_enter = date_of_birth
        date_str = date_to_enter.strftime("%d/%m/%Y")
        if date_of_birth_field.is_enabled():
            date_of_birth_field.clear()
            date_of_birth_field.send_keys( date_str)
        enter_text_field(driver, 'mbno',mobile_number )
        enter_text_field(driver, 'pd_email',email )
        try:
            print('business_details.gender', gender)
            if gender == 'Male':
    # Wait until the radio button for 'Male' is visible and click it
                male_radio =  driver.find_element(By.XPATH, "//input[@name='gd' and @value='M']")
                male_radio.click()  # Selects the Male radio button
            elif gender == 'Female':
           
                # Select radio button by value
                radio_button = driver.find_element(By.XPATH, "//input[@name='gd' and @value='F']")
                radio_button.click()

                # female_radio.click()  # Selects the Female radio button
            else :
            # Optionally, to select the Others radio button:
                others_radio  = driver.find_element(By.XPATH, "//input[@name='gd' and @value='O']")
                others_radio.click()  # Selects the Others radio button        
                

        except Exception as e:
            print(f"Error selecting radio button: {e}")

        #telstd tlphno
        area_code = '04734'
        tel_number =  224767
        telstd_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "telstd"))
        )
        # Clear the field and send the area code
        telstd_field.clear()
        telstd_field.send_keys(area_code)
        # Trigger Angular change detection by dispatching the 'input' event
        driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", telstd_field)
        tel_number_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "tlphno"))
        )
        # Clear the field and send the area code
        tel_number_field.clear()
        tel_number_field.send_keys(tel_number)

        enter_text_field(driver, 'dg','PROPRIETOR' )
        enter_text_field(driver, 'din','00000001' )
        enter_text_field(driver,'pan', pan_number)
        enter_text_field(driver, 'ppno',passport_number )
        enter_text_field(driver, 'pncd',pin_code)
        
        try:
                
                pin_code_field = driver.find_element(By.ID, 'pncd')
                if pin_code_field.is_enabled():
                        # Clear and input the pin code
                        pin_code_field.clear()
                        pin_code_field.send_keys(pin_code)
                        
                        # Dispatch 'input' event to trigger any suggestion list updates
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", pin_code_field)

                        # Wait for suggestion list to load
                        suggestion_list_xpath = "//li[contains(@ng-repeat, 'suggestionPincode')]"
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_all_elements_located((By.XPATH, suggestion_list_xpath))
                        )

                        # Wait for and click the specific pin code suggestion
                        suggestion_xpath = f"//li[contains(., '{pin_code}')]"
                        suggestion_item = WebDriverWait(driver, 50).until(
                            EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
                        )
                        suggestion_item.click()
                        
                else:
                    print("Pin code field is not enabled for input.")
        except TimeoutException:
                print("The suggestion list did not appear, or the desired item was not found.")
            # city_field = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.ID, "city"))
            # )
    # Clear and fill in the city field
        # city_field = driver.find_element(By.ID, 'city')
        city_name = "Kasargod"  # Replace with the desired city name
        # city_field.clear()
        # city_field.send_keys(city_name)        
        enter_text_field(driver,'city',city_name)
        # Wait for the suggestions to appear
        try:
            suggestion_list_xpath = "//li[contains(@ng-repeat, 'suggestionCity')]"
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, suggestion_list_xpath))
            )

            suggestion_xpath = f"//li[contains(., '{city_name}')]"
            suggestion_item = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
            )
            
            # Click on the suggestion
            suggestion_item.click()
        except TimeoutException:
            print("The suggestion list did not appear, or the desired item was not found.")

        enter_text_field(driver, 'pd_locality',locality_name)
        enter_text_field(driver, 'pd_road',road_street_name)
        enter_text_field(driver, 'pd_bdname',building_name)
        enter_text_field(driver, 'pd_bdnum',building_flat_number)
        enter_text_field(driver, 'pd_flrnum',floor_number)
        enter_text_field(driver, 'pd_landmark',land_mark) 
    
        

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'pd_upload')))
        # Locate the file input field
        file_input = driver.find_element(By.ID, 'pd_upload')  # Use the appropriate locator

        # Specify the file path
        # file_path = '/path/to/your/file.txt'
        file_path = r'C:\BHARAT-TAXES-CA-ERP-API\uploads\captcha_modified_images\12057.jpg'

        # Send the file path to the input element to upload it automatically
        file_input.send_keys(file_path)

        # checkbox = WebDriverWait(driver, 20).until(
        #     EC.element_to_be_clickable((By.ID, "pri_auth"))
        #     )
        # checkbox = driver.find_element(By.XPATH, '//label[@for="pri_auth"]')
  
        # Check if the checkbox is already selected
        # if not checkbox.is_selected():
            # Click the checkbox to select it
        #     checkbox.click()
        #     print("Checkbox is now checked.")
        # else:
        #     print("Checkbox was already checked.")  
                                


        # Wait until the button is enabled and clickable
        if index < len(promoters_details) - 1:
            # Wait until the "Add New" button is clickable and click it
            add_new_button = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Add New' and @data-ng-click=\"addPromoter('savenew')\"]"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", add_new_button)
            add_new_button.click()
            print("Add New button clicked for promoter:", index + 1)
        else:
            print("No more promoters to add.")

    
    try:
        save_continue_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Save & Continue' and @type='submit' and contains(@class, 'btn-primary')]"))
        )
        # Scroll the button into view if necessary
        driver.execute_script("arguments[0].scrollIntoView();", save_continue_button)
        
        # Click the "Save & Continue" button
        save_continue_button.click()
        print("Save & Continue button clicked successfully.")
    except TimeoutException:
        print("Save & Continue button did not appear or was not clickable.")

    except NoSuchWindowException:
        print("The browser window was closed unexpectedly.")

@router.post('/fill-authorized-signatory')
def fill_authorized_signatory(
    session_id : str,    
    customer_id : int,
    service_task_id : int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)):

    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    WebDriverWait(driver, 300).until(EC.url_contains('authsignatory'))
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'auth_prim'))
    )
    
        # Fill in the checkbox (Primary Authorized Signatory)
    checkbox = driver.find_element(By.ID, 'auth_prim')
    if not checkbox.is_selected():
        checkbox.click() 
    promoters_details = get_stakeholder_details(db,customer_id,service_task_id, 'AUTHORIZED_SIGNATORY',user_id)
    
    for index, person in enumerate(promoters_details):
        first_name      = person['personal_information']['first_name']
        middle_name     = person['personal_information']['middle_name']
        last_name       = person['personal_information']['last_name']
        f_first_name    = person["personal_information"]["fathers_first_name"]
        f_middle_name   = person["personal_information"]["fathers_middle_name"]
        f_last_name     = person["personal_information"]["fathers_last_name"]
        locality_name   = person["address"]["locality"]
        pin_code        = person["address"]["pin_code"]
        floor_number    = person["address"]["floor_number"]
        land_mark        = person["address"]["landmark"]
        building_flat_number = person["address"]["building_flat_number"]
        road_street_name     = person["address"]["road_street_name"]
        building_name        = person["address"]["premises_building_name"]
        email                = person["contact_details"]["email_address"]
        mobile_number        = person["contact_details"]["mobile_number"]
        date_of_birth        = person["personal_information"]["date_of_birth"]  
        gender               = person["personal_information"]["gender"]
        telephone_no_std_code = person["contact_details"]["telephone_number_with_std_code"]
        pan_number            = person["personal_information"]["pan_number"]
        passport_number       = person["personal_information"]["passport_number"]      

        
    #     try:
    #     # Wait for the checkbox to be clickable
    # #         checkbox = WebDriverWait(driver, 20).until(
    # #     EC.element_to_be_clickable((By.XPATH, "//input[@id='auth_prim']"))
    # # )
         
    
    #         checkbox = driver.find_element(By.XPATH, "//input[@id='auth_prim' and @data-ng-click=\"makePAuthSign(as)\"]")
    #         # checkbox = driver.find_element(By.XPATH, "//label[@for='auth_prim'")

    #         driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
            
    #         # Check the current status of the checkbox
    #         print('Checkbox status (before):', checkbox.is_selected())
            
    #         # Click the checkbox if it is not already selected
    #         if not checkbox.is_selected():
    #             checkbox.click()
    #             print("Checkbox is now checked.")
    #         else:
    #             print("Checkbox was already checked.")
    #     except Exception as e:
    #         print(f"Error interacting with the checkbox: {type(e).__name__}: {e}")

        first_name_field = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.ID, "fnm"))
        )
        enter_text_field(driver, 'fnm', first_name)
        enter_text_field(driver,'as_mname',middle_name)
        enter_text_field(driver,'as_lname',last_name)
        fathers_name = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.ID, "ffname"))
        )
        enter_text_field(driver, 'ffname',f_first_name )
        enter_text_field(driver, 'as_fmname',f_middle_name )
        enter_text_field(driver, 'as_flname',f_last_name )

        date_of_birth_field = driver.find_element(By.ID,'dob')
        date_to_enter = date_of_birth
        date_str = date_to_enter.strftime("%d/%m/%Y")
        if date_of_birth_field.is_enabled():
            date_of_birth_field.clear()
            date_of_birth_field.send_keys( date_str)
        enter_text_field(driver, 'mbno',mobile_number )
        enter_text_field(driver, 'em',email )
        try:
            print('business_details.gender', gender)
            if gender == 'Male':
    # Wait until the radio button for 'Male' is visible and click it
                male_radio =  driver.find_element(By.XPATH, "//input[@name='gd' and @value='M']")
                male_radio.click()  # Selects the Male radio button
            elif gender == 'Female':
           
                # Select radio button by value
                radio_button = driver.find_element(By.XPATH, "//input[@name='gd' and @value='F']")
                radio_button.click()

                # female_radio.click()  # Selects the Female radio button
            else :
            # Optionally, to select the Others radio button:
                others_radio  = driver.find_element(By.XPATH, "//input[@name='gd' and @value='O']")
                others_radio.click()  # Selects the Others radio button        
                

        except Exception as e:
            print(f"Error selecting radio button: {e}")

        #telstd tlphno
        area_code = '04734'
        tel_number =  224767
        telstd_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "tlpnstd"))
        )
        # Clear the field and send the area code
        telstd_field.clear()
        telstd_field.send_keys(area_code)
        # Trigger Angular change detection by dispatching the 'input' event
        driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", telstd_field)
        tel_number_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "tlphno"))
        )
        # Clear the field and send the area code
        tel_number_field.clear()
        tel_number_field.send_keys(tel_number)

        enter_text_field(driver, 'dg','PROPRIETOR' )
        enter_text_field(driver, 'din','00000001' )
        enter_text_field(driver,'pan', pan_number)
        enter_text_field(driver, 'ppno',passport_number )
        enter_text_field(driver, 'pncd',pin_code)
        
        try:
                
                pin_code_field = driver.find_element(By.ID, 'pncd')
                if pin_code_field.is_enabled():
                        # Clear and input the pin code
                        pin_code_field.clear()
                        pin_code_field.send_keys(pin_code)
                        
                        # Dispatch 'input' event to trigger any suggestion list updates
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", pin_code_field)

                        # Wait for suggestion list to load
                        suggestion_list_xpath = "//li[contains(@ng-repeat, 'suggestionPincode')]"
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_all_elements_located((By.XPATH, suggestion_list_xpath))
                        )

                        # Wait for and click the specific pin code suggestion
                        suggestion_xpath = f"//li[contains(., '{pin_code}')]"
                        suggestion_item = WebDriverWait(driver, 50).until(
                            EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
                        )
                        suggestion_item.click()
                        
                else:
                    print("Pin code field is not enabled for input.")
        except TimeoutException:
                print("The suggestion list did not appear, or the desired item was not found.")
            # city_field = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.ID, "city"))
            # )
    # Clear and fill in the city field
        # city_field = driver.find_element(By.ID, 'city')
        city_name = "Kasargod"  # Replace with the desired city name
        # city_field.clear()
        # city_field.send_keys(city_name)        
        enter_text_field(driver,'city',city_name)
        # Wait for the suggestions to appear
        try:
            suggestion_list_xpath = "//li[contains(@ng-repeat, 'suggestionCity')]"
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, suggestion_list_xpath))
            )

            suggestion_xpath = f"//li[contains(., '{city_name}')]"
            suggestion_item = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
            )
            
            # Click on the suggestion
            suggestion_item.click()
        except TimeoutException:
            print("The suggestion list did not appear, or the desired item was not found.")

        enter_text_field(driver, 'as_locality',locality_name)
        enter_text_field(driver, 'st',road_street_name)
        enter_text_field(driver, 'as_bdname',building_name)
        enter_text_field(driver, 'bno',building_flat_number)
        enter_text_field(driver, 'as_flrnum',floor_number)
        enter_text_field(driver, 'as_landmark',land_mark) 
    
        

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'as_upload_photo')))
        # Locate the file input field
        file_input = driver.find_element(By.ID, 'as_upload_photo')  # Use the appropriate locator

        # Specify the file path
        # file_path = '/path/to/your/file.txt'
        file_path = r'C:\BHARAT-TAXES-CA-ERP-API\uploads\captcha_modified_images\12057.jpg'

        # Send the file path to the input element to upload it automatically
        file_input.send_keys(file_path)
        select_proof = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "as_up_type"))
         )
        
          #Locate the dropdown
        dropdown = driver.find_element(By.ID, "as_up_type")
        
        # Wrap the element with the Select class
        select = Select(dropdown)
        
        # Select an option by value
        select.select_by_value("LOAU")
        print("Selected option by value: Letter of Authorisation")
                           


        # Wait until the button is enabled and clickable
        if index < len(promoters_details) - 1:
            # Wait until the "Add New" button is clickable and click it
            add_new_button = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Add New' and @data-ng-click=\"addAuthourized('savenew')\"]"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", add_new_button)
            add_new_button.click()
            print("Add New button clicked for promoter:", index + 1)
        else:
            print("No more promoters to add.")

    try:
        save_continue_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.ID, "save-continue-button"))
        )
        save_continue_button.click()
    except TimeoutException:
            print("The 'Save and Continue' button was not found within the specified time.")
    except NoSuchWindowException:
        print("The browser window was closed unexpectedly.")


@router.post('/fill-authorized-representative')
def fill_authorized_representative(
    session_id : str,
    customer_id : int,
    service_task_id : int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)):

    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    enrollment_id = '321900004442GPV'
    WebDriverWait(driver, 300).until(EC.url_contains('authrepresentative'))
    time.sleep(10)
    has_auth_representative_button = driver.find_element(By.XPATH, '//label[@for="as_cit_ind"]')
    
    driver.execute_script("arguments[0].scrollIntoView(true);", has_auth_representative_button)

    has_auth_representative_button.click()
    
    # radio_button = driver.find_element(By.XPATH, "//input[@name='arep_AR' and @value='TRP']")
    
    # # Scroll into view if needed
    # driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)
    
    # # Click the radio button if not already selected
    # # if not radio_button.is_selected():
    # radio_button.click()
    # enter_text_field(driver, 'ar_eid',enrollment_id)
    # search_button = WebDriverWait(driver, 10).until(
    # EC.element_to_be_clickable((By.XPATH, "//button[@data-ng-click='getAuthRep(enrolmentId,rpayload.arepdtls.typAR)']"))
    # )

    # # Click the button
    # search_button.click()
    radio_button = driver.find_element(By.XPATH, "//input[@name='arep_AR' and @value='OTHR']")
   
    # # Scroll into view if needed
    driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)
    
    # # Click the radio button if not already selected
    # if not radio_button.is_selected():
    radio_button.click()
    repersentative_details = get_stakeholder_details(db,customer_id,service_task_id, 'AUTHORIZED_REPRESENTATIVE',user_id)
    for person in repersentative_details:
        # ar_first_name   = person['personal_information']['first_name']
        ar_middle_name  = person['personal_information']['middle_name']
        ar_last_name    = person['personal_information']['last_name']
        ar_mobile_no    = person['contact_details']['mobile_number']
        ar_email        = person['contact_details']['email_address']
        ar_pan          = person['personal_information']['pan_number']
        telephone_number_with_std_code =  person['contact_details']['telephone_number_with_std_code']
        std_code, telephone_number = telephone_number_with_std_code.split("-")

        ar_tlphone_std  =   std_code
        ar_telephone_no = telephone_number
        # ar_fax_std      = '586'
        # ar_fax_no       = '38744'
        designation     = person['identity_information']['designation_code']
        # designation         = 'cah'
        enter_text_field(driver, 'ar_fname', person['personal_information']['first_name'])
        enter_text_field(driver, 'ar_mname', ar_middle_name)
        enter_text_field(driver, 'ar_lname', ar_last_name)
        
        designation_field = Select(driver.find_element(By.ID, 'ar_des'))
        designation_field.select_by_value(designation)
        
        enter_text_field(driver,'ar_mbno',ar_mobile_no)
        enter_text_field(driver, 'ar_em', ar_email)
        enter_text_field(driver, 'pan', ar_pan)
        enter_text_field(driver, 'ar_tlphnostd', ar_tlphone_std)
        enter_text_field(driver, 'tlphno',ar_telephone_no)
        # enter_text_field(driver, 'ar_fxno', ar_fax_std)
        # enter_text_field(driver, 'fxno', ar_fax_no)
    save_continue_button = WebDriverWait(driver, 50).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='Save & Continue' and @type='submit' and contains(@class, 'btn-primary')]"))
    )
    # Scroll the button into view if necessary
    driver.execute_script("arguments[0].scrollIntoView();", save_continue_button)
    
    # Click the "Save & Continue" button
    save_continue_button.click()

@router.post('/fill_principal_place')
def fill_principal_place(session_id : str,
    customer_id : int,
    service_task_id : int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)):

    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    WebDriverWait(driver, 300).until(EC.url_contains('business/place'))
    principal_place_details = get_business_place(customer_id,service_task_id,'PRINCIPAL_PLACE_ADDRESS',db,user_id)
    
    business_places = principal_place_details.get("business_places", [])

    # Check if the list is not empty
    if business_places:
        # Access the first dictionary in the list and get the pin_code
        pin_code = business_places[0].get("pin_code", " ")  # Use the first item
        print('Pin Code:', pin_code)
    else:
        print("No business places available")
        # pin_code            = principal_place_details['business_places']['pin_code']
    locality_name       = business_places[0].get('locality', " ") 
    road_street_name    = business_places[0].get('road_street_name', " ") 
    building_name       = business_places[0].get('premises_building_name', " ") 
    building_flat_number = business_places[0].get('building_flat_number', " ") 
    floor_number        = business_places[0].get('floor_number', " ") 
    land_mark           = business_places[0].get('landmark', " ") 
    office_email_address = business_places[0].get('office_email_address', " ")
    office_mobile_number = business_places[0].get('office_mobile_number', " ")
    office_phone_std_code =business_places[0].get('office_phone_std_code', " ")
    office_phone_number   =business_places[0].get('office_phone_number', " ")
    office_fax_std_code      = business_places[0].get('office_fax_std_code', " ")
    office_fax_number      = business_places[0].get('office_fax_number', " ")
    nature_of_possession   = business_places[0].get('nature_of_possession', " ")

        # pin_code = '671317'
    pin_code_field = driver.find_element(By.ID, 'pncd')
    if pin_code_field.is_enabled():
            # Clear and input the pin code
            pin_code_field.clear()
            pin_code_field.send_keys(pin_code)
            
            # Dispatch 'input' event to trigger any suggestion list updates
            driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", pin_code_field)

            # Wait for suggestion list to load
            suggestion_list_xpath = "//li[contains(@ng-repeat, 'suggestionPincode')]"
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, suggestion_list_xpath))
            )

            # Wait for and click the specific pin code suggestion
            suggestion_xpath = f"//li[contains(., '{pin_code}')]"
            suggestion_item = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
            )
            suggestion_item.click()
            
    else:
        print("Pin code field is not enabled for input.")

    enter_text_field(driver, 'ppbzdtls_locality',locality_name)
    enter_text_field(driver, 'st',road_street_name)
    enter_text_field(driver, 'bp_bdname',building_name)
    enter_text_field(driver, 'bno',building_flat_number)
    enter_text_field(driver, 'bp_flrnum',floor_number)
    enter_text_field(driver, 'ppbzdtls_landmark',land_mark) 
    #stj
    listbox = Select(driver.find_element(By.ID, "stj"))
    print('listbox', listbox.select_by_index(0))
    listbox.select_by_index(0)
#     WebDriverWait(driver, 10).until(
#     lambda d: len(Select(d.find_element(By.ID, "stj")).options) > 0
# )
   
    enter_text_field(driver, 'bp_email', office_email_address)
    enter_text_field(driver, 'tlphnoStd',office_phone_std_code)
    enter_text_field(driver,'tlphno',office_phone_number)
    enter_text_field(driver, 'bp_mobile',office_mobile_number)
    enter_text_field(driver, 'fxnostd',office_fax_std_code )
    enter_text_field(driver, 'fxno', office_fax_number)
    # bp_up_type
#bp_buss_poss
    nature_of_possession = 'CON'

    nature_of_possession_of_premises = Select(driver.find_element(By.ID, "bp_up_type"))
    # nature_of_possession_of_premises.select_by_value(nature_of_possession)
    nature_of_business =  business_places[0].get("nature_of_business", [])

    for business in nature_of_business:
        business_activity_id = business.get("business_activity_id")
        checkbox_xpath = f"//input[@type='checkbox' and @value='{business_activity_id}']"
        try:
            checkbox = driver.find_element(By.XPATH, checkbox_xpath)
            if not checkbox.is_selected():
                checkbox.click()
        except Exception as e:
            print(f"Checkbox for business activity ID {business_activity_id} not found: {e}")

# bp_add
    additional_business_place = driver.find_element(By.XPATH, '//label[@for="bp_add"]')
#     # Scroll into view
    driver.execute_script("arguments[0].scrollIntoView(true);", additional_business_place)
#         # driver.execute_script("arguments[0].checked= true;", composition_button)
#         time.sleep(3)
    if not additional_business_place.is_selected():
        additional_business_place.click()

    submit_button = driver.find_element(By.XPATH, "//button[@title='Save & Continue']")
    submit_button.click()

@router.post('/fill_additional_bussiness_places')
def fill_additional_bussiness_places(
    session_id : str,
    customer_id : int,
    service_task_id : int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    WebDriverWait(driver, 300).until(EC.url_contains('business/addlplace'))
    additional_place_details = get_business_place(customer_id,service_task_id ,'ADDITIONAL_PLACE',db,user_id)
    business_places = additional_place_details.get("business_places", [])
    count = len(business_places)
    # abp_ctr
    enter_text_field(driver, 'abp_ctr',count)
    if count>0:
        add_new_button = WebDriverWait(driver, 50).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-ng-click=\"addAddlPlace('new')\"]"))
                    )
        driver.execute_script("arguments[0].scrollIntoView();", add_new_button)
            
        if add_new_button.is_enabled():
            # add_new_button.click()
            driver.execute_script("arguments[0].click();", add_new_button)
        else:
            print("The 'Add New' button is disabled due to conditions.")
    i=0
    while count>0:
        
        # add_new_button.click()
        # driver.execute_script("addAddlPlace('new');",add_new_button)
        # add_new_button.click()
    # Check if the list is not empty
        if business_places:
            # Access the first dictionary in the list and get the pin_code
            pin_code = business_places[i].get("pin_code", " ")  # Use the first item
            print('Pin Code:', pin_code)
        else:
            print("No business places available")
            # pin_code            = principal_place_details['business_places']['pin_code']
        locality_name       = business_places[i].get('locality', " ") 
        road_street_name    = business_places[i].get('road_street_name', " ") 
        building_name       = business_places[i].get('premises_building_name', " ") 
        building_flat_number = business_places[i].get('building_flat_number', " ") 
        floor_number        = business_places[i].get('floor_number', " ") 
        land_mark           = business_places[i].get('landmark', " ") 
        office_email_address = business_places[i].get('office_email_address', " ")
        office_mobile_number = business_places[i].get('office_mobile_number', " ")
        office_phone_std_code =business_places[i].get('office_phone_std_code', " ")
        office_phone_number   =business_places[i].get('office_phone_number', " ")
        office_fax_std_code      = business_places[i].get('office_fax_std_code', " ")
        office_fax_number      = business_places[i].get('office_fax_number', " ")
        nature_of_possession   = business_places[i].get('nature_of_possession_code', " ")
        
            # pin_code = '671317'
        pin_code_field = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.ID, "pncd"))
        )
        pin_code_field = driver.find_element(By.ID, 'pncd')
        if pin_code_field.is_enabled():
                # Clear and input the pin code
                pin_code_field.clear()
                pin_code_field.send_keys(pin_code)
                
                # Dispatch 'input' event to trigger any suggestion list updates
                driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", pin_code_field)

                # Wait for suggestion list to load
                suggestion_list_xpath = "//li[contains(@ng-repeat, 'suggestionPincode')]"
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, suggestion_list_xpath))
                )

                # Wait for and click the specific pin code suggestion
                suggestion_xpath = f"//li[contains(., '{pin_code}')]"
                suggestion_item = WebDriverWait(driver, 50).until(
                    EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
                )
                suggestion_item.click()
                
        else:
            print("Pin code field is not enabled for input.")

        enter_text_field(driver, 'ap_locality',locality_name)
        enter_text_field(driver, 'st',road_street_name)
        enter_text_field(driver, 'ap_bdname',building_name)
        enter_text_field(driver, 'abp_bdnum',building_flat_number)
        enter_text_field(driver, 'ap_flrnum',floor_number)
        enter_text_field(driver, 'ap_landmark',land_mark) 
       
    
        enter_text_field(driver, 'ap_email', office_email_address)
        enter_text_field(driver, 'ap_tlpnstd',office_phone_std_code)
        enter_text_field(driver,'tlphno',office_phone_number)
        enter_text_field(driver, 'mbno',office_mobile_number)
        enter_text_field(driver, 'fxnostd',office_fax_std_code )
        enter_text_field(driver, 'fxno', office_fax_number)
        # bp_up_type
    #bp_buss_poss
        # nature_of_possession = 'CON'

        nature_of_possession_of_premises = Select(driver.find_element(By.ID, "psnt"))
        nature_of_possession_of_premises.select_by_value(nature_of_possession)
        # 
        proof = Select(driver.find_element(By.ID, "ap_up_type"))
        proof.select_by_value('CNLR')
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, 'ap_upload')))
        
        # Locate the file input field
        file_input = driver.find_element(By.ID, 'ap_upload')  # Use the appropriate locator

        # Specify the file path
        # file_path = '/path/to/your/file.txt'
        file_path = r'C:\BHARAT-TAXES-CA-ERP-API\uploads\invoice\aiwa licence.pdf'
        file_input.send_keys(file_path)
        nature_of_business =  business_places[i].get("nature_of_business", [])
        other_nature_of_business ='import'
        for business in nature_of_business:
            business_activity_code = business.get("business_activity_code")
            checkbox_xpath = f"//input[@type='checkbox' and @value='{business_activity_code}']"
            try:
                checkbox = driver.find_element(By.XPATH, checkbox_xpath)
                if not checkbox.is_selected():
                    checkbox.click()
            except Exception as e:
                print(f"Checkbox for business activity ID {business_activity_code} not found: {e}")
        count -=1
        i +=1
        enter_text_field(driver,'ap_otherntbz',other_nature_of_business)
        if count!=0:
            save_and_add_new = WebDriverWait(driver, 50).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-ng-click=\"addAddlPlace('savenew')\"]"))
                    )
            driver.execute_script("arguments[0].scrollIntoView();", save_and_add_new)
            
            if save_and_add_new.is_enabled():
                # add_new_button.click()
                driver.execute_script("arguments[0].click();", save_and_add_new)

        if count ==0 :
            # submit_button = driver.find_element(By.XPATH, "//button[@title='Save & Continue']")
            # submit_button.click()
            save_continue_button = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-ng-bind='trans.LBL_SAVE_CONTINUE']"))
            )
            # Scroll the button into view if necessary
            driver.execute_script("arguments[0].scrollIntoView();", save_continue_button)

            # Click the button
            save_continue_button.click()
    continue_button = WebDriverWait(driver, 50).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-ng-bind='trans.LBL_CONTINUE']"))
    )    
    # Scroll the button into view if necessary
    driver.execute_script("arguments[0].scrollIntoView();", continue_button)
    # Check if the button is enabled and displayed
    if continue_button.is_enabled() and continue_button.is_displayed():
        # Click the button
        continue_button.click()

# 
@router.post('/fill_goods_and_services')
def fill_goods_and_services(
    session_id : str,
    customer_id : int,
    service_task_id : int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    WebDriverWait(driver, 300).until(EC.url_contains('goodsservices'))
    hsn_commodities =get_hsn_commodities_by_customer_id(customer_id,service_task_id,user_id,db)
   

    for commodity in hsn_commodities:
        # Locate and fill the HSN/SAC code
        hsn_commodities_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'gs_hsn_value'))
        )
        if hsn_commodities_field.is_enabled():
            hsn_commodities_field.clear()
            hsn_commodities_field.send_keys(commodity['hsn_sac_code'])

        # Trigger the input event
        driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", hsn_commodities_field)

        try:
            # Wait for and select the correct suggestion
            suggestion_xpath = (
                f"//div[contains(@class, 'autocomplete-desc') and text()='{commodity['hsn_sac_description']}']"
            )
            suggestion_item = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
            )
            suggestion_item.click()
        except StaleElementReferenceException:
            # Retry finding and clicking the suggestion if it becomes stale
            suggestion_item = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, suggestion_xpath))
            )
            suggestion_item.click()

    save_continue_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Save & Continue' and @type='submit' and contains(@class, 'btn-primary')]"))
        )

    # Scroll the button into view
    driver.execute_script("arguments[0].scrollIntoView();", save_continue_button)

    # Click the button
    save_continue_button.click()
    print("Save & Continue button clicked successfully.")
    
@router.post('/fill_state_specific_info') 
def fill_state_specific_info(
    session_id : str,
    customer_id : int,
    service_task_id : int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    driver =  get_driver_session(session_id)
    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    WebDriverWait(driver, 300).until(EC.url_contains('statespecific'))
    state_specific_information =get_gst_state_specific_information_by_customer_id(customer_id,service_task_id ,db,user_id)
    if state_specific_information:
    # Access the first item in the list
        state_specific_info = state_specific_information[0]
    
    enter_text_field(driver,'ec_tax',state_specific_info.professional_tax_employee_code)
    enter_text_field(driver,'rc_tax',state_specific_info.professional_tax_registration_certificate)
    enter_text_field(driver,'lic_no',state_specific_info.state_excise_licence_number)
    enter_text_field(driver,'per_lic_no',state_specific_info.excise_licence_holder_name)

    save_continue_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Save & Continue' and @type='submit' and contains(@class, 'btn-primary')]"))
        )

    # Scroll the button into view
    driver.execute_script("arguments[0].scrollIntoView();", save_continue_button)

    # Click the button
    save_continue_button.click()

    
       
@router.on_event("shutdown")
def shutdown_event():
    for driver in webdriver_sessions.values():
        driver.quit()
    webdriver_sessions.clear()

