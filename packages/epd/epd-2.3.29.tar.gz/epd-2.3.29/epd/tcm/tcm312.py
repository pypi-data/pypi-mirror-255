# -*- coding: UTF-8 -*-
"""
TCM 32.1 classes.

..  Copyright (C) MpicoSys-Embedded Pico Systems, all Rights Reserved.
    This source code and any compilation or derivative thereof is the
    proprietary information of MpicoSys and is confidential in nature.
    Under no circumstances is this software to be exposed to or placed
    under an Open Source License of any type without the expressed
    written permission of MpicoSys.
"""

__copyright__ = "Copyright (C) MpicoSys-Embedded Pico Systems"
__author__ = "Paweł Musiał <pawel.musial@mpicosys.com>"
__version__ = "2.0"

from .TCGen2 import TCGen2
import epd.convert

from PIL import Image


# TODO convert to new format
class TCM312v320(TCGen2):
    """
    Class used to convert images TCM 
    """

    resolution_x = 1440
    resolution_y = 2560
    number_of_slots = 3
    supported_number_of_colors = [2, 4]
    panel_type = '312'
    system_version_code = b'\xd0\xb3'

    def get_epd_header(self,image):
        # EPD file format for 31.2
        return [0x3F,0x05,0xA0,0x0A,0x00,0x01,0x07]+[0x00,]*9


    def convert(self,img):
        if self.is_image_two_bit(img):
            return epd.convert.toType0_2bit(img.tobytes(),self.resolution_x)
        else:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            return epd.convert.toType7_1bit(img.tobytes())


class TCM312v320b7(TCGen2):
    """
    Class used to convert images TCM
    """

    resolution_x = 1440
    resolution_y = 2560
    number_of_slots = 3
    supported_number_of_colors = [2, 4]
    panel_type = '312'
    system_version_code = b'\xd0\xb7'

    def get_epd_header(self, image):
        # EPD file format for 31.2
        return [0x3F, 0x05, 0xA0, 0x0A, 0x00, 0x01, 0x07] + [0x00, ] * 9

    def convert(self, img):
        if self.is_image_two_bit(img):
            return epd.convert.toType0_2bit(img.tobytes(), self.resolution_x)
        else:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            return epd.convert.toType7_1bit(img.tobytes())
