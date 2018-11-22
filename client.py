import serial
import time
import aiohttp
import requests
import ast 
import datetime 
import RPi.GPIO as GPIO
import time
s = serial.Serial("/dev/tty.usbmodem144101")
s.baudrate = 115200
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

def time_checker():
    rdic = {}
    with open("sched.dict" , "r") as d:
        rdic = ast.literal_eval(d.read())
    tdic = rdic[str(datetime.date.today().isoweekday())]
    start = datetime.time(int(str(tdic["start"]).split('.')[0]),int(str(tdic["start"]).split('.')[1]),0)
    end = datetime.time(int(str(tdic["end"]).split('.')[0]),int(str(tdic["end"]).split('.')[1]),0)
    if start <= end :
        return start <= datetime.datetime.now().time() <= end
    else:
        return start <= datetime.datetime.now().time() or datetime.datetime.now().time() <= end
    
def get_price():
    with open("price.dict" , "r") as p:
        return ast.literal_eval(p)

def bid_push(card,price):
    r = requests.post("http://0.0.0.0:8080/bid_push",json={'cardid': str(card), 'bid': int(price)})
    return r.json()['result']

def get_cre(card):
    r = requests.post("http://0.0.0.0:8080/get_credit", json={'cardid': str(card)})
    return r.json()['point']

def credit():
    GPIO.output(7,GPIO.HIGH)
    time.sleep(50)
    GPIO.output(7,GPIO.LOW)
    time.sleep(5)


while 1:
    GPIO.output(7,GPIO.LOW)
    datain = s.readline()
    msg = datain.decode("ascii")
    msg = msg.replace(" ","").replace("\r\n","").replace("\n","")
    if msg.split("]")[0].replace("[","") == 'PUSH':
        try: 
            gotindex = msg.split("]")[1]
            if not gotindex == '':
                print("PUSH " + gotindex)
                result = ''
                if time_checker() == True :
                    result = bid_push(gotindex,get_price()["service"])
                else:
                    result = bid_push(gotindex,get_price()["normal"])
                if result == "ok" :
                    credit()
                else:
                    print("餘額不足")
        except Exception as e:
            pass
    else:
        try:
            print(msg.split("]")[0].replace("[",""))
            print(msg.split("]")[1])
            print("優惠時段:"+time_checker())
            print(get_cre(msg.split("]")[1]))
        except Exception as e:
            pass
