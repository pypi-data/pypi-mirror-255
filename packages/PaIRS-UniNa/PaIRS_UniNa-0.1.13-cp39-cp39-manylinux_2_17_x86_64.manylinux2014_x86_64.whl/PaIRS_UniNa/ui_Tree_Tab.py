from .addwidgets_ps import icons_path
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Tree_TabwWMUIM.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QScrollArea, QSizePolicy, QSpacerItem,
    QToolButton, QTreeWidgetItem, QVBoxLayout, QWidget)

from .addwidgets_ps import myQTreeWidget

class Ui_TreeTab(object):
    def setupUi(self, TreeTab):
        if not TreeTab.objectName():
            TreeTab.setObjectName(u"TreeTab")
        TreeTab.resize(500, 680)
        TreeTab.setMinimumSize(QSize(260, 340))
        TreeTab.setMaximumSize(QSize(1000, 16777215))
        font = QFont()
        font.setPointSize(11)
        TreeTab.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u""+ icons_path +"checklist.png", QSize(), QIcon.Normal, QIcon.Off)
        TreeTab.setWindowIcon(icon1)
        self.verticalLayout_7 = QVBoxLayout(TreeTab)
        self.verticalLayout_7.setSpacing(5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(10, 10, 10, 10)
        self.w_Mode = QWidget(TreeTab)
        self.w_Mode.setObjectName(u"w_Mode")
        self.w_Mode.setMinimumSize(QSize(0, 40))
        self.w_Mode.setMaximumSize(QSize(16777215, 40))
        self.w_Mode.setFont(font)
        self.horizontalLayout_5 = QHBoxLayout(self.w_Mode)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 10)
        self.icon = QLabel(self.w_Mode)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(35, 35))
        self.icon.setMaximumSize(QSize(35, 35))
        self.icon.setPixmap(QPixmap(u""+ icons_path +"checklist.png"))
        self.icon.setScaledContents(True)

        self.horizontalLayout_5.addWidget(self.icon)

        self.name_tab = QLabel(self.w_Mode)
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
        self.label_number.setMinimumSize(QSize(15, 0))
        self.label_number.setMaximumSize(QSize(30, 16777215))
        font2 = QFont()
        font2.setPointSize(9)
        self.label_number.setFont(font2)
        self.label_number.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_number)

        self.button_back = QToolButton(self.w_Mode)
        self.button_back.setObjectName(u"button_back")
        self.button_back.setMinimumSize(QSize(30, 30))
        self.button_back.setMaximumSize(QSize(30, 30))
        icon2 = QIcon()
        icon2.addFile(u""+ icons_path +"undo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_back.setIcon(icon2)
        self.button_back.setIconSize(QSize(24, 24))

        self.horizontalLayout_5.addWidget(self.button_back)

        self.button_forward = QToolButton(self.w_Mode)
        self.button_forward.setObjectName(u"button_forward")
        self.button_forward.setMinimumSize(QSize(30, 30))
        self.button_forward.setMaximumSize(QSize(30, 30))
        icon3 = QIcon()
        icon3.addFile(u""+ icons_path +"redo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_forward.setIcon(icon3)
        self.button_forward.setIconSize(QSize(24, 24))

        self.horizontalLayout_5.addWidget(self.button_forward)


        self.verticalLayout_7.addWidget(self.w_Mode)

        self.line = QFrame(TreeTab)
        self.line.setObjectName(u"line")
        self.line.setMinimumSize(QSize(0, 5))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_7.addWidget(self.line)

        self.scrollArea = QScrollArea(TreeTab)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 480, 607))
        self.verticalLayout_8 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_8.setSpacing(10)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 5, 10, 0)
        self.w_Tree_past = QWidget(self.scrollAreaWidgetContents)
        self.w_Tree_past.setObjectName(u"w_Tree_past")
        self.verticalLayout = QVBoxLayout(self.w_Tree_past)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.w_Past_controls = QWidget(self.w_Tree_past)
        self.w_Past_controls.setObjectName(u"w_Past_controls")
        self.w_Past_controls.setMinimumSize(QSize(0, 25))
        self.w_Past_controls.setMaximumSize(QSize(16777215, 25))
        self.pastCtrlLay = QHBoxLayout(self.w_Past_controls)
        self.pastCtrlLay.setSpacing(3)
        self.pastCtrlLay.setObjectName(u"pastCtrlLay")
        self.pastCtrlLay.setContentsMargins(0, 0, 0, 0)
        self.label_Tree_past = QLabel(self.w_Past_controls)
        self.label_Tree_past.setObjectName(u"label_Tree_past")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_Tree_past.sizePolicy().hasHeightForWidth())
        self.label_Tree_past.setSizePolicy(sizePolicy1)
        self.label_Tree_past.setMinimumSize(QSize(0, 20))
        self.label_Tree_past.setMaximumSize(QSize(16777215, 20))
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(False)
        font3.setItalic(True)
        self.label_Tree_past.setFont(font3)
        self.label_Tree_past.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.pastCtrlLay.addWidget(self.label_Tree_past)

        self.button_down_past = QToolButton(self.w_Past_controls)
        self.button_down_past.setObjectName(u"button_down_past")
        self.button_down_past.setMinimumSize(QSize(25, 25))
        self.button_down_past.setMaximumSize(QSize(25, 25))
        icon4 = QIcon()
        icon4.addFile(u""+ icons_path +"down.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_down_past.setIcon(icon4)
        self.button_down_past.setIconSize(QSize(18, 18))
        self.button_down_past.setArrowType(Qt.NoArrow)

        self.pastCtrlLay.addWidget(self.button_down_past)

        self.button_up_past = QToolButton(self.w_Past_controls)
        self.button_up_past.setObjectName(u"button_up_past")
        self.button_up_past.setMinimumSize(QSize(25, 25))
        self.button_up_past.setMaximumSize(QSize(25, 25))
        icon5 = QIcon()
        icon5.addFile(u""+ icons_path +"up.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_up_past.setIcon(icon5)
        self.button_up_past.setIconSize(QSize(18, 18))
        self.button_up_past.setArrowType(Qt.NoArrow)

        self.pastCtrlLay.addWidget(self.button_up_past)

        self.button_import_past = QToolButton(self.w_Past_controls)
        self.button_import_past.setObjectName(u"button_import_past")
        self.button_import_past.setMinimumSize(QSize(25, 25))
        self.button_import_past.setMaximumSize(QSize(25, 25))
        icon6 = QIcon()
        icon6.addFile(u""+ icons_path +"import.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_import_past.setIcon(icon6)
        self.button_import_past.setIconSize(QSize(18, 18))

        self.pastCtrlLay.addWidget(self.button_import_past)

        self.button_restore = QToolButton(self.w_Past_controls)
        self.button_restore.setObjectName(u"button_restore")
        self.button_restore.setMinimumSize(QSize(25, 25))
        self.button_restore.setMaximumSize(QSize(25, 25))
        icon7 = QIcon()
        icon7.addFile(u""+ icons_path +"restore.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_restore.setIcon(icon7)
        self.button_restore.setIconSize(QSize(20, 20))

        self.pastCtrlLay.addWidget(self.button_restore)

        self.button_delete_past = QToolButton(self.w_Past_controls)
        self.button_delete_past.setObjectName(u"button_delete_past")
        self.button_delete_past.setMinimumSize(QSize(25, 25))
        self.button_delete_past.setMaximumSize(QSize(25, 25))
        icon8 = QIcon()
        icon8.addFile(u""+ icons_path +"delete.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_delete_past.setIcon(icon8)
        self.button_delete_past.setIconSize(QSize(20, 20))

        self.pastCtrlLay.addWidget(self.button_delete_past)

        self.button_clean_past = QToolButton(self.w_Past_controls)
        self.button_clean_past.setObjectName(u"button_clean_past")
        self.button_clean_past.setMinimumSize(QSize(25, 25))
        self.button_clean_past.setMaximumSize(QSize(25, 25))
        icon9 = QIcon()
        icon9.addFile(u""+ icons_path +"clean_queue.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_clean_past.setIcon(icon9)
        self.button_clean_past.setIconSize(QSize(20, 20))

        self.pastCtrlLay.addWidget(self.button_clean_past)


        self.verticalLayout.addWidget(self.w_Past_controls)

        self.tree_past = myQTreeWidget(self.w_Tree_past)
        QTreeWidgetItem(self.tree_past)
        self.tree_past.setObjectName(u"tree_past")
        self.tree_past.setStyleSheet(u"QTreeView::item:selected {\n"
"    border: 1px solid;\n"
"	border-color: rgba(154, 166, 255, 255);\n"
"    background-color: rgba(214, 226, 255, 65);\n"
"    color: black\n"
"}\n"
"QTreeView::item:selected:focus{\n"
"    border: 1px solid blue;\n"
"    background-color: rgb(214, 226, 255);\n"
"    color: black\n"
"}")
        self.tree_past.setAlternatingRowColors(True)
        self.tree_past.setIndentation(10)
        self.tree_past.setUniformRowHeights(True)
        self.tree_past.setWordWrap(False)
        self.tree_past.setColumnCount(1)
        self.tree_past.header().setVisible(False)
        self.tree_past.header().setCascadingSectionResizes(False)
        self.tree_past.header().setMinimumSectionSize(15)
        self.tree_past.header().setHighlightSections(False)
        self.tree_past.header().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.tree_past)


        self.verticalLayout_8.addWidget(self.w_Tree_past)

        self.w_Tree_current = QWidget(self.scrollAreaWidgetContents)
        self.w_Tree_current.setObjectName(u"w_Tree_current")
        self.verticalLayout_2 = QVBoxLayout(self.w_Tree_current)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_Tree_current = QLabel(self.w_Tree_current)
        self.label_Tree_current.setObjectName(u"label_Tree_current")
        sizePolicy1.setHeightForWidth(self.label_Tree_current.sizePolicy().hasHeightForWidth())
        self.label_Tree_current.setSizePolicy(sizePolicy1)
        self.label_Tree_current.setMinimumSize(QSize(0, 20))
        self.label_Tree_current.setMaximumSize(QSize(16777215, 20))
        self.label_Tree_current.setFont(font3)
        self.label_Tree_current.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.label_Tree_current)

        self.tree_current = myQTreeWidget(self.w_Tree_current)
        QTreeWidgetItem(self.tree_current)
        self.tree_current.setObjectName(u"tree_current")
        self.tree_current.setMinimumSize(QSize(0, 26))
        self.tree_current.setMaximumSize(QSize(16777215, 26))
        self.tree_current.setStyleSheet(u"QTreeView::item:selected {\n"
"    border: 1px solid;\n"
"	border-color: rgba(154, 166, 255, 255);\n"
"    background-color: rgba(214, 226, 255, 65);\n"
"    color: black\n"
"}\n"
"QTreeView::item:selected:focus{\n"
"    border: 1px solid blue;\n"
"    background-color: rgb(214, 226, 255);\n"
"    color: black\n"
"}\n"
"")
        self.tree_current.setIndentation(10)
        self.tree_current.setUniformRowHeights(True)
        self.tree_current.setColumnCount(1)
        self.tree_current.header().setVisible(False)
        self.tree_current.header().setCascadingSectionResizes(False)
        self.tree_current.header().setMinimumSectionSize(15)
        self.tree_current.header().setHighlightSections(False)
        self.tree_current.header().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.tree_current)


        self.verticalLayout_8.addWidget(self.w_Tree_current)

        self.w_Tree_future = QWidget(self.scrollAreaWidgetContents)
        self.w_Tree_future.setObjectName(u"w_Tree_future")
        self.verticalLayout_3 = QVBoxLayout(self.w_Tree_future)
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.w_Future_controls = QWidget(self.w_Tree_future)
        self.w_Future_controls.setObjectName(u"w_Future_controls")
        self.futCtrlLay = QHBoxLayout(self.w_Future_controls)
        self.futCtrlLay.setSpacing(3)
        self.futCtrlLay.setObjectName(u"futCtrlLay")
        self.futCtrlLay.setContentsMargins(0, 0, 0, 0)
        self.label_Tree_future = QLabel(self.w_Future_controls)
        self.label_Tree_future.setObjectName(u"label_Tree_future")
        sizePolicy1.setHeightForWidth(self.label_Tree_future.sizePolicy().hasHeightForWidth())
        self.label_Tree_future.setSizePolicy(sizePolicy1)
        self.label_Tree_future.setMinimumSize(QSize(0, 20))
        self.label_Tree_future.setMaximumSize(QSize(16777215, 20))
        self.label_Tree_future.setFont(font3)
        self.label_Tree_future.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.futCtrlLay.addWidget(self.label_Tree_future)

        self.button_down_future = QToolButton(self.w_Future_controls)
        self.button_down_future.setObjectName(u"button_down_future")
        self.button_down_future.setMinimumSize(QSize(25, 25))
        self.button_down_future.setMaximumSize(QSize(25, 25))
        self.button_down_future.setIcon(icon4)
        self.button_down_future.setIconSize(QSize(18, 18))
        self.button_down_future.setArrowType(Qt.NoArrow)

        self.futCtrlLay.addWidget(self.button_down_future)

        self.button_up_future = QToolButton(self.w_Future_controls)
        self.button_up_future.setObjectName(u"button_up_future")
        self.button_up_future.setMinimumSize(QSize(25, 25))
        self.button_up_future.setMaximumSize(QSize(25, 25))
        self.button_up_future.setIcon(icon5)
        self.button_up_future.setIconSize(QSize(18, 18))
        self.button_up_future.setArrowType(Qt.NoArrow)

        self.futCtrlLay.addWidget(self.button_up_future)

        self.button_edit_item = QToolButton(self.w_Future_controls)
        self.button_edit_item.setObjectName(u"button_edit_item")
        self.button_edit_item.setMinimumSize(QSize(25, 25))
        self.button_edit_item.setMaximumSize(QSize(25, 25))
        icon10 = QIcon()
        icon10.addFile(u""+ icons_path +"pencil_bw.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_edit_item.setIcon(icon10)
        self.button_edit_item.setIconSize(QSize(18, 18))
        self.button_edit_item.setCheckable(True)
        self.button_edit_item.setArrowType(Qt.NoArrow)

        self.futCtrlLay.addWidget(self.button_edit_item)

        self.button_delete_future = QToolButton(self.w_Future_controls)
        self.button_delete_future.setObjectName(u"button_delete_future")
        self.button_delete_future.setMinimumSize(QSize(25, 25))
        self.button_delete_future.setMaximumSize(QSize(25, 25))
        self.button_delete_future.setIcon(icon8)
        self.button_delete_future.setIconSize(QSize(20, 20))

        self.futCtrlLay.addWidget(self.button_delete_future)

        self.button_clean_future = QToolButton(self.w_Future_controls)
        self.button_clean_future.setObjectName(u"button_clean_future")
        self.button_clean_future.setMinimumSize(QSize(25, 25))
        self.button_clean_future.setMaximumSize(QSize(25, 25))
        self.button_clean_future.setIcon(icon9)
        self.button_clean_future.setIconSize(QSize(20, 20))

        self.futCtrlLay.addWidget(self.button_clean_future)


        self.verticalLayout_3.addWidget(self.w_Future_controls)

        self.tree_future = myQTreeWidget(self.w_Tree_future)
        QTreeWidgetItem(self.tree_future)
        QTreeWidgetItem(self.tree_future)
        self.tree_future.setObjectName(u"tree_future")
        self.tree_future.setStyleSheet(u"QTreeView::item:selected {\n"
"    border: 1px solid;\n"
"	border-color: rgba(154, 166, 255, 255);\n"
"    background-color: rgba(214, 226, 255, 65);\n"
"    color: black\n"
"}\n"
"QTreeView::item:selected:focus{\n"
"    border: 1px solid blue;\n"
"    background-color: rgb(214, 226, 255);\n"
"    color: black\n"
"}")
        self.tree_future.setAlternatingRowColors(True)
        self.tree_future.setIndentation(10)
        self.tree_future.setUniformRowHeights(True)
        self.tree_future.setWordWrap(False)
        self.tree_future.setColumnCount(1)
        self.tree_future.header().setVisible(False)
        self.tree_future.header().setCascadingSectionResizes(False)
        self.tree_future.header().setMinimumSectionSize(15)
        self.tree_future.header().setHighlightSections(False)
        self.tree_future.header().setStretchLastSection(True)

        self.verticalLayout_3.addWidget(self.tree_future)


        self.verticalLayout_8.addWidget(self.w_Tree_future)

        self.w_proc_Buttons = QWidget(self.scrollAreaWidgetContents)
        self.w_proc_Buttons.setObjectName(u"w_proc_Buttons")
        self.horizontalLayout = QHBoxLayout(self.w_proc_Buttons)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.button_min = QToolButton(self.w_proc_Buttons)
        self.button_min.setObjectName(u"button_min")
        self.button_min.setMinimumSize(QSize(75, 30))
        self.button_min.setMaximumSize(QSize(75, 30))
        font4 = QFont()
        font4.setPointSize(11)
        font4.setBold(False)
        font4.setStrikeOut(False)
        self.button_min.setFont(font4)
        icon11 = QIcon()
        icon11.addFile(u""+ icons_path +"add.png", QSize(), QIcon.Normal, QIcon.Off)
        self.button_min.setIcon(icon11)
        self.button_min.setIconSize(QSize(20, 20))
        self.button_min.setCheckable(False)
        self.button_min.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.button_min)

        self.button_PIV = QToolButton(self.w_proc_Buttons)
        self.button_PIV.setObjectName(u"button_PIV")
        self.button_PIV.setMinimumSize(QSize(75, 30))
        self.button_PIV.setMaximumSize(QSize(75, 30))
        self.button_PIV.setFont(font4)
        self.button_PIV.setIcon(icon11)
        self.button_PIV.setIconSize(QSize(20, 20))
        self.button_PIV.setCheckable(False)
        self.button_PIV.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.button_PIV)

        self.hs_proc_Buttons = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.hs_proc_Buttons)


        self.verticalLayout_8.addWidget(self.w_proc_Buttons)

        self.verticalLayout_8.setStretch(0, 1)
        self.verticalLayout_8.setStretch(2, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_7.addWidget(self.scrollArea)

        QWidget.setTabOrder(self.button_back, self.button_forward)
        QWidget.setTabOrder(self.button_forward, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.tree_past)
        QWidget.setTabOrder(self.tree_past, self.button_down_past)
        QWidget.setTabOrder(self.button_down_past, self.button_up_past)
        QWidget.setTabOrder(self.button_up_past, self.button_import_past)
        QWidget.setTabOrder(self.button_import_past, self.tree_current)
        QWidget.setTabOrder(self.tree_current, self.tree_future)
        QWidget.setTabOrder(self.tree_future, self.button_down_future)
        QWidget.setTabOrder(self.button_down_future, self.button_up_future)
        QWidget.setTabOrder(self.button_up_future, self.button_edit_item)
        QWidget.setTabOrder(self.button_edit_item, self.button_min)
        QWidget.setTabOrder(self.button_min, self.button_PIV)

        self.retranslateUi(TreeTab)

        QMetaObject.connectSlotsByName(TreeTab)
    # setupUi

    def retranslateUi(self, TreeTab):
        TreeTab.setWindowTitle(QCoreApplication.translate("TreeTab", u"Tree", None))
#if QT_CONFIG(accessibility)
        TreeTab.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.icon.setText("")
        self.name_tab.setText(QCoreApplication.translate("TreeTab", u"Queue", None))
        self.label_number.setText(QCoreApplication.translate("TreeTab", u"1", None))
#if QT_CONFIG(tooltip)
        self.button_back.setToolTip(QCoreApplication.translate("TreeTab", u"Undo", None))
#endif // QT_CONFIG(tooltip)
        self.button_back.setText("")
#if QT_CONFIG(shortcut)
        self.button_back.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+Z", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_forward.setToolTip(QCoreApplication.translate("TreeTab", u"Redo", None))
#endif // QT_CONFIG(tooltip)
        self.button_forward.setText("")
#if QT_CONFIG(shortcut)
        self.button_forward.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+Y", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.label_Tree_past.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_Tree_past.setText(QCoreApplication.translate("TreeTab", u"Past", None))
#if QT_CONFIG(tooltip)
        self.button_down_past.setToolTip(QCoreApplication.translate("TreeTab", u"Move item down in the list", None))
#endif // QT_CONFIG(tooltip)
        self.button_down_past.setText("")
#if QT_CONFIG(shortcut)
        self.button_down_past.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+Down", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_up_past.setToolTip(QCoreApplication.translate("TreeTab", u"Move item up in the list", None))
#endif // QT_CONFIG(tooltip)
        self.button_up_past.setText("")
#if QT_CONFIG(shortcut)
        self.button_up_past.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+Up", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_import_past.setToolTip(QCoreApplication.translate("TreeTab", u"Import process file from disk", None))
#endif // QT_CONFIG(tooltip)
        self.button_import_past.setText("")
#if QT_CONFIG(shortcut)
        self.button_import_past.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_restore.setToolTip(QCoreApplication.translate("TreeTab", u"Restore process", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.button_restore.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+R", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_delete_past.setToolTip(QCoreApplication.translate("TreeTab", u"Delete process", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.button_delete_past.setShortcut(QCoreApplication.translate("TreeTab", u"Backspace", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_clean_past.setToolTip(QCoreApplication.translate("TreeTab", u"Clean the whole queue", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.button_clean_past.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+Shift+T", None))
#endif // QT_CONFIG(shortcut)
        ___qtreewidgetitem = self.tree_past.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("TreeTab", u"Name", None));

        __sortingEnabled = self.tree_past.isSortingEnabled()
        self.tree_past.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.tree_past.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("TreeTab", u"first", None));
        self.tree_past.setSortingEnabled(__sortingEnabled)

        self.label_Tree_current.setText(QCoreApplication.translate("TreeTab", u"Current", None))
        ___qtreewidgetitem2 = self.tree_current.headerItem()
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("TreeTab", u"Name", None));

        __sortingEnabled1 = self.tree_current.isSortingEnabled()
        self.tree_current.setSortingEnabled(False)
        ___qtreewidgetitem3 = self.tree_current.topLevelItem(0)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("TreeTab", u"current", None));
        self.tree_current.setSortingEnabled(__sortingEnabled1)

        self.label_Tree_future.setText(QCoreApplication.translate("TreeTab", u"Future", None))
