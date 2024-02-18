''' 2d PIV helper function for parfor   '''
from  datetime import timedelta

# In hex is easy 0606 both read and processed 01234156789abcdef 
FLAG_READ_ERR = [1, 1<<8] #2, 256=                    0001    1   0001 0000 0000
FLAG_READ = [2 ,1<<9] #1<<9=2**9=512                  0010    2
FLAG_PROC = [1<<2 ,1<<10] #8 ,1024                    0100    4
FLAG_FINALIZED = [1<<3  ,1<<11] #completely processed 1000    8
# In hex is easy 0E0E both read, processed and finalized
FLAG_CALLBACK_INTERNAL = 1<<16 #on if the callback has been called in its internal parts   
FLAG_GENERIC_ERROR = 1<<17 #on if the callback has been called in its internal parts   
FLAG_PROC_AB =FLAG_PROC[0]|FLAG_PROC[1]  #4+1024=1028=x404 se si somma anche FLAG_READ  6+1536=1542=x606
FLAG_FINALIZED_AB =FLAG_FINALIZED[0]|FLAG_FINALIZED[1]  
FLAG_PROC_OR_ERR=[ p|e for (p,e) in zip(FLAG_PROC,FLAG_READ_ERR)]
FLAG_FINALIZED_OR_ERR = [ p|e for (p,e) in zip(FLAG_FINALIZED,FLAG_READ_ERR)]
# usare con 
# supponendo che k sia 0 (img a) o 1 (img b) 
# if pim(i)&FLAG_PROC[k]: allora img i, k processata
# per annullare un bit f=f& (~FLAG_CALLBACK)

from .PaIRS_pypacks import*
from .Import_Tab import INPpar as INPpar
from .Export_Tab import OUTpar as OUTpar
from .Export_Tab import outType_items
from .Process_Tab import PROpar as PROpar
from .Vis_Tab import VISpar as VISpar
from .Vis_Tab import NamesPIV
from .TabTools import TABpar
from .__init__ import __version__,__subversion__,__year__


