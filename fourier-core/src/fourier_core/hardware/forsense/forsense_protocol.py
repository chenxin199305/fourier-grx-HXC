#!/usr/bin/env python3

"forsense protocol module"

import datetime
import struct
import threading


class ForsenseFrame_Exception(Exception):
    def __init__(self, err="IMU: HI221GW Frame Error"):
        Exception.__init__(self, err)


class ForsenseFrame_NoValid_Exception(ForsenseFrame_Exception):
    def __init__(self, err="IMU: No valid frame received"):
        Exception.__init__(self, err)


class ForsenseFrame_NotCompleted_Exception(ForsenseFrame_Exception):
    def __init__(self, err="IMU: No full frame received"):
        Exception.__init__(self, err)


class ForsenseFrame_ErrorFrame_Exception(ForsenseFrame_Exception):
    def __init__(self, err="IMU: Error frame"):
        Exception.__init__(self, err)


def _parse_data_packet_0x91(data_section: list):
    """
    解析 tag 0x91 的数据包

    :param data_section: 数据段列表
    :return: 包含解析结果的字典列表
    """

    acc_temp_list = []
    gyr_temp_list = []
    eul_temp_list = []
    quat_temp_list = []
    version_temp_list = []

    # reset index
    index = 0

    # acc
    index = 12
    acc_X = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    acc_Y = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    acc_Z = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    acc_dic = {
        "X": round(acc_X, 8),
        "Y": round(acc_Y, 8),
        "Z": round(acc_Z, 8),
    }
    acc_temp_list.append(acc_dic)

    # gyr
    index = 24
    gyr_X = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    gyr_Y = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    gyr_Z = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    gyr_dic = {
        "X": round(gyr_X, 8),
        "Y": round(gyr_Y, 8),
        "Z": round(gyr_Z, 8),
    }
    gyr_temp_list.append(gyr_dic)

    # eul
    index = 48
    eul_Roll = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    eul_Pitch = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    eul_Yaw = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    eul_dic = {
        "Roll": round(eul_Roll, 8),
        "Pitch": round(eul_Pitch, 8),
        "Yaw": round(eul_Yaw, 8),
    }
    eul_temp_list.append(eul_dic)

    # quat
    index = 60
    quat_W = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    quat_X = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    quat_Y = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    quat_Z = float(struct.unpack("<f", bytes(data_section[index: index + 4]))[0])
    index += 4
    quat_dic = {
        "W": round(quat_W, 3),
        "X": round(quat_X, 3),
        "Y": round(quat_Y, 3),
        "Z": round(quat_Z, 3),
    }
    quat_temp_list.append(quat_dic)

    # version
    index = 44
    hardware_version = int(struct.unpack("<B", bytes(data_section[index: index + 1]))[0])
    index += 1
    software_version = int(struct.unpack("<B", bytes(data_section[index: index + 1]))[0])
    index += 1
    version_dic = {
        "HV": hardware_version,
        "SV": software_version,
    }
    version_temp_list.append(version_dic)

    temp_dic_list = {
        "quat": quat_temp_list,
        "euler": eul_temp_list,
        "gyr": gyr_temp_list,
        "acc": acc_temp_list,
        "version": version_temp_list,
    }
    return temp_dic_list


data_packet_properties = {
    0x91: {
        "data_len": 76,
        "parse method": _parse_data_packet_0x91,
    },
}


def crc16_update(buffer_list, cal_len, cal_pos, crc=0):
    for temp_j in range(cal_len):
        byte = buffer_list[temp_j + cal_pos]
        crc ^= byte << 8
        crc &= 0xFFFFFFFF
        for temp_i in range(8):
            temp = crc << 1
            temp &= 0xFFFFFFFF
            if crc & 0x8000:
                temp ^= 0x1021
                temp &= 0xFFFFFFFF
            crc = temp

    return crc & 0xFFFF


SampleRate = 0
SamplesReceived = 0
prevSamplesReceived = 0
sample_rate_alive_flag = True


def sample_rate_timer_cb(sample_timer):
    global SampleRate, SamplesReceived, prevSamplesReceived, sample_rate_alive_flag

    SampleRate = SamplesReceived - prevSamplesReceived
    prevSamplesReceived = SamplesReceived

    print(
        "每秒幀率：",
        SampleRate,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    )

    if sample_rate_alive_flag == True:
        sample_timer = threading.Timer(1.00, sample_rate_timer_cb, args=(sample_timer,))
        sample_timer.start()


