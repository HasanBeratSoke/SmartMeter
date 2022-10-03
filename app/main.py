from email.mime import image
import io
from tokenize import String
import pytesseract as tess
import cv2 as cv
import numpy as np
import os
import glob
from pytesseract import Output
from PIL import Image as pl

#tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
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

'''
img = cv.imread('sayi2.jpeg')
img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
img_thresh = thresholding(img_gray)
img_open = opening(img_thresh)
img_canny = canny(img_open)
'''
#iw, ih, ic = img.shape

#d = tess.image_to_data(img, output_type=Output.DICT, config=cong)
#print(d.keys())

'''n_boxes = len(d['text'])
for i in range(n_boxes):
    if int(float((d['conf'][i]))) > 20:
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)     # draw the bounding box around the text
        cv.putText(img, d['text'][i], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        print(d['text'][i])

        #img = cv.rectangle(img_canny, (x, y), (x + iw, y + ih), (255, 255, 0), 4)
        #img = cv.putText(img, d['text'][i], (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)'''
    
print('\n-----------------------------------------------------')
#print(tess.image_to_string(img_canny,config=cong))
print('\n-----------------------------------------------------')
#print(tess.image_to_data(img_canny, config=cong))
print('\n-----------------------------------------------------')


import json
from flask import Flask, request, jsonify, render_template
from numpy import product
import base64

app = Flask(__name__,template_folder = 'template')
from flask import send_from_directory     


@app.route('/')
def index():
    return "<h1>beylerrr</h1>"
    

@app.route('/product', methods=['GET'])
def get_products():
    return jsonify({'product': "Hello World"})



@app.route('/base', methods=['POST'])
def base():
    data = request.get_json()
    print('---------------------------------------')
    print(data['base64'])
    print('---------------------------------------')
    #decoded_data=base64.urlsafe_b64decode((data['base64']) + '=' * (-len(data['base64']) % 4)) 
    #decoded_data = base64.standard_b64decode(data['base64']);
    """img_file = open('image4.jpeg', 'wb')
    img_file.write(decoded_data)
    img_file.close()"""
    
    rawdata = data['base64']
    b = base64.b64decode(rawdata)
    resim = pl.open(io.BytesIO(b))
    resim.save('image.png')
    
    #print(data['base64'])
    img = cv.imread('image.png')
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_thresh = thresholding(img_gray)
    img_open = opening(img_thresh)
    img_canny = canny(img_open)
    cıktı = tess.image_to_string(img_canny,config=cong)
    return jsonify(cıktı)









'''

cv.imshow('sonuc', img)

cv.waitKey(0)
cv.destroyAllWindows()

'''
