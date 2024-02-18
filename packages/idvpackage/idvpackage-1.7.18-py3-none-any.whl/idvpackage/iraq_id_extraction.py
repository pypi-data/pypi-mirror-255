import cv2
import numpy as np
from skimage.transform import radon
from google.cloud import vision_v1
from googletrans import Translator
import re
from idvpackage.common import *
import io
import os
from PIL import Image
from deep_translator import GoogleTranslator
from datetime import datetime

translator = Translator()

def rotate_image(img):
    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    if w > 640:
        gray = cv2.resize(gray, (640, int((h / w) * 640)))
    gray = gray - np.mean(gray)
    sinogram = radon(gray)
    r = np.array([np.sqrt(np.mean(np.abs(line) ** 2)) for line in sinogram.transpose()])
    rotation = np.argmax(r)
    angle = round(abs(90 - rotation) + 0.5)

    if abs(angle) > 5:
        rotated_img = img.rotate(angle, expand=True)
        return rotated_img

    return img


def crop_second_part(img):
    width, height = img.size
    half_width = width // 2
    second_part = img.crop((half_width, 0, width, height))
    return second_part


def crop_third_part(img):
    width, height = img.size
    part_height = height // 3
    third_part = img.crop((0, 2 * part_height, width, height))
    # third_part.save("/Users/fahadpatel/Pictures/thirdpart.jpg")
    return third_part


def extract_text_from_image_data(client, image):
    """Detects text in the file."""

    with io.BytesIO() as output:
        image.save(output, format="PNG")
        content = output.getvalue()

    image = vision_v1.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    return texts[0].description


def detect_id_card(client, image_data, id_text, part=None, country=None):
    
    if id_text:
        vertices = id_text[0].bounding_poly.vertices
        left = vertices[0].x
        top = vertices[0].y
        right = vertices[2].x
        bottom = vertices[2].y

        padding = 30
        left -= padding
        top -= padding
        right += padding
        bottom += padding

        # img = image_data
        img = Image.open(io.BytesIO(image_data))
        id_card = img.crop((max(0, left), max(0, top), right, bottom))
        # save_directory = "/Users/fahadpatel/Pictures/images"
        # id_card_path = os.path.join(save_directory, "cropped_img.jpg")
        # id_card.save(id_card_path)

        aligned_img = rotate_image(id_card)
        width, height = aligned_img.size
        if width < height:
            aligned_img = aligned_img.rotate(90, expand=True)
        
        tampered_result = calculate_error_difference(aligned_img, country)

        if part:
            if part=='second':
                part_img = crop_second_part(aligned_img)
                # part_img_path = os.path.join(save_directory, "second_part_img.jpg")
                # part_img.save(part_img_path)
            if part=='third':
                part_img = crop_third_part(aligned_img)
                # part_img_path = os.path.join(save_directory, "third_part_img.jpg")
                # part_img.save(part_img_path)
            
            # 2nd call to vision AI
            part_text = extract_text_from_image_data(client, part_img)

            return id_card, part_img, part_text, tampered_result
        else:
            return id_card, tampered_result
    else:
        print('No text found in the image.')


