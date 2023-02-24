from machine import ADC, Pin
import utime

soil = ADC(Pin(28))

min_moisture=20000
max_moisture=44000

readDelay = 1.0

while True:
    moisture = (max_moisture-soil.read_u16())*100/(max_moisture-min_moisture)
    print("moisture: " + "%.2f" % moisture +"% (adc: "+str(soil.read_u16())+")")
    utime.sleep(readDelay)