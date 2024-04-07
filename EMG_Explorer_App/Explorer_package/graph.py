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


    

class MyMultiPlotWidget2(pg.MultiPlotWidget):
        def __init__(self,i):
            pg.MultiPlotWidget.__init__(self)
            self.id = i
            self.plot = self.addPlot(title=f'graph {self.id}')

        def clear():
            pass

        def mouseDoubleClickEvent(self, event):
            event.accept()
            




class PlotGeneral(MyMultiPlotWidget2):
     
    def __init__(self,layout,layout_graph,i,parent):
        super().__init__(i)
        self.layout = layout
        self.layout_graph = layout_graph
        self.parent = parent

      
  

class PlotLine(PlotGeneral):
    def __init__(self, layout, layout_graph, i, parent):
        self.l = LayoutParameters()
        self.function = 'lineplot'
        super().__init__(layout, layout_graph, i, parent)



    def draw(self,y,x=None):
        if not x:
            x = np.arange(len(y))
        self.fig.plot.plot(x=x,y=y)

    def clear(self):
        self.fig.clear()

class FFT(PlotGeneral):
     
    def __init__(self, layout, layout_graph, i, parent):
        self.l = LayoutParameters2()
        self.function = 'fft'

        super().__init__(layout, layout_graph, i, parent)




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