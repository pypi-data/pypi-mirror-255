import re
from datetime import datetime
from itertools import permutations
import os
import tempfile
import cv2
import numpy as np
from PIL import Image
import io

# def func_gender( extract):
#     extract_no_space = extract.replace(' ','')
#     try:
#         pattern = r'\sM|F'
#         m = re.search(pattern, extract)
#         sex = m.group(0)[-1]
#     except:
#         pattern = r'\d{3}(?:M|F)\d'
#         m = re.findall(pattern, extract_no_space)
#         if len(m) != 0:
#             sex = m[0][3:4]
#         else:
#             sex = ''

#     return sex

def func_common_dates(  extract_no_space):
    dob = ''
    expiry_date = ''
    try:
        matches = re.findall(r'\d{2}/\d{2}/\d{4}', extract_no_space)
        y1 = matches[0][-4:]
        y2 = matches[1][-4:]
        if int(y1) < int(y2):
            dob = matches[0]
            expiry_date = matches[1]
        else:
            dob = matches[1]
            expiry_date = matches[0]
    except:
        dob = ''
        expiry_date = ''

    return dob, expiry_date

def convert_dob(input_date):
    day = input_date[4:6]
    month = input_date[2:4]
    year = input_date[0:2]

    current_year = datetime.now().year
    current_century = current_year // 100
    current_year_last_two_digits = current_year % 100

    century = current_century
    # If the given year is greater than the last two digits of the current year, assume last century
    if int(year) > current_year_last_two_digits:
        century = current_century - 1

    final_date = f"{day}/{month}/{century}{year}"

    return final_date

def func_dob(  extract):
    extract_no_space = extract.replace(' ','')
    dob, expiry_date = func_common_dates(extract_no_space)
    if dob == '':  
        match_dob = re.findall(r'\d{7}(?:M|F)\d', extract_no_space)
        for i in match_dob:
            print(i)
            raw_dob = i[0:6]
            print(raw_dob)
            year = str(datetime.today().year)[2:4]
            temp = '19'
            if int(raw_dob[0:2]) > int(year):
                temp = '19'
            else:
                temp = '20'      
            dob = raw_dob[4:6]+'/'+raw_dob[2:4]+'/'+temp+raw_dob[0:2]
            try:
                dt_obj = datetime.strptime(dob, '%d/%m/%Y')
                break
            except:
                print(f'invalid date {dob}')
                dob = ''
        else:
            pattern = r"\b(\d{14}).*?\b"

            new_dob_match = re.search(pattern, extract_no_space)

            if new_dob_match:
                new_dob = new_dob_match.group(1)
                new_dob = new_dob[:7]
                dob = convert_dob(new_dob)

    return dob

def func_expiry_date(  extract):
    extract_no_space = extract.replace(' ','')
    dob, expiry_date = func_common_dates(extract_no_space)
    if expiry_date == '':
        match_doe = re.findall(r'\d{7}[A-Z]{2,3}', extract_no_space) 
        for i in match_doe:
         
            raw_doe = i[0:6]
            print(raw_doe)
            expiry_date = raw_doe[4:6]+'/'+raw_doe[2:4]+'/20'+raw_doe[0:2]
            try:
                dt_obj = datetime.strptime(expiry_date, '%d/%m/%Y')
                break
            except:
   
                expiry_date = ''

    return expiry_date

def convert_expiry_date(input_date):
    day = input_date[4:6]
    month = input_date[2:4]
    year = input_date[0:2]

    current_year = datetime.now().year
    current_century = current_year // 100
    current_year_last_two_digits = current_year % 100
    century = current_century

    if int(year) <= current_year_last_two_digits:
        century = current_century
    else:
        century = current_century
    final_date = f"{day}/{month}/{century}{year}"

    return final_date

def extract_first_9_digits(string_input):
    match = re.search(r'\b\d{9}\b', string_input)
    if match:
        sequence = match.group(0)
        return sequence
    else:
        return ""

def func_card_number(  extract):
    extract_no_space = extract.replace(' ','')
    try:
        card_number = re.search(r'\d{9}', extract_no_space).group()
    except:
        card_number=  extract_first_9_digits(extract_no_space)

    return card_number


def count_digits_after_pattern(s):
    """
    Counts the number of digits that come after a specified pattern in a string.

    Parameters:
    s (str): The input string.
    pattern (str): The pattern to search for.

    Returns:
    int: The count of digits that come after the pattern.
    """
    # Construct the regex pattern to find the specified pattern followed by digits
    pattern = "<<<<"
    regex_pattern = re.compile(f"{re.escape(pattern)}(\d+)")
    
    # Search for the pattern in the string
    match = regex_pattern.search(s)
    
    # If a match is found, count the digits
    if match:
        digits_after_pattern = match.group(1)
        return len(digits_after_pattern)
    else:
        return 0  # Pattern not found

