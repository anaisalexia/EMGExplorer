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
        
        self.id = i

        self.layout = layout
        self.layout_graph = layout_graph
        self.parent = parent

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def clear(self):
        pass

      
  

class PlotLine(PlotGeneral,pg.MultiPlotWidget):

    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)

        self.l = LayoutParameters()
        self.function = 'lineplot'
        super().__init__(layout, layout_graph, i, parent)



    def draw(self,y,x=None):
        if not x:
            x = np.arange(len(y))
        self.fig.plot.plot(x=x,y=y)

    def clear(self):
        self.fig.clear()



class FFT(PlotGeneral,pg.MultiPlotWidget):
     
    def __init__(self, layout, layout_graph, i, parent):
        PlotGeneral.__init__(self,layout, layout_graph, i, parent)
        pg.MultiPlotWidget.__init__(self)
    
        self.l = LayoutParameters2()
        self.function = 'fft'





    def draw(self,y,x=None):
        if not x:
            x = np.arange(len(y))
        self.fig.plot.plot(x=x,y=y)

        self.fftplot.plot(self.time, self.signal)
        # self.fftplot.setMouseEnabled(x=True, y=False)
        self.fig.plot.showGrid(x=True)
        # self.fftplot.setMenuEnabled(False)
        # self.fftplot.setLabel('left', "Channel {} - Power".format(elec_id), "")
        self.fig.plot.setLabel('bottom', "frequency", "Hz")
        self.fig.plot.curves[0].setFftMode(True)
        # self.fftplot.enableAutoRange(True)
        

    def clear(self):
        self.fig.clear()





PLOT = {
    'fft':FFT,
    'plotline':PlotLine
}

# Emplacement -> type de widget
# type de widget -> Graph
# Graph -> setting du graph