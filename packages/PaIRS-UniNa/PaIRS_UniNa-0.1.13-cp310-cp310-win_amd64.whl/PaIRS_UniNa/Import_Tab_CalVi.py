import PySide6.QtGui
from .ui_Import_Tab_CalVi import*
#from Import_Tab_tools import*
from .TabTools import*

#bufferSizeLimit=2000*1e6  #bytes

class INPpar_CalVi(TABpar):
    def __init__(self):
        self.setup()
        super().__init__()
        self.name='INPpar_CalVi'
        self.surname='INPUT_Tab_CalVi'
        self.unchecked_fields+=['FlagValidPath','FlagValidPathOut','FlagValidRootOut']

    def setup(self):
        self.FlagValidPath = 1
        self.path = './'
        self.root = ''
        self.ext = ''
        self.cams=[]
        self.filenames=[]
        self.flagImages=[]
        self.plapar=[]
        self.x = -1
        self.y = -1
        self.w = 0
        self.h = 0
        self.W = 0
        self.H = 0
        self.row=0
        self.col=0
        self.list_Image_Files=[]
        self.list_eim=[]

        self.FlagOptPlane=0

        self.FlagSameAsInput=1
        self.FlagValidPathOut=1
        self.pathout='./'
        self.FlagValidRootOut=1
        self.radout='pyCal'

        self.errorMessage=''
        self.FlagReadCalib=False

        self.pathCompleter=basefold_DEBUGOptions
        
