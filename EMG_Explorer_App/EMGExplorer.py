# from Explorer_package.requirement import *
from Explorer_package import *
from Explorer_package.loading_function import *
from PyQt5.QtCore import Qt
import os


def Try_decorator(function):
    print('in deco')
    def wrapper(*arg):
        try:
            function(*arg)
        except Exception as e:
            print(function.__name__)
            print(e)

    return wrapper

class OneSetting(pTypes.GroupParameter):
    delete_trigger = pyqtSignal('PyQt_PyObject')
    position_trigger = pyqtSignal('PyQt_PyObject','PyQt_PyObject')

    @Try_decorator
    def __init__(self, c_f,name,pos,p,path):
        self.function = c_f
        self.path = path
        self.position = pos
        self.parent_param = p
        opts = {'name':name}
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)



        # create parameters
        self.var = self.function.__code__.co_varnames[:self.function.__code__.co_argcount]
        var_default = self.function.__defaults__
        if var_default:
            var_default = [None for i in range(len(self.var)-len(var_default))] + list(var_default)
        else:
            var_default = [None for i in range(len(self.var))]
        
        #action
        self.addChild({'name': 'Functionality', 'type': 'group', 'children': [
        {'name': 'Delete', 'type': 'action'},
        {'name' : 'Position', 'type':'str','value':self.position}
        ]})
        self.param('Functionality','Delete').sigActivated.connect(self.oc_delete_handler)
        self.param('Functionality','Position').sigValueChanged.connect(self.oc_position_handler)


        #variables
        for i,v in enumerate(self.var):
            
            d = var_default[i]
            if d:
                self.addChild({'name': v, 'type': type(d).__name__, 'value': d, 'siPrefix': True})
            else:
                self.addChild({'name': v})
            self.param(v).sigValueChanged.connect(self.aChanged)

        self.exefunction = None
    
    def oc_delete_handler(self):
        print('in delete handler')
        self.delete_trigger.emit(self.position)

    def oc_position_handler(self,param,val):
        self.position_trigger.emit(self.position,val)


    def aChanged(self):
        print(' a ')
    
        


class Filters():
    """ParameterTree of filters
    """
    def __init__(self,list_f=None,path=None) -> None:
        self.listChildren = {} if not list_f else list_f
        self.nb = len(self.listChildren.keys())
        print('nb child init', self.nb)
        self.tree = ParameterTree()
        self.path = path
        
        self.CreateTree()

    
    @Try_decorator
    def addNew(self,c_f,path):
        """Add a filter

        Args:
            val (_type_): _description_
        """
        val = f"{path[-1]}_[{'_'.join(path[:-1])}] "
        setting = OneSetting(c_f,val,self.nb,self,path[:-1])
        setting.delete_trigger.connect(self.oc_delete)
        setting.position_trigger.connect(self.oc_position)
        
        self.p.addChild(setting)
        self.listChildren[self.nb] = setting
        print('child param added pos:', self.nb,setting)
        self.nb += 1

    def clearTree(self):
        self.p.clearChildren()
        self.nb = 0

    def CreateTree(self):
        print('In Tree Creation')
        if self.path:
            self.p = Parameter.create(name='params', type='group',children=list(self.listChildren.values()))
            # self.LoadJson()
            self.tree.addParameters(self.p)

        else:
            self.p = Parameter.create(name='params', type='group', children=list(self.listChildren.values()))
            self.tree.addParameters(self.p)

    def LoadJson(self,path):
        # self.p.clearChildren()
        self.path = path
        f = open(self.path)
        data = json.load(f)


        for pos,process in data.items():
            pos = int(pos) 

            if pos < self.nb:
                pos+=self.nb
            # get function
            func = get_item_from_path(PROCESSING,process['path'] + [process['name']])
            # get path
            path = process['path'] + [process['name']]
            # add new
            print('before add New',func, path)
            self.addNew(func,path)
            # change argument
            print('pos and process',pos,process)
            for name_arg,val_arg in process['arguments'].items():
                # put the default value
                print(name_arg,val_arg,self.listChildren[pos].param(name_arg).value())
                self.listChildren[pos].param(name_arg).setValue(val_arg)
                print(name_arg,val_arg,self.listChildren[pos].param(name_arg).value())

        

    def shift_position(self,new_nb,type,nb_current=None):
        if nb_current == None:
            print('shift default value')
            nb_current = self.nb 

        print('shiiiii1iif',nb_current, 'to',new_nb)

        # if abs(new_nb-nb_current) == 1:
        #     print('diff == 1')
        #     tmp = self.listChildren[new_nb]
        #     self.listChildren[new_nb] = self.listChildren[nb_current]
        #     self.listChildren[new_nb].position = new_nb
        #     self.listChildren[nb_current] = tmp
        #     self.listChildren[new_nb].position = new_nb

        # else:
        if type == 'add': # new_nb<nb_current
            for n in range(nb_current-1,new_nb-1,-1):
                print('add',n,'to',n+1)
                self.listChildren[n+1] = self.listChildren[n]
                self.listChildren[n+1].position = n + 1
                self.listChildren[n+1].param('Functionality','Position').setValue(n+1,blockSignal=self.listChildren[n+1].oc_position_handler)

        elif type == 'del': # new_nb>nb_current
            print('IN ELIF DEL',new_nb,nb_current )
            for n in range(nb_current,new_nb):
                print('del',n+1,'to',n)
                self.listChildren[n] = self.listChildren[n+1]
                self.listChildren[n].position = n 
                self.listChildren[n].param('Functionality','Position').setValue(n,blockSignal=self.listChildren[n].oc_position_handler)


    def oc_delete(self,nb):
        print(nb)
        self.p.removeChild(self.listChildren[nb])
        self.listChildren.pop(nb)
        if nb == self.nb-1:
            pass
        else:
            self.shift_position(nb,'del')
        self.nb -= 1
    
    def oc_position(self,nb,new_val):
        print(nb,new_val)
        new_val = int(new_val)
        self.p.removeChild(self.listChildren[nb])
        self.p.insertChild(new_val,self.listChildren[nb])

        
        self.listChildren[nb].position = new_val
        if nb > new_val:
            print('shift add', nb,new_val)
            child = self.listChildren[nb]
            self.shift_position(new_val,'add',nb)
            self.listChildren[new_val] = child
        if new_val > nb:
            print('shift del',nb,new_val)
            child = self.listChildren[nb]
            self.shift_position(new_val,'del',nb)
            self.listChildren[new_val] = child

    def setting_to_json(self):
        dictjson = {}
        for n in range(self.nb):
            setting = self.listChildren[n]
            dictjson[n]={'name':setting.function.__name__,
                         'path':setting.path,
                         'arguments':dict(zip(setting.var,[setting.param(v).value() for v in setting.var]))}

        print(dictjson)
        return dictjson