def extract_name_fields_from_raw(text):
    try:
        generic_field_match_pattern = r':\s*([^:\n]*)'
        
        generic_field_matches = re.findall(generic_field_match_pattern, text)
        generic_fields_result = []
        for item in generic_field_matches:
            no_digits = ''.join([char for char in item if not char.isdigit()])
            if no_digits.strip():
                generic_fields_result.append(no_digits)

        generic_fields_result = [word for word in generic_fields_result if len(word.split()) <= 3 and '/' not in word and '|' not in word]

        print(f"DATA LIST: {generic_fields_result}")

        if len(generic_fields_result[0].split()) <= 2 and len(generic_fields_result) <= 8:
            given_name = generic_fields_result[0]
        else:
            given_name = ''
        
        if len(generic_fields_result[1].split()) <= 2:
            fathers_name = generic_fields_result[1]
        else:
            fathers_name = ''
            
        if len(generic_fields_result[3].split()) <= 2:
            surname = generic_fields_result[3].replace("الأم", "").replace("دايك", "").replace("مديرية ال", "").replace("/", "").replace("البطاقة الو", "").replace("ذكر", "")
        else:
            surname = ''

        try: 
            gender = ''
            gender_ar = generic_fields_result[-2]
            gender = translator.translate(gender_ar, src='ar', dest='en').text
            if str(gender).lower() == 'feminine':
                gender = 'female'
            
            if gender.lower() != 'male' or gender.lower() != 'female':
                if 'ذكر' in generic_fields_result:
                    gender = 'male'
                elif 'انثى' in generic_fields_result:
                    gender = 'female'
                else:
                    gender = ''
        except:
            gender_ar, gender = '', None

        name = f"{given_name} {fathers_name} {surname}"
        if name:
            name_en = GoogleTranslator('ar', 'en').translate(name).upper()
            # name_en = translator.translate(name, src='ar', dest='en').text.upper()

        names_data  = {
            "gender": gender,
            "gender_ar": gender_ar,
            "name": name,
            "first_name": given_name,
            "fathers_name": fathers_name,
            "last_name": surname,
            "name_en": name_en,
        }

        return names_data
    
    except:
        return {}


def identify_front(text):
    front_id_keywords = ["The Republic of Iraq", "The Ministry of Interior", "National Card"]
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    try:
        if re.search(pattern, text, re.IGNORECASE):
            return True
        else:
            return False
    except:
        return 'error'

def extract_numeric_fields_from_raw(ar_front_data):
    front_data = translator.translate(ar_front_data, src='ar', dest='en').text 
    gender_pattern = r"Sex.*?:\s*(\w+)"
    id_number_pattern = r"\b\d{12}\b"
    rfid_number_pattern = r"\b[A-Za-z]{2}\d{7}\b|\b[A-Za-z]\d{8}\b"
        
    gender_match = re.search(gender_pattern, front_data, re.IGNORECASE)
    if gender_match:
        gender = gender_match.group(1)
    else:
         gender = ''
        
    id_number_match = re.search(id_number_pattern, front_data, re.IGNORECASE)
    if id_number_match:
        id_number = id_number_match.group(0)
    else:
        try:
            id_number_match = re.search(id_number_pattern, ar_front_data, re.IGNORECASE)
            id_number = id_number_match.group(0)
        except:
            id_number = ''
        
    rfid_number_match = re.search(rfid_number_pattern, front_data.replace(" ",""), re.IGNORECASE)
    if rfid_number_match:
        rfid_number = rfid_number_match.group(0).upper()
    else:
        rfid_number = ''
    
    front_data = {
        "gender": gender,
        "id_number_front": id_number,
        "card_number_front": rfid_number
    }
    
    return front_data


def iraq_front_id_extraction(client, image_data, front_id_text, front_id_text_description):
    cropped_id_card, second_part, second_part_text, tampered_result_front = detect_id_card(client, image_data, front_id_text, part='second')
    front_data = extract_name_fields_from_raw(second_part_text)
    numeric_fields = extract_numeric_fields_from_raw(front_id_text_description)
    if not front_data:
        front_data = extract_name_fields_from_raw(front_id_text_description)

    gender_front_data = front_data.get('gender', '')
    gender_numeric_fields = numeric_fields.get('gender', '')

    gender = ''
    if gender_front_data and (gender_front_data.lower()=='male' or gender_front_data.lower()=='female'):
        gender = gender_front_data
    elif gender_numeric_fields and (gender_numeric_fields.lower()=='male' or gender_numeric_fields.lower()=='female'):
        gender = gender_numeric_fields

    front_data.update(numeric_fields)
    front_data['gender'] = gender
    if gender:
        front_data['gender_ar'] = translator.translate(gender, src='en', dest='ar').text

    front_data['front_tampered_result'] = tampered_result_front

    return front_data


def find_mrz2_from_original(back_data):
    mrz2 = re.search(r'\b\d{6,}.*?<{2,}|\b\d{6,}.*?く{2,}', back_data, re.MULTILINE)
    return mrz2.group(0) if mrz2 else None


