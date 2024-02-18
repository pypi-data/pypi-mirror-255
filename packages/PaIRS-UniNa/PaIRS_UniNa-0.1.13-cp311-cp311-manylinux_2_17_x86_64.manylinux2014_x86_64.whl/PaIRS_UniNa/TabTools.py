
from .PaIRS_pypacks import *
from .addwidgets_ps import *

Num_Prevs_Max=100
Num_Prevs_back_forw=10

FlagAsyncCallbacks=True
FlagSimulateError=False
globExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=10)  
class TABpar:
    def __init__(self,*args): 
        if len(args):
            self.name=args[0]
        else:
            self.name=str(uuid.uuid4())[:8]
        if len(args)>1:
            self.surname=args[1]
        else:
            self.surname=str(uuid.uuid4())[:8]
        self.ind=0   #fondamentale che sia 0
        self.indItem=0
        self.indTree=0
        self.tip='...'

        self.fields=[f for f,_ in self.__dict__.items()]
        self.uncopied_fields=['tip']
        self.unchecked_fields=['name','surname']+self.uncopied_fields
        pass

    def printPar(self,*args):
        before=after=''
        if len(args)>0: before=args[0]
        if len(args)>1: after=args[1]
        print(before+str(self.__dict__)+after)

    def duplicate(self):
        newist=type(self)()
        for f in self.fields:
            a=getattr(self,f)
            if  hasattr(a,'duplicate'): #type(a)==patternInfoList:
                setattr(newist,f,a.duplicate())
            else:
                setattr(newist,f,copy.deepcopy(a))
        return newist

    def copyfrom(self,newist,*args):
        """
        #args=exceptions
        """
        self.copyfromdiz(newist,self.fields,*args)

    def copyfromdiz(self,newist,diz,*args):
        """
        #args=exceptions
        """
        exceptions=self.uncopied_fields
        if len(args): exceptions=args[0]
        for f in diz:
            if f in exceptions: continue
            if not hasattr(self,f):
                pri.Error.red(f'copyfromdiz: field <{f}> is missing in {self.name} par structure!')
                continue
            if not hasattr(newist,f):
                pri.Error.red(f'copyfromdiz: field <{f}> is missing in {newist.name} par structure!')
                continue
            a=getattr(newist,f)
            b=getattr(self,f)
            if hasattr(a,'duplicate'): #type(a)==patternInfoList:
                if hasattr(a,'isDifferentFrom'): flag=a.isDifferentFrom(b,[],[])
                else: flag=True
                if flag: setattr(self,f,a.duplicate())
            else:
                if a!=f:
                    setattr(self,f,copy.deepcopy(a))
    
    def isDifferentFrom(self,v,*args):
        """
        #args=exceptions,fields,FlagStrict
        """
        exceptions=[]
        fields=self.fields
        FlagStrictDiff=False 
        if len(args): 
            exceptions=args[0]
            if len(args)>1: 
                if len(args[1]):
                    fields=args[1]           
            if len(args)>2: FlagStrictDiff=args[2] 
        if FlagStrictDiff: exceptions+=self.unchecked_fields
        Flag=False
        for f in fields:
            if f in exceptions: continue
            else:
                if not hasattr(self,f):
                    pri.Error.red(f'isDifferentFrom: field <{f}> is missing in {self.name} par structure!')
                    continue
                if not hasattr(v,f):
                    pri.Error.red(f'isDifferentFrom: field <{f}> is missing in {v.name} par structure!')
                    continue 
                a=getattr(self,f)
                b=getattr(v,f)
                if f=='Vect':
                    Flag=not all([np.array_equal(a[i],b[i]) for i in range(4)])
                    if Flag: 
                        break
                else:
                    if hasattr(a,'isDifferentFrom'): #in ('Pinfo','pinfo'):
                        if hasattr(a,'fields'):
                            Flag=a.isDifferentFrom(b,exceptions,a.fields,FlagStrictDiff)
                        else:
                            Flag=a.isDifferentFrom(b,exceptions)
                        if Flag: 
                            break
                    else:
                        if a!=b:
                            Flag=True
                            break
        if len(args)<2:
            if Flag:  
                pri.Callback.red(f'{self.name} is different in {f}:\t {b}   -->   {a}')
            else: 
                pri.Callback.green(f'{self.name} is unchanged')
        return Flag
    
    def isEqualTo(self,v,*args):
        """
        #args=exceptions,fields,FlagStrict
        """
        Flag=not self.isDifferentFrom(v,*args)
        return Flag
    
    def printDifferences(self,v,*args):
        """
        #args=exceptions,fields,FlagStrict
        """
        exceptions=[]
        fields=self.fields
        FlagStrictDiff=False 
        if len(args): 
            exceptions=args[0]
            if len(args)>1: 
                if len(args[1]):
                    fields=args[1]           
            if len(args)>2: FlagStrictDiff=args[2] 
        FlagStrictDiff=False 
        if len(args): FlagStrictDiff=args[0]
        if FlagStrictDiff: exceptions+=self.unchecked_fields
        df=''
        for f in fields:
            if f in exceptions: continue
            if not hasattr(self,f):
                pri.Error.red(f'printDifferences: field <{f}> is missing in {self.name} par structure!')
                continue
            if not hasattr(v,f):
                pri.Error.red(f'printDifferences: field <{f}> is missing in {v.name} par structure!')
                continue 
            a=getattr(self,f)
            b=getattr(v,f)
            Flag=False
            if f=='Vect':
                Flag=not all([np.array_equal(a[i],b[i]) for i in range(4)])
            else:
                if hasattr(a,'isDifferentFrom'): #in ('Pinfo','pinfo'):
                    if hasattr(a,'fields'):
                        Flag=a.isDifferentFrom(b,[],a.fields,FlagStrictDiff)
                        if Flag:
                            a.printDifferences(b,[],a.fields,FlagStrictDiff)
                    else:
                        Flag=a.isDifferentFrom(b,[])
                else:
                    if a!=b: Flag=True
            if Flag: 
                if not df: df=f'{self.name} differences in:'
                df=df+f'\n*\t{f}:\t {str(a)[:100]}   -->   {str(b)[:100]}'
        if not df: df=f'{self.name} no differences!'
        pri.Callback.magenta(df)

    def hasIndexOf(self,d):
      """ check if the indexes are the same """
      return self.indexes()==d.indexes()            

    def indexes(self):
        """
        indTree,indItem,ind=TABpar.indexes()
        """
        return self.indTree, self.indItem, self.ind
        
                        
