from .ui_Vis_Tab import*
from .Import_Tab_tools import *
from .Export_Tab import outType_items
from .TabTools import*
from .procTools import FLAG_FINALIZED


Flag_VIS_DEBUG=False

exampleFolder='../_examples/'
nStepsSlider=1e5
nStepsSpin=1e2

class VISpar(TABpar):
    FlagVis=True

    class INP(TABpar):
        def __init__(self):
            self.pinfo=patternInfoVar()
            self.range_to=0
            self.selected=imin_im_pair
            self.path=''
            self.FlagValidPath=False
            self.FlagValidRoot=False
            
            super().__init__()
            self.name='VISpar.INP'
            self.surname='VIS_Tab'
            self.unchecked_fields+=[]
    
    class OUT(TABpar):
        def __init__(self):
            self.path=''
            self.subfold=''
            self.root=''
            self.x     = 0                
            self.y     = 0                 
            self.w     = -1                
            self.h     = -1     
            #self.W     = -1                
            #self.H     = -1                          
            self.vecop  = []        
            self.outType=0 

            super().__init__()
            self.name='VISpar.OUT'
            self.surname='VIS_Tab'
            self.unchecked_fields+=[]
    
    class PRO(TABpar):
        def __init__(self):
            WSize_init=[128, 64, 32]
            WSpac_init=[ 32, 16, 8]
            self.Nit=len(WSize_init)
            self.Vect=[np.array(WSize_init,np.intc), np.array(WSpac_init,np.intc),\
                np.array(WSize_init,np.intc), np.array(WSpac_init,np.intc)]
            self.FlagBordo=True
            
            super().__init__()
            self.name='VISpar.PRO'
            self.surname='VIS_Tab'
            self.unchecked_fields+=[]
    
    class TRE(TABpar):
        def __init__(self):
            nTypeProc=3
            self.itemname  = ''
            self.filename_proc = ['']*nTypeProc
            self.name_proc = ['']*nTypeProc
            self.flagRun   = 0
            self.list_pim = []

            super().__init__()
            self.name='TREpar.PRO'
            self.surname='VIS_Tab'
            self.unchecked_fields+=[]

    def __init__(self):
        self.setup()
        super().__init__()
        self.name='VISpar'
        self.surname='VIS_Tab'
        self.unchecked_fields+=[]

    def setup(self):
        self.type=0
        self.nameimga=''
        self.nameimgb=''
        self.nameres=''

        self.flagShowIW=False
        self.flagMIN=False
        self.MapVar_type=0
        self.VecField_type=0
        self.combo_items=[]

        self.FlagYInvert=[False,False]
        self.FlagReset=[False,False] #XLim, CLim

        self.m=[0,0,{}]
        self.M=[0,0,{}]
        self.mean=[0,0,{}]
        self.std=[0,0,{}]
        self.size=[[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1]] #xmin,xmax,ymin,ymax,max vec spacing
        self.xlim=[0,1]
        self.ylim=[0,1]

        self.vmin=0
        self.vmax=1
        self.vmean=0.5
        self.vrange=1
        self.nclev=30
        self.vecsize=1
        self.vecspac=1
        self.streamdens=1
        
        self.nfield=imin_im_pair        
        self.Inp=self.INP() 
        self.Out=self.OUT()
        self.Pro=self.PRO()
        self.Tre=self.TRE()
        #self.FlagCheck=[False]*2
        self.FlagExistMean=[False]*2
        self.FlagExistRes=[False]*2
        self.FlagErrRead=[True]*3
        self.list_Image_Files=[]

class NamesPIV:
    def __init__(self):
        self.imga='imga'
        self.imgb='imgb'
        self.x='X'
        self.y='Y'
        self.u='U'
        self.v='V'
        self.up='uu'
        self.vp='vv'
        self.uvp='uv'
        self.sn='SN'
        self.FCl='CC'
        self.Info='Info'
        self.Mod='Mod'
        allFields={}
        for f,v in self.__dict__.items():
            allFields[v]=f
        self.allFields=allFields
        self.combo_dict={
                    self.imga: 'intensity (frame 0)',
                    self.imgb: 'intensity (frame 1)',
                    self.Mod: 'magnitude',
                    self.u:   'U',
                    self.v:   'V',
                    self.up:  "<u'u'>",
                    self.vp:  "<v'v'>",
                    self.uvp:  "<u'v'>",
                    self.sn:   "S/N",
                    self.Info: "Info",
                    self.FCl:   "CC"
                    }
        self.titles_dict={
                    self.imga: 'intensity (frame 0)',
                    self.imgb: 'intensity (frame 1)',
                    self.Mod: "velocity magnitude",
                    self.u: "x-velocity component",
                    self.v: "y-velocity component",
                    self.up:  "x normal Reynolds stress",
                    self.vp:  "y normal Reynolds stress",
                    self.uvp:  "xy tangential Reynolds stress",
                    self.sn: "signal-to-noise ratio",
                    self.Info: "outlier info",
                    self.FCl:   "Correlation coefficient"
                    }
        self.titles_cb_dict={
                    self.imga: '',
                    self.imgb: '',
                    self.Mod: "|Vel|",
                    self.u: "U",
                    self.v: "V",
                    self.up:  "<u'u'>",
                    self.vp:  "<v'v'>",
                    self.uvp:  "<u'v'>",
                    self.sn: "S/N",
                    self.Info: "i",
                    self.FCl:   "CC"
                    }

        self.fields=list(self.combo_dict)
        self.combo_list=[self.combo_dict[f] for f in self.fields]
        self.titles_list=[self.titles_dict[f] for f in self.fields]
        self.titles_cb_list=[self.titles_cb_dict[f] for f in self.fields]
        
        self.img=[self.imga,self.imgb]
        self.img_ind=[self.fields.index(f) for f in self.img]

        # should start with x, y ,u ,v
        self.instVel=[self.x,self.y,self.u,self.v,self.FCl,self.Info,self.sn]
        self.instVelFields=[self.allFields[f] for f in self.instVel   ]
        self.instVel_plot=[self.Mod,self.u,self.v,self.FCl,self.Info,self.sn]
        self.instVel_plot_ind=[self.fields.index(f) for f in self.instVel_plot if f in self.fields]
        
        
        self.avgVel=[self.x,self.y,self.u,self.v,self.up,self.vp,self.uvp,self.FCl,self.Info,self.sn]
        self.avgVelFields=[self.allFields[f] for f in self.avgVel  ]
        self.avgVel_plot=[self.Mod,self.u,self.v,self.up,self.vp,self.uvp,self.FCl,self.Info,self.sn]
        self.avgVel_plot_ind=[self.fields.index(f) for f in self.avgVel_plot if f in self.fields]

    def pick(self,lista,indici):
        return [lista[i] for i in indici]
    