def remove_special_characters1(string):
    # This pattern matches any character that is not a letter, digit, or space
    #pattern = r'[^a-zA-Z0-9<\s]'
    pattern = r'[^a-zA-Z0-9<>]'
    return re.sub(pattern, '', string)

def remove_special_characters_mrz2(string):
    # This pattern matches any character that is not a letter, digit, or space
    pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(pattern, '', string)

def validate_string(s):
    """
    Validates if the string follows the specific structure.

    Structure: 7 digits, followed by 'M' or 'F', then 7 digits again,
    then 3 uppercase letters, and ending with 1 digit.

    Parameters:
    s (str): The string to be validated.

    Returns:
    bool: True if the string follows the structure, False otherwise.
    """
    pattern = r'^\d{7}[MF]\d{7}[A-Z]{3}\d$'
    return bool(re.match(pattern, s))


def remove_special_characters2(string):
    # This pattern matches any character that is not a letter, digit, or space
    pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(pattern, ' ', string)

def func_name(extract):
    bio_data = extract[-40:]
    breakup = bio_data.split('\n')
    if len(breakup) == 2:
        name_extract = breakup.pop(0)
    else:
        country_extract = breakup.pop(0).replace(" ","")
        name_extract = breakup.pop(0)

# Check the alphanumeric nature of name_extract
    if not name_extract.isupper():
        name_extract = breakup.pop(0)
    
    try:
        name = name_extract.replace("<", " ").replace(">", " ").replace(".", " ").replace(":", " ").replace('«','').strip()
        name = ' '.join(name.split())
        name = name.replace("0", "O") # special case fix
    except:
        name = ""

    return name

def func_nationality(  extract):
    extract_no_space = extract.replace(' ','')
    try:
        pattern = r'\d{5}[A-Z]{3}|\d{5}[A-Z]{2}'

        m = re.findall(pattern, extract_no_space)
        country = m[len(m)-1].replace("<", "")[5:]
    except:
        country = ""

    if country == '':
        try:
            pattern = r'\d{2}[a-z][A-Z]{2}'

            m = re.findall(pattern, extract_no_space)
            country = m[len(m)-1].replace("<", "")[2:].upper()
        except:
            country = ""

    return country

def clean_string(input_string):
        cleaned_string = re.sub(r'[^\w\s]', ' ', input_string)
        return cleaned_string.strip()

def find_and_slice_number(input_number, digits):
    # Generate all possible permutations of the digits
    perms = [''.join(p) for p in permutations(digits)]
    
    # Initialize variables to keep track of the found pattern and its index
    found_pattern = None
    found_index = -1

    # Search for any permutation of the digits in the input_number
    for perm in perms:
        found_index = input_number.find(perm)
        if found_index != -1:
            found_pattern = perm
            break

    # If a pattern is found, slice the number accordingly
    if found_pattern:
        if found_index > len(input_number) - found_index - len(found_pattern):
            # Slice to the left
            sliced_number = input_number[:found_index + len(found_pattern)]
        else:
            # Slice to the right
            sliced_number = input_number[found_index:]
        
        return sliced_number
    else:
        return ''
    
def func_id_number(extract,dob):
        
    try:
        p = "784" + "\d{12}"
        id_re = re.search(p, clean_string(extract).replace(' ',''))
        id_number = id_re.group()
    except:
        
        try:
            pattern = r'\d{15,}'
            digits = '784'
            matches = re.findall(pattern, clean_string(extract).replace(' ',''))
            input_number = matches[0]
            dob=dob[-4:]
            id_number='784'+dob+find_and_slice_number(input_number, digits)[:8]
            
        except:
            id_number = ''

    return id_number


# #year = dob[-4:]
# p = "784" + "\d{12}"
# id_re = re.search(p, clean_string(data).replace(' ',''))
# id_number = id_re.group()



def convert_to_date(date_str):
    year = '19' + date_str[:2] if int(date_str[:2]) >= 50 else '20' + date_str[:2]
    month = date_str[2:4]
    day = date_str[4:6]
    return f"{day}/{month}/{year}"

def check_valid_date(date_str, format="%d/%m/%Y"):
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False
    

