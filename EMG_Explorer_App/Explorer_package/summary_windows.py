from .setup import *
from .custom_widget import ComboBoxExpandable
from .graph import create_menuJson
from .mainwindow_utils import get_item_from_path,deleteItemsOfLayout,flatten
from .loading_function import DATALOADER
from . processing_function import dictOfFiles_from_EmbeddedFolders,ROOT_GLOBALPROCESSING,apply_jsonFilterGlobal
from . processing_function import *
logger = logging.getLogger('main')





class SummaryElement(QWidget):
    """Element of the Summary. Contains the parameters that enable the user to chose a metric and a display.

    Args:
        QWidget (_type_): _description_

    Returns:
        _type_: _description_
    """
    position_changed = pyqtSignal(int,int)
    removed = pyqtSignal(str)

    def __init__(self,position,variables,information = None):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\layout_element_summary.ui', self)
        self.position = str(position)
        self.variables = ['All'] + variables

        self.information = {'Measure': [''],
                            'Range': 'channel',
                            'Display':[ ''],
                            'Variables':'',
                            'RangeDisplay':['']}
        if information != None:
            self.information = information

        self.init_layout()

        

    def init_layout(self):
        """Initialisation of the layout of an element of the Summary"""
        self.lineEdit_position.setText(self.position)

        self.menu = QtWidgets.QMenu(self)
        self.remove = self.menu.addAction('Remove')
        self.remove.triggered.connect(self.oc_remove)
        self.toolButton.setMenu(self.menu)
        self.toolButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.comboBox_measure = ComboBoxExpandable()
        self.comboBox_display = ComboBoxExpandable()
        self.comboBox_rangedisplay = ComboBoxExpandable()

        self.comboBox_measure.setData(MEASUREMENT_NAME)
        self.comboBox_display.setData(DISPLAY_NAME)
        self.comboBox_rangedisplay.setData(RANGEDISPLAY_NAME)

        self.comboBox_variables.addItems(self.variables)

        self.lcomboBox_measure.addWidget(self.comboBox_measure)
        self.lcomboBox_display.addWidget(self.comboBox_display)
        self.lcomboBox_rangeDisplay.addWidget(self.comboBox_rangedisplay)

        self.init_information()

        self.comboBox_range.addItems(['channel','variable','variable-general','group'])    
        self.comboBox_measure.pathChanged.connect(lambda x: self.oc_comboBoxChanged(x,'Measure'))
        self.comboBox_display.pathChanged.connect(lambda x: self.oc_comboBoxChanged(x,'Display'))
        self.comboBox_rangedisplay.pathChanged.connect(lambda x: self.oc_comboBoxChanged(x,'RangeDisplay'))
        self.comboBox_range.currentTextChanged.connect(lambda x: self.oc_comboBoxChanged(x,'Range'))
        self.comboBox_variables.currentTextChanged.connect(lambda x: self.oc_comboBoxChanged(x,'Variables'))

        self.lineEdit_position.textChanged.connect(self.oc_lineEdit_positionChanged)


    def init_information(self):
        """If default values have been given at the initialization, selects the default values for each component
        """
        self.comboBox_measure.setText(self.information['Measure'][-1])
        self.comboBox_range.setCurrentText(self.information['Range'])
        self.comboBox_variables.setCurrentText(self.information['Variables'])
        self.comboBox_display.setText(self.information['Display'][-1])
        self.comboBox_rangedisplay.setText(self.information['RangeDisplay'][-1])


    def oc_remove(self,action):
        """ emit removed signal with the position of the element in the summary structure"""
        self.removed.emit(self.position)

    def getInfo(self):
        """ return the components information of the element"""
        return self.information

    def oc_comboBoxChanged(self,arg,box):
        self.information[box] = arg

    def oc_lineEdit_positionChanged(self,text):
        """emit position_changed signal with the text input"""
        if text.isnumeric():
            self.position_changed.emit(self.position,int(text))
            self.position = int(text)
        else:
            self.lineEdit_position.setText(self.position)




