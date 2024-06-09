from importlib.machinery import SourceFileLoader
import os
from .setup import *
from .mainwindow_utils import get_item_from_path,Try_decorator,LoggerError_decorator

ROOT = 'EMG_Explorer_App\Explorer_package\processing'
ROOT_MEASUREMENT = 'EMG_Explorer_App\Explorer_package\summary_measurement'
ROOT_DISPLAY = 'EMG_Explorer_App\Explorer_package\summary_display'
ROOT_RANGEDISPLAY = 'EMG_Explorer_App\Explorer_package\summary_rangeDisplay'

ROOT_GLOBALPROCESSING = 'EMG_Explorer_App\Explorer_package\global_processing_pipelines'
logger = logging.getLogger('main')

@LoggerError_decorator
def apply_jsonFilter(x,pathFile,dictFile=None):
    if pathFile != None:
        f = open(f'{PATH_PIPELINE}{pathFile}.json')
        data = json.load(f)
    else:
        data = dictFile

    for nb,process in data.items():
        print(process)
        func = PROCESSING[process['path'][0]][process['name']]
        arg = process['arguments']
        arg[list(arg.keys())[0]] = x
        print('list arg', arg,x)
        x = func(**arg) 

    return x  

@LoggerError_decorator
def apply_jsonFilterGlobal(loader,pathData,pathFile=None,dictFile=None):
    if pathFile != None:
        f = open(f'{PATH_PIPELINE}{pathFile}.json')
        processDict = json.load(f)

    else:
        processDict = dictFile

    # apply process for each variable
    for gr in list(pathData.keys()):
        for var in list(pathData[gr].keys()):
            try:
                # find the accurate 
                processVar = processDict[var]

                for nb,process in processVar.items():
                    func = PROCESSING[process['path'][0]][process['name']]
                    arg = process['arguments']
                    arg_copy = arg.copy()
                    for k,v in arg_copy.items():
                        if v == None:
                            del arg[k]
                    arg['path'] = pathData
                    arg['loader'] = loader
                    func(**arg) 

            except Exception as e:
                logger.error(f"Application Global Filter - Processing of var {var} failed : {e}")



def generate_processing_dict(ROOT):
    """Generate the constant dictionnary PROCESSING. This dictionnary comprises all the function
    of the files that are in the "processing" folder.
    The function first saves the names of each processing file and the names the external module such as scipy,numpy... so that thez are not
    imported as function further in the process.
    For each file that comprises function, the file is imported as a module and the functions are saved in a dictionnary

    PROCESSING : {'file_name1':{'function_name1':function1,
                                'function_name2':function2,},
                'file_name2:{'function_name1':function1},
                ....}

    """
    mod_list = []
    requirements_list = []
    for name in os.listdir(ROOT):
        if name != '__pycache__':
            # save file name
            if name[:-3].split('_')[0] != 'requirement':
                mod_list += [name[:-3]]
            # save requirements module name
            requirements_name = ROOT + '/' + 'requirement_' + name
            if os.path.exists(requirements_name):
                mod = SourceFileLoader('requirement_' + name,requirements_name).load_module()
                for fc_name in dir(mod):
                    requirements_list.append(fc_name)



    PROCESSING = {}
    for name in mod_list:
        mod = SourceFileLoader(name,f"{ROOT}/{name}.py").load_module()
        PROCESSING[name] = {}

        for fc_name in dir(mod):
            fc = getattr(mod,fc_name)
            if (fc_name[0] != '_') & (fc_name not in requirements_list):
                PROCESSING[name][fc_name] = fc
    return PROCESSING

def menu_from_dict(dict_):
    """Create a dictionnary of path and names using the keys of a embbeded dictionnaries.

    Args:
        dict_ (dict): embedded dictionnaries

    Returns:
        menu (dict): tree/dictionnary of the keys of the input dictionnary
    """
    menu = {}
    for k,v in dict_.items():
        if isinstance(v,dict):
            menu[k] = menu_from_dict(v)
        else:
            return list(dict_.keys())
        
    return menu






def has_folder(ROOT):
    for path in os.listdir(ROOT):
        if os.path.isdir( ROOT + '\\' + path ):
            return True
    return False

def dictOfFiles_from_EmbeddedFolders(ROOT):
    list_process = []
    PROCESS = {}

    for path in os.listdir(ROOT):
        if os.path.isdir( ROOT + '\\' + path ):
            if has_folder(ROOT + '\\' + path ):
                PROCESS[path] = dictOfFiles_from_EmbeddedFolders(ROOT + '\\' + path)
            else:
                PROCESS[path] = os.listdir( ROOT + '\\' + path )
        else:
            list_process.append(path)

    if list_process != []:
        PROCESS['general'] = list_process


    return PROCESS
#{'Acceleration': ['global_processing3.json'], 'EMG': {'folder1': [], 'folder2': ['global_processing2.json']}, 'general': ['global_processing.json.json']}

PROCESSING = generate_processing_dict(ROOT)
PROCESSING_NAME = menu_from_dict(PROCESSING)

MEASUREMENT = generate_processing_dict(ROOT_MEASUREMENT)
DISPLAY = generate_processing_dict(ROOT_DISPLAY)
RANGEDISPLAY = generate_processing_dict(ROOT_RANGEDISPLAY)

MEASUREMENT_NAME = menu_from_dict(MEASUREMENT)
DISPLAY_NAME = menu_from_dict(DISPLAY)
RANGEDISPLAY_NAME = menu_from_dict(RANGEDISPLAY)

