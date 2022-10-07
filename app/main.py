
from email.mime import image
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
    encoded_data = str.encode(rawdata)
    

    b = base64.b64decode(encoded_data+ b'=' * (-len(rawdata) % 4) )
    val = io.BytesIO(b)
    img = pl.open(fp=val, mode='r') # ERROR IS HERE
    img.save("test.jpeg")

    """  
    rawdata = "data:image/jpeg;base64,%2F9j%2F4AAQSkZJRgABAQEAAAAAAAD%2F2wBDAAoHCAkIBgoJCAkLCwoMDxkQDw4ODx8WFxIZJCAmJiQgIyIoLToxKCs2KyIjMkQzNjs9QEFAJzBHTEY%2FSzo%2FQD7%2F2wBDAQsLCw8NDx0QEB0%2BKSMpPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj7%2FxAAfAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgv%2FxAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5%2Bjp6vHy8%2FT19vf4%2Bfr%2FxAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv%2FxAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4%2BTl5ufo6ery8%2FT19vf4%2Bfr%2FwAARCADwAUADASEAAhEBAxEB%2F9oADAMBAAIRAxEAPwDFSCPP%2BrWnmKP%2FAJ5rVeZPKkM8qP8A55ijyk%2F55rU3FyjvLTH%2BrWkMMWfuCh6i5EKYo%2F8AnmKPKiz9wUIFBDvLi7RrTvLi%2FwCea0XK9mg8mL%2FnmKd5UX%2FPNaAUEhRFF%2FzzWlEKf3BQHIO8qP8AuLThFH%2FzzWm2LkQvlR%2F881p%2Flxf88lpByIUQx%2F8APNacII%2F7gobF7ND%2FACov%2BeYp3lJ%2FcFG4%2BQcIo%2F7gqRYY%2FwDnmtBPs0PEUf8AzzWnrDH%2FAM81pj5R%2Fkx%2F881qQQx%2F881pC5EL5MX%2FADzWneTH%2FwA81oFyIXyY%2FwDnmtL5UX%2FPNaCfZoPKj%2F55ijyov7i1QezQhij%2FAOeYpvlRf881pEumhDHF%2FwA8xUflRf3BTuL2URDFF%2FcFNMMX%2FPIVRPsYnPYp1ZnYyHoeKdmla%2BowpfpTF1DrThU%2BSHYO9OFMYtOoF9oWnUwFp1FgFp9ADhTqQDgKeKbEPAp4FAx4FPAoESCnigQuKfQIWjFAgpKYDDTDQSQTTpEMu2KgS%2BhY%2FeP4jFAiwGDDinVQHOYpKnyNSM9aSpKF%2BtFOwC04ChAOxS0APApdtFg2FpQKAH0tAdB%2BKXFJDHCnCgQ4U8U7ASCngUAPxTxQIkFOFAh4paBDsUYoEGKbimIY1V528tCaBGasOTvfl%2FWpPKyOlMZLbLjirYWmSc1RxUG1iJqbQMD7UtN7aAh%2BOKdUlC0opvYkk%2FCgUhjgKdimAtOoAcKdSAdTqBDgKkFFwsPFPFCAfTxTESCngUAOFOoEOxRQSGKTFAEZFQTR7hTERwwZNWfISmSRLFh6mEdMDk6aaiRqRNSL0pNsdg9qcKZQoHNPoEOFSUXAWlosA6nUDQ4UtIB1LimA4U%2BkIcBT1oYElPFMB4p4FADxT6CWPFOpAOpaZNgxSYpiE20nl0xCrFg0FB5lBI8Qin%2BVVAcMevtTTWe50ET9qQ0DWwtOApMB1KKI6oQ8U8Uyhwp1IQ6loSAdTqBi4p1Ah9OoAcBTxSAeKeKBDxTxTAkFOpkjxTqBD6WgBcUuKaJHbaesdUIt2tkbmYRjj1NdFb2VvbriOJc%2BvelISjcdPawzrh41%2BuKyH0qVOgDj2pXKcDyo000GhDJScbRSK6DqUUXEO6U9aTHoPp9IY6nU2IWnUBsOop3AfTqkY4U%2FFO4hwp4qRDqeKYDqkFUA4VIKQhwp9Ah1OpiFFSAUxEypVmGEswAGSapEm9ZWgtlOeXbrVqoZqFFAzww0ygLDGxTd1P1AWnioQDhyKcBVdbAh4p2Oc0mhjxThR0AdS4oQDhS0CHU6pKHAU6mIcKfQA6n0CHin0AOFOFMQ8U8UxDqeKBD1qVaZJZQVuaZbhI%2FOZT5jevYVT2Gi%2FRUGgUUAeGHmm0wI26UwdKXkA4U8UXAeKdQA9afQUO706l5gOFKKAFp1Ahwp9AxacKRI6n0wHU6gBwp1AD6cKAHU8UEjhTxTESLUyVRJetYvPmjiPRjz9K6aky4hRSKCigDwymE80PcGNNRA9OKLAiQdKepoYwqQUguOqQUDHinClcm46loKsOFLTJsOpwoGOp1SMdTqZItOoAcKdQA6nCgB1OFMQ8GnZpiJAanjNNEm1oabrqST%2B4m3863KTKQUUFBRQB4XTTR1GMJqPj0oejC48U8UIB9PHtSeoD1p1KwDxThTEx1KKPMofS0gHU4UAOp1IBaUUxC08UCFpaYDqdmgBc0oamIcDTwaCR6tViM800DOi8Pf6u4%2F3x%2FKtikUFFAwooA8LNMJoYDCRTOT1qbdQHrT6oY4VJS6huPWlp9QJBTqkBwp1Ax1LQA6nCgTHU6kAU6mAop1Agp1AC5ozQAuaXNMQuacDTEPDVMj0xG34fuxHfGFvuzDjn%2BIV09IaCigoKKAPCM4pu7PShjGd6dUhYdTqbYbDxTwKLCuOxTqBjxThSAcOlLQA6nUxjqcKQh1LQA6loAXNLSEFLmmwClpgGaM0wFzRuoEO3U9Xpkk6y%2B9dNpevxsvk377HHSQ9Gp9Bpm8CD0pakoKKAPBz1pjUw3EWn1O7Acv0p3ehodx4p9DCw4U4Uhki04ChgKBRigB1OoEOpaBodS1ICinUxBS0xBS0AJRmmAuaTNITDdRupki7qN9UA4SU%2Fzfypklm2v57Zs21xJDnsvSr6eJdSRcGSF%2Fdo6Y0xzeKNQxx9nH%2FADVObxDqTtk3hC5%2B6igUJILnDmmVBpuOFO%2FGi4EijinUgHAc1IKLjsOp4FSMeBS0xC0%2BkNCilxQFh22gCmAuDS1IxaWmSFLTADRQAlFMQhNJmgBM0m6gQm6k30xBvo8yncTDzaTzqZI0zVG0tMDIJoFZtmuw6nDpmhDuPFSChgPpwFIWo%2BnCgocKWhAPFOpAKKeKAFpaYDqXFIBNtJtoEHNJTEJmjNAWCm5oTATNJmmAzNJuoEJuppamITfSF6BMb5lNL0ySMyVGZKbAqU4GpUTazHU5f0pMCQU9eaWwh9PFAxwp9FwFFOFK4xwp9ADqcKCbC06i4xadQAUUwFpuKQhhWmlaChtNzTJsNzSHPfigCEzRD%2FlrH%2F32KTzUPR1%2FOqENMydC6%2FiaTzRQITdTC9DAYXphemhEZeoi9JtkgDSinaxrzD6cCKnluwQ8dM1ItAxwp9Sxj6cKZI6nUWGOFO70APpwpAx1OoGLS0CFopgFJSASmmmA0%2FpWbf6xp9kvzyea39yL5qdriuc9deI7iX%2FAFKi3T82rJlu2c%2FvJJJP95qqwCC7A6ClF9jooPtSGH20793Sug0q9sLgw2klwYJyP3lzM37tasVjobjQb6GyN3aSxX9kq7mnU7MCsZLqGb%2FUsWPSpsTcVie9Rs1IREWqNnxVWuSWaM1Pqa7Dqf8ASjYNh4p9JDHikkDkfuyAfepEiWPPlru645p4pjHinCmMdS0APp4pCHUtIYtLTAdRSEFJQISq19dwWFq09y%2B1R%2BtAM4fWNenv2ZVJhg%2FuCqmnWrXknmMsi2i%2F62dewq9hhqL2CS%2BXp6SbV6u753VR70gG0uDTsDFxRj1GaoCcX13EmEupwB0TzDtrQjkjlMh%2B2xtOrYGIiA49anqLqacMjlfmzSsc09hERaoy1HN1IsX6dkVLRsxc08dKCR4NPFAxQakFJsBwp4oCw6nUDHCn0AKKf2oAUU6gQtOpDFooEJRQIgu7qKztXnnPyp2HU151rOpy3920svQcKnYVaCxo2GiLb2v9o6wh2LyLbpVHU9anvV8lB5FuDxGh4pDMvr1p1MZIAKWhMBRS0XAYVqP5o23KadxF%2B21F8ojseOBzWmkhcZo3ViQJqImhCNWlpIqw6nZpDHU8UAh1PBosA%2BnimK44U6kMcKfmgBRTqBjqWkA4UtAhc0ZoAKQcmmI4rxbqXn3htY3%2FAHUHykDuaf4V0ZXUaldcgH90nb%2Fep30DoUfFGqNe3hjRm8pOue5rBFUloCHipF6UrFiM2OlNy1IQuTTlegQ7dmg4NADDF8pNamnXSywiMv8AvV7e1FxF09KjoIuatIOlBqOFPFJktjlp4NFhjqeKEIcKdTGh9OpDFFPoELS0DH06kIWlzSYBRmgQZqK5l8q1mlHVIy1UhnnOmW%2F9r6zHC%2F3XJd8%2F3RXReI9ZFuEs7CRNoG1%2FL6D2o%2B0I4w8v9TmlxV847kiDinVIDDxTd1CAN%2FXIozTC%2BouaQsRSGSR3G0FHXcre9RDdE%2FnJn5fSixNzokbzIwaaaFoT5GqMUcdqe4wXrUlJjQ%2BnA0JjuPHpThQKw8GnCgB4p9AxaWpAdmloGOp2aoQZp2akAzSZoY2BNU9XuY7bSbiSYbkZdmPXNUiTzqyunsrnz4%2BG2FevTNQu5fqeaoZH0NLSYEwpx%2B7SsAzFJjFFugDTyabQIVaniZc4kzt9qZVhk6Irfu3Dx9jSRy%2BXIG7d6bIaNWN1hA3HCdjU%2Bc1JJrUGl1NhwNOHWmQh1PFFmMfS0IB9PFAhwp2akGOzTqbGKKdSAKdVALS5qRhSUxATXO%2BNJithawjo8m8%2FhTQHFtz1ptOwCUtDQywvSgnFShMDTKYXEpuKGAU3dTBi7vlxUbZxQI1I2E1skfParcMeyMLnpSehJs5oznoabiWxc08dKXoJaIeKdRcB1OoTGPSn0dQHA04GgGOp1AxQaXNAhRTs0gFzRmmIM0maQwzXLeNT%2FwAeX0amgOTpMU3oA%2FbTmGBQMFanZpS7AhpPNNoAWkPSh7iI6SgBQeavWl7Zwk%2Fb9LS8B9JWjagTNZ302cJJp2nyWQxyjzeZTM0MzNbdRTNGxacKTiJDqdmhIbHU%2BqWgDwaduqbAOpw6UDHCnZpgLS5pBcdmlpALmkzTCwmaDSEGa53xhEWt7WfBKx7kPHTNNAcfTsU%2BpQ48UP0zSHIizzTwaGQHBpOtFiri7qbnmkSMJpOKYxymnsu4igVzUiu4UjAO5fwzUokjcZDiiJJtHpRmgtinpTs%2BlMBRThQmSPHHSng0DFzSg0hj6cDQgFp1MB2aXNAh2aXdSGGaM0AFGaQmJVLWVSTRLwSKCBEWH17UwOei0uO48LJeRL%2FpTfPjPBHPFYXfGMUJD3Agk8009KBkVOBoZIZ5ozRcYUw0AM%2BtBp3EKD81ThuKVwH54opJAddSVVwHUopXBD%2BgpRQA6nA00A6nZ5pMBwJp2aNgFp%2BaGMXNLmmwFzSil0AXNFAmFGaBiVU1Qb9HvVPeBqBMNNT7NpdnEv8ABEv%2BNZd34biub0y29z9nEh%2BZCm7mkmGxzEo8ueWLvG5Xmoe9MYykzQAtLQAlJQNDKTNArhUqdKBBnB60bzSA6%2FzUY4yuR%2BdO3pjGavnglYHHUTzE7GnefHtwX%2FOpv1DVjvOXHDL%2BdAmTuwz9afMmg5NB3nIO45pwmT%2B%2BPzouHKyTzk%2FvCn7hUuaHZiiRM8EGnb19aOdCs7jhIvY0u8Z60%2BZBYd5g9cUCRT0Io0KsO3j1p28UXsKwm8etLuFDmhWE3il3ii40hNwqnq0yrpF5g8%2BUR%2BdHMhFrIXaoPCqF%2FSm7x60tAOP8SoItZ83jbcLu%2FHvWWXX1pNgtiJnX1FN3rTuMdvU96PMFK6GG8fSk3r60%2BZAxN4puR60cwWHB1pysPWnzJE2GPIN1J5gouFjud%2FrTtx70ciATJ9eacG%2Bb3p2SC4biTzS7ieKLWCwu%2FFPRvzosrBa2o7fz707NKwC7qcHoSQDt1LuoSQx240b6dhBmlzTsAuaM80rAGaM0hiZqrqXzWSp%2FeuIl%2FwDHqNALTNkknrTCaBFLVbc3ulywj7y%2FvE%2BorjsnAo0CJE5qLNCH5hn1pOlHKPUAaXdRZbBrcTfRuo5RD85FOShCGyEbvmFRMV%2FhFAH%2F2QAA"
    b = base64.b64decode(rawdata)
    resim = pl.open(io.BytesIO(b))
    resim.save('image.png') 
    """
    



    #print(data['base64'])
    img = cv.imread('image.png')
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_thresh = thresholding(img_gray)
    img_open = opening(img_thresh)
    img_canny = canny(img_open)
    cıktı = tess.image_to_string(img_canny,config=cong)
    return jsonify(cıktı)



