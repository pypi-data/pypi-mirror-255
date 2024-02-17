# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_prefDialog(object):
    def setupUi(self, prefDialog):
        prefDialog.setObjectName("prefDialog")
        prefDialog.setWindowModality(QtCore.Qt.WindowModal)
        prefDialog.resize(719, 554)
        self.gridLayout = QtWidgets.QGridLayout(prefDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(prefDialog)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_project = QtWidgets.QWidget()
        self.tab_project.setObjectName("tab_project")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_project)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label = QtWidgets.QLabel(self.tab_project)
        self.label.setObjectName("label")
        self.horizontalLayout_14.addWidget(self.label)
        self.cbTimeFormat = QtWidgets.QComboBox(self.tab_project)
        self.cbTimeFormat.setObjectName("cbTimeFormat")
        self.cbTimeFormat.addItem("")
        self.cbTimeFormat.addItem("")
        self.horizontalLayout_14.addWidget(self.cbTimeFormat)
        self.verticalLayout_5.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_6 = QtWidgets.QLabel(self.tab_project)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_15.addWidget(self.label_6)
        self.sbAutomaticBackup = QtWidgets.QSpinBox(self.tab_project)
        self.sbAutomaticBackup.setMinimum(-10000)
        self.sbAutomaticBackup.setMaximum(10000)
        self.sbAutomaticBackup.setProperty("value", 10)
        self.sbAutomaticBackup.setObjectName("sbAutomaticBackup")
        self.horizontalLayout_15.addWidget(self.sbAutomaticBackup)
        self.verticalLayout_5.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_3 = QtWidgets.QLabel(self.tab_project)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_13.addWidget(self.label_3)
        self.leSeparator = QtWidgets.QLineEdit(self.tab_project)
        self.leSeparator.setObjectName("leSeparator")
        self.horizontalLayout_13.addWidget(self.leSeparator)
        self.verticalLayout_5.addLayout(self.horizontalLayout_13)
        self.cbCheckForNewVersion = QtWidgets.QCheckBox(self.tab_project)
        self.cbCheckForNewVersion.setObjectName("cbCheckForNewVersion")
        self.verticalLayout_5.addWidget(self.cbCheckForNewVersion)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.lb_hwdec = QtWidgets.QLabel(self.tab_project)
        self.lb_hwdec.setObjectName("lb_hwdec")
        self.horizontalLayout_11.addWidget(self.lb_hwdec)
        self.cb_hwdec = QtWidgets.QComboBox(self.tab_project)
        self.cb_hwdec.setObjectName("cb_hwdec")
        self.horizontalLayout_11.addWidget(self.cb_hwdec)
        self.verticalLayout_5.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.lb_project_file_indent = QtWidgets.QLabel(self.tab_project)
        self.lb_project_file_indent.setObjectName("lb_project_file_indent")
        self.horizontalLayout_9.addWidget(self.lb_project_file_indent)
        self.combo_project_file_indentation = QtWidgets.QComboBox(self.tab_project)
        self.combo_project_file_indentation.setObjectName("combo_project_file_indentation")
        self.horizontalLayout_9.addWidget(self.combo_project_file_indentation)
        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.tabWidget.addTab(self.tab_project, "")
        self.tab_observations = QtWidgets.QWidget()
        self.tab_observations.setObjectName("tab_observations")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_observations)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.tab_observations)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.sbffSpeed = QtWidgets.QSpinBox(self.tab_observations)
        self.sbffSpeed.setMinimum(0)
        self.sbffSpeed.setMaximum(10000)
        self.sbffSpeed.setProperty("value", 10)
        self.sbffSpeed.setObjectName("sbffSpeed")
        self.horizontalLayout_4.addWidget(self.sbffSpeed)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.cb_adapt_fast_jump = QtWidgets.QCheckBox(self.tab_observations)
        self.cb_adapt_fast_jump.setObjectName("cb_adapt_fast_jump")
        self.verticalLayout.addWidget(self.cb_adapt_fast_jump)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.tab_observations)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.sbSpeedStep = QtWidgets.QDoubleSpinBox(self.tab_observations)
        self.sbSpeedStep.setDecimals(1)
        self.sbSpeedStep.setMinimum(0.1)
        self.sbSpeedStep.setMaximum(10.0)
        self.sbSpeedStep.setSingleStep(0.1)
        self.sbSpeedStep.setProperty("value", 0.1)
        self.sbSpeedStep.setObjectName("sbSpeedStep")
        self.horizontalLayout_5.addWidget(self.sbSpeedStep)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QtWidgets.QLabel(self.tab_observations)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        self.sbRepositionTimeOffset = QtWidgets.QSpinBox(self.tab_observations)
        self.sbRepositionTimeOffset.setMinimum(-10000)
        self.sbRepositionTimeOffset.setMaximum(10000)
        self.sbRepositionTimeOffset.setProperty("value", -3)
        self.sbRepositionTimeOffset.setObjectName("sbRepositionTimeOffset")
        self.horizontalLayout_6.addWidget(self.sbRepositionTimeOffset)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.cbConfirmSound = QtWidgets.QCheckBox(self.tab_observations)
        self.cbConfirmSound.setObjectName("cbConfirmSound")
        self.verticalLayout.addWidget(self.cbConfirmSound)
        self.cbCloseSameEvent = QtWidgets.QCheckBox(self.tab_observations)
        self.cbCloseSameEvent.setObjectName("cbCloseSameEvent")
        self.verticalLayout.addWidget(self.cbCloseSameEvent)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_8 = QtWidgets.QLabel(self.tab_observations)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_8.addWidget(self.label_8)
        self.sbBeepEvery = QtWidgets.QSpinBox(self.tab_observations)
        self.sbBeepEvery.setObjectName("sbBeepEvery")
        self.horizontalLayout_8.addWidget(self.sbBeepEvery)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.cb_display_subtitles = QtWidgets.QCheckBox(self.tab_observations)
        self.cb_display_subtitles.setObjectName("cb_display_subtitles")
        self.verticalLayout.addWidget(self.cb_display_subtitles)
        self.cbTrackingCursorAboveEvent = QtWidgets.QCheckBox(self.tab_observations)
        self.cbTrackingCursorAboveEvent.setObjectName("cbTrackingCursorAboveEvent")
        self.verticalLayout.addWidget(self.cbTrackingCursorAboveEvent)
        self.cbAlertNoFocalSubject = QtWidgets.QCheckBox(self.tab_observations)
        self.cbAlertNoFocalSubject.setObjectName("cbAlertNoFocalSubject")
        self.verticalLayout.addWidget(self.cbAlertNoFocalSubject)
        self.cb_pause_before_addevent = QtWidgets.QCheckBox(self.tab_observations)
        self.cb_pause_before_addevent.setObjectName("cb_pause_before_addevent")
        self.verticalLayout.addWidget(self.cb_pause_before_addevent)
        spacerItem1 = QtWidgets.QSpacerItem(20, 391, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab_observations, "")
        self.tab_ffmpeg = QtWidgets.QWidget()
        self.tab_ffmpeg.setObjectName("tab_ffmpeg")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_ffmpeg)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lbFFmpegPath = QtWidgets.QLabel(self.tab_ffmpeg)
        self.lbFFmpegPath.setScaledContents(False)
        self.lbFFmpegPath.setWordWrap(True)
        self.lbFFmpegPath.setObjectName("lbFFmpegPath")
        self.verticalLayout_3.addWidget(self.lbFFmpegPath)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lbFFmpegCacheDir = QtWidgets.QLabel(self.tab_ffmpeg)
        self.lbFFmpegCacheDir.setObjectName("lbFFmpegCacheDir")
        self.horizontalLayout_3.addWidget(self.lbFFmpegCacheDir)
        self.leFFmpegCacheDir = QtWidgets.QLineEdit(self.tab_ffmpeg)
        self.leFFmpegCacheDir.setObjectName("leFFmpegCacheDir")
        self.horizontalLayout_3.addWidget(self.leFFmpegCacheDir)
        self.pbBrowseFFmpegCacheDir = QtWidgets.QPushButton(self.tab_ffmpeg)
        self.pbBrowseFFmpegCacheDir.setObjectName("pbBrowseFFmpegCacheDir")
        self.horizontalLayout_3.addWidget(self.pbBrowseFFmpegCacheDir)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.tabWidget.addTab(self.tab_ffmpeg, "")
        self.tab_spectro = QtWidgets.QWidget()
        self.tab_spectro.setObjectName("tab_spectro")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tab_spectro)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_7 = QtWidgets.QLabel(self.tab_spectro)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_7.addWidget(self.label_7)
        self.cbSpectrogramColorMap = QtWidgets.QComboBox(self.tab_spectro)
        self.cbSpectrogramColorMap.setObjectName("cbSpectrogramColorMap")
        self.horizontalLayout_7.addWidget(self.cbSpectrogramColorMap)
        self.verticalLayout_8.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_12 = QtWidgets.QLabel(self.tab_spectro)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_10.addWidget(self.label_12)
        self.sb_time_interval = QtWidgets.QSpinBox(self.tab_spectro)
        self.sb_time_interval.setMinimum(2)
        self.sb_time_interval.setMaximum(360)
        self.sb_time_interval.setProperty("value", 10)
        self.sb_time_interval.setObjectName("sb_time_interval")
        self.horizontalLayout_10.addWidget(self.sb_time_interval)
        self.verticalLayout_8.addLayout(self.horizontalLayout_10)
        spacerItem3 = QtWidgets.QSpacerItem(20, 319, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem3)
        self.tabWidget.addTab(self.tab_spectro, "")
        self.tab_colors = QtWidgets.QWidget()
        self.tab_colors.setObjectName("tab_colors")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.tab_colors)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_10 = QtWidgets.QLabel(self.tab_colors)
        self.label_10.setOpenExternalLinks(True)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_6.addWidget(self.label_10)
        self.te_behav_colors = QtWidgets.QPlainTextEdit(self.tab_colors)
        self.te_behav_colors.setObjectName("te_behav_colors")
        self.verticalLayout_6.addWidget(self.te_behav_colors)
        self.pb_reset_behav_colors = QtWidgets.QPushButton(self.tab_colors)
        self.pb_reset_behav_colors.setObjectName("pb_reset_behav_colors")
        self.verticalLayout_6.addWidget(self.pb_reset_behav_colors)
        self.horizontalLayout_12.addLayout(self.verticalLayout_6)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_11 = QtWidgets.QLabel(self.tab_colors)
        self.label_11.setOpenExternalLinks(True)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_9.addWidget(self.label_11)
        self.te_category_colors = QtWidgets.QPlainTextEdit(self.tab_colors)
        self.te_category_colors.setObjectName("te_category_colors")
        self.verticalLayout_9.addWidget(self.te_category_colors)
        self.pb_reset_category_colors = QtWidgets.QPushButton(self.tab_colors)
        self.pb_reset_category_colors.setObjectName("pb_reset_category_colors")
        self.verticalLayout_9.addWidget(self.pb_reset_category_colors)
        self.horizontalLayout_12.addLayout(self.verticalLayout_9)
        self.verticalLayout_10.addLayout(self.horizontalLayout_12)
        self.tabWidget.addTab(self.tab_colors, "")
        self.tab_interface = QtWidgets.QWidget()
        self.tab_interface.setObjectName("tab_interface")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_interface)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_9 = QtWidgets.QLabel(self.tab_interface)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.sb_toolbar_icon_size = QtWidgets.QSpinBox(self.tab_interface)
        self.sb_toolbar_icon_size.setMinimum(12)
        self.sb_toolbar_icon_size.setMaximum(128)
        self.sb_toolbar_icon_size.setProperty("value", 24)
        self.sb_toolbar_icon_size.setObjectName("sb_toolbar_icon_size")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.sb_toolbar_icon_size)
        self.verticalLayout_7.addLayout(self.formLayout)
        self.tabWidget.addTab(self.tab_interface, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem4 = QtWidgets.QSpacerItem(241, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.pb_refresh = QtWidgets.QPushButton(prefDialog)
        self.pb_refresh.setObjectName("pb_refresh")
        self.horizontalLayout_2.addWidget(self.pb_refresh)
        self.pbCancel = QtWidgets.QPushButton(prefDialog)
        self.pbCancel.setObjectName("pbCancel")
        self.horizontalLayout_2.addWidget(self.pbCancel)
        self.pbOK = QtWidgets.QPushButton(prefDialog)
        self.pbOK.setObjectName("pbOK")
        self.horizontalLayout_2.addWidget(self.pbOK)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(prefDialog)
        self.tabWidget.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(prefDialog)

    def retranslateUi(self, prefDialog):
        _translate = QtCore.QCoreApplication.translate
        prefDialog.setWindowTitle(_translate("prefDialog", "Preferences"))
        self.label.setText(_translate("prefDialog", "Default project time format"))
        self.cbTimeFormat.setItemText(0, _translate("prefDialog", "seconds"))
        self.cbTimeFormat.setItemText(1, _translate("prefDialog", "hh:mm:ss.mss"))
        self.label_6.setText(_translate("prefDialog", "Auto-save project every (minutes)"))
        self.label_3.setText(_translate("prefDialog", "Separator for behavioural strings (events export)"))
        self.leSeparator.setText(_translate("prefDialog", "|"))
        self.cbCheckForNewVersion.setText(_translate("prefDialog", "Check for new version and news"))
        self.lb_hwdec.setText(_translate("prefDialog", "MPV player hardware video decoding"))
        self.lb_project_file_indent.setText(_translate("prefDialog", "Project file indentation type"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_project), _translate("prefDialog", "Project"))
        self.label_4.setText(_translate("prefDialog", "Fast forward/backward value (seconds)"))
        self.cb_adapt_fast_jump.setText(_translate("prefDialog", "Adapt the fast forward/backward jump to playback speed"))
        self.label_5.setText(_translate("prefDialog", "Playback speed step value"))
        self.label_2.setText(_translate("prefDialog", "Time offset for video/audio reposition (seconds)"))
        self.cbConfirmSound.setText(_translate("prefDialog", "Play sound when a key is pressed"))
        self.cbCloseSameEvent.setText(_translate("prefDialog", "Close the same current event independently of modifiers"))
        self.label_8.setText(_translate("prefDialog", "Beep every (seconds)"))
        self.cb_display_subtitles.setText(_translate("prefDialog", "Display subtitles"))
        self.cbTrackingCursorAboveEvent.setText(_translate("prefDialog", "Tracking cursor above current event"))
        self.cbAlertNoFocalSubject.setText(_translate("prefDialog", "Alert if focal subject is not set"))
        self.cb_pause_before_addevent.setText(_translate("prefDialog", "Pause media before \"Add event\" command"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_observations), _translate("prefDialog", "Observations"))
        self.lbFFmpegPath.setText(_translate("prefDialog", "FFmpeg path:"))
        self.lbFFmpegCacheDir.setText(_translate("prefDialog", "FFmpeg cache directory"))
        self.pbBrowseFFmpegCacheDir.setText(_translate("prefDialog", "..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ffmpeg), _translate("prefDialog", "FFmpeg framework"))
        self.label_7.setText(_translate("prefDialog", "Spectrogram color map"))
        self.label_12.setText(_translate("prefDialog", "Default time interval (s)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_spectro), _translate("prefDialog", "Spectrogram/Wave form"))
        self.label_10.setText(_translate("prefDialog", "<html><head/><body><p>List of colors for behaviors. See <a href=\"https://matplotlib.org/api/colors_api.html\"><span style=\" text-decoration: underline; color:#0000ff;\">matplotlib colors</span></a></p></body></html>"))
        self.pb_reset_behav_colors.setText(_translate("prefDialog", "Reset colors to default"))
        self.label_11.setText(_translate("prefDialog", "<html><head/><body><p>List of colors for behavioral categories. See <a href=\"https://matplotlib.org/api/colors_api.html\"><span style=\" text-decoration: underline; color:#0000ff;\">matplotlib colors</span></a></p></body></html>"))
        self.pb_reset_category_colors.setText(_translate("prefDialog", "Reset colors to default"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_colors), _translate("prefDialog", "Plot colors"))
        self.label_9.setText(_translate("prefDialog", "Toolbar icons size"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_interface), _translate("prefDialog", "Interface"))
        self.pb_refresh.setText(_translate("prefDialog", "Refresh"))
        self.pbCancel.setText(_translate("prefDialog", "Cancel"))
        self.pbOK.setText(_translate("prefDialog", "OK"))