def deleteItemsOfLayout(layout):
     if layout is not None:
         while layout.count():
             item = layout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                 widget.setParent(None)
             else:
                 deleteItemsOfLayout(item.layout())


class Layout_Parameters_Type(QWidget):
    signal_IndependantDataChecked = pyqtSignal(bool)
    selectedDataChanged = pyqtSignal()

    def __init__(self,p=None):
        self.parent = p
        super().__init__()
        loadUi( 'hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\layout_parameters_type.ui',self)
        self.layout_param = self.vlayout_parameters
        self.selectedData = {}

    # tab data interactivity
        self.selectDataWindow = None
        self.groupBox_dataSelection.clicked.connect(self.oc_groupBoxChecked)
        self.button_select.clicked.connect(self.oc_selectData)

        self.dataIndependent = False

    def oc_selectData(self):
        if self.selectDataWindow is None:
            self.selectDataWindow = WindowChannelSelection(self.parent)
            self.selectDataWindow.sendData.connect(self.save_selectedData)
        self.selectDataWindow.show()

    def save_selectedData(self,dictData):
        print('save selection data')
        # from dict Data to actual data
        loader = self.parent.get_currentLoader()
        self.selectedData = loader.get_DataFromDict(dictData)

        print('selected DATA',self.selectedData)
        self.selectedDataChanged.emit()
        self.selectDataWindow.close()

        # TAB DATA
    def isDataIndependent(self):
        return self.dataIndependent
    
    def get_data(self):
        return self.selectedData
    
    def oc_groupBoxChecked(self,state):
        if state :
            self.dataIndependent = True
            
        #::::: update list graph ?
        else:
            self.dataIndependent = False

        #::update list graph ?