class gPaIRS_Tab(QWidget):
    indTreeGlob=0
    indItemGlob=0
    FlagGlob=False

    class Tab_Signals(QObject):
        setTABpar_final=Signal(int,int,int)

        def __init__(self, parent):
            super().__init__(parent)
            self.setTABpar_final.connect(parent.setTABpar_final)

    def __init__(self,parent=None,UiClass=None,ParClass=TABpar):
        super().__init__()
         
        self.TABname='Tab'
        self.signals=self.Tab_Signals(self)
        self.father=parent
        
        self.ParClass=ParClass
        self.TABpar=self.ParClass()            #current configuration 
        self.TABpar_old=self.ParClass()        #last configuration in the current tab
        self.TABpar_prev=[[[self.ParClass()]],[],[]] #queue of previous configurations, alias undos/redos (indTree,indItem,ind)
        self.FlagAddingPar=[[[False]],[],[]]     #while executing add_TABpar function it is set to False to avoid recursion
        self.FlagAsyncCall=[[[False]],[],[]]   #while executing async callback part (fun2) it is set to True to avoid updating of parameters  
        self.Num_Prevs_Max=Num_Prevs_Max

        self.FlagNoWrapper=False  #if True, the addParWrapper is ineffective, thus no addition to "prev", no updating of last configuration
        self.FlagAddPrev=True     #if False, no further par are added to the queue of undos/redos "prev"

        self.setTABpar=lambda flagBridge: None
        self.setTABpar_prev=lambda itree,iitem,i,flagBridge: None
        self.set_TABpar_bridge=lambda: None
        self.set_TABpar_prev_bridge=lambda  itree,iitem,i: None
        self.add_TABpar_bridge=lambda tip,itree,iitem,i: None

        self.fUpdatingTabs=lambda flag: None

        #Controls
        if UiClass!=None:
            self.ui=UiClass()
        if hasattr(self.ui,'setupUi'):
            self.ui.setupUi(self)
        if hasattr(self.ui,'name_tab'):
            self.name_tab=self.ui.name_tab.text().replace(' ','')
        else:
            self.name_tab=''

        self.undo_icon=QIcon()
        self.undo_icon.addFile(u""+ icons_path +"undo.png", QSize(), QIcon.Normal, QIcon.Off)  
        self.redo_icon=QIcon()
        self.redo_icon.addFile(u""+ icons_path +"redo.png", QSize(), QIcon.Normal, QIcon.Off)  
        if not hasattr(self.ui,'button_back'): 
            setattr(self.ui,'button_back',QPushButton(self))
        else:
            self.ui.button_back.contextMenuEvent=lambda e: self.bfContextMenu(-1,e)
        if not hasattr(self.ui,'button_forward'): 
            setattr(self.ui,'button_forward',QPushButton(self))
        else:
            self.ui.button_forward.contextMenuEvent=lambda e: self.bfContextMenu(+1,e)
        if not hasattr(self.ui,'label_number'): 
            setattr(self.ui,'label_number',QLabel(self))
        if hasattr(self.ui,'button_close_tab'):
            b:QPushButton=self.ui.button_close_tab
            b.setCursor(Qt.CursorShape.PointingHandCursor)

        self.ui.button_back.clicked.connect(self.button_back_callback)
        self.ui.button_forward.clicked.connect(self.button_forward_callback)

        self.FlagDisplayControls=True  #if False, undo and redo buttons are hidden and so not usable
        self.ui.button_forward.hide()
        self.ui.button_back.hide()
        self.ui.label_number.setText('')
        self.ui.label_number.hide()

    def setupWid(self):
        setupWid(self)  
        fPixSize_TabNames=30
        qlabels=self.findChildren(QLabel)
        labs=[l for l in qlabels if 'name_tab' in l.objectName()]
        for lab in labs:
            lab:QLabel #=self.ui.name_tab
            font=lab.font()
            font.setPixelSize(fPixSize_TabNames)
            lab.setFont(font)    

