from PyQt5 import QtWidgets, QtGui
from pathlib import Path
import os


class Preview:
    temp_dir = "image_converter/preview"
    def __init__(self, label, root):
        self._label = label
        self._root = root
        self.root = root
        self._path = None
    
    @property
    def path(self):
        if self._path is None:
            return ""
        return os.path.join(self.root, self._path)
    
    @path.setter
    def path(self, path):
        if self._path is not None:
            if Path(self._path).is_file():
                self.delete()
        self._path = path
        return self.path

    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, label):
        if isinstance(QtWidgets.QLabel, label):
            self._label = label
    
    @property
    def root(self):
        return self._root
    
    @root.setter
    def root(self, root):
        root_ = os.path.join(self._root, self.temp_dir)
        if not Path(root_).is_dir():
            os.makedirs(root_)
        if Path(root_).is_dir():
            self._root = root_
        return self.root
    
    def delete(self):
        if Path(self.root).is_dir():
            os.remove(self.path)

    def refresh(self):
        if self.path is not None:
            self.label.clear()
            movie = QtGui.QMovie(self.path)
            self.label.setMovie(movie)
            movie.start()
    

