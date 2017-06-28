import os

from PyQt5 import QtCore, QtWidgets
from .GestureCreationWidget import GestureCreationWidget


class GestureCreationDialog(QtWidgets.QDialog):
    new_image_signal = QtCore.pyqtSignal()

    def __init__(self, gesture_name, image_id, parent=None):
        super(GestureCreationDialog, self).__init__(parent)

        self.gesture_name = gesture_name
        self.image_id = image_id

        self.initUI()

    def initUI(self):

        hbox = QtWidgets.QHBoxLayout()

        self.save_button = QtWidgets.QPushButton("Save",self)
        hbox.addWidget(self.save_button)

        self.exit_button = QtWidgets.QPushButton("Exit",self)
        hbox.addWidget(self.exit_button)

        self.gesture_creator = GestureCreationWidget(self)
        self.gesture_creator.clearImage()

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.gesture_creator)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        @QtCore.pyqtSlot()
        def save():
            file_format = "jpeg"
            self.saveFile(file_format)
            self.close()

        self.save_button.clicked.connect(save)

        @QtCore.pyqtSlot()
        def close():
            self.close()

        self.exit_button.clicked.connect(close)

    def load_image(self, qimage):
        print("load image")
        self.gesture_creator.open_qimage(qimage)

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()


    def update_image_id(self, id):
        self.image_id = id

    def maybeSave(self):
        if self.gesture_creator.isModified():
            ret = QtWidgets.QMessageBox.warning(self, "Symbol Editor",
                                                "The image has been modified.\n"
                                                "Do you want to save your changes?",
                                                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard |
                                                QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Save:
                return self.saveFile('jpeg')
            elif ret == QtWidgets.QMessageBox.Cancel:
                return False

        return True

    def saveFileAs(self, file_format):
        initialPath = QtCore.QDir.currentPath() \
                      + '/gestures/' \
                      + self.gesture_name \
                      + '/' \
                      + self.gesture_name + '_' + str(self.image_id) \
                      + '.' \
                      + file_format
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, "Save As",
                                                          initialPath,
                                                          "%s Files (*.%s);;All Files (*)" % (
                                                              file_format.upper(), file_format))
        if file_name:
            if self.gesture_creator.saveImage(file_name, file_format):
                self.new_image_signal.emit()
                self.gesture_creator.clearImage()
                self.close()
            else:
                return False
        return False

    def saveFile(self, file_format):
        file_name = QtCore.QDir.currentPath() \
                    + '/gestures/' \
                    + self.gesture_name \
                    + '/' \
                    + self.gesture_name \
                    + "_" + str(self.image_id) \
                    + '.' \
                    + str(file_format)
        if file_name:
            if self.gesture_creator.save_image(file_name, file_format):
                self.new_image_signal.emit()
                self.gesture_creator.clearImage()
                self.close()
            else:
                return False
        return False
