from io import BytesIO
from PIL import Image, ImageSequence
from PIL.ImageQt import ImageQt
from pathlib import Path
from os import path

from PyQt5 import QtCore

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
  
    image = Image.open(src) # Open image
    if out_format in [".jpeg", ".jpg"]:
        out_format = ".jpeg"
        if image.mode in ("RGBA", "P"):
            image = image.convert('RGB')
    if save:
        dest_path = Path(dest)
        if dest_path.is_file() and not force:
            raise ConverterDestExists(dest)
        image.save(dest, format=out_format.split(".")[-1])
    return image

def getPreview(images, path, duration):
    pil_images = [converter(src, None, ".png", True, False) for src in images]
    pil_images[0].save(path,
               save_all=True, append_images=pil_images[1:], optimize=False, duration=duration, loop=0)
    # image = Image.open(path.join(Path.cwd(), "img_gif.gif"))
    # return ImageQt(image)
    # image.seek(0)
    # buffer = QtCore.QBuffer()
    # buffer.open(QtCore.QBuffer.ReadWrite)
    # frames = []
    # for i, frame in enumerate(ImageSequence.Iterator(image)):
    #     frames.append(ImageQt(frame))
    #     buffer.seek(i)
    #     buffer.write(ImageQt(frame).bits())
    # print(buffer)
    # return frames
    return
