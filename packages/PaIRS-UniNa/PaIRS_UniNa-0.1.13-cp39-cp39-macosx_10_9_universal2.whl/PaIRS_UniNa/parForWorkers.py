'''
 parForWorker worker used for parfor
 '''

from typing import Callable
from .PaIRS_pypacks import *


# To me, pylint is correct in flagging this error here the top level module is database (it contains an __init__.py file)
# Your import should look like (fully absolute) 
# https://stackoverflow.com/a/51236340
#from PIV_ParFor import callBack, FlagStopWorkers

from .preProcParFor import *
from .pivParFor import *

prTime = PrintTA(PrintTA.yellow, PrintTA.faceStd,  PrintTAPriority.medium).prTime

class WorkerSignals(QObject):
    progress = Signal(int,int,int,list,str)
    result = Signal(int,int,list,str)
    finished = Signal(object,str)
    initialized = Signal()
    completed = Signal()
    kill = Signal(int)

class ParForWorker(QRunnable):
    def __init__(self,data:dataTreePar,indWorker:int,indProc:int,numUsedThreadsPIV:int,pfPool:ParForPool,parForMul:ParForMul,nameWorker:str,mainFun:Callable):
        #super(MIN_ParFor_Worker,self).__init__(data,indWorker,indProc,pfPool=ParForPool,parForMul=ParForMul)
        super().__init__()
        self.pfPool=pfPool
        self.parForMul=parForMul
        self.nameWorker=nameWorker # diverso per le due classi
        self.data=data.duplicate() #OPTIMIZE TA GP controllare se le modifiche fatte nel workers interferiscono con quelle fatte in progress_proc ed eventualmente evitare l'aggiornamento in resetProc e in store_proc
        self.indWorker = indWorker
        self.indProc = indProc
        self.numUsedThreadsPIV=numUsedThreadsPIV
        self.signals=WorkerSignals()
        self.isKilled = False
        self.isStoreCompleted = False
        self.numCallBackTotOk=0
        
        self.mainFun=mainFun

    @Slot()
    def run(self):
        if Flag_DEBUG_PARPOOL: debugpy.debug_this_thread()
        try:
            #pr(f'ParForWorker.run self.isKilled={self.isKilled}  self.indWorker={self.indWorker}  self.indProc={self.indProc}  ')
            self.parForMul.numUsedCores=self.numUsedThreadsPIV
            while self.indWorker!=self.indProc:# and not self.isKilled:
                timesleep(SleepTime_Workers) 
                if self.isKilled: 
                   self.signals.completed.emit()
                   return # in this case we are killing all the threads
            pri.Process.blue(f'ParForWorker.run starting {self.nameWorker} self.isKilled={self.isKilled}  self.indWorker={self.indWorker}  self.indProc={self.indProc}  ')
            self.mainFun()
        except:
            Message=printException('ParForWorker',flagMessage=True)
            self.signals.finished.emit(self.data,Message)
        #finally:#also after return eliminated
        pri.Process.blue(f'End of ParForWorker {self.nameWorker} ({self.indWorker}, {self.numCallBackTotOk} )')
        while not self.isStoreCompleted:
           timesleep(SleepTime_Workers) 
        self.signals.completed.emit()
        
        
        
                    
    @Slot()
    def killOrReset(self,isKilled):
        #pr('\n***********************\n*************************    ParForWorker.die {isKilled}')
        global FlagStopWorkers
        self.isKilled=isKilled
        FlagStopWorkers[0]=1 if isKilled else 0
        
    @Slot(int)
    def updateIndProc(self,indProc):
        #pr(f'updateIndProc {self.nameWorker} ({self.indWorker})')          
        self.indProc=indProc
        
    @Slot(int)
    def setNumCallBackTot(self,numCallBackTotOk):
        #if (self.numCallBackTotnumCallBackTotOk>numCallBackTotOk):         prLock(f'setNumCallBackTot numCallBackTotOk={numCallBackTotOk}')
        self.numCallBackTotOk=numCallBackTotOk

    @Slot()
    def storeCompleted(self):
       self.isStoreCompleted=True

