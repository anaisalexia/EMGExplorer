from .setup import *
from .mainwindow_utils import Try_decorator,get_item_from_path
from .custom_widget import ComboBoxExpandable
from .processing_function import *

logger = logging.getLogger('main')



class OneSetting(pTypes.GroupParameter):
    """Create One Groupe Parameter that will correspond to one function in the processing pipeline

    Args:
        pTypes (_type_): _description_
    """
    delete_trigger = pyqtSignal('PyQt_PyObject')
    position_trigger = pyqtSignal('PyQt_PyObject','PyQt_PyObject')

    @Try_decorator
    def __init__(self, c_f,name,pos,p,path):
        self.function = c_f
        self.path = path
        self.position = pos
        self.parent_param = p
        self.nameSetting = name
        opts = {'name':name}
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        # retrieve the name of the arguments of the function
        self.var = list(inspect.signature(self.function).parameters.keys())
        # retrieve the default value of the arguments of the function
        var_default = [inspect.signature(self.function).parameters[v].default if inspect.signature(self.function).parameters[v].default != inspect._empty else None for  v in self.var]
        # add as many None value as there are arguments without default value
        if var_default:
            var_default = [None for i in range(len(self.var)-len(var_default))] + list(var_default)
        else:
            var_default = [None for i in range(len(self.var))]
        
        # action Delete and Position to the Groupe Parameter
        self.addChild({'name': 'Functionality', 'type': 'group', 'children': [
        {'name': 'Delete', 'type': 'action'},
        {'name' : 'Position', 'type':'str','value':self.position}
        ]})
        self.param('Functionality','Delete').sigActivated.connect(self.oc_delete_handler)
        self.param('Functionality','Position').sigValueChanged.connect(self.oc_position_handler)


        # Add each argument as input field of the Parameter
        for i,v in enumerate(self.var):
            d = var_default[i]
            if d:
                self.addChild({'name': v, 'type': type(d).__name__, 'value': d, 'siPrefix': True})
            else:
                self.addChild({'name': v})
            # self.param(v).sigValueChanged.connect(self.aChanged) // as illustration for future usage

        self.exefunction = None
    
    def oc_delete_handler(self):
        """ emit delete_trigger signal with the position of the element in the processing pipeline"""
        self.delete_trigger.emit(self.position)

    def oc_position_handler(self,param,val):
        """ emit position_triggered signal with the position of the element in the processing pipeline and the value of the new position """
        self.position_trigger.emit(self.position,val)

    # def aChanged(self): // as illustration for future usage
        # pass
        
    


