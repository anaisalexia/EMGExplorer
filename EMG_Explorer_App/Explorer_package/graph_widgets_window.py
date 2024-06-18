from .setup import *
from .graph import PLOT
from .mainwindow_utils import deleteItemsOfLayout, Try_decorator
from .processing_function import apply_jsonFilterGlobal 



class Layout(QWidget):
    """Layout of the Graphic units.

    Args:
        QWidget (_type_): _description_
    """
    def __init__(self,nb,nb_v=1):
        super().__init__()
        loadUi(f'hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\Layout{nb}_{nb_v}.ui', self)


class Layout_Parameters_Type(QWidget):
    """Layout and interactivity of the setting of one graphic units. It enables the user to chose a type of graph and select the displayed channels

    Args:
        QWidget (_type_): _description_

    Returns:
        _type_: _description_
    """
    signal_IndependantDataChecked = pyqtSignal(bool)
    selectedDataChanged = pyqtSignal()

    def __init__(self,p=None):
        self.parent = p
        super().__init__()
        loadUi( 'hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\layout_parameters_type.ui',self)
        self.layout_param = self.vlayout_parameters
        self.selectedData = {}
        self.selectedDataPath = {}

        # tab data interactivity
        self.selectDataWindow = None
        self.groupBox_dataSelection.clicked.connect(self.oc_groupBoxChecked)
        self.button_select.clicked.connect(self.oc_selectData)

        self.dataIndependent = False

    def oc_selectData(self):
        """Open a windows to select the channels to display.
        """
        if self.selectDataWindow is None:
            self.selectDataWindow = WindowChannelSelection(self.parent)
            self.selectDataWindow.sendData.connect(self.save_selectedData)
        self.selectDataWindow.show()

    def save_selectedData(self,dictData):
        """return a path of the selected Data

        Args:
            dictData (_type_): _description_
        """
        print('save selection data',dictData)
        # from dict Data to actual data
        loader = self.parent.get_currentLoader()
        self.selectedData = loader.get_DataFromDict(dictData)
        self.selectedDataPath = dictData

        # print('selected DATA',self.selectedData)
        self.selectedDataChanged.emit()
        self.selectDataWindow.close()

        # TAB DATA
    def isDataIndependent(self):
        return self.dataIndependent
    
    def get_data(self):
        return self.selectedData
    
    def get_dataPath(self):
        return self.selectedDataPath
    
    def oc_groupBoxChecked(self,state):
        if state :
            self.dataIndependent = True
        else:
            self.dataIndependent = False

    def saveState(self):
        state = {'independent': self.dataIndependent,
                 'pathSelectedData': self.selectedDataPath,
                  'selectedData':self.selectedData  }
        return state
    
    def restoreState(self,state):
        self.groupBox_dataSelection.setChecked(state['independent'])
        self.selectedDataPath = state['pathSelectedData']
        self.selectedData = state['selectedData']




