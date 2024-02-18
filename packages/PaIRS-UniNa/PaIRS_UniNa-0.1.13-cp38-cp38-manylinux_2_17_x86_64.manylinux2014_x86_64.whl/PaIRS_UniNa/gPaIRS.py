from .ui_gPairs import *
from .ui_infoPaIRS import *
from .parForWorkers import *
from .TabTools import *
from .procTools import *

from .Tree_Tab import *
from .Import_Tab import *
from .Export_Tab import *
from .Process_Tab import *
from .Log_Tab import *
from .Vis_Tab import *
from .ResizePopup import*
from .Whatsnew import*

from .gPalette import darkPalette,lightPalette

import concurrent.futures

from .__init__ import __version__,__subversion__,__year__,__mail__,__website__

version=__version__
year=__year__
mail=__mail__
website=__website__
uicfg_version='0.1.6'
uicfg_version_to_load=uicfg_version
#uicfg_version_to_load='0.1.5'
w_button_min_size=680
Flag_fullDEBUG=True

#********************************************* Tree items
class treeToSave:
    class treeItems:
        def __init__(self,indTree):
            self.indTree=indTree
            self.names=[]
            self.idata=[]
            pass
    def __init__(self,TREpar):
        self.tree_names=['current','future','past']
        self.indTree=[0,1,-1]

        for k,n in zip(self.indTree,self.tree_names):
            setattr(self,n,self.treeItems(k))
            t=getattr(self,n)
            for i in getattr(TREpar,n):
                t.names.append(i.text(0))
                t.idata.append(i.data(0,Qt.UserRole).duplicate())

#********************************************* Additional windows
class FloatingObject(QMainWindow):
    def closeEvent(self, event):
        if not self.gui.GPApar.FlagUndocked:
            self.hide()
        else:
            self.gui.close_tab(self.tab)
            #self.button.setChecked(False)
            #setattr(self.gui.GPApar,'Flag'+self.name,False)
            #ind=self.gui.opwidnames.index(self.name)
            #if ind<3:
            #    self.gui.GPApar.prevTab=self.gui.GPApar.lastTab
            #    self.gui.GPApar.lastTab=ind
            #self.hide()   
        
    def __init__(self,parent,tab):
        super().__init__()
        self.gui:gPaIRS=parent
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
        elif type(tab) in (Import_Tab,Export_Tab,Process_Tab,Log_Tab,Vis_Tab,Tree_Tab):
            if type(tab)==Tree_Tab: self.name=''
            else: self.name=tab.ui.name_tab.text().replace(' ','')
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
            
class infoPaIRS(QMainWindow):
    def __init__(self,gui):
        super().__init__()
        ui=Ui_InfoPaiRS()
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

        self.fontPixelSize=gui.GPApar.fontPixelSize
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

#********************************************* GPaIRS
class GPApar(TABpar):
    def __init__(self):
        #attributes in fields
        self.setup()
        fields=[f for f,_ in self.__dict__.items()]

        #attributes out of fields
        super().__init__()
        self.fields=fields
        self.name='GPApar'
        self.surname='gPaIRS'
        self.unchecked_fields+=[]

    def setup(self):
        self.FlagUndocked       = False
        self.FlagAllTabs 		= True   
        self.prevTab      		= 0                
        self.lastTab    		= 0    
        self.FlagInput          = True
        self.FlagOutput         = True
        self.FlagProcess        = True
        self.FlagLog            = True
        self.FlagVis            = True    
        self.ProcessMode        = 0
        self.NumCores           = 0

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
        
