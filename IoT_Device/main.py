import paho.mqtt.client as mqtt
from ksoc_connection import *
import time
from ksoc_connection.logger import log, logging
from threading import Thread
import numpy as np

broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "IoT_Device"
client_id = f'python-mqtt-123'
username = ""
password = ""

def convertRegisterVal(data, start_bit=0, end_bit=4):
    data = np.right_shift(data,start_bit)
    mask = np.binary_repr(0xFFFFFFFF)[(start_bit-end_bit-1):]
    data = np.bitwise_and(data, int(mask,2))
    if type(data) == np.ndarray:
        data = data[0:1]
    return data

def unsign2sign(x, bit):
    '''
    return sign-extend value.

    Parameters:
            NA.
    Returns:
            (y) : a integer between 0~2^bit
    '''
    if x >= 0 and x < 2 ** (bit-1):
        y = x
    elif x >= 2 ** (bit-1) and x < 2**bit:
        y = x - 2**(bit)
    else:
        raise Exception('Value is out of bit range')
    return y

def convertEXPVal(data)->np.ndarray:
    val_line = ''
    for v in data:
        hex_val = hex(v).split('0x')[1].zfill(8)
        val_line = hex_val + val_line
    exponential = []
    for i in range(len(val_line), 0, -3):
        dec_val = int(val_line[i - 3:i], 16)
        dec_val = unsign2sign(dec_val, 12)
        exponential.append(dec_val)
    return np.asarray(exponential).astype('int16')

class PostProcess:
    def __init__(self, bg_id=0):
        self._bg_id = int(bg_id)
        self._current_ges = self._bg_id
        self._rising_ges = self._bg_id
        self._gesture_flag = False

    def run(self, preds:np.ndarray, lower_thd=0.5, upper_thd=0.6):
        """
        :param preds: A numpy array of model prediction with shape [classes, ]
        :param bg_id: Specific background ID
        :param lower_thd:
        :param upper_thd:
        :return: A tensor that has the same size as preds
        """
        if preds[self._bg_id] != preds.sum():
            preds[self._bg_id] = 0

        if self._gesture_flag and preds[self._current_ges] < lower_thd:
            # print('in 1')
            # print('current:{}'.format(self._current_ges))
            self._current_ges = self._bg_id
            self._gesture_flag = False

        if not (self._gesture_flag) and (preds.max() >= upper_thd) and (preds.argmax() != self._bg_id):
            # print('in 2')
            self._rising_ges = preds.argmax()
            self._current_ges = self._rising_ges
            self._gesture_flag = True
            # print('current:{}'.format(self._current_ges))

        # Record without background
        output = self._bg_id if self._rising_ges == self._bg_id else self._current_ges
        self._rising_ges = self._bg_id
        # print(output)

        return output

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
target=mqttc.loop_start()
# mqttc.loop_forever()




log.setLevel(logging.DEBUG)
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
        res_addrs_dict = {
            'SoftmaxExponential': [addr for addr in range(0x50000508, 0x5000051C + 1, 4)],
            'Gestures': [addr for addr in range(0x50000580, 0x50000580 + 1, 4)]
        }
        post_proc = PostProcess()
        integration.switchCollectionOfMultiResults(actions=0b101, 
                                                   read_interrupt=0, 
                                                   clear_interrupt=0, 
                                                   raw_size=(8192+2)*2, 
                                                   ch_of_RBank=1, 
                                                   reg_address=res_addrs_dict['SoftmaxExponential'])
        s = time.time_ns()
        # t.start()
        for i in range(20):
            print(f'=================={i}==================')
            data = integration.getMultiResults()[1]
            print(f'getMultiResults : {data[0][:4].hex(" ")}')
            exp = np.frombuffer(data[2], dtype='>u4')
            prediction = convertEXPVal(exp)
            print(prediction)
            ges = post_proc.run(prediction)
            if ges != 0:
                print(ges)
                mqttc.publish("/k60168/{01}/gesture", ges)  
            print(f'getMultiResults time : {(time.time_ns()-s)/1000000} ms')
            s = time.time_ns()


        print(integration.switchCollectionOfMultiResults(actions=0b0, read_interrupt=0, clear_interrupt=0, raw_size=(8192 + 2) * 2,
                                                  ch_of_RBank=1, reg_address=[]))
    mqttc.disconnect()