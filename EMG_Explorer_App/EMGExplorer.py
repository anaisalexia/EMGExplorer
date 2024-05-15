# from Explorer_package.requirement import *
from Explorer_package import *
from Explorer_package.loading_function import *
from PyQt5.QtCore import Qt
import os


    


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


