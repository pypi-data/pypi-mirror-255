from datetime import datetime
import re
import cv2
import numpy as np
from google.cloud import vision_v1
from idvpackage.constants import *
import pkg_resources
from PIL import Image
import base64
import io
from googletrans import Translator
from rapidfuzz import fuzz

translator = Translator()

def create_final_result(dictionary):
    result = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            sub_result = create_final_result(value)
            if sub_result == 'consider':
                return 'consider'
            elif sub_result == 'clear':
                result = 'clear'
        elif value in ['clear', 'consider', ""]:
            if value == 'consider':
                return 'consider'
            elif result != 'clear':
                result = value
    return result

def create_sub_result(document_report):
    sub_result = 'clear'

    digital_document = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("digital_document")
    corner_removed = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("corner_removed")
    watermarks_digital_text_overlay = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("watermarks_digital_text_overlay")
    obscured_security_features = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("obscured_security_features")
    screenshot = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("screenshot")
    document_on_printed_paper = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("document_on_printed_paper")
    photo_of_screen = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("photo_of_screen")
    scan = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("scan")

    consider_caution_count = sum(value == 'consider' for value in [digital_document, corner_removed, watermarks_digital_text_overlay, obscured_security_features, screenshot, document_on_printed_paper, photo_of_screen, scan])
    
    data_consistency = document_report["breakdown"]["data_consistency"]["result"]
    data_comparison = document_report["breakdown"]["data_comparison"]["result"]

    if data_consistency == 'consider' or data_comparison == 'consider':
        sub_result = 'caution'

    if consider_caution_count > 2:
        sub_result = 'suspected'

    return sub_result

def age_validation(dob, age_threshold=18):
    age_val = {
        "breakdown": {
            "minimum_accepted_age": {
            "properties": {},
            "result": ""
            }
        },
        "result": ""
        }
    
    dob = get_dates_to_generic_format(dob)
    try:
        dob_date = datetime.strptime(dob, "%d/%m/%Y")
    except:
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d")
        except:
            dob_date = ''

    if dob_date:
        current_date = datetime.now()

        age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))

        if age>=age_threshold:
            age_val["breakdown"]["minimum_accepted_age"]["result"] = "clear"
            age_val["result"] = "clear"
        else:
            age_val["breakdown"]["minimum_accepted_age"]["result"] = "consider"
            age_val["result"] = "consider"
    else:
        age_val["breakdown"]["minimum_accepted_age"]["result"] = "consider"
        age_val["result"] = "consider"

    return age_val
    
def created_at():
    current_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    return current_datetime

