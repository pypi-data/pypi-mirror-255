from .ui_Import_Tab import*
from .Import_Tab_tools import*
from .TabTools import*

class INPpar(TABpar):
    def __init__(self):
        self.setup()
        super().__init__()
        self.name='INPpar'
        self.surname='INPUT_Tab'
        self.unchecked_fields+=['FlagValidPath','FlagValidRoot','selected']

    def setup(self):
        self.FlagValidPath = 0
        self.path = ''
        self.FlagValidRoot = 0
        self.root = ''
        self.FlagUpdating = 0
        self.Pinfo = patternInfoList()
        self.pinfo = patternInfoVar()
        self.npairs = 0
        self.nimg_eff = 0
        self.nspa_eff = 0
        self.range_from = 0 
        self.range_to = 0
        self.selected = imin_im_pair
        self.flag_TR = False
        self.flag_min = True
        self.x = 0
        self.y = 0
        self.w = 1
        self.h = 1
        self.W = 1
        self.H = 1
        self.list_Image_Files=[]
        self.list_eim=[]
        self.list_Image_numbers=[]
        self.list_items=[]
        self.list_ind_items=[]
        self.pathCompleter=basefold_DEBUGOptions

class Import_Tab(gPaIRS_Tab):
    class Import_Tab_Signals(gPaIRS_Tab.Tab_Signals):
        set_Image_List=Signal()
        analysePath_signal=Signal(patternInfoList,str,int)
        createListImages_signal=Signal(bool,list,int)
        def __init__(self, parent):  
            super().__init__(parent)
            self.analysePath_signal.connect(parent.selectRootInPath)
            self.createListImages_signal.connect(parent.setInfoImages)

    def __init__(self,*args):
        parent=None
        flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: flagInit=args[1]
        super().__init__(parent,Ui_ImportTab,INPpar)
        self.signals=self.Import_Tab_Signals(self)

        #------------------------------------- Graphical interface: widgets
        self.ui: Ui_ImportTab
        ui=self.ui
        ui.w_range_frame.hide()
        ui.spin_range_from.addwid=[ui.spin_selected]
        ui.spin_range_to.addwid=[ui.spin_selected]
        ui.spin_x.addwid=[ui.spin_w]
        ui.spin_y.addwid=[ui.spin_h]

        self.setupWid()  #---------------- IMPORTANT
        self.ui.list_images.clear()

        #------------------------------------- Graphical interface: miscellanea
        self.mapx  = QPixmap(''+ icons_path +'redx.png')
        self.mapv  = QPixmap(''+ icons_path +'greenv.png')
        self.mapw  = QPixmap(''+ icons_path +'waiting_c.png')
        self.Lab_warning=QPixmap(u""+ icons_path +"warning.png")

        self.list_Path_Root=["edit_path","button_path","edit_root","button_import"]
        self.list_Spins=["spin_range_from","spin_range_to","spin_selected","spin_x","spin_y","spin_w","spin_h"]
        self.list_Image_Opt=["check_TR_sequence","button_resize"]
        self.list_List_Images=["list_images"]
        self.list_All=self.list_Path_Root[:]+self.list_Spins[:]+self.list_Image_Opt[:]+self.list_List_Images[:]
        self.spin_fields=("range_from","range_to","selected","x","y","w","h")
        self.TR_min_fields=("flag_TR","flag_min")

        self.icon_play=QIcon()
        self.icon_play.addFile(u""+ icons_path +"play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_pause=QIcon()
        self.icon_pause.addFile(u""+ icons_path +"pause.png", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_done=QIcon()
        self.icon_done.addFile(u""+ icons_path +"done.png", QSize(), QIcon.Normal, QIcon.Off)
        self.edit_path_label=QPixmap()
        self.edit_root_label=QPixmap()

        #------------------------------------- Declaration of parameters 
        self.INPpar_base=INPpar()
        self.INPpar:INPpar=self.TABpar
        self.INPpar_old:INPpar=self.TABpar_old
        self.defineSetTABpar(self.setINPpar)

        #------------------------------------- Callbacks 
        self.setupCallbacks()
        self.FlagSettingPar=False

        #------------------------------------- Initializing 
        if flagInit:
            self.initialize()

        #self.ParPointer.w=self.ParPointer.W=infoImages[5]
        #self.ParPointer.h=self.ParPointer.H=infoImages[6]

    def initialize(self):
        pri.Info.yellow(f'{"*"*20}   INPUT initialization   {"*"*20}')
        from .PaIRS_pypacks import basefold
        self.ui.edit_path.setFocus()
        self.ui.edit_path.setText(basefold)
        self.edit_path_action()
        INPpar_prev=self.TABpar_prev[0][0][0]
        self.getPinfoFromPath(INPpar_prev,[basefold,'']) 
        self.setTABpar_prev(0,0,0,True) #with bridge
        
    def setupCallbacks(self):
        #Callbacks
        self.ui.button_data.clicked.connect(lambda: downloadExampleData(self,'https://www.pairs.unina.it/web/PIV_data.zip'))

        self.ui.edit_path.textChanged.connect(self.edit_path_changing)
        self.ui.edit_path.editingFinished.connect(self.edit_path_finished)
        self.edit_path_callback=self.addParWrapper(self.edit_path_action,'Input folder path')
        self.ui.edit_path.returnPressed.connect(self.edit_path_callback) 
        self.ui.button_path.clicked.connect(\
            self.addParWrapper(self.button_path_callback,'Input folder path'))
        self.ui.edit_path.FunSetCompleterList=self.setPathCompleter

        self.ui.edit_root.textChanged.connect(self.edit_root_changing)
        self.ui.edit_root.editingFinished.connect(self.edit_root_finished)
        self.ui.edit_root.returnPressed.connect(\
            self.addParWrapper(self.edit_root_callback,'Pattern of image filenames'))
        self.ui.button_import.clicked.connect(\
            self.addParWrapper(self.button_import_callback,'Pattern of image filenames'))
        self.ui.edit_root.FunSetCompleterList=self.setRootCompleter

        self.setSpinCallbacks(['range_from','range_to'],['Number of the first image','Number of pairs'])
        self.ui.spin_range_from.valueChanged.connect(self.spin_range_from_callback)
        self.ui.spin_range_to.valueChanged.connect(self.spin_range_to_callback)
        fSpinSCallback=self.addParWrapper(self.spin_selected_callback,'Selection of pair')
        self.ui.spin_selected.valueChanged.connect(fSpinSCallback)
        fListSCallback=self.addParWrapper(self.list_images_callback,'Selection of pair')
        self.ui.list_images.currentRowChanged.connect(fListSCallback)

        self.ui.check_TR_sequence.stateChanged.connect(self.addParWrapper(self.check_TR_callback,'Time-resolved series'))
        self.ui.check_subtract.stateChanged.connect(self.addParWrapper(self.check_subtract_callback,'Subtract minimum'))

        self.setSpinxywhCallbacks()
        
#*************************************************** From Parameters to UI
    def setINPpar(self):
        self.FlagSettingPar=True
        #pri.Time.blue(1,'INPpar: beginning')
        self.ChangeText_path(self.INPpar.path)
        self.setPathLabel()
        self.setPathCompleter()
        self.ChangeText_root(self.INPpar.root)
        self.setRootCompleter()
        self.setRootLabel()
        if self.INPpar.FlagValidRoot in (0,-10):
            self.Disable_ImgObjects()   
        else:
            self.Enable_ImgObjects()   
        #pri.Time.blue(0,'INPpar: path-root')
        
        fields=['range_from','range_to','pinfo','FlagList']
        #if self.INPpar.isDifferentFrom(self.INPpar_old,[],fields):
        self.setListImages()
        #pri.Time.blue(0,'INPpar: list')
        self.ui.check_TR_sequence.setChecked(self.INPpar.flag_TR)
        self.ui.check_subtract.setChecked(self.INPpar.flag_min)
        self.setMinMaxSpin()
        if self.INPpar.isDifferentFrom(self.INPpar_old,self.INPpar.unchecked_fields,['pinfo']):
            self.INPpar.selected=imin_im_pair
        self.setValueSpin()
        self.FlagSettingPar=False
        #pri.Time.blue(0,'INPpar: end')

    def ChangeText_path(self,text): 
        text=myStandardPath(text)
        self.ui.edit_path.setText(text)
        
    def setPathLabel(self):
        if self.INPpar.FlagValidPath==1:
            self.ui.label_check_path.setPixmap(self.mapv)
            self.ui.label_check_path.setToolTip("This path exists! 😃")
        elif self.INPpar.FlagValidPath==0:
            self.ui.label_check_path.setPixmap(self.mapx)
            self.ui.label_check_path.setToolTip("This path does not exist! 😞")
        elif self.INPpar.FlagValidPath==-10:
            self.ui.label_check_path.setPixmap(self.mapw)
            self.ui.label_check_path.setToolTip("This path is currently under inspection! ⌛")
        #if self.INPpar.FlagValidPath in (0,-10):
            #self.ui.w_edit_root.setEnabled(False)
            #self.ui.button_import.setEnabled(False)
        #else:
            #self.ui.edit_root.setEnabled(True)
            #self.ui.button_import.setEnabled(True)
        self.edit_path_label=self.ui.label_check_path.pixmap()

    def setPathCompleter(self):
        self.edit_path_completer=QCompleter(self.INPpar.pathCompleter)
        self.edit_path_completer.setCompletionMode(QCompleter.CompletionMode(1))
        self.edit_path_completer.setModelSorting(QCompleter.ModelSorting(2))
        self.edit_path_completer.setWidget(self.ui.edit_path)
        if self.INPpar.path in self.INPpar.pathCompleter:
            k=self.INPpar.pathCompleter.index(self.INPpar.path)
            self.edit_path_completer.setCurrentRow(k) 
        self.ui.edit_path.setCompleter(self.edit_path_completer)
        self.ui.edit_path.FlagCompleter=True

    def ChangeText_root(self,text,*args):
        text=myStandardRoot(text)
        text=text.replace(';',' ; ')
        self.ui.edit_root.setText(text)
              
    def setFlagValidRoot(self,*args):
        if len(args): INPpar_prev=args[0]
        else: INPpar_prev=self.INPpar
        if INPpar_prev.FlagValidPath in (0,-10):
            INPpar_prev.FlagValidRoot=-10
        else:
            if  not len(INPpar_prev.list_eim):
                INPpar_prev.FlagValidRoot=0
            else:
                FlagExistAll=all(INPpar_prev.list_eim[INPpar_prev.list_ind_items[0]:INPpar_prev.list_ind_items[1]])
                if FlagExistAll:
                    INPpar_prev.FlagValidRoot=1
                else:
                    INPpar_prev.FlagValidRoot=-1
        
    def setRootLabel(self):
        if self.INPpar.FlagValidRoot==1:
            self.ui.label_check_root.setPixmap(self.mapv)
            self.ui.label_check_root.setToolTip("Files correctly identified! 😃")    
        elif self.INPpar.FlagValidRoot==0 or self.INPpar.FlagValidPath==0:
            self.ui.label_check_root.setPixmap(self.mapx)
            self.ui.label_check_root.setToolTip("There are no files with this filename root in the selected path! 😞")
        elif self.INPpar.FlagValidRoot==-1:
            self.ui.label_check_root.setPixmap(self.Lab_warning)
            self.ui.label_check_root.setToolTip("Some files seem missing: please, check! 🧐")
        elif self.INPpar.FlagValidRoot==-10:
            self.ui.label_check_root.setPixmap(self.mapw)
            self.ui.label_check_root.setToolTip("This pattern is currently under inspection! ⌛")
        #if self.INPpar.FlagValidRoot in (0,-10):
            #self.ui.edit_root.setEnabled(False)
            #self.ui.button_import.setEnabled(False)
        #else:
            self.ui.w_edit_root.setEnabled(True)
            #self.ui.button_import.setEnabled(True)
        self.edit_root_label=self.ui.label_check_root.pixmap()

    def setRootCompleter(self):
        roots=[r for k,r in enumerate(self.INPpar.Pinfo.root) if self.INPpar.Pinfo.nimg_tot[k]]
        self.edit_root_completer=QCompleter(roots)
        self.edit_root_completer.setCompletionMode(QCompleter.CompletionMode(1))
        self.edit_root_completer.setModelSorting(QCompleter.ModelSorting(2))
        self.edit_root_completer.setWidget(self.ui.edit_root)
        if len(roots):
            if self.INPpar.root in roots:
                k=roots.index(self.INPpar.root)
                self.edit_root_completer.setCurrentRow(k) 
        self.ui.edit_root.setCompleter(self.edit_root_completer)
        self.ui.edit_root.FlagCompleter=True
    
    
    def setMinMaxSpin(self):
        value_range_from=self.INPpar.range_from
        value_range_to=self.INPpar.range_to
        value_selected=self.INPpar.selected
        self.ui.spin_range_from.setMinimum(self.INPpar.pinfo.ind_in)
        self.ui.spin_range_from.setMaximum(self.INPpar.pinfo.ind_fin-(self.INPpar.pinfo.nfra==1)*1)
        self.newTip('spin_range_from')
        self.ui.spin_range_to.setMinimum(1)
        self.ui.spin_range_to.setMaximum(self.INPpar.npairs)
        self.newTip('spin_range_to')
        self.ui.spin_selected.setMinimum(imin_im_pair-1)
        self.ui.spin_selected.setMaximum(self.INPpar.npairs-1+imin_im_pair)
        self.setMinMaxSpinxywh()
        self.INPpar.range_from=value_range_from
        self.INPpar.range_to=value_range_to
        self.INPpar.selected=value_selected  

    def setValueSpin(self):
        self.ui.spin_range_from.setValue(self.INPpar.range_from)
        self.ui.spin_range_to.setValue(self.INPpar.range_to)
        self.ui.spin_selected.setValue(self.INPpar.selected)
        self.selectListItem()
        self.setValueSpinxywh()

    def Disable_ImgObjects(self):
        self.setMinMaxSpin()
        for nobj in range(len(self.spin_fields)):
            obj=getattr(self.ui,self.list_Spins[nobj])
            obj.setEnabled(False)
            field_value=getattr(self.INPpar_base,self.spin_fields[nobj])
            obj.setValue(field_value)
        self.ui.list_images.clear()
        self.ui.list_images.setEnabled(False)
        for nobj in range(len(self.TR_min_fields)):
            obj=getattr(self.ui,self.list_Image_Opt[nobj])
            obj.setEnabled(False)

    def Enable_ImgObjects(self):
        for nobj in range(len(self.list_Spins)):
            obj=getattr(self.ui,self.list_Spins[nobj])
            obj.setEnabled(True)
        self.ui.list_images.setEnabled(True)
        for nobj in range(len(self.list_Image_Opt)):
            obj=getattr(self.ui,self.list_Image_Opt[nobj])
            obj.setEnabled(True)

#*************************************************** Path and Images utilities
    def getPinfoFromPath(self,INPpar_prev,currpath_target):
        INPpar_prev: INPpar
        #INPpar_prev=self.INPpar_prev[ind_prev] 
        INPpar_prev.path=currpath_target[0]
        target=currpath_target[1]

        if os.path.exists(INPpar_prev.path):
            INPpar_prev.FlagValidPath=-10
            Pinfo=analysePath(INPpar_prev.path)
            INPpar_prev.FlagValidPath=1
            self.selectRootInPath(INPpar_prev,[Pinfo,target])
        else:
            INPpar_prev.FlagValidPath=INPpar_prev.FlagValidRoot=0
            INPpar_prev.Pinfo=patternInfoList()
            INPpar_prev.pinfo=patternInfoVar()
            INPpar_prev.root=''
            self.setInfoImages(INPpar_prev,[True,[]])
        return INPpar_prev

    @Slot(int,list)
    def selectRootInPath(self,INPpar_prev,Pinfo_target):
        INPpar_prev: INPpar
        Pinfo: patternInfoList
        #INPpar_prev=self.INPpar_prev[ind_prev]
        Pinfo=Pinfo_target[0]
        target=Pinfo_target[1]
        if Pinfo.pattern!=None:
            INPpar_prev.Pinfo=Pinfo.duplicate()
            if len(INPpar_prev.Pinfo.pattern):
                if target:
                    vk=[]
                    vnimg=[]
                    for k in range(len(INPpar_prev.Pinfo.pa)):
                        if INPpar_prev.Pinfo.pa[k].match(target):
                            vk.append(k)
                            vnimg.append(INPpar_prev.Pinfo.nimg_tot[k])
                    k=vk[np.argmax(np.asarray(vnimg))]    
                else:
                    k=np.argmax(np.asarray(Pinfo.nimg_tot))
                INPpar_prev.pinfo=INPpar_prev.Pinfo.extractPinfo(k)
                INPpar_prev.root=INPpar_prev.pinfo.root
                INPpar_prev.FlagValidRoot=-10
                self.setRoot(INPpar_prev,True)
            else:
                INPpar_prev.pinfo=patternInfoVar()
                INPpar_prev.root=''
                INPpar_prev.FlagValidRoot=0
                self.setInfoImages(INPpar_prev,[True,[]])
        return INPpar_prev
        
    def setRoot(self,INPpar_prev,flagDefault):
        INPpar_prev: INPpar
        #INPpar_prev=self.INPpar_prev[ind_prev]

        infoImages=createListImages(INPpar_prev.path,INPpar_prev.pinfo,INPpar_prev.flag_TR)
        self.setInfoImages(INPpar_prev,[flagDefault,infoImages])
        return INPpar_prev

    @Slot(int,list)
    def setInfoImages(self,INPpar_prev:INPpar,flagDefault_infoImages):
        INPpar_prev: INPpar
        #INPpar_prev=self.INPpar_prev[ind_prev]
        flagDefault=flagDefault_infoImages[0]
        infoImages=flagDefault_infoImages[1]
        
        if not len(infoImages):
            INPpar_prev.FlagValidRoot=0
            infoImages=[[],[],[],[],0,INPpar().W,INPpar().H,False]
        if flagDefault:
            INPpar_prev.FlagValidRoot=1
            flagTR=bool(infoImages[7])
            INPpar_prev.npairs=infoImages[4]
            INPpar_prev.nspa_eff=INPpar_prev.pinfo.nfra*(1+1*(bool(INPpar_prev.flag_TR)))
            INPpar_prev.nimg_eff=INPpar_prev.pinfo.nimg*INPpar_prev.nspa_eff-1*flagTR
            INPpar_prev.range_from=INPpar_prev.pinfo.ind_in
            INPpar_prev.range_to=INPpar_prev.npairs

            INPpar_prev.x=INPpar_prev.y=0
            INPpar_prev.w=INPpar_prev.W=infoImages[5]
            INPpar_prev.h=INPpar_prev.H=infoImages[6]

        INPpar_prev.list_Image_Files=infoImages[0]
        INPpar_prev.list_eim=infoImages[1]
        INPpar_prev.list_Image_numbers=infoImages[2]
        INPpar_prev.list_items=infoImages[3]
        ind_in=(INPpar_prev.range_from-INPpar_prev.pinfo.ind_in)*INPpar_prev.nspa_eff
        ind_fin=ind_in+INPpar_prev.range_to*2
        INPpar_prev.list_ind_items=[ind_in, ind_fin]
        self.setFlagValidRoot(INPpar_prev)
        return INPpar_prev
        
    def setListImages(self):
        FlagSettingPar=self.FlagSettingPar
        self.FlagSettingPar=True
        self.ui.list_images.clear()
        if not len(self.INPpar.list_Image_Files): return
        ind_in=(self.INPpar.range_from-self.INPpar.pinfo.ind_in)*self.INPpar.nspa_eff
        ind_fin=ind_in+self.INPpar.range_to*2
        self.INPpar.list_ind_items=self.INPpar.list_ind_items=[ind_in,ind_fin]
        
        listImage=[str(num+imin_im_pair)+":   "+im1+' - '+im2 for num,im1,im2 in\
                   zip(range(self.INPpar.range_to),self.INPpar.list_items[ind_in:ind_fin:2],self.INPpar.list_items[ind_in+1:ind_fin:2])]
        #listImage=[num+im for num,im in zip(self.list_Image_numbers[:nimg],self.list_Image_items[ind_in:ind_fin])]
        self.ui.list_images.addItems(listImage)
        self.FlagSettingPar=FlagSettingPar
        
    def getpinfofromRoot(self,INPpar_prev,path_pattern):
        INPpar_prev: INPpar
        #INPpar_prev=self.INPpar_prev[ind_prev]
        path=path_pattern[0]
        pattern=path_pattern[1]

        if INPpar_prev.root=='':
            INPpar_prev.pinfo=patternInfoVar()
            INPpar_prev.FlagValidRoot=0
        else:
            if pattern in INPpar_prev.Pinfo.root:
                k=INPpar_prev.Pinfo.root.index(pattern)
                pinfo=INPpar_prev.Pinfo.extractPinfo(k)
                INPpar_prev.FlagValidRoot=1
            else:
                INPpar_prev.FlagValidRoot=-10
                pinfo=analyseRoot(path,pattern)
            self.setNewpinfo(INPpar_prev,[pinfo])
        return INPpar_prev

    @Slot(int,list)
    def setNewpinfo(self,INPpar_prev,pinfo_):
        INPpar_prev: INPpar
        #INPpar_prev=self.INPpar_prev[ind_prev]

        pinfo=pinfo_[0] #if pinfo_[0].nimg_tot else INPpar_prev.pinfo
        if pinfo.root in INPpar_prev.Pinfo.root:
            k=INPpar_prev.Pinfo.root.index(pinfo.root)
        else:
            INPpar_prev.Pinfo=pinfo.addto(INPpar_prev.Pinfo)
            k=len(INPpar_prev.Pinfo.pattern)-1
        INPpar_prev.pinfo=INPpar_prev.Pinfo.extractPinfo(k)
        INPpar_prev.root=INPpar_prev.pinfo.root
        infoImages=createListImages(INPpar_prev.path,pinfo,INPpar_prev.flag_TR)
        flagDefault=True
        self.setInfoImages(INPpar_prev,[flagDefault,infoImages])      
        return INPpar_prev

#*************************************************** Edit path and root
    def edit_path_changing(self): 
        self.ui.label_check_path.setPixmap(QPixmap()) 
    
    def edit_path_finished(self): 
        self.ui.edit_path.setText(self.INPpar.path)
        self.setPathLabel()

    def edit_path_action(self,*args):
        if len(args): target=args[0]
        else: target=''
        currpath=myStandardPath(self.ui.edit_path.text())
        directory_path = myStandardPath(os.getcwd())
        if directory_path in currpath:
            currpath=currpath.replace(directory_path,'./')
        self.ui.edit_path.setText(currpath)
        flagNewPath=self.INPpar.path!=currpath
        self.INPpar.path=currpath
        self.INPpar.FlagValidPath=self.INPpar.FlagValidRoot=-10

        if not flagNewPath:
            if len(self.INPpar.list_Image_Files): target=self.INPpar.list_Image_Files[0]
            #FlagAddPar=-1
            FlagAddPar=+1
        else:
            if os.path.exists(self.INPpar.path):
                if self.INPpar.path in self.INPpar.pathCompleter:
                    self.INPpar.pathCompleter.pop(self.INPpar.pathCompleter.index(self.INPpar.path))
                self.INPpar.pathCompleter.insert(0,self.INPpar.path)
                if len(self.INPpar.pathCompleter)>10: self.INPpar.pathCompleter=self.INPpar.pathCompleter[:10]
            FlagAddPar=1
        fcallback_done=lambda i: self.getPinfoFromPath(i,[currpath,target])
        return [FlagAddPar,fcallback_done]
        
    def button_path_callback(self):
        directory = str(QFileDialog.getExistingDirectory(self,\
            "Choose a folder", dir=self.INPpar.path,options=optionNativeDialog))
        currpath='{}'.format(directory)
        if not currpath=='':
            self.ui.edit_path.setText(currpath)
            out_edit_path=self.edit_path_action()
            return out_edit_path
        else:
            return [-1,None]

    def edit_root_changing(self):
         self.ui.label_check_root.setPixmap(QPixmap()) 
    
    def edit_root_finished(self):
        self.ui.edit_root.setText(self.INPpar.root)
        self.setRootLabel()

    def edit_root_callback(self):
        currpatt=self.ui.edit_root.text()
        flagNewRoot=currpatt.replace(" ","")!=self.INPpar.root.replace(" ","")
        self.ui.edit_root.setText(currpatt)
        self.ui.edit_root.repaint()
        self.INPpar.root=currpatt
        self.INPpar.FlagValidRoot=-10
        if not flagNewRoot:
            #FlagAddPar=-1
            FlagAddPar=+1
        else:
            FlagAddPar=1
        fcallback_done=lambda i: self.getpinfofromRoot(i,[self.INPpar.path,currpatt])
        return [FlagAddPar,fcallback_done]
                        
    def button_import_callback(self):
        self.ui.label_check_root.setPixmap(self.mapw)
        filename, _ = QFileDialog.getOpenFileName(self,\
            "Select an image file of the sequence", filter=text_filter, dir=self.INPpar.path,\
                options=optionNativeDialog)
        filename=myStandardRoot('{}'.format(str(filename)))
        if not filename=='':
            directory_path = myStandardPath(os.getcwd())
            currpath, target = os.path.split(filename)
            currpath=myStandardPath(currpath)
            if directory_path in currpath:
                currpath=currpath.replace(directory_path,'./')
            if currpath==myStandardPath(self.ui.edit_path.text()):
                vk=[]
                vnimg=[]
                for k in range(len(self.INPpar.Pinfo.pa)):
                    if self.INPpar.Pinfo.pa[k].match(target): 
                        vk.append(k)
                        vnimg.append(self.INPpar.Pinfo.nimg_tot[k])
                k=vk[np.argmax(np.asarray(vnimg))]                
                self.ui.edit_root.setText(self.INPpar.Pinfo.root[k])
                out_edit_root=self.edit_root_callback()
                return out_edit_root
            else:
                self.ui.edit_path.setText(currpath)
                out_edit_path=self.edit_path_action(target)
                return out_edit_path
        else:
            return [-1,None]

#*************************************************** Image set controls
    def spin_range_from_callback(self):
        if not self.FlagSettingPar:
            flag=self.ui.spin_range_from.value()!=self.INPpar.range_from
            if flag:
                self.INPpar.range_from=self.ui.spin_range_from.value()
                if self.ui.spin_range_from.hasFocus():
                    self.spin_range_from_action()
                    self.setListImages()
                    self.ui.spin_range_from.setFocus()
            return [1,None]
        else:
            return [-1,None]
            
    def spin_range_from_action(self):
        value=self.ui.spin_range_from.value()
        ind_in=(value-self.INPpar.pinfo.ind_in)*self.INPpar.nspa_eff
        d=int((self.INPpar.nimg_eff-ind_in)/2)
        self.INPpar.list_ind_items[0]=ind_in
        self.ui.spin_range_to.setMaximum(d)
        self.newTip('spin_range_to')
        self.ui.spin_range_to.setValue(d)
        self.ui.spin_selected.setMaximum(d-1+imin_im_pair)
        
    def spin_range_to_callback(self):
        if not self.FlagSettingPar:
            flag=self.ui.spin_range_to.value()!=self.INPpar.range_to
            if flag:
                self.INPpar.range_to=self.ui.spin_range_to.value()
                if self.ui.spin_range_to.hasFocus():
                    self.spin_range_to_action()
                    self.setListImages()
                    self.ui.spin_range_to.setFocus()
            return [1,None]
        else:
            return [-1,None]
                
    def spin_range_to_action(self):
        value=self.ui.spin_range_to.value()
        value_selected=value-1+imin_im_pair
        if self.INPpar.selected>value_selected:
            self.INPpar.selected=value_selected
            self.ui.spin_selected.setValue(value_selected)
        self.ui.spin_selected.setMaximum(value_selected)
        
    def spin_selected_callback(self):
        if not self.FlagSettingPar:
            self.INPpar.selected=self.ui.spin_selected.value()
            if self.ui.spin_selected.hasFocus():
                self.spin_selected_action()
                self.ui.spin_selected.setFocus()
                return [0,None]
            else:
                return [-1,None]
            
    def spin_selected_action(self):
        self.INPpar.selected=self.ui.spin_selected.value()
        self.selectListItem()

    def selectListItem(self):
        ind=self.INPpar.selected-imin_im_pair
        self.ui.list_images.setCurrentRow(ind)

    def list_images_callback(self):
        if not self.FlagSettingPar:
            ind=self.ui.list_images.currentRow()
            self.ui.spin_selected.setValue(ind+imin_im_pair)
            self.INPpar.selected=self.ui.spin_selected.value()
            return [0,None]
        else:
            return [-1,None]

#*************************************************** Sequence type and pre-proc
    def check_TR_callback(self):
        if self.ui.check_TR_sequence.hasFocus():
            self.INPpar.flag_TR=self.ui.check_TR_sequence.isChecked()
            fcallback_done=lambda i: self.setRoot(i,True)
            return [1,fcallback_done]
        else:
            return [-1,None]

    def check_subtract_callback(self):
        if self.ui.check_subtract.hasFocus():
            self.INPpar.flag_min=self.ui.check_subtract.isChecked()
            return [1,None]
        else:
            return [-1,None]

if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Import_Tab(None)
    object.show()
    app.exec()
    app.quit()
    app=None