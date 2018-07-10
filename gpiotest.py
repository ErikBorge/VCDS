import RPi.GPIO as GPIO
from time import sleep

ledpin = 18 #12 BOARD or 18 BCM
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledpin, GPIO.OUT)

GPIO.output(ledpin, GPIO.LOW)
sleep(1)
GPIO.output(ledpin, GPIO.HIGH)
sleep(1)
GPIO.output(ledpin, GPIO.LOW)
sleep(1)
GPIO.output(ledpin, GPIO.HIGH)
sleep(1)
GPIO.output(ledpin, GPIO.LOW)

GPIO.cleanup()