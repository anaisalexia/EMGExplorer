# from Explorer_package.requirement import *
import sys, os
sys.path.append(os.getcwd())
sys.path.append("..")

from Explorer_package import *
from Explorer_package.loading_function import *
from PyQt5.QtCore import Qt
import os
from io import StringIO
import os
log_stream = StringIO() 
now = datetime.now()
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('background', 'w')


# https://github.com/fbjorn/QtWaitingSpinner


                   
# --------- LOGGER ---------------------
logger = logging.getLogger('main')
logging.basicConfig( format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG) 

# Stream handler
streamHandler = logging.StreamHandler(log_stream)
logger.addHandler(streamHandler)

# File Handler
# Information
CURRENT_PATH_LOG_INFO = f"{PAHT_LOG}log {str(now).replace(":","-")}.log"
f = open(CURRENT_PATH_LOG_INFO, "x")
f.close()
loggerFile = logging.FileHandler(filename=CURRENT_PATH_LOG_INFO, mode = "w")
loggerFile.setLevel(logging.INFO)
logger.addHandler(loggerFile)

## Debug
CURRENT_PATH_LOG_DEBUG = f'./logdebug.log'
if os.path.exists(CURRENT_PATH_LOG_DEBUG) == False : f = open(CURRENT_PATH_LOG_DEBUG, "x");f.close()
loggerDebugFile = logging.FileHandler(filename=CURRENT_PATH_LOG_DEBUG, mode = "w")
loggerDebugFile.setLevel(logging.DEBUG)
logger.addHandler(loggerDebugFile)

class OutputHandler(logging.Handler,QWidget):
    """Logging Handler to display a warning message or error. Not fully implemented

    Args:
        logging (_type_): _description_
        QWidget (_type_): _description_
    """
    log_received = pyqtSignal(str)

    def __init__(self) -> None:
        logging.Handler.__init__(self)
        QWidget.__init__(self)

    def emit(self, record):
        if record.levelno != logging.DEBUG:
            self.log_received.emit(record.getMessage())


class LogWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Loading of the UI
        loadUi('hdemg_viewer_exemple\\Qt_creator\\EMGExplorer_qt\\main_log_layout.ui', self)
        self.label_log.setWordWrap(True)
        self.label_wholeLog.setWordWrap(True)
        self.scrollArea_log.setVisible(False) 
        self.bool_logInfo = False
        self.button_log.clicked.connect(self.oc_buttonLog)

    def set_labelLog(self,info):
        self.label_log.setText(info)

    def oc_buttonLog(self):
        self.bool_logInfo = not self.bool_logInfo
        if self.bool_logInfo:
            self.update_log()
            self.scrollArea_log.setVisible(True) 

        else:
            self.scrollArea_log.setVisible(False) 
    
    def update_log(self,arg=None):
        if self.bool_logInfo:
            f  = open(CURRENT_PATH_LOG_INFO, "r")
            self.label_wholeLog.setText(log_stream.getvalue())
        
  # --------- END LOGGER ---------------------
 


