from .ui_Process_Tab_CalVi import*
from .TabTools import*

DotColor_labels=['Black dot', #0
                'White dot',  #1
                ]

DotTypeSearch_items=['cross-correlation mask',        #0
                     'top hat mask with tight tails', #1
                     'top hat mask with broad tails', #2
                     'Gaussian mask',                 #3
                     'interpolation',                 #4
                     'centroid',                      #5
                        ]
DotTypeSearch_order=[i for i in range(len(DotTypeSearch_items))] #************ change here, please!

TargetType_items=['single plane', #0
                  'double plane', #1
                    ]
TargetType_order=[i for i in range(len(TargetType_items))] #************ change here, please!

CamMod_items=['polynomial',         #0
              'rational',           #1
              'tri-polynomial',     #2
              'pinhole',            #3
              'pinhole + cylinder', #4
                ]
CamMod_order=[i for i in range(len(CamMod_items))] #************ change here, please!

CorrMod_items=['a: no correction',              #0
               'b: radial distortions',         #1
               'c: b + tangential distortions', #2
               'd: c + cylinder origin',        #3
               'e: d + cylinder rotation',      #4
               'f: e + cylinder radius and thickness', #5
               'g: f + refractive index ratio', #6
                ]
CorrMod_order=[i for i in range(len(CorrMod_items))] #************ change here, please!

CalibProcType_items=['standard',                #0
                     'unknown planes',          #1
                     'equation of the plane',   #2
                     'cylinder',                #3
                     ]
CalibProcType_order=[i for i in range(len(CalibProcType_items))] #************ change here, please!

CorrMod_Cyl_items=[ 'a: cylinder origin and rotation',      #0
                    'b: a + cylinder thickness',            #1
                    'c: b + refractive index (n) ratio',    #2
                    'd: b + internal radius',               #3
                    'e: a + internal radius and n ratio',   #4
                    'f: all cylinder parameters',           #5
                    ]
CorrMod_Cyl_order=[i for i in range(len(CorrMod_Cyl_items))] #************ change here, please!



def cont_fields(diz):
    cont=0
    for f,v in diz:
        if not 'fields' in f and f[0]!='_':
            cont+=1
    return cont
    
class PROpar_CalVi(TABpar):

    def __init__(self,*args):
        self.setup()
        super().__init__()
        self.name='PROpar'
        self.surname='PROCESS_Tab_CalVi'
        self.unchecked_fields+=['FlagTarget_reset','FlagCalib_reset']

    def setup(self):
        #***Dot
        self.DotColor=0
        self.DotTypeSearch=0
        self.DotThresh=0.5
        self.DotDiam=10

        #***Type of target
        self.TargetType=0
        self.DotDx=5
        self.DotDy=5
        #double plane target
        self.OriginXShift=2.5
        self.OriginYShift=2.5
        self.OriginZShift=2.5

        #***Calibration procedure
        self.CalibProcType=0  #standard
        self.FlagPlane=0
        self.FlagPinhole=1  

        #***Camera calibration model
        self.CamMod=3
        #polynomials/rational functions
        self.XDeg=2
        self.YDeg=2
        self.ZDeg=2
        #pinhole
        self.PixAR=1
        self.PixPitch=0.0065
        #correction model
        self.CorrMod=2  #radial+tangential distortions
        #cylinder parameters
        self.CylRad=30
        self.CylThick=2
        self.CylNRatio=1
        #correction model cylinder
        self.CorrMod_Cyl=0  #cylinder origin and rotation
        self.FlagSaveLOS=0