class gPaIRS(QMainWindow):
      
    def keyboardShortcut(self,sc):
        if sc=='Ctrl+W':
            self.raise_()
            self.activateWindow()
            w=self.focusWidget()
            if w: w.clearFocus()
            tree,_=self.w_Tree.pickTree(self.w_Tree.TREpar.indTree)
            tree.setFocus()
            return
        elif sc in ('Ctrl+0','Ctrl+Shift+0'):
            self.GPApar.fontPixelSize=fontPixelSize
            self.app.processEvents()
            self.setFontPixelSize()
        elif sc in  ('Ctrl+1','Ctrl+Minus'):
            if self.GPApar.fontPixelSize>fontPixelSize_lim[0]: 
                self.GPApar.fontPixelSize-=1
                self.app.processEvents()
                self.setFontPixelSize()
        elif sc in  ('Ctrl+Shift+1','Ctrl+Shift+Minus'):
            self.GPApar.fontPixelSize=fontPixelSize_lim[0]
            self.app.processEvents()
            self.setFontPixelSize()
        elif sc in  ('Ctrl+9','Ctrl+Plus'):
            if self.GPApar.fontPixelSize<fontPixelSize_lim[1]: 
                self.GPApar.fontPixelSize+=1
                self.app.processEvents()
                self.setFontPixelSize()
        elif sc in  ('Ctrl+Shift+9','Ctrl+Shift+Plus'):
            self.GPApar.fontPixelSize=fontPixelSize_lim[1]
            self.app.processEvents()
            self.setFontPixelSize()
        elif sc in 'Shift+Backspace':
            if self.w_Tree.ui.tree_past.hasFocus():
                self.w_Tree.ui.button_delete_past_callback()
            elif self.w_Tree.ui.tree_future.hasFocus():
                self.w_Tree.ui.button_delete_future_callback()

    def paintEvent(self,event):
        #print(self.ui.w_Buttons.width())
        #pri.General.yellow('***painting')
        super().paintEvent(event)
        """
        if hasattr(self,'ResizePopup'):
            #self.ResizePopup.hide()
            if self.ResizePopup.isVisible():
                bRButt=self.ui.button_default_sizes.mapToGlobal(self.ui.button_default_sizes.geometry().bottomRight())
                geom = self.ResizePopup.frameGeometry()
                geom.moveBottomLeft(bRButt) #QtGui.QCursor.pos())
                self.ResizePopup.setGeometry(geom)
        """
        if not self.FlagUndocking:
            self.setOpButtonLabel()

    def resizeEvent(self,event):
        if self.flagGeometryInit:
            self.flagGeometryInit=False
            return
        self.setFontPixelSize()
        super().resizeEvent(event)
        #self.updateGPAparGeom()     

    def closeEvent(self,event):
        ''' This event handler is called with the given event when Qt receives a window close request for a top-level widget        '''
        if self.FlagRun and not self.FlagClosing[0]:
            flagYes=self.questionDialog('PaIRS is currently executing the processes in the Future queue. If you close the application now, processing will be stopped. Are you sure you want to quit?')
            if not flagYes: 
                event.ignore()
                return
        self.hide()
        for f in self.floatings+self.floatw+[self.aboutDialog]:
            if f: f.hide()
        if not self.FlagClosing[0]:
            self.FlagClosing[0]=True
            print('\nClosing PaIRS...')
            PrintTA.flagPriority=PrintTAPriority.always
            if self.FlagRun:
                self.signals.killOrResetParForWorker.emit(True)
                event.ignore()
            else:
                self.correctClose()
    
    def correctClose(self):
        if self.pfPool: self.pfPool.closeParPool()
        if self.cfgname!=lastcfgname:
            self.saveas_uicfg(self.cfgname)
        self.save_lastcfg()
        self.closeAll()
        if self.GPApar.FlagOutDated:
            warningLatestVersion(self,self.app,flagExit=1,flagWarning=self.GPApar.FlagOutDated==1)
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
        self.w_Vis.close()

    class gPaIRS_signals(QObject):
        killOrResetParForWorker=Signal(bool)#used to kill or reset he parForWorker
        progress=Signal(int)
        indProc=Signal(int)
        parPoolInit=Signal()
        guiInit=Signal()
        setMapVar=Signal()
        pause_proc=Signal()
        printOutDated=Signal(bool)

    def __init__(self,flagDebug=False,app=None):
        self.app:QApplication=app
        self.name='PaIRS'
        activateFlagDebug(flagDebug)
        self.PIVvers=PaIRS_lib.Version(PaIRS_lib.MOD_PIV).split('\n')[0]
        pri.Time.blue(2,f'gPaIRS init PaIRS-PIV {self.PIVvers}')
        super().__init__()

        #------------------------------------- Launching Parallel Pool
        self.previousPlotTime=time() #previous time for plotting
        
        self.flagGeometryInit=True
        
        self.FlagGuiInit=False
        self.signals=self.gPaIRS_signals()
        self.numUsedThreadsPIV=NUMTHREADS_PIV
        self.FlagParPoolInit=False
        self.launchParPool(NUMTHREADS_PIV_MAX)
        
        self.procdata:dataTreePar
        #self.numProcOrErrTot=0  # at the end should be equal to the number of images to be processed
        self.numCallBackTotOk=0 # Callbacks that are relative to a normal termination 
        self.SecondaryThreads=[]

        #------------------------------------- Graphical interface: widgets
        ui=Ui_gPairs()
        ui.setupUi(self)
        self.ui=ui

        self.defineTabs() 
        self.Tree_icons=self.w_Tree.Tree_icons
        self.BSizeCallbacks=[]
        def createCallback(k):
            return lambda: self.setPresetSizes(k)
        for k in range(6):
            self.BSizeCallbacks.append(createCallback(k))
        #self.ResizePopup=ResizePopup(self.BSizeCallbacks)
        self.ResizePopup=None
    
        self.cfgname=lastcfgname
 
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
        self.w_Log.setLogFont(fontPixelSize-dfontLog)
        self.ui.spin_nworkers.setValue(self.numUsedThreadsPIV)
        self.ui.spin_nworkers.setMinimum(1)
        self.ui.spin_nworkers.setMaximum(NUMTHREADS_PIV_MAX)

        #for positioning and resizing
        window=QWindow()
        window.setTitle("title")
        window.showMaximized()
        self.MaxGeo=window.geometry()
        self.MaxFrameGeo=window.frameGeometry()
        window.close()
        
        self.main_splitter=ui.main_splitter
        self.secondary_splitter=ui.secondary_splitter
        self.Vis_maxWidth=self.w_Vis.maximumWidth()
        self.fVis_maxWidth=self.ui.f_VisTab.maximumWidth()
        self.minW=self.minimumWidth()
        self.maxW=self.maximumWidth()
        margins=self.ui.Clayout.contentsMargins()
        self.minW_ManTabs=self.minimumWidth()-margins.left()-margins.right()
        
        self.ui.button_pause.hide()
        self.ui.w_progress_Proc.hide()
        self.w_Log.ui.progress_Proc.hide()
        self.w_Import.ui.w_SizeImg.hide()

        #------------------------------------- Graphical interface: miscellanea
        self.icon_wrap = QIcon()
        self.icon_wrap.addFile(u""+ icons_path +"chain.png", QSize(), QIcon.Normal, QIcon.Off)  #"down_arrow.png"/"menu_vert.png"
        self.icon_unwrap = QIcon()
        self.icon_unwrap.addFile(u""+ icons_path +"chain_broken.png", QSize(), QIcon.Normal, QIcon.Off)  #"right_arrow.png"/"menu_docked.png"

        self.icon_dock_tabs = QIcon()
        self.icon_dock_tabs.addFile(u""+ icons_path +"dock_tabs.png", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_undock_tabs = QIcon()
        self.icon_undock_tabs.addFile(u""+ icons_path +"undock_tabs.png", QSize(), QIcon.Normal, QIcon.Off)

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
        
        self.FlagButtProcRun=[False]*dataTreePar.nTypeProc
        self.FlagButtMINRun=False
        self.FlagButtPIVRun=False
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
        self.logChanges:Log_Tab=None
        self.fontPixelSize=fontPixelSize
        self.ui.button_PaIRS_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signals.printOutDated.connect(lambda flagOutDated: self.ui.button_PaIRS_download.setVisible(flagOutDated))

        #------------------------------------- Declaration of parameters 
        self.PaIRS_threadpool=QThreadPool()
        if NUMTHREADS_gPaIRS:
            self.PaIRS_threadpool.setMaxThreadCount(NUMTHREADS_gPaIRS)

        self.GPApar_base=GPApar()
        self.GPApar_old=GPApar()
        self.GPApar=GPApar()
        self.GPApar.NumCores=self.numUsedThreadsPIV
        self.TABpar=self.GPApar

        self.FlagRun=False
        self.procWorkers=[]
        self.contProc=self.nProc=0
        self.FlagProcInit=False
        self.FlagProcPlot=False
        self.procFields=['numProcOrErrTot','Log','list_print','list_pim','numCallBackTotOk','numFinalized','flagRun','flagParForCompleted']
        self.namesPIV=NamesPIV()

        self.floatings=[]
        self.defineFloatings()
        self.floatw=[]
        
        self.menuDebug=None
        self.completingTask=None
        self.waitingDialog=None

        #------------------------------------- Callbacks 
        self.setupCallbacks()
        self.w_Tree.setFocus()
        self.w_Tree.setButtons=lambda: self.setQueueButtons()
        self.w_Tree.selectItem=lambda t,i,c: self.updateGuiFromTree(t,i,c)
        self.w_Tree.addNewItem2Prevs=self.addNewItem2Prevs
        self.w_Tree.addExistingItem2Prevs=self.addExistingItem2Prevs
        self.w_Tree.removeItemFromPrevs=self.removeItemFromPrevs
        self.w_Tree.moveupdownPrevs=self.moveupdownPrevs

        self.w_Vis.FlagAddPrev=False

        gPaIRS_Tab.indTreeGlob=0
        gPaIRS_Tab.indItemGlob=0
        gPaIRS_Tab.FlagGlob=True
        
        self.w_Import.FlagDisplayControls=False
        self.w_Export.FlagDisplayControls=False
        self.w_Process.FlagDisplayControls=False
        self.w_Log.FlagDisplayControls=False
        self.w_Vis.FlagDisplayControls=False

        #shortcuts
        scs=['Ctrl+W','Ctrl+0','Ctrl+Shift+0','Ctrl+1','Ctrl+Minus','Ctrl+Shift+1','Ctrl+Shift+Minus','Ctrl+9','Ctrl+Plus','Ctrl+Shift+9','Ctrl+Shift+Plus','Shift+Backspace']
        self.keyboardQShortcuts=[]
        for sc in scs:
            kQSc=QShortcut(QKeySequence(sc), self)
            kQSc.activated.connect(lambda sc=sc: self.keyboardShortcut(sc))
            self.keyboardQShortcuts.append(kQSc)

        #------------------------------------- Initialization
        from .PaIRS_pypacks import basefold
        basefold=myStandardPath(basefold)
        if os.path.exists(lastcfgname):
            WarningMessage='Error with loading the last configuration file.\n'
            Flag,var=self.import_uicfg(lastcfgname,WarningMessage) 
            if not Flag:
                os.remove(lastcfgname)
                self.initialize()
            else:    
                try:
                    GPApar_prev=var[1]
                    self.GPApar.copyfrom(GPApar_prev)
                    self.GPApar.currentVersion=__version__
                    self.GPApar.FlagOutDated=0 if self.GPApar.currentVersion==self.GPApar.latestVersion or not self.GPApar.latestVersion else self.GPApar.FlagOutDated
                    self.setGPApar() 
                except Exception as inst:
                    warningDialog(self,WarningMessage,flagScreenCenter=True)
                    pri.Error.red(f'{WarningMessage}:\n{traceback.print_exc()}\n\n{inst}')
                    os.remove(lastcfgname)
                    self.initialize()
        else:
            self.initialize()   
        self.GPApar_old.copyfrom(self.GPApar)   

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
        pri.Time.blue(0,'dopo setupUi')
        self.FlagClosing=[False]
        self.setupPathCompleter()

        self.FlagGuiInit=True
        self.load_gif = QMovie(u""+ icons_path +"loading_2.gif")
        self.load_gif.start()
        self.loaded_map=QPixmap(u""+ icons_path + "loaded.png")
        self.parPoolInitSetup()
        
        pri.Time.blue(0,'fine di tutto init')

    def setupPathCompleter(self):
        if Flag_fullDEBUG:
            opt=basefold_DEBUGOptions+self.w_Import.INPpar.pathCompleter
            self.w_Import.INPpar.pathCompleter=[]
            for p in [myStandardPath(p) for p in opt]:
                if p not in self.w_Import.INPpar.pathCompleter and os.path.exists(p):
                    self.w_Import.INPpar.pathCompleter.append(p)
                if len(self.w_Import.INPpar.pathCompleter)==10: break
            self.w_Import.setPathCompleter()

    def initialize(self):
        pri.Info.yellow('||| Initializing gPaIRS |||')
        self.reconfigure()
        #necessary to initialize sizes in both configurations
        self.GPApar.FlagUndocked=True
        self.DefaultSize() #undocked
        self.GPApar.FlagUndocked=False
        self.DefaultSize()  #docked
        self.setGPApar()  

    def defineFloatings(self):
        self.floatings=[]
        for i,wn in enumerate(self.opwidnames):
            wname="w_"+wn
            wid=getattr(self,wname)
            self.floatings.append(FloatingObject(self,wid))
        for f in self.floatings:
            self.GPApar.FloatingsGeom.append(f.geometry())
            self.GPApar.FloatingsVis.append(f.isVisible())
        geo=self.floatings[self.GPApar.prevTab].geometry()
        for k in range(3): self.GPApar.FloatingsGeom[k]=geo 
        self.GPApar.FloatingsGeom.append(self.geometry())
        self.GPApar.FloatingsVis.append(self.isVisible())

    def setupCallbacks(self):
        #------------------------------------- Main Window buttons
        for j,wn in enumerate(self.optabnames):
            if self.GPApar.FlagAllTabs:
                setattr(self.GPApar,"Flag"+wn,True)
            else:
                if j: setattr(self.GPApar,"Flag"+wn,False)
                else: setattr(self.GPApar,"Flag"+wn,True)
        """
        self.ui.button_Input.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Input'),'gPaIRS') )
        self.ui.button_Output.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Output'),'gPaIRS') )
        self.ui.button_Process.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Process'),'gPaIRS') )
        self.ui.button_Log.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Log'),'gPaIRS') )
        self.ui.button_Vis.clicked.connect(self.w_Tree.addParWrapper(lambda: self.button_Tab_callback('Vis'),'gPaIRS') )
        self.ui.button_default_sizes.clicked.connect(self.w_Tree.addParWrapper(self.button_default_sizes_callback,'gPaIRS'))
        self.ui.button_dock.clicked.connect(self.w_Tree.addParWrapper(self.button_dock_callback,'gPaIRS'))
        self.ui.button_Shape.clicked.connect(self.w_Tree.addParWrapper(self.button_Shape_callback,'gPaIRS'))
        """
        self.ui.button_Input.clicked.connect(lambda: self.button_Tab_callback('Input'))
        self.ui.button_Output.clicked.connect(lambda: self.button_Tab_callback('Output'))
        self.ui.button_Process.clicked.connect(lambda: self.button_Tab_callback('Process'))
        self.ui.button_Log.clicked.connect(lambda: self.button_Tab_callback('Log'))
        self.ui.button_Vis.clicked.connect(lambda: self.button_Tab_callback('Vis'))
        for k,wn in enumerate(self.opwidnames):
            def setClosedCallback(wn):
                w=getattr(self,'w_'+wn)
                w.ui.button_close_tab.clicked.connect(lambda: self.close_tab(w))
            setClosedCallback(wn)
        self.main_splitter.addfuncout['setScrollAreaWidth']=self.setOpButtonLabel
        self.secondary_splitter.addfuncout['setScrollAreaWidth']=self.setScrollAreaWidth
        

        self.ui.button_default_sizes.clicked.connect(self.button_default_sizes_callback)
        self.ui.button_dock.clicked.connect(self.button_dock_callback)
        self.ui.button_Shape.clicked.connect(self.button_Shape_callback)

        self.ui.button_Run.clicked.connect(self.w_Tree.addParWrapper(self.button_RunPause_callback,'gPaIRS'))
        self.ui.button_pause.clicked.connect(self.w_Tree.addParWrapper(self.button_RunPause_callback,'gPaIRS'))

        self.w_Tree.ui.button_min_callback=self.w_Tree.addParWrapper(lambda: self.addProc(dataTreePar.typeMIN),'gPaIRS') 
        self.w_Tree.ui.button_min.clicked.connect(self.w_Tree.ui.button_min_callback)
        self.w_Tree.ui.button_PIV_callback=self.w_Tree.addParWrapper(lambda: self.addProc(dataTreePar.typePIV),'gPaIRS') 
        self.w_Tree.ui.button_PIV.clicked.connect(self.w_Tree.ui.button_PIV_callback)
        self.w_Tree.ui.button_import_past_callback=self.w_Tree.addParWrapper(self.loadPastProc,'gPaIRS')
        self.w_Tree.ui.button_import_past.clicked.connect(self.w_Tree.ui.button_import_past_callback)
        self.w_Tree.ui.button_edit_item_callback=self.button_edit_item_callback
        self.w_Tree.ui.button_edit_item.clicked.connect(self.w_Tree.ui.button_edit_item_callback)

        #------------------------------------- Menu
        self.ui.actionPaIRS_Run.triggered.connect(lambda: runPaIRS(self,))
        self.ui.actionPaIRS_Clean_run.triggered.connect(lambda: runPaIRS(self,'-c'))
        self.ui.actionPaIRS_Debug_run.triggered.connect(lambda: runPaIRS(self,'-d'))
        self.ui.actionCalVi_Run.triggered.connect(lambda: runPaIRS(self,'-calvi'))
        self.ui.actionCalVi_Clean_run.triggered.connect(lambda: runPaIRS(self,'-calvi -c'))
        self.ui.actionCalVi_Debug_run.triggered.connect(lambda: runPaIRS(self,'-calvi -d'))
        self.ui.actionNew.triggered.connect(self.new_uicfg)
        self.ui.actionLoad.triggered.connect(self.load_uicfg)
        self.ui.actionSave.triggered.connect(self.save_uicfg)
        self.ui.actionSave_as.triggered.connect(self.saveas_uicfg)
        self.ui.actionClose.triggered.connect(self.close_uicfg)
        self.ui.aExit.triggered.connect(self.close)
        self.showChanges=lambda: changes(self,Log_Tab,fileChanges)
        self.ui.actionChanges.triggered.connect(self.showChanges)
        self.ui.actionChanges.triggered.connect(self.showChanges)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionGuide.triggered.connect(self.guide)  
        self.ui.button_PaIRS_download.clicked.connect(lambda: button_download_PaIRS_callback(self,self.app))

        #------------------------------------- Animations
        self.animation.valueChanged.connect(self.moveToColumn)  

        #------------------------------------- Additions
        self.ui.spin_nworkers.valueChanged.connect(self.spin_nworkers_callback)
        self.w_Import.ui.edit_path.textChanged.connect(self.change_edit_path)

    def change_edit_path(self):
        if self.w_Export.OUTpar.FlagSameAsInput:
            self.w_Export.ui.edit_path.setText(self.w_Import.ui.edit_path.text())

    def setFontPixelSize(self):
        if self.fontPixelSize==self.GPApar.fontPixelSize: return
        fPixSize=self.GPApar.fontPixelSize
        font=QFont()
        font.setFamily(fontName)
        font.setPixelSize(fPixSize)
        if self.app: self.app.setFont(font)
        setFontPixelSize(self,fPixSize)
        self.setTabFontPixelSize(fPixSize)
        for tn in self.optabnames:
            self.setOpButtonText(tn)
        if self.aboutDialog:
            self.aboutDialog.fontPixelSize=self.GPApar.fontPixelSize
            self.aboutDialog.setFontSizeText()
        if self.logChanges: self.logChanges.setFontPixelSize(fPixSize)
        if self.menuDebug: self.menuDebug.setFont(self.ui.menuFile.font())
        self.fontPixelSize=fPixSize
    
    def setTabFontPixelSize(self,fPixSize):
        fPixSize_TabNames=min([fPixSize*2,30])
        for tn,wn in zip(self.optabnames,self.opwidnames):
            w=getattr(self,'w_'+wn)
            setFontPixelSize(w,fPixSize)
            lab:QLabel=w.ui.name_tab
            font=lab.font()
            font.setPixelSize(fPixSize_TabNames)
            lab.setFont(font)
            button:RichTextPushButton=getattr(self.ui,f"button_{tn}")
            font=button.font()
            font.setPixelSize(fPixSize+1)
            button.setFont(font)
            button.lbl.setFont(font)
        lab=self.w_Tree.ui.name_tab
        font=lab.font()
        font.setPixelSize(fPixSize_TabNames)
        lab.setFont(font)
        self.w_Log.setLogFont(fPixSize-dfontLog)


#********************************************* TAB definitions
    def defineTabs(self):
        self.optabnames=['Input','Output','Process','Log','Vis']
        self.opwidnames=['Import','Export','Process','Log','Vis'] #+'Tab'
        wclasses=[Import_Tab,Export_Tab,Process_Tab,Log_Tab,Vis_Tab]+[Tree_Tab]
        
        for k,tname in enumerate(self.opwidnames+['Tree']):
            wname='w_'+tname
            setattr(self,wname,wclasses[k](self,tname in ('Log')))
            w=getattr(self,wname)
            lay=getattr(self.ui,'f'+tname+'_lay')
            lay.addWidget(w)
            w.show()
            

        self.w_Tree:Tree_Tab       
        self.w_Import:Import_Tab   
        self.w_Export:Export_Tab
        self.w_Process:Process_Tab
        self.w_Log:Log_Tab  
        self.w_Vis:Vis_Tab

        self.TABnames=['Import','Export','Process','Vis','Tree']
        self.TABParDataNames=['INP','OUT','PRO','VIS','']

        self.w_Tree.defineSetTABpar(self.setTREpar)
        self.defineTABbridges()
        
    def defineTABbridges(self):
        for tname in self.TABnames:
            w: gPaIRS_Tab
            self.defineTAB_setParBridge(tname)
            self.defineTAB_addParBridge(tname)
            wname='w_'+tname
            w=getattr(self,wname)
            w.TABname=tname
            w.fUpdatingTabs=self.setUpdatingState

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
            self.setItemConnections(indTree,indItem,ind)   
            if gPaIRS_Tab.indTreeGlob==1 and self.w_Tree.ui.button_edit_item.isChecked():
                self.checkFutureProc()
                self.w_Tree.TABpar.copyfrom(self.w_Tree.TABpar_prev[indTree][indItem][ind])
            return           
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
            indTree,indItem,ind=self.w_Tree.TABpar.indexes()
            self.setItemConnections(indTree,indItem,ind) #necessario perchè dopo la copia di TABpar in prev i collegamenti sono persi!!!
            if fw: fw.setFocus()
        def set_par_bridge_prev(indTree,indItem,ind):
            fw=self.focusWidget()
            self.actualBridge(tname,indTree,indItem,ind)
            for f in fset_par_prev:
                f(indTree,indItem,ind,False) #setting previous parameters without bridge (False=without bridge)
            self.setItemConnections(indTree,indItem,ind) #necessario perchè dopo la copia di TABpar in prev i collegamenti sono persi!!!
            if fw: fw.setFocus()
        w.defineTABbridge(set_par_bridge,set_par_bridge_prev)

    def actualBridge(self,tname,indTree,indItem,ind):
        if ind>-1:
            INP:INPpar=self.w_Import.TABpar_prev[indTree][indItem][ind]
            OUT:OUTpar=self.w_Export.TABpar_prev[indTree][indItem][ind]
            PRO:PROpar=self.w_Process.TABpar_prev[indTree][indItem][ind]
            VIS:VISpar=self.w_Vis.TABpar_prev[indTree][indItem][ind]
            TRE:dataTreePar=self.w_Tree.TABpar_prev[indTree][indItem][ind]
            pri.Callback.green(f'    --- gPaIRS bridge_prev {[indTree]}{[indItem]}{[ind]}  Tree indexes: {self.w_Tree.TABpar.indexes()}')
        else:
            INP=self.w_Import.TABpar
            OUT=self.w_Export.TABpar
            PRO=self.w_Process.TABpar
            VIS=self.w_Vis.TABpar
            self.w_Tree.TABpar.indTree,self.w_Tree.TABpar.indItem,self.w_Tree.TABpar.ind=getattr(self,'w_'+tname).TABpar.indexes()
            TRE=self.w_Tree.TABpar
            pri.Callback.green(f'    --- {tname} bridge_prev {[indTree]}{[indItem]}{[ind]}  Tree indexes: {self.w_Tree.TABpar.indexes()}')

            

        if TRE.indTree==0 and TRE.flagRun: #aggiusta current se la copia proviene da un processo con FlagRun!=0
            #data_prev=self.w_Tree.TABpar_prev[data.indTree][data.indItem][data.ind]
            VIS.Tre.copyfrom(VISpar.TRE())
            VIS.FlagExistMean=[False]*2
            VIS.FlagExistRes=[False]*2
            TRE.copyfrom(dataTreePar(),['ind','indItem','indTree'])
        
        if tname=='Import':
            OUT.copyfromdiz(INP,['x','y','w','h','W','H'])
            OUT.inputPath=INP.path
            OUT.FlagValidSet=not (INP.FlagValidPath in (0,-10) or INP.FlagValidRoot in (0,-10))
            self.w_Export.setFlagValid(OUT)
            if INP.FlagValidPath!=-10 or INP.FlagValidRoot!=-10:
                FlagReset=VIS.Inp.isDifferentFrom(INP,[],['pinfo'],True)
                VIS.Inp.copyfrom(INP)
                VIS.FlagReset=[FlagReset,FlagReset]
                VIS.Out.copyfrom(OUT)
                VIS.nfield=INP.selected
                VIS.list_Image_Files=copy.deepcopy(INP.list_Image_Files[INP.list_ind_items[0]:INP.list_ind_items[1]])
                self.w_Vis.updateVisfromINP(VIS)
        if tname=='Export':
            INP.copyfromdiz(OUT,['x','y','w','h','W','H'])
            if VIS.Out.isDifferentFrom(OUT,[],[],True):
                VIS.Out.copyfrom(OUT)
                VIS.FlagReset=[True,False]
                self.w_Vis.updateVisfromINP(VIS)
        if tname=='Process':
            VIS.Pro.copyfrom(PRO)
        if tname=='Vis':
            if INP.selected!=VIS.nfield:
                INP.selected=VIS.nfield
                VIS.Inp.copyfrom(INP)
        if tname=='Tree':
            VIS.Tre.copyfrom(TRE)
            INP.selected=VIS.nfield
            VIS.Inp.copyfrom(INP)
            self.w_Vis.updateVisfromINP(VIS)  
        return

    def setConnections(self):
        data=self.w_Tree.TABpar
        data.INP=self.w_Import.TABpar
        data.OUT=self.w_Export.TABpar
        data.PRO=self.w_Process.TABpar
        data.VIS=self.w_Vis.TABpar

        for indTree in range(len(self.w_Tree.TABpar_prev)):
            for indItem in range(len(self.w_Tree.TABpar_prev[indTree])):
                for ind in range(len(self.w_Tree.TABpar_prev[indTree][indItem])):
                    self.setItemConnections(indTree,indItem,ind)
        
    def setItemConnections(self,indTree,indItem,ind):
        data:dataTreePar=self.w_Tree.TABpar_prev[indTree][indItem][ind]
        data.INP=self.w_Import.TABpar_prev[indTree][indItem][ind]
        data.OUT=self.w_Export.TABpar_prev[indTree][indItem][ind]
        data.PRO=self.w_Process.TABpar_prev[indTree][indItem][ind]
        data.VIS=self.w_Vis.TABpar_prev[indTree][indItem][ind]
        data.VIS.Tre.list_pim=data.list_pim 
        return data
    
    def setUpdatingState(self,flagUpdating):
        if Flag_DISABLE_onUpdate: 
            for tname in self.TABnames:
                w: gPaIRS_Tab
                wname='w_'+tname
                w=getattr(self,wname)
                if tname=='Vis':
                    w.ui.w_plot.setEnabled(not flagUpdating)
                else:
                    w.ui.scrollArea.setEnabled(not flagUpdating)
            #w.setVisible(not flag)
        self.ui.label_updating_import.setVisible(flagUpdating)
        pass

#********************************************* Selection of items
    #self.TREselect_fun=lambda iTold,iT,t,i,c: None
    def updateGuiFromTree(self,tree,item,column):
        indTree_old=self.w_Tree.TREpar.indTree
        tree,queue=self.w_Tree.pickTree(indTree_old)

        idata: TABpar
        idata=item.data(column,Qt.UserRole)
        ind=len(self.w_Tree.TABpar_prev[idata.indTree][idata.indItem])-1 #idata.ind
        pri.Callback.magenta(f'$$$ Updating gPaIRS based on indTree={idata.indTree} indItem={idata.indItem} ind={ind}      from old tree#{indTree_old}')
        for t in self.TABnames:
            w=getattr(self,'w_'+t)
            w.TABpar.indTree=idata.indTree
            w.TABpar.indItem=idata.indItem
            w.TABpar.ind=ind

        self.w_Tree.setTABpar_prev(idata.indTree,idata.indItem,ind,True)       #idata.ind

        '''
        # TBD TA lo uso per controllare i cfg in output rapidamente
        tree,_=self.w_Tree.pickTree(self.w_Tree.TREpar.indTree)
        d=tree.currentItem().data(0,Qt.UserRole)
        data:dataTreePar=self.w_Tree.TABpar_prev[d.indTree][d.indItem][d.ind]
        data.writeCfgProcPiv()
        #'''      
        return 
    
    def setTREpar(self):
        #data:dataTreePar=self.w_Tree.TABpar
        tree,queue=self.w_Tree.pickTree(self.w_Tree.TABpar.indTree)
        i=queue[self.w_Tree.TABpar.indItem]
        idata=i.data(0,Qt.UserRole)
        #idata.ind=data.ind
        self.w_Tree.focusOnTree(tree)
        tree.setCurrentItem(i)
        data:dataTreePar=self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][idata.ind] #!!!GP idata.ind? Si!!! anzichè self.w_Tree.TABpar.ind
        
        self.setButtons(data)
        self.w_Log.ui.log.setText(data.Log)
        self.w_Log.moveToBottom()

        tree:QTreeWidget
        FlagCase=gPaIRS_Tab.indTreeGlob==data.indTree and gPaIRS_Tab.indItemGlob==data.indItem
        if  not FlagCase and self.w_Tree.ui.button_edit_item.isChecked():
            self.w_Tree.ui.button_edit_item.setChecked(False)
            self.button_edit_item_callback()
        elif FlagCase and self.w_Tree.ui.button_edit_item.isChecked():
            i.setIcon(0,self.Tree_icons.editing)
        return
        
    def setButtons(self,data):
        pri.Callback.yellow('||| Adjusting interface button graphics |||')
        if not self.FlagParPoolInit: 
            self.ui.button_Run.hide()
            self.ui.w_progress_Proc.hide()
            self.ui.button_pause.hide()
            self.FlagButtProcRun=[False]*dataTreePar.nTypeProc
            self.setButtonsAddProc(data)
            return
        self.setQueueButtons(data)
        if self.app and not self.FlagKeyCallbackExec: self.app.processEvents()
                 
    def setQueueButtons(self,*args):
        if len(args): data=args[0]
        else: data=self.w_Tree.TABpar
        Tree_Tab.setButtons(self.w_Tree,self.FlagRun)
        self.w_Tree.ui.button_edit_item.setEnabled(data.indTree==1 and not data.flagRun and not self.FlagRun)
        if not data.flagRun in (0,-1):
            self.w_Tree.ui.button_restore.setEnabled(False)
        self.setButtonsRun(data)
        self.setButtonsAddProc(data)

    def setButtonsRun(self,data):
        if not self.FlagRun:
            if data.indTree in (-1,0):
                if len(self.w_Tree.TREpar.future):
                    self.ui.button_Run.show()
                else:
                    self.ui.button_Run.hide()
                self.ui.button_pause.hide()
                self.ui.w_progress_Proc.hide()
            elif data.indTree==1:
                if data.flagRun:
                    self.ui.button_Run.hide()
                    self.setButtonPause(True)
                    self.ui.button_pause.show()
                    self.ui.w_progress_Proc.show()
                    self.setProgressBar(data)
                    self.showTimeToEnd(data)
                else:
                    self.ui.button_Run.show()
                    self.ui.button_pause.hide()
                    self.ui.w_progress_Proc.hide()
        else:
            self.ui.button_Run.hide()
            self.setButtonPause(False)
            self.ui.button_pause.show()
            self.ui.w_progress_Proc.show()
        if data.indTree==0:
            self.w_Log.ui.progress_Proc.hide()
            self.ui.button_pause.hide()
        elif data.indTree in (-1,1):
            if data.flagRun==0:
                self.w_Log.ui.progress_Proc.hide()
            else:
                self.w_Log.ui.progress_Proc.show()
                self.setLogProgressBar(data)

    def setButtonPause(self,flagPlay):
        if flagPlay:
            self.ui.button_pause.setIcon(self.w_Import.icon_play)
            stringa='Restart'
        else:
            self.ui.button_pause.setIcon(self.w_Import.icon_pause)
            stringa='Pause'
        tip=f'{stringa} process queue'+' ('+self.ui.button_pause.shortcut().toString(QKeySequence.NativeText)+')'
        self.ui.button_pause.setToolTip(tip)
        self.ui.button_pause.setStatusTip(tip)

    def setLogProgressBar(self,data):
        self.w_Log.ui.progress_Proc.setMinimum(0)
        self.w_Log.ui.progress_Proc.setMaximum(data.nimg)
        self.w_Log.ui.progress_Proc.setValue(data.numFinalized) 
        return

    def setButtonsAddProc(self,data):
        indTree=data.indTree
        typeProc=data.typeProc
        self.FlagButtProcRun=[False]*dataTreePar.nTypeProc
        if indTree==1:
            self.FlagButtProcRun[typeProc]=not self.FlagRun

        name_proc=['','ensemble minimum computation','PIV process']
        button_name=['','min','PIV']
        button_label=['','MIN','PIV']
        scut=['',u"Ctrl+M",u"Ctrl+,"]
        for k in range(1,dataTreePar.nTypeProc):
            b=getattr(self.w_Tree.ui,'button_'+button_name[k])
            if self.FlagButtProcRun[k]:
                b.setIcon(self.w_Tree.icon_run_piv)
                b.setText(' Run')
                b.setShortcut(QCoreApplication.translate("gPairs", scut[k], None))
                tip='Run the processes in the future queue and enjoy!'+' ('+b.shortcut().toString(QKeySequence.NativeText)+')'
            else:
                b.setIcon(self.w_Tree.icon_add)
                b.setText(' '+button_label[k])
                b.setShortcut(QCoreApplication.translate("gPairs", scut[k], None))
                tip=f'Add {name_proc[k]} to queue'+' ('+b.shortcut().toString(QKeySequence.NativeText)+')'
            b.setToolTip(tip)
            b.setStatusTip(tip)

    def setItemTips(self,item,data:dataTreePar):
        tooltip=statustip=item.text(0)
        statustip+=' - '+data.name_proc[data.typeProc]
        item.setToolTip(0,tooltip)
        item.setStatusTip(0,statustip)

    def button_edit_item_callback(self):
        if self.w_Tree.ui.button_edit_item.isChecked():
            tip='Stop editing current item'+' ('+self.w_Tree.ui.button_edit_item.shortcut().toString(QKeySequence.NativeText)+')'
            self.setGlobInd([],[],True)
        else:
            tip='Edit current item'+' ('+self.w_Tree.ui.button_edit_item.shortcut().toString(QKeySequence.NativeText)+')'
            self.setGlobInd(gPaIRS_Tab.indTreeGlob,gPaIRS_Tab.indItemGlob,False)
            self.setGlobInd(0,0,True)
        self.w_Tree.ui.button_edit_item.setToolTip(tip)
        self.w_Tree.ui.button_edit_item.setStatusTip(tip)

    def setGlobInd(self,indTree,indItem,FlagSet):
        if indTree==[]:
            indTree=self.w_Tree.TREpar.indTree
        tree,queue=self.w_Tree.pickTree(indTree)
        if indItem==[]:
            item=tree.currentItem()
            indItem=item.data(0,Qt.UserRole).indItem
        else:
            item=queue[indItem]
        data=self.w_Tree.TABpar_prev[indTree][indItem][-1]

        if FlagSet:
            #data.icon_type=self.Tree_icons.icontype('editing')
            item.setIcon(0,self.Tree_icons.editing)
            gPaIRS_Tab.indTreeGlob=indTree
            gPaIRS_Tab.indItemGlob=indItem
        else:
            self.setItemLabel(data)
        if (gPaIRS_Tab.indTreeGlob!=0 or gPaIRS_Tab.indItemGlob!=0) and FlagSet:
            data_current=self.w_Tree.TABpar_prev[0][0][-1] #last of current
            item_current=self.w_Tree.TREpar.current[0]
            self.w_Tree.ui.button_edit_item.setChecked(True)
            data_current.icon_type=self.Tree_icons.icontype('none')
            item_current.setIcon(0,self.Tree_icons.none)            
    
    def setItemLabel(self,data:dataTreePar):
        tree,queue=self.w_Tree.pickTree(data.indTree)
        item:QTreeWidgetItem=queue[data.indItem]
        item.setIcon(0,self.Tree_icons.icon(data.icon_type))

