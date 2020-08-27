import Adafruit_DHT
import RPi.GPIO as GPIO
import smbus
import time
import socket, json

# Define some constants from the datasheet

DEVICE     = 0x23 # Default device I2C address

POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value

# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13
# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10
# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20
# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_LOW_RES_MODE = 0x23

#bus = smbus.SMBus(0) # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1

GPIO.setmode(GPIO.BCM) # pin name set fallow board pin

sensor = Adafruit_DHT.DHT11

def convertToNumber(data):
    # Simple function to convert 2 bytes of data
    # into a decimal number. Optional parameter 'decimals'
    # will round to specified number of decimal places.
    result=(data[1] + (256 * data[0])) / 1.2
    return (result)

def readLight(addr=DEVICE):
    # Read data from I2C interface
    data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE_1)
    return convertToNumber(data)

def main():
    HOST = '127.0.0.1'
    PORT = 3105
    
    upload_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upload_client.connect((HOST, PORT))

    prev_t = 0
    prev_h = 0
    while True:
        h, t = Adafruit_DHT.read(sensor, 4)
        if h is not None and t is not None:
            prev_t = t
            prev_h = h
        lightLevel=readLight()
    # print("Light Level : " + format(lightLevel,'.2f') + " lx")

        cin = {'ctname': 'temp', 'con': str(prev_t)}
        msg = (json.dumps(cin) + '<EOF>')
        upload_client.sendall(msg.encode('utf-8'))

        cin = {'ctname': 'hum', 'con': str(prev_h)}
        msg = (json.dumps(cin) + '<EOF>')
        upload_client.sendall(msg.encode('utf-8'))

        cin = {'ctname': 'light', 'con': str(lightLevel)}
        msg = (json.dumps(cin) + '<EOF>')
        upload_client.sendall(msg.encode('utf-8'))

    # if h is not None and t is not None:

        print(prev_t,',', prev_h,',', lightLevel)

    #GPIO.cleanup()

if __name__=="__main__":
   main()