#*************************************************** Undo/redo
    def addParWrapper(self,fun,name,*args):  
        async def fun2_async(fun2,TABpar_prev):
            pri.Callback.magenta(f'{"#"*60}  async callback in {self.TABname} [{TABpar_prev.indTree}][{TABpar_prev.indItem}][{TABpar_prev.ind}]    --- start')
            if Flag_DEBUG: timesleep(time_fun2_async)
            try:
                TABpar_prev=fun2(TABpar_prev)
            except Exception as inst:
                funcname=''
                if hasattr(fun,'__func__'): 
                        if hasattr(fun.__func__,'__name__'):
                            funcname=f' [{fun.__func__.__name__}]'
                pri.Error.red(f"{'!'*100}\naddParWrapper Error fun2{funcname}:\n{traceback.format_exc()}\n\n{inst}\n{'!'*100}")
                if Flag_DEBUG: raise Exception("!!! Debug stop !!!") 
            return TABpar_prev
        def callbackfun():
            if self.FlagAddingPar[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind]: return
            if self.FlagAsyncCall[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind]: 
                pri.Callback.red(f'{"*"*30} callback from [{name}] {self.TABname} [{self.TABpar.indTree}][{self.TABpar.indItem}][{self.TABpar.ind}]    --- skipped')
                self.TABpar.copyfrom(self.TABpar_prev[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind])
                self.setTABpar(False)   #setting parameters with bridge
                return
            else:
                pri.Callback.green(f'{"*"*30} callback from [{name}] {self.TABname} [{self.TABpar.indTree}][{self.TABpar.indItem}][{self.TABpar.ind}]    --- executing')
                pass
            if fun==None: 
                self.add_TABpar(name)
                self.setTABpar(True)   #setting parameters with bridge
            else:
                try: 
                    output=fun(*args)
                    if output!=None:
                        flagAddPar=output[0]
                        fun2=output[1]
                    else:
                        flagAddPar=1
                        fun2=None
                except Exception as inst:
                    funcname=''
                    if hasattr(fun,'__func__'): 
                        if hasattr(fun.__func__,'__name__'):
                            funcname=f' [{fun.__func__.__name__}]'
                    pri.Error.red(f"{'!'*100}\naddParWrapper Error fun{funcname}:\n{traceback.format_exc()}\n\n{inst}\n{'!'*100}")
                    flagAddPar=0
                    fun2=None
                    if Flag_DEBUG: raise Exception("!!! Debug stop !!!") 
                finally:
                    if self.FlagNoWrapper: 
                        return
                    try:  
                        if flagAddPar>0:
                            self.add_TABpar(name)  #adding parameters to prev
                        if flagAddPar>-1:
                            self.TABpar_prev[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind].copyfrom(self.TABpar)
                            self.setTABpar(True)   #setting parameters with bridge
                        if fun2!=None:
                            TABpar_prev=self.TABpar_prev[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind]
                            self.FlagAsyncCall[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind]=True
                            self.fUpdatingTabs(True)

                            if FlagAsyncCallbacks:
                                f3=globExecutor.submit(asyncio.run,fun2_async(fun2,TABpar_prev))
                                def f3callback(_f3):
                                    self.signals.setTABpar_final.emit(self.TABpar.indTree,self.TABpar.indItem,self.TABpar.ind)
                                f3.add_done_callback(f3callback)
                            else:
                                fun2(TABpar_prev)
                                self.setTABpar_final(self.TABpar.indTree,self.TABpar.indItem,self.TABpar.ind)
                    except Exception as inst:
                        pri.Error.red(f"{'!'*100}\naddParWrapper Error in AddPar block::\n{traceback.format_exc()}\n\n{inst}\n{'!'*100}")
            return 
        return callbackfun

    @Slot(int,int,int)
    def setTABpar_final(self,indTree,indItem,ind):
        pri.Callback.magenta(f'{"#"*60}  async callback in {self.TABname} [{indTree}][{indItem}][{ind}]     --- end')
        if self.TABpar.indTree==indTree and self.TABpar.indItem==indItem and self.TABpar.ind==ind:
            self.setTABpar_prev(indTree,indItem,ind,True) #True=with bridge
        self.FlagAsyncCall[indTree][indItem][ind]=False
        self.fUpdatingTabs(False)
        
    def display_controls(self):
        if not self.FlagDisplayControls: return
        lprev=len(self.TABpar_prev[self.TABpar.indTree][self.TABpar.indItem])
        ind=self.TABpar.ind
        if lprev>1:
            self.ui.button_forward.show()
            self.ui.button_back.show()
        else:
            self.ui.button_forward.hide()
            self.ui.button_back.hide()
        if ind==lprev-1 or ind==-1:
            self.ui.button_forward.setEnabled(False)
        else:
            self.ui.button_forward.setEnabled(True)
        if ind==0:
            self.ui.button_back.setEnabled(False)
        else:
            self.ui.button_back.setEnabled(True)
        if ind==lprev-1 or ind==-1:
            self.ui.label_number.setText('')
        elif ind>=0:
            self.ui.label_number.setText("(-"+str(lprev-1-ind)+")")
        else:
            self.ui.label_number.setText("(-"+str(ind+1)+")")

    def add_TABpar(self,tip):
        if self.FlagAddPrev:
            indTree,indItem=self.getTABpar_prev()
        else:
            indTree=self.TABpar.indTree
            indItem=self.TABpar.indItem
        TABpar_prev=self.TABpar_prev[indTree][indItem]
        if not len(TABpar_prev):
            flagNewPar=True
        else:
            flagNewPar=self.TABpar.isDifferentFrom(TABpar_prev[-1],self.TABpar.unchecked_fields+['ind','indItem','indTree']) #* see below
        if flagNewPar:
            if self.FlagAddPrev: #something changed
                self.add_TABpar_copy(tip,indTree,indItem)
                self.add_TABpar_bridge(tip,indTree,indItem,-1)  #should create a copy of the other tabs' parameters (see gPaIRS)
            else:
                TABpar_prev[self.TABpar.ind].copyfrom(self.TABpar) #* see above flagNewPar: if there are changes in unchecked_fields this par is updated in any case
        else:
            self.TABpar.copyfrom(TABpar_prev[-1])

    def getTABpar_prev(self):
        if self.FlagGlob:
            indTree=self.indTreeGlob
            indItem=self.indItemGlob
        else:
            indTree=self.TABpar.indTree
            indItem=self.TABpar.indItem
        #nItem=len(self.TABpar_prev[indTree])
        #if nItem-1<indItem:
        #    nadd=(nItem-indItem+1)
        #    self.TABpar_prev[indTree]+=[[]]*nadd
        #    self.FlagAddingPar[indTree]+=[[]]*nadd
        #    self.FlagAsyncCall[indTree]+=[[]]*nadd
        return indTree,indItem

    def add_TABpar_copy(self,name,*args):
        if len(args)>1: 
            indTree=args[0]
            indItem=args[1]
        else:
            indTree,indItem=self.getTABpar_prev()
        TABpar_prev=self.TABpar_prev[indTree][indItem]
        TABpar_new=self.TABpar.duplicate()
        TABpar_prev.append(TABpar_new)
        self.FlagAddingPar[indTree][indItem].append(False)
        self.FlagAsyncCall[indTree][indItem].append(False)
        if len(TABpar_prev)>self.Num_Prevs_Max:
            TABpar_prev.pop(0)
            self.FlagAddingPar[indTree][indItem].pop(0)
            self.FlagAsyncCall[indTree][indItem].pop(0)
            for k,p in enumerate(TABpar_prev):
                p.ind=k
        else:
            TABpar_new.ind=len(TABpar_prev)-1
        TABpar_new.indItem=indItem
        TABpar_new.indTree=indTree
        TABpar_new.tip=name
        self.TABpar.ind=ind=len(TABpar_prev)-1  #in this way, we move to the last added par in the "prev"
        self.TABpar.indItem=indItem
        self.TABpar.indTree=indTree

        pri.Callback.yellow(f'   |-> +++ {self.TABpar.name}: new par [{indTree}][{indItem}][{ind}] <{name}>')

    def defineSetTABpar(self,setParFun):
        def setTABpar(FlagBridge):
            pri.Callback.magenta(f'    --- setting {self.TABpar.name} [{self.TABpar.indTree}][{self.TABpar.indItem}][{self.TABpar.ind}]')
            #pri.Time.blue(0,'')
            fAddingPar=self.FlagAddingPar[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind]
            self.FlagAddingPar[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind]=True
            try:
                setParFun()
                self.TABpar_prev[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind].copyfrom(self.TABpar) #updating in case TABpar is changed in setParFun (not a good practice, actually)
                self.TABpar_old.copyfrom(self.TABpar) #for async callback and other checks
                if FlagBridge:
                    self.set_TABpar_bridge()
            except:
                pri.Error.red(f'        |-> Error in setting the parameters')
                printException()
            finally:
                self.FlagAddingPar[self.TABpar.indTree][self.TABpar.indItem][self.TABpar.ind]=fAddingPar
                self.display_controls()
            #pri.Time.blue(0,'')
        def setTABpar_prev(indTree,indItem,ind,FlagBridge):
            pri.Callback.magenta(f'    --- setting {self.TABpar.name}_prev[{indTree}][{indItem}][{ind}]')
            #pri.Time.blue(0,'')
            fAddingPar=self.FlagAddingPar[indTree][indItem][ind]
            self.FlagAddingPar[indTree][indItem][ind]=True
            try:
                self.TABpar.copyfrom(self.TABpar_prev[indTree][indItem][ind]) 
                setParFun()
                self.TABpar_prev[indTree][indItem][ind].copyfrom(self.TABpar)  #updating in case TABpar is changed in setParFun (not a good practice, actually)
                self.TABpar_old.copyfrom(self.TABpar)        #for async callback and other checks
                if FlagBridge:
                    self.set_TABpar_prev_bridge(indTree,indItem,ind)
            except:
                pri.Error.red(f'        |-> Error in setting the parameters')
                printException()
            finally:
                try:
                    self.FlagAddingPar[indTree][indItem][ind]=fAddingPar
                except:
                    iterateList(self.FlagAddingPar,False)
                    pri.Error.red(f'{"*"*50}\rError in setting self.FlagAddingPar: restored!\r{"*"*50}')
                self.display_controls()
            #pri.Time.blue(0,'')
        self.setTABpar=setTABpar
        self.setTABpar_prev=setTABpar_prev

    def defineTABbridge(self,bridgeFun,bridgeFun_prev):
        def TABbridge():
            pri.Callback.green(f'::: bridge of {self.TABpar.name} [{self.TABpar.indTree}][{self.TABpar.indItem}][{self.TABpar.ind}]')
            bridgeFun()
        def TABbridge_prev(indTree,indItem,ind):
            pri.Callback.green(f'::: bridge of {self.TABpar.name}_prev[{indTree}][{indItem}][{ind}]')
            bridgeFun_prev(indTree,indItem,ind)
        self.set_TABpar_bridge=TABbridge
        self.set_TABpar_prev_bridge=TABbridge_prev

    def button_back_callback(self):
        ind=self.TABpar.ind-1
        self.setTABpar_prev(self.TABpar.indTree,self.TABpar.indItem,ind,True) #True=with bridge
        self.setFocus()

    def button_forward_callback(self):
        ind=self.TABpar.ind+1
        self.setTABpar_prev(self.TABpar.indTree,self.TABpar.indItem,ind,True) #True=with bridge
        self.setFocus()

    def bfContextMenu(self,bf,event):
        ind=self.TABpar.ind
        TABpar_prev=self.TABpar_prev[self.TABpar.indTree][self.TABpar.indItem]

        if bf==-1:
            b=self.ui.button_back
            f=self.button_back_callback
            kin=max([0,ind-Num_Prevs_back_forw])
            krange=[k for k in range(ind-1,kin,-1)]+[0]
            icon=self.undo_icon
            d=1
        elif bf==1:
            b=self.ui.button_forward
            f=self.button_forward_callback
            kfin=min([len(TABpar_prev)-1,ind+Num_Prevs_back_forw])
            krange=[k for k in range(ind+1,kfin)]+[len(TABpar_prev)-1]
            icon=self.redo_icon
            d=0

        menu=QMenu(b)
        act=[]
        nur=len(krange)
        flag=nur==Num_Prevs_back_forw
        for j,k in enumerate(krange):
            if j==nur-1: 
                if flag: menu.addSeparator()
                if k==0: s=' (first)'
                else: s=' (current)'
            else:
                if j==nur-2 and flag:
                    s=' (...)'
                else:
                    s=''
            n=f"{k-ind:+d}: "
            name=n+TABpar_prev[k+d].tip+s
            act.append(QAction(icon,name,b))
            menu.addAction(act[-1])  

        action = menu.exec_(b.mapToGlobal(event.pos()))
        for k,a in zip(krange,act):
            if a==action: 
                self.TABpar.ind=k-bf
                f()

    def cleanPrevs(self,indTree,indItem):
        TABpar_prev=self.TABpar_prev[indTree][indItem]
        for _ in range(len(TABpar_prev)-1):
            TABpar_prev.pop(0)
        TABpar_prev[0].ind=0
        if self.TABpar.indTree==indTree and self.TABpar.indItem==indItem:
            self.TABpar.ind=0

