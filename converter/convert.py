from PIL import Image

def converter(src, dest, out_format):
    image = Image.open(src)  # Open image
    image.save(dest, format=out_format.split(".")[-1])
