# -*- coding: UTF-8 -*-
"""
TCM 13.3 classes.

..  Copyright (C) MpicoSys-Embedded Pico Systems, all Rights Reserved.
    This source code and any compilation or derivative thereof is the
    proprietary information of MpicoSys and is confidential in nature.
    Under no circumstances is this software to be exposed to or placed
    under an Open Source License of any type without the expressed
    written permission of MpicoSys.
"""

from .TCGen2 import TCGen2
import epd.convert

__copyright__ = "Copyright (C) MpicoSys-Embedded Pico Systems"
__author__ = "Paweł Musiał <pawel.musial@mpicosys.com>"
__version__ = "2.0"


class TC2133v320(TCGen2):

    resolution_x = 1600
    resolution_y = 1200
    number_of_slots = 7
    supported_number_of_colors = [2,4]
    panel_type = '133'
    system_version_code = b'\xd0\xb2'

    def get_epd_header(self,image):
        # EPD file format for 13.3
        # http://trac.mpicosys.com/mpicosys/wiki/EpaperDrivingMain/EpaperImageFileDef/EpaperImageHeaderAssignedValues
        return [0x3E, 0x06, 0x40, 0x04, 0xB0, 0x01, 0x00]+[0x00,]*9 if not self.is_image_two_bit(image) else [0x3E, 0x06, 0x40, 0x04, 0xB0, 0x02, 0x00]+[0x00,]*9

    def get_epdheader_1bit(self):
        return [0x3E, 0x06, 0x40, 0x04, 0xB0, 0x01, 0x00] + [0x00, ] * 9

    def convert(self,img):
        if self.is_image_two_bit(img):
            return epd.convert.toType0_2bit(img.tobytes(),self.resolution_x)
        else:
            return epd.convert.toType0_1bit(img.tobytes())