class Import_Tab_CalVi(gPaIRS_Tab):

    class Import_Tab_Signals(gPaIRS_Tab.Tab_Signals):
        list_selection=Signal()
        pass

    def __init__(self,*args):
        parent=None
        flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: flagInit=args[1]
        super().__init__(parent,Ui_ImportTab_CalVi,INPpar_CalVi)
        self.signals=self.Import_Tab_Signals(self)

        #------------------------------------- Graphical interface: widgets
        self.ui: Ui_ImportTab_CalVi
        ui=self.ui
        ui.spin_x.addwid=[ui.spin_w]
        ui.spin_y.addwid=[ui.spin_h]

        self.setupWid()  #---------------- IMPORTANT  
        
        #------------------------------------- Graphical interface: miscellanea
        self.mapx  = QPixmap(''+ icons_path +'redx.png')
        self.mapv  = QPixmap(''+ icons_path +'greenv.png')
        self.mapw  = QPixmap(''+ icons_path +'waiting_c.png')
        self.Lab_warning=QPixmap(u""+ icons_path +"warning.png")

        self.list_Path_Root=["edit_path","button_path","edit_cams","button_import"]
        self.list_Spins=["spin_x","spin_y","spin_w","spin_h"]
        self.list_Image_Opt=["radio_cam"]
        self.list_List_Images=["list_images"]
        self.list_All=self.list_Path_Root[:]+self.list_Spins[:]+self.list_Image_Opt[:]+self.list_List_Images[:]
        self.spin_fields=("x","y","w","h")

        self.edit_path_label=QPixmap()
        self.edit_cams_label=QPixmap()

        self.tableHeaders =[self.ui.list_images.horizontalHeaderItem(i).text() for i in range(self.ui.list_images.columnCount())]
        header = self.ui.list_images.horizontalHeader()     
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        #header.setMinimumSectionSize(int(self.minimumWidth()/2))
        #header.setMaximumSectionSize(int(self.maximumWidth()/2))
        self.ui.list_images.InfoLabel=self.ui.label_info
        self.ui.list_images.DeleteButton=self.ui.button_delete
        #self.ui.list_images.addfuncreturn['plapar']=self.updatePlanePar
        #self.ui.list_images.addfuncout['plapar']=self.updatePlanePar
        self.ui.label_info.hide()

        #------------------------------------- Declaration of parameters 
        self.INPpar_base=INPpar_CalVi()
        self.INPpar_old:INPpar_CalVi=self.TABpar_old
        self.INPpar:INPpar_CalVi=self.TABpar
        self.defineSetTABpar(self.setINPpar)

        self.bufferImg={}
        self.bufferSize=0

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
        #self.ui.edit_path.setFocus()
        self.ui.edit_path.setText(basefold)
        self.edit_path_action()
        self.setTABpar(True) #with bridge
        
    def setupCallbacks(self):
        #Callbacks
        self.ui.button_data.clicked.connect(lambda: downloadExampleData(self,'https://www.pairs.unina.it/web/Calibration_data.zip'))

        self.ui.edit_path.textChanged.connect(self.edit_path_changing)
        self.ui.edit_path.editingFinished.connect(self.edit_path_finished)
        self.edit_path_callback=self.addParWrapper(self.edit_path_action,'Input folder path')
        self.ui.edit_path.returnPressed.connect(self.edit_path_callback) 
        self.ui.button_path.clicked.connect(\
            self.addParWrapper(self.button_path_callback,'Input folder path'))
        self.ui.edit_path.FunSetCompleterList=self.setPathCompleter

        self.ui.radio_cam.toggled.connect(self.addParWrapper(self.radio_cam_callback,'_cam* in filename'))
        self.ui.edit_cams.editingFinished.connect(self.addParWrapper(self.edit_cams_callback,'Camera id. numbers'))

        self.button_import_callback=self.addParWrapper(self.button_import_action,'Importing of target images')
        self.ui.button_import.clicked.connect(self.button_import_callback)
        self.button_import_plane_callback=self.addParWrapper(self.button_import_plane_action,'Importing of plane parameters')
        self.ui.button_import_plane.clicked.connect(self.button_import_plane_callback)
        self.button_up_callback= self.addParWrapper(lambda: self.button_updown_callback(-1),'Order of target images')
        self.ui.button_up.clicked.connect(self.button_up_callback)
        self.button_down_callback= self.addParWrapper(lambda: self.button_updown_callback(+1),'Order of target images')
        self.ui.button_down.clicked.connect(self.button_down_callback)
        self.button_delete_callback=self.addParWrapper(self.button_delete_action,'Deleting target images')
        self.ui.button_delete.clicked.connect(self.button_delete_callback)
        self.button_clean_callback=self.addParWrapper(self.button_clean_action,'Cleaning the image list')
        self.ui.button_clean.clicked.connect(self.button_clean_callback)
        self.ui.list_images.contextMenuEvent=lambda e: self.listContextMenuEvent(self.ui.list_images,e)

        self.ui.list_images.cellChanged.connect(self.addParWrapper(self.updatePlanePar,'Plane parameters'))
        self.ui.list_images.itemSelectionChanged.connect(self.addParWrapper(self.list_selection,'Item selection'))

        self.setSpinxywhCallbacks()

        self.ui.edit_path_out.textChanged.connect(self.edit_path_out_changing)
        #self.ui.edit_path_out.editingFinished.connect(self.edit_path_out_finished)
        self.ui.edit_root_out.textChanged.connect(self.edit_root_out_changing)
        #self.ui.edit_root_out.editingFinished.connect(self.edit_root_out_finished)

        signals=[["clicked"],
                 ["toggled"],
                 ["editingFinished"]]
        fields=["button",
                "check",
                "edit"]
        names=[ ['path_out'], #button,
                ['same_as_inp'], #check
                ['root_out','path_out']] #edit
        tips=[ ['Output folder path'], #button,
                ['Output folder path same as input'], #check
                ['Root of output files','Output folder path']] #edit
        
        for f,N,S,T in zip(fields,names,signals,tips):
            for n,t in zip(N,T):
                wid=getattr(self.ui,f+"_"+n)
                fcallback=getattr(self,f+"_"+n+"_callback")
                fcallbackWrapped=self.addParWrapper(fcallback,t)
                for s in S:
                    sig=getattr(wid,s)
                sig.connect(fcallbackWrapped)
  
    def listContextMenuEvent(self, list_images:QTableWidget, event):
        item=list_images.currentItem()
        if not item: return
        menu=QMenu(list_images)
        buttons=['import', 'import_plane',
                 -1,'down','up',
                 -1,'delete','clean']
        name=[]
        act=[]
        fun=[]
        for k,nb in enumerate(buttons):
            if type(nb)==str:
                b:QPushButton=getattr(self.ui,'button_'+nb)
                if b.isVisible() and b.isEnabled():
                    if hasattr(self,'button_'+nb+'_callback'):
                        name.append(nb)
                        act.append(QAction(b.icon(),toPlainText(b.toolTip().split('.')[0]),list_images))
                        menu.addAction(act[-1])
                        callback=getattr(self,'button_'+nb+'_callback')
                        fun.append(callback)
            else:
                if len(act): menu.addSeparator()

        if len(act):
            pri.Callback.yellow(f'||| Opening image list context menu |||')
            action = menu.exec_(list_images.mapToGlobal(event.pos()))
            for nb,a,f in zip(name,act,fun):
                if a==action: 
                    f()
                    break
        else:
            toolTip=item.toolTip()
            item.setToolTip('')

            message='No context menu available! Please, pause processing.'
            tip=QToolTip(self)
            toolTipDuration=self.toolTipDuration()
            self.setToolTipDuration(3000)
            tip.showText(QCursor.pos(),message)
            self.setToolTipDuration(toolTipDuration)
            item.setToolTip(toolTip)

