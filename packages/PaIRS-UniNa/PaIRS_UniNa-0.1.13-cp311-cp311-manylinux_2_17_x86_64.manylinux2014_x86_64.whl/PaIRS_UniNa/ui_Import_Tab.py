from .addwidgets_ps import icons_path
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Import_TabwdDBcl.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QFrame,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QScrollArea, QSizePolicy, QSpacerItem, QToolButton,
    QVBoxLayout, QWidget)

from .addwidgets_ps import (MyQLineEdit, MyQSpin, MyQSpinXW, MyTabLabel)

class Ui_ImportTab(object):
    def setupUi(self, ImportTab):
        if not ImportTab.objectName():
            ImportTab.setObjectName(u"ImportTab")
        ImportTab.resize(500, 680)
        ImportTab.setMinimumSize(QSize(260, 340))
        ImportTab.setMaximumSize(QSize(1000, 16777215))
        font = QFont()
        font.setPointSize(11)
        ImportTab.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u""+ icons_path +"import_logo.png", QSize(), QIcon.Normal, QIcon.Off)
        ImportTab.setWindowIcon(icon1)
        self.verticalLayout_7 = QVBoxLayout(ImportTab)
        self.verticalLayout_7.setSpacing(5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(10, 10, 10, 10)
        self.w_Mode = QWidget(ImportTab)
        self.w_Mode.setObjectName(u"w_Mode")
        self.w_Mode.setMinimumSize(QSize(0, 40))
        self.w_Mode.setMaximumSize(QSize(16777215, 40))
        self.w_Mode.setFont(font)
        self.horizontalLayout_5 = QHBoxLayout(self.w_Mode)
        self.horizontalLayout_5.setSpacing(3)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 10)
        self.icon = QLabel(self.w_Mode)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(35, 35))
        self.icon.setMaximumSize(QSize(35, 35))
        self.icon.setPixmap(QPixmap(u""+ icons_path +"import_logo.png"))
        self.icon.setScaledContents(True)

        self.horizontalLayout_5.addWidget(self.icon)

        self.name_tab = MyTabLabel(self.w_Mode)
        self.name_tab.setObjectName(u"name_tab")
        self.name_tab.setMinimumSize(QSize(0, 35))
        self.name_tab.setMaximumSize(QSize(16777215, 35))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(20)
        font1.setBold(True)
        self.name_tab.setFont(font1)

        self.horizontalLayout_5.addWidget(self.name_tab)

        self.w_button_data = QWidget(self.w_Mode)
        self.w_button_data.setObjectName(u"w_button_data")
        self.w_button_data.setMinimumSize(QSize(18, 24))
        self.w_button_data.setMaximumSize(QSize(18, 24))
        self.horizontalLayout_4 = QHBoxLayout(self.w_button_data)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, -1)
        self.button_data = QToolButton(self.w_button_data)
        self.button_data.setObjectName(u"button_data")
        self.button_data.setMinimumSize(QSize(18, 18))
        self.button_data.setMaximumSize(QSize(18, 18))
        self.button_data.setCursor(QCursor(Qt.PointingHandCursor))
        self.button_data.setLayoutDirection(Qt.LeftToRight)
        self.button_data.setStyleSheet(u"QToolButton{\n"
"border-radius: 15px;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u""+ icons_path +"flaticon_PaIRS_download.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_data.setIcon(icon2)
        self.button_data.setIconSize(QSize(15, 15))

        self.horizontalLayout_4.addWidget(self.button_data)


        self.horizontalLayout_5.addWidget(self.w_button_data)

        self.hs1 = QSpacerItem(70, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.hs1)

        self.label_number = QLabel(self.w_Mode)
        self.label_number.setObjectName(u"label_number")
        self.label_number.setMinimumSize(QSize(35, 0))
        font2 = QFont()
        font2.setPointSize(9)
        self.label_number.setFont(font2)
        self.label_number.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_number)

        self.hs_2 = QSpacerItem(5, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.hs_2)

        self.button_back = QToolButton(self.w_Mode)
        self.button_back.setObjectName(u"button_back")
        self.button_back.setMinimumSize(QSize(24, 24))
        self.button_back.setMaximumSize(QSize(24, 24))
        icon3 = QIcon()
        icon3.addFile(u""+ icons_path +"undo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_back.setIcon(icon3)
        self.button_back.setIconSize(QSize(20, 20))

        self.horizontalLayout_5.addWidget(self.button_back)

        self.button_forward = QToolButton(self.w_Mode)
        self.button_forward.setObjectName(u"button_forward")
        self.button_forward.setMinimumSize(QSize(24, 24))
        self.button_forward.setMaximumSize(QSize(24, 24))
        icon4 = QIcon()
        icon4.addFile(u""+ icons_path +"redo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_forward.setIcon(icon4)
        self.button_forward.setIconSize(QSize(20, 20))

        self.horizontalLayout_5.addWidget(self.button_forward)

        self.w_button_close_tab = QWidget(self.w_Mode)
        self.w_button_close_tab.setObjectName(u"w_button_close_tab")
        self.w_button_close_tab.setMinimumSize(QSize(18, 24))
        self.w_button_close_tab.setMaximumSize(QSize(18, 24))
        self.horizontalLayout_3 = QHBoxLayout(self.w_button_close_tab)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, -1)
        self.button_close_tab = QToolButton(self.w_button_close_tab)
        self.button_close_tab.setObjectName(u"button_close_tab")
        self.button_close_tab.setMinimumSize(QSize(18, 18))
        self.button_close_tab.setMaximumSize(QSize(18, 18))
        self.button_close_tab.setLayoutDirection(Qt.LeftToRight)
        self.button_close_tab.setStyleSheet(u"QToolButton{\n"
"border-radius: 15px;\n"
"}")
        icon5 = QIcon()
        icon5.addFile(u""+ icons_path +"close.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_close_tab.setIcon(icon5)
        self.button_close_tab.setIconSize(QSize(15, 15))

        self.horizontalLayout_3.addWidget(self.button_close_tab)


        self.horizontalLayout_5.addWidget(self.w_button_close_tab)


        self.verticalLayout_7.addWidget(self.w_Mode)

        self.line = QFrame(ImportTab)
        self.line.setObjectName(u"line")
        self.line.setMinimumSize(QSize(0, 5))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_7.addWidget(self.line)

        self.scrollArea = QScrollArea(ImportTab)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QSize(0, 0))
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 480, 605))
        self.scrollAreaWidgetContents.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout_8 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_8.setSpacing(10)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 15, 10, 0)
        self.w_InputFold_Button = QWidget(self.scrollAreaWidgetContents)
        self.w_InputFold_Button.setObjectName(u"w_InputFold_Button")
        self.w_InputFold_Button.setMinimumSize(QSize(400, 0))
        self.w_InputFold_Button.setMaximumSize(QSize(16777215, 44))
        self.horizontalLayout = QHBoxLayout(self.w_InputFold_Button)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.w_InputFold = QWidget(self.w_InputFold_Button)
        self.w_InputFold.setObjectName(u"w_InputFold")
        self.w_InputFold.setMinimumSize(QSize(320, 0))
        self.w_InputFold.setMaximumSize(QSize(16777215, 42))
        self.verticalLayout = QVBoxLayout(self.w_InputFold)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_path = QLabel(self.w_InputFold)
        self.label_path.setObjectName(u"label_path")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_path.sizePolicy().hasHeightForWidth())
        self.label_path.setSizePolicy(sizePolicy1)
        self.label_path.setMinimumSize(QSize(0, 20))
        self.label_path.setMaximumSize(QSize(16777215, 20))
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(False)
        font3.setItalic(True)
        self.label_path.setFont(font3)

        self.verticalLayout.addWidget(self.label_path)

        self.w_edit_path = QWidget(self.w_InputFold)
        self.w_edit_path.setObjectName(u"w_edit_path")
        self.w_edit_path.setMinimumSize(QSize(0, 0))
        self.w_edit_path.setMaximumSize(QSize(16777215, 22))
        palette = QPalette()
        self.w_edit_path.setPalette(palette)
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


        self.verticalLayout.addWidget(self.w_edit_path)


        self.horizontalLayout.addWidget(self.w_InputFold)

        self.w_button_path = QWidget(self.w_InputFold_Button)
        self.w_button_path.setObjectName(u"w_button_path")
        self.w_button_path.setMinimumSize(QSize(0, 44))
        self.w_button_path.setMaximumSize(QSize(16777215, 44))
        self.verticalLayout_2 = QVBoxLayout(self.w_button_path)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_path_2 = QLabel(self.w_button_path)
        self.label_path_2.setObjectName(u"label_path_2")
        sizePolicy1.setHeightForWidth(self.label_path_2.sizePolicy().hasHeightForWidth())
        self.label_path_2.setSizePolicy(sizePolicy1)
        self.label_path_2.setMinimumSize(QSize(0, 18))
        self.label_path_2.setMaximumSize(QSize(16777215, 18))
        self.label_path_2.setFont(font3)

        self.verticalLayout_2.addWidget(self.label_path_2)

        self.button_path = QToolButton(self.w_button_path)
        self.button_path.setObjectName(u"button_path")
        self.button_path.setMinimumSize(QSize(26, 26))
        self.button_path.setMaximumSize(QSize(26, 26))
        icon6 = QIcon()
        icon6.addFile(u""+ icons_path +"browse_folder_c.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_path.setIcon(icon6)
        self.button_path.setIconSize(QSize(22, 22))

        self.verticalLayout_2.addWidget(self.button_path)


        self.horizontalLayout.addWidget(self.w_button_path)


        self.verticalLayout_8.addWidget(self.w_InputFold_Button)

        self.w_InputImg_Button = QWidget(self.scrollAreaWidgetContents)
        self.w_InputImg_Button.setObjectName(u"w_InputImg_Button")
        self.w_InputImg_Button.setMinimumSize(QSize(400, 0))
        self.w_InputImg_Button.setMaximumSize(QSize(16777215, 44))
        self.horizontalLayout_2 = QHBoxLayout(self.w_InputImg_Button)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.w_InputImg = QWidget(self.w_InputImg_Button)
        self.w_InputImg.setObjectName(u"w_InputImg")
        self.w_InputImg.setMinimumSize(QSize(320, 0))
        self.w_InputImg.setMaximumSize(QSize(16777215, 42))
        self.verticalLayout_3 = QVBoxLayout(self.w_InputImg)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_root = QLabel(self.w_InputImg)
        self.label_root.setObjectName(u"label_root")
        sizePolicy1.setHeightForWidth(self.label_root.sizePolicy().hasHeightForWidth())
        self.label_root.setSizePolicy(sizePolicy1)
        self.label_root.setMinimumSize(QSize(0, 20))
        self.label_root.setMaximumSize(QSize(16777215, 20))
        palette1 = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipBase, brush)
        brush1 = QBrush(QColor(50, 50, 50, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        brush2 = QBrush(QColor(255, 255, 255, 63))
        brush2.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush2)
        self.label_root.setPalette(palette1)
        self.label_root.setFont(font3)

        self.verticalLayout_3.addWidget(self.label_root)

        self.w_edit_root = QWidget(self.w_InputImg)
        self.w_edit_root.setObjectName(u"w_edit_root")
        self.w_edit_root.setMinimumSize(QSize(0, 0))
        self.w_edit_root.setMaximumSize(QSize(16777215, 22))
        self.horizontalLayout_9 = QHBoxLayout(self.w_edit_root)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.edit_root = MyQLineEdit(self.w_edit_root)
        self.edit_root.setObjectName(u"edit_root")
        self.edit_root.setMaximumSize(QSize(16777215, 22))
        self.edit_root.setFont(font)
        self.edit_root.setStyleSheet(u"border-top: 1px solid gray;\n"
"border-left: 1px solid gray;\n"
"border-bottom: 1px solid gray;\n"
"")

        self.horizontalLayout_9.addWidget(self.edit_root)

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

        self.horizontalLayout_9.addWidget(self.label_check_root)


        self.verticalLayout_3.addWidget(self.w_edit_root)


        self.horizontalLayout_2.addWidget(self.w_InputImg)

        self.w_button_import = QWidget(self.w_InputImg_Button)
        self.w_button_import.setObjectName(u"w_button_import")
        self.w_button_import.setMinimumSize(QSize(0, 44))
        self.w_button_import.setMaximumSize(QSize(16777215, 44))
        self.verticalLayout_4 = QVBoxLayout(self.w_button_import)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_root_2 = QLabel(self.w_button_import)
        self.label_root_2.setObjectName(u"label_root_2")
        sizePolicy1.setHeightForWidth(self.label_root_2.sizePolicy().hasHeightForWidth())
        self.label_root_2.setSizePolicy(sizePolicy1)
        self.label_root_2.setMinimumSize(QSize(0, 18))
        self.label_root_2.setMaximumSize(QSize(16777215, 18))
        self.label_root_2.setFont(font3)

        self.verticalLayout_4.addWidget(self.label_root_2)

        self.button_import = QToolButton(self.w_button_import)
        self.button_import.setObjectName(u"button_import")
        self.button_import.setMinimumSize(QSize(26, 26))
        self.button_import.setMaximumSize(QSize(26, 26))
        icon7 = QIcon()
        icon7.addFile(u""+ icons_path +"browse_file_c.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_import.setIcon(icon7)
        self.button_import.setIconSize(QSize(22, 22))

        self.verticalLayout_4.addWidget(self.button_import)


        self.horizontalLayout_2.addWidget(self.w_button_import)


        self.verticalLayout_8.addWidget(self.w_InputImg_Button)

        self.w_SelectImages = QWidget(self.scrollAreaWidgetContents)
        self.w_SelectImages.setObjectName(u"w_SelectImages")
        self.verticalLayout_12 = QVBoxLayout(self.w_SelectImages)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.w_range_sel = QWidget(self.w_SelectImages)
        self.w_range_sel.setObjectName(u"w_range_sel")
        self.w_range_sel.setMinimumSize(QSize(0, 74))
        self.w_range_sel.setMaximumSize(QSize(16777215, 74))
        self.horizontalLayout_11 = QHBoxLayout(self.w_range_sel)
        self.horizontalLayout_11.setSpacing(20)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.w_label_list = QWidget(self.w_range_sel)
        self.w_label_list.setObjectName(u"w_label_list")
        self.w_label_list.setMinimumSize(QSize(0, 74))
        self.w_label_list.setMaximumSize(QSize(16777215, 74))
        self.verticalLayout_13 = QVBoxLayout(self.w_label_list)
        self.verticalLayout_13.setSpacing(10)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.w_range_from_to = QWidget(self.w_label_list)
        self.w_range_from_to.setObjectName(u"w_range_from_to")
        self.w_range_from_to.setMinimumSize(QSize(240, 44))
        self.w_range_from_to.setMaximumSize(QSize(16777215, 44))
        self.horizontalLayout_12 = QHBoxLayout(self.w_range_from_to)
        self.horizontalLayout_12.setSpacing(20)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.w_range_from = QWidget(self.w_range_from_to)
        self.w_range_from.setObjectName(u"w_range_from")
        self.w_range_from.setMinimumSize(QSize(100, 44))
        self.w_range_from.setMaximumSize(QSize(150, 44))
        self.verticalLayout_25 = QVBoxLayout(self.w_range_from)
        self.verticalLayout_25.setSpacing(0)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.label_range_from = QLabel(self.w_range_from)
        self.label_range_from.setObjectName(u"label_range_from")
        sizePolicy1.setHeightForWidth(self.label_range_from.sizePolicy().hasHeightForWidth())
        self.label_range_from.setSizePolicy(sizePolicy1)
        self.label_range_from.setMinimumSize(QSize(65, 20))
        self.label_range_from.setMaximumSize(QSize(16777215, 20))
        self.label_range_from.setFont(font3)
        self.label_range_from.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_25.addWidget(self.label_range_from)

        self.spin_range_from = MyQSpin(self.w_range_from)
        self.spin_range_from.setObjectName(u"spin_range_from")
        self.spin_range_from.setEnabled(True)
        self.spin_range_from.setMinimumSize(QSize(100, 24))
        self.spin_range_from.setMaximumSize(QSize(150, 24))
        self.spin_range_from.setFont(font)
        self.spin_range_from.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_range_from.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_range_from.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_range_from.setValue(1)

        self.verticalLayout_25.addWidget(self.spin_range_from)


        self.horizontalLayout_12.addWidget(self.w_range_from)

        self.w_range_to = QWidget(self.w_range_from_to)
        self.w_range_to.setObjectName(u"w_range_to")
        self.w_range_to.setMinimumSize(QSize(100, 44))
        self.w_range_to.setMaximumSize(QSize(150, 44))
        self.verticalLayout_26 = QVBoxLayout(self.w_range_to)
        self.verticalLayout_26.setSpacing(0)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.label_range_to = QLabel(self.w_range_to)
        self.label_range_to.setObjectName(u"label_range_to")
        sizePolicy1.setHeightForWidth(self.label_range_to.sizePolicy().hasHeightForWidth())
        self.label_range_to.setSizePolicy(sizePolicy1)
        self.label_range_to.setMinimumSize(QSize(65, 20))
        self.label_range_to.setMaximumSize(QSize(16777215, 20))
        self.label_range_to.setFont(font3)
        self.label_range_to.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_26.addWidget(self.label_range_to)

        self.spin_range_to = MyQSpin(self.w_range_to)
        self.spin_range_to.setObjectName(u"spin_range_to")
        self.spin_range_to.setEnabled(True)
        self.spin_range_to.setMinimumSize(QSize(100, 24))
        self.spin_range_to.setMaximumSize(QSize(150, 24))
        self.spin_range_to.setFont(font)
        self.spin_range_to.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_range_to.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_range_to.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_range_to.setValue(1)

        self.verticalLayout_26.addWidget(self.spin_range_to)


        self.horizontalLayout_12.addWidget(self.w_range_to)


        self.verticalLayout_13.addWidget(self.w_range_from_to)

        self.label_list = QLabel(self.w_label_list)
        self.label_list.setObjectName(u"label_list")
        sizePolicy1.setHeightForWidth(self.label_list.sizePolicy().hasHeightForWidth())
        self.label_list.setSizePolicy(sizePolicy1)
        self.label_list.setMinimumSize(QSize(250, 20))
        self.label_list.setMaximumSize(QSize(16777215, 20))
        self.label_list.setFont(font3)
        self.label_list.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_13.addWidget(self.label_list)


        self.horizontalLayout_11.addWidget(self.w_label_list)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer)

        self.w_range_selected = QWidget(self.w_range_sel)
        self.w_range_selected.setObjectName(u"w_range_selected")
        self.w_range_selected.setMinimumSize(QSize(100, 64))
        self.w_range_selected.setMaximumSize(QSize(100, 64))
        self.verticalLayout_27 = QVBoxLayout(self.w_range_selected)
        self.verticalLayout_27.setSpacing(0)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.verticalLayout_27.setContentsMargins(0, 20, 0, 0)
        self.label_selected = QLabel(self.w_range_selected)
        self.label_selected.setObjectName(u"label_selected")
        sizePolicy1.setHeightForWidth(self.label_selected.sizePolicy().hasHeightForWidth())
        self.label_selected.setSizePolicy(sizePolicy1)
        self.label_selected.setMinimumSize(QSize(65, 20))
        self.label_selected.setMaximumSize(QSize(16777215, 20))
        self.label_selected.setFont(font3)
        self.label_selected.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_27.addWidget(self.label_selected)

        self.spin_selected = MyQSpin(self.w_range_selected)
        self.spin_selected.setObjectName(u"spin_selected")
        self.spin_selected.setEnabled(True)
        self.spin_selected.setMinimumSize(QSize(65, 24))
        self.spin_selected.setMaximumSize(QSize(100, 24))
        self.spin_selected.setFont(font)
        self.spin_selected.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_selected.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_selected.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_selected.setValue(1)

        self.verticalLayout_27.addWidget(self.spin_selected)


        self.horizontalLayout_11.addWidget(self.w_range_selected)

        self.w_range_frame = QWidget(self.w_range_sel)
        self.w_range_frame.setObjectName(u"w_range_frame")
        self.w_range_frame.setMinimumSize(QSize(50, 64))
        self.w_range_frame.setMaximumSize(QSize(70, 64))
        self.verticalLayout_28 = QVBoxLayout(self.w_range_frame)
        self.verticalLayout_28.setSpacing(0)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(0, 20, 0, 0)
        self.label_frame = QLabel(self.w_range_frame)
        self.label_frame.setObjectName(u"label_frame")
        sizePolicy1.setHeightForWidth(self.label_frame.sizePolicy().hasHeightForWidth())
        self.label_frame.setSizePolicy(sizePolicy1)
        self.label_frame.setMinimumSize(QSize(50, 20))
        self.label_frame.setMaximumSize(QSize(70, 20))
        self.label_frame.setFont(font3)
        self.label_frame.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_28.addWidget(self.label_frame)

        self.spin_frame = MyQSpin(self.w_range_frame)
        self.spin_frame.setObjectName(u"spin_frame")
        self.spin_frame.setEnabled(True)
        self.spin_frame.setMinimumSize(QSize(50, 24))
        self.spin_frame.setMaximumSize(QSize(70, 24))
        self.spin_frame.setFont(font)
        self.spin_frame.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spin_frame.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spin_frame.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.spin_frame.setValue(1)

        self.verticalLayout_28.addWidget(self.spin_frame)


        self.horizontalLayout_11.addWidget(self.w_range_frame)


        self.verticalLayout_12.addWidget(self.w_range_sel)

        self.list_images = QListWidget(self.w_SelectImages)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        QListWidgetItem(self.list_images)
        self.list_images.setObjectName(u"list_images")
        self.list_images.setMinimumSize(QSize(0, 250))
        self.list_images.setFont(font)

        self.verticalLayout_12.addWidget(self.list_images)


        self.verticalLayout_8.addWidget(self.w_SelectImages)

        self.w_list_images = QWidget(self.scrollAreaWidgetContents)
        self.w_list_images.setObjectName(u"w_list_images")
        self.verticalLayout_5 = QVBoxLayout(self.w_list_images)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_8.addWidget(self.w_list_images)

        self.w_TR_min = QWidget(self.scrollAreaWidgetContents)
        self.w_TR_min.setObjectName(u"w_TR_min")
        self.w_TR_min.setMinimumSize(QSize(0, 26))
        self.w_TR_min.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_6 = QHBoxLayout(self.w_TR_min)
        self.horizontalLayout_6.setSpacing(10)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.check_TR_sequence = QCheckBox(self.w_TR_min)
        self.check_TR_sequence.setObjectName(u"check_TR_sequence")
        self.check_TR_sequence.setMinimumSize(QSize(0, 24))
        self.check_TR_sequence.setMaximumSize(QSize(16777215, 24))
        self.check_TR_sequence.setFont(font)
        self.check_TR_sequence.setLayoutDirection(Qt.LeftToRight)
        self.check_TR_sequence.setStyleSheet(u"border: none\n"
"")

        self.horizontalLayout_6.addWidget(self.check_TR_sequence)

        self.check_subtract = QCheckBox(self.w_TR_min)
        self.check_subtract.setObjectName(u"check_subtract")
        sizePolicy1.setHeightForWidth(self.check_subtract.sizePolicy().hasHeightForWidth())
        self.check_subtract.setSizePolicy(sizePolicy1)
        self.check_subtract.setMinimumSize(QSize(0, 24))
        self.check_subtract.setMaximumSize(QSize(16777215, 24))
        self.check_subtract.setFont(font)
        self.check_subtract.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout_6.addWidget(self.check_subtract)


        self.verticalLayout_8.addWidget(self.w_TR_min)

        self.w_SizeImg = QWidget(self.scrollAreaWidgetContents)
        self.w_SizeImg.setObjectName(u"w_SizeImg")
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
        sizePolicy1.setHeightForWidth(self.label_x.sizePolicy().hasHeightForWidth())
        self.label_x.setSizePolicy(sizePolicy1)
        self.label_x.setMinimumSize(QSize(90, 20))
        self.label_x.setMaximumSize(QSize(90, 20))
        self.label_x.setFont(font3)
        self.label_x.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_19.addWidget(self.label_x)

        self.spin_x = MyQSpinXW(self.w_x)
        self.spin_x.setObjectName(u"spin_x")
        self.spin_x.setEnabled(True)
        self.spin_x.setMinimumSize(QSize(90, 24))
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
        sizePolicy1.setHeightForWidth(self.label_y.sizePolicy().hasHeightForWidth())
        self.label_y.setSizePolicy(sizePolicy1)
        self.label_y.setMinimumSize(QSize(90, 20))
        self.label_y.setMaximumSize(QSize(90, 20))
        self.label_y.setFont(font3)
        self.label_y.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_20.addWidget(self.label_y)

        self.spin_y = MyQSpinXW(self.w_y)
        self.spin_y.setObjectName(u"spin_y")
        self.spin_y.setEnabled(True)
        self.spin_y.setMinimumSize(QSize(90, 24))
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
        sizePolicy1.setHeightForWidth(self.label_w.sizePolicy().hasHeightForWidth())
        self.label_w.setSizePolicy(sizePolicy1)
        self.label_w.setMinimumSize(QSize(90, 20))
        self.label_w.setMaximumSize(QSize(90, 20))
        self.label_w.setFont(font3)
        self.label_w.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_21.addWidget(self.label_w)

        self.spin_w = MyQSpin(self.w_width)
        self.spin_w.setObjectName(u"spin_w")
        self.spin_w.setEnabled(True)
        self.spin_w.setMinimumSize(QSize(90, 24))
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
        sizePolicy1.setHeightForWidth(self.label_h.sizePolicy().hasHeightForWidth())
        self.label_h.setSizePolicy(sizePolicy1)
        self.label_h.setMinimumSize(QSize(90, 20))
        self.label_h.setMaximumSize(QSize(90, 20))
        self.label_h.setFont(font3)
        self.label_h.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_22.addWidget(self.label_h)

        self.spin_h = MyQSpin(self.w_height)
        self.spin_h.setObjectName(u"spin_h")
        self.spin_h.setEnabled(True)
        self.spin_h.setMinimumSize(QSize(90, 24))
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
        self.verticalLayout_6 = QVBoxLayout(self.w_button_resize)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_button_resize = QLabel(self.w_button_resize)
        self.label_button_resize.setObjectName(u"label_button_resize")
        sizePolicy1.setHeightForWidth(self.label_button_resize.sizePolicy().hasHeightForWidth())
        self.label_button_resize.setSizePolicy(sizePolicy1)
        self.label_button_resize.setMinimumSize(QSize(0, 18))
        self.label_button_resize.setMaximumSize(QSize(16777215, 18))
        self.label_button_resize.setFont(font3)

        self.verticalLayout_6.addWidget(self.label_button_resize)

        self.button_resize = QToolButton(self.w_button_resize)
        self.button_resize.setObjectName(u"button_resize")
        self.button_resize.setMinimumSize(QSize(26, 26))
        self.button_resize.setMaximumSize(QSize(26, 26))
        icon8 = QIcon()
        icon8.addFile(u""+ icons_path +"resize_icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_resize.setIcon(icon8)
        self.button_resize.setIconSize(QSize(18, 18))

        self.verticalLayout_6.addWidget(self.button_resize)


        self.horizontalLayout_7.addWidget(self.w_button_resize)


        self.verticalLayout_8.addWidget(self.w_SizeImg)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_7.addWidget(self.scrollArea)

        QWidget.setTabOrder(self.button_back, self.button_forward)
        QWidget.setTabOrder(self.button_forward, self.button_close_tab)
        QWidget.setTabOrder(self.button_close_tab, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.edit_path)
        QWidget.setTabOrder(self.edit_path, self.button_path)
        QWidget.setTabOrder(self.button_path, self.edit_root)
        QWidget.setTabOrder(self.edit_root, self.button_import)
        QWidget.setTabOrder(self.button_import, self.spin_range_from)
        QWidget.setTabOrder(self.spin_range_from, self.spin_range_to)
        QWidget.setTabOrder(self.spin_range_to, self.spin_selected)
        QWidget.setTabOrder(self.spin_selected, self.spin_frame)
        QWidget.setTabOrder(self.spin_frame, self.list_images)
        QWidget.setTabOrder(self.list_images, self.check_TR_sequence)
        QWidget.setTabOrder(self.check_TR_sequence, self.check_subtract)
        QWidget.setTabOrder(self.check_subtract, self.spin_x)
        QWidget.setTabOrder(self.spin_x, self.spin_y)
        QWidget.setTabOrder(self.spin_y, self.spin_w)
        QWidget.setTabOrder(self.spin_w, self.spin_h)
        QWidget.setTabOrder(self.spin_h, self.button_resize)

        self.retranslateUi(ImportTab)

        QMetaObject.connectSlotsByName(ImportTab)
    # setupUi

    def retranslateUi(self, ImportTab):
        ImportTab.setWindowTitle(QCoreApplication.translate("ImportTab", u"Import", None))
#if QT_CONFIG(accessibility)
        ImportTab.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.icon.setText("")
        self.name_tab.setText(QCoreApplication.translate("ImportTab", u" Input", None))
#if QT_CONFIG(tooltip)
        self.button_data.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.button_data.setText("")
#if QT_CONFIG(shortcut)
        self.button_data.setShortcut(QCoreApplication.translate("ImportTab", u"Backspace, Return", None))
#endif // QT_CONFIG(shortcut)
        self.label_number.setText(QCoreApplication.translate("ImportTab", u"1", None))
#if QT_CONFIG(tooltip)
        self.button_back.setToolTip(QCoreApplication.translate("ImportTab", u"Undo", None))
#endif // QT_CONFIG(tooltip)
        self.button_back.setText("")
#if QT_CONFIG(tooltip)
        self.button_forward.setToolTip(QCoreApplication.translate("ImportTab", u"Redo", None))
#endif // QT_CONFIG(tooltip)
        self.button_forward.setText("")
#if QT_CONFIG(tooltip)
        self.button_close_tab.setToolTip(QCoreApplication.translate("ImportTab", u"Close tab", None))
#endif // QT_CONFIG(tooltip)
        self.button_close_tab.setText("")
#if QT_CONFIG(shortcut)
        self.button_close_tab.setShortcut(QCoreApplication.translate("ImportTab", u"Alt+I", None))
#endif // QT_CONFIG(shortcut)
        self.label_path.setText(QCoreApplication.translate("ImportTab", u"Input folder path", None))
#if QT_CONFIG(tooltip)
        self.edit_path.setToolTip(QCoreApplication.translate("ImportTab", u"Path of the directory containing the image files", None))
#endif // QT_CONFIG(tooltip)
        self.edit_path.setText(QCoreApplication.translate("ImportTab", u".\\img\\fold3\\", None))
        self.label_check_path.setText("")
        self.label_path_2.setText("")
#if QT_CONFIG(tooltip)
        self.button_path.setToolTip(QCoreApplication.translate("ImportTab", u"Explore and find the path of the directory containing the image files", None))
#endif // QT_CONFIG(tooltip)
        self.button_path.setText("")
#if QT_CONFIG(shortcut)
        self.button_path.setShortcut(QCoreApplication.translate("ImportTab", u"Ctrl+Alt+I", None))
#endif // QT_CONFIG(shortcut)
        self.label_root.setText(QCoreApplication.translate("ImportTab", u"Pattern of image filenames", None))
#if QT_CONFIG(tooltip)
        self.edit_root.setToolTip(QCoreApplication.translate("ImportTab", u"Pattern of the filenames of the images", None))
#endif // QT_CONFIG(tooltip)
        self.edit_root.setText(QCoreApplication.translate("ImportTab", u"img_cam0_a*.png ; img_cam0_b*.png", None))
        self.label_check_root.setText("")
        self.label_root_2.setText("")
#if QT_CONFIG(tooltip)
        self.button_import.setToolTip(QCoreApplication.translate("ImportTab", u"Explore and find directly the image files", None))
#endif // QT_CONFIG(tooltip)
        self.button_import.setText("")
#if QT_CONFIG(shortcut)
        self.button_import.setShortcut(QCoreApplication.translate("ImportTab", u"Ctrl+Alt+J", None))
#endif // QT_CONFIG(shortcut)
        self.label_range_from.setText(QCoreApplication.translate("ImportTab", u"from", None))
#if QT_CONFIG(tooltip)
        self.spin_range_from.setToolTip(QCoreApplication.translate("ImportTab", u"Number of the first image in the sequence to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_range_to.setText(QCoreApplication.translate("ImportTab", u"# of image pairs", None))
#if QT_CONFIG(tooltip)
        self.spin_range_to.setToolTip(QCoreApplication.translate("ImportTab", u"Number of image pairs to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_list.setText(QCoreApplication.translate("ImportTab", u"Identified image pairs", None))
        self.label_selected.setText(QCoreApplication.translate("ImportTab", u"selected", None))
#if QT_CONFIG(tooltip)
        self.spin_selected.setToolTip(QCoreApplication.translate("ImportTab", u"Number of the selected image", None))
#endif // QT_CONFIG(tooltip)
        self.label_frame.setText(QCoreApplication.translate("ImportTab", u"frame", None))
#if QT_CONFIG(tooltip)
        self.spin_frame.setToolTip(QCoreApplication.translate("ImportTab", u"Frame of the selected image", None))
#endif // QT_CONFIG(tooltip)

        __sortingEnabled = self.list_images.isSortingEnabled()
        self.list_images.setSortingEnabled(False)
        ___qlistwidgetitem = self.list_images.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem1 = self.list_images.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem2 = self.list_images.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem3 = self.list_images.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem4 = self.list_images.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("ImportTab", u"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", None));
        ___qlistwidgetitem5 = self.list_images.item(5)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem6 = self.list_images.item(6)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem7 = self.list_images.item(7)
        ___qlistwidgetitem7.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem8 = self.list_images.item(8)
        ___qlistwidgetitem8.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem9 = self.list_images.item(9)
        ___qlistwidgetitem9.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem10 = self.list_images.item(10)
        ___qlistwidgetitem10.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem11 = self.list_images.item(11)
        ___qlistwidgetitem11.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem12 = self.list_images.item(12)
        ___qlistwidgetitem12.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        ___qlistwidgetitem13 = self.list_images.item(13)
        ___qlistwidgetitem13.setText(QCoreApplication.translate("ImportTab", u"New Item", None));
        self.list_images.setSortingEnabled(__sortingEnabled)

#if QT_CONFIG(tooltip)
        self.list_images.setToolTip(QCoreApplication.translate("ImportTab", u"List of identified image pairs (select to show)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.check_TR_sequence.setToolTip(QCoreApplication.translate("ImportTab", u"If activated, the images are processed in time-resolved mode", None))
#endif // QT_CONFIG(tooltip)
        self.check_TR_sequence.setText(QCoreApplication.translate("ImportTab", u"Time-resolved series", None))
#if QT_CONFIG(tooltip)
        self.check_subtract.setToolTip(QCoreApplication.translate("ImportTab", u"Subtract ensemble minimum", None))
#endif // QT_CONFIG(tooltip)
        self.check_subtract.setText(QCoreApplication.translate("ImportTab", u"subtract minimum", None))
        self.label_x.setText(QCoreApplication.translate("ImportTab", u"X0 (# column)", None))
#if QT_CONFIG(tooltip)
        self.spin_x.setToolTip(QCoreApplication.translate("ImportTab", u"First column of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_y.setText(QCoreApplication.translate("ImportTab", u"Y0 (# row)", None))
#if QT_CONFIG(tooltip)
        self.spin_y.setToolTip(QCoreApplication.translate("ImportTab", u"First row of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_w.setText(QCoreApplication.translate("ImportTab", u"Width (pixels)", None))
#if QT_CONFIG(tooltip)
        self.spin_w.setToolTip(QCoreApplication.translate("ImportTab", u"Width of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_h.setText(QCoreApplication.translate("ImportTab", u"Height (pixels)", None))
#if QT_CONFIG(tooltip)
        self.spin_h.setToolTip(QCoreApplication.translate("ImportTab", u"Heigth of the image area to process", None))
#endif // QT_CONFIG(tooltip)
        self.label_button_resize.setText("")
#if QT_CONFIG(tooltip)
        self.button_resize.setToolTip(QCoreApplication.translate("ImportTab", u"Restore full image", None))
#endif // QT_CONFIG(tooltip)
        self.button_resize.setText("")
    # retranslateUi

