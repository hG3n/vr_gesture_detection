#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 10.05.17 10:43
@author: ephtron
"""

import os
from PyQt5 import QtWidgets, QtGui, QtCore
from scipy import misc

from lib.GestureCreationWidget import GestureCreationWidget
from lib.Recognizer import Recognizer

import lib.Utility


class RecogniceWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(RecogniceWidget, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.gesture_creator = GestureCreationWidget(self)
        self.gesture_creator.clearImage()

        self.dataset = None
        self.targets = None

        self.recognizer = Recognizer()

        self.learn_button = QtWidgets.QPushButton("Fit current gestures", self)
        self.layout.addWidget(self.learn_button)
        self.layout.addWidget(self.gesture_creator)

        @QtCore.pyqtSlot()
        def on_click_learn():
            print("learn")
            self.dataset, self.targets = lib.Utility.load_datasets("gestures/", 4)
            self.recognizer.initialize(self.dataset)

        self.learn_button.clicked.connect(on_click_learn)


        self.button_layout = QtWidgets.QHBoxLayout()
        self.clear_button = QtWidgets.QPushButton("Clear", self)
        self.button_layout.addWidget(self.clear_button)

        @QtCore.pyqtSlot()
        def on_click_clear():
            print("clear")
            self.gesture_creator.clearImage()

        _width = self.clear_button.fontMetrics().boundingRect("Clear").width() + 7
        self.clear_button.setMaximumWidth(_width)
        self.clear_button.clicked.connect(on_click_clear)

        self.predict_button = QtWidgets.QPushButton("Predict", self)
        self.button_layout.addWidget(self.predict_button)
        _width = self.predict_button.fontMetrics().boundingRect("Predict").width() + 7
        self.predict_button.setMaximumWidth(_width)
        self.predict_button.clicked.connect(self.predict_gesture_image)

        self.layout.addLayout(self.button_layout)

    def predict_gesture_image(self):
        _image = self.gesture_creator.get_image()
        _color_img = lib.Utility.qimage_to_image_array(_image)
        _grey_img = lib.Utility.ndarray_color_to_grey(_color_img)

        new_size = (16, 16)
        _grey_img_scaled = misc.imresize(_grey_img, new_size) / 16

        _grey_img_array = _grey_img_scaled.flatten()

        result = self.recognizer.predict([_grey_img_array])
        print(result)