#*************************************************** Parallel Pool
    def launchParPool(self,nworkers):
        # TA ho deciso di utilizzare concurrent.futures per lanciare il processo in parallelo perchè non ho capito bene come usare 
        # quello di QT
        # Avevo provato anche Thread ma non sono stato capace di capire come lanciare 
        # Ho provato a lanciare le due operazioni all'interno di initParForAsync in parallelo ma mi sembra che sia molto lento
        # Alla fine ho adottato una configurazione mista con initParForAsync scritta in mod asincrono
        # Quando initParForAsync termina chiama initParForComplete che effettua le ultime cose 

        if hasattr(self, 'pfPool'):#this function should be called only once but just in case we check and close the parPool
          self.pfPool.closeParPool()
        else:
          self.pfPool=None
          self.parForMul=None
        self.FlagParPoolInit=False
        self.signals.parPoolInit.connect(self.parPoolInitSetup)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        f3=executor.submit(asyncio.run,initParForAsync(nworkers))
        def initParForComplete(_f3):
          pri.Time.blue(0,'fine initParFor1')
          (pfPool,parForMul)=f3.result()
          #timesleep(5)
          pri.Time.blue(0,'PIV_ParFor_Worker dopo ParForMul')
          parForMul.sleepTime=ParFor_sleepTime #time between calls of callBack
          self.pfPool=pfPool
          self.parForMul=parForMul
          self.parForMul.numUsedCores=self.numUsedThreadsPIV # =NUMTHREADS_PIV#potrebbe essere minore di NUMTHREADS_PIV_MAX con cui è stato impostato
          self.FlagParPoolInit=True
          self.signals.parPoolInit.emit()
        f3.add_done_callback(initParForComplete)

    @Slot(int)
    def parPoolInitSetup(self):
        if self.FlagGuiInit:
            tree,_=self.w_Tree.pickTree(self.w_Tree.TREpar.indTree)
            idata=tree.currentItem().data(0,Qt.UserRole)
            data=self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][-1] #!!!GP idata.ind?
            self.setButtons(data)
            if not self.FlagParPoolInit:
                self.FlagParPoolInit=False
        
                self.ui.label_gif.setPixmap(QPixmap())
                self.ui.label_gif.setMovie(self.load_gif)
                
                self.ui.label_loading.setText('Starting parallel pool with') 
                self.ui.spin_nworkers.setEnabled(False)
                self.ui.label_loading_2.setText('workers...') 
            else:
                self.ui.label_gif.setMovie(QMovie())
                self.ui.label_gif.setPixmap(self.loaded_map)
                
                self.ui.label_loading.setText('Parallel pool with')
                self.ui.spin_nworkers.setEnabled(True)
                self.ui.label_loading_2.setText('workers started!')   
                #self.repaint()                

    def spin_nworkers_callback(self):
        val=self.ui.spin_nworkers.value() 
        self.GPApar.NumCores=val
        if val <=NUMTHREADS_PIV_MAX:
            self.numUsedThreadsPIV=val 

#*************************************************** Warnings
    def warningDialog(self,Message,time_milliseconds=0,flagScreenCenter=False,icon=QIcon(),palette=None,pixmap=None,title='Warning!',flagRichText=False,flagNoButtons=False):
        return warningDialog(self,Message,time_milliseconds,flagScreenCenter,icon,palette,pixmap,title,flagRichText,flagNoButtons)

    def questionDialog(self,Message):
        flagYes=questionDialog(self,Message)
        return flagYes

#*************************************************** Menus
    def setGPaIRSTitle(self):
        if self.cfgname==lastcfgname:
            cfgString=''
            self.ui.actionClose.setEnabled(False)
        else:
            cfgString=f': {self.cfgname}'
            self.ui.actionClose.setEnabled(True)
        if Flag_DEBUG:#TA per non incasinarmi
            windowTitle=f'PaIRS (v{version}.{__subversion__}) -- cfg v{uicfg_version} -- PIV {self.PIVvers} -- {platform.system()}'
        else:
            windowTitle=f'PaIRS (v{version})'
        windowTitle+=cfgString
        self.setWindowTitle(windowTitle)

