from .PaIRS_pypacks import*

#Ncont=500

class patternInfoList:
    def __init__(self):
        self.pattern= []
        self.ext= []
        self.root= []
        self.pa= []
        self.n= []
        self.ndig= []
        self.nab= []
        self.nimg= []
        self.nimg_tot= []
        self.ind_in= []
        self.ind_fin= []
        self.fra= []
        self.nfra= []

    def addto(self,S):
        for field, f in S.__dict__.items():
            s_value=getattr(self,field)
            if type(s_value)==list: 
                for x in s_value:
                    f.append(x)
            else: 
                f.append(s_value)
        return S

    def copyto(self,S):
        for field, value in self.__dict__.items():
            setattr(S,field,value)
        return S
    
    def duplicate(self):
        S=patternInfoList()
        for field, value in self.__dict__.items():
            setattr(S,field,value)
        return S

    def delfromList(self,ind_del):
        for k in range(len(ind_del)-1,-1,-1):
            for _,f in self.__dict__.items():
                del f[ind_del[k]]

    def extractPinfo(self,k):
        S=patternInfoList()
        for field, value in self.__dict__.items():
            setattr(S,field,value[k])
        return S
    
    def isDifferentFrom(self,v,exceptions,*args):
        Flag=False
        for f, _  in self.__dict__.items():
            if f in exceptions: continue
            a=getattr(self,f)
            b=getattr(v,f)
            if a!=b:
                Flag=True
                break
        return Flag

class patternInfoVar(patternInfoList):
    def __init__(self):
        super().__init__()
        for field, f in self.__dict__.items():
            if field in ('pattern','ext','root',):
                setattr(self,field,'')
            elif field == 'pa':
                setattr(self,field,[[]])
            else:   
                setattr(self,field,0)
        self.target=''
        self.split_target=''
        self.jdig=''
        self.nab=0