class Process_Tab_CalVi(gPaIRS_Tab):
    class Process_Tab_Signals(gPaIRS_Tab.Tab_Signals):
        pass

    def __init__(self,*args):
        parent=None
        flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: flagInit=args[1]
        super().__init__(parent,Ui_ProcessTab_CalVi,PROpar_CalVi)
        self.signals=self.Process_Tab_Signals(self)
    
        #------------------------------------- Graphical interface: widgets
        self.ui: Ui_ProcessTab_CalVi
        ui=self.ui

        #necessary to change the name and the order of the items
        self.spins=self.findChildren(MyQSpin)+self.findChildren(MyQDoubleSpin)
        self.checks=self.findChildren(QCheckBox)
        self.combos=self.findChildren(QComboBox)
        for c in self.combos:
            c:QComboBox
            nameCombo=c.objectName().split('combo_')[-1]
            itemsCombo=eval(nameCombo+'_items')
            orderCombo=eval(nameCombo+'_order')
            c.clear()
            for i in orderCombo:
                c.addItem(itemsCombo[i])

        self.setupWid()  #---------------- IMPORTANT

        #------------------------------------- Graphical interface: miscellanea
        self.Flag_CYLINDERCAL_option=None
        self.Flag_CYLINDERCAL=True

        #------------------------------------- Declaration of parameters 
        self.PROpar_base=PROpar_CalVi()
        self.PROpar:PROpar_CalVi=self.TABpar
        self.PROpar_old:PROpar_CalVi=self.TABpar_old
        self.defineSetTABpar(self.setPROpar)

        #------------------------------------- Callbacks 
        self.setupCallbacks()

        #------------------------------------- Initializing    
        if flagInit:     
            self.initialize()


    def initialize(self):
        pri.Info.yellow(f'{"*"*20}   PROCESS initialization   {"*"*20}')
        self.setTABpar(True)
        
    def setupCallbacks(self):
        #Callbacks
        
        spin_names=['DotThresh',
                    'DotDiam',
                    'DotDx',
                    'DotDy',
                    'OriginXShift',
                    'OriginYShift',
                    'OriginZShift',
                    'XDeg',
                    'YDeg',
                    'ZDeg',
                    'PixAR',
                    'PixPitch',
                    'CylRad',
                    'CylThick',
                    'CylNRatio'
                    ]
        spin_tips=['Threshold on maximum/minimum value for search of control points',
                   'Dot diameter in pixels (search radius is 2.5 times this value)',
                   'Spacing of dots along x on each level of the target',
                   'Spacing of dots along y on each level of the target',
                   'Shift of the origin along x on the second level of the target',
                   'Shift of the origin along y on the second level of the target',
                   'Shift of the origin along z on the second level of the target',
                   'Degree of polynomial along x',
                   'Degree of polynomial along y',
                   'Degree of polynomial along z',
                   'Pixel aspect ratio (y/x)',
                   'Pixel pitch in millimeter units',
                   'Initial value for cylinder internal radius in mm',
                   'Initial value for cylinder wall thickness in mm',
                   'Refractive index ratio (fluid/solid wall)'
                   ]
        self.defineSpinCallbacks()
        self.setSpinCallbacks(spin_names,spin_tips)

        self.defineCheckCallbacks()
        self.defineComboCallbacks()

        signals=[["clicked"], #button
                 ["toggled"], #check
                 ["activated"],  #combo      #"currentIndexChanged"   #***** rimpiazzare?
                 ]  
        fields=["button",
                "check",
                "combo",
                ]
        names=[ ['DotColor'], #button
                ['Plane',
                 'Pinhole',
                 'SaveLOS'], #check
                ['DotTypeSearch',
                 'TargetType',
                 'CalibProcType',
                 'CamMod',
                 'CorrMod',
                 'CorrMod_Cyl'], #combo
                  ]
        tips=[ ['White/black dot in the image'], #button
                ['Optimize the plane constants',
                 'Optimize the pinhole parameters',
                 'Save physical coordinates of the intersections of the lines of sight with the cylinder'], #check
                ['Type of search for control points',
                 'Type of target (single or double plane)',
                 'Type of calibration procedure',
                 'Type of mapping function',
                 'Parameters of the correction to be optimized',
                 'Cylinder parameters of the correction to be optimized'], #combo
                  ]
        
        for f,N,S,T in zip(fields,names,signals,tips):
            for n,t in zip(N,T):
                wid=getattr(self.ui,f+"_"+n)
                fcallback=getattr(self,f+"_"+n+"_callback")
                fcallbackWrapped=self.addParWrapper(fcallback,t)
                for s in S:
                    sig=getattr(wid,s)
                sig.connect(fcallbackWrapped)

    
    def defineSpinCallbacks(self):
        spins=self.findChildren(MyQSpin)+self.findChildren(MyQDoubleSpin)
        for c in spins:
            c:MyQSpin
            nameSpin=c.objectName().split('spin_')[-1]
            def createCallback(nameSpin):
                    def callbackFun():
                        setattr(self.PROpar,nameSpin,getattr(self.ui,'spin_'+nameSpin).value())
                    return callbackFun
            setattr(self,'spin_'+nameSpin+'_callback',createCallback(nameSpin))
    
    def defineCheckCallbacks(self):
        checks=self.findChildren(QCheckBox)
        for c in checks:
            c:QCheckBox
            nameCheck=c.objectName().split('check_')[-1]
            def createCallback(nameCheck):
                    def callbackFun():
                        setattr(self.PROpar,'Flag'+nameCheck,getattr(self.ui,'check_'+nameCheck).isChecked())
                        if hasattr(self,'check_'+nameCheck+'_action'):
                            fun=getattr(self,'check_'+nameCheck+'_action')
                            fun()
                    return callbackFun
            setattr(self,'check_'+nameCheck+'_callback',createCallback(nameCheck))
    
    def defineComboCallbacks(self):
        combos=self.findChildren(QComboBox)
        for c in combos:
            c:QComboBox
            nameCombo=c.objectName().split('combo_')[-1]
            def createCallback(nameCombo):
                    def callbackFun():
                        itemText=getattr(self.ui,'combo_'+nameCombo).currentText()
                        itemsCombo=eval(nameCombo+'_items')
                        setattr(self.PROpar,nameCombo,itemsCombo.index(itemText))
                        if hasattr(self,'combo_'+nameCombo+'_action'):
                            fun=getattr(self,'combo_'+nameCombo+'_action')
                            fun()
                    return callbackFun
            setattr(self,'combo_'+nameCombo+'_callback',createCallback(nameCombo))
            
 #*************************************************** Target parameters callbacks
    def button_DotColor_callback(self):
        if self.ui.button_DotColor.text()==DotColor_labels[0]: self.PROpar.DotColor=1
        else: self.PROpar.DotColor=0

 #*************************************************** Calibration parameters callbacks (action)
    def combo_CalibProcType_action(self):
        if self.PROpar.CalibProcType in (1,2):
            self.PROpar.FlagPlane=1

        if self.PROpar.CalibProcType in (0,1):
            self.PROpar.FlagPinhole=1
        elif self.PROpar.CalibProcType==2:
            self.PROpar.FlagPinhole=0

        if self.PROpar.CalibProcType in (1,2) and self.PROpar.CamMod!=3:
            self.PROpar.CamMod=3
        elif self.PROpar.CalibProcType==3:
            self.PROpar.CamMod=4
        self.combo_CamMod_action()
        if self.father:
            self.father.w_Import.check_cams()

    def combo_CamMod_action(self):
        if not(self.PROpar.CalibProcType==0 and self.PROpar.CamMod==4) and self.PROpar.CorrMod>2:
            self.PROpar.CorrMod=2
    
    def check_SaveLOS_action(self):
        if self.ui.check_SaveLOS.isChecked():
            warningDialog(self,'Please notice that the feature to save the lines-of-sight (LOS) data to the disk is not currently available!\n\nContact the authors via email if interested.')

