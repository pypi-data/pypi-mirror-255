from googletrans import Translator
import re
from datetime import datetime
import gender_guesser.detector as gender
import pycountry
from rapidfuzz import fuzz
from idvpackage.common import *

translator = Translator()


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


def get_dates_to_generic_format(date):
    formats = ["%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return None


def validate_date(date):
    try:
        date = datetime.strptime(date, "%d-%m-%Y")
        return date.strftime("%d-%m-%Y")
    except ValueError:
        try:
            date = datetime.strptime(date, "%d/%m/%Y")
            return date.strftime("%d/%m/%Y")
        except:
            return ''

def identify_gender(name):
    d = gender.Detector()
    gender_prediction = d.get_gender(name)
    return gender_prediction


def translated_gender_identifier(passport_text):
    translator = Translator()
    trans_res = translator.translate(passport_text, src='ar', dest='en').text 
    if re.search('male', trans_res, re.IGNORECASE):
        return 'M'
    if re.search('female', trans_res, re.IGNORECASE):
        return 'F'

    return ''


def extract_names(passport_text):
    try:
        pattern = r'Full Name\s+([A-Z\s-]+)\nSurname\s+([A-Z\s-]+)'
        matches = re.search(pattern, passport_text)
        if matches:
            name = matches.group(1).strip()
            last_name = matches.group(2).strip()
            return name, last_name
        else:
            pattern = r'Full Name\s+([A-Z][A-Za-z\s-]+)|Name\s+([A-Z][A-Za-z\s-]+)|Sumame\s+([A-Z]+)|Surname\s+([A-Z]+)'

            matches = re.findall(pattern, passport_text)
            clean_matches = [match[0].strip() if match[0] else match[1] for match in matches]
            
            if len(clean_matches) > 1:
                name, last_name = clean_matches[0], clean_matches[1]
            elif len(matches) == 1:
                name, last_name = clean_matches[0].split("Surname")
                if len(name.split(" ")) > 3:
                    name_list = name.split("\n")
                    name = name_list[1]
                if len(last_name)>1:
                    last_name.split("\n")[0]
            
            return name.replace("\n", ""), last_name.replace("\n", "")
    except:
        return '', ''


def extract_names_exception(passport_text):
    ## REMOVE REDUNDANT WORDS AFFECTING ALGO
    threshold = 50
    passport_lines = passport_text.split("\n")
    keyword = 'WHEN NEEDED'
    for text in passport_lines:
        similarity = fuzz.partial_ratio(text.lower(), keyword.lower())
        if similarity >= threshold:
            passport_text = passport_text.replace(text, "")

    ## Find 3 consecutive uppercase words as name and single uppercase word as last name
    name_pattern = r'([A-Z]{3,} [A-Z]{3,} [A-Z]{1,}|[A-Z]{3,} [A-Z]{3,} [A-Z]{1,} [A-Z]{1,})\s+([A-Z-]+)'
    match = re.search(name_pattern, passport_text)
    
    if match:
        name = match.group(1).strip()
        last_name = match.group(2).strip()
        return name, last_name
    else:
        return '', ''
    

def iraq_passport_extraction(passport_text):
    passport_details = {}

    patterns = {
        'passport_number': (r"([A-Da-d]\d{8}|[A-Da-d]\d{7})", lambda match: match.group(1) if match else ''),
        'passport_number_mrz': (r"([A-Za-z]\d{8}|[A-Za-z]\d{7})", lambda match: match.group(1) if match else ''),
        'passport_date_of_birth': (r'(\d+)[MF]', lambda match: convert_dob(match.group(1)) if match else ''),
        'passport_date_of_expiry': (r'[MF](\d+)', lambda match: convert_expiry_date(match.group(1)) if match else ''),
        'passport_gender': (r'(\d)([A-Za-z])(\d)', lambda match: match.group(2) if match else '')
    }
    
    passport_text_clean = passport_text.replace(" ", "")
    
    mrz1_pattern = r"P<{COUNTRY_CODE}[A-Z<]+<<[A-Z<]+<"
    
    iso_nationalities = [country.alpha_3 for country in pycountry.countries]
    
    name_dict = {}
    for country_code in iso_nationalities:
        current_pattern = mrz1_pattern.format(COUNTRY_CODE=country_code)

        mrz1_match = re.search(current_pattern, passport_text_clean)
        if mrz1_match:
            mrz1 = mrz1_match.group(0)
            
            extracted_text = mrz1.replace('P<','').replace(country_code,'').replace('<', ' ')
            # print(f"TEXT: {extracted_text}")
            name_list = extracted_text.strip().split()
            name = ' '.join(name_list[1:])
            passport_surname = name_list[0]

            if re.search(r'\bal\b', passport_surname.lower()):
                passport_surname = '-'.join(name_list[0:2])
                name = ' '.join(name_list[2:])

            name_dict = {
                'full_name': name,
                'surname': passport_surname
            }

            passport_details.update(name_dict)
        
            break
        else:
            mrz1 = None
    
    if not mrz1:
        pattern = r"P[<\w@<]+<<[\w<]+<"
        matches = re.findall(pattern, passport_text)

        if matches:
            processed_matches = matches[0][5:]
        
            extracted_text = processed_matches.replace('@', '').replace('<', ' ')
            name_list = extracted_text.strip().split()
            name = ' '.join(name_list[1:])
            passport_surname = name_list[0]
            if re.search(r'\bal\b', passport_surname.lower()) or re.search(r'\bl\b', passport_surname.lower()):
                passport_surname = '-'.join(name_list[0:2])
                name = ' '.join(name_list[2:])
                    
            name_dict = {
                    'full_name': name,
                    'surname': passport_surname
                }
            
            passport_details.update(name_dict)
    
    ## HANDLE NAME GENERIC FOR VALIDATION
    name_generic, passport_surname_generic = extract_names(passport_text)
    if len(name_generic.split(" "))<3:
        name_generic_temp, passport_surname_generic_temp = extract_names_exception(passport_text)
        if name_generic_temp:
            name_generic, passport_surname_generic = name_generic_temp, passport_surname_generic_temp

    name_generic, passport_surname_generic = ''.join(filter(lambda x: x.isupper() or x == '-' or x == ' ', name_generic)), ''.join(filter(lambda x: x.isupper() or x == '-' or x == ' ', passport_surname_generic))
    name_dict = {
            'full_name_generic': name_generic,
            'surname_generic': passport_surname_generic
        }
    passport_details.update(name_dict)

    mrz2_pattern = r"\n[A-Z]\d+.*?(?=[<]{2,})"
    mrz2_matches = re.findall(mrz2_pattern, passport_text_clean)
    
    if mrz2_matches:
        mrz2 = mrz2_matches[0][1:]
    else:
        mrz2 = ''

    ## EXTRACTING FIELDS FROM MRZ2
    mrz2_keys = ['passport_gender', 'passport_number_mrz', 'passport_date_of_birth', 'passport_date_of_expiry']

    for key, value in patterns.items():
        pattern = value[0]
        transform_func = value[1]

        text = passport_text
        if key in mrz2_keys:
            text = mrz2

        match = re.search(pattern, text)
        passport_details[key] = transform_func(match) if match else ''
    
    if passport_details['passport_number_mrz'] and (passport_details['passport_number_mrz']!=passport_details['passport_number']):
        passport_details['passport_number'] = passport_details['passport_number_mrz']

    ## HANDLE PASSPORT NO FROM MRZ
    if not passport_details.get('passport_number_mrz'):
        passport_number_pattern = r"([A-Za-z]\d{8,}[A-Za-z]{2,}.*?|[A-Za-z]*\d{8,}[A-Za-z]{2,}.*?)"
        passport_number_match = re.search(passport_number_pattern, passport_text_clean)
        if passport_number_match:
            passport_number = passport_number_match.group(1)
            passport_details['passport_number_mrz'] = passport_number[:9]
        
    ## HANDLE DOB DOE FROM MRZ
    if not (passport_details.get('passport_date_of_birth') or passport_details.get('passport_date_of_expiry')):
        dob_pattern = r"(\d{7})[MF]"
        dob_match = re.search(dob_pattern, passport_text_clean)
        if dob_match:
            dob = dob_match.group(1)
            passport_details['passport_date_of_birth'] = convert_dob(dob)
        else:
            dob_pattern = r'.*?[\S]R[\S](\d{9,})\b'
            dob_match = re.search(dob_pattern, passport_text_clean)
            if dob_match:
                dob = dob_match.group(1)[:7]
                passport_details['passport_date_of_birth'] = validate_date(convert_dob(dob))
    
        doe_pattern = r"[MF](\d+)"
        doe_match = re.search(doe_pattern, passport_text_clean)
        if doe_match:
            expiry = doe_match.group(1)
            passport_details['passport_date_of_expiry'] = validate_date(convert_expiry_date(expiry))
        else:
            doe_pattern = r'.*?[\S]R[\S](\d{9,})\b'
            doe_match = re.search(doe_pattern, passport_text_clean)
            if doe_match:
                expiry = doe_match.group(1)[8:]
                passport_details['passport_date_of_expiry'] = validate_date(convert_expiry_date(expiry))

    ## HANDLE DOB AND DOE CASES FROM GENERIC DATA FOR VALIDATION
    dob = ''
    expiry = ''
    
    try:
        matches = re.findall(r'\d{4}/\d{2}/\d{2}', passport_text)
        date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in matches]
        sorted_dates = sorted(date_objects)
        sorted_date_strings = [date.strftime('%d/%m/%Y') for date in sorted_dates]

        # print(f"DATES: {sorted_date_strings}")
        dob = sorted_date_strings[0]
        expiry = sorted_date_strings[-1]
    except:
        matches = re.findall(r'\b\d{2}[./]\d{2}[./]\d{4}\b', passport_text)
        date_objects = [datetime.strptime(date.replace('.', '/'), '%d/%m/%Y') for date in matches]
        sorted_dates = sorted(date_objects)
        sorted_date_strings = [date.strftime('%d/%m/%Y') for date in sorted_dates]

        # print(f"DATES 2: {sorted_date_strings}")
        if len(sorted_date_strings)>1:
            dob = sorted_date_strings[0]
            expiry = sorted_date_strings[-1]
        else:
            matches = re.findall(r'\d{4}-\d{2}-\d{2}', passport_text)
            date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in matches]
            sorted_dates = sorted(date_objects)
            sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

            # print(f"DATES 3: {sorted_date_strings}")
            if len(sorted_date_strings)>1:
                dob = sorted_date_strings[0].replace('-', '/')
                expiry = sorted_date_strings[-1].replace('-', '/')
            
            else:
                matches = re.findall(r'\d{2}-\d{2}-\d{4}', passport_text)
                date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in matches]
                sorted_dates = sorted(date_objects)
                sorted_date_strings = [date.strftime('%d-%m-%Y') for date in sorted_dates]

                # print(f"DATES 4: {sorted_date_strings}")
                if sorted_date_strings:
                    dob = sorted_date_strings[0].replace('-', '/')
                    expiry = sorted_date_strings[-1].replace('-', '/')

    passport_details['passport_date_of_birth_generic'] = get_dates_to_generic_format(dob)
    passport_details['passport_date_of_expiry_generic'] = get_dates_to_generic_format(expiry)
    
    ## HANDLE GENDER CASES EXCEPTIONS
    if not (passport_details['passport_gender']):
        gender_pattern = r'(\d)([MFmf])(\d)'
        gender_match = re.search(gender_pattern, passport_text_clean)
        if gender_match:
            passport_details['passport_gender'] = gender_match.group(2)
        else:
            if re.search(r'ذكر', passport_text) or re.search(r'ذکر', passport_text):
                passport_details['passport_gender'] = 'M'

            elif re.search(r'انثى', passport_text):
                passport_details['passport_gender'] = 'F'

            else:
                if passport_details.get('full_name'):
                    first_name = passport_details['full_name'].split()[0].capitalize()
                    predicted_gender = identify_gender(first_name)
                    passport_details['passport_gender'] = 'M' if predicted_gender.lower() == 'male' else 'F' if predicted_gender.lower() == 'female' and predicted_gender != 'unknown' else translated_gender_identifier(passport_text)

    return passport_details