#*************************************************** From Parameters to UI
    def setINPpar(self):
        self.FlagSettingPar=True
        #pri.Time.blue(1,'INPpar: beginning')
        self.ChangeText_path(self.INPpar.path)
        self.INPpar.FlagValidPath=os.path.exists(self.INPpar.path)
        self.setPathLabel()
        self.setPathCompleter()
        self.set_cams()
        self.set_list_images_items()
        if self.INPpar.FlagValidPath:
            self.Enable_ImgObjects()   
        else:
            self.Disable_ImgObjects()   

        flagSelect=self.ui.list_images.currentRow()>-1
        self.ui.button_down.setEnabled(flagSelect)
        self.ui.button_up.setEnabled(flagSelect)
        self.ui.button_delete.setEnabled(flagSelect)
        
        #pri.Time.blue(0,'INPpar: path-root')
        
        #pri.Time.blue(0,'INPpar: list')
        x=self.TABpar.x
        y=self.TABpar.y
        w=self.TABpar.w
        h=self.TABpar.h
        self.setMinMaxSpinxywh()
        self.TABpar.x=x
        self.TABpar.y=y
        self.TABpar.w=w
        self.TABpar.h=h
        self.setValueSpinxywh()

        self.ui.check_same_as_inp.setChecked(self.INPpar.FlagSameAsInput)
        self.check_same_as_inp_action()  #todo GP: credo sia ridondante ma avevo dei problemi
        self.ui.w_OutputFolder.setEnabled(not self.INPpar.FlagSameAsInput)
        self.ui.edit_path_out.setText(self.INPpar.pathout)
        self.setFlagValidPathOut()
        self.setPathOutLabel()
        self.ui.w_button_path_out.setEnabled(not self.INPpar.FlagSameAsInput)
        self.ui.edit_root_out.setText(self.INPpar.radout)
        self.setFlagValidRootOut()
        self.setRootOutLabel()

        self.FlagSettingPar=False
        #self.signals.list_selection.emit()
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
        self.ui.edit_cams.setText(text)

    def Disable_ImgObjects(self):
        for nobj in range(len(self.spin_fields)):
            obj=getattr(self.ui,self.list_Spins[nobj])
            obj.setEnabled(False)
            field_value=getattr(self.INPpar_base,self.spin_fields[nobj])
            obj.setValue(field_value)
        self.ui.w_InputImg.setVisible(False)
        self.ui.list_images.setEnabled(False)
        self.ui.w_SizeImg.setVisible(False)
        for nobj in range(len(self.list_Image_Opt)):
            obj=getattr(self.ui,self.list_Image_Opt[nobj])
            obj.setEnabled(False)
        self.ui.button_import_plane.setEnabled(False)
        self.ui.button_delete.setEnabled(False)
        self.ui.button_clean.setEnabled(False)
        
    def Enable_ImgObjects(self):
        for nobj in range(len(self.list_Spins)):
            obj=getattr(self.ui,self.list_Spins[nobj])
            obj.setEnabled(len(self.INPpar.filenames))
        self.ui.w_InputImg.setVisible(len(self.INPpar.cams))
        self.ui.list_images.setEnabled(True)
        self.ui.w_SizeImg.setVisible(len(self.INPpar.filenames))
        for nobj in range(len(self.list_Image_Opt)):
            obj=getattr(self.ui,self.list_Image_Opt[nobj])
            obj.setEnabled(True)
        self.ui.button_import_plane.setEnabled(len(self.INPpar.filenames))
        self.ui.button_delete.setEnabled(len(self.INPpar.filenames))
        self.ui.button_clean.setEnabled(len(self.INPpar.filenames))


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
        self.set_currpath(currpath)
        if os.path.exists(currpath):
            if currpath in self.INPpar.pathCompleter:
                self.INPpar.pathCompleter.pop(self.INPpar.pathCompleter.index(currpath))
            self.INPpar.pathCompleter.insert(0,currpath)
            if len(self.INPpar.pathCompleter)>10: self.INPpar.pathCompleter=self.INPpar.pathCompleter[:10]
        self.check_same_as_inp_action()
        
    def set_currpath(self,currpath,flagAdjustList=True):
        oldpath=self.INPpar.path
        self.ui.edit_path.setText(currpath)
        self.INPpar.path=currpath

        if os.path.exists(currpath):
            self.INPpar.FlagValidPath=1
            #if oldpath!=currpath:
            #    self.reset_list_images()
        else:
            self.INPpar.FlagValidPath=0
            self.INPpar.cams=[]
        if flagAdjustList: self.adjust_list_images()

    def reset_list_images(self):
        self.INPpar.filenames=[]
        self.INPpar.plapar=[]
        self.INPpar.x = self.INPpar.y = -1
        self.INPpar.w = self.INPpar.h = 0
        self.INPpar.W = self.INPpar.H = 0
        self.INPpar.row=0
        self.INPpar.col=0

    def button_path_callback(self):
        directory = str(QFileDialog.getExistingDirectory(self,\
            "Choose a folder", dir=self.INPpar.path,options=optionNativeDialog))
        currpath='{}'.format(directory)
        if not currpath=='':
            self.ui.edit_path.setText(currpath)
            self.edit_path_action()
    
    def radio_cam_callback(self):
        if self.ui.radio_cam.isChecked():
            if not len(self.INPpar.cams):
                ncam=0
                for f in self.INPpar.filenames:
                    pats=re.findall('_cam\d+', f)
                    if len(pats):
                        ncam=int(pats[-1].replace("_cam",""))
                        break
                self.INPpar.cams=[ncam]
                self.adjust_list_images()
            else:
                return
        else:
            if len(self.INPpar.cams):
                scam=str(self.INPpar.cams[0])
                self.INPpar.filenames=[f.replace('*',scam) for f in self.INPpar.filenames]
                self.INPpar.cams=[]
                self.adjust_list_images()
            else:
                return
        
    def edit_cams_callback(self):
        text=self.ui.edit_cams.text()
        split_text=re.split('(\d+)', text)[1:-1:2]
        a=np.array([int(i) for i in split_text],dtype=np.intc)
        indexes = np.unique(a, return_index=True)[1]
        self.INPpar.cams=[a[index] for index in sorted(indexes)]
        self.check_cams()
        self.adjust_list_images()
                 
    def button_import_action(self):
        filenames, _ = QFileDialog.getOpenFileNames(self,\
            "Select an image file of the sequence", filter=text_filter, dir=self.INPpar.path,\
                options=optionNativeDialog)
        if len(filenames):
            oldpath=self.INPpar.path
            filename0=myStandardRoot('{}'.format(str(filenames[0])))
            directory_path = myStandardPath(os.getcwd())
            currpath, target = os.path.split(filename0)
            currpath=myStandardPath(currpath)
            if directory_path in currpath:
                currpath=currpath.replace(directory_path,'./')
            self.set_currpath(currpath,flagAdjustList=False)
            if self.INPpar.FlagValidPath:
                f_new=[]
                f_warning=[]
                for f in filenames:
                    f=os.path.basename(f)
                    FlagNew=True
                    if len(self.INPpar.cams): 
                        fsplitted=re.split('_cam\d+', f)
                        if len(fsplitted)>1:
                            fsplitted.insert(-1,'_cam*')
                            f="".join(fsplitted)
                        else:
                            f_warning.append(f) #redundant
                            FlagNew=False
                    if f and not f in self.INPpar.filenames and not f in f_new and FlagNew:
                        f_new.append(f)
                if len(f_new):
                    for t in f_new:
                        self.INPpar.filenames.append(t)
                        if self.INPpar.FlagOptPlane:
                            self.INPpar.plapar.append([float(0)]*6)
                        else:
                            self.INPpar.plapar.append([float(0)])
                else:
                    self.set_currpath(oldpath,flagAdjustList=False)
                if len(f_warning):
                    list_img_warn=';\n'.join(f_warning)
                    Message=f'The following files located in the path {currpath} do not contain the pattern _cam* in their name and will not be included in the list of image files for the calibration process:\n{list_img_warn}.'
                    warningDialog(self,Message)
            self.adjust_list_images()
        return

    def button_import_plane_action(self):
        plaparName, _ = QFileDialog.getOpenFileName(self,\
            "Select a plane parameter file", filter=f'*{outExt.pla}',\
                dir=self.INPpar.path,\
                options=optionNativeDialog)
        if not plaparName: return
        try:
            if os.path.exists(plaparName):
                with open(plaparName, 'r') as file:
                    data=file.read()
                    dp=eval(data)
                    pass
        except:
            WarningMessage=f'Error with loading the file: {plaparName}\n'
            warningDialog(self,WarningMessage)
        else:
            try:
                if len(self.INPpar.plapar[self.INPpar.row])==1:
                    self.INPpar.plapar[self.INPpar.row]=[round(dp['z (mm)'],3)]
                else:
                    self.INPpar.plapar[self.INPpar.row]=[round(p,3) for p in list(dp.values())]
            except:
                WarningMessage=f'Error with setting the plane parameters read from file: {plaparName}\n'
                warningDialog(self,WarningMessage)

    def button_delete_action(self):
        k=self.INPpar.row=self.ui.list_images.currentRow()
        if k>-1:
            self.INPpar.filenames.pop(k)
            self.INPpar.plapar.pop(k)
        self.adjust_list_images()
    
    def button_clean_action(self):
        """
        for k in range(len(self.INPpar.filenames)):
            self.INPpar.row=0
            self.INPpar.filenames.pop(0)
            self.INPpar.plapar.pop(0)
            self.adjust_list_images()
        """
        self.reset_list_images()
        self.adjust_list_images()
        #"""
        return
        
    def button_updown_callback(self,d):
        k=self.ui.list_images.currentRow()
        if d==-1 and k==0: return
        if d==+1 and k==len(self.INPpar.filenames)-1: return
        self.INPpar.row+=d
        filename=self.INPpar.filenames.pop(k)
        self.INPpar.filenames.insert(k+d,filename)
        par=self.INPpar.plapar.pop(k)
        self.INPpar.plapar.insert(k+d,par)
        self.adjust_list_images()
        self.ui.list_images.setFocus()
        return [0,None]

    def list_selection(self):
        self.ui.list_images.resizeInfoLabel()
        flagSelect=self.ui.list_images.currentRow()>-1
        self.ui.button_down.setEnabled(flagSelect)
        self.ui.button_up.setEnabled(flagSelect)
        self.ui.button_delete.setEnabled(flagSelect)

        self.INPpar.row=self.ui.list_images.currentRow()
        self.INPpar.col=self.ui.list_images.currentColumn()
        self.signals.list_selection.emit()
        return [-1,None]

