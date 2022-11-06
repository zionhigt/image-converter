import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from MainWindow import Ui_MainWindow

from files.gif_previewer import Preview
from files.file_selector import srcToDest

from pathlib import Path

from controller.callback import Callback

_translate = QtCore.QCoreApplication.translate



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.callbacks = Callback(self)
        self.initCallbacks()

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

        self.preview = Preview(label=self.label_2, root=self.dest_path)
        self.gif_speed = 40 

        self.initOutExtCombo()
        # self.initSpeedSlider()

    def initCallbacks(self, *args, **kwargs):
        self.callbacks.init((
            (self.toolButton_2, "clicked", "getSrc"),
            (self.actionOpen_folder, "triggered", "getSrc"),
            (self.pushButton, "clicked", "deleteSrc"),
            (self.actionOpen_file, "triggered", "getFile"),
            (self.toolButton_3, "clicked", "getDest"),
            (self.toolButton_6, "clicked", "getDest"),
            (self.checkBox_2, "clicked", "getCheckAllSrc"),
            (self.checkBox, "clicked", "checkDestForce"),
            (self.comboBox_2, "currentTextChanged", "filterSrc"),
            (self.comboBox_3, "currentTextChanged", "setOutExt"),
            (self.commandLinkButton, "clicked", "convert"),
            (self.listWidget_3, "itemClicked", "srcItemChanged"),
            (self.toolButton_4, "clicked", "gifPreview"),
            (self.horizontalSlider, "valueChanged", "gifSpeedChange"),
        ))
        QtWidgets.QApplication.processEvents()
        self.checkBox.setToolTip("En mode force, la destination déjà existante sera écrasée.")

    def initSpeedSlider(self, *args, **kwargs):
        bar = self.horizontalSlider
        bar.setMinimum(40)
        bar.setMaximum(360)

    def setSrcPath(self, path, *args, **kwargs):
        self.src_path = path
        self.label_3.setText(_translate("MainWindow", self.src_path))

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

    def checkDestForce(self, *args, **kwargs):
        self.dest_force = self.checkBox.isChecked()

    def initOutExtCombo(self, *args, **kwargs):
        for i, e in enumerate(self.available_out_ext):
            self.comboBox_3.addItem("")    
            self.comboBox_3.setItemText(i, _translate("MainWindow", e))

    def setOutExt(self, value, *args, **kwargs):
        self.out_ext = value
        self.refreshDest()


    def showList(self, list_type, dest, *args, **kwargs):
        l = getattr(self, "%s_list" % list_type)
        if l is not None:
            for item in l:
                dest.addItem(item)
        is_all_selected = bool(len(self.src_list) and all([int(i.checkState()) != 0 for i in self.src_list]))
        cls = QtCore.Qt.Checked if is_all_selected else QtCore.Qt.Unchecked
        self.checkBox_2.setCheckState(cls)

    def appendToSelectedSrc(self, item, *args, **kwargs):
        if not item in self.src_selected:
            self.src_selected.append(item)

    def removeToSelectedSrc(self, item, *args, **kwargs):
        self.src_selected = list(filter(lambda x: x is not item, self.src_selected))

    def checkItem(self, item, *args, **kwargs):
        item.setCheckState(QtCore.Qt.Checked)
        self.appendToSelectedSrc(item)
        self.refreshDest()

    def uncheckItem(self, item, *args, **kwargs):
        item.setCheckState(QtCore.Qt.Unchecked)
        self.removeToSelectedSrc(item)
        self.refreshDest()


    def setDestPath(self, path, *args, **kwargs):
        self.dest_path = path
        self.label_6.setText(_translate("MainWindow", self.dest_path))

    def _refreshSrcCombo(self, *args, **kwargs):
        self.comboBox_2.clear()
        for i, e in enumerate(self.src_ext):
            self.comboBox_2.addItem("")    
            self.comboBox_2.setItemText(i, _translate("MainWindow", e))


    def refreshDest(self, *args, **kwargs):
        self.listWidget_4.clear()
        self.dest_list = []
        for item in self.src_selected:
            out_text = srcToDest(item.text(), self.dest_path, self.out_ext)
            dest_item = self.makeItem(out_text, checked=None)
            self.dest_list.append(dest_item)
        
        self.showList("dest", self.listWidget_4)

    def pushToLog(self, text, stat, *args, **kwargs):
        lists_widget = [
            self.listWidget,
            self.listWidget_7,
        ]
        status = {
            "error": QtGui.QColor("red"),
            "warning": QtGui.QColor("orange"),
            "success": QtGui.QColor("green"),
            "info": QtGui.QColor("blue"),
        }
        for container in lists_widget:
            log_item = self.makeItem(text, checked=None)
            log_item.setForeground(status.get(stat, QtGui.QColor("black")))
            container.addItem(log_item)

    def makeItem(self, text, checked=False, *args, **kwargs):
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

    def startLoader(self):
        self.label_2.clear()
        movie = QtGui.QMovie("./loader.gif")
        self.label_2.setMovie(movie)
        movie.start()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

    def stopLoader(self):
        self.label_2.clear()

    def srcEmptyLog(self):
        self.pushToLog("""La source ne contient aucun élément !
            - Choississez un dossier source et sélectionnez des fichiers
            - Ouvrez un fichier depuis le menu Fichier"""
             , "error")



app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()