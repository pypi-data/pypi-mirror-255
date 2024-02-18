from .ui_Export_Tab import*
from .TabTools import *

outType_items={
    '.mat': 'binary',
     '.plt': 'tecplot (binary)', 
    #'tecplot (ASCII)':  '.plt',
}
class OUTpar(TABpar):
    def __init__(self):
        self.setup()
        super().__init__()
        self.name='OUTpar'
        self.surname='OUTPUT_Tab'
        self.unchecked_fields+=['FlagValidPath','FlagValidSubFold','FlagValidRoot','FlagSameAsInput']

    def setup(self):
        self.FlagValidSet       = True
        self.FlagSameAsInput    = True                 
        self.FlagValidPath  	= True                  
        self.path        		= basefold 
        self.inputPath        	= basefold                    
        self.FlagSubFold 		= True                  
        self.FlagValidSubFold 	= 1                 
        self.subfold     		= 'out_PaIRS/'                       
        self.FlagSave    		= True                  
        self.FlagValidRoot    	= True                   
        self.root        		= 'out'                 
        self.outType     		= 0                    
        self.x           		= 0                
        self.y           		= 0                 
        self.w           		= 1                 
        self.h           		= 1                  
        self.W           		= 1                
        self.H           		= 1                 
        self.aimop        		= [0]
        self.bimop        		= [0]
        self.vecop        		= [0]    
        self.xres        		= float(1.000)                   
        self.pixAR       		= float(1.000)                     
        self.dt          		= float(1000)       

