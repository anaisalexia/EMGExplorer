from .setup import *


class LayoutParameters(QWidget):

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_graph.ui', self)

    def interactivity(self):
        pass


class LayoutParameters2(QWidget):

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_graph2.ui', self)


    def interactivity(self):
        pass


    



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



    def draw(self,data):

        y = data.values

        for t in ['Time','time']:
            if t in data.dims:
                x = np.array(data[t])

        self.plot.plot(x=x,y=y)
        # self.plot.setXRange(min(x), max(x), padding=0)

        self.plot.enableAutoRange(True)


    def clearGraph(self):
        self.plot.clear()



class FFT(pg.MultiPlotWidget):
    __metaclass__ = PlotGeneral

     
    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
        self.plot = self.addPlot(title=f'graph {self.id}')
    
        self.l = LayoutParameters2()
        self.function = 'fft'





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





PLOT = {
    'fft':FFT,
    'plotline':PlotLine
}

# Emplacement -> type de widget
# type de widget -> Graph
# Graph -> setting du graph