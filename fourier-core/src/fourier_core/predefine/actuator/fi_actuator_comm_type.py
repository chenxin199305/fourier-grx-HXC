from enum import IntEnum


class ActuatorCommType(IntEnum):
    CAN = 0x01
    ETHERNET = 0x02
    ETHERCAT = 0x03
    RS485 = 0x04
    RS232 = 0x05
    USB = 0x06
    SPI = 0x07
    I2C = 0x08
    MODBUS = 0x09
    PROFINET = 0x0A
    POWERLINK = 0x0B
    IO_LINK = 0x0C
    OTHER = 0x0D
