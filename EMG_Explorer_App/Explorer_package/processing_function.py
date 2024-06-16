from importlib.machinery import SourceFileLoader
from .setup import *
from .mainwindow_utils import get_item_from_path,Try_decorator,LoggerError_decorator

sys.path.append('EMG_Explorer_App/Explorer_package/processing')
sys.path.append('EMG_Explorer_App/Explorer_package/global_processing')
sys.path.append(os.getcwd())

logger = logging.getLogger('main')



@LoggerError_decorator
def apply_jsonFilter(x,pathFile,dictFile=None):
    """Apply a single processing pipeline described in a JSON file to an array.

    Args:
        x (array): _description_
        pathFile (str): path to the JSON file that contains the processing pipeline
        dictFile (_type_, optional): _description_. Defaults to None.

    Returns:
        array: filtered array
    """
    try: 
        if pathFile != None:
            f = open(f'{PATH_PIPELINE}{pathFile}.json')
            data = json.load(f)
        else:
            data = dictFile

    except Exception as e:
        logger.error(f"Application Single Filter - JSON file for single processing could not be loaded : {e}")
        return x


    for nb,process in data.items():
        try:
            func = PROCESSING[process['path'][0]][process['name']]
            arg = process['arguments']
            arg[list(arg.keys())[0]] = x
            x = func(**arg) 
        except Exception as e:
            logger.error(f"Application Single Filter - Processing {nb} ({process}) could not be applied : {e}")

    return x  



def apply_jsonFilterGlobal(loader,pathData,pathFile=None,dictFile=None):
    """Apply the processing steps described in a JSON file to the data selected by a path and contained in a Loader.

    Args:
        loader (Loader): _description_
        pathData (list): _description_
        pathFile (str, optional): _description_. Defaults to None.
        dictFile (dictionnary, optional): _description_. Defaults to None.
    """
    if pathFile != None:
        f = open(f'{PATH_GLOBAL_PIPELINE}{pathFile}.json')
        processDict = json.load(f)

    else:
        processDict = dictFile

    # apply process for each groups and variables
    if processDict != {}:

        for gr in list(pathData.keys()):
            for var in list(pathData[gr].keys()):
                try:
                    try:
                        processVar = processDict[var]
                    except:
                        logger.debug(f"Application Global Filter - No filtering for {var}")
                        continue

                    for nb,process in processVar.items():
                        # fetch the function 
                        func = PROCESSINGGLOBAL[process['path'][0]][process['name']]
                        arg = process['arguments']
                        arg_copy = arg.copy()
                        # delete the argument that have no values
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
    Example : {'processing_fichier1': ['butterfilter', 'butterfilter_bandpass', 'double_threshold'], ' processing_fichier2' : [function1, function2]}

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
    """Check if the folder has folder.

    Args:
        ROOT (str): path to a folder

    Returns:
        bool: _description_
    """
    for path in os.listdir(ROOT):
        if os.path.isdir( ROOT + '\\' + path ):
            return True
    return False




def dictOfFiles_from_EmbeddedFolders(ROOT):
    """Returns a dictionnary of a path of files contain in embedded folders. 
    Example: {'Acceleration': ['global_processing3.json'], 'EMG': {'folder1': [], 'folder2': ['global_processing2.json']}, 'general': ['global_processing.json']}

    Args:
        ROOT (str): path to a folder

    Returns:
        dictionnary: _description_
    """
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



PROCESSING = generate_processing_dict(ROOT)
PROCESSING_NAME = menu_from_dict(PROCESSING)
PROCESSINGGLOBAL = generate_processing_dict(ROOT_PROCESSINGGLOBAL)
PROCESSINGGLOBAL_NAME = menu_from_dict(PROCESSINGGLOBAL)

print('MENU FROM DICT ', PROCESSING_NAME, '----------------')
MEASUREMENT = generate_processing_dict(ROOT_MEASUREMENT)
DISPLAY = generate_processing_dict(ROOT_DISPLAY)
RANGEDISPLAY = generate_processing_dict(ROOT_RANGEDISPLAY)

MEASUREMENT_NAME = menu_from_dict(MEASUREMENT)
DISPLAY_NAME = menu_from_dict(DISPLAY)
RANGEDISPLAY_NAME = menu_from_dict(RANGEDISPLAY)

