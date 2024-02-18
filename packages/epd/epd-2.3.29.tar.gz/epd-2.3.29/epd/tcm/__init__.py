# -*- coding: utf-8 -*-
"""
TCM factory method.

..  Copyright (C) MpicoSys-Embedded Pico Systems, all Rights Reserved.
    This source code and any compilation or derivative thereof is the
    proprietary information of MpicoSys and is confidential in nature.
    Under no circumstances is this software to be exposed to or placed
    under an Open Source License of any type without the expressed
    written permission of MpicoSys.
"""

import epd.tcm.tcm27
import epd.tcm.tcm102
import epd.tcm.tcm74
import epd.tcm.tcm133
import epd.tcm.tcm312
import epd.tcm.tcm97
import epd.tcm.tcm113
import epd.tcm.tcm280

__copyright__ = "Copyright (C) MpicoSys-Embedded Pico Systems"
__author__ = "Paweł Musiał <pawel.musial@mpicosys.com>"
__version__ = "1.0"

class TCMNotExistsError(Exception):

    """
    TCM not exists error.
    Raised when user try to create a converter for not existing TCM.
    """

    def __init__(self, tcm):
        """ Class constructor. """
        self.tcm = tcm

    def __str__(self):
        """ String representation of error. """
        return "Cannot create TCM class for requested TCM: %s" % self.tcm

def TCM(system_version_code):
    """
    TCM factory method.

    Create an instance of requested TCM class by its system version code:
    http://trac.mpicosys.com/mpicosys/wiki/EpaperDrivingMain/EpaperSystemValuesDefinition.

    Available TCM's:

    :param system_version_code : TCM system version code
    :raise module.exception.TCMNotExistsError: raised when
        cannot find the requested TCM.
    """

    # check device family
    device_family = system_version_code [0]
    device_code = system_version_code[1]

    if device_family == 0xD0:
        if device_code == 0xA8: # TC-P74-110
            return tcm74.TCM74v110()
        elif device_code == 0xA9: # TC-P74-220
            return tcm74.TCM74v110()
        elif device_code == 0xAA: # TC-P74-230
            return tcm74.TCM74v110()
        elif device_code == 0xAC: # TC-P102-220 variants X and XC exist (FLASH/NVRAM)
            return tcm102.TCM102v220()
        # elif device_code == 0xAD: # TC-P102-231
        #     return TCM102v220()
        elif device_code == 0xB1:  # TC2-P102-231
            return tcm74.TCM274v231()
        elif device_code == 0xAF: # TC2-P102-231
            return tcm102.TCM2102v231()
        elif device_code == 0xB2: # TC2-E133-320
            return tcm133.TC2133v320()
        elif device_code == 0xB3: # TC2-E312-320
            return tcm312.TCM312v320()
        elif device_code == 0xB7: # TC2-E312-320
            return tcm312.TCM312v320b7()
        elif device_code == 0xB4: # TC2-E97
            return tcm97.TC2_E97_v320()
        elif device_code == 0xB5: # TC2-E113
            return tcm113.TC2_E113_FS()
        else:
            raise TCMNotExistsError("Unsupported device family %x" % device_family)
    elif device_family == 0xE0:
        if device_code == 0xE0:
            return tcm27.TC227()
        else:
            raise TCMNotExistsError("Unsupported device family %x" % device_family)
    else:
        raise TCMNotExistsError("Unsupported device code %x" % device_code )

