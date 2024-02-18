from .PaIRS_pypacks import *
from .ui_Tree_Tab import*
from .TabTools import*
from .procTools import dataTreePar

class TREpar(TABpar):
    def __init__(self):
        self.setup()
        super().__init__()
        self.name='TREpar'
        self.surname='QUEUE_Tab'
        self.unchecked_fields+=self.fields

    def setup(self):
        self.indTree = 0
        #these lists are called queues
        self.past = []
        self.current = []
        self.future = []
class Tree_Tab(gPaIRS_Tab):

    class Tree_Tab_Signals(gPaIRS_Tab.Tab_Signals):
        selection=Signal(int,int,QTreeWidgetItem,int)
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self,*args):
        parent=None
        flagInit=True
        if len(args): parent=args[0]
        if len(args)>1: flagInit=args[1]
        super().__init__(parent,Ui_TreeTab,dataTreePar)
        self.signals=self.Tree_Tab_Signals(self)

       #------------------------------------- Graphical interface: widgets
        self.ui: Ui_TreeTab
        ui=self.ui
        #tree are the real widgets, queues are the lists of their items
        ui.tree_past.clear()
        ui.tree_current.clear()
        ui.tree_future.clear()

        self.setupWid()  #---------------- IMPORTANT
        
        #------------------------------------- Graphical interface: miscellanea
        self.Tree_icons=TREico()

        self.icon_add=QIcon()
        self.icon_add.addFile(u""+ icons_path +"add.png", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_run_piv=QIcon()
        self.icon_run_piv.addFile(u""+ icons_path +"run_piv.png", QSize(), QIcon.Normal, QIcon.Off)

        self.icon_delete= QIcon()
        self.icon_delete.addFile(u""+ icons_path +"delete.png", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_fast_delete= QIcon()
        self.icon_fast_delete.addFile(u""+ icons_path +"fast_delete.png", QSize(), QIcon.Normal, QIcon.Off)

        self.itemSize=self.ui.tree_current.size()-QSize(0,4)
        self.TreeNames=['tree_past','tree_current','tree_future']  
        self.QueueNames=['past','current','future']
        
        #------------------------------------- Declaration of parameters 
        self.TREpar=TREpar()
        self.TREpar_base=TREpar()

        self.TREselect_fun=lambda iTold,iT,t,i,c: None
        self.addNewItem2Prevs=lambda iT,iIt: None
        self.addExistingItem2Prevs=lambda iTold,iItold,iT,iIt: None
        self.removeItemFromPrevs=lambda iT,iIt: None
        self.moveupdownPrevs=lambda iT,iIt,d: None
        
        #------------------------------------- Callbacks 
        self.setupCallbacks()
        self.FlagNoWrapper=True

        #------------------------------------- Initializing 
        #for c in self.findChildren(QPushButton)+self.findChildren(QToolButton):
        #    if c in (self.ui.button_min,self.ui.button_PIV,self.ui.button_import_past): continue
        #    c.hide()
            
        if flagInit:
            self.initialize()
            
    def initialize(self):
        self.clearAllTimes()
        self.addNewItem2TreeQueue(0,"current",QIcon())
        self.setExample()
        self.checkButtons()

    def setupCallbacks(self):
        ui=self.ui
        ui.tree_past.itemClicked.connect(lambda i,c: self.addParWrapper(self.selectItem(ui.tree_past,i,c),'Past tree selection'))
        ui.tree_current.itemClicked.connect(lambda i,c: self.addParWrapper(self.selectItem(ui.tree_current,i,c),'Current tree selection'))
        ui.tree_future.itemClicked.connect(lambda i,c: self.addParWrapper(self.selectItem(ui.tree_future,i,c),'Future tree selection'))

        ui.button_delete_future_callback=ui.button_delete_past_callback=self.addParWrapper(self.removeFromCurrentTree,'Button delete')
        ui.button_delete_past.clicked.connect(ui.button_delete_past_callback)
        ui.button_delete_future.clicked.connect(ui.button_delete_future_callback)
        self.setFastDelete(False)

        ui.button_restore_callback=self.addParWrapper(self.restoreItemFromTree,'Button restore')
        ui.button_restore.clicked.connect(ui.button_restore_callback)

        ui.button_clean_past_callback=self.addParWrapper(lambda: self.cleanTreeQueue(-1),'Button clean')
        ui.button_clean_past.clicked.connect(ui.button_clean_past_callback)
        ui.button_clean_future_callback=self.addParWrapper(lambda: self.cleanTreeQueue(+1),'Button clean')
        ui.button_clean_future.clicked.connect(ui.button_clean_future_callback)
        ui.button_clean_past.setVisible(True)
        ui.button_clean_future.setVisible(True)

        ui.tree_past.addfuncshift_pressed['func']=self.addParWrapper(lambda: self.setFastDelete(True),'Tree: input from keyboard')
        ui.tree_past.addfuncshift_released['func']=self.addParWrapper(lambda: self.setFastDelete(False),'Tree: input from keyboard')
       
        ui.tree_past.addfuncout['func']=self.addParWrapper(lambda: self.setFastDelete(False),'Tree: input from keyboard')
        ui.tree_past.addfuncin['func']=self.addParWrapper(lambda: self.setFastDelete_FocusIn(),'Tree: input from keyboard')

        #ui.tree_past.addfuncdel_pressed['func']=self.addParWrapper(lambda: self.removeFromCurrentTree(),'Tree: input from keyboard')
        #ui.tree_past.addfunckey_pressed['func']=lambda k: self.addParWrapper(self.keyCallbacks(k),'Tree: input from keyboard')
        #ui.tree_future.addfuncdel_pressed['func']=self.addParWrapper(lambda: self.removeFromCurrentTree(),'Tree: input from keyboard')
        #ui.tree_future.addfunckey_pressed['func']=lambda k: self.addParWrapper(self.keyCallbacks(k),'Tree: input from keyboard')

        ui.tree_past.addfuncarrows_pressed['func']=lambda k: self.addParWrapper(self.movingAcrossTrees(k),'Tree: input from keyboard')
        ui.tree_current.addfuncarrows_pressed['func']=lambda k: self.addParWrapper(self.movingAcrossTrees(k),'Tree: input from keyboard')
        ui.tree_future.addfuncarrows_pressed['func']=lambda k: self.addParWrapper(self.movingAcrossTrees(k),'Tree: input from keyboard')   
        
        ui.button_up_past_callback=self.addParWrapper(lambda: self.moveupdown(-1),'Move past item up')
        ui.button_down_past_callback=self.addParWrapper(lambda: self.moveupdown(+1),'Move past item down')
        ui.button_up_future_callback=self.addParWrapper(lambda: self.moveupdown(-1),'Move future item up')
        ui.button_down_future_callback=self.addParWrapper(lambda: self.moveupdown(+1),'Move future item down')
        ui.button_up_past.clicked.connect(ui.button_up_past_callback)
        ui.button_down_past.clicked.connect(ui.button_down_past_callback)
        ui.button_up_future.clicked.connect(ui.button_up_future_callback)
        ui.button_down_future.clicked.connect(ui.button_down_future_callback)

        ui.tree_past.contextMenuEvent=lambda e: self.treeContextMenuEvent(ui.tree_past,e)
        ui.tree_current.contextMenuEvent=lambda e: self.treeContextMenuEvent(ui.tree_current,e)
        ui.tree_future.contextMenuEvent=lambda e: self.treeContextMenuEvent(ui.tree_future,e)

    def treeContextMenuEvent(self, tree:myQTreeWidget, event):
        item=tree.currentItem()
        if not item: return
        self.selectItem(tree,item,0)
        menu=QMenu(tree)
        buttons_in_past=['up_past','down_past',
                        -1,'import_past',
                        -1,'restore','delete_past','clean_past',
                        -1,'min','PIV']
        buttons_in_current=['min','PIV']
        buttons_in_future=['up_future','down_future',
                            -1,'edit_item',
                            -1,'delete_future','clean_future',
                            -1,'min','PIV']
        buttons=[buttons_in_past,buttons_in_current,buttons_in_future]
        name=[]
        act=[]
        fun=[]
        for k,nb in enumerate(buttons[self.TREpar.indTree+1]):
            if type(nb)==str:
                b:QPushButton=getattr(self.ui,'button_'+nb)
                if b.isVisible() and b.isEnabled():
                    if hasattr(self.ui,'button_'+nb+'_callback'):
                        name.append(nb)
                        act.append(QAction(b.icon(),toPlainText(b.toolTip().split('.')[0]),tree))
                        menu.addAction(act[-1])
                        callback=getattr(self.ui,'button_'+nb+'_callback')
                        fun.append(callback)
            else:
                if len(act): menu.addSeparator()

        if len(act):
            pri.Callback.yellow(f'||| Opening {self.QueueNames[self.TREpar.indTree]} tree item context menu |||')
            action = menu.exec_(tree.mapToGlobal(event.pos()))
            flag=False
            for nb,a,f in zip(name,act,fun):
                if a==action: 
                    if nb=='edit_item': 
                        self.ui.button_edit_item.setChecked(not self.ui.button_edit_item.isChecked())
                    f()
                    flag=True
            if not flag: 
                self.focusOnTree(tree)
        else:
            toolTip=item.toolTip(0)
            item.setToolTip(0,'')

            message='No context menu available! Please, pause processing.'
            tip=QToolTip(self)
            toolTipDuration=self.toolTipDuration()
            self.setToolTipDuration(3000)
            tip.showText(QCursor.pos(),message)
            self.setToolTipDuration(toolTipDuration)

            item.setToolTip(0,toolTip)

#*************************************************** Selection
    def pickTree(self,ind_name):
        if type(ind_name)==str: name=ind_name
        else: name=self.QueueNames[ind_name+1]
        tree=getattr(self.ui,'tree_'+name)
        queue=getattr(self.TREpar,name)
        return tree, queue

    def selectTree(self,ind_name,*args):
        tree,queue=self.pickTree(ind_name)
        l=len(queue)
        if not l: return
        if len(args): 
            indItem=min([args[0],l-1])                
        else: indItem=-1
        tree: QTreeWidget
        self.selectItem(tree,queue[indItem],0)
            
    def selectPast(self,*args):
        self.selectTree(-1,*args)

    def selectCurrent(self,*args):
        self.selectTree(0,*args)

    def selectFuture(self,*args):
        self.selectTree(1,*args)
    
    def selectItem(self,tree,item,column):
        #args[0]=queue_prev
        indTree_old=self.TREpar.indTree
        self.focusOnTree(tree)
        tree.setCurrentItem(item)
        self.checkButtons()

    def focusOnTree(self,tree):
        if type(tree)==int: #tree=-1,0,1
            indTree=tree
        elif type(tree)==str: #tree='past','current','future'
            indTree=self.TreeNames.index(tree)
        else:
            indTree=self.TreeNames.index(tree.objectName())
        for it,tname in enumerate(self.TreeNames):
            t=getattr(self.ui,tname)
            if it==indTree: 
                t.setFocus()
            else: 
                t.setCurrentItem(QTreeWidgetItem())
        self.TREpar.indTree=indTree-1
        
    def checkButtons(self):
        _,queue=self.pickTree(self.TREpar.indTree)
        if len(queue): 
            self.setButtons()
        else:
            self.selectCurrent()  #comes back to checkButtons recursively

    def setButtons(self,FlagRun=False):
        tree: QTreeWidget
        indTree=self.TREpar.indTree
        tree,queue=self.pickTree(indTree)
        indItem=tree.indexOfTopLevelItem(tree.currentItem())
        isItemFirst=indItem==0
        isItemLast=indItem==len(queue)-1
        
        Flag=indTree==-1
        self.ui.button_down_past.setEnabled(Flag and not isItemLast)
        self.ui.button_up_past.setEnabled(Flag and not isItemFirst)
        self.ui.button_restore.setEnabled(Flag)
        self.ui.button_delete_past.setEnabled(Flag)
        self.ui.button_clean_past.setEnabled(len(self.TREpar.past)>0)
        
        Flag=indTree==1 and not FlagRun
        self.ui.button_down_future.setEnabled(Flag and not isItemLast)
        self.ui.button_up_future.setEnabled(Flag and not isItemFirst)
        self.ui.button_edit_item.setEnabled(Flag)
        self.ui.button_delete_future.setEnabled(Flag)
        self.ui.button_clean_future.setEnabled(not FlagRun and len(self.TREpar.future)>0)
    
    def hideButtons(self):
        self.TREpar.indTree=-2
        self.checkButtons()

    def moveupdown(self,d):
        tree: QTreeWidget
        queue: list
        indTree=self.TREpar.indTree
        tree,queue=self.pickTree(indTree)
        indItem=tree.indexOfTopLevelItem(tree.currentItem())
        item=queue[indItem]
        tree.takeTopLevelItem(indItem)
        tree.insertTopLevelItem(indItem+d,item)
        queue.insert(indItem+d,queue.pop(indItem))
        #del queue[indItem]
        #queue.insert(indItem+d,item)
        for k in range(min([indItem+d,indItem]),len(queue)):
            i=queue[k]
            i.data(0,Qt.UserRole).indItem=k
        tree.setCurrentItem(item)
        self.checkButtons()
        self.moveupdownPrevs(indTree,indItem,d)
        
    
#*************************************************** Addition
    def createItemInTree(self,tree,queue,name,idata,icon):
        currentItem=QTreeWidgetItem(tree)
        currentItem.setText(0,name)
        currentItem.setData(0,Qt.UserRole,idata)
        currentItem.setSizeHint(0,self.itemSize)
        currentItem.setIcon(0,icon)
        currentItem.setToolTip(0,name)
        currentItem.setStatusTip(0,name)
        tree.addTopLevelItem(currentItem)
        tree.setCurrentItem(currentItem)
        queue.append(currentItem)
        return currentItem

    def addNewItem2TreeQueue(self,indTree,name,icon,*args):
        if not len(args):
            flagSelection=True
        else:
            flagSelection=args[0]
        tree,queue=self.pickTree(indTree)
        if not flagSelection: ci=tree.currentItem()
        idata=TABpar(name,'QUEUE_Tab')
        idata.ind=0
        idata.indTree=indTree
        idata.indItem=indItem_new=len(queue)
        currentItem=self.createItemInTree(tree,queue,name,idata,icon)
        self.addNewItem2Prevs(indTree,indItem_new)
        if flagSelection:
            self.selectItem(tree,currentItem,0)
        else:
            tree.setCurrentItem(ci)

    def addExisitngItem2TreeQueue(self,indTree,name,idata,icon,*args):
        if not len(args):
            flagSelection=True
        else:
            flagSelection=args[0]
        tree,queue=self.pickTree(indTree)
        if not flagSelection: ci=tree.currentItem()
        indTree_old=idata.indTree
        indItem_old=idata.indItem
        idata.indTree=indTree
        idata.indItem=indItem_new=len(queue)
        currentItem=self.createItemInTree(tree,queue,name,idata,icon)
        self.addExistingItem2Prevs(indTree_old,indItem_old,indTree,indItem_new)
        if flagSelection:
            self.selectItem(tree,currentItem,0)
        else:
            tree.setCurrentItem(ci)

#*************************************************** Removal
    def removeFromCurrentTree(self,*args):
        if not len(args):
            flagSelection=True
        else:
            flagSelection=args[0]
        if len(args)<=1:
            indTree=self.TREpar.indTree
            tree,queue=self.pickTree(indTree)
            if tree==None: return
            tree: QTreeWidget
            i=tree.currentItem()
        else:
            i=args[1]
            idata=i.data(0,Qt.UserRole)
            indTree=idata.indTree
            tree,queue=self.pickTree(indTree)
            if tree==None: return
        if tree==self.ui.tree_current: return
        if indTree==-1 and not self.FlagFastDelete:
            WarningMessage="Are you sure you want to permanently delete this item?\n"+\
            "(Once deleted from the past queue, you will not be able to recover the related process.)"
            flag=questionDialog(self,WarningMessage)
        else:
            flag=True
        if indTree==1:
            icon=self.Tree_icons.cancelled
            self.addExisitngItem2TreeQueue(-1,i.text(0),i.data(0,Qt.UserRole),icon,False)
        if flag:
            self.removeItem(i,indTree,tree,queue,flagSelection)

    def removeItem(self,i,indTree,tree: QTreeWidget,queue,*args):
        if not len(args):
            flagSelection=True
        else:
            flagSelection=args[0]
        if not flagSelection: ci=tree.currentItem()
        indItem=tree.indexOfTopLevelItem(i)        
        tree.removeItemWidget(i, 0)
        tree.takeTopLevelItem(indItem)
        queue.pop(indItem)
        for k in range(indItem,len(queue)):
            queue[k].data(0,Qt.UserRole).indItem=k
        self.removeItemFromPrevs(indTree,indItem)
        if flagSelection:
            if len(queue): 
                if indItem:
                    self.selectItem(tree,queue[indItem-1],0)
                else:
                    self.selectItem(tree,queue[indItem],0)
                tree.setFocus()
            else:
                self.selectCurrent()  #move to current!
        else:
            tree.setCurrentItem(ci)

    def setFastDelete(self,flag):
        self.FlagFastDelete=flag
        if self.TREpar.indTree==0: return
        elif self.TREpar.indTree==-1: b=self.ui.button_delete_past
        elif self.TREpar.indTree==+1: b=self.ui.button_delete_future
        if self.FlagFastDelete:
            b.setIcon(self.icon_fast_delete)
            tip='Delete process (Delete/Backspace). Release Shift key for warning upon deletion'
        else:
            b.setIcon(self.icon_delete)
            tip='Delete process (Delete/Backspace). Press Shift key for avoiding warning upon deletion'
        b.setToolTip(tip)
        b.setStatusTip(tip)
        if b.underMouse():
            QtWidgets.QToolTip.showText(QCursor.pos(),tip,b)

    def setFastDelete_FocusIn(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        flag=modifiers == QtCore.Qt.ShiftModifier
        self.setFastDelete(flag)

#*************************************************** Removal
    def restoreItemFromTree(self):
        indTree=self.TREpar.indTree
        tree,queue=self.pickTree(self.TREpar.indTree)
        if tree==None: return
        tree: QTreeWidget
        i=tree.currentItem()
        icon=self.Tree_icons.waiting
        self.addExisitngItem2TreeQueue(+1,i.text(0),i.data(0,Qt.UserRole),icon,False)
        self.removeItem(i,indTree,tree,queue,False)
        self.selectFuture(len(self.TREpar.future))

#*************************************************** Cleaning
    def cleanTreeQueue(self,*args):
        if len(args): indTree=args[0]
        else: indTree=self.TREpar.indTree
        if indTree==-1: name='past'
        elif indTree==+1: name='future'
        WarningMessage=f"Are you sure you want to permanently clean the {name} queue?\n"+\
        f"(Once cleaned off, you will not be able to recover the processes of the queue.)"

        if questionDialog(self,WarningMessage):
            self.clearTenses([name])
            self.checkButtons()

    def clearTenses(self,tenses):
        for name in tenses:
            self.emptyTree(name)

    def clearPastFuture(self):
        self.clearTenses(['past','future'])

    def clearAllTimes(self):
        self.clearTenses(['past','current','future'])

    def emptyTree(self,name):
        t,q=self.pickTree(name)
        indTree=self.QueueNames.index(name)-1
        for _ in range(len(q)): 
            self.removeItem(q[0],indTree,t,q,False)

#*************************************************** Keyboard inputs
    def movingAcrossTrees(self,key):
        Flag=True
        if self.TREpar.indTree==0:
            i=self.ui.tree_current.currentItem()
            k=self.ui.tree_current.indexOfTopLevelItem(i)
            if k==0 and key == QtCore.Qt.Key_Up: 
                self.selectPast(-1)
                Flag=False
            elif k+1==len(self.TREpar.current) and key == QtCore.Qt.Key_Down:
                self.selectFuture(0)
                Flag=False
            else:
                if key == QtCore.Qt.Key_Up: d=-1
                elif key == QtCore.Qt.Key_Down: d=+1
                self.selectCurrent(k+d)
        elif self.TREpar.indTree==-1:
            i=self.ui.tree_past.currentItem()
            k=self.ui.tree_past.indexOfTopLevelItem(i)
            if k+1==len(self.TREpar.past) and key == QtCore.Qt.Key_Down:
                self.selectCurrent(0)
                Flag=False
            else:
                if key == QtCore.Qt.Key_Up and k>0: d=-1
                elif key == QtCore.Qt.Key_Down: d=+1
                else: d=0
                if d: self.selectPast(k+d)
        elif self.TREpar.indTree==+1:
            i=self.ui.tree_future.currentItem()
            k=self.ui.tree_future.indexOfTopLevelItem(i)
            if k==0 and key == QtCore.Qt.Key_Up:
                self.selectCurrent(-1)
                Flag=False
            else:
                if key == QtCore.Qt.Key_Up: d=-1
                elif key == QtCore.Qt.Key_Down and k<len(self.TREpar.future): d=+1
                else: d=0
                if d: self.selectFuture(k+d)
        return Flag

    def keyCallbacks(self,key):
        if self.TREpar.indTree==-1:
            if key == QtCore.Qt.Key_C:
                self.cleanTreeQueue()
            elif key == QtCore.Qt.Key_R:
                self.restoreItemFromTree()
        elif self.TREpar.indTree==+1:
            if key == QtCore.Qt.Key_C:
                self.cleanTreeQueue()
            if key == QtCore.Qt.Key_D and Flag_DEBUG:
                tree,_,_=self.pickTree(self.TREpar.indTree)
                i=tree.currentItem()
                i.data(0,Qt.UserRole).flagRun=-1
                self.removeFromCurrentTree()
        return

#*************************************************** Example
    def setExample(self):
        name="first #1"+"a"*30
        self.addNewItem2TreeQueue(-1,name,self.Tree_icons.done)
        self.addNewItem2TreeQueue(-1,"second",self.Tree_icons.cancelled)
        self.addNewItem2TreeQueue(-1,"thrid",self.Tree_icons.trash)

        name="Minimum #1"+"b"*30
        self.addNewItem2TreeQueue(1,name,self.Tree_icons.running)
        self.addNewItem2TreeQueue(1,"PIV process #1", self.Tree_icons.waiting)
        self.addNewItem2TreeQueue(1,"PIV process #2",self.Tree_icons.issue)


if __name__ == "__main__":
    import sys
    app=QApplication.instance()
    if not app:app = QApplication(sys.argv)
    app.setStyle('Fusion')
    object = Tree_Tab()
    object.show()
    app.exec()
    app.quit()
    app=None
