import pathlib
import humanize
import os

def select(root):
    res = []
    dir_ = pathlib.Path(root)
    for d in dir_.iterdir():
        if d.is_file():
            res.append(d)
    return res

def srcToDest(src, dest, ext_out):
    file_name = os.path.splitext(os.path.split(src)[1])[0]
    return os.path.join(dest, file_name + ext_out)

def getExtention(path):
    return os.path.splitext(os.path.split(path)[1])[1]

def getSize(path):
    size = pathlib.Path(path).stat().st_size
    natural_size = humanize.naturalsize(size)
    return (size, natural_size)