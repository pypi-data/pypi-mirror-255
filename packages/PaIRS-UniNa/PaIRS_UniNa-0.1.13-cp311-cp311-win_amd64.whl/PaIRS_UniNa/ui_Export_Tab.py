from .addwidgets_ps import icons_path
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Export_TabFZQKmm.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QRadioButton, QScrollArea, QSizePolicy, QSpacerItem,
    QToolButton, QVBoxLayout, QWidget)

from .addwidgets_ps import (CollapsibleBox, MyQDoubleSpin, MyQLineEdit, MyQSpin,
    MyQSpinXW, MyTabLabel, MyToolButton)

class Ui_ExportTab(object):
    def setupUi(self, ExportTab):
        if not ExportTab.objectName():
            ExportTab.setObjectName(u"ExportTab")
        ExportTab.resize(500, 680)
        ExportTab.setMinimumSize(QSize(260, 340))
        ExportTab.setMaximumSize(QSize(1000, 16777215))
        icon1 = QIcon()
        icon1.addFile(u""+ icons_path +"export_logo.png", QSize(), QIcon.Normal, QIcon.Off)
        ExportTab.setWindowIcon(icon1)
        self.verticalLayout = QVBoxLayout(ExportTab)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.w_Mode = QWidget(ExportTab)
        self.w_Mode.setObjectName(u"w_Mode")
        self.w_Mode.setMinimumSize(QSize(0, 40))
        self.w_Mode.setMaximumSize(QSize(16777215, 40))
        font = QFont()
        font.setPointSize(11)
        self.w_Mode.setFont(font)
        self.horizontalLayout_5 = QHBoxLayout(self.w_Mode)
        self.horizontalLayout_5.setSpacing(3)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 10)
        self.icon = QLabel(self.w_Mode)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(35, 35))
        self.icon.setMaximumSize(QSize(35, 35))
        self.icon.setPixmap(QPixmap(u""+ icons_path +"export_logo.png"))
        self.icon.setScaledContents(True)

        self.horizontalLayout_5.addWidget(self.icon)

        self.name_tab = MyTabLabel(self.w_Mode)
        self.name_tab.setObjectName(u"name_tab")
        self.name_tab.setMinimumSize(QSize(200, 35))
        self.name_tab.setMaximumSize(QSize(16777215, 35))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(20)
        font1.setBold(True)
        self.name_tab.setFont(font1)

        self.horizontalLayout_5.addWidget(self.name_tab)

        self.hs1 = QSpacerItem(70, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.hs1)

        self.label_number = QLabel(self.w_Mode)
        self.label_number.setObjectName(u"label_number")
        self.label_number.setMinimumSize(QSize(35, 0))
        font2 = QFont()
        font2.setPointSize(9)
        self.label_number.setFont(font2)
        self.label_number.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_number)

        self.hs = QSpacerItem(5, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.hs)

        self.button_back = QToolButton(self.w_Mode)
        self.button_back.setObjectName(u"button_back")
        self.button_back.setMinimumSize(QSize(24, 24))
        self.button_back.setMaximumSize(QSize(24, 24))
        icon2 = QIcon()
        icon2.addFile(u""+ icons_path +"undo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_back.setIcon(icon2)
        self.button_back.setIconSize(QSize(20, 20))

        self.horizontalLayout_5.addWidget(self.button_back)

        self.button_forward = QToolButton(self.w_Mode)
        self.button_forward.setObjectName(u"button_forward")
        self.button_forward.setMinimumSize(QSize(24, 24))
        self.button_forward.setMaximumSize(QSize(24, 24))
        icon3 = QIcon()
        icon3.addFile(u""+ icons_path +"redo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_forward.setIcon(icon3)
        self.button_forward.setIconSize(QSize(20, 20))

        self.horizontalLayout_5.addWidget(self.button_forward)

        self.w_button_close_tab = QWidget(self.w_Mode)
        self.w_button_close_tab.setObjectName(u"w_button_close_tab")
        self.w_button_close_tab.setMinimumSize(QSize(18, 24))
        self.w_button_close_tab.setMaximumSize(QSize(18, 24))
        self.horizontalLayout_15 = QHBoxLayout(self.w_button_close_tab)
        self.horizontalLayout_15.setSpacing(0)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, -1)
        self.button_close_tab = QToolButton(self.w_button_close_tab)
        self.button_close_tab.setObjectName(u"button_close_tab")
        self.button_close_tab.setMinimumSize(QSize(18, 18))
        self.button_close_tab.setMaximumSize(QSize(18, 18))
        self.button_close_tab.setLayoutDirection(Qt.LeftToRight)
        self.button_close_tab.setStyleSheet(u"QToolButton{\n"
"border-radius: 15px;\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u""+ icons_path +"close.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_close_tab.setIcon(icon4)
        self.button_close_tab.setIconSize(QSize(15, 15))

        self.horizontalLayout_15.addWidget(self.button_close_tab)


        self.horizontalLayout_5.addWidget(self.w_button_close_tab)


        self.verticalLayout.addWidget(self.w_Mode)

        self.line = QFrame(ExportTab)
        self.line.setObjectName(u"line")
        self.line.setMinimumSize(QSize(0, 5))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.scrollArea = QScrollArea(ExportTab)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QSize(0, 0))
        self.scrollArea.setMaximumSize(QSize(16777215, 16777215))
        self.scrollArea.setStyleSheet(u" QScrollArea {\n"
"        border: 1pix solid gray;\n"
"    }\n"
"\n"
"QScrollBar:horizontal\n"
"    {\n"
"        height: 15px;\n"
"        margin: 3px 10px 3px 10px;\n"
"        border: 1px transparent #2A2929;\n"
"        border-radius: 4px;\n"
"        background-color:  rgba(200,200,200,50);    /* #2A2929; */\n"
"    }\n"
"\n"
"QScrollBar::handle:horizontal\n"
"    {\n"
"        background-color: rgba(180,180,180,180);      /* #605F5F; */\n"
"        min-width: 5px;\n"
"        border-radius: 4px;\n"
"    }\n"
"\n"
"QScrollBar:vertical\n"
"    {\n"
"        background-color: rgba(200,200,200,50);  ;\n"
"        width: 15px;\n"
"        margin: 10px 3px 10px 3px;\n"
"        border: 1px transparent #2A2929;\n"
"        border-radius: 4px;\n"
"    }\n"
"\n"
"QScrollBar::handle:vertical\n"
"    {\n"
"        background-color: rgba(180,180,180,180);         /* #605F5F; */\n"
"        min-height: 5px;\n"
"        border-radius: 4px;\n"
"    }\n"
"\n"
"QScrollBar::add-line {\n"
"        border: none;\n"
"      "
                        "  background: none;\n"
"    }\n"
"\n"
"QScrollBar::sub-line {\n"
"        border: none;\n"
"        background: none;\n"
"    }\n"
"")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 487, 592))
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 0))
        self.scrollAreaWidgetContents.setStyleSheet(u"\u2020")
        self.verticalLayout_10 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_10.setSpacing(15)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 15, 10, 5)
        self.CollapBox_Flip = CollapsibleBox(self.scrollAreaWidgetContents)
        self.CollapBox_Flip.setObjectName(u"CollapBox_Flip")
        sizePolicy1.setHeightForWidth(self.CollapBox_Flip.sizePolicy().hasHeightForWidth())
        self.CollapBox_Flip.setSizePolicy(sizePolicy1)
        self.CollapBox_Flip.setMinimumSize(QSize(0, 230))
        self.CollapBox_Flip.setMaximumSize(QSize(16777215, 270))
        self.verticalLayout_24 = QVBoxLayout(self.CollapBox_Flip)
        self.verticalLayout_24.setSpacing(0)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.lay_CollapBox_Flip = QHBoxLayout()
        self.lay_CollapBox_Flip.setSpacing(0)
        self.lay_CollapBox_Flip.setObjectName(u"lay_CollapBox_Flip")
        self.lay_CollapBox_Flip.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.tool_CollapBox_Flip = QToolButton(self.CollapBox_Flip)
        self.tool_CollapBox_Flip.setObjectName(u"tool_CollapBox_Flip")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tool_CollapBox_Flip.sizePolicy().hasHeightForWidth())
        self.tool_CollapBox_Flip.setSizePolicy(sizePolicy2)
        self.tool_CollapBox_Flip.setMinimumSize(QSize(0, 20))
        self.tool_CollapBox_Flip.setMaximumSize(QSize(16777215, 20))
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(True)
        self.tool_CollapBox_Flip.setFont(font3)
        self.tool_CollapBox_Flip.setStyleSheet(u"QToolButton { border: none; }")
        self.tool_CollapBox_Flip.setCheckable(True)
        self.tool_CollapBox_Flip.setChecked(True)
        self.tool_CollapBox_Flip.setPopupMode(QToolButton.InstantPopup)
        self.tool_CollapBox_Flip.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tool_CollapBox_Flip.setArrowType(Qt.DownArrow)

        self.lay_CollapBox_Flip.addWidget(self.tool_CollapBox_Flip)

        self.hsp_CollapBox_Flip = QSpacerItem(100, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.lay_CollapBox_Flip.addItem(self.hsp_CollapBox_Flip)

        self.push_CollapBox_Flip = MyToolButton(self.CollapBox_Flip)
        self.push_CollapBox_Flip.setObjectName(u"push_CollapBox_Flip")
        self.push_CollapBox_Flip.setMinimumSize(QSize(18, 18))
        self.push_CollapBox_Flip.setMaximumSize(QSize(18, 18))
        self.push_CollapBox_Flip.setLayoutDirection(Qt.LeftToRight)
        self.push_CollapBox_Flip.setIcon(icon2)
        self.push_CollapBox_Flip.setIconSize(QSize(12, 12))

        self.lay_CollapBox_Flip.addWidget(self.push_CollapBox_Flip)


        self.verticalLayout_24.addLayout(self.lay_CollapBox_Flip)

        self.w_Flip_Image = QGroupBox(self.CollapBox_Flip)
        self.w_Flip_Image.setObjectName(u"w_Flip_Image")
        sizePolicy1.setHeightForWidth(self.w_Flip_Image.sizePolicy().hasHeightForWidth())
        self.w_Flip_Image.setSizePolicy(sizePolicy1)
        self.w_Flip_Image.setMinimumSize(QSize(0, 210))
        self.w_Flip_Image.setMaximumSize(QSize(16777215, 230))
        font4 = QFont()
        font4.setPointSize(10)
        font4.setBold(True)
        font4.setItalic(False)
        font4.setKerning(False)
        self.w_Flip_Image.setFont(font4)
        self.w_Flip_Image.setStyleSheet(u"QGroupBox{border: 1px solid gray; border-radius: 6px;}\n"
"")
        self.verticalLayout_15 = QVBoxLayout(self.w_Flip_Image)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(10, 5, 10, 5)
        self.w_SizeImg = QWidget(self.w_Flip_Image)
        self.w_SizeImg.setObjectName(u"w_SizeImg")
        self.w_SizeImg.setMinimumSize(QSize(0, 50))
        self.w_SizeImg.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_7 = QHBoxLayout(self.w_SizeImg)
        self.horizontalLayout_7.setSpacing(5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.w_x = QWidget(self.w_SizeImg)
        self.w_x.setObjectName(u"w_x")
        self.w_x.setMinimumSize(QSize(100, 44))
        self.w_x.setMaximumSize(QSize(150, 44))
        self.verticalLayout_19 = QVBoxLayout(self.w_x)
        self.verticalLayout_19.setSpacing(0)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.label_x = QLabel(self.w_x)
        self.label_x.setObjectName(u"label_x")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_x.sizePolicy().hasHeightForWidth())
        self.label_x.setSizePolicy(sizePolicy3)
        self.label_x.setMinimumSize(QSize(0, 20))
        self.label_x.setMaximumSize(QSize(90, 20))
        font5 = QFont()
        font5.setPointSize(10)
        font5.setBold(False)
        font5.setItalic(True)
        self.label_x.setFont(font5)
        self.label_x.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_19.addWidget(self.label_x)

        self.spin_x = MyQSpinXW(self.w_x)
        self.spin_x.setObjectName(u"spin_x")
        self.spin_x.setEnabled(True)
        self.spin_x.setMinimumSize(QSize(0, 24))
        self.spin_x.setMaximumSize(QSize(90, 24))
        self.spin_x.setFont(font)
        self.spin_x.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_x.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_x.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_x.setValue(1)

        self.verticalLayout_19.addWidget(self.spin_x)


        self.horizontalLayout_7.addWidget(self.w_x)

        self.w_y = QWidget(self.w_SizeImg)
        self.w_y.setObjectName(u"w_y")
        self.w_y.setMinimumSize(QSize(100, 44))
        self.w_y.setMaximumSize(QSize(150, 44))
        self.verticalLayout_20 = QVBoxLayout(self.w_y)
        self.verticalLayout_20.setSpacing(0)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.label_y = QLabel(self.w_y)
        self.label_y.setObjectName(u"label_y")
        sizePolicy3.setHeightForWidth(self.label_y.sizePolicy().hasHeightForWidth())
        self.label_y.setSizePolicy(sizePolicy3)
        self.label_y.setMinimumSize(QSize(0, 20))
        self.label_y.setMaximumSize(QSize(90, 20))
        self.label_y.setFont(font5)
        self.label_y.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_20.addWidget(self.label_y)

        self.spin_y = MyQSpinXW(self.w_y)
        self.spin_y.setObjectName(u"spin_y")
        self.spin_y.setEnabled(True)
        self.spin_y.setMinimumSize(QSize(0, 24))
        self.spin_y.setMaximumSize(QSize(90, 24))
        self.spin_y.setFont(font)
        self.spin_y.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_y.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_y.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_y.setValue(1)

        self.verticalLayout_20.addWidget(self.spin_y)


        self.horizontalLayout_7.addWidget(self.w_y)

        self.w_width = QWidget(self.w_SizeImg)
        self.w_width.setObjectName(u"w_width")
        self.w_width.setMinimumSize(QSize(100, 44))
        self.w_width.setMaximumSize(QSize(150, 44))
        self.verticalLayout_21 = QVBoxLayout(self.w_width)
        self.verticalLayout_21.setSpacing(0)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.label_w = QLabel(self.w_width)
        self.label_w.setObjectName(u"label_w")
        sizePolicy3.setHeightForWidth(self.label_w.sizePolicy().hasHeightForWidth())
        self.label_w.setSizePolicy(sizePolicy3)
        self.label_w.setMinimumSize(QSize(0, 20))
        self.label_w.setMaximumSize(QSize(90, 20))
        self.label_w.setFont(font5)
        self.label_w.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_21.addWidget(self.label_w)

        self.spin_w = MyQSpin(self.w_width)
        self.spin_w.setObjectName(u"spin_w")
        self.spin_w.setEnabled(True)
        self.spin_w.setMinimumSize(QSize(0, 24))
        self.spin_w.setMaximumSize(QSize(90, 24))
        self.spin_w.setFont(font)
        self.spin_w.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_w.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_w.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_w.setValue(1)

        self.verticalLayout_21.addWidget(self.spin_w)


        self.horizontalLayout_7.addWidget(self.w_width)

        self.w_height = QWidget(self.w_SizeImg)
        self.w_height.setObjectName(u"w_height")
        self.w_height.setMinimumSize(QSize(100, 44))
        self.w_height.setMaximumSize(QSize(150, 44))
        self.verticalLayout_22 = QVBoxLayout(self.w_height)
        self.verticalLayout_22.setSpacing(0)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.label_h = QLabel(self.w_height)
        self.label_h.setObjectName(u"label_h")
        sizePolicy3.setHeightForWidth(self.label_h.sizePolicy().hasHeightForWidth())
        self.label_h.setSizePolicy(sizePolicy3)
        self.label_h.setMinimumSize(QSize(0, 20))
        self.label_h.setMaximumSize(QSize(90, 20))
        self.label_h.setFont(font5)
        self.label_h.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_22.addWidget(self.label_h)

        self.spin_h = MyQSpin(self.w_height)
        self.spin_h.setObjectName(u"spin_h")
        self.spin_h.setEnabled(True)
        self.spin_h.setMinimumSize(QSize(0, 24))
        self.spin_h.setMaximumSize(QSize(90, 24))
        self.spin_h.setFont(font)
        self.spin_h.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_h.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_h.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_h.setValue(1)

        self.verticalLayout_22.addWidget(self.spin_h)


        self.horizontalLayout_7.addWidget(self.w_height)

        self.w_button_resize = QWidget(self.w_SizeImg)
        self.w_button_resize.setObjectName(u"w_button_resize")
        self.w_button_resize.setMinimumSize(QSize(0, 44))
        self.w_button_resize.setMaximumSize(QSize(26, 44))
        self.verticalLayout_11 = QVBoxLayout(self.w_button_resize)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.label_button_resize = QLabel(self.w_button_resize)
        self.label_button_resize.setObjectName(u"label_button_resize")
        sizePolicy3.setHeightForWidth(self.label_button_resize.sizePolicy().hasHeightForWidth())
        self.label_button_resize.setSizePolicy(sizePolicy3)
        self.label_button_resize.setMinimumSize(QSize(0, 18))
        self.label_button_resize.setMaximumSize(QSize(16777215, 18))
        self.label_button_resize.setFont(font5)

        self.verticalLayout_11.addWidget(self.label_button_resize)

        self.button_resize = QToolButton(self.w_button_resize)
        self.button_resize.setObjectName(u"button_resize")
        self.button_resize.setMinimumSize(QSize(26, 26))
        self.button_resize.setMaximumSize(QSize(26, 26))
        icon5 = QIcon()
        icon5.addFile(u""+ icons_path +"resize_icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_resize.setIcon(icon5)
        self.button_resize.setIconSize(QSize(18, 18))

        self.verticalLayout_11.addWidget(self.button_resize)


        self.horizontalLayout_7.addWidget(self.w_button_resize)

        self.hs_SizeImg = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.hs_SizeImg)

        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 1)
        self.horizontalLayout_7.setStretch(2, 1)
        self.horizontalLayout_7.setStretch(3, 1)
        self.horizontalLayout_7.setStretch(4, 1)
        self.horizontalLayout_7.setStretch(5, 1)

        self.verticalLayout_15.addWidget(self.w_SizeImg)

        self.w_Flip_Mirror = QWidget(self.w_Flip_Image)
        self.w_Flip_Mirror.setObjectName(u"w_Flip_Mirror")
        self.w_Flip_Mirror.setMinimumSize(QSize(0, 150))
        self.horizontalLayout_4 = QHBoxLayout(self.w_Flip_Mirror)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.w_Tools = QWidget(self.w_Flip_Mirror)
        self.w_Tools.setObjectName(u"w_Tools")
        self.w_Tools.setMinimumSize(QSize(140, 140))
        self.w_Tools.setMaximumSize(QSize(140, 140))
        self.verticalLayout_12 = QVBoxLayout(self.w_Tools)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 10)
        self.w_reset_rot_flip = QWidget(self.w_Tools)
        self.w_reset_rot_flip.setObjectName(u"w_reset_rot_flip")
        self.horizontalLayout_14 = QHBoxLayout(self.w_reset_rot_flip)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.label_Image_tool = QLabel(self.w_reset_rot_flip)
        self.label_Image_tool.setObjectName(u"label_Image_tool")
        self.label_Image_tool.setMinimumSize(QSize(50, 30))
        self.label_Image_tool.setMaximumSize(QSize(60, 30))
        self.label_Image_tool.setFont(font5)
        self.label_Image_tool.setStyleSheet(u"border: none;")
        self.label_Image_tool.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.horizontalLayout_14.addWidget(self.label_Image_tool)

        self.hs_image = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.hs_image)

        self.button_reset_rot_flip = QToolButton(self.w_reset_rot_flip)
        self.button_reset_rot_flip.setObjectName(u"button_reset_rot_flip")
        self.button_reset_rot_flip.setMinimumSize(QSize(25, 25))
        self.button_reset_rot_flip.setMaximumSize(QSize(25, 25))
        icon6 = QIcon()
        icon6.addFile(u""+ icons_path +"reset.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_reset_rot_flip.setIcon(icon6)
        self.button_reset_rot_flip.setIconSize(QSize(18, 18))

        self.horizontalLayout_14.addWidget(self.button_reset_rot_flip)

        self.hs_image_2 = QSpacerItem(8, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.hs_image_2)


        self.verticalLayout_12.addWidget(self.w_reset_rot_flip)

        self.w_Image_tool = QWidget(self.w_Tools)
        self.w_Image_tool.setObjectName(u"w_Image_tool")
        self.w_Image_tool.setMinimumSize(QSize(0, 30))
        self.w_Image_tool.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_6 = QHBoxLayout(self.w_Image_tool)
        self.horizontalLayout_6.setSpacing(5)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.button_rot_counter = QToolButton(self.w_Image_tool)
        self.button_rot_counter.setObjectName(u"button_rot_counter")
        self.button_rot_counter.setMinimumSize(QSize(30, 30))
        self.button_rot_counter.setMaximumSize(QSize(30, 30))
        icon7 = QIcon()
        icon7.addFile(u""+ icons_path +"rotate_counter.png", QSize(), QIcon.Normal, QIcon.Off)
        icon7.addFile(u""+ icons_path +"rotate_counter.png", QSize(), QIcon.Selected, QIcon.On)
        self.button_rot_counter.setIcon(icon7)
        self.button_rot_counter.setIconSize(QSize(28, 28))

        self.horizontalLayout_6.addWidget(self.button_rot_counter)

        self.button_rot_clock = QToolButton(self.w_Image_tool)
        self.button_rot_clock.setObjectName(u"button_rot_clock")
        self.button_rot_clock.setMinimumSize(QSize(30, 30))
        self.button_rot_clock.setMaximumSize(QSize(30, 30))
        icon8 = QIcon()
        icon8.addFile(u""+ icons_path +"rotate_clock.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_rot_clock.setIcon(icon8)
        self.button_rot_clock.setIconSize(QSize(28, 28))

        self.horizontalLayout_6.addWidget(self.button_rot_clock)

        self.button_mirror_y = QToolButton(self.w_Image_tool)
        self.button_mirror_y.setObjectName(u"button_mirror_y")
        self.button_mirror_y.setMinimumSize(QSize(30, 30))
        self.button_mirror_y.setMaximumSize(QSize(30, 30))
        icon9 = QIcon()
        icon9.addFile(u""+ icons_path +"mirror_x.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_mirror_y.setIcon(icon9)
        self.button_mirror_y.setIconSize(QSize(28, 28))

        self.horizontalLayout_6.addWidget(self.button_mirror_y)

        self.button_mirror_x = QToolButton(self.w_Image_tool)
        self.button_mirror_x.setObjectName(u"button_mirror_x")
        self.button_mirror_x.setMinimumSize(QSize(30, 30))
        self.button_mirror_x.setMaximumSize(QSize(30, 30))
        icon10 = QIcon()
        icon10.addFile(u""+ icons_path +"mirror_y.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_mirror_x.setIcon(icon10)
        self.button_mirror_x.setIconSize(QSize(28, 28))

        self.horizontalLayout_6.addWidget(self.button_mirror_x)


        self.verticalLayout_12.addWidget(self.w_Image_tool)

        self.label_Velocity_tool = QLabel(self.w_Tools)
        self.label_Velocity_tool.setObjectName(u"label_Velocity_tool")
        self.label_Velocity_tool.setMinimumSize(QSize(50, 25))
        self.label_Velocity_tool.setMaximumSize(QSize(60, 25))
        self.label_Velocity_tool.setFont(font5)
        self.label_Velocity_tool.setStyleSheet(u"border: none;")
        self.label_Velocity_tool.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_12.addWidget(self.label_Velocity_tool)

        self.w_Velocity_tool = QWidget(self.w_Tools)
        self.w_Velocity_tool.setObjectName(u"w_Velocity_tool")
        self.w_Velocity_tool.setMinimumSize(QSize(0, 30))
        self.w_Velocity_tool.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_12 = QHBoxLayout(self.w_Velocity_tool)
        self.horizontalLayout_12.setSpacing(5)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.button_rotv_counter = QToolButton(self.w_Velocity_tool)
        self.button_rotv_counter.setObjectName(u"button_rotv_counter")
        self.button_rotv_counter.setMinimumSize(QSize(30, 30))
        self.button_rotv_counter.setMaximumSize(QSize(30, 30))
        icon11 = QIcon()
        icon11.addFile(u""+ icons_path +"rotate_v_counter.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_rotv_counter.setIcon(icon11)
        self.button_rotv_counter.setIconSize(QSize(26, 26))

        self.horizontalLayout_12.addWidget(self.button_rotv_counter)

        self.button_rotv_clock = QToolButton(self.w_Velocity_tool)
        self.button_rotv_clock.setObjectName(u"button_rotv_clock")
        self.button_rotv_clock.setMinimumSize(QSize(30, 30))
        self.button_rotv_clock.setMaximumSize(QSize(30, 30))
        icon12 = QIcon()
        icon12.addFile(u""+ icons_path +"rotate_v_clock.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_rotv_clock.setIcon(icon12)
        self.button_rotv_clock.setIconSize(QSize(26, 26))

        self.horizontalLayout_12.addWidget(self.button_rotv_clock)

        self.button_flip_u = QToolButton(self.w_Velocity_tool)
        self.button_flip_u.setObjectName(u"button_flip_u")
        self.button_flip_u.setMinimumSize(QSize(30, 30))
        self.button_flip_u.setMaximumSize(QSize(30, 30))
        icon13 = QIcon()
        icon13.addFile(u""+ icons_path +"mirror_u.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_flip_u.setIcon(icon13)
        self.button_flip_u.setIconSize(QSize(28, 28))

        self.horizontalLayout_12.addWidget(self.button_flip_u)

        self.button_flip_v = QToolButton(self.w_Velocity_tool)
        self.button_flip_v.setObjectName(u"button_flip_v")
        self.button_flip_v.setMinimumSize(QSize(30, 30))
        self.button_flip_v.setMaximumSize(QSize(30, 30))
        icon14 = QIcon()
        icon14.addFile(u""+ icons_path +"mirror_v.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_flip_v.setIcon(icon14)
        self.button_flip_v.setIconSize(QSize(28, 28))

        self.horizontalLayout_12.addWidget(self.button_flip_v)


        self.verticalLayout_12.addWidget(self.w_Velocity_tool)


        self.horizontalLayout_4.addWidget(self.w_Tools)

        self.hs_flip_image = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.hs_flip_image)

        self.w_Images_ex = QWidget(self.w_Flip_Mirror)
        self.w_Images_ex.setObjectName(u"w_Images_ex")
        self.w_Images_ex.setMinimumSize(QSize(0, 140))
        self.w_Images_ex.setMaximumSize(QSize(16777215, 140))
        self.horizontalLayout_16 = QHBoxLayout(self.w_Images_ex)
        self.horizontalLayout_16.setSpacing(0)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.w_Im_ex = QWidget(self.w_Images_ex)
        self.w_Im_ex.setObjectName(u"w_Im_ex")
        self.w_Im_ex.setMinimumSize(QSize(100, 140))
        self.w_Im_ex.setMaximumSize(QSize(100, 140))
        self.verticalLayout_16 = QVBoxLayout(self.w_Im_ex)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.label_Im_example = QLabel(self.w_Im_ex)
        self.label_Im_example.setObjectName(u"label_Im_example")
        self.label_Im_example.setMinimumSize(QSize(100, 0))
        self.label_Im_example.setMaximumSize(QSize(100, 20))
        self.label_Im_example.setFont(font5)
        self.label_Im_example.setStyleSheet(u"border: none;")
        self.label_Im_example.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.label_Im_example)

        self.w_Im_example = QWidget(self.w_Im_ex)
        self.w_Im_example.setObjectName(u"w_Im_example")
        self.w_Im_example.setMinimumSize(QSize(100, 100))
        self.w_Im_example.setMaximumSize(QSize(100, 100))
        self.aim = QLabel(self.w_Im_example)
        self.aim.setObjectName(u"aim")
        self.aim.setGeometry(QRect(0, 30, 100, 70))
        sizePolicy.setHeightForWidth(self.aim.sizePolicy().hasHeightForWidth())
        self.aim.setSizePolicy(sizePolicy)
        self.aim.setMinimumSize(QSize(100, 70))
        self.aim.setMaximumSize(QSize(100, 70))
        self.aim.setPixmap(QPixmap(u""+ icons_path +"axes.png"))
        self.aim.setScaledContents(True)
        self.bim = QLabel(self.w_Im_example)
        self.bim.setObjectName(u"bim")
        self.bim.setGeometry(QRect(5, 35, 90, 60))
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.bim.sizePolicy().hasHeightForWidth())
        self.bim.setSizePolicy(sizePolicy4)
        self.bim.setMinimumSize(QSize(90, 60))
        self.bim.setMaximumSize(QSize(90, 60))
        self.bim.setPixmap(QPixmap(u""+ icons_path +"background_vectors.png"))
        self.bim.setScaledContents(True)
        self.bim.setIndent(2)
        self.bim.raise_()
        self.aim.raise_()

        self.verticalLayout_16.addWidget(self.w_Im_example)

        self.w_lab_op = QWidget(self.w_Im_ex)
        self.w_lab_op.setObjectName(u"w_lab_op")
        self.horizontalLayout_17 = QHBoxLayout(self.w_lab_op)
        self.horizontalLayout_17.setSpacing(5)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(0, 0, 20, 0)
        self.lab_op1 = QLabel(self.w_lab_op)
        self.lab_op1.setObjectName(u"lab_op1")
        self.lab_op1.setMinimumSize(QSize(20, 20))
        self.lab_op1.setMaximumSize(QSize(20, 20))
        self.lab_op1.setFont(font5)
        self.lab_op1.setStyleSheet(u"border: none;")
        self.lab_op1.setScaledContents(True)
        self.lab_op1.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_17.addWidget(self.lab_op1)

        self.lab_op2 = QLabel(self.w_lab_op)
        self.lab_op2.setObjectName(u"lab_op2")
        self.lab_op2.setMinimumSize(QSize(20, 20))
        self.lab_op2.setMaximumSize(QSize(20, 20))
        self.lab_op2.setFont(font5)
        self.lab_op2.setStyleSheet(u"border: none;")
        self.lab_op2.setScaledContents(True)
        self.lab_op2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_17.addWidget(self.lab_op2)

        self.lab_op3 = QLabel(self.w_lab_op)
        self.lab_op3.setObjectName(u"lab_op3")
        self.lab_op3.setMinimumSize(QSize(20, 20))
        self.lab_op3.setMaximumSize(QSize(20, 20))
        self.lab_op3.setFont(font5)
        self.lab_op3.setStyleSheet(u"border: none;")
        self.lab_op3.setScaledContents(True)
        self.lab_op3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_17.addWidget(self.lab_op3)


        self.verticalLayout_16.addWidget(self.w_lab_op)


        self.horizontalLayout_16.addWidget(self.w_Im_ex)

        self.hs_Images_ex = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.hs_Images_ex)

        self.w_Im_ex_2 = QWidget(self.w_Images_ex)
        self.w_Im_ex_2.setObjectName(u"w_Im_ex_2")
        self.w_Im_ex_2.setMinimumSize(QSize(100, 140))
        self.w_Im_ex_2.setMaximumSize(QSize(100, 140))
        self.verticalLayout_14 = QVBoxLayout(self.w_Im_ex_2)
        self.verticalLayout_14.setSpacing(0)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.label_Im_example_2 = QLabel(self.w_Im_ex_2)
        self.label_Im_example_2.setObjectName(u"label_Im_example_2")
        self.label_Im_example_2.setMinimumSize(QSize(100, 0))
        self.label_Im_example_2.setMaximumSize(QSize(100, 20))
        self.label_Im_example_2.setFont(font5)
        self.label_Im_example_2.setStyleSheet(u"border: none;")
        self.label_Im_example_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_14.addWidget(self.label_Im_example_2)

        self.w_Im_example_2 = QWidget(self.w_Im_ex_2)
        self.w_Im_example_2.setObjectName(u"w_Im_example_2")
        self.w_Im_example_2.setMinimumSize(QSize(100, 100))
        self.w_Im_example_2.setMaximumSize(QSize(100, 100))
        self.aim_2 = QLabel(self.w_Im_example_2)
        self.aim_2.setObjectName(u"aim_2")
        self.aim_2.setGeometry(QRect(0, 30, 100, 70))
        sizePolicy.setHeightForWidth(self.aim_2.sizePolicy().hasHeightForWidth())
        self.aim_2.setSizePolicy(sizePolicy)
        self.aim_2.setMinimumSize(QSize(100, 70))
        self.aim_2.setMaximumSize(QSize(100, 70))
        self.aim_2.setPixmap(QPixmap(u""+ icons_path +"axes.png"))
        self.aim_2.setScaledContents(True)
        self.bim_2 = QLabel(self.w_Im_example_2)
        self.bim_2.setObjectName(u"bim_2")
        self.bim_2.setGeometry(QRect(5, 35, 90, 60))
        sizePolicy4.setHeightForWidth(self.bim_2.sizePolicy().hasHeightForWidth())
        self.bim_2.setSizePolicy(sizePolicy4)
        self.bim_2.setMinimumSize(QSize(90, 60))
        self.bim_2.setMaximumSize(QSize(90, 60))
        self.bim_2.setPixmap(QPixmap(u""+ icons_path +"background.png"))
        self.bim_2.setScaledContents(True)
        self.bim_2.setIndent(2)
        self.bim_2.raise_()
        self.aim_2.raise_()

        self.verticalLayout_14.addWidget(self.w_Im_example_2)

        self.w_lab_op_2 = QWidget(self.w_Im_ex_2)
        self.w_lab_op_2.setObjectName(u"w_lab_op_2")
        self.horizontalLayout_18 = QHBoxLayout(self.w_lab_op_2)
        self.horizontalLayout_18.setSpacing(5)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(0, 0, 20, 0)
        self.lab_op0_2 = QLabel(self.w_lab_op_2)
        self.lab_op0_2.setObjectName(u"lab_op0_2")
        self.lab_op0_2.setMinimumSize(QSize(100, 0))
        self.lab_op0_2.setMaximumSize(QSize(100, 20))
        self.lab_op0_2.setFont(font5)
        self.lab_op0_2.setStyleSheet(u"border: none;")
        self.lab_op0_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_18.addWidget(self.lab_op0_2)

        self.lab_op1_2 = QLabel(self.w_lab_op_2)
        self.lab_op1_2.setObjectName(u"lab_op1_2")
        self.lab_op1_2.setMinimumSize(QSize(20, 20))
        self.lab_op1_2.setMaximumSize(QSize(20, 20))
        self.lab_op1_2.setFont(font5)
        self.lab_op1_2.setStyleSheet(u"border: none;")
        self.lab_op1_2.setScaledContents(True)
        self.lab_op1_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_18.addWidget(self.lab_op1_2)

        self.lab_op2_2 = QLabel(self.w_lab_op_2)
        self.lab_op2_2.setObjectName(u"lab_op2_2")
        self.lab_op2_2.setMinimumSize(QSize(20, 20))
        self.lab_op2_2.setMaximumSize(QSize(20, 20))
        self.lab_op2_2.setFont(font5)
        self.lab_op2_2.setStyleSheet(u"border: none;")
        self.lab_op2_2.setScaledContents(True)
        self.lab_op2_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_18.addWidget(self.lab_op2_2)

        self.lab_op3_2 = QLabel(self.w_lab_op_2)
        self.lab_op3_2.setObjectName(u"lab_op3_2")
        self.lab_op3_2.setMinimumSize(QSize(20, 20))
        self.lab_op3_2.setMaximumSize(QSize(20, 20))
        self.lab_op3_2.setFont(font5)
        self.lab_op3_2.setStyleSheet(u"border: none;")
        self.lab_op3_2.setScaledContents(True)
        self.lab_op3_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_18.addWidget(self.lab_op3_2)


        self.verticalLayout_14.addWidget(self.w_lab_op_2)


        self.horizontalLayout_16.addWidget(self.w_Im_ex_2)

        self.hs_Images_ex_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.hs_Images_ex_2)

        self.w_Im_ex_3 = QWidget(self.w_Images_ex)
        self.w_Im_ex_3.setObjectName(u"w_Im_ex_3")
        self.w_Im_ex_3.setMinimumSize(QSize(100, 140))
        self.w_Im_ex_3.setMaximumSize(QSize(100, 140))
        self.verticalLayout_17 = QVBoxLayout(self.w_Im_ex_3)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.label_Im_example_3 = QLabel(self.w_Im_ex_3)
        self.label_Im_example_3.setObjectName(u"label_Im_example_3")
        self.label_Im_example_3.setMinimumSize(QSize(100, 0))
        self.label_Im_example_3.setMaximumSize(QSize(100, 20))
        self.label_Im_example_3.setFont(font5)
        self.label_Im_example_3.setStyleSheet(u"border: none;")
        self.label_Im_example_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_Im_example_3)

        self.w_Im_example_3 = QWidget(self.w_Im_ex_3)
        self.w_Im_example_3.setObjectName(u"w_Im_example_3")
        self.w_Im_example_3.setMinimumSize(QSize(100, 100))
        self.w_Im_example_3.setMaximumSize(QSize(100, 100))
        self.aim_3 = QLabel(self.w_Im_example_3)
        self.aim_3.setObjectName(u"aim_3")
        self.aim_3.setGeometry(QRect(0, 30, 100, 70))
        sizePolicy.setHeightForWidth(self.aim_3.sizePolicy().hasHeightForWidth())
        self.aim_3.setSizePolicy(sizePolicy)
        self.aim_3.setMinimumSize(QSize(100, 70))
        self.aim_3.setMaximumSize(QSize(100, 70))
        self.aim_3.setPixmap(QPixmap(u""+ icons_path +"axes.png"))
        self.aim_3.setScaledContents(True)
        self.bim_3 = QLabel(self.w_Im_example_3)
        self.bim_3.setObjectName(u"bim_3")
        self.bim_3.setGeometry(QRect(5, 35, 90, 60))
        sizePolicy4.setHeightForWidth(self.bim_3.sizePolicy().hasHeightForWidth())
        self.bim_3.setSizePolicy(sizePolicy4)
        self.bim_3.setMinimumSize(QSize(90, 60))
        self.bim_3.setMaximumSize(QSize(90, 60))
        self.bim_3.setPixmap(QPixmap(u""+ icons_path +"background_vectors.png"))
        self.bim_3.setScaledContents(True)
        self.bim_3.setIndent(2)
        self.bim_3.raise_()
        self.aim_3.raise_()

        self.verticalLayout_17.addWidget(self.w_Im_example_3)

        self.w_lab_op_3 = QWidget(self.w_Im_ex_3)
        self.w_lab_op_3.setObjectName(u"w_lab_op_3")
        self.horizontalLayout_19 = QHBoxLayout(self.w_lab_op_3)
        self.horizontalLayout_19.setSpacing(5)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(0, 0, 20, 0)
        self.lab_op0_3 = QLabel(self.w_lab_op_3)
        self.lab_op0_3.setObjectName(u"lab_op0_3")
        self.lab_op0_3.setMinimumSize(QSize(100, 0))
        self.lab_op0_3.setMaximumSize(QSize(100, 20))
        self.lab_op0_3.setFont(font5)
        self.lab_op0_3.setStyleSheet(u"border: none;")
        self.lab_op0_3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_19.addWidget(self.lab_op0_3)

        self.lab_op1_3 = QLabel(self.w_lab_op_3)
        self.lab_op1_3.setObjectName(u"lab_op1_3")
        self.lab_op1_3.setMinimumSize(QSize(20, 20))
        self.lab_op1_3.setMaximumSize(QSize(20, 20))
        self.lab_op1_3.setFont(font5)
        self.lab_op1_3.setStyleSheet(u"border: none;")
        self.lab_op1_3.setScaledContents(True)
        self.lab_op1_3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_19.addWidget(self.lab_op1_3)

        self.lab_op2_3 = QLabel(self.w_lab_op_3)
        self.lab_op2_3.setObjectName(u"lab_op2_3")
        self.lab_op2_3.setMinimumSize(QSize(20, 20))
        self.lab_op2_3.setMaximumSize(QSize(20, 20))
        self.lab_op2_3.setFont(font5)
        self.lab_op2_3.setStyleSheet(u"border: none;")
        self.lab_op2_3.setScaledContents(True)
        self.lab_op2_3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_19.addWidget(self.lab_op2_3)

        self.lab_op3_3 = QLabel(self.w_lab_op_3)
        self.lab_op3_3.setObjectName(u"lab_op3_3")
        self.lab_op3_3.setMinimumSize(QSize(20, 20))
        self.lab_op3_3.setMaximumSize(QSize(20, 20))
        self.lab_op3_3.setFont(font5)
        self.lab_op3_3.setStyleSheet(u"border: none;")
        self.lab_op3_3.setScaledContents(True)
        self.lab_op3_3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_19.addWidget(self.lab_op3_3)


        self.verticalLayout_17.addWidget(self.w_lab_op_3)


        self.horizontalLayout_16.addWidget(self.w_Im_ex_3)


        self.horizontalLayout_4.addWidget(self.w_Images_ex)

        self.hs_flip_image_3 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.hs_flip_image_3)


        self.verticalLayout_15.addWidget(self.w_Flip_Mirror)


        self.verticalLayout_24.addWidget(self.w_Flip_Image)


        self.verticalLayout_10.addWidget(self.CollapBox_Flip)

        self.w_Resolution = QWidget(self.scrollAreaWidgetContents)
        self.w_Resolution.setObjectName(u"w_Resolution")
        self.w_Resolution.setMinimumSize(QSize(0, 64))
        self.w_Resolution.setMaximumSize(QSize(16777215, 64))
        self.horizontalLayout_11 = QHBoxLayout(self.w_Resolution)
        self.horizontalLayout_11.setSpacing(5)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.w_x_Resolution = QWidget(self.w_Resolution)
        self.w_x_Resolution.setObjectName(u"w_x_Resolution")
        self.w_x_Resolution.setMinimumSize(QSize(110, 64))
        self.w_x_Resolution.setMaximumSize(QSize(140, 64))
        self.verticalLayout_29 = QVBoxLayout(self.w_x_Resolution)
        self.verticalLayout_29.setSpacing(0)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.verticalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.label_x_res = QLabel(self.w_x_Resolution)
        self.label_x_res.setObjectName(u"label_x_res")
        sizePolicy3.setHeightForWidth(self.label_x_res.sizePolicy().hasHeightForWidth())
        self.label_x_res.setSizePolicy(sizePolicy3)
        self.label_x_res.setMinimumSize(QSize(0, 20))
        self.label_x_res.setMaximumSize(QSize(16777215, 20))
        self.label_x_res.setFont(font5)
        self.label_x_res.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_29.addWidget(self.label_x_res)

        self.spin_x_res = MyQDoubleSpin(self.w_x_Resolution)
        self.spin_x_res.setObjectName(u"spin_x_res")
        self.spin_x_res.setMinimumSize(QSize(0, 0))
        self.spin_x_res.setMaximumSize(QSize(1000000, 24))
        self.spin_x_res.setFont(font)
        self.spin_x_res.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spin_x_res.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_x_res.setDecimals(6)
        self.spin_x_res.setMinimum(0.000001000000000)
        self.spin_x_res.setMaximum(99999999999999991611392.000000000000000)
        self.spin_x_res.setSingleStep(0.100000000000000)
        self.spin_x_res.setValue(1.000000000000000)

        self.verticalLayout_29.addWidget(self.spin_x_res)

        self.label_x_res_2 = QLabel(self.w_x_Resolution)
        self.label_x_res_2.setObjectName(u"label_x_res_2")
        sizePolicy3.setHeightForWidth(self.label_x_res_2.sizePolicy().hasHeightForWidth())
        self.label_x_res_2.setSizePolicy(sizePolicy3)
        self.label_x_res_2.setMinimumSize(QSize(0, 20))
        self.label_x_res_2.setMaximumSize(QSize(16777215, 20))
        self.label_x_res_2.setFont(font5)
        self.label_x_res_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_29.addWidget(self.label_x_res_2)


        self.horizontalLayout_11.addWidget(self.w_x_Resolution)

        self.w_y_Resolution = QWidget(self.w_Resolution)
        self.w_y_Resolution.setObjectName(u"w_y_Resolution")
        self.w_y_Resolution.setMinimumSize(QSize(120, 64))
        self.w_y_Resolution.setMaximumSize(QSize(140, 64))
        self.verticalLayout_28 = QVBoxLayout(self.w_y_Resolution)
        self.verticalLayout_28.setSpacing(0)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.label_y_res = QLabel(self.w_y_Resolution)
        self.label_y_res.setObjectName(u"label_y_res")
        sizePolicy3.setHeightForWidth(self.label_y_res.sizePolicy().hasHeightForWidth())
        self.label_y_res.setSizePolicy(sizePolicy3)
        self.label_y_res.setMinimumSize(QSize(0, 20))
        self.label_y_res.setMaximumSize(QSize(16777215, 20))
        self.label_y_res.setFont(font5)
        self.label_y_res.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_28.addWidget(self.label_y_res)

        self.spin_y_res = MyQDoubleSpin(self.w_y_Resolution)
        self.spin_y_res.setObjectName(u"spin_y_res")
        self.spin_y_res.setMinimumSize(QSize(0, 0))
        self.spin_y_res.setMaximumSize(QSize(1000000, 24))
        self.spin_y_res.setFont(font)
        self.spin_y_res.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spin_y_res.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_y_res.setDecimals(6)
        self.spin_y_res.setMinimum(0.000001000000000)
        self.spin_y_res.setMaximum(99999999999999991611392.000000000000000)
        self.spin_y_res.setSingleStep(0.010000000000000)
        self.spin_y_res.setValue(1.000000000000000)

        self.verticalLayout_28.addWidget(self.spin_y_res)

        self.label_y_res_2 = QLabel(self.w_y_Resolution)
        self.label_y_res_2.setObjectName(u"label_y_res_2")
        sizePolicy3.setHeightForWidth(self.label_y_res_2.sizePolicy().hasHeightForWidth())
        self.label_y_res_2.setSizePolicy(sizePolicy3)
        self.label_y_res_2.setMinimumSize(QSize(0, 20))
        self.label_y_res_2.setMaximumSize(QSize(16777215, 20))
        self.label_y_res_2.setFont(font5)
        self.label_y_res_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_28.addWidget(self.label_y_res_2)


        self.horizontalLayout_11.addWidget(self.w_y_Resolution)

        self.w_dt = QWidget(self.w_Resolution)
        self.w_dt.setObjectName(u"w_dt")
        self.w_dt.setMinimumSize(QSize(120, 64))
        self.w_dt.setMaximumSize(QSize(140, 64))
        self.verticalLayout_27 = QVBoxLayout(self.w_dt)
        self.verticalLayout_27.setSpacing(0)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.verticalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.label_dt = QLabel(self.w_dt)
        self.label_dt.setObjectName(u"label_dt")
        sizePolicy3.setHeightForWidth(self.label_dt.sizePolicy().hasHeightForWidth())
        self.label_dt.setSizePolicy(sizePolicy3)
        self.label_dt.setMinimumSize(QSize(0, 20))
        self.label_dt.setMaximumSize(QSize(16777215, 20))
        self.label_dt.setFont(font5)
        self.label_dt.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_27.addWidget(self.label_dt)

        self.spin_dt = MyQDoubleSpin(self.w_dt)
        self.spin_dt.setObjectName(u"spin_dt")
        self.spin_dt.setMinimumSize(QSize(0, 0))
        self.spin_dt.setMaximumSize(QSize(1000000, 24))
        self.spin_dt.setFont(font)
        self.spin_dt.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spin_dt.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_dt.setDecimals(6)
        self.spin_dt.setMinimum(0.000001000000000)
        self.spin_dt.setMaximum(99999999999999991611392.000000000000000)
        self.spin_dt.setSingleStep(0.100000000000000)
        self.spin_dt.setValue(0.001000000000000)

        self.verticalLayout_27.addWidget(self.spin_dt)

        self.label_dt_2 = QLabel(self.w_dt)
        self.label_dt_2.setObjectName(u"label_dt_2")
        sizePolicy3.setHeightForWidth(self.label_dt_2.sizePolicy().hasHeightForWidth())
        self.label_dt_2.setSizePolicy(sizePolicy3)
        self.label_dt_2.setMinimumSize(QSize(0, 20))
        self.label_dt_2.setMaximumSize(QSize(16777215, 20))
        self.label_dt_2.setFont(font5)
        self.label_dt_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_27.addWidget(self.label_dt_2)


        self.horizontalLayout_11.addWidget(self.w_dt)

        self.w_Res_eff = QWidget(self.w_Resolution)
        self.w_Res_eff.setObjectName(u"w_Res_eff")
        sizePolicy1.setHeightForWidth(self.w_Res_eff.sizePolicy().hasHeightForWidth())
        self.w_Res_eff.setSizePolicy(sizePolicy1)
        self.w_Res_eff.setMinimumSize(QSize(100, 60))
        self.w_Res_eff.setMaximumSize(QSize(150, 60))
        self.verticalLayout_30 = QVBoxLayout(self.w_Res_eff)
        self.verticalLayout_30.setSpacing(0)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.verticalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.label_Res = QLabel(self.w_Res_eff)
        self.label_Res.setObjectName(u"label_Res")
        sizePolicy3.setHeightForWidth(self.label_Res.sizePolicy().hasHeightForWidth())
        self.label_Res.setSizePolicy(sizePolicy3)
        self.label_Res.setMinimumSize(QSize(0, 20))
        self.label_Res.setMaximumSize(QSize(16777215, 20))
        self.label_Res.setFont(font5)
        self.label_Res.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_30.addWidget(self.label_Res)

        self.label_Res_x = QLabel(self.w_Res_eff)
        self.label_Res_x.setObjectName(u"label_Res_x")
        sizePolicy3.setHeightForWidth(self.label_Res_x.sizePolicy().hasHeightForWidth())
        self.label_Res_x.setSizePolicy(sizePolicy3)
        self.label_Res_x.setMinimumSize(QSize(0, 20))
        self.label_Res_x.setMaximumSize(QSize(16777215, 20))
        self.label_Res_x.setFont(font5)
        self.label_Res_x.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_30.addWidget(self.label_Res_x)

        self.label_Res_y = QLabel(self.w_Res_eff)
        self.label_Res_y.setObjectName(u"label_Res_y")
        sizePolicy3.setHeightForWidth(self.label_Res_y.sizePolicy().hasHeightForWidth())
        self.label_Res_y.setSizePolicy(sizePolicy3)
        self.label_Res_y.setMinimumSize(QSize(0, 20))
        self.label_Res_y.setMaximumSize(QSize(16777215, 20))
        self.label_Res_y.setFont(font5)
        self.label_Res_y.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_30.addWidget(self.label_Res_y)


        self.horizontalLayout_11.addWidget(self.w_Res_eff)

        self.horizontalLayout_11.setStretch(0, 1)
        self.horizontalLayout_11.setStretch(1, 1)
        self.horizontalLayout_11.setStretch(2, 1)
        self.horizontalLayout_11.setStretch(3, 1)

        self.verticalLayout_10.addWidget(self.w_Resolution)

        self.w_OutputSave = QWidget(self.scrollAreaWidgetContents)
        self.w_OutputSave.setObjectName(u"w_OutputSave")
        self.w_OutputSave.setMinimumSize(QSize(0, 0))
        self.w_OutputSave.setMaximumSize(QSize(16777215, 44))
        self.horizontalLayout_2 = QHBoxLayout(self.w_OutputSave)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.w_CheckSave = QWidget(self.w_OutputSave)
        self.w_CheckSave.setObjectName(u"w_CheckSave")
        self.w_CheckSave.setMinimumSize(QSize(0, 0))
        self.w_CheckSave.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_9 = QVBoxLayout(self.w_CheckSave)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.check_save = QRadioButton(self.w_CheckSave)
        self.check_save.setObjectName(u"check_save")
        self.check_save.setMinimumSize(QSize(0, 0))
        self.check_save.setMaximumSize(QSize(16777215, 16777215))
        self.check_save.setFont(font)
        self.check_save.setLayoutDirection(Qt.LeftToRight)
        self.check_save.setIconSize(QSize(22, 22))

        self.verticalLayout_9.addWidget(self.check_save)


        self.horizontalLayout_2.addWidget(self.w_CheckSave)

        self.w_SaveResults = QWidget(self.w_OutputSave)
        self.w_SaveResults.setObjectName(u"w_SaveResults")
        self.horizontalLayout_9 = QHBoxLayout(self.w_SaveResults)
        self.horizontalLayout_9.setSpacing(10)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.w_OutputImg = QWidget(self.w_SaveResults)
        self.w_OutputImg.setObjectName(u"w_OutputImg")
        self.w_OutputImg.setMinimumSize(QSize(100, 0))
        self.w_OutputImg.setMaximumSize(QSize(16777215, 42))
        self.verticalLayout_4 = QVBoxLayout(self.w_OutputImg)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_root = QLabel(self.w_OutputImg)
        self.label_root.setObjectName(u"label_root")
        sizePolicy3.setHeightForWidth(self.label_root.sizePolicy().hasHeightForWidth())
        self.label_root.setSizePolicy(sizePolicy3)
        self.label_root.setMinimumSize(QSize(0, 20))
        self.label_root.setMaximumSize(QSize(16777215, 20))
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush)
        brush1 = QBrush(QColor(50, 50, 50, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        brush2 = QBrush(QColor(255, 255, 255, 63))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush2)
        self.label_root.setPalette(palette)
        self.label_root.setFont(font5)

        self.verticalLayout_4.addWidget(self.label_root)

        self.w_edit_root = QWidget(self.w_OutputImg)
        self.w_edit_root.setObjectName(u"w_edit_root")
        self.w_edit_root.setMinimumSize(QSize(0, 0))
        self.w_edit_root.setMaximumSize(QSize(16777215, 22))
        self.horizontalLayout_13 = QHBoxLayout(self.w_edit_root)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.edit_root = MyQLineEdit(self.w_edit_root)
        self.edit_root.setObjectName(u"edit_root")
        self.edit_root.setMaximumSize(QSize(16777215, 22))
        self.edit_root.setFont(font)
        self.edit_root.setStyleSheet(u"border-top: 1px solid gray;\n"
"border-left: 1px solid gray;\n"
"border-bottom: 1px solid gray;\n"
"")

        self.horizontalLayout_13.addWidget(self.edit_root)

        self.label_check_root = QLabel(self.w_edit_root)
        self.label_check_root.setObjectName(u"label_check_root")
        self.label_check_root.setMinimumSize(QSize(22, 22))
        self.label_check_root.setMaximumSize(QSize(22, 22))
        self.label_check_root.setStyleSheet(u"border-top: 1px solid gray;\n"
"border-right: 1px solid gray;\n"
"border-bottom: 1px solid gray;\n"
"padding: 2px;")
        self.label_check_root.setPixmap(QPixmap(u""+ icons_path +"greenv.png"))
        self.label_check_root.setScaledContents(True)
        self.label_check_root.setMargin(0)

        self.horizontalLayout_13.addWidget(self.label_check_root)


        self.verticalLayout_4.addWidget(self.w_edit_root)


        self.horizontalLayout_9.addWidget(self.w_OutputImg)

        self.w_combo_out_type = QWidget(self.w_SaveResults)
        self.w_combo_out_type.setObjectName(u"w_combo_out_type")
        self.w_combo_out_type.setMinimumSize(QSize(100, 44))
        self.w_combo_out_type.setMaximumSize(QSize(16777215, 44))
        self.verticalLayout_5 = QVBoxLayout(self.w_combo_out_type)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_out_type = QLabel(self.w_combo_out_type)
        self.label_out_type.setObjectName(u"label_out_type")
        sizePolicy3.setHeightForWidth(self.label_out_type.sizePolicy().hasHeightForWidth())
        self.label_out_type.setSizePolicy(sizePolicy3)
        self.label_out_type.setMinimumSize(QSize(0, 18))
        self.label_out_type.setMaximumSize(QSize(16777215, 18))
        self.label_out_type.setFont(font5)

        self.verticalLayout_5.addWidget(self.label_out_type)

        self.combo_out_type = QComboBox(self.w_combo_out_type)
        self.combo_out_type.addItem("")
        self.combo_out_type.addItem("")
        self.combo_out_type.addItem("")
        self.combo_out_type.setObjectName(u"combo_out_type")
        self.combo_out_type.setFont(font)

        self.verticalLayout_5.addWidget(self.combo_out_type)


        self.horizontalLayout_9.addWidget(self.w_combo_out_type)


        self.horizontalLayout_2.addWidget(self.w_SaveResults)


        self.verticalLayout_10.addWidget(self.w_OutputSave)

        self.w_OutputFold_Button = QWidget(self.scrollAreaWidgetContents)
        self.w_OutputFold_Button.setObjectName(u"w_OutputFold_Button")
        self.w_OutputFold_Button.setMinimumSize(QSize(0, 44))
        self.w_OutputFold_Button.setMaximumSize(QSize(16777215, 44))
        self.horizontalLayout = QHBoxLayout(self.w_OutputFold_Button)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.check_same_as_input = QRadioButton(self.w_OutputFold_Button)
        self.check_same_as_input.setObjectName(u"check_same_as_input")
        self.check_same_as_input.setMinimumSize(QSize(120, 0))
        self.check_same_as_input.setMaximumSize(QSize(16777215, 16777215))
        self.check_same_as_input.setFont(font)
        self.check_same_as_input.setLayoutDirection(Qt.LeftToRight)
        self.check_same_as_input.setIconSize(QSize(22, 22))

        self.horizontalLayout.addWidget(self.check_same_as_input)

        self.w_OutputFold = QWidget(self.w_OutputFold_Button)
        self.w_OutputFold.setObjectName(u"w_OutputFold")
        self.w_OutputFold.setMinimumSize(QSize(0, 44))
        self.w_OutputFold.setMaximumSize(QSize(16777215, 44))
        self.w_OutputFold.setSizeIncrement(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.w_OutputFold)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_path = QLabel(self.w_OutputFold)
        self.label_path.setObjectName(u"label_path")
        sizePolicy3.setHeightForWidth(self.label_path.sizePolicy().hasHeightForWidth())
        self.label_path.setSizePolicy(sizePolicy3)
        self.label_path.setMinimumSize(QSize(0, 20))
        self.label_path.setMaximumSize(QSize(16777215, 20))
        self.label_path.setFont(font5)

        self.verticalLayout_2.addWidget(self.label_path)

        self.w_edit_path = QWidget(self.w_OutputFold)
        self.w_edit_path.setObjectName(u"w_edit_path")
        self.w_edit_path.setMinimumSize(QSize(0, 0))
        self.w_edit_path.setMaximumSize(QSize(16777215, 22))
        palette1 = QPalette()
        self.w_edit_path.setPalette(palette1)
        self.horizontalLayout_8 = QHBoxLayout(self.w_edit_path)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.edit_path = MyQLineEdit(self.w_edit_path)
        self.edit_path.setObjectName(u"edit_path")
        self.edit_path.setMaximumSize(QSize(16777215, 22))
        self.edit_path.setFont(font)
        self.edit_path.setStyleSheet(u"border-top: 1px solid gray;\n"
"border-left: 1px solid gray;\n"
"border-bottom: 1px solid gray;\n"
"")

        self.horizontalLayout_8.addWidget(self.edit_path)

        self.label_check_path = QLabel(self.w_edit_path)
        self.label_check_path.setObjectName(u"label_check_path")
        self.label_check_path.setMinimumSize(QSize(22, 22))
        self.label_check_path.setMaximumSize(QSize(22, 22))
        self.label_check_path.setStyleSheet(u"border-top: 1px solid gray;\n"
"border-right: 1px solid gray;\n"
"border-bottom: 1px solid gray;\n"
"padding: 2px;")
        self.label_check_path.setPixmap(QPixmap(u""+ icons_path +"greenv.png"))
        self.label_check_path.setScaledContents(True)
        self.label_check_path.setMargin(0)
        self.label_check_path.setIndent(-1)

        self.horizontalLayout_8.addWidget(self.label_check_path)


        self.verticalLayout_2.addWidget(self.w_edit_path)


        self.horizontalLayout.addWidget(self.w_OutputFold)

        self.w_button_path = QWidget(self.w_OutputFold_Button)
        self.w_button_path.setObjectName(u"w_button_path")
        self.w_button_path.setMinimumSize(QSize(0, 44))
        self.w_button_path.setMaximumSize(QSize(16777215, 44))
        self.verticalLayout_3 = QVBoxLayout(self.w_button_path)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_path_2 = QLabel(self.w_button_path)
        self.label_path_2.setObjectName(u"label_path_2")
        sizePolicy3.setHeightForWidth(self.label_path_2.sizePolicy().hasHeightForWidth())
        self.label_path_2.setSizePolicy(sizePolicy3)
        self.label_path_2.setMinimumSize(QSize(0, 18))
        self.label_path_2.setMaximumSize(QSize(16777215, 18))
        self.label_path_2.setFont(font5)

        self.verticalLayout_3.addWidget(self.label_path_2)

        self.button_path = QToolButton(self.w_button_path)
        self.button_path.setObjectName(u"button_path")
        self.button_path.setMinimumSize(QSize(26, 26))
        self.button_path.setMaximumSize(QSize(26, 26))
        icon15 = QIcon()
        icon15.addFile(u""+ icons_path +"browse_folder_c.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_path.setIcon(icon15)
        self.button_path.setIconSize(QSize(22, 22))

        self.verticalLayout_3.addWidget(self.button_path)


        self.horizontalLayout.addWidget(self.w_button_path)


        self.verticalLayout_10.addWidget(self.w_OutputFold_Button)

        self.w_OutputSubfold = QWidget(self.scrollAreaWidgetContents)
        self.w_OutputSubfold.setObjectName(u"w_OutputSubfold")
        self.w_OutputSubfold.setMinimumSize(QSize(0, 0))
        self.w_OutputSubfold.setMaximumSize(QSize(16777215, 44))
        self.horizontalLayout_3 = QHBoxLayout(self.w_OutputSubfold)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.w_CheckSubfold = QWidget(self.w_OutputSubfold)
        self.w_CheckSubfold.setObjectName(u"w_CheckSubfold")
        self.w_CheckSubfold.setMinimumSize(QSize(0, 0))
        self.w_CheckSubfold.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_6 = QVBoxLayout(self.w_CheckSubfold)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.check_subfold = QRadioButton(self.w_CheckSubfold)
        self.check_subfold.setObjectName(u"check_subfold")
        self.check_subfold.setMinimumSize(QSize(120, 0))
        self.check_subfold.setMaximumSize(QSize(16777215, 16777215))
        self.check_subfold.setFont(font)
        self.check_subfold.setLayoutDirection(Qt.LeftToRight)
        self.check_subfold.setIconSize(QSize(22, 22))

        self.verticalLayout_6.addWidget(self.check_subfold)


        self.horizontalLayout_3.addWidget(self.w_CheckSubfold)

        self.w_OutputSubfold_name = QWidget(self.w_OutputSubfold)
        self.w_OutputSubfold_name.setObjectName(u"w_OutputSubfold_name")
        self.w_OutputSubfold_name.setMinimumSize(QSize(180, 0))
        self.w_OutputSubfold_name.setMaximumSize(QSize(16777215, 42))
        self.verticalLayout_7 = QVBoxLayout(self.w_OutputSubfold_name)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.label_subfold = QLabel(self.w_OutputSubfold_name)
        self.label_subfold.setObjectName(u"label_subfold")
        sizePolicy3.setHeightForWidth(self.label_subfold.sizePolicy().hasHeightForWidth())
        self.label_subfold.setSizePolicy(sizePolicy3)
        self.label_subfold.setMinimumSize(QSize(0, 20))
        self.label_subfold.setMaximumSize(QSize(16777215, 20))
        self.label_subfold.setFont(font5)

        self.verticalLayout_7.addWidget(self.label_subfold)

        self.w_edit_path_subfold = QWidget(self.w_OutputSubfold_name)
        self.w_edit_path_subfold.setObjectName(u"w_edit_path_subfold")
        self.w_edit_path_subfold.setMinimumSize(QSize(0, 0))
        self.w_edit_path_subfold.setMaximumSize(QSize(16777215, 22))
        palette2 = QPalette()
        self.w_edit_path_subfold.setPalette(palette2)
        self.horizontalLayout_10 = QHBoxLayout(self.w_edit_path_subfold)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.edit_path_subfold = MyQLineEdit(self.w_edit_path_subfold)
        self.edit_path_subfold.setObjectName(u"edit_path_subfold")
        self.edit_path_subfold.setMaximumSize(QSize(16777215, 22))
        self.edit_path_subfold.setFont(font)
        self.edit_path_subfold.setStyleSheet(u"border-top: 1px solid gray;\n"
"border-left: 1px solid gray;\n"
"border-bottom: 1px solid gray;\n"
"")

        self.horizontalLayout_10.addWidget(self.edit_path_subfold)

        self.label_check_path_subfold = QLabel(self.w_edit_path_subfold)
        self.label_check_path_subfold.setObjectName(u"label_check_path_subfold")
        self.label_check_path_subfold.setMinimumSize(QSize(22, 22))
        self.label_check_path_subfold.setMaximumSize(QSize(22, 22))
        self.label_check_path_subfold.setStyleSheet(u"border-top: 1px solid gray;\n"
"border-right: 1px solid gray;\n"
"border-bottom: 1px solid gray;\n"
"padding: 2px;")
        self.label_check_path_subfold.setPixmap(QPixmap(u""+ icons_path +"greenv.png"))
        self.label_check_path_subfold.setScaledContents(True)
        self.label_check_path_subfold.setMargin(0)
        self.label_check_path_subfold.setIndent(-1)

        self.horizontalLayout_10.addWidget(self.label_check_path_subfold)


        self.verticalLayout_7.addWidget(self.w_edit_path_subfold)


        self.horizontalLayout_3.addWidget(self.w_OutputSubfold_name)


        self.verticalLayout_10.addWidget(self.w_OutputSubfold)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        QWidget.setTabOrder(self.button_back, self.button_forward)
        QWidget.setTabOrder(self.button_forward, self.button_close_tab)
        QWidget.setTabOrder(self.button_close_tab, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.tool_CollapBox_Flip)
        QWidget.setTabOrder(self.tool_CollapBox_Flip, self.push_CollapBox_Flip)
        QWidget.setTabOrder(self.push_CollapBox_Flip, self.spin_x)
        QWidget.setTabOrder(self.spin_x, self.spin_y)
        QWidget.setTabOrder(self.spin_y, self.spin_w)
        QWidget.setTabOrder(self.spin_w, self.spin_h)
        QWidget.setTabOrder(self.spin_h, self.button_resize)
        QWidget.setTabOrder(self.button_resize, self.button_reset_rot_flip)
        QWidget.setTabOrder(self.button_reset_rot_flip, self.button_rot_counter)
        QWidget.setTabOrder(self.button_rot_counter, self.button_rot_clock)
        QWidget.setTabOrder(self.button_rot_clock, self.button_mirror_y)
        QWidget.setTabOrder(self.button_mirror_y, self.button_mirror_x)
        QWidget.setTabOrder(self.button_mirror_x, self.button_rotv_counter)
        QWidget.setTabOrder(self.button_rotv_counter, self.button_rotv_clock)
        QWidget.setTabOrder(self.button_rotv_clock, self.button_flip_u)
        QWidget.setTabOrder(self.button_flip_u, self.button_flip_v)
        QWidget.setTabOrder(self.button_flip_v, self.spin_x_res)
        QWidget.setTabOrder(self.spin_x_res, self.spin_y_res)
        QWidget.setTabOrder(self.spin_y_res, self.spin_dt)
        QWidget.setTabOrder(self.spin_dt, self.check_save)
        QWidget.setTabOrder(self.check_save, self.edit_root)
        QWidget.setTabOrder(self.edit_root, self.combo_out_type)
        QWidget.setTabOrder(self.combo_out_type, self.check_same_as_input)
        QWidget.setTabOrder(self.check_same_as_input, self.edit_path)
        QWidget.setTabOrder(self.edit_path, self.button_path)
        QWidget.setTabOrder(self.button_path, self.check_subfold)
        QWidget.setTabOrder(self.check_subfold, self.edit_path_subfold)

        self.retranslateUi(ExportTab)

        QMetaObject.connectSlotsByName(ExportTab)
    # setupUi

    def retranslateUi(self, ExportTab):
        ExportTab.setWindowTitle(QCoreApplication.translate("ExportTab", u"Export", None))
        self.icon.setText("")
        self.name_tab.setText(QCoreApplication.translate("ExportTab", u" Output", None))
        self.label_number.setText(QCoreApplication.translate("ExportTab", u"1", None))
#if QT_CONFIG(tooltip)
        self.button_back.setToolTip(QCoreApplication.translate("ExportTab", u"Undo", None))
#endif // QT_CONFIG(tooltip)
        self.button_back.setText("")
#if QT_CONFIG(tooltip)
        self.button_forward.setToolTip(QCoreApplication.translate("ExportTab", u"Redo", None))
#endif // QT_CONFIG(tooltip)
        self.button_forward.setText("")
#if QT_CONFIG(tooltip)
        self.button_close_tab.setToolTip(QCoreApplication.translate("ExportTab", u"Close tab", None))
#endif // QT_CONFIG(tooltip)
        self.button_close_tab.setText("")
#if QT_CONFIG(shortcut)
        self.button_close_tab.setShortcut(QCoreApplication.translate("ExportTab", u"Alt+O", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.tool_CollapBox_Flip.setToolTip(QCoreApplication.translate("ExportTab", u"Image size and shape option box", None))
#endif // QT_CONFIG(tooltip)
        self.tool_CollapBox_Flip.setText(QCoreApplication.translate("ExportTab", u"Resize/reshape", None))
#if QT_CONFIG(tooltip)
        self.push_CollapBox_Flip.setToolTip(QCoreApplication.translate("ExportTab", u"Set default options for the selected type of process", None))
#endif // QT_CONFIG(tooltip)
        self.push_CollapBox_Flip.setText("")
        self.label_x.setText(QCoreApplication.translate("ExportTab", u"X0 (# column)", None))
#if QT_CONFIG(tooltip)
        self.spin_x.setToolTip(QCoreApplication.translate("ExportTab", u"First column of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_y.setText(QCoreApplication.translate("ExportTab", u"Y0 (# row)", None))
#if QT_CONFIG(tooltip)
        self.spin_y.setToolTip(QCoreApplication.translate("ExportTab", u"First row of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_w.setText(QCoreApplication.translate("ExportTab", u"Width (pixels)", None))
#if QT_CONFIG(tooltip)
        self.spin_w.setToolTip(QCoreApplication.translate("ExportTab", u"Width of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_h.setText(QCoreApplication.translate("ExportTab", u"Height (pixels)", None))
#if QT_CONFIG(tooltip)
        self.spin_h.setToolTip(QCoreApplication.translate("ExportTab", u"Heigth of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_button_resize.setText("")
#if QT_CONFIG(tooltip)
        self.button_resize.setToolTip(QCoreApplication.translate("ExportTab", u"Restore full image", None))
#endif // QT_CONFIG(tooltip)
        self.button_resize.setText("")
        self.label_Image_tool.setText(QCoreApplication.translate("ExportTab", u"Image", None))
#if QT_CONFIG(tooltip)
        self.button_reset_rot_flip.setToolTip(QCoreApplication.translate("ExportTab", u"Restore original orientation", None))
#endif // QT_CONFIG(tooltip)
        self.button_reset_rot_flip.setText("")
#if QT_CONFIG(tooltip)
        self.button_rot_counter.setToolTip(QCoreApplication.translate("ExportTab", u"Rotate the image by 90\u00b0 counterclockwise (before PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_rot_counter.setText("")
#if QT_CONFIG(tooltip)
        self.button_rot_clock.setToolTip(QCoreApplication.translate("ExportTab", u"Rotate the image by 90\u00b0 clockwise  (before PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_rot_clock.setText("")
#if QT_CONFIG(tooltip)
        self.button_mirror_y.setToolTip(QCoreApplication.translate("ExportTab", u"Mirror the image horizontally  (before PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_mirror_y.setText("")
#if QT_CONFIG(tooltip)
        self.button_mirror_x.setToolTip(QCoreApplication.translate("ExportTab", u"Mirror the image vertically  (before PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_mirror_x.setText("")
        self.label_Velocity_tool.setText(QCoreApplication.translate("ExportTab", u"Velocity", None))
#if QT_CONFIG(tooltip)
        self.button_rotv_counter.setToolTip(QCoreApplication.translate("ExportTab", u"Rotate the image and the vector field by 90\u00b0 counterclockwise (after PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_rotv_counter.setText("")
#if QT_CONFIG(tooltip)
        self.button_rotv_clock.setToolTip(QCoreApplication.translate("ExportTab", u"Rotate the image and the vector field by 90\u00b0 clockwise (after PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_rotv_clock.setText("")
#if QT_CONFIG(tooltip)
        self.button_flip_u.setToolTip(QCoreApplication.translate("ExportTab", u"Mirror the image and the vector field horizontally (after PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_flip_u.setText("")
#if QT_CONFIG(tooltip)
        self.button_flip_v.setToolTip(QCoreApplication.translate("ExportTab", u"Mirror the image and the vector field vertically (after PIV process)", None))
#endif // QT_CONFIG(tooltip)
        self.button_flip_v.setText("")
#if QT_CONFIG(tooltip)
        self.w_Im_ex.setToolTip(QCoreApplication.translate("ExportTab", u"Original image with no transformation", None))
#endif // QT_CONFIG(tooltip)
        self.label_Im_example.setText(QCoreApplication.translate("ExportTab", u"Original", None))
        self.aim.setText("")
        self.bim.setText("")
        self.lab_op1.setText("")
        self.lab_op2.setText("")
        self.lab_op3.setText("")
#if QT_CONFIG(tooltip)
        self.w_Im_ex_2.setToolTip(QCoreApplication.translate("ExportTab", u"Image transformed before running PIV process", None))
#endif // QT_CONFIG(tooltip)
        self.label_Im_example_2.setText(QCoreApplication.translate("ExportTab", u"Image", None))
        self.aim_2.setText("")
        self.bim_2.setText("")
        self.lab_op0_2.setText(QCoreApplication.translate("ExportTab", u"No transf.", None))
        self.lab_op1_2.setText("")
        self.lab_op2_2.setText("")
        self.lab_op3_2.setText("")
#if QT_CONFIG(tooltip)
        self.w_Im_ex_3.setToolTip(QCoreApplication.translate("ExportTab", u"Image and velocity field after both image and velocity transformations", None))
#endif // QT_CONFIG(tooltip)
        self.label_Im_example_3.setText(QCoreApplication.translate("ExportTab", u"Results", None))
        self.aim_3.setText("")
        self.bim_3.setText("")
        self.lab_op0_3.setText(QCoreApplication.translate("ExportTab", u"No transf.", None))
        self.lab_op1_3.setText("")
        self.lab_op2_3.setText("")
        self.lab_op3_3.setText("")
        self.label_x_res.setText(QCoreApplication.translate("ExportTab", u"X resolution", None))
#if QT_CONFIG(tooltip)
        self.spin_x_res.setToolTip(QCoreApplication.translate("ExportTab", u"Image resolution along the X direction in pixel/millimeter", None))
#endif // QT_CONFIG(tooltip)
        self.label_x_res_2.setText(QCoreApplication.translate("ExportTab", u"(pixel/mm)", None))
        self.label_y_res.setText(QCoreApplication.translate("ExportTab", u"Pixel aspect ratio", None))
#if QT_CONFIG(tooltip)
        self.spin_y_res.setToolTip(QCoreApplication.translate("ExportTab", u"Pixel aspect ratio", None))
#endif // QT_CONFIG(tooltip)
        self.label_y_res_2.setText(QCoreApplication.translate("ExportTab", u"(Y/X)", None))
        self.label_dt.setText(QCoreApplication.translate("ExportTab", u"Time delay \u0394t ", None))
#if QT_CONFIG(tooltip)
        self.spin_dt.setToolTip(QCoreApplication.translate("ExportTab", u"Time delay between laser pulses in microseconds", None))
#endif // QT_CONFIG(tooltip)
        self.label_dt_2.setText(QCoreApplication.translate("ExportTab", u"(\u03bcs)", None))
        self.label_Res.setText(QCoreApplication.translate("ExportTab", u"    1 pix./\u0394t =", None))
        self.label_Res_x.setText(QCoreApplication.translate("ExportTab", u"X: 1 m/s", None))
        self.label_Res_y.setText(QCoreApplication.translate("ExportTab", u"Y: 1 m/s", None))
#if QT_CONFIG(tooltip)
        self.check_save.setToolTip(QCoreApplication.translate("ExportTab", u"Save results to the disk", None))
#endif // QT_CONFIG(tooltip)
        self.check_save.setText(QCoreApplication.translate("ExportTab", u"Save results", None))
        self.label_root.setText(QCoreApplication.translate("ExportTab", u"Root of output files", None))
#if QT_CONFIG(tooltip)
        self.edit_root.setToolTip(QCoreApplication.translate("ExportTab", u"Pattern of the filenames of the output files", None))
#endif // QT_CONFIG(tooltip)
        self.edit_root.setText(QCoreApplication.translate("ExportTab", u"out", None))
        self.label_check_root.setText("")
        self.label_out_type.setText(QCoreApplication.translate("ExportTab", u"Type", None))
        self.combo_out_type.setItemText(0, QCoreApplication.translate("ExportTab", u"binary", None))
        self.combo_out_type.setItemText(1, QCoreApplication.translate("ExportTab", u"tecplot (binary)", None))
        self.combo_out_type.setItemText(2, QCoreApplication.translate("ExportTab", u"tecplot (ASCII)", None))

#if QT_CONFIG(tooltip)
        self.combo_out_type.setToolTip(QCoreApplication.translate("ExportTab", u"Type of the output files", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.check_same_as_input.setToolTip(QCoreApplication.translate("ExportTab", u"Save the output files in the folder containing the input image files", None))
#endif // QT_CONFIG(tooltip)
        self.check_same_as_input.setText(QCoreApplication.translate("ExportTab", u"Same as input", None))
        self.label_path.setText(QCoreApplication.translate("ExportTab", u"Output folder path", None))
#if QT_CONFIG(tooltip)
        self.edit_path.setToolTip(QCoreApplication.translate("ExportTab", u"Path of the directory where to the save the output files", None))
#endif // QT_CONFIG(tooltip)
        self.edit_path.setText(QCoreApplication.translate("ExportTab", u".\\img\\fold3\\", None))
        self.label_check_path.setText("")
        self.label_path_2.setText("")
#if QT_CONFIG(tooltip)
        self.button_path.setToolTip(QCoreApplication.translate("ExportTab", u"Explore and select the path of the directory of the output files", None))
#endif // QT_CONFIG(tooltip)
        self.button_path.setText("")
#if QT_CONFIG(shortcut)
        self.button_path.setShortcut(QCoreApplication.translate("ExportTab", u"Ctrl+O, Ctrl+I", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.check_subfold.setToolTip(QCoreApplication.translate("ExportTab", u"Create a subfolder with the output files in the above path", None))
#endif // QT_CONFIG(tooltip)
        self.check_subfold.setText(QCoreApplication.translate("ExportTab", u"Create subfolder", None))
        self.label_subfold.setText(QCoreApplication.translate("ExportTab", u"Subfolder name", None))
#if QT_CONFIG(tooltip)
        self.edit_path_subfold.setToolTip(QCoreApplication.translate("ExportTab", u"Name of the output subfolder", None))
#endif // QT_CONFIG(tooltip)
        self.edit_path_subfold.setText(QCoreApplication.translate("ExportTab", u".\\img\\fold3\\", None))
        self.label_check_path_subfold.setText("")
    # retranslateUi