class OneGraph():
    def __init__(self,frame_graph,layout_parameters,i,parent) -> None:
        """Creates an object that will manage the event of a box

        Args:
            frame_graph (frame): frame of the main windows were the widget should be displayed
            layout_parameters (layout): layout of the main windows were the parameters of the object should be displayed
            i (int): id of the widget
            parent (mainWindow): mainWindow
        """

        self.ui_graph = None
        self.id = i
        self.parent = parent
        
        
        # Init layout of the parameters box
        self.ui_parameters = Layout_Parameters_Type(self.parent)
        for fc in [None] + list(PLOT.keys()):
            self.ui_parameters.comboBox_type.addItem(fc)
        self.layout_parameters = layout_parameters
        self.selectedData = None

        # Init layout of the graph box
        self.layout_graph = QGridLayout()
        self.b = QPushButton()
        self.layout_graph.addWidget(self.b)
        frame_graph.setLayout(self.layout_graph)

        self.b.clicked.connect(self.oc_Buttonclick)
        self.ui_parameters.comboBox_type.currentIndexChanged.connect(self.oc_comboBox_type_change)

        # DATA, layout interactivity
        self.ui_parameters.selectedDataChanged.connect(self.update_drawing)

        

    # TAB PARAMETERS
    def oc_Buttonclick(self):
        """Opens the menu of the current box
        """
        self.add_paramUi_to_layout()
        self.parent.current_id = self.id
        try:
            self.ui_graph.update_settings()
        except: pass


    def oc_comboBox_type_change(self):
        """Changes the graph of the current box
        """
        type_ = self.ui_parameters.comboBox_type.currentText()
        if type_:
            self.setPlot(PLOT[type_])
            self.add_graphUi_to_layout()
            data = self.ui_graph.get_data()
            self.ui_graph.draw(data)
        else:
            self.ui_graph.clearGraph()

    
    
    def get_selectedData(self):
        return self.selectedData

    # GRAPH
    def retrieve_Data(self):
        print('retrieve_data')
        if not self.ui_parameters.isDataIndependent():
            # retrieve data from the mainwindow
            data = self.ui_graph.get_data()
            print('retrive not independent data',data)

            

        else:
            #retrieve data from the parameters
            data = self.ui_parameters.get_data()
            print('retrive independent data',data)

        print('retrieved dataaaa', data)
        return data
    
    def update_drawing(self):
        if self.ui_graph:
            self.ui_graph.clearGraph()
            data = self.retrieve_Data()
            print('update drawing',data)

            self.ui_graph.draw(data)

    def add_paramUi_to_layout(self):
        """Changes the settings of the graph
        """
        print('add layout ')
        deleteItemsOfLayout(self.layout_parameters)
        self.layout_parameters.addWidget(self.ui_parameters)
        self.parent.tabWidget.setCurrentIndex(0)

    def add_graphUi_to_layout(self):
        """add a graph to the box
        """
        deleteItemsOfLayout(self.layout_graph)
        self.layout_graph.addWidget(self.b)
        if self.ui_graph:
            self.layout_graph.addWidget(self.ui_graph)

    def add_setting_to_param(self):
        """Add settings to the parameters box
        """
        deleteItemsOfLayout(self.ui_parameters.layout_param)
        self.ui_parameters.layout_param.addWidget(self.ui_graph.l)


    def setPlot(self,plot):
        """Set the plot of the current object

        Args:
            plot (_type_): _description_
        """
        self.ui_graph = plot(self.layout_parameters,
                            self.layout_graph,
                            self.id,
                            self.parent)
        self.add_setting_to_param()

    def clearPlot(self):
        if self.ui_graph:
            self.ui_graph.clearGraph()



def walkDatatree_setAttrDataset(info,node):

    if type(list(info.values())[0]) == dict:
        for name,child_dict in info.items():
            child_node = QTreeWidgetItem(node)
            child_node.setText(0, str(name))
            walkDatatree_setAttrDataset(child_dict,child_node)
                
    else: 
        for k,v in info.items():
            child_node = QTreeWidgetItem(node)            
            child_node.setText(0,str(k))
            child_node.setText(1,str(v))
        return info
        
    
    return info
                    


class Layout(QWidget):
    def __init__(self,nb,nb_v=1):
        super().__init__()
        loadUi(f'hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\Layout{nb}_{nb_v}.ui', self)


# class NewFilterWindow(QWidget):

#     # automatic name after preprocessing function + nb of the step
#     # param : add, delete, change position

#     def __init__(self):
#         super().__init__()
#         # self.parent = parent
#         loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\GraphParameters.ui', self)