#********************* File
    def pauseQuestion(self,taskDescription='continuing',task=None):
        FlagPause=False
        if self.contProc!=self.nProc:
            FlagPause=self.questionDialog(f'PaIRS is currently executing the processes in the Future queue. Do you want to pause them before {taskDescription}?')
            if FlagPause: 
                if self.FlagRun: self.button_RunPause_callback()
                self.setEnabled(False)
                self.completingTask=task
                self.waitingDialog=self.warningDialog('Please, wait while stopping the running processes!',pixmap=''+ icons_path +'waiting_c.png',flagNoButtons=True)
        return FlagPause

    def new_uicfg(self):
        if self.pauseQuestion('creating a new project',lambda: self.new_uicfg()): return
        if self.cfgname!=lastcfgname:
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
        self.cfgname=lastcfgname
        self.setGPaIRSTitle()
        pathCompleter=self.w_Import.INPpar.pathCompleter
        self.w_Tree.clearAllTimes()
        TRE=self.w_Tree.TREpar
        tree_current=self.w_Tree.ui.tree_current
        self.w_Tree.createItemInTree(tree_current,TRE.current,"current",dataTreePar(),QIcon())
        for tname in self.TABnames:
            w:gPaIRS_Tab=getattr(self,"w_"+tname)        
            w.TABpar.copyfrom(w.ParClass())
            w.TABpar_prev=[[[w.ParClass()]],[],[]] 
            w.FlagAddingPar=[[[False]],[],[]]    
            w.FlagAsyncCall=[[[False]],[],[]]   
        self.setGlobInd(0,0,True)
        #self.setConnections()
        self.w_Tree.TABpar_prev[0][0][0].setCompleteLog()
        INPpar_prev=self.w_Import.TABpar_prev[0][0][0]
        INPpar_prev.pathCompleter=pathCompleter
        self.w_Import.FlagAddPrev=False        
        self.w_Import.getPinfoFromPath(INPpar_prev,['./','']) 
        self.w_Import.setTABpar_prev(0,0,0,True) #with bridge
        self.w_Import.FlagAddPrev=True

        from .PaIRS_pypacks import basefold
        if basefold!='./':
            self.w_Import.ui.edit_path.setText(basefold)
            self.w_Import.edit_path_callback()

            for tname in self.TABnames:
                w:gPaIRS_Tab=getattr(self,"w_"+tname)        
                w.TABpar_prev[0][0].pop(0)
                w.TABpar_prev[0][0][0].ind=0
                w.TABpar.ind=0
                w.FlagAddingPar[0][0].pop(0)
                w.FlagAsyncCall[0][0].pop(0)
            self.w_Tree.selectCurrent()

    def getCurrentCfgVar(self):
        self.updateGPAparGeom()
        #var = [serialeCfg self.GPApar.duplicate(), t, self.w_Vis.VISpar.duplicate()]
        info=['uicfg-gPairS',uicfg_version,__version__, __subversion__, __year__]
        geom = self.GPApar.duplicate()
        tree=treeToSave(self.w_Tree.TREpar)
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
        var=[info]+[geom]+[tree]+[WIDnames]+[prevs]+[FlagAddingPar]+[FlagAsyncCall]
        return var

    def setCfgVar(self,var):
        #var=info+geom+tree_var+WIDnames+prevs
        #self.ui.centralwidget.hide()
        info=var[0]  #['gPairS',__version__, __subversion__, __year__]
        if info[0]!='uicfg-gPairS':
            WarningMessage='The file is not a valid PaIRS configuration file!'
            return False, WarningMessage
        else:
            ver=[int(i) for i in info[1].split('.')]
            cfgver=[int(i) for i in uicfg_version_to_load.split('.')]
            if not all([ver[k]>=cfgver[k] for k in range(len(ver))]):
                WarningMessage=f'The file is out-of-date (v{ver}) and not compatible with the current version (v{cfgver})!'
                return False, WarningMessage
        self.w_Tree.clearAllTimes()
        geom=var[1]
        tree_var:treeToSave=var[2]
        for n in tree_var.tree_names:
            t=getattr(tree_var,n)
            tree,queue=self.w_Tree.pickTree(n)
            for name,idata in zip(t.names,t.idata):
                self.w_Tree.createItemInTree(tree,queue,name,idata,QIcon())
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
        self.setConnections()
        self.setGlobInd(0,0,True)
        self.checkPastProc()
        self.checkFutureProc()
        self.w_Tree.selectCurrent()
        #self.ui.centralwidget.show()
        return True,''

    def save_uicfg(self,filename='',Title="Select location and name of the project file to save"):
        if self.cfgname==lastcfgname:
            self.saveas_uicfg(filename,Title)
        else:
            self.saveas_uicfg(self.cfgname,Title)

    def saveas_uicfg(self,filename='',Title="Select location and name of the project file to save"):
        if self.pauseQuestion('saving the current project',lambda: self.saveas_uicfg(filename,Title)): return
        if filename=='':
            filename, _ = QFileDialog.getSaveFileName(self,Title, 
                    dir=self.w_Import.INPpar.path+"uicfg", filter=f'*{outExt.cfg}',\
                    options=optionNativeDialog)
            if filename[-4:]=='.cfg': filename=filename[:-4]  #per adattarlo al mac
            filename=myStandardRoot('{}'.format(str(filename)))
            if not filename: return
        if not outExt.cfg in filename:
            filename=filename+outExt.cfg
        if filename:
            var=self.getCurrentCfgVar()
            filename=myStandardRoot(filename)
            try:
                with open(filename, 'wb') as file:
                    pickle.dump(var, file)
                    pri.Info.white(f'>>>>> Saving ui configuration file:\t{filename}')
                    self.cfgname=filename
                    self.setGPaIRSTitle()
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
        with open(lastcfgname, 'wb') as file:
                pickle.dump(var2, file)
                pri.Info.white(f'    >>>>> Saving last ui configuration to file:\t{lastcfgname}')

    def load_uicfg(self):
        if self.pauseQuestion('opening an old project',lambda: self.load_uicfg()): return
        filename, _ = QFileDialog.getOpenFileName(self,\
            "Select a PaIRS configuration file", filter=f'*{outExt.cfg}',\
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
                self.setGPaIRSTitle()
            else:
                warningDialog(self,WarningMessage+WarningMessage2)
        except Exception as inst:
            warningDialog(self,WarningMessage)
            pri.Error.red(f'{WarningMessage}:\n{traceback.print_exc()}\n\n{inst}')
            Flag=False 
        return Flag,var

#********************* Help    
    def guide(self):
        #url = QUrl("http://wpage.unina.it/etfd/PaIRS/PaIRS-UniNa-Guide.pdf")
        url = QUrl("https://www.pairs.unina.it/web/PaIRS-UniNa-Guide.pdf")
        QDesktopServices.openUrl(url)

    def about(self):
        if self.aboutDialog:
            self.aboutDialog.hide()
            self.aboutDialog.show()
        else:
            self.aboutDialog=infoPaIRS(self)
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
        self.ui.aSaveLastCfg = self.menuDebug.addAction("Save lastuicfg"+outExt.cfg)
        self.ui.aSaveLastCfg.triggered.connect(self.save_lastcfg)

        self.ui.aDeleteLastCfg = self.menuDebug.addAction("Delete lastuicfg"+outExt.cfg)
        def delete_lastcfg():
            os.remove(lastcfgname)
            pri.Info.white(f'    xxxxx Deleting last ui configuration file:\t{lastcfgname}')
        self.delete_lastcfg=delete_lastcfg
        self.ui.aDeleteLastCfg.triggered.connect(delete_lastcfg)

        #--------------------------- printings
        self.menuDebug.addSeparator()
        self.ui.printMenu=self.menuDebug.addMenu('Print')
        printTypes_list=list(self.GPApar.printTypes)
        printActions=[]
        def setPrint(name,act,k):
            flag=act.isChecked()
            self.GPApar.printTypes[name]=flag
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
            flag=self.GPApar.printTypes[name]
            act.setChecked(flag)
            setPrint(name,act,k)
            act.triggered.connect(genCallback(name,act,k))

        #--------------------------- operation
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
            self.ui.aKill = self.menuDebug.addAction("Stop processes and close")
            def aKill():
                self.FlagClosing[0]=True
                self.signals.killOrResetParForWorker.emit(True)
            self.aKill=aKill
            self.ui.aKill.triggered.connect(aKill)

            self.ui.aFocusWid = self.menuDebug.addAction("Print widget with focus")
            def aFocusWid():
                pri.General.yellow(f"The widget with focus is:   {self.focusWidget()}")
            self.aCheckConnections=aFocusWid
            self.ui.aFocusWid.triggered.connect(aFocusWid)

            self.ui.aPrintListImages = self.menuDebug.addAction("Print list of image pairs")
            def aPrintListImages():
                pri.General.white(f"{self.w_Import.INPpar.pinfo.root}:")
                for i in range(self.w_Import.ui.list_images.count()):
                    item=self.w_Import.ui.list_images.item(i)
                    pri.General.white(f"   {item.text()}")
            self.aPrintListImages=aPrintListImages
            self.ui.aPrintListImages.triggered.connect(aPrintListImages)

            self.ui.aCheckConnections = self.menuDebug.addAction("Check tree data connections")
            def aCheckConnections():
                tree,_=self.w_Tree.pickTree(self.w_Tree.TREpar.indTree)
                d=tree.currentItem().data(0,Qt.UserRole)
                data=self.w_Tree.TABpar_prev[d.indTree][d.indItem][self.w_Tree.TABpar.ind] #!!!GP d.ind?
                INP=self.w_Import.TABpar_prev[d.indTree][d.indItem][self.w_Tree.TABpar.ind] #!!! d.ind?

                pri.General.yellow('Setting dummy_name field:')
                setattr(data.INP,'dummy_name',str(uuid.uuid4())[:8])
                pri.General.yellow(f'   data.INP.dummy_name = {data.INP.dummy_name}')
                setattr(INP,'dummy_name',str(uuid.uuid4())[:8])
                pri.General.yellow(f'        INP.dummy_name = {INP.dummy_name}')
                pri.General.yellow(f'-> data.INP.dummy_name = {data.INP.dummy_name}')


                data.INP.dummy_name=str(uuid.uuid4())[:8]
                pri.General.yellow(f'changing >>> data.INP.dummy_name = {data.INP.dummy_name}')
                pri.General.yellow(f'                  INP.dummy_name = {INP.dummy_name}')

                INP.dummy_name=str(uuid.uuid4())[:8]
                pri.General.yellow(f'changing >>>      INP.dummy_name = {INP.dummy_name}')
                pri.General.yellow(f'             data.INP.dummy_name = {data.INP.dummy_name}')
            self.aCheckConnections=aCheckConnections
            self.ui.aCheckConnections.triggered.connect(aCheckConnections)

        #--------------------------- Save PIV cfg
        self.menuDebug.addSeparator()
        self.ui.aSaveCfgPIV=self.menuDebug.addAction("Save PIV cfg")
        def aSaveCfgPIV():
            tree,_=self.w_Tree.pickTree(self.w_Tree.TREpar.indTree)
            d=tree.currentItem().data(0,Qt.UserRole)
            data:dataTreePar=self.w_Tree.TABpar_prev[d.indTree][d.indItem][self.w_Tree.TABpar.ind] #!!!GP d.ind?
            data.writeCfgProcPiv()
            
        self.aSaveCfgPIV=aSaveCfgPIV
        self.ui.aSaveCfgPIV.triggered.connect(aSaveCfgPIV)
        
        #--------------------------- graphics
        if Flag_fullDEBUG:
            self.menuDebug.addSeparator()

            self.ui.aUndock = self.menuDebug.addAction("Undock a widget")
            self.ui.aUndock.triggered.connect(self.extractWidget)

            self.ui.aLogo = self.menuDebug.addAction("Change PaIRS logo")
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
        words = ["self.w_Import", "self.w_Export", 
        "self.w_Process", 
        "self.w_Process.ui.CollapBox_IntWind",
        "self.w_Process.ui.CollapBox_FinIt",
        "self.w_Process.ui.CollapBox_top",
        "self.w_Process.ui.CollapBox_Interp",
        "self.w_Process.ui.CollapBox_Validation",
        "self.w_Process.ui.CollapBox_Windowing",
        "self.w_Vis","self.w_Vis.ui.CollapBox_PlotTools", 
        "self.ui.w_Managing_Tabs","self.w_Tree",
        "self.w_Log","self.ui.w_Buttons",
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
        self.setGPaIRSTitle()
        self.menuDebug.menuAction().setVisible(Flag)

#***************************************************************************************************
#               TREE functions 
#***************************************************************************************************

#*************************************************** Addition of process to past queue
    def addItemToPast(self,data,icon,flagSelection):
        self.w_Tree.TABpar.copyfrom(data)
        self.w_Tree.addNewItem2TreeQueue(1,data.itemname,icon,flagSelection)
        #self.w_Tree.selectCurrent()
        return

    def loadPastProc(self):
        filename, _ = QFileDialog.getOpenFileName(self,\
                "Select an image file of the sequence", filter=f'*{outExt.min}; *{outExt.piv}',\
                    dir=self.w_Import.INPpar.path,\
                    options=optionNativeDialog)
        if not filename: return
        try:
            with open(filename, 'rb') as file:
                data:dataTreePar = pickle.load(file)
                FlagAlreadyInQueue=False
                dirname=os.path.dirname(filename)
                for k in range(len(data.filename_proc)):
                    if data.filename_proc[k]:
                        data.filename_proc[k]=data.filename_proc[k].replace(os.path.dirname(data.filename_proc[k]),dirname)
                data.OUT.path=data.VIS.Out.path=myStandardPath(dirname)
                data.OUT.subfold=data.VIS.Out.subfold=''
                for n,i in enumerate(self.w_Tree.TREpar.past):
                    ido=i.data(0,Qt.UserRole) #idata_old
                    data_old=self.w_Tree.TABpar_prev[ido.indTree][ido.indItem][-1] #!!!GP ido.ind?
                    FlagAlreadyInQueue=data.name_proc[data.typeProc]==data_old.name_proc[data_old.typeProc]
                    if FlagAlreadyInQueue: break
                if not FlagAlreadyInQueue:
                    for wn,pn in zip(self.TABnames[:-1],self.TABParDataNames[:-1]):
                        w=getattr(self,'w_'+wn)
                        w.TABpar.copyfrom(getattr(data,pn))
                    self.w_Tree.TABpar.copyfrom(data)
                    self.w_Tree.addNewItem2TreeQueue(-1,data.itemname,QIcon(),True)
                    data_new=self.w_Tree.TABpar_prev[-1][-1][-1]
                    data.printDifferences(data_new)
                    pass
                else:
                    WarningMessage=f'The selected process is already in the past queue (process #{n+1})!'
                    warningDialog(self,WarningMessage)
                    self.w_Tree.selectPast(n)
        except Exception as inst:
            pri.Error.red(f'Error while loading past process:\n{traceback.print_exc()}\n\n{inst}\n')
            return

#*************************************************** Addition of process to future queue
    def addProc(self,typeProc):
        if self.FlagButtProcRun[typeProc]: #addProc turned to Run button
            self.button_RunPause_callback()
            return
        OUT=self.w_Export.OUTpar
        FlagValidInput=all([self.w_Import.ui.list_images.isEnabled,\
            self.w_Import.INPpar.FlagValidPath,self.w_Import.INPpar.FlagValidRoot])
        FlagValid=all([FlagValidInput,\
            OUT.FlagValidPath,OUT.FlagValidSubFold,OUT.FlagValidRoot,\
            ])
        if FlagValid:
            self.addProcItem(typeProc)
        else:           
            n=sum([int(not f) for f in [FlagValidInput,OUT.FlagValidPath,OUT.FlagValidSubFold,OUT.FlagValidRoot]])
            nMess=n
            def addstop(mess,n):
                if n==nMess and n>1: mess+='!\n\nFurthermore:\n- '
                elif n>1: mess+=';\n- '
                else: mess+='.'
                n-=1
                return mess, n
            
            Message="Please, "
            if not FlagValidInput:
                Message+="select a valid set of images to process"
                Message,n=addstop(Message,n)    
            if not OUT.FlagValidPath:
                Message+="choose a valid output folder path"
                Message,n=addstop(Message,n)
            if not OUT.FlagValidSubFold:
                Message+="choose a valid output subfolder path"
                Message,n=addstop(Message,n)
            if not OUT.FlagValidRoot:
                Message+="choose a valid root of the output filename"
                Message,n=addstop(Message,n)
            warningDialog(self,Message)
    
#********************************** Create New Items 
    def addProcItem(self,typeProc,*args):
        if args:
            data=args[0]
            FlagExistProc=args[1]
            WarningMessage=args[2]
            icon=args[3]
        else:
            data=self.createProc(typeProc)
            if data.typeProc==dataTreePar.typeMIN:
                FlagExistProc, WarningMessage, icon=self.warningFutureMinProc(data,[],True,True)
            elif data.typeProc==dataTreePar.typePIV:
                FlagExistProc, WarningMessage, icon=self.warningFuturePivProc(data,[],True,True)
        if FlagExistProc<0:
            self.addItemToFuture(data,icon,True)
        else:
            self.moveToExistingItem(FlagExistProc,WarningMessage)              

    def createProc(self,typeProc):
        data=dataTreePar(typeProc)
        data.INP.copyfrom(self.w_Import.INPpar)
        data.OUT.copyfrom(self.w_Export.OUTpar)
        data.PRO.copyfrom(self.w_Process.PROpar)
        data.VIS.copyfrom(self.w_Vis.VISpar)
        data.freset_par='w_Import'

        data.setProc()
        data.assignDataName()

        data.indTree=1
        data.indItem=len(self.w_Tree.TREpar.future)
        return data    

    def warningFutureMinProc(self,data:dataTreePar,item:QTreeWidgetItem,FlagDispWarning,FlagDispDummyWarning):
        FlagExistMin=-2
        WarningMessage=''
        icon=self.Tree_icons.waiting
        data.icon_type=self.Tree_icons.icontype('waiting')
        Flag=False
        for n,i in enumerate(self.w_Tree.TREpar.future):
            i:QTreeWidgetItem
            idatai:TABpar=i.data(0,Qt.UserRole)
            datai:dataTreePar=self.w_Tree.TABpar_prev[idatai.indTree][idatai.indItem][-1]
            if datai.typeProc!=data.typeProc or (datai.indTree==data.indTree and datai.indItem==data.indItem): 
                continue
            else:
                if data.isEqualTo(datai,data.item_fields+data.procfields,[],True):
                    FlagExistMin=n
                    WarningMessage=''
                elif datai.filename_proc[dataTreePar.typeMIN]==data.filename_proc[dataTreePar.typeMIN]:
                    #data.printDifferences(datai,data.item_fields+data.procfields,[],True)
                    FlagExistMin=n
                    WarningMessage='A pre-processing computation with the same output path (folder and root name) but different settings exists in the queue.'+f'\nPlease, change the output path or delete the process #{n+1}.'
            Flag=WarningMessage or FlagExistMin>=0
            if Flag: break
        if not Flag:
            if os.path.exists(data.filename_proc[dataTreePar.typeMIN]):
                WarningMessage='Output files for the pre-processing computation with the same path already exist! They will be overwritten.'           
                data.warnings[0]='- Output files with the same output path (folder and root name) but different settings existed when the pre-processing computation was launched and were overwritten.\n'  
                FlagExistMin=-1
        if WarningMessage:
            icon=self.Tree_icons.issue
            data.icon_type=self.Tree_icons.icontype('issue')
            data.warnings[1]=WarningMessage
            if FlagDispWarning:
                warningDialog(self,WarningMessage)
        else:
            if FlagExistMin>=0 and FlagDispDummyWarning:
                info=f'Pre-processing computation already present in the future queue! [#{n+1}]'
                warningDialog(self,info)
        if item: 
            item.setIcon(0,icon)
            self.setItemTips(item,data)
        data.setCompleteLog()
        return FlagExistMin, WarningMessage, icon
        #else:
        #    self.addItemToFuture(data,icon,flagSelection)
    
    def warningFuturePivProc(self,data:dataTreePar,item:QTreeWidgetItem,FlagDispWarning,FlagDispMinWarning):
        FlagExistMin=-2
        FlagExistMean=-2
        WarningMessage=''
        warn0=''
        icon=self.Tree_icons.waiting
        data.icon_type=self.Tree_icons.icontype('waiting')
        Flag=False
        for n,i in enumerate(self.w_Tree.TREpar.future):
            i:QTreeWidgetItem
            idatai:TABpar=i.data(0,Qt.UserRole)
            datai=self.w_Tree.TABpar_prev[idatai.indTree][idatai.indItem][-1]
            if datai.typeProc!=data.typeProc or (datai.indTree==data.indTree and datai.indItem==data.indItem): 
                continue
            else:
                if data.isEqualTo(datai,data.item_fields+data.procfields,[],True):
                    WarningMessage=''
                    FlagExistMean=n
                elif datai.filename_proc[dataTreePar.typePIV]==data.filename_proc[dataTreePar.typePIV]:
                    #data.printDifferences(datai,data.item_fields+data.procfields,[],True)
                    WarningMessage='A PIV process with the same output path (folder and root name) but different settings exists in the queue.'+f'\nPlease, change the output path or delete the process #{n+1}.'
                    FlagExistMean=n
            Flag=WarningMessage or FlagExistMean>=0
            if Flag: break
        if not Flag: 
            if data.INP.flag_min:
                data2:dataTreePar=data.duplicate()
                data2.typeProc=dataTreePar.typeMIN
                FlagExistMin, WarningMessage, icon_min=self.warningFutureMinProc(data2,item,False,False)
                if FlagExistMin==-2:   #il processo di min non esiste
                    """
                    if FlagCreateMinProc:  #se vuoi crearlo, nessun problema, lo crei visualizzando il warning corrispondente
                        data2.name='itemTREEpar:MinProc'
                        data2.filename_proc[dataTreePar.typePIV]=""
                        data2.filename_proc[dataTreePar.typeMIN]=f"{data.outPathRoot}{outExt.min}"
                        data2.itemname=f"Minimum computation ({data2.filename_proc[data2.typeProc]})"
                        data2.Log=self.w_Log.logHeader(f'{data2.itemname}\n\n{WarningMessage}\n\n')
                        
                        self.addProcItem(data2.typeProc,data2,FlagExistMin,WarningMessage,icon_min)

                        warningDialog(self,WarningMessage)
                        WarningMessage=''
                        data.indItem+=1
                    else:  #se non vuoi crearlo, warning sul fatto che dovresti crearlo
                        WarningMessage='A corresponding pre-processing computation is not found in the queue.\nPlease add it, before the PIV process!'
                        data.warnings[0]='- A corresponding pre-processing computation was not present in the queue upstream of the current PIV process when it was launched.\n'
                    """
                    WarningMessage='A corresponding pre-processing computation is not found neither in the queue nor in the disk.\nPlease add it, before the PIV process!'
                    data.warnings[0]='- A corresponding pre-processing computation was not present in the queue nor in the disk of the current PIV process when it was launched.\n'
                elif FlagExistMin>=-1 and FlagExistMin<data.indItem: #il processo di minimo esiste prima di quello che stai valutando
                    FlagErr=False
                    if FlagExistMin==-1:
                        filename_preproc=data.filename_proc[dataTreePar.typeMIN]
                        try:
                            with open(filename_preproc, 'rb') as file:
                                datai:dataTreePar=pickle.load(file)
                            WarningMessage=f'A corresponding pre-processing computation is found in the disk.\n'
                            warn0=f'- A corresponding pre-processing computation was found in the disk when the current PIV process was launched. '
                        except Exception as inst:
                            pri.Error.red(f'Error while opening saved pre-process {filename_preproc}:\n{traceback.print_exc()}\n\n{inst}\n')
                            WarningMessage='A corresponding pre-processing computation is found in the disk. However, there were problems with openining it.\nPlease add a new pre-process to the future queue, before the PIV process!'
                            data.warnings[0]='- A corresponding pre-processing computation was present in the disk when the current PIV process was launched. However, there were problems with openining it.\n'
                            FlagErr=True
                    else:
                        datai:dataTreePar=self.w_Tree.TABpar_prev[data.indTree][FlagExistMin][-1]
                        WarningMessage=f'A corresponding pre-processing computation is found in the queue (process #{FlagExistMin+1}).\n'
                        warn0=f'- A corresponding pre-processing computation was found in the queue upstream of the current PIV process when it was launched. '
                    if not FlagErr:
                        exc=['ind','indItem','indTree','compMin','mediaPIV']
                        if data.INP.isDifferentFrom(datai.INP,exc,['pinfo']):
                            WarningMessage+=f'However, it is related to a different set of image pairs: {datai.INP.path}{datai.INP.root}.'
                            warn0+=f'However, it was related to a different set of image pairs: {datai.INP.path}{datai.INP.root}.'
                        else:
                            nWarn=0
                            ind_in_preproc=datai.INP.range_from
                            ind_fin_preproc=ind_in_preproc+datai.INP.range_to*int(2/(1+1*(bool(datai.INP.flag_TR))))
                            range_preproc=f'({ind_in_preproc}-{ind_fin_preproc})'
                            ind_in=data.INP.range_from
                            ind_fin=ind_in+data.INP.range_to*int(2/(1+1*(bool(data.INP.flag_TR))))
                            range_proc=f'({ind_in}-{ind_fin})'
                            if range_preproc!=range_proc:
                                WarningMessage+=f'However, the range of image pairs {range_preproc} is different from that of the PIV process {range_proc}.\n'
                                warn0+=f'However, the range of image pairs {range_preproc} was different from that of the current PIV process {range_proc}. '
                                nWarn+=1
                            """"
                            if data.OUT.isDifferentFrom(datai.OUT,exc,['x','y','w','h','bimop']):
                                if not nWarn: 
                                    WarningMessage+=f'However, '
                                    warn0+=f'However, '
                                elif nWarn: 
                                    WarningMessage+=f'\nFurthermore, '
                                    warn0+=f' Furthermore, '
                                WarningMessage+=f'the image flip/rotation operations made in the pre-process are different from those specified in the PIV process.'
                                warn0+='the image flip/rotation operations made in the pre-process were different from those specified in the PIV process.'
                                nWarn+=1
                            """
                            if not nWarn:
                                WarningMessage=''  #WarningMessage from warningFutureMinProc could be not empty
                                warn0=''
                            else:
                                warn0+='\n'
                if FlagDispMinWarning and WarningMessage:
                    warningDialog(self,WarningMessage)
                    WarningMessage=''
                    data.indItem+=1            
                elif FlagExistMin>data.indItem: #il processo esiste ma è successivo alla PIV: warning->spostalo; FlagCreateMinProc è sicuramente False
                    WarningMessage=f'A corresponding pre-processing computation has been found in the queue (process #{FlagExistMin+1}).\nHowever, it follows the PIV process.\nPlease change the queue order!'
                    data.warnings[0]='- A corresponding pre-processing computation was not present in the queue upstream of the current PIV process when it was launched.\n'
            if os.path.exists(data.filename_proc[dataTreePar.typePIV]):
                if WarningMessage: WarningMessage+='\n\n'
                WarningMessage+='Output files for the PIV process with the same path already exist! They will be overwritten.'
                warn0+='- Output files with the same output path (folder and root name) but different settings existed when the PIV computation was launched and were overwritten\n'
                FlagExistMean=-1
        if WarningMessage:
            icon=self.Tree_icons.issue
            data.icon_type=self.Tree_icons.icontype('issue')
            data.warnings[1]=WarningMessage
            data.warnings[0]=warn0
            if FlagDispWarning:
                warningDialog(self,WarningMessage)  
        else:
            if FlagExistMean>=0 and FlagDispWarning:
                info=f'PIV process already present in the future queue! [#{n+1}]'  
                warningDialog(self,info)
        if item: 
            item.setIcon(0,icon)
            self.setItemTips(item,data)
        data.setCompleteLog()
        return FlagExistMean, WarningMessage, icon
    
    def addItemToFuture(self,data:dataTreePar,icon,flagSelection):
        self.w_Tree.TABpar.copyfrom(data)
        self.w_Tree.addNewItem2TreeQueue(1,data.itemname,icon,flagSelection)
        #self.w_Tree.selectCurrent()
        return
    
    def moveToExistingItem(self,n,message):
        if n>-1:
            self.w_Tree.FlagAddPrev=False
            self.w_Tree.selectFuture(n)
            self.w_Tree.FlagAddPrev=True
        if message:
            tip=QToolTip(self)
            toolTipDuration=self.toolTipDuration()
            self.setToolTipDuration(3000)
            tip.showText(QCursor.pos(),message)
            self.setToolTipDuration(toolTipDuration)

#************************************************ Addition of items to and handling of trees       
    def addNewItem2Prevs(self,indTree,indItem_new):
        indTreeGlob_old=gPaIRS_Tab.indTreeGlob
        indItemGlob_old=gPaIRS_Tab.indItemGlob
        FlagGlobalAdd=gPaIRS_Tab.FlagGlob
        for tnames in self.TABnames:
            w: gPaIRS_Tab
            wname='w_'+tnames
            w=getattr(self,wname)
            w.TABpar_prev[indTree].append([])
            w.FlagAddingPar[indTree].append([])
            w.FlagAsyncCall[indTree].append([])
        gPaIRS_Tab.FlagGlob=True
        gPaIRS_Tab.indTreeGlob=indTree
        gPaIRS_Tab.indItemGlob=indItem_new
        self.w_Tree.add_TABpar(f'new process added to {self.w_Tree.QueueNames[indTree]}')
        #self.w_Tree.add_TABpar_bridge()
        gPaIRS_Tab.FlagGlob=FlagGlobalAdd
        gPaIRS_Tab.indTreeGlob=indTreeGlob_old
        gPaIRS_Tab.indItemGlob=indItemGlob_old
        if indTree==-1: self.checkPastProc()
        elif indTree==1: self.checkFutureProc()

    def addExistingItem2Prevs(self,indTree_old,indItem_old,indTree,indItem_new):
        for tnames in self.TABnames:
            w: gPaIRS_Tab
            wname='w_'+tnames
            w=getattr(self,wname)
            w.TABpar_prev[indTree].append(w.TABpar_prev[indTree_old][indItem_old])
            w.FlagAddingPar[indTree].append(w.FlagAddingPar[indTree_old][indItem_old])
            w.FlagAsyncCall[indTree].append(w.FlagAsyncCall[indTree_old][indItem_old])
            for p in w.TABpar_prev[indTree][indItem_new]:
                p.indTree=indTree
                p.indItem=indItem_new
        if indTree==-1: self.checkPastProc()
        elif indTree==1: self.checkFutureProc()
        return
    
    def removeItemFromPrevs(self,indTree,indItem):
        ind=self.w_Tree.TABpar.indexes()
        FlagSelect=False
        if len(self.w_Tree.TABpar_prev[ind[0]]):
            if len(self.w_Tree.TABpar_prev[ind[0]][ind[1]]):
                data_sel=self.w_Tree.TABpar_prev[ind[0]][ind[1]][ind[2]]
                FlagSelect=True
        for tnames in self.TABnames:
            w: gPaIRS_Tab
            wname='w_'+tnames
            w=getattr(self,wname)
            w.TABpar_prev[indTree].pop(indItem)
            w.FlagAddingPar[indTree].pop(indItem)
            w.FlagAsyncCall[indTree].pop(indItem)
            for k in range(indItem,len(w.TABpar_prev[indTree])):
                for p in w.TABpar_prev[indTree][k]:
                    p.indItem=k
        if FlagSelect:
            newInd=data_sel.indexes()
            self.w_Tree.TABpar.indTree=newInd[0]
            self.w_Tree.TABpar.indItem=newInd[1]
            self.w_Tree.TABpar.ind=newInd[2]
        if indTree==1 and len(self.w_Tree.TREpar.future): self.checkFutureProc()
        return

    def moveupdownPrevs(self,indTree,indItem,d):
        ind=self.w_Tree.TABpar.indexes()
        FlagSelect=False
        if len(self.w_Tree.TABpar_prev[ind[0]]):
            if len(self.w_Tree.TABpar_prev[ind[0]][ind[1]]):
                data_sel=self.w_Tree.TABpar_prev[ind[0]][ind[1]][ind[2]]
                FlagSelect=True
        for tnames in self.TABnames:
            w: gPaIRS_Tab
            wname='w_'+tnames
            w=getattr(self,wname)
            q=w.TABpar_prev[indTree]
            q.insert(indItem+d,q.pop(indItem))
            for k in range(min([indItem+d,indItem]),len(q)):
                qk=q[k]
                for p in qk:
                    p.indItem=k
            q=w.FlagAddingPar[indTree]
            q.insert(indItem+d,q.pop(indItem))
            q=w.FlagAsyncCall[indTree]
            q.insert(indItem+d,q.pop(indItem))
        if FlagSelect:
            newInd=data_sel.indexes()
            self.w_Tree.TABpar.indTree=newInd[0]
            self.w_Tree.TABpar.indItem=newInd[1]
            self.w_Tree.TABpar.ind=newInd[2]
        self.checkFutureProc()
        self.w_Tree.selectTree(indTree,indItem+d) 

    def checkPastProc(self,*args):
        if len(args): ra=[args[0]]
        else: ra=range(0,len(self.w_Tree.TREpar.past))
        for n in ra:
            i:QTreeWidgetItem=self.w_Tree.TREpar.past[n]
            idata:TABpar=i.data(0,Qt.UserRole)
            ind=-1 #idata.ind
            data:dataTreePar=self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][ind]
            filename=data.filename_proc[data.typeProc]
            if data.flagRun!=0:
                Flag=os.path.exists(filename) 
                if Flag:
                    try:
                        with open(filename, 'rb') as file:
                            data_stored:dataTreePar = pickle.load(file)
                        Flag=data_stored.name_proc[data.typeProc]==data.name_proc[data.typeProc]
                        WarningMessage='The selected process is out of date!\nIt would be better to remove it from the queue.'
                    except Exception as inst:
                        pri.Error.red(f'checkPastProc: reading filename #{i}:' + str(inst.__cause__))
                        data_stored=None
                        Flag=False
                        WarningMessage='There were errors with opening files related to this process.\n'+\
                            'The files might be corrupted or perhaps they were generated with an old version of PaIRS.'
                else:
                    WarningMessage='Files related to this process are not available!'
                if not Flag: 
                    data.icon_type=self.Tree_icons.icontype('missing')
                    i.setIcon(0,self.Tree_icons.missing)
                    data.warnings[1]=WarningMessage
                    data.flagRun=data.VIS.Tre.flagRun=-2
                else:
                    if data.flagRun==-1:
                        data.icon_type=self.Tree_icons.icontype('cancelled')
                        i.setIcon(0,self.Tree_icons.cancelled)
                    elif data.flagRun==1:
                        data.icon_type=self.Tree_icons.icontype('done')
                        i.setIcon(0,self.Tree_icons.done)
                    elif data.flagRun==2:
                        data.icon_type=self.Tree_icons.icontype('completed')
                        i.setIcon(0,self.Tree_icons.completed)
            else:
                data.icon_type=self.Tree_icons.icontype('trash')
                i.setIcon(0,self.Tree_icons.trash)
            self.setItemTips(i,data)
            data.setCompleteLog()

    def checkFutureProc(self):
        for i in self.w_Tree.TREpar.future:
            i:QTreeWidgetItem
            idata:TABpar=i.data(0,Qt.UserRole)
            data:dataTreePar=self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][-1]
            if not data.flagRun:
                data.setProc()
                if data.typeProc==dataTreePar.typeMIN:
                    self.warningFutureMinProc(data,i,False,False)
                if data.typeProc==dataTreePar.typePIV:
                    self.warningFuturePivProc(data,i,False,False)
            else:
                data.icon_type=self.Tree_icons.icontype('paused')
                i.setIcon(0,self.Tree_icons.paused)
        #self.w_Tree.TABpar.copyfrom(self.w_Tree.TABpar_prev[self.w_Tree.TABpar.indTree][self.w_Tree.TABpar.indItem][self.w_Tree.TABpar.ind])
 
