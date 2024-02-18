from .ui_Vis_Tab_CalVi import*
from .TabTools import*
from .calib import Calib, CalibTasks, calibTasksText, CalibFunctions, calibFunctionsText
from .calibView import CalibView
from .Import_Tab_CalVi import INPpar_CalVi
from .Process_Tab_CalVi import PROpar_CalVi


bufferSizeLimit=2000*1e6  #bytes
if __name__ == "__main__":
    cfgName='../../img/calib/NewCam0.cfg'
    cfgName='../../img/calib/NewCam0_Mod.cfg'
    FlagRun=True
else:
    cfgName=''
    FlagRun=False

class VISpar_CalVi(TABpar):
    FlagVis=True

    def __init__(self):
        self.setup()
        super().__init__()
        self.name='VISpar'
        self.surname='VIS_Tab'
        self.unchecked_fields+=[]

    def setup(self):
        self.cfgName=cfgName
        self.FlagRun=FlagRun

        self.nPlane=0
        self.plane=0
        self.nCam=0
        self.cam=0
        self.scaleFactor=1.0
        self.LLim=0
        self.LMin=0
        self.LMax=0

        self.MaskType=0
        self.FlagShowMask=1
        self.FlagPlotMask=0

        self.xOriOff=0
        self.yOriOff=0
        self.xm=0
        self.xp=0
        self.ym=0
        self.yp=0

        self.orPosAndShift=[]
        self.angAndMask=[]
        self.spotDistAndRemoval=[]
        
        self.list_Image_Files=[]
        self.list_eim=[]

        self.errorMessage=''