class Export_Tab(gPaIRS_Tab):
    class Export_Tab_signals(gPaIRS_Tab.Tab_Signals):
        pass

    def __init__(self,*args):
        parent=None
        flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: flagInit=args[1]
        super().__init__(parent,Ui_ExportTab,OUTpar)
        self.signals=self.Export_Tab_signals(self)

        #------------------------------------- Graphical interface: widgets
        self.ui: Ui_ExportTab
        ui=self.ui
        ui.spin_x.addwid=[ui.spin_w]
        ui.spin_y.addwid=[ui.spin_h]
        ui.combo_out_type.clear()
        for item in outType_items.values():
            ui.combo_out_type.addItem(item)

        self.setupWid()  #---------------- IMPORTANT

        #------------------------------------- Graphical interface: miscellanea
        self.mapx  = QPixmap(''+ icons_path +'redx.png')
        self.mapv  = QPixmap(''+ icons_path +'greenv.png')
        self.mapw  = QPixmap(''+ icons_path +'waiting_c.png')
        self.Lab_warning=QPixmap(u""+ icons_path +"warning.png")

        self.aim_qtim=ImageQt(''+ icons_path +'axes.png')
        self.bim_qtim=ImageQt(''+ icons_path +'background.png')
        self.vim_qtim=ImageQt(''+ icons_path +'background_vectors.png')


        self.aim_qtim=ImageQt(''+ icons_path +'axes.png')
        self.bim_qtim=ImageQt(''+ icons_path +'background.png')
        self.vim_qtim=ImageQt(''+ icons_path +'background_vectors.png')
        self.image_labels=[None,ImageQt(''+ icons_path +'rotate_counter.png'),
                           ImageQt(''+ icons_path +'mirror_x.png'),ImageQt(''+ icons_path +'mirror_y.png'),
                           ImageQt(''+ icons_path +'rotate_clock.png')]
        self.velocity_labels=[None,ImageQt(''+ icons_path +'rotate_v_counter.png'),
                           ImageQt(''+ icons_path +'mirror_u.png'),ImageQt(''+ icons_path +'mirror_v.png'),
                           ImageQt(''+ icons_path +'rotate_v_clock.png')]

        aim,bim,vim=self.getQPixmap()
        self.ui.aim.setPixmap(aim)  
        self.ui.aim_2.setPixmap(aim) 
        self.ui.aim_3.setPixmap(aim) 
        self.ui.bim.setPixmap(vim)  
        self.ui.bim_2.setPixmap(bim) 
        self.ui.bim_3.setPixmap(vim) 
        
        self.rotate_counter = QTransform().rotate(-90)
        self.rotate_clock   = QTransform().rotate(+90)
        self.mirror_x       = QTransform().scale(1,-1)
        self.mirror_y       = QTransform().scale(-1,1)        

        #------------------------------------- Declaration of parameters 
        self.OUTpar_base=OUTpar()
        self.OUTpar:OUTpar=self.TABpar
        self.OUTpar_old:OUTpar=self.TABpar_old
        self.defineSetTABpar(self.setOUTpar)

        #------------------------------------- Callbacks 
        self.setupCallbacks()

        #------------------------------------- Initializing 
        if flagInit:
            self.initialize()
            
    def initialize(self):
        pri.Info.yellow(f'{"*"*20}   OUTPUT initialization   {"*"*20}')
        self.OUTpar.w=self.OUTpar.h=self.OUTpar.W=self.OUTpar.H=1000
        self.adjustOUTpar()
        self.setTABpar(True)
       
    def setupCallbacks(self):
        #Callbacks
        self.setSpinxywhCallbacks()
        spin_names=['x_res','y_res','dt']
        spin_tips=['Image resolution along X','Image resolution along Y','Time delay between frames']
        self.setSpinCallbacks(spin_names,spin_tips)

        signals=[["clicked"],
                 ["toggled"],
                 ["returnPressed","editingFinished"],
                 ["activated"]]
        fields=["button",
                "check",
                "edit",
                "combo"]
        names=[ ['rot_counter','rot_clock','mirror_x','mirror_y','rotv_counter','rotv_clock',\
                 'flip_u','flip_v','reset_rot_flip','path'], #button,
                ['save','same_as_input','subfold'], #check
                ['root','path','path_subfold'], #edit
                ['out_type']] #combo
        tips=[ ['Counterclockwise rotation of image','Clockwise rotation of image','Horizontal mirroring of image','Vertical mirroring of image','Counterclockwise rotation of velocity field','Clockwise rotation of velocity field',\
                 'Flip of velocity vectors along X','Flip of velocity vectors along Y','Reset of rotations and mirroring/flip','Output folder path'], #button,
                ['Save results','Output folder path same as input','Create subfolder'], #check
                ['Root of output files','Output folder path','Output subfolder path'], #edit
                ['Type of output files','Files to be saved']] #combo
        
        for f,N,S,T in zip(fields,names,signals,tips):
            for n,t in zip(N,T):
                wid=getattr(self.ui,f+"_"+n)
                fcallback=getattr(self,f+"_"+n+"_callback")
                fcallbackWrapped=self.addParWrapper(fcallback,t)
                for s in S:
                    sig=getattr(wid,s)
                sig.connect(fcallbackWrapped)


