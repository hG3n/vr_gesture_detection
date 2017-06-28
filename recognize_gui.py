#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys

from PyQt5 import QtWidgets, QtCore
from lib.GestureViewWidget import GestureViewWidget
from lib.GestureAddWidget import GestureAddWidget
from lib.ConverterWidget import ConverterWidget
from lib.RecognizeWidget import RecogniceWidget


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        """
        Main widget that holds the different views on our symbols
        Additionally it offers the option to add a new symbol
        :param parent:
        """
        super(MainWidget, self).__init__(parent)

        self.gestures = []
        if not os.path.exists("gestures/"):
            os.makedirs("gestures/")

        for file in os.listdir("gestures/"):
            if not os.path.isfile(file):
                self.gestures.append(file)

        self.gesture_views = {}

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.recognizer_widget = RecogniceWidget(self)
        self.vbox.addWidget(self.recognizer_widget)

        self.gesture_adder = GestureAddWidget(self)
        self.gesture_adder.add_gesture_signal.connect(self.add_gesture)

        self.vbox.addWidget(self.gesture_adder)

        self.gestures_box = QtWidgets.QGroupBox("Known Gestures:", self)
        self.gestures_layout = QtWidgets.QVBoxLayout(self.gestures_box)
        # list all existing gestures
        for gesture in self.gestures:
            _gesture_view = GestureViewWidget(gesture, self)
            self.gestures_layout.addWidget(_gesture_view)
            self.gesture_views[gesture] = _gesture_view
        self.gestures_box.setLayout(self.gestures_layout)
        self.vbox.addWidget(self.gestures_box)

        self.capturings_box = QtWidgets.QGroupBox("Captured Point-Lists:", self)
        self.capturings_layout = QtWidgets.QVBoxLayout(self.capturings_box)

        self.refresh_button = QtWidgets.QPushButton("Refresh", self)
        self.capturings_layout.addWidget(self.refresh_button)
        # list all point_lists captured in our vr application
        self.point_list_path = "gesture_point_lists"
        print("POINT LIST PATH",self.point_list_path)

        @QtCore.pyqtSlot()
        def on_click_refresh():
            self.create_gpl_file_widgets()

        self.refresh_button.clicked.connect(on_click_refresh)

        self.read_new_gestures = []
        self.create_gpl_file_widgets()


        self.capturings_box.setLayout(self.capturings_layout)
        self.vbox.addWidget(self.capturings_box)

        self.box = QtWidgets.QGroupBox('Gesture Panel:', self)
        self.box.setLayout(self.vbox)

        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidget(self.box)
        self.scroll.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.scroll)

    def create_gpl_file_widgets(self):
        print("reading")
        for file in os.listdir(self.point_list_path):
            if file.endswith(".gpl") and file not in self.read_new_gestures:
                self.read_new_gestures.append(file)
                _parser_widget = ConverterWidget(file, self.point_list_path, self)
                self.capturings_layout.addWidget(_parser_widget)
                _parser_widget.add_gesture_signal.connect(self.add_gesture)
                _parser_widget.add_gesture_image_signal.connect(self.save_gesture_image)
                print(os.path.join("gesture_point_lists/", file))

    def add_gesture(self, gesture_name):
        if gesture_name not in self.gestures:

            directory = "gestures/" + gesture_name
            if not os.path.exists(directory):
                os.makedirs(directory)

            self.gestures.append(gesture_name)
            _gesture_view = GestureViewWidget(gesture_name, self)
            self.gestures_layout.addWidget(_gesture_view)
            self.gesture_views[gesture_name] = (_gesture_view)

    def save_gesture_image(self, gesture_name, gesture_image):
        _gesture_view = self.gesture_views[gesture_name]
        _id = _gesture_view.get_next_gesture_image_id()
        _file_format = "jpeg"
        _file_name = QtCore.QDir.currentPath() \
                     + '/gestures/' \
                     + gesture_name \
                     + '/' \
                     + gesture_name \
                     + "_" + str(_id) \
                     + '.' \
                     + str(_file_format)
        gesture_image.save(_file_name)
        self.gesture_views[gesture_name].update_gesture()


def main():
    app = QtWidgets.QApplication([])
    mw = QtWidgets.QMainWindow()
    mw.setWindowTitle("Recog - Nice")
    w = MainWidget(parent=mw)
    mw.setCentralWidget(w)
    mw.resize(600, 800)
    mw.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
