import paho.mqtt.client as mqtt

broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "IoT_Device"
client_id = f'python-mqtt-123'
username = ""
password = ""

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client:mqtt.Client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client:mqtt.Client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(broker, port, 60)
mqttc.subscribe(topic)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()
