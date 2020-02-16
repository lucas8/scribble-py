import cv2
import numpy as np


def mouseRGB(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        colorsB = frame[y,x,0]
        colorsG = frame[y,x,1]
        colorsR = frame[y,x,2]
        colors = frame[y,x]
        print("H: ",colorsR)
        print("S: ",colorsG)
        print("V: ",colorsB)
        #print("BRG Format: ",colors)
        print("Coordinates of pixel: X: ",x,"Y: ",y)


cv2.namedWindow('mouseRGB')
cv2.setMouseCallback('mouseRGB',mouseRGB)

#capture = cv2.VideoCapture(0)

# while(True):
#
#     ret, frame = capture.read()
frame = cv2.imread("/Users/2020shatgiskessell/Downloads/IMG_1606.JPG")
frame = cv2.resize(frame,(500,500))
frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
cv2.imshow('mouseRGB', frame)
cv2.waitKey(0)

# capture.release()
# cv2.destroyAllWindows()