#*************************************************** PROCESS
#********************************** Launching
    def button_RunPause_callback(self):
        pri.Process.magenta(f'button_RunPause_callback self.FlagRun={self.FlagRun}  ')
        self.ui.button_pause.setEnabled(False)#ta disabilitato sempre lo riabilita il worker prima di iniziare
        self.signals.killOrResetParForWorker.emit(self.FlagRun)
        self.FlagRun= not self.FlagRun
        if self.FlagRun:
            self.w_Tree.ui.button_min.hide()
            self.w_Tree.ui.button_PIV.hide()
            self.setButtonPause(False)
            tip="Pause process queue"+' ('+self.ui.button_pause.shortcut().toString(QKeySequence.NativeText)+')'
            self.ui.button_pause.setToolTip(tip)
            self.ui.button_pause.setStatusTip(tip)
            #self.GPApar.FlagInput= False
            #self.GPApar.FlagOutput= False
            #self.GPApar.FlagProcess= False
            #self.setTabLayout()

            #self.w_Tree.ui.tree_current.setEnabled(False)
            #self.w_Tree.ui.tree_past.setEnabled(False)
            #self.w_Tree.ui.button_import_past.setEnabled(False)
            if Flag_RESIZEONRUN==1: 
                self.BSizeCallbacks[4]()
            elif Flag_RESIZEONRUN==2:
                if self.GPApar.FlagLog: self.moveToTab('Log')
                elif self.GPApar.FlagVis: self.moveToTab('Vis')
            self.run()
        else:
            self.w_Tree.ui.button_min.show()
            self.w_Tree.ui.button_PIV.show()
            self.setButtonPause(True)
            tip="Restart process queue"+' ('+self.ui.button_pause.shortcut().toString(QKeySequence.NativeText)+')'
            self.ui.button_pause.setToolTip(tip)
            self.ui.button_pause.setStatusTip(tip)
            self.w_Tree.ui.tree_past.setEnabled(True)
            self.w_Tree.ui.tree_current.setEnabled(True)
            self.w_Tree.ui.tree_past.setEnabled(True)
            self.w_Tree.ui.button_import_past.setEnabled(True)
            self.ui.button_Run.setEnabled(False)  
    
    def run(self):
        if self.w_Tree.ui.button_edit_item.isChecked():
            self.w_Tree.ui.button_edit_item.setChecked(False)
            self.button_edit_item_callback()
        self.contProc=0
        self.nProc=len(self.w_Tree.TREpar.future)
        self.ui.button_pause.show()
        self.ui.w_progress_Proc.show()
        self.ui.button_Run.hide()
        self.ui.label_updating_pairs.setVisible(True)
        self.initializeWorkers()
        self.indProc=-1
        data_sel=self.w_Tree.TABpar
        self.setButtons(data_sel)
        self.updateIndProc()
    
    def updateIndProc(self):
        i=self.w_Tree.TREpar.future[0]
        idata=i.data(0,Qt.UserRole)
        for wname in self.TABnames:
            w=getattr(self,'w_'+wname)
            w.cleanPrevs(idata.indTree,idata.indItem)
        idata.ind=0
        data:dataTreePar
        self.procdata=data=self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][idata.ind]#.duplicate()
        self.procdata.uncopied_fields+=self.procFields

        self.resetProc(data)
        self.setProgressBar(data)
        data.resetLog()
        self.w_Log.moveToBottom()
        data.flagRun=data.VIS.Tre.flagRun=-2  #come ultimo o comunque dopo resetProc
        
        #self.w_Tree.selectFuture(0)

        i.setIcon(0,self.Tree_icons.running)
        self.indProc+=1
        self.FlagProcInit=True
        self.signals.indProc.emit(self.indProc)
        if  data.flagRun==0:#not launched
          data.resetTimeStat() 
        data.onStartTimeStat()

    def nextProc(self):
        self.UpdatingImage=True
        i=self.w_Tree.TREpar.future[0] #.currentItem()
        idata=i.data(0,Qt.UserRole)
        data=self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][-1]
        self.w_Tree.TREpar.flagRun=data.flagRun
        flagSelected=data.hasIndexOf(self.w_Tree.TABpar)
        self.w_Tree.removeFromCurrentTree(False,self.w_Tree.TREpar.future[0])
        #self.w_Tree.removeFromCurrentTree(False) #no selection, it is already selected
        #self.checkPastProc()

        if len(self.w_Tree.TREpar.future) and self.FlagRun:
            if flagSelected:
                self.w_Tree.selectFuture(0)
            else:
                data_sel=self.w_Tree.TABpar
                self.setButtons(data_sel)
            self.updateIndProc()
        else:
            self.button_RunPause_callback()
            ##self.w_Tree.selectCurrent()
            if flagSelected:
                self.w_Tree.selectPast()
            else:
                data_sel=self.w_Tree.TABpar
                self.setButtons(data_sel)

    def resetProc(self,data:dataTreePar):
        if not data.flagRun and data.typeProc==dataTreePar.typePIV and data.INP.flag_min:
            filename_preproc=data.filename_proc[dataTreePar.typeMIN]   
            if not os.path.exists(filename_preproc):      
                data.warnings[1]+='A corresponding pre-processing computation is not found in the disk.\n'
                data.warnings[0]+='- A corresponding pre-processing computation was not present in the disk when the current PIV process was launched. The process was executed on raw images.\n'
                data.filename_proc[dataTreePar.typeMIN]=''
                data.INP.flag_min=False
            else:                   
                try:
                    with open(filename_preproc, 'rb') as file:
                        data_preproc:dataTreePar=pickle.load(file)
                    exc=['ind','indItem','indTree','compMin','mediaPIV']
                    if data.INP.isDifferentFrom(data_preproc.INP,exc,['pinfo']):
                        data.warnings[1]+=f'However, it is related to a different set of image pairs: {data_preproc.INP.path}{data_preproc.INP.root}.'
                        data.warnings[0]+=f'However, it was related to a different set of image pairs: {data_preproc.INP.path}{data_preproc.INP.root}.'
                    data.compMin=data_preproc.compMin
                    data.filename_proc[dataTreePar.typeMIN]=data_preproc.filename_proc[dataTreePar.typeMIN]
                    data.name_proc[dataTreePar.typeMIN]=data_preproc.name_proc[dataTreePar.typeMIN]
                    pri.Info.yellow(f'Loading and setting preproc files for process {data.filename_proc[dataTreePar.typePIV]}')
                except Exception as inst:
                    pri.Error.red(f'Error while opening saved pre-process {filename_preproc}:\n{traceback.print_exc()}\n\n{inst}\n')
                    data.warnings[1]+='A corresponding pre-processing computation is found in the disk. However, there were problems with openining it.\n'
                    data.warnings[0]+='- A corresponding pre-processing computation was present in the disk when the current PIV process was launched. However, there were problems with openining it. The process was executed on raw images.\n'
                    data.filename_proc[dataTreePar.typeMIN]=''
                    data.INP.flag_min=False
                    
        data.flagParForCompleted=False
        data.numCallBackTotOk=data.numFinalized
        self.signals.progress.emit(data.numFinalized)
        data.numProcOrErrTot=0
        self.procWorkers[self.indProc+1].data=data
        self.ui.time_stamp.hide()
        return

    def setProgressBar(self,data:dataTreePar):
        self.ui.progress_Proc.setMinimum(0)
        self.ui.progress_Proc.setMaximum(data.nimg)
        self.ui.progress_Proc.setValue(data.numFinalized) 
        return
        
