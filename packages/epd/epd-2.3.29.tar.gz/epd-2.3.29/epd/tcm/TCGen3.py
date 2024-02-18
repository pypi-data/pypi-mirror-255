# -*- coding: UTF-8 -*-
"""
Abstract TCM class for version 3.

..  Copyright (C) MpicoSys-Embedded Pico Systems, all Rights Reserved.
    This source code and any compilation or derivative thereof is the
    proprietary information of MpicoSys and is confidential in nature.
    Under no circumstances is this software to be exposed to or placed
    under an Open Source License of any type without the expressed
    written permission of MpicoSys.
"""

__copyright__ = "Copyright (C) MpicoSys-Embedded Pico Systems"
__author__ = "Paweł Musiał <pawel.musial@mpicosys.com>"
__version__ = "1.0"

import epd.convert
import hashlib
import struct

class TCMWrongImage(Exception):
    def __init__(self, message):
        """ Class constructor. """
        self.msg = message

    def __str__(self):
        """ String representation of error. """
        return "Problem with provided image to TCM converter: %s" % self.msg

class TCGen3(object):
    # SYSTEM
    TCM_ENABLE = 0x01
    TCM_DISABLE = 0x02
    LED_CONTROL = 0x03

    # DISPLAY
    DISPLAY_UPDATE = 0x10
    WRITE_TO_DISPLAY = 0x11
    CLEAR_SCREEN = 0x12
    COPY_DISPLAY_TO_MEMORY = 0x13
    READ_FROM_DISPLAY = 0x14

    # MEMORY
    CHECK_FILE = 0x30
    WRITE_TO_MEMORY = 0x31
    CLEAR_MEMORY = 0x32
    COPY_MEMORY_TO_DISPLAY = 0x33
    READ_FROM_MEMORY = 0x34

    # GRAPHIC LIB
    PUT_STRING = 0x50
    PUT_STRING_WRAP = 0x51
    GET_STRING_WIDTH = 0x52
    CHANGE_ORIENTATION = 0x53
    DRAW_LINE = 0x54
    DRAW_CIRCLE = 0x55
    DRAW_RECTANGLE = 0x56

    # SYSTEM CONTROL
    GET_SYSTEM_INFO = 0x70
    GET_UNIQUE_ID = 0x71
    LEDS_CONTROL = 0x72
    GET_LEDS_DATA = 0x73
    GET_LIGHTING_DATA = 0x74
    GET_TEMPERATURE = 0x75
    GET_VCOM = 0x76
    SET_VCOM = 0x77

    # DEVELOPMENT CONFIG
    UPLOAD_NEW_FIRMWARE = 0x90
    JUMP_TO_APP = 0x91
    JUMP_TO_BOOT = 0x92
    ERASE_ENTIRE_RAM = 0x93
    ERASE_ENTIRE_FLASH = 0x94
    SYSTEM_RESTART = 0x95
    GET_DISPLAY_INFO = 0x96
    GET_CONFIG_DATA = 0x97

    def __init__(self):
        self.compression = False

    def get_epd_file(self,img,filename=None):
        if len(image.getcolors()) > 2:
            raise TCMWrongImage("Image has more colors than 2")
        bits = 1 # change to support more bits
        data = epd.convert.toType0_1bit(img.tobytes())
        if filename is None:
            # use image hash as file name
            filename = bytes(hashlib.sha1(data).hexdigest())[:16]

        return b'EPD' + struct.pack("<BHHII16s", 48 + bits, img.width, img.height, len(data), epd.convert.crc32(data), filename) + data


    def DisplayUpdate(self, waveform=0): # TODO: add waveform validation
        return struct.pack('<BBBB', self.DISPLAY_UPDATE, waveform, 0, 0)

    def WriteToDisplay(self, datafile, position_x=0, position_y=0): # TODO add address and position validation
        return struct.pack('<BBBBHH', self.WRITE_TO_DISPLAY, 0, 0, 0, position_x, position_y) + datafile

    def ClearScreen(self):
        return struct.pack('<BBBB', self.CLEAR_SCREEN, 0, 0, 0)

    def CopyDisplayToMemory(self, address): # TODO add address validation
        return struct.pack('<BBBBI', self.COPY_DISPLAY_TO_MEMORY, 0, 0, 0, address)

    def ReadFromDisplay(self):
        return struct.pack('<BBBB', self.READ_FROM_DISPLAY, 0, 0, 0)

    def CheckFile(self, address):
        return struct.pack('<BBBBI', self.CHECK_FILE, 0, 0, 0, address)

    def WriteToMemory(self, address, datafile):
        return struct.pack('<BBBBI', self.WRITE_TO_MEMORY, 0, 0, 0, address) + datafile

    def CopyMemoryToDisplay(self, address, position_x, position_y, colormode=0):
        return struct.pack('<BBBBIHH', self.COPY_MEMORY_TO_DISPLAY, colormode, 0, 0, address, position_x, position_y)

    def ReadFromMemory(self, address):
        return struct.pack('<BBBBI', self.READ_FROM_MEMORY, 0, 0, 0, address)

    def PutString(self, fontid, color, position_x, position_y, string):
        return struct.pack('<BBBBIHH', self.PUT_STRING, fontid, color, 0, address, position_x, position_y) + string.encode('ascii')

    def PutStringWrap(self, fontid, color, position_x, position_y, position_x2, position_y2, string):
        return struct.pack('<BBBBIHHHH', self.PUT_STRING_WRAP, fontid, color, 0, address, position_x, position_y, position_x2, position_y2) + string.encode('ascii')



    def GetSystemInfo(self):
        return struct.pack('<BBBB', self.GET_SYSTEM_INFO, 0, 0, 0)
    def GetUniqueId(self):
        return struct.pack('<BBBB', self.GET_UNIQUE_ID, 0, 0, 0)