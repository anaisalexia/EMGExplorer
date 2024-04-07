# from Explorer_package.requirement import *
from Explorer_package import *
from Explorer_package.loading_function import *
from PyQt5.QtCore import Qt
import os

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
        for fc in PLOT.keys():
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

    def oc_comboBox_type_change(self):
        """Changes the graph of the current box
        """
        self.setPlot(PLOT[self.ui_parameters.comboBox_type.currentText()])
        self.add_graphUi_to_layout()

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
        self.data = {}
        # self.layout_param = self.frame_parameters
        self.layout_param = self.verticalLayout


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
        print('iiiiiiniiit')
        self.show()

    

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
        
        self.data = load_multiple_files(files)

        # update the list
        for loader in self.data.keys():
            self.listWidget_file.addItem(loader)




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

        for group in self.data[file_name].dict_group.keys():
            self.comboBox_group.addItem(group)


    def update_fileSystem_comboBox_Variable(self):
        print('update var')
        """Add the data variables that matches the selected group in the comboBox
        """
        # remove previous items
        self.comboBox_variable.clear()

        file_name = self.listWidget_file.currentItem().text()
        dict_group = self.data[file_name].dict_group
        group = self.comboBox_group.currentText()

        for var in list(dict_group[group].keys()):
            self.comboBox_variable.addItem(var)


    def update_fileSystem_comboBox_Channel(self):
        print('update ch')
        """Add the channels that matches with the selected variables
        """
        self.comboBox_dim.clear()

        file_name = self.listWidget_file.currentItem().text()
        dict_group = self.data[file_name].dict_group
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()


        dims = dict_group[group][var]

        if len(dims) != 0:
            self.label_timeline_dim.setText(str(var))
            for item in dict_group[group][var]:
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
       

    def oc_comboBox_group_change(self,):
        print('oc combo')
        last_selection = self.comboBox_variable.currentText()
        self.update_fileSystem_comboBox_Variable()
        self.comboBox_variable.setCurrentIndex(np.max([0,self.comboBox_variable.findText(last_selection)]))

    def oc_comboBox_variable_change(self,):
        print('oc var')
        self.update_fileSystem_comboBox_Channel()


    def interactivity_fileSystem(self):
        self.listWidget_file.currentItemChanged.connect(self.oc_ListWidget_change)
        self.comboBox_group.textActivated.connect(self.oc_comboBox_group_change)
        self.comboBox_variable.textActivated.connect(self.oc_comboBox_variable_change)


        


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