from papermill.iorw import load_notebook_node
from papermill.parameterize import parameterize_notebook

def execute_notebook(nb_path, params, overrides=None):
    """
    Converts a notebook (url or filepath) to a callback function.
    Params should be a dictionary, using papermill parameter insertion
    """
    nb = load_notebook_node(nb_path)
    parameterized = parameterize_notebook(nb, params) 
    ### ^^ injects new cells under cells which are tagged 'parameters'
    if overrides:
        ldict = overrides
    else:
        ldict = locals()
    
    for cell in parameterized.cells:
        if cell.cell_type == 'code':
            if overrides and 'override' in cell.metadata.tags:
                continue
            elif 'return' in cell.metadata.tags:
                return eval(cell.source, globals(), ldict)
            else:
                exec(cell.source, globals(), ldict)
    return {}