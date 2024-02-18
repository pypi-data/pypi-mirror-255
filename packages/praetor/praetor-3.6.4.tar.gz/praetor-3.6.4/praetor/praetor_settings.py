import os

memory = False  # record allocated RAM per code segment - True/False
wrap_open = False  # record provenance for pythons open function - True/False
build_prov = False  # merge all recorded provenance files - True/False
flatten_prov = False  # requires provtoolbox installation, removes duplicates and shrinks
global_tracking = False # option to record global variables throughout the code

provenance_directory = './' # location for generated provenance storage
modules = []  # list of python modules/functions to record provenance for - use the name assigned to it in python
blacklist = []  # list of function to not include provenance for
staticmethods = [] # leave blank unless there are complaints about static methods
json_file = 'full_json.json' # name of json file. No need to change, it's defined here as many files need access to it
run_dir = os.path.dirname(os.path.realpath(__file__)) # os.getcwd()
unique_string = '!!!!!!!!!' # identifies func start/end in logs, must not be present in the logs otherwise
max_value_length = 128 # maximum no og chars for a value before it is stored separately from the provenance

if provenance_directory[-1] != '/':
    provenance_directory += '/'


