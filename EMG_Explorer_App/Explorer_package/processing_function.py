from importlib.machinery import SourceFileLoader
import os
from .setup import *

ROOT = 'EMG_Explorer_App\Explorer_package\processing'


def apply_jsonFilter(x,pathFile):
    f = open(f'{PATH_PIPELINE}{pathFile}.json')
    data = json.load(f)
    print('in apply json filter',pathFile,data)
    for nb,process in data.items():
        print(process)
        func = PROCESSING[process['path'][0]][process['name']]
        arg = process['arguments']
        arg[list(arg.keys())[0]] = x
        print('list arg', arg,x)
        x = func(**arg) 

    return x  

def generate_processing_dict():
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

def get_item_from_path(dict_dict,path):
    """get the item of embedded dictionnaries from a path made of keys

    Args:
        dict_dict (_type_): _description_
        path (_type_): _description_
    """
    item = dict_dict[path[0]]
    for key in path[1:]:
        item = item[key]
        
    return item

PROCESSING = generate_processing_dict()

PROCESSING_NAME = menu_from_dict(PROCESSING)