class Vis_Tab(gPaIRS_Tab):
    class VIS_Tab_Signals(gPaIRS_Tab.Tab_Signals):
        pass

    def __init__(self,*args):
        parent=None
        flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: flagInit=args[1]
        super().__init__(parent,Ui_VisTab,VISpar)
        self.signals=self.VIS_Tab_Signals(self)

        #------------------------------------- Graphical interface: widgets
        self.ui: Ui_VisTab
        ui=self.ui
        self.Ptoolbar=None
        self.addPlotToolBar()

        self.ui.sliders=self.findChildren(QSlider)
        for child in self.ui.sliders:
            child.setMinimum(0)
            child.setMaximum(nStepsSlider)

        self.setupWid()  #---------------- IMPORTANT

        #------------------------------------- Graphical interface: miscellanea
        self.orect=[]
        self.imga=None
        self.imgb=None
        self.res=None
        self.nameimga=self.nameimgb=self.nameres='...'
        self.procimga=None
        self.procimgb=None
        self.procres=None
        self.nameprocimga=self.nameprocimgb=self.nameprocres=''
        self.qui=None
        self.stream=None
        self.cb=None
        #self.VarNames=["Mod","U","V","Fc","info"]
        self.namesPIV=NamesPIV()
        

        #------------------------------------- Declaration of parameters 
        self.VISpar_base=VISpar()
        self.VISpar:VISpar=self.TABpar
        self.VISpar_old:VISpar=self.TABpar_old
        self.defineSetTABpar(self.setVISpar)

        self.flagInitImg=False
        self.fRead=[lambda f,v: self.getImg([0],f,v),
                    lambda f,v: self.getImg([1],f,v),
                    lambda f,v: self.getRes(f,v)]
        self.funPlot=self.setMapVar
        self.fLoad=[False]*3
        
        
        #------------------------------------- Callbacks 
        self.setupCallbacks()
        self.FlagSettingPar=False

        #------------------------------------- Initializing       
        if flagInit:
            self.initialize()
        #------------------------------------- todos  
        ui.button_showMTF.hide()

    def addPlotToolBar(self):
        if self.Ptoolbar:
            self.Ptoolbar.setParent(None)
        self.Ptoolbar = NavigationToolbar(self.ui.plot, self)
        unwanted_buttons = ['Home','Back','Forward','Customize'] #'Subplots','Save'
        for x in self.Ptoolbar.actions():
            if x.text() in unwanted_buttons:
                self.Ptoolbar.removeAction(x)
        self.ui.lay_w_Plot.addWidget(self.Ptoolbar)

    def initialize(self):
        pri.Info.yellow(f'{"*"*20}   VIS initialization   {"*"*20}')
        self.setExample()
        self.setTABpar(True)  #with bridge

    def setExample(self):
        from .procTools import dataTreePar
        self.VISpar.Inp.path=exampleFolder
        self.VISpar.Inp.FlagValidPath=int(os.path.exists(self.VISpar.Inp.path))
        Pinfo=analysePath(exampleFolder)
        if Pinfo.nimg_tot:
            k=np.argmax(np.asarray(Pinfo.nimg_tot))
            pinfo=Pinfo.extractPinfo(k)
        else:
            pinfo=patternInfoVar()
        pinfo.fra==''
        self.VISpar.Inp.pinfo=pinfo
        results=createListImages(exampleFolder,pinfo,False)
        self.VISpar.Inp.FlagValidRoot=all(results[1])-(not all(results[1]))
        self.VISpar.Inp.range_to=results[4]
        self.VISpar.list_Image_Files=results[0]

        self.VISpar.Out.path=exampleFolder
        self.VISpar.Out.subfold='out_PaIRS/'
        self.VISpar.Out.root='out'
        self.VISpar.Out.w=results[5]                
        self.VISpar.Out.h=results[6]

        minproc_name=myStandardRoot(self.VISpar.Out.path+self.VISpar.Out.subfold+self.VISpar.Out.root+outExt.min)
        with open(minproc_name, 'rb') as file:
            data:dataTreePar = pickle.load(file)
        self.VISpar.Tre.filename_proc[dataTreePar.typeMIN]=minproc_name
        self.VISpar.Tre.name_proc[dataTreePar.typeMIN]=data.name_proc[dataTreePar.typeMIN]
        self.VISpar.Tre.flagRun=-1
        
        pivproc_name=myStandardRoot(self.VISpar.Out.path+self.VISpar.Out.subfold+self.VISpar.Out.root+outExt.piv)
        with open(pivproc_name, 'rb') as file:
            data:dataTreePar = pickle.load(file)
        self.VISpar.Tre.filename_proc[dataTreePar.typePIV]=pivproc_name
        self.VISpar.Tre.name_proc[dataTreePar.typePIV]=data.name_proc[dataTreePar.typePIV]
        self.VISpar.Tre.list_pim=data.VIS.Tre.list_pim

        self.VISpar.FlagReset=[True,True]
        self.updateVisfromINP(self.VISpar)

    def setupCallbacks(self):
        #Callbacks
        self.defineSpinCallbacks()
        self.defineSliderCallbacks()

        slider_names=['min','max','mean','range','nclev','vecsize','vecspac','streamdens']
        spin_names=slider_names+['xmin','ymin','xmax','ymax']
        slider_tips=['Minimum level','Maximum level','Mean level','Level range','Number of contour level',
                   'Size of vectors','Spacing of vectors','Density of streamlines']
        spin_tips=slider_tips+['X minimum limit','Y minimum limit','X maximum limit','Y maximum limit']
        for nsp in ['xmin','ymin','xmax','ymax']:
            def SpinXYCallback(nsp):
                sp=getattr(self.ui,'spin_'+nsp)
                return lambda: self.setXYLimFromSpin(sp)
            setattr(self,'spin_'+nsp+'_callback',SpinXYCallback(nsp))
        self.setSpinCallbacks(spin_names,spin_tips)
        self.spin_frame_number_callback=self.addParWrapper(self.spin_frame_number_changing,'Frame number')
        self.ui.spin_frame_number.valueChanged.connect(self.spin_frame_number_callback)
        self.spin_field_number_callback=self.addParWrapper(self.spin_field_number_changing,'Field number')
        self.ui.spin_field_number.valueChanged.connect(self.spin_field_number_callback)

        signals=[["clicked"],
                 ["activated"],       #"currentIndexChanged"   #***** rimpiazzare?
                 ["sliderReleased"]]     #"valueChanged"   #***** lento
        fields=["button",
                "combo",
                "slider"]
        names=[ ['restore','showIW','subMIN','showMTF','invert_y','resize'], #button
                ['map_var','field_rep'], #combo
                slider_names+[]] #slider
        tips=[ ['Restore levels','Show IWs','Subtract minimum','Show MTF','Invert Y axis direction','Resize image'], #button
                ['Map variable to display','Type of field representation'], #combo
                slider_tips+[]] #slider
        
        for f,N,S,T in zip(fields,names,signals,tips):
            for n,t in zip(N,T):
                wid=getattr(self.ui,f+"_"+n)
                fcallback=getattr(self,f+"_"+n+"_callback")
                fcallbackWrapped=self.addParWrapper(fcallback,t)
                for s in S:
                    sig=getattr(wid,s)
                sig.connect(fcallbackWrapped)

        self.ui.left.clicked.connect(lambda: self.leftrightCallback(-1))
        self.ui.right.clicked.connect(lambda: self.leftrightCallback(+1))   

        self.fPlotCallback=self.addParWrapper(self.updatingPlot,'X-Y limits')
        self.ui.plot.addfuncrelease['fPlotCallback']=self.fPlotCallback
        self.fLoadingCallback=self.addParWrapper(lambda: None,'loading')

        self.QS_copy2clipboard=QShortcut(QKeySequence('Ctrl+C'), self.ui.plot)  
        self.QS_copy2clipboard.activated.connect(self.ui.plot.copy2clipboard)
        self.QS_copy2newfig=QShortcut(QKeySequence('Ctrl+F'), self.ui.plot)
        self.QS_copy2newfig.activated.connect(lambda: self.ui.plot.copy2newfig(self.ui.name_var.toolTip()))
        
    def defineSpinCallbacks(self):
        self.spin_min_callback=lambda: self.movingSpinMinMax(self.ui.spin_min,self.ui.spin_max,+1)
        self.spin_max_callback=lambda: self.movingSpinMinMax(self.ui.spin_max,self.ui.spin_min,-1)
        self.spin_mean_callback=lambda: self.movingSpinMeanRange(self.ui.spin_mean,1)
        self.spin_range_callback=lambda: self.movingSpinMeanRange(self.ui.spin_range,2)

        self.spin_nclev_callback=lambda: self.movingSpinContourQuiver(self.ui.spin_nclev,0)
        self.spin_vecsize_callback=lambda: self.movingSpinContourQuiver(self.ui.spin_vecsize,1)
        self.spin_vecspac_callback=lambda: self.movingSpinContourQuiver(self.ui.spin_vecspac,2)
        self.spin_streamdens_callback=lambda: self.movingSpinContourQuiver(self.ui.spin_streamdens,3)

    def defineSliderCallbacks(self):
        self.slider_min_callback=lambda: self.movingSliderMinMax(self.ui.slider_min,self.ui.spin_min,self.ui.spin_max,+1)
        self.slider_max_callback=lambda: self.movingSliderMinMax(self.ui.slider_max,self.ui.spin_max,self.ui.spin_min,-1)
        self.slider_mean_callback=lambda: self.movingSliderMeanRange(self.ui.slider_mean,self.ui.spin_mean,1)
        self.slider_range_callback=lambda: self.movingSliderMeanRange(self.ui.slider_range,self.ui.spin_range,2)

        self.slider_nclev_callback=lambda: self.movingSliderContourQuiver(self.ui.slider_nclev,self.ui.spin_nclev,0)
        self.slider_vecsize_callback=lambda: self.movingSliderContourQuiver(self.ui.slider_vecsize,self.ui.spin_vecsize,1)
        self.slider_vecspac_callback=lambda: self.movingSliderContourQuiver(self.ui.slider_vecspac,self.ui.spin_vecspac,2)
        self.slider_streamdens_callback=lambda: self.movingSliderContourQuiver(self.ui.slider_streamdens,self.ui.spin_streamdens,3)

