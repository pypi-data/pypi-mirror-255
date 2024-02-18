
''' frewr'''
# pylint: disable=pointless-string-statement, too-many-instance-attributes, no-name-in-module, multiple-imports
# pylint: disable= import-error 
# pylint: disable=multiple-statements,c-extension-no-member
import sys #, traceback
from typing import Callable
from enum import Enum
#import faulthandler # per capire da dove vengono gli errori c
import platform

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import  QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtWidgets import QApplication, QPushButton,  QSpinBox
from .addwidgets_ps import *

from PIL import Image, ImageQt
import numpy as np


from PySide6.QtCore import  Slot, QThreadPool, QObject, Signal #,QRunnable


#from PySide6.QtWidgets import QMainWindow
from .calib import Calib, CalibWorker,CalibTasks, calibTasksText, CalibFunctions, calibFunctionsText

from .PaIRS_pypacks import pri, Flag_DEBUG_PARPOOL
#if Flag_DEBUG_PARPOOL: import debugpy # pylint: disable=unused-import #nel caso mettere nel thread debugpy.debug_this_thread()

#faulthandler.enable() # per capire da dove vengono gli errori c
if __package__ or "." in __name__:
  import PaIRS_UniNa.PaIRS_PIV as PaIRS_lib # pylint: disable=unused-import
  from PaIRS_UniNa.PaIRS_PIV import Punto
  from PaIRS_UniNa.PaIRS_PIV import CalFlags
else:
  if platform.system() == "Darwin":
    sys.path.append('../lib/mac')
  else:
    #sys.path.append('PaIRS_PIV')
    sys.path.append('../lib')
  import PaIRS_PIV as PaIRS_lib # pylint: disable=unused-import # type: ignore
  from PaIRS_PIV import Punto # type: ignore
  from PaIRS_PIV import CalFlags # type: ignore


class CircleType(Enum):
  circle = 1 # pylint: disable=invalid-name
  square= 2  # pylint: disable=invalid-name
  filledCircle=3 # pylint: disable=invalid-name

mainInCircleColors=['#ff0000', '#ff00ff','#0000ff']
foundCircleColor='#ff0000'
maxErrorCircleColor='#ffff00'
OriginCircleColor='#00ff00'
mainInCircleType=[CircleType.circle, CircleType.square,CircleType.circle]
rFoundCircle=5
rInpCircle=15
penWidth=2
percLunFreccia=0.25#lunghezza testa      
lunFreccia=100#scalatura freccia
angFreccia=30*np.pi/180 
tanFreccia=percLunFreccia*np.tan(angFreccia)
    
class    Circle():
  def __init__(self,x,y,r:int=rInpCircle,col:str=foundCircleColor,ty:CircleType=CircleType.filledCircle):#'#EB5160'
    self.r=r
    self.col=col
    self.type=ty
    self.xe=x
    self.ye=y
    self.x=x
    self.y=y
  @classmethod
  def fromPunto(cls, pu:Punto,r:int=5,col:str=foundCircleColor,ty:CircleType=CircleType.circle)->Punto:
      ''' retrun a circle from a Punto'''
      return cls(pu.x,pu.y,r,col,ty)
          #raise inst
class SignalsImageViewer(QObject):
  ''' signals used to comunicate form calib to view'''
  pointFromView=Signal(object)
  replyFromView=Signal(int)
  