class Filters():
    """ParameterTree that represents a Processing Pipeline. Filter is a composition of Group Parameter (Setting)
    """
    def __init__(self,list_f=None,path=None) -> None:
        self.listChildren = {} if not list_f else list_f
        self.nb = len(self.listChildren.keys())
        print('nb child init', self.nb)
        self.tree = ParameterTree()
        self.path = path
        
        self.CreateTree()

    
    @Try_decorator
    def addNew(self,c_f,path):
        """Add a filter

        Args:
            c_f (function)
            path (list): list of key to reach the function in a PROCESSING dicitonnary
        """
        base_name = f"{path[-1]}_[{'_'.join(path[:-1])}]_"
        val_fc = lambda x:  f"{base_name}{x}"
        val = val_fc(0)

        # check if there is already a setting with the same name
        i = 0
        for id,existingsetting in self.listChildren.items():
            if val == existingsetting.nameSetting:
                while(val == existingsetting.nameSetting):
                    val = val_fc(i)
                    i += 1

        # create and add a new setting that wil represents the function        
        setting = OneSetting(c_f,val,self.nb,self,path)
        setting.delete_trigger.connect(self.oc_delete)
        setting.position_trigger.connect(self.oc_position)
        
        self.p.addChild(setting)
        self.listChildren[self.nb] = setting
        self.nb += 1

    def clearTree(self):
        """clear the Tree of filters"""
        self.p.clearChildren()
        self.listChildren = {}
        self.nb = 0

    def CreateTree(self):
        """Initialization of the Tree of Settings"""
        if self.path:
            self.p = Parameter.create(name='params', type='group',children=list(self.listChildren.values()))
            # self.LoadJson()
            self.tree.addParameters(self.p)

        else:
            self.p = Parameter.create(name='params', type='group', children=list(self.listChildren.values()))
            self.tree.addParameters(self.p)

    def LoadJson(self,path):
        """Load a JSON file which structure correspong to a dictionnary of Settings"""

        self.path = path
        f = open(self.path)
        data = json.load(f)

        # add a Setting for each processing of the file
        for pos,process in data.items():
            pos = int(pos) 

            if pos < self.nb:
                pos+=self.nb
            # get function
            func = get_item_from_path(PROCESSING,process['path'])
            # get path
            path = process['path']
            # add new
            self.addNew(func,path)
            # change argument
            for name_arg,val_arg in process['arguments'].items():
                # put the default value
                self.listChildren[pos].param(name_arg).setValue(val_arg)

        

    def shift_position(self,new_nb,type,nb_current=None):
        """Shift the proccessing of a pipeline by incrementing or decrementing their positions

        Args:
            new_nb (_type_): _description_
            type (_type_): _description_
            nb_current (_type_, optional): _description_. Defaults to None.
        """

        if nb_current == None:
            print('shift default value')
            nb_current = self.nb 

        if type == 'add': # new_nb<nb_current
            for n in range(nb_current-1,new_nb-1,-1):
                print('add',n,'to',n+1)
                self.listChildren[n+1] = self.listChildren[n]
                self.listChildren[n+1].position = n + 1
                self.listChildren[n+1].param('Functionality','Position').setValue(n+1,blockSignal=self.listChildren[n+1].oc_position_handler)

        elif type == 'del': # new_nb>nb_current
            for n in range(nb_current,new_nb):
                print('del',n+1,'to',n)
                self.listChildren[n] = self.listChildren[n+1]
                self.listChildren[n].position = n 
                self.listChildren[n].param('Functionality','Position').setValue(n,blockSignal=self.listChildren[n].oc_position_handler)


    def oc_delete(self,nb):
        """Delete one Setting from the pipeline

        Args:
            nb (_type_): _description_
        """
        self.p.removeChild(self.listChildren[nb])
        self.listChildren.pop(nb)
        if nb == self.nb-1:
            pass
        else:
             for n in range(nb,self.nb -1):
                self.listChildren[n] = self.listChildren[n+1]
                self.listChildren[n].position = n 
                self.listChildren[n].param('Functionality','Position').setValue(n,blockSignal=self.listChildren[n].oc_position_handler)

        self.nb -= 1
    
    def oc_position(self,nb,new_val):
        """Change the position of one Setting"""

        new_val = int(new_val)
        self.p.removeChild(self.listChildren[nb])
        self.p.insertChild(new_val,self.listChildren[nb])

        self.listChildren[nb].position = new_val
        if nb > new_val:
            print('shift add', nb,new_val)
            child = self.listChildren[nb]
            self.shift_position(new_val,'add',nb)
            self.listChildren[new_val] = child
        if new_val > nb:
            print('shift del',nb,new_val)
            child = self.listChildren[nb]
            self.shift_position(new_val,'del',nb)
            self.listChildren[new_val] = child

    def setting_to_json(self):
        """Return a dict that describs the structure of the processign pipeline"""
        dictjson = {}
        for n in range(self.nb):
            setting = self.listChildren[n]
            dictjson[n]={'name': setting.function.__name__,
                         'process name': setting.nameSetting,
                         'path':setting.path,
                         'arguments':dict(zip(setting.var,[setting.param(v).value() for v in setting.var]))}

        return dictjson