""" 
with open('rawdata.txt', 'wb') as f:
        f.write(rawdata)

# Your code
file = open('rawdata.txt', 'rb')
encoded_data = file.read()
file.close() # reading bytes raw data 
 """
""" rawdata = r"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"
encoded_data = str.encode(rawdata)
#encoded_data = bytes()

b = base64.b64decode(encoded_data+ b'=' * (-len(rawdata) % 4) )
val = io.BytesIO(b)
img = pl.open(fp=val, mode='r') # ERROR IS HERE
img.save("test.jpeg") """

""" 
#file = open('C:\\Users\\hasan\\Desktop\\Sayac_Okuyucu\\sayac_okuyucu\\app\\rawdata.txt', 'rb')
encoded_data = file.read()
file.close()
 """
#rawdata =r'%2F9j%2F4AAQSkZJRgABAQEAAAAAAAD%2F2wBDAAoHCAkIBgoJCAkLCwoMDxkQDw4ODx8WFxIZJCAmJiQgIyIoLToxKCs2KyIjMkQzNjs9QEFAJzBHTEY%2FSzo%2FQD7%2F2wBDAQsLCw8NDx0QEB0%2BKSMpPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj4%2BPj7%2FxAAfAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgv%2FxAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5%2Bjp6vHy8%2FT19vf4%2Bfr%2FxAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv%2FxAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4%2BTl5ufo6ery8%2FT19vf4%2Bfr%2FwAARCADwAUADASEAAhEBAxEB%2F9oADAMBAAIRAxEAPwDFSCPP%2BrWnmKP%2FAJ5rVeZPKkM8qP8A55ijyk%2F55rU3FyjvLTH%2BrWkMMWfuCh6i5EKYo%2F8AnmKPKiz9wUIFBDvLi7RrTvLi%2FwCea0XK9mg8mL%2FnmKd5UX%2FPNaAUEhRFF%2FzzWlEKf3BQHIO8qP8AuLThFH%2FzzWm2LkQvlR%2F881p%2Flxf88lpByIUQx%2F8APNacII%2F7gobF7ND%2FACov%2BeYp3lJ%2FcFG4%2BQcIo%2F7gqRYY%2FwDnmtBPs0PEUf8AzzWnrDH%2FAM81pj5R%2Fkx%2F881qQQx%2F881pC5EL5MX%2FADzWneTH%2FwA81oFyIXyY%2FwDnmtL5UX%2FPNaCfZoPKj%2F55ijyov7i1QezQhij%2FAOeYpvlRf881pEumhDHF%2FwA8xUflRf3BTuL2URDFF%2FcFNMMX%2FPIVRPsYnPYp1ZnYyHoeKdmla%2BowpfpTF1DrThU%2BSHYO9OFMYtOoF9oWnUwFp1FgFp9ADhTqQDgKeKbEPAp4FAx4FPAoESCnigQuKfQIWjFAgpKYDDTDQSQTTpEMu2KgS%2BhY%2FeP4jFAiwGDDinVQHOYpKnyNSM9aSpKF%2BtFOwC04ChAOxS0APApdtFg2FpQKAH0tAdB%2BKXFJDHCnCgQ4U8U7ASCngUAPxTxQIkFOFAh4paBDsUYoEGKbimIY1V528tCaBGasOTvfl%2FWpPKyOlMZLbLjirYWmSc1RxUG1iJqbQMD7UtN7aAh%2BOKdUlC0opvYkk%2FCgUhjgKdimAtOoAcKdSAdTqBDgKkFFwsPFPFCAfTxTESCngUAOFOoEOxRQSGKTFAEZFQTR7hTERwwZNWfISmSRLFh6mEdMDk6aaiRqRNSL0pNsdg9qcKZQoHNPoEOFSUXAWlosA6nUDQ4UtIB1LimA4U%2BkIcBT1oYElPFMB4p4FADxT6CWPFOpAOpaZNgxSYpiE20nl0xCrFg0FB5lBI8Qin%2BVVAcMevtTTWe50ET9qQ0DWwtOApMB1KKI6oQ8U8Uyhwp1IQ6loSAdTqBi4p1Ah9OoAcBTxSAeKeKBDxTxTAkFOpkjxTqBD6WgBcUuKaJHbaesdUIt2tkbmYRjj1NdFb2VvbriOJc%2BvelISjcdPawzrh41%2BuKyH0qVOgDj2pXKcDyo000GhDJScbRSK6DqUUXEO6U9aTHoPp9IY6nU2IWnUBsOop3AfTqkY4U%2FFO4hwp4qRDqeKYDqkFUA4VIKQhwp9Ah1OpiFFSAUxEypVmGEswAGSapEm9ZWgtlOeXbrVqoZqFFAzww0ygLDGxTd1P1AWnioQDhyKcBVdbAh4p2Oc0mhjxThR0AdS4oQDhS0CHU6pKHAU6mIcKfQA6n0CHin0AOFOFMQ8U8UxDqeKBD1qVaZJZQVuaZbhI%2FOZT5jevYVT2Gi%2FRUGgUUAeGHmm0wI26UwdKXkA4U8UXAeKdQA9afQUO706l5gOFKKAFp1Ahwp9AxacKRI6n0wHU6gBwp1AD6cKAHU8UEjhTxTESLUyVRJetYvPmjiPRjz9K6aky4hRSKCigDwymE80PcGNNRA9OKLAiQdKepoYwqQUguOqQUDHinClcm46loKsOFLTJsOpwoGOp1SMdTqZItOoAcKdQA6nCgB1OFMQ8GnZpiJAanjNNEm1oabrqST%2B4m3863KTKQUUFBRQB4XTTR1GMJqPj0oejC48U8UIB9PHtSeoD1p1KwDxThTEx1KKPMofS0gHU4UAOp1IBaUUxC08UCFpaYDqdmgBc0oamIcDTwaCR6tViM800DOi8Pf6u4%2F3x%2FKtikUFFAwooA8LNMJoYDCRTOT1qbdQHrT6oY4VJS6huPWlp9QJBTqkBwp1Ax1LQA6nCgTHU6kAU6mAop1Agp1AC5ozQAuaXNMQuacDTEPDVMj0xG34fuxHfGFvuzDjn%2BIV09IaCigoKKAPCM4pu7PShjGd6dUhYdTqbYbDxTwKLCuOxTqBjxThSAcOlLQA6nUxjqcKQh1LQA6loAXNLSEFLmmwClpgGaM0wFzRuoEO3U9Xpkk6y%2B9dNpevxsvk377HHSQ9Gp9Bpm8CD0pakoKKAPBz1pjUw3EWn1O7Acv0p3ehodx4p9DCw4U4Uhki04ChgKBRigB1OoEOpaBodS1ICinUxBS0xBS0AJRmmAuaTNITDdRupki7qN9UA4SU%2Fzfypklm2v57Zs21xJDnsvSr6eJdSRcGSF%2Fdo6Y0xzeKNQxx9nH%2FADVObxDqTtk3hC5%2B6igUJILnDmmVBpuOFO%2FGi4EijinUgHAc1IKLjsOp4FSMeBS0xC0%2BkNCilxQFh22gCmAuDS1IxaWmSFLTADRQAlFMQhNJmgBM0m6gQm6k30xBvo8yncTDzaTzqZI0zVG0tMDIJoFZtmuw6nDpmhDuPFSChgPpwFIWo%2BnCgocKWhAPFOpAKKeKAFpaYDqXFIBNtJtoEHNJTEJmjNAWCm5oTATNJmmAzNJuoEJuppamITfSF6BMb5lNL0ySMyVGZKbAqU4GpUTazHU5f0pMCQU9eaWwh9PFAxwp9FwFFOFK4xwp9ADqcKCbC06i4xadQAUUwFpuKQhhWmlaChtNzTJsNzSHPfigCEzRD%2FlrH%2F32KTzUPR1%2FOqENMydC6%2FiaTzRQITdTC9DAYXphemhEZeoi9JtkgDSinaxrzD6cCKnluwQ8dM1ItAxwp9Sxj6cKZI6nUWGOFO70APpwpAx1OoGLS0CFopgFJSASmmmA0%2FpWbf6xp9kvzyea39yL5qdriuc9deI7iX%2FAFKi3T82rJlu2c%2FvJJJP95qqwCC7A6ClF9jooPtSGH20793Sug0q9sLgw2klwYJyP3lzM37tasVjobjQb6GyN3aSxX9kq7mnU7MCsZLqGb%2FUsWPSpsTcVie9Rs1IREWqNnxVWuSWaM1Pqa7Dqf8ASjYNh4p9JDHikkDkfuyAfepEiWPPlru645p4pjHinCmMdS0APp4pCHUtIYtLTAdRSEFJQISq19dwWFq09y%2B1R%2BtAM4fWNenv2ZVJhg%2FuCqmnWrXknmMsi2i%2F62dewq9hhqL2CS%2BXp6SbV6u753VR70gG0uDTsDFxRj1GaoCcX13EmEupwB0TzDtrQjkjlMh%2B2xtOrYGIiA49anqLqacMjlfmzSsc09hERaoy1HN1IsX6dkVLRsxc08dKCR4NPFAxQakFJsBwp4oCw6nUDHCn0AKKf2oAUU6gQtOpDFooEJRQIgu7qKztXnnPyp2HU151rOpy3920svQcKnYVaCxo2GiLb2v9o6wh2LyLbpVHU9anvV8lB5FuDxGh4pDMvr1p1MZIAKWhMBRS0XAYVqP5o23KadxF%2B21F8ojseOBzWmkhcZo3ViQJqImhCNWlpIqw6nZpDHU8UAh1PBosA%2BnimK44U6kMcKfmgBRTqBjqWkA4UtAhc0ZoAKQcmmI4rxbqXn3htY3%2FAHUHykDuaf4V0ZXUaldcgH90nb%2Fep30DoUfFGqNe3hjRm8pOue5rBFUloCHipF6UrFiM2OlNy1IQuTTlegQ7dmg4NADDF8pNamnXSywiMv8AvV7e1FxF09KjoIuatIOlBqOFPFJktjlp4NFhjqeKEIcKdTGh9OpDFFPoELS0DH06kIWlzSYBRmgQZqK5l8q1mlHVIy1UhnnOmW%2F9r6zHC%2F3XJd8%2F3RXReI9ZFuEs7CRNoG1%2FL6D2o%2B0I4w8v9TmlxV847kiDinVIDDxTd1CAN%2FXIozTC%2BouaQsRSGSR3G0FHXcre9RDdE%2FnJn5fSixNzokbzIwaaaFoT5GqMUcdqe4wXrUlJjQ%2BnA0JjuPHpThQKw8GnCgB4p9AxaWpAdmloGOp2aoQZp2akAzSZoY2BNU9XuY7bSbiSYbkZdmPXNUiTzqyunsrnz4%2BG2FevTNQu5fqeaoZH0NLSYEwpx%2B7SsAzFJjFFugDTyabQIVaniZc4kzt9qZVhk6Irfu3Dx9jSRy%2BXIG7d6bIaNWN1hA3HCdjU%2Bc1JJrUGl1NhwNOHWmQh1PFFmMfS0IB9PFAhwp2akGOzTqbGKKdSAKdVALS5qRhSUxATXO%2BNJithawjo8m8%2FhTQHFtz1ptOwCUtDQywvSgnFShMDTKYXEpuKGAU3dTBi7vlxUbZxQI1I2E1skfParcMeyMLnpSehJs5oznoabiWxc08dKXoJaIeKdRcB1OoTGPSn0dQHA04GgGOp1AxQaXNAhRTs0gFzRmmIM0maQwzXLeNT%2FwAeX0amgOTpMU3oA%2FbTmGBQMFanZpS7AhpPNNoAWkPSh7iI6SgBQeavWl7Zwk%2Fb9LS8B9JWjagTNZ302cJJp2nyWQxyjzeZTM0MzNbdRTNGxacKTiJDqdmhIbHU%2BqWgDwaduqbAOpw6UDHCnZpgLS5pBcdmlpALmkzTCwmaDSEGa53xhEWt7WfBKx7kPHTNNAcfTsU%2BpQ48UP0zSHIizzTwaGQHBpOtFiri7qbnmkSMJpOKYxymnsu4igVzUiu4UjAO5fwzUokjcZDiiJJtHpRmgtinpTs%2BlMBRThQmSPHHSng0DFzSg0hj6cDQgFp1MB2aXNAh2aXdSGGaM0AFGaQmJVLWVSTRLwSKCBEWH17UwOei0uO48LJeRL%2FpTfPjPBHPFYXfGMUJD3Agk8009KBkVOBoZIZ5ozRcYUw0AM%2BtBp3EKD81ThuKVwH54opJAddSVVwHUopXBD%2BgpRQA6nA00A6nZ5pMBwJp2aNgFp%2BaGMXNLmmwFzSil0AXNFAmFGaBiVU1Qb9HvVPeBqBMNNT7NpdnEv8ABEv%2BNZd34biub0y29z9nEh%2BZCm7mkmGxzEo8ueWLvG5Xmoe9MYykzQAtLQAlJQNDKTNArhUqdKBBnB60bzSA6%2FzUY4yuR%2BdO3pjGavnglYHHUTzE7GnefHtwX%2FOpv1DVjvOXHDL%2BdAmTuwz9afMmg5NB3nIO45pwmT%2B%2BPzouHKyTzk%2FvCn7hUuaHZiiRM8EGnb19aOdCs7jhIvY0u8Z60%2BZBYd5g9cUCRT0Io0KsO3j1p28UXsKwm8etLuFDmhWE3il3ii40hNwqnq0yrpF5g8%2BUR%2BdHMhFrIXaoPCqF%2FSm7x60tAOP8SoItZ83jbcLu%2FHvWWXX1pNgtiJnX1FN3rTuMdvU96PMFK6GG8fSk3r60%2BZAxN4puR60cwWHB1pysPWnzJE2GPIN1J5gouFjud%2FrTtx70ciATJ9eacG%2Bb3p2SC4biTzS7ieKLWCwu%2FFPRvzosrBa2o7fz707NKwC7qcHoSQDt1LuoSQx240b6dhBmlzTsAuaM80rAGaM0hiZqrqXzWSp%2FeuIl%2FwDHqNALTNkknrTCaBFLVbc3ulywj7y%2FvE%2BorjsnAo0CJE5qLNCH5hn1pOlHKPUAaXdRZbBrcTfRuo5RD85FOShCGyEbvmFRMV%2FhFAH%2F2QAA'
#rawdatas = (rawdata+ r'=' * (-len(rawdata) % 4))