#*************************************************** Spin boxes
    def spinFocusIn(self,sp):
        sp.valIn=sp.value()
        sp.FlagIn=True

    def spinWrapper(self,sp,fcallback):
        def newfcallback():
            fcallback()
            if sp.FlagIn:
                if sp.value()!=sp.valIn:
                    sp.FlagIn=False
                    flagAddPar=+1
                else:
                    flagAddPar=0
            else: flagAddPar=-1
            return [flagAddPar,None]
        return newfcallback
    
    def setSpinCallbacks(self,SpinNames,*args):
        if len(args): Tips=args[0]
        else: Tips=SpinNames
        def spinCallback(sname,tip):
            sp=getattr(self.ui,"spin_"+sname)
            sp.FlagIn=False
            sp.valIn=sp.value()
            fcallback=getattr(self,"spin_"+sname+"_callback")
            #sp.valueChanged.connect(self.addParWrapper(self.spinWrapper(sp,fcallback),sname))
            sp.valueChanged.connect(fcallback)
            sp.addfuncin['initCallback']=lambda spin=sp: self.spinFocusIn(spin)
            def fout():
                if sp.value()!=sp.valIn:
                    return [1,None]
                else:
                    return [-1,None] 
            sp.addfuncout['callback']=self.addParWrapper(fout,tip)
            sp.addfuncreturn['callback']=self.addParWrapper(None,tip)
        for sname,tip in zip(SpinNames,Tips):
            spinCallback(sname,tip)
            