#*************************************************** Callbacks
#********** Interaction with plot area
    def updatingPlot(self):
        self.VISpar.xlim=list(self.ui.plot.axes.get_xlim())
        self.VISpar.ylim=list(self.ui.plot.axes.get_ylim())

    def setValueXYLimSpin(self):
        self.ui.spin_xmin.setValue(self.VISpar.xlim[0])
        self.ui.spin_xmax.setValue(self.VISpar.xlim[1])
        self.ui.spin_ymin.setValue(self.VISpar.ylim[0])
        self.ui.spin_ymax.setValue(self.VISpar.ylim[1])

    def setXYLimFromSpin(self,sp):
        if sp.hasFocus():
            self.VISpar.xlim[0]=self.ui.spin_xmin.value()
            self.VISpar.xlim[1]=self.ui.spin_xmax.value()
            self.VISpar.ylim[0]=self.ui.spin_ymin.value()
            self.VISpar.ylim[1]=self.ui.spin_ymax.value()
            self.setAxisLim()

#********** Buttons and image spins
    def button_showIW_callback(self):
        self.VISpar.flagShowIW=self.ui.button_showIW.isChecked()
        self.setDefaultXLim()

    def button_showMTF_callback(self):
        if self.ui.button_showMTF.isChecked():
            pass
        else:
            pass

    def button_subMIN_callback(self):
        self.VISpar.flagMIN=self.ui.button_subMIN.isChecked()

    def button_resize_callback(self):
        self.setDefaultXLim()

    def button_invert_y_callback(self):
        self.VISpar.FlagYInvert[self.VISpar.type]=self.ui.button_invert_y.isChecked()

    def button_restore_callback(self):
        self.setDefaultCLim()

    def leftrightCallback(self,di):
        i=self.ui.image_levels.currentIndex()
        i=i+di
        c=self.ctoolpages
        if i<0: i=c
        elif i>c: i=0
        self.ui.image_levels.setCurrentIndex(i)
        self.ui.label_title.setText(f"Settings ({i+1}/{c+1})")

    def spin_field_number_changing(self):
        if not self.FlagSettingPar:
            nfield_old=self.VISpar.nfield
            self.VISpar.nfield=self.ui.spin_field_number.value()
            if self.ui.spin_field_number.hasFocus():
                i=self.VISpar.nfield-imin_im_pair
                self.checkSavedProc(i)
                self.fLoad=[False]*3
                self.importVar()
            if nfield_old!=self.VISpar.nfield and (self.VISpar.nfield==imin_im_pair-1 or nfield_old==imin_im_pair-1):
                self.setDefaultCLim()
            return [1,None]
        else: 
            return[-1,None]

    def spin_frame_number_changing(self):
        if not self.FlagSettingPar:
            self.ui.combo_map_var.setCurrentIndex(self.ui.spin_frame_number.value())
            if self.ui.spin_frame_number.hasFocus():
                self.combo_map_var_action()
            return [1,None]
        else:
            return [-1,None]

