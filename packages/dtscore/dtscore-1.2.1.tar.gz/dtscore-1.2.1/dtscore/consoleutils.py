"""
    Console utilities
"""
import os
import glob
from typing import Optional
from dtscore import globals as gl

#--------------------------------------------------------------------------------------------------
def promptfor_bool(prompt:str) -> bool:
    print(prompt + " (Y/N)?: ", end="")
    yesno = input().upper()
    match yesno:
        case "Y": return True
        case "N": return False
        case _:
            print("Invalid - response must be Y or N")
            return promptfor_bool(prompt)

#--------------------------------------------------------------------------------------------------
def promptfor_text(prompt:str, toupper:bool=False) -> str:
    print(prompt + ': ', end='')
    response = input()
    return response.upper() if toupper else response

#--------------------------------------------------------------------------------------------------
def promptfor_option(prompt:str, options:list[str]) -> str:
    print(prompt + ": ", end="")
    response = input().upper()
    if response not in options:
        print(f'{response} is invalid, re-enter.')
        response = promptfor_option(prompt, options)
    return response
    
#--------------------------------------------------------------------------------------------------
def promptfor_cutoffandplotrange() -> tuple[str,str]:
    print('enter cutoff date (yyyymmdd): ', end='')
    cutoff = input()

    print(f'plot range start date (yyyymmdd) or enter for {cutoff} default: ', end='')
    response = input()
    startdate = response if len(response) > 0 else cutoff
    print(f'plot range end date (yyyymmdd): ', end='')
    enddate = input()
    plotrange = f'{startdate} - {enddate}'
    return cutoff, plotrange
