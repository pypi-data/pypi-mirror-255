import cv2
import numpy as np
from PIL import Image, ImageOps
from skimage.transform import radon
from google.cloud import vision_v1
import re
from datetime import datetime
import io
from deep_translator import GoogleTranslator
import pycountry
from rapidfuzz import process, fuzz
import pycountry

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
    part_height = height // 6
    third_part = img.crop((0, 4.5 * part_height, width, height))
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


def detect_id_card(client, image_data, id_text, part=None):
    
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

        aligned_img = rotate_image(id_card)

        width, height = aligned_img.size
        if width < height:
            aligned_img = aligned_img.rotate(90, expand=True)
            
        if part=='second':
            part_img = crop_second_part(aligned_img)
        if part=='third':
            part_img = crop_third_part(aligned_img)
        
        # 2nd call to vision AI
        part_text = extract_text_from_image_data(client, part_img)
        # print(f"PART TEXT: {part_text}")

        return id_card, part_img, part_text
    else:
        print('No text found in the image.')

def is_arabic(word):
    return re.search(r'[\u0600-\u06FF]', word) is not None

def extract_name_fields_from_cropped_part(text):
    pattern = r"Name:\s*([A-Z\s]+)"
    name_dict = {}
    match = re.search(pattern, text)

    if match:
        extracted_name = match.group(1).strip()
        name_dict["name"] = extracted_name
        name_parts = extracted_name.split()

        first_name = name_parts[0].upper()
        last_name = name_parts[-1].upper()

        name_dict["first_name"] = first_name
        name_dict["last_name"] = last_name

    words_in_text = text.split()
    arabic_words_in_text = [word for word in words_in_text if is_arabic(word)]
    # print(arabic_words_in_text)

    for word in arabic_words_in_text:
        similarity = fuzz.partial_ratio(word, 'الاسم')
        if similarity >= 80:
            arabic_words_in_text.remove(word)

    name_ar = ' '.join(arabic_words_in_text)
    # print(f"name ar: {name_ar}")
    if name_ar:
        name_ar = name_ar.lower().replace("name", "").replace(":", "")
        name_dict["name_ar"] = name_ar
        name_en = GoogleTranslator(dest = 'en').translate(name_ar)
        name_dict["name_en"] = name_en

    return name_dict

def identify_front(text):
    front_id_keywords = ["State of Qatar"]
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    try:
        if re.search(pattern, text, re.IGNORECASE):
            return True
        else:
            return False
    except:
        return 'error'

def sort_dates_by_datetime(dates):
    return sorted(dates, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))

def extract_and_check_country(words):
    for word in words:
        try:
            country = pycountry.countries.lookup(word)
            if country:
                return country.name.upper()
        except LookupError:
            pass

    return None

def extract_name_after_nationality(word_list, nationality):
    nationality_index = word_list.index(nationality) if nationality in word_list else -1

    if nationality_index != -1 and nationality_index < len(word_list) - 1:
        words_after_nationality = word_list[nationality_index + 1:]
        return words_after_nationality
    else:
        return []

def get_fuzzy_match_score(line, patterns, threshold=70):
    result = process.extractOne(line, patterns, scorer=fuzz.WRatio)
    if result and result[1] > threshold:
        return result[1]
    return None

