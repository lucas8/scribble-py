import cv2
import numpy as np
from sklearn.cluster import KMeans
import pytesseract
import string
from spellchecker import SpellChecker
import json

from handwriting_ocr import run_ocr


#mvp_sketch = cv2.imread("/Users/2020shatgiskessell/Downloads/IMG_1607.JPG")
#mvp_sketch = cv2.resize(mvp_sketch,(900,1440))

spell = SpellChecker()

def get_component(component_name,color_range_l,color_range_u,hsv_img,img):
    buttons_arr = []

    # lower_green = np.array([36, 25, 25])
    # upper_green= np.array([100, 255, 255])
    buttons = cv2.inRange(hsv_img,color_range_l,color_range_u)
    kernel = np.ones((5,5),np.uint8)
    closing = cv2.morphologyEx(buttons, cv2.MORPH_CLOSE, kernel)
    #get contours
    im2, contours, hierarchy = cv2.findContours(buttons, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #remove noise contours
    button_contours = []
    for i in range(len(contours)):
        cnt = contours[i]
        h = hierarchy[0,i,3]
        #print (cv2.contourArea(cnt))
        if cv2.contourArea(cnt) > 1000 and h == -1:
            button_contours.append(cnt)

    for button_cnt in button_contours:
        #get text box roi
        upper_left_cords,bottom_right_cords = get_bounding_cords (button_cnt)
        x1,y1 = upper_left_cords
        x2,y2 = bottom_right_cords
        button = img[y1-2:y2+2, x1-2:x2+2]
        # cv2.imshow("button",button)
        # cv2.waitKey(0)
        #run run_ocr
        text = pytesseract.image_to_string(button)
        #postprocess text
        text = text.translate(str.maketrans('', '', string.punctuation))
        found_text = False
        for char in text:
            if not found_text and char == " ":
                text = text.replace(char,"")
            if char != " ":
                found_text = True
        text = spell.correction(text)
        button_dict = {"type":component_name, "ulx":int(x1),"uly":int(y1),"lrx":int(x2),"lry":int(y2),"text":text}
        buttons_arr.append(button_dict)

    return buttons_arr

def get_text_box(hsv_img,img):
    lower_brown = np.array([0, 0, 40])
    upper_brown = np.array([200, 35, 100])
    text_box = cv2.inRange(hsv_img,lower_brown,upper_brown)
    kernel = np.ones((5,5),np.uint8)
    closing = cv2.morphologyEx(text_box, cv2.MORPH_CLOSE, kernel)
    #get contours
    im2, contours, hierarchy = cv2.findContours(text_box, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    upper_left_cords,bottom_right_cords = get_bounding_cords (contours)
    #get text box roi
    x1,y1 = upper_left_cords
    x2,y2 = bottom_right_cords
    text_box = img[y1:y2, x1:x2]
    #run run_ocr
    text = pytesseract.image_to_string(text_box)
    #postprocess text
    text = text.translate(str.maketrans('', '', string.punctuation))
    found_text = False
    for char in text:
        if not found_text and char == " ":
            text = text.replace(char,"")
        if char != " ":
            found_text = True
    text = spell.correction(text)

    return upper_left_cords, bottom_right_cords,text

def get_bounding_cords (cnt):
    upper_left_cords = (1000,1000)
    bottom_right_cords = (0,0)
    #get bounding box cords
    #for cnt in contours:
    cnt = cnt.reshape(len(cnt),2)
    #print (cnt)
    for cords in cnt:
        x = cords[0]
        y = cords[1]
        x_min,y_min = upper_left_cords
        x_max,y_max = bottom_right_cords
        if x + y < x_min + y_min:
            upper_left_cords = (x,y)
        elif x + y > x_max + y_max:
            bottom_right_cords = (x,y)

    return upper_left_cords,bottom_right_cords

def component_detector(img):
    img = cv2.imread(img)
    img = cv2.resize(img,(900,500))

    pages = []

    img_blurred = cv2.GaussianBlur(img,(5,5),0)
    hsv_img = cv2.cvtColor(img_blurred, cv2.COLOR_BGR2HSV)

    #isolate evverything that is not orange
    lower_orange = np.array([0, 110, 200])
    upper_orange = np.array([8, 180, 250])
    page_outline = cv2.inRange(hsv_img,lower_orange,upper_orange)

    kernel = np.ones((5,5),np.uint8)
    closing = cv2.morphologyEx(page_outline, cv2.MORPH_CLOSE, kernel)
    #get contours
    im2, contours, hierarchy = cv2.findContours(page_outline, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #remove noise contours and get seperate pages
    pages_cnts = []
    for i in range(len(contours)):
        cnt = contours[i]
        h = hierarchy[0,i,3]
        if cv2.contourArea(cnt) > 10 and h == -1:
            pages_cnts.append(cnt)

    for page_cnt in pages_cnts:
        page_components = []
        #get the page from page outline
        #img = cv2.drawContours(img, [page_cnt], 0, (0,255,0), 3)
        upper_left_cords,bottom_right_cords = get_bounding_cords(page_cnt)
        x1,y1 = upper_left_cords
        x2,y2 = bottom_right_cords
        page = img[y1:y2, x1:x2]

        hsv_img = cv2.cvtColor(page, cv2.COLOR_BGR2HSV)
        buttons = get_component("button",np.array([36, 25, 25]),np.array([100, 255, 255]),hsv_img,page)
        texts = get_component("text",np.array([0, 0, 40]),np.array([200, 35, 100]),hsv_img,page)

        page_components.extend(buttons)
        page_components.extend(texts)

        # page_components = json.dumps(page_components)
        pages.append(page_components)
    #pages = json.dumps(pages)
    return pages

# pages = component_detector("/Users/2020shatgiskessell/Downloads/IMG_1607.JPG")
# print (pages)
