# -*- coding: UTF-8 -*-

from .TCGen2 import TCGen2
import epd.convert

__copyright__ = "Copyright (C) MpicoSys-Embedded Pico Systems"
__author__ = "Paweł Musiał <pawel.musial@mpicosys.com>"
__version__ = "2.0"


class TCM274v231(TCGen2):
    """
    TCM2 7.4 v231 converter class.

    .. seealso ::
       * `EPD image formats <http://trac.mpicosys.com/mpicosys/
         wiki/EpaperDrivingMain/EpaperEpdImageFormats>`_ on MpicoSys
         TRAC
    """

    resolution_x = 480
    resolution_y = 800
    supported_number_of_colors = [2,]
    panel_type = '74'

    def get_epd_header(self,image):
        # EPD file format for 7.4
        # http://trac.mpicosys.com/mpicosys/wiki/EpaperDrivingMain/EpaperImageFileDef/EpaperImageHeaderAssignedValues

        return [0x3A, 0x01, 0xE0, 0x03, 0x20, 0x01, 0x00]+[0x00,]*9

    def convert(self,img):
        return epd.convert.toType0_1bit(img.tobytes())