class SingleProcessing(QWidget):
    """QWidget that manages the creation of a single processing pipeline for pre visualization."""

    processingSaved = pyqtSignal(str)
    apply = pyqtSignal()

    def __init__(self,parent):
        super().__init__()
        
        # Loading of the UI
        self.p = parent
        loadUi('hdemg_viewer_exemple\\Qt_creator\\EMGExplorer_qt\\layout_singleProcessing.ui', self)

        # Creation of the Tree
        self.paramtree = Filters(None)
        self.layout_setting.addWidget(self.paramtree.tree)
        self.button_openJson.clicked.connect(self.oc_openFilter)
        self.button_clearFilter.clicked.connect(self.paramtree.clearTree)

        # Initialization and Instantiation of the comboBox for the Global Processing Selection
        self.comboExpandable = ComboBoxExpandable()
        self.comboExpandable.setData(PROCESSING_NAME)
        self.layout_expComboBox.addWidget(self.comboExpandable)

        self.comboExpandable.pathChanged.connect(self.oc_add_filter)
        self.button_saveFilterAs.clicked.connect(self.oc_saveFilter)
        self.button_saveFilter.clicked.connect(lambda x :self.oc_saveFilter(save=True))
        self.button_apply.clicked.connect(lambda x : self.apply.emit())

        self.open_processing_path = []

    
    def oc_openFilter(self):
        # get path
        path = QFileDialog.getOpenFileName(self, 'Open File',)
                                       #"/home/jana/untitled.png",
                                    #    "Json (*.json)")
        #open filter
        self.paramtree.LoadJson(path[0])
        self.open_processing_path = path[0]

    
    def oc_add_filter(self,path):
        """Add a filter to the pipeline

        Args:
            path (str): path to the clicked section of the menu. eg ['group 1','name']
        """
        self.paramtree.addNew(get_item_from_path(PROCESSING,path),path )

    def oc_saveFilter(self,save=False):
        """Save the description of the processing pipeline in a JSON file"""
        dictjson = self.paramtree.setting_to_json()

        if not save:
            namepath = QFileDialog.getSaveFileName(self, 'Save File',
                                        #"/home/jana/untitled.png",
                                        "Json (*.json)")
            if os.path.exists(f'{namepath[0]}.json'):
                logger.warning(f"Single Processing - Processing could not be saved, the file {namepath[0]} already exists ")
            else:
                with open(f'{namepath[0]}.json', 'w') as f:
                    json.dump(dictjson, f)
                logger.info(f"Single Processing - Processing saved in file {namepath[0]} ")

        
        else:            
            with open(f'{self.open_processing_path}', 'w') as f:
                json.dump(dictjson, f)
            if os.path.exists(f'{self.open_processing_path}'):
                logger.warning(f"Single Processing - Processing saved, the file {self.open_processing_path} has been overwritten ")
            else:
                logger.info(f"Single Processing - Processing saved in file {self.open_processing_path} ")






#####################
## GLOBAL PROCESSING
####################

