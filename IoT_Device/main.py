import paho.mqtt.client as mqtt
from ksoc_connection import *
import time
from ksoc_connection.logger import log, logging
from threading import Thread

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
# mqttc.on_message = on_message

mqttc.connect(broker, port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
t = Thread(target=mqttc.loop_forever)
# mqttc.loop_forever()

log.setLevel(logging.INFO)
if __name__ == '__main__':
    with KKTIntegration(KKTVComPortConnection(timeout=1)) as integration:
        integration.connectDevice()
        print(f'Chirp ID : {integration.getChipID()[1]}')
        read = integration.readHWRegister(0x50000530)
        print(f'read reg ({hex(0x50000504)}) : {read[0]} {hex(read[1])}')
        print(f'write reg ({hex(0x50000504)}) : {integration.writeHWRegister(0x50000504, 0x00000000)}')
        read = integration.readHWRegister(0x50000504)
        print(f'read reg ({hex(0x50000504)}) : {read[0]} {hex(read[1])}')
        # integration.setPowerSavingMode(2)
        # print(f'power saving mode: {integration.getPowerSavingMode()[1]}')
        integration.switchCollectionOfMultiResults(actions=0b1, read_interrupt=0, clear_interrupt=0, raw_size=(8192+2)*2, ch_of_RBank=1, reg_address=[])
        s = time.time_ns()
        t.start()
        for i in range(20):
            print(f'=================={i}==================')
            data = integration.getMultiResults()[1]
            print(f'getMultiResults : {data[0][:4].hex(" ")}')
            mqttc.publish(topic, data[0][0:2])
            print(f'getMultiResults time : {(time.time_ns()-s)/1000000} ms')
            s = time.time_ns()


        print(integration.switchCollectionOfMultiResults(actions=0b0, read_interrupt=0, clear_interrupt=0, raw_size=(8192 + 2) * 2,
                                                  ch_of_RBank=1, reg_address=[]))