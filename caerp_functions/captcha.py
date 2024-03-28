
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from caerp_auth import oauth2
from caerp_schema.common.common_schema import CAPTCHARequest
from jose import JWTError, jwt
from caerp_auth.oauth2 import SECRET_KEY, ALGORITHM
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


from settings import CAPTCHA_FONT_PATH,BASE_URL,CAPTCHA_MODIFIED_IMAGE_PATH,CAPTCHA_IMAGE_PATH
import random,os

# CAPTCHA_MODIFIED_IMAGE_PATH = "uploads/captcha_modified_images"
# CAPTCHA_IMAGE_PATH = "resources/captcha_image/10001.jpg"
# CAPTCHA_FONT_PATH = "resources/fonts"


router = APIRouter(
    prefix ='/captcha',
    tags=["CAPTCHA"]

)



@router.get('/generate_captcha')
def generate_captcha():
    # Generate two random numbers between 1 and 100
    num1 = random.randint(5, 30)
    num2 = random.randint(5, 30)
    # operation = random.choice(['+', '-'])    
    # Perform the operation
    # if operation == '+':
    result = num1 + num2
    text = f'{num1} + {num2} = ?'
    # else:
    #     result = num1 - num2
    #     text = f'{num1} - {num2} = ?'
   
    output_image_path = text_masked_image(text)

    access_token = oauth2.create_access_token(data={"result": result })
   

    return {
        'output_image_path': output_image_path,
        'token': access_token
    }




@router.post("/verify_captcha/")
async def verify_captcha(captcha_request: CAPTCHARequest,token: str = Depends(oauth2.oauth2_scheme)):
    # Validate user's input against expected result

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   
    expected_result = payload.get("result")
    
    user_answer = captcha_request.answer
    if user_answer == expected_result:
        return {"success": True, "message": "CAPTCHA is correct!"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect CAPTCHA answer!")


# @router.get("/text-to-image/")
def text_masked_image(text: str):
    # Define directories
    

    # Load the random image
    random_image = Image.open(CAPTCHA_IMAGE_PATH)

    # Choose random font
    random_font_path = choose_random_file(CAPTCHA_FONT_PATH, ['.ttf', '.otf'])
    if not random_font_path:
        return {"error": "No valid font files found."}

    # Define text properties
    font_size = 24
    text_color = (0, 0, 0)  # Black color
    position = (100, 40)

    # Load the random font
    font = ImageFont.truetype(random_font_path, font_size)

    # Create a drawing context
    draw = ImageDraw.Draw(random_image)

    # Draw the text on the image
    draw.text(position, text, fill=text_color, font=font)


    random_filename = f'{random.randint(10000, 99999)}.jpg'
    
    output_path = os.path.join(CAPTCHA_MODIFIED_IMAGE_PATH, random_filename)
    
    # upl;oads/nnn/100001.jpg
   


    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Save the modified image
    # output_image_path = choose_random_file(output_directory,['.png', '.jpg', '.jpeg'])
    random_image.save(output_path)

    # return output_path
    return {"photo_url": f"{BASE_URL}/common/captcha/generate_captcha/{random_filename}"}

    # return {"message": "Image with text has been created."}

       


def choose_random_file(directory, extensions):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return None

    # Get a list of all files in the directory
    files = os.listdir(directory)

    # Filter files by extension
    valid_files = [file for file in files if any(file.lower().endswith(ext.lower()) for ext in extensions)]

    # Check if there are any valid files
    if not valid_files:
        print(f"No valid files found in '{directory}'.")
        return None

    # Choose a random file
    random_file = random.choice(valid_files)
    return os.path.join(directory, random_file)