#*************************************************** Rotation and flip
    def getQPixmap(self):
        aim=QPixmap.fromImage(self.aim_qtim)
        bim=QPixmap.fromImage(self.bim_qtim)
        vim=QPixmap.fromImage(self.vim_qtim)
        return aim, bim, vim

    def RotMirror(self,addop):
        if addop[0]!=0:
            self.OUTpar.aimop=self.OUTpar.aimop+[addop[0]]
            Itransf=np.eye(2,2)
            Itransf=self.imTransf_op2I(Itransf,self.OUTpar.aimop,False)
            self.OUTpar.aimop=self.imTransf_I2op(Itransf)
        if addop[1]!=0:
            self.OUTpar.bimop=self.OUTpar.bimop+[addop[1]]
            Itransf=np.eye(2,2)
            Itransf=self.imTransf_op2I(Itransf,self.OUTpar.bimop,False)
            self.OUTpar.bimop=self.imTransf_I2op(Itransf)
        self.OUTpar.vecop=self.OUTpar.bimop+self.OUTpar.aimop
        Itransf=np.eye(2,2)
        Itransf=self.imTransf_op2I(Itransf,self.OUTpar.vecop,False)
        self.OUTpar.vecop=self.imTransf_I2op(Itransf)           
            
      
    def RotMirror_Pixmaps(self):
        #aim_qtim,bim_qtim,aim_rot,bim_rot,v_rot,vmat_rot = self.allocateQPixmap()
        _,bim_rot,vim_rot = self.getQPixmap()
        opList=[self.OUTpar.bimop,self.OUTpar.vecop]
        labList=[self.ui.bim_2,self.ui.bim_3]
        imList=[bim_rot,vim_rot]

        for ops,lab,im in zip(opList,labList,imList):
            for _,op in enumerate(ops):
                if op==1:
                    im=im.transformed(self.rotate_counter)
                elif op==-1:
                    im=im.transformed(self.rotate_clock)
                elif op==3:
                    im=im.transformed(self.mirror_x)
                elif op==2:
                    im=im.transformed(self.mirror_y)
            geom=lab.geometry()
            geom.setWidth(im.width())
            geom.setHeight(im.height())
            geom.setY(lab.parentWidget().maximumHeight()-im.height()-5)
            lab.setMinimumSize(im.width(),im.height())
            lab.setMaximumSize (im.width(),im.height())
            lab.setGeometry(geom)
            lab.setPixmap(im) 
            
        opList=[self.OUTpar.bimop,self.OUTpar.aimop]
        imageList=[self.image_labels,self.velocity_labels]
        nList=[2,3]
        for ops,image_labels,n in zip(opList,imageList,nList):
            cont=0
            for k,op in enumerate(ops):
                if op:
                    cont+=1
                    lab:QLabel=getattr(self.ui,f'lab_op{k+1}_{n}')
                    lab.setPixmap(QPixmap.fromImage(image_labels[op]))
            for j in range(cont,3):
                lab:QLabel=getattr(self.ui,f'lab_op{j+1}_{n}')
                lab.setPixmap(QPixmap())
            if cont:
                getattr(self.ui,f'lab_op{0}_{n}').hide()
            else:
                getattr(self.ui,f'lab_op{0}_{n}').show()
        return 

    def imTransf_op2I(self,I,op,flagInv):
        for i in range(len(op)):
            if op[i]==1:   #rotation counter
                I=self.matRot90(I.copy(),flagInv)
            elif op[i]==-1:  #clock
                I=self.matRot90(I.copy(), not flagInv)
            elif op[i]==3 or op[i]==2:  
                I=self.matMirror(I.copy(),op[i]-2)
        return I
            
    def matRot90(self,I,flagInv):
        #RH =(I[0,0]==I[1,1]) and (I[0,1]==-I[1,0])
        #if not RH: flagInv= not flagInv
        if not flagInv:  #direct counter
            a=I[0:np.size(I,0),0].copy()
            I[0:np.size(I,0),0]=-I[0:np.size(I,0),1]
            I[0:np.size(I,0),1]=+a   
        else:
            a=I[0:np.size(I,0),0].copy()
            I[0:np.size(I,0),0]=+I[0:np.size(I,0),1]
            I[0:np.size(I,0),1]=-a    
        return I

    def matMirror(self,I,ind):
        #ind=1 mirror_x, ind=0 mirror_y 
        I[0:np.size(I,0),ind]=-I[0:np.size(I,0),ind]
        return I
            
    def imTransf_I2op(self,I):
        op=[0]
        RHim= I[0,0]==I[1,1] and I[1,0]==-I[0,1]
        if RHim:
            if I[0,0]==1: op=[0]
            elif I[0,0]==-1: op=[1,1]
            elif I[0,1]==1: op=[1]
            elif I[0,1]==-1: op=[-1]
        else:
            if I[0,0]==1: op=[3]
            elif I[0,0]==-1: op=[2]
            elif I[0,1]==1: op=[1,2]
            elif I[0,1]==-1: op=[1,3]
        return op

    def button_rot_counter_callback(self): 
        self.RotMirror([0,1])

    def button_rot_clock_callback(self):
        self.RotMirror([0,-1])

    def button_mirror_x_callback(self):
        self.RotMirror([0,3])

    def button_mirror_y_callback(self):
        self.RotMirror([0,2])

    def button_rotv_counter_callback(self):
        self.RotMirror([1,0])

    def button_rotv_clock_callback(self):
        self.RotMirror([-1,0])

    def button_flip_v_callback(self):
        self.RotMirror([3,0])

    def button_flip_u_callback(self):
        self.RotMirror([2,0,2])
    
    def button_reset_rot_flip_callback(self):
        self.OUTpar.aimop=[0]
        self.OUTpar.bimop=[0]
        self.OUTpar.vecop=[0]
        self.RotMirror([-2,-2,-2])