def extract_numeric_fields_from_raw(ar_front_data):
    front_data = GoogleTranslator(dest = 'en').translate(ar_front_data)
    id_number_pattern = r"\b\d{11}\b"
    
    words = re.findall(r'\b[A-Z]{3,}\b', ar_front_data)
    # print(f"WORDS: {words}")
    nationality = extract_and_check_country(words)
    country = pycountry.countries.lookup(nationality)
    nationality_iso =  country.alpha_3
    
    names_list = extract_name_after_nationality(words, nationality)
    name = ' '.join(names_list)

    id_number_match = re.search(id_number_pattern, ar_front_data, re.IGNORECASE)
    if id_number_match:
        id_number = id_number_match.group(0)
    else:
        try:
            id_number_match = re.search(id_number_pattern, ar_front_data, re.IGNORECASE)
            id_number = id_number_match.group(0)
        except:
            id_number = ''
    
    dates = sort_dates_by_datetime(re.findall(r'\d{2}/\d{2}/\d{4}', ar_front_data))
    # print(f"DATES: {dates}")
    dob = dates[0]
    expiry = dates[-1]
    
    patterns_to_remove = [
        r"State Of Qatar", r"Residency Permit", r"ID\.No:", r"D\.O\.B\.:", r"D\.O\.B:",
        r"Expiry:", r"Nationality:", r"\d{9}", r"\d{2}/\d{2}/\d{4}", r"بنغلاديش", r"الهند",
        r"on", re.escape(nationality), r"الرقم الشخصي:", r"تاريخ الميلاد:", r"الصلاحية:",
        r"الجنسية:", r"دولة قطر", r"رخصة إقامة", r"المهنة:", r"الاسم:", r"Name:", re.escape(name)
        ]

    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns_to_remove]

    lines = ar_front_data.split("\n")

    # filtered_lines = [line for line in lines if not any(pattern.search(line) for pattern in compiled_patterns)]
    countries_list = ['أفغانستان', 'جزر أولاند', 'ألبانيا', 'الجزائر', 'ساموا الأمريكية', 'أندورا', 'أنغولا', 'أنغويلا', 'القارة القطبية الجنوبية', 'أنتيغوا وبربودا', 'الأرجنتين', 'أرمينيا', 'أروبا', 'أستراليا', 'النمسا', 'أذربيجان', 'باهاماس', 'البحرين', 'بنغلاديش', 'بربادوس', 'بيلاروسيا', 'بلجيكا', 'بليز', 'بنين', 'برمودا', 'بوتان', 'بوليفيا', 'البوسنة والهرسك', 'بوتسوانا', 'جزيرة بوفيه', 'البرازيل', 'إقليم المحيط الهندي البريطاني', 'جزر العذراء البريطانية', 'بروناي', 'بلغاريا', 'بوركينا فاسو', 'بوروندي', 'كابو فيردي', 'كمبوديا', 'الكاميرون', 'كندا', 'الجزر الكاريبية الهولندية', 'جزر كايمان', 'جمهورية أفريقيا الوسطى', 'تشاد', 'تشيلي', 'الصين', 'جزيرة الكريسماس', 'جزر كوكوس', 'كولومبيا', 'جزر القمر', 'جمهورية الكونغو', 'جزر كوك', 'كوستاريكا', 'كرواتيا', 'كوبا', 'كوراساو', 'قبرص', 'التشيك', 'الدنمارك', 'جيبوتي', 'دومينيكا', 'جمهورية الدومينيكان', 'جمهورية الكونغو الديمقراطية', 'الاكوادور', 'مصر', 'السلفادور', 'غينيا الاستوائية', 'إريتريا', 'إستونيا', 'إسواتيني', 'إثيوبيا', 'جزر فوكلاند', 'جزر فارو', 'فيجي', 'فنلندا', 'فرنسا', 'غويانا الفرنسية', 'بولينزيا الفرنسية', 'أراض فرنسية جنوبية', 'الجابون', 'غامبيا', '\u202bجورجيا', 'ألمانيا', 'غانا', 'جبل طارق', 'اليونان', 'جرينلاند', 'غرينادا', 'غوادلوب', 'غوام', 'غواتيمالا', 'غيرنزي', 'غينيا', 'غينيا بيساو', 'غيانا', 'هايتي', 'جزيرة هيرد وجزر ماكدونالد', 'هندوراس', 'هونج كونج', 'هنجاريا', 'آيسلندا', 'الهند', 'أندونيسيا', 'إيران', 'العراق', 'أيرلندا', 'جزيرة مان', 'إيطاليا', 'ساحل العاج', 'جامايكا', 'اليابان', 'جيرسي', 'الأردن', 'كازاخستان', 'كينيا', 'كيريباتي', 'كوسوفو', 'الكويت', 'قيرغيزستان', 'لاوس', 'لاتفيا', 'لبنان', 'ليسوتو', 'ليبيريا', 'ليبيا', 'ليختنشتاين', 'ليتوانيا', 'لوكسمبورغ', 'ماكاو', 'مدغشقر', 'مالاوي', 'ماليزيا', 'المالديف', 'مالي', 'مالطا', 'جزر مارشال', 'مارتينيك', 'موريتانيا', 'موريشيوس', 'مايوت', 'المكسيك', 'ولايات ميكرونيسيا المتحدة', 'مولدوفا', 'موناكو', 'منغوليا', 'مونتينيغرو', 'مونتسرات', 'المغرب', 'موزمبيق', 'ميانمار', 'ناميبيا', 'ناورو', 'نيبال', 'هولندا', 'جزر الأنتيل الهولندية', 'كاليدونيا الجديدة', 'نيوزيلندا', 'نيكاراغوا', 'النيجر', 'نيجيريا', 'نييوي', 'جزيرة نورفولك', 'كوريا الشمالية', 'مقدونيا الشمالية', 'جزر ماريانا الشمالية', 'النرويج', 'سلطنة عمان', 'باكستان', 'بالاو', 'فلسطين', 'بنما', 'بابوا غينيا الجديدة', 'باراغواي', 'بيرو', 'الفلبين', 'جزر بيتكيرن', 'بولندا', 'البرتغال', 'بورتوريكو', 'قطر', 'ريونيون', 'رومانيا', 'روسيا', 'رواندا', 'سان بارتيلمي', 'سانت هيلينا', 'سانت كيتس ونيفيس', 'سانت لوسيا', 'سانت مارتن', 'سان بيير وميكلون', 'سانت فينسنت والغرينادين', 'ساموا', 'سان مارينو', 'ساو تومي وبرينسيب', 'السعودية', 'السنغال', 'صربيا', 'سيشل', 'سيراليون', 'سنغافورة', 'سانت مارتن', 'سلوفاكيا', 'سلوفينيا', 'جزر سليمان', 'الصومال', 'جنوب أفريقيا', 'جورجيا الجنوبية وجزر ساندويتش الجنوبية', 'كوريا الجنوبية', 'جنوب السودان', 'إسبانيا', 'سريلانكا', 'السودان', 'سورينام', 'سفالبارد ويان ماين', 'السويد', 'سويسرا', 'سوريا', 'تايوان', 'طاجيكستان', 'تنزانيا', 'تايلاند', 'تيمور الشرقية', 'توجو', 'توكيلاو', 'تونغا', 'ترينيداد وتوباغو', 'تونس', 'تركيا', 'تركمانستان', 'جزر توركس وكايكوس', 'توفالو', 'جزر الولايات المتحدة الصغيرة النائية', 'جزر العذراء الأمريكية', 'أوغندا', 'أوكرانيا', 'الإمارات العربية المتحدة', 'المملكة المتحدة', 'الولايات المتحدة الأمريكية', 'أوروغواي', 'أوزبكستان', 'فانواتو', 'مدينة الفاتيكان', 'فنزويلا', 'فيتنام', 'واليس وفوتونا', 'الصحراء الغربية', 'اليمن', 'زامبيا', 'زيمبابوي']
    
    arabic_keywords_to_remove = [
        "الرقم الشخصي", "تاريخ الميلاد", "الصلاحية", "الجنسية", "دولة قطر", "رخصة إقامة", "المهنة", "الإسم", "اداره"
    ] 

    filtered_lines = []
    for line in lines:
        match_score = get_fuzzy_match_score(line, arabic_keywords_to_remove)
        match_score1 = get_fuzzy_match_score(line, countries_list)

        if match_score or match_score1:
            score = match_score if match_score else match_score1
    #         print(f"Line: '{line}' matched with a score of {score}")
        elif not any(pattern.search(line) for pattern in compiled_patterns):
            filtered_lines.append(line)

    # print(f"\n\nFILTERED: {filtered_lines}\n\n")

    arabic_list = []
    occupation = ''
    try:
        arabic_words = [word for word in filtered_lines if is_arabic(word)]
        occupation = arabic_words[0]

    except:
        occupation = ''

    # print(f"OCCUPATION: {occupation}")

    front_data = {
        # "name_raw": name,
        "nationality": nationality_iso,
        "id_number": id_number,
        "dob": dob,
        "expiry_date": expiry,
        "occupation": occupation,
        "occupation_en": GoogleTranslator(dest = 'en').translate(occupation) if occupation else ''
    }
    
    return front_data