class Vis_Tab_CalVi(gPaIRS_Tab):
    class VIS_Tab_Signals(gPaIRS_Tab.Tab_Signals):
        run=Signal(bool)
        pass
    def closeEvent(self,event):
        ''' called when closing 
        I had to add this to be sure that calib was destroyed'''
        
        #self.calibView.imageViewerThreadpool.clear()
        pri.Info.white("Vis_Tab_CalVi closeEvent")
        del self.calibView
    
    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.setZoom()

    def __init__(self,*args):
        parent=None
        self.flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: self.flagInit=args[1]
        super().__init__(parent,Ui_VisTab_CalVi,VISpar_CalVi)
        self.signals=self.VIS_Tab_Signals(self)

        #------------------------------------- Graphical interface: widgets
        self.ui: Ui_VisTab_CalVi
        ui=self.ui

        self.setupWid()  #---------------- IMPORTANT
        #introducing CalibView
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.calibView=CalibView(self.scrollArea,self.outFromCalibView,self.outToStatusBarFromCalibView,self.textFromCalib,self.workerCompleted)
        self.scrollArea.setWidget(self.calibView)
        self.ui.splitter.insertWidget(0,self.scrollArea)

        #------------------------------------- Graphical interface: miscellanea
        self.ui.status_L.setText('')
        self.ui.status_R.setText('')
        self.FlagFirstShow=False
        self.FlagSettingNewCalib=False
        self.setLogFont(fontPixelSize-dfontLog)

        #------------------------------------- Declaration of parameters 
        self.VISpar_base=VISpar_CalVi()
        self.VISpar:VISpar_CalVi=self.TABpar
        self.VISpar_old:VISpar_CalVi=self.TABpar_old
        self.defineSetTABpar(self.setVISpar)
        
        
        #------------------------------------- Callbacks 
        self.setupCallbacks()
        self.FlagSettingPar=False
        self.FlagAddPrev=False
        self.updateGCalVi= lambda: None
        self.calibView.flagCurrentTask=CalibTasks.stop#todo GP per me si deve cancellare è stato già fatto nell'init di CalibView
        self.bufferImg={}
        self.bufferSize=[]
        self.setRunButtonText=lambda: None

        #------------------------------------- Initializing       
        if self.flagInit:
            self.initialize()

    def initialize(self):
        pri.Info.yellow(f'{"*"*20}   VIS initialization   {"*"*20}')
        self.defaultSplitterSize()

        if self.VISpar.cfgName:
            #self.VISpar.FlagRun=True
            flagOp=self.calibView.calib.readCfg()
            self.calibView.calib.readImgs() #todo verificare eventuali errori e dimensioni delle immagini in questo momento non da errore e l'img viene tagliata
            
            self.calib2VIS()
            self.setVISpar()
            
            #self.signals.run.emit(not flagOp)
            self.runCalVi('_Mod' in self.VISpar.cfgName)
        #self.ui.plot.show() 
        #self.setTABpar(True)  #with bridge
    
    def defaultSplitterSize(self):
        self.ui.splitter.setSizes([self.width()-self.ui.w_Commands.minimumWidth(),self.ui.w_Commands.minimumWidth()])

    @Slot(bool)
    def runCalVi(self,flagMod=False):
        self.calibView.flagFirstTask=CalibTasks.findPlanesFromOrigin if flagMod else CalibTasks.findAllPlanes
        self.VISpar.plane=self.VISpar.cam=0
        self.setVISpar()
        if flagMod: self.ui.log.setText('')
        if self.calibView.executeCalibTask(self.calibView.flagFirstTask):
            self.setTaskButtonsText()
            self.resetScaleFactor()

    def stopCalVi(self):
        self.calibView.executeCalibTask(CalibTasks.stop)
        self.setTaskButtonsText()
        self.plotPlane()

    def show(self):
        super().show()
        if not self.FlagFirstShow:
            self.FlagFirstShow=True
            self.resetScaleFactor()

    def setupCallbacks(self):
        self.ui.button_zoom_minus.clicked.connect(self.addParWrapper(lambda:self.zoom(0.8),'Zoom'))
        self.ui.button_zoom_equal.clicked.connect(self.addParWrapper(self.resetScaleFactor,'Zoom'))
        self.ui.button_zoom_plus.clicked.connect(self.addParWrapper(lambda:self.zoom(1.25),'Zoom'))
        self.ui.splitter.addfuncout['setScrollAreaWidth']=self.setZoom
        

        self.taskButtons=[self.ui.button_findAll,
                          self.ui.button_find,
                          self.ui.button_calibrate,
                          self.ui.button_saveCoord,
                          ]
        self.taskButton_callbacks=[]
        for k,ind in enumerate([f.value for f in CalibTasks if f.value>0]):
            self.taskButton_callbacks.append(lambda dum=ind, flag=k!=3,ff=self.taskButtonPressed: ff(CalibTasks(dum),flag))
            self.taskButtons[k].clicked.connect(self.taskButton_callbacks[k])

        self.buttonsToDisableNotCalibrated=[] #used to gray buttons if not calibrated
        self.functionButtons=[
                              self.ui.button_deleteErr,
                              self.ui.button_focusErr,
                              self.ui.button_copyGrid,
                              ]
        self.functionButtons_callbacks=[]
        for k,ind in  enumerate([f.value for f in CalibFunctions if f.value>0]):
            self.functionButtons_callbacks.append(lambda dum=ind, flag=True,ff=self.functionButtonPressed: ff(CalibFunctions(dum),flag))
            self.functionButtons[k].clicked.connect(self.functionButtons_callbacks[k])
            self.buttonsToDisableNotCalibrated.append(self.functionButtons[k])

        
        functionButtons_insert=[0,0,0]
        for k,ind in  enumerate([f.value for f in CalibFunctions]):
            action=QAction(self.functionButtons[k].icon(),calibFunctionsText[abs(ind)],self)
            self.calibView.contextMenuActions.insert(functionButtons_insert[k],action)
            action.triggered.connect(lambda dum=ind, flag=True,ff=self.functionButtonPressed: ff(CalibFunctions(dum),flag))
            if ind>0:
                self.buttonsToDisableNotCalibrated.append(action)

        self.originOffbox=self.ui.g_OriOff
        self.remPoinsBox=self.ui.g_GriLim
        self.buttonsToDisable=[
                              self.ui.spin_plane,
                              self.originOffbox,
                              self.remPoinsBox,
                             ] #used to gray buttons when calibrating
        
        self.spin_plane_callback=self.addParWrapper(self.spinImgChanged,'Plane changed')
        self.ui.spin_plane.valueChanged.connect(self.spin_plane_callback)
        self.spin_cam_callback=self.spinImgChanged
        self.spin_xOriOff_callback=lambda off: self.spin_OriOff_callback(off,self.ui.spin_xOriOff,True)
        self.spin_yOriOff_callback=lambda off: self.spin_OriOff_callback(off,self.ui.spin_yOriOff,False)

        self.spin_yp_callback=lambda off: self.spin_remPoi_callback(off, self.ui.spin_yp,False,True)
        self.spin_ym_callback=lambda off: self.spin_remPoi_callback(off, self.ui.spin_ym,False,False)
        self.spin_xp_callback=lambda off: self.spin_remPoi_callback(off, self.ui.spin_xp,True,True)
        self.spin_xm_callback=lambda off: self.spin_remPoi_callback(off, self.ui.spin_xm,True,False)
        self.ui.button_copyGrid.clicked.connect(self.copyRemPoints)
        
        spin_names=['cam',
                    'LMin',
                    'LMax',
                    'yOriOff',
                    'xOriOff',
                    'yp',
                    'ym',
                    'xp',
                    'xm',
                    ]
        spin_tips=['Camera number  (from 1 to number of cameras)',
                   'Minimum value of the image intensity',
                   'Maximum value of the image intensity',
                   'Shift the origin along y with respect to the first selected point in current target image',
                   'Shift the origin along x with respect to the first selected point in current target image',
                   'Maximum y limit for the point grid',
                   'Minimum y limit for the point grid',
                   'Maximum x limit for the point grid',
                   'Minimum x limit for the point grid',
                   ]
        self.setSpinCallbacks(spin_names,spin_tips)


        self.button_restore_callback=self.addParWrapper(self.restoreLevels,'Restore image levels')
        self.ui.button_restore.clicked.connect(self.button_restore_callback)

        self.radio_showMask_callback=self.addParWrapper(self.showMask,'Show/hide correlation mask')
        self.ui.radio_showMask.clicked.connect(self.radio_showMask_callback)

        self.tool_plotMask_callback=self.addParWrapper(self.plotMask,'Plot correlation mask')
        self.ui.tool_plotMask.clicked.connect(self.tool_plotMask_callback)

        self.signals.run.connect(self.runCalVi)
        return
    
    def setLogFont(self,fPixSize):
        logfont=self.ui.log.font()
        logfont.setFamily('Courier New')
        logfont.setPixelSize(fPixSize)
        self.ui.log.setFont(logfont)