#*************************************************** Image set controls
    def set_cams(self):
        flag=len(self.INPpar.cams)>0
        self.ui.radio_cam.setChecked(flag)
        self.ui.w_InputImg.setEnabled(flag)
        if flag:
            self.INPpar.root=", ".join([str(v) for v in self.INPpar.cams])
        else:
            self.INPpar.root=''
        self.ChangeText_root(self.INPpar.root)
        return 
       
    def check_cams(self):
        if self.father:
            if len(self.INPpar.cams)>1 and self.father.w_Process.PROpar.CalibProcType==0:
                warningDialog(self,'Standard calibration can be performed only one camera at once! The first camera identification number will be retained for the current configuration.')
                self.INPpar.cams=[self.INPpar.cams[0]]
        
    def adjust_list_images(self):
        #self.set_cams()
        #deleting filenames not compatible with the option _cam* in the filename
        flag_ncam=len(self.INPpar.cams)
        ind_del=[]
        for k,f in enumerate(self.INPpar.filenames):
            if (not '_cam' in f and flag_ncam) or\
                ('_cam*' in f and not flag_ncam):
                ind_del.append(k)
        for kk in range(len(ind_del)-1,-1,-1):
            k=ind_del[kk]
            self.INPpar.filenames.pop(k)
            self.INPpar.plapar.pop(k)
        
        #check that the filename contains * and not an identifier number
        if len(self.INPpar.cams):
            for k,f in enumerate(self.INPpar.filenames):
                if '_cam*' in f: continue
                fsplitted=re.split('_cam\d+', f)
                fsplitted.insert(-1,'_cam*')
                f="".join(fsplitted)
                self.INPpar.filenames[k]=f
        f_unique=[]
        plapar_unique=[]
        for f,p in zip(self.INPpar.filenames,self.INPpar.plapar):
            if not f in f_unique: 
                f_unique.append(f)
                plapar_unique.append(p)
        self.INPpar.filenames=f_unique
        self.INPpar.plapar=plapar_unique

        self.INPpar.list_Image_Files=[]
        self.INPpar.list_eim=[]
        flagImgSize=False
        self.INPpar.row=min([len(self.INPpar.filenames),self.INPpar.row])
        for k,f in enumerate(self.INPpar.filenames):
            if flag_ncam:
                list_Image_Files_camk=[self.INPpar.path+f.replace("*",str(ncam)) for ncam in self.INPpar.cams]
            else:
                list_Image_Files_camk=[self.INPpar.path+f]

            list_eim_camk=[os.path.exists(fk) for fk in list_Image_Files_camk]
            self.INPpar.list_Image_Files.append(list_Image_Files_camk)
            self.INPpar.list_eim.append(list_eim_camk)

            if not flagImgSize:
                try:
                    im = Image.open(list_Image_Files_camk[0])
                    self.INPpar.ext=os.path.splitext(list_Image_Files_camk[0])[-1]
                    pri.General.blue(f'File extension: {self.INPpar.ext}')
                    flagImgSize=True
                except:
                    pri.Error.blue(f'Error opening image file: {list_Image_Files_camk[0]}')
                else:
                    self.INPpar.W,self.INPpar.H=im.size
                    if self.INPpar.w<1 or self.INPpar.w>self.INPpar.W:
                        self.INPpar.w=self.INPpar.W
                    if self.INPpar.h<1 or self.INPpar.H>self.INPpar.H:
                        self.INPpar.h=self.INPpar.H
                    if self.INPpar.x<0: self.INPpar.x=0
                    elif self.INPpar.x>self.INPpar.W-self.INPpar.w: self.INPpar.x=self.INPpar.W-self.INPpar.w
                    if self.INPpar.y<0: self.INPpar.y=0
                    elif self.INPpar.y>self.INPpar.H-self.INPpar.h: self.INPpar.y=self.INPpar.H-self.INPpar.h
        return
                
    def set_list_images_items(self):
        self.listClear()
        self.INPpar.flagImages=[0]*len(self.INPpar.filenames)
        for k,f in enumerate(self.INPpar.filenames):
            c=self.ui.list_images.rowCount()
            self.ui.list_images.insertRow(c)
            list_eim_camk=self.INPpar.list_eim[k]

            item_filename=QTableWidgetItem(f)
            item_filename.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
            item_filename.setToolTip(f)
            self.ui.list_images.setItem(c, 0, item_filename)
            if self.INPpar.row==k and self.INPpar.col==0: 
                item_filename.setSelected(True)
                self.ui.list_images.setCurrentItem(item_filename)

            if self.INPpar.FlagOptPlane:
                tiptext='Plane parameters: \u03B2 (°), \u03B1 (°), \u03B3 (°), x (mm), y (mm), z (mm)'
            else:
                tiptext='Plane parameters: z (mm)'
            tooltip=QLabel()
            tooltip.setTextFormat(Qt.TextFormat.RichText)
            tooltip.setText(tiptext)

            item_parameters=QTableWidgetItem(", ".join([str(s) for s in self.INPpar.plapar[k]]))
            item_parameters.setToolTip(tooltip.text())
            self.ui.list_images.setItem(c, 1, item_parameters)

            message='' 
            tiptext=[]
            if len(self.INPpar.plapar[k])==0:
                message+="⚠"
                tiptext+=[f"⚠︎: Corresponding plane parameters are not defined!"]
                self.INPpar.flagImages[k]|=1
            for q in range(k):
                if self.INPpar.plapar[k]==self.INPpar.plapar[q]:
                    message+="⚠"
                    tiptext+=[f"⚠︎: Plane parameters are coincident with those of plane {'#'} ({q})!"]
                    self.INPpar.flagImages[k]|=2
                    break
            if not all(list_eim_camk):
                message+="❌"
                if len(self.INPpar.cams):
                    cams=",".join([str(self.INPpar.cams[kk]) for kk,e in enumerate(list_eim_camk) if not e])
                    tiptext+=[f"❌: Image files for cameras {'#'} ({cams}) are missing!"]
                else:
                    tiptext+=[f"❌: Image files is missing!"]
                self.INPpar.flagImages[k]|=4
            if tiptext:
                tiptext=f"<br>".join(tiptext)
            else:
                message="✅"
                tiptext='✅: Check if the values of the plane parameters are correct!'
            tooltip=QLabel()
            tooltip.setTextFormat(Qt.TextFormat.RichText)
            tooltip.setText(tiptext)
            if self.INPpar.row==k and self.INPpar.col==1: 
                item_parameters.setSelected(True)
                self.ui.list_images.setCurrentItem(item_parameters)

            item_message=QTableWidgetItem(message)
            item_message.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
            item_message.setToolTip(tooltip.text())
            self.ui.list_images.setItem(c, 2, item_message)
            if self.INPpar.row==k and self.INPpar.col==2: 
                item_message.setSelected(True)
                self.ui.list_images.setCurrentItem(item_message)
        
        self.errorMessage()
        self.ui.list_images.resizeInfoLabel()
        return

    def errorMessage(self):
        self.INPpar.errorMessage=''
        if not len(self.INPpar.flagImages):
            self.INPpar.errorMessage+='Select a valid set of target image files!\n\n'
        if not self.INPpar.FlagValidPathOut:
            self.INPpar.errorMessage+='Choose a valid path for the output folder!\n\n'
        if not self.INPpar.FlagValidRootOut:
            self.INPpar.errorMessage+='Specify a valid root for the name of the output files!\n\n'
        if any(self.INPpar.flagImages):
            errorFiles=[[],[]]
            for k,f in enumerate(self.INPpar.flagImages):
                if f&3: errorFiles[0].append(self.INPpar.filenames[k])
                elif f&4: errorFiles[1].append(self.INPpar.filenames[k])
            if len(errorFiles[0]) or len(errorFiles[1]):
                errorMessage=''
                if len(errorFiles[0]):
                    errList=f";\n   ".join(errorFiles[0])
                    errorMessage+=f'Define appropriately the plane parameters for the following images:\n   {errList}.\n\n'         
                if len(errorFiles[1]):
                    errList=f";\n   ".join(errorFiles[1])
                    errorMessage+=f'Check for missing files related to the following images:\n   {errList}.'         
                #pri.Error.blue(errorMessage)
            self.INPpar.errorMessage+=errorMessage
        if self.INPpar.errorMessage:
            self.INPpar.errorMessage='Please check the following issues before starting calibration!\n\n'+self.INPpar.errorMessage

    def listClear(self):
        self.ui.list_images.clear()
        nRow=self.ui.list_images.rowCount()
        for k in range(nRow):
            self.ui.list_images.removeRow(self.ui.list_images.rowAt(k))
        self.ui.list_images.setHorizontalHeaderLabels(self.tableHeaders)

    def updatePlanePar(self):
        if self.ui.list_images.currentColumn()==1:
            r=self.ui.list_images.currentRow()
            item=self.ui.list_images.item(r,1)
            text=item.text()
            oldtext=", ".join([str(s) for s in self.INPpar.plapar[r]])
            if text!=oldtext:
                #fex=re.compile('[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)')
                if self.INPpar.FlagOptPlane:
                    tsplitted=re.split(',',text)
                    #pri.Callback.white(tsplitted)
                    if len(tsplitted)==6 and all([isfloat(p) for p in tsplitted]):
                        self.INPpar.plapar[r]=[float(p) for p in tsplitted]
                else:
                    if isfloat(text):
                        self.INPpar.plapar[r]=[float(text)]
                pri.Callback.green(f'***** new par {", ".join([str(s) for s in self.INPpar.plapar[r]])}')

