from .setup import *


class LayoutParameters(QWidget):

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_graph.ui', self)

        # add widget combobox option for instance
        # add interactivity between parameters of the layout
         ## Windows Parameters
        # # Definition of the button Parameters ...
        # self.menu = QMenu()
        # self.menu.addAction("Delete",self.oc_action1)
        # self.menu.addAction("Split",self.oc_action1)
        # self.menu_type = QMenu('Change type')
        # self.menu_type.addAction("type1",self.oc_action1)
        # self.menu_type.addAction("type2",self.oc_action1)
        # self.menu.addMenu(self.menu_type)

        # self.toolButton.setMenu(self.menu)

    def interactivity(self):
        pass


class LayoutParameters2(QWidget):

    def __init__(self,):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\parameters_graph2.ui', self)

        # add widget combobox option for instance
        # add interactivity between parameters of the layout
         ## Windows Parameters
        # # Definition of the button Parameters ...
        # self.menu = QMenu()
        # self.menu.addAction("Delete",self.oc_action1)
        # self.menu.addAction("Split",self.oc_action1)
        # self.menu_type = QMenu('Change type')
        # self.menu_type.addAction("type1",self.oc_action1)
        # self.menu_type.addAction("type2",self.oc_action1)
        # self.menu.addMenu(self.menu_type)

        # self.toolButton.setMenu(self.menu)

    def interactivity(self):
        pass


class Figure():

    def plot(x,y):
         pass
    
    def clear():
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
        self.layout = self.parent.layout_param
        self.layout_graph = layout_graph
        self.parent = parent

        for fc in PLOT.keys():
            self.l.comboBox_type.addItem(fc)
        self.l.comboBox_type.setCurrentIndex(np.max([0,self.l.comboBox_type.findText(self.function)])) 

        self.l.comboBox_type.currentIndexChanged.connect(self.oc_comboBox_type_change)

       
    
    def mouseDoubleClickEvent(self, event):
        print('clicked')
        self.parent.current_id = self.id
        self.layout.removeItem(self.layout.findChild(QGridLayout))
        if self.layout.findChild(QGridLayout):
            self.layout.findChild(QGridLayout).deleteLater()
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        self.grid.addWidget(self.l)
        event.accept()
        
    def oc_comboBox_type_change(self):
        print('change')
        plot = PLOT[self.l.comboBox_type.currentText()](self.parent.layout_param,self.parent.dict_layout_graph[self.parent.current_id],int(self.parent.current_id),self.parent)
        self.parent.dict_layout_graph[self.parent.current_id].removeWidget(self.parent.dict_displayed_graph[self.parent.current_id])
        # self.gridLayout_3.removeWidget(self.layout)
        # self.layout.deleteLater()

        self.parent.dict_displayed_graph[self.parent.current_id] =  plot
        self.parent.dict_layout_graph[self.parent.current_id].addWidget(self.parent.dict_displayed_graph[self.parent.current_id])
    

class PlotLine(PlotGeneral):
    def __init__(self, layout, layout_graph, i, parent):
        self.l = LayoutParameters()
        self.function = 'lineplot'
        super().__init__(layout, layout_graph, i, parent)


        # for fc in PLOT.keys():
        #     self.l.comboBox_type.addItem(fc)
        # self.l.comboBox_type.setCurrentIndex(np.max([0,self.comboBox_group.findText(self.function)])) 

        # self.l.comboBox_type.currentIndexChanged.connect(self.oc_comboBox_type_change)

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

        # for fc in PLOT.keys():
        #     self.l.comboBox_type.addItem(fc)
        # self.l.comboBox_type.setCurrentIndex(np.max([0,self.comboBox_group.findText(self.function)])) 

        # self.l.comboBox_type.currentIndexChanged.connect(self.oc_comboBox_type_change)
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