#********************************** Initialization of workers
    def initializeWorkers(self):
        self.indWorker=-1
        self.indProc=-1
        future=self.w_Tree.TREpar.future
        while self.pfPool is None:
          #TBD  serve lo sleep? Se non ci sono errori cancellare
          pri.Error.white('****************\n****************\n****************\nwhile self.pfPool is None\n****************\n****************\n******************\n')
          if Flag_DEBUG: 1/0
          sleep(0.5)
        self.procWorkers=[]
        for i in future:
            i:QTreeWidgetItem
            self.indWorker+=1
            idata:TABpar=i.data(0,Qt.UserRole)
            data=self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][-1]
            self.initialize_proc(data)

    def initialize_proc(self,data:dataTreePar):
        currpath=myStandardPath(data.OUT.path+data.OUT.subfold)
        if not os.path.exists(currpath): 
            try:
                os.mkdir(currpath)
            except Exception as inst:
                pri.Error.red(f'It was not possible to make the output folder:\n{traceback.print_exc}\n\n{inst}')

        if data.typeProc==dataTreePar.typeMIN:
            procWorker=MIN_ParFor_Worker(data,self.indWorker,self.indProc,self.numUsedThreadsPIV,self.pfPool,self.parForMul)
        else:
            procWorker=PIV_ParFor_Worker(data,self.indWorker,self.indProc,self.numUsedThreadsPIV,self.pfPool,self.parForMul)
            
        procWorker.signals.progress.connect(self.progress_proc)
        self.signals.progress.connect(procWorker.setNumCallBackTot)
        procWorker.signals.finished.connect(self.pause_proc)
        procWorker.signals.initialized.connect(self.buttonPauseHideShow)
        procWorker.signals.completed.connect(self.stopProcs)
        self.signals.pause_proc.connect(procWorker.storeCompleted) 
        #self.ui.button_pause.clicked.connect(MIN_worker.die)
        self.signals.killOrResetParForWorker.connect(procWorker.killOrReset)
        self.signals.indProc.connect(procWorker.updateIndProc) 
        self.FlagInitialized=True
        self.procWorkers.append(procWorker)
        self.PaIRS_threadpool.start(procWorker)
            
#********************************** Progress
    @Slot(int,int,int,list,str)
    def progress_proc(self,procId,i,pim,Var,stampa):
        ''' E' la funzione chiamata alla fine di ogni elaborazione dai vari threads in parfor è chiamata wrapUp CallBack'''
        data=self.procdata
        #******************** Updating total number of tasks passed to the pool
        data.numProcOrErrTot+=1
        #pri.Time.blue(0,f'progress_proc start i={i} pim={hex(pim)} {"*"*25}   {procId}  FlagRun={self.FlagRun}')
        
        if i<0:  return  #When restarting a process return  immediately if the images have been already processed
        #******************** Updating Log
        data.Log+=stampa

        data.list_print[i]=stampa
        data.list_pim[i]=pim

        if not pim&FLAG_CALLBACK_INTERNAL: return   #c'è un errore prima della fine di tutti i processi relativi ad i
        #******************** Updating Progress Bar
        data.numCallBackTotOk+=1 #Always at the end the progress bar will go back to the correct value
        self.signals.progress.emit(data.numCallBackTotOk) #fundamental in multithreading

        if self.FlagRun: 
            self.ui.progress_Proc.setValue(data.numProcOrErrTot)
        else:
            self.ui.progress_Proc.setValue(data.numFinalized)
        
        flagSelected=data.hasIndexOf(self.w_Tree.TABpar)

        if flagSelected:
            if self.FlagRun: 
                self.w_Log.ui.progress_Proc.setValue(data.numProcOrErrTot)
            else:
                self.w_Log.ui.progress_Proc.setValue(data.numFinalized)
        
        if data.typeProc==dataTreePar.typeMIN:
            flagFinalized=(pim&FLAG_FINALIZED[0]) and (pim&FLAG_FINALIZED[1])
        elif data.typeProc==dataTreePar.typePIV:
            flagFinalized=pim&FLAG_FINALIZED[0]
        
        if not flagFinalized: return   
        #******************** Updating numFinalized
        data.numFinalized+=1
          
        if data.flagParForCompleted: return
        #******************** updating log
        if flagSelected: 
          #self.w_Log.ui.log.setText(data.Log)
          self.w_Log.logWrite(stampa)
          self.w_Log.moveToBottom()
        
        pri.Process.green(f'progress_proc {i} data.numProcOrErrTot={data.numProcOrErrTot} self.numFinalized={data.numFinalized}')
        # prLock ha smesso di funzionare perchè?
        #prLock(f'progress_proc {i} data.numProcOrErrTot={data.numProcOrErrTot}  self.numCallBackTotOk={self.numCallBackTotOk}')

        if not self.FlagRun or procId%self.numUsedThreadsPIV: return   #evitare aggiornamento tempo
        #if not self.FlagRun : return   #evitare aggiornamento tempo
        #******************** Updating time counter and stats
        actualTime=time()
        self.showTimeToEnd(data,time=actualTime)

        if not Flag_GRAPHICS and not self.w_Vis.VISpar.FlagVis: return 
        if actualTime<self.previousPlotTime+deltaTimePlot: return 
        if not flagSelected: return 
        # fra l'altro mi sembra che queata funzione sia abbastanza onerosa
        #updating plot
        pri.Time.green(f'plotting the field {i} over {data.numProcOrErrTot} ')
        if data.typeProc==dataTreePar.typeMIN: self.plotProgressMIN(Var,data)
        elif data.typeProc==dataTreePar.typePIV: self.plotProgessPIV(Var,data,i)
        try:
            #self.w_Vis.setVISpar()  # plotta 
            if data.hasIndexOf(self.w_Tree.TABpar): #and data.flagRun>-2:
                self.w_Vis.VISpar.copyfrom(data.VIS)
                self.w_Vis.setTABpar_prev(data.indTree,data.indItem,data.ind,True)   
                pri.Process.yellow(f'{"*"*50} Result plotted!')
        except:
            pri.Error.red('Error Plotting in progress_proc',color=PrintTA.red)
        self.previousPlotTime=time()
        return 
        #pri.Time.green(0,f'progress_proc end   i={i} pim={hex(pim)} {"-"*25}   {procId}   FlagRun={self.FlagRun}')

    def showTimeToEnd(self,data:dataTreePar,time=0):
        if data.numCallBackTotOk:
            eta=data.deltaTime2String(data.eta) if time==0 else data.calcTimeStat(time,data.numCallBackTotOk)
        else:
            eta='no info'
        self.ui.time_stamp.show()
        self.ui.time_stamp.setText(f'Time to the end: {eta}')

    def plotProgressMIN(self,Imin,data:dataTreePar):
        if len(Imin):
            self.w_Vis.procimga=Imin[0] 
            if len(Imin[0]): 
                self.w_Vis.getImgInfo(self.w_Vis.VISpar,0,Imin[0]) 
                self.w_Vis.VISpar.FlagErrRead[0]=False
            else:
                self.w_Vis.VISpar.FlagErrRead[0]=True
            self.w_Vis.procimgb=Imin[1] 
            if len(Imin[1]): 
                self.w_Vis.getImgInfo(self.w_Vis.VISpar,1,Imin[1]) 
                self.w_Vis.VISpar.FlagErrRead[1]=False
            else:
                self.w_Vis.VISpar.FlagErrRead[1]=True
            root_min=myStandardRoot(data.OUT.path+data.OUT.subfold+data.OUT.root)+"_"
            self.w_Vis.nameprocimga=root_min+"a_min"+data.INP.pinfo.ext
            self.w_Vis.nameprocimgb=root_min+"b_min"+data.INP.pinfo.ext  
        else:
            self.w_Vis.procimga=self.w_Vis.procimgb=[]
            self.w_Vis.nameprocimga=self.w_Vis.nameprocimgb=''

        if self.FlagProcInit:
            self.FlagProcInit=False
            data.flagRun=data.VIS.Tre.flagRun=-10

            data.VIS.MapVar_type=0
            data.VIS.type=0
            self.w_Vis.setDefaultXLim(data.VIS)
            self.w_Vis.setDefaultCLim(data.VIS)
            data.VIS.FlagReset=[False,False] 
            data.VIS.nfield=data.VIS.Inp.selected=imin_im_pair-1
            self.w_Vis.updateVisfromINP(data.VIS)

            if len(Imin): 
                self.w_Vis.VISpar.nfield=data.VIS.nfield
              
            
        if len(Imin) or data.VIS.nfield==self.w_Vis.VISpar.nfield:
            self.w_Vis.VISpar_old.nfield=imin_im_pair-2
            self.w_Vis.imga=self.w_Vis.procimga
            self.w_Vis.imgb=self.w_Vis.procimgb

            self.w_Vis.nameres=self.w_Vis.nameprocres
            self.w_Vis.nameimga=self.w_Vis.nameprocimga
            self.w_Vis.nameimgb=self.w_Vis.nameprocimgb
        
        return

    def plotProgessPIV(self,Var,data:dataTreePar,i):
        flag=len(Var) or i<0
        if flag:
            nameVar=self.namesPIV.instVel
            res={}
            for j,n in enumerate(nameVar):
                res[n]=Var[j]
            res["Mod"]=np.sqrt(res["U"]**2+res["V"]**2)
            self.w_Vis.procres=res
            self.w_Vis.nameprocres=os.path.join(f"{data.outPathRoot}_{i:0{data.ndig:d}d}{data.outExt}")
        else:
            self.w_Vis.procres=Var
            self.w_Vis.nameprocres=''

        if self.FlagProcInit:
            self.FlagProcInit=False
            if data.INP.flag_min:
                data.flagRun=data.VIS.Tre.flagRun=-11
            else:
                data.flagRun=data.VIS.Tre.flagRun=-12

            data.VIS.MapVar_type=2
            data.VIS.type=1
            data.VIS.VecField_type=0
            data.VIS.FlagErrRead[2]=False
            self.w_Vis.getResInfo(data.VIS,2,res) 
            self.w_Vis.setDefaultXLim(data.VIS)
            self.w_Vis.setDefaultCLim(data.VIS)
            data.VIS.FlagReset=[False,False] 
            data.VIS.nfield=data.VIS.Inp.selected=imin_im_pair-1
            self.w_Vis.updateVisfromINP(data.VIS)

            if flag: 
                self.w_Vis.VISpar.nfield=data.VIS.nfield
                if data.INP.flag_min:
                    self.w_Vis.procimga=data.compMin.Imin[0]
                    self.w_Vis.procimgb=data.compMin.Imin[1]
                    root_min=myStandardRoot(data.OUT.path+data.OUT.subfold+data.OUT.root)+"_"
                    self.w_Vis.nameprocimga=root_min+"a_min"+data.INP.pinfo.ext
                    self.w_Vis.nameprocimgb=root_min+"b_min"+data.INP.pinfo.ext  
            
        if flag and data.VIS.nfield==self.w_Vis.VISpar.nfield:
            self.w_Vis.VISpar_old.nfield=imin_im_pair-2
            self.w_Vis.res=self.w_Vis.procres
            self.w_Vis.imga=self.w_Vis.procimga
            self.w_Vis.imgb=self.w_Vis.procimgb

            self.w_Vis.nameres=self.w_Vis.nameprocres
            self.w_Vis.nameimga=self.w_Vis.nameprocimga
            self.w_Vis.nameimgb=self.w_Vis.nameprocimgb
        return 
    
#********************************** Pause
    @Slot(dataTreePar)
    def pause_proc(self,data:dataTreePar,errMessage=''):
        ''' pause_proc also when ends '''
        pri.Time.red(f'pause_proc Begin ')
        if errMessage=='': self.store_proc(data)
        else: 
            self.procdata.warnings[0]+='\n'+data.headerSection('CRITICAL ERROR',errMessage,'X')

        if self.w_Vis.VISpar.nfield==imin_im_pair-1:
            self.w_Vis.VISpar_old.nfield=imin_im_pair-2                  
        #pri.Process.red(f'pause_MINproc self.numCallBackTotOk={self.numCallBackTotOk} mi.nimg={mi.nimg}')
        if data.FlagFinished or errMessage!='': #save and continue 
            if not self.FlagRun: # bug noto se uno mette in pausa mentre sta finendo di salvare (al 100%) da errore, basta ripremere play oppure eliminare il check
                pri.Process.red('**************************** pause_proc Error ****************************')
            else:
                self.nextProc()
        else:
            if data.hasIndexOf(self.w_Tree.TABpar):
                self.w_Tree.selectFuture(0)
            if data.flagRun==-1:
                i:QTreeWidgetItem=self.w_Tree.TREpar.future[0]
                data.icon_type=self.Tree_icons.icontype('paused')
                i.setIcon(0,self.Tree_icons.paused)
            self.setButtons(data)
        pri.Time.red(f'pause_proc END')
        self.signals.pause_proc.emit()

    def store_proc(self,data_worker:dataTreePar):
        data=self.procdata #self.w_Tree.TABpar_prev[idata.indTree][idata.indItem][-1]
        for f in self.procFields:
            i=self.procdata.uncopied_fields.index(f)
            self.procdata.uncopied_fields.pop(i)
        if not data.numFinalized: return
        pri.Time.yellow(f'{"-"*100} store PROC')

        data.onPauseTimeStat()
        if self.FlagProcInit:
            if data.typeProc==dataTreePar.typeMIN: self.plotProgressMIN([],data)
            elif data.typeProc==dataTreePar.typePIV: 
                nameFields=data_worker.mediaPIV.namesPIV.avgVelFields
                Var=[getattr(data_worker.mediaPIV,f) for f in nameFields ]
                self.plotProgessPIV(Var,data,-1)

        #Copio ciò che è stato modificato nel worker
        #siccome data_worker sarà distrutto non faccio una deepcopy con copyfrom
        data.compMin=data_worker.compMin
        data.mediaPIV=data_worker.mediaPIV
        data.FlagFinished=data_worker.FlagFinished

        if data.typeProc==dataTreePar.typePIV:
            data.writeCfgProcPiv()
        #Aggiusto ciò che deve essere aggiornato
        data.icont=data.numProcOrErrTot
        data.warnings[1]=''
        data.setCompleteLog()
        if data.nimg==data.numCallBackTotOk: #data.FlagFinished:   #todo TA da GP: secondo te è corretto?
            data.flagRun=data.VIS.Tre.flagRun=int(data.numFinalized==data.nimg)+1
        else: 
            data.flagRun=data.VIS.Tre.flagRun=-1  

        with open(data.filename_proc[data.typeProc], 'wb') as file:
            pickle.dump(data, file)
            pri.Info.white(f'---> Saving {data.filename_proc[data.typeProc]}')
        #data.compMin=CompMin()
        #data.mediaPIV=mediaPIV()
        with open(data.filename_proc[data.typeProc]+'.log', 'a') as file:
             file.write(data.Log)
        
        
        pri.Time.yellow(f'{"-"*100} store PROC  END')

    @Slot()
    def buttonPauseHideShow(self):
        #pr ('buttonPauseHideShow')
        self.ui.button_pause.setEnabled(True) #.show()

    @Slot()
    def stopProcs(self):
        self.contProc+=1
        pri.Time.red(f'stopProcs     self.contProc={self.contProc}/{self.nProc}   self.numCallBackTotOk={self.numCallBackTotOk}  numFinalized={self.procdata.numFinalized}  {self.FlagRun}')
        
        if self.contProc==self.nProc:
            self.setEnabled(True)
            self.procWorkers=[]
            self.ui.button_pause.setEnabled(True)
            self.ui.button_Run.setEnabled(True)
            data_sel=self.w_Tree.TABpar
            self.setButtons(data_sel)
            self.ui.label_updating_pairs.setVisible(False)
            if self.waitingDialog:
                self.waitingDialog.done(0)
                self.waitingDialog=None
            if self.completingTask:
                self.completingTask()
                self.completingTask=None

            if self.FlagClosing[0]:
                self.correctClose()
            
        
