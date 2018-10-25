import pandas as pd
from kbucket import client as kb
from IPython.display import Image
from IPython.display import HTML
import json

def displayResult(result,summary=True,comparison=False,summary_plots=False):
    if summary:
        rows=[]
        rows.append(result['dataset_name'])
        rows.append(result['dataset_dir'])
        rows.append(result['sorting_processor_name'])
        rows.append(result['sorting_processor_version'])
        rows.append(result['sorting_params'])
        df=pd.DataFrame(rows,index=['Dataset','Directory','Sorting processor','Sorting version','Sorting parameters'],columns=[''])
        def stylefunc(val):
            return 'text-align: left'
        s=df.style.applymap(stylefunc)
        display(s)
    
    if comparison:
        table=_read_json_file(kb.realizeFile(result['comparison_with_truth']['json']))
        df=pd.DataFrame(table).transpose()
        display(df)

    if summary_plots:
        obj=result['summary']['plots']
        for key in obj:
            display(HTML('<h3>{}</h3>'.format(key)))
            path=obj[key]
            path=kb.realizeFile(path)
            display(Image(path,format='jpeg'))
        
def _read_text_file(fname):
    with open(fname,'r') as f:
        return f.read()
    
def _read_json_file(fname):
    with open(fname,'r') as f:
        return json.load(f)