#*************************************************** Special spin boxes (x,y,w,h)
    def setSpinxywhCallbacks(self):
        self.spin_x_callback=lambda: spin_x_callback(self)
        self.spin_y_callback=lambda: spin_y_callback(self)
        self.spin_w_callback=lambda: spin_w_callback(self)
        self.spin_h_callback=lambda: spin_h_callback(self)
        self.button_resize_callback=lambda: button_resize_callback(self)
        self.setSpinCallbacks(['x','y','w','h'],
            ['First column of image area to process','First row of image','Width of image area to process','Height of image area to process'])
        self.ui.button_resize.clicked.connect(self.addParWrapper(self.button_resize_callback,'resize button'))

    def setMinMaxSpinxywh(self):
        h=self.TABpar.h
        w=self.TABpar.w
        self.ui.spin_x.setMinimum(0)
        self.ui.spin_x.setMaximum(self.TABpar.W-1)
        self.ui.spin_y.setMinimum(0)
        self.ui.spin_y.setMaximum(self.TABpar.H-1)
        self.ui.spin_w.setMinimum(1)
        self.ui.spin_w.setMaximum(self.TABpar.W)
        self.ui.spin_h.setMinimum(1)
        self.ui.spin_h.setMaximum(self.TABpar.H)
        self.TABpar.h=h
        self.TABpar.w=w
        for sname in ('spin_x','spin_y','spin_w','spin_h'):
            self.newTip(sname)

    def newTip(self,field):
        s: MyQSpin
        if field=='spin_range_from':  #INPpar
            s=self.ui.spin_range_from
            stringa=". Range: "+str(s.minimum())+'-'+str(s.maximum())
            newtip=self.tip_spin_range_from+stringa
        elif field=='spin_range_to':  #INPpar
            s=self.ui.spin_range_to
            stringa=". Max.: "+str(s.maximum())
            newtip=self.tip_spin_range_to+stringa
        elif field in ('spin_x','spin_y','spin_w','spin_h'):  #INPpar and #OUTpar
            s=getattr(self.ui,field)
            tip=getattr(self,"tip_"+field)
            stringa=". Image size: "+str(self.TABpar.W)+"x"+str(self.TABpar.H)
            newtip=tip+stringa
        s.setToolTip(newtip)
        s.setStatusTip(newtip)  

    def setValueSpinxywh(self):
        self.ui.spin_x.setValue(self.TABpar.x)
        self.ui.spin_y.setValue(self.TABpar.y)
        self.ui.spin_w.setValue(self.TABpar.w)
        self.ui.spin_h.setValue(self.TABpar.h)
        self.check_resize()

    def check_resize(self):
        if self.TABpar.W!=self.ui.spin_w.value() or \
            self.TABpar.H!=self.ui.spin_h.value():
            self.ui.button_resize.show()
        else:
            self.ui.button_resize.hide()   

