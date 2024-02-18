import PySide6.QtGui
from .ui_gCalVi import *
from .ui_infoCalVi import *
from .TabTools import *
#from procTools import *

from .Import_Tab_CalVi import *
from .Process_Tab_CalVi import *
from .Vis_Tab_CalVi import *
from .Log_Tab import *
from .Whatsnew import *

from .gPalette import darkPalette,lightPalette

import concurrent.futures

from .__init__ import __version__,__subversion__,__year__,__mail__,__website__

version=__version__
year=__year__
mail=__mail__
website=__website__
uicfg_version='0.0.0'
w_button_min_size=680
Flag_fullDEBUG=True
Flag_ResetScaleOnChanges=False
Flag_DEBUG_CleanLaunch=False


#********************************************* Additional windows
class FloatingObject(QMainWindow):
    def closeEvent(self, event):
        if not self.gui.CALpar.FlagUndocked:
            self.hide()
        else:
            self.gui.close_tab(self.tab)
            #self.button.setChecked(False)
            #setattr(self.gui.CALpar,'Flag'+self.name,False)
            #ind=self.gui.opwidnames.index(self.name)
            #if ind<3:
            #    self.gui.CALpar.prevTab=self.gui.CALpar.lastTab
            #    self.gui.CALpar.lastTab=ind
            #self.hide()   
        
    def __init__(self,parent,tab):
        super().__init__()
        self.gui:gCalVi=parent
        self.name=''
        self.button=None
        self.tab=tab
        self.setup()
        
    def setup(self):
        tab=self.tab
        if type(tab)==CollapsibleBox:
            self.setWindowTitle(tab.toggle_button.text())
            self.setWindowIcon(self.gui.windowIcon())
            parent=tab
        elif type(tab) in (Import_Tab_CalVi,Process_Tab_CalVi,Vis_Tab_CalVi): 
            self.name=tab.ui.name_tab.text().replace(' ','')
            self.setWindowTitle(tab.ui.name_tab.text())
            self.setWindowIcon(tab.ui.icon.pixmap())
            parent=tab.parent()
        else:
            self.setWindowTitle(self.gui.windowTitle())
            self.setWindowIcon(self.gui.windowIcon())
            parent=tab
        if type(parent.parent()) in (QSplitter,QLayout,myQSplitter):
            self.lay:QLayout=parent.parent()
        else:
            self.lay:QLayout=parent.parent().layout()
        self.pa=parent
        self.index=self.lay.indexOf(parent)
        #self.setCentralWidget(parent)            

        self.setBaseSize(parent.baseSize())
        self.setAutoFillBackground(False) 
        self.setMinimumSize(parent.minimumSize())
        self.setMaximumSize(parent.maximumSize())
        
        #pri.Info.magenta(f'{self.name}  Sizes: min {parent.minimumSize()}, max {parent.maximumSize()},'+\
        #            f' min {self.minimumSize()}, max {self.maximumSize()}')
        
        if self.name:
            self.button=getattr(self.gui.ui,'button_'+self.name)

    def setFloat(self):
        self.setCentralWidget(self.pa)
        self.centralWidget().setMinimumSize(self.pa.minimumSize())
        self.centralWidget().setMaximumSize(self.pa.maximumSize())

class FloatingWidget(FloatingObject):
    def closeEvent(self, event):
        index=min([self.index,self.lay.count()-1])
        self.lay.insertWidget(index,self.pa)
        self.close()
        i=self.gui.floatw.index(self)
        self.gui.floatw.pop(i)
        self.gui.undockTabs()

    def __init__(self,parent,tab):
        super().__init__(parent,tab)

        geo=self.pa.geometry()
        geoP=self.gui.geometry()
        x=geoP.x()+int(geoP.width()*0.5)-int(geo.width()*0.5)
        y=geoP.y()+int(geoP.height()*0.5)-int(geo.height()*0.5)
        self.setGeometry(x,y,geo.width(),geo.height())
        self.setFloat()
        self.show()
            
class infoCalVi(QMainWindow):
    def __init__(self,gui):
        super().__init__()
        ui=Ui_InfoCalVi()
        ui.setupUi(self)
        self.ui=ui
        setupWid(self)
        
        infotext=self.ui.info.text().replace('#.#.#',version)
        infotext=infotext.replace('yyyy',year)
        mailString=f'<a href="mailto:{mail}"><span style=" text-decoration: underline; color:#0000ff; font-size:11pt">{mail}</a>'
        infotext=infotext.replace('mmmm',mailString)
        websiteString=f'<a href="{website}"><span style=" text-decoration: underline; color:#0000ff; font-size:11pt">{website}</a>'
        infotext=infotext.replace('wwww',websiteString)
        self.ui.info.setText(infotext)

        self.fontPixelSize=gui.CALpar.fontPixelSize
        self.setFontSizeText()

        self.gui=gui
        for w in self.findChildren(QObject):
            if hasattr(w,'keyPressEvent'):
                def createKeyPressFun(w):
                    def KeyPressFun(e):
                        if w.hasFocus():
                            #pri.Info.yellow(w)
                            type(w).keyPressEvent(w,e)
                            if not e.key() in self.gui.blockedKeys:
                                self.gui.keyPressEvent(e)
                    return KeyPressFun
                w.keyPressEvent=createKeyPressFun(w)

    def setFontSizeText(self):
        fPixSize=self.fontPixelSize
        setFontPixelSize(self,fPixSize)
        setFontSizeText(self.ui.info,[fPixSize+6,fPixSize*2])
        setFontSizeText(self.ui.info_uni,[fPixSize+4])
        setFontSizeText(self.ui.ger_cv,[fPixSize+1])
        setFontSizeText(self.ui.tom_cv,[fPixSize+1])
        setFontSizeText(self.ui.list_ref,[fPixSize+1])

#********************************************* GCalVi
class CALpar(TABpar):
    def __init__(self):
        #attributes in fields
        self.setup()
        fields=[f for f,_ in self.__dict__.items()]

        #attributes out of fields
        super().__init__()
        self.fields=fields
        self.name='CALpar'
        self.surname='gCalVi'
        self.unchecked_fields+=[]

    def setup(self):
        self.FlagUndocked       = False
        self.prevTab      		= 0                
        self.lastTab    		= 0    
        self.FlagInput          = True
        self.FlagProcess        = True
        self.FlagVis            = True    

        self.Geometry           = 0
        self.SplitterSizes      = [[],[],[]]
        self.ScrollAreaValues   = []

        self.FloatingsGeom      = []
        self.FloatingsVis       = []
        self.FScrollAreaValues  = []
        
        self.FlagButtLabel      = True
        self.paletteType        = 2   #-1,2=standard, 0=light, 1=dark
        self.printTypes         = printTypes
        self.fontPixelSize      = fontPixelSize

        self.FlagOutDated = 0
        self.currentVersion = __version__
        self.latestVersion  = ''

