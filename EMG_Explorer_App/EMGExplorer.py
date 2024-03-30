# from Explorer_package.requirement import *
from Explorer_package import *
from Explorer_package.loading_function import *
from PyQt5.QtCore import Qt
import os


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
        
        ## Windows Parameters
        # Definition of the button Parameters ...
        self.menu = QMenu()
        self.menu.addAction("Delete",self.oc_action1)
        self.menu.addAction("Split",self.oc_action1)
        self.menu_type = QMenu('Change type')
        self.menu_type.addAction("type1",self.oc_action1)
        self.menu_type.addAction("type2",self.oc_action1)
        self.menu.addMenu(self.menu_type)

        self.toolButton.setMenu(self.menu)
        self.nb_layout = 3
        self.nb_version = 1

        ## GRAPH

        self.time = np.arange(100)
        self.signal = np.random.random(100)

        self.update_list_layout_graph()
        self.initialize_layout_graph()

       
        # self.p2.plot(np.random.normal(size=100), pen=(255,0,0), name="Red curve")
        # self.p2.showGrid(x=True, y=True)
        self.interactivity_fileSystem()
        self.show()

    # class Mylayout(QGridLayout):
    #     def __init__(self, parent):
    #         QGridLayout.__init__(self, parent)
    #         print("c")

    
    #     def mousePressEvent(self, event):
    #             print("clicked")
    #             event.accept()
    class MyMultiPlotWidget(pg.MultiPlotWidget):
        def __init__(self,parent):
            pg.MultiPlotWidget.__init__(self)
            self.parent = parent

    
        def mouseDoubleClickEvent(self, event):
            print("clicked")
            self.parent.label_5.setText(str(np.random.randn()))
            event.accept()

    def update_list_layout_graph(self):
        """Updates the variable dict_layout_graph
        Create a dictionnary with the layout that can be used to display graphs 
        { id : Gridlayout}
        """
        self.dict_layout_graph = {}
        i = 0
        for frame in self.layout.findChildren(QFrame):
            if 'graph' in frame.objectName().split('_'):
                self.dict_layout_graph[i] = QGridLayout(frame)
                i += 1
                # self.dict_layout[i].setObjectName(u"gridLayout")


        
    def initialize_layout_graph(self):
        """Initialize/ create the graph and put them in the layouts of dict_layout_graph.
        windows : pg plotwidget
        plot x = plot
        """
        self.dict_displayed_graph = {}     
        for id,layout in self.dict_layout_graph.items():
            self.dict_displayed_graph[id] = { 'window': self.MyMultiPlotWidget(self)}
            self.dict_displayed_graph[id]['window'].setBackground("w")
            layout.addWidget(self.dict_displayed_graph[id]['window'])
            self.dict_displayed_graph[id]['plot1'] = self.dict_displayed_graph[id]['window'].addPlot(title=f'graph {id}')
            # self.dict_displayed_graph[id]['window'].mousePressEvent.connect(lambda: print('cooooooooo'))

    # def update_layout_graph(self):
    #     """update the graph displayed
    #     create new ones if there are not enough graph 
    #     """
    #     nb_displayed = len(self.dict_displayed_graph)
    #     nb_frame = len(self.dict_layout_graph)
    #     if nb_frame > nb_displayed:
    #         for id in self.dict_layout_graph.keys()[-(nb_frame-nb_displayed):]:
    #             layout = self.dict_layout_graph[id]
    #             self.dict_displayed_graph[id] = { 'window': pg.MultiPlotWidget()}
    #             self.dict_displayed_graph[id]['window'].setBackground("w")
    #             layout.addWidget(self.dict_displayed_graph[id]['window'])
    #             self.dict_displayed_graph[id]['plot1'] = self.dict_displayed_graph[id]['window'].addPlot(title=f'graph {id}')

                        
        
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



    ## FILE SYSTEM
                
    def update_fileSystem_comboBox_Group(self):
        """Add the group paths to the comboBox
        """
        # remove previous items
        self.comboBox_group.clear()

        # select current Item
        selected_file = self.listWidget_file.currentItem()
        if selected_file == None:
            self.listWidget_file.setCurrentRow(0)
        
        selected_file = self.listWidget_file.currentItem().text()

        for dict_group in self.data[selected_file]['path_data'].keys():
            self.comboBox_group.addItem(dict_group)


    def update_fileSystem_comboBox_Variable(self):

        """Add the data variables that matches the selected group in the comboBox
        """
        # remove previous items
        self.comboBox_variable.clear()

        data = self.data[self.listWidget_file.currentItem().text()]['data']
        group = self.comboBox_group.currentText()

        for var in list(data[group].data_vars):
            self.comboBox_variable.addItem(var)


    def oc_ListWidget_change(self,item):        
        last_selection = self.comboBox_group.currentText()
        self.update_fileSystem_comboBox_Group()
        self.comboBox_group.setCurrentIndex(np.max([0,self.comboBox_group.findText(last_selection)])) 
        # find TExt return -1 if there is no match

        # update comboBox variable
        self.oc_comboBox_group_change()
        self.oc_comboBox_variable_change()
       

    def oc_comboBox_group_change(self,):
        last_selection = self.comboBox_variable.currentText()
        self.update_fileSystem_comboBox_Variable()
        self.comboBox_variable.setCurrentIndex(np.max([0,self.comboBox_variable.findText(last_selection)]))


    def oc_comboBox_variable_change(self,):
        self.comboBox_dim.clear()
        self.data_array = self.data[self.listWidget_file.currentItem().text()]['data'][self.comboBox_group.currentText()][self.comboBox_variable.currentText()]

        dims = list(self.data_array.dims)
        for t in ['Time','time']:
            try:
                dims.remove(t)
            except:
                pass

        if len(dims) != 0:
            dim_name = dims[0] # could be replace by a list of the dims if more than 2

            self.label_timeline_dim.setText(dim_name)
            for item in self.data_array[dim_name].values:
                self.comboBox_dim.addItem(str(item))
        else:
            self.label_timeline_dim.setText('no dim')
            self.comboBox_dim.addItem('None')





    
    def interactivity_fileSystem(self):
        self.listWidget_file.currentItemChanged.connect(self.oc_ListWidget_change)
        self.comboBox_group.textActivated.connect(self.oc_comboBox_group_change)
        self.comboBox_variable.textActivated.connect(self.oc_comboBox_variable_change)




    def oc_load_files(self):
        # load the paths
        files,extension = QFileDialog.getOpenFileNames(self, 'Open file',  'C:\\Users\\mtlsa\\Documents\\UTC\\GB05\\TX\\Python_EMGExplorer\\data',"Nc files (*.nc )")
        # files.setFileMode(QFileDialog.FileMode.ExistingFiles)

        
        self.data = load_multiple_nc_files(files)

        # update the list
        for name in self.data.keys():
            self.listWidget_file.addItem(name)

        # update the data at hand
        self.update_fileSystem_comboBox_Group()
        self.update_fileSystem_comboBox_Variable()
        


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