#*************************************************** Image sizes
def spin_x_callback(self):
    self.TABpar.x=self.ui.spin_x.value()
    if self.ui.spin_x.hasFocus():
        dx=self.TABpar.W-self.TABpar.x
        self.ui.spin_w.setMaximum(dx)
        if self.ui.spin_x.Win<dx:
            dx=self.ui.spin_x.Win
        self.TABpar.w=dx
        self.ui.spin_w.setValue(dx)
        
def spin_y_callback(self):
    self.TABpar.y=self.ui.spin_y.value()
    if self.ui.spin_y.hasFocus():
        dy=self.ui.spin_y.Win-self.TABpar.y
        self.ui.spin_h.setMaximum(dy)
        if self.ui.spin_y.Win<dy:
            dy=self.ui.spin_y.Win
        self.TABpar.h=dy    
        self.ui.spin_h.setValue(dy)
        
def spin_w_callback(self):
    self.TABpar.w=self.ui.spin_w.value()

def spin_h_callback(self):
    self.TABpar.h=self.ui.spin_h.value()

def button_resize_callback(self):
        self.ui.spin_x.setValue(0)
        self.ui.spin_y.setValue(0)
        self.ui.spin_w.setMaximum(self.TABpar.W)
        self.ui.spin_w.setValue(self.TABpar.W)
        self.ui.spin_h.setMaximum(self.TABpar.H)
        self.ui.spin_h.setValue(self.TABpar.H)
        self.check_resize()
        return [1, None]

