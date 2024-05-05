from .setup import *
from .custom_widget import *
from .processing_function import PROCESSING_NAME,get_item_from_path,PROCESSING,apply_jsonFilter

NAME_JSONFOLDER = 'Custom Filters'

def create_menuJson(root):
    dictJson = {NAME_JSONFOLDER: []}
    for name in os.listdir(root):
        if name[:-5]!= '.json':
            dictJson[NAME_JSONFOLDER] += [name[:-5]]

    return dictJson

class LayoutParameters(QWidget):
    processingPathChanged_handler = pyqtSignal(list)

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

    def oc_pathChanged_handler(self,path):
        print('path changed handler',path)
        self.processingPathChanged_handler.emit(path)
    

class LayoutParameters2(QWidget):

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_graph2.ui', self)



    def interactivity(self):
        pass

    
class LayoutParameters_MultiplePlot(QWidget):

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_multipleplot.ui', self)

    # def update_limit(self):
    #     self.spinBox_limit.setValue(self.spinBox_nbChannel.value() * self.spinBox_nbRow.value() * self.spinBox_nbColumn.value())
        
    def update_nbChannel(self):
        self.spinBox_nbChannel.setValue(np.ceil(self.spinBox_limit.value() / (self.spinBox_nbRow.value() * self.spinBox_nbColumn.value())))

    def interactivity(self):
        self.spinBox_nbRow.textChanged.connect(self.update_nbChannel)
        self.spinBox_nbCol.textChanged.connect(self.update_nbChannel)
        self.spinBox_limit.textChanged.connect(self.update_nbChannel)


    
class LayoutParameters_MultiplePlot2(QWidget):

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


class PlotGeneral(ABC):
     
    def __init__(self,layout,layout_graph,i,parent):
        # super().__init__()
        self.id = i
        self.layout = layout
        self.layout_graph = layout_graph
        self.parent = parent

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def clearGraph(self):
        pass

      
  

class PlotLine(pg.MultiPlotWidget):
    __metaclass__ = PlotGeneral

    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
        
        self.plot = self.addPlot(title=f'graph {self.id}')
        self.l = LayoutParameters()
        self.function = 'lineplot'
        self.plotData = None
        self.currentPath = ['None']

        self.init_layoutGraphInteractivity()


    def get_data(self):
        return self.parent.get_dataChannel()


    def draw(self,data):
        if isinstance(data,np.ndarray):
            self.plotData = {'x':data[0,:],'y':data[1,:]}
        
        else:
            y = data.values
            for t in ['Time','time']:
                if t in data.dims:
                    x = np.array(data[t])

            self.plotData = {'x':x,'y':y}

        self.applyFilter(self.currentPath)
        self.plot.enableAutoRange(True)



    def clearGraph(self):
        self.plot.clear()

    # LAYOUT FUNCTIONNALITY
    def init_layoutGraphInteractivity(self):
        print('layout graph interactivity init')
        self.l.processingPathChanged_handler.connect(self.applyFilter)

    def applyFilter(self,path):
        print('apply filter :',path)
        self.currentPath = path
        if path[0] == 'None':
            self.plot.plot(x=self.plotData['x'],y=self.plotData['y'])
        else:
            self.clearGraph()
            if path[0] == NAME_JSONFOLDER:
                y = apply_jsonFilter(self.plotData['y'],path[1])
                self.plot.plot(x=self.plotData['x'],y=y)

            else:
                func = get_item_from_path(PROCESSING,path)
                print('function from path', func)
                self.plot.plot(x=self.plotData['x'],y=func(self.plotData['y']))



class FFT(pg.MultiPlotWidget):
    __metaclass__ = PlotGeneral

     
    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
        self.plot = self.addPlot(title=f'graph {self.id}')
    
        self.l = LayoutParameters2()
        self.function = 'fft'



    def get_data(self):
        return self.parent.get_dataChannel()

    def draw(self,data):
        y = data.values

        for t in ['Time','time']:
            if t in data.dims:
                x = np.array(data[t])

        self.plot.plot(x=x,y=y)

        # self.fftplot.setMouseEnabled(x=True, y=False)
        self.plot.showGrid(x=True)
        # self.fftplot.setMenuEnabled(False)
        # self.fftplot.setLabel('left', "Channel {} - Power".format(elec_id), "")
        self.plot.setLabel('bottom', "frequency", "Hz")
        self.plot.curves[0].setFftMode(True)
        self.plot.enableAutoRange(True)

        # self.fftplot.enableAutoRange(True)
        

    def clearGraph(self):
        self.plot.clear()


class MultiplePlot(pg.MultiPlotWidget):
    __metaclass__ = PlotGeneral

    def __init__(self, layout, layout_graph, i, parent):
        self.row = 4
        self.column = 2
        self.limit_max = 128
        self.limit_min = 0
        self.nb_channel = self.limit_max - self.limit_min
        self.nb_plot = self.row * self.column
        self.nb_line =  np.ceil(self.nb_channel / self.nb_plot)



#       p3 = win.addPlot(title="Drawing with points")
# p3.plot(np.random.normal(size=100), pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')


