from .setup import *




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
    def setData(self,group,var,channel,data):
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
        self.dict_group = {}
        self.path = path
        self.name = name
        self.attrs = {}
        self.openFile()


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
        self.loadGroup()

    def loadGroup(self)->dict:
        """Return a dictionnary with the groups, variables and channels names
        e.g. : {'group_name': {'var_name1':['channel1','channel2'],
                               'var_name2' : []}}
        The prupose of this dictionnary is to update the comboBoxes of the interface
        that are used to select the data

        """
        # Extract the variables
        self.dict_group = walkDatatree_getPathDataset(self.data,{})
        print('dict group after load',self.dict_group)

    def getGroup(self):
        return self.dict_group

    def getData(self,group,var,dim,channel):
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
        return self.data[group][var].loc[{dim:channel}] 
    
    def getDataVariable(self,group,var,dim):
        """Returns the selected data

        Args:
            group (str): _description_
            var (str): _description_
            channel (str): _description_

        Returns:
            np.array: 
        """
        return self.data[group][var] 
    
    def setData(self,group,var,channel,data):
        pass
        

    def saveData(self):
        pass

    # ATTRIBUTS
    def loadAttributs(self):
        self.attrs = walkDatatree_getAttrDataset(self.data)
        print('atrs load',self.attrs)
    
    def saveAttributs(self):
        pass
    

DATALOADER = {
    '.nc' : MyDataLoaderNC
}


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