def find_expiry_date(original_text,mrz2):
    
    dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', original_text)
    expiry_date = ''

    if len(dates) == 2:
        
        date1 = datetime.strptime(dates[0], '%d/%m/%Y')
        date2 = datetime.strptime(dates[1], '%d/%m/%Y')
        
        if date2 < date1:
            expiry_date = dates[0]
        elif date2 > date1:
            expiry_date = dates[1]
            
    elif mrz2:
        match_expiry_date = re.search(r'[A-Za-z](\d+)', mrz2)
        if match_expiry_date:
            expiry_date = match_expiry_date.group(1)[:6]
            expiry_date = convert_to_date(expiry_date)
    
            
    if not check_valid_date(expiry_date):
            expiry_date=''
    return expiry_date

def find_dob(original_text,mrz2):
    
     dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', original_text)
     dob = ''
  
     if len(dates) == 2:
            date1 = datetime.strptime(dates[0], '%d/%m/%Y')
            date2 = datetime.strptime(dates[1], '%d/%m/%Y')

            if date2 < date1:
                dob = dates[1]
            elif date2 > date1:
                dob = dates[0] 
                
     elif mrz2:
        match_dob = re.search(r'(\d+)[A-Za-z]', mrz2)
        if match_dob:
            dob = match_dob.group(1)[:6] 
            dob=convert_to_date(dob)
    
     if not check_valid_date(dob):
            dob=''
     return dob


def convert_date_format(date_str):
    # Parse the date from DD/MM/YYYY format
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    # Convert it to YYYY-MM-DD format
    formatted_date = date_obj.strftime('%Y-%m-%d')
    return formatted_date


def convert_gender(gender_char):
    if gender_char.lower() == 'm':
        return 'Male'
    elif gender_char.lower() == 'f': 
        return 'Female'
    else:  
        return ''


def compute_ela_cv(image, quality):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

    SCALE = 15

    try:
        image_np = np.array(image)

        cv2.imwrite(temp_file.name, image_np, [cv2.IMWRITE_JPEG_QUALITY, quality])

        # read compressed image
        compressed_img = cv2.imread(temp_file.name)

        # get absolute difference between img1 and img2 and multiply by scale
        diff = SCALE * cv2.absdiff(image_np, compressed_img)
        return diff
    finally:
        # Close and delete the temporary file
        temp_file.close()
        os.unlink(temp_file.name)


def calculate_error_difference(image, country=None):
    ela_val = compute_ela_cv(image, quality=94)
    diff_avg = ela_val.mean()

    print(f"DIFFERENCE: {diff_avg}")
    if country == 'UAE':
        if diff_avg <= 25:
            label = 'Genuine'
        else:
            label = 'Tampered'
    else:
        if diff_avg <= 10.5:
            label = 'Genuine'
        else:
            label = 'Tampered'
            
    return label


def eastern_arabic_to_english(eastern_numeral):
    try:
        arabic_to_english_map = {
            '٠': '0', '۰': '0',
            '١': '1', '۱': '1',
            '٢': '2', '۲': '2',
            '٣': '3', '۳': '3',
            '٤': '4', '۴': '4',
            '٥': '5', '۵': '5',
            '٦': '6', '۶': '6',
            '٧': '7', '۷': '7',
            '٨': '8', '۸': '8',
            '٩': '9', '۹': '9',
            '/': '/'
        }

        english_numeral = ''.join([arabic_to_english_map[char] if char in arabic_to_english_map else char for char in eastern_numeral])
        
        return english_numeral

    except:
        return eastern_numeral

def english_to_eastern_arabic(english_numeral):
    try:
        english_to_arabic_map = {
            '0': '٠', 
            '1': '١', 
            '2': '٢', 
            '3': '٣', 
            '4': '٤', 
            '5': '٥', 
            '6': '٦', 
            '7': '٧', 
            '8': '٨', 
            '9': '٩'
        }

        eastern_arabic_numeral = ''.join([english_to_arabic_map[char] if char in english_to_arabic_map else char for char in english_numeral])
        
        return eastern_arabic_numeral

    except Exception as e:
        return str(e)  


def detect_id_card_uae(image_data, id_text):
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
        save_directory = "/Users/fahadpatel/Pictures/images"
        id_card_path = os.path.join(save_directory, "cropped_img.jpg")
        id_card.save(id_card_path)

        aligned_img = id_card
        width, height = id_card.size
        if width < height:
            aligned_img = id_card.rotate(90, expand=True)
        
        tampered_result = calculate_error_difference(aligned_img, country = 'UAE')

        return tampered_result