class MIN_ParFor_Worker(ParForWorker):
  def __init__(self,data:dataTreePar,indWorker:int,indProc:int,numUsedThreadsPIV:int,pfPool:ParForPool,parForMul:ParForMul):
    super().__init__(data,indWorker,indProc,numUsedThreadsPIV,pfPool,parForMul,nameWorker='calcMin_Worker',mainFun=self.calcmin)

  def calcmin(self):
        stringaErr=''
        global FlagStopWorkers
        pri.Time.blue(0,'calcmin')
        FlagStopWorkers[0]=0
        
        #pp=ParForMul()
        #pp.sleepTime=ParFor_sleepTime #time between calls of callBack
        #pp.numCoresParPool=numUsedThreadsPIV
        
        self.data.compMin.restoreMin()
        args=(self.data,self.numUsedThreadsPIV)
        kwargs={} 
        numCallBackTotOk=self.data.numFinalized  #su quelli non finalized ci ripassiamo quindi inizialmente il num di callback ok = num di finalized

        nImg=range(self.data.nimg)
        #nImg=range(2*self.data.nimg)
        
        myCallBack=lambda a,b,c,d,e,f: callBackMin(a,b,c,d,e,f,self.signals.progress)
        #for ii,f in enumerate(self.data.list_pim):          pr(f'{ii}-{hex(f)}  ',end='')
        pri.Process.blue(f'Init calcmin Contab={self.data.compMin.contab}   numCallBackTotOk={numCallBackTotOk}  numUsedThreadsPIV={self.numUsedThreadsPIV}')
        self.signals.initialized.emit()
        #TBD TA all the exceptions should be managed inside parForExtPool therefore the try should be useless just in case I check
        try:
          (mi,flagOut,VarOut,flagError)=self.parForMul.parForExtPool(self.pfPool.parPool,procMIN,nImg,initTask=initMIN,finalTask=finalMIN, wrapUp=saveAndMin, callBack=myCallBack,*args,**kwargs)
        except Exception as e:  
          PrintTA().printEvidenced('Calcmin exception raised.\nThis should never happen.')
          raise (e)
        if flagError: 
          self.signals.finished.emit(self.data,printException('calcmin',flagMessage=True,exception=self.parForMul.exception))
          return
          
        pri.Time.blue(0,'dopo  parForExtPool ****************************************')
        '''
        def callBackSaveMin(f3):
          pri.Time.blue(0,'callBackSaveMin')
          #(pfPool,parForMul)=f3.result()
        async def callSaveMin(data:dataTreePar,Imin=list): 
           #t1=asyncio.create_task(saveMin(self.data,mi.Imin)) 
           #await t1
           saveMin(self.data,mi.Imin) #nel caso controllare errore come sotto
        '''
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        if mi.contab[0]!=0:
          mi.calcMed()
          #OPTIMIZE TAGP sul mio pc (TA) saveMin è lenta (5 secondi) forse si può organizzare con una funzione async tanto non ci interessa quando finisce
          #f3=executor.submit(asyncio.run,callSaveMin(self.data,mi.Imin))
          #f3.add_done_callback(callBackSaveMin)
          try:
            saveMin(self.data,mi.Imin) 
          except:
             stringaErr+=printException('calcmin',flagMessage=True)+'\n'
        pri.Time.blue(0,'dopo  saveMin ****************************************')
        #for ii,f in enumerate(flagOut):          pr(f'{ii}-{hex(f)}  ',end='')
        numCallBackTotOk+=sum(1 if x&FLAG_CALLBACK_INTERNAL else 0 for x in flagOut)     

        #initTime=time()
        self.data.flagParForCompleted=True
        while self.numCallBackTotOk!=numCallBackTotOk:
            pri.Process.blue (f'Error Calcmin self.numCallBackTotOk={self.numCallBackTotOk} numCallBackTotOk={numCallBackTotOk} ')
            timesleep(SleepTime_Workers)
        
        #numProcOrErrTot=sum(1 if (f&FLAG_FINALIZED_OR_ERR[0])and (f&FLAG_FINALIZED_OR_ERR[1]) else 0 for f  in flagOut)   
        numProcOrErrTot=sum(1 if f else 0 for f  in flagOut)   
        pri.Process.blue (f'Fine calcmin **************  numCallBackTotOk={numCallBackTotOk}  numProcOrErrTot={numProcOrErrTot} numFinalized={self.data.numFinalized}')
        pri.Time.blue(0,'fine calcmin ****************************************')
        

        if mi.contab[0]!=0:
          pri.Time.blue(0,f'Min value coord(20,20) Min=[{mi.Imin[0][20][20]},{mi.Imin[1][20][20]}]  med=[{mi.med[0][20][20]},{mi.med[1][20][20]}]')
          pri.Time.blue(0,f'Min value coord(52,52) Min=[{mi.Imin[0][52][52]} {mi.Imin[1][52][52]}]  med=[{mi.med[0][52][52]} {mi.med[1][52][52]}]')
                # In pause_MINproc oltre a salvare il minimo si verifica se tutte le img programmate sono state processate anche con esito negativo, nel caso si passa al task successivo
        
        self.data.compMin=mi
        self.data.FlagFinished=self.data.nimg==numProcOrErrTot
        self.signals.finished.emit(self.data,stringaErr)

