from .setup import *
from .custom_widget import *
from .processing_function import PROCESSING_NAME,get_item_from_path,PROCESSING,apply_jsonFilter
from .mainwindow_utils import Try_decorator

logger = logging.getLogger('main')


NAME_JSONFOLDER = 'Custom Filters'

#########################
## FUNCTIONS
#########################
def create_menuJson(root):
    """Create a dictionnary of file name

    Args:
        root (_type_): _description_

    Returns:
        _type_: _description_
    """
    dictJson = {NAME_JSONFOLDER: []}
    for name in os.listdir(root):
        if name[:-5]!= '.json':
            dictJson[NAME_JSONFOLDER] += [name[:-5]]

    return dictJson


#########################
## Parameters layouts
#########################


class LayoutParameters(QWidget):
    """Layout of the Parameters of a Plot

    Args:
        QWidget (_type_): _description_
    """
    processingPathChanged_handler = pyqtSignal(list)
    checkProcessedRaw = pyqtSignal(bool)

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_graph.ui', self)
        self.init_interface()
        self.init_interactivity()


    def init_interface(self):
        # create a menu to display the processing
        self.comboMenu = ComboBoxExpandable()
        self.comboMenu.setData(PROCESSING_NAME)
        self.lcomboBox_processing.addWidget(self.comboMenu)

        menuJson = create_menuJson(PATH_PIPELINE)
        self.comboMenu.append_element(['None'],self.comboMenu.menu())
        self.comboMenu.append_element(menuJson,self.comboMenu.menu())

    def update_interface(self):
        # update comboBoxmenu
        self.comboMenu.menu().clear()
        self.comboMenu.setData(PROCESSING_NAME)
        self.lcomboBox_processing.addWidget(self.comboMenu)

        menuJson = create_menuJson(PATH_PIPELINE)
        self.comboMenu.append_element(['None'],self.comboMenu.menu())
        self.comboMenu.append_element(menuJson,self.comboMenu.menu())

    def init_interactivity(self):
        self.comboMenu.pathChanged.connect(self.oc_pathChanged_handler)
        self.checkBox_processedRaw.stateChanged.connect(self.oc_checkBoxRaw)

    def oc_checkBoxRaw(self,checked):
        self.checkProcessedRaw.emit(checked)

    def oc_pathChanged_handler(self,path):
        print('path changed handler',path)
        self.processingPathChanged_handler.emit(path)
    

class LayoutParameters2(QWidget):
    """Layout of the Parameter of a Plot

    Args:
        QWidget (_type_): _description_
    """

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_graph2.ui', self)

    def interactivity(self):
        pass



    
class LayoutParameters_MultiplePlot2(QWidget):
    """Layout of the parameters of a Multiple channels Plots

    Args:
        QWidget (_type_): _description_
    """

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_multiplot2.ui', self)

    def update_nbChannel(self):
        self.spinBox_nbChannel.setValue(np.ceil(self.spinBox_limit.value() / (self.spinBox_nbColumn.value())))

    def interactivity(self):
        self.spinBox_nbCol.textChanged.connect(self.update_nbChannel)
        self.spinBox_limit.textChanged.connect(self.update_nbChannel)

    # def update_limit(self):
    #     self.spinBox_limit.setValue(self.spinBox_nbChannel.value() * self.spinBox_nbRow.value() * self.spinBox_nbColumn.value())
        
    # def update_nbChannel(self):
    #     self.spinBox_nbChannel.setValue(np.ceil(self.spinBox_limit.value() / (self.spinBox_nbRow.value() * self.spinBox_nbColumn.value())))

    # def interactivity(self):
    #     self.spinBox_nbRow.textChanged.connect(self.update_nbChannel)
    #     self.spinBox_nbCol.textChanged.connect(self.update_nbChannel)
    #     self.spinBox_limit.textChanged.connect(self.update_nbChannel)




#########################
## Plot Types
#########################