class GroupParametersGlobalProcessing(QWidget):
    """Manage the parameters tree of one variable

    Args:
        QWidget (_type_): _description_

    Returns:
        _type_: _description_
    """

    delete_trigger = pyqtSignal(str)

    def __init__(self,name):
        super().__init__()
        self.groupName = name
        self.listProcessing = {} 
        self.nb = len(self.listProcessing.keys()) 

        self.groupParamters = Parameter.create( name=self.groupName, type='group')
        self.groupParamters.addChild({'name': 'Functionality', 'type': 'group', 'children': [
        {'name': 'Delete', 'type': 'action'},
        {'name': 'Load', 'type': 'action'},
        ]})
        self.paramsAdd = Parameter.create(name='Add', type='popupmenu', title= '+')
        self.groupParamters.child('Functionality').addChild(self.paramsAdd)
        self.paramsAdd.setData(PROCESSINGGLOBAL_NAME)

        self.paramsAdd.pathChanged.connect(lambda path : self.addNew(get_item_from_path(PROCESSINGGLOBAL,path),path ))
        self.groupParamters.param('Functionality','Delete').sigActivated.connect(self.oc_delete_handler)

        self.groupParamters.param('Functionality','Load').sigActivated.connect(self.oc_open)


    def oc_delete_handler(self):
        self.delete_trigger.emit(self.groupName)

    def getParameters(self):

        return self.groupParamters
    
    def addNew(self,processing,path):
        """Add a filter

        Args:
            val (_type_): _description_
        """

        # create an unique name for the Parameter so it can be added to the Tree
        val_fc = lambda x: f"{path[-1]}_[{'_'.join(path[:-1])}]_{x} "
        val = val_fc(0)   

        i = 1
        for id,existingsetting in self.listProcessing.items():
            if val == existingsetting.nameSetting:
                while(val == existingsetting.nameSetting):
                    val = val_fc(i)
                    i += 1

        # Add a new Filter to the pipeline
        setting = OneSetting(processing,val,self.nb,self,path)
        setting.delete_trigger.connect(self.oc_delete)
        setting.position_trigger.connect(self.oc_position)
        
        self.groupParamters.addChild(setting)
        self.listProcessing[self.nb] = setting
        self.nb += 1    

    def clearGroupParameters(self):
        self.groupParamters.clearChildren()
        self.nb = 0

    def oc_open(self):
        path = QFileDialog.getOpenFileName(None, 'Open File')
                                       #"/home/jana/untitled.png",
                                    #    "Json (*.json)")
        #open filter
        print('path open is', path)
        self.LoadJson(path[0])
    

    def LoadJson(self,path,data=None):
        # self.p.clearChildren()
        if (path == None) and (data != None):
            data = data
        else:
            self.path = path
            f = open(self.path)
            data = json.load(f)
        

        for pos,process in data.items():
            pos = int(pos) 

            if pos < self.nb:
                pos+=self.nb
            # get function
            func = get_item_from_path(PROCESSINGGLOBAL,process['path'] )
            # get path
            path = process['path']
            # add new
            self.addNew(func,path)
            # change argument
            for name_arg,val_arg in process['arguments'].items():
                # put the default value
                print(name_arg,val_arg,self.listProcessing[pos].param(name_arg).value())
                self.listProcessing[pos].param(name_arg).setValue(val_arg)
                print(name_arg,val_arg,self.listProcessing[pos].param(name_arg).value())


    def shift_position(self,new_nb,type,nb_current=None):
        if nb_current == None:
            print('shift default value')
            nb_current = self.nb


        # else:
        if type == 'add': # new_nb<nb_current
            for n in range(nb_current-1,new_nb-1,-1):
                print('add',n,'to',n+1)
                self.listProcessing[n+1] = self.listProcessing[n]
                self.listProcessing[n+1].position = n + 1
                self.listProcessing[n+1].param('Functionality','Position').setValue(n+1,blockSignal=self.listProcessing[n+1].oc_position_handler)

        elif type == 'del': # new_nb>nb_current
            print('IN ELIF DEL',new_nb,nb_current )
            for n in range(nb_current,new_nb):
                print('del',n+1,'to',n)
                self.listProcessing[n] = self.listProcessing[n+1]
                self.listProcessing[n].position = n 
                self.listProcessing[n].param('Functionality','Position').setValue(n,blockSignal=self.listProcessing[n].oc_position_handler)


    def oc_delete(self,nb):
        print(nb)
        self.groupParamters.removeChild(self.listProcessing[nb])
        self.listProcessing.pop(nb)
        if nb == self.nb-1:
            pass
        else:
             for n in range(nb,self.nb -1):
                print('del',n+1,'to',n)
                self.listProcessing[n] = self.listProcessing[n+1]
                self.listProcessing[n].position = n 
                self.listProcessing[n].param('Functionality','Position').setValue(n,blockSignal=self.listProcessing[n].oc_position_handler)

        self.nb -= 1
    
    def oc_position(self,nb,new_val):
        print('oc_posiiiiition',nb,new_val)
        new_val = int(new_val)
        self.groupParamters.removeChild(self.listProcessing[nb])
        self.groupParamters.insertChild(new_val+1,self.listProcessing[nb])

        
        self.listProcessing[nb].position = new_val
        if nb > new_val:
            print('shift add', nb,new_val)
            child = self.listProcessing[nb]
            self.shift_position(new_val,'add',nb)
            self.listProcessing[new_val] = child
        if new_val > nb:
            print('shift del',nb,new_val)
            child = self.listProcessing[nb]
            self.shift_position(new_val,'del',nb)
            self.listProcessing[new_val] = child

    def setting_to_json(self):
        dictjson = {}
        for n in range(self.nb):
            setting = self.listProcessing[n]
            dictjson[n]={'name':setting.function.__name__,
                        'process name': setting.nameSetting,

                         'path':setting.path,
                         'arguments':dict(zip(setting.var,[setting.param(v).value() for v in setting.var]))}

        return dictjson