class WindowChannelSelection(QWidget):
    sendData = pyqtSignal('PyQt_PyObject')
    
    def __init__(self,p):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\Form_selection_channels.ui', self)
        self.p = p
        self.dictSelection = {}

        self.tree = QtWidgets.QTreeWidget()
        loader = self.p.get_currentLoader()
        dict_group = loader.getGroup()

        self.button_selectAll.clicked.connect(partial(self.oc_selectAll,self.tree.invisibleRootItem()))
        self.button_deselectAll.clicked.connect(partial(self.oc_deselectAll,self.tree.invisibleRootItem()))
        self.button_Select.clicked.connect(self.oc_select)

        for gr in list(dict_group.keys()):
            item_group = QtWidgets.QTreeWidgetItem(self.tree)
            item_group.setText(0,str(gr))
            item_group.setFlags(item_group.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for v in list(dict_group[gr].keys()):
                item_var = QtWidgets.QTreeWidgetItem(item_group)
                item_var.setFlags(item_var.flags() | Qt.ItemIsUserCheckable)
                item_var.setText(0,str(v))
                item_var.setCheckState(0, Qt.Unchecked)

                for dim_name,ch in list(dict_group[gr][v].items()):
                    item_dim = QtWidgets.QTreeWidgetItem(item_var)
                    item_dim.setFlags(item_dim.flags() | Qt.ItemIsUserCheckable)
                    item_dim.setText(0,str(dim_name))
                    item_dim.setCheckState(0, Qt.Unchecked)

                    for c in ch:
                        item_ch = QtWidgets.QTreeWidgetItem(item_dim)
                        item_ch.setFlags(item_ch.flags() | Qt.ItemIsUserCheckable)
                        item_ch.setText(0,str(c))
                        item_ch.setCheckState(0, Qt.Unchecked)

        self.layout_tree.addWidget(self.tree)

    def oc_deselectAll(self,item):
        nb_children = item.childCount()
        item.setCheckState(0, Qt.Unchecked)

        if nb_children > 0:

            for i in range(nb_children):
                self.oc_deselectAll(item.child(i))
  

    def oc_selectAll(self,item):
        nb_children = item.childCount()
        item.setCheckState(0, Qt.Checked)

        if nb_children > 0:
            for i in range(nb_children):
                self.oc_selectAll(item.child(i))
      

    def get_selectedItems(self): 

        def has_childLeaf(item):
            nb_children = item.childCount()
            for i in range(nb_children):
                child = item.child(i)
                nb_chil_children = child.childCount()
                if nb_chil_children > 0:
                    return False
            return True
                    
            
        def recurse(item):
                list_dict = {}
                if has_childLeaf(item):
                    list_checked = []
                    for j in range(item.childCount()):
                         if  item.child(j).checkState(0) == Qt.Checked :
                            list_checked.append(item.child(j).text(0))
                    return list_checked 
                    
                else:
                    for i in range (item.childCount()):
                        list_dict[item.child(i).text(0)] = recurse(item.child(i))
                return list_dict
        
        return recurse(self.tree.invisibleRootItem())

    def oc_select(self):
        dictData= self.get_selectedItems()
        self.sendData.emit(dictData)



    # @Try_decorator
    # def init_menu(self):
    #     self.toolbutton = QtWidgets.QToolButton(self)
    #     self.toolbutton.setText('Group')
    #     self.toolmenu = QtWidgets.QMenu(self)

    #     file_name = self.p.listWidget_file.currentItem().text()
    #     actionSelectAll = self.toolmenu.addAction('Select all')
    #     actionSelectAll.setCheckable(True)
    #     actionSelectAll.triggered.connect(self.oc_selectAllGroup)
    #     actionDeselectAll = self.toolmenu.addAction('Deselect all')
    #     actionDeselectAll.setCheckable(True)
    #     actionDeselectAll.triggered.connect(self.oc_deselectAllGroup)

    #     #add to layout
    #     self.lcomboBox_group.addWidget(self.toolbutton)
    #     print('dict group selection',self.p.dataLoader[file_name].dict_group)
    #     for group in self.p.dataLoader[file_name].dict_group.keys():
    #         print('groupe selection init',group)
    #         action = self.toolmenu.addAction(group)
    #         action.setCheckable(True)
    #         action.triggered.connect(partial(self.oc_groupChecked,group))
    #     self.toolbutton.setMenu(self.toolmenu)
    #     self.toolbutton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    # def init_menuVar(self):
    #     self.toolbuttonVar = QtWidgets.QToolButton(self)
    #     self.toolbuttonVar.setText('Variable')
    #     self.toolmenuVar = QtWidgets.QMenu(self)

    #     # interactivity
    #     actionSelectAll = self.toolmenuVar.addAction('Select all')
    #     actionSelectAll.setCheckable(True)
    #     actionSelectAll.triggered.connect(self.oc_selectAllVar)
    #     actionDeselectAll = self.toolmenuVar.addAction('Deselect all')
    #     actionDeselectAll.setCheckable(True)
    #     actionDeselectAll.triggered.connect(self.oc_deselectAllVar)

    #     # add to layout
    #     self.lcomboBox_var.addWidget(self.toolbuttonVar)
    #     self.toolbuttonVar.setMenu(self.toolmenuVar)
    #     self.toolbuttonVar.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    # def update_variable(self,group,type):

    #     file_name = self.p.listWidget_file.currentItem().text()
    #     dict_group = self.p.dataLoader[file_name].dict_group

    #     if type == 'add':
    #         # add variable
    #         for var in list(dict_group[group].keys()):
    #             action = self.toolmenuVar.addAction(f'{var}/{group}')
    #             action.setCheckable(True)
    #             action.triggered.connect(partial(self.oc_varChecked,group,var))
    #     else:
    #         # delete variables
    #         for a in self.toolmenuVar.actions():
    #             if a.text().split('/')[-1] == group:
    #                 self.toolmenuVar.removeAction(a)

    # def update_channel(self,group,var,type):

    #     file_name = self.p.listWidget_file.currentItem().text()
    #     dict_group = self.p.dataLoader[file_name].dict_group
    #     channels = list(dict_group[group][var].keys())

    #     if len(channels)!=0:
    #         channels =  dict_group[group][var][channels[0]]

    #         if type == 'add':
    #             for ch in channels:
    #                 item = QListWidgetItem(f'{ch}/var/group')
    #                 self.listWidget.addItem(item)
    #                 item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    #                 item.setCheckState(Qt.Unchecked)
    #                 # item.itemChanged.connect(self.oc_itemChanged)

    # def oc_oc_itemChanged(self,item):
    #     if item.isChecked():
    #         pass#::::::::::
    #     else:
    #         pass
    #     #:::::::::::::::::::

    # def oc_groupChecked(self,group,checked):
    #     if checked:
    #         self.dictSelection[group] = {}
    #         self.update_variable(group,'add')
    #     else:
    #         try:
    #             self.dictSelection.pop(group)
    #             self.update_variable(group,'del')
    #         except:
    #             print('no group in dict selection')


    # def oc_varChecked(self,group,var,checked):
    #     if checked:
    #         self.dictSelection[group][var] = []
    #         self.update_channel(group,var,'add')

    #     else:
    #         try:
    #             self.dictSelection[group].pop(var)
    #             self.update_channel(group,var,'del')

    #         except:
    #             print('no var in group in dict Selection')


    # def oc_selectAllGroup(self):
    #     for a in self.toolmenu.actions():
    #         a.setChecked(True)

    # def oc_deselectAllGroup(self):
    #     for a in self.toolmenu.actions():
    #         a.setChecked(False)

    # def oc_selectAllVar(self):
    #     for a in self.toolmenuVar.actions():
    #         a.setChecked(True)

    # def oc_deselectAllVar(self):
    #     for a in self.toolmenuVar.actions():
    #         a.setChecked(False)


class SummaryWindow(QWidget):

    generateSummary = pyqtSignal(dict)

    def __init__(self,parent):
        super().__init__()
        # self.parent = parent
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\AnalysisWin.ui', self)
        self.p = parent
        self.init_layout()
        self.init_interactivity()

        self.processing = ''

        self.group_list = []
        self.var_list = []

        self.checkBox_current.setChecked(True)
        self.groupBox_load.setChecked(False)
        self.file_list = [loader.getPath() for loader in list(self.p.dataLoader.values())]

        self.save_path = ''
        self.save_processing = False

        
    
    
    def init_layout(self):

        self.label_savePath.setWordWrap(True)

        self.comboGr = comboBoxCheckable('Group')
        self.comboVar = comboBoxCheckable('Variable')
        loader = self.p.get_currentLoader()
        group_names = loader.getListGroup()
        var_names = loader.getListVariable()

        self.comboGr.setData(group_names)
        self.comboVar.setData(var_names)

        self.layout_GrVarCh.addWidget(self.comboGr)
        self.layout_GrVarCh.addWidget(self.comboVar)

        self.comboExpandable_processing = ComboBoxExpandable()
        self.comboExpandable_processing.setData(PROCESSING_NAME)
        self.layout_comboBoxExpandable_processing.addWidget(self.comboExpandable_processing)

        menuJson = create_menuJson(PATH_PIPELINE)
        self.comboExpandable_processing.append_element(['None'],self.comboExpandable_processing.menu())
        self.comboExpandable_processing.append_element(menuJson,self.comboExpandable_processing.menu())

        self.comboExpandable_processing.pathChanged.connect(self.oc_comboBoxExp)
    

    def init_interactivity(self):
        self.checkBox_current.stateChanged.connect(self.oc_checkBoxCurrent)
        self.groupBox_load.clicked.connect(self.oc_groupBoxLoad)
        self.button_generate.clicked.connect(self.oc_buttonGenerate)
        self.button_select.clicked.connect(self.oc_buttonSelect)
        self.button_selectSavePath.clicked.connect(self.oc_buttonSelectSavePath)

    def oc_comboBoxExp(self,path):
        self.processing = path

    def oc_checkBoxCurrent(self,state):
        if state :
            self.groupBox_load.setChecked(False)
            self.file_list = [loader.getPath() for loader in list(self.p.dataLoader.values())]
        else:
            self.file_list = []

    def oc_groupBoxLoad(self,state):
        if state:
            self.file_list = []
            self.checkBox_current.setChecked(False)

        else:
            self.listWidget_path.clear()
            self.file_list = []

    def oc_cuttonClear(self):
        self.listWidget_path.clear()

    def oc_buttonSelect(self):
        file_list = QFileDialog.getOpenFileNames(self, 'Open File',)[0]
                                       #"/home/jana/untitled.png",
                                    #    "Json (*.json)")
        for file in file_list:
            if file not in self.file_list:
                self.file_list.append(file)
                self.listWidget_path.addItem(file)
                                

        
    def oc_buttonSelectSavePath(self):
        self.save_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.label_savePath.setText(self.save_path)


    def oc_buttonGenerate(self):
        if self.save_path == '':
            dlg = QtWidgets.QMessageBox.warning(self, '!','No path for saving')

        dict_generation = {

            'processing': self.processing,
            'group list': self.group_list,
            'variable list':self.var_list,
            'file list':self.file_list,
            'path save':self.save_path,
            'save processing':self.checkBox_saveProcessing.isChecked(),
        }
        print('SUMMARY GENERATION', dict_generation)



    

class Canvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        super().__init__(self.fig)

    def clear(self):
        self.fig.clear()


class EMGExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Loading of the UI
        loadUi('hdemg_viewer_exemple\\Qt_creator\\EMGExplorer_qt\\EMGExplorer_mainwindow_base.ui', self)

        # Initialisation of variables
        self.w = None
        self.wnewFilter = None
        self.layout = Layout(3,1)
        self.dock = {}
        # Restores the previous state of the app
        self.restoreSettings()

        #
        self.dataLoader = {}
        self.layout_param = self.layout_parameters


        ## MENU
        # Definition of the action
        self.actiontype_1.triggered.connect(self.oc_actiontype1)
        self.actionNew.triggered.connect(self.oc_newFilter)
        self.actionRun_Analysis.triggered.connect(self.oc_newSummary)
        self.actionLoad.triggered.connect(self.oc_load_files)

        self.action4_windows.triggered.connect(partial(self.oc_update_layout_graph,4,1))
        self.action3_windows.triggered.connect(partial(self.oc_update_layout_graph,3,1))

        # Information window
        self.treeWidget.itemDoubleClicked.connect(self.oc_itemPressed)
        
        self.nb_layout = 3
        self.nb_version = 1

        ## GRAPH

        self.time = np.arange(100)
        self.signal = np.random.random(100)
        self.current_id = 0

        self.update_list_layout_graph()
        # self.initialize_layout_graph()
        
   
        self.interactivity_fileSystem()
      

        # SETTINGS INIT
        # self.setting = {0:OneSetting(None,'Custom parameter')}
        

        self.paramtree = Filters(None)
        self.layout_setting.addWidget(self.paramtree.tree)
        self.button_openJson.clicked.connect(self.oc_openFilter)
        self.button_clearFilter.clicked.connect(self.paramtree.clearTree)


        self.comboExpandable = ComboBoxExpandable()
        self.comboExpandable.setData(PROCESSING_NAME)
        self.layout_expComboBox.addWidget(self.comboExpandable)

        self.comboExpandable.pathChanged.connect(self.oc_add_filter)
        self.button_saveFilter.clicked.connect(self.oc_saveFilter)

        
        print('iiiiiiniiit')


        self.show()

    def oc_openFilter(self):
        # get path
        path = QFileDialog.getOpenFileName(self, 'Open File',)
                                       #"/home/jana/untitled.png",
                                    #    "Json (*.json)")
        #open filter
        print('path open is', path)
        self.paramtree.LoadJson(path[0])

    def oc_clearFilter(self):
        self.paramtree.clearTree()


    def oc_add_filter(self,path):
        """add a filter to the pipeline

        Args:
            path (str): path to the clicked section of the menu. eg ['group 1','name']
        """
        print(path)
        print(get_item_from_path(PROCESSING,path))
        self.paramtree.addNew(get_item_from_path(PROCESSING,path),path )

    def oc_saveFilter(self):
        dictjson = self.paramtree.setting_to_json()
        namepath = QFileDialog.getSaveFileName(self, 'Save File',
                                       #"/home/jana/untitled.png",
                                       "Json (*.json)")
        if os.path.exists(f'{namepath[0]}.json'):
            print('the file exist already')
        else:
            with open(f'{namepath[0]}.json', 'w') as f:
                json.dump(dictjson, f)


    def get_dataChannel(self):
        file_name = self.listWidget_file.currentItem().text()
        loader = self.dataLoader[file_name]
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()
        ch = self.comboBox_dim.currentText()
        dim = self.label_timeline_dim.text()
        
        return loader.getData(group,var,dim,ch)
    
    def get_dataVariable(self):
        file_name = self.listWidget_file.currentItem().text()
        loader = self.dataLoader[file_name]
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()
        dim = self.label_timeline_dim.text()
        
        return loader.getDataVariable(group,var,dim)
    
    def get_currentPlot(self):
        return self.dict_layout_graph[self.current_id]

    
    def update_list_layout_graph(self):
        """Updates the variable dict_layout_graph
        Create a dictionnary with the layout that can be used to display graphs 
        { id : Gridlayout}
        """
        self.dict_layout_graph = {}
        i = 0
        for frame in self.layout.findChildren(QFrame):
            if 'graph' in frame.objectName().split('_'):
            
                self.dict_layout_graph[i] = OneGraph(frame,self.layout_param,i,self)
                i += 1

    

      
        
    def oc_update_layout_graph(self,nb,nb_v):
        """Changes the layout of of the graphs. update the displayed plot

        Args:
            nb (int): number of graphs
            nb_v (int): number cooresponding to the layout of the graphs
        """
        # update the number of windows in the graph
        self.gridLayout_3.removeWidget(self.layout)
        self.layout.deleteLater()
        self.nb_layout = nb
        self.nb_version = nb_v
        self.layout = Layout(nb,nb_v)
        self.gridLayout_3.addWidget(self.layout)

        # update the list of the frames used to display graph
        self.update_list_layout_graph()


    def update_parameters_win(self,graph_id):
        param = self.dict_displayed_graph[graph_id]['param']
        # if the same type of graph is displayed




    def oc_newFilter(self):
        if self.wnewFilter is None:
            # self.wnewFilter = NewFilterWindow()
            self.wnewFilter = WindowChannelSelection(self)
        self.wnewFilter.show()



    def oc_newSummary(self):
        if self.w is None:
            self.w = SummaryWindow(self)
        self.w.show()
        


    def oc_itemPressed(self, item, int_col):
        if int_col!=0:
            text, ok = QInputDialog().getText(self, "input",
                                            "data:", QLineEdit.Normal,
                                     item.text(int_col))
            if ok and text:
                item.setText(int_col,text)



    def oc_action1(self):
        self.oc_actiontype1()



    def oc_actiontype1(self):
        self.dock[self.nb_dock] = QDockWidget('dock',self)
        self.dock[self.nb_dock].setObjectName(f'dock {self.nb_dock}')

        self.dock[self.nb_dock].visibilityChanged.connect(partial(self.oc_visibility,self.nb_dock))
        self.dock[self.nb_dock].setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dock[self.nb_dock])
        self.nb_dock +=1


    def oc_visibility(self,dock,visibility):
        #### !! PB: error bc called when the win closes
        if not visibility:
            self.removeDockWidget(self.dock[dock])
            self.dock[dock].deleteLater()
            del self.dock[dock]
            # self.widget_name = None

    
    def restoreSettings(self):
        """Restores the last state of the app
        """
        name_folder = 'ExplorerEMG'
        name_seting = 'MyLayout'

        settings = QSettings(name_folder, name_seting)

        # restore general layout and window state
        geometry = settings.value("geometry", QByteArray())
        self.restoreGeometry(geometry)
        state = settings.value("windowState", QByteArray())
        self.restoreState(state)

        self.nb_layout = settings.value("nb_layout", QByteArray())
        self.nb_version = settings.value("nb_version", QByteArray())
        self.layout = Layout(self.nb_layout,self.nb_version)
        self.gridLayout_3.addWidget(self.layout)

        # restore splitters state
        for splitter in self.findChildren(QSplitter):
            try:
                splitterSettings=settings.value(splitter.objectName())
                if splitterSettings:
                    splitter.restoreState(splitterSettings)
            except Exception as e:
                print(e)

        #restore dock
        self.nb_dock = 0
        while(True):

            dockSetting = settings.value(f'dock {self.nb_dock}')

            if dockSetting:
                self.dock[self.nb_dock] = QDockWidget(f'dock {self.nb_dock}',self)
                self.dock[self.nb_dock].setObjectName(f'dock {self.nb_dock}')

                self.dock[self.nb_dock].visibilityChanged.connect(partial(self.oc_visibility,self.nb_dock))
                self.addDockWidget(Qt.RightDockWidgetArea,self.dock[self.nb_dock])
                self.dock[self.nb_dock].restoreGeometry(dockSetting)                    
                self.nb_dock += 1
            else:
                break
            



    def closeEvent(self, event):
        """Function triggered when the mainwindow is closed

        Args:
            event ( ): event
        """
        name_folder = 'ExplorerEMG'
        name_seting = 'MyLayout'        
        settings = QSettings(name_folder, name_seting)
        settings.clear()

        # save general layout and window states
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("nb_layout",self.nb_layout)
        settings.setValue("nb_version",self.nb_version)

        # save splitters state
        for splitter in self.findChildren(QSplitter):
            splitterSettings=splitter.saveState()
            if splitterSettings:
                settings.setValue(splitter.objectName(), splitter.saveState()) 

        # save dock state
        i = 0
        for id,dock in self.dock.items():
            dockSettings = dock.saveGeometry()
            if dockSettings:
                settings.setValue(f'dock {i}', dock.saveGeometry()) 
                i += 1


        # save tab state







    ## FILES MANAGEMENT

    def oc_load_files(self):
        # load the paths
        files,extension = QFileDialog.getOpenFileNames(self, 'Open file',  'C:\\Users\\mtlsa\\Documents\\UTC\\GB05\\TX\\Python_EMGExplorer\\data',"files (*.*)")
        
        self.dataLoader = load_multiple_files(files)

        # update the list
        for loader in self.dataLoader.keys():
            self.listWidget_file.addItem(loader)

    def get_currentLoader(self):
        file_name = self.listWidget_file.currentItem().text()
        return self.dataLoader[file_name]



    # COMBOBOX FILE SYSTEM   
    def update_fileSystem_comboBox_Group(self):
        print('update group')
        """Add the group paths to the comboBox
        """
        # remove previous items
        self.comboBox_group.clear()

        # select current Item
        file_name = self.listWidget_file.currentItem()
        if file_name == None:
            self.listWidget_file.setCurrentRow(0)
        
        file_name = self.listWidget_file.currentItem().text()

        for group in self.dataLoader[file_name].dict_group.keys():
            self.comboBox_group.addItem(group)


    def update_fileSystem_comboBox_Variable(self):
        print('update var')
        """Add the data variables that matches the selected group in the comboBox
        """
        # remove previous items
        self.comboBox_variable.clear()

        file_name = self.listWidget_file.currentItem().text()
        dict_group = self.dataLoader[file_name].dict_group
        group = self.comboBox_group.currentText()

        for var in list(dict_group[group].keys()):
            self.comboBox_variable.addItem(var)


    def update_fileSystem_comboBox_Channel(self):
        print('update ch')
        """Add the channels that matches with the selected variables
        """
        self.comboBox_dim.clear()

        file_name = self.listWidget_file.currentItem().text()
        dict_group = self.dataLoader[file_name].dict_group
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()


        dims = list(dict_group[group][var].keys())

        if len(dims) != 0:
            self.label_timeline_dim.setText(str(dims[0]))
            for item in dict_group[group][var][dims[0]]:
                self.comboBox_dim.addItem(str(item))
        else:
            self.label_timeline_dim.setText('no dim')
            self.comboBox_dim.addItem('None')

        self.oc_comboBox_dim_change()


    def clearAllPlot(self):
        for plot in list(self.dict_layout_graph.values()):
           plot.clearPlot() 

    # file system interactivity
    def oc_ListWidget_change(self,item):    
        print('oc widget')    
        last_selection = self.comboBox_group.currentText()
        self.update_fileSystem_comboBox_Group()
        self.comboBox_group.setCurrentIndex(np.max([0,self.comboBox_group.findText(last_selection)])) 
        # find TExt return -1 if there is no match

        # update comboBox variable
        self.oc_comboBox_group_change()
        self.oc_comboBox_variable_change()

        # load attrs
        loader = self.get_currentLoader()
        loader.loadAttributs()

        if loader.attrs:
            walkDatatree_setAttrDataset(loader.attrs,self.treeWidget)
        
       

    def oc_comboBox_group_change(self,):
        """When triggered, the list of variable is changed, the plot are eventually cleared or updated
        """
        print('oc combo')

        last_selection = self.comboBox_variable.currentText()
        # update the list of variables

        self.update_fileSystem_comboBox_Variable()
        foundText = self.comboBox_variable.findText(last_selection)
        self.comboBox_variable.setCurrentIndex(np.max([0,foundText]))

        #clear the plot if the last variable selected is not in the new list
        if foundText == -1:
            self.clearAllPlot()

        else:
            self.oc_comboBox_dim_change()

      


    def oc_comboBox_variable_change(self,):
        """When a variable is selected, the list of displayable channels are changed
        """
        print('oc var')
        self.update_fileSystem_comboBox_Channel()

    def oc_comboBox_dim_change(self,):
        for plot in self.dict_layout_graph.values():
            try:
                plot.update_drawing()
            except:
                pass


    def interactivity_fileSystem(self):
        self.listWidget_file.currentItemChanged.connect(self.oc_ListWidget_change)
        self.comboBox_group.textActivated.connect(self.oc_comboBox_group_change)
        self.comboBox_variable.textActivated.connect(self.oc_comboBox_variable_change)
        self.comboBox_dim.textActivated.connect(self.oc_comboBox_dim_change)


        