#*************************************************** Analyse Path
def analysePath(path,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    path=myStandardRoot(path) #maybe useless
    Pinfo=patternInfoList()
    myNone=patternInfoVar()

    """
    cont=0
    while not FlagStop[0] and cont<Ncont:
        timesleep(.01)
        cont+=1
    """
    files=findFiles_sorted(path+"*.*") # needed to use the recompiled reg expressions
    if FlagStop[0]: return myNone
    icont=-1
    for file in files:
        icont+=1
        flag_done=False
        basename=os.path.basename(file)
        if len(Pinfo.pa): # this check is done before the ext check since it is faster?!
            Pinfo,flag_done=checkPinfo(basename,Pinfo,flag_done,FlagStop)
        if not flag_done:
            if FlagStop[0]: return myNone
            if any(file.endswith(ex) for ex in supported_exts):
                target, ext=os.path.splitext(os.path.basename(file))
                Pinfo_file=getPatternInfo(target, ext, FlagStop)
                if FlagStop[0]: return myNone
                if len(Pinfo_file.pa): 
                    for ii in range(icont):
                        file_prev=files[ii]
                        basename=os.path.basename(file_prev)
                        Pinfo_file,flag_done=checkPinfo(basename,Pinfo_file,flag_done,FlagStop)
                    Pinfo=Pinfo_file.addto(Pinfo)
    if len(Pinfo.pa): # needed in any case
        ind_del=[]  # delete all patterns corresponding to single images
        for k in range(0,len(Pinfo.nimg_tot)):
            if FlagStop[0]: return myNone
            Pinfo.nimg[k]=Pinfo.ind_fin[k]-Pinfo.ind_in[k]+1
            if (Pinfo.nimg_tot[k]<2 and len(Pinfo.fra[k])<2) or len(Pinfo.fra[k])==1:
                ind_del.append(k)
        if FlagStop[0]: return myNone
        Pinfo.delfromList(ind_del)
    for j in range(len(Pinfo.fra)):
        if FlagStop[0]: return myNone
        if len(Pinfo.fra[j])>1:
            Pinfo.nfra[j]=len(Pinfo.fra[j])
            root=[]
            for k in range(len(Pinfo.fra[j])):
                if FlagStop[0]: return myNone
                root.append(Pinfo.root[j].replace('@',Pinfo.fra[j][k]))
            Pinfo.root[j]=" ; ".join(root)
        else:
            if Pinfo.nimg_tot[j]: Pinfo.nfra[j]=1
    return Pinfo


def checkPinfo(basename,Pinfo,flag_done,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    myNone=None
    for k in range(0,len(Pinfo.pa)):
        if FlagStop[0]: return myNone
        if Pinfo.pa[k].match(basename):
            Pinfo.nimg_tot[k] +=1
            indf=int(basename[Pinfo.n[k]+1:Pinfo.n[k]+1+Pinfo.ndig[k]])
            Pinfo.ind_in[k]=min(Pinfo.ind_in[k],indf)
            Pinfo.ind_fin[k]=max(Pinfo.ind_fin[k],indf)
            if Pinfo.fra[k]!='':
                if FlagStop[0]: return myNone
                newframe=basename[Pinfo.nab[k]]
                if newframe.isalpha() and not (newframe in Pinfo.fra[k]):
                    Pinfo.fra[k]=Pinfo.fra[k]+newframe
            flag_done=True
    return Pinfo, flag_done

def getPatternInfo(target,ext,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    S=patternInfoList()
    
    if not target=='': # no image file was found in the path
        # the pattern is the name of the image file without extension and with a star *
        # in the place of the sequential image number; in general it is different between
        # frame a and b
        split_target=re.split('(\d+)', target)
        jdig=0
        for j in range(0,len(split_target)):
            if FlagStop[0]: return None
            if len(split_target[j]):
                if split_target[j][0].isdigit():
                    s=patternInfoVar()
                    s.target=target
                    s.split_target=split_target
                    s.ext=ext
                    s.jdig=j
                    s.n=-1
                    s.nab=-1
                    s.ndig=len(s.split_target[s.jdig])
                    s.ind_in=int(s.split_target[s.jdig])
                    s.ind_fin=int(s.split_target[s.jdig])
                    s.nimg_tot=1
                    s.nimg=1
                    for k in range(0,s.jdig):
                        s.n=s.n+len(s.split_target[k])
                    sn=getPattern(s.duplicate(),FlagStop)
                    if FlagStop[0]: return None
                    S=sn.addto(S)
                    del sn
                    
                    if s.target[s.n].isalpha():
                        s.nab=s.n
                        sn=getPattern(s.duplicate(),FlagStop)
                        if FlagStop[0]: return None
                        S=sn.addto(S)
                        del sn
                    
                    m=s.n+s.ndig+1
                    if len(s.target)>m: 
                        if s.target[m].isalpha():
                            s.nab=s.n+2
                            s.ndig=len(s.split_target[s.jdig]) 
                            s=getPattern(s.duplicate(),FlagStop)
                            if FlagStop[0]: return None
                            S=s.addto(S)
                    
                    del s
                    #s=patternInfo(split_target, jmax, pa, pab, root, flag_ab, pattern, pattern_b, n, m, nab, ext)
    return S

def getPattern(s=patternInfoVar,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    target_star=s.split_target.copy()
    target_star[s.jdig]='*' 
    pattern=target_star[0]
    for j in range(1,len(s.split_target)):
        pattern=pattern+target_star[j]
    if FlagStop[0]: return None
    
    if s.nab!=-1:
        pattern_list=list(pattern)
        s.fra=pattern_list[s.nab]
        pattern_list[s.nab]='@'
        s.pattern="".join(pattern_list)
        if s.nab>s.n:
            s.nab=s.nab+s.ndig-1
    else:
        s.fra=''
        s.pattern=pattern
    s.root=s.pattern+s.ext
    sdig="*{"+str(s.ndig)+"}"
    s.root=s.root.replace("*",sdig,1)

    if FlagStop[0]: return None

    s.pa=getpa(s,FlagStop)
    if FlagStop[0]: return None
    return s

def getpa(s,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    sdig='\\d{'+str(s.ndig)+'}'
    if s.nab!=-1:
        if s.target[s.nab].islower():
            wdig='[a-z]'
        else:
            wdig='[A-Z]'
    else:
        wdig=''
    if FlagStop[0]: return None
    pattern_dig=s.pattern+s.ext
    pattern_dig=pattern_dig.replace('@',wdig)
    pattern_dig=pattern_dig.replace('*','.*')
    pattern_dig=pattern_dig.replace('.*',sdig,1)
    pa=re.compile(pattern_dig)
    return pa

def getpaf(s,frame,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    sdig='\\d{'+str(s.ndig)+'}'
    if s.target[s.nab].islower():
        wdig=f'[{frame}]'
    else:
        wdig=f'[{frame}]'
    if FlagStop[0]: return None
    pattern_dig=s.pattern+s.ext
    pattern_dig=pattern_dig.replace('@',wdig)
    pattern_dig=pattern_dig.replace('*','.*')
    pattern_dig=pattern_dig.replace('.*',sdig,1)
    pa=re.compile(pattern_dig)
    return pa

#*************************************************** Create List of Images
def createListImages(path,pinfo=patternInfoList,flagTR=bool,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]

    """
    cont=0
    while not FlagStop[0] and cont<Ncont:
        timesleep(.01)
        cont+=1
    """

    roots=re.split(";",pinfo.root)
    lists_images=[]
    lists_eim=[]
    #lists_num=[]
    #lists_fra=[]
    orda=ord('a')-1
    for r in list(roots):
        if FlagStop[0]: return None
        orda+=1
        list_image=[]
        list_eim=[]
        #list_num=[]
        #list_fra=[]
        root=r.replace(" ","")
        sdig="%0" + "%d" % (pinfo.ndig) + "d"
        pattern_dig=re.sub('\*{\d+}',sdig,root,1)
        for i in range(pinfo.nimg):
            if FlagStop[0]: return None
            image_name=pattern_dig   % (i+pinfo.ind_in)
            list_image.append(image_name)
            list_eim.append(os.path.exists(path+image_name))
            #list_num.append(i)
            #list_fra.append(chr(orda))
        lists_images.append(list_image)
        lists_eim.append(list_eim)
        #lists_num.append(list_num)
        #lists_fra.append(list_fra)
        del list_image, list_eim #, list_num, list_fra
    
    if FlagStop[0]: return None
    list_Image_Files,flagOdd=buildList(lists_images,flagTR,FlagStop)
    if FlagStop[0]: return None
    list_eim, _=buildList(lists_eim,flagTR,FlagStop)
    if FlagStop[0]: return None
    #list_num=buildList(lists_num,flagTR)
    #list_fra=buildList(lists_fra,flagTR)

    nimg_eff=int(len(list_Image_Files)/2)
    list_num=[num for num in range(nimg_eff)]
    if FlagStop[0]: return None
    list_num=interlace_lists([list_num,list_num],FlagStop)
    if FlagStop[0]: return None
    list_fra_a=['a' for num in range(nimg_eff)]
    if FlagStop[0]: return None
    list_fra_b=['b' for num in range(nimg_eff)]
    if FlagStop[0]: return None
    list_fra=interlace_lists([list_fra_a,list_fra_b],FlagStop)
    if FlagStop[0]: return None

    
    list_Image_numbers=[]
    list_Image_items=[]
    for k in range(nimg_eff*2):
        if FlagStop[0]: return None
        numberk=str(list_num[k]+imin_im_pair)+list_fra[k]+":  "
        list_Image_numbers.append(numberk)
        itemk=list_Image_Files[k]
        if not list_eim[k]:
            itemk=itemk+"  (⚠)"
        list_Image_items.append(itemk)
    nimg_eff=nimg_eff-1*flagOdd
    if flagOdd: list_eim[-1]=True
    
    #read image dimensions
    if len(list_eim):
        j=0
        while j<len(list_eim): 
            if FlagStop[0]: return None
            if not list_eim[j]: j+=1
            else: break
        if FlagStop[0]: return None
        if j<len(list_eim):
            I=Image.open(path+list_Image_Files[j])
            w=I.width
            h=I.height
        else:
            w=h=0
    else:
        w=h=0

    results=[list_Image_Files, list_eim, list_Image_numbers, list_Image_items, nimg_eff, w, h, flagTR]
    return results

def buildList(l,flagTR,*args): 
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    nfra=len(l)
    if nfra>1:
        l=interlace_lists(l,FlagStop)
    else:
        l=l[0]
    if FlagStop[0]: return None

    flagOdd=len(l)%2
    if flagOdd: l.append('')
    l=[l[:-1],l[1:]]
    if not flagTR:
        if nfra>1:
            for lc in l:
                if FlagStop[0]: return None
                del lc[nfra-1::nfra]
        else:
            for lc in l:
                if FlagStop[0]: return None
                del lc[1::2]

    l=interlace_lists(l,FlagStop)  
    if FlagStop[0]: return None
    return l,flagOdd
            
def interlace_lists(l,*args): 
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    nfra=len(l)
    nimg=len(l[0])
    lint= [None]*(nfra*nimg)
    if FlagStop[0]: return None
    for k in range(nfra):
        if FlagStop[0]: return None
        lint[k::nfra]=l[k]
    return lint

#*************************************************** Add new pinfo from user input
def analyseRoot(path,pattern,*args):
    if len(args)==0:
        FlagStop=[False]
    else:
        FlagStop=args[0]
    pinfo=patternInfoVar()
    myNone=patternInfoVar()

    roots=re.split(";",pattern)
    i=0
    flagat="@" in roots[i]
    while not flagat and i<len(roots)-1: 
        i+=1
        flagat="@" in roots[i]
        break
    if flagat: roots=[roots[i]]
   
    flag_done=False
    ndig=None
    isLower=0
    for k in range(len(roots)):
        if FlagStop[0]: return myNone
        roots[k]=roots[k].replace(" ","")
        roots[k]=re.sub("\*+","*",roots[k])
        if ndig==None: 
            astseq=re.findall("\*\{\d+\}",roots[k])
            if len(astseq):
                if k==0: ndig=int(re.findall("\{\d+\}",astseq[0])[0][1:-1])
            else:
                if k==0: ndig=0
        roots[k]=re.sub("\*\{\d+\}","*",roots[k])
        if FlagStop[0]: return myNone
        if pinfo.ext: 
            if not pinfo.ext in roots[k]:
                roots[k]=roots[k]+"*"+pinfo.ext
                roots[k]=re.sub("\*+","*",roots[k])
                pa=getpaun(roots[k],ndig,isLower)
            else: pa=getpaun(roots[k],ndig,isLower)
        else:  pa=getpaun(roots[k],ndig,isLower)
        files=findFiles_sorted(path+roots[k].replace('@','*')+"*") # needed to use the recompiled reg expressions   
        if FlagStop[0]: return myNone   
        for file in files:
            if FlagStop[0]: return myNone
            basename=os.path.basename(file)
            if not flag_done:
                if any(file.endswith(ex) for ex in supported_exts) and pa.match(basename)!=None:
                    target, ext=os.path.splitext(basename)
                    Pinfo=getPatternInfo(target, ext, FlagStop)
                    root_eff=os.path.splitext(roots[k])[0]
                    if  root_eff in Pinfo.pattern:
                        pinfo=Pinfo.extractPinfo(Pinfo.pattern.index(root_eff))
                        roots[k]=re.sub("\*\{\d+\}","*",pinfo.root)
                        ndig=pinfo.ndig
                        pa=getpaun(roots[k],ndig,isLower)
                        flag_done=True
                    elif len(Pinfo.pattern):
                        kp=np.argmax(np.asarray(Pinfo.nimg_tot))
                        pinfo=Pinfo.extractPinfo(kp)
                        roots[k]=re.sub("\*\{\d+\}","*",pinfo.root)
                        ndig=pinfo.ndig
                        pa=getpaun(roots[k],ndig,isLower)
                        flag_done=True
                    if flag_done and k==0 and not pinfo.ext in roots[k]:
                        #if len(roots)==1 there is a @ and I cannot replace the pattern
                        roots[k]=roots[k]+"*"+pinfo.ext
                        roots[k]=re.sub("\*+","*",roots[k])
                        pa=getpaun(roots[k],ndig,isLower)
                    if flag_done and flagat:
                        if basename[pinfo.nab].islower(): 
                            isLower=1
                            pa=getpaun(pattern,ndig,isLower)
                        else: 
                            isLower=-1
                            pa=getpaun(roots[k],ndig,isLower)
            else:
                if pa.match(basename):
                    pinfo.nimg_tot +=1
                    indf=int(basename[pinfo.n+1:pinfo.n+1+pinfo.ndig])
                    pinfo.ind_in=min(pinfo.ind_in,indf)
                    pinfo.ind_fin=max(pinfo.ind_fin,indf)
                    if pinfo.fra!='':
                        if FlagStop[0]: return myNone
                        newframe=basename[pinfo.nab]
                        if newframe.isalpha() and not (newframe in pinfo.fra):
                            pinfo.fra=pinfo.fra+newframe  
    if pinfo.nimg_tot>0:
        pinfo.nimg=pinfo.ind_fin-pinfo.ind_in+1
        if FlagStop[0]: return myNone
        if len(roots)==1:
            if flag_done:
                if len(pinfo.fra)>1:
                    root=[]
                    for k in range(len(pinfo.fra)):
                        if FlagStop[0]: return myNone
                        root.append(pinfo.root.replace('@',pinfo.fra[k]))
                    pinfo.root=" ; ".join(root)    
        else:
            root=[]
            for k in range(len(roots)):
                if FlagStop[0]: return myNone
                pinfo.fra=pinfo.fra+chr(97+k)
                sdig="*{"+str(pinfo.ndig)+"}"
                root.append(roots[k].replace('*',sdig,1))
            pinfo.root=" ; ".join(root)
        pinfo.pattern=pattern 
    else:
        pinfo.nimg_tot=0
        pinfo.nimg=0
        pinfo.root=pattern
        pinfo.ndig=0
    return pinfo   
        
def getpaun(pattern,ndig,isLower): #getpa un=unknown number of digits and lower/uppercase
    if ndig:
        sdig='\\d{'+str(ndig)+'}[^0-9]*'
    else:
        sdig='\\d+'
    if isLower==0:
        wdig='[a-zA-Z]'
    elif isLower>0:
        wdig='[a-z]'
    elif isLower<0:
        wdig='[A-Z]'
    pattern_dig=pattern+'**'
    pattern_dig=pattern_dig.replace('@',wdig)
    pattern_dig=pattern_dig.replace('*','.*')
    pattern_dig=pattern_dig.replace('.*',sdig,1)
    pa=re.compile(pattern_dig)
    return pa

#*************************************************** TESTING
if __name__ == "__main__":
    working_fold=basefold
    working_fold='C:/desk/PIV_Img/swirler_png/'
    #working_fold='/Users/gerardo/Desktop/img/img1/'
    flagTR=False

    print('*'*50)
    Pinfo=analysePath(working_fold)
    print(f'analysePath("{working_fold}"):')
    print(f'   root={Pinfo.root}')
    print(f'   nimg={Pinfo.nimg}')
    print(f'   nimg_tot={Pinfo.nimg_tot}')
    print(f'   ind_in={Pinfo.ind_in}')
    print(f'   ind_in={Pinfo.ind_fin}')

    if Pinfo.nimg_tot:
        k=np.argmax(np.asarray(Pinfo.nimg_tot))
        pinfo=Pinfo.extractPinfo(k)
    else:
        pinfo=patternInfoVar()
    pinfo.fra==''
    results=createListImages(working_fold,pinfo,flagTR)
    print(f'root with largest # of images=\n   root={pinfo.root}')
    for num,im in zip(results[2], results[3]):
         print(f'   {num+im}')
    

    root='img_cam0_b*; img_cam0_a*'
    print('*'*50)
    print(f'analyseRoot("{working_fold}","{root}"):')
    pinfo=analyseRoot(working_fold,root)
    print(f'root={pinfo.root}')
    print(f'nimg={pinfo.nimg}')
    print(f'nimg_tot={pinfo.nimg_tot}')
    print(f'pattern={pinfo.pattern}')
    results=createListImages(working_fold,pinfo,flagTR)
    for num,im in zip(results[2], results[3]):
        print(f'   {num+im}')

    print('\n\nTHE END')
