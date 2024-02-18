# -*- coding: UTF-8 -*-
"""
TCM 28.0 classes.

..  Copyright (C) MpicoSys-Embedded Pico Systems, all Rights Reserved.
    This source code and any compilation or derivative thereof is the
    proprietary information of MpicoSys and is confidential in nature.
    Under no circumstances is this software to be exposed to or placed
    under an Open Source License of any type without the expressed
    written permission of MpicoSys.
"""

from .TCGen3 import TCGen3
import epd.convert

__copyright__ = "Copyright (C) MpicoSys-Embedded Pico Systems"
__author__ = "Paweł Musiał <pawel.musial@mpicosys.com>"
__version__ = "2.0"


class TC280(TCGen3):

    resolution_x = 3840
    resolution_y = 1600
    supported_number_of_colors = [2,4]
    panel_type = '280'
    system_version_code = b'\xd0\xba'




