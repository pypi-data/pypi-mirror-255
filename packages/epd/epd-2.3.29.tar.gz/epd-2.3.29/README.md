# EPD (ePaper Driving) library for MpicoSys TCM (Timing Controller Module).

## This library consist of the following parts:
- image preparation for use with 1 and 2 bit color ePaper display,
- image conversion and compression to TCM format,
- commands formatting for use with TCM,

### Image preparation
from PIL import Image
import epd.image

img = Image.open("test_image.png")
img1bit = epd.image.pilimage_to_1bit(img)
img2bit = epd.image.pilimage_to_2bit(img)

### Image conversion to EPD data
import epd.convert
not_compressed_epd_data = epd.convert.toType0_1bit(img1bit.tobytes())
compressed_data =  epd.convert.compress_lz(no_compressed_data)

### TCM Commands formatting 
import epd.tcm

img = Image.open("test_133_image.png")
tcm = epd.tcm.TCM(system_version_code)
epd_data = tcm.get_epd_header(img)+tcm.convert(img)