def setupWid(self:QWidget):
    setFontPixelSize(self,fontPixelSize)
    
    c=self.findChildren(QObject)
    for w in c:
        w:QToolButton
        if hasattr(w,'toolTip'):
            tooltip=toPlainText(w.toolTip())
            if hasattr(w,'shortcut'):
                scut=w.shortcut().toString(QKeySequence.NativeText)
                if scut:
                    scut=toPlainText('('+scut+')')
                    if scut not in tooltip:
                        tooltip+=' '+scut
                        w.setToolTip(tooltip)
            if hasattr(w,'statusTip'):
                w.setStatusTip(tooltip)
                    
    self.ui.labels=self.findChildren(QLabel)
    #for child in self.ui.labels:
    #    child:QLabel
    #    child.setToolTip(child.text())
    #    child.setStatusTip(child.text())
    self.ui.edits=self.findChildren(MyQLineEdit)+self.findChildren(MyQLineEditNumber)
    for child in self.ui.edits:
        child.setup()
    for child in self.ui.edits:
        child.setup2()
    self.ui.spins=self.findChildren(MyQSpin)
    for child in self.ui.spins:
        child.setup()
    self.ui.dspins=self.findChildren(MyQDoubleSpin)
    for child in self.ui.dspins:
        child.setup()
    self.ui.CollapBoxes=self.findChildren(CollapsibleBox)
    for child in self.ui.CollapBoxes:
        child.setup()

    for sname in ('range_from','range_to','x','y','w','h'):
        if hasattr(self.ui,"spin_"+sname):
            sp=getattr(self.ui,"spin_"+sname)
            setattr(self,"tip_spin_"+sname,sp.toolTip())

def setFontPixelSize(self,fPixSize):
    font=self.font()
    font.setFamily(fontName)
    font.setPixelSize(fPixSize)
    self.setFont(font)
    c=self.findChildren(QObject)
    for w in c:
        w:QWidget
        if hasattr(w,'setFont'):
            font=w.font()
            font.setFamily(fontName)
            t=type(w)
            if issubclass(t,QLabel):
                setFontSizeText(w,[fPixSize-1])
            elif issubclass(t,QPushButton) or issubclass(t,QToolButton):
                font.setPixelSize(fPixSize+1)
                w.setFont(font)
                adjustFont(w)
            else:
                font.setPixelSize(fPixSize)
                w.setFont(font)
                adjustFont(w)

def setFontSizeText(lab:QLabel,fPixSizes):
    text=lab.text()
    text=re.sub("font-size:\d+pt",f"font-size:{fPixSizes[0]}px",text)   
    text=re.sub("font-size:\d+px",f"font-size:{fPixSizes[0]}px",text)  
    if len(fPixSizes)>1:
        for k in range(len(fPixSizes)-1,0,-1):
            text=re.sub("font-size:\d+px",f"font-size:{fPixSizes[k]}px",text,k)
    lab.setText(text)
    font=lab.font()
    font.setPixelSize(fPixSizes[0])
    lab.setFont(font)
    adjustFont(lab)