#********************************************* Setting parameters
    def setVISpar(self):
        FlagImg=bool(len(self.calibView.calib.imgs))
        FlagMask=self.VISpar.MaskType not in (2,3) and bool(len(self.calibView.calib.ccMask))
        if FlagImg:
            self.ui.g_Image.setEnabled(True)
            self.ui.spin_plane.setEnabled(self.VISpar.nPlane>1)
            self.ui.spin_cam.setEnabled(self.VISpar.nCam>1)
        else:
            self.ui.g_Image.setEnabled(False)     

        FlagZoomLevels=FlagImg or FlagMask
        self.ui.g_Zoom.setEnabled(FlagZoomLevels)
        self.ui.g_Levels.setEnabled(FlagZoomLevels)
        
        self.ui.g_Mask.setVisible(FlagMask)
        self.ui.radio_showMask.setChecked(self.VISpar.FlagShowMask)
        self.ui.tool_plotMask.setEnabled(self.VISpar.FlagShowMask)
        self.ui.tool_plotMask.setChecked(self.VISpar.FlagPlotMask and self.VISpar.FlagShowMask)
        
        self.ui.w_Commands.setVisible(self.VISpar.FlagRun)
        flagNewRun=self.VISpar.isDifferentFrom(self.VISpar_old,[],['FlagRun'],True)
        if flagNewRun: self.defaultSplitterSize()
        if self.VISpar.FlagRun:
            self.calibView.contextMenu =QtWidgets.QMenu(self)
            for a in self.calibView.contextMenuActions:
                self.calibView.contextMenu.addAction(a)
            self.calibView.contextMenu.insertSeparator(self.calibView.contextMenuActions[1])
        else:
            self.calibView.contextMenu =None
            
        self.setRunButtonText()

        self.ui.status_L.setText('')
        self.ui.status_R.setText('')
        self.setSpinMaxMinLimValues()
        if not self.FlagSettingNewCalib: self.calibView.scaleFactor=self.VISpar.scaleFactor
        self.setZoom()
        self.plotPlane()
        flagPlotMask=self.VISpar.isDifferentFrom(self.VISpar_old,[],['FlagPlotMask'],True)
        if  flagPlotMask or flagNewRun or self.FlagSettingNewCalib:
            self.FlagSettingNewCalib=False
            if flagPlotMask:
                self.restoreLevels()
                self.setSpinMaxMinLimValues()

            self.resetScaleFactor()
            self.setZoom()
            self.plotPlane()
        return
    
    def calib2VIS(self,flagResetLevels=True,flagResetZoom=True):
        c=self.calibView.calib
        self.VISpar.nPlane=c.nPlanesPerCam
        self.VISpar.nCam=c.nCams
        """
        if flagReset:
            self.VISpar.plane=0
            self.VISpar.cam=0
        else:
            self.VISpar.plane=c.nPlanesPerCam if self.VISpar.plane>c.nPlanesPerCam else self.VISpar.plane
            self.VISpar.cam=c.nCams if self.VISpar.cam>c.nCams else self.VISpar.cam
        """
        
        c.setLMinMax()
        self.VISpar.LLim=c.LLim
        if flagResetLevels: 
            self.VISpar.LMin=c.LMin
            self.VISpar.LMax=c.LMax
        else:
            self.VISpar.LMax=c.LMax if self.VISpar.LMax>c.LLim else self.VISpar.LMax
            self.VISpar.LMin=self.VISpar.LMax-1 if self.VISpar.LMin >self.VISpar.LMax-1 else self.VISpar.LMin

        self.VISpar.MaskType=abs(self.calibView.calib.cal.data.FlagPos)
        if self.VISpar.MaskType in (2,3):
            self.VISpar.FlagShowMask=0
            self.VISpar.FlagPlotMask=0
        self.FlagSettingNewCalib=flagResetZoom
        #self.setVISpar()

    def setSpinMaxMinLimValues(self):
        spins=['plane','cam','LMin','LMax']
        vals=[]
        for s in spins: vals.append(getattr(self.VISpar,s))
        self.setSpinMaxMin()
        for s,v in zip(spins,vals): setattr(self.VISpar,s,v)
        self.setSpinValues()

    def setSpinMaxMin(self):
        self.ui.spin_plane.setMinimum(1*bool(self.VISpar.nPlane))
        self.ui.spin_plane.setMaximum(self.VISpar.nPlane)
        self.ui.spin_cam.setMinimum(1*bool(self.VISpar.nCam))
        self.ui.spin_cam.setMaximum(self.VISpar.nCam)

        self.ui.spin_LMin.setMinimum(-self.VISpar.LLim)
        self.ui.spin_LMin.setMaximum(self.VISpar.LMax-1)
        self.ui.spin_LMax.setMinimum(self.VISpar.LMin+1)
        self.ui.spin_LMax.setMaximum(self.VISpar.LLim)

    def setSpinValues(self):
        spin_p1=['plane','cam']
        spins=self.findChildren(MyQSpin)+self.findChildren(MyQDoubleSpin)
        for s in spins:
            s:MyQSpin
            nameSpin=s.objectName().split('spin_')[-1]
            if nameSpin in spin_p1: d=1
            else: d=0
            s.setValue(getattr(self.VISpar,nameSpin)+d)
        self.calibView.calib.LMax=self.VISpar.LMax
        self.calibView.calib.LMin=self.VISpar.LMin

    def spin_LMin_callback(self):
        self.VISpar.LMin=self.ui.spin_LMin.value()
        if self.ui.spin_LMin.hasFocus():
            self.ui.spin_LMax.setMinimum(self.VISpar.LMin+1)
            #self.plotPlane()

    def spin_LMax_callback(self):
        self.VISpar.LMax=self.ui.spin_LMax.value()
        if self.ui.spin_LMax.hasFocus():
            self.ui.spin_LMin.setMaximum(self.VISpar.LMax-1)
            #self.plotPlane()

    def restoreLevels(self):
        pc=self.VISpar.plane
        c=self.VISpar.cam
        p=pc+c*self.calibView.calib.nPlanesPerCam
        c=self.calibView.calib
        c.setLMinMax(p)
        self.VISpar.LLim=c.LLim
        self.VISpar.LMin=c.LMin
        self.VISpar.LMax=c.LMax

    def plotPlane(self):
        if not self.calibView.calib.cal.data.Numpiani: 
            self.calibView.hide()
            return
        else:
            self.calibView.show()
        pc=self.VISpar.plane
        c=self.VISpar.cam
        p=pc+c*self.calibView.calib.nPlanesPerCam
        self.calibView.plotPlane(p)

    def spin_OriOff_callback(self,Off,spin:QSpinBox,flagX):
        self.focusOnTarget(False)
        nameSpin=spin.objectName().split('spin_')[-1]
        setattr(self.VISpar,nameSpin,spin.value())
        if spin.hasFocus():
            self.calibView.spinOriginChanged(Off, spin,flagX)

    def spin_remPoi_callback(self,Off,spin:QSpinBox,flagX,flagPos):
        self.focusOnTarget(False)
        nameSpin=spin.objectName().split('spin_')[-1]
        setattr(self.VISpar,nameSpin,spin.value())
        if spin.hasFocus():
            self.calibView.spinRemPoints(Off,spin,flagX,flagPos)
    
    def copyRemPoints(self):
        self.focusOnTarget(False)
        self.calibView.copyRemPoints()

    def showMask(self):
        self.VISpar.FlagShowMask=self.ui.radio_showMask.isChecked()
        if not self.VISpar.FlagShowMask: self.VISpar.FlagPlotMask=False
        self.calibView.calib.flagShowMask=self.VISpar.FlagShowMask
        self.calibView.calib.flagPlotMask=self.VISpar.FlagPlotMask
    
    def plotMask(self):
        self.VISpar.FlagPlotMask=self.ui.tool_plotMask.isChecked()
        self.calibView.calib.flagPlotMask=self.VISpar.FlagPlotMask
        #self.restoreLevels()

