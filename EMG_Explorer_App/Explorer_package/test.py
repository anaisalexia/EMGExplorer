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


# from importlib.machinery import SourceFileLoader
# import os

# ROOT = 'EMG_Explorer_App/Explorer_package/processing'
# mod_list = []
# requirements_list = []
# for name in os.listdir(ROOT):
#     if (name != '__pycache__') and (name.split('_')[0] != 'requirement'):
#         # save file name
#         mod_list += [name[:-3]]
#         # save requirements module name
#         requirements_name = ROOT + '/' + 'requirement_' + name
#         if os.path.exists(requirements_name):
#             mod = SourceFileLoader('requirement_' + name,requirements_name).load_module()
#             for fc_name in dir(mod):
#                 requirements_list.append(fc_name)



# PROCESSING = {}
# for name in mod_list:
#     mod = SourceFileLoader(name,f"{ROOT}/{name}.py").load_module()
#     PROCESSING[name] = {}

#     for fc_name in dir(mod):
#         fc = getattr(mod,fc_name)
#         if (fc_name[0] != '_') & (fc_name not in requirements_list):
#             PROCESSING[name][fc_name] = fc

            

# def menu_from_dict(dict_):
#     menu = {}
#     for k,v in dict_.items():
#         if isinstance(v,dict):
#             menu[k] = menu_from_dict(v)
#         else:
#             return list(dict_.keys())
        
#     return menu
        
# dict_ = menu_from_dict(PROCESSING)
# print(PROCESSING)



# # EXTRACT ARGUMENT FROM FUNCTION
# def function_test(arg1,arg2 = 2,arg3=3):
#     d = 3 
#     arg2=4
#     return arg1

# print(function_test.__code__.co_varnames)
# print(function_test.__code__.co_argcount)
# print(function_test.__code__.co_varnames[:function_test.__code__.co_argcount])
# print(function_test.__defaults__)

#TEST

# def get_item_from_path(dict_dict,path):
#     """get the item of embedded dictionnaries from a path made of keys

#     Args:
#         dict_dict (_type_): _description_
#         path (_type_): _description_
#     """
#     item = dict_dict[path[0]]
#     for key in path[1:]:
#         item = item[key]
        
#     return item

# dict_dict = {'d1':{'d2':1,'d3':3},'d4':{'d5':5}}
# print(get_item_from_path(dict_dict,['d1','d2']))
# print(get_item_from_path(dict_dict,['d4','d5']))
# print(type('').__name__)


# # FENETRE
# from PyQt5 import QtWidgets, QtGui, QtCore

# class CheckableComboBox(QtWidgets.QComboBox):
#     def __init__(self):
#         super(CheckableComboBox, self).__init__()
#         self.view().pressed.connect(self.handleItemPressed)
#         self.setModel(QtGui.QStandardItemModel(self))

#     def handleItemPressed(self, index):
#         item = self.model().itemFromIndex(index)
#         if item.checkState() == QtCore.Qt.Checked:
#             item.setCheckState(QtCore.Qt.Unchecked)
#         else:
#             item.setCheckState(QtCore.Qt.Checked)

# class Dialog_01(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         myQWidget = QtWidgets.QWidget()
#         myBoxLayout = QtWidgets.QHBoxLayout()
#         myQWidget.setLayout(myBoxLayout)
#         self.setCentralWidget(myQWidget)
#         self.ComboBox = CheckableComboBox()
#         self.toolbutton = QtWidgets.QToolButton(self)
#         self.toolbutton.setText('Categories ')
#         self.toolmenu = QtWidgets.QMenu(self)
#         self.toolmenu.addAction('/')
#         # for i in range(3):
#         #     self.ComboBox.addItem('Category %s' % i)
#         #     item = self.ComboBox.model().item(i, 0)
#         #     item.setCheckState(QtCore.Qt.Unchecked)
#         #     action = self.toolmenu.addAction('Category %s' % i)
#         #     action.setCheckable(True)
#         #     action.triggered.connect(self.oc_triggered)
#         self.toolbutton.setMenu(self.toolmenu)
#         self.toolbutton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
#         myBoxLayout.addWidget(self.toolbutton)
#         myBoxLayout.addWidget(self.ComboBox)

