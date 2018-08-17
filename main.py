#Autonomous car image comparison system for cleanliness, logic

import pygame
import cv2 as cv2
import numpy as np
from skimage.measure import compare_ssim
import argparse
import imutils
import RPi.GPIO as GPIO
import sys
from picamera import PiCamera
from time import sleep
import contours
import object_detection

objdetect = False
if objdetect:
	object_detection.initialize()

#variables
difference = False
status = False
takepic = True
newpic, refpic, diffpic, threshpic = None, None, None, None
score = 0
scorelimit = 0.98
threshvariable = 255
#diffpic, threshpic = None, None
camera = PiCamera()
picwidth = 576
picheight = 432
camera.resolution = (picwidth, picheight)
#camera.start_preview()
sleep(2)

ledpin = 18 #12 BOARD or 18 BCM
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledpin, GPIO.OUT)
GPIO.output(ledpin, GPIO.LOW)

#display variables
pygame.init()
pygame.font.init()
boxfont = pygame.font.Font('/home/pi/.fonts/OpenSans-Light.ttf', 20)
boxfontbold = pygame.font.Font('/home/pi/.fonts/OpenSans-Bold.ttf', 20)
picfont = pygame.font.Font('/home/pi/.fonts/OpenSans-Light.ttf', 18)
headerfont = pygame.font.Font('/home/pi/.fonts/OpenSans-Bold.ttf', 30)
display_width = 1920 #1280 + 50    # 2 x 640 + 50 = 1330
display_height = 1080 #960 + 50   # 2 x 480 + 50 = 1010
screen = pygame.display.set_mode((display_width,display_height),pygame.FULLSCREEN)
#pygame.display.set_caption('AV cleanliness super smart mega system 3000')
black = (39,42,44)
white = (255,255,255)
red = (248,203,202) #(255,135,135)
darkred = (204,51,51)
green = (225,240,223) #(194,255,192)
darkgreen = (51,153,51)
yellow = (246,198,120)
crossthickness = 30
boxwidth = 220
boxheight = 80
borderwidth = 7
x1=display_width/2-crossthickness/2-picwidth
y1=display_height-picheight*2-crossthickness-40
x2=display_width/2+crossthickness/2
y2=display_height-picheight-40
middlex=x2-crossthickness/2
middley=y2-crossthickness/2
screen.fill(black)
DDLogo = pygame.image.load("DDLogo.png")
DDLogo = pygame.transform.scale(DDLogo,(138,63))
headertext = headerfont.render("VEHICLE CLEANLINESS DETECTION SYSTEM", False, black)
headertextwidth = headertext.get_width()
pygame.display.update()

#functions
#def doorbutton():
    # if #GPIO == HIGH:
    #     return True
    # else:
    #     return False
def takeRefPic():
    GPIO.output(ledpin, GPIO.HIGH)
    sleep(0.5)
    camera.capture("images/refpic.jpg")
    pic = cv2.imread("images/refpic.jpg")
    sleep(0.5)
    GPIO.output(ledpin, GPIO.LOW)
    return pic
def takeNewPic():
    GPIO.output(ledpin, GPIO.HIGH)
    sleep(0.5)
    camera.capture("images/newpic.jpg")
    pic = cv2.imread("images/newpic.jpg")
    sleep(0.5)
    GPIO.output(ledpin, GPIO.LOW)
    return pic
