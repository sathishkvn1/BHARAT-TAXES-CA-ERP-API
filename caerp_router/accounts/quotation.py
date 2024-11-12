import os
from fastapi import APIRouter, Depends,HTTPException,status,Query
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import text
from sqlalchemy.orm import Session
from caerp_db.database import get_db
from caerp_db.accounts import db_quotation
# from caerp_constants.caerp_constants import EntryPoint
from caerp_schema.accounts.quotation_schema import AccProformaInvoiceShema, AccQuotationSchema, AccTaxInvoiceShema
from typing import List, Optional, Union
from datetime import date
from caerp_auth import oauth2
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import EntryPoint
import pdfkit

from caerp_schema.office.office_schema import ServiceRequirementSchema



TEMPLATE_PROFORMA_INVOICE_DETAILS   = "C:/BHARAT-TAXES-CA-ERP-API/templates/proforma_invoice_template.html"
UPLOAD_DIR_INVOICE_DETAILS          = "uploads/invoice"

TEMPLATE_TAX_INVOICE_DETAILS       = "C:/BHARAT-TAXES-CA-ERP-API/templates/tax_invoice_template.html"




router  = APIRouter(
    tags=['Quotation']
)


@router.get('/generate_quotation_service_details')
def generate_quotation_service_details(
    work_order_master_id: int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")   
    financial_year_id   =  auth_info.get("financial_year_id") 
    customer_id         =  auth_info.get("mother_customer_id") 
    result   = db_quotation.generate_quotation_service_details(db,work_order_master_id,financial_year_id,customer_id )
 
    return result


@router.post('/save_quotation_data')
def save_quotation_data(
        request : AccQuotationSchema,
        quotation_id : Optional[int],
        db : Session = Depends(get_db),
        token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    financial_year_id   =  auth_info.get("financial_year_id") 
    customer_id         =  auth_info.get("mother_customer_id")
    result = db_quotation.save_quotation_data(request,user_id,financial_year_id,customer_id,db,quotation_id)
    return result




@router.post('/update_quotation_status')
def update_quotation_status(
        quotation_id : int,
        quotation_status : str,
        # quotation_version: int,
        db:Session = Depends(get_db)
):
   result = db_quotation.update_quotation_status(quotation_id,quotation_status,db)
   return result


@router.post('/send_proposal')
def send_proposal(
    quotation_id :int,
    work_order_master_id : int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    result = db_quotation.send_proposal(quotation_id,work_order_master_id,db)
    return result

@router.get('/get_quotation_list')
def get_quotqtion_list(
    search_value: Union[str, int] = "ALL",
    # status: Optional[str]='ALL',
    status: Union[str, int] = "ALL",
    work_order_master_id : Optional[int] = None,
    quotation_id : Optional[int] = None,
    from_date : Optional[date] = None,
    to_date : Optional[date] =None,
    include_details: Optional[bool] = Query(False),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)

): 
    """
    Fetch a list of quotations with optional filters.

    - **search_value**: String or integer to search quotations by name, email, mobile or quotation_number.
    - **status**: Filter by quotation status.
    - **work_order_master_id**: Filter by work order master ID.
    - **quotation_id**: Filter by specific quotation ID.
    - **from_date**: Include quotations created on or after this date.
    - **to_date**: Include quotations created on or before this date.
    - **include_details**: Boolean to include detailed quotation information.

    **Returns**:
    - List of quotations or a message if no quotations are found.
    """
    result = db_quotation.get_quotation_data(db,include_details,work_order_master_id,quotation_id,status,from_date,to_date,search_value)
#    result = db_quotation.get_quotation_data(db,status,work_order_master_id,quotation_id,from_date,to_date,search_value)
    return result


#--------------------------------------------------------------------------------------------------


TEMPLATE_QUOTATION_DETAILS  = "C:/BHARAT-TAXES-CA-ERP-API/templates/quotation_template.html"
UPLOAD_DIR_QUOTATION_DETAILS       = "uploads/quotation_details"





# def generate_quotation_pdf(quotations, file_path):
#     # Load the template environment
#     template_dir = os.path.dirname(TEMPLATE_QUOTATION_DETAILS)
#     template_name = os.path.basename(TEMPLATE_QUOTATION_DETAILS)
#     env = Environment(loader=FileSystemLoader(template_dir))
#     template = env.get_template(template_name)

#     # Debugging: Check the type and structure of the quotations
#     print('Type of quotations:', type(quotations))
#     print('Quotations content:', quotations)

#     # Prepare data for the template
#     if quotations:
#         if isinstance(quotations, dict):
#             details = quotations.get('quotation_details', [])
#             work_order_master = quotations.get('work_order_master', {})
#         else:
#             # Assuming quotations is an object
#             details = quotations.quotation_details
#             work_order_master = quotations.work_order_master
        
#         # Debugging: Print details and work order master
#         print("Quotation Details:", details)
#         print("Work Order Master:", work_order_master)

#         # Calculate totals and other important fields
#         total = sum(item.get('total_amount', 0) for item in details)
#         additional_discount = quotations['quotation_master'].get('additional_discount', 0)
#         gst_amount = sum(item.get('gst_amount', 0) for item in details)
#         total_amount = quotations['quotation_master'].get('net_amount', 0)
#         round_off = quotations['quotation_master'].get('round_off', 0)
#         bill_discount = quotations['quotation_master'].get('bill_discount', 0)
#         grand_total = quotations['quotation_master'].get('grand_total', 0)

#         # Debugging: Check calculated values
#         print("Total:", total)
#         print("GST Amount:", gst_amount)
#         print("Grand Total:", grand_total)

#         # Prepare the data for rendering in the template
#         data = {
#             'quotations': details,
#             'total': total,
#             'grand_total': grand_total,
#             'additional_discount': additional_discount,
#             'gst_amount': gst_amount,
#             'total_amount': total_amount,
#             'current_date': date.today(),
#             'work_order_master': work_order_master,
#             'round_off': round_off,
#             'bill_discount': bill_discount
#         }

#         # Render the template with the provided data
#         html_content = template.render(data)

#         # Debugging: Print the generated HTML content
#         print("Generated HTML content:", html_content)

#         # PDF generation using pdfkit
#         wkhtmltopdf_path = 'C:/wkhtmltox/wkhtmltopdf/bin/wkhtmltopdf.exe'
#         if not os.path.isfile(wkhtmltopdf_path):
#             raise FileNotFoundError(f'wkhtmltopdf executable not found at path: {wkhtmltopdf_path}')
        
#         config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

#         # PDF options
#         options = {
#             'footer-center': 'Page [page] of [topage]',
#             'footer-font-size': '8',
#             'margin-bottom': '20mm',
#             'no-outline': None
#         }

#         try:
#             # Convert HTML content to PDF
#             pdfkit.from_string(html_content, file_path, configuration=config, options=options)
#         except Exception as e:
#             print(f'Error during PDF generation: {e}')
#             raise RuntimeError(f'Error generating PDF: {e}')

#         # Return the generated PDF file
#         return open(file_path, "rb")


def generate_quotation_pdf(quotations, file_path):

    # Load the template environment
    template_dir = os.path.dirname(TEMPLATE_QUOTATION_DETAILS)
    template_name = os.path.basename(TEMPLATE_QUOTATION_DETAILS)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    # Prepare data for the template
    if quotations:
        # Extract and format data from the quotations object
        # details = quotations[0].quotation_details
        details = quotations[0].quotation_details
        gst_amount = sum(item.igst_amount for item in details)

        for item in details:
            item.service_charge = f"{(item.service_charge + item.govt_agency_fee + item.stamp_fee + item.stamp_duty):.2f}"
            item.discount_amount = f"{item.discount_amount:.2f}" if item.discount_amount is not None else "0.00"
            item.igst_amount = f"{(item.igst_amount + item.cgst_amount + item.sgst_amount):.2f}" if item.igst_amount or item.cgst_amount or item.sgst_amount else "0.00"
            item.total_amount = f"{item.total_amount:.2f}"
            item.taxable_amount = f"{item.taxable_amount:.2f}"
        # total = sum(item.total_amount for item in details)
        # advance = quotations.quotation_master.advance_amount
        additional_discount = f"{quotations[0].quotation_master.additional_discount_amount:.2f}"
        total_amount = f"{quotations[0].quotation_master.net_amount:.2f}"
        round_off  = f"{quotations[0].quotation_master.round_off_amount:.2f}"
        bill_discount = f"{quotations[0].quotation_master.bill_discount_amount:.2f}"
        grand_total = f"{quotations[0].quotation_master.grand_total_amount:.2f}"
        # taxable_amount = f"{quotations[0].quotation_master.taxable_amount:.2f}"
        data = {
            'quotations': details,
            # 'total': total,
            'grand_total': grand_total,
            # 'advance': advance,
            'additional_discount': additional_discount,
            'gst_amount': gst_amount,
            'total_amount': total_amount,
            'current_date': date.today(),
            'work_order_master': quotations[0].quotation_master,
            'round_off':round_off,
            'bill_discount': bill_discount,
            # 'taxable_amount': taxable_amount  
        }

        # Render the template with data
        html_content = template.render(data)

        # Debug print: Check the HTML content generated
        print("Generated HTML content:", html_content)

        # Configuration for pdfkit
        # wkhtmltopdf_path = 'D:/sruthi/wkhtmltopdf/bin/wkhtmltopdf.exe'
        wkhtmltopdf_path = 'C:/wkhtmltox/wkhtmltopdf/bin/wkhtmltopdf.exe'
        if not os.path.isfile(wkhtmltopdf_path):
            raise FileNotFoundError(f'wkhtmltopdf executable not found at path: {wkhtmltopdf_path}')
        
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # PDF options
        options = {
            'footer-center': 'Page [page] of [topage]',
            'footer-font-size': '8',
            'margin-bottom': '20mm',
            'no-outline': None
        }
        
        try:
            # Convert HTML to PDF
            pdfkit.from_string(html_content, file_path, configuration=config, options=options)
        except Exception as e:
            raise RuntimeError(f'Error generating PDF: {e}')

        return open(file_path, "rb")

@router.get('/get_quotation_pdf')
def get_quotation_pdf(
    status: Optional[str]='ALL',
    work_order_master_id : Optional[int] = None,
    quotation_id : Optional[int] = None,
    from_date : Optional[date] = None,
    to_date : Optional[date] = None,
    db: Session = Depends(get_db)
):
    quotations = db_quotation.get_quotation_data(db, 'true' , work_order_master_id, quotation_id, status,from_date, to_date)
    if not quotations:
        raise HTTPException(status_code=404, detail="No quotations found")
    # print('Quotations ', quotations)
    file_path = os.path.join(UPLOAD_DIR_QUOTATION_DETAILS , "quotations.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    pdf_buffer = generate_quotation_pdf(quotations, file_path)
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=quotations.pdf"})


# @router.get('/get_quotation_pdf')
# def get_quotation_pdf(
#     status: Optional[str] = 'ALL',
#     work_order_master_id: Optional[int] = None,
#     quotation_id: Optional[int] = None,
#     from_date: Optional[date] = Query(date.today()),
#     to_date: Optional[date] = None,
#     db: Session = Depends(get_db)
# ):
#     # Fetch quotations from the database
#     quotations = db_quotation.get_quotation_data(db, status, work_order_master_id, quotation_id, from_date, to_date)

#     # Debugging print statement to check type of quotations
#     print('Type of quotations............:', type(quotations))
#     print('quotations.............:', quotations)

#     # Check if quotations were found
#     if not quotations or 'message' in quotations:
#         # If quotations are not found, raise a 404 error
#         raise HTTPException(status_code=404, detail=quotations.get('message', 'No quotations found'))

#     # Create the file path for the PDF
#     file_path = os.path.join(UPLOAD_DIR_QUOTATION_DETAILS, "quotations.pdf")
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#     # Generate PDF and return response
#     pdf_buffer = generate_quotation_pdf(quotations, file_path)
    
#     return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=quotations.pdf"})



#-------------------------------------------------------------------------------------------------------------
@router.post('/save_service_requirement_status')
def save_service_requirement_status(
    # work_order_details_id : int,
    request: List[ServiceRequirementSchema],
    db: Session =Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)
):
    """
     Save the service requirement status for a work order.

    Parameters:
    
    - request (ServiceRequirementSchema): The schema containing the service requirement details.
      - work_order_details_id (int): The ID of the work order details for which the service requirement status is being set.
      - "service_required" (str): Indicates whether the service is required. Possible values are "LATER", "YES", or "NO".
      - "service_required_date" (Optional[date]): If "service_required" is set to "LATER", this date field is required to specify when the service is needed.
    - db (Session): The database session to use for the operation. Automatically injected by FastAPI's dependency injection system.
    - token (str): The authentication token of the user making the request. Automatically injected by FastAPI's dependency injection system.

    Returns:
    - A JSON response indicating the result of the operation, typically the status or details of the saved service requirement.

    Raises:
    - HTTPException: If the authentication token is missing or invalid, a 401 Unauthorized error is raised.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")

    result = db_quotation.save_service_requirement_status( db,   request, user_id )
    return result


#--------------------------------------------------------------------------------------------
@router.get('/generate_profoma_invoice')
def generate_profoma_invoice(
    work_order_master_id : int,
    db : Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)):

            if not token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

            auth_info = authenticate_user(token)
            user_id = auth_info.get("user_id")
            financial_year_id   =  auth_info.get("financial_year_id") 
            customer_id         =  auth_info.get("mother_customer_id")             
            result   = db_quotation.generate_profoma_invoice_details(db,work_order_master_id,user_id,financial_year_id,customer_id)
            return result
#----------------------------------------------------------------------------------------


@router.get('/get_proforma_invoice_details')
def get_proforma_invoice_details(
     work_order_master_id : Optional[int] =None,
     proforma_invoice_master_id : Optional[int] =None,
     status: Union[str, int] = "ALL",
     include_details: Optional[bool] = Query(False),
     search_value: Union[str, int] = "ALL",
     from_date: Optional[date] = None,
     to_date: Optional[date] = None,
     token: str = Depends(oauth2.oauth2_scheme),
     db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

        # auth_info = authenticate_user(token)
        # user_id = auth_info.get("user_id")
            
    result = db_quotation.get_proforma_invoice_details(db,work_order_master_id,proforma_invoice_master_id,include_details,status,search_value,from_date,to_date)
    return result
#---------------------------------------------------------------------------------

@router.post('/save_proforma_invoice')
def save_proforma_invoice(
    work_order_master_id: int,
    request:AccProformaInvoiceShema,
    db:Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)):
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

        auth_info = authenticate_user(token)
        user_id = auth_info.get("user_id")
        result = db_quotation.save_profoma_invoice( db, work_order_master_id,request,user_id)
        return result


#---------------------------------------------------------------------------------------------


@router.get('/get_demand_notice')
def get_demand_notice(
     work_order_master_id : int,
     db: Session = Depends(get_db)
):
     
     result = db_quotation.get_demand_notice(work_order_master_id,db)
     return result

#----------------------------------------------------------------------------------------------------
@router.get('/consultation_invoice_generation')
def consultation_invoice_generation(
     work_order_master_id: int,
     appointment_master_id: int,
     db: Session = Depends(get_db),
     token: str = Depends(oauth2.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    auth_info = authenticate_user(token)
    user_id = auth_info.get("user_id")
    financial_year_id   =  auth_info.get("financial_year_id") 
    customer_id         =  auth_info.get("mother_customer_id") 
     
    result = db_quotation.consultation_invoice_generation(work_order_master_id,appointment_master_id,db,user_id,financial_year_id,customer_id)
    return result
#--------------------------------------------------------------------

@router.get('/get_invoice_details')
def get_invoice_details(
     work_order_master_id : int,
     invoice_master_id : int,
     db: Session = Depends(get_db)
):
     result = db_quotation.get_invoice_details(db,work_order_master_id,invoice_master_id)
     return result


#-----------------------------------------------------------------------------------------

# wkhtmltopdf_path = 'C:/wkhtmltox/wkhtmltopdf/bin/wkhtmltopdf.exe'

def generate_tax_invoice_pdf(invoice, file_path):

    # Load the template environment
    template_dir = os.path.dirname(TEMPLATE_TAX_INVOICE_DETAILS)
    template_name = os.path.basename(TEMPLATE_TAX_INVOICE_DETAILS)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)

    # Prepare data for the template
    if invoice:

        # Extract and format data from the quotations object
        details             = invoice[0].tax_invoice_details
        total = sum(item.total_amount for item in details)
        gst_amount              = sum(item.igst_amount for item in details)

        for item in details:
            item.service_charge = f"{(item.service_charge+ item.govt_agency_fee + item.stamp_fee + item.stamp_duty):.2f}"
            item.discount_amount = f"{item.discount_amount:.2f}" if item.discount_amount is not None else "0.00"
            item.igst_amount = f"{(item.igst_amount + item.cgst_amount + item.sgst_amount):.2f}" if item.igst_amount or item.cgst_amount or item.sgst_amount else "0.00"
            item.total_amount = f"{item.total_amount:.2f}"
            item.taxable_amount = f"{item.taxable_amount:.2f}"
       
        work_order_master   = invoice[0].tax_invoice_master 

        advance                 = f"{invoice[0].tax_invoice_master.advance_amount:.2f}"
        additional_fee_required = f"{invoice[0].tax_invoice_master.additional_fee_amount:.2f}"
        additional_discount     = f"{invoice[0].tax_invoice_master.additional_discount_amount:.2f}"
        total_amount            = f"{invoice[0].tax_invoice_master.net_amount:.2f}"
        round_off               = f"{invoice[0].tax_invoice_master.round_off_amount:.2f}"
        bill_discount           = f"{invoice[0].tax_invoice_master.bill_discount_amount:.2f}"
        grand_total             = f"{invoice[0].tax_invoice_master.grand_total_amount:.2f}"

        # Debug print: Check the content of details
        # print("Invoice Details  === :", invoice)
        # print("Work Order Master Details:", work_order_master)

        data = {
            'invoice': details,
            'total': total,
            'advance': advance,
            'additional_fee_required':additional_fee_required,
            'additional_discount': additional_discount,
            'gst_amount': gst_amount,
            'total_amount': total_amount,
            'current_date': date.today(),
            'work_order_master': work_order_master, 
            'round_off': round_off,
            'bill_discount': bill_discount,
            'grand_total': grand_total
        }

        # Render the template with data
        html_content = template.render(data)

        # Debug print: Check the HTML content generated
        # print("Generated HTML content:", html_content)

        # Configuration for pdfkit
        
        # wkhtmltopdf_path = 'D:/sruthi/wkhtmltopdf/bin/wkhtmltopdf.exe'
        wkhtmltopdf_path = 'C:/wkhtmltox/wkhtmltopdf/bin/wkhtmltopdf.exe'
        
        if not os.path.isfile(wkhtmltopdf_path):
            raise FileNotFoundError(f'wkhtmltopdf executable not found at path: {wkhtmltopdf_path}')
        
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # PDF options
        options = {
            'footer-center': 'Page [page] of [topage]',
            'footer-font-size': '8',
            'margin-bottom': '20mm',
            'no-outline': None
        }
        
        try:
            # Convert HTML to PDF
            pdfkit.from_string(html_content, file_path, configuration=config, options=options)
        except Exception as e:
            raise RuntimeError(f'Error generating PDF: {e}')

        return open(file_path, "rb")
    
@router.get('/get_tax_invoice_pdf')
def get_tax_invoice_pdf(
     work_order_master_id : int,
     tax_invoice_master_id : int,
     db: Session = Depends(get_db)
):
     invoice  = db_quotation.get_tax_invoice_details(db,work_order_master_id,tax_invoice_master_id)
     if not invoice:
                  raise HTTPException(status_code=404, detail="No invoice found")
     
     file_path = os.path.join(UPLOAD_DIR_INVOICE_DETAILS , f"tax_invoice{tax_invoice_master_id}.pdf")
     os.makedirs(os.path.dirname(file_path), exist_ok=True)

     pdf_buffer = generate_tax_invoice_pdf(invoice, file_path)
    
     return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=invoice.pdf"})

     
     
    #  return result






# def generate_proforma_invoice_pdf(invoice, file_path):

#     # Load the template environment
#     template_dir = os.path.dirname(TEMPLATE_PROFORMA_INVOICE_DETAILS)
#     template_name = os.path.basename(TEMPLATE_PROFORMA_INVOICE_DETAILS)
#     env = Environment(loader=FileSystemLoader(template_dir))
#     template = env.get_template(template_name)

#     # Prepare data for the template
#     if invoice:

#         # Extract and format data from the quotations object
#         details = invoice.proforma_invoice_details
#         work_order_master = invoice.work_order_master 
#         total = sum(item.total_amount for item in details)
#         advance = invoice.proforma_invoice_master.advance_amount
#         additional_discount = invoice.proforma_invoice_master.additional_discount_amount
#         gst_amount = sum(item.gst_amount for item in details)
#         total_amount = invoice.proforma_invoice_master.net_amount
#         round_off  = invoice.proforma_invoice_master.round_off_amount
#         bill_discount = invoice.proforma_invoice_master.bill_discount_amount
#         grand_total = invoice.proforma_invoice_master.grand_total_amount


#         # Debug print: Check the content of details
#         # print("Invoice Details  === :", invoice)
#         # print("Work Order Master Details:", work_order_master)

#         data = {
#             'invoice': details,
#             'total': total,
#             'advance': advance,
#             'additional_discount': additional_discount,
#             'gst_amount': gst_amount,
#             'total_amount': total_amount,
#             'current_date': date.today(),
#             'work_order_master': work_order_master, 
#             'round_off': round_off,
#             'bill_discount': bill_discount,
#             'grand_total': grand_total
#         }

#         # Render the template with data
#         html_content = template.render(data)

#         # Debug print: Check the HTML content generated
#         # print("Generated HTML content:", html_content)

#         # Configuration for pdfkit
        
#         wkhtmltopdf_path = 'C:/wkhtmltox/wkhtmltopdf/bin/wkhtmltopdf.exe'
#         if not os.path.isfile(wkhtmltopdf_path):
#             raise FileNotFoundError(f'wkhtmltopdf executable not found at path: {wkhtmltopdf_path}')
        
#         config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

#         # PDF options
#         options = {
#             'footer-center': 'Page [page] of [topage]',
#             'footer-font-size': '8',
#             'margin-bottom': '20mm',
#             'no-outline': None
#         }
        
#         try:
#             # Convert HTML to PDF
#             pdfkit.from_string(html_content, file_path, configuration=config, options=options)
#         except Exception as e:
#             raise RuntimeError(f'Error generating PDF: {e}')

#         return open(file_path, "rb")



def generate_proforma_invoice_pdf(invoice, file_path):

    # Load the template environment
    template_dir = os.path.dirname(TEMPLATE_PROFORMA_INVOICE_DETAILS)
    template_name = os.path.basename(TEMPLATE_PROFORMA_INVOICE_DETAILS)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)

    # Prepare data for the template
    if invoice:

        # Extract and format data from the quotations object
        details = invoice[0].proforma_invoice_details
        work_order_master = invoice[0].proforma_invoice_master 
        total = sum(item.total_amount for item in details)
        gst_amount = sum(item.igst_amount for item in details)

        for item in details:
            item.service_charge = f"{(item.service_charge+ item.govt_agency_fee + item.stamp_fee + item.stamp_duty):.2f}"
            item.discount_amount = f"{item.discount_amount:.2f}" if item.discount_amount is not None else "0.00"
            item.igst_amount = f"{(item.igst_amount + item.cgst_amount + item.sgst_amount):.2f}" if item.igst_amount or item.cgst_amount or item.sgst_amount else "0.00"
            item.total_amount = f"{item.total_amount:.2f}"
            item.taxable_amount = f"{item.taxable_amount:.2f}"
       
        advance = f"{invoice[0].proforma_invoice_master.advance_amount:.2f}"
        additional_discount = f"{invoice[0].proforma_invoice_master.additional_discount_amount:.2f}"
        total_amount = f"{invoice[0].proforma_invoice_master.net_amount:.2f}"
        round_off  = f"{invoice[0].proforma_invoice_master.round_off_amount:.2f}"
        bill_discount = f"{invoice[0].proforma_invoice_master.bill_discount_amount:.2f}"
        grand_total = f"{invoice[0].proforma_invoice_master.grand_total_amount:.2f}"


        # Debug print: Check the content of details
        # print("Invoice Details  === :", invoice)
        # print("Work Order Master Details:", work_order_master)

        data = {
            'invoice': details,
            'total': total,
            'advance': advance,
            'additional_discount': additional_discount,
            'gst_amount': gst_amount,
            'total_amount': total_amount,
            'current_date': date.today(),
            'work_order_master': work_order_master, 
            'round_off': round_off,
            'bill_discount': bill_discount,
            'grand_total': grand_total
        }

        # Render the template with data
        html_content = template.render(data)

        # Debug print: Check the HTML content generated
        # print("Generated HTML content:", html_content)

        # Configuration for pdfkit
        
        wkhtmltopdf_path = 'C:/wkhtmltox/wkhtmltopdf/bin/wkhtmltopdf.exe'
        if not os.path.isfile(wkhtmltopdf_path):
            raise FileNotFoundError(f'wkhtmltopdf executable not found at path: {wkhtmltopdf_path}')
        
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # PDF options
        options = {
            'footer-center': 'Page [page] of [topage]',
            'footer-font-size': '8',
            'margin-bottom': '20mm',
            'no-outline': None
        }
        
        try:
            # Convert HTML to PDF
            pdfkit.from_string(html_content, file_path, configuration=config, options=options)
        except Exception as e:
            raise RuntimeError(f'Error generating PDF: {e}')

        return open(file_path, "rb")




@router.get('/get_proforma_invoice_pdf')
def get_proforma_invoice_pdf(
     work_order_master_id : int,
     proforma_invoice_master_id : int,
     db: Session = Depends(get_db)
):
     invoice  = db_quotation.get_proforma_invoice_details(db,work_order_master_id,proforma_invoice_master_id)
     if not invoice:
                  raise HTTPException(status_code=404, detail="No invoice found")
     
     file_path = os.path.join(UPLOAD_DIR_INVOICE_DETAILS , f"proforma_invoice{proforma_invoice_master_id}.pdf")
     os.makedirs(os.path.dirname(file_path), exist_ok=True)

     pdf_buffer = generate_proforma_invoice_pdf(invoice, file_path)
    
     return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=invoice.pdf"})

     
     
    #  return result



#----------------------------------------------------------------------------------------------------



@router.get('/get_service_price_details_by_service_id')
def get_service_price_details_by_service_id(
     service_master_id :int,
     constitution_id: int,
     db: Session = Depends(get_db)
):
    """
    Retrieve service price details by `service_master_id` and `constitution_id`.

    This endpoint checks if a price has been set for a given service and constitution.
    If the price details are available, they are returned; otherwise, an appropriate
    message is returned, indicating that the service price is not set.

    **Parameters**:
    - `service_master_id` (int): The ID of the service.
    - `constitution_id` (int): The ID of the constitution to check the service price for.

    **Returns**:
    - If price details exist: Returns the service price details.
    - If no price details found: A message indicating that the service price is not set for the given service and constitution.

    **Response Example** (Failure):
    ```json
    {
      "success": false,
      "message": "Service price details not found. Please ensure that the service price is set for the given service and constitution.",
      "service_master_id": 1,
      "constitution_id": 2
    }
    ```
    """
    result = db_quotation.get_service_price_details_by_service_id(db,service_master_id,constitution_id)
    if result:
        return {
             'success': True,
             'result': result}
    else:
          return {
            'success': False,
            'message': 'Service price details not found. Please ensure that the service price is set for the given service and constitution.',
            'service_master_id': service_master_id,
            'constitution_id': constitution_id
        }
     

    #-----------------------------------------------------



@router.get('/get_tax_invoice_details')
def get_tax_invoice_details(
     work_order_master_id : Optional[int]= None,
     tax_invoice_master_id : Optional[int]= None,
     include_details: Optional[bool] = Query(False),
     status: Union[str, int] = "ALL",
     search_value: Union[str, int] = "ALL",
     from_date: Optional[date] = None,
     to_date: Optional[date] = None,
     token: str = Depends(oauth2.oauth2_scheme),
     db: Session = Depends(get_db)
):
     if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing") 
     
     result = db_quotation.get_tax_invoice_details(db,work_order_master_id,tax_invoice_master_id,include_details,status,search_value,from_date,to_date)
     return result




@router.post('/save_tax_invoice')
def save_tax_invoice(
    work_order_master_id: int,
    request:AccTaxInvoiceShema,
    db:Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_scheme)):
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

        auth_info = authenticate_user(token)
        user_id = auth_info.get("user_id")
        result = db_quotation.save_tax_invoice( db, work_order_master_id,request,user_id)
        return result

@router.post('/send_proforma_invoice')
def send_proforma_invoice(
    proforma_invoice_master_id :int,
    work_order_master_id : int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    result = db_quotation.send_proforma_invoice(proforma_invoice_master_id,work_order_master_id,db)
    return result



@router.post('/send_tax_invoice')
def send_tax_invoice(
    tax_invoice_master_id :int,
    work_order_master_id : int,
    token: str = Depends(oauth2.oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    result = db_quotation.send_tax_invoice(tax_invoice_master_id,work_order_master_id,db)
    return result
