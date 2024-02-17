# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'boris/observation.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(959, 677)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lb_star = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lb_star.setFont(font)
        self.lb_star.setStyleSheet("color: red")
        self.lb_star.setObjectName("lb_star")
        self.horizontalLayout_2.addWidget(self.lb_star)
        self.leObservationId = QtWidgets.QLineEdit(Form)
        self.leObservationId.setObjectName("leObservationId")
        self.horizontalLayout_2.addWidget(self.leObservationId)
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_2.addWidget(self.label_8)
        self.dteDate = QtWidgets.QDateTimeEdit(Form)
        self.dteDate.setCalendarPopup(True)
        self.dteDate.setObjectName("dteDate")
        self.horizontalLayout_2.addWidget(self.dteDate)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_2.addWidget(self.label_9)
        self.teDescription = QtWidgets.QTextEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.teDescription.sizePolicy().hasHeightForWidth())
        self.teDescription.setSizePolicy(sizePolicy)
        self.teDescription.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.teDescription.setAcceptDrops(False)
        self.teDescription.setObjectName("teDescription")
        self.verticalLayout_2.addWidget(self.teDescription)
        self.cb_time_offset = QtWidgets.QCheckBox(self.layoutWidget)
        self.cb_time_offset.setObjectName("cb_time_offset")
        self.verticalLayout_2.addWidget(self.cb_time_offset)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.lbTimeOffset = QtWidgets.QLabel(self.layoutWidget)
        self.lbTimeOffset.setObjectName("lbTimeOffset")
        self.horizontalLayout_6.addWidget(self.lbTimeOffset)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.cb_observation_time_interval = QtWidgets.QCheckBox(self.layoutWidget)
        self.cb_observation_time_interval.setObjectName("cb_observation_time_interval")
        self.verticalLayout_2.addWidget(self.cb_observation_time_interval)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_11.addWidget(self.label_3)
        self.twIndepVariables = QtWidgets.QTableWidget(self.layoutWidget1)
        self.twIndepVariables.setObjectName("twIndepVariables")
        self.twIndepVariables.setColumnCount(3)
        self.twIndepVariables.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.twIndepVariables.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.twIndepVariables.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.twIndepVariables.setHorizontalHeaderItem(2, item)
        self.verticalLayout_11.addWidget(self.twIndepVariables)
        self.verticalLayout_6.addWidget(self.splitter)
        self.gb_observation_type = QtWidgets.QGroupBox(Form)
        self.gb_observation_type.setObjectName("gb_observation_type")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.gb_observation_type)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.rb_media_files = QtWidgets.QRadioButton(self.gb_observation_type)
        self.rb_media_files.setObjectName("rb_media_files")
        self.horizontalLayout_4.addWidget(self.rb_media_files)
        self.rb_live = QtWidgets.QRadioButton(self.gb_observation_type)
        self.rb_live.setObjectName("rb_live")
        self.horizontalLayout_4.addWidget(self.rb_live)
        self.rb_images = QtWidgets.QRadioButton(self.gb_observation_type)
        self.rb_images.setEnabled(True)
        self.rb_images.setObjectName("rb_images")
        self.horizontalLayout_4.addWidget(self.rb_images)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_4)
        self.verticalLayout_6.addWidget(self.gb_observation_type)
        self.sw_observation_type = QtWidgets.QStackedWidget(Form)
        self.sw_observation_type.setObjectName("sw_observation_type")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.sw_observation_type.addWidget(self.page)
        self.pg_media_files = QtWidgets.QWidget()
        self.pg_media_files.setObjectName("pg_media_files")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.pg_media_files)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.tabWidget = QtWidgets.QTabWidget(self.pg_media_files)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_player_1 = QtWidgets.QWidget()
        self.tab_player_1.setObjectName("tab_player_1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_player_1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.twVideo1 = QtWidgets.QTableWidget(self.tab_player_1)
        self.twVideo1.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.twVideo1.setAlternatingRowColors(True)
        self.twVideo1.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.twVideo1.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.twVideo1.setTextElideMode(QtCore.Qt.ElideNone)
        self.twVideo1.setObjectName("twVideo1")
        self.twVideo1.setColumnCount(7)
        self.twVideo1.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.twVideo1.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.twVideo1.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.twVideo1.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.twVideo1.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.twVideo1.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.twVideo1.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.twVideo1.setHorizontalHeaderItem(6, item)
        self.verticalLayout_3.addWidget(self.twVideo1)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pbAddVideo = QtWidgets.QPushButton(self.tab_player_1)
        self.pbAddVideo.setObjectName("pbAddVideo")
        self.horizontalLayout_3.addWidget(self.pbAddVideo)
        self.pbRemoveVideo = QtWidgets.QPushButton(self.tab_player_1)
        self.pbRemoveVideo.setObjectName("pbRemoveVideo")
        self.horizontalLayout_3.addWidget(self.pbRemoveVideo)
        self.pb_use_media_file_name_as_obsid = QtWidgets.QPushButton(self.tab_player_1)
        self.pb_use_media_file_name_as_obsid.setObjectName("pb_use_media_file_name_as_obsid")
        self.horizontalLayout_3.addWidget(self.pb_use_media_file_name_as_obsid)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.cbVisualizeSpectrogram = QtWidgets.QCheckBox(self.tab_player_1)
        self.cbVisualizeSpectrogram.setObjectName("cbVisualizeSpectrogram")
        self.horizontalLayout_15.addWidget(self.cbVisualizeSpectrogram)
        self.cb_visualize_waveform = QtWidgets.QCheckBox(self.tab_player_1)
        self.cb_visualize_waveform.setObjectName("cb_visualize_waveform")
        self.horizontalLayout_15.addWidget(self.cb_visualize_waveform)
        self.cb_media_creation_date_as_offset = QtWidgets.QCheckBox(self.tab_player_1)
        self.cb_media_creation_date_as_offset.setEnabled(False)
        self.cb_media_creation_date_as_offset.setObjectName("cb_media_creation_date_as_offset")
        self.horizontalLayout_15.addWidget(self.cb_media_creation_date_as_offset)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_5 = QtWidgets.QLabel(self.tab_player_1)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_12.addWidget(self.label_5)
        self.sb_media_scan_sampling = QtWidgets.QSpinBox(self.tab_player_1)
        self.sb_media_scan_sampling.setMaximum(1000000)
        self.sb_media_scan_sampling.setObjectName("sb_media_scan_sampling")
        self.horizontalLayout_12.addWidget(self.sb_media_scan_sampling)
        self.label_2 = QtWidgets.QLabel(self.tab_player_1)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_12.addWidget(self.label_2)
        self.sb_image_display_duration = QtWidgets.QSpinBox(self.tab_player_1)
        self.sb_image_display_duration.setMinimum(1)
        self.sb_image_display_duration.setMaximum(86400)
        self.sb_image_display_duration.setObjectName("sb_image_display_duration")
        self.horizontalLayout_12.addWidget(self.sb_image_display_duration)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem4)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.cbCloseCurrentBehaviorsBetweenVideo = QtWidgets.QCheckBox(self.tab_player_1)
        self.cbCloseCurrentBehaviorsBetweenVideo.setEnabled(False)
        self.cbCloseCurrentBehaviorsBetweenVideo.setObjectName("cbCloseCurrentBehaviorsBetweenVideo")
        self.verticalLayout.addWidget(self.cbCloseCurrentBehaviorsBetweenVideo)
        self.tabWidget.addTab(self.tab_player_1, "")
        self.tab_data_files = QtWidgets.QWidget()
        self.tab_data_files.setObjectName("tab_data_files")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.tab_data_files)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.splitter_5 = QtWidgets.QSplitter(self.tab_data_files)
        self.splitter_5.setOrientation(QtCore.Qt.Vertical)
        self.splitter_5.setObjectName("splitter_5")
        self.layoutWidget_4 = QtWidgets.QWidget(self.splitter_5)
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.layoutWidget_4)
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_7 = QtWidgets.QLabel(self.layoutWidget_4)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_15.addWidget(self.label_7)
        self.tw_data_files = QtWidgets.QTableWidget(self.layoutWidget_4)
        self.tw_data_files.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.tw_data_files.setObjectName("tw_data_files")
        self.tw_data_files.setColumnCount(9)
        self.tw_data_files.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_data_files.setHorizontalHeaderItem(8, item)
        self.verticalLayout_15.addWidget(self.tw_data_files)
        self.layoutWidget_5 = QtWidgets.QWidget(self.splitter_5)
        self.layoutWidget_5.setObjectName("layoutWidget_5")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.layoutWidget_5)
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pb_add_data_file = QtWidgets.QPushButton(self.layoutWidget_5)
        self.pb_add_data_file.setObjectName("pb_add_data_file")
        self.horizontalLayout_5.addWidget(self.pb_add_data_file)
        self.pb_remove_data_file = QtWidgets.QPushButton(self.layoutWidget_5)
        self.pb_remove_data_file.setObjectName("pb_remove_data_file")
        self.horizontalLayout_5.addWidget(self.pb_remove_data_file)
        self.pb_view_data_head = QtWidgets.QPushButton(self.layoutWidget_5)
        self.pb_view_data_head.setObjectName("pb_view_data_head")
        self.horizontalLayout_5.addWidget(self.pb_view_data_head)
        self.pb_plot_data = QtWidgets.QPushButton(self.layoutWidget_5)
        self.pb_plot_data.setObjectName("pb_plot_data")
        self.horizontalLayout_5.addWidget(self.pb_plot_data)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)
        self.verticalLayout_16.addLayout(self.horizontalLayout_5)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_16.addItem(spacerItem6)
        self.verticalLayout_17.addWidget(self.splitter_5)
        self.tabWidget.addTab(self.tab_data_files, "")
        self.verticalLayout_7.addWidget(self.tabWidget)
        self.sw_observation_type.addWidget(self.pg_media_files)
        self.pg_live = QtWidgets.QWidget()
        self.pg_live.setObjectName("pg_live")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.pg_live)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_4 = QtWidgets.QLabel(self.pg_live)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_8.addWidget(self.label_4)
        self.sbScanSampling = QtWidgets.QSpinBox(self.pg_live)
        self.sbScanSampling.setMaximum(1000000)
        self.sbScanSampling.setObjectName("sbScanSampling")
        self.horizontalLayout_8.addWidget(self.sbScanSampling)
        self.label_6 = QtWidgets.QLabel(self.pg_live)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_8.addWidget(self.label_6)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem7)
        self.verticalLayout_8.addLayout(self.horizontalLayout_8)
        self.cb_start_from_current_time = QtWidgets.QCheckBox(self.pg_live)
        self.cb_start_from_current_time.setObjectName("cb_start_from_current_time")
        self.verticalLayout_8.addWidget(self.cb_start_from_current_time)
        self.rb_day_time = QtWidgets.QRadioButton(self.pg_live)
        self.rb_day_time.setEnabled(False)
        self.rb_day_time.setChecked(True)
        self.rb_day_time.setObjectName("rb_day_time")
        self.verticalLayout_8.addWidget(self.rb_day_time)
        self.rb_epoch_time = QtWidgets.QRadioButton(self.pg_live)
        self.rb_epoch_time.setEnabled(False)
        self.rb_epoch_time.setObjectName("rb_epoch_time")
        self.verticalLayout_8.addWidget(self.rb_epoch_time)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem8)
        self.verticalLayout_4.addLayout(self.verticalLayout_8)
        self.sw_observation_type.addWidget(self.pg_live)
        self.pg_images = QtWidgets.QWidget()
        self.pg_images.setObjectName("pg_images")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.pg_images)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.lw_images_directory = QtWidgets.QListWidget(self.pg_images)
        self.lw_images_directory.setObjectName("lw_images_directory")
        self.horizontalLayout_9.addWidget(self.lw_images_directory)
        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        self.lb_images_info = QtWidgets.QLabel(self.pg_images)
        self.lb_images_info.setObjectName("lb_images_info")
        self.verticalLayout_5.addWidget(self.lb_images_info)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.pb_add_directory = QtWidgets.QPushButton(self.pg_images)
        self.pb_add_directory.setObjectName("pb_add_directory")
        self.horizontalLayout_14.addWidget(self.pb_add_directory)
        self.pb_remove_directory = QtWidgets.QPushButton(self.pg_images)
        self.pb_remove_directory.setObjectName("pb_remove_directory")
        self.horizontalLayout_14.addWidget(self.pb_remove_directory)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem9)
        self.verticalLayout_5.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.pb_use_img_dir_as_obsid = QtWidgets.QPushButton(self.pg_images)
        self.pb_use_img_dir_as_obsid.setObjectName("pb_use_img_dir_as_obsid")
        self.horizontalLayout_13.addWidget(self.pb_use_img_dir_as_obsid)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem10)
        self.verticalLayout_5.addLayout(self.horizontalLayout_13)
        self.groupBox = QtWidgets.QGroupBox(self.pg_images)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.rb_no_time = QtWidgets.QRadioButton(self.groupBox)
        self.rb_no_time.setObjectName("rb_no_time")
        self.horizontalLayout_10.addWidget(self.rb_no_time)
        self.rb_use_exif = QtWidgets.QRadioButton(self.groupBox)
        self.rb_use_exif.setObjectName("rb_use_exif")
        self.horizontalLayout_10.addWidget(self.rb_use_exif)
        self.rb_time_lapse = QtWidgets.QRadioButton(self.groupBox)
        self.rb_time_lapse.setObjectName("rb_time_lapse")
        self.horizontalLayout_10.addWidget(self.rb_time_lapse)
        self.sb_time_lapse = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.sb_time_lapse.setDecimals(3)
        self.sb_time_lapse.setMaximum(86400.0)
        self.sb_time_lapse.setObjectName("sb_time_lapse")
        self.horizontalLayout_10.addWidget(self.sb_time_lapse)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem11)
        self.horizontalLayout_11.addLayout(self.horizontalLayout_10)
        self.verticalLayout_5.addWidget(self.groupBox)
        self.sw_observation_type.addWidget(self.pg_images)
        self.verticalLayout_6.addWidget(self.sw_observation_type)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem12)
        self.pbCancel = QtWidgets.QPushButton(Form)
        self.pbCancel.setObjectName("pbCancel")
        self.horizontalLayout.addWidget(self.pbCancel)
        self.pbSave = QtWidgets.QPushButton(Form)
        self.pbSave.setObjectName("pbSave")
        self.horizontalLayout.addWidget(self.pbSave)
        self.pbLaunch = QtWidgets.QPushButton(Form)
        self.pbLaunch.setObjectName("pbLaunch")
        self.horizontalLayout.addWidget(self.pbLaunch)
        self.verticalLayout_6.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        self.sw_observation_type.setCurrentIndex(2)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "New observation"))
        self.label.setText(_translate("Form", "Observation id"))
        self.lb_star.setText(_translate("Form", "*"))
        self.label_8.setText(_translate("Form", "Date and time"))
        self.dteDate.setDisplayFormat(_translate("Form", "yyyy-MM-dd hh:mm:ss.zzz"))
        self.label_9.setText(_translate("Form", "Description"))
        self.cb_time_offset.setText(_translate("Form", "Time offset"))
        self.lbTimeOffset.setText(_translate("Form", "Time value"))
        self.cb_observation_time_interval.setText(_translate("Form", "Limit observation to a time interval"))
        self.label_3.setText(_translate("Form", "Independent variables"))
        item = self.twIndepVariables.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Variable"))
        item = self.twIndepVariables.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Type"))
        item = self.twIndepVariables.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Value"))
        self.gb_observation_type.setTitle(_translate("Form", "Observation type"))
        self.rb_media_files.setText(_translate("Form", "Observation from media file(s)"))
        self.rb_live.setText(_translate("Form", "Live observation"))
        self.rb_images.setText(_translate("Form", "Observation from pictures"))
        item = self.twVideo1.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Player"))
        item = self.twVideo1.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Offset (seconds)"))
        item = self.twVideo1.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Path"))
        item = self.twVideo1.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Duration"))
        item = self.twVideo1.horizontalHeaderItem(4)
        item.setText(_translate("Form", "FPS"))
        item = self.twVideo1.horizontalHeaderItem(5)
        item.setText(_translate("Form", "Video"))
        item = self.twVideo1.horizontalHeaderItem(6)
        item.setText(_translate("Form", "Audio"))
        self.pbAddVideo.setText(_translate("Form", "Add media"))
        self.pbRemoveVideo.setText(_translate("Form", "Remove selected media"))
        self.pb_use_media_file_name_as_obsid.setText(_translate("Form", "Use media file name as observation id"))
        self.cbVisualizeSpectrogram.setText(_translate("Form", "Visualize the sound spectrogram for the player #1"))
        self.cb_visualize_waveform.setText(_translate("Form", "Visualize the waveform for the player #1"))
        self.cb_media_creation_date_as_offset.setText(_translate("Form", "Use the media creation date/time metadata as offset"))
        self.label_5.setText(_translate("Form", "Scan sampling every (s)"))
        self.label_2.setText(_translate("Form", "Image display duration (s)"))
        self.cbCloseCurrentBehaviorsBetweenVideo.setText(_translate("Form", "Stop ongoing state events between successive media files"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_player_1), _translate("Form", "Media files"))
        self.label_7.setText(_translate("Form", "Data files to plot"))
        item = self.tw_data_files.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Path"))
        item = self.tw_data_files.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Columns to plot"))
        item = self.tw_data_files.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Plot title"))
        item = self.tw_data_files.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Variable name"))
        item = self.tw_data_files.horizontalHeaderItem(4)
        item.setText(_translate("Form", "Converters"))
        item = self.tw_data_files.horizontalHeaderItem(5)
        item.setText(_translate("Form", "Time interval (s)"))
        item = self.tw_data_files.horizontalHeaderItem(6)
        item.setText(_translate("Form", "Start position (s)"))
        item = self.tw_data_files.horizontalHeaderItem(7)
        item.setText(_translate("Form", "Substract first value"))
        item = self.tw_data_files.horizontalHeaderItem(8)
        item.setText(_translate("Form", "Color"))
        self.pb_add_data_file.setText(_translate("Form", "Add data file"))
        self.pb_remove_data_file.setText(_translate("Form", "Remove selected data file"))
        self.pb_view_data_head.setText(_translate("Form", "View data from file"))
        self.pb_plot_data.setText(_translate("Form", "Show plot"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_data_files), _translate("Form", "Data files"))
        self.label_4.setText(_translate("Form", "Scan sampling every"))
        self.label_6.setText(_translate("Form", "seconds"))
        self.cb_start_from_current_time.setText(_translate("Form", "Start from current time"))
        self.rb_day_time.setText(_translate("Form", "Day time"))
        self.rb_epoch_time.setText(_translate("Form", "Epoch time (seconds since 1970-01-01)"))
        self.lb_images_info.setText(_translate("Form", "Image info:"))
        self.pb_add_directory.setText(_translate("Form", "Add directory"))
        self.pb_remove_directory.setText(_translate("Form", "Remove directory"))
        self.pb_use_img_dir_as_obsid.setText(_translate("Form", "Use the pictures directory as observation id"))
        self.groupBox.setTitle(_translate("Form", "Time"))
        self.rb_no_time.setText(_translate("Form", "No time"))
        self.rb_use_exif.setText(_translate("Form", "Use the EXIF DateTimeOriginal tag"))
        self.rb_time_lapse.setText(_translate("Form", "Time lapse (s)"))
        self.pbCancel.setText(_translate("Form", "Cancel"))
        self.pbSave.setText(_translate("Form", "Save"))
        self.pbLaunch.setText(_translate("Form", "Start"))