def qatar_front_id_extraction(client, image_data, front_id_text, front_id_text_description):
    cropped_id_card, third_part, third_part_text = detect_id_card(client, image_data, front_id_text, part='third')
    # print(f"THIRD: {third_part_text}")
    front_data = extract_name_fields_from_cropped_part(third_part_text.replace("\n", ""))
    numeric_fields = extract_numeric_fields_from_raw(front_id_text_description)

    front_data.update(numeric_fields)
    
    return front_data

def extract_employer_from_back(data, passport_number, passport_date, serial_no):
    patterns_to_remove = [r"رق[ـم]* ج[ـوا]*ز السفر", r"تاريخ انتهاء ?الجواز", r"الرقم المسلسل", 
                          r"ن[ـو]*ع الرخص[ـة]*", r"مدير عام الإدارة العامة( للجوازات| الجورت)?", 
                          r"ترفيع حامل البطاقة", r"توقيع حامل البطاقة", r"passport_number|passport_date|serial_no", 
                          r"Holder's signature", r"Passport Number", r"Passport Expiry",
                          r"Serial No", r"Residency Type", r"Employer", r"Directorate of Passports", 
                          r"General Director of the General", re.escape(passport_number), 
                          re.escape(passport_date), re.escape(serial_no), r":",
                        ]

    compiled_patterns = [re.compile(pattern) for pattern in patterns_to_remove]

    for pattern in compiled_patterns:
        data = re.sub(pattern, "", data)

    lines = data.split("\n")

    lines = [line for line in lines if line.strip()]
    
    # print(f"Filtered data: {lines}")

    employer = max(lines, key=len)

    return employer


