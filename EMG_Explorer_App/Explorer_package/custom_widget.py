from PyQt5 import QtCore, QtWidgets

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