def is_valid_and_not_expired(expiry_date, country):
    if country == 'LBN':    
        return 'clear'
        
    try:
        parsed_date = datetime.strptime(expiry_date, "%d/%m/%Y")
        current_date = datetime.now()
        
        if parsed_date < current_date:
            return 'consider'
        return 'clear'
    
    except:
        try:
            parsed_date = datetime.strptime(expiry_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            if parsed_date < current_date:
                return 'consider'
            return 'clear'

        except:
            return 'consider'

def identify_document_type(text, country):
    text = text.upper()
    emirates_id_pattern = r'\b(ILARE\w*|IDARE\w*|RESIDENT IDENTITY)\b'
    iqama_id_pattern = r'KINGDOM OF SAUDI ARABIA|RESIDENT IDENTITY|MINISTRY OF INTERIOR'
    iraq_id_pattern = r'Register|Signature|Family Number|The Directorate of Nationality|IDIRQ|The Republic of Iraq|Ministry of|National Card'
    lbn_id_pattern = r'Marital status|Family status|Lebanon Republic|Republic of Lebanon'
    qtr_id_pattern = r'State of Qatar|Residency Permit|Director General of the General Department|Directorate of Passports|Passport number'
    passport_pattern = r'\b(PASSPORT|PPT)\b'
    driver_license_pattern = r'\b(DRIVER|LICENSE|DL)\b'
    
    if re.search(emirates_id_pattern, text, re.IGNORECASE):
        return "EID"

    if country == 'IRQ' and re.search(iraq_id_pattern, text, re.IGNORECASE):
        return "INC"
    
    if country == 'LBN' and re.search(lbn_id_pattern, text, re.IGNORECASE):
        return "LBN"
    
    if country == 'QTR' and re.search(qtr_id_pattern, text, re.IGNORECASE):
        return "QTR"
        
    if re.search(passport_pattern, text, re.IGNORECASE):
        return "PASSPORT"

    if re.search(driver_license_pattern, text, re.IGNORECASE):
        return "DL"

    return "Unknown"

def identify_front_id(text):
    front_id_keywords = ['Resident Identity', 'United arab emirates', 'federal authority for identity', 'ID Number', 'Kingdom of saudi arabia', 'ministry of']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id(text):
    back_id_keywords = ['ILARE', 'IDARE', 'Signature']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_front_id_iraq(text):
    front_id_keywords = ['The Republic of Iraq', 'Ministry of', 'National Card']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id_iraq(text):
    back_id_keywords = ['IDIRQ', 'Signature', 'Register', 'Family Number', 'The Directorate of Nationality']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_front_id_lebanon(text):
    front_id_keywords = ['Lebanon Republic', 'Ministry of', 'Republic of Lebanon']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id_lebanon(text):
    back_id_keywords = ['Marital status', 'Family status']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_front_id_qatar(text):
    front_id_keywords = ['State of Qatar', 'Residency Permit']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id_qatar(text):
    back_id_keywords = ['Director General of the General Department', 'Directorate of Passports', 'Passport number']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

# def document_on_printed_paper(image, edge_threshold=100, contour_area_threshold=5000, paper_texture_threshold=0.008):
#     image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     image_blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)
#     image_edges = cv2.Canny(image_blurred, edge_threshold, edge_threshold * 2)

#     image_contours, _ = cv2.findContours(image_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     image_paper_edges = [contour for contour in image_contours if cv2.contourArea(contour) > contour_area_threshold]

#     paper_edge_ratio = len(image_paper_edges) / max(len(image_contours), 1)
#     print(f"paper edge ratio: {paper_edge_ratio}")

#     # Determine if the image contains a printed paper texture
#     if paper_edge_ratio >= paper_texture_threshold:
#         return 'consider'
#     else:
#         return 'clear'
#     # print(front_paper_edges, back_paper_edges)
    
#     # if len(image_paper_edges) > 0:
#     #     return 'consider'
#     # else:
#     #     return 'clear'

def document_on_printed_paper(image, block_size=11, c_value=2, texture_threshold=0.1, contour_area_threshold=5000):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_thresh = cv2.adaptiveThreshold(image_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, c_value)
    image_contours, _ = cv2.findContours(image_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out small noise contours
    image_paper_edges = [contour for contour in image_contours if cv2.contourArea(contour) > contour_area_threshold]

    # Calculate the percentage of paper texture in the image
    texture_ratio = len(image_paper_edges) / max(len(image_contours), 1)

    # Determine if the image contains a printed paper texture
    if texture_ratio >= texture_threshold:
        return 'consider'
    else:
        return 'clear'


def check_logo_existence_iraq(logo_content, id_card_content, threshold=3, good_mathces_filter=0.6):
    nparr_logo = np.frombuffer(logo_content, np.uint8)
    logo = cv2.imdecode(nparr_logo, cv2.IMREAD_GRAYSCALE)

    nparr_id_card = np.frombuffer(id_card_content, np.uint8)
    id_card = cv2.imdecode(nparr_id_card, cv2.IMREAD_COLOR)
    id_card_gray = cv2.cvtColor(id_card, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(logo, None)
    kp2, des2 = sift.detectAndCompute(id_card_gray, None)

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1, des2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < good_mathces_filter * n.distance:
            good_matches.append(m)

    # 40
    min_good_matches = threshold
    # min_good_matches = 3

    if len(good_matches) >= min_good_matches:
        return True
    else:
        return False


def detect_logo(client, input_image_content, country, compare_type=None, side=None):
    if country == 'UAE':
        reference_logo_path = pkg_resources.resource_filename('idvpackage', 'template_images/emirates_id_logo.jpeg')

        with open(reference_logo_path, 'rb') as logo_file:
            reference_image_content = logo_file.read()

        reference_image = vision_v1.types.Image(content=reference_image_content)
        input_image = vision_v1.types.Image(content=input_image_content)

        reference_response = client.logo_detection(image=reference_image)
        input_response = client.logo_detection(image=input_image)

        reference_logos = reference_response.logo_annotations
        input_logos = input_response.logo_annotations

        for reference_logo in reference_logos:
            for input_logo in input_logos:
                if reference_logo.description.lower() == input_logo.description.lower():
                    return 'clear'

        return 'consider'

    if country in ['IRQ', 'LBN', 'QTR'] and compare_type != 'template':
        if country == 'IRQ':
            logo_path = 'template_images/iraq_id_logo.png'
            good_mathces_filter = 0.6
        elif country == 'QTR':
            logo_path = 'template_images/qatar_id_logo.jpeg'
            good_mathces_filter = 0.7

        reference_logo_path = pkg_resources.resource_filename('idvpackage', logo_path)
        with open(reference_logo_path, 'rb') as logo_file:
            reference_image_content = logo_file.read()
        result = check_logo_existence_iraq(reference_image_content, input_image_content, 3, good_mathces_filter)

        if result:
            return 'clear'
        else:
            return 'consider'
    
    if country in ['IRQ', 'LBN', 'QTR'] and compare_type == 'template':
        if side == 'front':
            if country == 'QTR':
                threshold = 300
                front_template_path = 'template_images/qatar_front_standard_template.jpeg'
            elif country == 'IRQ':
                threshold = 40
                front_template_path = 'template_images/iraq_standard_template.png'
            else:  # LBN
                threshold = 60
                front_template_path = 'template_images/lbn_front_standard_template.png'
            reference_logo_path = pkg_resources.resource_filename('idvpackage', front_template_path)
        if side == 'back':
            if country == 'QTR':
                threshold = 235
                back_template_path = 'template_images/qatar_back_standard_template.jpeg'
            elif country == 'IRQ':
                threshold = 140
                back_template_path = 'template_images/iraq_back_standard_template.jpg'
            else:  # LBN
                threshold = 120
                back_template_path = 'template_images/lbn_back_standard_template.png'
            reference_logo_path = pkg_resources.resource_filename('idvpackage', back_template_path)

        with open(reference_logo_path, 'rb') as logo_file:
            reference_image_content = logo_file.read()

        result = check_logo_existence_iraq(reference_image_content, input_image_content, threshold)

        if result:
            return 'clear'
        else:
            return 'consider'


# def detect_logo(client, input_image_content, country):
#     if country == 'UAE':
#         reference_logo_path = pkg_resources.resource_filename('idvpackage', 'emirates_id_logo.jpeg')
    
        
#         with open(reference_logo_path, 'rb') as logo_file:
#             reference_image_content = logo_file.read()

#         reference_image = vision_v1.types.Image(content=reference_image_content)
#         input_image = vision_v1.types.Image(content=input_image_content)

#         reference_response = client.logo_detection(image=reference_image)
#         input_response = client.logo_detection(image=input_image)

#         reference_logos = reference_response.logo_annotations
#         input_logos = input_response.logo_annotations

#         for reference_logo in reference_logos:
#             for input_logo in input_logos:
#                 if reference_logo.description.lower() == input_logo.description.lower():
#                     return 'clear'

#         return 'consider'

#     if country == 'IRQ':
#         reference_logo_path = pkg_resources.resource_filename('idvpackage', 'iraq_id_logo.png')
#         result = check_logo_existence_iraq(reference_logo_path, input_image_content)

#         if result:
#             return 'clear'
#         else:
#             return 'consider'


def detect_logo_saudi(client, input_image):
    reference_logo_path = pkg_resources.resource_filename('idvpackage', 'template_images/sau_id_logo.png')
    
    with open(reference_logo_path, 'rb') as logo_file:
        reference_image_content = logo_file.read()

    reference_image = vision_v1.types.Image(content=reference_image_content)
    input_image = vision_v1.types.Image(content=input_image)

    reference_response = client.logo_detection(image=reference_image)
    input_response = client.logo_detection(image=input_image)

    reference_logos = reference_response.logo_annotations
    input_logos = input_response.logo_annotations

    for reference_logo in reference_logos:
        for input_logo in input_logos:
            if reference_logo.description.lower() == input_logo.description.lower():
                return 'clear'

    return 'consider'


def perform_feature_matching(image, template_image_path):
    template_image = cv2.imread(template_image_path, cv2.IMREAD_COLOR)

    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(template_image, None)
    kp2, des2 = sift.detectAndCompute(image, None)

    if len(kp1) == 0 or len(kp2) == 0:
        return 0.0 
    
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    similarity_score = len(good_matches) / len(kp1)

    return similarity_score


# part of detecting screenshot - checks for time values seen on phone
def extract_time_values(text_annotations):
    time_values = []
    for annotation in text_annotations:
        text = annotation.description
        time_matches = re.findall(r'\d{1,2}:\d{2}', text)
        time_values.extend(time_matches)
    return time_values


def detect_screenshot(client, image):
    icons = 0
    battery_value_and_time = 0

    similarity_threshold = 0.45

    for filename in pkg_resources.resource_listdir('idvpackage', 'icons'):
        if filename.endswith('.png'):
            icon_path = pkg_resources.resource_filename('idvpackage', f'icons/{filename}')
            image_data = np.frombuffer(base64.b64decode(image), dtype=np.uint8)

            front_similarity_score = perform_feature_matching(image_data, icon_path)
            if front_similarity_score >= similarity_threshold:
                icons+=1

    image_data = vision_v1.Image(content=base64.b64decode(image))

    image_response = client.text_detection(image=image_data)

    image_text_annotations = image_response.text_annotations

    image_time_values = extract_time_values(image_text_annotations)

    if image_time_values:
        battery_value_and_time+=1

    if icons or battery_value_and_time:
        return 'consider'
    else:
        return 'clear'


def detect_photo_on_screen(client, image):
    flag = 'clear'

    image_data = vision_v1.Image(content=base64.b64decode(image))
    
    image_response = client.label_detection(image=image_data)
    image_labels = image_response.label_annotations

    confidence_threshold = 0.58  

    keywords = ['mobile phone', 'mobile device', 'portable communications device', 'display device', 'communication device', 'smartphone', 'cell phone', "hand", 'touchscreen', 'laptop', 'notebook', 'computer', 'screen', 'finger', 'thumb', 'gadget']

    for label in image_labels:
        description = label.description.lower()
        # print(description)
        confidence = label.score
        # print(f"Confidence: {confidence}")
        if confidence >= confidence_threshold:
            match = any(fuzz.ratio(description, keyword.lower()) >= 90 for keyword in keywords)
            if match:
                return 'consider'

    return flag

def fuzzy_match_fields(field1, field2, threshold=70):
    similarity = fuzz.partial_ratio(field1, field2)
    return similarity >= threshold

def standardize_date(input_date):
        input_formats = [
            "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y",
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y",
            "%Y%m%d", "%m%d%Y", "%d%m%Y",
            "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y",
            "%Y %m %d", "%d %m %Y", "%m %d %Y",
        ]

        for format in input_formats:
            try:
                parsed_date = datetime.strptime(input_date, format)
                standardized_date = parsed_date.strftime("%d/%m/%Y")
                return standardized_date
            except ValueError:
                pass

        return None

def compare_dates(date_str1, date_str2):
    date_format = "%d/%m/%Y"

    date1 = datetime.strptime(date_str1, date_format)
    date2 = datetime.strptime(date_str2, date_format)

    if date1 == date2:
        return True
    else:
        return False

def standardize_gender(gender):
    if gender == 'male' or gender == 'm':
        return 'Male'

    elif gender == 'female' or gender == 'f':
        return 'Female'

## for data comparison, accept data from dev and match with data extracted from id
def data_comparison_check(data, country):
    data_comparison = DATA_COMPARISON

    user_data = data.get('manual_input', '')
    if user_data:
        if compare_dates(standardize_date(data.get('dob', '')), standardize_date(user_data.get('dob', ''))):
            data_comparison['breakdown']['date_of_birth']['result'] = 'clear'
        else:
            data_comparison['breakdown']['date_of_birth']['result'] = 'consider'
        
        user_gender = standardize_gender(user_data.get('gender', '').lower())
        id_gender = standardize_gender(data.get('gender', '').lower())

        if user_gender == id_gender:
            data_comparison['breakdown']['gender']['result'] = 'clear'
        else:
            data_comparison['breakdown']['gender']['result'] = 'consider'

        # if not fuzzy_match_fields(data.get('gender', '').lower(),user_data.get('gender', '').lower()):
        #     data_comparison['breakdown']['gender']['result'] = 'consider'
    
        if country == 'IRQ' or country == 'QTR':
            name_parts = data.get('name_en', '').split()

            first_name = name_parts[0].lower()
            last_name = name_parts[-1].lower()
        
        elif country == 'LBN':
            first_name = data.get('first_name_en', '').lower()
            last_name = data.get('last_name_en', '').lower()

        else:
            first_name = data.get('first_name', '').lower()
            last_name = data.get('last_name', '').lower()

        if fuzzy_match_fields(first_name, user_data.get('first_name', '').lower()):
            data_comparison['breakdown']['first_name']['result'] = 'clear'
        else:
            data_comparison['breakdown']['first_name']['result'] = 'consider'

        if fuzzy_match_fields(last_name, user_data.get('last_name', '').lower()):
            data_comparison['breakdown']['last_name']['result'] = 'clear'
        else:
            data_comparison['breakdown']['last_name']['result'] = 'consider'
            
    result = create_final_result(data_comparison)    
    data_comparison['result'] = result

    return data_comparison

def data_consistency_check(data, front_id_text, back_id_text, country):
    data_consistency = DATA_CONSISTENCY

    passport_data = data.get('passport')
    if passport_data:
        if not data.get('dob') == passport_data.get('passport_date_of_birth'):
            data_consistency['breakdown']['date_of_birth']['result'] = 'consider'
        
        if not fuzzy_match_fields(data.get('first_name').lower(),passport_data.get('passport_given_name').lower()):
            data_consistency['breakdown']['first_name']['result'] = 'consider'
        
        if not fuzzy_match_fields(data.get('gender').lower(),passport_data.get('passport_gender').lower()):
            data_consistency['breakdown']['gender']['result'] = 'consider'

        if not fuzzy_match_fields(data.get('last_name').lower(),passport_data.get('passport_surname').lower()):
            data_consistency['breakdown']['last_name']['result'] = 'consider'

    #### For data consistency compare data from different sources, like id and passport. 
    #### so the dob from id should match with dob extracted from passport

    if country == 'UAE':
        doc_type1 = identify_document_type(front_id_text, country)
        doc_type2 = identify_document_type(back_id_text, country)
        if doc_type1 == 'EID' or doc_type2=='EID':
            data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            data_consistency['breakdown']['document_type']['result'] = 'consider'

    if country == 'SAU':
        doc_type1 = identify_front_id(front_id_text)
        if doc_type1:
            data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            data_consistency['breakdown']['document_type']['result'] = 'consider'
    
    if country == 'IRQ':
        translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        doc_type1 = identify_document_type(translated_front_id_text, country)
        doc_type2 = identify_document_type(translated_back_id_text, country)
        if doc_type1 == 'INC' or doc_type2=='INC':
            data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            data_consistency['breakdown']['document_type']['result'] = 'consider'
    
    if country == 'QTR':
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        doc_type1 = identify_document_type(front_id_text, country)
        doc_type2 = identify_document_type(translated_back_id_text, country)
        if doc_type1 == 'QTR' or doc_type2=='QTR':
            data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            data_consistency['breakdown']['document_type']['result'] = 'consider'

    if country == 'LBN':
        translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        doc_type1 = identify_document_type(translated_front_id_text, country)
        doc_type2 = identify_document_type(translated_back_id_text, country)
        print(f"doc_type1: {doc_type1}, doc_type2: {doc_type2}")
        if doc_type1 == 'LBN' or doc_type2=='LBN':
            data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            data_consistency['breakdown']['document_type']['result'] = 'consider'

    result = create_final_result(data_consistency)    
    data_consistency['result'] = result

    return data_consistency

def get_dates_to_generic_format(date):
    formats = ["%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return date

def data_validation_check(data, country):
    data_validation = DATA_VALIDATION

    try:
        dob = data.get('dob')
        # print(f"DOB: {dob}")
        dob = get_dates_to_generic_format(dob)
        parsed_date = datetime.strptime(dob, "%d/%m/%Y")
        data_validation["breakdown"]['date_of_birth']["result"] = 'clear'
    except:
        try:
            dob = data.get('dob')
            parsed_date = datetime.strptime(dob, "%Y-%m-%d")
            data_validation["breakdown"]['date_of_birth']["result"] = 'clear'
        except:
            data_validation["breakdown"]['date_of_birth']["result"] = 'consider'

    try:
        doe = data.get('expiry_date')
        doe = get_dates_to_generic_format(doe)
        parsed_date = datetime.strptime(doe, "%d/%m/%Y")
        data_validation["breakdown"]['expiry_date']["result"] = 'clear'
    except:
        try:
            doe = data.get('expiry_date')
            parsed_date = datetime.strptime(doe, "%Y-%m-%d")
            data_validation["breakdown"]['expiry_date']["result"] = 'clear'
        except:
            data_validation["breakdown"]['expiry_date']["result"] = 'consider'

    gender = data.get('gender', '')
    
    if gender.isalpha() and (gender.lower()=='male' or gender.lower()=='female' or gender.lower()=='m' or gender.lower()=='f'):
        data_validation["breakdown"]['gender']["result"] = 'clear'
    else:
        data_validation["breakdown"]['gender']["result"] = 'consider'
    
    if country == 'LBN':
        data_validation["breakdown"]['expiry_date']["result"] = 'clear'
        data_validation['breakdown']['valid_nationality']["result"] = 'clear'
        data_validation['breakdown']['document_expiration']["result"] = 'clear'
    else:
        data_validation['breakdown']['valid_nationality']["result"] = data.get('valid_nationality')

    if country == 'UAE' or country == 'IRQ':
        doc_no = data.get('card_number', '')
        if len(doc_no)==9:
            data_validation["breakdown"]['document_numbers']["result"] = 'clear'
        else:
            data_validation["breakdown"]['document_numbers']["result"] = 'consider'

    if country == 'LBN':
        doc_no = data.get('card_number', '')
        if len(doc_no)>=1 and len(doc_no)<5:
            data_validation["breakdown"]['document_numbers']["result"] = 'clear'
        else:
            data_validation["breakdown"]['document_numbers']["result"] = 'consider'
    
    if country == 'QTR':
        data_validation["breakdown"]['document_numbers']["result"] = 'clear'

    doe = data.get('expiry_date', '')
    expiry_result = is_valid_and_not_expired(get_dates_to_generic_format(doe), country)
    data_validation['breakdown']['document_expiration']["result"] = expiry_result

    mrz = data.get('mrz', '')
    mrz1 = data.get('mrz1', '')
    mrz2 = data.get('mrz2', '')
    mrz3 = data.get('mrz3', '')
    if len(mrz) == 1 and mrz1 and mrz2 and mrz3:
        data_validation["breakdown"]['mrz']["result"] = 'clear'
    else:
        data_validation["breakdown"]['mrz']["result"] = 'consider'

    if country == 'IRQ' and not data.get('card_number'):
        doc_no = data.get('card_number_front', '')
        if len(doc_no)==9:
            data_validation["breakdown"]['document_numbers']["result"] = 'clear'
        else:
            data_validation["breakdown"]['document_numbers']["result"] = 'consider'

    result = create_final_result(data_validation)
    data_validation['result'] = result

    # if data_validation["breakdown"]['date_of_birth']["result"]=='clear' and data_validation["breakdown"]['expiry_date']["result"]=='clear' and data_validation["breakdown"]['gender']["result"]=='clear' and data_validation["breakdown"]['mrz']["result"]=='clear':
    #     data_validation['result'] = 'clear'

    return data_validation

## pending
def image_integrity_check(data, front_id_text, back_id_text, coloured, blurred, glare, missing_fields, country):
    image_integrity = IMAGE_INTEGRITY

    image_integrity['breakdown']['colour_picture']['result'] = coloured
    image_integrity['breakdown']['conclusive_document_quality']['properties']['corner_removed'] = is_valid_and_not_expired(get_dates_to_generic_format(data.get('expiry_date', '')), country)
    image_integrity['breakdown']['conclusive_document_quality']['properties']['abnormal_document_features'] = blurred
    image_integrity['breakdown']['image_quality']['properties']['blurred_photo'] = blurred
    image_integrity['breakdown']['image_quality']['properties']['covered_photo'] = missing_fields
    image_integrity['breakdown']['image_quality']['properties']['cut_off_document'] = missing_fields
    image_integrity['breakdown']['image_quality']['properties']['glare_on_photo'] = glare
    image_integrity['breakdown']['image_quality']['properties']['other_photo_issue'] =  missing_fields
    
    image_quality_result = create_final_result(image_integrity['breakdown']['image_quality'])
    image_integrity['breakdown']['image_quality']['result'] = image_quality_result

    f_result = identify_front_id(front_id_text)
    front_doc_on_pp = data.get('front_doc_on_pp')

    if country == 'UAE':
        b_result = identify_back_id(back_id_text)

        if back_id_text and b_result:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        else:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'

        if f_result and b_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'
    
    if country == 'SAU':
        if f_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'
        
        image_integrity['breakdown']['conclusive_document_quality']['properties']['digital_document'] = front_doc_on_pp

    if country == 'IRQ':
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        b_result = identify_back_id_iraq(translated_back_id_text)

        if back_id_text and b_result:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        else:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'
        
        translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
        f_result = identify_front_id_iraq(translated_front_id_text)

        if f_result and b_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'

    if country == 'LBN':
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        b_result = identify_back_id_lebanon(translated_back_id_text)

        if back_id_text and b_result:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        else:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'
        
        translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
        f_result = identify_front_id_lebanon(translated_front_id_text)

        if f_result and b_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'
    
    if country == 'QTR':
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        b_result = identify_back_id_qatar(translated_back_id_text)

        if back_id_text and b_result:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        else:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'
        
        f_result = identify_front_id_qatar(front_id_text)

        if f_result and b_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'

    image_integrity['breakdown']['conclusive_document_quality']['properties']['watermarks_digital_text_overlay'] = data.get('front_logo_result')
    # image_integrity['breakdown']['image_quality']['properties']['blurred_photo'] = blurred
    # image_integrity['breakdown']['image_quality']['properties']['glare_on_photo'] = glare

    image_quality_result = create_final_result(image_integrity['breakdown']['image_quality'])
    conclusive_document_quality_result = create_final_result(image_integrity['breakdown']['conclusive_document_quality'])
    image_integrity['breakdown']['conclusive_document_quality']["result"] = conclusive_document_quality_result
    colour_picture_result = image_integrity['breakdown']['colour_picture']['result']
    supported_documents_result = image_integrity['breakdown']['supported_document']['result']

    back_doc_on_pp = data.get('doc_on_pp')
    if front_doc_on_pp == 'consider' or back_doc_on_pp == 'consider':
        image_integrity['breakdown']['conclusive_document_quality']['properties']['digital_document'] = 'consider'

    if image_quality_result == 'consider' or conclusive_document_quality_result == 'consider' or colour_picture_result == 'consider' or supported_documents_result == 'consider':
        image_integrity['result'] = 'consider'

    return image_integrity

def visual_authenticity_check(data, front_id_text, back_id_text, selfie, facial_similarity, face_match_threshold, country):
    print(f"\nSimilarity: {facial_similarity}\n")
    visual_authenticity = VISUAL_AUTHENTICITY

    if np.any(selfie):
        ## if facial similarity is matching the threshold or even if facial similarity comes above 40 then we say face was detected - approach can be changed
        if facial_similarity >= face_match_threshold or (facial_similarity >= 0.40 and facial_similarity < face_match_threshold):
            visual_authenticity['breakdown']['face_detection'] = 'clear'
            visual_authenticity['breakdown']['security_features'] = 'clear'
        else:
            visual_authenticity['breakdown']['face_detection'] = 'consider'
            visual_authenticity['breakdown']['security_features'] = 'consider'
    else:
        visual_authenticity['breakdown']['face_detection'] = ''
        visual_authenticity['breakdown']['security_features'] = ''
    
    doc_type1 = identify_document_type(front_id_text, country)
    front_doc_on_pp = data.get('front_doc_on_pp')
    front_screenshot = data.get('front_screenshot_result')
    front_photo_on_screen_result = data.get('front_photo_on_screen_result')

    if country != 'SAU':
        back_screenshot = data.get('screenshot_result')
        if front_screenshot == 'consider' or back_screenshot == 'consider':
            visual_authenticity['breakdown']['original_document_present']['properties']['screenshot'] = 'consider'

        back_photo_on_screen_result = data.get('photo_on_screen_result')
        if front_photo_on_screen_result == 'consider' or back_photo_on_screen_result == 'consider':
            visual_authenticity['breakdown']['original_document_present']['properties']['photo_of_screen'] = 'consider'

    if country == 'UAE':
        doc_type2 = identify_document_type(back_id_text, country)
        if doc_type1 == 'EID' and doc_type2 == 'EID':
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

    if country == 'SAU':
        if identify_front_id(front_id_text):
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'
    
        visual_authenticity['breakdown']['original_document_present']['properties']['document_on_printed_paper'] = front_doc_on_pp
        visual_authenticity['breakdown']['original_document_present']['properties']['screenshot'] = front_screenshot
        visual_authenticity['breakdown']['original_document_present']['properties']['photo_of_screen'] = front_photo_on_screen_result

    if country == 'IRQ':
        translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        
        doc_type1 = identify_document_type(translated_front_id_text, country)
        doc_type2 = identify_document_type(translated_back_id_text, country)
        if doc_type1 == 'INC' and doc_type2 == 'INC':
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

        visual_authenticity['breakdown']['template']['result'] = data.get('front_template_result')
        print(f"tampering: {data.get('tampering_result')}")
        visual_authenticity['breakdown']['digital_tampering']['result'] = data.get('tampering_result')

    if country == 'LBN':
        translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        
        doc_type1 = identify_document_type(translated_front_id_text, country)
        doc_type2 = identify_document_type(translated_back_id_text, country)
        if doc_type1 == 'LBN' and doc_type2 == 'LBN':
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

    if country == 'QTR':
        translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        
        doc_type1 = identify_document_type(front_id_text, country)
        doc_type2 = identify_document_type(translated_back_id_text, country)
        if doc_type1 == 'QTR' and doc_type2 == 'QTR':
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

    original_document_present_result  = create_final_result(visual_authenticity['breakdown']['original_document_present'])
    visual_authenticity['breakdown']['original_document_present']['result'] = original_document_present_result
    final_result = create_final_result(visual_authenticity)
    visual_authenticity['result'] = final_result

    back_doc_on_pp = data.get('doc_on_pp')
    if front_doc_on_pp == 'consider' or back_doc_on_pp == 'consider':
        visual_authenticity['breakdown']['original_document_present']['properties']['document_on_printed_paper'] = 'consider'

    return visual_authenticity

def main_details(data, country):
    main_properties = MAIN_DATA

    try:
        dob = get_dates_to_generic_format(data.get('dob'))
        doe = get_dates_to_generic_format(data.get('expiry_date', ''))
        main_properties['date_of_birth'] = dob
        main_properties['date_of_expiry'] = doe
        
        if data.get('card_number'):
            card_data_t = {
            "type": "type",
            "value": "document_number"
            }

            card_data_v = {
                "type": "value",
                "value": data['card_number']
            }

            main_properties['document_numbers'].append(card_data_t)
            main_properties['document_numbers'].append(card_data_v)

        if data.get('id_number'):
            id_data_t = {
                        "type": "type",
                        "value": "personal_number"
                    }
            id_data_v = {
                        "type": "value",
                        "value": data['id_number']
                    }
                
            main_properties['document_numbers'].append(id_data_t) 
            main_properties['document_numbers'].append(id_data_v) 
        
        # main_properties['document_type'] = 'national_identity_card'
        # main_properties['name'] = data.get('name')
        # main_properties['first_name'] = data.get('first_name', '')
        # main_properties['gender'] = data.get('gender', '')
        # main_properties['issuing_country'] = data.get('issuing_place', '')
        # main_properties['last_name'] = data.get('last_name', '')
        # main_properties['mrz_line1'] = data.get('mrz1', '')
        # main_properties['mrz_line2'] = data.get('mrz2', '')
        # main_properties['mrz_line3'] = data.get('mrz3', '')
        # main_properties['nationality'] = data.get('nationality')

        keys = ['name', 'first_name', 'gender', 'issuing_place', 'last_name', 'nationality', 'issuing_country', 'occupation', 'employer']

        main_properties['document_type'] = 'national_identity_card'
        main_properties['mrz_line1'] = data.get('mrz1', '')
        main_properties['mrz_line2'] = data.get('mrz2', '')
        main_properties['mrz_line3'] = data.get('mrz3', '')

        for key in keys:
            main_properties[key] = data.get(key, '')

        if country == 'IRQ' or country == 'LBN' or country == 'QTR':
            if country == 'IRQ':
                main_prop_data = {}
                keys = ['name_en', 'issuing_authority', 'gender_ar', 'place_of_birth', 'issuing_authority_en', 'place_of_birth_en']

            if country == 'LBN':
                main_prop_data = {}
                keys = ['fathers_name', 'last_name', 'name_en', 'first_name_en', 'fathers_name_en', 'last_name_en', 'gender_ar', 'place_of_birth', 'issue_date', 'issue_date_en', 'card_number_ar', 'id_number_ar']

            if country == 'QTR':
                main_prop_data = {}
                keys = ['passport_number', 'name_ar', 'name_en', 'passport_expiry', 'occupation', 'employer', 'employer_en', 'occupation_en']

            for key in keys:
                main_prop_data[key] =  data.get(key, '')

            main_properties.update(main_prop_data)

            if not data.get('card_number') and data.get('card_number_front'):
                card_data_t = {
                "type": "type",
                "value": "document_number"
                }

                card_data_v = {
                    "type": "value",
                    "value": data['card_number_front']
                }

                main_properties['document_numbers'].append(card_data_t)
                main_properties['document_numbers'].append(card_data_v)

            if not data.get('id_number') and data.get('id_number_front'):
                id_data_t = {
                            "type": "type",
                            "value": "personal_number"
                        }
                id_data_v = {
                            "type": "value",
                            "value": data['id_number_front']
                        }
                    
                main_properties['document_numbers'].append(id_data_t) 
                main_properties['document_numbers'].append(id_data_v) 

    except:
        main_properties

    return main_properties    

def form_final_data_document_report(data, front_id_text, back_id_text, country, coloured, selfie, facial_similarity, blurred, glare, missing_fields, face_match_threshold):
    try:
        document_report = {
            ## pending - to be filled by dev
            "_id": "",
            "breakdown": {
                "age_validation": age_validation(data.get('dob')),
                "compromised_document": {
                    "result": "clear"
                    },
                "data_comparison": data_comparison_check(data, country),
                "data_consistency": data_consistency_check(data, front_id_text, back_id_text, country),
                "data_validation": data_validation_check(data, country),
                "image_integrity": image_integrity_check(data, front_id_text, back_id_text, coloured, blurred, glare, missing_fields, country),
                "issuing_authority": {
                "breakdown": {
                    "nfc_active_authentication": {
                    "properties": {}
                    },
                    "nfc_passive_authentication": {
                    "properties": {}
                    }
                }
                },
                "police_record": {},
                "visual_authenticity": visual_authenticity_check(data, front_id_text, back_id_text, selfie, facial_similarity, face_match_threshold, country)
            },
            ## pending - to be filled by dev
            "check_id": "", 
            "created_at": created_at(),
            "documents": [
                {
                ## pending - id value in table stored in db for front id - to be filled by dev
                "id": ""
                },
                {
                ## pending - id value in table stored in db for front id - to be filled by dev
                "id": ""
                }
            ],
            # to be filled by dev
            "href": "",
            "name": "document",
            "properties": main_details(data, country),
            "result": "",
            "status": "complete",
            "sub_result": ""
        }
        
        final_result = create_final_result(document_report)
        document_report['result'] = final_result
        
        sub_result = create_sub_result(document_report)
        document_report['sub_result'] = sub_result

        return document_report
    
    except Exception as e:
        print(e)
        return {}

def form_final_facial_similarity_report(data, selfie, facial_similarity, liveness_result, face_match_threshold, country):
    facial_report = FACIAL_REPORT
    
    facial_report['created_at'] = created_at()
    
    facial_report['breakdown']['face_comparison']['breakdown']['face_match']['properties']['score'] = facial_similarity

    if not np.any(selfie):
        facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result'] = ''
        facial_report['breakdown']['face_comparison']['result'] = ''
        facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = ''
        facial_report['breakdown']['image_integrity']['breakdown']['source_integrity']['result'] = ''

    if np.any(selfie) and facial_similarity >= face_match_threshold:
        facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result'] = 'clear'
        facial_report['breakdown']['face_comparison']['result'] = 'clear'
        facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'clear'
    elif facial_similarity != 0 and facial_similarity < face_match_threshold:
        facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result']  = 'consider'
        facial_report['breakdown']['face_comparison']['result'] = 'consider'
        facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'clear'
    else:
        facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result']  = 'consider'
        facial_report['breakdown']['face_comparison']['result'] = 'consider'
        facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'consider'

    front_photo_on_screen_result = data.get('front_photo_on_screen_result')

    if country == 'UAE':
        photo_on_screen_result = data.get('photo_on_screen_result')
        if front_photo_on_screen_result == 'consider' or photo_on_screen_result == 'consider':
            facial_report['breakdown']['image_integrity']['breakdown']['source_integrity']['result'] = 'consider'

    if country == 'SAU':
        facial_report['breakdown']['image_integrity']['breakdown']['source_integrity']['result'] = front_photo_on_screen_result

    facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['properties']['score'] = round(1-facial_similarity,2)

    if liveness_result == 'consider':
        facial_report['breakdown']['visual_authenticity']['breakdown']['liveness_detected']['result'] = 'consider'
        facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = 'consider'
        facial_report['breakdown']['visual_authenticity']['result'] = 'consider'
    elif liveness_result == 'clear' and facial_similarity < face_match_threshold:
        facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = 'consider'
        facial_report['breakdown']['visual_authenticity']['result'] = 'consider'
    elif liveness_result == None:
        facial_report['breakdown']['visual_authenticity']['breakdown']['liveness_detected']['result'] = ''
        facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['properties']['score'] = ''
        facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = ''

    # if np.any(selfie) and liveness_result:
    visual_authenticity_final_result = create_final_result(facial_report['breakdown']['visual_authenticity'])
    facial_report['breakdown']['visual_authenticity']['result'] = visual_authenticity_final_result

    image_integrity_final_result = create_final_result(facial_report['breakdown']['image_integrity'])
    facial_report['breakdown']['image_integrity']['result'] = image_integrity_final_result

    complete_final_result = create_final_result(facial_report['breakdown'])
    facial_report['result'] = complete_final_result
    facial_report['sub_result'] = complete_final_result

    return facial_report