def qatar_back_id_extraction(back_id_text_description):
    serial_no_pattern = r"\b\d{14}\b|\b[A-Za-z0-9]{13,16}\b"
    passport_no_pattern = r"([A-Za-z]\d{8}|[A-Za-z]{2}\d{7}|[A-Za-z]\d{7})"
    # emp_pattern = r'Employer:\s*([\w\s.]+.)\n\b'

    serial_no_match = re.search(serial_no_pattern, back_id_text_description, re.IGNORECASE)
    try:
        if serial_no_match:
            serial_no = serial_no_match.group(0)
        else:
            serial_no = serial_no_match.group(1)
    except:
        serial_no = ''

    passport_no_match = re.search(passport_no_pattern, back_id_text_description, re.IGNORECASE)
    if passport_no_match:
        passport_no = passport_no_match.group(0)
    else:
        passport_no = ''

    dates = sort_dates_by_datetime(re.findall(r'\d{2}/\d{2}/\d{4}', back_id_text_description))
    passport_expiry = dates[0] if dates else ''

    employer = extract_employer_from_back(back_id_text_description, passport_no, passport_expiry, serial_no)

    employer_en = ''
    if employer:
        employer_en = GoogleTranslator(dest = 'en').translate(employer)

    back_data = {
        "passport_number": passport_no,
        "passport_expiry": passport_expiry,
        "card_number": serial_no,
        "employer": str(employer),
        "employer_en": employer_en,
        "issuing_country": "QTR"
    }

    return back_data
