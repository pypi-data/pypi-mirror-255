# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'boris/video_equalizer.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Equalizer(object):
    def setupUi(self, Equalizer):
        Equalizer.setObjectName("Equalizer")
        Equalizer.resize(388, 284)
        self.verticalLayout = QtWidgets.QVBoxLayout(Equalizer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_6 = QtWidgets.QLabel(Equalizer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.cb_player = QtWidgets.QComboBox(Equalizer)
        self.cb_player.setObjectName("cb_player")
        self.verticalLayout.addWidget(self.cb_player)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Equalizer)
        self.label.setMinimumSize(QtCore.QSize(70, 0))
        self.label.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.hs_brightness = QtWidgets.QSlider(Equalizer)
        self.hs_brightness.setMinimumSize(QtCore.QSize(200, 0))
        self.hs_brightness.setMaximumSize(QtCore.QSize(200, 16777215))
        self.hs_brightness.setMinimum(-100)
        self.hs_brightness.setProperty("value", 0)
        self.hs_brightness.setOrientation(QtCore.Qt.Horizontal)
        self.hs_brightness.setObjectName("hs_brightness")
        self.horizontalLayout.addWidget(self.hs_brightness)
        self.lb_brightness = QtWidgets.QLabel(Equalizer)
        self.lb_brightness.setMinimumSize(QtCore.QSize(25, 0))
        self.lb_brightness.setMaximumSize(QtCore.QSize(25, 16777215))
        self.lb_brightness.setObjectName("lb_brightness")
        self.horizontalLayout.addWidget(self.lb_brightness)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Equalizer)
        self.label_2.setMinimumSize(QtCore.QSize(70, 0))
        self.label_2.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.hs_contrast = QtWidgets.QSlider(Equalizer)
        self.hs_contrast.setMinimumSize(QtCore.QSize(200, 0))
        self.hs_contrast.setMaximumSize(QtCore.QSize(200, 16777215))
        self.hs_contrast.setMinimum(-100)
        self.hs_contrast.setProperty("value", 0)
        self.hs_contrast.setOrientation(QtCore.Qt.Horizontal)
        self.hs_contrast.setObjectName("hs_contrast")
        self.horizontalLayout_2.addWidget(self.hs_contrast)
        self.lb_contrast = QtWidgets.QLabel(Equalizer)
        self.lb_contrast.setMinimumSize(QtCore.QSize(25, 0))
        self.lb_contrast.setMaximumSize(QtCore.QSize(25, 16777215))
        self.lb_contrast.setObjectName("lb_contrast")
        self.horizontalLayout_2.addWidget(self.lb_contrast)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(Equalizer)
        self.label_3.setMinimumSize(QtCore.QSize(70, 0))
        self.label_3.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.hs_saturation = QtWidgets.QSlider(Equalizer)
        self.hs_saturation.setMinimumSize(QtCore.QSize(200, 0))
        self.hs_saturation.setMaximumSize(QtCore.QSize(200, 16777215))
        self.hs_saturation.setMinimum(-100)
        self.hs_saturation.setProperty("value", 0)
        self.hs_saturation.setOrientation(QtCore.Qt.Horizontal)
        self.hs_saturation.setObjectName("hs_saturation")
        self.horizontalLayout_3.addWidget(self.hs_saturation)
        self.lb_saturation = QtWidgets.QLabel(Equalizer)
        self.lb_saturation.setMinimumSize(QtCore.QSize(25, 0))
        self.lb_saturation.setMaximumSize(QtCore.QSize(25, 16777215))
        self.lb_saturation.setObjectName("lb_saturation")
        self.horizontalLayout_3.addWidget(self.lb_saturation)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(Equalizer)
        self.label_4.setMinimumSize(QtCore.QSize(70, 0))
        self.label_4.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.hs_gamma = QtWidgets.QSlider(Equalizer)
        self.hs_gamma.setMinimumSize(QtCore.QSize(200, 0))
        self.hs_gamma.setMaximumSize(QtCore.QSize(200, 16777215))
        self.hs_gamma.setMinimum(-100)
        self.hs_gamma.setProperty("value", 0)
        self.hs_gamma.setOrientation(QtCore.Qt.Horizontal)
        self.hs_gamma.setObjectName("hs_gamma")
        self.horizontalLayout_4.addWidget(self.hs_gamma)
        self.lb_gamma = QtWidgets.QLabel(Equalizer)
        self.lb_gamma.setMinimumSize(QtCore.QSize(25, 0))
        self.lb_gamma.setMaximumSize(QtCore.QSize(25, 16777215))
        self.lb_gamma.setObjectName("lb_gamma")
        self.horizontalLayout_4.addWidget(self.lb_gamma)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(Equalizer)
        self.label_5.setMinimumSize(QtCore.QSize(70, 0))
        self.label_5.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.hs_hue = QtWidgets.QSlider(Equalizer)
        self.hs_hue.setMinimumSize(QtCore.QSize(200, 0))
        self.hs_hue.setMaximumSize(QtCore.QSize(200, 16777215))
        self.hs_hue.setMinimum(-100)
        self.hs_hue.setProperty("value", 0)
        self.hs_hue.setOrientation(QtCore.Qt.Horizontal)
        self.hs_hue.setObjectName("hs_hue")
        self.horizontalLayout_5.addWidget(self.hs_hue)
        self.lb_hue = QtWidgets.QLabel(Equalizer)
        self.lb_hue.setMinimumSize(QtCore.QSize(25, 0))
        self.lb_hue.setMaximumSize(QtCore.QSize(25, 16777215))
        self.lb_hue.setObjectName("lb_hue")
        self.horizontalLayout_5.addWidget(self.lb_hue)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.pb_reset_all = QtWidgets.QPushButton(Equalizer)
        self.pb_reset_all.setObjectName("pb_reset_all")
        self.horizontalLayout_6.addWidget(self.pb_reset_all)
        self.pb_reset = QtWidgets.QPushButton(Equalizer)
        self.pb_reset.setObjectName("pb_reset")
        self.horizontalLayout_6.addWidget(self.pb_reset)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.pb_close = QtWidgets.QPushButton(Equalizer)
        self.pb_close.setObjectName("pb_close")
        self.horizontalLayout_7.addWidget(self.pb_close)
        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.retranslateUi(Equalizer)
        QtCore.QMetaObject.connectSlotsByName(Equalizer)

    def retranslateUi(self, Equalizer):
        _translate = QtCore.QCoreApplication.translate
        Equalizer.setWindowTitle(_translate("Equalizer", "Video equalizer"))
        self.label_6.setText(_translate("Equalizer", "Video equalizer"))
        self.label.setText(_translate("Equalizer", "Brightness"))
        self.lb_brightness.setText(_translate("Equalizer", "0"))
        self.label_2.setText(_translate("Equalizer", "Contrast"))
        self.lb_contrast.setText(_translate("Equalizer", "0"))
        self.label_3.setText(_translate("Equalizer", "Saturation"))
        self.lb_saturation.setText(_translate("Equalizer", "0"))
        self.label_4.setText(_translate("Equalizer", "Gamma"))
        self.lb_gamma.setText(_translate("Equalizer", "0"))
        self.label_5.setText(_translate("Equalizer", "Hue"))
        self.lb_hue.setText(_translate("Equalizer", "0"))
        self.pb_reset_all.setText(_translate("Equalizer", "Reset all players"))
        self.pb_reset.setText(_translate("Equalizer", "Reset current player"))
        self.pb_close.setText(_translate("Equalizer", "Close"))
