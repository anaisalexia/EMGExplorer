from .setup import *
logger = logging.getLogger('main')



def Try_decorator(function):
    """Decorator that prints the function name and errors if any

    Args:
        function (function): _description_
    """

    def wrapper(*arg,**kwargs):
        try:
            function(*arg,**kwargs)
        except Exception as e:
            print(function.__name__)
            print(e)

    return wrapper


def LoggerError_decorator(function):
    """Decorator that write an error in the logger with the function name and the error if any

    Args:
        function (function): _description_
    """
    def wrapper(*arg,**kwargs):
        try:
            x = function(*arg,**kwargs)
            return x
        except Exception as e:
            logger.error(f" An error occured during the execution of {function.__name__} : {e}")

    return wrapper


def convertText(txt):
    """Convert text to digit if the text is a digit

    Args:
        txt (str): _description_

    Returns:
        str: _description_
    """
    try:
        if txt.isdigit():
            return int(txt)
    except:
        pass
    return txt


def deleteItemsOfLayout(layout):
    """Delete all the widgets of a layout.

    Args:
        layout (QLayout): _description_
    """
    if layout is not None:
         while layout.count():
             item = layout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                 widget.setParent(None)
             else:
                 deleteItemsOfLayout(item.layout())


def walkDatatree_setAttrDataset(info,node):
    """Set the Items of a TreeWidget from a dictionnary

    Args:
        info (dictionnary): _description_
        node (QTreeWidget): _description_

    Returns:
        QTreeWidget: _description_
    """
    # info is a dict/ a value that could be a dict, node is a treewidget
    for k,v in info.items():
        #if v is a dictionnary
        if type(v)==dict:
            child_node = QTreeWidgetItem(node)
            child_node.setText(0, str(k))
            walkDatatree_setAttrDataset(v,child_node)
    
        else:
            child_node = QTreeWidgetItem(node)            
            child_node.setText(0,str(k))
            child_node.setText(1,str(v))
            # return info
    
    return info
             
                    
def get_item_from_path(dict_dict,path):
    """Retrieve the item of embedded dictionnaries from a path made of a list of keys

    Args:
        dict_dict (_type_): _description_
        path (_type_): _description_
    """
    item = dict_dict[path[0]]
    for key in path[1:]:
        item = item[key]
        
    return item



def flatten(dictionary, parent_key=False, separator='.'):
    """Flatten embedded dictionnary to that each leaf is attributed to a key made from the path to the leaf.

    Args:
        dictionary (_type_): _description_
        parent_key (bool, optional): _description_. Defaults to False.
        separator (str, optional): _description_. Defaults to '.'.
    """
  
    def isLeaf(items):
        # is leaf if the value of the dictionnary is a simple dictionnary and has no embedded dicitonnary
        if isinstance(items,dict):
            for k,v in items.items():
                if isinstance(v,dict):
                    return False
            return True
        else:
            return False
    
    def hasLeaf(items):
        for k,v in items.items():
            if not isinstance(v,dict):
                return True
        return False
        

    list_group = []

    def recurse(attrs,key):
        print(key)

        if isLeaf(attrs):
            list_group.append({key:attrs})
        
        elif hasLeaf(attrs):
            new_attrs = {}
            for k,v in attrs.items():
                if not isinstance(v,dict):
                    new_attrs[k] = v
                else:
                    recurse(v,key + "." + k)
            list_group.append({key:new_attrs})
                    
        
        else:
            for k,v in attrs.items():
                if isinstance(v,dict):
                    recurse(v,str(key) + "." + str(k) if str(key) != "" else str(k))

    recurse(dictionary,"")  

    return list_group
        