#*************************************************** Output
#******************** path
    def check_same_as_inp_callback(self):
        self.INPpar.FlagSameAsInput=self.ui.check_same_as_inp.isChecked()
        self.check_same_as_inp_action()
        
    def check_same_as_inp_action(self):
        if self.INPpar.FlagSameAsInput:
            self.INPpar.pathout=self.INPpar.path
        self.setFlagValidPathOut()

    def edit_path_out_changing(self): 
         self.ui.label_check_path_out.setPixmap(QPixmap()) 
    
    def edit_path_out_finished(self): 
        self.ui.edit_path_out.setText(self.INPpar.pathout)
        self.setPathOutLabel()

    def edit_path_out_callback(self):
        currpath=myStandardPath(self.ui.edit_path_out.text())     
        directory_path = myStandardPath(os.getcwd())
        if directory_path in currpath:
            currpath=currpath.replace(directory_path,'./')         
        self.INPpar.pathout=currpath        
        self.setFlagValidPathOut()

    def setFlagValidPathOut(self):
        self.INPpar.FlagValidPathOut=os.path.exists(self.INPpar.pathout)
    
    def setPathOutLabel(self):
        if self.INPpar.FlagValidPathOut:
            self.ui.label_check_path_out.setPixmap(self.mapv)
            self.ui.label_check_path_out.setToolTip("This path exists! 😃")
        else:
            self.ui.label_check_path_out.setPixmap(self.mapx)
            self.ui.label_check_path_out.setToolTip("This path does not exist! 😞")

    def button_path_out_callback(self):
        directory = str(QFileDialog.getExistingDirectory(self,\
            "Choose a folder", dir=self.INPpar.pathout,options=optionNativeDialog))
        currpath='{}'.format(directory)
        if not currpath=='':
            self.ui.edit_path_out.setText(currpath)
            self.edit_path_out_callback()