def adjustFont(self:QLabel):
    if not hasattr(self,'geometry'): return
    if not hasattr(self,'text') and not hasattr(self,'currentText'): return 
    flagParent=self.isVisible() and bool(self.parent())
    font = self.font()
    if hasattr(self,'text'):
        text = self.text()
    elif hasattr(self,'currentText'):
        text = self.currentText()
    else: return
    if 'Parallel' in text:
        pass

    if hasattr(self,'text'):
        if 'Find' in self.text():
            pass
    
    S=self.geometry()
    maxS = QRect(self.pos(),self.maximumSize())
    minS = QRect(self.pos(),self.minimumSize())
    if flagParent:
        r=self.parent().rect()
        S&= r
        maxS&= QRect(QPoint(r.x(),r.y()),self.parent().maximumSize())
        minS&= QRect(QPoint(r.x(),r.y()),self.parent().minimumSize()) 
    
    textSize=QtGui.QFontMetrics(font).size(QtCore.Qt.TextSingleLine, text)
    if (textSize.height()<=S.height()) and (textSize.width()<=S.width()):
        return
    while True:
        if font.pixelSize()<=fontPixelSize_lim[0]:
            font.setPixelSize(fontPixelSize_lim[0])
            break
        if (textSize.height()<=S.height()):
            break
        font.setPixelSize(font.pixelSize()-1)
        textSize=QtGui.QFontMetrics(font).size(QtCore.Qt.TextSingleLine, text)

    textWidth=min([textSize.width(),maxS.width()])
    textWidth=max([textWidth,minS.width()])
    if S.width()<textWidth:
        s=self.geometry()
        s.setWidth(textWidth)
        self.setGeometry(s)
        if flagParent:
            S=s&self.parent().rect()
        else:
            S=s
    while True:
        if font.pixelSize()<=fontPixelSize_lim[0]:
            font.setPixelSize(fontPixelSize_lim[0])
            break
        if (textSize.width()<=S.width()):
            break
        font.setPixelSize(font.pixelSize()-1)
        textSize=QtGui.QFontMetrics(font).size(QtCore.Qt.TextSingleLine, text)
    
    self.setFont(font)

#*************************************************** Other
def iterateList(l,value):
        if type(l)==list:
            if len(l):
                if type(l[0])==list:
                    for m in l:
                        iterateList(m,value)
                else:
                    for k in range(len(l)):
                        l[k]=value

#*************************************************** TREE icons
class TREico:
    def __init__(self):
        self.none = QIcon()

        self.completed = QIcon()  
        self.completed.addFile(""+ icons_path +"completed.png", QSize(), QIcon.Normal, QIcon.Off)

        self.done = QIcon()       
        self.done.addFile(""+ icons_path +"done.png", QSize(), QIcon.Normal, QIcon.Off)
    
        self.cancelled = QIcon()  
        self.cancelled.addFile(""+ icons_path +"cancelled.png", QSize(), QIcon.Normal, QIcon.Off)

        self.trash = QIcon()      
        self.trash.addFile(""+ icons_path +"trash.png", QSize(), QIcon.Normal, QIcon.Off)

        self.running = QIcon()
        self.running.addFile(""+ icons_path +"processing.png", QSize(), QIcon.Normal, QIcon.Off)

        self.waiting = QIcon()
        self.waiting.addFile(""+ icons_path +"waiting_circle.png", QSize(), QIcon.Normal, QIcon.Off)

        self.issue = QIcon()
        self.issue.addFile(""+ icons_path +"issue.png", QSize(), QIcon.Normal, QIcon.Off)
    
        self.missing = QIcon()
        self.missing.addFile(""+ icons_path +"missing.png", QSize(), QIcon.Normal, QIcon.Off)

        self.editing = QIcon()
        self.editing.addFile(""+ icons_path +"editing.png", QSize(), QIcon.Normal, QIcon.Off)

        self.paused = QIcon()
        self.paused.addFile(""+ icons_path +"paused.png", QSize(), QIcon.Normal, QIcon.Off)

        self.icon_names=[f for f,_ in self.__dict__.items()]

    def icontype(self,type_name):
        type=self.icon_names.index(type_name)
        return type
    
    def icon(self,icon_type):
        if type(icon_type)==int:
            type_name=self.icon_names[icon_type]
        else:
            type_name=icon_type
        icon=getattr(self,type_name)
        return icon

def funexample():
    def fun2(i):
        if FlagSimulateError:
            raise Exception("funexample: the requested exception!") 
        pri.Info.cyan('funexample: Hello, sir!')
    return [1,fun2]

if __name__ == "__main__":
    a=TABpar()
    b=TABpar()

    a.printPar('a: ')
    c=a.duplicate()
    b.printPar('b: ')

    a.copyfrom(b)
    a.printPar('a: ','   copied from b')
    c.printPar('c: ')
    c.copyfromdiz(b,['surname'])
    c.printPar('c: ', '   surname copied from b')

    print(f'Is a different from b? {a.isDifferentFrom(b,())}')
    print(f'Is a equal to b? {a.isEqualTo(b,())}')
    print(f'Is c different from b? {c.isDifferentFrom(b,())}')
    print(f'Is c equal to b? {c.isEqualTo(b,())}')
    print(f'Is c different from b except surname? {c.isDifferentFrom(b,("surname"))}')
    print(f'Is c equal to b except name? {c.isEqualTo(b,("name"))}')

    """
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    TAB = gPaIRS_Tab(None,QWidget)
    callbackfun=TAB.addParWrapper(funexample,'example')
    callbackfun()
    app.exec()
    app.quit()
    app=None
    """