class dataTreePar(TABpar):
    nTypeProc=3
    typeNull=0
    typeMIN=1
    typePIV=2

    def __init__(self,*args):
        typeProc=0
        flagRun=0
        if len(args): typeProc=args[0]
        if len(args)>1: flagRun=args[1]
        self.setup(typeProc,flagRun)
        super().__init__()
        self.name='dataTreePar'
        if typeProc==dataTreePar.typeMIN:
            self.name+=':MINproc'
        elif typeProc==dataTreePar.typePIV:
            self.name+=':PIVproc'
        self.surname='itemTreePar.gPaIRS'
        self.unchecked_fields+=['name_fields']

    def setup(self,typeProc,flagRun):
        #typeProc, names, icon, log: item fields
        self.typeProc=typeProc

        self.itemname=''
        self.filename_proc = ['']*dataTreePar.nTypeProc
        self.name_proc = ['']*dataTreePar.nTypeProc
        self.icon_type=0

        self.Log=''
        self.subHeader=''
        self.procLog=['','','']  #LogProc, LogStat, LogErr
        self.warnings=['',''] #warnings once completed the process, warnings related to current state

        self.item_fields=[f for f,_ in self.__dict__.items()]+['indTree','indItem','ind']

        #process
        self.flagRun=flagRun  #0:not launched yet, 1:completed, -1:interrupted
        #min data
        self.inpPath=''
        self.outPathRoot=''
        self.inpExt=''
        self.flag_TR=None
        self.compMin:CompMin=CompMin()
        #piv data
        self.NumThreads=-1
        self.ndig=-1
        self.outExt=''
        self.Imin=[]
        self.mediaPIV:mediaPIV=mediaPIV()
        self.numUsedThreadsPIV=1

        #common
        self.INP=INPpar()
        self.OUT=OUTpar()
        self.PRO=PROpar('fast')
        self.VIS=VISpar()
        self.nimg=0
        self.list_Image_Files=[]
        self.list_eim=[]
        self.list_pim=[]        
        self.list_print=[]

        fields=[f for f,_ in self.__dict__.items()]
        self.numCallBackTotOk=0  #numero di callback ricevute= quelle con problema + finalized
        self.numFinalized=0   #numero di processi andati a buon fine
        self.numProcOrErrTot=0
        self.FlagFinished=False
        self.flagParForCompleted=False  # par for completed                
                

        # processing time
        self.initProcTime=time()  #initial time qhen starting the process
        self.eta=0  # expexted time to finish the process
        self.procTime=0 # processing time 
        self.timePerImage=0
        
        #interface
        self.freset_par=''
        self.procfields=[f for f,_ in self.__dict__.items() if f not in fields]+ ['compMin','mediaPIV']
        self.setCompleteLog()
        return

    def setProc(self):
        self.inpPath=self.INP.path
        self.outPathRoot=myStandardRoot(self.OUT.path+self.OUT.subfold+self.OUT.root)
        self.inpExt=self.INP.pinfo.ext
        ind_in=self.INP.list_ind_items[0]
        ind_fin=self.INP.list_ind_items[1]
        self.list_Image_Files=self.INP.list_Image_Files[ind_in:ind_fin]
        self.list_eim=self.INP.list_eim[ind_in:ind_fin]
        self.flag_TR=self.INP.flag_TR
        self.compMin.flag_TR=self.flag_TR

        if self.typeProc==dataTreePar.typeMIN:
            self.nimg=(len(self.list_Image_Files)//2+1)//2 if self.flag_TR else len(self.list_Image_Files)//2
        elif self.typeProc==dataTreePar.typePIV:
            self.nimg=int(len(self.list_Image_Files)/2)
            self.ndig=self.INP.pinfo.ndig
            self.outExt=list(outType_items)[self.OUT.outType]
            self.numUsedThreadsPIV=self.numUsedThreadsPIV  #TODEL 

        self.list_pim=[0]*self.nimg
        self.VIS.Tre.list_pim=self.list_pim
        self.list_print=['']*self.nimg
    
    def assignDataName(self):
        username=platform.system() +'-'+os.environ.get('USER', os.environ.get('USERNAME'))
        date_time=QDate.currentDate().toString('yyyy/MM/dd')+'-'+\
            QTime().currentTime().toString()
        ppid=str(os.getppid())+'-'+str(os.getpid())
        version_user_info='PaIRS-v'+__version__+'_'+username+'_'+date_time
        id=ppid+'_'+str(uuid.uuid4())
        for t in range(dataTreePar.nTypeProc):
            self.name_proc[t]=version_user_info+'_proc'+str(t)+'_'+id

        if self.typeProc==dataTreePar.typeMIN:
            self.name='itemTREEpar:MinProc'
            self.filename_proc[self.typeProc]=f"{self.outPathRoot}{outExt.min}"
            self.itemname=f"Minimum computation ({self.filename_proc[self.typeProc]})"
        elif self.typeProc==dataTreePar.typePIV:
            self.name='itemTREEpar:PIVProc'
            if self.INP.flag_min: 
                self.filename_proc[dataTreePar.typeMIN]=f"{self.outPathRoot}{outExt.min}"
            else:
                self.filename_proc[dataTreePar.typeMIN]=''
            self.filename_proc[self.typeProc]=f"{self.outPathRoot}{outExt.piv}"
            self.itemname=f"PIV computation ({self.filename_proc[self.typeProc]})"
    
    def resetTimeStat(self):        
        ''' reset all the TimeStat parameters should be called before starting a new process maybe it is useless ask GP'''
        self.procTime=0
        self.eta=0
        self.timePerImage=0

    def onStartTimeStat(self):
        ''' Should be called whenever play is pressed '''
        pri.Time.blue(f'onStartTimeStat self.procTime={self.procTime}')
        self.initProcTime=time()

    def onPauseTimeStat(self):        
        ''' Should be called whenever pause is pressed '''
        actualTime=time()
        self.calcTimeStat(actualTime,self.numFinalized) #if paused should evaluate the correct eta when restarting
        self.procTime+=actualTime-self.initProcTime
        pri.Time.blue(f'onPauseTimeStat self.procTime={self.procTime}  self.eta={self.eta} self.numFinalized={self.numFinalized}')

    def deltaTime2String(self,dt,FlagMilliseconds=False):
       if FlagMilliseconds:
          s=str(timedelta(seconds=int(dt)))
          s+="."+f"{dt:#.3f}".split('.')[-1] #
       else:
          s=str(timedelta(seconds=round(dt)))
       return s
       
    def calcTimeStat(self,actualTime,numDone):
        '''  Should be called when when the eta should be updated '''
        procTime=self.procTime+actualTime-self.initProcTime
        numStilToProc=self.nimg-numDone
        
        if numDone==0:
           self.eta=0
           self.timePerImage=0
        else:
          self.timePerImage=(procTime)/numDone
          self.eta=self.timePerImage*numStilToProc
        
        #pr(f'dt={procTime} ETA={self.eta} {self.deltaTime2String(self.eta)} dt+ETA={round(procTime+ self.eta)} timePerImage={self.timePerImage} numStilToProc={numStilToProc} numDone={numDone} ')
        return self.deltaTime2String(self.eta)

    def setPIV(self):
        self.PIV=data2PIV(self) 

    def createLogHeader(self):
        header=PaIRS_Header
        if self.typeProc==0: #minimum
          name='Welcome to PaIRS!\nEnjoy it!\n\n'
          header=header+name
        else:
          name=f'{self.itemname}\n'
          name+=self.name_proc[self.typeProc]
          date_time=QDate.currentDate().toString('yyyy/MM/dd')+' at '+\
              QTime().currentTime().toString()
          header+=f'{name}\n'+'Last modified date: '+date_time+'\n\n\n'
        return header

    def setCompleteLog(self):
        warn1=self.headerSection('WARNINGS',self.warnings[1],'!')  
        if self.flagRun:
            warn0=''
            self.createLogProc()
            LogProc = self.headerSection('OUTPUT',self.procLog[0])
            LogStat = self.headerSection('PROGRESS status',self.procLog[1]) 
            LogErr = self.headerSection('ERROR report',self.procLog[2])
            procLog=LogProc+LogStat+LogErr 
            if self.warnings[0]: warn0='*Further information:\n'+self.warnings[0]+'\n'        
            self.Log=self.createLogHeader()+procLog+warn0+warn1
        else:
            self.Log=self.createLogHeader()+warn1

    def headerSection(self,nameSection,Log,*args):
        if len(Log):
            c='-'
            n=36
            if len(args): c=args[0]
            if len(args)>1: n=args[1]
            ln=len(nameSection)
            ns=int((n-ln)/2)
            Log=f'{f"{c}"*n}\n{" "*ns}{nameSection}{" "*ns}\n{f"{c}"*n}\n'+Log+'\n'
        return Log
    
    def createLogProc(self):
        splitAs='\n   '#used to join the strings together tab or spaces may be use to indent the error
        numImgTot=len(self.list_pim) if self.typeProc==2 else (2*len(self.list_pim))
        LogProc=''
        LogErr=''
        cont=0
        contErr=0
        for i,p in enumerate(self.list_pim):
            if not p: 
              continue
            if self.typeProc==1: #minimum
                cont+=2
                flag=(p&FLAG_FINALIZED[0]) and (p&FLAG_FINALIZED[1]) 
                if (p&FLAG_FINALIZED[0]):
                    if (p&FLAG_FINALIZED[1]):
                      LogProc+=(self.list_print[i])
                    else:
                      sAppo=self.list_print[i].split('\n')
                      LogProc+=sAppo[0]+'\n'
                      if (not p&FLAG_READ[1]) and p&FLAG_READ_ERR[1]:
                        LogErr+=splitAs.join(sAppo[1:-1])+'\n'
                        contErr+=1
                        #pri.Process.magenta(f'LogProc {i} {p}   {splitAs.join(sAppo[1:-1])} {hex(p)}   ')  
                      else:# la b nonè stata proprio letta
                          cont-=1
                          #pri.Process.magenta(f'LogProc wrong {i} {p}   {splitAs.join(sAppo[1:-1])} {hex(p)}  ')
                else:
                    sAppo=self.list_print[i].split('\n')
                    if (p&FLAG_FINALIZED[1]):
                      LogProc+=(sAppo[-2])+'\n'
                      LogErr+=splitAs.join(sAppo[0:-2])+'\n'
                      contErr+=1
                    else:
                      iDum=len(sAppo)//2
                      LogErr+=splitAs.join(sAppo[0:iDum])+'\n'+splitAs.join(sAppo[iDum:-1])+'\n'
                      contErr+=2
            elif self.typeProc==2: #PIV process
                cont+=1
                if p&FLAG_FINALIZED[0]:
                  LogProc+=self.list_print[i]+"\n"
                  #pr(f'LogProc {i} {p}   {self.list_print[i]} {hex(p)}   =    {hex(FLAG_FINALIZED_AB)}\n')
                else:
                  contErr+=1
                  LogErr+=splitAs.join(self.list_print[i].split('\n')[0:-1])+'\n'

        if not LogProc: LogProc='No output produced!\n\n'
        
        if LogErr:
          LogErr=f'There were {contErr}/{numImgTot} errors in the current process:\n\n'+LogErr
        else:
          LogErr=f'There were {contErr}/{numImgTot} errors in the current process!\n\n'
        pProc=cont*100/numImgTot
        pLeft=100-pProc
        if cont:
          pErr=contErr*100/cont
        else:
          pErr=0
        pCorr=100-pErr
        LogStat=\
              f'Percentage of pairs\n'+\
              f'          processed:   {pProc:.2f}%\n'+\
              f'          remaining:   {pLeft:.2f}%\n'+\
              f'     without errors:   {pCorr:.2f}%\n'+\
              f'        with errors:   {pErr:.2f}%\n\n'+\
              f'Time\n'+\
              f'     of the process:   {self.deltaTime2String(self.procTime,True)}\n'+\
              f'          per image:   {self.deltaTime2String(self.timePerImage,True)}\n'+\
              f'         to the end:   {self.deltaTime2String(self.eta,True)}\n'
        self.procLog=[LogProc,LogStat,LogErr]
        return 

    def resetLog(self):
       self.Log=self.createLogHeader()+self.procLog[0]

    def writeCfgProcPiv(self):
        if self.outPathRoot=='':
          outPathRoot=myStandardRoot(self.OUT.path+self.OUT.subfold+self.OUT.root)
        else:
          outPathRoot=self.outPathRoot
        foldOut=os.path.dirname(outPathRoot)
        if not os.path.exists(foldOut):
           os.mkdir(foldOut)
        writeCfgProcPiv(self,f"{outPathRoot}.cfg")

class mediaPIV():
  ''' helper class to perform the avearages '''
  def __init__(self):
    self.namesPIV=NamesPIV()
    #self.avgVel=[self.x,self.y,self.u,self.v,self.up,self.vp,self.uvp,self.FCl,self.Info,self.sn]
    self.x=np.zeros(1)
    self.y=np.zeros(1)
    self.u=np.zeros(1)
    self.v=np.zeros(1)
    self.up=np.zeros(1)
    self.vp=np.zeros(1)
    self.uvp=np.zeros(1)
    self.sn=np.zeros(1)
    self.FCl=np.zeros(1)
    self.Info=np.zeros(1)
    
    # just for checking that the variables are the same 
    # I cannot do it automatically since variables are not recognized by vscode
    for n in self.namesPIV.avgVelFields:       
       v=getattr(self,n)
    
    self.cont=0
    self.nimg=0

  def sum(self,var):
    # should start with x, y ,u ,v
    infoSi=1
    self.cont=self.cont+1
    for v, n in zip(var[2:], self.namesPIV.instVelFields[2:]) :
      f=getattr(self,n)
      #piv.Info #verificare se sia il caso di sommare solo se =Infosi
      setattr(self,n,f+1*(v==infoSi) if n=='Info' else f+v )
      
    '''
    self.u=self.u+var[2] #piv.u
    self.v=self.v+var[3] #piv.v
    self.FCl=self.FCl+var[4] #piv.FCl
    self.Info=self.Info+1*(var[5]==infoSi)  #piv.Info #verificare se sia il caso di sommare solo se =Infosi
    self.sn=self.sn+var[6] #piv.sn
    '''
    self.up=self.up+var[2]*var[2] #piv.up
    self.vp=self.vp+var[3]*var[3] #piv.up
    self.uvp=self.uvp+var[2]*var[3] #piv.up
    
    if self.x.size<=1:
      self.x=var[0]  #piv.x dovrebbero essere tutti uguali
      self.y=var[1]  #piv.y dovrebbero essere tutti uguali

  def sumMedia(self,medToSum):
    self.cont=self.cont+medToSum.cont
    self.u=self.u+medToSum.u
    self.v=self.v+medToSum.v
    self.sn=self.sn+medToSum.sn
    self.FCl=self.FCl+medToSum.FCl
    self.up=self.up+medToSum.up
    self.vp=self.vp+medToSum.vp
    self.uvp=self.uvp+medToSum.uvp
    self.Info=self.Info+medToSum.Info
    if self.x.size<=1:
      self.x=medToSum.x  #piv.x dovrebbero essere tutti uguali
      self.y=medToSum.y  #piv.y dovrebbero essere tutti uguali

  def calcMedia(self):
    if self.cont>0:

      self.u/=self.cont
      self.v/=self.cont
      self.sn/=self.cont
      self.FCl/=self.cont
      self.Info/=self.cont#percentuale di vettori buoni 1=100% 0 nememno un vettore buono
      self.up=(self.up/self.cont-self.u*self.u)#nan or inf is no good vector
      self.vp=(self.vp/self.cont-self.v*self.v)#nan or inf is no good vector
      self.uvp=(self.uvp/self.cont-self.u*self.v)#nan or inf is no good vector
      
  
  def restoreSum(self):
        
    #OPTIMIZE TA GP gestione delle statistiche ora si usano tutti i vettori anche quelli corretti forse si dovrebbe dare la possibiltà all'utente di scegliere?
    self.up=(self.up+self.u*self.u)*self.cont # inf is no good vector
    self.vp=(self.vp+self.v*self.v)*self.cont # inf is no good vector
    self.uvp=(self.uvp+self.u*self.v)*self.cont # inf is no good vector

    self.u=self.u*self.cont
    self.v=self.v*self.cont
    self.sn=self.sn*self.cont
    self.Info=self.Info*self.cont#percentuale di vettori buoni 1=100% 0 nememno un vettore buono

  
class CompMin():
  ''' helper class to compute minimum '''
  def __init__(self):
    self.Imin=[np.zeros(0),np.zeros(0)]
    self.med=[np.zeros(1),np.zeros(1)]
    self.contab=[0,0]
    #self.cont=0
    #self.cont0=0
    
    self.flag_TR=None
  
  def minSum(self,I,k):
    ''' min '''   
    #sleep(0.15) 
    # min or max
    if len(I):# why 
      if self.contab[k]==0:
        self.Imin[k]=I
      else:
        self.Imin[k]=np.minimum(I,self.Imin[k])
      # verage std and the like
      self.med[k]=self.med[k]+I#+= non funziona all'inizio
      self.contab[k]+=1
    #prLock(f"minSum   contab={self.contab[k]}")
  def checkImg(self,I,sogliaMedia,sogliaStd)->bool:
    ''' checkImg '''   
    dum=1/I.size
    media=I.ravel().sum()*dum#faster than mean
    dev=np.square(I-media).ravel().sum()*dum
    return media>sogliaMedia and dev >sogliaStd*sogliaStd 
    
  def calcMin(self,minMed):
    ''' calcMin and sum media  '''
    #pri.Time.magenta(0,f"self.cont0={self.cont0}")
    #self.cont+=self.cont0
    #nImg=1 if self.flag_TR else 2
    nImg=2
    for k in range(nImg):
    
      if minMed.contab[k]>0:
        if self.contab[k]==0:
          self.Imin[k]=minMed.Imin[k]
        else:
          self.Imin[k]=np.minimum(minMed.Imin[k],self.Imin[k])
        self.med[k]=self.med[k]+minMed.med[k]
        self.contab[k]+=minMed.contab[k]# uno viene comunque sommato in min
    
  def calcMed(self):
    ''' calcMed and sum media  '''
    pri.Time.magenta(f"calcMed   contab={self.contab}  ")
    #nImg=1 if self.flag_TR else 2
    nImg=2
    for k in range(nImg):
      if self.contab[k]>0:
        self.med[k]/=self.contab[k]
    pri.Time.magenta(f"calcMed   fine contab={self.contab}  ")
        
    

  def restoreMin(self):
    #pr(f"restoreMin   contab={self.contab}    self.cont={self.cont} self.cont0={self.cont0}")
    #nImg=1 if self.flag_TR else 2
    nImg=2
    for k in range(nImg):
      self.med[k]*=self.contab[k]

def foList(li,formato):
  ''' format a list call with 
    where:
    li is a list 
    format is the format that would have been used fo a single element of the list
    e.g. print(f'{a:<4d}') -> print(f'{foList([a a],"<4d")}') 
  '''
  return f"{''.join(f' {x:{formato}}' for x in li)}"
# todo delete olf function
def writeCfgProcPivOld(data,nomeFile):
    PIV=data2PIV(data)
    PIV.SetVect([v.astype(np.intc) for v in data.PRO.Vect])
    inp=PIV.Inp
    vect=data.PRO.Vect
    
    with open(nomeFile,'w', encoding="utf8") as f:
        f.write('%TA000N3 Do not modify the previous string - It indicates the file version\n')
        f.write('% PIV process configuration file - A % symbol on the first column indicates a comment\n')
        f.write('% Windows dimensions ***************************************\n')
        #    % Windows dimensions ***************************************
        f.write(f'[{foList(vect[0],"<3d")}], 			Height of the windows (rows) - insert the sequence of numbers separated by a blank character (1)\n')
        f.write(f'[{foList(vect[2],"<3d")}], 			Width of the windows (columns) (2)\n')
        f.write(f'[{foList(vect[1],"<3d")}], 			Grid distance along the height direction (y) (3)\n')
        f.write(f'[{foList(vect[3],"<3d")}], 			Grid distance along the width direction (x) (4)\n')
        f.write(f'{inp.FlagBordo}, 			Flag boundary: if =1 the first vector is placed at a distance to the boundary equal to the grid distance (5)\n')
        #     % Process parameters - Interpolation ***********************************
        f.write(f'% Process parameters - Interpolation ***********************************\n')
        f.write(f'{inp.IntIniz}, 			Type of interpolation in the initial part of the process (6)\n')
        f.write(f'{inp.IntFin}, 			Type of interpolation in the final part of the process (7)\n')
        f.write(f'{inp.FlagInt}, 			Flag Interpolation: if >0 the final interpolation is used in the final #par iterations (8)\n')
        f.write(f'{inp.IntCorr}, 			Type of interpolation of the correlation map (0=gauss classic; 1=gauss reviewed; 2=Simplex) (9)\n')
        f.write(f'{inp.IntVel}, 			Type of interpolation of the velocity field (1=bilinear; 2= Simplex,...) (10)\n')
        #     % Process parameters **************************************\n')
        f.write(f'% Process parameters **************************************\n')
        f.write(f'{inp.FlagDirectCorr}, 			Flag direct correlation on the final iterations (0=no 1=yes ) (11)\n')
        f.write(f'{inp.NIterazioni}, 			Number of final iterations (12)\n')
        f.write(f'% Activation flags   **************************************\n')
        #     % Activation flags - Validation **************************************
        f.write(f'1, 			Flag Validation (0=default parameters (see manual); otherwise the validation parameters in the final part of the cfg file are activated) (13)\n')
        f.write(f'1, 			Flag Windowing (0=default parameters (see manual); otherwise the windowing parameters in the final part of the cfg file are activated) (14)\n')
        f.write(f'1, 			Flag Filter    (0=default parameters (see manual); otherwise the additional filter parameters in the final part of the cfg file are activated) (29)\n')
        f.write(f'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
        f.write(f'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
        #     % Process parameters - Validation **************************************
        
        f.write(f'% Process parameters - Validation **************************************\n')
        f.write(f'{inp.FlagValid}, 			Flag median test: 0=no; 1=classic; 2=universal (Scarano, 			Westerweel 2005) (15)\n')
        f.write(f'{inp.SemiDimValid}, 			Half-dimension of the kernel (it uses 2*(#par)+1 vectors for each direction) (16)\n')
        f.write(f'{inp.SogliaMed:.2f},			Threshold for the median test - Advised value 2 (1.0 - 3.0) (17)\n')
        f.write(f'{inp.ErroreMed:.2f},			Allowed Error in pixel for the median test - Advised value 0.1 (0.0 -> no limits) (18)\n')
        f.write(f'{inp.FlagAttivaValSN}, 			Flag test sn/CC: 0=no; 1=sn; 2=CC; 3=both  +4 for limiting the maximum displacement (19)\n')
        f.write(f'{inp.SogliaSN:.2f},			Threshold for the signal/noise test (Advised value 1.5) - it doesn\'t work on the direct correlation (20)\n')
        f.write(f'{inp.SogliaFcl:.2f},			Threshold correlation coefficient (Advised value 0.25) (21)\n')
        f.write(f'{inp.FlagSecMax}, 			Flag correction with the second maximum; 0=not active; otherwise it is active (22)\n')
        f.write(f'{inp.FlagCorrezioneVel}, 			Flag correction vectors: 0=average on correct vectors; 1=weighted average with the distance; 2=iterative average (23)\n')
        f.write(f'{inp.SogliaNoise:.2f},			Minimum allowed average value in the interrogation window (24)\n')
        f.write(f'{inp.SogliaStd:.2f},			Minimum allowed std deviation value in the interrogation window(25)\n')
        f.write(f'{inp.FlagValidNog}, 			Flag Nogueira Test (discontinued) : 0 --> no; !=0 -->yes  (if activated disables the other validation criteria )\n')
        f.write(f'0.2, 			First parameter Nogueira Test(0.20-0.35)  \n')
        f.write(f'0.1, 			Second parameter Nogueira Test(0.01-0.1)  \n')
        f.write(f'{0}, 			Hart Correction uses 4 interrogation windows  W=W-W/Par e H=H-/Par 0 disables\n')
        f.write(f'{0}, 			Value of info for a good vector   \n')
        f.write(f'{1}, 			Value of info for an outlier\n')
        #   % Windowing parameters (Astarita, 			Exp Flu, 			2007) *************************
        f.write(f'% Windowing parameters (Astarita EiF 2007) *************************\n')
        f.write(f'{inp.FlagCalcVel}, 			Weighting window for absolute velocity (0=TopHat, 1=Nogueira,	2=Blackmann,...) (26)\n')
        f.write(f'{inp.FlagWindowing}, 			Weighting window for the correlation map (0=TopHat 1= Nogueira 2=Blackmann 3=top hat at 50%) (27)\n')  
        f.write(f'{inp.SemiDimCalcVel}, 			Half-width of the filtering window (0=window dimension) (28)\n')
        #   % Adaptive PIV parameters (Astarita, 			Exp Flu, 			2009) *************************
        f.write(f'% Adaptive PIV parameters (Astarita EiF 2009) *************************\n')
        f.write(f'{inp.MaxC:.3f},  		Maximum value of zita (30)\n')  
        f.write(f'{inp.MinC:.3f},  		Minimum value of zita (30) \n')
        f.write(f'{inp.LarMin}, 			Minimum Half-width of the weighting window (31)\n')
        f.write(f'{inp.LarMax}, 			Maximum Half-width of the weighting window (31)\n')
        #   % Further processing parameters *************************
        f.write(f'% Further processing parameters *************************\n')
        f.write(f'{inp.FlagSommaProd}, 			Flag product or sum of correlation 0 prod 1 sum (only used if par 27 or 11 are !=0) (32)\n')
        f.write(f'{inp.ItAtt if not -1000 else 0 }, 			Flag for restarting from a previous process (0 no otherwise the previous iteration) (33)\n')
        #   % Filter parameters *************************
        FlagFilt=0
        CutOff=18
        VelCut=-1
        f.write(f'% Additional  filter parameters 2009) *************************\n')
        f.write(f'{FlagFilt:}, 			Flag for alternate direction filtering 0 disable 1 dense predictor 2 displacement (34)\n')  
        f.write(f'{CutOff:.2f},  		Vertical Cutoff wavelength (35) \n')
        f.write(f'{VelCut:.2f},  		Vertical filter rate (36)\n')
        f.write(f'{CutOff:.2f},  		Horizontal Cutoff wavelength (35) \n')
        f.write(f'{VelCut}, 			Horizontal filter rate (36)\n')
        f.write(f'{inp.FlagRemNoise}, 			Flag to activate noise removal on the images (37)\n')
        PercCap=-.001
        PercFc=-3
        f.write(f'{PercFc}, 			Parameter for noise removal  (38)\n')
        f.write(f'{PercCap}, 		Number of std to cap the particles (negative disables) (39)\n')

    
    ''' 
    try:
      p=PaIRS_lib.PIV()
      p.readCfgProc(nomeFile)
    except Exception as inst:
      pri.Error.white(inst.__cause__)

    import inspect
    notUsedKey=['FlagLog','HCellaVec','HOverlapVec','ImgH','ImgW','RisX','RisY','WCellaVec','WOverlapVec','dt','this'    ]
    diPro= dict(inspect.getmembers(PIV.Inp))
    flagEqual=1
    for k,v in inspect.getmembers(p.Inp):
      if not k[0].startswith('_'):
        if not k in notUsedKey:
          if v!=diPro[k]:
            flagEqual=0
            print(f'{k}={v}->{diPro[k]}')
    if flagEqual:
      pr('The cfg is identical to the master')
    #verifica uguaglianza PROpar, mancano i vettori
    flagEqual=1
    try:
      pro=PIV2Pro(p)
      pDum=data2PIV(data)
      pDum.SetVect([v.astype(np.intc) for v in data.PRO.Vect])
      pro=PIV2Pro(pDum)
      
      notUsedKey=['change_top','copyfrom','copyfromdiz','duplicate','indexes','isDifferentFrom','isEqualTo','printDifferences','printPar','setup','tip','uncopied_fields','indTree','indItem']
      listOfList=['Vect'    ]
      diPro= dict(inspect.getmembers(data.PRO))
      #pro.printDifferences(data.PRO,[],[],True) #questo è automatico
      for k,v in inspect.getmembers(pro):
        if not k[0].startswith('_') and not k in notUsedKey:

          if  k in listOfList:
            
              for i,(a,b) in enumerate(zip (v,diPro[k])):
                if (a!=b).any():
                  flagEqual=0
                  print(f'{k}[{i}]={a}->{b}')
          else:
              if v!=diPro[k]:
                flagEqual=0
                print(f'{k}={v}->{diPro[k]}')
      if flagEqual:
        pr('The PROpar is identical to the master')
    except Exception as inst:
        pri.Error.red(f'{inst}')
                    
    
    #'''         
def writeCfgProcPiv(data,nomeFile):
    PIV=data2PIV(data)
    inp=PIV.Inp
    vect=PIV.GetVect()
    vectWindowing=PIV.GetWindowingVect()
    
    with open(nomeFile,'w', encoding="utf8") as f:
        f.write('%TA000N5 Do not modify the previous string - It indicates the file version\n')
        f.write('% PIV process configuration file - A % symbol on the first column indicates a comment\n')
        f.write('% Windows dimensions position and iterations *******************************\n')
        #    % Windows dimensions position and iterations *******************************
        f.write(f'[{foList(vect[0],"<3d")}],      Height of the windows - sequence separated by a space            (1)\n')
        f.write(f'[{foList(vect[2],"<3d")}],      Width of the IW if equal to -1 then square IW are used           (1)\n')
        f.write(f'[{foList(vect[1],"<3d")}],      Grid distance along the height direction (y)                     (2)\n')
        f.write(f'[{foList(vect[3],"<3d")}],      Grid distance along x if equal to -1 then a square grid is used  (2)\n')
        f.write(f'{inp.FlagBordo},                   Pos flag: 0 normal 1 1st vector is placed par#2 from the border  (3)\n')
        f.write(f'{inp.NIterazioni},                   Number of final iterations                                       (4)\n')
        
        #     % Process parameters - Interpolation ***********************************
        f.write(f'% Process parameters - Interpolation ***********************************\n')
        f.write(f'[{foList([inp.IntIniz,inp.FlagInt,inp.IntFin],"<3d")}],      Image Interpolation: [intial; #iter; final]                      (5)\n')
        f.write(f'{inp.IntCorr},                   Correlation peak IS (3=gauss; 4=gauss reviewed; 5=Simplex)       (6)\n')
        f.write(f'{inp.IntVel},                  Dense predictor IS (1=bilinear; 2=Simplex...)                    (7)\n')
        #     % Process parameters - Validation ******************************************\n')
        f.write(f'% Process parameters - Validation ******************************************\n')
        f.write(f'[{foList([inp.FlagValid,inp.SemiDimValid,inp.SogliaMed,inp.ErroreMed],".6g")}],       Median test: [0=no; 1=med; 2=univ; kernel dim=1; thr=2; eps=0.1]  (8)\n')
        f.write(f'[{foList([inp.FlagAttivaValSN,inp.SogliaSN,inp.SogliaFcl],".6g")}],       sn/CC test: [0=no; 1=sn; 2=CC; 3=both;sn thr=1.5; cc thr=0.3]     (9)\n')
        f.write(f'[{foList([inp.FlagValidNog,inp.SogliaMedia,inp.SogliaNumVet],".6g")}],      Nog test:[0 no; 1 active; par1; par2]                             (10)\n')
        f.write(f'[{foList([inp.SogliaNoise,inp.SogliaStd],".6g")}],             Minimum threshold: [mean=2; std=3]                                (11)\n')
        f.write(f'{inp.FlagCorrHart},                  Hart correction 4 IW of  W=W-W/Par are used o correct outliers    (12)\n')
        f.write(f'{inp.FlagSecMax},                  Flag second maximum correction; 0 no 1 active                     (13)\n')
        f.write(f'{inp.FlagCorrezioneVel},                  Flag vectors correction: 0=average on correct vectors; 1=weighted average with the distance; 2=iterative average  (14)\n')
        f.write(f'[{foList([inp.InfoSi,inp.InfoNo],".6g")}],             Output values (info): [value for good=1; value for corrected=0]   (15)\n')
        # % Windowing parameters (Astarita, Exp Flu, 2007) ***************************
        
        f.write(f'% Windowing parameters (Astarita, Exp Flu, 2007) ***************************\n')
        f.write(f'[{foList(vectWindowing[1],"<3d")}],             WW for predictor  (0=TopHat; 2=Blackmann;...)                     (16)\n')
        f.write(f'[{foList(vectWindowing[2],"<3d")}],             WW for the correlation map (0=TopHat;2=Blackmann 3=top hat at 50%)(17)\n')
        f.write(f'[{foList(vectWindowing[3],"<3d")}],             Half-width of the filtering window (0=window dimension)           (18)\n')
        f.write(f'[{foList(vectWindowing[4],"<3d")}],     Flag direct correlation (0=no 1=yes )                             (19)\n')
        f.write(f'[{foList(vectWindowing[0],"<3d")}],         Max displacement if <0  fraction of wa i.e. -4-> Wa/4             (20)\n')
        f.write(f'{inp.FlagSommaProd},                  Double CC operation (0 Product 1 sum)                             (21)\n')
        f.write(f'[{foList([inp.flagAdaptive,inp.MaxC,inp.MinC,inp.LarMin,inp.LarMax],".6g")}], Adaptive process [0=no;#of it; par1; par2; par3; par4]            (22)\n')
        f.write(f'{inp.ItAtt if not -1000 else 0 },                  Flag for restarting from a previous process (0 no; prev iter)     (23)\n')
        # % Filter parameters  *******************************************************
        f.write(f'% Filter parameters  *******************************************************\n')
        f.write(f'[{foList([inp.FlagFilt,inp.CutOffH,inp.VelCutH,inp.CutOffW,inp.VelCutW ],".6g")}],   Additional AD filter [0 no; 1 Pred; 2 disp; cutoff H;Rate H;W;W]  (24)\n')
        f.write(f'[{foList([inp.FlagRemNoise,inp.PercFc,],".6g")}],          Noise reduction removal of particles [0 no; it=2; perc=0.01]      (25)\n')
        
        f.write(f'[{0 if inp.PercCap<0 else 1:d} {abs(inp.PercCap):.6g}],           Noise reduction capping [0 no; val=1.05]    (26)\n')
        f.write('\n')
        
        
    
    '''
        # Mettere alla fine di updateGuiFromTree
        tree,_=self.w_Tree.pickTree(self.w_Tree.TREpar.indTree)
        d=tree.currentItem().data(0,Qt.UserRole)
        data:dataTreePar=self.w_Tree.TABpar_prev[d.indTree][d.indItem][d.ind]
        data.writeCfgProcPiv()
        #''' 
    ''' 
    try:
      p=PaIRS_lib.PIV()
      p.readCfgProc(nomeFile)
    except Exception as inst:
      pri.Error.white(inst)

    import inspect
    notUsedKey=['FlagLog','HCellaVec','HOverlapVec','ImgH','ImgW','RisX','RisY','WCellaVec','WOverlapVec','dt','this' ,'FlagCalcVelVec',  'FlagDirectCorrVec','FlagWindowingVec','MaxDispInCCVec','SemiDimCalcVelVec' ]
    diPro= dict(inspect.getmembers(PIV.Inp))
    app=1e-6# to avoid false detections in case of float
    flagEqual=1
    for k,v in inspect.getmembers(p.Inp):
      if not k[0].startswith('_'):
        if not k in notUsedKey:
          if v!=diPro[k]:
            flagEqual=0
            print(f'{k}={v}->{diPro[k]}')
    if flagEqual:
      pr('The cfg is identical to the master')
    #verifica uguaglianza PROpar, mancano i vettori
    flagEqual=1
    
    try:
      #pro=PIV2Pro(p)
      pDum=data2PIV(data)
      pDum.SetVect([v.astype(np.intc) for v in data.PRO.Vect])
      pro=PIV2Pro(pDum)
      
      notUsedKey=['change_top','copyfrom','copyfromdiz','duplicate','indexes','isDifferentFrom','isEqualTo','printDifferences','printPar','setup','tip','uncopied_fields','indTree','indItem']
      listOfList=['Vect' ]##  to add ,'windowingVect'   
      diPro= dict(inspect.getmembers(data.PRO))
      #pro.printDifferences(data.PRO,[],[],True) #questo è automatico
      for k,v in inspect.getmembers(pro):
        if not k[0].startswith('_') and not k in notUsedKey:

          if  k in listOfList:
            
              for i,(a,b) in enumerate(zip (v,diPro[k])):
                if (a!=b).any():
                  flagEqual=0
                  print(f'{k}[{i}]={a}->{b}')
          else:
              if v!=diPro[k]:
                if isinstance(v, float) and v !=0 : 
                  if abs((v-diPro[k])/v) >app:
                    flagEqual=0
                    print(f'{k}={v}->{diPro[k]}')
      if flagEqual:
        pr('The PROpar is identical to the master')
    except Exception as inst:
        pri.Error.red(f'{inst}')
                    
    
    #'''           
# TODO rivedere quando Gerardo aggiunge i vettori
def PIV2Pro(piv:PaIRS_lib.PIV)-> PROpar:  
  pro=PROpar()
  
  #PIV.SetVect([v.astype(np.intc) for v in data.PRO.Vect])
  pro.Vect=[v.astype(np.intc) for v in piv.GetVect()]
  #pro.windowingVect=[v.astype(np.intc) for v in piv.GetVect()]
  
  pro.SogliaNoise=piv.Inp.SogliaNoise
  pro.SogliaStd=piv.Inp.SogliaStd
  pro.SogliaMed=piv.Inp.SogliaMed
  pro.ErroreMed=piv.Inp.ErroreMed
  # Parameters not used in PaIrs but read by readcfg.
  # int FlagFilt;			
  # Tom_Real CutOffH;		// Lunghezza d'onda massima per il filtro					
  # Tom_Real CutOffW;		// Lunghezza d'onda massima per il filtro					
  # Tom_Real VelCutH;		// Rateo di filtraggio											
  # Tom_Real VelCutW;		//																		
  # Tom_Real PercCap;		// PPercentuale massimo livello di grigio non trattato
  # Tom_Real PercFc;		//	Percentuale per considerare cattivo un punto	
  # int FlagCorrHart;		// Flag Per Correzione Hart					
  # These parameters are not exposed in Inp if needed modify PIV_input.i
  #Valid Nog 
  pro.SogliaMedia=0.25#piv.Inp.SogliaMedia
  pro.SogliaNumVet=0.10#piv.Inp.SogliaNumVet
  pro.FlagCorrHart=0#piv.Inp.SogliaNumVet
  
  if piv.Inp.FlagValidNog==1:
    pro.FlagNogTest=1
    pro.FlagMedTest=0
    pro.FlagCPTest=0
    pro.FlagSNTest =0
  else:
    if piv.Inp.FlagValid>0 :
      pro.FlagMedTest=1
      pro.TypeMed=piv.Inp.FlagValid-1
      pro.KernMed=piv.Inp.SemiDimValid
      pro.FlagSecMax=piv.Inp.FlagSecMax 
    pro.FlagSNTest =1 if piv.Inp.FlagAttivaValSN&1  else 0
    pro.FlagCPTest =1 if piv.Inp.FlagAttivaValSN&2  else 0

  pro.SogliaSN=piv.Inp.SogliaSN
  pro.SogliaCP=piv.Inp.SogliaFcl

  pro.IntIniz=piv.Inp.IntIniz
  pro.IntFin=piv.Inp.IntFin
  pro.FlagInt=piv.Inp.FlagInt
  pro.IntVel=piv.Inp.IntVel 
  pro.FlagCorrezioneVel=piv.Inp.FlagCorrezioneVel
  #pro.FlagCorrHart=PIV.Inp.FlagCorrHart
  pro.IntCorr=piv.Inp.IntCorr 
  pro.FlagWindowing=piv.Inp.FlagWindowing

  pro.MaxC=piv.Inp.MaxC
  pro.MinC=piv.Inp.MinC
  pro.LarMin=piv.Inp.LarMin
  pro.LarMax=piv.Inp.LarMax

  pro.FlagCalcVel=piv.Inp.FlagCalcVel
  pro.FlagSommaProd=piv.Inp.FlagSommaProd
  pro.FlagDirectCorr=piv.Inp.FlagDirectCorr
  pro.FlagBordo=piv.Inp.FlagBordo



  if piv.Inp.SemiDimCalcVel<0:
     pro.NItAdaptative=-piv.Inp.SemiDimCalcVel
     pro.NIterazioni=piv.Inp.NIterazioni-pro.NItAdaptative
     pro.FlagAdaptative=1
  else:   
      pro.SemiDimCalcVel=piv.Inp.SemiDimCalcVel
      pro.NIterazioni=piv.Inp.NIterazioni
      pro.FlagAdaptative=0

  return pro
   
def data2PIV(data):
    PIV=PaIRS_lib.PIV()
    
    PIV.DefaultValues()
    OUT=data.OUT
    PRO=data.PRO

    # % Windows dimensions position and iterations *******************************
    PIV.SetVect([v.astype(np.intc) for v in data.PRO.Vect])
    PIV.Inp.FlagBordo=PRO.FlagBordo
    PIV.Inp.NIterazioni=PRO.NIterazioni+PRO.NItAdaptative if PRO.FlagAdaptative else PRO.NIterazioni
    # % Process parameters - Interpolation ***********************************
    PIV.Inp.IntIniz=PRO.IntIniz
    PIV.Inp.FlagInt=PRO.FlagInt
    PIV.Inp.IntFin=PRO.IntFin
    PIV.Inp.IntCorr=PRO.IntCorr+3     
    PIV.Inp.IntVel=PRO.IntVel 

    # % Process parameters - Validation ******************************************
    #  Median test : [0 = no; 1 = med; 2 = univ, kernel dim = 1, thr = 2, eps = 0.1] (8)
    PIV.Inp.FlagValid=1 if PRO.TypeMed==0 else 2
    PIV.Inp.SemiDimValid=PRO.KernMed
    PIV.Inp.SogliaMed=PRO.SogliaMed
    PIV.Inp.ErroreMed=PRO.ErroreMed
    PIV.Inp.jumpDimValid=1
    # sn/CC test: [0=no; 1=sn; 2=CC; 3=both,sn thr=1.5, cc thr=0.3]     (9)
    PIV.Inp.FlagAttivaValSN=1 if PRO.FlagSNTest else 0
    PIV.Inp.FlagAttivaValSN|=2 if PRO.FlagCPTest else 0
    PIV.Inp.SogliaSN=PRO.SogliaSN
    PIV.Inp.SogliaFcl=PRO.SogliaCP

    # Nog test : [0 no; 1 active, par1, par2] (10)
    PIV.Inp.FlagValidNog=1 if PRO.FlagNogTest else 0
    PIV.Inp.SogliaMedia=PRO.SogliaMedia
    PIV.Inp.SogliaNumVet=PRO.SogliaNumVet
    
    PIV.Inp.SogliaNoise=PRO.SogliaNoise
    PIV.Inp.SogliaStd=PRO.SogliaStd
    
    PIV.Inp.FlagCorrHart=0 # to be seen 
    PIV.Inp.FlagSecMax=1 if PRO.FlagSecMax else 0
    PIV.Inp.FlagCorrezioneVel=PRO.FlagCorrezioneVel
    # Output values(info) : [value for good = 1, value for corrected = 0] (16)
    PIV.Inp.InfoSi=1
    PIV.Inp.InfoNo=0
    
    # % Windowing parameters (Astarita, Exp Flu, 2007) ***************************
    PIV.Inp.numInitIt=max(len(v) for v in data.PRO.Vect)
    PIV.Inp.FlagWindowing=PRO.FlagWindowing
    """
    if (PIV.Inp.FlagWindowing >= 0) :
      FlagWindowingVec=np.array([PIV.Inp.FlagWindowing],dtype=np.intc)
    else :
      numInitIt = PIV.Inp.numInitIt +1# if negative onlhy in the final iterations
      FlagWindowingVec=np.array([0 if ii<numInitIt -1 else -PIV.Inp.FlagWindowing for ii in range(numInitIt) ],dtype=np.intc)
    """
    FlagWindowingVec=np.array(PRO.vFlagWindowing,dtype=np.intc)

    flagCalcVelVec=np.array(PRO.vFlagCalcVel,dtype=np.intc)
    semiDimCalcVelVec=np.array(PRO.vSemiDimCalcVel,dtype=np.intc)
    
    PIV.Inp.FlagDirectCorr=PRO.FlagDirectCorr
    """
    if (PIV.Inp.FlagDirectCorr == 0) :
      FlagDirectCorrVec=np.array([PIV.Inp.FlagDirectCorr],dtype=np.intc)
    else :
      numInitIt = PIV.Inp.numInitIt +(PIV.Inp.FlagDirectCorr - 1)# if equal to 2 then should be one element longer
      FlagDirectCorrVec=np.array([0 if ii<numInitIt -1 else 1 for ii in range(numInitIt) ],dtype=np.intc)
    """
    FlagDirectCorrVec=np.array(PRO.vDC,dtype=np.intc)

    maxDispInCCVec=np.array(PRO.vMaxDisp,dtype=np.intc) 
    vect1=[maxDispInCCVec,flagCalcVelVec,FlagWindowingVec,semiDimCalcVelVec,FlagDirectCorrVec]
    
    PIV.Inp.numInitIt=max(*[len(v) for v in vect1],PIV.Inp.numInitIt)
 
    PIV.SetWindowingVect(vect1)
    PIV.Inp.FlagSommaProd=PRO.FlagSommaProd

    # Adaptive process[0 = no; #of it, par1, par2, par3, par4](22)
    # questo  è l'equivalente del c
    #PIV.Inp.flagAdaptive =-PIV.Inp.SemiDimCalcVel if  PIV.Inp.SemiDimCalcVel <= -1 else  0
    #PIV.Inp.SemiDimCalcVel = abs(PIV.Inp.SemiDimCalcVel)
    #flagCalcVelVec=np.array(abs(PIV.Inp.SemiDimCalcVel),dtype=np.intc)
    PIV.Inp.flagAdaptive =PRO.NItAdaptative if PRO.FlagAdaptative else 0
    PIV.Inp.MaxC=PRO.MaxC
    PIV.Inp.MinC=PRO.MinC
    PIV.Inp.LarMin=PRO.LarMin
    PIV.Inp.LarMax=PRO.LarMax    

    PIV.Inp.ItAtt=-1000
    
    
    PIV.Inp.RisX=OUT.xres#*float(10.0)
    PIV.Inp.RisY=OUT.xres*OUT.pixAR#*float(10.0)
    PIV.Inp.dt=OUT.dt*float(10)
    PIV.Inp.ImgH=OUT.h
    PIV.Inp.ImgW=OUT.W
    ''' already done in DefaultValues

    PIV.Inp.FlagFilt = 0; # Flag filtro: 0 nessuno, 1 AD,   
    PIV.Inp.CutOffH=18; # Lunghezza d'onda massima per il filtro    
    PIV.Inp.VelCutH=-1; # Rateo di filtraggio	    
    PIV.Inp.CutOffW=18; # Lunghezza d'onda massima per il filtro
    PIV.Inp.VelCutW=-1; #   
    PIV.Inp.FlagRemNoise = 0;     # Flag per eliminare rumore 0 no,1 si   
    PIV.Inp.PercFc=0.01;		#	Percentuale per considerare cattivo un punto
    PIV.Inp.PercCap=-1.05;		# PPercentuale massimo livello di grigio non trattato
    '''
    


    
    
    
    

    return PIV

def printPIVLog(PIV):
    stampa="It    IW      #IW        #Vect/#Tot      %       CC       CC(avg)   DC%\n"#  NR% Cap%\n"
    for j in range(len(PIV.PD.It)):
        riga="%3d %3dx%-3d %4dx%-4d %7d/%-7d %5.1f  %8.7f  %8.7f  %4.1f\n" %\
            (PIV.PD.It[j], PIV.PD.WCella[j], PIV.PD.HCella[j], PIV.PD.W[j], PIV.PD.H[j], PIV.PD.NVect[j],\
            PIV.PD.W[j]*PIV.PD.H[j], 100.0*PIV.PD.NVect[j]/(PIV.PD.W[j]*PIV.PD.H[j]), PIV.PD.Fc[j],\
                PIV.PD.FcMedia[j], 100.0*PIV.PD.ContErorreDc[j]/(PIV.PD.W[j]*PIV.PD.H[j]))#,\
                    #100.0*PIV.PD.ContRemNoise[j]/(PIV.Inp.ImgW*PIV.Inp.ImgH),\
                    #100.0*PIV.PD.ContCap[j]/(PIV.Inp.ImgW*PIV.Inp.ImgH))
        stampa=stampa+riga
    return stampa

def saveMin(data:dataTreePar,Imin=list):
  pri.Time.magenta('saveMin Init ')
  frames='ab'
  #nImg=1 if self.flag_TR else 2
  nImg=2
  for j in range(nImg):
    name_min=f"{data.outPathRoot}_{frames[j]}_min{data.inpExt}"
    im = Image.fromarray(Imin[j])
    im.save(name_min)
  pri.Time.magenta('saveMin End')
  
def saveResults(data:dataTreePar,i,Var,nameVar):
    #pri.Time.magenta('saveResults Init')
    if i<0:
        nameFileOut=os.path.join(f"{data.outPathRoot}{data.outExt}")
    else:
        nameFileOut=os.path.join(f"{data.outPathRoot}_{i:0{data.ndig:d}d}{data.outExt}")
    #infoPrint.white(f'---> Saving field #{i}: {nameFileOut}')
    if '.plt' in data.outExt:
        writePlt(nameFileOut,Var,f'PaIRS - 2D PIV',nameVar,nameFileOut)
    elif  '.mat' in data.outExt:
        dict_out={}
        for j in range(len(nameVar)):
            dict_out[nameVar[j]]=Var[j]
        scipy.io.savemat(nameFileOut,dict_out)
        #import timeit
        #timeit.timeit (lambda :'writePlt(nameFileOut,Var,"b16",nameVar,nameFileOut)')
        #timeit.timeit (lambda :'scipy.io.savemat(nameFileOut,dict_out)')
    #pri.Time.magenta('saveResults End')

def memoryUsagePsutil():
    ''' return the memory usage in MB '''
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss 
    #print(f"Memory={mem/ float(2 ** 20)}MByte")
    return mem
