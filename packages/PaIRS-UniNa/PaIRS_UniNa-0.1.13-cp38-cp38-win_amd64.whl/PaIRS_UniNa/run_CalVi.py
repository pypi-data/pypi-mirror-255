if __package__ or "." in __name__:
    from PaIRS_UniNa import CalVi
else:
    import CalVi

FlagRun=0

if __name__ == "__main__":
    if FlagRun==0:
        CalVi.run()
    elif FlagRun==1:
        CalVi.cleanRun()
    elif FlagRun==2:
        CalVi.debugRun()