class EMGExplorer(QMainWindow):
    """QMainWindow, main window of the EMG Explorer. It instantiates the Widgets.

    Args:
        QMainWindow (_type_): _description_
    """


    def __init__(self):
        super().__init__()
        # Loading of the UI
        loadUi('hdemg_viewer_exemple\\Qt_creator\\EMGExplorer_qt\\EMGExplorer_mainwindow_base2.ui', self)

        # Initialisation Log
        self.log = LogWindow()
        self.layout_log.addWidget(self.log)
        warning_handler = OutputHandler()
        warning_handler.log_received.connect(self.log.set_labelLog)
        warning_handler.log_received.connect(self.log.update_log)
        logger.addHandler(warning_handler)


        # Initialisation of variables
        self.w = None
        self.wnewFilter = None
        self.layout = Layout(3,1)
        self.dock = {}
        self.dataLoader = {}
        self.layout_param = self.layout_parameters
        self.path_globalProcessing = ['None']

        ## MENU
        # Definition of the action
        self.actiontype_1.triggered.connect(self.oc_actiontype1)
        self.actionNew.triggered.connect(self.oc_newFilter)
        self.actionRun_Analysis.triggered.connect(self.oc_newSummary)
        self.actionLoad.triggered.connect(self.oc_load_files)
        self.actionRemove.triggered.connect(self.oc_remove_files)

        self.action4_windows.triggered.connect(partial(self.oc_update_layout_graph,4,1))
        self.action3_windows.triggered.connect(partial(self.oc_update_layout_graph,3,1))

        # Information window
        self.treeWidget.itemDoubleClicked.connect(self.oc_itemPressed)
        
        self.nb_layout = 3
        self.nb_version = 1
        self.current_id = 0


        # self.time = np.arange(100)
        # self.signal = np.random.random(100)


        # Restores the previous state of the app
        self.restoreSettings()
        self.update_list_layout_graph()
        self.restoreGraph()
    
        # Initializes the processing widgets
        self.init_processingWidget()
        
        self.init_comboBoxGlobalProcessing()
        self.interactivity_fileSystem()
        self.restoreGlobalProcessing()


        # Initialisation shortcut
        self.init_shortcut()

        logger.info('Initialisation of the Interface done')
        self.show()


    def init_shortcut(self):
        shortcut = QKeySequence(Qt.Key_D)
        self.shortcut = QShortcut(shortcut, self)
        self.shortcut.activated.connect(lambda : self.nextChannel(1))

        shortcut = QKeySequence(Qt.Key_Q)
        self.shortcut = QShortcut(shortcut, self)
        self.shortcut.activated.connect(lambda : self.nextChannel(-1))

    def nextChannel(self,i):
        ch = int(self.comboBox_dim.currentText()) + i
        self.comboBox_dim.setCurrentText(str(ch))
        self.oc_comboBox_dim_change()


    




    #### Global processing ComboBox ####
    def init_comboBoxGlobalProcessing(self):
        self.comboBoxGlobalProcessing = ComboBoxExpandable()
        self.update_comboBoxGlobalProcessing()
        self.lcomboBox_globalProcessing.addWidget(self.comboBoxGlobalProcessing)
        self.comboBoxGlobalProcessing.pathChanged.connect(self.update_pathGlobalProcessing)
        
    
    def update_comboBoxGlobalProcessing(self):
        lastSelection = self.comboBoxGlobalProcessing.text()
        if lastSelection:
            print(lastSelection)
            self.comboBoxGlobalProcessing.setText(lastSelection)

        menuJson = dictOfFiles_from_EmbeddedFolders(ROOT_GLOBALPROCESSING)
        self.comboBoxGlobalProcessing.setData(menuJson)
        self.comboBoxGlobalProcessing.append_element(['None'],self.comboBoxGlobalProcessing.menu())

    

    def update_pathGlobalProcessing(self,listpath:list):
        self.path_globalProcessing = listpath
        self.oc_comboBox_dim_change()

    def get_currentGlobalProcessingDict(self):
        if self.path_globalProcessing != ['None']:
            listpath = list(filter(lambda a: a != 'general', self.path_globalProcessing))
            f = open(f'{ROOT_GLOBALPROCESSING}/{"/".join(listpath)}')
            data = json.load(f)
            return data
        else:
            return {}
    #### end Global processing ####


    ####  Processing Widget ####
    def init_processingWidget(self):
        # Initialization Single Processing window
        self.widget_singleProcessing = SingleProcessing(self)
        self.layout_singleProcessing.addWidget(self.widget_singleProcessing)
        self.widget_singleProcessing.apply.connect(self.updateAllGraph)


        # Initialization Global Processing window
        self.widget_globalProcessing = GlobalProcessingTab(self)
        self.layout_globaProcessing.addWidget(self.widget_globalProcessing)
        self.widget_globalProcessing.processingSaved.connect(self.update_comboBoxGlobalProcessing)


    #### Getter, data, path, loader ####
    def get_dataChannel(self):
        file_name = self.listWidget_file.currentItem().text()
        loader = self.dataLoader[file_name]
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()
        ch = self.comboBox_dim.currentText()
        dim = self.label_timeline_dim.text()
        
        return loader.getData(group,var,dim,ch)
    
    def get_dataChannelPath(self):
        """Return the current loader and a path to the currently selected channel 


        Returns:
            _type_: _description_
        """
        file_name = self.listWidget_file.currentItem().text()
        loader = self.dataLoader[file_name]
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()
        ch = self.comboBox_dim.currentText()
        dim = self.label_timeline_dim.text()
        ch = convertText(ch)
        dictPath = {group : {var : {dim : [ch]}}}
        return loader,dictPath

    
    def get_dataVariable(self):
        file_name = self.listWidget_file.currentItem().text()
        loader = self.dataLoader[file_name]
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()
        dim = self.label_timeline_dim.text()
        
        return loader.getDataVariable(group,var,dim)
    
    def get_dataVariablePath(self):
        """Return the current loader and a path to all channel of the currently selected variable

        Returns:
            _type_: _description_
        """
        file_name = self.listWidget_file.currentItem().text()
        loader = self.dataLoader[file_name]
        group = self.comboBox_group.currentText()
        var = self.comboBox_variable.currentText()
        dim = self.label_timeline_dim.text()
        list_ch = [convertText(ch) for ch in loader.getListChannel(group,var,dim)]
        dictPath = {group : {var : {dim : list_ch}}}
        return loader,dictPath

    def get_currentLoader(self):
        """Return the loader of the currently selected file.

        Returns:
            _type_: _description_
        """
        try:
            file_name = self.listWidget_file.currentItem().text()
            return self.dataLoader[file_name]
        except:
            return None

    def get_globalProcessing(self):
        return self.path_globalProcessing 
    
    #### end Getter, data, path, loader #### 
    


    #### Layout of the Graphs, List of Graph, Graphs ####
    def clearAllPlot(self):
        for plot in list(self.dict_layout_graph.values()):
           plot.clearPlot() 
    
    def updateAllGraph(self):
        # for i,graph in self.dict_layout_graph.items():
        #     graph.update_drawing()
        for plot in self.dict_layout_graph.values():
            try:
                plot.update_drawing()
            except Exception as e:
                logger.error(f"Update drawing - error {e}")


    def update_list_layout_graph(self):
        """Updates the variable dict_layout_graph
        Create a dictionnary with objects of the class Graph that can be used to display plots.
        { id : OneGraph }
        """
        self.dict_layout_graph = {}
        i = 0
        for frame in self.layout.findChildren(QFrame):
            if 'graph' in frame.objectName().split('_'):
            
                self.dict_layout_graph[i] = OneGraph(frame,self.layout_param,i,self)
                i += 1

      
    def oc_update_layout_graph(self,nb,nb_v):
        """Changes the general layout of the graphs and update the displayed plots.

        Args:
            nb (int): number of graphs on the layout
            nb_v (int): number cooresponding to the version of the layout of the graphs (in case their is multiple x-layout graph)
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
    #### end Layout of the Graphs, List of Graph, Graphs ####






    #### Menu Action functions #### 
    def oc_newFilter(self):
        if self.wnewFilter is None:
            # self.wnewFilter = NewFilterWindow()
            self.wnewFilter = WindowChannelSelection(self)
        self.wnewFilter.show()


    def oc_newSummary(self):
        if self.w is None:
            self.w = SummaryWindow(self)
        else:
            self.w.update_comboBoxGlobalProcessing()
            self.w.update_file_list()

        self.w.show()
        
    
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
        """ change the visibility of a dock window"""
        #### !! PB: error bc called when the win closes
        if not visibility:
            self.removeDockWidget(self.dock[dock])
            self.dock[dock].deleteLater()
            del self.dock[dock]
            # self.widget_name = None
    #### end Menu Action functions ####



    #### Metadata Tab ####
    def oc_itemPressed(self, item, int_col):
        """ Set the text of a meta data """
        if int_col!=0:
            text, ok = QInputDialog().getText(self, "input",
                                            "data:", QLineEdit.Normal,
                                     item.text(int_col))
            if ok and text:
                item.setText(int_col,text)
    #### end Metadata Tab ####



    

    #### Saving and restoring Layout #### 
    def restoreSettings(self):
        """Restores the last state of the application
        """
        name_folder = 'ExplorerEMG'
        name_seting = 'MyLayout'

        try:
            settings = QSettings(name_folder, name_seting)
        except Exception as e:
            logger.error(f'Restore Setting - Settings could not be found : {e}')
            return

        try:
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
        except Exception as e:
            logger.error(f'Restore Setting - Settings could not be restored : {e}')

        

    def restoreGraph(self):
        """Restores the state of the last Graph displayed on the application
        """
        name_folder = 'ExplorerEMG'
        name_seting = 'MyLayout'


        try:
            settings = QSettings(name_folder, name_seting)

            for id in range(0,settings.value('Nb Graph')):
                state = settings.value(f'graph {id}')
                graphId = state['id']
                self.dict_layout_graph[graphId].restoreState(state)
        except Exception as e:
            logger.error(f'Restore Setting - Graph settings could not be restored : {e}')

    def restoreGlobalProcessing(self):
        """Selects the name of the last Global Processing used in the applicaiton.
        """
        try:
            name_folder = 'ExplorerEMG'
            name_seting = 'MyLayout'

            settings = QSettings(name_folder, name_seting)
            self.path_globalProcessing = settings.value('globalProcessingPath')
            self.comboBoxGlobalProcessing.setText(self.path_globalProcessing[-1])
        except Exception as e:
            logger.error(f'Restore Setting - Global Processing settings could not be restored : {e}')

    def closeEvent(self, event):
        """Function triggered when the mainwindow is closed. It saves the stats if the layout, splitters, Graphs and Global Processing.

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

        # save graph
        settings.setValue('Nb Graph',len(self.dict_layout_graph))
        for id,graph in self.dict_layout_graph.items():
            settings.setValue(f'graph {id}',graph.saveState())

        # save Processing global
        settings.setValue('globalProcessingPath',self.path_globalProcessing)

    #### end Saving and restoring Layout #### 




    


    #### FILES MANAGEMENT ####

    def oc_load_files(self):
        """Opens a windows to select the files to be loaded. The data of the files are extracted and the Loader corresponding to each files is 
        stored in self.dataLoader. The name of the file are then added to the ListWidget.
        self.dataLoader[i] = Loader()
        """
        # retrieve the paths
        files,extension = QFileDialog.getOpenFileNames(self, 'Open file',  'C:\\Users\\mtlsa\\Documents\\UTC\\GB05\\TX\\Python_EMGExplorer\\data',"files (*.*)")
        
        # load the Loaders
        data = load_multiple_files(files)
        list_file = self.dataLoader.keys()
        for name_file in data.keys():
            if name_file not in list_file:
                self.dataLoader[name_file] = data[name_file]

            else:
                data.pop(name_file)
                logger.warning(f"Explorer - File {name_file} not loaded, it was already in the list")

        # update the list of files names
        for loader in data.keys():
            self.listWidget_file.addItem(loader)


    def oc_remove_files(self):
        """Removes all the stored files from the listWidget and dictionnary of Loaders"""
        self.listWidget_file.clear()
        self.dataLoader = {}

    

    # file system update  
    def update_fileSystem_comboBox_Group(self):
        """Add the groups'name corresponding to the selected file to the dedicated comboBox
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
        """Add the data variable names that matche the selected group to the dedicated comboBox
        """
        # remove previous items
        self.comboBox_variable.clear()

        file_name = self.listWidget_file.currentItem().text()
        dict_group = self.dataLoader[file_name].dict_group
        group = self.comboBox_group.currentText()

        for var in list(dict_group[group].keys()):
            self.comboBox_variable.addItem(var)


    def update_fileSystem_comboBox_Channel(self):
        """ Add the channel names that matche the selected group/var to the dedicated comboBox. It then triggers the update of the plots
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

        # self.updateAllGraph()


    # file system interactivity
    def oc_ListWidget_change(self,item):
        """Update the list of groups/var/channel displayed that correspond to the currently selected file.
        Load the attributs of the new selected file.
        """    
        # update the variable shown in Global Processing Widget
        self.widget_globalProcessing.updateComboBox(self.get_currentLoader().getListVariable())

        # Update the comboBox group and chose the last selected group name if any
        last_selection = self.comboBox_group.currentText()
        self.update_fileSystem_comboBox_Group()
        self.comboBox_group.setCurrentIndex(np.max([0,self.comboBox_group.findText(last_selection)])) 
        # findText returns -1 if there is no match

        # update comboBox variable
        self.oc_comboBox_group_change()
        self.oc_comboBox_variable_change()

        # load attrs
        loader = self.get_currentLoader()
        loader.loadAttributs()

        if loader.attrs:
            self.treeWidget.clear()
            walkDatatree_setAttrDataset(loader.attrs,self.treeWidget)
        
       

    def oc_comboBox_group_change(self,):
        """Update the list of variables, the list of channel and the plots. It choses the last selected variable if present in the new list of variables.
        """
        # update the list of variables and chose the last selected variable if there is a matche
        last_selection = self.comboBox_variable.currentText()
        self.update_fileSystem_comboBox_Variable()
        # looks for a match between the last selected variable and the new list of variables
        foundText = self.comboBox_variable.findText(last_selection)
        self.comboBox_variable.setCurrentIndex(np.max([0,foundText]))

        #clear the plot if the last variable selected is not in the new list
        if foundText == -1:
            self.clearAllPlot()

        else:
            self.updateAllGraph()

      
    def oc_comboBox_variable_change(self,):
        """Updates the list of displayable channels are changed and the graph are updated
        """
        self.update_fileSystem_comboBox_Channel()
        self.updateAllGraph()


    def oc_comboBox_dim_change(self,):
        """Updates the graphs
        """
        self.updateAllGraph()


    

    def interactivity_fileSystem(self):
        """Initialize the interactivity of the file system
        """
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
    logger.debug('Interface closed')