#********** Combos etc. 
    def combo_map_var_callback(self):
        if self.VISpar.MapVar_type!=self.mapVarType():
            self.combo_map_var_action()

    def combo_map_var_action(self):
        type_old=int(self.VISpar.MapVar_type>1)
        self.VISpar.MapVar_type=self.mapVarType()
        self.VISpar.type=int(self.VISpar.MapVar_type>1)
        if self.VISpar.type: t=2
        else: t=self.VISpar.MapVar_type
        if not self.fLoad[t]:
            self.importVar()
        if type_old!=self.VISpar.type: 
            self.setDefaultXLim()
            self.setDefaultCLim()
        else:
            if self.VISpar.type==1: self.setDefaultCLim()
        
    def mapVarType(self):
        if self.ui.combo_map_var.currentText():
            ind=self.namesPIV.combo_list.index(self.ui.combo_map_var.currentText())
        else: ind=0
        return ind

    def setDefaultXLim(self,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        mapVarType=VISpar_prev.MapVar_type
        """
        if mapVarType in (0,1):
            VISpar_prev.FlagYInvert[self.VISpar.type]=True
        else:
            VISpar_prev.FlagYInvert[self.VISpar.type]=False
        """
        j=mapVarType if mapVarType in (0,1) else 2
        VISpar_prev.xlim=VISpar_prev.size[j][0:2]
        VISpar_prev.ylim=VISpar_prev.size[j][2:4]
        
    def setDefaultCLim(self,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        mapVarType=VISpar_prev.MapVar_type
        flagImg=mapVarType in (0,1)
        if flagImg:
            me=VISpar_prev.mean[mapVarType]
            st=VISpar_prev.std[mapVarType]
        else:
            j=self.namesPIV.fields[mapVarType]
            me=VISpar_prev.mean[2][j]
            st=VISpar_prev.std[2][j]
        VISpar_prev.vmin=me-2*st
        VISpar_prev.vmax=me+2*st
        if flagImg: VISpar_prev.vmin=max([VISpar_prev.vmin,0])
        self.adjustValues(0,VISpar_prev)
    
    def adjustValues(self,flag,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        #flag=0  from min/max to mean/range
        #flag=1  from mean/range to min/max; mean is fixed
        #flag=2  from mean/range to min/max; range is fixed
        if flag==0:
            mi=VISpar_prev.vmin
            Ma=VISpar_prev.vmax
            VISpar_prev.vmean=0.5*(mi+Ma)
            VISpar_prev.vrange=Ma-mi
        else:
            m,M,step,_,_,_=self.getmM()
            med_val=VISpar_prev.vmean
            if med_val==M-step:
                range_val=2*step
            else:
                range_val=VISpar_prev.vrange
            VISpar_prev.vmin=mi=max([med_val-range_val*0.5,m])
            if mi==m:
                if flag==1:
                    VISpar_prev.vmax=Ma=2*med_val-mi
                    VISpar_prev.vrange=Ma-mi 
                else:
                    VISpar_prev.vmax=Ma=mi+range_val
                    VISpar_prev.vmean=0.5*(mi+Ma)
            else:
                VISpar_prev.vmax=Ma=min([med_val+range_val*0.5,M])
                if Ma==M:
                    if flag==1:
                        VISpar_prev.vmin=mi=2*med_val-Ma
                        VISpar_prev.vrange=Ma-mi 
                    else:
                        VISpar_prev.vmin=mi=Ma-range_val
                        VISpar_prev.vmean=0.5*(mi+Ma)

    def combo_field_rep_callback(self):
        self.VISpar.VecField_type=self.ui.combo_field_rep.currentIndex()
   
#********** Min-max
    def movingSpinMinMax(self,sp_min,sp_max,dv):
        if sp_min.hasFocus():
            self.changeSpinMinMax(sp_min,sp_max,dv)

    def changeSpinMinMax(self,sp_min,sp_max,dv):
        v=sp_min.value()
        if (dv>0 and v>=sp_max.value()) or \
            (dv<0 and v<=sp_max.value()):
            sp_max.setValue(v+dv*sp_min.singleStep())
        self.VISpar.vmin=self.ui.spin_min.value()
        self.VISpar.vmax=self.ui.spin_max.value()
        self.adjustValues(0)
    
    def movingSliderMinMax(self,sl_min,sp_min,sp_max,dv):
        if sl_min.hasFocus():
            v=sl_min.value()/(nStepsSlider-1)*(sp_min.maximum()-sp_min.minimum())+sp_min.minimum()
            sp_min.setValue(v)
            self.changeSpinMinMax(sp_min,sp_max,dv)

#********** Mean-range
    def movingSpinMeanRange(self,sp,n):
        #n=1 for mean, 2 for range
        if sp.hasFocus():
            self.changeSpinMeanRange(sp,n)

    def changeSpinMeanRange(self,sp,n):
        self.VISpar.vmean=self.ui.spin_mean.value()
        self.VISpar.vrange=self.ui.spin_range.value()
        self.adjustValues(n)

    def movingSliderMeanRange(self,sl,sp,n):
        if sl.hasFocus():
            v=sl.value()/(nStepsSlider-1)*(sp.maximum()-sp.minimum())+sp.minimum()
            sp.setValue(v)
            self.changeSpinMeanRange(sp,n)

#********** Remaining
    def movingSpinContourQuiver(self,sp,n):
        if sp.hasFocus():
            self.changeSpinContourQuiver(sp,n)

    def changeSpinContourQuiver(self,sp,n):
        if n==0: self.VISpar.nclev=sp.value()
        elif n==1: self.VISpar.vecsize=sp.value()
        elif n==2: self.VISpar.vecspac=sp.value()
        elif n==3: self.VISpar.streamdens=sp.value()

    def movingSliderContourQuiver(self,sl,sp,n):
        if sl.hasFocus():
            v=sl.value()/(nStepsSlider-1)*(sp.maximum()-sp.minimum())+sp.minimum()
            sp.setValue(v)
            self.changeSpinContourQuiver(sp,n)

#*************************************************** Menus
    def contextMenuEvent(self, event):   
        contextMenu = QMenu(self)
        copy2clipboard = contextMenu.addAction("Copy to clipboard ("+self.QS_copy2clipboard.key().toString(QKeySequence.NativeText)+")")
        copy2newfig = contextMenu.addAction("Open in new figure ("+self.QS_copy2newfig.key().toString(QKeySequence.NativeText)+")")
        contextMenu.addSeparator()
        if len(self.ui.plot.fig2)>1:
            showAll = contextMenu.addAction("Show all")
            closeAll = contextMenu.addAction("Close all")
            alignAll = contextMenu.addAction("Align all")
            contextMenu.addSeparator()
        else:
            showAll = None 
            closeAll= None
            alignAll= None
        loadImga = contextMenu.addAction("Load image frame 0")
        loadImga.setCheckable(self.fLoad[0])
        loadImga.setChecked(self.fLoad[0])
        loadImgb = contextMenu.addAction("Load image frame 1")
        loadImgb.setCheckable(self.fLoad[1])
        loadImgb.setChecked(self.fLoad[1])
        loadRes = contextMenu.addAction("Load result")
        loadRes.setCheckable(self.fLoad[2])
        loadRes.setChecked(self.fLoad[2])
        action = contextMenu.exec(self.mapToGlobal(event.pos()))
        if action == copy2clipboard:
            self.ui.plot.copy2clipboard()
        elif action == copy2newfig:
            self.ui.plot.copy2newfig(self.ui.name_var.toolTip())
        elif action == showAll:
            self.ui.plot.showAll()
        elif action == closeAll:
            self.ui.plot.closeAll()
        elif action == alignAll:
            self.ui.plot.alignAll()
        elif action == loadImga:
            self.loadImg([0])
        elif action == loadImgb:
            self.loadImg([1])
        elif action == loadRes:
            self.loadRes()

    def loadImg(self,*args):
        if len(args): iab=args[0]
        else: iab=[0]
        filename, _ = QFileDialog.getOpenFileName(self,\
            "Select an image file of the sequence", filter=text_filter,\
                options=optionNativeDialog)
        if filename:
            if iab[0]==0:
                self.VISpar.nameimga=myStandardRoot('{}'.format(str(filename)))
            else:
                self.VISpar.nameimgb=myStandardRoot('{}'.format(str(filename)))
            self.getImg(iab,True)
            combo_items=self.namesPIV.combo_list[:2]
            curr_combo_items=self.VISpar.combo_items
            self.VISpar.combo_items=[]
            for f in self.namesPIV.combo_list:
                if f in curr_combo_items or f in combo_items:
                    self.VISpar.combo_items.append(f)
            self.VISpar.MapVar_type=iab[0]
            self.VISpar.type=0
            self.VISpar.FlagYInvert[self.VISpar.type]=True
            self.VISpar.FlagExistRes[0]=[True]
            self.setDefaultCLim()
            self.setDefaultXLim()
            self.fLoadingCallback()
            self.fLoad[iab[0]]=True
        
    def getImg(self,iab,FlagNewRead,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        pri.PlotTime.white(f'{"*"*25} Opening image - start')

        imgab=['imga','imgb']
        for i in iab:
            n=imgab[i]
            flagProc=VISpar_prev.Tre.flagRun<=-10 and VISpar_prev.nfield==imin_im_pair-1
            if flagProc: 
                prefix='proc'
                name_VISpar=getattr(self,'name'+prefix+n)
                name_VISpa_old=''
            else: 
                prefix=''
                name_VISpar=getattr(VISpar_prev,'name'+n)
                name_VISpa_old=getattr(self.VISpar_old,'name'+n)
            nameimg=name_VISpar
            I=None
            #if getattr(self,'name'+n,nameimg)==name_VISpar: continue
            VISpar_prev.FlagErrRead[i]=True
            if name_VISpar:
                try: 
                    if flagProc:
                        I=getattr(self,prefix+n)
                        VISpar_prev.FlagErrRead[i]=np.size(I)==np.size(np.zeros(1))
                    else:
                        if os.path.exists(name_VISpar):
                            pri.Info.cyan(f'Opening: {name_VISpar}  [<--{name_VISpa_old}]')
                            #img=mplimage.imread(name_VISpar)
                            imgraw=Image.open(name_VISpar)
                            I=np.ascontiguousarray(imgraw)
                            I=transfIm(VISpar_prev.Out,Images=[I])[0]
                            VISpar_prev.FlagErrRead[i]=False
                except Exception as inst:
                    pri.Error.red(f'Error opening image file: {name_VISpar}\n{traceback.print_exc()}\n{inst}')
            #else:
                #nameimg=f'Void image file'
            #if VISpar_prev.indTree==self.VISpar.indTree and VISpar_prev.indItem==self.VISpar.indItem and VISpar_prev.ind==self.VISpar.ind:
            setattr(self,n,I)  
            setattr(self,'name'+n,nameimg)

        if FlagNewRead:
            self.getImgInfo(VISpar_prev,i,I)
            pri.Info.green(f'Setting sizes of {name_VISpar} M={VISpar_prev.M[i]} mean={VISpar_prev.mean[i]} std={VISpar_prev.std[i]}')  
        pri.PlotTime.white(f'{"*"*25} Opening image - end')

    def getImgInfo(self,VISpar_prev,i,I):
        VISpar_prev.m[i]=0
        if not VISpar_prev.FlagErrRead[i]:
            VISpar_prev.M[i]=I.max()
            VISpar_prev.mean[i]=np.mean(I)
            VISpar_prev.std[i]=np.std(I)
            VISpar_prev.size[i]=[0,np.size(I,1),0,np.size(I,0),1]
        else:
            VISpar_prev.M[i]=1
            VISpar_prev.mean[i]=VISpar_prev.std[i]=0
            VISpar_prev.size[i]=[0,0,0,0,1]
        
    def loadRes(self):
        filename, _ = QFileDialog.getOpenFileName(self,\
            "Select an image file of the sequence", filter="All files (*.mat *.plt);; .mat (*.mat);; .plt (*.plt)",\
                options=optionNativeDialog)
        if filename:
            self.VISpar.nameres=myStandardRoot('{}'.format(str(filename)))
            self.getRes(True)
            combo_items=[self.namesPIV.combo_dict[f] for f in self.namesPIV.fields if f in self.res]
            curr_combo_items=self.VISpar.combo_items
            self.VISpar.combo_items=[]
            for f in self.namesPIV.combo_list:
                if f in curr_combo_items or f in combo_items:
                    self.VISpar.combo_items.append(f)
            self.VISpar.MapVar_type=2
            self.VISpar.type=1
            self.VISpar.FlagYInvert[self.VISpar.type]=False
            self.VISpar.FlagExistRes[1]=[True]
            self.setDefaultCLim()
            self.setDefaultXLim()
            self.fLoadingCallback()
            self.fLoad[2]=True
            
    def getRes(self,FlagNewRead,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        pri.PlotTime.white(f'{"*"*25} Opening result - start')

        i=2
        res=None
        VISpar_prev.FlagErrRead[i]=True
        flagMean=VISpar_prev.nfield==imin_im_pair-1
        flagProc=VISpar_prev.Tre.flagRun<=-10 and flagMean
        if flagProc: 
            prefix='proc'
            nameres=getattr(self,'name'+prefix+'res')
        else: 
            prefix=''
            nameres=getattr(VISpar_prev,'nameres')
        if nameres:
            try: 
                if flagProc:
                    res=self.procres
                    VISpar_prev.FlagErrRead[i]=False  
                else:
                    if os.path.exists(nameres):
                        pri.Info.cyan(f'Opening: {nameres} [<--{self.VISpar_old.nameres}]')
                        ext=os.path.splitext(nameres)[-1]
                        if ext=='.mat':
                            res = scipy.io.loadmat(nameres)
                        elif ext=='.plt':
                            tres = readPlt(nameres)
                            res={}                                
                            for j, n in enumerate(tres[1]):
                                res[n]=tres[0][:,:,j]
                        res["Mod"]=np.sqrt(res["U"]**2+res["V"]**2)
                        VISpar_prev.FlagErrRead[i]=False
            except Exception as inst:
                    pri.Error.red(f'Error opening image file: {nameres}\n{traceback.print_exc()}\n{inst}')

            #if VISpar_prev.indTree==self.VISpar.indTree and VISpar_prev.indItem==self.VISpar.indItem and VISpar_prev.ind==self.VISpar.ind:
            self.res=res
            self.nameres=nameres
        #else:
        #    self.nameres=f'Void result file'
        if FlagNewRead:
            self.getResInfo(VISpar_prev,i,res)
        pri.PlotTime.white(f'{"*"*25}  Opening result - end')
            
    def getResInfo(self,VISpar_prev:VISpar,i,res):
        if not VISpar_prev.FlagErrRead[i]:
            VISpar_prev.m[i]={}
            VISpar_prev.M[i]={}
            for vn in list(res):
                if not vn in self.namesPIV.fields: continue
                V=res[vn]
                m=V.min()
                M=V.max()
                mm=1.5*max([abs(m),abs(M)])
                if mm<0.1: mm=1
                VISpar_prev.m[i][vn]=-mm
                VISpar_prev.M[i][vn]=+mm
                VISpar_prev.mean[i][vn]=np.mean(V)
                VISpar_prev.std[i][vn]=np.std(V)
            X=res["X"]
            Y=res["Y"]
            VISpar_prev.size[i]=[X.min(),X.max(),Y.min(),Y.max(),int(max([np.size(X,0),np.size(X,1)])/4)]
        else:
            VISpar_prev.m[i]=VISpar_prev.M[i]={}
            VISpar_prev.mean[i]=VISpar_prev.std[i]={}
            VISpar_prev.size[i]=[0,0,0,0,1]

    def setMinMaxField(self):
        if any(self.VISpar.FlagExistMean): 
            self.ui.spin_field_number.setMinimum(-1+imin_im_pair)
        else:
            self.ui.spin_field_number.setMinimum(0+imin_im_pair)    
        if len(self.VISpar.list_Image_Files):
            self.ui.spin_field_number.setMaximum(self.VISpar.Inp.range_to-1+imin_im_pair)
            self.ui.spin_field_number.setEnabled(True)
        else:
            self.ui.spin_field_number.setMaximum(self.ui.spin_field_number.minimum())
            self.ui.spin_field_number.setEnabled(False)

#*************************************************** From Parameters to UI
    def readVar(self,FlagNewRead,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        j=VISpar_prev.MapVar_type
        if j>1: j=2
        field=['nameimga','nameimgb','nameres'][j]
        if len(args): FlagNewRead=True
        if FlagNewRead or getattr(self,field)!=getattr(VISpar_prev,field): #\
            #or VISpar_prev.Out.isDifferentFrom(self.VISpar_old.Out,[],['x','y','w','h','vecop'],True): 
            self.fRead[j](FlagNewRead,VISpar_prev)
        return 

    def importVar(self,*args):
        if not self.VISpar.FlagVis:
            pri.Callback.yellow(f'{">"*30} importVar skipped (tab closed) {"<"*30}')
            return
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        
        flagExistRes=VISpar_prev.FlagExistRes
        if any(flagExistRes):
            mapVarItem=self.namesPIV.combo_list[VISpar_prev.MapVar_type]
            VISpar_prev.combo_items=[]
            if VISpar_prev.FlagExistRes[0]: 
                VISpar_prev.combo_items+=self.namesPIV.pick(self.namesPIV.combo_list,self.namesPIV.img_ind)
            if VISpar_prev.FlagExistRes[1]:
                if VISpar_prev.nfield==imin_im_pair-1 and VISpar_prev.Tre.flagRun>-10:
                    VISpar_prev.combo_items+=self.namesPIV.pick(self.namesPIV.combo_list,self.namesPIV.avgVel_plot_ind)
                else:
                    VISpar_prev.combo_items+=self.namesPIV.pick(self.namesPIV.combo_list,self.namesPIV.instVel_plot_ind)
            if not mapVarItem in VISpar_prev.combo_items:
                mapVarItem=VISpar_prev.combo_items[0]
            mapVarType=self.namesPIV.combo_list.index(mapVarItem)
            resType=int(mapVarType>1)
            if resType!=VISpar_prev.type: #zoom
                VISpar_prev.FlagReset[0]=True
                VISpar_prev.type=resType
            if mapVarType!=VISpar_prev.MapVar_type or (): #levels
                VISpar_prev.FlagReset[1]=True
                VISpar_prev.MapVar_type=mapVarType
        else:
            VISpar_prev.combo_items=[]
            VISpar_prev.MapVar_type= VISpar_prev.type=-1
            return

        self.readVar(True,VISpar_prev)

        if not VISpar_prev.FlagErrRead[VISpar_prev.type]:
            if VISpar_prev.FlagReset[0]:
                self.setDefaultXLim(VISpar_prev)
                VISpar_prev.FlagReset[0]=False
            if VISpar_prev.FlagReset[1]:
                self.setDefaultCLim(VISpar_prev)
                VISpar_prev.FlagReset[1]=False
        return

    def setVISpar(self):
        self.FlagSettingPar=True
        if not self.VISpar.FlagVis:
            pri.Callback.yellow(f'{">"*30} setVISpar skipped (tab closed) {"<"*30}')
            return
        if self.VISpar.Inp.FlagValidPath==-10 or self.VISpar.Inp.FlagValidPath==-10:
            self.hide()
            return
        self.setVisible(True)

        self.readVar(False)
        self.setCombos()
        self.setNameVar()
        self.setMinMaxField()
        self.ui.spin_field_number.setValue(self.VISpar.nfield)
        self.setMinMaxSpin()
        self.setValueSpin()
        self.setValueXYLimSpin()
        if self.VISpar.type==0:
            self.ui.button_showIW.show()
            if self.VISpar.FlagExistMean[0] and self.VISpar.nfield>imin_im_pair-1: 
                self.ui.button_subMIN.show()
            else: self.ui.button_subMIN.hide()   
            self.ui.button_showIW.setChecked(self.VISpar.flagShowIW)
            self.ui.button_subMIN.setChecked(self.VISpar.flagMIN)
        else:
            self.ui.button_showIW.hide()
            self.ui.button_subMIN.hide()
        self.ui.button_invert_y.setChecked(self.VISpar.FlagYInvert[self.VISpar.type])
  
        self.ui.spin_field_number.setValue(self.VISpar.nfield)
        if self.VISpar.type==0:
            self.ui.label_frame_number.show()     
            self.ui.spin_frame_number.show()    
            self.ui.spin_frame_number.setValue(self.VISpar.MapVar_type)
        else:
            self.ui.label_frame_number.hide()  
            self.ui.spin_frame_number.hide()

        if self.VISpar.type==0: j=self.VISpar.MapVar_type
        else: j=2
        self.ui.spin_frame_number.setEnabled(True)
        if not self.VISpar.FlagErrRead[j]:
            self.funPlot()
            #self.setMapVar()  
            #self.exitVISnofile(False)
        else:
            self.exitVISerr(1)
            """
            if all(self.FlagErr):
            #    self.exitVISnofile(False) 
                self.exitVISerr(2) 
            else:
                self.exitVISerr(1)
            #    self.exitVISnofile(True)      
            """
        self.FlagSettingPar=False

    def exitVISerr(self,flagErr):
        if flagErr:
            FlagPlot=False
            if flagErr==2: FlagSpin=False
            else: FlagSpin=True
        else:
            FlagPlot=True
            FlagSpin=True

        #if not FlagPlot:self.ui.CollapBox_PlotTools.closeBox()
        self.ui.CollapBox_PlotTools.setEnabled(FlagPlot)   
        self.Ptoolbar.setVisible(FlagPlot)
        self.ui.Plot_tools.setEnabled(FlagPlot)
        for child in self.ui.plot.fig.get_children():
            child.set_visible(FlagPlot)

        if not FlagSpin:
            self.ui.spin_field_number.setValue(-1+imin_im_pair)
        self.ui.spin_field_number.setEnabled(FlagSpin)
        self.ui.spin_frame_number.setEnabled(FlagSpin)
        #if not FlagPlot: self.plotPaIRS()
            
    def exitVISnofile(self,flagErr):
        if flagErr:
            self.ui.plot.axes.cla()
            if len(self.ui.plot.fig.axes)>1: 
                self.ui.plot.fig.axes[1].remove()
            self.ui.plot.axes.axis('off')
            self.ui.plot.axes.get_xaxis().set_visible(False)
            self.ui.plot.axes.get_yaxis().set_visible(False)
            for s in ('top','right','bottom','left'):
                self.ui.plot.axes.spines[s].set_visible(False) 
            
            self.ui.plot.hide()
            self.Ptoolbar.hide()
            self.ui.Plot_tools.setEnabled(False)
        else:
            self.ui.plot.axes.axis('on')
            self.ui.plot.axes.get_xaxis().set_visible(True)
            self.ui.plot.axes.get_yaxis().set_visible(True)
            for s in ('top','right','bottom','left'):
                self.ui.plot.axes.spines[s].set_visible(True) 
            self.Ptoolbar.show()
            self.ui.Plot_tools.setEnabled(True)
    
    def plotPaIRS(self):
        logoname=''+ icons_path +'logo_PaIRS_completo.png'
        img=np.array(Image.open(logoname)) #mplimage.imread(logoname)
        self.ui.plot.axes.cla() 
        if len(self.ui.plot.fig.axes)>1: 
            self.ui.plot.fig.axes[1].remove()
        self.imgshow=self.ui.plot.axes.imshow(img)
        self.ui.plot.axes.axis('off')
        self.ui.plot.axes.get_xaxis().set_visible(False)
        self.ui.plot.axes.get_yaxis().set_visible(False)
        self.ui.plot.draw()

    def setCombos(self):
        self.ui.combo_map_var.clear()
        self.ui.combo_map_var.addItems(self.VISpar.combo_items)
        if len(self.VISpar.combo_items):
            field=self.namesPIV.combo_list[self.VISpar.MapVar_type]
            if field in self.VISpar.combo_items:
                i=self.VISpar.combo_items.index(field)
            else:
                i=-1
        else: i=-1
        self.ui.combo_map_var.setCurrentIndex(i)
        if self.VISpar.type==0:
            self.ui.label_field_rep.hide()
            self.ui.combo_field_rep.hide()

            self.ctoolpages=c=self.ui.image_levels.count()-2
            i=self.ui.image_levels.currentIndex()
            if i==c+1:
                i=0
                self.ui.image_levels.setCurrentIndex(i)
            self.ui.label_title.setText(f"Settings ({i+1}/{c+1})")

            #self.disableImageLevels(not self.VISpar.nameimga)
        else:
            if not self.VISpar.nameres:
                self.ui.label_field_rep.hide()
                self.ui.combo_field_rep.hide()
            else:
                self.ui.label_field_rep.show()
                self.ui.combo_field_rep.show()
                self.ui.combo_field_rep.setCurrentIndex(self.VISpar.VecField_type)

            self.ctoolpages=c=self.ui.image_levels.count()-1
            i=self.ui.image_levels.currentIndex()
            self.ui.label_title.setText(f"Settings ({i+1}/{c+1})")
            self.checkContourQuiver()

            #self.disableImageLevels(not self.VISpar.nameres)

    def checkContourQuiver(self):
        wnames_all=("vecsize","vecspac","streamdens")
        if self.VISpar.VecField_type==1:
            wnames=("vecsize","vecspac")
        elif self.VISpar.VecField_type==2:
            wnames=("streamdens")
        else:
            wnames=()
        for n in wnames_all:
            flag= n in wnames
            for l in ("label_","slider_","spin_"):
                w=getattr(self.ui,l+n)
                if flag: w.show()
                else: w.hide()  

    def setMinMaxSpin(self):
        m,M,step,step_mean,step_range,vecspac_max=self.getmM()

        self.ui.spin_min.setMinimum(m)
        self.ui.spin_min.setMaximum(M-2*step)
        self.ui.spin_min.setSingleStep(step)
        self.ui.spin_max.setMinimum(m+2*step)
        self.ui.spin_max.setMaximum(M)
        self.ui.spin_max.setSingleStep(step)

        self.ui.spin_mean.setMinimum(m+step)
        self.ui.spin_mean.setMaximum(M-step)
        self.ui.spin_mean.setSingleStep(step_mean)
        self.ui.spin_range.setMinimum(2*step)
        self.ui.spin_range.setMaximum(M-m)
        self.ui.spin_range.setSingleStep(step_range)

        self.ui.spin_vecspac.setMaximum(vecspac_max)
    
    def getmM(self):
        if self.VISpar.type==0:
            m=self.VISpar.m[self.VISpar.MapVar_type]
            M=self.VISpar.M[self.VISpar.MapVar_type]
            range_max=M-m
            step=1
            step_mean=1
            step_range=1
        elif self.VISpar.type==1:
            j=self.namesPIV.fields[self.VISpar.MapVar_type]
            m=self.VISpar.m[2][j]
            M=self.VISpar.M[2][j]
            range_max=M-m
            step=max([(M-1-m)/nStepsSpin,0.01])
            step_mean=max([(M-m-2*step)/nStepsSpin,0.01])
            step_range=(range_max-2*step)/nStepsSpin
        else:
            m=M=step=step_mean=step_range=0
        vecspac_max=self.VISpar.size[-1][-1]
        return m,M,step,step_mean,step_range,vecspac_max
    
    def setValueSpin(self):
        #self.ui.spin_field_number.setValue(self.VISpar.nfield)
        names=["min","max","mean","range","nclev","vecsize","streamdens"]
        for i,n in enumerate(names):
            sp=getattr(self.ui,"spin_"+n)
            if i<4: field="v"+n
            else: field=n
            v=getattr(self.VISpar,field)
            sp.setValue(v)
        self.setSlidersFromSpins()

    def setSlidersFromSpins(self):
        names=["min","max","mean","range","nclev","vecsize","streamdens"]
        for n in names:
            sp=getattr(self.ui,"spin_"+n)
            sl=getattr(self.ui,"slider_"+n)
            if (sp.maximum()-sp.minimum())>0:
                sl_value=int((sp.value()-sp.minimum())/(sp.maximum()-sp.minimum())*nStepsSlider)
            else: sl_value=0
            sl.setValue(sl_value)

    def setNameVar(self):
        if self.VISpar.type==0:
            if self.VISpar.FlagErrRead[self.VISpar.MapVar_type]: 
                self.setNameVarLabel('Input file not available!','')
            else:
                name=getattr(self,['nameimga','nameimgb'][self.VISpar.MapVar_type])
                self.setNameVarLabel(f'Input file: {os.path.basename(name)}',\
                    f'Input file: {name}')
        else:
            if self.VISpar.FlagErrRead[2]:
                self.setNameVarLabel('Output file not available!','')
            else:
                name=self.nameres
                self.setNameVarLabel(f'Output file: {os.path.basename(name)}',\
                    f'Output file: {name}')
            
    def setNameVarLabel(self,stringa,stringa2):
        if stringa:
            self.ui.name_var.setText(stringa) 
            self.ui.name_var.setToolTip(stringa2) 
            self.ui.name_var.setStatusTip(stringa2) 
            self.ui.name_var.show()
        else:
            self.ui.name_var.hide()

    def setMapVar(self):    
        pri.PlotTime.magenta(f'{"/"*25} Plotting image - start')
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor) 
        try:
            if self.VISpar.type==0:
                self.showImg()
            else:
                self.showRes()
        except:
            printException()
        self.exitVISerr(False)  
        QApplication.restoreOverrideCursor()
        pri.PlotTime.magenta(f'{"%"*25} Plotting image - end')

    def showImg(self):
        fields=['MapVar_type','flagMIN','nfield']
        flagImg=self.VISpar.isDifferentFrom(self.VISpar_old,[],fields,True)
        FlagOut=self.VISpar.Out.isDifferentFrom(self.VISpar_old.Out,[],['x','y','w','h','vecop'],True)
        flagImg=flagImg or FlagOut
        if flagImg:
            self.ui.plot.axes.cla()
            if self.cb: 
                try:
                    self.cb.remove()
                except:
                    pass
                self.cb=None
            img=getattr(self,['imga','imgb'][self.VISpar.MapVar_type])
            if self.VISpar.flagMIN and len(self.Imin[self.VISpar.MapVar_type])>0\
                and self.VISpar.nfield>-1+imin_im_pair:
                img=img-self.Imin[self.VISpar.MapVar_type]
            self.img=img
            self.ui.plot.axes.set_title(self.ui.combo_map_var.currentText())
            self.imgshow=self.ui.plot.axes.imshow(img,
                origin='upper',extent=(0,np.size(img,1),np.size(img,0),0),                  
                vmin=self.VISpar.vmin,vmax=self.VISpar.vmax)
            self.imgshow.set_cmap(mpl.colormaps['gray'])
            divider = make_axes_locatable(self.ui.plot.axes)
            cax = divider.append_axes("right", size="5%", pad=0.05) 
            self.cb=self.ui.plot.fig.colorbar(self.imgshow,cax=cax) 
            self.cb.ax.set_title("I")
        else:
            fields=['vmin','vmax']
            flagCLim=self.VISpar.isDifferentFrom(self.VISpar_old,[],fields,True)
            if flagCLim:
                self.imgshow.set_clim(self.VISpar.vmin,self.VISpar.vmax)


        fields=['xlim','ylim','FlagYInvert','Out']
        flagXLim=self.VISpar.isDifferentFrom(self.VISpar_old,[],fields,True)
        if flagXLim or flagImg:
            self.setAxisLim()
        self.Ptoolbar.update()

        fields=['flagShowIW','Pro']
        flagIW=self.VISpar.isDifferentFrom(self.VISpar_old,[],fields,True)
        if flagIW or flagImg:
            self.showRect()
        
        flagDraw=flagImg or flagXLim or flagIW or flagCLim
        if flagDraw: 
            #self.ui.plot.draw()
            self.ui.plot.draw_idle() 

        if not self.flagInitImg: self.flagInitImg=True
        return flagDraw

    def showRes(self):
        flagContour=self.showContMap()
        fields=['VecField_type']
        if self.VISpar.VecField_type==1: fields+=['vecsize','vecspac']
        elif self.VISpar.VecField_type==2: fields+=['streamdens']
        flagVecField=self.VISpar.isDifferentFrom(self.VISpar_old,[],fields,True)
        flagVecField=flagVecField or flagContour
        self.showVecField(flagVecField)
        if flagVecField:
            #self.ui.plot.draw()
            self.ui.plot.draw_idle() 
        
    def showContMap(self):
        fields=['MapVar_type','nfield','vmin','vmax','nclev']
        flagContour=self.VISpar.isDifferentFrom(self.VISpar_old,[],fields,True)
        if flagContour:
            self.ui.plot.axes.cla()
            self.contour=None
            if self.cb: 
                try:
                    self.cb.remove()
                except:
                    pass
                self.cb=None
            X=self.res[self.namesPIV.x]
            Y=self.res[self.namesPIV.y]
            #infoPrint.white(VarNames[self.VISpar.MapVar_type-2])
            var_field=self.namesPIV.fields[self.VISpar.MapVar_type]
            self.ui.plot.axes.set_title(self.namesPIV.titles_list[self.VISpar.MapVar_type])
            V=self.res[var_field]
            self.map=V
            if self.VISpar.vmin<self.VISpar.vmax:
                levs=np.linspace(self.VISpar.vmin,self.VISpar.vmax,self.VISpar.nclev)
            else:
                levs=np.linspace(self.VISpar.vmax-self.ui.spin_min.singleStep(),\
                    self.VISpar.vmax,self.VISpar.nclev) 
            colormap = pyplt.get_cmap('jet')
            colors=colormap(np.linspace(0, 1, len(levs)))
            cmap = mpl.colors.ListedColormap(colors) 
            self.contour=self.ui.plot.axes.contourf(X, Y, V, levs, \
                cmap=cmap, origin='lower', extend='both')
            self.contour.set_clim(levs[0],levs[-1])
            divider = make_axes_locatable(self.ui.plot.axes)
            cax = divider.append_axes("right", size="5%", pad=0.05) 
            self.cb=self.ui.plot.fig.colorbar(self.contour,cax=cax) 

            self.ui.plot.fig.get_axes()[1].set_title(self.namesPIV.titles_cb_list[self.VISpar.MapVar_type])
            self.ui.plot.axes.set_xlabel("x")
            self.ui.plot.axes.set_ylabel("y")
            
        fields=['xlim','ylim','FlagYInvert']
        flagXLim=self.VISpar.isDifferentFrom(self.VISpar_old,[],fields,True)
        if flagXLim or flagContour:
            self.setAxisLim()
        self.Ptoolbar.update()

        flagContour=flagContour or flagXLim
        if not self.flagInitImg: self.flagInitImg=True
        return flagContour
    
    def setAxisLim(self):
        self.ui.plot.axes.set_xlim(self.VISpar.xlim[0],self.VISpar.xlim[1])
        ylim=self.VISpar.ylim 
        if self.VISpar.FlagYInvert[self.VISpar.type]: 
            self.ui.plot.axes.set_ylim(max(ylim),min(ylim))
        else:
            self.ui.plot.axes.set_ylim(min(ylim),max(ylim))
        self.ui.plot.axes.set_aspect('equal', adjustable='box')
        
    def showVecField(self,flagVecField):
        if flagVecField:
            ind=self.VISpar.VecField_type
            if self.qui!=None:
                self.qui.remove()
                self.qui=None
            if self.stream!=None:
                self.stream.lines.remove()
                for ax in self.ui.plot.axes.get_children():
                    if isinstance(ax, mpl.patches.FancyArrowPatch):
                        ax.remove()       
                self.stream=None
            if ind in (1,2):
                X=self.res["X"]
                Y=self.res["Y"]
                U=self.res["U"]
                V=self.res["V"]
                if ind==1:
                    fac=np.abs(X[0,1]-X[0,0])/np.amax(self.res["Mod"])                    
                    spa=self.VISpar.vecspac
                    self.qui=self.ui.plot.axes.quiver(
                        X[::spa,::spa],Y[::spa,::spa],U[::spa,::spa]*fac,V[::spa,::spa]*fac,
                        angles='xy',scale_units='xy',scale=1/self.VISpar.vecsize, 
                        width=0.005,headwidth=5,headaxislength=5)
                elif ind==2:
                    self.stream=self.ui.plot.axes.streamplot(X,Y,U,V,color='k',\
                        density=self.VISpar.streamdens)

    def cleanRect(self):
        if len(self.orect):
            for r in self.orect: 
                if type(r)==list:
                    for s in r:
                        try: s.remove()
                        except:  pass
                else:
                    try: r.remove()
                    except: pass

    def showRect(self):
        if not len(self.VISpar.Pro.Vect): return
        self.cleanRect()
        if not self.VISpar.flagShowIW: return
        colors='rgbymc'
        lwidth=1
        nov_hor=3
        nov_vert=3

        H=self.VISpar.size[self.VISpar.MapVar_type][1]
        Vect = self.VISpar.Pro.Vect
        nw=len(Vect[0])
        xin0=yin0=0
        xmax=ymax=0
        xlim_min=ylim_min=float('inf')
        xlim_max=ylim_max=-float('inf')
        self.orect=[]
        for k in range(nw):
            if self.VISpar.Pro.FlagBordo:
                if not xin0: dx=-Vect[0][k]/2+Vect[1][k]
                else: dx=0
                if not yin0: dy=-Vect[2][k]/2+Vect[3][k]
                else: dy=0
            else:
                dx=dy=0
            for i in range(nov_vert):
                yin=yin0+i*Vect[3][k]+dy
                ylim_min=min([ylim_min,yin])
                for j in range(nov_hor):
                    xin=xin0+j*Vect[1][k]+dx
                    xlim_min=min([xlim_min,xin])
                    kk=i+j*nov_vert
                    if kk%2: lst=':'
                    else: lst='-'
                    kc=k%len(colors)
                    rect = mpl.patches.Rectangle((xin, yin), Vect[0][k], Vect[2][k],\
                        linewidth=lwidth, edgecolor=colors[kc], facecolor=colors[kc],\
                            alpha=0.25,linestyle=lst)
                    self.ui.plot.axes.add_patch(rect)
                    rect2 = mpl.patches.Rectangle((xin, yin), Vect[0][k], Vect[2][k],\
                        linewidth=lwidth, edgecolor=colors[kc], facecolor='none',\
                            alpha=1,linestyle=lst)
                    self.ui.plot.axes.add_patch(rect2)
                    points=self.ui.plot.axes.plot(xin+ Vect[0][k]/2,yin+ Vect[2][k]/2,\
                        'o',color=colors[kc])
                    if not kk: 
                        if self.VISpar.FlagYInvert[self.VISpar.type]: va='top'
                        else: va='bottom'
                        text=self.ui.plot.axes.text(xin+5,yin+5,str(k),\
                        horizontalalignment='left',verticalalignment=va,\
                        fontsize='large',color='w',fontweight='bold')
                    self.orect=self.orect+[rect,rect2,points,text]
            xmaxk=xin+Vect[0][k]
            ymaxk=yin+Vect[2][k]
            xlim_max=max([xlim_max,xmaxk])
            ylim_max=max([ylim_max,ymaxk])
            if xmaxk>xmax: xmax=xmaxk
            if ymaxk>ymax: ymax=ymaxk
            if k==nw-1: continue
            if ymaxk+Vect[2][k+1]+(nov_vert-1)*Vect[3][k+1]<H:
                yin0=ymaxk
            else:
                yin0=0
                xin0=xmax
        xlim=self.ui.plot.axes.get_xlim()
        xlim_min=min([xlim[0],xlim_min])
        xlim_max=max([xlim[1],xlim_max])
        self.ui.plot.axes.set_xlim(xlim_min,xlim_max)
        if self.VISpar.FlagYInvert[self.VISpar.type]: 
            ylim=self.ui.plot.axes.get_ylim()
            ylim_max=min([ylim[1],ylim_min])
            ylim_min=max([ylim[0],ylim_max])
        else:
            ylim=self.ui.plot.axes.get_ylim()
            ylim_min=min([ylim[0],ylim_min])
            ylim_max=max([ylim[1],ylim_max])
        self.ui.plot.axes.set_ylim(ylim_min,ylim_max)
        self.VISpar.xlim=list(self.ui.plot.axes.get_xlim())
        self.VISpar.ylim=list(self.ui.plot.axes.get_ylim())

#*************************************************** Displaying images
    def updateVisfromINP(self,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        
        self.checkSavedProc(-1,VISpar_prev)
        VISpar_prev.nfield=VISpar_prev.Inp.selected
        if VISpar_prev.nfield==imin_im_pair-1 and not any(VISpar_prev.FlagExistMean):
            VISpar_prev.nfield+=1

        i=VISpar_prev.nfield-imin_im_pair
        self.checkSavedProc(i,VISpar_prev)
        self.fLoad=[False]*3
        self.importVar(VISpar_prev)
        

    def checkSavedProc(self,i,*args):
        if len(args): VISpar_prev:VISpar=args[0]
        else: VISpar_prev=self.VISpar
        INP=VISpar_prev.Inp
        OUT=VISpar_prev.Out
        TRE=VISpar_prev.Tre

        if i<0 and TRE.flagRun:
            if TRE.flagRun<-1:
                VISpar_prev.FlagExistMean=[TRE.flagRun in (-10,-11),TRE.flagRun in (-11,-12)] #flagRun=-10: solo min, -11:min+PIV, -12:solo PIV
            else:
                fnames=TRE.filename_proc[1:3]
                dnames=TRE.name_proc[1:3]
                VISpar_prev.FlagExistMean=[False,False]
                for k,f in enumerate(fnames):
                    if not f: 
                        VISpar_prev.FlagExistMean[k]=False
                        continue
                    try:
                        with open(f, 'rb') as file:
                            data = pickle.load(file)
                        VISpar_prev.FlagExistMean[k]=dnames[k]==data.name_proc[k+1]
                    except Exception as inst:
                        pri.Error.red(f"VIS: error opening result files {f}:\n   {traceback.format_exc()}, {inst}")
                        VISpar_prev.FlagExistMean[k]=False
        elif i<0 and not TRE.flagRun:
            VISpar_prev.FlagExistMean=[False,False]

        VISpar_prev.nameimga=VISpar_prev.nameimgb=VISpar_prev.nameres=''
        currpath=myStandardPath(OUT.path+OUT.subfold)
        root=OUT.root
        outExt=list(outType_items)[OUT.outType]
        if INP.pinfo.ndig!=[]:
            ndig=INP.pinfo.ndig
        else:
            ndig=0
        if  i<0:
            if VISpar_prev.FlagExistMean[0]:
                root_min=myStandardRoot(OUT.path+OUT.subfold+OUT.root)+"_"
                VISpar_prev.nameimga=root_min+"a_min"+INP.pinfo.ext
                VISpar_prev.nameimgb=root_min+"b_min"+INP.pinfo.ext      
                VISpar_prev.FlagExistRes[0]=os.path.exists(VISpar_prev.nameimga) or os.path.exists(VISpar_prev.nameimgb) 
            else:
                VISpar_prev.FlagExistRes[0]=False             

            if VISpar_prev.FlagExistMean[1]:
                VISpar_prev.nameres=os.path.join(f"{currpath}{root}{outExt}")    
                VISpar_prev.FlagExistRes[1]=os.path.exists(VISpar_prev.nameres)
            else:
                VISpar_prev.FlagExistRes[1]=False                
        else:
            if len(VISpar_prev.list_Image_Files):
                VISpar_prev.nameimga=INP.path+VISpar_prev.list_Image_Files[i*2]
                VISpar_prev.nameimgb=INP.path+VISpar_prev.list_Image_Files[i*2+1]   
                VISpar_prev.FlagExistRes[0]=os.path.exists(VISpar_prev.nameimga) or os.path.exists(VISpar_prev.nameimgb) 
            else:
                VISpar_prev.FlagExistRes[0]=False

            if len(VISpar_prev.Tre.list_pim):
                if VISpar_prev.FlagExistMean[1] and VISpar_prev.Tre.list_pim[i]&FLAG_FINALIZED[0]:
                    VISpar_prev.nameres=os.path.join(f"{currpath}{root}_{i:0{ndig:d}d}{outExt}")
                    VISpar_prev.FlagExistRes[1]=os.path.exists(VISpar_prev.nameres)
                else:
                    VISpar_prev.FlagExistRes[1]=False
            else:
                VISpar_prev.FlagExistRes[1]=False

        if  i<0:
            #self.setMinMaxField()

            if VISpar_prev.FlagExistMean[0]:
                Imin=[np.zeros(0),np.zeros(0)]
                currpath=myStandardPath(VISpar_prev.Out.path+VISpar_prev.Out.subfold)
                root=myStandardRoot(VISpar_prev.Out.root)
                ext=VISpar_prev.Inp.pinfo.ext 
                for j,f in enumerate('ab'):
                    nameout=f"{currpath}{root}_{f}_min{ext}"
                    if os.path.exists(nameout):
                        try:
                            Imin[j]=np.array(Image.open(nameout))
                        except Exception as inst:
                            pri.Error.red(f"VIS: error opening minimum image {nameout}:\n   {traceback.format_exc()}, {inst}")
                self.Imin=Imin
            else:
                self.Imin=[np.zeros(0),np.zeros(0)]


if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Vis_Tab(None)
    object.show()
    app.exec()
    app.quit()
    app=None

async def plotImg(self,flagImg,flagCLim,flagXLim,flagIW,flagDraw):
    pax=self.ui.plot.axes
    
    if flagImg:
        pax.cla()
        if len(pax.figure.axes)>1: 
            try:
                pax.figure.axes[1].remove()
            except:
                pass
        img=getattr(self,['imga','imgb'][self.VISpar.MapVar_type])
        if self.VISpar.flagMIN and len(self.Imin[self.VISpar.MapVar_type])>0\
            and self.VISpar.nfield>-1+imin_im_pair:
            img=img-self.Imin[self.VISpar.MapVar_type]
        self.img=img
        pax.set_title(self.ui.combo_map_var.currentText())
        self.imgshow=pax.imshow(img,
            origin='upper',extent=(0,np.size(img,1),np.size(img,0),0),                  
            vmin=self.VISpar.vmin,vmax=self.VISpar.vmax)
        self.imgshow.set_cmap(mpl.colormaps['gray'])
        divider = make_axes_locatable(pax)
        cax = divider.append_axes("right", size="5%", pad=0.05) 
        cb=pax.figure.colorbar(self.imgshow,cax=cax) 
        cb.ax.set_title("I")

    if flagCLim:
        self.imgshow.set_clim(self.VISpar.vmin,self.VISpar.vmax)

    if flagXLim:
        self.setAxisLim(pax)
    self.Ptoolbar.update()

    if flagIW or flagImg:
        self.showRect(pax)
    
    if flagDraw: 
        #self.ui.plot.draw()
        self.ui.plot.draw_idle() 

    if not self.flagInitImg: self.flagInitImg=True
    return self.ui.plot