""" 
# Encode from an image
im = pl.open('sayac.jpeg')
val = io.BytesIO()
im.save(val, 'JPEG')
with open('rawdata.txt', 'wb') as f:
  f.write(base64.b64encode(val.getvalue()))
 """
""" # Your code
file = open('rawdata2.txt', 'rb')
encoded_data = file.read()
file.close() # reading bytes raw data 

b = base64.b64decode(encoded_data+ b'=' * (-len(rawdata) % 4) )
val = io.BytesIO(b)
img = pl.open(fp=val, mode='r') # ERROR IS HERE
img.save("test27.jpeg")



 """

""" with open("new_image.jpeg", "wb") as new_file:
    new_file.write(base64.decodebytes(encoded_data))
 """
""" img = pl.open(io.BytesIO(base64.decodebytes(bytes(rawdatas,encoding= "utf-8"))))
img.save('my-image.jpeg')
 """







""" 
#decode base64 string data
decoded_data=base64.b64decode((encoded_data))
#write the decoded data back to original format in  file
img_file = open('imageee.jpeg', 'wb')
img_file.write(decoded_data)
img_file.close()

imagege = cv.imread('imageee.jpeg')
cv.imshow('image',imagege)
 """
# print(decoded_data)
# img_file = open('image.jpeg', 'wb')
# img_file.write(decoded_data)
# out = io.BytesIO(decoded_data)
# out.seek(0)
# imageee = pl.open(out)
# imageee.save('images.jpeg')
# img_file.close()
""" 
im_arr = np.frombuffer(decoded_data, dtype=np.uint8)
img = cv.imdecode(im_arr, flags=cv.IMREAD_COLOR)
cv.imshow("image", img)
cv.waitKey(0)
 """
""" imagedata = base64.b64decode(rawdata.encode('utf-8') + b'=' * (-len(rawdata) % 4))
val = base64.decodebytes(imagedata)
resim = pl.open(io.BytesIO(val))
resim.show()
filename = "test.jpeg"
filepath = r"C:\\Users\\hasan\\Desktop\\Sayac_Okuyucu\\sayac_okuyucu\\ "
fileee = filepath + filename
resim.save(fileee,'jpeg') """

""" 
with open("imToooSave.jpeg", "wb") as fh:
  fh.write(base64.b64decode(rawdata.encode('utf-8')+ b'=' * (-len(rawdata) % 4)))
     """


#with open("imageTooSave.png", "wb") as fh:
 #   fh.write(base64.decodebytes(rawdata.encode('utf-8') + b'=' * (-len(rawdata) % 4)))



