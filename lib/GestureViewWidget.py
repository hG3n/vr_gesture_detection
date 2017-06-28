import os, re
from PyQt5 import QtWidgets, QtGui, QtCore

from .GestureEditDialog import GestureEditDialog
from .GestureCreationDialog import GestureCreationDialog


class GestureViewWidget(QtWidgets.QWidget):
    def __init__(self, gesture_name, parent=None):
        super(GestureViewWidget, self).__init__(parent)

        self.gesture_name = gesture_name
        self.path = 'gestures/' + self.gesture_name + '/'
        self.ids = self.get_image_ids()
        print("Size:", len(self.ids))

        self.next_gesture_image_id = 0
        if len(self.ids) > 0:
            self.next_gesture_image_id = self.ids[-1] + 1
            print("next id: ", self.next_gesture_image_id)

        self.image_count = len([name for name in os.listdir('gestures/' + self.gesture_name) if name.endswith(".jpeg")])
        print(self.gesture_name + " with " + str(self.image_count) + " images")

        self.gesture_creation_dialog = GestureCreationDialog(self.gesture_name, self.next_gesture_image_id, self)
        self.gesture_creation_dialog.new_image_signal.connect(self.update_gesture)

        self.gesture_edit_dialog = GestureEditDialog(self.gesture_name, self.ids, self)

        self.label = QtWidgets.QLabel("Gesture " + self.gesture_name)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.label)

        self.image_label = QtWidgets.QLabel(self)
        if len(self.ids) > 0:
            self.sample_image = self.path + self.gesture_name + "_" + str(self.ids[0]) + ".jpeg"
            if os.path.exists(self.path):
                self.pixmap = QtGui.QPixmap(self.sample_image)
                self.pixmap = self.pixmap.scaled(64, 64)
                self.image_label.setPixmap(self.pixmap)
        self.layout.addWidget(self.image_label)

        self.button_layout = QtWidgets.QVBoxLayout()

        self.edit_button = QtWidgets.QPushButton("Edit Gesture Images", self)
        self.button_layout.addWidget(self.edit_button)

        self.add_button = QtWidgets.QPushButton("Add Gesture Image", self)
        self.button_layout.addWidget(self.add_button)

        self.layout.addLayout(self.button_layout)

        @QtCore.pyqtSlot()
        def on_click_edit():
            self.gesture_edit_dialog.exec_()

        self.edit_button.clicked.connect(on_click_edit)

        @QtCore.pyqtSlot()
        def on_click_creation():
            self.gesture_creation_dialog.exec_()

        self.add_button.clicked.connect(on_click_creation)
        self.setLayout(self.layout)

    def get_next_gesture_image_id(self):
        return self.next_gesture_image_id

    def update_gesture(self):
        self.ids = self.get_image_ids()
        if len(self.ids) > 0:
            self.next_gesture_image_id = self.ids[-1] + 1

        self.gesture_creation_dialog.update_image_id(self.next_gesture_image_id)
        self.gesture_edit_dialog.update_image_ids(self.ids)
        self.image_count = len(self.ids)
        print(self.gesture_name + " updated. Now has " + str(self.image_count) + " images")

        self.sample_image = self.path + self.gesture_name + "_" + str(self.ids[0]) + ".jpeg"
        if os.path.exists(self.path):
            self.pixmap = QtGui.QPixmap(self.sample_image)
            self.pixmap = self.pixmap.scaled(64, 64)
            self.image_label.setPixmap(self.pixmap)

    def get_image_ids(self):
        _ids = [int(re.findall('\d+', n)[0]) for n in os.listdir(self.path) if n.endswith(".jpeg")]
        _ids.sort()

        return _ids