def handle_name_extraction(third_part_text):
    mrz_pattern = r'(IDIRQ[\S].*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*)'

    try:
        mrz = re.findall(mrz_pattern, third_part_text.replace(" ","").strip(), re.MULTILINE)
        mrz_str = mrz[0].replace(" ", "")
        mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
        mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None

        first_name, last_name = '', ''
        if mrz3:
            name_list = re.findall(r'\b[^<\s]+\b', mrz3)

            if name_list:
                if len(name_list)>1:
                    first_name = name_list[1].upper().replace("X", "")
                    last_name = name_list[0].upper().replace("X", "")
                else:
                    first_name = name_list[0].upper().replace("X", "")

                return {
                    "first_name_back": first_name,
                    "last_name_back": last_name,
                }
            else:
                return {}
        
    except:
       return {}
    

def handle_mrz_extraction(third_part_text, back_data, back_data_dict):
    mrz_pattern = r'(IDIRQ[\S].*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*)'
    mrz1_data_pattern = r'IDIRQ([\S]{2}\d{7}|[\S]\d{8}).*?(\d{13})'

    try:
        mrz = re.findall(mrz_pattern, third_part_text.replace(" ","").strip(), re.MULTILINE)
        mrz_str = mrz[0].replace(" ", "")
    except:
        mrz_str = ''

    mrz1 = re.search(r'(IDIRQ.*?<{2,})', mrz_str, re.DOTALL)
    mrz1 = mrz1.group(1) if mrz1 else None

    mrz2 = re.search(r'\b\d{6,}.*?<{2,}', mrz_str, re.MULTILINE)
    mrz2 = mrz2.group(0) if mrz2 else None

    mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
    mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None

    rfid_number = ''
    id_number = ''

    mrz1_data_match = re.search(mrz1_data_pattern, mrz_str)
    if mrz1_data_match:
        rfid_number = mrz1_data_match.group(1)
        id_number = mrz1_data_match.group(2)

    rfid_number = rfid_number.upper()
    id_number = id_number[1:14] 
    
    try:
        pattern = r'(?<=[\S]\d{7})[A-Z]{3}'

        national = re.search(pattern, mrz[0].replace(" ", ""))
        if national:
            nationality = national.group()
        else:
            national2 = re.search(pattern, mrz[0].replace(" ", "").replace("\n", ""))
            if national2:
                nationality = national2.group()
            else:
                nationality = ''
    except:
        nationality = ''

    try:
        dob_pattern = r'(\d+)[MF]'
        dob_match = re.search(dob_pattern, mrz2)
        dob_mrz = convert_dob(dob_match.group(1)) if dob_match else ''

        doe_pattern = r'[MF](\d+)'
        doe_match = re.search(doe_pattern, mrz2)
        expiry_date_mrz = convert_expiry_date(doe_match.group(1)) if doe_match else ''
    except:
        dob_mrz, expiry_date_mrz = '', ''

    if back_data_dict.get('id_number'):
        id_number = back_data_dict['id_number']
    
    if back_data_dict.get('card_number'):
        rfid_number = back_data_dict['card_number']

    if back_data_dict.get('mrz1'):
        mrz1 = back_data_dict['mrz1']

    back_data_new = {
        "id_number": id_number,
        "card_number": rfid_number,
        "nationality": nationality,
        "mrz": [mrz_str],
        "mrz1": mrz1,
        "mrz2": mrz2,
        "mrz3": mrz3,
        "dob_mrz": dob_mrz,
        "expiry_date_mrz": expiry_date_mrz
    }

    ## HANDLING EDGE CASES FOR ID NUMBER AND CARD NUMBER
    if not (back_data_new.get('id_number') or back_data_new.get('card_number')):
        print("getting id number")
        mrz_pattern = r'(IDI[\S]{2}.*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*)'
        mrz1_data_pattern = r'IDI[\S]{2}([\S]{2}\d{7}|[\S]\d{8}).*?(\d{13})'

        try:
            mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
            mrz_str = mrz[0].replace(" ", "")
            print(f"MRZ: {mrz_str}")
        except:
            mrz_str = ''

        back_data_new['mrz'] = [mrz_str]

        mrz1 = re.search(r'(IDI[\S]{2}.*?<{2,})', mrz_str, re.DOTALL)
        mrz1 = mrz1.group(1) if mrz1 else None
        back_data_new['mrz1'] = mrz1

        mrz2 = re.search(r'\b\d{7}.*?(?:<<\d|<<\n)', mrz_str)
        mrz2 = mrz2.group(0) if mrz2 else None
        back_data_new['mrz2'] = mrz2

        mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
        mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None
        back_data_new['mrz3'] = mrz3

        rfid_number = ''
        id_number = ''

        mrz1_data_match = re.search(mrz1_data_pattern, mrz_str)
        if mrz1_data_match:
            rfid_number = mrz1_data_match.group(1)
            id_number = mrz1_data_match.group(2)

        rfid_number = rfid_number.upper()
        id_number = id_number[1:14] 
        print(f"\n\nID: {id_number}, {rfid_number}\n\n")
        back_data_new['id_number'] = id_number
        back_data_new['card_number'] = rfid_number

    ## HANDLE DOB AND DOE FROM MRZ
    if not (back_data_new.get('dob_mrz') or back_data_new.get('expiry_date_mrz')):
        if not mrz2:
            mrz2 = re.search(r'\b\d{6,}.*?<{2,}|\b\d{6,}.*?く{2,}', mrz_str, re.MULTILINE)
            mrz2 = mrz2.group(0) if mrz2 else find_mrz2_from_original(back_data.replace(" ","").strip())

        if mrz2:
            dob_pattern = r"(\d{7})[MF]"
            dob_match = re.search(dob_pattern, mrz2)
            if dob_match:
                dob = dob_match.group(1)
                back_data_new['dob_mrz'] = convert_dob(dob)
            else:
                print("in")
                dob_pattern = r'(\d{12,})[\S]R[\S]\b'
                dob_match = re.search(dob_pattern, mrz2)

                if dob_match:
                    dob = dob_match.group(1)[:7]
                    back_data_new['dob_mrz'] = convert_dob(dob)
        
            doe_pattern = r"[MF](\d+)"
            doe_match = re.search(doe_pattern, mrz2)
            if doe_match:
                expiry = doe_match.group(1)
                back_data_new['expiry_date_mrz'] = convert_expiry_date(expiry)
            else:
                doe_pattern = r'(\d{12,})[\S]R[\S]\b'
                doe_match = re.search(doe_pattern, mrz2)
                
                if doe_match:
                    expiry = doe_match.group(1)[8:]
                    if len(expiry)<7:
                        expiry = doe_match.group(1)[7:]
                    back_data_new['expiry_date_mrz'] = convert_expiry_date(expiry)

    if not back_data_new.get('nationality'):
        mrz_pattern = r'(IDI[\S]{2}.*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*)'
        try:
            mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
        except:
            mrz = ''

        if mrz:
            national = re.search(pattern, mrz[0].replace(" ", "").replace("\n", ""))
            if national:
                nationality = national.group()
            else:
                nationality = ''
        
            back_data_new['nationality'] = nationality

    if not back_data_new.get('nationality'):
        nationality_pattern = r'\d{6,}([\S]{3})\b'
        nationality_match = re.search(nationality_pattern, mrz2)
        if nationality_match:
            nationality = nationality_match.group(1)
            back_data_new['nationality'] = nationality

    return back_data_new


