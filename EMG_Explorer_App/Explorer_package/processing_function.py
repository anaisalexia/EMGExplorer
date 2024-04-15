from importlib.machinery import SourceFileLoader
import os

ROOT = 'EMG_Explorer_App\Explorer_package\processing'

def generate_processing_dict():
    mod_list = []
    requirements_list = []
    for name in os.listdir(ROOT):
        if name != '__pycache__':
            # save file name
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
    menu = {}
    for k,v in dict_.items():
        if isinstance(v,dict):
            menu[k] = menu_from_dict(v)
        else:
            return list(dict_.keys())
        
    return menu

PROCESSING = generate_processing_dict()
PROCESSING_NAME = menu_from_dict(PROCESSING)
