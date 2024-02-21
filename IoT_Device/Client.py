from ksoc_connection import *
from ksoc_connection.logger import log, logging
import paho.mqtt.client as mqtt 
from FiniteReceiveMachine import ReceiveEngine
import numpy as np
from utility import *

log.setLevel(logging.INFO)

class DeviceClient:
    def __init__(self, device_id:str, host:str, port:int):
        self.device_id = device_id

        self.integration = KKTIntegration(KKTVComPortConnection(timeout=1))
        self.integration.connectDevice()

        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

        self.mqttc.connect(host, port, 60)

        self.engine = ReceiveEngine(receiver=self.integration.getMultiResults, 
                                    handler=self.receive_data)
        
        self.post_proc = PostProcess()

    def __del__(self):
        self.mqttc.disconnect()
        self.integration.disconnectDevice()

    def run(self):
        self.mqttc.loop_start()

    def on_connect(self, client:mqtt.Client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe("$SYS/#")
        client.subscribe("$K{self.device_id}/read_register")
        client.subscribe("$K{self.device_id}/write_register")
        client.subscribe("$K{self.device_id}/launch")
        client.subscribe("$K{self.device_id}/stop")
        # client.subscribe("$K{self.device_id}/gesture")


    def on_message(self, client:mqtt.Client, userdata, msg:mqtt.MQTTMessage):

        if msg.topic == f"$K{self.device_id}/read_register":
            print(f"Read Register: {msg.payload}")
            self.read_register(msg.payload)
        elif msg.topic == f"$K{self.device_id}/write_register":
            print(f"Write Register: {msg.payload}")
            self.write_register(msg.payload[:4], msg.payload[4:])
        elif msg.topic == f"$K{self.device_id}/launch":
            print(f"Launch")
            self.launch()
        elif msg.topic == f"$K{self.device_id}/stop":
            print(f"Stop")
            self.stop()
        elif msg.topic == "$K{self.device_id}/gesture":
            print(f"Gesture: {msg.payload.decode()}")

        # print(msg.topic+" "+str(msg.payload))


    def receive_data(self, data:dict):
        # print(f'getMultiResults : {data[0][:4].hex(" ")}')
        exp = np.frombuffer(data[2], dtype='>u4')
        prediction = convertEXPVal(exp)
        # print(prediction)
        ges = self.post_proc.run(prediction)
        if ges != 0:
            print(ges)
            self.mqttc.publish("$K{self.device_id}/gesture", str(ges).encode())

    def read_register(self, address:bytes):
        address = int.from_bytes(address, "big")
        read = self.integration.readHWRegister(address)
        print(f'read reg ({hex(address)}) : {read[0]} {hex(read[1])}')

    def write_register(self, address:bytes, value:bytes):
        address = int.from_bytes(address, "big")
        value = int.from_bytes(value, "big")
        print(f'write reg ({hex(address)}) : {self.integration.writeHWRegister(address, value)}')

    def launch(self):
        res_addrs_dict = {
            'SoftmaxExponential': [addr for addr in range(0x50000508, 0x5000051C + 1, 4)],
            'Gestures': [addr for addr in range(0x50000580, 0x50000580 + 1, 4)]
        }
        self.integration.switchCollectionOfMultiResults(
                                                    actions=0b101, 
                                                   read_interrupt=0, 
                                                   clear_interrupt=0, 
                                                   raw_size=(8192+2)*2, 
                                                   ch_of_RBank=1, 
                                                   reg_address=res_addrs_dict['SoftmaxExponential'])
        self.engine.start()
        
    def stop(self):
       integration.switchCollectionOfMultiResults(actions=0b0, read_interrupt=0, clear_interrupt=0, raw_size=(8192 + 2) * 2,
                                                  ch_of_RBank=1, reg_address=[])
       
if __name__ == '__main__':
    device = DeviceClient("test", "mqtt.eclipseprojects.io", 1883)
    device.run()
    device.launch()
    key = input("Press Esc to quit...")
    device.stop()