class PIV_ParFor_Worker(ParForWorker):
  def __init__(self,data:dataTreePar,indWorker:int,indProc:int,numUsedThreadsPIV:int,pfPool:ParForPool,parForMul:ParForMul):
    super().__init__(data,indWorker,indProc,numUsedThreadsPIV,pfPool,parForMul,nameWorker='PIV_Worker',mainFun=self.runPIVParFor)
  
  def runPIVParFor(self):
        stringaErr=''
        global FlagStopWorkers
        pri.Time.cyan(3,'runPIVParFor')
        FlagStopWorkers[0]=0
        # TODEL
        
        flagDebugMem=False
        if flagDebugMem:# TODEL?
          m1=memoryUsagePsutil() 
        filename_preproc=self.data.filename_proc[dataTreePar.typeMIN]

        self.data.mediaPIV.restoreSum()
        
        #args=(self.data,)
        args=(self.data,self.numUsedThreadsPIV)
        kwargs={'finalPIVPIppo': self.data.nimg}#unused just for example
        kwargs={}
        numCallBackTotOk=self.data.numFinalized  #su quelli non finalized ci ripassiamo quindi inizialmente il num di callback ok = num di finalized


        nImg=range(self.data.nimg)
        myCallBack=lambda a,b,c,d,e,f: callBackPIV(a,b,c,d,e,f,self.signals.progress)
        pri.Process.blue(f'runPIVParFor   mediaPIV cont={self.data.mediaPIV.cont}  self.numCallBackTotOk={self.numCallBackTotOk}   self.data.nimg={self.data.nimg}')

        self.signals.initialized.emit()
        #TBD TA all the exceptions should be managed inside parForExtPool therefore the try should be useless just in case I check
        try:
          (me,flagOut,VarOut,flagError)=self.parForMul.parForExtPool(self.pfPool.parPool,procPIV,nImg,initTask=initPIV,finalTask=finalPIV, wrapUp=saveAndMean, callBack=myCallBack,*args,**kwargs)
        except Exception as e:
          PrintTA().printEvidenced('Calcmin exception raised\nThis should never happen ')
          raise (e)
        if flagError: 
          self.signals.finished.emit(self.data,printException('calcmin',flagMessage=True,exception=self.parForMul.exception))
          return
        
        try:
          if me.cont:
            me:mediaPIV
            me.calcMedia()
            nameFields=me.namesPIV.avgVelFields
            Var=[getattr(me,f) for f in nameFields ]#me.x,me.y,me.u,me.v,me.up,me.vp,me.uvp,me.sn,me.Info]
            nameVar=me.namesPIV.avgVel  
            saveResults(self.data,-1,Var,nameVar)
        except:
           stringaErr+=printException('calcmin',flagMessage=True,exception=self.parForMul.exception)+'\n'
        numCallBackTotOk+=sum(1 if x&FLAG_CALLBACK_INTERNAL else 0 for x in flagOut)            
        
        # Tbd 
        '''
        if flagDebugMem:
          pri.Time.cyan(0,'Save results')
          pr(f"Number of garbage element not collected before {gc.get_count()}",end='')   
          gc.collect()
          pr(f" after {gc.get_count()}")
          pr(f"********************** End Fun Main -> {(memoryUsagePsutil()-m1)/ float(2 ** 20)}MByte")
          pr(*gc.garbage)
        '''
        
        
        
        #initTime=time()
        self.data.flagParForCompleted=True
        while self.numCallBackTotOk!=numCallBackTotOk :
            pri.Process.blue (f'Error runPIVParFor self.numCallBackTotOk={self.numCallBackTotOk} numCallBackTotOk={numCallBackTotOk}    numUsedThreadsPIV={self.numUsedThreadsPIV}')
            timesleep(SleepTime_Workers)
               
        if me.cont:
          pri.Time.cyan(f'u={me.u[5][4]} v={me.v[5][4]}  up={me.up[5][4]} vp={me.vp[5][4]} uvp={me.uvp[5][4]} sn={me.sn[5][4]} Info={me.Info[5][4]}')
    
        #self.numFinalized=sum(1 if f&FLAG_FINALIZED[0]  else 0 for f  in flagOut)   
        numProcOrErrTot=sum(1 if f else 0 for f  in flagOut)   

        #for ii,f in enumerate(flagOut):          pr(f'{ii}-{hex(f)}  ',end='')
        pri.Process.blue (f'Fine runPIVParFor **************  numCallBackTotOk={numCallBackTotOk}  numProcOrErrTot={numProcOrErrTot} numFinalized={self.data.numFinalized}')
        
        self.data.mediaPIV=me
        self.data.FlagFinished=self.data.nimg==numProcOrErrTot
        self.signals.finished.emit(self.data,stringaErr)  