#     def oc_triggered(self):
#         print(self.toolmenu.actions())
#         print(self.toolmenu.actions()[0].text())
#         print(self.toolmenu.actions()[0].isChecked())
#         print(self.toolmenu.actions()[2].setChecked(True))
#         print(self.toolmenu.actions()[1].setChecked(False))
#         # print(self.toolmenu.actions()[2].setUnchecked())

# if __name__ == '__main__':

#     app = QtWidgets.QApplication(['Test'])
#     dialog_1 = Dialog_01()
#     dialog_1.show()
#     app.exec_()



# TREEEEEEEEEEEEEEEEE
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys

# def get_selectedItems(tree):

#         def has_childLeaf(item):
#             nb_children = item.childCount()
#             for i in range(nb_children):
#                 child = item.child(i)
#                 nb_chil_children = child.childCount()
#                 if nb_chil_children > 0:
#                     return False
#             return True
                    
            
#         def recurse(item):
#                 list_dict = {}
#                 if has_childLeaf(item):
#                     list_checked = []
#                     for j in range(item.childCount()):
#                          if  item.child(j).checkState(0) == Qt.Checked :
#                             list_checked.append(item.child(j).text(0))
#                     return list_checked 
                    
#                 else:
#                     for i in range (item.childCount()):
#                         list_dict[item.child(i).text(0)] = recurse(item.child(i))
#                 return list_dict
        
#         return recurse(tree.invisibleRootItem())



# def main(): 
#     app     = QtWidgets.QApplication(sys.argv)
#     tree    = QtWidgets.QTreeWidget()
#     headerItem  = QtWidgets.QTreeWidgetItem()
#     item    = QtWidgets.QTreeWidgetItem()

#     for i in range(3):
#         parent = QtWidgets.QTreeWidgetItem(tree)
#         parent.setText(0, "Parent {}".format(i))
#         parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
#         for x in range(5):
#             child = QtWidgets.QTreeWidgetItem(parent)
#             child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
#             child.setText(0, "Child {}".format(x))
#             child.setCheckState(0, Qt.Checked)
#             for y in range(5):
#                 child2 = QtWidgets.QTreeWidgetItem(child)
#                 child2.setFlags(child2.flags() | Qt.ItemIsUserCheckable)
#                 child2.setText(0, "Child2 {}".format(y))
#                 child2.setCheckState(0, Qt.Checked)
#     tree.show() 

    
#     print(get_selectedItems(tree))
#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()

# import json
 
# # Opening JSON file
# ROOT_FILTER = 'EMG_Explorer_App\\Explorer_package\\processing\\'
# f = open('EMG_Explorer_App\\Explorer_package\\processing pipelines\\test.json')
# data = json.load(f)
# sig = np.random.randint(1,10,(1,10))
# print(data,sig)

# for nb,process in data.items():
#     func = PROCESSING[process['path']['name']]
#     arg = process['arguments']
#     arg[list(arg.keys())[0]] = x
#     x = func(arg)

# from custom_widget import comboBoxCheckable
# app     = QtWidgets.QApplication(sys.argv)

# list_ = ['b','rt','gh']
# combo = comboBoxCheckable()
# # combo.currentTextChanged.connect(lambda x: print(f'hi {x}'))
# combo.setData(list_)
# combo.show()
# sys.exit(app.exec_())




import plotly.express as px
from jinja2 import Template

# data_canada = px.data.gapminder().query("country == 'Canada'")
# fig = px.bar(data_canada, x='year', y='pop')

# output_html_path=r"EMG_Explorer_App/Template/test1/template1_filled.html"
# input_template_path = r"EMG_Explorer_App/Template/test1/template1.html"

# plotly_jinja_data = fig.to_html(full_html=False)
# #consider also defining the include_plotlyjs parameter to point to an external Plotly.js as described above

# arg = "<p> Other paragraph.</p> "
# data = {"fig":plotly_jinja_data,"arg":arg}

# with open(output_html_path, "w", encoding="utf-8") as output_file:
#     with open(input_template_path) as template_file:
#         j2_template = Template(template_file.read())
#         output_file.write(j2_template.render(data))

import pandas as pd

# def array_to_df(array):
#     return pd.DataFrame(array,columns=['y'],index=np.arange(len(array)))

