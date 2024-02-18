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


class TC2_E113_FS(TCGen2):

    resolution_x = 2400
    resolution_y = 1035
    number_of_slots = 3
    supported_number_of_colors = [2,4]
    panel_type = '113'
    system_version_code = b'\xd0\xb5'

    # TODO image flip should be done here ...

    def get_epd_header(self,image):
        # EPD file format for 9.7
        # http://trac.mpicosys.com/mpicosys/wiki/EpaperDrivingMain/EpaperImageFileDef/EpaperImageHeaderAssignedValues
        color_depth_byte = 0x01 if not self.is_image_two_bit(image) else 0x02 # doc says it is 0x04 ...
        return [0x44, 0x09, 0x60, 0x04, 0x0A, color_depth_byte, 0x00]+[0x00,]*9

    def get_epdheader_1bit(self):
        return [0x44, 0x09, 0x60, 0x04, 0x0A, 0x01, 0x00] + [0x00, ] * 9

    def convert(self,img):
        # this display requires XY flip of the image
        if self.is_image_two_bit(img):
            return epd.convert.toType0_2bit(img.tobytes(),self.resolution_x)
        else:
            return epd.convert.flip_xy(data=epd.convert.toType0_1bit(img.tobytes()), image_bytes_width=self.resolution_x/8)


