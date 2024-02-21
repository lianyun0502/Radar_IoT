import numpy as np

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