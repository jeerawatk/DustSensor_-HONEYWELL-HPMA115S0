import time
import datetime
import pymongo
import RPi.GPIO as GPIO
import serial, time
from time import localtime, strftime
import sqlite3
from TM1637 import FourDigit
from time import sleep

#port = serial.Serial("/dev/ttyS0", baudrate=9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=0.1)
port = serial.Serial('/dev/ttyAMA0',9600)
#port = serial.Serial('/dev/ttyS0',9600)
#sqlite_file = 'dust_db.sqlite'

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
min = 15
delay = min*60
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["dustData"]
mycol = mydb["data"]


def main():
    #db = sqlite3.connect(sqlite_file)
    #cursor = db.cursor()
    #cursor.execute('''CREATE TABLE IF NOT EXISTS dust_table (id INTEGER PRIMARY KEY AUTOINCREMENT, data TIMESTAMP, pm25 REAL, pm10 REAL)''')
    GPIO.output(12, GPIO.HIGH) # Turn on
    #time.sleep(10)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    if port.isOpen():
        port.close()
        time.sleep(0.5)
    port.open()
    time.sleep(0.1)
    data = port.read(32);
    time.sleep(0.1)
    try:
        if port.isOpen():
            port.close()
        if ord(data[0]) == 66 and ord(data[1]) == 77:
            suma = 0
            for a in range(30):
                suma += ord(data[a])
            if suma == ord(data[30])*256+ord(data[31]):
                PM25 = int(ord(data[6])*256+ord(data[7]))
                PM10 = int((ord(data[8])*256+ord(data[9]))/0.75)
                print 'PM2.5: %d ug/m3' % round(PM25)
                print 'PM10: %d ug/m3' % round(PM10)
                data_pm25 = int(round(PM25))
                data_pm10 = int(round(PM10))
                if data_pm25 > 0 :
                    if data_pm25 < 100:
                        data_pm25 = str(data_pm25)+' '
                    d = FourDigit(dio=38,clk=40,lum=1)
                    d.erase()
                    d.setLuminosity(4)
                    d.show(str(data_pm25))
                    time.sleep(1)
                    data = { "pm25": str(data_pm25), "pm10": str(data_pm10), "timestamp": str(st) }
                    x = mycol.insert_one(data)
                    GPIO.output(12, GPIO.LOW) # Turn off
                    time.sleep(delay-0.05)
                #datetime = strftime("%Y-%m-%d %H:%M:%S", localtime())
                #cursor.execute('''INSERT INTO dust_table(data, pm25, pm10) VALUES(?,?,?)''', (datetime, PM25, PM10))
            #else:
                #print "no data"
        #else:
            #print "no data"
    except Exception as ex:
        print ex
        if port.isOpen():
            port.close()
        time.sleep(0.5)
        #if port.isOpen():
        #    port.close()
    finally:
        #db.commit()
        #db.close()
        if port.isOpen():
            port.close()
        time.sleep(0.5)
        #if port.isOpen():
        #    port.close()
        #print "OFF"
    
    return

if __name__=="__main__":
    #for a in range(350):
    while True:
        #if port.isOpen():
        #    port.close()
        main()
        #if port.isOpen():
            #port.close()
        time.sleep(0.2)
