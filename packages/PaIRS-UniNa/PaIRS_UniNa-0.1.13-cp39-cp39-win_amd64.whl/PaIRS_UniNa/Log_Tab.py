from .ui_Log_Tab import*
from .TabTools import*
from .procTools import dataTreePar
from .__init__ import __version__,__year__

class Log_Tab(gPaIRS_Tab):
    class Log_Tab_Signals(gPaIRS_Tab.Tab_Signals):
        pass

    def __init__(self,*args):
        parent=None
        flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: flagInit=args[1]
        super().__init__(parent,Ui_LogTab)
        self.signals=self.Log_Tab_Signals(self)

        #------------------------------------- Graphical interface: widgets
        self.setLogFont(fontPixelSize-dfontLog)
             
        #------------------------------------- Initializing  
        if flagInit:   
            self.initialize()

    def initialize(self):
        self.logClear()
        self.logWrite(self.logHeader('Welcome to PaIRS!\nEnjoy it!\n\n'))

    def setLogFont(self,fPixSize):
        self.ui: Ui_LogTab   
        logfont=self.font()
        logfont.setFamily('Courier New')
        logfont.setPixelSize(fPixSize)
        self.ui.log.setFont(logfont)

    def logHeader(self,message):
        header=PaIRS_Header+message
        return header
    
    def logWrite(self, text):
        cursor = self.ui.log.textCursor() 
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.log.setTextCursor(cursor)
        self.ui.log.ensureCursorVisible()
        

    def logClear(self):
        self.ui.log.setText('')

    def moveToTop(self):
        self.ui.log.verticalScrollBar().setValue(self.ui.log.verticalScrollBar().minimum())

    def moveToBottom(self):
        self.ui.log.verticalScrollBar().setValue(self.ui.log.verticalScrollBar().maximum())


if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Log_Tab(None)
    object.show()
    app.exec()
    app.quit()
    app=None