class OneGraph():
    """It is a Graphic Units. It is the base structure of one plot, it comprises: the layout of the plot, the layout of the parameters. It makes the connexion between the interface and the plots.
    """
    def __init__(self,frame_graph,layout_parameters,i,parent) -> None:
        """Creates a Widget that will mnanage the type of plot displayed by the user.

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
        # create the combobox to choose the type of plot
        self.ui_parameters = Layout_Parameters_Type(self.parent)
        for fc in ['None'] + list(PLOT.keys()):
            self.ui_parameters.comboBox_type.addItem(fc)
        self.layout_parameters = layout_parameters
        self.selectedData = None

        # Init layout of the graph box
        # add a push button to select the graph and a layout where the graph can be placed
        self.layout_graph = QGridLayout()
        self.button = QPushButton()
        self.layout_graph.addWidget(self.button)
        frame_graph.setLayout(self.layout_graph)

        self.button.clicked.connect(self.oc_Buttonclick)
        self.ui_parameters.comboBox_type.currentIndexChanged.connect(self.oc_comboBox_type_change)

        # DATA, layout interactivity
        self.ui_parameters.selectedDataChanged.connect(self.update_drawing)

        

    # TAB PARAMETERS
    def add_paramUi_to_layout(self):
        """Changes the Parameters tab of the graph, to display the setting of the selected graph
        """
        deleteItemsOfLayout(self.layout_parameters)
        self.layout_parameters.addWidget(self.ui_parameters)
        self.parent.tabWidget.setCurrentIndex(0)

    def add_graphUi_to_layout(self):
        """add a button and the layout of the future plot to the Graph box
        """
        deleteItemsOfLayout(self.layout_graph)
        self.layout_graph.addWidget(self.button)
        if self.ui_graph:
            self.layout_graph.addWidget(self.ui_graph)

    def add_setting_to_param(self):
        """Add settings to the layout of the parameters layout
        """
        deleteItemsOfLayout(self.ui_parameters.layout_param)
        self.ui_parameters.layout_param.addWidget(self.ui_graph.l)

    def oc_Buttonclick(self):
        """Set or Opens the menu of the current box
        """
        self.add_paramUi_to_layout()
        self.parent.current_id = self.id
        try:
            self.ui_graph.update_settings()
        except: pass


    def oc_comboBox_type_change(self):
        """Changes the type of graph of the current box
        """
        type_ = self.ui_parameters.comboBox_type.currentText()
        if type_ != 'None' :
            # add a plot to the layout of the graph layout 
            self.setPlot(PLOT[type_])
            # add the setting of the plot to the graph setting
            self.add_graphUi_to_layout()
            self.update_drawing()
        elif type_ == 'None':
            if self.ui_graph != None:
                self.ui_graph.clearGraph()
                self.ui_graph = None

        else:
            self.ui_graph.clearGraph()

    
    
    def get_selectedData(self):
        """Return selected data

        Returns:
            _type_: _description_
        """
        return self.selectedData

    # GRAPH
    def retrieve_Data(self):
        """Retrieve the current loader and the path to the selected Data.

        Returns:
            _type_: _description_
        """
        if not self.ui_parameters.isDataIndependent():
            # retrieve data from the mainwindow throught the plot (the plot dictates the data it needs)
            # loader, path = self.parent.get_dataPath()
            loader, path = self.ui_graph.get_dataPath()

        else:
            #retrieve datapath from the parameters and the loader
            loader = self.parent.get_currentLoader()
            path = self.ui_parameters.get_dataPath()
            # Example of path {'/': {'Trigger': [], 'Accelerations': {'axes': ['X']}, 'HDsEMG': {'Channel': []}}}  

        return loader,path
    
    
    def update_drawing(self):
        """Update the drawing of the Plot of the Graphique Unit. 
        """

        if self.ui_graph:
            self.ui_graph.clearGraph()
            loader,path = self.retrieve_Data()

            #reset data for processing with original data in the current loader
            self.parent.get_currentLoader().init_dataLoader(path)
            #apply global filters
            dictGlobalProcessing = self.parent.get_currentGlobalProcessingDict()
            if dictGlobalProcessing != {}:
                apply_jsonFilterGlobal(loader,path,pathFile=None,dictFile=dictGlobalProcessing)

                            
            kwargs = {}
            self.ui_graph.draw(loader,path,**kwargs)


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

    def saveState(self):
        """Save the state of the graph in a dicitonnary (id, type, selectedDate)

        Returns:
            _type_: _description_
        """
        state = {'id': self.id,
                 'type' : self.ui_parameters.comboBox_type.currentText(),
                 'selectedDataState' : self.ui_parameters.saveState()}
        print(state)
        return state

    def restoreState(self,state):
        """Restore the state of the graph with a dictionnary.

        Args:
            state (_type_): _description_
        """
        type_ = state['type']
        self.id = state['id']
        self.ui_parameters.restoreState(state['selectedDataState'])
        self.ui_parameters.comboBox_type.setCurrentText(type_)









class WindowChannelSelection(QWidget):
    """Display a windows that allows the user to select the channels to be displayed.

    Args:
        QWidget (_type_): _description_

    Returns:
        _type_: _description_
    """
    sendData = pyqtSignal('PyQt_PyObject')
    
    def __init__(self,parent):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\Form_selection_channels.ui', self)
        self.p = parent
        self.dictSelection = {}

        self.tree = QtWidgets.QTreeWidget()
        loader = self.p.get_currentLoader()
        dict_group = loader.getGroup()

        self.button_selectAll.clicked.connect(partial(self.oc_selectAll,self.tree.invisibleRootItem()))
        self.button_deselectAll.clicked.connect(partial(self.oc_deselectAll,self.tree.invisibleRootItem()))
        self.button_Select.clicked.connect(self.oc_select)

        # Create a tree of checkBox
        for gr in list(dict_group.keys()):
            item_group = QtWidgets.QTreeWidgetItem(self.tree)
            item_group.setText(0,str(gr))
            item_group.setFlags(item_group.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for v in list(dict_group[gr].keys()):
                item_var = QtWidgets.QTreeWidgetItem(item_group)
                item_var.setFlags(item_var.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate )
                item_var.setText(0,str(v))
                item_var.setCheckState(0, Qt.Unchecked)

                for dim_name,ch in list(dict_group[gr][v].items()):
                    item_dim = QtWidgets.QTreeWidgetItem(item_var)
                    item_dim.setFlags(item_dim.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                    item_dim.setText(0,str(dim_name))
                    item_dim.setCheckState(0, Qt.Unchecked)

                    for c in ch:
                        item_ch = QtWidgets.QTreeWidgetItem(item_dim)
                        item_ch.setFlags(item_ch.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                        item_ch.setText(0,str(c))
                        item_ch.setCheckState(0, Qt.Unchecked)

        self.layout_tree.addWidget(self.tree)

    def oc_deselectAll(self,item):
        """Deselect all channels

        Args:
            item (_type_): _description_
        """
        nb_children = item.childCount()
        item.setCheckState(0, Qt.Unchecked)

        if nb_children > 0:

            for i in range(nb_children):
                self.oc_deselectAll(item.child(i))
  

    def oc_selectAll(self,item):
        """Select all channels

        Args:
            item (_type_): _description_
        """
        nb_children = item.childCount()
        item.setCheckState(0, Qt.Checked)

        if nb_children > 0:
            for i in range(nb_children):
                self.oc_selectAll(item.child(i))
      

    def get_selectedItems(self): 
        """Return a dictionnary as a tree of the selected channel
        Example : {'/': {'Trigger': [], 'Accelerations': {'axes': ['Y']}, 'HDsEMG': {'Channel': ['6', '10', '11', '12']}}}


        Returns:
            _type_: _description_
        """
        path = {}
        loader = self.p.get_currentLoader()
        dict_group = loader.getGroup()

        item = self.tree.invisibleRootItem()
        for igr in range(item.childCount()):
            itemGr = item.child(igr)
            path[itemGr.text(0)] = {}

            for ivar in range(itemGr.childCount()):
                itemVar = itemGr.child(ivar)
                path[itemGr.text(0)][itemVar.text(0)] = {}

                for idim in range(itemVar.childCount()):
                    itemdim = itemVar.child(idim)
                    path[itemGr.text(0)][itemVar.text(0)][itemdim.text(0)] = []


                    for ich in range(itemdim.childCount()):
                        itemCh = itemdim.child(ich)

                        if itemCh.checkState(0) == Qt.Checked :
                            path[itemGr.text(0)][itemVar.text(0)][itemdim.text(0)].append(itemCh.text(0))

        # not used : get the paht but using recursive function
        # def has_childLeaf(item):
        #     nb_children = item.childCount()
        #     for i in range(nb_children):
        #         child = item.child(i)
        #         nb_chil_children = child.childCount()
        #         if nb_chil_children > 0:
        #             return False
        #     return True
                    
            
        # def recurse(item):
        #         list_dict = {}
        #         if has_childLeaf(item):
        #             list_checked = []
        #             for j in range(item.childCount()):
        #                  if  item.child(j).checkState(0) == Qt.Checked :
        #                     list_checked.append(item.child(j).text(0))
        #             return list_checked 
                    
        #         else:
        #             for i in range (item.childCount()):
        #                 list_dict[item.child(i).text(0)] = recurse(item.child(i))
        #         return list_dict
        
        # return recurse(self.tree.invisibleRootItem())
        return path

    def oc_select(self):
        """Emit the selected data with the signal sendData
        """
        dictData = self.get_selectedItems()
        # eg: {'/': {'Trigger': [], 'Accelerations': {'axes': ['Y']}, 'HDsEMG': {'Channel': ['6', '10', '11', '12']}}}
        self.sendData.emit(dictData)

        


