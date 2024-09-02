import os
from fastapi import APIRouter, Depends,HTTPException,status,Query
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from caerp_db.database import get_db
from caerp_db.accounts import db_quotation
# from caerp_constants.caerp_constants import EntryPoint
from caerp_schema.accounts.quotation_schema import AccQuotationSchema
from typing import Optional
from datetime import date
from caerp_auth import oauth2
from caerp_auth.authentication import authenticate_user
from caerp_constants.caerp_constants import EntryPoint
import pdfkit


router  = APIRouter(
    tags=['Quotation']
)


@router.get('/generate_quotation_service_details')
def generate_quotation_service_details(
    work_order_master_id: int,
    entry_point : EntryPoint,
    # work_order_details_id: int,
    # service_goods_master_id : int,
    # constitution_id :int,
    db: Session = Depends(get_db)
):
    if entry_point == 'QUOTATION':
                result  = db_quotation.generate_profoma_invoice_details(db,work_order_master_id)
    elif entry_point == 'WORK_ORDER':
         
        result   = db_quotation.generate_quotation_service_details(db,work_order_master_id)
    else: 
         return {'message ':'Invalid Entry point' }
#   result  = db_quotation.generate_profoma_invoice_details(db,work_order_master_id)
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
    result = db_quotation.save_quotation_data(request,user_id,db,quotation_id)
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
    db: Session = Depends(get_db)
):
    result = db_quotation.send_proposal(quotation_id,work_order_master_id,db)
    return result

@router.get('/get_quotation_list')
def get_quotqtion_list(
    status: Optional[str]='ALL',
    work_order_master_id : Optional[int] = None,
    quotation_id : Optional[int] = None,
    from_date : Optional[date] = Query(date.today()),
    to_date : Optional[date] =None,
    db: Session = Depends(get_db)
): 
   result = db_quotation.get_quotation_data(db,status,work_order_master_id,quotation_id,from_date,to_date)
   return result

#--------------------------------------------------------------------------------------------------


TEMPLATE_QUOTATION_DETAILS  = "C:/BHARAT-TAXES-CA-ERP-API/templates/quotation_template.html"
UPLOAD_DIR_QUOTATION_DETAILS       = "uploads/quotation_details"





def generate_quotation_pdf(quotations, file_path):
    from jinja2 import Environment, FileSystemLoader
    import pdfkit
    import os
    from datetime import date

    # Load the template environment
    template_dir = os.path.dirname(TEMPLATE_QUOTATION_DETAILS)
    template_name = os.path.basename(TEMPLATE_QUOTATION_DETAILS)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)

    # Prepare data for the template
    if quotations:
        # Extract and format data from the quotations object
        details = quotations[0].quotation_details
        work_order_master = quotations[0].work_order_master 
        total = sum(item.total_amount for item in details)
        advance = quotations[0].quotation_master.net_amount
        additional_discount = quotations[0].quotation_master.additional_discount
        gst_amount = sum(item.gst_amount for item in details)
        total_amount = quotations[0].quotation_master.grand_total

        # Debug print: Check the content of details
        # print("Quotation Details:", details)
        # print("Work Order Master Details:", work_order_master)

        data = {
            'quotations': details,
            'total': total,
            'advance': advance,
            'additional_discount': additional_discount,
            'gst_amount': gst_amount,
            'total_amount': total_amount,
            'current_date': date.today(),
            'work_order_master': work_order_master 
        }

        # Render the template with data
        html_content = template.render(data)

        # Debug print: Check the HTML content generated
        print("Generated HTML content:", html_content)

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


@router.get('/get_quotation_pdf')
def get_quotation_pdf(
    status: Optional[str]='ALL',
    work_order_master_id : Optional[int] = None,
    quotation_id : Optional[int] = None,
    from_date : Optional[date] = Query(date.today()),
    to_date : Optional[date] = None,
    db: Session = Depends(get_db)
):
    quotations = db_quotation.get_quotation_data(db, status, work_order_master_id, quotation_id, from_date, to_date)
    print("Quotations fetched from database:", quotations)
    if not quotations:
        raise HTTPException(status_code=404, detail="No quotations found")

    file_path = os.path.join(UPLOAD_DIR_QUOTATION_DETAILS , "quotations.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    pdf_buffer = generate_quotation_pdf(quotations, file_path)
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=quotations.pdf"})