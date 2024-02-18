''' helper functions for reading cfg files'''
from typing import Tuple,Callable,TextIO,Union
def readNumCfg(f,ind:int,convFun:Callable,separator=',',comment='%')->Tuple[int,Union [int,float]]:
  ''' reads a number from a cfg file'''
  
  while (line:=f.readline())[0]==comment:
    ind+=1
  
  return  ind+1,convFun(line.strip().split(separator)[0])

def readCfgTag(f:TextIO)->str:
  ''' returns the cfg tag'''
  return f.readline()[0:8]

def readNumVecCfg(f,ind:int,convFun,separator=',',comment='%')->Tuple[int,list[Union [int,float]]]:
  ''' reads a vector of numbers from a cfg file'''
  
  while (line:=f.readline())[0]==comment:
    ind+=1
  nums=line.strip().split(separator)[0].split('[')[1].split(']')[0].strip()

  return  ind+1,[convFun(num) for num in nums.split(' ')]