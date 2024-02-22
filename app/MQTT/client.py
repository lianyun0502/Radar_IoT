import paho.mqtt.client as mqtt
import time

broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "IoT_Device"
client_id = f'python-mqtt-124'
username = ""
password = ""


s = time.time_ns()
def on_connect(client:mqtt.Client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(topic="$SYS/#")

def on_message(client:mqtt.Client, userdata, msg:mqtt.MQTTMessage):
    global s
    if msg.topic == topic:
        print(msg.topic)
        # print(str(msg.payload))
        print(f'getMultiResults time : {(time.time_ns()-s)/1000000} ms')
        s = time.time_ns()
     

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(broker, port, 60)
mqttc.subscribe(topic)

mqttc.loop_start()
