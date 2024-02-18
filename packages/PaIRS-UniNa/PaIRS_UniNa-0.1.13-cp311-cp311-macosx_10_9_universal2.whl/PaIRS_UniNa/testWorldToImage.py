import sys, traceback, os
#from typing import Tuple,Callable#,TextIO,Union

import platform
import numpy as np

from .tAVarie import pri, PrintTA ,PrintTAPriority
#from  readcfg import readNumCfg, readCfgTag,readNumVecCfg
if __package__ or "." in __name__:
  import PaIRS_UniNa.PaIRS_PIV as PaIRS_lib
  from PaIRS_UniNa.PaIRS_PIV import Punto
  from PaIRS_UniNa.PaIRS_PIV import CalFlags
else:
  if platform.system() == "Darwin":
    sys.path.append('../lib/mac')
    #sys.path.append('../lib')
  else:
    #sys.path.append('PaIRS_PIV')
    sys.path.append('../lib')
    sys.path.append('TpivPython/lib')
  import PaIRS_PIV as PaIRS_lib # type: ignore
  from PaIRS_PIV import Punto # type: ignore
  from PaIRS_PIV import CalFlags # type: ignore
#import debugpy #nel casso mettere nel thread debugpy.debug_this_thread()
#from calib import Calib,MappingFunction, CalibWorker,CalibTasks, calibTasksText, CalibFunctions, calibFunctionsText
#from imageviewer import CalibView


mapFun=PaIRS_lib.MappingFunction()
#mapFun.readCal(['C:\desk\Attuali\PythonLibC\PIV\img\calib\pyCal1.cal','C:\desk\Attuali\PythonLibC\PIV\img\calib\pyCal1Copia.cal'])
#mapFun.readCal(['C:/desk/PIV_Img/cal/pyCal0.cal'])
mapFun.readCal(['/Users/gerardo/Desktop/PaIRS_examples/cal/pyCal1.cal'])
nPunti=4
b = np.array([0.1, 0.2])[:,None]
tipo=np.float64
points=np.array([[1,2,3]]*nPunti,dtype=tipo,order='C')+np.array(np.arange(nPunti)*0.001,dtype=tipo)[:,None]
X1=mapFun.worldToImg(points,-1,None)

tipo=np.float32
points=np.array([[1,2,3]]*nPunti,dtype=tipo,order='C')+np.array(np.arange(nPunti)*0.001,dtype=tipo)[:,None]
X=np.zeros([mapFun.nCam, nPunti,2],dtype=np.float32,order='C')

X1=mapFun.worldToImg(points,-1,X)
print(X1)
point=mapFun.worldToImgPoint([0,0,0],0)
print(f'{point.x} {point.y}')
'''
calib=Calib()

cams=[0 ,1]
data.NCam = len(cams) # Numero di elementi nel vettore cam (numero di camere da calibrare)

flagCal,numCostCalib,cost=calib.readCalFileNew('C:\desk\Attuali\PythonLibC\PIV\img\calib\pyCal1.cal')
calib.cal.vect.cost
print(calib)
'''