#*************************************************** Graphical interface appearence
    def setGPApar(self):
        self.w_Process.ui.combo_mode.setCurrentIndex(self.GPApar.ProcessMode)
        self.w_Process.combo_mode_callback()
        self.undockTabs()
        self.setTabLayout()
        self.checkPastProc()
        self.checkFutureProc()
        self.ui.button_PaIRS_download.setVisible(self.GPApar.currentVersion!=self.GPApar.latestVersion and bool(self.GPApar.latestVersion))
        if self.GPApar.NumCores >NUMTHREADS_PIV_MAX:
            self.GPApar.NumCores=NUMTHREADS_PIV_MAX
        self.numUsedThreadsPIV=self.GPApar.NumCores  
        self.ui.spin_nworkers.setValue(self.GPApar.NumCores)  
        self.setFontPixelSize()
        #self.ui.centralwidget.show()

    def setTabLayout(self,*args):
        if len(args): itab=args[0]
        else: itab=range(5)    
        #self.update()        
        self.setButtonLayout()
        self.adjustGeometry(itab)
        if not self.GPApar.FlagUndocked and self.FlagGuiInit:
            self.updateGPAparGeom()
       
    def setButtonLayout(self):
        widname=self.optabnames[self.GPApar.lastTab]
        for k,tn in enumerate(self.optabnames):
            if k<3 and not self.GPApar.FlagUndocked and not self.GPApar.FlagAllTabs:    
                flag=getattr(self.GPApar,f"Flag{tn}") and tn==widname
            else: 
                flag=getattr(self.GPApar,f"Flag{tn}")
            setattr(self.GPApar,f"Flag{tn}",flag)
            if tn=='Vis':
                VISpar.FlagVis=self.GPApar.FlagVis

            button:RichTextPushButton=getattr(self.ui,f"button_{tn}")
            wid:gPaIRS_Tab=getattr(self,'w_'+self.opwidnames[k])
            button.setChecked(flag)
            self.GPApar.FloatingsVis[k]=flag

            if self.GPApar.FlagUndocked:
                wid.ui.w_button_close_tab.hide()
            else:
                wid.ui.w_button_close_tab.show()
                if self.GPApar.FlagAllTabs:
                    button.setChecked(not self.GPApar.FlagAllTabs)
                else:
                    button.setChecked(tn==widname)

            self.setOpButtonText(tn)

        if self.GPApar.FlagUndocked:
            self.ui.button_dock.setIcon(self.icon_dock_tabs)
            tipDock="Dock tabs"+' ('+self.ui.button_dock.shortcut().toString(QKeySequence.NativeText)+')'

            self.ui.button_Shape.hide()
            self.ui.link.hide()
            self.ui.link_2.hide()
            self.ui.IOP_butt_lay.setSpacing(self.ui.link_2.width())
        else:
            self.ui.button_dock.setIcon(self.icon_undock_tabs)
            tipDock="Undock tabs"+' ('+self.ui.button_dock.shortcut().toString(QKeySequence.NativeText)+')'
            self.ui.button_Shape.show()
            if self.GPApar.FlagAllTabs:
                tipShape="Join Input, Output and Process tabs"+' ('+self.ui.button_Shape.shortcut().toString(QKeySequence.NativeText)+')'
                self.ui.button_Shape.setIcon(self.icon_wrap)
                self.ui.link.hide()
                self.ui.link_2.hide()
                self.ui.IOP_butt_lay.setSpacing(self.ui.link_2.width())
            else:
                tipShape="Separate Input, Output and Process tabs"+' ('+self.ui.button_Shape.shortcut().toString(QKeySequence.NativeText)+')'
                self.ui.button_Shape.setIcon(self.icon_unwrap)
                self.ui.link.show()
                self.ui.link_2.show()
                self.ui.IOP_butt_lay.setSpacing(0)
            self.ui.button_Shape.setToolTip(tipShape)
            self.ui.button_Shape.setStatusTip(tipShape)
        self.ui.button_dock.setToolTip(tipDock)
        self.ui.button_dock.setStatusTip(tipDock)

    def setOpButtonLabel(self,*args):
        if len(args):
            self.GPApar.FlagButtLabel=args[0]
        else:
            if self.GPApar.FlagUndocked:
                self.GPApar.FlagButtLabel=self.width()>w_button_min_size
            else:
                if all([not getattr(self.GPApar,'Flag'+tn) for tn in self.optabnames]):
                    s=self.main_splitter.sizes()[0] #s=max([self.main_splitter.sizes()[0],self.minW_ManTabs])
                    self.GPApar.FlagButtLabel=s>w_button_min_size
                else:
                    self.GPApar.FlagButtLabel=self.main_splitter.sizes()[-1]>w_button_min_size
        if self.GPApar.FlagButtLabel==self.FlagButtLabel: return
        self.FlagButtLabel=self.GPApar.FlagButtLabel
        for tn in self.optabnames:
            self.setOpButtonText(tn)
        return
    
    def setOpButtonText(self,tabname):
        button:RichTextPushButton=getattr(self.ui,f"button_{tabname}")
        flag=getattr(self.GPApar,f"Flag{tabname}")
        if flag:
            s=''
        else:
            fPixSize=button.font().pixelSize()
            s=f'<sup><span style=" font-size:{fPixSize-2}px"> 🔒</span></sup>'
        if self.GPApar.FlagButtLabel:
            button.setText(tabname+s)
        else:
            button.setText(s)

    def adjustGeometry(self,*args):
        if len(args): itab=args[0]
        else: itab=range(5)
        pri.Geometry.yellow(f'{"<>"*5} Adjusting geometry {"<>"*5}')
        if self.GPApar.FlagUndocked: 
            for k,f in enumerate(self.floatings):
                if self.GPApar.FloatingsGeom[k]:
                    f.setGeometry(self.GPApar.FloatingsGeom[k])
                if self.GPApar.FloatingsVis[k] and self.FlagGuiInit: 
                    f.show()
                    f.pa.show()
                else: 
                    f.hide()
                setattr(self.GPApar,'Flag'+self.optabnames[k],self.GPApar.FloatingsVis[k])
            """
            for k in itab:
                f=self.floatings[k]
                if self.GPApar.FloatingsVis[k]: 
                    f.setWindowFlags(f.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                    f.show()
                    f.setWindowFlags(f.windowFlags()  & ~ QtCore.Qt.WindowStaysOnTopHint)
                    f.show()
                else: f.hide()
            """
            self.setGeometry(self.GPApar.FloatingsGeom[-1])
            self.GPApar.FloatingsVis[-1]=True
            for k,wn in enumerate(self.opwidnames[:-1]):
                w=getattr(self,'w_'+wn)
                w.ui.scrollArea.verticalScrollBar().setValue(self.GPApar.FScrollAreaValues[k])
            pri.Geometry.yellow(f'*** Undocked configuration:\n    Floatings Geometry={self.GPApar.FloatingsGeom}\n    Floatings Vis={self.GPApar.FloatingsVis}')
        else:
            cont=0
            for k,wn in enumerate(self.optabnames):
                tabname="f_"+self.opwidnames[k]+"Tab"
                tab=getattr(self.ui,tabname)
                flag=getattr(self.GPApar,'Flag'+wn)
                tab.setVisible(flag)
                cont+=flag                
            Flag=cont>0
            self.hideOpTabs(not Flag)
            self.setGeometry(self.GPApar.Geometry) 
            if Flag: 
                self.main_splitter.setSizes(self.GPApar.SplitterSizes[0])
                splitterSizes=self.GPApar.SplitterSizes[1]
                self.setSecondarySplitterSizes(splitterSizes)
                self.ui.scrollArea.horizontalScrollBar().setValue(self.GPApar.ScrollAreaValues[0])
                for k,wn in enumerate(self.opwidnames[:-1]):
                    w=getattr(self,'w_'+wn)
                    w.ui.scrollArea.verticalScrollBar().setValue(self.GPApar.ScrollAreaValues[k+1])
        if self.FlagGuiInit: self.show()
        pri.Geometry.yellow(f'*** Docked configuration:\n    Geom={self.GPApar.Geometry}\n    Main Spiltter Sizes={self.GPApar.SplitterSizes[0]}\n    Secondary Spiltter Sizes={self.GPApar.SplitterSizes[1]}')

    def setSecondarySplitterSizes(self,splitterSizes):
        self.OpWidth=self.OpMaxWidth=0
        for k,tname in enumerate(self.opwidnames):
            flagname="Flag"+self.optabnames[k]
            flag=getattr(self.GPApar,flagname)
            tabname=f"f_"+tname+"Tab"
            tab=getattr(self.ui,tabname)
            if flag:
                if not splitterSizes[k]:
                    splitterSizes[k]=self.GPApar.SplitterSizes[2][k]
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
        self.updateGPAparGeom()
        self.setTabLayout()    
        self.setFontPixelSize()
        
    def close_tab(self,w:gPaIRS_Tab):
        w.parent().hide()
        setattr(self.GPApar,'Flag'+w.name_tab,False)
        self.updateGPAparGeom()
        if self.GPApar.FlagUndocked:
            self.setButtonLayout()
        else:
            self.setTabLayout()

    def updateGPAparGeom(self): 
        pri.Geometry.green(f"{'-'*10} Updating geometry {'-'*10}")
        self.GPApar.ProcessMode=mode_items.index(PROpar.mode)
        if self.GPApar.FlagUndocked:
            for i,f in enumerate(self.floatings):
                self.GPApar.FloatingsGeom[i]=f.geometry()
                self.GPApar.FloatingsVis[i]=f.isVisible()
            geo=self.floatings[self.GPApar.prevTab].geometry()
            #for k in range(3): self.GPApar.FloatingsGeom[k]=geo 
            self.GPApar.FloatingsGeom[i+1]=self.geometry()
            self.GPApar.FloatingsVis[i+1]=self.isVisible()
            for k,wn in enumerate(self.opwidnames):
                if wn!='Vis':
                    w=getattr(self,'w_'+wn)
                    self.GPApar.FScrollAreaValues[k]=w.ui.scrollArea.verticalScrollBar().value()
            pri.Geometry.green(f'*** Undocked configuration:\n    Floatings Geometry={self.GPApar.FloatingsGeom}\n    Floatings Vis={self.GPApar.FloatingsVis}')
        else:
            self.GPApar.Geometry=self.geometry()   
            self.GPApar.SplitterSizes[0]=self.main_splitter.sizes()
            self.GPApar.SplitterSizes[1]=splitterSizes=self.secondary_splitter.sizes()
            self.GPApar.ScrollAreaValues[0]=self.ui.scrollArea.horizontalScrollBar().value()
            for k,wn in enumerate(self.opwidnames):
                if splitterSizes[k]:
                    if k<3 and not self.GPApar.FlagAllTabs:
                        for j in range(3): self.GPApar.SplitterSizes[2][j]=splitterSizes[k]
                    else:
                        self.GPApar.SplitterSizes[2][k]=splitterSizes[k]
            for k,wn in enumerate(self.opwidnames):
                if wn!='Vis':
                    w=getattr(self,'w_'+wn)
                    self.GPApar.ScrollAreaValues[k+1]=w.ui.scrollArea.verticalScrollBar().value()
            pri.Geometry.green(f'*** Docked configuration:\n    Geom={self.GPApar.Geometry}\n    Main Spiltter Sizes={self.GPApar.SplitterSizes[0]}\n    Secondary Spiltter Sizes={self.GPApar.SplitterSizes[1]}')

    def button_Tab_callback(self,name):
        b:QPushButton=getattr(self.ui,"button_"+name)
        flagname="Flag"+name
        FlagVisible=getattr(self.GPApar,flagname)
        if b.isCheckable():
            setattr(self.GPApar,flagname,b.isChecked())
        else:
            setattr(self.GPApar,flagname,True)
        if name=='Vis' and not FlagVisible:
            VISpar.FlagVis=self.GPApar.FlagVis
            if VISpar.FlagVis:
                #devo fare ciò che ho skippato
                self.w_Vis.importVar()
                #w=getattr(self,self.w_Tree.TABpar.freset_par)
                w=self.w_Vis
                self.w_Vis.VISpar_old.nfield=imin_im_pair-2 #necessario per far si che veramente crei il nuovo plot
                w.setVISpar()
                self.w_Vis.VISpar_old.nfield=self.w_Vis.VISpar.nfield
        itab=self.optabnames.index(name)
        self.GPApar.prevTab=self.GPApar.lastTab
        if itab<3: self.GPApar.lastTab=itab  
        self.updateGPAparGeom()
        self.setTabLayout([itab])
        if not self.GPApar.FlagUndocked:
            if getattr(self.GPApar,flagname):
                #self.update()
                wTab=self.GPApar.SplitterSizes[0][2]-self.secondary_splitter.handleWidth()
                if self.GPApar.SplitterSizes[1][itab]>wTab:
                    self.GPApar.SplitterSizes[1][itab]=wTab
                    self.adjustGeometry()
        self.moveToTab(name)
        tab=getattr(self,'w_'+self.opwidnames[itab])
        w=self.focusWidget()
        w.clearFocus()
        if name !='Vis':
            tab:Import_Tab
            tab.ui.scrollArea.setFocus()
        else:
            tab:Vis_Tab
            tab.ui.spin_field_number.setFocus()
                
    def moveToTab(self,name,finished=lambda: None):
        i=self.optabnames.index(name)
        if not self.GPApar.FlagUndocked:
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
        flag=getattr(self.GPApar,flagname)
        tabname="f_"+self.opwidnames[self.optabnames.index(name)]+"Tab"
        tab=getattr(self.ui,tabname)
        if flag:
            tab.show()
            self.OpWidth+=tab.geometry().width()+self.secondary_splitter.handleWidth()
            self.OpMaxWidth+=tab.maximumWidth()+self.secondary_splitter.handleWidth()
        else:
            tab.hide()
        
    def button_Shape_callback(self):
        self.updateGPAparGeom()
        self.GPApar.FlagAllTabs=not self.GPApar.FlagAllTabs
        self.setTabLayout()
    
    def button_dock_callback(self):
        self.FlagUndocking=True
        self.updateGPAparGeom()
        #self.hide()
        self.GPApar.FlagUndocked= not self.GPApar.FlagUndocked
        self.undockTabs()
        if Flag_RESIZEONRUN:
            if self.FlagRun: 
                self.BSizeCallbacks[4]()
            else: 
                self.setTabLayout()
                if self.GPApar.FlagLog: self.moveToTab('Log')
                elif self.GPApar.FlagVis: self.moveToTab('Vis')
        else: 
            self.setTabLayout()
        #self.show()
        self.FlagUndocking=False

    def undockTabs(self):
        if self.GPApar.FlagUndocked:
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
        self.hideOpTabs(self.GPApar.FlagUndocked)
        
    def hideOpTabs(self,flagUndocked):
        dpix=20
        if flagUndocked:
            self.ui.manlay.insertWidget(1,self.ui.w_Buttons)
            self.ui.w_Operating_Tabs.hide()
            self.ui.main_sep.hide()
            self.centralWidget().setMaximumWidth(self.ui.f_Tree_Process.maximumWidth())
            self.centralWidget().setMinimumWidth(self.ui.w_Buttons.minimumWidth()+dpix)
            self.setMaximumWidth(self.ui.f_Tree_Process.maximumWidth())
            self.setMinimumWidth(self.ui.w_Buttons.minimumWidth()+dpix)
        else:
            self.ui.oplay.insertWidget(0,self.ui.w_Buttons)
            self.ui.w_Operating_Tabs.show()
            self.ui.main_sep.show()
            self.centralWidget().setMaximumWidth(self.maxW)
            self.centralWidget().setMinimumWidth(self.minW)
            self.setMaximumWidth(self.maxW)
            self.setMinimumWidth(self.minW)
        size=self.size()
        newSize=QSize(min([size.width(),self.maxW]),size.height())
        self.resize(newSize)

        """
        if flagUndocked:
            self.GPApar.FlagButtLabel=self.GPApar.FloatingsGeom[-1].width()>w_button_min_size
        else:
            if all([not getattr(self.GPApar,'Flag'+tn) for tn in self.optabnames]):
                margins=self.ui.Clayout.contentsMargins()
                s=max([self.GPApar.SplitterSizes[0][0],self.minimumWidth()-margins.left()-margins.right()])
                self.GPApar.FlagButtLabel=s>w_button_min_size
            else:
                self.GPApar.FlagButtLabel=self.GPApar.SplitterSizes[0][-1]>w_button_min_size
        self.setOpButtonLabel(self.GPApar.FlagButtLabel)
        """

    def button_default_sizes_callback(self):
        bRButt=self.ui.button_default_sizes.mapToGlobal(self.ui.button_default_sizes.geometry().bottomRight())
        geom = self.ResizePopup.frameGeometry()
        geom.moveBottomLeft(bRButt) #QtGui.QCursor.pos())
        self.ResizePopup.setGeometry(geom)
        self.ResizePopup.show()
        #QTimer.singleShot(ResizePopup_time, lambda : self.ResizePopup.hide())

    def setPresetSizes(self,kind):
        if not self.GPApar.FlagUndocked:
            if kind!=5:
                self.updateGPAparGeom()
                fields_docked=['Geometry','SplitterSizes','ScrollAreaValues','FlagAllTabs','lastTab']+['Flag'+f for f in self.optabnames]
                self.GPApar_old.copyfromdiz(self.GPApar,fields_docked)
            self.DockedSizes(kind)
        else:
            if kind!=5:
                self.updateGPAparGeom()
                fields_undocked=['FloatingsGeom','FloatingsVis']+['Flag'+f for f in self.optabnames]
                self.GPApar_old.copyfromdiz(self.GPApar,fields_undocked)
            self.UndockedSizes(kind)
        self.setGPApar()

    def DockedSizes(self,kind):
        if kind==0:
            self.DefaultSize()
        if kind==1:
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wG=int(self.MaxGeo.width()*0.5)
            self.GPApar.Geometry.setX(self.MaxGeo.x())
            self.GPApar.Geometry.setY(self.MaxGeo.y())
            self.GPApar.Geometry.setWidth(wG)
            self.GPApar.Geometry.setHeight(self.MaxGeo.height())
            
            margins=self.ui.Clayout.contentsMargins()
            self.GPApar.SplitterSizes[0][0]=wMan_fin
            self.GPApar.SplitterSizes[0][2]=wG-sum(self.GPApar.SplitterSizes[0][:2])-margins.left()-margins.right()-self.main_splitter.handleWidth()*2
            wTabs=self.GPApar.SplitterSizes[0][2]
            self.GPApar.SplitterSizes[1][:5]=[wTabs]*5
            self.GPApar.ScrollAreaValues=[0]*5

            self.GPApar.FlagAllTabs=True
            self.GPApar.lastTab=0
            self.GPApar.FlagInput=self.GPApar.FlagOutput=self.GPApar.FlagProcess=True
            self.GPApar.FlagLog=self.GPApar.FlagVis=True
        elif kind==2:
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wG=int(self.MaxGeo.width()*0.5)
            wG+=wG-wMan_fin
            self.GPApar.Geometry.setX(self.MaxGeo.x())
            self.GPApar.Geometry.setY(self.MaxGeo.y())
            self.GPApar.Geometry.setWidth(wG)
            self.GPApar.Geometry.setHeight(self.MaxGeo.height())
            
            margins=self.ui.Clayout.contentsMargins()
            self.GPApar.SplitterSizes[0][0]=wMan_fin
            self.GPApar.SplitterSizes[0][2]=wG-sum(self.GPApar.SplitterSizes[0][:2])-margins.left()-margins.right()-self.main_splitter.handleWidth()*2
            wTabs=(self.GPApar.SplitterSizes[0][2]*0.5-self.secondary_splitter.handleWidth())
            self.GPApar.SplitterSizes[1][:5]=[wTabs]*5
            self.GPApar.ScrollAreaValues=[0]*5

            self.GPApar.FlagAllTabs=False
            self.GPApar.lastTab=0
            self.GPApar.FlagInput=True
            self.GPApar.FlagOutput=self.GPApar.FlagProcess=False
            self.GPApar.FlagLog=False
            self.GPApar.FlagVis=True
        elif kind==3:
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wG=self.MaxGeo.width()
            self.GPApar.Geometry.setX(self.MaxGeo.x())
            self.GPApar.Geometry.setY(self.MaxGeo.y())
            self.GPApar.Geometry.setWidth(wG)
            self.GPApar.Geometry.setHeight(self.MaxGeo.height())
            
            margins=self.ui.Clayout.contentsMargins()
            self.GPApar.SplitterSizes[0][0]=wMan_fin
            self.GPApar.SplitterSizes[0][2]=wG-sum(self.GPApar.SplitterSizes[0][:2])-margins.left()-margins.right()-self.main_splitter.handleWidth()*2
            wTabs=(self.GPApar.SplitterSizes[0][2]/3-self.secondary_splitter.handleWidth()*2)
            self.GPApar.SplitterSizes[1][:5]=[wTabs]*5
            self.GPApar.ScrollAreaValues=[0]*5

            self.GPApar.FlagAllTabs=False
            self.GPApar.lastTab=0
            self.GPApar.FlagInput=True
            self.GPApar.FlagOutput=self.GPApar.FlagProcess=False
            self.GPApar.FlagLog=True
            self.GPApar.FlagVis=True
        elif kind==4:
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wG=self.MaxGeo.width()
            self.GPApar.Geometry.setX(self.MaxGeo.x())
            self.GPApar.Geometry.setY(self.MaxGeo.y())
            self.GPApar.Geometry.setWidth(wG)
            self.GPApar.Geometry.setHeight(self.MaxGeo.height())
            
            margins=self.ui.Clayout.contentsMargins()
            self.GPApar.SplitterSizes[0][0]=wMan_fin
            self.GPApar.SplitterSizes[0][2]=wG-sum(self.GPApar.SplitterSizes[0][:2])-margins.left()-margins.right()-self.main_splitter.handleWidth()*2
            wTabs=(self.GPApar.SplitterSizes[0][2]*0.5-self.secondary_splitter.handleWidth())
            self.GPApar.SplitterSizes[1][:5]=[wTabs]*5

            self.GPApar.FlagAllTabs=False
            self.GPApar.lastTab=0
            self.GPApar.FlagInput=self.GPApar.FlagOutput=self.GPApar.FlagProcess=False
            self.GPApar.FlagLog=True
            self.GPApar.FlagVis=True
        elif kind==5:
            fields_docked=['Geometry','SplitterSizes','ScrollAreaValues','FlagAllTabs','lastTab']+['Flag'+f for f in self.optabnames]
            self.GPApar.copyfromdiz(self.GPApar_old,fields_docked)

        self.GPApar.FlagButtLabel=self.GPApar.SplitterSizes[0][2]>w_button_min_size
               
    def UndockedSizes(self,kind):
        geo=self.MaxGeo
        x0=geo.x()
        y0=geo.y()
        w=geo.width()
        h=geo.height()
        dx=self.MaxFrameGeo.width()-geo.width()
        if kind==0:
            self.DefaultSize()
        elif kind==1:
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wMain=max([min([wMan_fin,self.maximumWidth()]),self.minimumWidth()])

            xTabs=x0+wMain+dx
            yTabs=y0
            wTabs=w*0.5-wMain
            wTabs=max([min([wTabs,self.floatings[0].maximumWidth()]),self.floatings[0].minimumWidth()])

            self.GPApar.FloatingsGeom[-1]=QRect(x0,y0,wMain,h)  #main window
            self.GPApar.FloatingsGeom[:5]=[QRect(xTabs,yTabs,wTabs,h)]*5  
            self.GPApar.FScrollAreaValues=[0]*4
        
            self.GPApar.FlagInput=True
            self.GPApar.FlagOutput=self.GPApar.FlagProcess=self.GPApar.FlagLog=self.GPApar.FlagVis=False
        elif kind==2:
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wMain=max([min([wMan_fin,self.maximumWidth()]),self.minimumWidth()])

            xTabs=x0+wMain+dx
            yTabs=y0
            wTabs=w*0.5-wMain
            wTabs=max([min([wTabs,self.floatings[0].maximumWidth()]),self.floatings[0].minimumWidth()])

            xVis=x0+wMain+wTabs+dx*2
            yVis=y0
            wVis=wTabs

            self.GPApar.FloatingsGeom[-1]=QRect(x0,y0,wMain,h)  #main window
            self.GPApar.FloatingsGeom[:3]=[QRect(xTabs,yTabs,wTabs,h)]*3  
            self.GPApar.FloatingsGeom[3:5]=[QRect(xVis,yVis,wVis,h)]*2 
            self.GPApar.FScrollAreaValues=[0]*4
        
            self.GPApar.FlagInput=True
            self.GPApar.FlagOutput=self.GPApar.FlagProcess=False
            self.GPApar.FlagLog=False
            self.GPApar.FlagVis=True
        elif kind==3:
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wMain=max([min([wMan_fin,self.maximumWidth()]),self.minimumWidth()])

            xTabs=x0+wMain+dx
            yTabs=y0
            wTabs=(w-wMain)/3
            wTabs=max([min([wTabs,self.floatings[0].maximumWidth()]),self.floatings[0].minimumWidth()])
            xLog=x0+wMain+wTabs+2*dx
            xVis=x0+wMain+2*wTabs+3*dx

            self.GPApar.FloatingsGeom[-1]=QRect(x0,y0,wMain,h)  #main window
            self.GPApar.FloatingsGeom[:3]=[QRect(xTabs,yTabs,wTabs,h)]*5  
            self.GPApar.FloatingsGeom[3]=QRect(xLog,yTabs,wTabs,h)  
            self.GPApar.FloatingsGeom[4]=QRect(xVis,yTabs,wTabs,h)  
            self.GPApar.FScrollAreaValues=[0]*4
        
            self.GPApar.FlagInput=True
            self.GPApar.FlagOutput=self.GPApar.FlagProcess=False
            self.GPApar.FlagLog=self.GPApar.FlagVis=True
        elif kind==4: 
            wMan_fin=self.ui.w_Managing_Tabs.minimumWidth()
            wMain=max([min([wMan_fin,self.maximumWidth()]),self.minimumWidth()])

            xLog=x0+wMain+dx
            yLog=y0
            wLog=self.w_Log.ui.log.lineWrapColumnOrWidth()
            
            xVis=x0+wMain+wLog+dx*2
            yVis=y0
            wVis=wVis=w-wMain-wLog-2*dx

            self.GPApar.FloatingsGeom[-1]=QRect(x0,y0,wMain,h)  #main window
            self.GPApar.FloatingsGeom[:4]=[QRect(xLog,yLog,wLog,h)]*4  #Log
            self.GPApar.FloatingsGeom[4]=QRect(xVis,yVis,wVis,h) #Vis
            self.GPApar.FScrollAreaValues=[0]*4

            self.GPApar.FlagInput=self.GPApar.FlagOutput=self.GPApar.FlagProcess=False
            self.GPApar.FlagLog=self.GPApar.FlagVis=True
        elif kind==5:
            fields_undocked=['FloatingsGeom','FloatingsVis']+['Flag'+f for f in self.optabnames]
            self.GPApar.copyfromdiz(self.GPApar_old,fields_undocked)

        if kind!=5:
            for k,tn in enumerate(self.optabnames):
                flag=getattr(self.GPApar,'Flag'+tn)
                self.GPApar.FloatingsVis[k]=flag
            self.GPApar.FloatingsVis[-1]=True
            
    def DefaultSize(self):
        geo=self.MaxGeo
        x0=geo.x()
        y0=geo.y()
        w=geo.width()
        h=geo.height()
        
        pri.Geometry.blue(f'{"°"*10} Setting sizes {"°"*10}')
        if not self.GPApar.FlagUndocked:

            handleWidth1=self.main_splitter.handleWidth()   
            handleWidth2=self.secondary_splitter.handleWidth()   
            dpix=[100,75]
            Geometry=QRect(int(dpix[0])+x0,int(dpix[1])+y0,int(w-2*dpix[0]),int(h-2*dpix[1]))
            wp=Geometry.width()
            #hp=Geometry.height()
            nw=3
            wt=int(wp/nw)
            wsep=self.ui.main_sep.width()
            MainSplitterSizes=[wt+handleWidth1,wsep+handleWidth1,(wt+handleWidth2)*(nw-1)+f_empty_width]
            SecondarySplitterSizes=[wt+handleWidth2]*5+[f_empty_width]
            #self.GPApar.FlagAllTabs=True
            self.GPApar.Geometry=Geometry
            self.GPApar.SplitterSizes[0]=MainSplitterSizes
            self.GPApar.SplitterSizes[1]=copy.deepcopy(SecondarySplitterSizes)
            self.GPApar.SplitterSizes[2]=copy.deepcopy(SecondarySplitterSizes)
            self.GPApar.ScrollAreaValues=[0]*5

            self.GPApar.FlagAllTabs=True
            self.GPApar.FlagInput=self.GPApar.FlagOutput=self.GPApar.FlagProcess=True
            self.GPApar.FlagLog=self.GPApar.FlagVis=True
            pri.Geometry.blue(f'--> Docked configuration:\n    Geom={self.GPApar.Geometry}\n    Main Spiltter Sizes={self.GPApar.SplitterSizes[0]}\n    Secondary Spiltter Sizes={self.GPApar.SplitterSizes[1]}')
        else:
            dx=self.MaxFrameGeo.width()-w
            dy=self.MaxFrameGeo.height()-h
            m=self.ui.Clayout.contentsMargins() 
            wMain=self.ui.w_Buttons.minimumWidth()+m.left()+m.right()
            wpf=int((w-wMain-dx)*0.45)
            wIOP=self.w_Import.minimumWidth()
            if wpf>wIOP: wIOP=wpf
            wVis=w-wMain-wIOP-2*dx
            hIOP=self.w_Import.minimumWidth()
            if int(h*0.55>hIOP): hIOP=int(h*0.55)
            hLog=h-hIOP-dy
            FGeometry_main=QRect(x0,y0,wMain,h)
            FGeometry_IOP=QRect(x0+wMain+dx,y0,wIOP,hIOP)
            FGeometry_Log=QRect(x0+wMain+dx,y0+hIOP+dy,wIOP,hLog)
            FGeometry_Vis=QRect(x0+wMain+wIOP+dx*2,y0,wVis,h)
            self.GPApar.FloatingsGeom=[FGeometry_IOP]*3+[FGeometry_Log]+[FGeometry_Vis]+[FGeometry_main]
            self.GPApar.FloatingsVis=[True]+[False]*2+[True]*3
            self.GPApar.FScrollAreaValues=[0]*4
            pri.Geometry.blue(f'--> Undocked configuration:\n    Floatings Geometry={self.GPApar.FloatingsGeom}\n    Floatings Vis={self.GPApar.FloatingsVis}')