def main():
    app = QApplication(sys.argv)
    ex = EMGExplorer()
    ex.raise_()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()







# all in one file
# print(dir(exp.processing_function))

# import processing function
# print(os.listdir('EMG_Explorer_App/Explorer_package/processing'))
#['processing1.py', 'processing2.py', '__pycache__']


# from importlib.machinery import SourceFileLoader
 
# mod_list = []
# for name in os.listdir('EMG_Explorer_App/Explorer_package/processing'):
#     if name != '__pycache__':
#         mod_list += [name[:-3]]

# # imports the module from the given path
# PROCESSING = {}
# for name in mod_list:
#     mod = SourceFileLoader(name,f"EMG_Explorer_App/Explorer_package/processing/{name}.py").load_module()
#     PROCESSING[name] = {}

#     for fc_name in dir(mod):
#         fc = getattr(mod,fc_name)
#         if fc_name[0] != '_':
#             PROCESSING[name][fc_name] = fc

# # print(PROCESSING)
            
# PROCESSING['processing1']['add']()



# self.graph = pg.GraphicsLayoutWidget(border=pg.mkPen((0, 0, 0)))
# self.timeplot = self.graph.addPlot(row=0, col=0, rowspan=1, colspan=1)
# self.fftplot = self.graph.addPlot(row=1, col=0, rowspan=1, colspan=1)

