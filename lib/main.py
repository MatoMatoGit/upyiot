from lib import NetCon
#from lib import Led
#from lib import MicroDNSSrv
#from lib import LedControlWebServer
from lib import Sensor
#from lib import AdcADS101x
from lib import DummySensor
from lib import umqtt

# try:
#     import usocket as socket
# except:
#     import socket
import time
import machine
import ubinascii
import uasyncio
import ujson
import os
#from lib import SystemTime
#from SystemTime import SystemTime

f = open('config.json', 'r')
cfg = ujson.load(f)
print('\nLoaded sensor config file:\n')
print(cfg)

try:
    os.mkdir("sensors")
except OSError:
    print("Directory sensors already exists")
    pass

# led_blue = Led(2, True)
# led_red = Led(0, False)

#AdcCh1 = Adc(1)
TempSensorSamples = [20, 21, 25, 30, 35, 35, 20, 12, 10, 40]
DummyTempSensor = DummySensor.DummySensor(TempSensorSamples)
TempSensor = Sensor.Sensor("/sensors", "temp", 30, DummyTempSensor)

device_id = cfg["ap"]["ssid_prefix"] + str(ubinascii.hexlify(machine.unique_id()).decode('utf-8'))

con = NetCon.NetCon("/", (device_id + cfg["ap"]["ssid_suffix"], cfg["ap"]["pw"], cfg["ap"]["ip"]), True)

# led.On()
# for i in range(led.PwmDutyMinGet(), led.PwmDutyMaxGet(), 1):
#     led.Intensity(led.PwmDutyMaxGet() - i)
#     time.sleep_ms(10)
# led.On()
global MqttClient
#global TimeSvc

#con.StationSettingsReset()
if con.StationSettingsAreSet() is False:
    con.StationSettingsStore("WuiFui", "89NZ6DWRNPFD!")
if con.StationStart() is True:
#    global TimeSvc
    global MqttClient 
    
#    TimeSvc = SystemTime.InstanceGet()
    
    MqttClient = umqtt.MQTTClient(device_id, '192.168.2.10', 1883)
    print("[MQTT] Connecting to server.")
    connected = False
    while connected is False:
        try:
            MqttClient.connect()
            connected = True
            print("[MQTT] Connected.")
        except OSError:
            print("[MQTT] Failed to connect to server.")
            time.sleep(5)
            continue
    
#dns = MicroDNSSrv.Create({ '*' : '192.168.0.254' })
#con.AccessPointStart()
#dns.Start()

# led_srv = LedControlWebServer.LedControlWebServer(2)
# 
# while True:
#     led_srv.RunLoop()
# 
# async def LedSrvTask():
#     led_srv.RunLoop()
#     await uasyncio.sleep(1)

# 
# def web_page():
#     if led_blue.State() == 0:
#         gpio_state="ON"
#     else:
#         gpio_state="OFF"
#      
#     html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
#     <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
#     h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
#     border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
#     .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
#     <p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
#     <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>
#     <form>Netwerk naam:<br><input type="text" name="network"><br>Wachtwoord:<br><input type="text" name="password"></form> 
#     </strong></p><p><a href="/?led=on"><button class="button">Opslaan</button></a></p></body></html>"""
#     return html

# async def web_server():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind(('', 80))
#     s.listen(1)
#  
#     while True:
#          
#         conn, addr = s.accept()
#         #ss = ussl.wrap_socket(s, server_side=True, key=key, cert=cert)
#         #print('Secure socket: {}'.format(ss))
#         print('Got a connection from %s' % str(addr))
#         request = conn.recv(1024)
#          
#         request = str(request)
#         print('Content = %s' % request)
#         led_on = request.find('/?led=on')
#         led_off = request.find('/?led=off')
#          
#         if led_on == 6:
#             print('LED ON')
#             led_blue.Off()
#         if led_off == 6:
#             print('LED OFF')
#             led_blue.On()
#         response = web_page()
#         conn.send('HTTP/1.1 200 OK\n')
#         conn.send('Content-Type: text/html\n')
#         conn.send('Connection: close\n\n')
#         conn.sendall(response)
#         conn.close()
#          
#         await uasyncio.sleep(1)


# async def Blink():
#     while True:
#         led_red.Toggle()
#         await uasyncio.sleep(1)
        

async def ReadSensor():
    while True:
        print("Temperature: {} C".format(TempSensor.Read()))
        await uasyncio.sleep(10)
    
async def PublishSensor():
    global MqttClient
    while True:
        sample_buf = []
        num_samples = TempSensor.SamplesGet(sample_buf)
        temp_dict = {}
        temp_dict["sensor_type"] = "temp"
        temp_dict["n"] = num_samples
        temp_dict["samples"] = sample_buf
        dict_json = ujson.dumps(temp_dict)
        print(dict_json)
        print("Publishing temperature sensor values: {}".format(dict_json))
        MqttClient.publish("/sensor/temp", dict_json)
        TempSensor.SamplesClear()
        await uasyncio.sleep(60)


if __name__ == '__main__':
    loop = uasyncio.get_event_loop()
    #loop.create_task(web_server())
    #loop.create_task(Blink())
    #loop.create_task(SystemTime.SystemTimeService())
    loop.create_task(ReadSensor())
    loop.create_task(PublishSensor())
    loop.run_forever()


