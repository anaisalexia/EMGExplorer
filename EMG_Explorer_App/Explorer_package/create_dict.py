# from importlib.machinery import SourceFileLoader
# import os 

# def dict_from_module_loading_function(mod_name):

#     # if folder:
#     # for name in os.listdir(f'EMG_Explorer_App/Explorer_package/{mod_name}'):
#     #     if name != '__pycache__':
#     #         mod_list += [name[:-3]]

#     # imports the module from the given path
#     DICT = {}
#     mod = SourceFileLoader(mod_name,f"EMG_Explorer_App/Explorer_package/{mod_name}.py").load_module()

#     for fc_name in dir(mod):
#         fc = getattr(mod,fc_name)
#         if fc_name[:len('MyDataLoader')] == 'MyDataLoader':
#             DICT[fc.format()] = fc

#     return DICT

# DATALOADER = dict_from_module_loading_function('loading_function')
# print(DATALOADER)
                


# def load_multiple_files(paths): # load _ multiple files
#     """_summary_

#     Args:
#         paths (list): _description_
#     """
#     data = {}
#     for path in paths:
#         name = os.path.split(path)[-1]
#         type_format = name.split('.')[-1]
#         loader = DATALOADER[f'.{type_format}'](path,name)        
#         data[name] = loader
        
#     return data
