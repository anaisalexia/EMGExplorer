
def Try_decorator(function):
    print('in deco')
    def wrapper(*arg):
        try:
            function(*arg)
        except Exception as e:
            print(function.__name__)
            print(e)

    return wrapper


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
                    
