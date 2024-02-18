"""
    Utilties
    ! functions in this module must not use imports from other dts core modules to avoid
    ! circular references
"""
import os
from datetime import datetime

#--------------------------------------------------------------------------------------------------
#   add a date time stamp on the filename
def datestampFileName(fileName:str) -> str:
    (base,ext) = os.path.splitext(fileName)
    return f'{base}_{datetime.now():%Y%m%d_%H%M%S}{ext}'

def appendtofilename(filename:str, append:str) -> str:
    base, ext = os.path.splitext(filename)
    return f'{base}_{append}{ext}'

#--------------------------------------------------------------------------------------------------
#   add an index number to the filename
def index_filename(fileName:str, rundate: str, index:int) -> str:
    (base,ext) = os.path.splitext(fileName)
    return f'{rundate}_{base}_{index:02}{ext}'

# -------------------------------------------------------------------------------------------------
#   Partition a list
#   - return a generator that applies a "window_size" moving window to the list
#   - for list a=[1,2,3,4,5,6], partition(a,2) will generate [1,2], [2,3]...[5,6]
def partition(aList:list, windows_size:int):
    for start in range(0,len(aList)-windows_size+1):
        yield aList[start:start+windows_size]


#---------------------------------------------------------------
#   do summary print of dataframe
# def quick_print(df:pd.DataFrame, head_size:int=5, do_info:bool=False, do_exit:bool=False):
#     print(df.head(head_size))
#     if do_info : print(df.info())
#     print('**********************\n')
#     if do_exit : exit()

