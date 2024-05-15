from .setup import *
from .custom_widget import comboBoxCheckable,ComboBoxExpandable
from .graph import create_menuJson

class SummaryElement(QWidget):

    position_changed = pyqtSignal(int,int)
    removed = pyqtSignal(int)
    # comboBox_changed = pyqtSignal(dict)

    def __init__(self,position):
        super().__init__()
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\layout_element_summary.ui', self)
        self.position = str(position)
        self.init_layout()

        self.information = {'Measure': '',
                            'Range': '',
                            'Display': ''}

    def init_layout(self):
        self.lineEdit_position.setText(self.position)

        self.menu = QtWidgets.QMenu(self)
        self.remove = self.menu.addAction('Remove')
        self.remove.triggered.connect(self.oc_remove)
        self.toolButton.setMenu(self.menu)
        self.toolButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.comboBox_measure = ComboBoxExpandable()
        self.comboBox_display = ComboBoxExpandable()

        self.comboBox_measure.setData(MEASUREMENT_NAME)
        self.comboBox_display.setData(DISPLAY_NAME)

        self.lcomboBox_measure.addWidget(self.comboBox_measure)
        self.lcomboBox_display.addWidget(self.comboBox_display)

        self.comboBox_range.addItems(['channel','variable','variable-general','group'])    
        self.comboBox_measure.pathChanged.connect(lambda x: self.oc_comboBoxChanged(x,'Measure'))
        self.comboBox_display.pathChanged.connect(lambda x: self.oc_comboBoxChanged(x,'Display'))
        self.comboBox_range.currentTextChanged.connect(lambda x: self.oc_comboBoxChanged(x,'Range'))

        self.lineEdit_position.textChanged.connect(self.oc_lineEdit_positionChanged)

    def oc_remove(self,action):
        print('EMIT REMOVE',self.position)
        self.removed.emit(self.position)

    def getInfo(self):
        return self.information

    def oc_comboBoxChanged(self,arg,box):
        self.information[box] = arg
        # print('EMIT COMBO CHANGED',self.information)
        # self.comboBox_changed.emit(self.information)

    def oc_lineEdit_positionChanged(self,text):
        if text.isnumeric():
            print('EMIT POSITION',self.position,'to',int(text))
            self.position_changed.emit(self.position,int(text))
            self.position = int(text)
        else:
            self.lineEdit_position.setText(self.position)


