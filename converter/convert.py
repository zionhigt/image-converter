from io import BytesIO
from PIL import Image, ImageSequence
from PIL.ImageQt import ImageQt
from pathlib import Path
from os import path
import io

from PyQt5 import QtCore, QtGui

from files.gif_previewer import Preview

class ConverterSrcNotExists(Exception):
    def __init__(self, src, *args, **kwargs):
        super().__init__("%s :\nLa source n'existe pas !" % src, *args, **kwargs)

class ConverterDestExists(Exception):
    def __init__(self, dest, *args, **kwargs):
        super().__init__("%s :\nLa destination existe déjà !" % dest, *args, **kwargs)

def converter(src, dest, out_format, force=False, save=True):
    src_path = Path(src)
    if not src_path.is_file():
        raise ConverterSrcNotExists(src)
  
    image = Image.open(src)
    if out_format in [".jpeg", ".jpg"]:
        out_format = ".jpeg"
        if image.mode in ("RGBA", "P"):
            image = image.convert('RGB')
    if save and dest is not None:
        dest_path = Path(dest)
        if dest_path.is_file() and not force:
            raise ConverterDestExists(dest)
        image.save(dest, format=out_format.split(".")[-1])
    return image


def resizeImageFromHeight(image, height):
    original_width, original_height = image.size
    factor = height / original_height
    sizes = [int(factor * original_width), height]
    image.resize(sizes)
    return image

def getPreview(images, duration, height):
    pil_images = [
        resizeImageFromHeight(
            converter(src=src, dest=None, out_format=".png", force=True, save=False),
            height
        )
        for src in images
    ]
    pil_images = []
    for src in images:
        pil_images.append(
            resizeImageFromHeight(
                converter(src=src, dest=None, out_format=".png", force=True, save=False),
                height
            )
        )

    img, *imgs = pil_images
    bytes_io = io.BytesIO()
    fps = len(images) / duration
    print(fps)
    img.save(fp=bytes_io, format='GIF', append_images=imgs, save_all=True, fps=0.5, loop=0)
    q_byte_array = QtCore.QByteArray(bytes_io.getvalue())
    bytes_io.close()
    q_buffer = QtCore.QBuffer(q_byte_array)
    return q_buffer