class GlobalProcessingTab(QWidget):
    """Widget for creating and editing a global Processing

    Args:
        QWidget (_type_): _description_

    Returns:
        _type_: _description_
    """

    processingSaved = pyqtSignal(str)

    def __init__(self,parent):
        super().__init__()
        
        # Loading of the UI
        loadUi('hdemg_viewer_exemple\\Qt_creator\\EMGExplorer_qt\\layout_globalProcessing.ui', self)
        self.p = parent

        self.globalProcessingTree = ParameterTree()
        self.layout_Processing.addWidget(self.globalProcessingTree)
        self.globalProcessingDict = {}

        self.comboBoxAddVar.textActivated.connect(self.addNewGroupParameters)
        self.button_save.clicked.connect(self.oc_saveFilter)
        self.button_clear.clicked.connect(self.oc_clear)
        self.button_open.clicked.connect(self.oc_open)

    def addNewGroupParameters(self,groupName):
        """Add a New group of filters that will correspond to the processing of one variable"""
        if groupName not in list(self.globalProcessingDict.keys()):
            self.globalProcessingDict[groupName] = GroupParametersGlobalProcessing(groupName)
            self.globalProcessingTree.addParameters(self.globalProcessingDict[groupName].getParameters())
            self.globalProcessingDict[groupName].delete_trigger.connect(lambda name: self.oc_delete(name))
    
    def oc_delete(self,name):
        """ Delete the processing of a variable"""
        self.globalProcessingDict.pop(name)
        self.globalProcessingTree.clear()
        for group in list(self.globalProcessingDict.keys()):
            self.globalProcessingTree.addParameters(self.globalProcessingDict[group].getParameters())


    def updateComboBox(self,data):
        """Update the variable that should be accesssible for the creation of a processing pipeline"""
        self.comboBoxAddVar.clear()
        self.comboBoxAddVar.addItems(data)


    def setting_to_json(self):
        """Return a description in the form of a dicitonnary of the processing structure"""
        dictjson = {}
        for k,v in self.globalProcessingDict.items():
            dictjson[k]= v.setting_to_json()

        print(dictjson)
        return dictjson
    
    def oc_saveFilter(self):
        """ Save the global processing in a JSON file"""
        dictjson = self.setting_to_json()
        namepath = QFileDialog.getSaveFileName(self, 'Save File',
                                       #"/home/jana/untitled.png",
                                       "Json (*.json)")
        if os.path.exists(f'{namepath[0]}.json'):
            logger.info(f'Gloabl Processing - Save - File not saved. The file {namepath[0]}.json already exists')
        else:
            with open(f'{namepath[0]}.json', 'w') as f:
                json.dump(dictjson, f)
                logger.info(f'Gloabl Processing - Save - File saved. The file {namepath[0]}.json has been saved.')

            self.processingSaved.emit(namepath[0])

    def oc_clear(self):
        self.globalProcessingTree.clear()
        self.globalProcessingDict = {}


    def oc_open(self):
        # get path
        path = QFileDialog.getOpenFileName(self, 'Open File',)
                                       #"/home/jana/untitled.png",
                                    #    "Json (*.json)")
        #open filter
        self.loadJson(path[0])


    def loadJson(self,path):
        self.path = path
        f = open(self.path)
        data = json.load(f)

        for group,dictprocessing in data.items():
            self.addNewGroupParameters(group)
            self.globalProcessingDict[group].LoadJson(path=None,data=dictprocessing)