def iraq_back_id_extraction(client, image_data, back_id_text, back_data):
    mrz_pattern = r'(IDIRQA.*\n*.*\n*.*\n*.*|IDIRQA.*\n*.*\n*.*\n*.*)'
    mrz1_data_pattern = r'IDIRQ([A-Za-z]{2}\d{7}|[A-Za-z]\d{8}).*?(\d{13})'
    nationality_pattern = r'([A-Z]+)<<'
    place_of_birth_pattern = r'(?:محل|الولادة)[^:]*:\s*(.*?)\n'
    issuing_authority_pattern_1 = r"مديرية الجنسية والمعلومات المدنية"
    issuing_authority_pattern_2 = r"دائرة احوال -.*?(?=\n|\r|$)"

    try:
        mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
        mrz_str = mrz[0].replace(" ", "")
    except:
        mrz_str = ''
    
    mrz1 = re.search(r'(IDIRQ.*?<<<)', mrz_str, re.DOTALL)
    mrz1 = mrz1.group(1) if mrz1 else None

    mrz2 = re.search(r'\b\d{6,}.*?<{2,}', mrz_str, re.MULTILINE)
    mrz2 = mrz2.group(0) if mrz2 else None

    mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
    mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None

    rfid_number = ''
    id_number = ''

    mrz1_data_match = re.search(mrz1_data_pattern, mrz_str)
    if mrz1_data_match:
        rfid_number = mrz1_data_match.group(1)
        id_number = mrz1_data_match.group(2)

    rfid_number = rfid_number.upper()
    id_number = id_number[1:14] 
    
    dob = func_dob(mrz_str)
    if not dob:
        matches = re.findall(r'\d{4}/\d{2}/\d{2}', back_data)
        sorted_dates = sorted(matches)
        dob = sorted_dates[0]
        
    expiry = func_expiry_date(mrz_str)
    if not expiry:
        matches = re.findall(r'\d{4}/\d{2}/\d{2}', back_data)
        sorted_dates = sorted(matches)
        expiry = sorted_dates[-1]
    
    # nationality_matches = re.search(nationality_pattern, mrz[0])
    # if nationality_matches:
    #     nationality = nationality_matches.group(1)
    # else:
    try:
        pattern = r'(?<=[A-Z]\d{7})[A-Z]{3}'
        national = re.search(pattern, back_data)
        if national:
            nationality = national.group()
        else:
            nationality = ''
    except:
        nationality = ''
    
    if len(nationality)>3:
        pattern = r'(?<=[A-Z]\d{7})[A-Z]{3}'
        national = re.search(pattern, back_data)
        if national:
            nationality = national.group()
    
    first_name, last_name = '', ''
    if mrz3:
        name_list = re.findall(r'\b[^<\s]+\b', mrz3)

        if len(name_list)>1:
            first_name = name_list[1].upper().replace("X", "")
            last_name = name_list[0].upper().replace("X", "")
        else:
            first_name = name_list[0].upper().replace("X", "")

