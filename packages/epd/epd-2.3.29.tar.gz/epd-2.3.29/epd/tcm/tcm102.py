# -*- coding: UTF-8 -*-
"""
TCM 10.2 classes.

..  Copyright (C) MpicoSys-Embedded Pico Systems, all Rights Reserved.
    This source code and any compilation or derivative thereof is the
    proprietary information of MpicoSys and is confidential in nature.
    Under no circumstances is this software to be exposed to or placed
    under an Open Source License of any type without the expressed
    written permission of MpicoSys.
"""


from .TCGen2 import TCGen2
from .TCGen1 import TCGen1
import epd.convert

__copyright__ = "Copyright (C) MpicoSys-Embedded Pico Systems"
__author__ = "Paweł Musiał <pawel.musial@mpicosys.com>"
__version__ = "2.0"


class TCM2102v231(TCGen2):
    """
    TCM 10.2 v220 converter class.

    .. seealso ::
       * `EPD image formats <http://trac.mpicosys.com/mpicosys/
         wiki/EpaperDrivingMain/EpaperEpdImageFormats>`_ on MpicoSys
         TRAC
    """

    resolution_x = 1024
    resolution_y = 1280
    supported_number_of_colors = [2,]
    panel_type = '102'
    system_version_code = b'\xd0\xaf'

    def get_epd_header(self,image):
        # EPD file format for 10.2
        # http://trac.mpicosys.com/mpicosys/wiki/EpaperDrivingMain/EpaperImageFileDef/EpaperImageHeaderAssignedValues

        return [0x3D, 0x04, 0x00, 0x05, 0x00, 0x01, 0x00]+[0x00,]*9

    def convert(self,img):
        return epd.convert.toType0_1bit(img.tobytes())


class TCM102v220(TCGen1):

    resolution_x = 1024
    resolution_y = 1280
    supported_number_of_colors = [2,]
    panel_type = '102'
    system_version_code = b'\xd0\xac'

    def get_epd_header(self,image):
        # EPD file format for 10.2
        # http://trac.mpicosys.com/mpicosys/wiki/EpaperDrivingMain/EpaperImageFileDef/EpaperImageHeaderAssignedValues

        return [0x3D, 0x04, 0x00, 0x05, 0x00, 0x01, 0x20]+[0x00,]*9

    def convert(self,img):
        return epd.convert.toType0_1bit(img.tobytes())