#if QT_CONFIG(tooltip)
        self.button_down_future.setToolTip(QCoreApplication.translate("TreeTab", u"Move item down in the list", None))
#endif // QT_CONFIG(tooltip)
        self.button_down_future.setText("")
#if QT_CONFIG(shortcut)
        self.button_down_future.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+Down", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_up_future.setToolTip(QCoreApplication.translate("TreeTab", u"Move item up in the list", None))
#endif // QT_CONFIG(tooltip)
        self.button_up_future.setText("")
#if QT_CONFIG(shortcut)
        self.button_up_future.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+Up", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_edit_item.setToolTip(QCoreApplication.translate("TreeTab", u"Edit item", None))
#endif // QT_CONFIG(tooltip)
        self.button_edit_item.setText("")
#if QT_CONFIG(shortcut)
        self.button_edit_item.setShortcut(QCoreApplication.translate("TreeTab", u"F2", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_delete_future.setToolTip(QCoreApplication.translate("TreeTab", u"Delete process", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.button_delete_future.setShortcut(QCoreApplication.translate("TreeTab", u"Backspace", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_clean_future.setToolTip(QCoreApplication.translate("TreeTab", u"Clean the whole queue", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.button_clean_future.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+T", None))
#endif // QT_CONFIG(shortcut)
        ___qtreewidgetitem4 = self.tree_future.headerItem()
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("TreeTab", u"Name", None));

        __sortingEnabled2 = self.tree_future.isSortingEnabled()
        self.tree_future.setSortingEnabled(False)
        ___qtreewidgetitem5 = self.tree_future.topLevelItem(0)
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("TreeTab", u"next #1", None));
        ___qtreewidgetitem6 = self.tree_future.topLevelItem(1)
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("TreeTab", u"next #2", None));
        self.tree_future.setSortingEnabled(__sortingEnabled2)

#if QT_CONFIG(tooltip)
        self.button_min.setToolTip(QCoreApplication.translate("TreeTab", u"Add ensemble minimum computation to queue", None))
#endif // QT_CONFIG(tooltip)
        self.button_min.setText(QCoreApplication.translate("TreeTab", u" MIN", None))
#if QT_CONFIG(shortcut)
        self.button_min.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+M", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.button_PIV.setToolTip(QCoreApplication.translate("TreeTab", u"Add PIV process to queue", None))
#endif // QT_CONFIG(tooltip)
        self.button_PIV.setText(QCoreApplication.translate("TreeTab", u" PIV", None))
#if QT_CONFIG(shortcut)
        self.button_PIV.setShortcut(QCoreApplication.translate("TreeTab", u"Ctrl+,", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

