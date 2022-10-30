import sys
from PyQt5 import QtWidgets, QtCore, QtGui

import humanize

from MainWindow import Ui_MainWindow

from files.file_selector import select, srcToDest, getExtention, getSize
from converter.convert import converter, ConverterDestExists, ConverterSrcNotExists
import os

from pathlib import Path

_translate = QtCore.QCoreApplication.translate



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.toolButton_2.clicked.connect(self.getSrc)
        self.actionOpen_folder.triggered.connect(self.getSrc)
        self.pushButton.clicked.connect(self.deleteSrc)
        self.actionOpen_file.triggered.connect(self.getFile)
        self.toolButton_3.clicked.connect(self.getDest)
        self.checkBox_2.clicked.connect(self.getCheckAllSrc)
        self.checkBox.clicked.connect(self.checkDestForce)
        self.checkBox.setToolTip("En mode force, la destination déjà existante sera écrasée.")
        self.comboBox_2.currentTextChanged.connect(self.filterSrc)
        self.comboBox_3.currentTextChanged.connect(self.setOutExt)
        self.commandLinkButton.clicked.connect(self.convert)
        self.listWidget_3.itemClicked.connect(self.srcItemChanged)

        self.available_in_ext = [
            ".webp",
            ".jpeg",
            ".jpg",
            ".png"
        ]
        self.available_out_ext = [
            ".webp",
            ".jpeg",
            ".png"
        ]

        self._src_list = []
        self._src_selected = []
        self.src_ext = []
        self.src_path = str(Path.home())
        self.setSrcPath(self.src_path)

        self.dest_list = []
        self.out_ext = self.available_out_ext[0]
        self.dest_path = str(Path.home())
        self.dest_force = False
        self.setDestPath(self.dest_path)

        self.initOutExtCombo()

    @property
    def src_list(self):
        return self._src_list

    @src_list.setter
    def src_list(self, value):
        self._src_list = value
        
    @property
    def src_selected(self):
        return self._src_selected

    @src_selected.setter
    def src_selected(self, value):
        self._src_selected = value

    def checkDestForce(self):
        self.dest_force = self.checkBox.isChecked()

    def initOutExtCombo(self):
        for i, e in enumerate(self.available_out_ext):
            self.comboBox_3.addItem("")    
            self.comboBox_3.setItemText(i, _translate("MainWindow", e))

    def setOutExt(self, value):
        self.out_ext = value
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
        is_all_selected = bool(len(self.src_list) and all([int(i.checkState()) != 0 for i in self.src_list]))
        cls = QtCore.Qt.Checked if is_all_selected else QtCore.Qt.Unchecked
        self.checkBox_2.setCheckState(cls)

    def appendToSelectedSrc(self, item):
        if not item in self.src_selected:
            self.src_selected.append(item)

    def removeToSelectedSrc(self, item):
        self.src_selected = list(filter(lambda x: x is not item, self.src_selected))

    def srcItemChanged(self, item):
        method = self.checkItem if int(item.checkState()) == 2 else self.uncheckItem
        method(item)

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

    def _refreshSrcCombo(self):
        self.comboBox_2.clear()
        for i, e in enumerate(self.src_ext):
            self.comboBox_2.addItem("")    
            self.comboBox_2.setItemText(i, _translate("MainWindow", e))

    def pushToSrcList(self, image_name):
        item = None
        src_items_text = [i.text() for i in self.src_list]
        ext = getExtention(image_name)
        if (image_name not in src_items_text) and ext in self.available_in_ext:
            item = self.makeItem(image_name)
            self.src_list.append(item)
            if not ext in self.src_ext and ext in self.available_in_ext:
                self.src_ext.append(ext)
        return item

    def flushSrc(self):
        self._refreshSrcCombo()
        self.showList("src", self.listWidget_3)

    def getFile(self):
        image_filter = "Images files (%s)" % " ".join(["*" + i for i in self.available_in_ext]) 
        image_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Selectionnez une image', self.src_path, image_filter)
        if image_name:
            item = self.pushToSrcList(image_name)
            self.checkItem(item)
            self.flushSrc()

    def getSrc(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Selectionnez un dossier d\'image:', self.src_path, QtWidgets.QFileDialog.ShowDirsOnly)
        # prevent cancel
        if dir_:
            self.setSrcPath(dir_)
            files = select(dir_)
            for i, f in enumerate(files):
                image_name = str(f)
                self.pushToSrcList(image_name)

            self.flushSrc()
    
    def deleteSrc(self):
        if len(self.src_selected):
            clean_src = [item for item in self.src_list if item not in self.src_selected]
            clean_src_ext = []
            for item in clean_src:
                ext = getExtention(item.text())
                if ext not in clean_src_ext:
                    clean_src_ext.append(ext)
            self.src_ext = clean_src_ext
            self.src_list = clean_src
            for item in self.src_selected:
                index = self.listWidget_3.row(item)
                if int(index) > -1:
                    self.listWidget_3.takeItem(index)
            self.src_selected = []
            self.flushSrc()
            self.refreshDest()
        else:
            self.pushToLog("Aucune selection à supprimer", "error")


    def getDest(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select image folder:', self.dest_path, QtWidgets.QFileDialog.ShowDirsOnly)
        # prevent cancel
        if dir_:
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

    def pushToLog(self, text, stat):
        status = {
            "error": QtGui.QColor("red"),
            "warning": QtGui.QColor("orange"),
            "success": QtGui.QColor("green"),
            "info": QtGui.QColor("blue"),
        }
        log_item = self.makeItem(text, checked=None)
        log_item.setForeground(status.get(stat, QtGui.QColor("black")))
        self.listWidget.addItem(log_item)

    def convert(self):
        if len(self.src_selected):
            sizes = []
            for i, item in enumerate(self.src_selected):
                log = []
                try:
                    out_text = srcToDest(item.text(), self.dest_path, self.out_ext)
                    converter(item.text(), out_text, self.out_ext, force=self.dest_force)
                    
                    log = ["%s ---> %s" %(item.text(), out_text), "success"]
                    sizes.append((getSize(item.text()), getSize(out_text)))
                except ConverterSrcNotExists as e:
                    log = [str(e), "error"]
                except ConverterDestExists as e:
                    log = [str(e), "warning"]

                self.pushToLog(*log)
                forwarding_ratio =  (i + 1) / len(self.src_selected) * 100
                self.progressBar.setProperty("value", forwarding_ratio)
            delta_size = sum([i[0][0] - i[1][0] for i in sizes])
            self.pushToLog("%s %s" % (humanize.naturalsize(abs(delta_size)), " ont été libérés" if delta_size > 0 else " ont été ajoutés"), "info")

        else:
            self.pushToLog("La source ne contient aucun élément ! \n - Choississez un dossier source et sélectionnez des fichiers\n - Ouvrez un fichier depuis le menu Fichier", "error")

        


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()