#*************************************************** Greetings
    def setupLogo(self):
        today = datetime.date.today()
        d=today.strftime("%d/%m/%Y")
        happy_days=[
            #[d, 'Happy birthday to PaIRS! 🎈🎂🍾'], #to test
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
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_PaIRS_party_rect.png"))
            self.ui.lab_happy_days.show()
            self.ui.lab_happy_days.setText(happy_days[i][1])
        else:
            self.FlagHappyLogo=False
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_PaIRS_rect.png"))
            self.ui.lab_happy_days.hide()

    def happyLogo(self):
        self.FlagHappyLogo=not self.FlagHappyLogo
        if self.FlagHappyLogo:
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_PaIRS_party_rect.png"))
            self.ui.lab_happy_days.show()
            self.ui.lab_happy_days.setText('Greetings! Today is a great day! 🎈🎉')
        else:
            self.ui.logo.setPixmap(QPixmap(u""+ icons_path +"logo_PaIRS_rect.png"))
            self.ui.lab_happy_days.hide()

#*************************************************** Palette
    def setGPaIRSPalette(self):
        setAppGuiPalette(self,self.palettes[self.GPApar.paletteType])

    def paletteContextMenuEvent(self, event):   
        contextMenu = QMenu(self)
        act=[]
        for n in self.paletteNames:
            act.append(contextMenu.addAction(f"{n} mode"))
        act[self.GPApar.paletteType].setCheckable(True)
        act[self.GPApar.paletteType].setChecked(True)
        userAct = contextMenu.exec(self.mapToGlobal(event.pos()))
        for k,a in enumerate(act):
            if a==userAct:
                self.GPApar.paletteType=k
                self.setGPaIRSPalette()

def launchPaIRS(flagDebug=False,flagInputDebug=False):
    print('\n'+PaIRS_Header+'Starting the interface...')
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font=QFont()
    font.setFamily(fontName)
    font.setPixelSize(fontPixelSize)
    app.setFont(font)
    app.pyicon=app.windowIcon()
    icon=QIcon()
    icon.addFile(''+ icons_path +'icon_PaIRS.png',QSize(), QIcon.Normal, QIcon.Off)
    app.setWindowIcon(icon)
    try:
        if (platform.system() == "Windows"):
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('PaIRS')
    except:
        pri.General.red('It was not possible to set the application icon')

    if not flagDebug or Flag_SHOWSPLASH:
        splash=showSplash()
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
    gui=gPaIRS(flagDebug,app)
    gui.palettes[2]=standardPalette
    gui.setGPaIRSPalette()

    currentVersion=__version__ #if __subversion__=='0' else  __version__+'.'+__subversion__
    flagStopAndDownload=checkLatestVersion(gui,currentVersion,app,splash)
    if flagStopAndDownload:
        gui.correctClose()
        runPaIRS(gui,flagQuestion=False)
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
    print('\nWelcome to PaIRS!\nEnjoy it!')
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
    
def quitPaIRS(app:QApplication,flagPrint=True):
    app.setWindowIcon(app.pyicon)
    app.quit()
    if flagPrint: print('\nPaIRS closed.\nSee you soon!')
    if hasattr(app,'SecondaryThreads'):
        if len(app.SecondaryThreads):
            while any([s.isRunning for s in app.SecondaryThreads]):
                timesleep(.1)
                pass
    app=None
    return

def setAppGuiPalette(self:gPaIRS,palette:QPalette):
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
    self.ResizePopup=ResizePopup(self.BSizeCallbacks) #non riesco a farlo come gli altri
    self.w_Vis.addPlotToolBar()

if __name__ == "__main__":
    app,gui,flagPrint=launchPaIRS(True)
    quitPaIRS(app,flagPrint)