#********************************************* Zoom functions
    def resetScaleFactor(self):
        ''' reset the scale factor so that the image perfectly feet the window'''
        self.calibView.resetScaleFactor(self.scrollArea.size())
        self.VISpar.scaleFactor=self.calibView.scaleFactor
        self.zoomImage(1)

    def zoom(self,zoom):
        ''' zooms f a factor zoom if negative reset to no zoom '''
        if zoom<=0:
            zoom =self.calibView.scaleFactor = 1.0
        self.zoomImage(zoom)
  
    def zoomImage(self, zoom):
        ''' zooms the image of self.CalibView.scaleFactor times a factor zoom
        adjust also the scrollBars'''
        self.calibView.scaleFactor *= zoom
        self.VISpar.scaleFactor=self.calibView.scaleFactor
        self.setZoom()
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), zoom)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), zoom)
        
    def setZoom(self):
        self.calibView.resize(self.calibView.scaleFactor * self.calibView.pixmap().size())
        
    def adjustScrollBar(self, scrollBar:QScrollBar, factor):
        ''' adjust the position when zooming in or out 
        # TBS copied and possibly modified wrongly'''  
        scrollBar.setValue(int(factor * scrollBar.value()+ ((factor - 1) * scrollBar.pageStep()/2)))


#********************************************* CalibView function
    def outFromCalibView(self,out:str):
        ''' output From CalibView called from plotImg'''
        calib=self.calibView.calib
        da=calib.cal.vect
        p=calib.plane
        c=int(p/calib.nPlanesPerCam)
        pc=p-c*calib.nPlanesPerCam
        
        self.VISpar.plane=pc
        self.VISpar.cam=c
        self.ui.spin_cam.setValue(c+1)
        self.ui.spin_plane.setValue(pc+1)
        
        self.ui.spin_xOriOff.setValue(da.xOrShift[p])
        self.ui.spin_yOriOff.setValue(da.yOrShift[p])

        self.ui.spin_xm.setValue(da.remPointsLe[p])
        self.ui.spin_xp.setValue(da.remPointsRi[p])
        self.ui.spin_ym.setValue(da.remPointsDo[p])
        self.ui.spin_yp.setValue(da.remPointsUp[p])

        if self.VISpar.FlagPlotMask:
            out2=' [CC mask]'
        else:
            out2=' [target image]'
        self.ui.status_R.setText(out+out2)
        self.calibView.setStatusTip(out+out2)

    def outToStatusBarFromCalibView(self,out:str):
        ''' output to status bar From CalibView '''
        self.ui.status_L.setText(out)
        #self.calibView.setToolTip(out)

    Slot(str)
    def textFromCalib(self,out:str):
        ''' set single line text from calib'''
        
        #print(f'textFromCalib  {out}')
        self.ui.log.setText(out)

        
        

    def workerCompleted(self,flagError):
        ''' called when worker has completed '''
        if flagError:
            warningDialog(self,'An error occurred during calibration!\n\nPlease, restart the procedure manually.')
        if  not self.calibView.flagCurrentTask is CalibTasks.stop:# pylint: disable=unneeded-not
            if self.calibView.executeCalibTask(CalibTasks.stop):
                self.setTaskButtonsText()

    def setTaskButtonsText(self):
        ''' set all the button texts and enable/disable them '''
        flagEnab=True if (self.calibView.flagCurrentTask==CalibTasks.stop) else False
        self.updateGCalVi()
        for f in  [f for f in CalibTasks if f.value>0]:
            if flagEnab:  # stop the process -> enable all buttons and restore text
                self.taskButtons [f.value-1].setText(calibTasksText[f.value])
                self.taskButtons [f.value-1].setEnabled(True)
            else:
                if self.calibView.flagCurrentTask is f: 
                    self.taskButtons [f.value-1].setText(calibTasksText[0])
                else:
                    self.taskButtons [f.value-1].setEnabled(False)
        for b in self.buttonsToDisable:
            b.setEnabled(flagEnab)
        for b  in  self.buttonsToDisableNotCalibrated:      
            b.setEnabled(self.calibView.calib.cal.flagCalibrated)    
        #for b in self.functionButtons:      b.setEnabled(flagEnab)
        #pri.Callback.green('-----abcde----- TaskButtonsText -----abcde-----')
   
    def taskButtonPressed(self,flag:CalibTasks,flagFocus):
        ''' one of the button has been  pressed '''
        if flagFocus: self.focusOnTarget()
        if self.calibView.executeCalibTask(flag):
            self.setTaskButtonsText()
        #pri.Callback.green('-----xxxxx----- taskButtonPressed -----xxxxx-----')
   
    def functionButtonPressed(self,flag:CalibTasks,flagFocus):
        ''' one of the button has been  pressed '''
        if flagFocus: self.focusOnTarget()
        self.calibView.executeCalibFunction(flag)  
        #pri.Callback.green('-----|||||----- functionButtonPressed -----|||||-----')
   
    def focusOnTarget(self,flagCallback=True):
        if self.VISpar.FlagPlotMask:
            self.ui.tool_plotMask.setChecked(False)
            self.tool_plotMask_callback()


