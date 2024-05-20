from .setup import *


# data =[{
#         "Courses": ["Math", "Science", "English"]
#     },
#     {
#         "Cars": ["Ford", "BMW", "Mercedes"]
#     }
# ]

#   combo = ComboBoxExpandable()
#         combo.setData(data)

#         result_label = QtWidgets.QLabel()

#         combo.currentTextChanged.connect(result_label.setText)
#         combo.pathChanged.connect(print)

#         lay = QtWidgets.QFormLayout(self)
#         lay.addRow("Select: ", combo)

def menu_from_dict(dict_):
    menu = {}
    list_k = []
    for k,v in dict_.items():
        if isinstance(v,dict):
            menu[k] = menu_from_dict(v)
        else:
            return list(dict_.values())
        


class comboBoxCheckable(QtWidgets.QPushButton):

    currentTextChanged = QtCore.pyqtSignal(list)

    def __init__(self,name=' '):
        super().__init__()
        self.init_menu(name)

    def init_menu(self,name):
        self.setText(name)

    def setData(self,data):
        self.menu = QtWidgets.QMenu(self)
        self.all = QtWidgets.QAction('All',self.menu )
        self.all.setCheckable(True)
        self.none = QtWidgets.QAction('None',self.menu )
        self.none.setCheckable(True)
        self.menu.addAction(self.all)
        self.menu.addAction(self.none)


        for element in data:
            action = QtWidgets.QAction(element,self.menu)
            action.setCheckable(True)
            self.menu.addAction(action)
        
        self.menu.triggered.connect(self.on_triggered)
        self.setMenu(self.menu)

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def on_triggered(self, action):
        text = action.text()
        if text == 'All':
            self.on_checked_all(action)
        elif text == 'None':
            self.on_checked_none(action)
        else:
            self.all.setChecked(False)
            self.none.setChecked(False)


        self.currentTextChanged.emit(self.list_checked())
        print(self.list_checked())

    def list_checked(self):
        list_checked = [action.text() for action in self.menu.actions() if (action.isChecked()) and (action.text()!='All') and (action.text()!='None') ]
        return list_checked
    
    def on_checked_all(self,action):
        self.menu.blockSignals(True)

        if action.isChecked():
            for action in self.menu.actions():
                action.setChecked(True)
            self.none.setChecked(False)
        else:
            for action in self.menu.actions():
                action.setChecked(False)

        self.menu.blockSignals(False)


    def on_checked_none(self,action):
        self.menu.blockSignals(True)

        for action in self.menu.actions():
            if action.text() != 'None':
                action.setChecked(False)

        self.menu.blockSignals(False)


        


# retrouver la référence internet
class ComboBoxExpandable(QtWidgets.QPushButton):
    """Exandable comboBox

    Args:
        QtWidgets (_type_): _description_
    """
    currentTextChanged = QtCore.pyqtSignal(str)
    pathChanged = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def setData(self, value):
        menu = QtWidgets.QMenu(self)
        self.setMenu(menu)
        self.append_element(value, menu)
        menu.triggered.connect(self.on_triggered)

    def append_element(value, menu):
        if isinstance(value, list):
            for e in value:
                ComboBoxExpandable.append_element(e, menu)
        elif isinstance(value, dict):
            for k, v in value.items():
                ComboBoxExpandable.append_element(v, menu.addMenu(k))
        else:
            menu.addAction(value)

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def on_triggered(self, action):
        self.setText(action.text())
        path = [action.text()] 
        w = action.parentWidget()
        while w.parentWidget() and isinstance(w.parentWidget(), QtWidgets.QMenu):
            path.insert(0, w.title())
            w = w.parentWidget()
        self.pathChanged.emit(path)
        self.currentTextChanged.emit(self.text())

    @staticmethod
    def append_element(value, menu):
        if isinstance(value, list):
            for e in value:
                ComboBoxExpandable.append_element(e, menu)
        elif isinstance(value, dict):
            for k, v in value.items():
                ComboBoxExpandable.append_element(v, menu.addMenu(k))
        else:
            menu.addAction(value)




class PopupMenuParameter2(parameterTypes.ActionParameter):
    pathChanged = pyqtSignal(list)

    def __init__(self, **opts):
        super().__init__(**opts)
        self.button = ComboBoxExpandable()
        self.sigActivated.connect(self.showMenuPopup)
        self.button.pathChanged.connect(self.oc_pathChanged)

    def showMenuPopup(self):
        self.button.menu().popup(QtGui.QCursor.pos())
    
    def setData(self,data):
        self.button.setData(data)

    def oc_pathChanged(self,path):
        self.pathChanged.emit(path)



registerParameterType('popupmenu', PopupMenuParameter2, override=True)

# # Create parameters
# params = [
#     {'name': 'PopupMenuParameter', 'type': 'popupmenu', 'title': '+'},
# ]

# # Create parameter tree and set parameters
# param_tree = ParameterTree()
# parameter = Parameter.create(name='params', type='group', children=params)

# param_tree.setParameters(parameter)
# parameter.child('PopupMenuParameter').button.setData({"1":{"3":"4","5":"6"}})         
    