# win.nextRow()

        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
        
        self.plot = {}
        self.init_plot()
        
        self.l = LayoutParameters()
        self.function = 'multiple_plot'


    def init_plot(self):
        for i in range(self.nb_plot):
            if (i%self.column==0) and (i!=0):
                self.nextRow()
            self.plot[i] = self.addPlot(title=f'graph {self.id}')

    def get_data(self):
        return self.parent.get_dataVariable()

    def draw(self,data):
        print('draw')

        limit = np.min([self.limit_max,len(data)])
        print('draw',limit)

        i_plot = 0
        self.nb_line = np.ceil(limit-self.limit_min / self.nb_plot)

        for i_ch in range(self.limit_min,limit+1):
            y = data[i_ch].values

            for t in ['Time','time']:
                if t in data.dims:
                    x = np.array(data[t])
            print(y)
            self.plot[i_plot%self.nb_line].plot(x=x,y=y)
            self.plot[i_plot%self.nb_line].enableAutoRange(True)
            i_plot +=1
        # self.plot.setXRange(min(x), max(x), padding=0)

        # self.plot.enableAutoRange(True)


    def clearGraph(self):
        for i in range(self.nb_plot):
            self.plot[i].clear()

def Try_decorator(function):
    print('in deco')
    def wrapper(*arg):
        try:
            function(*arg)
        except Exception as e:
            print(function.__name__)
            print(e)

    return wrapper






class ComboBoxcustom(QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(QComboBox, self).showPopup()




class MultiplePlot2(pg.MultiPlotWidget):
    __metaclass__ = PlotGeneral

    def __init__(self, layout, layout_graph, i, parent):
        self.column = 2
        self.limit_max = 128
        self.limit_min = 0
        self.distance = 2

        self.nb_channel = self.limit_max - self.limit_min
        self.nb_line = lambda x : np.ceil(x / self.column)


        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
        
        self.plot = {}
        self.line = {}
        self.init_plot()


        self.l = LayoutParameters_MultiplePlot2()
        self.function = 'multiple_plot2'
        self.data_plot = None
        self.init_interactivity()

        self.graph_child=[]
        self.scene().sigMouseClicked.connect(self.mouse_clicked) 


    def mouse_clicked(self, mouseClickEvent):
        # mouseClickEvent is a pyqtgraph.GraphicsScene.mouseEvents.MouseClickEvent
        # print('clicked plot 0x{:x}, event: {}'.format(id(self), mouseClickEvent))
        try:
            plot = self.scene().itemsNearEvent(mouseClickEvent)[1]

            print(self.scene().itemsNearEvent(mouseClickEvent)[3].getData())
            print(self.graph_child)
            for child in self.graph_child:
                print(child)
                child.clearGraph()
                child.draw(np.array(self.scene().itemsNearEvent(mouseClickEvent)[3].getData()))
        except Exception as e:
            print(e,'no line')
            pass


    @Try_decorator
    def init_interactivity(self):
        self.l.spinBox_distance.valueChanged.connect(self.update_distance)
        self.l.comboBox_child.textActivated.connect(self.update_child_list)
        self.l.comboBox_child.view().pressed.connect(print('updafe'))   
        print('fin')



    @Try_decorator
    def update_distance(self,arg):
        self.draw(self.data_plot,arg)

    def init_plot(self):
        for i in range(self.column):
            self.plot[i] = self.addPlot(title=f'graph {self.id}')

    def get_data(self):
        return self.parent.get_dataVariable()

    @Try_decorator
    def draw(self,data,distance=None,timestamp=False):
        self.clearGraph()
        print('draw')
        self.data_plot = data

        limit = np.min([self.limit_max,len(data)])

        nb_line = self.nb_line(limit)
        if not distance:
            self.distance = np.nanmean(np.nanmax(data,axis=1)-np.nanmean(data,axis=1))
            self.l.spinBox_distance.blockSignals(True)
            self.l.spinBox_distance.setValue(self.distance)
            self.l.spinBox_distance.blockSignals(False)

        else:
            self.distance = distance


        tick_distance = np.arange(0,self.distance*nb_line,self.distance)
        tick = []
        for i,i_ch in enumerate(range(self.limit_min,limit+1)):
            y = data[i_ch].values
            y = y - np.mean(y) + self.distance * (i%nb_line)            

            if timestamp:
                for t in ['Time','time']:
                    if t in data.dims:
                        x = np.array(data[t])
                        try:
                            tick = t.values()
                        except : pass
            else:
                x= np.arange(0,len(y))

            self.line[i] = self.plot[i//nb_line].plot(x=x,y=y)
            self.plot[i//nb_line].addItem(self.line[i])
            self.plot[i//nb_line].enableAutoRange(True)
            self.plot[i//nb_line].enableAutoRange(True)
            # self.line[i].sigClicked.connect(lambda x: print('connect'))

        print('draw done')

    @Try_decorator
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



PLOT = {
    'fft':FFT,
    'plotline':PlotLine,
    'multiple_plot':MultiplePlot,
    'multiple_plot2':MultiplePlot2
}

# Emplacement -> type de widget
# type de widget -> Graph
# Graph -> setting du graph