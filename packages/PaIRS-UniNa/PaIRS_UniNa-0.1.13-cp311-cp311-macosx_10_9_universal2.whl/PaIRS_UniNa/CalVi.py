from .gCalVi import *

def run():
    gui:gCalVi
    app,gui,flagPrint=launchCalVi()
    quitCalVi(app,flagPrint)

def cleanRun():
    if os.path.exists(lastcfgname_CalVi):
        os.remove(lastcfgname_CalVi)
    run()
   
def debugRun():
    gui:gCalVi
    app,gui,flagPrint=launchCalVi(flagInputDebug=True)
    quitCalVi(app,flagPrint)