class CalibView(QLabel):  
  ''' View class for the wrapper (calib)'''
  def aa__del__(self):# should not be used because some times it is not called when deleting the object there fore I have changed the name
    ''' destructor '''
    pri.Time.red(0,'Destructor calibView')
    pri.Info.white('Destructor CalibView.')
  def __init__(self,parent:QObject=None, outFromCalibView:Callable=None,outToStatusBarFromCalibView:Callable=None,textFromCalib:Callable=None,workerCompleted:Callable=None,):
      ''' 
        outFromCalibView called by plotImg -- output function called to give some single line info und to update the interface
        outToStatusBarFromCalibView output function with position and gray level 
        two other slot are passed and set when the worker is created
        self.worker.signals.textFromCalib.connect(textFromCalib) instruction for the user
        self.worker.signals.finished.connect(workerCompleted)
            '''
      super().__init__(parent)
      self.textFromCalib=textFromCalib  #Output function to status bar
      self.outToCaller=outFromCalibView  #output function to caller called by plot
      self.workerCompleted=workerCompleted
      self.outToStatusBarCaller=outToStatusBarFromCalibView #output function to caller called by mouseMoveEvent
      self.setBackgroundRole(QtGui.QPalette.Base)
      self.setSizePolicy(QtWidgets.QSizePolicy.Ignored,  QtWidgets.QSizePolicy.Ignored)
      self.setScaledContents(True)

      # Threadpool
      self.imageViewerThreadpool=QThreadPool()
      self.imageViewerThreadpool.setMaxThreadCount(10)

      #  Calib and the like
      self.calib=Calib()
      self.cfgName=''
      #flagOp=self.calib.readCfg()
      #self.calib.readImgs()#todo verificare eventuali errori e dimensioni delle immagini in questo momento non da errore e l'img viene tagliata
      self.rectMask=None
      
      self.flagGetPoint=0# if true acquire points and pass them to calib
      
      self.worker:CalibWorker=None
      self.signals=SignalsImageViewer()
      self.signals.pointFromView.connect(self.calib.pointFromView) 
      self.signals.replyFromView.connect(self.calib.replyFromView) 
      

      self.oldPos=QtCore.QPointF(0, 0)
      self.contextMenu:QtWidgets.Qmenu=None
      self.contextMenuActions:list[QAction]=[]
      '''
      # for now unused should be used to change the level and position
      self.timer = QtCore.QTimer(self)
      self.timer.timeout.connect( self.onTimer)        
      self.timer.start(100)
      self.oldPos=QtGui.QCursor.pos()
      '''
      
      self.setMouseTracking(True)
      self.flagButCalib=CalibTasks.findAllPlanes
      self.puMiddleButton=Punto(-1,-1)# point found when pressing with the middle button
      self.flagSearchMaskZone=False
      self.scaleFactor=1.0
      pri.Time.cyan(0,'End Init calibView')
      #pri.Callback.white (PaIRS_lib.Version(PaIRS_lib.MOD_Calib))
  
  def resetScaleFactor(self,scrollAreaSize):
    ''' reset the scale factor so that the image perfectly feet the window'''
    if self.calib.flagPlotMask:
      if len(self.calib.ccMask):
        (h,w)=self.calib.ccMask[0].shape
      else:
        return
    else:
       if len(self.calib.imgs):
          (h,w)=self.calib.imgs[0].shape
       else:
         return
    delta=4# by tom maybe delta pixel are added ??
    self.scaleFactor=min(    scrollAreaSize.height()/(h+delta),    scrollAreaSize.width()/(w+delta))
  @Slot(int)
  def drawCirclesFromCalib(self,plane:int):
    ''' draw all the circles '''
    self.drawCircles(plane)
  @Slot(object)
  def drawSingleCircleFromCalib(self,pu:Punto,flag:int,ind:int):
    ''' draws a single Circle from a point received by calib '''
    ci=Circle.fromPunto(pu) if flag else Circle.fromPunto(pu,r=rInpCircle,col=mainInCircleColors[ind],ty=mainInCircleType[ind])
    self.drawSingleCircle(ci)

  @Slot(object)
  def flagGetPointFromCalib(self,flag:int):
    ''' setter of flagGetPoint from calib'''
    self.flagGetPoint=flag
  @Slot(str)
  def askFromCalib(self,text:str):
    '''    ask if ok from Calib'''
    msgBox=QtWidgets.QMessageBox(self)
    okButton=QtWidgets.QMessageBox.Yes
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
    msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
    msgBox.setText(text)
    msgBox.setIcon(QtWidgets.QMessageBox.Question)

    okButton=msgBox.button(QtWidgets.QMessageBox.Yes)
    msgBox.show()

    screenGeometry = QtGui.QGuiApplication.primaryScreen().availableGeometry()
    screenGeo = screenGeometry.bottomRight()
    #msgGeo = QtCore.QRect(QtCore.QPoint(0,0), msgBox.sizeHint())
    msgGeo = QtCore.QRect(QtCore.QPoint(0,0), msgBox.size())
    msgGeo.moveBottomRight(screenGeo)
    #msgBox.move(msgGeo.bottomRight())
    #msgBox.move(100,0)
    a=msgBox.mapToGlobal(QtCore.QPoint(0, 0))
    a=QtCore.QPoint(*(msgBox.size()).toTuple())
    
    msgBox.move(msgGeo.bottomRight()-a-QtCore.QPoint(0,30))
    oldPos=QtGui.QCursor.pos()
    QtGui.QCursor.setPos(okButton.mapToGlobal(QtCore.QPoint(0, 0)+QtCore.QPoint(*(okButton.size()/2).toTuple())))
    #self.window().mapToGlobal(QtCore.QPoint(0, 0)) #main window
    #self.parentWidget().mapToGlobal(QtCore.QPoint(0, 0)) #parent widget
    res=msgBox.exec()
    QtGui.QCursor.setPos(oldPos)
  
    #res=QtWidgets.QMessageBox.question(self, "Calib",text )
    
    flag=1 if res == QtWidgets.QMessageBox.Yes  else  0
    self.signals.replyFromView.emit(flag)

  def createWorker(self,flag:CalibTasks,textFromCalib:Callable,workerCompleted:Callable):
    ''' create the worker, connects the signals and start'''
    self.worker=CalibWorker()
    self.worker.signals.drawSingleCircleFromCalib.connect(self.drawSingleCircleFromCalib)
    self.worker.signals.drawCirclesFromCalib.connect(self.drawCirclesFromCalib)
    self.worker.signals.flagGetPointFromCalib.connect(self.flagGetPointFromCalib)
    self.worker.signals.askFromCalib.connect(self.askFromCalib)
    self.worker.signals.plotImgFromCalib.connect(self.plotImg)
    self.worker.setTask(self.calib,flag)
    
    self.worker.signals.textFromCalib.connect(textFromCalib)
    self.worker.signals.finished.connect(workerCompleted)
    self.imageViewerThreadpool.start(self.worker)  

  def executeCalibTask(self,flag:CalibTasks):
    ''' button  pressed '''
    if flag is self.flagCurrentTask or flag  is CalibTasks.stop:# in this case always stop
      self.calib.flagExitFromView=True
      self.flagCurrentTask=flag=CalibTasks.stop
      self.flagGetPoint=0# if true acquire points and pass them to calib
      return True
    elif not self.flagCurrentTask is CalibTasks.stop: # already running a task simply exit function # pylint: disable=unneeded-not,superfluous-parens
      return False
    
    self.flagCurrentTask=flag
    self.calib.flagExitFromView=False
    self.createWorker(flag,self.textFromCalib,self.workerCompleted)
    return True

  def executeCalibFunction(self,flag:CalibFunctions):
    ''' button  pressed '''
    if flag is CalibFunctions.removeMaxErrPoint and self.calib.cal.flagCalibrated:
      self.calib.cal.vect.flag[self.calib.cal.data.kMax,self.calib.cal.data.jMax]=CalFlags.P_REMOVED
      self.calib.cal.removeMaxErrPoint()
          
      strPriErrCalib=self.calib.prettyPrintErrCalib()
      pri.Process.blue (strPriErrCalib)
      self.textFromCalib(strPriErrCalib)
      self.plotPlane(self.calib.cal.data.kMax)
    elif flag is CalibFunctions.findMaxErrPoint:
      self.plotPlane(self.calib.cal.data.kMax)
    elif flag is CalibFunctions.RemovePoint:
      
      pu=Punto(*self.scaleToImg(self.contextMenuPos).toTuple())
      if not self.insideImg(pu):
        return
      else:
        self.calib.cal.removePoint(pu)
        self.plotPlane(self.calib.plane)
        

    #self.scaleToImg(mouseEv.position())
  
      
  def plotPlane(self,plane):
    ''' plot image of plane=plane'''
    if 0<=plane <self.calib.nPlanes:
      self.calib.cal.data.piano=self.calib.plane=plane
      self.calib.cal.initFindPoint(plane)
      FlagPlot=self.plotImg(plane)   
      if FlagPlot and not self.calib.flagPlotMask: 
        self.drawCircles(plane)   
    #XY=self.calib.cal.pointFromCalib([0,0,0],0)
    #pri.Info.green(f"Punto (x,y,z)=(0,0,0) -> (X,Y)=({XY.x},{XY.y})")
      
    #self.outToStatusBarCaller(f'Cam#:{self.calib.plane//self.calib.nPlanesPerCam} Plane:{self.calib.plane%self.calib.nPlanesPerCam}')
    
  @Slot(int)
  def plotImg(self,plane=0,flagDrawRect=False):
    ''' plot the image whenever the plane is changed '''  
    pri.Callback.white('+++ Plotting image in Vis +++')
    img,FlagPlot=self.calib.preparePlot(plane)
    if not FlagPlot: 
      self.setPixmap(QtGui.QPixmap())
      return FlagPlot
    dumStr='' if self.calib.cal.data.FlagCam else f'_cam{self.calib.cams[self.calib.plane//self.calib.nPlanesPerCam]}'
    nomeImg=self.calib.cal.getImgRoot(self.calib.plane%self.calib.nPlanesPerCam)+dumStr+self.calib.cal.data.EstensioneIn
    self.outToCaller(nomeImg)
    img=ImageQt.ImageQt(Image.fromarray(img))
    self.setPixmap(QtGui.QPixmap.fromImage(img))
    if flagDrawRect:
      self.drawRectangleCC(plane)
    return FlagPlot
    
  #def onTimer(self):
    ''' used to pri.Callback.white the position and the gray level'''
    '''
    newPos=QtGui.QCursor.pos()
    if newPos!=self.oldPos:
      self.oldPos=newPos
      try:
        pu = self.mapFrom(self, newPos)/self.scaleFactor
        f= 0<=pu.x() <self.pixmap().width()
        if not (f and (0<= pu.y() <self.pixmap().height())):
         return
        pri.Callback.white(f'    {pu.x()}')
        j=int(pu.x())
        i=int(pu.y())
        self.outToStatusBarCaller(f'({i},{j}) {self.calib.imgs[self.calib.plane][i,j]}')
      except:
        pri.Callback.white ('Exception in onTimer')
    '''  
  
  def insideImg(self,pu:Punto)->bool:
    ''' checks if a point is inside the image'''  
    f= 0<=pu.x <self.pixmap().width()
    return f and (0<= pu.y <self.pixmap().height())
  
  def contextMenuEvent(self, event):
    # Show the context menu
    if self.contextMenu:
      self.contextMenuPos=event.position()
      self.contextMenu.exec(event.globalPosition().toPoint())  

  def mouseMoveEvent(self, mouseEv):
    ''' mouse move'''
    if self.calib.imgPlot.size==1: return
    try:
      newPos=self.scaleToImg(mouseEv.position())
      if newPos!=self.oldPos:
        self.oldPos=newPos
        pu=Punto(*newPos.toTuple())
        j=int(pu.x)
        i=int(pu.y)
        try:
          #self.outToStatusBarCaller(f'Cam #{self.calib.plane//self.calib.nPlanesPerCam} Plane #{self.calib.plane%self.calib.nPlanesPerCam}: ({i},{j}) {self.calib.imgs[self.calib.plane][i,j]}')
          if self.calib.flagPlotMask:
            self.outToStatusBarCaller(f'(x,y)=({i},{j}), Lev={self.calib.arrayPlot[i,j]:.2f}')
          else:
            self.outToStatusBarCaller(f'(x,y)=({i},{j}), Lev={self.calib.arrayPlot[i,j]:d}')
        except IndexError as exc:
          return  #out of bounds I am not checking but  exit from the function
        if mouseEv.buttons()==QtCore.Qt.MiddleButton and not self.calib.flagPlotMask: # in this case use buttons instead of button !!!!
          self.rectMask= QtCore.QRectF(min (self.puMiddleButton.x(),newPos.x()), min (self.puMiddleButton.y(),newPos.y()),abs(self.puMiddleButton.x()-newPos.x()),abs(self.puMiddleButton.y()-newPos.y()))
          self.update()
          
    except Exception as exc:# pylint: disable=broad-exception-caught
      pri.Error.red(f'Exception in mouseMoveEvent {str(exc)}')# tin qt some exception are non propagated

  def mousePressEvent(self, mouseEv):  
    ''' when mouse pressed'''
    try:
      if mouseEv.button()==QtCore.Qt.RightButton:
        self.contextMenuEvent(mouseEv)  
      elif mouseEv.button()==QtCore.Qt.MiddleButton and not self.calib.flagPlotMask:
        #self.puMiddleButton=self.scaleToImg(mouseEv.position())
        self.puMiddleButton=self.scaleToImg(mouseEv.position())
        self.flagSearchMaskZone=True
        pri.Callback.white('Mouse pressed')
    except Exception as exc:# pylint: disable=broad-exception-caught
      pri.Error.red(f'Exception in mousePressEvent {str(exc)}')# tin qt some exception are non propagated
  
  def paintEvent(self, event):
    ''' called  any time a repaint should be done used here in only to plot moving things on particular the rectangle defining the cc mask'''
    super().paintEvent(event)
    try:
      
      if self.rectMask is None or self.calib.flagPlotMask:
        return
      painter = QtGui.QPainter(self)
      pen = QtGui.QPen()
      pen.setWidth(penWidth)
      pen.setColor(QtGui.QColor(mainInCircleColors[2]))
      painter.setPen(pen)
    
      painter.drawRect(QtCore.QRectF(*self.scaleFromImgIterable(self.rectMask.getRect())))
    except Exception as exc:# pylint: disable=broad-exception-caught
      pri.Error.red(f'Exception in paintEvent {str(exc)}')# tin qt some exception are non propagated
      
  def mouseReleaseEvent(self, mouseEv):
    ''' exception raised in qt functions (slot?) are not propagated:
    # https://stackoverflow.com/questions/45787237/exception-handled-surprisingly-in-pyside-slots
    '''
    try:
      if mouseEv.button()==QtCore.Qt.LeftButton:
        if self.flagGetPoint:
          try:
            pu=Punto(*self.scaleToImg(mouseEv.position()).toTuple())
            if not self.insideImg(pu):
                return
            self.signals.pointFromView.emit(pu)
          except Exception as exc:
            pri.Error.red(str(exc))# the try should be useless but you never know since in qt some exception are non propagated
      elif mouseEv.button()==QtCore.Qt.MiddleButton and not self.calib.flagPlotMask:
        if (self.flagSearchMaskZone):
          self.setMaskZone()
          #todo add the code to revaluate the cc mask
          pri.Callback.white('Middle use Released')
    except Exception as exc:# pylint: disable=broad-exception-caught
      pri.Error.red(f'Exception in mouseReleaseEvent {str(exc)}')# tin qt some exception are non propagated

  #def drawRectangle(self, p,painter,pen):
  def setMaskZone(self):
    data=self.calib.cal.data
    p=self.calib.plane
    
    if (self.rectMask.height()< data.DimWinCC or self.rectMask.width()< data.DimWinCC ):
      raise ValueError('Error the selected window is to small') #from exc 
      
    else:
      
      self.calib.cal.setPuTrovaCC(self.rectMask.getRect(),p)
      if self.calib.flagFindAllPlanes and p==0: #when starting select a mask for all the planes
        for p1 in range(1,self.calib.nPlanes):
          self.calib.cal.setPuTrovaCC(self.rectMask.getRect(),p1)
          self.calib.cal.vect.flagPlane[p1]|= CalFlags.PLANE_NOT_INIT_TROVA_PUNTO|CalFlags.PLANE_NOT_FOUND
      self.calib.changeMask(p)
      self.plotPlane(p)
      
    self.flagSearchMaskZone=False
    self.rectMask=None# maybe is reduntant but we are using his to avoid plotting the rectangle 

  def setCirclePainter(self,canvas,cir): 
    ''' used to speed up drawCircles'''  
    painter = QtGui.QPainter(canvas)
    pen = QtGui.QPen()
    pen.setWidth(penWidth/self.scaleFactor)
    pen.setColor(QtGui.QColor(cir.col))
    painter.setPen(pen)
    if cir.type==CircleType.circle:
      def pCir(X:float, Y:float,r:float):
        painter.drawRoundedRect(X-r, Y-r,2*r,2*r,r,r)
    elif cir.type==CircleType.square:
      def pCir(X:float, Y:float,r:float):
        painter.drawRect(X-r, Y-r,2*r,2*r)
    elif cir.type==CircleType.filledCircle:
      def pCir(X:float, Y:float,r:float):
        painter.drawRoundedRect(X-r, Y-r,2*r,2*r,r,r)
      painter.setBrush(QtGui.QBrush(QtGui.QColor(cir.col)))
    return (painter,pen,pCir)  
  
  def drawArrow(self,painter,l,x1,y1,x,y):
    ''' draw arrow from x1 to x scaled with l''' 
    dx=(x-x1)*l
    dy=(y-y1)*l
    x2=x1+dx
    y2=y1+dy
    painter.drawLine(x1,y1,x2,y2)
    painter.drawLine(x2,y2,x2-dx*percLunFreccia+dy*tanFreccia ,y2-dy*percLunFreccia-dx*tanFreccia)
    painter.drawLine(x2,y2,x2-dx*percLunFreccia-dy*tanFreccia ,y2-dy*percLunFreccia+dx*tanFreccia)
  
  def drawAxis(self, p,painter,pen): 
    ''' draws the axis'''                                   
    calVect=self.calib.cal.vect
    flagDrawCircles=True
    percLine=0.25
    def c1(x1,x2,percLine):
       
       return x1 + (x2 - x1)*percLine
    offSetText=4
    def cLeftText( x1,x2,y1,y2 ): 
      return (c1(x1,x2,percLine if x2>x1 else (1-percLine))+offSetText,c1(y1,y2,percLine if y1>y2 else (1-percLine))-offSetText)
    def c2( x1,x2,y1,y2 ): 
        return (c1(x1,x2,percLine),c1(y1,y2,percLine),c1(x1,x2,1-percLine),c1(y1,y2,1-percLine))
  
    font = QtGui.QFont()
    font.setFamily('Arial')
    font.setPointSize(40)#todo dimesione testo e font
    painter.setFont(font)
    calVect=self.calib.cal.vect

    
    #origin
    ii=self.calib.cal.indFromCoord(0,0,p)
    if calVect.flag[p,ii]==1:
      puOr=Punto(calVect.XOr[p],calVect.YOr[p])
      ind=0
      #puOr=Punto(out.X[p,ii], out.Y[p,ii])
      #for pp in range (0,self.calib.cal.data.Numpiani):        pri.General.green(out.X[pp,ii], out.Y[pp,ii])
      #pri.General.green(f'Or=({out.X[p,iOr]}, {out.Y[p,iOr]})   x=({out.X[p,ii]}, {out.Y[p,ii]})  y=({out.X[p,iOr+1]}, {out.Y[p,iOr+1]})')


      if flagDrawCircles:
        r=rInpCircle
        def pCir(X:float, Y:float,r:float):
          painter.drawRoundedRect(X-r, Y-r,2*r,2*r,r,r)
          #pri.General.green(X,Y)
        pen.setColor(QtGui.QColor(mainInCircleColors[ind]))
        painter.setPen(pen)
        pCir(puOr.x,puOr.y,r)
    # y axis 
    ind=2
    ii=self.calib.cal.indFromCoord(1,0,p)
    if calVect.flag[p,ii]==1:
      pu=Punto(calVect.X[p,ii], calVect.Y[p,ii])
      pen.setColor(QtGui.QColor(mainInCircleColors[ind]))
      painter.setPen(pen)
      self.drawArrow(painter,1,*c2( puOr.x ,pu.x ,puOr.y ,pu.y ))
      painter.drawText(*cLeftText( puOr.x ,pu.x ,puOr.y ,pu.y ),'Y')
      
      if flagDrawCircles:
        pCir(pu.x,pu.y,r)
    #asse x
    ind=1
    ii=self.calib.cal.indFromCoord(0,1,p)
    if calVect.flag[p,ii]==1:
      pu=Punto(calVect.X[p,ii], calVect.Y[p,ii])
      pen.setColor(QtGui.QColor(mainInCircleColors[ind]))
      painter.setPen(pen)
      
      painter.drawText(*cLeftText( puOr.x ,pu.x ,puOr.y ,pu.y ),'X')
      self.drawArrow(painter,1,*c2( puOr.x ,pu.x ,puOr.y ,pu.y ))
      if flagDrawCircles:
        pCir(pu.x,pu.y,r)
    # origin shift
    if (calVect.xOrShift[p] != 0 or  calVect.yOrShift[p] != 0):#plot origin
      ii=self.calib.cal.indFromCoord( int(calVect.yOrShift[p]), int(calVect.xOrShift[p]),p)
      if calVect.flag[p,ii]==1:
        
        pu=Punto(calVect.X[p,ii], calVect.Y[p,ii])
        pen.setColor(QtGui.QColor(OriginCircleColor))
        painter.setPen(pen)
        r=2*rInpCircle
        pCir(pu.x,pu.y,r)
        r=rInpCircle
        pCir(pu.x,pu.y,r)
  def drawRectangleCC(self, p):
    rect=QtCore.QRectF(*self.calib.cal.getPuTrovaCC(p))
    if rect.height()!=0:
      cir=Circle.fromPunto(Punto(0,0))
      canvas = self.pixmap()
      (painter,pen,pCir)=self.setCirclePainter(canvas,cir)
      pen.setColor(QtGui.QColor(mainInCircleColors[2]))
      painter.setPen(pen)
      painter.drawRect(rect)
      painter.end()
      self.setPixmap(canvas)
    
  ''' draw circles of the same type and color'''           
  def drawCircles(self, p,):
    ''' draw circles of the same type and color and the axis with the main points'''    
    rect=QtCore.QRectF(*self.calib.cal.getPuTrovaCC(p))
    if self.flagGetPoint:
      for i in range(self.calib.flagRicerca):
        #i=self.calib.flagRicerca-1
        if self.calib.flagFoundPoints[i]:
          pu=self.calib.foundPoints[i]
          self.drawSingleCircleFromCalib(pu,0,i) # draws a circle on the detected points
          self.drawSingleCircleFromCalib(pu,1,0) # draws a circle on the detected points
          
      
    if self.calib.tryFindPlane(p) and rect.height()==0:
      return # Cosa si deve fare? Forse va bene così in fondo non è stato possibile trovare il piano
    calVect=self.calib.cal.vect
    cir=Circle.fromPunto(Punto(0,0))
    canvas = self.pixmap()
    (painter,pen,pCir)=self.setCirclePainter(canvas,cir)
    if not self.calib.tryFindPlane(p):
      r=cir.r#/self.scaleFactor
      #try:
      indOk=np.nonzero(calVect.flag[p]==1)[0]
      for i in indOk:
        pCir(calVect.X[p,i], calVect.Y[p,i],r)
      if self.calib.cal.flagCalibrated:    
        data=self.calib.cal.data
        for i in indOk:
          self.drawArrow(painter,lunFreccia,calVect.X[p,i], calVect.Y[p,i],calVect.Xc[p,i]-data.ColPart, calVect.Yc[p,i]-data.RigaPart)
        if p==data.kMax:
          pen.setColor(QtGui.QColor(maxErrorCircleColor))
          painter.setPen(pen)
          r=rInpCircle
          painter.drawRect(calVect.X[p,self.calib.cal.data.jMax]-r,calVect.Y[p,self.calib.cal.data.jMax]-r,2*r,2*r)
          r*=2
          painter.drawRoundedRect(calVect.X[p,self.calib.cal.data.jMax]-r,calVect.Y[p,self.calib.cal.data.jMax]-r,2*r,2*r,r,r)
      self.drawAxis(p,painter,pen)      
    
    
    if rect.height()!=0:
      pen.setColor(QtGui.QColor(mainInCircleColors[2]))
      painter.setPen(pen)
      painter.drawRect(rect)
    
    #except:        pri.Callback.white('u')
    painter.end()
    self.setPixmap(canvas)
  
  def drawSingleCircle(self, cir):
    ''' draws a single circle '''
    #pri.Callback.white(cir)
    canvas = self.pixmap()
    (painter,_,pCir)=self.setCirclePainter(canvas,cir)
    r=cir.r#/self.scaleFactor
    pCir(cir.x, cir.y,r)
    painter.end()
    self.setPixmap(canvas)      
        
  def scaleToImg(self,point):
    ''' from mouse position to image '''    
    #widgetPos = self.mapFrom(self, pos)# not needed any more since we are now plotting directly in the QLabel
    #return Punto(widgetPos.x()/self.scaleFactor,widgetPos.y()/self.scaleFactor)
    return point/self.scaleFactor
  def scaleFromImg(self,point):
    ''' from image to view  '''    
    return point*self.scaleFactor
  def scaleFromImgIterable(self,li):
    ''' from image to view  '''    
    return [d*self.scaleFactor for d in li]
    
  """
  def wheelEvent(self,event):
    if event.angleDelta().y()/120>0:
      self.plotPlane(self.calib.plane+1)
    else:
      self.plotPlane(self.calib.plane-1)
  """

  def spinImgChanged(self,plane):
    ''' plot image of plane=plane'''
    self.plotPlane(plane)

  def spinOriginChanged(self,Off:int,spin:QSpinBox,flagX:bool):
    ''' offset Origin '''
    p=self.calib.plane
    calVect=self.calib.cal.vect
    ma=calVect.W[p] / 2 if flagX else calVect.H[p] / 2
    if not  -ma<Off<ma:  # if inside
      Off=int(-ma if Off < -ma else ma if Off > ma else Off)
      spin.setValue(Off)
    if flagX:
      calVect.xOrShift[p]=Off
    else:
      calVect.yOrShift[p]=Off
    self.plotPlane(self.calib.plane)
  
  def copyRemPoints(self):
    p=self.calib.plane
    calVect=self.calib.cal.vect
    
    for pp in range(self.calib.nPlanes):
      if pp is p : 
        continue
      self.calib.cal.data.piano=pp
      
      calVect.remPointsRi[pp]=calVect.remPointsRi[p]
      calVect.remPointsLe[pp]=calVect.remPointsLe[p]
      calVect.remPointsUp[pp]=calVect.remPointsUp[p]
      calVect.remPointsDo[pp]=calVect.remPointsDo[p]
      self.calib.cal.removeBulk()
    self.calib.cal.data.piano=p
  def spinRemPoints(self,Off:int,spin:QSpinBox,flagX:bool,flagPos:bool):
    ''' Remove points '''
    p=self.calib.plane
    p=self.calib.cal.data.piano=p
    calVect=self.calib.cal.vect
    ma=calVect.W[p] / 2 if flagX else calVect.H[p] / 2
    if not  -ma<Off<ma:  # if inside
      Off=int(-ma if Off < -ma else ma if Off > ma else Off)
      spin.setValue(Off)
    if flagX:
      if flagPos:
        calVect.remPointsRi[p]=Off
      else:
        calVect.remPointsLe[p]=Off
    else:
      if flagPos:
        calVect.remPointsUp[p]=Off
      else:
        calVect.remPointsDo[p]=Off
    self.calib.cal.removeBulk()
    self.plotPlane(self.calib.plane)
  

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    sys.exit(app.exec())
    