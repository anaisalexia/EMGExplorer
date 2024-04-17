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

    @Try_decorator
    def __init__(self, name):
        opts = {'name':name}
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        self.addChild({'name': 'Delete', 'type': 'action'},)
        self.addChild({'name': 'pos = x', 'type': 'float', 'value': 0, 'siPrefix': True})
        self.addChild({'name': 'A = ...', 'type': 'float', 'value': 7, 'suffix': 'Hz', 'siPrefix': True})
        self.addChild({'name': 'B = ...', 'type': 'float', 'value': 1/7., 'suffix': 'Hz', 'siPrefix': True})
        self.a = self.param('A = ...')
        self.b = self.param('B = ...')
        self.a.sigValueChanged.connect(self.aChanged)
        self.b.sigValueChanged.connect(self.bChanged)
        self.exefunction = None

    def aChanged(self):
        self.b.setValue(1.0 / self.a.value(), blockSignal=self.bChanged)

    def bChanged(self):
        self.a.setValue(1.0 / self.b.value(), blockSignal=self.aChanged)

class addOneSetting(pTypes.GroupParameter):
    def __init__(self, parent_ ):
        opts = {'name':'add'}
        opts['type'] = 'group'
        opts['addText'] = "Add"
        self.dict_filter = {'filter1':'name1'}
        opts['addList'] = list(self.dict_filter.keys())
        self.parent_ = parent_ 
        pTypes.GroupParameter.__init__(self, **opts)
    
    def addNew(self, typ):
        val = self.dict_filter[typ]
        self.parent_.addNew(val)
        


class Filters():
    def __init__(self,list_f=None) -> None:
        self.listFilters = {} if not list_f else list_f
        self.nb = len(self.listFilters.keys())
        self.tree = ParameterTree()
        # self.add = addOneSetting(self)
        # self.listFilters[self.nb] =self.add
        self.nb += 1
        self.CreateTree()
    
    @Try_decorator
    def addNew(self,val):
        setting =OneSetting(val)
        print(setting)
        self.p.addChild(setting)
        # self.p.removeChild(self.p.children()[1])
        # self.p.addChild(OneSetting(val))
        # self.p


    def addFilter(self,filter):
        self.listFilters[self.nb] = filter
        # self.listFilters[self.nb].param('delete', 'delete').sigActivated.connect(delete)

        self.nb += 1

    def CreateTree(self):
        print(self.listFilters)
        self.p = Parameter.create(name='params', type='group', children=list(self.listFilters.values()))
        self.tree.addParameters(self.p)

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
    def __init__(self):
        super().__init__()
        loadUi( 'hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\layout_parameters_type.ui',self)
        self.layout_param =self.vlayout_parameters



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
        self.ui_parameters = Layout_Parameters_Type()
        for fc in [None] + list(PLOT.keys()):
            self.ui_parameters.comboBox_type.addItem(fc)
        self.layout_parameters = layout_parameters


        # Init layout of the graph box
        self.layout_graph = QGridLayout()
        self.b = QPushButton()
        self.layout_graph.addWidget(self.b)
        frame_graph.setLayout(self.layout_graph)


        self.b.clicked.connect(self.oc_Buttonclick)
        self.ui_parameters.comboBox_type.currentIndexChanged.connect(self.oc_comboBox_type_change)


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

    def update_drawing(self):
        self.ui_graph.clearGraph()
        data = self.ui_graph.get_data()
        self.ui_graph.draw(data)

    def add_paramUi_to_layout(self):
        """Changes the settings of the graph
        """
        deleteItemsOfLayout(self.layout_parameters)
        self.layout_parameters.addWidget(self.ui_parameters)

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


class NewFilterWindow(QWidget):

    # automatic name after preprocessing function + nb of the step
    # param : add, delete, change position

    def __init__(self):
        super().__init__()
        # self.parent = parent
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\GraphParameters.ui', self)

class SummaryWindow(QWidget):

    def __init__(self):
        super().__init__()
        # self.parent = parent
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\AnalysisWin.ui', self)

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
        self.setting = {0:OneSetting('Custom parameter')}
        

        self.paramtre = Filters(self.setting)
        self.layout_setting.addWidget(self.paramtre.tree)

        self.comboExpandable = ComboBoxExpandable()
        self.comboExpandable.setData(PROCESSING_NAME)
        self.layout_setting.addWidget(self.comboExpandable)

        self.comboExpandable.pathChanged.connect(self.oc_add_filter)
        
        print('iiiiiiniiit')


        self.show()

    def oc_add_filter(self,path):
        print(f"{path[-1]}_[{'_'.join(path[:-1])}] ")
        self.paramtre.addNew(f"{path[-1]}_[{'_'.join(path[:-1])}] " )

    
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
            self.wnewFilter = NewFilterWindow()
        self.wnewFilter.show()



    def oc_newSummary(self):
        if self.w is None:
            self.w = SummaryWindow()
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
        print('oc combo')
        last_selection = self.comboBox_variable.currentText()
        self.update_fileSystem_comboBox_Variable()
        self.comboBox_variable.setCurrentIndex(np.max([0,self.comboBox_variable.findText(last_selection)]))

    def oc_comboBox_variable_change(self,):
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
    print(PROCESSING)
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