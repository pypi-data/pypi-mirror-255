import time
import numpy as np
import pytesseract
from pytesseract import Output
import os
username = os.getlogin()
tesseractPath = f'C:\\Users\\{username}\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'
if not os.path.exists(tesseractPath):
    raise ValueError(f"{tesseractPath} does not exist.\nPlease download tesseract.exe on your machine")
else:
    pytesseract.pytesseract.tesseract_cmd = tesseractPath


def get_word_coordinates(screenshot_gray, word='robot'):
    d = pytesseract.image_to_data(screenshot_gray, output_type=Output.DICT)
    n_boxes = len(d['level'])
    min_words = 99999
    matched_coord = None
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        if(word in d['text'][i]):
            if(min_words > len(d['text'][i].split(" "))):
                matched_coord = (x, y, w, h)
                min_words = len(d['text'][i].split(" "))
    return matched_coord