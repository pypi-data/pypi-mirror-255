from PIL import Image

def pilimage_to_1bit(img):
    img1bit=img.convert("P",dither=Image.FLOYDSTEINBERG, palette=Image.ADAPTIVE, colors=2)
    onebit_palette = [0xFF,]*3+[0x00,]*255*3
    img1bit.putpalette(onebit_palette)
    return img1bit

def pilimage_to_2bit(img):
    img2bit=img.convert("P",dither=Image.FLOYDSTEINBERG, palette=Image.ADAPTIVE, colors=4)
    twobit_palette = [0xFF, 0xFF, 0xFF] + [0xAA, 0xAA, 0xAA] + [0x55, 0x55, 0x55] + [0, 0, 0] + [0x00,]*252*3
    img2bit.putpalette(twobit_palette)
    return img2bit