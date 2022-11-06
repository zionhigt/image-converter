from PyQt5 import QtWidgets, QtCore

import os

import humanize

from files.file_selector import select, getExtention, getSize, srcToDest

from converter.convert import converter, getPreview, ConverterDestExists, ConverterSrcNotExists

_translate = QtCore.QCoreApplication.translate


class Callback:
    def __init__(self, ui):
        self.ui = ui
    
    def init(self, declarations):
        for component, event_, method in declarations:
            connector = getattr(component, event_)
            if connector is not None:
                _method = getattr(self, method)
                if _method is not None:
                    connector.connect(_method)
                else:
                    print("Callback class has not method named %s" % method)
            else:
                print("No signal %s for component %s" % (event_, component))

    def getSrc(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            'Selectionnez un dossier d\'image:', self.ui.src_path,
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        # prevent cancel
        if dir_:
            self.setSrcPath(dir_)
            files = select(dir_)
            for i, f in enumerate(files):
                image_name = str(f)
                self.pushToSrcList(image_name)

            self.flushSrc()
    
    def setSrcPath(self, *args, **kwargs):
        return self.ui.setSrcPath(*args)
    
    def pushToSrcList(self, image_name):
        item = None
        src_items_text = [i.text() for i in self.ui.src_list]
        ext = getExtention(image_name)
        if (image_name not in src_items_text) and ext in self.ui.available_in_ext:
            item = self.ui.makeItem(image_name)
            self.ui.src_list.append(item)
            if not ext in self.ui.src_ext and ext in self.ui.available_in_ext:
                self.ui.src_ext.append(ext)
        return item

    def flushSrc(self):
        self.ui._refreshSrcCombo()
        self.ui.showList("src", self.ui.listWidget_3)
    
    def deleteSrc(self):
        if len(self.ui.src_selected):
            clean_src = [item for item in self.ui.src_list if item not in self.ui.src_selected]
            clean_src_ext = []
            for item in clean_src:
                ext = getExtention(item.text())
                if ext not in clean_src_ext:
                    clean_src_ext.append(ext)
            self.ui.src_ext = clean_src_ext
            self.ui.src_list = clean_src
            for item in self.ui.src_selected:
                index = self.ui.listWidget_3.row(item)
                if int(index) > -1:
                    self.ui.listWidget_3.takeItem(index)
            self.ui.src_selected = []
            self.flushSrc()
            self.ui.refreshDest()
        else:
            self.ui.pushToLog("Aucune selection à supprimer", "error")
    
    def getFile(self):
        image_filter = "Images files (%s)" % " ".join(["*" + i for i in self.ui.available_in_ext]) 
        image_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Selectionnez une image',
            self.ui.src_path,
            image_filter
        )
        if image_name:
            item = self.pushToSrcList(image_name)
            self.ui.checkItem(item)
            self.flushSrc()
    
    def getDest(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            'Select image folder:',
            self.ui.dest_path,
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        # prevent cancel
        dest_labels = [self.ui.label_6, self.ui.label_12]
        if dir_:
            for label in dest_labels:
                label.setText(_translate("MainWindow", dir_))
            self.ui.dest_path = dir_
            self.ui.refreshDest()
    
    def getCheckAllSrc(self):
        method = self.ui.checkItem
        if not self.ui.checkBox_2.isChecked():
            method = self.ui.uncheckItem
        for item in self.ui.src_list:
            method(item)

    def checkDestForce(self, *args, **kwargs):
        return self.ui.checkDestForce(*args)

    def filterSrc(self, value):
        filtered = [i for i in self.ui.src_list if (
            os.path.splitext(i.text())[1] == value
        )]
        for item in self.ui.src_list:
            self.ui.uncheckItem(item)
        for item in filtered:
            self.ui.checkItem(item)
        self.ui.src_selected = filtered

    def setOutExt(self, *args, **kwargs):
        return self.ui.setOutExt(*args)
    
    def convert(self):
        if len(self.ui.src_selected):
            sizes = []
            for i, item in enumerate(self.ui.src_selected):
                log = []
                try:
                    out_text = srcToDest(item.text(), self.ui.dest_path, self.ui.out_ext)
                    converter(item.text(), out_text, self.ui.out_ext, force=self.ui.dest_force)
                    
                    log = ["%s ---> %s" %(item.text(), out_text), "success"]
                    sizes.append((getSize(item.text()), getSize(out_text)))

                except ConverterSrcNotExists as e:
                    log = [str(e), "error"]
                except ConverterDestExists as e:
                    log = [str(e), "warning"]

                self.ui.pushToLog(*log)
                forwarding_ratio =  (i + 1) / len(self.ui.src_selected) * 100
                self.ui.progressBar.setProperty("value", forwarding_ratio)
            delta_size = sum([i[0][0] - i[1][0] for i in sizes])
            self.ui.pushToLog("%s %s" % (
                humanize.naturalsize(abs(delta_size)),
                " ont été libérés" if delta_size > 0 else " ont été ajoutés"
                ), "info")

        else:
            self.ui.srcEmptyLog()
            
    def srcItemChanged(self, item):
        method = self.ui.checkItem if int(item.checkState()) == 2 else self.ui.uncheckItem
        method(item)

    def gifPreview(self):
        if len(self.ui.src_selected):
            images = [i.text() for i in self.ui.src_selected]
            self.ui.startLoader()
            height = self.ui.label_2.height()
            buff = getPreview(images, self.ui.gif_speed, height)
            self.ui.stopLoader()
            self.ui.preview.refresh(buff)
        else:
            self.ui.srcEmptyLog()

    def speedChanged(fn):
        def wrap(self, value):
            self.ui.label_7.setText(_translate("MainWindow", "%s s"% value))
            return fn(self, value)
        return wrap

    @speedChanged
    def gifSpeedChange(self, value):
        self.ui.gif_speed = value
