


import io
from stat import filemode
#from tkinter import Image
from tokenize import String
import pytesseract as tess
import cv2 as cv
import numpy as np
import os
import glob
from pytesseract import Output
from PIL import Image as pl
import json
from flask import Flask, request, jsonify, render_template
from numpy import product
import base64
from roboflow import Roboflow
import asyncio
from flask import send_from_directory   

tess.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'

cong = r'--oem 3 --psm 6 outputbase digits'

# gray scale
def get_grayscale(image):
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv.medianBlur(image, 5)

# thresholding
def thresholding(image):
    return cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

# dilation
def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv.dilate(image, kernel, iterations=1)

# erosion
def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv.erode(image, kernel, iterations=1)

# opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv.morphologyEx(image, cv.MORPH_OPEN, kernel)

# canny edge detection
def canny(image):
    return cv.Canny(image, 100, 200)

# skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv.warpAffine(
        image, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
    return rotated

# template matching
def match_template(image, template):
    return cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)


rf = Roboflow(api_key="yk7y1Pvo0YE7xPuaLBvD")
project = rf.workspace("hasan-berat").project("gas-meter-3ajnr")
model = project.version(2).model


def pre(img_path):
    j  =  model.predict(img_path, confidence=40, overlap=30).json()
    return j 



app = Flask(__name__,template_folder = 'template')
  


@app.route('/')
def index():
    return "<h1>Sayac Projesi...</h1>"



@app.route('/base', methods=['POST'])
async def base():
    
    global x1 
    global x2 
    global y1 
    global y2 

    data = request.get_json()
    print(data['base64'])

    # its come base64 raw code
    rawdata = data['base64']
    encoded_data = str.encode(rawdata)
    

    b = base64.b64decode(encoded_data+ b'=' * (-len(rawdata) % 4) )
    val = io.BytesIO(b)
    img = pl.open(fp=val, mode='r') 
    img.save("test.jpeg") # converted and saved base64 to image
    

    img_path  = "test.jpeg"
    img = cv.imread(img_path)

    
    j = pre(img_path)
    print(j)
 
    try:
        detec = j['predictions']
        for bounding_box in detec:
             x1 = int(bounding_box['x'] - bounding_box['width'] / 2)
             x2 = int(bounding_box['x'] + bounding_box['width'] / 2)
             y1 = int(bounding_box['y'] - bounding_box['height'] / 2)
             y2 = int(bounding_box['y'] + bounding_box['height'] / 2)
      
        img = img[y1:y2, x1:x2]

    except NameError as err:
        print("type error: {0}".format(err))


    """ 
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_thresh = thresholding(img_gray)
    img_open = opening(img_thresh)
    img_canny = canny(img_open)
    """   
    cıktı = tess.image_to_string(img,config=cong)
    print('CIKTI ==> ', cıktı)
    
    return jsonify(cıktı)
