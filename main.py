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
picwidth = 640
picheight = 480
camera.resolution = (picwidth, picheight)
camera.start_preview()
sleep(2)

ledpin = 18 #12 BOARD or 18 BCM
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledpin, GPIO.OUT)
GPIO.output(ledpin, GPIO.LOW)

#display variables
pygame.init()
pygame.font.init()
boxfont = pygame.font.SysFont('Arial', 30)
picfont = pygame.font.SysFont('Arial', 18)
display_width = 1280 + 50   # 2 x 640 + 50 = 1330
display_height = 960 + 50   # 2 x 480 + 50 = 1010
screen = pygame.display.set_mode((display_width,display_height))
#pygame.display.set_caption('AV cleanliness super smart mega system 3000')
black = (39,42,44)
white = (255,255,255)
red = (255,135,135)
green = (194,255,192)
yellow = (246,198,120)
crossthickness = 50
boxwidth = 250
boxheight = 150
borderwidth = 7
screen.fill(black)
pygame.display.update()

#functions
#def doorbutton():
    # if #GPIO == HIGH:
    #     return True
    # else:
    #     return False
def takeRefPic():
    GPIO.output(ledpin, GPIO.HIGH)
    camera.capture("images/refpic.jpg")
    pic = cv2.imread("images/refpic.jpg")
    GPIO.output(ledpin, GPIO.LOW)
    return pic
def takeNewPic():
    GPIO.output(ledpin, GPIO.HIGH)
    sleep(1)
    camera.capture("images/newpic.jpg")
    pic = cv2.imread("images/newpic.jpg")
    sleep(1)
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
    if objdetect:
    	object_detection.detect(newpic)
    
    if score<scorelimit:
        return True
    else:
        return False

def updateDisplay(stat):
    if stat: #update display variables
	statustext = ["DIFFERENCE","DETECTED"]
        statuscolor = red
    else:
        statustext = "LOOKS GOOD"
        statuscolor = green
    screen.fill(statuscolor)

    #show images
    refpicPygame = pygame.image.load("images/refpic.jpg")
    showImage(refpicPygame,0,0)
    newpicPygame = pygame.image.load("images/newpic.jpg")
    showImage(newpicPygame,picwidth+crossthickness,0)
    diffpicPygame = pygame.image.load("images/diffpic.jpg")
    showImage(diffpicPygame,0,picheight+crossthickness)
    threshpicPygame = pygame.image.load("images/threshpic.jpg")
    showImage(threshpicPygame,picwidth+crossthickness,picheight+crossthickness)

    #rectangles around pictures
    pygame.draw.rect(screen,yellow,(0+borderwidth/2,0+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#up left
    pygame.draw.rect(screen,yellow,(0,0,picwidth/5,picheight/12),0)
    refpictext = picfont.render("REFERENCE", False, black)
    refpictextwidth = refpictext.get_width()
    screen.blit(refpictext, (picwidth/5/2-refpictextwidth/2,borderwidth+5))

    pygame.draw.rect(screen,yellow,(picwidth+crossthickness+borderwidth/2,0+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#up right
    pygame.draw.rect(screen,yellow,(picwidth*2+crossthickness-picwidth/5,0,picwidth/5,picheight/12),0)
    newpictext = picfont.render("NEW", False, black)
    newpictextwidth = newpictext.get_width()
    screen.blit(newpictext, (picwidth*2+crossthickness-picwidth/10-newpictextwidth/2,borderwidth+5))

    pygame.draw.rect(screen,yellow,(0+borderwidth/2,picheight+crossthickness+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#down left
    pygame.draw.rect(screen,yellow,(0,picheight+crossthickness,picwidth/5,picheight/12),0)
    diffpictext = picfont.render("DIFFERENCE", False, black)
    diffpictextwidth = diffpictext.get_width()
    screen.blit(diffpictext, (picwidth/5/2-diffpictextwidth/2,picheight+crossthickness+borderwidth+5))

    pygame.draw.rect(screen,yellow,(picwidth+crossthickness+borderwidth/2,picheight+crossthickness+borderwidth/2,picwidth-borderwidth/2,picheight-borderwidth/2),borderwidth)	#down right
    pygame.draw.rect(screen,yellow,(picwidth*2+crossthickness-picwidth/5,picheight+crossthickness,picwidth/5,picheight/12),0)
    threshpictext = picfont.render("BINARY", False, black)
    threshpictextwidth = threshpictext.get_width()
    screen.blit(threshpictext, (picwidth*2+crossthickness-picwidth/10-threshpictextwidth/2,picheight+crossthickness+borderwidth+5))

    #box in the middle
    pygame.draw.rect(screen,statuscolor,(picwidth+crossthickness/2-boxwidth/2,picheight+crossthickness/2-boxheight/2,boxwidth,boxheight),0)
    pygame.draw.rect(screen,yellow,(picwidth+crossthickness/2-boxwidth/2,picheight+crossthickness/2-boxheight/2,boxwidth,boxheight),5)

    #show status
    if status==True:
    	loc = 0
    	for i in range(len(statustext)):
    		boxtext = boxfont.render(statustext[i], False, black)
    		boxtextwidth = boxtext.get_width()
    		screen.blit(boxtext, (picwidth+crossthickness/2-boxtextwidth/2,picheight+crossthickness/2-boxheight/2.5+loc))
		loc+=40
    else:
    	boxtext = boxfont.render(statustext, False, black)
    	boxtextwidth = boxtext.get_width()
    	screen.blit(boxtext, (picwidth+crossthickness/2-boxtextwidth/2,picheight+crossthickness/2-boxheight/2.5))
    scoretext = boxfont.render("SSIM = " + str("{0:.3f}".format(score)), False, black)
    scoretextwidth = scoretext.get_width()
    
    screen.blit(scoretext, (picwidth+crossthickness/2-scoretextwidth/2,picheight+crossthickness))

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
                pygame.quit()
                quit()


# When everything is done, release the capture
camera.release()