# array = np.random.randint(1,10,(10,1))
# fig = px.box(array_to_df(array),y='y')

# fig.show()


import sys
from PyQt5.QtWidgets import QApplication, QMenu, QPushButton, QVBoxLayout, QWidget
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree, parameterTypes, registerParameterItemType,registerParameterType
# from custom_widget import ComboBoxExpandable

# class PopupMenuParameter2(parameterTypes.ActionParameter):
#     def __init__(self, **opts):
#         super().__init__(**opts)
#         self.button = ComboBoxExpandable()
#         self.sigActivated.connect(self.showMenuPopup)

#     def showMenuPopup(self):
#         self.button.menu.popup(QtGui.QCursor.pos())

# # # Custom parameter class
# # class PopupMenuParameter(parameterTypes.ActionParameter):
# #     def __init__(self, **opts):
# #         super().__init__(**opts)
# #         self.button = QtWidgets.QToolButton()
# #         self.menu = QMenu()
# #         self.button.setMenu(self.menu)
# #         self.button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
# #         print('menu created')
        

# #     def showMenu2(self):
# #         self.menu.popup(QtGui.QCursor.pos())

# #     def setData(self, value):
# #         self.append_element(value, self.menu)
# #         self.menu.triggered.connect(self.on_triggered)

# #     @QtCore.pyqtSlot(QtWidgets.QAction)
# #     def on_triggered(self, action):
# #         self.setText(action.text())
# #         path = [action.text()] 
# #         w = action.parentWidget()
# #         while w.parentWidget() and isinstance(w.parentWidget(), QtWidgets.QMenu):
# #             path.insert(0, w.title())
# #             w = w.parentWidget()
# #         self.pathChanged.emit(path)
# #         self.currentTextChanged.emit(self.text())

# #     @staticmethod
# #     def append_element(value, menu):
# #         if isinstance(value, list):
# #             for e in value:
# #                 PopupMenuParameter.append_element(e, menu)
# #         elif isinstance(value, dict):
# #             for k, v in value.items():
# #                 PopupMenuParameter.append_element(v, menu.addMenu(k))
# #         else:
# #             menu.addAction(value)

# if __name__ == "__main__":
#     app = QApplication([])

#     registerParameterType('popupmenu', PopupMenuParameter2, override=True)

#     # Create parameters
#     params = [
#         {'name': 'PopupMenuParameter', 'type': 'popupmenu', 'title': '+'},
#     ]

#     # Create parameter tree and set parameters
#     param_tree = ParameterTree()
#     parameter = Parameter.create(name='params', type='group', children=params)

#     param_tree.setParameters(parameter)
#     parameter.child('PopupMenuParameter').button.setData({"1":{"3":"4","5":"6"}})         
    
#     win = QWidget()
#     layout = QVBoxLayout()
#     layout.addWidget(param_tree)
#     win.setLayout(layout)
#     win.show()

#     sys.exit(app.exec_())


import os

# print(os.listdir('EMG_Explorer_App\Explorer_package\global_processing_pipelines'))
# print(os.path.isdir('EMG_Explorer_App\Explorer_package\global_processing_pipelines'))

# ROOT = 'EMG_Explorer_App\Explorer_package\global_processing_pipelines'


# def has_folder(ROOT):
#     for path in os.listdir(ROOT):
#         if os.path.isdir( ROOT + '\\' + path ):
#             return True
#     return False

# def dictOfFiles_from_EmbeddedFolders(ROOT):
#     list_process = []
#     PROCESS = {}

#     for path in os.listdir(ROOT):
#         if os.path.isdir( ROOT + '\\' + path ):
#             if has_folder(ROOT + '\\' + path ):
#                 PROCESS[path] = dictOfFiles_from_EmbeddedFolders(ROOT + '\\' + path)
#             else:
#                 PROCESS[path] = os.listdir( ROOT + '\\' + path )
#         else:
#             list_process.append(path)

#     if list_process != []:
#         PROCESS['general'] = list_process


#     return PROCESS
    


# pro = dictOfFiles_from_EmbeddedFolders(ROOT)
# print(pro)

list_t = ['general',1,3,'general']
list_t =  list(filter(lambda a: a != 'general', list_t))
print(list_t)