#*************************************************** From Parameters to UI
    def adjustOUTpar(self):
        self.OUTpar.path=myStandardPath(self.OUTpar.path)
        self.setFlagValidPath()
        self.OUTpar.subfold=myStandardPath(self.OUTpar.subfold)
        self.setFlagValidSubFold()
        self.OUTpar.root=myStandardRoot(self.OUTpar.root)
        self.setFlagValidRoot()
        return

    def setOUTpar(self):
        #Resize/Reshape
        self.ui.w_Flip_Image.setEnabled(self.OUTpar.FlagValidSet)
        self.setMinMaxSpinxywh()
        self.setValueSpinxywh()
        self.RotMirror_Pixmaps()
        self.setResolution()

        self.ui.check_save.setChecked(self.OUTpar.FlagSave)
        self.check_save_action()
        self.setRootLabel()
        self.ui.check_same_as_input.setChecked(self.OUTpar.FlagSameAsInput)
        self.check_same_as_input_action()
        self.ui.edit_path.setText(self.OUTpar.path)
        self.setPathLabel()
        self.ui.check_subfold.setChecked(self.OUTpar.FlagSubFold)
        self.check_subfold_action()
        self.ui.edit_path_subfold.setText(self.OUTpar.subfold)
        self.setSubFoldLabel()
           
    def setResolution(self):
        self.ui.spin_x_res.setValue(self.OUTpar.xres)
        self.ui.spin_y_res.setValue(self.OUTpar.pixAR)
        self.ui.spin_dt.setValue(self.OUTpar.dt)
        self.adjustResLabel()
    
    def adjustResLabel(self):
        Velx=float(1000/(self.OUTpar.xres*self.OUTpar.dt))
        Vely=float(Velx/self.OUTpar.pixAR)
        self.ui.label_Res_x.setText(f"X: {Velx:.6g} m/s")
        adjustFont(self.ui.label_Res_x)
        self.ui.label_Res_y.setText(f"Y: {Vely:.6g} m/s")
        adjustFont(self.ui.label_Res_y)

    def check_save_action(self):
        if not self.OUTpar.FlagSave:
            self.ui.w_SaveResults.hide()
            self.ui.w_OutputFold_Button.hide()
            self.ui.w_OutputSubfold.hide()
        else:
            self.ui.w_SaveResults.show()
            self.ui.w_OutputFold_Button.show()
            self.ui.w_OutputSubfold.show()
            self.ui.edit_root.setText(self.OUTpar.root)
            self.ui.combo_out_type.setCurrentIndex(self.OUTpar.outType)

    def setRootLabel(self):
        if self.OUTpar.FlagValidRoot==-2:
            self.ui.label_check_root.setPixmap(self.Lab_warning)
            self.ui.label_check_root.setToolTip("There are files with the same filename root in the selected path! 😰")
        elif self.OUTpar.FlagValidRoot==-1:
            self.ui.label_check_root.setPixmap(self.Lab_warning)
            self.ui.label_check_root.setToolTip("It was not possible to make the specified output directory! 😰")
        elif self.OUTpar.FlagValidRoot==0:
            self.ui.label_check_root.setPixmap(self.mapx)
            self.ui.label_check_root.setToolTip("Filename root not admitted! 😞")
        if self.OUTpar.FlagValidRoot==1:
            self.ui.label_check_root.setPixmap(self.mapv)
            self.ui.label_check_root.setToolTip("Filename root admitted! 😃")
    
    def setPathLabel(self):
        if self.OUTpar.FlagValidPath:
            self.ui.label_check_path.setPixmap(self.mapv)
            self.ui.label_check_path.setToolTip("This path exists! 😃")
        else:
            self.ui.label_check_path.setPixmap(self.mapx)
            self.ui.label_check_path.setToolTip("This path does not exist! 😞")

    def check_subfold_action(self):
        if not self.OUTpar.FlagSubFold:
            self.ui.w_OutputSubfold_name.hide()
        else:
            self.ui.w_OutputSubfold_name.show()
            self.ui.edit_path_subfold.setText(myStandardPath(self.OUTpar.subfold))
    
    def setSubFoldLabel(self):
        if self.OUTpar.FlagValidSubFold==-1:
            self.ui.label_check_path_subfold.setPixmap(self.Lab_warning)
            self.ui.label_check_path_subfold.setToolTip("Current path already exists! 😰")
        elif self.OUTpar.FlagValidSubFold==0:
            self.ui.label_check_path_subfold.setPixmap(self.mapx)
            self.ui.label_check_path_subfold.setToolTip("Pathname not admitted! 😞")
        elif self.OUTpar.FlagValidSubFold==1:
            self.ui.label_check_path_subfold.setPixmap(self.mapv)
            self.ui.label_check_path_subfold.setToolTip("Pathname admitted! 😃")

