import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from MainWindow import Ui_MainWindow

from files.file_selector import select, srcToDest, getExtention
from converter.convert import converter
import os

from pathlib import Path

_translate = QtCore.QCoreApplication.translate



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.toolButton_2.clicked.connect(self.getSrc)
        self.actionOpen_folder.triggered.connect(self.getSrc)
        self.toolButton_3.clicked.connect(self.getDest)
        self.checkBox_2.clicked.connect(self.getCheckAllSrc)
        self.comboBox_2.currentTextChanged.connect(self.filterSrc)
        self.comboBox_3.currentTextChanged.connect(self.setOutExt)
        self.commandLinkButton.clicked.connect(self.convert)

        self.available_in_ext = [
            ".webp",
            ".jpeg",
            ".jpg",
            ".png"
        ]
        self.available_out_ext = [
            ".webp",
            ".jpeg",
            ".jpg",
            ".png"
        ]

        self.src_list = []
        self.src_selected = []
        self.src_ext = []
        self.src_path = str(Path.home())
        self.setSrcPath(self.src_path)

        self.dest_list = []
        self.out_ext = self.available_out_ext[0]
        self.dest_path = str(Path.home())
        self.setDestPath(self.dest_path)

        self.initOutExtCombo()

    def initOutExtCombo(self):
        for i, e in enumerate(self.available_out_ext):
            self.comboBox_3.addItem("")    
            self.comboBox_3.setItemText(i + 1, _translate("MainWindow", e))

    def setOutExt(self, value):
        self.out_ext = value
        print(self.out_ext)
        self.refreshDest()

    def makeItem(self, text, checked=False):
        item = QtWidgets.QListWidgetItem()
        font = QtGui.QFont()
        font.setFamily("Liberation Sans Narrow")
        item.setFont(font)
        if checked is not None:
            check_state = QtCore.Qt.Checked
            if not checked:
                check_state = QtCore.Qt.Unchecked
            item.setCheckState(check_state)
        item.setText(_translate("MainWindow", text))

        return item

    def showList(self, list_type, dest):
        l = getattr(self, "%s_list" % list_type)
        if l is not None:
            for item in l:
                dest.addItem(item)

    def appendToSelectedSrc(self, item):
        if not item in self.src_selected:
            self.src_selected.append(item)

    def removeToSelectedSrc(self, item):
        self.src_selected = list(filter(lambda x: x is not item, self.src_selected))

    def checkItem(self, item):
        item.setCheckState(QtCore.Qt.Checked)
        self.appendToSelectedSrc(item)
        self.refreshDest()

    def uncheckItem(self, item):
        item.setCheckState(QtCore.Qt.Unchecked)
        self.removeToSelectedSrc(item)
        self.refreshDest()


    def getCheckAllSrc(self):
        method = self.checkItem
        if not self.checkBox_2.isChecked():
            method = self.uncheckItem
        for item in self.src_list:
            method(item)

    def filterSrc(self, value):
        filtered = [i for i in self.src_list if (
            os.path.splitext(i.text())[1] == value
        )]
        for item in self.src_list:
            self.uncheckItem(item)
        for item in filtered:
            self.checkItem(item)
        self.src_selected = filtered

    def setSrcPath(self, path):
        self.src_path = path
        self.label_3.setText(_translate("MainWindow", self.src_path))

    def setDestPath(self, path):
        self.dest_path = path
        self.label_6.setText(_translate("MainWindow", self.dest_path))

    def getSrc(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select image folder:', self.src_path, QtWidgets.QFileDialog.ShowDirsOnly)
        # prevent cancel
        if dir_:
            self.setSrcPath(dir_)
            files = select(dir_)
            for i, f in enumerate(files):
                image_name = str(f)
                src_items_text = [i.text() for i in self.src_list]
                if (image_name not in src_items_text) and getExtention(image_name) in self.available_in_ext:
                    item = self.makeItem(image_name)
                    self.src_list.append(item)
                    ext = os.path.splitext(image_name)[1]
                    if not ext in self.src_ext and ext in self.available_in_ext:
                        self.src_ext.append(ext)

            # self.comboBox_2.addItem("")    
            # self.comboBox_2.setItemText(0, _translate("MainWindow", "Tout"))
            for i, e in enumerate(self.src_ext):
                self.comboBox_2.addItem("")    
                self.comboBox_2.setItemText(i + 1, _translate("MainWindow", e))
            self.showList("src", self.listWidget_3)

    def getDest(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select image folder:', self.dest_path, QtWidgets.QFileDialog.ShowDirsOnly)
        self.label_6.setText(_translate("MainWindow", dir_))
        self.dest_path = dir_
        self.refreshDest()

    def refreshDest(self):
        self.listWidget_4.clear()
        self.dest_list = []
        for item in self.src_selected:
            out_text = srcToDest(item.text(), self.dest_path, self.out_ext)
            dest_item = self.makeItem(out_text, checked=None)
            self.dest_list.append(dest_item)
        
        self.showList("dest", self.listWidget_4)
    
    def convert(self):
        if len(self.src_selected):
            for i, item in enumerate(self.src_selected):
                out_text = srcToDest(item.text(), self.dest_path, self.out_ext)
                log_item = self.makeItem("%s ---> %s" %(item.text(), out_text), checked=None)
                self.listWidget.addItem(log_item)
                forward_ratio =  (i + 1) / len(self.src_selected) * 100
                converter(item.text(), out_text, self.out_ext)
                self.progressBar.setProperty("value", forward_ratio)

        


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()