# self.timeplot.plot(x=self.time, y=self.signal, pen=pen)
# self.timeplot.setMouseEnabled(x=True, y=False)
# self.timeplot.setLimits(xMin=0, xMax=self.time.max())
# self.timeplot.autoRange()
# self.timeplot.showGrid(x=True)
# self.timeplot.setMenuEnabled(False)
# self.timeplot.setLabel('left', "Channel {} - EMG".format(elec_id), "")
# self.timeplot.setLabel('bottom', "time", "s")
# self.timeplot.sigXRangeChanged.connect(self.update_fft)
# self.timepoint = pg.InfiniteLine(0,pen=pg.mkPen({'color': "#FF0", 'width': 4}))  # pg.CurvePoint(self.timeplot.curves[0])
# self.timeplot.addItem(self.timepoint)
# # arrow = pg.ArrowItem(angle=-90)
# # arrow.setParentItem(self.timepoint)

# self.fftplot.plot(self.time, self.signal, pen=pen)
# self.fftplot.setMouseEnabled(x=True, y=False)
# self.fftplot.showGrid(x=True)
# self.fftplot.setMenuEnabled(False)
# self.fftplot.setLabel('left', "Channel {} - Power".format(elec_id), "")
# self.fftplot.setLabel('bottom', "frequency", "Hz")
# self.fftplot.curves[0].setFftMode(True)
# self.fftplot.enableAutoRange(True)

# self.rvbox.addWidget(self.graph)
# self.ploted = True


# fct = 'rms'
#         gridvar = numpy.apply_along_axis(eval("self.{}".format(fct)), 2, gridvar) #fonctionne sans le self et rms une fonction normal ?

# @staticmethod
#     def rms(x):
#         return numpy.sqrt(x.dot(x) / x.size)