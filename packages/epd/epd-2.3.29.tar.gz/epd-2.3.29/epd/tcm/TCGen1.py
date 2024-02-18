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


class TCGen1(object):

    def __init__(self):
        self.compression = False # TCGen1 does not support compression

    def is_image_two_bit(self,image):
        return False            # TCGen1 only 1 bit is supported

    def build_epd_UploadImageData(self,data):
        return [0x20, 0x01, 0x00,len(data)] + data

    def get_epd_commands(self, image, packet_size=200):
        """
        Get set of EPD commands with converted image.

        Returns a list with EPD commands that should be
        send into the TCM to display converted image.

        :return: List with EPD commands
        :rtype: list

        .. seealso ::
           * `EPD transfer protocol <http://trac.mpicosys.com/mpicosys/
             wiki/EpaperDrivingMain/EpaperTransferProtocolDef>`_ on
             MpicoSys TRAC
        """

        epdCommands = []

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

        return epd_data

    def get_reset_data_pointer_command(self):
        return [0x20,0x0D,0x00]


    def get_display_update_command(self,update_type="default"):
        return [0x24,0x01,0x00]

