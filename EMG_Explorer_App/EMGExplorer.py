# from Explorer_package.requirement import *
from Explorer_package import *
import Explorer_package as exp
from PyQt5.QtCore import Qt

class NewFilterWindow(QWidget):

    # automatic name after preprocessing function + nb of the step
    # param : add, delete, change position

    def __init__(self):
        super().__init__()
        # self.parent = parent
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\GraphParameters.ui', self)

class SummaryWindow(QWidget):

    def __init__(self):
        super().__init__()
        # self.parent = parent
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\AnalysisWin.ui', self)

class Canvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        super().__init__(self.fig)

    def clear(self):
        self.fig.clear()


class EMGExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\EMGExplorer_mainwindow.ui', self)
        self.w = None
        self.wnewFilter = None

        self.actiontype_1.triggered.connect(self.oc_actiontype1)
        self.actionNew.triggered.connect(self.oc_newFilter)
        self.actionRun_Analysis.triggered.connect(self.oc_newSummary)

        self.menu = QMenu()
        self.menu.addAction("Delete",self.oc_action1)
        self.menu.addAction("Split",self.oc_action1)
        self.menu_type = QMenu('Change type')
        self.menu_type.addAction("type1",self.oc_action1)
        self.menu_type.addAction("type2",self.oc_action1)
        self.menu.addMenu(self.menu_type)

        self.toolButton.setMenu(self.menu)
        self.show()

        self.time = np.arange(100)
        self.signal = np.random.random(100)
        
        self.verticalLayout_2.addWidget(Canvas())
        self.verticalLayout_4.addWidget(Canvas())
        self.verticalLayout_11.addWidget(Canvas())

        self.treeWidget.itemDoubleClicked.connect(self.oc_itemPressed)

    def oc_newFilter(self):
        if self.wnewFilter is None:
            self.wnewFilter = NewFilterWindow()
        self.wnewFilter.show()

    def oc_newSummary(self):
        if self.w is None:
            self.w = SummaryWindow()
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
        self.dock = QDockWidget('dock',self)
        self.listWidget=QListWidget()
        # self.listWidget.addItem('Item1')
        # self.listWidget.addItem('Item2')
        # self.listWidget.addItem('Item3')
        # self.listWidget.addItem('Item4')

        self.dock.setWidget(self.listWidget)
        self.dock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dock)


def main():
    app = QApplication(sys.argv)
    ex = EMGExplorer()
    ex.raise_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()




# class Example(QWidget):
#     def __init__(self):
#         super(Example, self).__init__()
#         self.initUI()

#     def initUI(self):
#         hbox = QHBoxLayout(self)

#         topleft = QFrame()
#         topleft.setFrameShape(QFrame.StyledPanel)
#         bottom = QFrame()
#         bottom.setFrameShape(QFrame.StyledPanel)

#         splitter1 = QSplitter(Qt.Horizontal)
#         textedit = QTextEdit()
#         splitter1.addWidget(topleft)
#         splitter1.addWidget(textedit)
#         splitter1.setSizes([100,200])

#         splitter2 = QSplitter(Qt.Vertical)
#         splitter2.addWidget(splitter1)
#         splitter2.addWidget(bottom)

#         hbox.addWidget(splitter2)

#         self.setLayout(hbox)
#         QApplication.setStyle(QStyleFactory.create('Cleanlooks'))

#         self.setGeometry(300, 300, 300, 200)
#         self.setWindowTitle('QSplitter demo')
#         self.show()

# def main():
#    app = QApplication(sys.argv)
#    ex = Example()
#    sys.exit(app.exec_())
	
# if __name__ == '__main__':
#    main()


# class MainWindow(QMainWindow):
#     # passer les parametres du threshold de defaut dans la creation de la fenetre
#     #ajouter mode de traitement

#     def __init__(self):
#         super(MainWindow, self).__init__()

#         # self.window = QMainWindow()
#         loadUi('hdemg_viewer_exemple\\Qt_creator\\EMGExplorer_qt\\EMGExplorer_mainwindow.ui', self)
#         self.show()


# app = QApplication(sys.argv)
# w = MainWindow()
# app.exec_()

#https://stackoverflow.com/questions/28309376/how-to-manage-qsplitter-in-qt-designer 



# all in one file
# print(dir(exp.processing_function))

# import processing function
# print(os.listdir('EMG_Explorer_App/Explorer_package/processing'))
#['processing1.py', 'processing2.py', '__pycache__']


# from importlib.machinery import SourceFileLoader
 
# mod_list = []
# for name in os.listdir('EMG_Explorer_App/Explorer_package/processing'):
#     if name != '__pycache__':
#         mod_list += [name[:-3]]

# # imports the module from the given path
# PROCESSING = {}
# for name in mod_list:
#     mod = SourceFileLoader(name,f"EMG_Explorer_App/Explorer_package/processing/{name}.py").load_module()
#     PROCESSING[name] = {}

#     for fc_name in dir(mod):
#         fc = getattr(mod,fc_name)
#         if fc_name[0] != '_':
#             PROCESSING[name][fc_name] = fc

# # print(PROCESSING)
            
# PROCESSING['processing1']['add']()



# self.graph = pg.GraphicsLayoutWidget(border=pg.mkPen((0, 0, 0)))
# self.timeplot = self.graph.addPlot(row=0, col=0, rowspan=1, colspan=1)
# self.fftplot = self.graph.addPlot(row=1, col=0, rowspan=1, colspan=1)

# self.timeplot.plot(x=self.time, y=self.signal, pen=pen)
# self.timeplot.setMouseEnabled(x=True, y=False)
# self.timeplot.setLimits(xMin=0, xMax=self.time.max())
# self.timeplot.autoRange()
# self.timeplot.showGrid(x=True)
# self.timeplot.setMenuEnabled(False)
# self.timeplot.setLabel('left', "Channel {} - EMG".format(elec_id), "")
# self.timeplot.setLabel('bottom', "time", "s")
# self.timeplot.sigXRangeChanged.connect(self.update_fft)
# self.timepoint = pg.InfiniteLine(0,pen=pg.mkPen({'color': "#FF0", 'width': 4}))  # pg.CurvePoint(self.timeplot.curves[0])
# self.timeplot.addItem(self.timepoint)
# # arrow = pg.ArrowItem(angle=-90)
# # arrow.setParentItem(self.timepoint)

# self.fftplot.plot(self.time, self.signal, pen=pen)
# self.fftplot.setMouseEnabled(x=True, y=False)
# self.fftplot.showGrid(x=True)
# self.fftplot.setMenuEnabled(False)
# self.fftplot.setLabel('left', "Channel {} - Power".format(elec_id), "")
# self.fftplot.setLabel('bottom', "frequency", "Hz")
# self.fftplot.curves[0].setFftMode(True)
# self.fftplot.enableAutoRange(True)

# self.rvbox.addWidget(self.graph)
# self.ploted = True


# fct = 'rms'
#         gridvar = numpy.apply_along_axis(eval("self.{}".format(fct)), 2, gridvar) #fonctionne sans le self et rms une fonction normal ?

# @staticmethod
#     def rms(x):
#         return numpy.sqrt(x.dot(x) / x.size)