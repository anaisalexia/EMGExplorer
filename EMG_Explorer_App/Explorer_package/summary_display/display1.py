import sys
sys.path.append('EMG_Explorer_App/Explorer_package/summary_display')

from requirement_display1 import *


# DISPLAYS RETURN TEXT OR PATH TO AN IMAGE

# EXEMPLE Channel
#         Group      Var      Dim   Value
#     0     /  Accelerations   X  3.897428
#     1     /  Accelerations   Y  3.544009
#     2     /  Accelerations   Z  4.241707


def displaySig(row):
    fig = px.line(x=np.arange(row['Value'].shape[0]),y=row['Value'],title = f"{row['Group']} {row['Var']} {row['Dim']}")
    return fig.to_html(full_html=False)

# def displayAllMultipleSignal(array):


def heatmap4(array):
    array = np.reshape(array,(4,-1))    
    fig = px.imshow(array,text_auto=True)
    return fig.to_html(full_html=False)

def annotatedHeatmap8(df:pd.DataFrame):
    array = np.array(df['Value'])
    dim =  np.array(df['Dim'])
    array = np.reshape(array,(8,-1))    
    dim = np.reshape(dim,(8,-1))    
    print(df,dim,array)
    fig = px.imshow(array)
    fig.update_traces(text=dim, texttemplate="%{text}")
    # fig = ff.create_annotated_heatmap(array ,annotation_text=dim)
    return fig.to_html(full_html=False)


def heatmap8(array):
    array = np.reshape(array,(8,-1))    
    fig = px.imshow(array)
    return fig.to_html(full_html=False)

def text(value, metric = '',*args):
    text_metric = '' if metric == '' else f'{metric}: '
    if len(args) != 0:
        for i in range(len(args)):
            text_metric += f'{args[i]} '
    text_metric += str(value) 

    return text_metric


def boxplot(array):
    if isinstance(array,pd.DataFrame):
        fig = px.box(array.values)
    else: fig = px.box(array)
    return fig.to_html(full_html=False)



