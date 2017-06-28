#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui

__author__ = "ephtron"


class GestureCreationWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GestureCreationWidget, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.modified = False
        self.scribbeling = False
        self.penWidth = 4
        self.penColor = QtCore.Qt.white
        image_size = QtCore.QSize(100, 100)

        self.gesture_image = QtGui.QImage(image_size, QtGui.QImage.Format_RGB32)
        self.lastPoint = QtCore.QPoint
        self.setFixedSize(100, 100)

    def open_image(self, file_name):
        loaded_image = QtGui.QImage()
        if not loaded_image.load(file_name):
            return False

        w = loaded_image.width()
        h = loaded_image.height()
        # self.mainWindow.resize(w,h)

        self.gesture_image = loaded_image
        self.modified = False
        self.update()

    def open_qimage(self, qimage):
        loaded_image = qimage
        print("loaded image", loaded_image)

        self.gesture_image = loaded_image
        self.modified = False
        self.update()

    def save_image(self, file_name, file_format):
        visible_image = self.gesture_image
        self.resizeImage(visible_image, self.size())
        if visible_image.save(file_name, file_format):
            self.modified = False
            return True
        else:
            return False

    def setPenColor(self, new_color):
        self.penColor = new_color

    def setPenWidth(self, new_width):
        self.penWidth = new_width

    def clearImage(self):
        self.gesture_image.fill(QtGui.qRgb(0, 0, 0))
        # modified not needed here, as we only refresh after saving
        # self.modified = True
        self.update()

    def get_image(self):
        return self.gesture_image

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbeling = True

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton and self.scribbeling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton and self.scribbeling:
            self.drawLineTo(event.pos())
            self.scribbeling = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(event.rect(), self.gesture_image)

    def resizeEvent(self, event):
        self.resizeImage(self.gesture_image, event.size())
        super(GestureCreationWidget, self).resizeEvent(event)
        print("Resize", event.size())

    def drawLineTo(self, end_point):
        painter = QtGui.QPainter(self.gesture_image)
        painter.setPen(QtGui.QPen(self.penColor, self.penWidth,
                                  QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,
                                  QtCore.Qt.RoundJoin))
        painter.drawLine(QtCore.QPoint(self.lastPoint), QtCore.QPoint(end_point))
        self.modified = True

        self.update()
        self.lastPoint = QtCore.QPoint(end_point)

    def resizeImage(self, image, new_size):
        # print("WriterWidget - resizeImage:")
        print(new_size)
        if image.size() == new_size:
            return

        new_image = QtGui.QImage(new_size, QtGui.QImage.Format_RGB32)
        new_image.fill(QtGui.qRgb(255, 255, 255))
        painter = QtGui.QPainter(new_image)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.gesture_image = new_image

    def print_(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        print_dialog = QtGui.QPrintDialog(printer, self)
        if print_dialog.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size, QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(),
                                size.width(), size.height())
            painter.setWindow(self.gesture_image.rect())
            painter.drawImage(0, 0, self.gesture_image)
            painter.end()

    def isModified(self):
        return self.modified

    def getPenColor(self):
        return self.penColor

    def getPenWidth(self):
        return self.penWidth
