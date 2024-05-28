from .setup import *
import logging

logger = logging.getLogger(f'main.{__name__}')


def merge2datatree(datatree1:DataTree,datatree2:DataTree):
    dict1 = datatree1.to_dict()
    dict2 = datatree2.to_dict()
    dict1group = list(dict1.keys())
    for k,xar in dict2.items():
        dict1[k] = xar
    return DataTree.from_dict(dict1)


### BASE CLASS ###

class MyDataLoader(ABC):

    def __init__(self,path,name) -> None:
        self.data
        self.dict_group
        self.path = path
        self.name = name
        self.openFile()

    # DATA
    @staticmethod
    @abstractmethod
    def format():
        return ''

    @abstractmethod
    def openFile(self):
        """Update data

        Returns:
            update self.data
        """
        self.data = []

    @abstractmethod
    def loadGroup(self)->dict:
        """Return a dictionnary with the groups, variables and channels names
        e.g. : {'group_name': {'var_name1':['channel1','channel2'],
                               'var_name2' : []}}
        The prupose of this dictionnary is to update the comboBoxes of the interface
        that are used to select the data

        """
        self.dict_group = {'':{'':[]}}

    @abstractmethod
    def getData(self,group,var,channel):
        """Returns the selected data

        Args:
            group (str): _description_
            var (str): _description_
            channel (str): _description_

        Returns:
            np.array: 
        """
        return np.array([])
    
    @abstractmethod
    def setData(self,group,var,dim,channel,data):
        pass
    
    @abstractmethod
    def saveData(self):
        pass

    # ATTRIBUTS
    @abstractmethod
    def loadAttributs(self):
        return {}
    
    @abstractmethod
    def saveAttributs(self):
        pass
    
    

    





### DATALOADER .NC ###
def walkDatatree_getPathDataset(node,path):

    if node.is_leaf:
        if node.has_data:
            dict_node = { }
            for var in list(node.data_vars):

                data = node[var]
                dims = list(data.dims)
                print('diiiiims',dims)
                for t in ['Time','time']:
                    try:
                        dims.remove(t)
                    except:
                        pass

                if len(dims) != 0:
                    dim_name = dims[0] # could be replace by a list of the dims if more than 2        
                    dict_node[var] = {str(dim_name): list(node[var][dim_name].values)}
                
                else:
                    dict_node[var] = {}

            path[node.path] = dict_node
            return path
        return path
                
    else: # node has children
        for child in node.children:
            walkDatatree_getPathDataset(node[child],path)
    
    return path


def walkDatatree_getAttrDataset(node):
    info = {}
    if node.is_leaf:
        if node.has_attrs:
            dict_node = node.attrs
            
            info[node.name] = dict_node
            return info
        return info
                
    else: 
        for child in node.children:
            folder = node.name
            info[ folder if folder != None else 'Root'] = walkDatatree_getAttrDataset(node[child])
    
    return info






