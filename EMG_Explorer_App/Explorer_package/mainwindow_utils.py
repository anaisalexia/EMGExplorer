from .setup import *



def Try_decorator(function):
    print('in deco')
    def wrapper(*arg,**kwargs):
        try:
            function(*arg,**kwargs)
        except Exception as e:
            print(function.__name__)
            print(e)

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

    if type(list(info.values())[0]) == dict:
        for name,child_dict in info.items():
            child_node = QTreeWidgetItem(node)
            child_node.setText(0, str(name))
            walkDatatree_setAttrDataset(child_dict,child_node)
                
    else: 
        for k,v in info.items():
            child_node = QTreeWidgetItem(node)            
            child_node.setText(0,str(k))
            child_node.setText(1,str(v))
        return info
        
    
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