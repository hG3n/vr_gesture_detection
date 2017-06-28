from PyQt5 import QtWidgets, QtCore, QtGui

from lib.GestureParser import GestureParser, ScaleMode, save_image


class ConverterWidget(QtWidgets.QWidget):
    add_gesture_signal = QtCore.pyqtSignal(str)
    add_gesture_image_signal = QtCore.pyqtSignal(str, QtGui.QImage)

    def __init__(self, name, path, parent=None):
        super(ConverterWidget, self).__init__(parent)

        self.name = name
        self.path = path
        self.gesture_parser = GestureParser(SCALE_MODE=ScaleMode.SCALE_MAX, IMAGE_DIMENSION=32)

        self.label = QtWidgets.QLabel(self.name, self)
        self.image_label = QtWidgets.QLabel(self)
        self.pixmap = QtGui.QPixmap()
        _image_array = self.get_image_array()
        _image = self.convert_point_list_to_qimage(_image_array)
        self.pixmap = QtGui.QPixmap(_image)
        self.pixmap = self.pixmap.scaled(64, 64)
        self.image_label.setPixmap(self.pixmap)

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setPlaceholderText("Gesture Name")
        self.parse_button = QtWidgets.QPushButton("Convert to image", self)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.parse_button)


        @QtCore.pyqtSlot()
        def on_click():
            gesture_name = self.line_edit.text()
            if gesture_name:
                self.add_gesture_signal.emit(gesture_name)
                _img =  self.convert_point_list_to_qimage(self.get_image_array())
                self.add_gesture_image_signal.emit(gesture_name, _img)
                # self.save_image_array_as_image(self.get_image_array(), gesture_name)

                self.layout.removeWidget(self.line_edit)
                self.layout.removeWidget(self.parse_button)
                self.line_edit.deleteLater()
                self.parse_button.deleteLater()

        self.parse_button.clicked.connect(on_click)

    def get_image_array(self):
        _point_list = self.gesture_parser.convert_gpl_to_pointlist(self.path, self.name)
        _image_array = self.gesture_parser.convert_point_list_to_scaled_image_array(_point_list)
        return _image_array

    def convert_point_list_to_qimage(self, image_array):
        width = image_array.shape[0]
        height = image_array.shape[1]
        black = QtGui.QColor(0, 0, 0).rgb()
        white = QtGui.QColor(255, 255, 255).rgb()
        img = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
        for r in range(width):
            for c in range(height):

                if image_array[r, c] == 255:
                    img.setPixel(c, r, white)
                else:
                    img.setPixel(c, r, black)
        return img

    def save_image_array_as_image(self, image_array, gesture_name):
        _path = QtCore.QDir.currentPath() + '/gestures/' \
                + gesture_name + '/'
        _file_name = gesture_name + "_100"
        save_image(image_array, _path, _file_name, "jpeg")
