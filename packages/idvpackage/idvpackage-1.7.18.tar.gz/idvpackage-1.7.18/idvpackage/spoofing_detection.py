import cv2
import numpy as np
import os
from idvpackage.spoof_detection.anti_spoof_predict import AntiSpoofPredict
from idvpackage.spoof_detection.generate_patches import CropImage
from idvpackage.spoof_detection.utility import parse_model_name
import warnings
import argparse
import base64
import pkg_resources

warnings.filterwarnings('ignore')

def check_image(image):
    height, width, channel = image.shape
    if width/height != 3/4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    else:
        return True

def compute_label(image, model_test, image_cropper):
    image = cv2.resize(image, (int(image.shape[0] * 3 / 4), image.shape[0]))
    result = check_image(image)
    if result is False:
        return None, None, None

    image_bbox = model_test.get_bbox(image)
    prediction = np.zeros((1, 3))

    model_dir = pkg_resources.resource_filename('idvpackage', '/resources/anti_spoof_models')

    # Sum the prediction from single model's result
    for model_name in os.listdir(model_dir):
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        param = {
            "org_img": image,
            "bbox": image_bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            param["crop"] = False
        img = image_cropper.crop(**param)
        prediction += model_test.predict(img, os.path.join(model_dir, model_name))

    # Draw result of prediction
    label = np.argmax(prediction)
    value = prediction[0][label] / 2

    if label == 2 and value > 0.52:
        label_text = "SPOOF"
    elif label == 2 and value < 0.52:
        label_text = "REAL"
    elif label == 1 and value > 0.50:
        label_text = "REAL"
    elif label == 1 and value < 0.50:
        label_text = "SPOOF"
    else:
        label_text = "UNKNOWN"

    return label_text, label, value

def process_image(base64_image, model_test, image_cropper):
    image_bytes = base64.b64decode(base64_image)
    image_np = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    label_text, label, value = compute_label(frame, model_test, image_cropper)
    
    return label_text, label, value

def spoof_detection_main(base64_image):
    desc = "test"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--device_id",
        type=int,
        default=0,
        help="which gpu id, [0/1/2/3]")
    args = parser.parse_args()

    model_test = AntiSpoofPredict(args.device_id)
    image_cropper = CropImage()

    label_text, label, value = process_image(base64_image, model_test, image_cropper)

    # print("Prediction Results:")
    # print(f"Label Text: {label_text}")
    # print(f"Label: {label}")
    # print(f"Value: {value}")

    return label_text, label, value
