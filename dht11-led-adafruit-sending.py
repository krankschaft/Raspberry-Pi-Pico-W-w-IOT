from machine import Pin
from time import sleep
from machine import Timer
from umqtt.simple import MQTTClient
import dht
import network
import time
import sys
import os

led = Pin("LED",Pin.OUT)
sensor = dht.DHT11(Pin(4))

WIFI_SSID     = 'Tertiary infotech'
WIFI_PASSWORD = 'Tertiary888'

random_num = int.from_bytes(os.urandom(3), 'little')
mqtt_client_id      = bytes('client_'+str(random_num), 'utf-8') # Just a random client ID

ADAFRUIT_IO_URL     = 'io.adafruit.com' 
ADAFRUIT_USERNAME   = 'krankschaft'
ADAFRUIT_IO_KEY     = 'aio_YCUQ68zYRkO7tj7oz9Fg0XAvRcTV'

TEMP_FEED_ID      = 'temperature'
HUM_FEED_ID       = 'humidity'
TOGGLE_FEED_ID    = 'LED'

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(WIFI_SSID,WIFI_PASSWORD)
    if not wifi.isconnected():
        print('Connecting..')
        timeout = 0
        while (not wifi.isconnected() and timeout < 5):
            print(5 - timeout)
            timeout = timeout + 1
            time.sleep(1) 
    if(wifi.isconnected()):
        print('Connected!')
        print('IP: ', wifi.ifconfig()[0])
    else:
        print('Not connected!')
        sys.exit()
      
connect_wifi() # Connecting to WiFi Router 

client = MQTTClient(client_id=mqtt_client_id, 
                    server=ADAFRUIT_IO_URL, 
                    user=ADAFRUIT_USERNAME, 
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)

def connect_mqtt():
    try:
        print("Connecting to MQTT ...")
        client.connect()
        print("Connected to MQTT")
    except Exception as e:
        print('Could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        sys.exit()

connect_mqtt()

toggle_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, TOGGLE_FEED_ID), 'utf-8') # format - ~/feeds/led
temp_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, TEMP_FEED_ID), 'utf-8') # format - ~/feeds/temp
hum_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, HUM_FEED_ID), 'utf-8') # format - ~/feeds/hum

def cb(topic, msg): # callback function
#     print('Received Data: Topic = {}, Msg = {}'.format(topic, msg))
    received_data = str(msg, 'utf-8') # Receiving data
    if topic == hum_feed:
        val = float(received_data)
        if val > 60.0:
            print("Too humid !!!\n")
            led.on()
        else:
            led.off()
        
client.set_callback(cb) # callback function
client.subscribe(toggle_feed) # subscribing to particular topic
client.subscribe(hum_feed) # subscribing to particular topic

def sens_data(data):
    sensor.measure()                    # Measuring 
    temp = sensor.temperature()         # getting Temp
    hum = sensor.humidity()
    try:
        client.publish(temp_feed,    
                  bytes(str(temp), 'utf-8'),   # Publishing Temp feed to adafruit.io
                  qos=0)
    
        client.publish(hum_feed,    
                  bytes(str(hum), 'utf-8'),   # Publishing Hum feed to adafruit.io
                  qos=0)
    except:
        connect_mqtt()
        return
    print("Temperature : ", str(temp))
    print("Humidity    : ", str(hum))
    print()
    
timer = Timer(-1)
timer.init(period=5000, mode=Timer.PERIODIC, callback = sens_data)

while True:
    try:
        client.wait_msg()
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        client.disconnect()
        sys.exit()