class MyDataLoaderNC(MyDataLoader):

    def __init__(self,path,name) -> None:
        self.data = {}
        self.data_original = {}
        self.dict_group = {}
        self.path = path
        self.name = name
        self.attrs = {}
        self.openFile()
        logger.info(f'File open {name}')


    # DATA
    @staticmethod
    def format():
        return '.nc'

    def openFile(self):
        """Load .nc file and extract the path of the groups that have data variables

        Returns:
            update self.data
        """
        self.data =  datatree.open_datatree(self.path)
        self.data_original = datatree.open_datatree(self.path)
        self.loadGroup()

    def loadGroup(self)->dict:
        """Return a dictionnary with the groups, variables and channels names
        e.g. : {'group_name': {'var_name1':['channel1','channel2'],
                               'var_name2' : []}}
        The prupose of this dictionnary is to update the comboBoxes of the interface
        that are used to select the data
        ex: dict group after load {'/': {'Trigger': {}, 'Accelerations': {'axes': ['X', 'Y', 'Z']}, 'HDsEMG': {'Channel': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]}}}
        """
        # Extract the variables
        self.dict_group = walkDatatree_getPathDataset(self.data,{})
        print('dict group after load',self.dict_group)

    # ATTRIBUTS
    def loadAttributs(self):
        self.attrs = walkDatatree_getAttrDataset(self.data)
    
    def saveAttributs(self,attrs):
        """_summary_

        Args:
            attrs (dict): _description_
        """
        pass

    def init_dataLoader(self,path):
        for gr in path.keys():
            for var in path[gr].keys():
                for dim in path[gr][f'{var}'].keys():
                    for ch in path[gr][f'{var}'][dim]:
                        x = np.array(self.getDataOriginal(gr,var,dim,ch)   )             
                        self.setData(gr,f'{var}',dim,ch,x)

    def getPath(self):
        return self.path
        
    def getGroup(self):
        return self.dict_group
    
    def getName(self):
        return self.name

    
    def getListGroup(self):
        return list(self.dict_group.keys())

    def getListVariable(self,group=None):
        if group != None:
            group_dict = self.dict_group[group]
            return list(group_dict.keys())
        else:
            list_var = []
            for gr in self.getListGroup():
                list_var += list(self.dict_group[gr].keys())
            return list_var
        
    def getListDimension(self,group=None,var=None):
        if group != None:
            if var != None:
                return list(self.dict_group[group][var].keys())
            else:
                list_dim = []
                for var in self.dict_group[group]:
                    list_dim += list(self.dict_group[group][var].keys())
                return list_dim
            
        else:
            list_dim = []
            for group in list(self.dict_group.keys()):
                for var in self.dict_group[group]:
                    list_dim += list(self.dict_group[group][var].keys())
                return list_dim 
            

    def getListChannel(self,group=None,var=None,dim=None):
        if group != None:
            group_dict = self.dict_group[group]
            if var != None:
                group_var = group_dict[var]
                if dim==None : return group_var[list(group_var.keys())[0]]
                else: return group_var[dim]
            else:
                list_ch = []
                for var in self.getListVariable(group):
                    for dim in self.getListDimension(group,var) if dim == None else [dim]:
                        group_var = group_dict[var]
                        list_ch += group_var[dim].values()
                return list_ch
            
        else:
            list_ch = []
            for gr in self.getListGroup():
                for var in self.getListVariable(gr):
                    for dim in self.getListDimension(gr,var) if dim == None else [dim]:
                        group_var = group_dict[var]
                        list_ch += group_var[dim].values()
            return list_ch



    def getDataOriginal(self,group,var,dim,channel):
        """Returns the selected data

        Args:
            group (str): _description_
            var (str): _description_
            channel (str): _description_

        Returns:
            xarray: 
        """
        try:
            if channel.isdigit():
                channel = int(channel) #could be fix with item instead of text ?
        except:
            pass
        return self.data_original[group][var].loc[{dim:channel}] 
    

    def getData(self,group,var,dim,channel):
        """Returns the selected data

        Args:
            group (str): _description_
            var (str): _description_
            channel (str): _description_

        Returns:
            xarray: 
        """
        try:
            if channel.isdigit():
                channel = int(channel) #could be fix with item instead of text ?
        except:
            pass

        return self.data[group][var].loc[{dim:channel}] 
    
    
    def setData(self,group,var,dim,channel,data):
        try:
            if channel.isdigit():
                channel = int(channel) #could be fix with item instead of text ?
        except:
            pass

        self.data[group][var].loc[{dim:channel}] = data

    

    def getDataVariable(self,group,var,dim=None):
        """Returns the selected data

        Args:
            group (str): _description_
            var (str): _description_
            channel (str): _description_

        Returns:
            np.array: 
        """
        if dim != None:
            return self.data[group][var][dim]
        return self.data[group][var] 
    
    def get_DataFromDict(self,dictData):
        # ex from {'/': {'Trigger': [], 'Accelerations': ['Y'], 'HDsEMG': ['8', '9']}}
        """return a list of xarray per variable

        Args:
            dictData (_type_): _description_
        """
        data_list = []
        def recursedata(dict_data,data):
            for k,v in dict_data.items():
                print('k',k)
                if isinstance(v,list):
                    for ch in v:
                        if ch.isnumeric(): ch = int(ch)
                        data_list.append(data[list(data[k]).index(ch),:])

                else:
                    recursedata(v,data[k])

        recursedata(dictData,self.data)    

        return data_list


    def setMultipleData(self,data,pathDict):
        """

        Args:
            data (_type_): xarray Dataset
            pathDict (_type_): _description_

        Returns:
            _type_: _description_
        """
        if pathDict in list(self.data.to_dict().keys()):
            print('Path already in file')

        datatreeToAdd = DataTree.from_dict({pathDict:data})
        self.data = merge2datatree(self.data,datatreeToAdd)

        

        # fooData = DataTree.from_dict({'/add':foo})
                

    def saveData(self):
        pass

    
    

def getDataDatatree(data,group,var,dim,channel):
    """Returns the selected data

    Args:
        group (str): _description_
        var (str): _description_
        channel (str): _description_

    Returns:
        np.array: 
    """
    
    try : channel = int(channel) #could be fix with item instead of text ?
    except: pass
    return data[group][var].loc[{dim:channel}] 

def get_dim(list_dim:list):
    """return the first dimention that is not time 

    Args:
        list_dim (list): _description_

    Returns:
        _type_: _description_
    """
    for t in ['Time','time']:
        if t in list_dim:
            list_dim.remove(t)
    if len(list_dim) != 0:
        return list_dim[0]
    else:
        return None
    
def xarray_to_dataframe(xarray):
    df = pd.DataFrame(None,columns=['Group','Var','Dim','Value'])
    rows = []

    for gr in xarray.groups:
        d = xarray[gr]
        if d.is_leaf:
            for var in list(d.data_vars):
                dim = get_dim(list(d[var].dims))
                if dim != None:
                    for ch in d[var][dim].values:
                        value = getDataDatatree(xarray,gr,var,dim,ch).values
                        row = dict(zip(['Group','Var','Dim','Value'],
                                    [gr,var,ch,value]))
                        rows.append(row)


        # Concatenate the list of rows into the DataFrame
    df = pd.concat([df, pd.DataFrame(rows)])
    return df

DATALOADER = {
    '.nc' : MyDataLoaderNC
}


def init_dataLoader(loader,path):
        for gr in path.keys():
            for var in path[gr].keys():
                for dim in path[gr][f'{var}'].keys():
                    for ch in path[gr][f'{var}'][dim]:
                        x = loader.getDataOriginal(gr,var,dim,ch).values()                
                        loader.setData(gr,f'{var}',dim,ch,x)

def load_multiple_files(paths): # load _ multiple files
    """_summary_

    Args:
        paths (list): _description_
    """
    data = {}
    for path in paths:
        name = os.path.split(path)[-1]
        type_format = name.split('.')[-1]
        loader = DATALOADER[f'.{type_format}'](path,name)        
        data[name] = loader
        
    return data