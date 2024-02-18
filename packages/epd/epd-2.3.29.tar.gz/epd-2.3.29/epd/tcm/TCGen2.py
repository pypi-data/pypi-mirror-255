# -*- coding: UTF-8 -*-
"""
Abstract TCM class.

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

class TCGen2(object):

    def __init__(self):
        self.compression = False

    def is_image_two_bit(self,image):
        return True if len(image.getcolors()) > 2 else False

    def build_epd_UploadImageData(self,data):
        cmp = 0x10 if self.compression else 0x01
        return [0x20, cmp, 0x00,len(data)] + data

    def get_epd_commands(self, image, packet_size=200, epd_data=None):
        """
        .. seealso ::
           * `EPD transfer protocol <http://trac.mpicosys.com/mpicosys/
             wiki/EpaperDrivingMain/EpaperTransferProtocolDef>`_ on
             MpicoSys TRAC
        """

        epdCommands = []

        if epd_data is None:
            epd_data = self.get_epd_file(image)
        bytestogo = len(epd_data)
        pointer = 0

        while bytestogo > 0:
            # form EPD frame
            if bytestogo > packet_size:
                bytestosend = packet_size
            else:
                bytestosend = bytestogo

            bytestogo -= bytestosend
            epdframe = self.build_epd_UploadImageData(epd_data[pointer:pointer + bytestosend])
            pointer += bytestosend
            epdCommands.append(epdframe)

        return epdCommands

    def get_epd_file(self,image):
        header = self.get_epd_header(image)

        imagedata = self.convert(image)

        epd_data = header + imagedata

        if self.compression:
            data = epd.convert.compress_lz(bytes(epd_data))
            epd_data = list(data)

        return epd_data

    def get_reset_data_pointer_command(self):
        return [0x20,0x0D,0x00]


    def get_display_update_command(self,update_type="default"):
        if update_type == "WBW":
            return [0x81,0x01,0x00]

        if update_type == "BWB":
            return [0x82,0x01,0x00]

        if update_type == "flashless":
            return [0x85,0x01,0x00]

        if update_type == "flashless-inverted":
            return [0x86,0x01,0x00]

        # default "normal"
        return [0x24,0x01,0x00]

    def crc16_add(byte, acc):
        acc ^= 0xFF & byte
        acc = (acc >> 8) | (0xFFFF & (acc << 8))
        acc ^= (0xFFFF & ((acc & 0xff00) << 4))
        acc ^= (acc >> 8) >> 4
        acc ^= (acc & 0xff00) >> 5
        return (0xFFFF & acc)


