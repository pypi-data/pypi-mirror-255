"""
    File utilities
"""
from typing import Optional
import json
import os
import glob
from typing import Optional
from dtscore import globals as gl
from dtscore import utils

ANALYSES_CONFIGS_FOLDER = '.configs'

apphome = gl.apphome
getconfigspath = gl.getconfigspath
getconfigsrelativepath = gl.getconfigsrelativepath
getreportspath = gl.getreportspath
getreportsrelativepath = gl.getreportsrelativepath
getportfoliospath = gl.getportfoliospath
getportfoliosrelativepath = gl.getportfoliosrelativepath
getscriptspath = gl.getscriptspath
getscriptsrelativepath = gl.getscriptsrelativepath

#--------------------------------------------------------------------------------------------------
def get_appconfig(filename:str) -> Optional[dict]:
    configspath = get_globalconfigspath()
    if os.path.exists(os.path.join(configspath,filename)):
        return read_json(configspath, filename)
    else:
        return None

#--------------------------------------------------------------------------------------------------
def get_recentportfoliodetailpath(analysisfolder:str) -> str:
    return _do_glob(analysisfolder, gl.glob_portfolio_detail)

#--------------------------------------------------------------------------------------------------
def get_recentportfolioholdingdetailpath(analysisfolder:str) -> str:
    return _do_glob(analysisfolder, gl.glob_portfolioholding_detail)

#--------------------------------------------------------------------------------------------------
def get_recentordersheetpath(analysisfolder:str) -> str:
    return _do_glob(analysisfolder, gl.glob_ordersheet)

# -------------------------------------------------------------------------------------------------
def get_coredatapath() -> str:
    return os.path.join(gl.apphome, gl.coredatafolder)

# -------------------------------------------------------------------------------------------------
def get_globalconfigspath() -> str:
    return os.path.join(gl.apphome, gl.analysesfolder, ANALYSES_CONFIGS_FOLDER)

# -------------------------------------------------------------------------------------------------
def get_globalconfigsrelativepath() -> str:
    return os.path.join(gl.analysesfolder, ANALYSES_CONFIGS_FOLDER)

# -------------------------------------------------------------------------------------------------
def get_recentportfoliodetailpath(analysisfolder:str) -> str:
    return _do_glob(analysisfolder, gl.glob_portfolio_detail)

#--------------------------------------------------------------------------------------------------
def get_recentportfolioholdingdetailpath(analysisfolder:str) -> str:
    return _do_glob(analysisfolder, gl.glob_portfolioholding_detail)

#--------------------------------------------------------------------------------------------------
def get_recent_ordersheet_filepath(analysisfolder:str) -> str:
    return _do_glob(analysisfolder, gl.glob_ordersheet)

#--------------------------------------------------------------------------------------------------
#   read a json file and return as dictionary
def read_json(filepath:str, filename:str) -> dict:
    fullpath = os.path.join(filepath, filename)
    with open(fullpath, mode='r') as file:
        jsondict = json.load(fp=file)
    return jsondict

# -------------------------------------------------------------------------------------------------
#   Write configuration to console and file
def write_json(schema:dict, filepath:str, filename:str, datestamp:bool = True) -> str:
    if schema is None or len(schema) == 0: raise Exception("Internal error: schema is None or empty.")
    if filepath is None or filepath == '': raise Exception("Internal error: filepath parameter is None or empty.")
    if filename is None or filename == '': raise Exception("Internal error: filename parameter is None or empty.")

    finalfilename = utils.datestampFileName(filename) if datestamp else filename
    output_filename_fullpath = os.path.join(filepath, finalfilename)

    with open(output_filename_fullpath, mode='w') as output_file:
        json.dump(obj=schema, fp=output_file)

    return finalfilename

# -------------------------------------------------------------------------------------------------
#   generic function to write a list of strings to an external file
def write_text(text:list[str], filepath:str, filename:str) -> str:
    if text is None or len(text) == 0: raise Exception("Internal error: text is None or empty.")
    if filepath is None or filepath == '': raise Exception("Internal error: filepath parameter is None or empty.")
    if filename is None or filename == '': raise Exception("Internal error: filename parameter is None or empty.")
    fullpath = os.path.join(filepath, filename)
    with open(fullpath, mode='w') as file:
        file.writelines(text)
    return filename

#--------------------------------------------------------------------------------------------------
#   private method
def _do_glob(analysisfolder:str, pattern:str) -> Optional[str]:
    globpath = os.path.join(gl.apphome,gl.analysesfolder,analysisfolder, gl.reportsfolder, pattern)
    all_filenames = glob.glob(globpath, recursive=False)
    #   !!proper sorting relies on date stamped file names!!
    all_filenames.sort(reverse=True)
    #   select the latest filename
    return all_filenames[0] if len(all_filenames) > 0 else None

#--------------------------------------------------------------------------------------------------
#   Entry
if __name__ == '__main__':
    print('This file cannot be run as a script')
# else:
#     log = _log.get_log(__name__, gl.loglevel)