def checkDifference(ref, new):
    #global refpic, newpic, diffpic, threshpic, score, scorelimit
    global diffpic, threshpic, score, scorelimit
    diffpic, threshpic = None, None

    refgray = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    refgray = cv2.GaussianBlur(refgray,(5,5),0)
    newgray = cv2.cvtColor(new, cv2.COLOR_BGR2GRAY)
    newgray = cv2.GaussianBlur(newgray,(5,5),0)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    #(score, diffpic) = compare_ssim(refgray, newgray, full=True)
    (score, diffpic) = compare_ssim(refgray, newgray, gaussian_weights=True, full=True)
    diffpic = (diffpic * 255).astype("uint8")

    print("SSIM: {}".format(score))
    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    threshpic = cv2.threshold(diffpic, threshvariable, 255,
    	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    #threshpic = cv2.adaptiveThreshold(diffpic,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
    #        cv2.THRESH_BINARY_INV,11,20)
    hierarchy = None
    _ , cnts, hierarchy = cv2.findContours(threshpic.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    threshpic = cv2.threshold(diffpic, threshvariable, 255,
    	cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]	#just set it back to not inverted
    #cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    # loop over the contours
    if score<scorelimit:
	    #for c in cnts:
	    for i in range(len(cnts)):
	    	# compute the bounding box of the contour and then draw the
	       	# bounding box on both input images to represent where the two
	       	# images differ
		if hierarchy[0,i,3] == -1:
			(x, y, w, h) = cv2.boundingRect(cnts[i])
	       		#cv2.rectangle(ref, (x, y), (x + w, y + h), (0, 0, 255), 2)
	       		cv2.rectangle(new, (x, y), (x + w, y + h), (0, 0, 255), 2)
    
    cv2.imwrite("images/threshpic.jpg", threshpic)
    cv2.imwrite("images/diffpic.jpg", diffpic)
    cv2.imwrite("images/newpic.jpg", newpic)
    #cv2.imwrite("images/refpic.jpg", refpic)
    
    if objdetect and score<scorelimit:
    	object_detection.detect(newpic)

    if score<scorelimit:
        return True
    else:
        return False

def updateDisplay(stat):
    if stat: #update display variables
	statustext = "Difference detected"
        statuscolor = red
	fontcolor = darkred
    else:
        statustext = "Looks good"
        statuscolor = green
	fontcolor = darkgreen
    screen.fill(statuscolor)

    screen.blit(headertext, (middlex-headertextwidth/2,y1-110))
    showImage(DDLogo,20,display_height-90)
    #show images
    refpicPygame = pygame.image.load("images/refpic.jpg")
    showImage(refpicPygame,x1,y1)
    newpicPygame = pygame.image.load("images/newpic.jpg")
    showImage(newpicPygame,x2,y1)
    diffpicPygame = pygame.image.load("images/diffpic.jpg")
    showImage(diffpicPygame,x1,y2)
    threshpicPygame = pygame.image.load("images/threshpic.jpg")
    showImage(threshpicPygame,x2,y2)

    #rectangles around pictures
    #pygame.draw.rect(screen,yellow,(0+borderwidth/2,0+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#up left
    #pygame.draw.rect(screen,yellow,(0,0,picwidth/5,picheight/12),0)
    refpictext = picfont.render("reference", False, black)
    refpictextwidth = refpictext.get_width()
    screen.blit(refpictext, (x1,y1-31))

    #pygame.draw.rect(screen,yellow,(picwidth+crossthickness+borderwidth/2,0+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#up right
    #pygame.draw.rect(screen,yellow,(picwidth*2+crossthickness-picwidth/5,0,picwidth/5,picheight/12),0)
    newpictext = picfont.render("new", False, black)
    newpictextwidth = newpictext.get_width()
    screen.blit(newpictext, (x2,y1-31))

    #pygame.draw.rect(screen,yellow,(0+borderwidth/2,picheight+crossthickness+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#down left
    #pygame.draw.rect(screen,yellow,(0,picheight+crossthickness,picwidth/5,picheight/12),0)
    diffpictext = picfont.render("difference", False, black)
    diffpictextwidth = diffpictext.get_width()
    screen.blit(diffpictext, (x1,y2+picheight+3))

    #pygame.draw.rect(screen,yellow,(picwidth+crossthickness+borderwidth/2,picheight+crossthickness+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#down right
    #pygame.draw.rect(screen,yellow,(picwidth*2+crossthickness-picwidth/5,picheight+crossthickness,picwidth/5,picheight/12),0)
    threshpictext = picfont.render("binary", False, black)
    threshpictextwidth = threshpictext.get_width()
    screen.blit(threshpictext, (x2,y2+picheight+3))

    #box in the middle
    pygame.draw.rect(screen,statuscolor,(x2-crossthickness/2-boxwidth/2,y2-crossthickness/2-boxheight/2,boxwidth,boxheight),0)
    #pygame.draw.rect(screen,yellow,(picwidth+crossthickness/2-boxwidth/2,picheight+crossthickness/2-boxheight/2,boxwidth,boxheight),5)

    #show status
    #if status==True:
    	#loc = 0
    	#for i in range(len(statustext)):
    	#	boxtext = boxfontbold.render(statustext[i], False, fontcolor)
    	#	boxtextwidth = boxtext.get_width()
    	#	screen.blit(boxtext, (middlex-boxtextwidth/2,middley-boxheight/2.5+loc))
	#	loc+=40
    #else:
    boxtext = boxfontbold.render(statustext, False, fontcolor)
    boxtextwidth = boxtext.get_width()
    screen.blit(boxtext, (middlex-boxtextwidth/2,middley-boxheight/2.5+3))
    scoretext = boxfont.render("SSIM = " + str("{0:.3f}".format(score)), False, fontcolor)
    scoretextwidth = scoretext.get_width()
    
    screen.blit(scoretext, (middlex-scoretextwidth/2,y2-17))

    pygame.display.update()

def showImage(image,x,y):
    screen.blit(image, (x,y))

refpic = takeRefPic()    # take reference picture
newpic = refpic
updateDisplay(status)

while True:
    #if doorbutton():
    if takepic:
        if checkDifference(refpic, newpic): #compare pictures and check for difference
        	status = True
	else:
		status = False
        updateDisplay(status)
        takepic = False
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                refpic = takeRefPic()
		newpic = refpic
		takepic = True
            if event.key == pygame.K_n:
		newpic = takeNewPic()
                takepic = True
            if event.key == pygame.K_q:
		GPIO.cleanup()
		#camera.release()
                pygame.quit()
                quit()


# When everything is done, release the capture
camera.release()