#*************************************************** Edit path and root
#******************** path
    def check_same_as_input_callback(self):
        self.OUTpar.FlagSameAsInput=self.ui.check_same_as_input.isChecked()
        self.check_same_as_input_action()
        self.setFlagValidPath()
        self.setFlagValidSubFold()
        
    def check_same_as_input_action(self):
        if self.OUTpar.FlagSameAsInput:
            self.ui.w_OutputFold.setEnabled(False)
            self.ui.w_button_path.setEnabled(False)
            self.OUTpar.path=self.OUTpar.inputPath
            self.ui.edit_path.setText(self.OUTpar.inputPath)
        else:
            self.ui.w_OutputFold.setEnabled(True)
            self.ui.w_button_path.setEnabled(True)

    def edit_path_changing(self): 
         self.ui.label_check_path.setPixmap(QPixmap()) 

    def edit_path_callback(self):
        currpath=myStandardPath(self.ui.edit_path.text())     
        directory_path = myStandardPath(os.getcwd())
        if directory_path in currpath:
            currpath=currpath.replace(directory_path,'./')         
        self.OUTpar.path=currpath        
        self.setFlagValidPath()

    def setFlagValidPath(self,*args):
        if len(args): OUTpar_prev=args[0]
        else: OUTpar_prev=self.OUTpar
        OUTpar_prev.FlagValidPath=os.path.exists(self.OUTpar.path)

    def button_path_callback(self):
        directory = str(QFileDialog.getExistingDirectory(self,\
            "Choose a folder", dir=self.OUTpar.path,options=optionNativeDialog))
        currpath='{}'.format(directory)
        if not currpath=='':
            self.ui.edit_path.setText(currpath)
            out_edit_path=self.edit_path_callback()
            return out_edit_path
        else:
            return [-1,None]

#******************** subfold
    def check_subfold_callback(self):
        self.OUTpar.FlagSubFold=self.ui.check_subfold.isChecked()
        self.check_subfold_action()

    def edit_path_subfold_changing(self): 
         self.ui.label_check_path_subfold.setPixmap(QPixmap()) 

    def edit_path_subfold_callback(self):
        subfold=myStandardPath(self.ui.edit_path_subfold.text())
        self.OUTpar.subfold=subfold
        self.setFlagValidSubFold()
    
    def setFlagValidSubFold(self,*args):
        if len(args): OUTpar_prev=args[0]
        else: OUTpar_prev=self.OUTpar
        if OUTpar_prev.FlagValidPath:
            currpath=myStandardPath(OUTpar_prev.path)
        else:
            currpath='./'
        currpath=myStandardPath(currpath+OUTpar_prev.subfold)
        if  OUTpar_prev.FlagValidPath and os.path.exists(currpath):
            OUTpar_prev.FlagValidSubFold=-1
        else:
            try:
                os.mkdir(currpath)
            except:
                FlagDeleteFolder=False
                OUTpar_prev.FlagValidSubFold=0
            else:
                FlagDeleteFolder=True
                OUTpar_prev.FlagValidSubFold=1
            finally:
                if FlagDeleteFolder:
                    os.rmdir(currpath)