class gCalVi(QMainWindow):

    def keyboardShortcut(self,sc):
        if sc=='Ctrl+W':
            return
        elif sc in ('Ctrl+0','Ctrl+Shift+0'):
            self.CALpar.fontPixelSize=fontPixelSize
            self.app.processEvents()
            self.setFontPixelSize()
        elif sc in  ('Ctrl+1','Ctrl+Minus'):
            if self.CALpar.fontPixelSize>fontPixelSize_lim[0]: 
                self.CALpar.fontPixelSize-=1
                self.app.processEvents()
                self.setFontPixelSize()
        elif sc in  ('Ctrl+Shift+1','Ctrl+Shift+Minus'):
            self.CALpar.fontPixelSize=fontPixelSize_lim[0]
            self.app.processEvents()
            self.setFontPixelSize()
        elif sc in  ('Ctrl+9','Ctrl+Plus'):
            if self.CALpar.fontPixelSize<fontPixelSize_lim[1]: 
                self.CALpar.fontPixelSize+=1
                self.app.processEvents()
                self.setFontPixelSize()
        elif sc in  ('Ctrl+Shift+9','Ctrl+Shift+Plus'):
            self.CALpar.fontPixelSize=fontPixelSize_lim[1]
            self.app.processEvents()
            self.setFontPixelSize()
    
    def paintEvent(self,event):
        #pri.General.yellow('***painting')
        super().paintEvent(event)
       
        if not self.FlagUndocking:
            self.setOpButtonLabel()

    def resizeEvent(self,event):
        if self.flagGeometryInit:
            self.flagGeometryInit=False
            return
        self.setFontPixelSize()
        super().resizeEvent(event)
        #self.updateCALparGeom()     

    def closeEvent(self,event):
        ''' This event handler is called with the given event when Qt receives a window close request for a top-level widget        '''
        if self.FlagRun and not self.FlagClosing[0]:
            flagYes=self.questionDialog('CalVi is currently running on a process. If you close the application now, processing will be stopped. Are you sure you want to quit?')
            if not flagYes: 
                event.ignore()
                return
        self.hide()
        for f in self.floatings+self.floatw+[self.aboutDialog]:
            if f: f.hide()
        print('\nClosing CalVi...')
        if self.FlagRun:
            self.button_Abort_callback()    
        self.correctClose()
    
    def correctClose(self):
        if self.cfgname!=lastcfgname_CalVi:
            self.saveas_uicfg(self.cfgname)
        self.save_lastcfg()
        PrintTA.flagPriority=PrintTAPriority.always
        self.closeAll()
        self.close()
        self.app.processEvents()
        self.app.SecondaryThreads=self.SecondaryThreads
        self.app.quit()

    def closeAll(self):
        if hasattr(self,"floatings"):
            for w in self.floatings:
                w.close()
        if hasattr(self,"floatw"):
            for w in self.floatw:
                w.close()
        self.w_Vis.close()   #***** ?????

    class gCalVi_signals(QObject):
        guiInit=Signal()
        killOrResetParForWorker=Signal(bool)#used to kill or reset he parForWorker
        setImg=Signal()
        run=Signal()
        printOutDated=Signal(bool)

    def __init__(self,flagDebug=False,app=None):
        self.app:QApplication=app
        self.name='CalVi'
        activateFlagDebug(flagDebug)
        self.PIVvers=PaIRS_lib.Version(PaIRS_lib.MOD_PIV).split('\n')[0]
        pri.Time.blue(2,f'gCalVi init PaIRS-PIV {self.PIVvers}')
        super().__init__()

        #------------------------------------- Launching Parallel Pool
        self.previousPlotTime=time() #previous time for plotting
        self.signals=self.gCalVi_signals()
        self.flagGeometryInit=True
        
        self.FlagGuiInit=False
        self.signals=self.gCalVi_signals()
        self.signals.guiInit.connect(self.show)
        #self.numUsedThreadsPIV=NUMTHREADS_PIV
        #self.FlagParPoolInit=False
        #self.launchParPool(NUMTHREADS_PIV_MAX)
        self.SecondaryThreads=[]
        
        #------------------------------------- Graphical interface: widgets
        ui=Ui_gCalVi()
        ui.setupUi(self)
        self.ui=ui

        self.defineTabs() 
        self.cfgname=lastcfgname_CalVi
        self.w_Vis.setRunButtonText=self.setRunButtonText
        
        self.FlagHappyLogo=False
        self.setupLogo()

        setupWid(self) #---------------- IMPORTANT
        self.setTabFontPixelSize(fontPixelSize)
        #for the keyboard shortcut
        self.FlagKeyCallbackExec=False
        self.blockedKeys=[Qt.Key.Key_Up,Qt.Key.Key_Down,Qt.Key.Key_Left,Qt.Key.Key_Right]
        for w in self.findChildren(QObject):
            if hasattr(w,'keyPressEvent'):
                def createKeyPressFun(w):
                    def KeyPressFun(e):
                        if w.hasFocus():
                            #pri.Info.yellow(w)
                            if not self.FlagKeyCallbackExec:
                                self.FlagKeyCallbackExec=True
                                type(w).keyPressEvent(w,e)
                            if not e.key() in self.blockedKeys:
                                self.keyPressEvent(e)
                            self.FlagKeyCallbackExec=False
                    return KeyPressFun
                w.keyPressEvent=createKeyPressFun(w)
        self.w_Vis.setLogFont(fontPixelSize-dfontLog)

        #for positioning and resizing
        window=QWindow()
        window.setTitle("title")
        window.showMaximized()
        self.MaxGeo=window.geometry()
        self.MaxFrameGeo=window.frameGeometry()
        window.close()
        
        self.secondary_splitter=ui.secondary_splitter
        self.Vis_maxWidth=self.w_Vis.maximumWidth()
        self.fVis_maxWidth=self.ui.f_VisTab.maximumWidth()
        self.minW=self.minimumWidth()
        self.maxW=self.maximumWidth()
        margins=self.ui.Clayout.contentsMargins()
        self.minW_ManTabs=self.minimumWidth()-margins.left()-margins.right()
        
        #------------------------------------- Graphical interface: miscellanea
        self.icon_dock_tabs = QIcon()
        self.icon_dock_tabs.addFile(u""+ icons_path +"dock_tabs.png", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_undock_tabs = QIcon()
        self.icon_undock_tabs.addFile(u""+ icons_path +"undock_tabs.png", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_play = QIcon()
        self.icon_play.addFile(u""+ icons_path +"play.png", QSize(), QIcon.Normal, QIcon.Off)  #"down_arrow.png"/"menu_vert.png"
        self.icon_pause = QIcon()
        self.icon_pause.addFile(u""+ icons_path +"pause.png", QSize(), QIcon.Normal, QIcon.Off)  #"right_arrow.png"/"menu_docked.png"

        self.animation = QVariantAnimation(self.ui.scrollArea)

        self.updating_import_gif = QMovie(u""+ icons_path +"updating_import.gif")
        self.updating_import_gif.setScaledSize(self.ui.label_updating_import.size())
        #self.ui.label_updating_import.setScaledContents(True)     
        self.updating_import_gif.start()
        self.ui.label_updating_import.setMovie(self.updating_import_gif)
        self.ui.label_updating_import.setVisible(False)

        self.updating_pairs_gif = QMovie(u""+ icons_path +"updating_pairs.gif")
        self.updating_pairs_gif.setScaledSize(self.ui.label_updating_pairs.size())
        #self.ui.label_updating_pairs.setScaledContents(True)     
        self.updating_pairs_gif.start()
        self.ui.label_updating_pairs.setMovie(self.updating_pairs_gif)
        self.ui.label_updating_pairs.setVisible(False)
        
        self.FlagUndocking=False
        self.FlagButtLabel=None
        self.palettes=[lightPalette(),darkPalette(),None]
        self.paletteNames=['Light','Dark','System']
        #self.ui.logo.contextMenuEvent=self.paletteContextMenuEvent
        self.ui.logo.mousePressEvent=self.paletteContextMenuEvent
        cursor_lamp_pixmap=QtGui.QPixmap(''+ icons_path +'cursor_lamp.png').scaled(QSize(24,24), Qt.KeepAspectRatio)
        cursor_lamp = QtGui.QCursor(cursor_lamp_pixmap,-1,-1)
        self.ui.logo.setCursor(cursor_lamp)

        self.aboutDialog=None
        self.logChanges=None

        self.fontPixelSize=fontPixelSize
        self.ui.button_PaIRS_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signals.printOutDated.connect(lambda flagOutDated: self.ui.button_PaIRS_download.setVisible(flagOutDated))

        #------------------------------------- Declaration of parameters 
        self.CALpar_base=CALpar()
        self.CALpar_old=CALpar()
        self.CALpar=CALpar()
        self.TABpar=self.CALpar

        self.FlagFirstShow=True
        self.FlagRun=False
        self.procWorkers=[]
        self.contProc=self.nProc=0
        self.FlagProcInit=False
        self.FlagProcPlot=False
        self.procFields=['numProcOrErrTot','Log','list_print','list_pim','numCallBackTotOk','numFinalized','flagRun','flagParForCompleted']

        self.floatings=[]
        self.defineFloatings()
        self.floatw=[]
        
        self.menuDebug=None

        #------------------------------------- Callbacks 
        self.setupCallbacks()
     
        self.w_Vis.FlagAddPrev=False

        gPaIRS_Tab.indTreeGlob=0
        gPaIRS_Tab.indItemGlob=0
        gPaIRS_Tab.FlagGlob=True
        
        self.w_Import.FlagDisplayControls=True
        self.w_Process.FlagDisplayControls=False
        self.w_Vis.FlagDisplayControls=False

        self.moveBFbuttons()

        #shortcuts
        scs=['Ctrl+W','Ctrl+0','Ctrl+Shift+0','Ctrl+1','Ctrl+Minus','Ctrl+Shift+1','Ctrl+Shift+Minus','Ctrl+9','Ctrl+Plus','Ctrl+Shift+9','Ctrl+Shift+Plus']
        self.keyboardQShortcuts=[]
        for sc in scs:
            kQSc=QShortcut(QKeySequence(sc), self)
            kQSc.activated.connect(lambda sc=sc: self.keyboardShortcut(sc))
            self.keyboardQShortcuts.append(kQSc)

        self.w_Import.signals.list_selection.connect(self.selectImgFromImport)
        self.w_Vis.updateGCalVi=self.setRunningState

        #------------------------------------- Initialization
        from .PaIRS_pypacks import basefold
        basefold=myStandardPath(basefold)
        from .PaIRS_pypacks import basefold
        basefold=myStandardPath(basefold)
        if os.path.exists(lastcfgname_CalVi) and not Flag_DEBUG_CleanLaunch:
            WarningMessage='Error with loading the last configuration file.\n'
            Flag,var=self.import_uicfg(lastcfgname_CalVi,WarningMessage) 
            if not Flag:
                os.remove(lastcfgname_CalVi)
                self.initialize()
            else:    
                try:
                    CALpar_prev=var[1]
                    self.CALpar.copyfrom(CALpar_prev)
                    self.setCALpar() 
                except Exception as inst:
                    warningDialog(self,WarningMessage,flagScreenCenter=True)
                    pri.Error.red(f'{WarningMessage}:\n{traceback.print_exc()}\n\n{inst}')
                    os.remove(lastcfgname_CalVi)
                    self.initialize()
        else:
            self.initialize()   
        self.CALpar_old.copyfrom(self.CALpar)    

        #------------------------------------- Debug
        self.addDebugMenu()
        self.menuDebug.setFont(self.ui.menuFile.font())
        self.menuDebug.menuAction().setVisible(Flag_DEBUG)
        self.userDebugShortcut = QShortcut(QKeySequence('Shift+Alt+D'), self)
        self.userDebugShortcut.activated.connect(self.userDebugMode)
        self.developerDebugShortcut = QShortcut(QKeySequence('Alt+D, Alt+E, Alt+B, Alt+Return'), self)
        self.developerDebugShortcut.activated.connect(lambda:self.setDebugMode(True))
        #self.exitDebugShortcut = QShortcut(QKeySequence('Shift+Alt+D'), self)
        #self.exitDebugShortcut.activated.connect(lambda:self.setDebugMode(False))
        self.setDebugMode(flagDebug)# should be put not upper than here
        self.w_Process.Flag_CYLINDERCAL_option=self.ui.aCyl

        pri.Time.blue(0,'dopo setupUi')
        self.FlagClosing=[False]
        self.w_Import.setPathCompleter()

        self.load_gif = QMovie(u""+ icons_path +"loading_2.gif")
        self.load_gif.start()
        self.loaded_map=QPixmap(u""+ icons_path + "loaded.png")
        self.w_Import.ui.button_back.hide()
        self.w_Import.ui.button_forward.hide()
        
        self.FlagGuiInit=True
        pri.Time.blue(0,'fine di tutto init')
        
    def initialize(self):
        pri.Info.yellow('||| Initializing gCalVi |||')
        #necessary to initialize sizes in both configurations
        self.CALpar.FlagUndocked=True
        self.DefaultSize() #undocked
        self.CALpar.FlagUndocked=False
        self.DefaultSize()  #docked
        self.w_Import.initialize()
        self.w_Process.initialize()
        self.w_Vis.calibView.hide()
        #self.w_Vis.initialize()
        self.setCALpar()             
    
    def moveBFbuttons(self):
        self.w_Import.ui.bfLayout.removeWidget(self.w_Import.ui.label_number)
        self.w_Import.ui.bfLayout.removeItem(self.w_Import.ui.hs_bf)
        self.w_Import.ui.bfLayout.removeWidget(self.w_Import.ui.button_back)
        self.w_Import.ui.bfLayout.removeWidget(self.w_Import.ui.button_forward)
        self.ui.bfLayout.addWidget(self.w_Import.ui.label_number)
        self.ui.bfLayout.addItem(self.w_Import.ui.hs_bf)
        self.ui.bfLayout.addWidget(self.w_Import.ui.button_back)
        self.ui.bfLayout.addWidget(self.w_Import.ui.button_forward)

    def defineFloatings(self):
        self.floatings=[]
        for i,wn in enumerate(self.opwidnames):
            wname="w_"+wn
            wid=getattr(self,wname)
            self.floatings.append(FloatingObject(self,wid))
        for f in self.floatings:
            self.CALpar.FloatingsGeom.append(f.geometry())
            self.CALpar.FloatingsVis.append(f.isVisible())
        geo=self.floatings[self.CALpar.prevTab].geometry()
        for k in range(3): self.CALpar.FloatingsGeom[k]=geo 
        self.CALpar.FloatingsGeom.append(self.geometry())
        self.CALpar.FloatingsVis.append(self.isVisible())

    def setupCallbacks(self):
        #------------------------------------- Main Window buttons
        for j,wn in enumerate(self.optabnames):
            setattr(self.CALpar,"Flag"+wn,True)
        """
        self.ui.button_Input.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Input'),'gCalVi') )
        self.ui.button_Output.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Output'),'gCalVi') )
        self.ui.button_Process.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Process'),'gCalVi') )
        self.ui.button_Log.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Log'),'gCalVi') )
        self.ui.button_Vis.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Vis'),'gCalVi') )
        self.ui.button_default_sizes.clicked.connect(self.w_Tree.addParWrapper(self.button_default_sizes_callback,'gCalVi'))
        self.ui.button_dock.clicked.connect(self.w_Tree.addParWrapper(self.button_dock_callback,'gCalVi'))
        self.ui.button_Shape.clicked.connect(self.w_Tree.addParWrapper(self.button_Shape_callback,'gCalVi'))
        """
        self.ui.button_Input.clicked.connect(lambda: self.button_Tab_callback('Input'))
        self.ui.button_Process.clicked.connect(lambda: self.button_Tab_callback('Process'))
        self.ui.button_Vis.clicked.connect(lambda: self.button_Tab_callback('Vis'))
        for k,wn in enumerate(self.opwidnames):
            def setClosedCallback(wn):
                w=getattr(self,'w_'+wn)
                w.ui.button_close_tab.clicked.connect(lambda: self.close_tab(w))
            setClosedCallback(wn)
        self.secondary_splitter.addfuncout['setScrollAreaWidth']=self.setScrollAreaWidth
        

        self.ui.button_default_sizes.clicked.connect(self.button_default_sizes_callback)
        self.ui.button_dock.clicked.connect(self.button_dock_callback)

        self.ui.button_Run.clicked.connect(self.w_Vis.addParWrapper(self.run,'gCalVi'))
        self.button_Abort_callback=self.w_Vis.addParWrapper(self.abort,'gCalVi')
        self.ui.button_Abort.clicked.connect(self.button_Abort_callback)
        self.ui.button_import.clicked.connect(self.importProc)

        #------------------------------------- Menu
        self.ui.actionPaIRS_Run.triggered.connect(lambda: runPaIRS(self,))
        self.ui.actionPaIRS_Clean_run.triggered.connect(lambda: runPaIRS(self,'-c'))
        self.ui.actionPaIRS_Debug_run.triggered.connect(lambda: runPaIRS(self,'-d'))
        self.ui.actionCalVi_Run.triggered.connect(lambda: runPaIRS(self,'-calvi'))
        self.ui.actionCalVi_Clean_run.triggered.connect(lambda: runPaIRS(self,'-calvi -c'))
        self.ui.actionCalVi_Debug_run.triggered.connect(lambda: runPaIRS(self,'-calvi -d'))
        #self.ui.actionCalVI.triggered.connect(self.runCalVi)
        self.ui.actionNew.triggered.connect(self.new_uicfg)
        self.ui.actionLoad.triggered.connect(self.load_uicfg)
        self.ui.actionSave.triggered.connect(self.save_uicfg)
        self.ui.actionSave_as.triggered.connect(self.saveas_uicfg)
        self.ui.actionClose.triggered.connect(self.close_uicfg)
        self.ui.aExit.triggered.connect(self.close)
        self.showChanges=lambda: changes(self,Log_Tab,fileChanges)
        self.ui.actionChanges.triggered.connect(self.showChanges)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionGuide.triggered.connect(self.guide)  
        self.ui.button_PaIRS_download.clicked.connect(lambda: button_download_PaIRS_callback(self,self.app))

        #------------------------------------- Animations
        self.animation.valueChanged.connect(self.moveToColumn)  

    def setFontPixelSize(self):
        if self.fontPixelSize==self.CALpar.fontPixelSize: return
        fPixSize=self.CALpar.fontPixelSize
        font=QFont()
        font.setFamily(fontName)
        font.setPixelSize(fPixSize)
        if self.app: self.app.setFont(font)
        setFontPixelSize(self,fPixSize)
        self.setTabFontPixelSize(fPixSize)
        for tn in self.optabnames:
            self.setOpButtonText(tn)
        if self.aboutDialog:
            self.aboutDialog.fontPixelSize=self.CALpar.fontPixelSize
            self.aboutDialog.setFontSizeText()
        if self.logChanges: self.logChanges.setFontPixelSize(fPixSize)
        if self.menuDebug: self.menuDebug.setFont(self.ui.menuFile.font())
        self.fontPixelSize=fPixSize
    
    def setTabFontPixelSize(self,fPixSize):
        fPixSize_TabNames=min([fPixSize*2,30])
        for tn,wn in zip(self.optabnames,self.opwidnames):
            w=getattr(self,'w_'+wn)
            setFontPixelSize(w,fPixSize)
            qlabels=self.findChildren(QLabel)
            labs=[l for l in qlabels if 'name_tab' in l.objectName()]
            for lab in labs:
                lab:QLabel #=self.ui.name_tab
                font=lab.font()
                font.setPixelSize(fPixSize_TabNames)
                lab.setFont(font)    
            button:RichTextPushButton=getattr(self.ui,f"button_{tn}")
            font=button.font()
            font.setPixelSize(fPixSize+1)
            button.setFont(font)
            button.lbl.setFont(font)
        for tn in ('Run','Abort'):
            button:RichTextPushButton=getattr(self.ui,f"button_{tn}")
            font=button.font()
            font.setPixelSize(fPixSize+1)
            button.setFont(font)
            button.lbl.setFont(font)
        self.w_Vis.setLogFont(fPixSize-dfontLog)


#********************************************* TAB definitions
    def defineTabs(self):
        self.optabnames=['Input','Process','Vis']
        self.opwidnames=['Import','Process','Vis'] #+'Tab'
        wclasses=[Import_Tab_CalVi,Process_Tab_CalVi,Vis_Tab_CalVi]
        
        for k,tname in enumerate(self.opwidnames):
            wname='w_'+tname
            setattr(self,wname,wclasses[k](self,False))
            w=getattr(self,wname)
            lay=getattr(self.ui,'f'+tname+'_lay')
            lay.addWidget(w)
            #w.show()
            

        self.w_Import:Import_Tab_CalVi   
        self.w_Process:Process_Tab_CalVi
        self.w_Vis:Vis_Tab_CalVi

        self.TABnames=['Import','Process','Vis']
        self.TABParDataNames=['INP','PRO','VIS']

        self.defineTABbridges()
        
    def defineTABbridges(self):
        for tname in self.TABnames:
            w: gPaIRS_Tab
            self.defineTAB_setParBridge(tname)
            self.defineTAB_addParBridge(tname)
            wname='w_'+tname
            w=getattr(self,wname)
            w.TABname=tname
            w.fUpdatingTabs=self.setRunningState

    def defineTAB_addParBridge(self,tname):
        w: gPaIRS_Tab
        wname='w_'+tname
        w=getattr(self,wname)
        fadd_par_copy=[]
        w2=[]
        for tname2 in self.TABnames:
            if tname2!=tname:
                wname2='w_'+tname2
                w2.append(getattr(self,wname2))
                fadd_par_copy.append(w2[-1].add_TABpar_copy)
        def add_par_bridge(tip,indTree,indItem,ind):
            w2j: gPaIRS_Tab
            #self.w_Tree.TABpar=dataTreePar()
            for f,w2j in zip(fadd_par_copy,w2):
                w2j.TABpar.freset_par=wname
                f(tip)
        w.add_TABpar_bridge=add_par_bridge

    def defineTAB_setParBridge(self,tname):
        w: gPaIRS_Tab
        wname='w_'+tname
        w=getattr(self,wname)
        fset_par=[]
        fset_par_prev=[]
        w2=[]
        for tname2 in self.TABnames:
            if tname2!=tname:
                wname2='w_'+tname2
                w2.append(getattr(self,wname2))
                fset_par.append(w2[-1].setTABpar)
                fset_par_prev.append(w2[-1].setTABpar_prev)
        def set_par_bridge():
            fw=self.focusWidget()
            self.actualBridge(tname,-1,-1,-1)
            for f in fset_par:
                f(False)  #setting parameters without bridge (False=without bridge)
            if fw: fw.setFocus()
        def set_par_bridge_prev(indTree,indItem,ind):
            fw=self.focusWidget()
            self.actualBridge(tname,indTree,indItem,ind)
            for f in fset_par_prev:
                f(indTree,indItem,ind,False) #setting previous parameters without bridge (False=without bridge)
            if fw: fw.setFocus()
        w.defineTABbridge(set_par_bridge,set_par_bridge_prev)

    def actualBridge(self,tname,indTree,indItem,ind):
        if ind>-1:
            pri.Callback.green(f'    --- gCalVi bridge_prev {[indTree]}{[indItem]}{[ind]}')
            INP:INPpar_CalVi=self.w_Import.TABpar_prev[indTree][indItem][ind]
            PRO:PROpar_CalVi=self.w_Process.TABpar_prev[indTree][indItem][ind]
            VIS:VISpar_CalVi=self.w_Vis.TABpar_prev[indTree][indItem][ind]
        else:
            INP=self.w_Import.TABpar
            PRO=self.w_Process.TABpar
            VIS=self.w_Vis.TABpar

        INP.FlagReadCalib=PRO.CalibProcType>=2
        if tname=='Import':
            self.initDataAndSetImgFromGui(INP,PRO)
            indTree,indItem,ind=self.w_Import.INPpar.indexes()
            if ind:
                flagResetLevels=self.w_Import.TABpar_prev[indTree][indItem][ind-1].isDifferentFrom(self.w_Import.TABpar,[],['path'],True) or len(self.w_Import.TABpar_prev[indTree][indItem][ind-1].filenames)==0
                flagResetZoom=self.w_Import.TABpar_prev[indTree][indItem][ind-1].isDifferentFrom(self.w_Import.TABpar,[],['x','y','w','h','W','H'],True) or len(self.w_Import.TABpar_prev[indTree][indItem][ind-1].filenames)==0
            else:
                flagResetLevels=flagResetZoom=True
            self.w_Vis.calib2VIS(flagResetLevels=flagResetLevels,flagResetZoom=flagResetZoom)
            pass
        if tname=='Process':
            self.w_Import.INPpar.FlagOptPlane=self.w_Process.PROpar.CalibProcType>0
            if len(self.w_Import.INPpar.plapar):
                if self.w_Import.INPpar.FlagOptPlane:
                    for k,p in enumerate(self.w_Import.INPpar.plapar):
                        if len(p)==1:
                            self.w_Import.INPpar.plapar[k]=[float(0)]*5+[p[0]]
                else:
                    for k,p in enumerate(self.w_Import.INPpar.plapar):
                        if len(p)>1:
                            self.w_Import.INPpar.plapar[k]=[p[-1]]
            self.initDataAndSetImgFromGui(INP,PRO)
            indTree,indItem,ind=self.w_Process.PROpar.indexes()
            self.w_Vis.calib2VIS(flagResetLevels=False,flagResetZoom=False)
            pass
        if tname=='Vis':
            INP.row=VIS.plane
            pass
        return
    
    def initDataAndSetImgFromGui(self,INP,PRO):
        self.w_Vis.initDataFromGui(INP,PRO)
        inddel=self.w_Vis.setImgFromGui()
        if len(inddel): #todo GP: migliorare? (setto due volte le immagini e faccio in calib il check)
            Message=f'The following image files have sizes not compatible with the first image file of the list ({self.w_Import.INPpar.filenames[0]}):\n'
            for k in inddel:
                if k==inddel[-1]: colon='.'
                else: colon=';'
                Message+=f'- {self.w_Import.INPpar.filenames[k]}{colon}\n'
            Message+='They will not be added to the list.'
            self.warningDialog(Message)
            for i in range(len(inddel)-1,-1,-1):
                k=inddel[i]
                self.w_Import.INPpar.filenames.pop(k)
                self.w_Import.INPpar.plapar.pop(k)
            self.w_Import.adjust_list_images()
            self.w_Import.setINPpar()
            self.w_Vis.initDataFromGui(INP,PRO)
            inddel=self.w_Vis.setImgFromGui()
    
    @Slot()
    def selectImgFromImport(self):
        r=self.w_Import.ui.list_images.currentRow()
        self.w_Vis.VISpar.plane=r
        self.w_Vis.setTABpar(False)

    def setRunningState(self):
        flag=self.w_Vis.calibView.flagCurrentTask!=CalibTasks.stop
        self.ui.label_updating_pairs.setVisible(flag)
        pass

#*************************************************** Run

    def run(self):
        self.FlagRun=self.w_Vis.VISpar.FlagRun=not self.w_Vis.VISpar.FlagRun

        self.setFlagRun()
        if self.w_Vis.VISpar.FlagRun:
            #indTree,indItem,ind=self.w_Import.INPpar.indexes()
            #self.actualBridge('Import',indTree,indItem,ind)
            self.initDataAndSetImgFromGui(self.w_Import.INPpar,self.w_Process.PROpar)
            if self.w_Import.INPpar.errorMessage:
                warningDialog(self,self.w_Import.INPpar.errorMessage)
                self.abort()
                return
            if self.w_Vis.VISpar.errorMessage:
                warningDialog(self,self.w_Vis.VISpar.errorMessage)
                self.abort()
                return
            self.button_Tab_callback('Vis')
            pri.Info.cyan(f'Running calibration   FlagRestart={self.w_Vis.FlagResume}')
            if self.w_Vis.FlagResume>-1:
                self.w_Vis.FlagSettingNewCalib=not bool(self.w_Vis.FlagResume)
                #self.w_Vis.VISpar_old.FlagRun=bool(self.w_Vis.FlagResume) #riesuma lo zoom ma non la posizione
                self.w_Vis.runCalVi(flagMod=bool(self.w_Vis.FlagResume))
            else:
                flagYes=self.questionDialog('A calibration result file already exists in the current output path. Do you want to overwrite it?')
                if flagYes: 
                    self.w_Vis.FlagResume=0
                    self.w_Vis.runCalVi(flagMod=False)
                else: 
                    self.run()
        else:
            if self.w_Vis.FlagResume>-1: 
                self.saveCal()
                if (self.w_Import.INPpar.FlagOptPlane or self.w_Process.PROpar.CamMod==4) and self.w_Vis.calibView.calib.FlagCalibration:
                    if self.w_Import.INPpar.FlagOptPlane: self.savePlanePar()
                    self.updateIPpar()
                    self.saveCal('_Mod')
            #indTree,indItem,ind=self.w_Import.INPpar.indexes()
            #self.actualBridge('Import',indTree,indItem,ind)
            self.initDataAndSetImgFromGui(self.w_Import.INPpar,self.w_Process.PROpar)
            self.w_Vis.stopCalVi()

    def abort(self):
        self.w_Vis.FlagResume=-1
        self.run()
            
    def updateIPpar(self):
        if self.w_Import.INPpar.FlagOptPlane:
            costPlanes=self.w_Vis.calibView.calib.cal.vect.costPlanes
            for i in range(len(self.w_Import.INPpar.filenames)):
                self.w_Import.INPpar.plapar[i]=[round(p,3) for p in costPlanes[i]]
        if self.w_Process.PROpar.CamMod==4:
            cost=self.w_Vis.calibView.calib.cal.vect.cost[0]
            self.w_Process.PROpar.CylRad=cost[21]
            self.w_Process.PROpar.CylThick=cost[22]
            self.w_Process.PROpar.CylNRatio=cost[23]
        VIS=self.w_Vis.VISpar
        self.w_Vis.TABpar_prev[VIS.indTree][VIS.indItem][VIS.ind].copyfrom(VIS)
        self.w_Import.add_TABpar('Completed process')
        self.w_Import.setTABpar(True)   #setting parameters with bridge
        
    def saveCal(self,add_str=''):
        VIS=self.w_Vis.VISpar
        data=self.w_Vis.calibView.calib.cal.data
        calVect=self.w_Vis.calibView.calib.cal.vect
        VIS.orPosAndShift=[]
        VIS.angAndMask=[]
        VIS.spotDistAndRemoval=[]
        for c in range(data.NCam):
            for p1 in range(data.Numpiani_PerCam):
                p=p1+c*data.Numpiani_PerCam
                VIS.orPosAndShift.append([])
                VIS.angAndMask.append([])
                VIS.spotDistAndRemoval.append([])

                VIS.orPosAndShift[p].append(calVect.XOr[p] - data.ColPart)
                VIS.orPosAndShift[p].append(calVect.YOr[p] - data.RigaPart)
                VIS.orPosAndShift[p].append(calVect.xOrShift[p])
                VIS.orPosAndShift[p].append(calVect.yOrShift[p])
                
                VIS.angAndMask[p].append(calVect.angCol[p])
                VIS.angAndMask[p].append(calVect.angRow[p])
                for i in self.w_Vis.calibView.calib.cal.getPuTrovaCC(p):
                    VIS.angAndMask[p].append(i)

                VIS.spotDistAndRemoval[p].append(calVect.dColPix[p])
                VIS.spotDistAndRemoval[p].append(calVect.dRigPix[p])
                VIS.spotDistAndRemoval[p].append(calVect.remPointsUp[p])
                VIS.spotDistAndRemoval[p].append(calVect.remPointsDo[p])
                VIS.spotDistAndRemoval[p].append(calVect.remPointsLe[p])
                VIS.spotDistAndRemoval[p].append(calVect.remPointsRi[p])
        
        INP=self.w_Import.INPpar
        if len(INP.cams)==1: camString=f'_cam{INP.cams[0]}'
        else: camString=''
        varName=f'{data.percorsoOut}{data.NomeFileOut}{camString}{add_str}{outExt.cal}'
        var=[INP,self.w_Process.PROpar,VIS,myStandardPath(os.path.dirname(varName))]
        with open(varName,'wb') as file:
            pickle.dump(var,file)
            pri.Info.blue(f'>>> Saving calibration process file {varName}')            
        return
    
    def savePlanePar(self):
        data=self.w_Vis.calibView.calib.cal.data
        calVect=self.w_Vis.calibView.calib.cal.vect
        INP=self.w_Import.INPpar
        if len(INP.cams)==1: camString=f'_cam{INP.cams[0]}'
        else: camString=''
        plaparRad=f'{data.percorsoOut}{data.NomeFileOut}{camString}_plane'
        plapar_names=['beta  (°)','alpha (°)','gamma (°)','x (mm)','y (mm)','z (mm)']
        for i,c in enumerate(calVect.costPlanes):
            dp={}
            for p,v in zip(plapar_names,c):
                dp[p]=v
            plaparName=plaparRad+f"{i+1:d}_z{dp['z (mm)']:.2f}{outExt.pla}"
            with open(plaparName,'w') as file:
                file.write(str(dp).replace('{','{\n ').replace(',',',\n').replace('}','\n}'))
            pri.Info.blue(f'    Saving plane data file {plaparName}')

    def importProc(self):
        varName, _ = QFileDialog.getOpenFileName(self,\
            "Select a CalVi result file", filter=f'*{outExt.cal}',\
                dir=self.w_Import.INPpar.path,\
                options=optionNativeDialog)
        if not varName: return
        try:
            if os.path.exists(varName):
                with open(varName, 'rb') as file:
                    var=pickle.load(file)
        except:
            WarningMessage=f'Error with loading the file: {varName}\n'
            self.warningDialog(WarningMessage)
        else:
            FlagErr=False
            if len(var)>=3:
                if type(var[0])==type(self.w_Import.INPpar) and type(var[1])==type(self.w_Process.PROpar):
                    INP:INPpar_CalVi=var[0]
                    if len(var)>3:
                        self.adjust_INPpath(INP,'path',varName,var[3])
                        self.adjust_INPpath(INP,'pathout',varName,var[3])
                    self.w_Import.INPpar.copyfrom(INP,TABpar().fields)
                    self.w_Import.adjust_list_images()
                    self.w_Process.PROpar.copyfrom(var[1],TABpar().fields)
                    VIS=self.w_Vis.VISpar
                    self.w_Vis.TABpar_prev[VIS.indTree][VIS.indItem][VIS.ind].copyfrom(VIS)
                    self.w_Import.add_TABpar('Imported process')
                    self.w_Import.setTABpar(True)   #setting parameters with bridge
                else: FlagErr=True
            else: FlagErr=True
            if FlagErr:
                WarningMessage=f'Error with setting the process file: {varName}\n'
                self.warningDialog(WarningMessage)

    def adjust_INPpath(self,INP,pathField,varName,path_old):
        if not os.path.exists(getattr(INP,pathField)):
            path_new=myStandardPath(os.path.dirname(varName))
            inpPath=myStandardPath(os.path.abspath(path_new+os.path.relpath(INP.path,path_old)))
            if os.path.exists(inpPath):
                setattr(INP,pathField,inpPath)

#*************************************************** Warnings
    def warningDialog(self,Message,time_milliseconds=0,flagScreenCenter=False):
        warningDialog(self,Message,time_milliseconds,flagScreenCenter)

    def questionDialog(self,Message):
        flagYes=questionDialog(self,Message)
        return flagYes

#*************************************************** Menus
    def setGCalViTitle(self):
        if self.cfgname==lastcfgname_CalVi:
            cfgString=''
            self.ui.actionClose.setEnabled(False)
        else:
            cfgString=f': {self.cfgname}'
            self.ui.actionClose.setEnabled(True)
        if Flag_DEBUG:#TA per non incasinarmi
            windowTitle=f'CalVi (v{version}.{__subversion__}) -- cfg v{uicfg_version} -- PIV {self.PIVvers} -- {platform.system()}'
        else:
            windowTitle=f'CalVi (v{version})'
        windowTitle+=cfgString
        self.setWindowTitle(windowTitle)        

#********************* File
    def pauseQuestion(self,taskDescription='continuing',task=None):
        FlagPause=self.FlagRun
        if self.FlagRun:
            if self.questionDialog(f'CalVi is currently running on a process. Do you want to abort it before {taskDescription}?'): 
                self.button_Abort_callback()
                task()
        return FlagPause
    
    def new_uicfg(self):
        if self.pauseQuestion('creating a new project',lambda: self.new_uicfg()): return
        if self.cfgname!=lastcfgname_CalVi:
            FlagYes=True
            self.saveas_uicfg(self.cfgname)
        else:
            Question="The current project is unsaved. Would you like to save it before starting a new one?"
            FlagYes=questionDialog(self,Question)
        if FlagYes:
            self.save_uicfg()
        self.reconfigure()
        self.saveas_uicfg('',"Select location and name of the new project")

    def close_uicfg(self):
        if self.pauseQuestion('closing the current project',lambda: self.close_uicfg()): return
        self.save_uicfg()
        self.reconfigure()
        
    def reconfigure(self):
        self.cfgname=lastcfgname_CalVi
        self.setGCalViTitle()
        pathCompleter=self.w_Import.INPpar.pathCompleter
        for tname in self.TABnames:
            w:gPaIRS_Tab=getattr(self,"w_"+tname)        
            w.TABpar.copyfrom(w.ParClass())
            w.TABpar_prev=[[[w.ParClass()]],[],[]] 
            w.FlagAddingPar=[[[False]],[],[]]    
            w.FlagAsyncCall=[[[False]],[],[]]   
        from .PaIRS_pypacks import basefold
        self.w_Import.INPpar.pathCompleter=pathCompleter
        self.w_Import.FlagAddPrev=False        
        self.w_Import.set_currpath(basefold)
        self.w_Import.edit_path_callback() #setTABpar_prev(0,0,0,True) #with bridge
        self.w_Import.FlagAddPrev=True

    def getCurrentCfgVar(self):
        self.updateCALparGeom()
        info=['uicfg-gCalVi',uicfg_version,__version__, __subversion__, __year__]
        geom = self.CALpar.duplicate()
        WIDnames=[]
        prevs=[]
        FlagAddingPar=[]
        FlagAsyncCall=[]
        for tname in self.TABnames:
            w: gPaIRS_Tab
            wname='w_'+tname
            w=getattr(self,wname)
            WIDnames.append(wname)
            prevs.append(w.TABpar_prev)
            FlagAddingPar.append(w.FlagAddingPar)
            FlagAsyncCall.append(w.FlagAsyncCall)
        var=[info]+[geom]+[None]+[WIDnames]+[prevs]+[FlagAddingPar]+[FlagAsyncCall]
        return var

    def setCfgVar(self,var):
        #var=info+geom+tree_var+WIDnames+prevs
        #self.ui.centralwidget.hide()
        info=var[0]  #['uicfg-gCalVi',uicfg_version,__version__, __subversion__, __year__]
        if info[0]!='uicfg-gCalVi':
            WarningMessage='The file is not a valid CalVi configuration file!'
            return False, WarningMessage
        else:
            ver=[int(i) for i in info[1].split('.')]
            cfgver=[int(i) for i in uicfg_version.split('.')]
            if not all([ver[k]>=cfgver[k] for k in range(len(ver))]):
                WarningMessage=f'The file is out-of-date (v{ver}) and not compatible with the current version (v{cfgver})!'
                return False, WarningMessage
        geom=var[1]
        WIDnames=var[3]
        prevs=var[4]
        FlagAddingPar=var[5]
        FlagAsyncCall=var[6]
        for k,wname in enumerate(WIDnames):
            w:gPaIRS_Tab=getattr(self,wname)
            w.TABpar_prev=prevs[k]
            iterateList(FlagAddingPar[k],False)
            w.FlagAddingPar=FlagAddingPar[k]
            iterateList(FlagAsyncCall[k],False)
            w.FlagAsyncCall=FlagAsyncCall[k]
            w.TABpar.copyfrom(prevs[k][0][0][-1])
            w.TABpar.indTree=0
            w.TABpar.indItem=0
            w.TABpar.ind=len(prevs[k][0][0])-1
        VISpar_curr=self.w_Vis.VISpar.duplicate()
        VISpar_curr.FlagRun=False   
        self.w_Import.setTABpar(True)
        self.w_Vis.VISpar_old.copyfrom(VISpar_curr)
        self.w_Vis.TABpar_prev[0][0][0].copyfrom(VISpar_curr)
        self.w_Vis.TABpar.copyfrom(VISpar_curr)
        self.w_Vis.setTABpar(True)
        return True,''

    def save_uicfg(self,filename='',Title="Select location and name of the project file to save"):
        if self.cfgname==lastcfgname_CalVi:
            self.saveas_uicfg(filename,Title)
        else:
            self.saveas_uicfg(self.cfgname,Title)

    def saveas_uicfg(self,filename='',Title="Select location and name of the project file to save"):
        if self.pauseQuestion('saving the current project',lambda: self.saveas_uicfg(filename,Title)): return
        if filename=='':
            filename, _ = QFileDialog.getSaveFileName(self,Title, 
                    dir=self.w_Import.INPpar.path+"uicfg", filter=f'*{outExt.cfg_calvi}',\
                    options=optionNativeDialog)
            if filename[-4:]=='.cfg': filename=filename[:-4]  #per adattarlo al mac
            filename=myStandardRoot('{}'.format(str(filename)))
            if not filename: return
        if not outExt.cfg_calvi in filename:
            filename=filename+outExt.cfg_calvi
        if filename:
            var=self.getCurrentCfgVar()
            filename=myStandardRoot(filename)
            try:
                with open(filename, 'wb') as file:
                    pickle.dump(var, file)
                    pri.Info.white(f'>>>>> Saving ui configuration file:\t{filename}')
                    self.cfgname=filename
                    self.setGCalViTitle()
            except Exception as inst:
                warningDialog(self,f'Error while saving the configuration file {filename}!\nPlease, retry.')
        return
    
    def save_lastcfg(self,*args):
        if len(args): var=args[0]
        else: var=self.getCurrentCfgVar()
        prevs=var[4]
        FlagAddingPar=var[5]
        FlagAsyncCall=var[6]
        last_prevs=[]
        last_FlagAddingPar=[]
        last_FlagAsyncCall=[]
        for k in range(len(prevs)):
            last_prevs.append([])
            last_FlagAddingPar.append([])
            last_FlagAsyncCall.append([])
            for indTree in range(len(prevs[k])):
                last_prevs[k].append([])
                last_FlagAddingPar[k].append([])
                last_FlagAsyncCall[k].append([])
                for indItem in range(len(prevs[k][indTree])):
                    p=prevs[k][indTree][indItem][-1].duplicate()
                    p.ind=0
                    fadd=FlagAddingPar[k][indTree][indItem][-1]
                    fasy=FlagAsyncCall[k][indTree][indItem][-1]
                    last_prevs[k][indTree].append([p])
                    last_FlagAddingPar[k][indTree].append([fadd])
                    last_FlagAsyncCall[k][indTree].append([fasy])
        var2=var[:4]+[last_prevs,last_FlagAddingPar,last_FlagAsyncCall]
        with open(lastcfgname_CalVi, 'wb') as file:
            pickle.dump(var2, file)
            pri.Info.white(f'    >>>>> Saving last ui configuration to file:\t{lastcfgname_CalVi}')
        return

    def load_uicfg(self):
        if self.pauseQuestion('opening an old project',lambda: self.load_uicfg()): return
        filename, _ = QFileDialog.getOpenFileName(self,\
            "Select a CalVi configuration file", filter=f'*{outExt.cfg_calvi}',\
                dir=self.w_Import.INPpar.path,\
                options=optionNativeDialog)
        if not filename: return
        WarningMessage=f'Error with loading the file: {filename}\n'
        self.import_uicfg(filename,WarningMessage)

    def import_uicfg(self,filename,WarningMessage):
        var=[]
        try:
            with open(filename, 'rb') as file:
                var = pickle.load(file)
            Flag,WarningMessage2=self.setCfgVar(var)
            if Flag:
                self.cfgname=filename
                self.setGCalViTitle()
            else:
                warningDialog(self,WarningMessage+WarningMessage2)
        except Exception as inst:
            warningDialog(self,WarningMessage)
            pri.Error.red(f'{WarningMessage}:\n{traceback.print_exc()}\n\n{inst}')
            Flag=False 
        return Flag,var

#********************* Help
    def guide(self):
        url = QUrl("https://www.pairs.unina.it/web/CalVi-Guide.pdf")
        QDesktopServices.openUrl(url)

    def about(self):
        if self.aboutDialog:
            self.aboutDialog.hide()
            self.aboutDialog.show()
        else:
            self.aboutDialog=infoCalVi(self)
            self.aboutDialog.show()

#********************* Debug
    def addDebugMenu(self):
        global Flag_fullDEBUG, pri
        menubar=self.ui.menubar
        self.menuDebug=menubar.addMenu("Debug")

        #--------------------------- new ui cfg
        self.menuDebug.addSeparator()
        self.ui.aNew = self.menuDebug.addAction("New")
        self.ui.aNew.triggered.connect(self.reconfigure)

        #--------------------------- last ui cfg
        self.menuDebug.addSeparator()
        self.ui.aSaveLastCfg = self.menuDebug.addAction("Save lastuicfg"+outExt.cfg_calvi)
        self.ui.aSaveLastCfg.triggered.connect(self.save_lastcfg)

        self.ui.aDeleteLastCfg = self.menuDebug.addAction("Delete lastuicfg"+outExt.cfg_calvi)
        def delete_lastcfg():
            if os.path.exists(lastcfgname_CalVi):
                os.remove(lastcfgname_CalVi)
            pri.Info.white(f'    xxxxx Deleting last ui configuration file:\t{lastcfgname_CalVi}')
        self.delete_lastcfg=delete_lastcfg
        self.ui.aDeleteLastCfg.triggered.connect(delete_lastcfg)

        #--------------------------- printings
        self.menuDebug.addSeparator()
        self.ui.printMenu=self.menuDebug.addMenu('Print')
        printTypes_list=list(self.CALpar.printTypes)
        printActions=[]
        def setPrint(name,act,k):
            flag=act.isChecked()
            self.CALpar.printTypes[name]=flag
            flagTime=getattr(getattr(pri,name),'flagTime')
            faceStd=getattr(getattr(pri,name),'faceStd')
            if flag:
                setattr(pri,name,ColorPrint(flagTime=flagTime,prio=PrintTAPriority.medium,faceStd=faceStd))
            else:
                setattr(pri,name,ColorPrint(flagTime=flagTime,prio=PrintTAPriority.never,faceStd=faceStd))
            #print(f'{name}  {flag}')
            #pri.Callback.white(f'pri.Callback.white(): setPrint')
            return
        def genCallback(name,act,k):
            n=name
            a=act
            j=k
            return lambda: setPrint(n,a,j)
        for k,name in enumerate(printTypes_list):
            flagFullDebug=getattr(getattr(pri,name),'flagFullDebug')
            if flagFullDebug and not Flag_fullDEBUG: continue
            act=self.ui.printMenu.addAction(name)
            printActions.append(act)
            act.setCheckable(True)
            flag=self.CALpar.printTypes[name]
            act.setChecked(flag)
            setPrint(name,act,k)
            act.triggered.connect(genCallback(name,act,k))

        #--------------------------- operation
        self.menuDebug.addSeparator()
        self.ui.aCyl = self.menuDebug.addAction("Activate cylinder cal.")
        if Flag_fullDEBUG: 
            self.w_Process.Flag_CYLINDERCAL=True
        self.ui.aCyl.setCheckable(True)
        self.ui.aCyl.setChecked(self.w_Process.Flag_CYLINDERCAL)
        def aCyl():
            #from PaIRS_pypacks import Flag_CYLINDERCAL
            self.w_Process.Flag_CYLINDERCAL=self.ui.aCyl.isChecked()
            self.w_Process.setPROpar()
        self.ui.aCyl.triggered.connect(aCyl)
        aCyl()

        
        if Flag_fullDEBUG:
            self.menuDebug.addSeparator()
            self.ui.aShowDownload = self.menuDebug.addAction("Show/hide download button")
            def aShowDownload():
                self.ui.button_PaIRS_download.setVisible(not self.ui.button_PaIRS_download.isVisible())
            self.ui.aShowDownload.triggered.connect(aShowDownload)

            self.ui.aResetFlagOutDated = self.menuDebug.addAction("Reset FlagOutDated")
            def aResetFlagOutDated():
                self.GPApar.FlagOutDated=0 if self.GPApar.currentVersion==self.GPApar.latestVersion else 1
                packageName='PaIRS-UniNa'
                currentVersion=self.GPApar.currentVersion
                latestVersion=self.GPApar.latestVersion
                if self.GPApar.FlagOutDated==1:
                    sOut=f'{packageName} the current version ({currentVersion}) of {packageName} is obsolete! Please, install the latest version: {latestVersion} by using:\npython -m pip install --upgrade {packageName}'
                else:
                    sOut=f'{packageName} The current version ({currentVersion}) of {packageName} is up-to-date! Enjoy it!'
                pri.Info.yellow(f'[{self.GPApar.FlagOutDated}] '+sOut) 
            self.ui.aResetFlagOutDated.triggered.connect(aResetFlagOutDated)

            self.ui.aCheckOutDated = self.menuDebug.addAction("Check for new packages")
            def aCheckOutDated():
                self.GPApar.FlagOutDated=0
                self.ui.button_PaIRS_download.hide()
                checkLatestVersion(self,__version__,self.app,splash=None)
            self.ui.aCheckOutDated.triggered.connect(aCheckOutDated)

            self.menuDebug.addSeparator()
            self.ui.aResetWhatsNew = self.menuDebug.addAction("Reset whatsnew.txt")
            def aResetWhatsNew():
                if os.path.exists(fileWhatsNew[1]):
                    try:
                        os.rename(fileWhatsNew[1],fileWhatsNew[0])
                    except Exception as inst:
                        pri.Error.red(f'There was a problem while renaming the file {fileWhatsNew[1]}:\n{inst}')
            self.ui.aResetWhatsNew.triggered.connect(aResetWhatsNew)

            self.ui.aShowWhatsNew = self.menuDebug.addAction("Show What's new window")
            def aShowWhatsNew():
                whatsNew(self)
            self.ui.aShowWhatsNew.triggered.connect(aShowWhatsNew)

            self.menuDebug.addSeparator()
            self.ui.aFocusWid = self.menuDebug.addAction("Print widget with focus")
            def aFocusWid():
                pri.General.yellow(f"The widget with focus is:   {self.focusWidget()}")
            self.aCheckConnections=aFocusWid
            self.ui.aFocusWid.triggered.connect(aFocusWid)

            self.ui.aPrintListImages = self.menuDebug.addAction("Print list of image pairs")
            def aPrintListImages():
                
                for i,f in enumerate(self.w_Import.INPpar.filenames):
                    pri.General.white(f"{f}:")
                    for fc in self.w_Import.INPpar.list_Image_Files[i]:
                        pri.General.white(f"   {fc}")
            self.aPrintListImages=aPrintListImages
            self.ui.aPrintListImages.triggered.connect(aPrintListImages)

        #--------------------------- Save PIV cfg
        self.menuDebug.addSeparator()
        self.ui.aSaveCfgCalVi=self.menuDebug.addAction("Save CalVi cfg")
        def aSaveCfgCalVi():
            return
        self.aSaveCfgCalVi=aSaveCfgCalVi
        self.ui.aSaveCfgCalVi.triggered.connect(aSaveCfgCalVi)
        
        #--------------------------- graphics
        if Flag_fullDEBUG:
            self.menuDebug.addSeparator()

            self.ui.aUndock = self.menuDebug.addAction("Undock a widget")
            self.ui.aUndock.triggered.connect(self.extractWidget)

            self.ui.aLogo = self.menuDebug.addAction("Change CalVi logo")
            self.ui.aLogo.triggered.connect(self.happyLogo)

            self.ui.aGifs = self.menuDebug.addAction("Show/hide gifs")
            def showGifs():
                flag=not self.ui.label_updating_import.isVisible()
                self.ui.label_updating_import.setVisible(flag)
                self.ui.label_updating_pairs.setVisible(flag)
            self.ui.aGifs.triggered.connect(showGifs)

        #--------------------------- exit
        self.menuDebug.addSeparator()

        self.ui.aExitDebug = self.menuDebug.addAction("Exit debug mode")
        self.ui.aExitDebug.triggered.connect(lambda:self.setDebugMode(False))

    def extractWidget(self):
        title="Undock a widget"
        label="Enter the widget name:"
        words = ["self.w_Import",
        "self.w_Process", 
        "self.w_Process.ui.CollapBox_Target",
        "self.w_Process.ui.CollapBox_Calibration",
        "self.w_Vis",
        "self.ui.w_Buttons_Run",
        ]
        
        ok,text=inputDialog(self,title,label,completer_list=words,width=500)
        if ok:
            try:                    
                ts=text.split('.')
                parent=".".join(ts[:-1])
                child=ts[-1]
                tab=getattr(eval(parent),child)
                self.floatw.append(FloatingWidget(self,tab))
                pass
            except:
                pass
    
    def userDebugMode(self):
        if not Flag_DEBUG:
            self.inputDebugMode()
        else:
            self.setDebugMode(False)

    def inputDebugMode(self):
        _,text=inputDialog(self,'Debug','Insert password for debug mode:',width=300,flagScreenCenter=not self.isVisible())
        if text==pwddbg:
            self.setDebugMode(True)
        else:
            warningDialog(self,'Password for debug mode is wrong!\nPaIRS will stay in normal mode.',time_milliseconds=5000)
            self.setDebugMode(False)
    
    def setDebugMode(self,Flag):
        global Flag_DEBUG
        Flag_DEBUG=Flag
        activateFlagDebug(Flag_DEBUG)
        self.setGCalViTitle()
        self.menuDebug.menuAction().setVisible(Flag)

#*************************************************** Graphical interface appearence
    def setCALpar(self):
        self.undockTabs()
        self.setTabLayout()
        self.ui.button_PaIRS_download.setVisible(self.CALpar.currentVersion!=self.CALpar.latestVersion and bool(self.CALpar.latestVersion))
        self.setRunButtonText()
        self.setGCalViTitle()
        self.setFontPixelSize()
        self.app.processEvents()
        self.setFlagRun()

    def setFlagRun(self):
        self.setRunButtonText()
        self.ui.button_Abort.setVisible(self.w_Vis.VISpar.FlagRun)
        self.ui.button_Run.setShortcut(QCoreApplication.translate("gCalVi", u"Ctrl+Return", None))
        self.ui.button_import.setEnabled(not self.w_Vis.VISpar.FlagRun)
        self.w_Import.FlagDisplayControls=not self.w_Vis.VISpar.FlagRun
        self.w_Import.ui.button_back.setVisible(not self.w_Vis.VISpar.FlagRun)
        self.w_Import.ui.button_forward.setVisible(not self.w_Vis.VISpar.FlagRun)
        self.w_Import.ui.scrollArea.setEnabled(not self.w_Vis.VISpar.FlagRun)
        self.w_Import.ui.w_OutputFold_Button.setEnabled(not self.w_Vis.VISpar.FlagRun)
        self.w_Process.ui.scrollArea.setEnabled(not self.w_Vis.VISpar.FlagRun)
        #self.ui.centralwidget.show()

    def setTabLayout(self,*args):
        if len(args): itab=args[0]
        else: itab=range(5)    
        #self.update()        
        self.setButtonLayout()
        self.adjustGeometry(itab)
        if not self.CALpar.FlagUndocked and self.FlagGuiInit:
            self.updateCALparGeom()
       
    def setButtonLayout(self):
        widname=self.optabnames[self.CALpar.lastTab]
        for k,tn in enumerate(self.optabnames):
            flag=getattr(self.CALpar,f"Flag{tn}")
            setattr(self.CALpar,f"Flag{tn}",flag)

            button:RichTextPushButton=getattr(self.ui,f"button_{tn}")
            wid:gPaIRS_Tab=getattr(self,'w_'+self.opwidnames[k])
            button.setChecked(flag)
            self.CALpar.FloatingsVis[k]=flag

            if self.CALpar.FlagUndocked:
                wid.ui.w_button_close_tab.hide()
            else:
                wid.ui.w_button_close_tab.show()

            self.setOpButtonText(tn)

        if self.CALpar.FlagUndocked:
            self.ui.button_dock.setIcon(self.icon_dock_tabs)
            tipDock="Dock tabs"+' ('+self.ui.button_dock.shortcut().toString(QKeySequence.NativeText)+')'
        else:
            self.ui.button_dock.setIcon(self.icon_undock_tabs)
            tipDock="Undock tabs"+' ('+self.ui.button_dock.shortcut().toString(QKeySequence.NativeText)+')'
        self.ui.button_dock.setToolTip(tipDock)
        self.ui.button_dock.setStatusTip(tipDock)

    def setOpButtonLabel(self,*args):
        if len(args):
            self.CALpar.FlagButtLabel=args[0]
        else:
            if self.CALpar.FlagUndocked:
                self.CALpar.FlagButtLabel=self.ui.w_Buttons_Run.width()>w_button_min_size
            else:
                if all([not getattr(self.CALpar,'Flag'+tn) for tn in self.optabnames]):
                    s=self.ui.w_Buttons_Run.width() #s=max([self.main_splitter.sizes()[0],self.minW_ManTabs])
                    self.CALpar.FlagButtLabel=s>w_button_min_size
                else:
                    self.CALpar.FlagButtLabel=self.ui.w_Buttons_Run.width()>w_button_min_size
        if self.CALpar.FlagButtLabel==self.FlagButtLabel: return
        self.FlagButtLabel=self.CALpar.FlagButtLabel
        for tn in self.optabnames:
            self.setOpButtonText(tn)
        self.setRunButtonText()
        self.setAbortButtonText()
        return
    
    def setOpButtonText(self,tabname):
        button:RichTextPushButton=getattr(self.ui,f"button_{tabname}")
        flag=getattr(self.CALpar,f"Flag{tabname}")
        if flag:
            s=''
        else:
            fPixSize=button.font().pixelSize()
            s=f'<sup><span style=" font-size:{fPixSize-2}px"> 🔒</span></sup>'
        if self.CALpar.FlagButtLabel:
            button.setText(tabname+s)
        else:
            button.setText(s)
    
    def setRunButtonText(self):
        button=self.ui.button_Run
        if not self.w_Vis.VISpar.FlagRun:
            flag=bool(self.w_Vis.VISpar.errorMessage) or bool(self.w_Import.INPpar.errorMessage) 
            if flag:
                fPixSize=button.font().pixelSize()
                s=f'<sup><span style=" font-size:{fPixSize-2}px"> ⚠</span></sup>'
            else:
                s=''
            text='Run'
            button.setIcon(self.icon_play)
        else:
            s=''
            text='Stop'
            button.setIcon(self.icon_pause)
        if self.CALpar.FlagButtLabel:
            button.setText(text+s)
        else:
            button.setText(s)
    
    def setAbortButtonText(self):
        button=self.ui.button_Abort
        if self.CALpar.FlagButtLabel:
            button.setText('Abort')
        else:
            button.setText('')

    def adjustGeometry(self,*args):
        if len(args): itab=args[0]
        else: itab=range(5)
        pri.Geometry.yellow(f'{"<>"*5} Adjusting geometry {"<>"*5}')
        if self.CALpar.FlagUndocked: 
            for k,f in enumerate(self.floatings):
                if self.CALpar.FloatingsGeom[k]:
                    f.setGeometry(self.CALpar.FloatingsGeom[k])
                if self.CALpar.FloatingsVis[k] and self.FlagGuiInit: 
                    f.show()
                    f.pa.show()
                else: 
                    f.hide()
                setattr(self.CALpar,'Flag'+self.optabnames[k],self.CALpar.FloatingsVis[k])
            """
            for k in itab:
                f=self.floatings[k]
                if self.CALpar.FloatingsVis[k]: 
                    f.setWindowFlags(f.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                    f.show()
                    f.setWindowFlags(f.windowFlags()  & ~ QtCore.Qt.WindowStaysOnTopHint)
                    f.show()
                else: f.hide()
            """
            self.setMaximumHeight(self.ui.w_Buttons_Run.maximumHeight())
            self.setGeometry(self.CALpar.FloatingsGeom[-1])
            self.CALpar.FloatingsVis[-1]=True
            for k,wn in enumerate(self.opwidnames[:-1]):
                w=getattr(self,'w_'+wn)
                w.ui.scrollArea.verticalScrollBar().setValue(self.CALpar.FScrollAreaValues[k])
            pri.Geometry.yellow(f'*** Undocked configuration:\n    Floatings Geometry={self.CALpar.FloatingsGeom}\n    Floatings Vis={self.CALpar.FloatingsVis}')
        else:
            cont=0
            for k,wn in enumerate(self.optabnames):
                tabname="f_"+self.opwidnames[k]+"Tab"
                tab=getattr(self.ui,tabname)
                flag=getattr(self.CALpar,'Flag'+wn)
                tab.setVisible(flag)
                cont+=flag                
            Flag=cont>0
            self.hideOpTabs(not Flag)
            if not Flag:
                self.ui.w_Operating_Tabs.hide()
                self.setMaximumHeight(self.ui.w_Buttons_Run.maximumHeight())
            else:
                self.ui.w_Operating_Tabs.show()
                self.setMaximumHeight(int(2**16))
            self.setGeometry(self.CALpar.Geometry) 
            if Flag: 
                #self.main_splitter.setSizes(self.CALpar.SplitterSizes[0])
                splitterSizes=self.CALpar.SplitterSizes[1]
                self.setSecondarySplitterSizes(splitterSizes)
                self.ui.scrollArea.horizontalScrollBar().setValue(self.CALpar.ScrollAreaValues[0])
                for k,wn in enumerate(self.opwidnames[:-1]):
                    w=getattr(self,'w_'+wn)
                    w.ui.scrollArea.verticalScrollBar().setValue(self.CALpar.ScrollAreaValues[k+1])
            pri.Geometry.yellow(f'*** Docked configuration:\n    Geom={self.CALpar.Geometry}\n    Main Spiltter Sizes={self.CALpar.SplitterSizes[0]}\n    Secondary Spiltter Sizes={self.CALpar.SplitterSizes[1]}')
        if self.FlagGuiInit: 
            self.show()
            if self.FlagFirstShow:
                self.FlagFirstShow=False
                #self.w_Vis.button_restore_callback()                
                #self.w_Vis.resetScaleFactor()
                self.w_Vis.resetScaleFactor()
                self.w_Vis.plotPlane()
                self.w_Vis.calibView.show()
        else:
            if Flag_ResetScaleOnChanges: pass#self.w_Vis.ui.plot.resetScaleFactor()

    def setSecondarySplitterSizes(self,splitterSizes):
        self.OpWidth=self.OpMaxWidth=0
        for k,tname in enumerate(self.opwidnames):
            flagname="Flag"+self.optabnames[k]
            flag=getattr(self.CALpar,flagname)
            tabname=f"f_"+tname+"Tab"
            tab=getattr(self.ui,tabname)
            if flag:
                if not splitterSizes[k]:
                    splitterSizes[k]=self.CALpar.SplitterSizes[2][k]
                else:
                    splitterSizes[k]=max([splitterSizes[k],tab.minimumWidth()])
                self.OpWidth+=splitterSizes[k]+self.secondary_splitter.handleWidth()
                self.OpMaxWidth+=tab.maximumWidth()+self.secondary_splitter.handleWidth()
            else:
                splitterSizes[k]=0
        if self.OpWidth==self.OpMaxWidth: 
            w_f_empty=0
        else: 
            w_f_empty=min([f_empty_width, self.OpMaxWidth-self.OpWidth])
            widthOpTab=self.ui.w_Operating_Tabs.width()
            dw=widthOpTab-self.OpWidth
            if dw>0: w_f_empty=dw
        self.ui.scrollAreaWidgetContents.setMinimumWidth(self.OpWidth+w_f_empty)
        self.ui.secondary_splitter.setMinimumWidth(self.OpWidth+w_f_empty)
        self.ui.scrollAreaWidgetContents.resize(self.OpWidth+w_f_empty,self.ui.scrollAreaWidgetContents.height())
        self.ui.secondary_splitter.resize(self.OpWidth+w_f_empty,self.ui.secondary_splitter.height())
        splitterSizes[-1]=w_f_empty
        self.ui.secondary_splitter.setSizes(splitterSizes)  
    
    def setScrollAreaWidth(self):
        self.updateCALparGeom()
        self.setTabLayout()    
        self.setFontPixelSize()
        
    def close_tab(self,w:gPaIRS_Tab):
        w.parent().hide()
        setattr(self.CALpar,'Flag'+w.name_tab,False)
        self.updateCALparGeom()
        if self.CALpar.FlagUndocked:
            self.setButtonLayout()
        else:
            self.setTabLayout()

    def updateCALparGeom(self): 
        pri.Geometry.green(f"{'-'*10} Updating geometry {'-'*10}")
        if self.CALpar.FlagUndocked:
            for i,f in enumerate(self.floatings):
                self.CALpar.FloatingsGeom[i]=f.geometry()
                self.CALpar.FloatingsVis[i]=f.isVisible()
            #geo=self.floatings[self.CALpar.prevTab].geometry()
            #for k in range(3): self.CALpar.FloatingsGeom[k]=geo 
            self.CALpar.FloatingsGeom[i+1]=self.geometry()
            self.CALpar.FloatingsVis[i+1]=self.isVisible()
            for k,wn in enumerate(self.opwidnames):
                if wn!='Vis':
                    w=getattr(self,'w_'+wn)
                    self.CALpar.FScrollAreaValues[k]=w.ui.scrollArea.verticalScrollBar().value()
            pri.Geometry.green(f'*** Undocked configuration:\n    Floatings Geometry={self.CALpar.FloatingsGeom}\n    Floatings Vis={self.CALpar.FloatingsVis}')
        else:
            self.CALpar.Geometry=self.geometry()   
            self.CALpar.SplitterSizes[0]=None
            self.CALpar.SplitterSizes[1]=splitterSizes=self.secondary_splitter.sizes()
            self.CALpar.ScrollAreaValues[0]=self.ui.scrollArea.horizontalScrollBar().value()
            for k,wn in enumerate(self.opwidnames):
                if splitterSizes[k]:
                    self.CALpar.SplitterSizes[2][k]=splitterSizes[k]
            for k,wn in enumerate(self.opwidnames):
                if wn!='Vis':
                    w=getattr(self,'w_'+wn)
                    self.CALpar.ScrollAreaValues[k+1]=w.ui.scrollArea.verticalScrollBar().value()
            pri.Geometry.green(f'*** Docked configuration:\n    Geom={self.CALpar.Geometry}\n    Main Spiltter Sizes={self.CALpar.SplitterSizes[0]}\n    Secondary Spiltter Sizes={self.CALpar.SplitterSizes[1]}')

    def button_Tab_callback(self,name):
        b:QPushButton=getattr(self.ui,"button_"+name)
        flagname="Flag"+name
        FlagVisible=getattr(self.CALpar,flagname)
        if b.isCheckable():
            setattr(self.CALpar,flagname,b.isChecked())
        else:
            setattr(self.CALpar,flagname,True)
        itab=self.optabnames.index(name)
        self.CALpar.prevTab=self.CALpar.lastTab
        if itab<3: self.CALpar.lastTab=itab  
        self.updateCALparGeom()
        self.setTabLayout([itab])
        if not self.CALpar.FlagUndocked:
            if getattr(self.CALpar,flagname):
                #self.update()
                wTab=self.ui.w_Operating_Tabs.width() #self.CALpar.SplitterSizes[0][2]-self.secondary_splitter.handleWidth()
                if self.CALpar.SplitterSizes[1][itab]>wTab:
                    self.CALpar.SplitterSizes[1][itab]=wTab
                    self.adjustGeometry()
        self.moveToTab(name)
        tab=getattr(self,'w_'+self.opwidnames[itab])
        w=self.focusWidget()
        if w: w.clearFocus()
        if name !='Vis':
            tab:Import_Tab_CalVi
            tab.ui.scrollArea.setFocus()
              
    def moveToTab(self,name,finished=lambda: None):
        i=self.optabnames.index(name)
        if not self.CALpar.FlagUndocked:
            hbar = self.ui.scrollArea.horizontalScrollBar()
            s=self.secondary_splitter.sizes()
            
            f=sum([sk>0 for sk in s[:i]])
            Xin=sum(s[:i])+(f)*self.secondary_splitter.handleWidth()
            v=min([Xin,hbar.maximum()]) 
            self.startAnimation(v,finished)
        else:
            f=self.floatings[i]
            f.setWindowFlags(f.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            f.show()
            f.setWindowFlags(f.windowFlags()  & ~ QtCore.Qt.WindowStaysOnTopHint)
            f.show()

    #@Slot()
    def startAnimation(self,v,finished=lambda: None):
        self.animation.stop()
        self.animation.setStartValue(self.ui.scrollArea.horizontalScrollBar().value())
        self.animation.setEndValue(v)
        self.animation.setDuration(time_ScrollBar) 
        self.animation.finished.connect(finished)
        self.animation.start()

    #@Slot(QVariant)
    def moveToColumn(self, i):
        self.ui.scrollArea.horizontalScrollBar().setValue(i)

    def button_Tab_action(self,name):
        flagname="Flag"+name
        flag=getattr(self.CALpar,flagname)
        tabname="f_"+self.opwidnames[self.optabnames.index(name)]+"Tab"
        tab=getattr(self.ui,tabname)
        if flag:
            tab.show()
            self.OpWidth+=tab.geometry().width()+self.secondary_splitter.handleWidth()
            self.OpMaxWidth+=tab.maximumWidth()+self.secondary_splitter.handleWidth()
        else:
            tab.hide()
        
    def button_dock_callback(self):
        self.FlagUndocking=True
        self.updateCALparGeom()
        #self.hide()
        self.CALpar.FlagUndocked= not self.CALpar.FlagUndocked
        self.undockTabs()
        if Flag_RESIZEONRUN:
            if self.FlagRun: 
                self.BSizeCallbacks[4]()
            else: 
                self.setTabLayout()
                if self.CALpar.FlagLog: self.moveToTab('Log')
                elif self.CALpar.FlagVis: self.moveToTab('Vis')
        else: 
            self.setTabLayout()
        #self.show()
        self.FlagUndocking=False

    def undockTabs(self):
        if self.CALpar.FlagUndocked:
            for i,wn in enumerate(self.opwidnames):
                self.floatings[i].setFloat()
                if wn=='Vis':
                    self.floatings[i].setMaximumWidth(self.maxW)
                    self.ui.f_VisTab.setMaximumWidth(self.maxW)
                    self.w_Vis.setMaximumWidth(self.maxW)
        else:
            for i,wn in enumerate(self.opwidnames):
                tabname="f_"+wn+"Tab"
                tab=getattr(self.ui,tabname)
                self.secondary_splitter.addWidget(tab)    
                self.secondary_splitter.setCollapsible(i,False)
            self.secondary_splitter.addWidget(self.ui.f_empty)
            self.secondary_splitter.setCollapsible(i+1,False)
            for i in range(len(self.floatings)):
                self.floatings[i].close()
            #self.floatings=[]
            self.ui.f_VisTab.setMaximumWidth(self.fVis_maxWidth)
            self.w_Vis.setMaximumWidth(self.Vis_maxWidth)
        self.hideOpTabs(self.CALpar.FlagUndocked)
        
    def hideOpTabs(self,flagUndocked):
        dpix=20
        if flagUndocked:
            #self.ui.manlay.insertWidget(1,self.ui.w_Buttons)
            #self.ui.main_sep.hide()
            self.ui.w_Operating_Tabs.hide()
            self.centralWidget().setMaximumWidth(self.ui.w_Buttons_Run.maximumWidth())
            self.centralWidget().setMinimumWidth(self.ui.w_Buttons_Run.minimumWidth()+dpix)
            self.setMaximumWidth(self.ui.w_Buttons_Run.maximumWidth())
            self.setMinimumWidth(self.ui.w_Buttons_Run.minimumWidth()+dpix)
        else:
            self.ui.w_Operating_Tabs.show()
            self.centralWidget().setMaximumWidth(self.maxW)
            self.centralWidget().setMinimumWidth(self.minW)
            self.setMaximumWidth(self.maxW)
            self.setMinimumWidth(self.minW)
        size=self.size()
        newSize=QSize(min([size.width(),self.maxW]),size.height())
        self.resize(newSize)

        """
        if flagUndocked:
            self.CALpar.FlagButtLabel=self.CALpar.FloatingsGeom[-1].width()>w_button_min_size
        else:
            if all([not getattr(self.CALpar,'Flag'+tn) for tn in self.optabnames]):
                margins=self.ui.Clayout.contentsMargins()
                s=max([self.CALpar.SplitterSizes[0][0],self.minimumWidth()-margins.left()-margins.right()])
                self.CALpar.FlagButtLabel=s>w_button_min_size
            else:
                self.CALpar.FlagButtLabel=self.CALpar.SplitterSizes[0][-1]>w_button_min_size
        self.setOpButtonLabel(self.CALpar.FlagButtLabel)
        """

    def button_default_sizes_callback(self):
        self.DefaultSize()
        self.setTabLayout()
        return
    
    def DefaultSize(self):
        geo=self.MaxGeo
        x0=geo.x()
        y0=geo.y()
        w=geo.width()
        h=geo.height()
        
        pri.Geometry.blue(f'{"°"*10} Setting sizes {"°"*10}')
        if not self.CALpar.FlagUndocked:

            handleWidth2=self.secondary_splitter.handleWidth()   
            dpix=[100,75]
            Geometry=QRect(int(dpix[0])+x0,int(dpix[1])+y0,int(w-2*dpix[0]),int(h-2*dpix[1]))
            wp=Geometry.width()
            #hp=Geometry.height()
            nw=3
            wt=int(wp/nw)
            SecondarySplitterSizes=[wt+handleWidth2]*2+[1000]+[f_empty_width]
            self.CALpar.Geometry=Geometry
            self.CALpar.SplitterSizes[0]=None
            self.CALpar.SplitterSizes[1]=copy.deepcopy(SecondarySplitterSizes)
            self.CALpar.SplitterSizes[2]=copy.deepcopy(SecondarySplitterSizes)
            self.CALpar.ScrollAreaValues=[0]*3

            self.CALpar.FlagInput=self.CALpar.FlagProcess=self.CALpar.FlagVis=True
            pri.Geometry.blue(f'--> Docked configuration:\n    Geom={self.CALpar.Geometry}\n    Main Spiltter Sizes={self.CALpar.SplitterSizes[0]}\n    Secondary Spiltter Sizes={self.CALpar.SplitterSizes[1]}')
        else:
            dx=self.MaxFrameGeo.width()-w
            dy=self.MaxFrameGeo.height()-h
            m=self.ui.Clayout.contentsMargins() 
            wMain=self.ui.w_Buttons_Run.minimumWidth()+m.left()+m.right()
            hMain=self.ui.w_Buttons_Run.minimumHeight()+m.top()+m.bottom()+int(self.FlagHappyLogo)*(self.ui.lab_happy_days.height()+self.ui.Clayout.spacing())
            hSBM=self.ui.statusbar.minimumHeight()+self.ui.menubar.minimumHeight()
            wpf=wMain
            wIOP=self.w_Import.minimumWidth()
            if wpf>wIOP: wIOP=wpf
            wVis=w-wIOP-dx
            hIO=self.w_Import.minimumWidth()
            if int(h*0.5>hIO): hIO=int(h*0.5)
            hP=h-hMain-hSBM-hIO-2*dy
            FGeometry_main=QRect(x0,y0,wIOP,hMain)
            FGeometry_IO=QRect(x0,y0+hMain+hSBM+dy,wIOP,hIO)
            FGeometry_Pro=QRect(x0,y0+hMain+hSBM+hIO+2*dy,wIOP,hP)
            FGeometry_Vis=QRect(x0+wIOP+dx,y0,wVis,h)
            self.CALpar.FloatingsGeom=[FGeometry_IO]+[FGeometry_Pro]+[FGeometry_Vis]+[FGeometry_main]
            self.CALpar.FloatingsVis=[True]*4
            self.CALpar.FScrollAreaValues=[0]*4  #***** ?????
            pri.Geometry.blue(f'--> Undocked configuration:\n    Floatings Geometry={self.CALpar.FloatingsGeom}\n    Floatings Vis={self.CALpar.FloatingsVis}')

#*************************************************** Greetings
    def setupLogo(self):
        today = datetime.date.today()
        d=today.strftime("%d/%m/%Y")
        happy_days=[
            #[d, 'Happy birthday to CalVi! 🎈🎂🍾'], #to test
            ['20/12/1991', 'Happy birthday to Gerardo! 🎈🎂🍾'],
            ['05/02/1969', 'Happy birthday to Tommaso! 🎈🎂🍾'],
            ['11/07/1987', 'Happy birthday to Carlo! 🎈🎂🍾'],
            ['19/09/1963', 'Happy birthday to Gennaro! 🎈🎂🍾'],
            ['18/10/1985', 'Happy birthday to Stefano! 🎈🎂🍾'],
            ['13/08/1985', 'Happy birthday to Andrea! 🎈🎂🍾'],
            ['22/12/1988', 'Happy birthday to Gioacchino! 🎈🎂🍾'],
            ['03/09/1991', 'Happy birthday to Giusy! 🎈🎂🍾'],
            ['03/11/1989', 'Happy birthday to Massimo! 🎈🎂🍾'],
            ['15/06/1991', 'Happy birthday to Mattia! 🎈🎂🍾'],
            ['14/07/1993', 'Happy birthday to Mirko! 🎈🎂🍾'],
            ['01/01', 'Happy New Year! 🎊🧨'],
            ['25/12', 'Merry Christmas! 🎄✨'],
            ['31/10', 'Happy Halloween! 🎃👻'],
            ['22/06', 'Hello, Summer! 🌞🌊'],
        ]

        i=-1
        for j,l in enumerate(happy_days):
            if l[0][:6]==d[:6]:
                i=j
                break

        if i>-1:
            self.FlagHappyLogo=True
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_CalVi_party.png"))
            self.ui.lab_happy_days.setText(happy_days[i][1])
        else:
            self.FlagHappyLogo=False
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_CalVi.png"))
            self.ui.lab_happy_days.setText('')

    def happyLogo(self):
        self.FlagHappyLogo=not self.FlagHappyLogo
        if self.FlagHappyLogo:
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_CalVi_party.png"))
            self.ui.lab_happy_days.setText('Greetings! Today is a great day! 🎈🎉')
        else:
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_CalVi.png"))
            self.ui.lab_happy_days.setText('')

#*************************************************** Palette
    def setGPaIRSPalette(self):
        setAppGuiPalette(self,self.palettes[self.CALpar.paletteType])

    def paletteContextMenuEvent(self, event):   
        contextMenu = QMenu(self)
        act=[]
        for n in self.paletteNames:
            act.append(contextMenu.addAction(f"{n} mode"))
        act[self.CALpar.paletteType].setCheckable(True)
        act[self.CALpar.paletteType].setChecked(True)
        userAct = contextMenu.exec(event.globalPosition().toPoint())
        for k,a in enumerate(act):
            if a==userAct:
                self.CALpar.paletteType=k
                self.setGPaIRSPalette()

def launchCalVi(flagDebug=False,flagInputDebug=False):
    print('\n'+CalVi_Header+'Starting the interface...')
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font=QFont()
    font.setFamily(fontName)
    font.setPixelSize(fontPixelSize)
    app.setFont(font)
    app.pyicon=app.windowIcon()
    icon=QIcon()
    icon.addFile(''+ icons_path +'icon_CalVi.png',QSize(), QIcon.Normal, QIcon.Off)
    app.setWindowIcon(icon)
    try:
        if (platform.system() == "Windows"):
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('CalVi')
    except:
        pri.General.red('It was not possible to set the application icon')

    if not flagDebug or Flag_SHOWSPLASH:
        splash=showSplash(filename=''+ icons_path +'logo_CalVi_completo.png')
        app.processEvents()
    else:
        splash=None   
    
    standardPalette=app.style().standardPalette()
    global Flag_fullDEBUG
    Flag_fullDEBUG=flagDebug
    for n in printTypes:
        p:ColorPrint=getattr(pri,n)
        if p.flagFullDebug and not Flag_fullDEBUG:
            p.prio=PrintTAPriority.never
            p.setPrints()
        
    if flagInputDebug:
        _,text=inputDialog(None,'Debug','Insert password for debug mode:',icon=icon,palette=standardPalette,width=300)
        flagDebug=text==pwddbg
        if not flagDebug:
            warningDialog(None,'Password for debug mode is wrong!\nPaIRS will be started in normal mode.',icon=icon,time_milliseconds=5000)
    gui=gCalVi(flagDebug,app)
    gui.palettes[2]=standardPalette
    gui.setGPaIRSPalette()

    currentVersion=__version__ #if __subversion__=='0' else  __version__+'.'+__subversion__
    flagStopAndDownload=checkLatestVersion(gui,currentVersion,app,splash)
    if flagStopAndDownload:
        gui.correctClose()
        runPaIRS(gui,command='-calvi',flagQuestion=False)
        return [app,gui,False]

    gui.splash=splash
    #warningDlg.setModal(True)
    if splash:
        splash.setWindowFlags(splash.windowFlags()|Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
        
    if splash:
        gui.ui.logo.hide()
    gui.adjustGeometry()
    gui.setFontPixelSize()
    if splash: 
        splashAnimation(splash,gui.ui.logo)
        #QTimer.singleShot(time_showSplashOnTop,splash.hide)
    print('\nWelcome to CalVi!\nEnjoy it!')
    if os.path.exists(fileWhatsNew[0]): whatsNew(gui)
    app.exec()
    return [app,gui,True]

def splashAnimation(self:QLabel,logo:QLabel):
    margin=23
    ml=logo.width()/self.width()*margin
    wl=logo.width()+2*ml
    hl=wl/self.width()*self.height()
    
    self.anim = QPropertyAnimation(self, b"pos")
    pos=logo.mapToGlobal(logo.geometry().topLeft())
    pos.setX(pos.x()-ml)
    self.anim.setEndValue(pos)
    self.anim.setDuration(time_showSplashOnTop)
    self.anim_2 = QPropertyAnimation(self, b"size")
    
    self.anim_2.setEndValue(QSize(wl, hl))
    self.anim_2.setDuration(time_showSplashOnTop)
    self.anim_group = QParallelAnimationGroup()
    self.anim_group.addAnimation(self.anim)
    self.anim_group.addAnimation(self.anim_2)
    self.anim_group.finished.connect(self.hide)
    self.anim_group.finished.connect(logo.show)
    self.anim_group.start()
    
def quitCalVi(app:QApplication,flagPrint=True):
    app.setWindowIcon(app.pyicon)
    app.quit()
    if flagPrint: print('\nCalVi closed.\nSee you soon!')
    if hasattr(app,'SecondaryThreads'):
        if len(app.SecondaryThreads):
            while any([s.isRunning for s in app.SecondaryThreads]):
                timesleep(.1)
                pass
    app=None
    return

def setAppGuiPalette(self:gCalVi,palette:QPalette):
    if self.app: self.app.setPalette(palette)
    if self.focusWidget():
        self.focusWidget().clearFocus()
    for f in  set([self]+self.floatings+self.floatw+self.findChildren(QDialog)+[self.aboutDialog]+[self.logChanges]):
        if f:
            f.setPalette(palette)
            for c in f.findChildren(QObject):
                if hasattr(c,'setPalette') and not type(c) in (MplCanvas, mplFigure, QStatusBar):
                    c.setPalette(palette)
                if hasattr(c,'initialStyle'):
                    c.setStyleSheet(c.initialStyle)
            for c in f.findChildren(QObject):
                c:MyQLineEdit
                if hasattr(c,'setup'):
                    c.initFlag=False
                    c.styleFlag=False
                    c.setup()
            for c in f.findChildren(QObject):
                if hasattr(c,'setup2'):
                    c.initFlag2=False
                    c.setup2()


if __name__ == "__main__":
    gui:gCalVi
    app,gui,flagPrint=launchCalVi(True)
    quitCalVi(app,flagPrint)
