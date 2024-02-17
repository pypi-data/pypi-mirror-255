import tempfile
from importlib.util import module_from_spec, spec_from_loader


#import databricks_connector
from . import databricks_connector


#variables
export_error="Notebook empty"

patch_func = ('patch_globals = lambda x: globals().update'
              '({k: v for k, v in x.items() if k not in globals()})')



#global vars give access to notebook content and notebook name
def persist_notebook(base_url, access_token, scope_name, global_vars):
    
    #assert notebook length
    assert len(global_vars.get('In', [])) > 1, export_error
    
    #extract notebook contents
    notebook_contents= '\n\n'.join(global_vars['In'][:-1])
    
    #write notebook contents to temporary file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(bytes(notebook_contents, 'utf-8'))

    #get notebook name
    notebook_name = global_vars['dbutils'].notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get().split('/')[-1]
        
    #persist temp file name (so that it can be accessed)
    if assert_scope_existence(base_url, access_token, scope_name):
    
        add_secret(base_url, access_token, scope_name, notebook_name, f.name)   
    
    return True

#global vars allows to extract secret value
def import_notebook(base_url, access_token, scope_name, global_vars, notebook_name):
    
    #extract filename using databricks secrets
    filename_holding_secret = global_vars['dbutils'].secrets.get(scope=scope_name, key=notebook_name)
    
    #extract contents
    with open(filename_holding_secret, 'rb') as f:
        contents = f.read().decode('utf-8')

    print(contents)
        
    #create module
    module = module_from_spec(spec_from_loader("doesn't matter", loader=None))
    
    #don't know what this does
    exec(patch_func, module.__dict__)
    module.patch_globals(global_vars)
    
    #add notebook code
    exec(contents, module.__dict__)
    
    return module