#******************** root
    def edit_root_out_changing(self):
         self.ui.label_check_root.setPixmap(QPixmap()) 
    
    def edit_root_out_finished(self): 
        self.ui.edit_root_out.setText(self.INPpar.radout)
        self.setRootOutLabel()

    def edit_root_out_callback(self):
        entry=myStandardRoot(self.ui.edit_root_out.text())
        self.ui.edit_root_out.setText(entry)
        self.INPpar.radout=entry
        self.setFlagValidRootOut()

    def setFlagValidRootOut(self,*args):
        if len(args): INPpar_prev=args[0]
        else: INPpar_prev=self.INPpar
        ext='.cal'
        FlagExistPath=INPpar_prev.FlagValidPathOut
        if FlagExistPath:
            currpath=myStandardPath(INPpar_prev.pathout)
        else:
            currpath='./'
        pattern=myStandardRoot(currpath+INPpar_prev.radout)+'*'+ext
        FlagExist=False
        if FlagExistPath:
            files=findFiles_sorted(pattern)
            FlagExist=len(files)>0
        if  FlagExist: 
            INPpar_prev.FlagValidRootOut=-2
        else:
            try:
                filename=pattern.replace('*','a0')+'.delmeplease'
                open(filename,'w')
            except:
                FlagDeleteFile=False
                INPpar_prev.FlagValidRootOut=0
            else:
                FlagDeleteFile=True
                INPpar_prev.FlagValidRootOut=1
            finally:
                if FlagDeleteFile:
                    os.remove(filename)

    def setRootOutLabel(self):
        if self.INPpar.FlagValidRootOut==-2:
            if not self.INPpar.FlagReadCalib:
                self.ui.label_check_root.setPixmap(self.Lab_warning)
                self.ui.label_check_root.setToolTip("There are files with the same filename root in the selected path! 😰")
            else:
                self.ui.label_check_root.setPixmap(self.mapv)
                self.ui.label_check_root.setToolTip("Filename root admitted! 😃")
        elif self.INPpar.FlagValidRootOut==0:
            self.ui.label_check_root.setPixmap(self.mapx)
            self.ui.label_check_root.setToolTip("Filename root not admitted! 😞")
        if self.INPpar.FlagValidRootOut==1:
            self.ui.label_check_root.setPixmap(self.mapv)
            self.ui.label_check_root.setToolTip("Filename root admitted! 😃")

if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Import_Tab_CalVi(None)
    object.show()
    app.exec()
    app.quit()
    app=None