class SummaryWindow(QWidget):
    """Widget to create a Summary of metrics. Enables the user to save or open a structure of summary and creates its own.

    Args:
        QWidget (_type_): _description_

    Returns:
        _type_: _description_
    """

    generateSummary = pyqtSignal(dict)

    def __init__(self,parent):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\AnalysisWin.ui', self)
        self.p = parent
        self.path_globalProcessing = ['None']

        self.init_layout()
        self.init_interactivity()

        # SET UP
        self.list_variables = []

        self.checkBox_current.setChecked(True)
        self.groupBox_load.setChecked(False)
        self.file_list = []
        self.update_file_list()
        
        self.save_path = ''
        self.save_processing = False

        # ELEMENTS
        self.dict_summaryElementsLayout = {}
        self.dict_summaryElement = {}
        self.nb_element = 0

    
    
    def init_layout(self):
        """ intialization of the layout """
        self.label_savePath.setWordWrap(True)
        self.init_comboBox_globalProcessing()


    def init_interactivity(self):
        """ Set up of the interactivity of the Summary owns components and of the Summary's elements """
        # OWN SET UP
        self.checkBox_current.stateChanged.connect(self.oc_checkBoxCurrent)
        self.groupBox_load.clicked.connect(self.oc_groupBoxLoad)
        self.button_generate.clicked.connect(self.oc_buttonGenerate)
        self.button_select.clicked.connect(self.oc_buttonSelect)
        self.button_selectSavePath.clicked.connect(self.oc_buttonSelectSavePath)

        # ELEMENTS SET UP
        self.button_addElement.clicked.connect(self.oc_buttonAddElement)
        self.button_saveSummary.clicked.connect(self.oc_save)
        self.button_openSummary.clicked.connect(self.oc_open)
        self.button_clearSummary.clicked.connect(self.oc_clear)


    def init_comboBox_globalProcessing(self):
        
        self.comboBoxGlobalProcessing = ComboBoxExpandable()
        self.update_comboBoxGlobalProcessing()
        self.layout_comboBoxExpandable_processing.addWidget(self.comboBoxGlobalProcessing)
        self.comboBoxGlobalProcessing.pathChanged.connect(self.update_pathGlobalProcessing)
        
    
    def update_comboBoxGlobalProcessing(self):
        lastSelection = self.p.get_globalProcessing()
        self.path_globalProcessing = lastSelection
        menuJson = dictOfFiles_from_EmbeddedFolders(ROOT_GLOBALPROCESSING)
        self.comboBoxGlobalProcessing.setData(menuJson)
        self.comboBoxGlobalProcessing.append_element(['None'],self.comboBoxGlobalProcessing.menu())

        if lastSelection:
            self.comboBoxGlobalProcessing.setText(lastSelection[-1])

    def update_file_list(self):
        try:
            self.file_list = [loader.getPath() for loader in list(self.p.dataLoader.values())]
        except:
            pass

    def update_pathGlobalProcessing(self,listpath:list):
        self.path_globalProcessing = listpath

    def get_currentGlobalProcessingName(self):
        return self.path_globalProcessing[-1]
    
    def get_currentGlobalProcessingDict(self):
        if self.path_globalProcessing != ['None']:
            listpath = list(filter(lambda a: a != 'general', self.path_globalProcessing))
            f = open(f'{ROOT_GLOBALPROCESSING}/{"/".join(listpath)}')
            data = json.load(f)
            return data
        else:
            return {}


    def oc_checkBoxCurrent(self,state):
        if state :
            self.groupBox_load.setChecked(False)
            self.file_list = [loader.getPath() for loader in list(self.p.dataLoader.values())]
        else:
            self.file_list = []

    def oc_groupBoxLoad(self,state):
        if state:
            self.file_list = []
            self.checkBox_current.setChecked(False)

        else:
            self.listWidget_path.clear()
            self.file_list = []

    def oc_cuttonClear(self):
        self.listWidget_path.clear()

    def oc_buttonSelect(self):
        file_list = QFileDialog.getOpenFileNames(self, 'Open File',)[0]
                                       #"/home/jana/untitled.png",
                                    #    "Json (*.json)")
        for file in file_list:
            if file not in self.file_list:
                self.file_list.append(file)
                self.listWidget_path.addItem(file)
                                
        
    def oc_buttonSelectSavePath(self):
        self.save_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.label_savePath.setText(self.save_path)


    def oc_buttonGenerate(self):
        """Generate a Summary following to the chosen elements of its structure
        """

        # retrive the information of each element of the summary interface
        self.dict_summaryElement = {}
        for i,element in self.dict_summaryElementsLayout.items():
            self.dict_summaryElement[i] = element.getInfo()

        # check if a path to save the summary is selected
        if ((self.checkBox_saveProcessing.isChecked()) and (self.save_path == '')) :
            dlg = QtWidgets.QMessageBox.warning(self, '!','Missing Information')

        dict_generation = {
            'processing': self.get_currentGlobalProcessingDict(),
            'file list':self.file_list,
            'path save':self.save_path,
            'save processing':self.checkBox_saveProcessing.isChecked(),
            'summary elements':self.dict_summaryElement,
        }
        # SUMMARY GENERATION {'processing': '', 'group list': [], 'variable list': [], 'file list': [],
        #                      'path save': 'C:/Users/mtlsa/Documents/UTC/GB05/TX/Python_EMGExplorer/data', 'save processing': False, 
        #                     'summary elements': {0: {'Measure': ['time_domain', 'dfa'], 'Range': 'channel', 'Display': ['display1', 'boxplot']}, 1: {'Measure': ['time_domain', 'lyapunov_exp'], 'Range': 'variable', 'Display': ['display1', 'sys']}}} 

        input_template_path = ROOT_TEMPLATE
        output_html_path = lambda file,suffix,x : f"{self.save_path}\\Summary_{file}_{suffix}_{x}.html"

        # initialization of the variable that will hold the string that describ each Display
        displays = []

        # global processing dictionnary
        function_processing_dict = dict_generation['processing']


        ## For each file: generate a summary and/or save the filtered signals into new files
        for filepath in self.file_list:
            try:
                displays = []

                # retrieve loader
                name = os.path.split(filepath)[-1]
                type_format = name.split('.')[-1]
                name_woFormat = name.split('.')[-2]
                displays += [f"<h4> {name_woFormat}</h4> "]
                displays += [f"<p> {filepath}</p> "]

                # Apply the global processing
                loader = DATALOADER[f'.{type_format}'](filepath,name)
                try:
                    apply_jsonFilterGlobal(loader,pathData=loader.getGroup(), pathFile=None,dictFile=function_processing_dict)
                except Exception as e:
                    logger.error(f'Summary - Filters could not be applied to file {filepath}: {e}')


                ## SAVING ##
                # for each var that is modified
                # loader.save(path,variable,process)
                try:
                    if dict_generation['save processing']:
                        
                        # retrieve the suffix of the furtur saved file
                        saving_name_suffix = self.lineEdit_suffixFile.text()
                        if saving_name_suffix == '':
                            saving_name_suffix = 'filtered'

                        # For each variable  and proccesing of the global processing dictionnary
                        for variable,process in function_processing_dict.items():
                            # the proccessing of a variable is applied to all group
                            for group in loader.getListGroup():
                                variable_newName_fc = lambda x : f"{variable}_{self.get_currentGlobalProcessingName()[:-5]}_{x}"
                                variable_newName = variable_newName_fc(0)
                                variable_newName_nb = 0

                                # create a name for the new filtered variable that does not already exists in the present data : Variable_NameProcessing_Nb
                                while variable_newName in loader.getListVariable():
                                    variable_newName_nb +=1
                                    variable_newName = variable_newName_fc(variable_newName_nb)

                                # copy the (processed) data into a new variable in the original data
                                loader.setToDataOriginal(group, variable_newName,variable)
                                # // data_original[group][variable_newName] = loader.data[group][variable]

                                # add attributs to the new data variable
                                loader.setAttrs(group,variable_newName,'Processing',process)
                                # // data_original[group][variable_newName].assign_attrs({'Processing':str(process)})
                        
                        # create a new file name so that the data are not overwritten
                        saving_name_nb = 0
                        saving_path_fc = lambda x : f'{self.save_path}\\{loader.getName().split('.')[0]}_{saving_name_suffix}_{x}.nc'
                        saving_path = saving_path_fc(saving_name_nb)

                        while(os.path.exists(saving_path)):
                            saving_name_nb += 1
                            saving_path = saving_path_fc(saving_name_nb)
                        
                        #save the data
                        try:
                            loader.saveData(saving_path)
                            # // ex: loader.data_original.to_netcdf(saving_path, mode = 'w')
                            logger.info(f'File Saved : {saving_path}')

                        except Exception as e:
                            logger.warning(f'Summary - File Saving Failed: {saving_path} {e}')
                
                except Exception as e:
                    logger.warning(f'An error occured during saving file {saving_path} : {e}')



                ## SUMMARY ##
                # retrieve the suffix to name the summary
                suffixSummary = self.lineEdit_suffix.text()

                # Create the html code for each element of the summary
                for element in self.dict_summaryElement.values():
                    displays += [f"<h4> {element}</h4> "]

                    # retrieve the components of the elements (eg functions and range) for computing the metric and the display
                    function_measure = get_item_from_path(MEASUREMENT,element['Measure'])
                    function_display = get_item_from_path(DISPLAY,element['Display'])
                    function_rangeDisplay = get_item_from_path(RANGEDISPLAY, element['RangeDisplay'])
                    list_var = element['Variables']

                    # Measurement
                    df_element = pd.DataFrame(None,columns=['Group','Var','Dim','Value'])
                    rows = []

                    #Computes the metric for each group; vairable and channel to create a DataFrame such as 
                    # EXEMPLE Channel
                    #         Group      Var      Dim   Value
                    #     0     /  Accelerations   X  3.897428
                    #     1     /  Accelerations   Y  3.544009

                    for gr in loader.getListGroup():
                        for var in [list_var] if list_var != 'All' else loader.getListVariable():
                            for dim in loader.getListDimension(group=gr,var=var):
                                for ch in loader.getListChannel(group=gr,var=var):

                                    try:
                                        data_channel = np.array(loader.getData(gr,var,dim,ch))
                                        result_measure_ch = function_measure(data_channel)
                                        row = dict(zip(['Group','Var','Dim','Value'],
                                            [gr,var,ch,result_measure_ch]))

                                        rows.append(row)

                                    except Exception as e:
                                        logger.error(f"Summary - Measurement {function_measure.__name__} could no be computed for {gr} {var} {dim} {ch}: {e}")
                                        row = dict(zip(['Group','Var','Dim','Value'], [gr,var,ch,np.NAN]))
                                        rows.append(row)


                    df_element = pd.concat([df_element, pd.DataFrame(rows)])

                    # Range : Computes the mean of the computed metrics over the variables or groups as indicated in the element's range
                    all_range = ['Group','Var','Dim']
                    range_measure = element['Range']
                    df_range = None
                    if range_measure == 'channel':
                        pass
                    elif range_measure == 'variable':
                        df_range = ['Group','Var']
                    elif range_measure == 'variable_general':
                        df_range = ['Var']
                    elif range_measure == 'group':
                        df_range = ['Group']

                    try:
                        # if the metric need to be averaged
                        if df_range != None: 
                            df_element = df_element.groupby(df_range, group_keys=True)[['Value']].apply(lambda x : np.nanmean(x)).reset_index()
                            df_element = df_element.rename(columns={0:"Value"})
                            # add back the column
                            if df_range != None:
                                for column_removed in all_range:
                                    if column_removed not in df_range:
                                        df_element[column_removed] = np.zeros((1,df_element.shape[0]))
                    except Exception as e:
                        logger.error(f"Summary - Range {df_range} could no be computed : {e}")
                        displays += ["Error while averaging tge metrics"]
                        continue

                    # EXEMPLE no averaging Channel
                    #         Group      Var      Dim   Value
                    #     0     /  Accelerations   X  3.897428
                    #     1     /  Accelerations   Y  3.544009
                    #     2     /  Accelerations   Z  4.241707

                    # EXEMPLE averaging over variable
                    #           Group    Var     Dim     Value
                    #     0     /  Accelerations  0    3.894381
                    

                    try:
                        # creation of the html code corresponding to the display of the element
                        display = function_rangeDisplay(function_display,df_element)
                        # display = function_display(np.array(row['Value']))
                        displays += [f'<p> {gr} {var} </p>']
                        displays += display
                    except Exception as e:
                        logger.error(f"Summary - Display {function_display.__name__} could no be computed : {e}")
                        displays += ["Error while rendering the display"]
                        continue


                # If a summary has been created: finalize the summary and save
                if self.dict_summaryElement != {}:
                    dict_file = dict_generation.copy()
                    dict_file.pop('file list')
                    # retrieve the attributs of a file
                    loader.loadAttributs()
                    param = flatten(loader.getAttrs())
                    logger.debug(param)

                    # dictionnary for jinja rendering
                    data = {"data":dict_file,"fig":' '.join(displays),"params":param}

                    # create a unique name for saving the summary and avoiding overwriting data
                    path_summarySave = output_html_path(name_woFormat,suffixSummary,0)
                    i = 0
                    while os.path.exists(path_summarySave) :
                        path_summarySave = output_html_path(name_woFormat,suffixSummary,i)
                        i += 1

                    # SAve the summary
                    with open(path_summarySave, "w", encoding="utf-8") as output_file:
                        with open(input_template_path) as template_file:
                            j2_template = Template(template_file.read())
                            output_file.write(j2_template.render(data ))
                            logger.info(f"Summary - Summary saved. Dile {path_summarySave}")

            
            except Exception as e:
                logger.warning(f"Summary - An error occured during Summary generation of {filepath} : {e}")
    


    def update_variables(self):
        filepath = self.file_list[0]
        name = os.path.split(filepath)[-1]
        type_format = name.split('.')[-1]
        loader = DATALOADER[f'.{type_format}'](filepath,name)
        self.list_variables = loader.getListVariable()


    def oc_buttonAddElement(self):
        self.update_variables()
        self.addElement()

    def addElement(self,info=None):
        element = SummaryElement(self.nb_element,self.list_variables,info)
        element.removed.connect(self.oc_removeElement)
        self.dict_summaryElementsLayout[self.nb_element] = element
        self.layout_scrollArea.addWidget(element)
        self.nb_element += 1

    def oc_removeElement(self,id_element):
        id_element = int(id_element)
        self.nb_element -= 1
        self.dict_summaryElementsLayout.pop(id_element)
        for i in range(id_element+1,self.nb_element):
            self.dict_summaryElementsLayout[i-1] = self.dict_summaryElementsLayout[i]
        deleteItemsOfLayout(self.layout_scrollArea)
        self.rebuild_layoutScrollArea()

        logger.info(f'Summary : new dict element after removal of {id_element} : {self.dict_summaryElementsLayout}')

    def oc_save(self):
        dict_save = {}
        for nb,element in self.dict_summaryElementsLayout.items():
            dict_save[nb] = element.getInfo()

        namepath = QFileDialog.getSaveFileName(self, 'Save File',
                                       #"/home/jana/untitled.png",
                                       "Json (*.json)")
        if os.path.exists(f'{namepath[0]}.json'):
            print('the file exist already')
        else:
            with open(f'{namepath[0]}.json', 'w') as f:
                json.dump(dict_save, f)
    
    def oc_open(self):
        path = QFileDialog.getOpenFileName(self, 'Open File',)
                                       #"/home/jana/untitled.png",
                                    #    "Json (*.json)")
        #open filter
        print('path open is', path)
        self.loadJson(path[0])

    def oc_clear(self):
        self.dict_summaryElementsLayout = {}
        self.nb_element = 0
        deleteItemsOfLayout(self.layout_scrollArea)

    
    def rebuild_layoutScrollArea(self):
        for index,element in self.dict_summaryElementsLayout.items():
            self.layout_scrollArea.addWidget(element)

    def loadJson(self,path):
        f = open(path)
        data = json.load(f)

        self.update_variables()
        for nb,element_info in data.items():
            self.addElement(element_info)




