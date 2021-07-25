import os
import glob
import picamera
import RPi.GPIO as GPIO
import time
import smtplib
from time import sleep
# from playsound import playsound
# from soundplayer import SoundPlayer
import os

GPIO.setwarnings(False)
from datetime import datetime
import pyrebase

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

firebaseConfig = {
    'apiKey': "AIzaSyASqDNha_yw-pMvGzmUV4vYQgbo51Ra194",
    'authDomain': "smart-doorbell-173f4.firebaseapp.com",
    'databaseURL': "https://smart-doorbell-173f4-default-rtdb.firebaseio.com",
    'projectId': "smart-doorbell-173f4",
    'storageBucket': "smart-doorbell-173f4.appspot.com",
    'messagingSenderId': "490462304492",
    'appId': "1:490462304492:web:5c21161e443bbd1ce82dc9",
    'measurementId': "G-VYFBC19GGF"

}

firebase = pyrebase.initialize_app(firebaseConfig)

storage = firebase.storage()

sender = 'psai4231@gmail.com'
password = 'Proz@143'
receiver = 'psai4200@gmail.com'

DIR = './Desktop/'
prefix = 'image'
trig = 12
echo = 10

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# GPIO.setup(15, GPIO.IN)
GPIO.setup(40, GPIO.IN)
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(38, GPIO.OUT)

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(16, GPIO.OUT)


def send_mail(filename):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'Visitor'

    body = 'Find the picture in attachments'
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename= %s' % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()


def capture_img():
    print('Capturing')
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    files = sorted(glob.glob(os.path.join(DIR, prefix + '[0-9][0-9][0-9].jpg')))
    count = 0

    if len(files) > 0:
        count = int(files[-1][-7:-4]) + 1
    filename = os.path.join(DIR, prefix + '%03d.jpg' % count)
    with picamera.PiCamera() as camera:
        pic = camera.capture(filename)
    send_mail(filename)


while True:
    GPIO.output(trig, True)
    sleep(0.00001)
    GPIO.output(trig, False)
    while GPIO.input(echo) == 0:
        pulse_start = time.time()
    while GPIO.input(echo) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 34000) / 2
    dist = round(distance, 2)
    sleep(.5)
    if dist < 40:
        print('alarm ringing')
        # playsound('/home/pi/Desktop/doorbell-ring.mp3')
        # p = SoundPlayer("/home/pi/Desktop/doorbell-ring.mp3 ",1)
        # p.play(0.2)
        os.system('mpg321 /home/pi/Desktop/doorbell-ring.mp3 &')
        GPIO.output(16, True)
        sleep(.5)
        GPIO.output(16, False)
    A = GPIO.input(40)
    if A == 0:
        print("Waiting")
        sleep(0.4)
    elif A == 1:
        GPIO.output(38, True)
        print("Captured->Sending")
        GPIO.output(38, True)
        sleep(3)
        capture_img()
        GPIO.output(38, False)
    try:
        if A == 1:
            print("pushed")
            now = datetime.now()
            dt = now.strftime("%d%m%Y%H:%M:%S")
            name = dt + ".jpg"
            with picamera.PiCamera() as camera:
                camera.capture(name)
            print(name + " saved")
            storage.child(name).put(name)
            print("Image sent")
            os.remove(name)
            print("File Removed")
            sleep(2)
    except:
        camera.close()