from PIL import Image
from pathlib import Path

class ConverterSrcNotExists(Exception):
    def __init__(self, src, *args, **kwargs):
        super().__init__("%s :\nLa source n'existe pas !" % src, *args, **kwargs)

class ConverterDestExists(Exception):
    def __init__(self, dest, *args, **kwargs):
        super().__init__("%s :\nLa destination existe déjà !" % dest, *args, **kwargs)

def converter(src, dest, out_format, force=False):
    src_path = Path(src)
    dest_path = Path(dest)
    if not src_path.is_file():
        raise ConverterSrcNotExists(src)
    if dest_path.is_file() and not force:
        raise ConverterDestExists(dest)
    image = Image.open(src)  # Open image
    image.save(dest, format=out_format.split(".")[-1])
