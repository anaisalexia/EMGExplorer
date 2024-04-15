import numpy as np
import pyqtgraph as pg
import h5py

from scipy import signal
import numpy as np
import pandas as pd
import xarray as xr

import xarray as xr
from datatree import DataTree
import datatree

#PLOT WITH PG

# fig = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")

# root = '.\\data\\'
# names = ['emg_record2.nc','PSL_ 0009_PN_J7_iso_1.nc','S2_20MVC2.nc']
# name  = names[0]


# data12 =  datatree.open_datatree(root + names[0])

# y = data12['/S01/60MVC/Trial_02']['EMG'].loc[{'Channel':int('1')}]
# x = data12['/S01/60MVC/Trial_02']['EMG'].loc[{'Channel':int('1')}].Time
# print( x)

# # fig = pg.MultiPlotWidget()
# plot = fig.addPlot(title='test')
# time = np.arange(1000,2000)
# data = np.random.normal(size=1000)

# plot.plot(x=x ,y=y, pen=(255,0,0))
# # pg.plot(data, title="Simplest possible plotting example")


# if __name__ == '__main__':
#     pg.exec()





# def demean(signal,arg1,arg2):
#     return signal - np.mean(signal)

# def addx(signal,x):
#     return signal + x

# PROC = {
#     'demean': demean,
#     'addx':addx
# }


# app = pg.mkQApp("Parameter Tree Example")
# import pyqtgraph.parametertree.parameterTypes as pTypes
# from pyqtgraph.parametertree import Parameter, ParameterTree

# class FilteringGroupAdd(pTypes.GroupParameter):
#     def __init__(self, **opts):
#         opts['type'] = 'group'
#         opts['addText'] = "Add"
#         opts['addList'] = ['demean', 'addx']
#         pTypes.GroupParameter.__init__(self, **opts)
    
#     def addNew(self, fc_name):
#         fc = PROC[fc_name]
#         self.addChild(dict(name="ScalableParam %d" % (len(self.childs)+1), type=typ, value=val, removable=True, renamable=True))

# class FilteringGroup(pTypes.GroupParameter):
#     def __init__(self, **opts):
#         opts['type'] = 'group'
#         opts['addText'] = "Processing"
#         opts['addList'] = ['demean', 'addx']
#         pTypes.GroupParameter.__init__(self, **opts)
    
#     def addNew(self, fc_name):
#         fc = PROC[fc_name]
#         self.addChild(dict(name="ScalableParam %d" % (len(self.childs)+1), type=typ, value=val, removable=True, renamable=True))

# ## Create tree of Parameter objects
# p = Parameter.create(name='params', type='group', children=params)
# ## test save/restore
# state = p.saveState()
# p.restoreState(state)
# compareState = p.saveState()
# assert pg.eq(compareState, state)


# if __name__ == '__main__':
#     pg.exec()







# import processing function
# print(os.listdir('EMG_Explorer_App/Explorer_package/processing'))
# ['processing1.py', 'processing2.py', '__pycache__']


from importlib.machinery import SourceFileLoader
import os

ROOT = 'EMG_Explorer_App/Explorer_package/processing'
mod_list = []
requirements_list = []
for name in os.listdir(ROOT):
    if (name != '__pycache__') and (name.split('_')[0] != 'requirement'):
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

            

def menu_from_dict(dict_):
    menu = {}
    for k,v in dict_.items():
        if isinstance(v,dict):
            menu[k] = menu_from_dict(v)
        else:
            return list(dict_.keys())
        
    return menu
        
dict_ = menu_from_dict(PROCESSING)