class SummaryWindow(QWidget):

    generateSummary = pyqtSignal(dict)

    def __init__(self,parent):
        super().__init__()
        # self.parent = parent
        loadUi('hdemg_viewer_exemple\Qt_creator\EMGExplorer_qt\AnalysisWin.ui', self)
        self.p = parent
        self.init_layout()
        self.init_interactivity()

        # SET UP
        self.processing = ''

        self.group_list = []
        self.var_list = []

        self.checkBox_current.setChecked(True)
        self.groupBox_load.setChecked(False)
        self.file_list = []
        try:
            self.file_list = [loader.getPath() for loader in list(self.p.dataLoader.values())]
        except:
            pass

        self.save_path = ''
        self.save_processing = False

        # ELEMENTS
        self.dict_summaryElementsLayout = {}
        self.dict_summaryElement = {}
        self.nb_element = 0

    
    
    def init_layout(self):

        self.label_savePath.setWordWrap(True)

        self.comboGr = comboBoxCheckable('Group')
        self.comboVar = comboBoxCheckable('Variable')
        try:
            loader = self.p.get_currentLoader()
            group_names = loader.getListGroup()
            var_names = loader.getListVariable()

            self.comboGr.setData(group_names)
            self.comboVar.setData(var_names)
        except:
            pass

        

        self.layout_GrVarCh.addWidget(self.comboGr)
        self.layout_GrVarCh.addWidget(self.comboVar)
        self.comboGr.currentTextChanged.connect(self.oc_comboBoxGr)
        self.comboVar.currentTextChanged.connect(self.oc_comboBoxVar)


        self.comboExpandable_processing = ComboBoxExpandable()
        self.comboExpandable_processing.setData(PROCESSING_NAME)
        self.layout_comboBoxExpandable_processing.addWidget(self.comboExpandable_processing)

        menuJson = create_menuJson(PATH_PIPELINE)
        self.comboExpandable_processing.append_element(['None'],self.comboExpandable_processing.menu())
        self.comboExpandable_processing.append_element(menuJson,self.comboExpandable_processing.menu())

        self.comboExpandable_processing.pathChanged.connect(self.oc_comboBoxExp)
    

    def init_interactivity(self):
        # SET UP
        self.checkBox_current.stateChanged.connect(self.oc_checkBoxCurrent)
        self.groupBox_load.clicked.connect(self.oc_groupBoxLoad)
        self.button_generate.clicked.connect(self.oc_buttonGenerate)
        self.button_select.clicked.connect(self.oc_buttonSelect)
        self.button_selectSavePath.clicked.connect(self.oc_buttonSelectSavePath)

        # ELEMENTS
        self.button_addElement.clicked.connect(self.oc_buttonAddElement)

    def oc_comboBoxExp(self,path):
        self.processing = path

    def oc_comboBoxGr(self,list_gr):
        self.group_list = list_gr

    def oc_comboBoxVar(self,list_var):
        self.var_list = list_var

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
        self.dict_summaryElement = {}
        for i,element in self.dict_summaryElementsLayout.items():
            self.dict_summaryElement[i] = element.getInfo()

        if (self.save_path == '') or (self.dict_summaryElement == {}):
            dlg = QtWidgets.QMessageBox.warning(self, '!','Missing Information')

        dict_generation = {
            'processing': self.processing,
            'group list': self.group_list,
            'variable list':self.var_list,
            'file list':self.file_list,
            'path save':self.save_path,
            'save processing':self.checkBox_saveProcessing.isChecked(),
            'summary elements':self.dict_summaryElement,
        }
        print('SUMMARY GENERATION', dict_generation)
        # SUMMARY GENERATION {'processing': '', 'group list': [], 'variable list': [], 'file list': [],
        #                      'path save': 'C:/Users/mtlsa/Documents/UTC/GB05/TX/Python_EMGExplorer/data', 'save processing': False, 
        #                     'summary elements': {0: {'Measure': ['time_domain', 'dfa'], 'Range': 'channel', 'Display': ['display1', 'boxplot']}, 1: {'Measure': ['time_domain', 'lyapunov_exp'], 'Range': 'variable', 'Display': ['display1', 'sys']}}} 

        input_template_path = r"EMG_Explorer_App/Template/template/templateSummary.html"
        output_html_path = r"EMG_Explorer_App/Template/template/templateSummary_filled.html"

        # plotly_jinja_data = fig.to_html(full_html=False)
        # #consider also defining the include_plotlyjs parameter to point to an external Plotly.js as described above

        info = "<p> Other paragraph.</p> "

        displays = []

        function_processing = get_item_from_path(PROCESSING,self.processing)
        # dict_getData = {"channel":self.p.}
        for filepath in self.file_list:
            displays += [f"<h4> {filepath}</h4> "]
            # retrieve loader
            name = os.path.split(filepath)[-1]
            type_format = name.split('.')[-1]
            loader = DATALOADER[f'.{type_format}'](filepath,name)

            for element in self.dict_summaryElement.values():
                displays += [f"<h4> {element}</h4> "]
                function_measure = get_item_from_path(MEASUREMENT,element['Measure'])
                function_display = get_item_from_path(DISPLAY,element['Display'])

                # Measurement
                df_element = pd.DataFrame(None,columns=['Group','Var','Dim','Value'])
                rows = []
                for gr in self.group_list if len(self.group_list) != 0 else loader.getListGroup():
                    print('group',gr)
                    for var in self.var_list if len(self.var_list) != 0 else loader.getListVariable():
                        print('var',var)
                        data_variable = loader.getDataVariable(gr,var)
                        dim = get_dim(list(data_variable.dims))
                        print('dims',dim)
                        if get_dim(list(data_variable.dims)) != None:
                            for ch in data_variable[get_dim(list(data_variable.dims))].values:
                                print(ch)
                                # np.array of the values
                                data_channel = function_processing(loader.getData(gr,var,dim,ch).values)
                                result_measure_ch = function_measure(data_channel)
                                row = dict(zip(['Group','Var','Dim','Value'],
                                    [gr,var,ch,result_measure_ch]))
                                print(row)
                                rows.append(row)

                df_element = pd.concat([df_element, pd.DataFrame(rows)])

                # Range
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

                if df_range != None: 
                    df_element = df_element.groupby(df_range, group_keys=True)[['Value']].apply(lambda x : np.nanmean(x)).reset_index()

                print('BEFORE DISPLAY', df_element)
                # Display
                
                if range_measure == 'channel':
                    print('channel range measure')
                    for gr in self.group_list if len(self.group_list) != 0 else loader.getListGroup():
                        print(gr)
                        df_group = df_element.loc[df_element['Group']==gr,:]
                        for var in self.var_list if len(self.var_list) != 0 else loader.getListVariable():
                            print(var)
                            df_var = df_group.loc[df_group['Var']==var,:]
                            # print('value for display',np.array(df_var['Value']))
                            if np.array(df_var['Value']).shape[0] != 0:
                                try:
                                    display = function_display(np.array(df_var['Value']))
                                    displays += [f'<p> {gr} {var} </p>',display]
                                except Exception as e:
                                    print(e)
                                    pass

                elif range_measure == 'variable':
                    print('variable range measure')

                    for gr in self.group_list if len(self.group_list) != 0 else loader.getListGroup():
                        print(gr)
                        df_group = df_element.loc[df_element['Group']==gr,:]
                        for var in self.var_list if len(self.var_list) != 0 else loader.getListVariable():
                            print(var)
                            df_var = df_group.loc[df_group['Var']==var,:]
                            # print('value for display',np.array(df_var['Value']))
                            if np.array(df_var['Value']).shape[0] != 0:
                                try:
                                    display = function_display(np.array(df_var['Value']))
                                    displays += [f'<p> {gr} {var} </p>',display]
                                except Exception as e:
                                    print(e)
                                    pass

                elif range_measure == 'variable_general':
                    pass
                elif range_measure == 'group':
                    pass
                

        data = {"data":dict_generation,"fig":' '.join(displays)}

        with open(output_html_path, "w", encoding="utf-8") as output_file:
            with open(input_template_path) as template_file:
                # print('Template rendered', data)
                j2_template = Template(template_file.read())
                output_file.write(j2_template.render(data ))

    
    def oc_buttonAddElement(self):
        element = SummaryElement(self.nb_element)
        self.dict_summaryElementsLayout[self.nb_element] = element
        self.layout_scrollArea.addWidget(element)
        self.nb_element += 1


