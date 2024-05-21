from .setup import *
from .graph import PLOT
from .mainwindow_utils import deleteItemsOfLayout, Try_decorator
from .processing_function import apply_jsonFilterGlobal 

class Canvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        super().__init__(self.fig)

    def clear(self):
        self.fig.clear()



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
            loader,path = self.ui_graph.get_dataPath()
            print('retrive not independent data')

        else:
            #retrieve data from the parameters
            loader,path = self.ui_parameters.get_data()
            print('retrive independent data')

        print('retrieved dataaaa', loader,path)
        return loader,path
    
    def update_drawing(self):
        if self.ui_graph:
            self.ui_graph.clearGraph()
            loader,path = self.retrieve_Data()
            print('update drawing',loader,path)

            #reset data actual loader
            self.parent.get_currentLoader().init_dataLoader(path)
            #apply global filters
            dictGlobalProcessing = self.parent.get_currentGlobalProcessingDict()
            apply_jsonFilterGlobal(loader,path,pathFile=None,dictFile=dictGlobalProcessing)

            # transmit data to draw
            data = []
            for gr in list(path.keys()):
                for var in list(path[gr].keys()):
                    for dim in list(path[gr][var].keys()):
                        for ch in path[gr][var][dim]:
                            data.append(loader.getData(gr,var,dim,ch))
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




class Layout(QWidget):
    def __init__(self,nb,nb_v=1):
        super().__init__()
        loadUi(f'hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\Layout{nb}_{nb_v}.ui', self)




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