#     issuing_authority_matches = re.findall(issuing_authority_pattern, back_data)
#     if issuing_authority_matches:
#         issuing_authority = issuing_authority_matches[-1][1]
#     else:
#         issuing_authority = ''

    issuing_authority = ''
    issuing_authority_match_1 = re.search(issuing_authority_pattern_1, back_data)
    issuing_authority_match_2 = re.search(issuing_authority_pattern_2, back_data)

    if issuing_authority_match_1:
        issuing_authority = issuing_authority_match_1.group(0)

    if issuing_authority_match_2:
        issuing_authority = issuing_authority_match_2.group(0)
        
    place_of_birth_match = re.search(place_of_birth_pattern, back_data)
    if place_of_birth_match:
        place_of_birth = place_of_birth_match.group(1).strip()
        place_of_birth_list = place_of_birth.split(":")
        if len(place_of_birth_list)>=2:
            place_of_birth = place_of_birth_list[1].strip()
        elif len(place_of_birth_list)==1:
            place_of_birth = place_of_birth_list[0]
        else:
            place_of_birth = ''
    else:
        place_of_birth = ''
    
    if issuing_authority:
        issuing_authority_en = translator.translate(issuing_authority, src='ar', dest='en').text.upper()

    if place_of_birth:
        place_of_birth_en = translator.translate(place_of_birth, src='ar', dest='en').text.upper()
    
    try:
        dob_pattern = r'(\d+)[MF]'
        dob_match = re.search(dob_pattern, mrz2)
        dob_mrz = convert_dob(dob_match.group(1)) if dob_match else ''

        doe_pattern = r'[MF](\d+)'
        doe_match = re.search(doe_pattern, mrz2)
        expiry_date_mrz = convert_expiry_date(doe_match.group(1)) if doe_match else ''
    except:
        dob_mrz, expiry_date_mrz = '', ''

    back_data_dict = {
        "mrz": [mrz_str],
        "mrz1": mrz1,
        "mrz2": mrz2,
        "mrz3": mrz3,
        "id_number": id_number,
        "card_number": rfid_number,
        "dob": dob,
        "first_name_back": first_name,
        "last_name_back": last_name,
        "expiry_date": expiry,
        "nationality": nationality,
        "issuing_authority": issuing_authority,
        "place_of_birth": place_of_birth,
        "issuing_authority_en": issuing_authority_en,
        "place_of_birth_en": place_of_birth_en,
        "issuing_country": "IRQ",
        "dob_mrz": dob_mrz,
        "expiry_date_mrz": expiry_date_mrz
    }

    ## HANDLE DOB DOE FROM MRZ
    if not (back_data_dict.get('dob_mrz') or back_data_dict.get('expiry_date_mrz')):
        mrz_pattern = r'(IDIRQ[\S].*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*)'
        try:
            mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
            mrz_str = mrz[0].replace(" ", "")
            
            mrz2 = re.search(r'\b\d{6,}.*?<{2,}', mrz_str, re.MULTILINE)
            mrz2 = mrz2.group(0) if mrz2 else None
        except:
            mrz_str = ''
        
        if mrz2:
            dob_pattern = r"(\d{7})[MF]"
            dob_match = re.search(dob_pattern, mrz2)
            if dob_match:
                dob = dob_match.group(1)
                back_data_dict['dob_mrz'] = convert_dob(dob)
            else:
                dob_pattern = r'(\d{12,})[\S]R[\S]\b'
                dob_match = re.search(dob_pattern, mrz2)
                if dob_match:
                    dob = dob_match.group(1)[:7]
                    back_data_dict['dob_mrz'] = convert_dob(dob)
        
            doe_pattern = r"[MF](\d+)"
            doe_match = re.search(doe_pattern, mrz2)
            if doe_match:
                expiry = doe_match.group(1)
                back_data_dict['expiry_date_mrz'] = convert_expiry_date(expiry)
            else:
                doe_pattern = r'(\d{12,})[\S]R[\S]\b'
                doe_match = re.search(doe_pattern, mrz2)
                if doe_match:
                    expiry = doe_match.group(1)[8:]
                    if len(expiry)<7:
                        expiry = doe_match.group(1)[7:]
                    back_data_dict['expiry_date_mrz'] = convert_expiry_date(expiry)

            if not back_data_dict.get('nationality'):
                nationality_pattern = r'\d{6,}([\S]{3})\b'
                nationality_match = re.search(nationality_pattern, mrz2)
                if nationality_match:
                    nationality = nationality_match.group(1)
                    back_data_dict['nationality'] = nationality

    non_optional_keys = ["id_number", "card_number", "nationality", "dob_mrz"]
    empty_string_keys = [key for key, value in back_data_dict.items() if key in non_optional_keys and value == '']

    cropped_id_card, third_part, third_part_text, tampered_result_back = detect_id_card(client, image_data, back_id_text, part='third')
   
    back_data_dict['back_tampered_result'] = tampered_result_back

    if empty_string_keys or len(back_data_dict['nationality'])>3 or len(back_data_dict['id_number'])<12 or not back_data_dict.get('mrz2') or not back_data_dict.get('first_name_back'):
        print("handling")
        back_res = handle_mrz_extraction(third_part_text, back_data, back_data_dict)
        back_data_dict.update(back_res)
        name_res = handle_name_extraction(third_part_text)
        if name_res:
            back_data_dict.update(name_res)
        else:
            name_res = handle_name_extraction(back_data)
            if name_res:
                back_data_dict.update(name_res)

    return back_data_dict
