from .setup import *
logger = logging.getLogger('main')



def Try_decorator(function):
    print('in deco')
    def wrapper(*arg,**kwargs):
        try:
            function(*arg,**kwargs)
        except Exception as e:
            print(function.__name__)
            print(e)

    return wrapper


def LoggerError_decorator(function):
    def wrapper(*arg,**kwargs):
        try:
            x = function(*arg,**kwargs)
            return x
        except Exception as e:
            logger.error(f" An error occured during the execution of {function.__name__} : {e}")

    return wrapper


def convertText(txt):
    try:
        if txt.isdigit():
            return int(txt)
    except:
        pass
    return txt


def deleteItemsOfLayout(layout):
     if layout is not None:
         while layout.count():
             item = layout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                 widget.setParent(None)
             else:
                 deleteItemsOfLayout(item.layout())


def walkDatatree_setAttrDataset(info,node):
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


    # if type(list(info.values())[0]) == dict:
    #     for name,child_dict in info.items():
    #         child_node = QTreeWidgetItem(node)
    #         child_node.setText(0, str(name))
    #         walkDatatree_setAttrDataset(child_dict,child_node)
                
    # else: 
    #     for k,v in info.items():
    #         child_node = QTreeWidgetItem(node)            
    #         child_node.setText(0,str(k))
    #         child_node.setText(1,str(v))
    #     return info
        
    
    return info
             
                    
def get_item_from_path(dict_dict,path):
    """get the item of embedded dictionnaries from a path made of keys

    Args:
        dict_dict (_type_): _description_
        path (_type_): _description_
    """
    item = dict_dict[path[0]]
    for key in path[1:]:
        item = item[key]
        
    return item