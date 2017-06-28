import os

from PyQt5 import QtCore, QtWidgets
from .GestureImageWidget import GestureImageWidget


class GestureEditDialog(QtWidgets.QDialog):
    new_image_signal = QtCore.pyqtSignal()

    def __init__(self, gesture_name, image_ids, parent=None):
        super(GestureEditDialog, self).__init__(parent)

        self.gesture_name = gesture_name
        self.image_ids = image_ids
        self.image_widgets = []
        self.layout = QtWidgets.QVBoxLayout(self)

        self.grid_layout = QtWidgets.QGridLayout()
        self.setup_grid()

        _hbox = QtWidgets.QHBoxLayout()
        self.exit_button = QtWidgets.QPushButton("Exit")
        _hbox.addWidget(self.exit_button)

        self.grid_box = QtWidgets.QGroupBox("All Gestures Images", self)
        self.grid_box.setLayout(self.grid_layout)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.grid_box)
        self.scroll.setWidgetResizable(True)

        self.layout.addWidget(self.scroll)
        self.layout.addLayout(_hbox)
        self.setLayout(self.layout)
        self.resize(1000, 900)

        @QtCore.pyqtSlot()
        def close():
            self.close()

        self.exit_button.clicked.connect(close)

    def setup_grid(self):
        _grid_width = 6
        if len(self.image_ids) > _grid_width:
            _positions = [(i, j) for i in range(_grid_width) for j in range(len(self.image_ids) // (_grid_width - 1) +1)]
        else:
            _positions = [(0, i) for i in range(len(self.image_ids))]
        for idx, image in enumerate(os.listdir("gestures/" + self.gesture_name)):
            if image.endswith(".jpeg"):
                _image_widget = GestureImageWidget(self.gesture_name, self.image_ids[idx], self)
                _image_widget.remove_image_signal.connect(self.update_grid)
                self.image_widgets.append(_image_widget)
                self.grid_layout.addWidget(_image_widget, *_positions[idx])

    def update_image_ids(self, ids):
        self.image_ids = ids
        self.update_grid()

    def update_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().deleteLater()

        self.setup_grid()


