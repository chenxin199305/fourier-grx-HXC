import struct

from fourier_core.predefine import *


def array_find(input_array, find_array, start_index=0, stop_index=-1):
    stop_index = len(input_array) + stop_index if stop_index < 0 else stop_index
    for i in range(start_index, stop_index - len(find_array) + 1):
        if input_array[i:i + len(find_array)] == find_array:
            return FunctionResult.SUCCESS, i
    return FunctionResult.FAIL, -1


def hex2int32(data):
    return struct.unpack(">i", bytes(data))[0]


def array_to_int(array):
    if len(array) == 1:
        to_int_value = (array[0] << 0)
        return FunctionResult.SUCCESS, to_int_value
    elif len(array) == 2:
        to_int_value = (array[0] << 8) + (array[1] << 0)
        return FunctionResult.SUCCESS, to_int_value
    elif len(array) == 4:
        to_int_value = (array[0] << 24) + (array[1] << 16) + (array[2] << 8) + (array[3] << 0)
        return FunctionResult.SUCCESS, to_int_value
    else:
        return FunctionResult.FAIL, 0


def hex2float(data):
    return round(struct.unpack(">f", bytes(data))[0], 4)


def array_to_float(array):
    if len(array) == 4:
        return FunctionResult.SUCCESS, hex2float(array)
    return FunctionResult.FAIL, 0


def int2hex(data):
    return list(struct.unpack('4B', struct.pack('>i', int(data))))


def int_to_array(value, size):
    if size not in [1, 2, 4]:
        return FunctionResult.FAIL, []
    to_array_value = [(value >> (8 * i)) & 0xFF for i in reversed(range(size))]
    return FunctionResult.SUCCESS, to_array_value


def float2hex(data):
    return list(struct.unpack('4B', struct.pack('>f', float(data))))


def float_to_array(value, size):
    if size == 4:
        return FunctionResult.SUCCESS, float2hex(value)
    return FunctionResult.FAIL, []
