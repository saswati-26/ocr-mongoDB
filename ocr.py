import pytesseract
import cv2
import numpy as np
import requests
import os

TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX')

def process_image(image_url):
    response = requests.get(image_url)
    image_array = np.frombuffer(response.content, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    text = pytesseract.image_to_string(image)
    return text.strip()
