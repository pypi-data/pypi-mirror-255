"""
    Configuration writer
"""
import json
import os
from dtscore import utils
from dtscore import logging as _log
from dtscore import globals as gl

# ----------------------------------------------------------------------------------------------------
#   Write configuration to console and file
def writejson(schema:dict, filepath:str, filename:str, datestamp:bool = True) -> str:
    if schema is None or len(schema) == 0: raise Exception("Internal error: schema is None or empty.")
    if filepath is None or filepath == '': raise Exception("Internal error: filepath parameter is None or empty.")
    if filename is None or filename == '': raise Exception("Internal error: filename parameter is None or empty.")
    #config_str = json.dumps(schema)
    #print(config_str)

    finalfilename = utils.datestampFileName(filename) if datestamp else filename
    output_filename_fullpath = os.path.join(filepath, finalfilename)

    with open(output_filename_fullpath, mode='xt') as output_file:
        json.dump(obj=schema, fp=output_file)

    return finalfilename

# ----------------------------------------------------------------------------------------------------
#   generic function to write a list of strings to an external file
def writetext(text:list[str], filepath:str, filename:str) -> str:
    if text is None or len(text) == 0: raise Exception("Internal error: text is None or empty.")
    if filepath is None or filepath == '': raise Exception("Internal error: filepath parameter is None or empty.")
    if filename is None or filename == '': raise Exception("Internal error: filename parameter is None or empty.")
    fullpath = os.path.join(filepath, filename)
    with open(fullpath, mode='w') as file:
        file.writelines(text)
    return filename

if __name__ == '__main__':
    print('This file cannot be run as a script')
else:
    log = _log.get_log(__name__, gl.loglevel)