#********************************************* Spin callbacks
    def spinImgChanged(self):
        ''' changes the plotted image'''
        pc=self.ui.spin_plane.value()-1
        self.VISpar.plane=pc
        c=self.ui.spin_cam.value()-1
        self.VISpar.cam=c
        if self.ui.spin_plane.hasFocus() or self.ui.spin_cam.hasFocus():
            self.plotPlane()

    def setImgFromGui(self):
        inddel=[]
        calib=self.calibView.calib    
        calib.imgs=[]
        calib.ccMask=[]
        flagFirstImage=True
        npType=np.uint16
        if self.list_Image_Files: #only used to read the first image and fix the img dimensions
            for j in range(len(self.list_Image_Files[0])):
                for k,fp in enumerate(self.list_Image_Files):
                    f=fp[j]
                    if self.list_eim[k][j]:
                        if f not in self.bufferImg:
                            im=Image.open(f)
                            #da=
                            self.bufferImg[f]=da=np.array(im,dtype=npType)
                        else:
                            da=self.bufferImg[f]
                        if flagFirstImage:
                            Him,Wim=da.shape
                            flagFirstImage=False
                            break
                if not flagFirstImage: break
        data=calib.cal.data
        if flagFirstImage:
            Him=data.ImgH
            Wim=data.ImgW
        if self.list_Image_Files: #reading the images 
            for j in range(len(self.list_Image_Files[0])):
                for k,fp in enumerate(self.list_Image_Files):
                    f=fp[j]
                    if f not in self.bufferImg:
                        if self.list_eim[k][j]:
                            im=Image.open(f)
                            da=np.array(im,dtype=npType)
                        else:
                            da=np.zeros((Him,Wim),dtype=npType)
                        self.bufferImg[f]=da
                    else:
                        da=self.bufferImg[f]
                    h,w=da.shape
                    if (Wim,Him)!=(w,h):
                        inddel.append(k)
                    calib.imgs.append(np.ascontiguousarray(da[data.RigaPart:data.RigaPart+data.ImgH,data.ColPart:data.ColPart+data.ImgW],dtype=npType))
                    if data.TipoTarget:
                        calib.imgs.append(np.ascontiguousarray(da[data.RigaPart:data.RigaPart+data.ImgH,data.ColPart:data.ColPart+data.ImgW],dtype=npType))

                
        self.bufferSize=0
        for f in self.bufferImg:#deleting buffer if to big
                a:np.ndarray=self.bufferImg[f]
                self.bufferSize+=a.size*a.itemsize
        if self.bufferSize>bufferSizeLimit:
                imgList=list(self.bufferImg)
                while self.bufferSize>bufferSizeLimit and len(imgList) and imgList[0] not in self.list_Image_Files:
                        k=0
                        f=imgList[k]
                        a=self.bufferImg[f]
                        self.bufferSize-=a.size*a.itemsize
                        self.bufferImg.pop(f)
                        imgList.pop(k)

        if calib.imgs:        
            calib.cal.setImgs(calib.imgs)
            calib.ccMask=calib.cal.getMask()
            pass
        return inddel

    def initDataFromGui(self,INP:INPpar_CalVi,PRO:PROpar_CalVi):
        calib=self.calibView.calib
        calib.cal.DefaultValues()
        calib.FlagCalibration=False
        self.list_Image_Files=INP.list_Image_Files
        self.list_eim=INP.list_eim
        self.FlagResume=0
        #-------------------------------------- %
        #            Not in cfg             %
        # --------------------------------------%
        
        data=calib.cal.data
        calVect=calib.cal.vect
        data.PercErrMax = 0.1                # 0.10 Percentuale massima per errore in posizioneTom da modificare 
        # InitParOptCalVi(&dati->POC); #todo

        #-------------------------------------- %
        #            Input and Output parameters             %
        # --------------------------------------%
        data.percorso = INP.path     #percorso file di input
        data.EstensioneIn = INP.ext #estensione in (b16 o tif)
        data.FlagCam=0 if len(INP.cams) else 1    
        data.percorsoOut = INP.pathout # percorso file di output
        data.NomeFileOut = INP.radout # nome file di output

        camString=''
        cams=INP.cams
        if cams:
            if len(cams)==1: camString=f'_cam{cams[0]}'
        else:
            cams=[-1]
        calib.cfgName=f'{data.percorsoOut}{data.NomeFileOut}{camString}.cfg'
        data.NCam = len(cams) # Numero di elementi nel vettore cam (numero di camere da calibrare)

        varName=f'{data.percorsoOut}{data.NomeFileOut}{camString}{outExt.cal}'
        #var=[INP,self.w_Process.PROpar,VIS]
        if os.path.exists(varName):
            with open(varName, 'rb') as file:
                var=pickle.load(file)
                self.FlagResume=1 if INP.isEqualTo(var[0],[],['cams','filenames','x','y','w','h','W','H']) else -1
                INP.printDifferences(var[0])
                if self.FlagResume>0:
                    self.VISpar.copyfrom(var[2],TABpar().fields+['FlagRun'])

        #-------------------------------------- %
        #            Distance between spots                     %
        # --------------------------------------%
        data.pasX = PRO.DotDx            # passo della griglia lungo X
        data.pasY = PRO.DotDy            # passo della griglia lungo Y

        #-------------------------------------- %
        #            Calibration parameters                     %
        # --------------------------------------%
        data.Threshold = PRO.DotThresh    # valore percentuale della soglia
        data.FlagPos = (2*bool(PRO.DotColor)-1)*([0,3,4,5,1,2][PRO.DotTypeSearch]+1)            # Tipo ricerca pallino 1 CC 2 Interp 3 geom Positivi pallini bianchi negativi pallini neri 4 e 5 TopHat piu gaussiana 6 gaussiana
        #Cal = (TipoCal >> CalFlags.SHIFT) & CalFlags.MASK;
        #Cyl = (TipoCal >> CalFlags.SHIFT_CYL) & CalFlags.MASK;
        data.raggioInizialeRicerca=int(PRO.DotDiam*2.5)
        calType=PRO.CalibProcType
        F_Ph=int(PRO.FlagPinhole)
        F_Pl=int(PRO.FlagPlane)
        F_Sa=int(PRO.FlagSaveLOS)
        P_Cyl=PRO.CorrMod_Cyl
        P_Ph=0
        data.TipoCal=calib.toTipoCal(calType,F_Ph,F_Pl,F_Sa,P_Cyl,P_Ph) # Calibration type [Type F_Ph F_Pl F_Sa P_Cyl P_Ph] 	

        #-------------------------------------- %
        #                        Image Parameters                     %
        # --------------------------------------%
        data.ImgW=INP.w
        data.ImgH=INP.h
        data.ColPart=INP.x
        data.RigaPart=INP.y

        #-------------------------------------- %
        #                     Target parameters                     %
        # --------------------------------------%
        data.TipoTarget = PRO.TargetType # Tipo di target 0 normale singolo piano 1 doppio piano con dx dy sfalsato al 50%)
        data.dx = PRO.OriginXShift                 # TipoTarget==1 sfasamento fra i piani target altirmenti non utlizzato
        data.dy = PRO.OriginYShift                 # TipoTarget==1 sfasamento fra i piani target altirmenti non utlizzato
        data.dz = PRO.OriginZShift                # TipoTarget==1 distanza fra i piani target altirmenti non utlizzato
        if data.TipoTarget==0:            data.dx = data.dy = data.dz = 0
        data.Numpiani_PerCam=len(INP.filenames)*(data.TipoTarget+1) # numero di piani da calibrare per camera in caso di target doppio piano inserire 2 * numero di spostamenti target
        data.Numpiani = data.NCam * data.Numpiani_PerCam

        if len(INP.filenames) <1 : #when initializing the filenames are not known
            return

        CamModType=[1,2,3,10,30][PRO.CamMod]
        if CamModType in (1,2,3):
            modPar=[PRO.XDeg,PRO.YDeg,PRO.ZDeg]
        elif CamModType==10:
            CamModType+=[0,2,4][PRO.CorrMod]
            modPar=[PRO.PixAR,PRO.PixPitch]
        elif CamModType==30:
            CamModType+=[0,2,4,5,6,7,8][PRO.CorrMod]
            modPar=[PRO.PixAR,PRO.PixPitch,PRO.CylRad,PRO.CylThick,PRO.CylNRatio]
        additionalPar=[CamModType]+modPar     # Calibration type and parameters 	(12)    

        calib.cal.allocAndinit(additionalPar,0)
        for i,c in enumerate (cams):
            calVect.cam[i]=c

        # -------------------------------------- %
        #             Plane img name and coordinates     %
        # -------------------------------------- %
        imgRoot=[]
        for f in INP.filenames:
            if data.FlagCam==0:
                imgRoot.append(os.path.splitext(f)[0].replace('_cam*',''))
            else:
                imgRoot.append(os.path.splitext(f)[0])

        
        if calType:
            z=[0.0]*len(INP.plapar)
            costPlanes=INP.plapar
        else:
            z=[p[-1] for p in INP.plapar]
            costPlanes=[[0.0]*5+[zk] for zk in z]
        if data.TipoTarget==1:
            for k in range(len(INP.filenames)):
                k2=k*2+1
                imgRootk=imgRoot[2*k]
                imgRoot.insert(k2,imgRootk)
                zk=z[2*k]
                z.insert(k2,zk+data.dz)
                cP=costPlanes[2*k]
                cP2=[c for c in cP]
                cP2[-1]+=data.dz
                costPlanes.insert(k2,cP2)
            pass

        
        for p1 in range(data.Numpiani_PerCam):
            for c in range(data.NCam):
                p=p1+c*data.Numpiani_PerCam
                calib.cal.setImgRoot(p,imgRoot[p1])
                calVect.z[p]    = z[p1]

                if self.FlagResume<=0:
                    calVect.XOr[p] = calVect.YOr[p]  = calVect.angCol[p]  = calVect.angRow[p]  = calVect.xOrShift[p] = calVect.yOrShift[p] = 0
                    calib.cal.setPuTrovaCC([0,0,0,0],p)
                    calVect.dColPix[p] =calVect.dRigPix[p] = 10000 #not really important but has to be big
                    calVect.remPointsUp[p] = calVect.remPointsDo[p] = calVect.remPointsLe[p] = calVect.remPointsRi[p] = 0
                else:
                    calVect.XOr[p]  = self.VISpar.orPosAndShift[p][0] + data.ColPart
                    calVect.YOr[p]  = self.VISpar.orPosAndShift[p][1] + data.RigaPart
                    calVect.angCol[p]  = self.VISpar.angAndMask[p][0]
                    calVect.angRow[p]  = self.VISpar.angAndMask[p][1]

                    calVect.xOrShift[p] = round(self.VISpar.orPosAndShift[p][2])
                    calVect.yOrShift[p] = round(self.VISpar.orPosAndShift[p][3])

                    self.calibView.calib.cal.setPuTrovaCC(self.VISpar.angAndMask[p][2:],p)
                    #calVect.flagPlane[p]|= PaIRS_lib.CalFlags.PLANE_NOT_INIT_TROVA_PUNTO|PaIRS_lib.CalFlags.PLANE_NOT_FOUND
                    #self.cal.getPuTrovaCC(p)
                    calVect.dColPix[p] = round(self.VISpar.spotDistAndRemoval[p][0])
                    calVect.dRigPix[p] = round(self.VISpar.spotDistAndRemoval[p][1])
                    #self.cal.calcBounds(p)
                    calVect.remPointsUp[p] = round(self.VISpar.spotDistAndRemoval[p][2])
                    calVect.remPointsDo[p] = round(self.VISpar.spotDistAndRemoval[p][3])
                    calVect.remPointsLe[p] = round(self.VISpar.spotDistAndRemoval[p][4])
                    calVect.remPointsRi[p] = round(self.VISpar.spotDistAndRemoval[p][5])
            
                
            if calType!=0: #no standard calibration    planes involved
                calVect.costPlanes[p1]=costPlanes[p1]
        calib.cal.allocAndinit(additionalPar,1)
        errorFiles=[[],[]]
        if calType >= 2:# Calibrazione piano per controllo     Legge le costanti di calibrazione
            # si devono leggere o passare le costanti di calibrazione
            for cam in range(data.NCam):
                buffer=f'{data.percorso}{data.NomeFileOut}{abs(calVect.cam[cam])}.cal'
                if os.path.exists(buffer):
                    try:
                        calib.readCalFile(buffer,calVect.cost[cam],data.NumCostCalib,CamModType)
                    except Exception as inst:
                        errorFiles[1].append(f'{os.path.basename(buffer)} ({inst})')
                else:
                    errorFiles[0].append(f'{os.path.basename(buffer)}')
        errorMessage=''
        if len(errorFiles[0]) or len(errorFiles[1]):
            errorMessage='Error while initialising the calibration process.\n\n'
            if len(errorFiles[0]):
                errList=f";\n   ".join(errorFiles[0])
                errorMessage+=f'The following files do not exist in the specified path ({data.percorso}):\n   {errList}.\n\n'         
            if len(errorFiles[1]):
                errList=f";\n   ".join(errorFiles[1])
                errorMessage+=f'There were errors with opening the following files in the specified path ({data.percorso}):\n   {errList}.'         
            #pri.Error.blue(errorMessage)
        self.VISpar.errorMessage=errorMessage

        calib.cal.allocAndinit(additionalPar,2)

        pri.Process.yellow(f'TipoCal = [{calType} {F_Ph} {F_Pl} {F_Sa} {P_Cyl} {P_Ph}]')
        pri.Process.yellow(f'initDataFromGui:     additionalPar={additionalPar}')
        pri.Process.yellow(f'initDataFromGui:     plapar={INP.plapar},     z={z}')
        pri.Process.yellow(f'initDataFromGui:     calVect.z={calVect.z}')


        calib.nCams=calib.cal.data.NCam
        calib.cams=calib.cal.getCams()
        calib.nPlanes=calib.cal.data.Numpiani
        calib.nPlanesPerCam=calib.cal.data.Numpiani_PerCam

        return 
  
if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Vis_Tab_CalVi(None)
    object.show()
    app.exec()
    app.quit()
    app=None