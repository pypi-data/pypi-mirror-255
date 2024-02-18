# -*- coding: UTF-8 -*-
"""
TCM 2.7 classes.

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
__version__ = "1.0"


class TC227(TCGen2):

    resolution_x = 264
    resolution_y = 176
    supported_number_of_colors = [2]
    panel_type = '27'
    system_version_code = b'\xe0\xe0'

    def get_epd_header(self,image):
        # EPD file format for 2.7
        # http://trac.mpicosys.com/mpicosys/wiki/EpaperDrivingMain/EpaperImageFileDef/EpaperImageHeaderAssignedValues
        return [0x32, 0x01, 0x08, 0x00, 0xB0, 0x01, 0x00]+[0x00,]*9

    def convert(self,img):
        return epd.convert.toType0_1bit(img.tobytes())