#*************************************************** From Parameters to UI
    def setCYLPARDebug(self):
        #combo_CalibProcType
        self.ui.combo_CalibProcType.clear()
        if self.Flag_CYLINDERCAL: l=len(CalibProcType_items)
        else: l=len(CalibProcType_items)-1
        for it in CalibProcType_items[:l]:
            self.ui.combo_CalibProcType.addItem(it)
        if bool(self.Flag_CYLINDERCAL_option):
            self.Flag_CYLINDERCAL_option.setEnabled(self.PROpar.CalibProcType!=3)

    def setPROpar(self):
        #pri.Time.blue(1,'setPROpar: Beginning')
        if self.PROpar.TargetType==0:
            self.ui.w_DoublePlane.hide()
        else:
            self.ui.w_DoublePlane.show()

        self.setCYLPARDebug()

        #check_Plane
        if self.PROpar.CalibProcType==0:
            self.ui.check_Plane.setText('Show plane const.')
        else:
            self.ui.check_Plane.setText('Opt. plane const.')        
        if self.PROpar.CalibProcType in (1,2):
            self.ui.check_Plane.setChecked(True)
            self.ui.check_Plane.setEnabled(False)
        else:
            self.ui.check_Plane.setEnabled(True)

        #check_Pinhole
        if self.PROpar.CalibProcType!=3:
            self.ui.check_Pinhole.setChecked(self.PROpar.CalibProcType<2)
            self.ui.check_Pinhole.setEnabled(False)
        else:
            self.ui.check_Pinhole.setEnabled(True)

        #combo_CamMod
        self.ui.combo_CamMod.clear()
        flagEnabled=True
        if self.PROpar.CalibProcType==0:
            for it in CamMod_items:
                self.ui.combo_CamMod.addItem(it)
        elif self.PROpar.CalibProcType in (1,2): #unknwon planes (2) compatible with cylinder ?
            self.ui.combo_CamMod.addItem(CamMod_items[3])
            flagEnabled=False
        elif self.PROpar.CalibProcType==3:
            self.ui.combo_CamMod.addItem(CamMod_items[-1])
            flagEnabled=False
        self.ui.combo_CamMod.setEnabled(flagEnabled)
            
        #stacked_Widget
        if self.PROpar.CamMod<3:
            self.ui.w_CamMod_par.setCurrentIndex(0)
            self.ui.check_Plane.setVisible(False)
            self.ui.check_Pinhole.setVisible(False)
        else:
            self.ui.w_CamMod_par.setCurrentIndex(1)
            self.ui.check_Plane.setVisible(True)
            self.ui.check_Pinhole.setVisible(True)

        if self.PROpar.CamMod>=3 and not self.PROpar.FlagPinhole:
            self.ui.w_CamMod_par.setEnabled(False)
        else:
            self.ui.w_CamMod_par.setEnabled(True)

        #combo_corrMod
        self.ui.w_CylPar.setVisible(self.PROpar.CamMod==4)
        if self.PROpar.CamMod<3 or not self.PROpar.FlagPinhole:
            self.ui.combo_CorrMod.hide()
            self.ui.label_CorrMod.hide()
        else:
            self.ui.combo_CorrMod.show()
            self.ui.label_CorrMod.show()

            self.ui.combo_CorrMod.clear()
            if self.PROpar.CalibProcType==0 and self.PROpar.CamMod==4: l=len(CorrMod_items)
            else: l=3
            for it in CorrMod_items[:l]:
                self.ui.combo_CorrMod.addItem(it)            

        if self.PROpar.CalibProcType!=3:
            self.ui.w_CalibProc_Cyl.hide()
        else:
            self.ui.w_CalibProc_Cyl.show()


        #***Dot
        self.ui.button_DotColor.setText(DotColor_labels[self.PROpar.DotColor])
        for s in self.spins:
            s:MyQSpin
            nameSpin=s.objectName().split('spin_')[-1]
            s.setValue(getattr(self.PROpar,nameSpin))
        for c in self.checks:
            c:QCheckBox
            nameCheck=c.objectName().split('check_')[-1]
            c.setChecked(getattr(self.PROpar,'Flag'+nameCheck))
        for b in self.combos:
            b:QComboBox
            nameCombo=b.objectName().split('combo_')[-1]
            items=[b.itemText(i) for i in range(b.count())]
            itemsCombo=eval(nameCombo+'_items')
            b.setCurrentIndex(items.index(itemsCombo[getattr(self.PROpar,nameCombo)]))
        #pri.Time.blue(0,'setPROpar: end')
    

if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Process_Tab_CalVi(None)
    object.show()
    app.exec()
    app.quit()
    app=None