class PlotGeneral(ABC):
     
    def __init__(self,layout,layout_graph,i,parent):
        # super().__init__()
        self.id = i
        self.layout = layout
        self.layout_graph = layout_graph
        self.parent = parent



    @abstractmethod
    def get_dataPath(self):
        """return the loader and the path to the current selected channel. 

        Returns:
            _type_: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def clearGraph(self):
        raise NotImplementedError()


    @abstractmethod
    def get_dataPath(self):
        """return the loader and the path to the current selected channel. 

        Returns:
            _type_: _description_
        """
        raise NotImplementedError()


    @abstractmethod
    def setInformation(self,**kwargs):
        raise NotImplementedError()


    @abstractmethod
    def draw(self,loader=None,path=None,**kwargs):
        """Draw the data from a loader according to a path. Apply filters if specified in the parameter Layout

        Args:
            loader (_type_, optional): _description_. Defaults to None.
            path (_type_, optional): _description_. Defaults to None.
        """

        raise NotImplementedError()


    @abstractmethod
    def clearGraph(self):
        raise NotImplementedError()





#############
# PLOT LINE #
#############

def extracteDatafromLoaderPath(loader,path):
    """Extract data from the loader according to paths. 

    Args:
        loader (_type_): _description_
        path (_type_): _description_

    Returns:
        _type_: list of xarray, each xarray corresponds to one group, one variable , one channel
    """
    data = []

    for gr in list(path.keys()):
            for var in list(path[gr].keys()):
                for dim in list(path[gr][var].keys()):
                    for ch in path[gr][var][dim]:
                        data.append(loader.getData(gr,var,dim,ch))    
    return data 
  
def extracteIndividualPathfromPath(loader,path):
    """Extract data from the loader according to paths. 

    Args:
        loader (_type_): _description_
        path (_type_): _description_

    Returns:
        _type_: list of xarray, each xarray corresponds to one group, one variable , one channel
    """
    data = []

    for gr in list(path.keys()):
            for var in list(path[gr].keys()):
                for dim in list(path[gr][var].keys()):
                    for ch in path[gr][var][dim]:
                        data.append({gr:{var:{dim:[ch]}}})    
    return data 

def extracteOriginalDatafromLoaderPath(loader,path):
    """Extract data from the loader according to paths. 

    Args:
        loader (_type_): _description_
        path (_type_): _description_

    Returns:
        _type_: list of xarray, each xarray corresponds to one group, one variable , one channel
    """
    data = []
    for gr in list(path.keys()):
            for var in list(path[gr].keys()):
                for dim in list(path[gr][var].keys()):
                    for ch in path[gr][var][dim]:
                        data.append(loader.getDataOriginal(gr,var,dim,ch))    
    return data 

def extractTitlefromPath(loader=None, path=None):
    title = " "
    for gr in list(path.keys()):
            title += f"{gr} - "
            for var in list(path[gr].keys()):
                title += f"{var} - "

                for dim in list(path[gr][var].keys()):
                    title += f"{dim} : "

                    for ch in path[gr][var][dim]:
                        title += f" {ch} "
    return title 






class PlotLine(pg.MultiPlotWidget):
    """Plot of type Lineplot. Display a single channel.

    Args:
        pg (_type_): _description_

    Returns:
        _type_: _description_
    """
    __metaclass__ = PlotGeneral

    def __init__(self, layout, layout_graph, i, parent):
        """Initialization of the Plot and its parameters Layout.

        Args:
            layout (_type_): _description_
            layout_graph (_type_): _description_
            i (_type_): _description_
            parent (_type_): _description_
        """
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)

        self.plot = self.addPlot()
        self.l = LayoutParameters()
        self.function = 'lineplot'

        
        self.currentPath = ['None']
        self.displayRaw = False

        self.pen = pg.mkPen(color=(52, 138, 189), width=2)
        self.pen_raw =  pg.mkPen(color=(138,52, 189), width=2)
        self.lastLoader = None
        self.lastPath = None

        self.init_layoutGraphInteractivity()


    
    def get_dataPath(self):
        """return the loader and the path to the current selected channel. 

        Returns:
            _type_: _description_
        """
        return self.parent.get_dataChannelPath()

    def setInformation(self,**kwargs):
        """Set the x and y labels and the title of the plot.
        """
        title = kwargs['title']
        xlabel = kwargs['xlabel']
        ylabel = kwargs['ylabel']
        self.plot.setLabels(left=ylabel,bottom=xlabel)
        self.plot.setLabel('top',f"<h4>{self.id}: {title}</h4>")



    def draw(self,loader=None,path=None,**kwargs):
        """Draw the data from a loader according to a path. Aplly filters if specified in the parameter Layout

        Args:
            loader (_type_, optional): _description_. Defaults to None.
            path (_type_, optional): _description_. Defaults to None.
        """

        # Save the new loader and path if any
        if loader != None:
            self.lastLoader = loader
        if path != None:
            self.lastPath = path

        #clear the plot
        logger.debug(f"Graph - In drawing function with path :{self.lastPath}")
        self.clearGraph()

        # Extract the data to draw in forms of a list of xarray from the loader and the path
        data = extracteDatafromLoaderPath(self.lastLoader,self.lastPath)
        logger.debug(f"Graph - Extracted data {data }")

        # Set up the plot's informations
        title = extractTitlefromPath(path=self.lastPath)
        xlabel = "Time (pts) "
        ylabel = "Amplitude"
        self.setInformation(title=title,xlabel=xlabel,ylabel=ylabel)

        # Display the raw data if the corresponding checkbox is checked
        if self.displayRaw:
            dataOriginal = extracteOriginalDatafromLoaderPath(self.lastLoader,self.lastPath)
            for xr in dataOriginal:
                # if isinstance(xr,np.ndarray):
                #     self.plotData = {'x':xr[0,:],'y':xr[1,:]}
                
                # else:
                y = xr.values
                x = np.arange(len(y))

                line1 = self.plot.plot(x=x,y=y,pen=self.pen_raw)
                line1.setAlpha(0.4, False)

        
        # Display the filtered data if the corresponding checkbox is checked
        for xr in data:
            if isinstance(xr,np.ndarray):
                self.plotData = {'x':xr[0,:],'y':xr[1,:]}
            
            else:
                y = xr.values
                x = np.arange(len(y))

                self.plotData = {'x':x,'y':y}
           

            self.applyFilter()
            self.plot.plot(x=self.plotData['x'],y=self.plotData['y'],pen=self.pen)
            self.plot.enableAutoRange(True)
            # pg.setConfigOption('background', 'w')

        



    def clearGraph(self):
        self.plot.clear()
        self.setInformation(title = '', xlabel = '',  ylabel = '')



    # LAYOUT FUNCTIONNALITY
    def init_layoutGraphInteractivity(self):
        """Initialize the Layout interactivity that relies on the Plot's components
        """
        self.l.processingPathChanged_handler.connect(self.oc_draw)
        self.l.checkProcessedRaw.connect(self.oc_processedRaw)
        
    def oc_processedRaw(self,checked):
        """Draw raw signal under processed one.

        Args:
            checked (_type_): _description_
        """
        self.displayRaw = checked
        self.draw()

    def oc_draw(self,path):
        self.currentPath = path
        self.draw()

    def applyFilter(self):
        """Apply pre visualisation filters
        """
        if self.currentPath[0] == 'None':
            pass
        else:
            try:
                if self.currentPath[0] == NAME_JSONFOLDER:
                    y = apply_jsonFilter(self.plotData['y'],self.currentPath[1])
                    self.plotData['y'] =y

                else:
                    func = get_item_from_path(PROCESSING,self.currentPath)
                    self.plotData['y']=func(self.plotData['y'])
            except Exception as e:
                logger.error(f'PlotLine - Filter could not be applied : {e}')



##########
# None #
#######

class NonePlot(pg.MultiPlotWidget):
    __metaclass__ = PlotGeneral

     
    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
      
        self.l = LayoutParameters2()
        self.function = 'None'



    def get_dataPath(self):
        return 

    def setInformation(self,**kwargs):
        pass


    def draw(self,loader=None,path=None,**kwargs):
        
        pass


    def clearGraph(self):
        pass


###########################
# FFT plot single channel #
###########################



class FFT(pg.MultiPlotWidget):
    __metaclass__ = PlotGeneral

     
    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
        self.plot = self.addPlot()
    
        self.l = LayoutParameters2()
        self.function = 'fft'

        self.pen = pg.mkPen(color=(52, 138, 189), width=2)
        self.lastLoader = None
        self.lastPath = None


    
    def get_dataPath(self):
        """return the loader and the path to the current selected channel

        Returns:
            _type_: _description_
        """
        return self.parent.get_dataChannelPath()

    def setInformation(self,**kwargs):
        title = kwargs['title']
        xlabel = kwargs['xlabel']
        ylabel = kwargs['ylabel']
        self.plot.setLabels(left=ylabel,bottom=xlabel)
        self.plot.setLabel('top',f"<h4>{self.id} FFT : {title}</h4>")


    def draw(self,loader=None,path=None,**kwargs):
        """Draw the data

        Args:
            loader (_type_, optional): _description_. Defaults to None.
            path (_type_, optional): _description_. Defaults to None.
        """

        # Save the new loader and path if any
        if loader != None:
            self.lastLoader = loader
        if path != None:
            self.lastPath = path

        #clear the plot
        logger.debug(f"Graph - In drawing function with path :{self.lastPath}")
        self.clearGraph()

        # Extract the data to draw in forms of a list of xarray from the loader and the path
        data = extracteDatafromLoaderPath(self.lastLoader,self.lastPath)
        logger.debug(f"Graph - Extracted data {data }")

        # Set up the plot's informations
        title = extractTitlefromPath(path=self.lastPath)
        xlabel = "Frequency (Hz)"
        ylabel = "Amplitude"
        self.setInformation(title=title,xlabel=xlabel,ylabel=ylabel)

        # Plots the fft
        for xr in data:
            y = xr.values
            x = np.arange(len(y))

            self.plot.plot(x=x,y=y,pen=self.pen)          
            self.plot.curves[0].setFftMode(True)
            self.plot.enableAutoRange(True)


    def clearGraph(self):
        self.plot.clear()
        self.setInformation(title = '', xlabel = '',  ylabel = '')



######################
# MULTI CHANNEL PLOT #
######################


class DataItemPath(pg.PlotDataItem):
    """Custom Plot Data Item for PyqtGraph.

    Args:
        pg (_type_): _description_
    """
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.path = kargs['path']


class MultiplePlot2(pg.MultiPlotWidget):
    """Plot to display multiple channels.

    Args:
        pg (_type_): _description_

    Returns:
        _type_: _description_
    """
    __metaclass__ = PlotGeneral

    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)

        self.l = LayoutParameters_MultiplePlot2()
        self.function = 'multiple_plot2'
        self.lastLoader = None
        self.lastPath = None
        self.pen = pg.mkPen(color=(52, 138, 189), width=2)

        self.column = 2
        self.limit_max = 128
        self.limit_min = 0
        self.distance = 2

        self.nb_channel = self.limit_max - self.limit_min
        self.nb_line = lambda x : np.ceil(x / self.column)
        self.title = ""

        
        self.plot = {}
        self.line = {}
        self.init_plot()


        self.data_plot = None
        self.init_interactivity()

        self.graph_child=[]

    def init_plot(self):
        for i in range(self.column):
            self.plot[i] = self.addPlot()

    def setInformation(self,**kwargs):
        for i in range(self.column):
            self.title = title = kwargs['title']
            xlabel = kwargs['xlabel']
            ylabel = kwargs['ylabel']
            self.plot[i].setLabels(left=ylabel,bottom=xlabel)
            self.plot[i].setLabel('top',f"<h4>{self.id}: {title}</h4>")


    def init_interactivity(self):
        self.l.spinBox_distance.valueChanged.connect(self.update_distance)
        self.l.comboBox_child.textActivated.connect(self.update_child_list)

    def get_dataPath(self):
        """return the loader and the path to the current selected channel

        Returns:
            _type_: _description_
        """
        return self.parent.get_dataVariablePath()

    def itemClicked(self,pltDataItem):
        print(pltDataItem,pltDataItem.path)
        path = pltDataItem.path
        try:
            gr = list(path.keys())[0]
            var = list(path[gr].keys())[0]
            dim = list(path[gr][var].keys())[0]
            ch = path[gr][var][dim]

            title = f"<h4>{self.id}: {self.title} Selected : {ch}</h4> "
            for i in range(self.column): 
                self.plot[i].setLabel('top',title)


        except:
            pass
        for child in self.graph_child:
            try:
                print(child)
                child.clearGraph()
                child.draw(self.lastLoader,pltDataItem.path)

            except Exception as e:
                logger.debug('Could not draw in child graph')
                pass
       

    # // as illustration, a way to get the nearest data from a mouse click
    # def mouse_clicked(self, mouseClickEvent): 
    #     # mouseClickEvent is a pyqtgraph.GraphicsScene.mouseEvents.MouseClickEvent
    #     # print('clicked plot 0x{:x}, event: {}'.format(id(self), mouseClickEvent))
    #     try:
    #         # plot = self.scene().itemsNearEvent(mouseClickEvent)[1]

    #         print(self.scene().itemsNearEvent(mouseClickEvent)[3].getData())
    #         print(self.graph_child)
    #         for child in self.graph_child:
    #             print(child)
    #             child.clearGraph()

    #             data_scene = np.array(self.scene().itemsNearEvent(mouseClickEvent)[3].getData())
    #             time = data_scene[0,:]
    #             y = data_scene[1,:]
    #             y_ch = np.arange(y.shape[0])
    #             xrData = xr.DataArray(y,coords=[time],dims=['time'])


    #             print('xrDataarry multiplot', xrData)
    #             child.draw([xrData])
    #     except Exception as e:
    #         print(e,'no line')
    #         pass


    

    def update_distance(self,arg):
        self.draw(self.data_plot,arg)

    

    def get_data(self):
        return self.parent.get_dataVariable()
    
    

    def draw(self,loader,path,**kwargs):

        # Save the new loader and path if any
        if loader != None:
            self.lastLoader = loader
        if path != None:
            self.lastPath = path
            self.compute_distance = True
            # compute the new distance
            

        #clear the plot
        logger.debug(f"Graph - In drawing function with path :{self.lastPath}")
        self.clearGraph()
        self.setInformation(xlabel = 'Time (pts)', ylabel = 'Amplitude', title = f"{list(self.lastPath.keys())[0]} - {list(self.lastPath[list(self.lastPath.keys())[0]].keys())[0]}")

        # Extract the data to draw in forms of a list of xarray from the loader and the path
        data = extracteDatafromLoaderPath(self.lastLoader,self.lastPath)
        data_path = extracteIndividualPathfromPath(None,path=path)

        logger.debug(f"Graph - Extracted data {data }")

        limit = np.min([self.limit_max,len(data)])
        nb_line = self.nb_line(limit)
      

        # tick_distance = np.arange(0,self.distance*nb_line,self.distance)
        # tick = []
        if  self.compute_distance:
            self.distance = np.nanmean(np.nanmax(data,axis=1)-np.nanmean(data,axis=1))
            self.l.spinBox_distance.blockSignals(True)
            self.l.spinBox_distance.setValue(self.distance)
            self.l.spinBox_distance.blockSignals(False)
            self.compute_distance = False


        # text_label = pg.LabelItem("Your text")
        # # text_label.setParentItem(self.plot[0].graphicsItem())
        # text_label.setParentItem(self.line[i])
        # text_label.anchor(itemPos=(0, 0), parentPos=(0, 0))   

        for i,i_ch in enumerate(range(self.limit_min,limit+1)):
            gr = list(data_path[i].keys())[0]
            var = list(data_path[i][gr].keys())[0]
            dim = list(data_path[i][gr][var].keys())[0]
            ch = data_path[i][gr][var][dim]

            y = data[i_ch].values
            y = y - np.mean(y) + self.distance * (i%nb_line)            

            x= np.arange(0,len(y))
          
            self.line[i] = DataItemPath(x=x,y=y,pen=self.pen,path=data_path[i])
            # self.line[i] = self.plot[i//nb_line].plot(x=x,y=y,pen=self.pen)
            self.plot[i//nb_line].addItem(self.line[i])
            self.plot[i//nb_line].enableAutoRange(True)
            self.plot[i//nb_line].enableAutoRange(True)
            self.line[i].setCurveClickable(True,10)
            text_label = pg.LabelItem(str(ch))
            # text_label.setParentItem(self.plot[0].graphicsItem())
            text_label.setParentItem(self.line[i])
            # text_label.autoAnchor((0.1,0.1),True)  

            self.line[i].sigClicked.connect(self.itemClicked)
            


    def update_settings(self):
        print('update')
        self.l.comboBox_child.clear()

        for id_graph in ['None'] + list(self.parent.dict_layout_graph.keys()):
            self.l.comboBox_child.addItem(str(id_graph))

    def update_child_list(self,arg):
        if isinstance(arg,list):
            if arg not in self.graph_child: self.graph_child = [self.parent.dict_layout_graph[int(k)].ui_graph for k in arg]
        else: 
            if arg not in self.graph_child: self.graph_child = [self.parent.dict_layout_graph[int(arg)].ui_graph ]

    def clearGraph(self):
        for i in range(self.column):
            self.plot[i].clear()
        self.setInformation(title = '', xlabel = '',  ylabel = '')




#########################
## Plot Dictionnaries
#########################

PLOT = {
    'fft':FFT,
    'plotline':PlotLine,
    # 'multiple_plot':MultiplePlot,
    'multiple_plot2':MultiplePlot2
}