#******************** root
    def check_save_callback(self):
        self.OUTpar.FlagSave=self.ui.check_save.isChecked()
        self.check_save_action()

    def edit_root_changing(self):
         self.ui.label_check_root.setPixmap(QPixmap()) 
        
    def edit_root_callback(self):
        entry=myStandardRoot(self.ui.edit_root.text())
        self.ui.edit_root.setText(entry)
        self.OUTpar.root=entry
        self.setFlagValidRoot()

    def setFlagValidRoot(self,*args):
        if len(args): OUTpar_prev=args[0]
        else: OUTpar_prev=self.OUTpar
        ext=list(outType_items)[OUTpar_prev.outType]
        FlagExistPath=False
        FlagCreateSubFold=False
        if OUTpar_prev.FlagValidPath:
            currpath=myStandardPath(OUTpar_prev.path)
            if OUTpar_prev.FlagValidSubFold:
                currpath=myStandardPath(currpath+OUTpar_prev.subfold)
                if OUTpar_prev.FlagValidSubFold==1: FlagCreateSubFold=not os.path.exists(currpath)
                elif OUTpar_prev.FlagValidSubFold==-1: FlagExistPath=True
        else:
            currpath='./'
        pattern=myStandardRoot(currpath+OUTpar_prev.root)+'*'+ext
        FlagExist=False
        if FlagExistPath:
            files=findFiles_sorted(pattern)
            FlagExist=len(files)>0
        if  FlagExist: 
            OUTpar_prev.FlagValidRoot=-2
        else:
            try:
                if FlagCreateSubFold:
                    os.mkdir(currpath)
                    FlagDeleteSubFold=True
                else:
                    FlagDeleteSubFold=False
            except:
                FlagDeleteSubFold=False
                OUTpar_prev.FlagValidRoot=-1
            else:
                try:
                    filename=pattern.replace('*','a0')+'.delmeplease'
                    open(filename,'w')
                except:
                    FlagDeleteFile=False
                    OUTpar_prev.FlagValidRoot=0
                else:
                    FlagDeleteFile=True
                    OUTpar_prev.FlagValidRoot=1
                finally:
                    if FlagDeleteFile:
                        os.remove(filename)
            finally:
                if FlagDeleteSubFold:
                    os.rmdir(currpath)

    def combo_out_type_callback(self):
        self.OUTpar.outType=self.ui.combo_out_type.currentIndex()
        self.setFlagValidRoot()
    
    def setFlagValid(self,*args):
        if len(args): OUTpar_prev=args[0]
        else: OUTpar_prev=self.OUTpar
        self.setFlagValidPath(OUTpar_prev)
        self.setFlagValidSubFold(OUTpar_prev)
        self.setFlagValidRoot(OUTpar_prev)

#*************************************************** Resolution
    def spin_x_res_callback(self):
        if self.ui.spin_x_res.hasFocus():
            self.OUTpar.xres=self.ui.spin_x_res.value()
            self.adjustResLabel()

    def spin_y_res_callback(self):
        if self.ui.spin_y_res.hasFocus():
            self.OUTpar.pixAR=self.ui.spin_y_res.value()
            self.adjustResLabel()

    def spin_dt_callback(self):
        if self.ui.spin_dt.hasFocus():
            self.OUTpar.dt=self.ui.spin_dt.value()
            self.adjustResLabel()


if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Export_Tab(None)
    object.show()
    app.exec()
    app.quit()
    app=None