def sample_rate_timer_close():
    global sample_rate_alive_flag
    sample_rate_alive_flag = False


# 找到幀頭
def find_frame_header(buffer_list: list):
    # 循環查找，直至拋出異常
    while True:
        # 查找幀頭的第一個標識符0x5a,若未找到，將會拋出ValueError異常
        try:
            header_ind = buffer_list.index(0x5A)
        except ValueError:
            raise ForsenseFrame_NotCompleted_Exception

        if header_ind + 1 > len(buffer_list) - 1:
            raise ForsenseFrame_NotCompleted_Exception

        if buffer_list[header_ind + 1] == 0xA5:
            # 找到幀頭標識符0x5aa5，返回幀頭位置
            return header_ind
        else:
            # 未找到幀頭標識符，切片繼續查找
            buffer_list = buffer_list[header_ind + 1:]


# 驗證獲取長度
def _get_frame_length(buffer_list, header_pos):
    return int(struct.unpack("<h", bytes(buffer_list[header_pos + 2: header_pos + 4]))[0])


# 驗證長度是否合法
def _verify_frame_length(buffer_list: list, header_pos):
    # 獲取到幀長度
    frame_len = int(struct.unpack("<h", bytes(buffer_list[header_pos + 2: header_pos + 4]))[0])

    # 判斷幀長度是否合法
    if frame_len >= 1024:
        raise ForsenseFrame_ErrorFrame_Exception
    elif frame_len + header_pos + 6 > len(buffer_list):
        raise ForsenseFrame_NotCompleted_Exception


# 驗證crc是否正確
def _verify_frame_crc(buffer_list, header_pos=0):
    # 獲取到幀長度
    frame_len = int(struct.unpack("<h", bytes(buffer_list[header_pos + 2: header_pos + 4]))[0])

    # 獲取幀內的crc
    f_crc = int(struct.unpack("<H", bytes(buffer_list[header_pos + 4: header_pos + 4 + 2]))[0])

    # 計算幀的crc
    # CRC covers: header(2) + length(2) + data(frame_len), excludes CRC itself
    cal_crc = crc16_update(buffer_list, cal_len=2, cal_pos=header_pos, crc=0)  # 5A A5
    cal_crc = crc16_update(buffer_list, cal_len=2, cal_pos=header_pos + 2, crc=cal_crc)  # length
    cal_crc = crc16_update(buffer_list, cal_len=frame_len, cal_pos=header_pos + 6, crc=cal_crc)  # data

    if cal_crc != f_crc:
        raise ForsenseFrame_ErrorFrame_Exception


# 截取一條完整且合法的幀，並將幀頭幀尾返回
def intercept_one_complete_frame(buffer_list):
    # 找幀頭
    header_pos = find_frame_header(buffer_list)

    # 獲取幀長度，若失敗會拋出異常
    try:
        frame_len = int(struct.unpack("<H", bytes(buffer_list[header_pos + 2:  header_pos + 4]))[0])
    except struct.error:
        raise ForsenseFrame_NotCompleted_Exception

    end_pos = header_pos + (6 - 1) + frame_len

    # 驗證幀長度
    _verify_frame_length(buffer_list, header_pos)

    # 驗證crc
    _verify_frame_crc(buffer_list, header_pos)

    return header_pos, end_pos


# 從完整幀中獲取資訊
def extraction_information_from_frame(
        bin_buffer: list,
        fifo_buffer,
):
    # 幀率統計
    global SamplesReceived

    SamplesReceived = SamplesReceived + 1

    # 處理數據幀
    data_dic = {}

    data_frame_list = bin_buffer[6:]

    # 遍歷解析數據段內包含的數據
    while len(data_frame_list) > 0:
        if data_frame_list[0] in data_packet_properties:
            temp_dic = data_packet_properties[data_frame_list[0]]["parse method"](data_frame_list)
            data_dic.update(temp_dic)

            data_len = data_packet_properties[data_frame_list[0]]["data_len"]
            data_frame_list = data_frame_list[data_len:]
        else:
            # raise ForsenseFrame_ErrorFrame_Exception
            data_frame_list = data_frame_list[1:]

    fifo_buffer.put(data_dic)
