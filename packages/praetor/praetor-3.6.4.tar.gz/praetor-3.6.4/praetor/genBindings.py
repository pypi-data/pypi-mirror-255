#!/usr/bin/env python
# coding: utf-8

from collections import Counter
import datetime
import functools
import hashlib
import importlib
import inspect
import json
import os
import subprocess
import sys
import textwrap
import time
import types
import uuid

try:
    from _thread import get_ident
except ImportError:
    from _dummy_thread import get_ident

try:
    prtr_path = os.environ['PRAETOR']
    sys.path.append(prtr_path)
    import praetor_settings_user as praetor_settings
except:
    from praetor import praetor_settings

sys.path.append(praetor_settings.provenance_directory+'{}/'.format(os.environ['PRAETOR_pipeline_id']))

from praetor import praetorTemplates

import templateDictionary


if praetor_settings.memory:
    from memory_profiler import memory_usage

ts = time.time()

bindings = {
    "context": {"xsd": "http://www.w3.org/2001/XMLSchema#", "lsim": "http://example.org/", "urn_uuid": "urn:uuid:",
                "run": "http://example.org/"}}

session_id = 'praetor'
prov_id_counter = Counter()
prov_id_cache = dict()
prov_id_activity_cache = []
call_func_list = []
glob_vars = [{}]
praetor_rec = 0

dtypes = {'int': 'int', 'unsignedInt': 'unsignedInt', 'hexBinary': 'hexBinary', 'NOTATION': 'NOTATION',
          'nonPositiveInteger': 'nonPositiveInteger', 'float': 'float', 'ENTITY': 'ENTITY', 'bool': 'boolean',
          'positiveInteger': 'positiveInteger', 'duration': 'duration', 'IDREFS': 'IDREFS',
          'unsignedLong': 'unsignedLong', 'normalizedString': 'normalizedString', 'dateTimeStamp': 'dateTimeStamp',
          'NMTOKEN': 'NMTOKEN', 'negativeInteger': 'negativeInteger', 'base64Binary': 'base64Binary',
          'long': 'long', 'unsignedShort': 'unsignedShort', 'ENTITIES': 'ENTITIES', 'anyURI': 'anyURI',
          'NMTOKENS': 'NMTOKENS', 'IDREF': 'IDREF', 'unsignedByte': 'unsignedByte', 'Name': 'Name',
          'dayTimeDuration': 'dayTimeDuration', 'date': 'date', 'integer': 'integer', 'byte': 'byte', 'ID': 'ID',
          'gMonth': 'gMonth', 'short': 'short', 'language': 'language', 'gMonthDay': 'gMonthDay',
          'double': 'double', 'Decimal': 'decimal', 'gDay': 'gDay', 'gYearMonth': 'gYearMonth',
          'QName': 'QName', 'datetime': 'dateTime', 'nonNegativeInteger': 'nonNegativeInteger', 'gYear': 'gYear',
          'token': 'token', 'time': 'time', 'yearMonthDuration': 'yearMonthDuration', 'NCName': 'NCName',
          'str': 'string'}



def md5(fname):
    '''
    Function to create hash codes that represent data, files, etc.
    :param fname: Name of file to read and hash
    :return: Hash code specific to file fname
    '''
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_agent_string(modules):
    '''
    Create unique id for the agent of a pipeline and get the version of python and all imported modules
    :param modules: List of module names imported
    :return: Unique id for the agent and list of versions for modules
    '''
    versions = []
    try:
        procPy = subprocess.Popen(['python3', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        procPy = subprocess.Popen(['python', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pythonVersion = procPy.stdout.read().decode('utf-8')
    loc = 'Python '
    pyVer = pythonVersion[pythonVersion.find(loc)+len(loc):]
    pyVer = pyVer.strip()
    pyVer = ''.join(e for e in pyVer if e.isalnum() or e == '.' or e == '-')
    pyVer = 'run:'+pyVer
    
    for mod in modules:
        proc1 = subprocess.Popen(['pip3', 'show',mod], stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['grep', 'Version'], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc1.stdout.close()

        out, err = proc2.communicate()
        versions.append(out.decode('utf-8'))

    versions = [x.replace('\n', '') for x in versions]
    versions = [x[x.find(': ')+2:] for x in versions]

    modString = [x + '_' + y for x, y in zip(modules, versions)]
    modString = ', '.join(modString)
    return modString, pyVer



def get_modules():
    '''
    Function to create the agent_json.json file, including creating a unique id for the agent, determining all modules
    imported, find their versions, structure and input all infroamtion into agent_json.json
    :return: agent_json.json
    '''
    modules = []
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            modName = val.__name__
            loc = modName.find('.')
            if loc != -1:
                modName = val.__name__[0:loc]
            modules.append(modName)

    exclude = ['__builtin__',
               'Tester','_thread','graphlib','scriptScript','__future__','_threading_local','grp','scriptresubmitter',
               '_abc','_tkinter','gzip','secrets','_aix_support','_tracemalloc','hashlib','select','_ast','_uuid',
               'heapq','selectors','_asyncio','_warnings','hmac','setuptools','_bisect','_weakref','html','shelve',
               '_blake2','_weakrefset','http','shlex','_bootlocale','_xxsubinterpreters','idlelib','shutil',
               '_bootsubprocess','_xxtestfuzz','imaplib','signal','_bz2','_zoneinfo','imghdr','site','_codecs','abc',
               'imp','smtpd','_codecs_cn','aifc','importlib','smtplib','_codecs_hk','antigravity','inspect','sndhdr',
               '_codecs_iso2022','argparse','io','socket','_codecs_jp','array','ipaddress','socketserver','_codecs_kr',
               'ast','itertools','spwd','_codecs_tw','asynchat','json','sqlite3','_collections','asyncio','keyword',
               'sre_compile','_collections_abc','asyncore','latexWriter','sre_constants','_compat_pickle','atexit',
               'lib2to3','sre_parse','_compression','audioop','linecache','ssl','_contextvars','base64','locale',
               'stat','_crypt','bdb','logging','statistics','_csv','binascii','lzma','string','_ctypes','binhex',
               'mailbox','stringprep','_ctypes_test','bisect','mailcap','struct','_curses','builtins','marshal',
               'subprocess','_curses_panel','bwd','math','sunau','_datetime','bz2','mimetypes','symbol','_decimal',
               'cProfile','mmap','symtable','_distutils_hack','calendar','modulefinder','sys','_elementtree','cgi',
               'multiprocessing','sysconfig','_functools','cgitb','netrc','syslog','_hashlib','chunk','nis','tabnanny',
               '_heapq','cmath','nntplib','tarfile','_imp','cmd','ntpath','telnetlib','_io','code','nturl2path',
               'tempfile','_json','codecs','numbers','termios','_locale','codeop','opcode','test','_lsprof',
               'collections','operator','tester','_lzma','colorsys','optparse','testing_prtr_packagetemplateDictionary',
               '_markupbase','compileall','os','textwrap','_md5','concurrent','ossaudiodev','this','_multibytecodec',
               'configparser','parser','threading','_multiprocessing','contextlib','pathlib','time','_opcode',
               'contextvars','pdb','timeit','_operator','copy','periodic','tkinter','_osx_support','copyreg','pickle',
               'token','_peg_parser','crypt','pickletools','tokenize','_pickle','csv','pip','trace','_posixshmem',
               'ctypes','pipes','traceback','_posixsubprocess','curses','pkg_resources','tracemalloc','_py_abc',
               'dataclasses','pkgutil','tty','_pydecimal','datetime','platform','turtle','_pyio','dbm','plistlib',
               'turtledemo','_queue','decimal','poplib','types','_random','difflib','posix','typing','_sha1','dis',
               'posixpath','unicodedata','_sha256','distutils','pprint','unittest','_sha3','doctest','profile','urllib',
               '_sha512','email','provcall-NoWorkflow-save','uu','_signal','encodings','pstats','uuid','_sitebuiltins',
               'ensurepip','pty','valuefilemaker','_socket','enum','pwd','venv','_sqlite3','errno','py_compile',
               'warnings','_sre','faulthandler','pyclbr','wave','_ssl','fcntl','pydoc','weakref','_stat','filecmp',
               'pydoc_data','webbrowser','_statistics','fileinput','pyexpat','wheel','_string','fnmatch','pytest',
               'wsgiref','_strptime','formatter','python_modules','xdrlib','_struct','fractions','queue','xml',
               '_symtable','ftplib','quopri','xmlrpc','_sysconfigdata__linux_x86_64-linux-gnu','functools',
               'random','xxlimited','_sysconfigdata_x86_64_conda_cos6_linux_gnu','gc','re','xxsubtype',
               '_sysconfigdata_x86_64_conda_linux_gnu','genBindings','readline','zerosigmaker','_testbuffer',
               'genericpath','reprlib','zipapp','_testcapi','getopt','resource','zipfile','_testimportmultiple',
               'getpass','rlcompleter','zipimport','_testinternalcapi','gettext','runpy','zlib','_testmultiphase',
               'glob','sched','zoneinfo',
               'genBindings','praetor','convert2prov','decorate','praetorTemplates','praetor_settings',
               'praetor_settings_user','templateDictionary', 'python_modules']

    modules = [x for x in modules if x not in exclude]

    json_total = {}
    modules_versions, py_version = get_agent_string(modules)

    bindings['var'] = {}
    bindings['var']['modules'] = ['run: ({})'. format(modules_versions)]
    bindings['var']['python_version'] = [py_version]
    bindings['var']['lifeline'] = ['urn_uuid:{}'.format(os.environ["PRAETOR_pipeline_id"])]

    json_dir = praetor_settings.provenance_directory + os.environ['PRAETOR_pipeline_id'] + '/json/'

    json_total['agent'] = bindings

    with open(json_dir + 'agent_json.json', 'w') as f:
        json.dump(json_total, f)


def timestamp():
    ts = str(time.time())
    return ts


def datetimestamp():
    dts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    return dts


def gen_identifier(variable, naming_template="entity"):
    '''
    General utility function to create prov ids for python objects
    :param variable: Value of object to create id for
    :param naming_template: Name related to the object in question to include in the id
    :return: id for target object
    '''
    try:
        prov_id = prov_id_cache[id(variable)]
    except KeyError:
        prov_id_counter[naming_template] += 1
        prov_id = '{}_{}_{}'.format(naming_template, session_id, prov_id_counter[naming_template])
        prov_id_cache[id(variable)] = prov_id

    return prov_id


def escape_forbidden_characters(in_string):
    '''
    Escape forbidden characters in input string in accordance with PROV-N
    :param in_string: input string to escape characters within
    :return: modified in_string with escaped characters
    '''
    forbidden = '\\(=)|,:;[]'
    allowed_special = '/._-'
    no_forbidden = [x if x.isalnum() else '\\' + x if x in forbidden else x if x in allowed_special else '' for x in
                 in_string]
    final_string = ''.join(no_forbidden)
    return final_string


def remove_quotes_from_string(in_string):
    out_string = [x for x in in_string if x not in ['"', "'"]]
    out_string = ''.join(out_string)
    return out_string


def find_type(value):
    '''
    If possible, return the type of input value and convert it to string
    :param value: Input value to type
    :param praetor_rec: switch to turn off provenance recording
    :return: String value, type of value
    '''

    global praetor_rec
    try:
        praetor_rec += 1
        outVal = str(value)
        praetor_rec = 0
        outVal = remove_quotes_from_string(outVal)
        otype = type(value).__name__
        if otype in dtypes.keys():
            ptype = dtypes[otype]
        else:
            ptype = 'string'
    except:
        praetor_rec += 1
        outVal = str(value)
        praetor_rec = 0
        outVal = remove_quotes_from_string(outVal)
        ptype = 'string'
    return outVal, ptype


def reduce_lists(in_list):
    '''
    Sub-rountine for un-nesting lists if they are present
    :param in_list: Nested input list
    :return: Flattened version of in_list
    '''
    while any(isinstance(i, list) for i in in_list):
        flat_new = []
        for sublist in in_list:
            if not isinstance(sublist, list):
                flat_new.append(sublist)
            else:
                for value in sublist:
                    flat_new.append(value)
        in_list = flat_new

    return in_list


def get_default_args(func):
    '''
    Extract the source code for a wrapped function
    :param decorated: Function source code including decorator
    :return: Function source code excluding decorator
    '''
    try:
        signature = inspect.signature(func)
    except (TypeError, AttributeError, ValueError) as e:
        return [], []
    out_dict =  {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    keys = [x for x in out_dict.keys()]
    values = [x for x in out_dict.values()]
    return keys, values


def extract_wrapped(decorated):
    closure = (c.cell_contents for c in decorated.__closure__)
    return next((c for c in closure if isinstance(c, types.FunctionType)), None)


def extract_string_type(type_string):
    locater = "'"
    loc1 = type_string.find(locater)
    loc2 = type_string[loc1+len(locater):].find(locater)
    final_type = type_string[loc1+len(locater):loc1+len(locater)+loc2]
    return final_type


def get_class_that_defined_method(meth):
    try:
        for cls in inspect.getmro(meth.im_class):
            if meth.__name__ in cls.__dict__:
                return cls.__name__

    except AttributeError:
        return None
    return None


def find_dict_differences(dict1, dict2):
    '''
    Used to find the differences between two dictionaries of global variables
    :param dict1: initial global variable dictionary
    :param dict2: updated global variable dictionary
    :return: Items in dict2 that are not in dict1
    '''
    differences = {}

    for key in dict2.keys():
        if key not in dict1:
            differences[key] = (dict2[key])

    for key in set(dict1.keys()).intersection(dict2.keys()):
        try:
            if dict1[key] != dict2[key]:
                differences[key] = ( dict2[key])
        except ValueError:
            if str(dict1[key]) != str(dict2[key]):
                differences[key] = (dict2[key])

    return differences


def track_globs(initial_globals):
    '''
    Find changes in global variabes between and old set and a freshly generated one
    :param initial_globals: Set of global variables to compare to
    :return: Differences between current and previous global variables
    '''
    final_globals = dict(globals())
    changed_globals = {name: value for name, value in final_globals.items() if name not in initial_globals or initial_globals[name] != value}
    return changed_globals


def provcall(inlist, outlist, template, longname, startTime, endTime, memUse, json_name,
             json_out='full_json.json', jsonDir='./', maxValueLength=praetor_settings.max_value_length, module_name='main',
             global_inputs=None, global_outputs=None):
    '''
    Consumes as input the various parameters and metrics surrounding a function execution and writes them into a json
    file as bindings, ready to combine with a template and make provenance.
    :param inlist: List of input values
    :param outlist: List of output values
    :param template: Name of provenance template corresponding to the function
    :param longname: Full name of the function (String)
    :param startTime: Start time of execution (dateTime object)
    :param endTime: End time of execution (dateTime object)
    :param memUse: Average memory consumption during function (Bytes)
    :param json_name: String for key to identify function execution in json file
    :param json_out: Name of json file to write data to
    :param jsonDir: Directory where json_out is located
    :param maxValueLength: Max number of characters for an input/output before it is saved as a "big entity"
    :param module_name: Name of thing where the function is defined (either main or a module)
    :param global_inputs: Dictionary of global variables consumed by a function
    :param global_outputs: Dictionary of global variables produced by a function
    :return: Updates json_out with the above information for the target function execution
    '''

    global praetor_rec

    template = ''.join(e if e.isalnum() else e if e == '_' else '' for e in template)
    longname = ''.join(e if e.isalnum() else e if e == '_' else '' for e in longname)
    identifier = uuid.uuid4()
    json_total = {}
    bindings['var'] = {}
    bindings['var']['messageStartTime'] = [{"@type": "xsd:dateTime", "@value": startTime}]
    bindings['var']['moduleName'] = [{"@type": "xsd:string", "@value": module_name}]
    bindings['var']['activityName'] = [{"@type": "xsd:string", "@value": longname}]

    if len(call_func_list) != 0 and call_func_list[-1] != '<module>':
        bindings['var']['message2'] = [{"@id": prov_id_activity_cache[-1][0]}]
        bindings['var']['message2StartTime'] = [{"@type": "xsd:dateTime", "@value": prov_id_activity_cache[-1][1]}]
        bindings['var']['message2EndTime'] = [{"@type": "xsd:dateTime", "@value": prov_id_activity_cache[-1][2]}]
        bindings['var']['template'] = [template + 'started']
    else:
        bindings['var']['template'] = [template]
    bindings['var']['message'] = [{"@id": "urn_uuid:{}_{}".format(longname, identifier)}]
    prov_id_activity_cache.append(["urn_uuid:{}_{}".format(longname, identifier),startTime,endTime])

    if longname in templateDictionary.tempDict:
        try:
            if len(outlist) < len(templateDictionary.tempDict[longname][1]):
                lenDiff = len(templateDictionary.tempDict[longname][1]) - len(outlist)
                for extra in range(lenDiff):
                    outlist.append('Not Computed')
            if len(inlist) < len(templateDictionary.tempDict[longname][0]):
                lenDiff = len(templateDictionary.tempDict[longname][0]) - len(inlist)
                for extra in range(lenDiff):
                    inlist.append('Not Computed')
        except KeyError:
            pass

    longfileDir = jsonDir.replace('json', 'big_entities')

    for x in range(len(outlist)):
        if callable(outlist[x]):
            outVal, ptype = find_type('callable_{}'.format(type(outlist[x])))
            object_id = gen_identifier(outVal, naming_template='{}_outEntity_{}'.format(longname, x))
        else:
            outVal, ptype = find_type(outlist[x])
            object_id = gen_identifier(outlist[x], naming_template='{}_outEntity_{}'.format(longname, x))

        if len(outVal) > maxValueLength:
            with open(longfileDir + object_id + '.txt', 'w') as f:
                praetor_rec += 1
                f.write(str(outlist[x]))
                praetor_rec = 0
            outVal = longfileDir + object_id + '.txt'
            ptype = 'string'
        bindings['var']['output' + str(x)] = [{"@id": "run:" + object_id}]
        bindings['var']['output' + str(x) + 'value'] = [{"@value": outVal, "@type": "xsd:{}".format(ptype)}]

    if global_outputs is not None:
        object_id = gen_identifier(global_outputs, naming_template='globals')
        bindings['var']['praetorglobaloutput'] = [{"@id": "run:" + object_id}]
        for glob_key, glob_val in global_outputs.items():
            object_id = gen_identifier(glob_val, naming_template='globals_{}'.format(glob_key))
            g_val, ptype = find_type(glob_val)
            if len(g_val) > maxValueLength:
                with open(longfileDir + object_id + '.txt', 'w') as f:
                    f.write(str(glob_val))
                g_val = longfileDir + object_id + '.txt'
                ptype = 'string'
            bindings['var']['praetorglobaloutput{}'.format(glob_key)] = [{"@id": "run:" + object_id,
                                                                          "@value": g_val,
                                                                          "@type": "xsd:{}".format(ptype),
                                                                          "@label": 'run:{}'.format(glob_key)}]

    for x in range(len(inlist)):
        if callable(inlist[x]):
            inVal, ptype = find_type('callable_{}'.format(type(inlist[x])))
            object_id = gen_identifier(inVal, naming_template='{}_inEntity_{}'.format(longname, x))
        else:
            inVal, ptype = find_type(inlist[x])
            object_id = gen_identifier(inlist[x], naming_template='{}_inEntity_{}'.format(longname, x))

        if len(inVal) > maxValueLength:
            with open(longfileDir + object_id + '.txt', 'w') as f:
                praetor_rec += 1
                f.write(str(inlist[x]))
                praetor_rec = 0
            inVal = longfileDir + object_id + '.txt'
            ptype = 'string'

        bindings['var']['input' + str(x)] = [{"@id": "run:" + object_id}]
        bindings['var']['input' + str(x) + 'value'] = [{"@value": inVal, "@type": "xsd:{}".format(ptype)}]

    if global_inputs is not None:
        object_id = gen_identifier(global_inputs, naming_template='globals')
        bindings['var']['praetorglobalinput'] = [{"@id": "run:" + object_id}]
        for glob_key, glob_val in global_inputs.items():
            object_id = gen_identifier(glob_val, naming_template='globals_{}'.format(glob_key))
            g_val, ptype = find_type(glob_val)
            if len(g_val) > maxValueLength:
                with open(longfileDir + object_id + '.txt', 'w') as f:
                    f.write(str(glob_val))
                g_val = longfileDir + object_id + '.txt'
                ptype = 'string'
            bindings['var']['praetorglobalinput{}'.format(glob_key)] = [{"@id": "run:" + object_id, "@value": g_val,
                                                                         "@type": "xsd:{}".format(ptype),
                                                                         "@label": 'run:{}'.format(glob_key)}]

    bindings['var']['messageEndTime'] = [{"@type": "xsd:dateTime", "@value": endTime}]
    bindings['var']['memoryUsage'] = [{"@type": "xsd:string", "@value": memUse}]

    if len(call_func_list) != 0 and call_func_list[-1] != '<module>':
        json_total[json_name + 'started'] = bindings
        with open(jsonDir + json_out, 'a') as f:
            json.dump(json_total, f)
            f.write('\n')

    else:
        json_total[json_name] = bindings
        with open(jsonDir + json_out, 'a') as f:
            json.dump(json_total, f)
            f.write('\n')


def printDict():
    print(prov_id_cache, "prov_id_cache")


def get_globals():
    '''
    Creates a dictionary of all global variables present within the target pipeline, execluding those added by the
    praetor  code and built-in variables
    :return: Dictionary of global variables
    '''
    frame_1 = inspect.currentframe().f_back
    frame = frame_1.f_back
    globals_dict = frame.f_globals
    main_script_globals = {key:value for key,value in globals_dict.items() if not key.startswith('__')
                           and not any(sub in key for sub in ['genBindings', 'praetor', 'prov_id_counter'])
                           and not (inspect.ismodule(value) or inspect.isfunction(value) or inspect.isclass(value))}
    return main_script_globals


def create_template(func, template_name, template_name_started, function_name, filePath):
    '''
    Create a PROV-N template for a target python function
    :param func: Target function object
    :param template_name: Name of PROV-N template to create
    :param template_name_started: Name of PROV-N template if the function was started by another
    :param function_name: Name of function
    :param filePath: Path where templates will be generated
    :param global_tracking: Whether to track global variables
    :return: Creates the appropriate template for the function and stores a copy of the source code
    '''
    if isinstance(func, types.FunctionType):
        try:
            func_unwrapped = extract_wrapped(func)
        except (TypeError, AttributeError) as e:
            func_unwrapped = func
        func_source = inspect.unwrap(func_unwrapped)
        source = textwrap.dedent(inspect.getsource(func_source))
        source_str = source.encode('ascii', 'ignore').decode("utf-8")
        output_list = praetorTemplates.separate_output(source_str)
        try:
            input_list = [key for key in inspect.signature(func_source).parameters.keys()]
        except (TypeError, AttributeError, ValueError) as e:
            input_list = ['inputs_not_found']
        funct_name = func_source.__name__
        function_parameters = [funct_name, input_list, output_list]
        temp_sep_dict = {function_parameters[0]: [function_parameters[1], function_parameters[2]]}
        importlib.reload(templateDictionary)
        full_temp_dict = templateDictionary.tempDict
        full_temp_dict.update(temp_sep_dict)
        bundle, bundleStarted = praetorTemplates.generateBundle(function_parameters, praetorTemplates.bundleStart,
                                                                praetorTemplates.bundleEnd)

        with open(filePath + 'templates/' + template_name, 'w') as f:
            f.write(bundle)

        with open(filePath + 'templates/' + template_name_started, 'w') as f:
            f.write(bundleStarted)

        with open(filePath + 'function_store/' + function_name, 'w') as f:
            f.write(source_str)

        with open(filePath + 'templateDictionary.py', 'w') as f:
            f.write('tempDict = {}'.format(full_temp_dict))


def provWrap(func):
    '''
    Wrapper to decorate a function with in order to record provenance
    :param func: Target function object to wrap
    :return: An altered version of func which records provenance
    '''
    provWrap.count = 0

    def wrap(*args, **kwargs):
        name = func.__name__
        if name in praetor_settings.blacklist or praetor_rec != 0:
            return func(*args, **kwargs)
        try:
            module_loc = func.__module__
            if module_loc == '__main__':
                module_loc = 'main'
                module_name = ''
            else:
                module_name = '_' + module_loc
        except Exception:
            module_loc = 'undefined'
            module_name = ''

        try:
            input_list = [key for key in inspect.signature(func).parameters.keys()]
        except (TypeError, AttributeError, ValueError) as e:
            input_list = ['inputs_not_found']
            print('inputs for function {} not found'.format(name))

        longname = name
        template = name + module_name + '_template.provn'
        json_name = name + module_name
        template_name_started = name + module_name + 'started_template.provn'
        function_name = name + module_name + 'function.txt'
        inlist = list(args)
        filePath = praetor_settings.provenance_directory + os.environ['PRAETOR_pipeline_id'] + '/'
        jsonDir = filePath + 'json/'

        if not os.path.isfile(filePath + 'templates/' + template):
            create_template(func, template, template_name_started, function_name, filePath)

        try:
            defaultsKeys, defaultsVals = get_default_args(func)
        except TypeError:
            defaultsKeys, defaultsVals = [], []
        kwarg_list = []
        for key in input_list:
            if key in kwargs.keys():
                kwarg_list.append(kwargs[key])
            elif key in defaultsKeys:
                kwarg_list.append(defaultsVals[defaultsKeys.index(key)])

        inlist.extend(kwarg_list)


        if not praetor_settings.global_tracking:
            global_inputs = None
        else:
            global_start = get_globals()
            global_inputs = find_dict_differences(glob_vars[0], global_start)
            glob_vars.insert(0, global_start)

        startTime = datetimestamp()

        print('{} function_start: {}.{}'.format(praetor_settings.unique_string, module_loc, name))
        if praetor_settings.memory:
            try:
                mem_use, output = memory_usage((func, args, kwargs), retval=True)
                max_mem = str(max(mem_use))
            except:
                output = func(*args, **kwargs)
                max_mem = '0'
        else:
            output = func(*args, **kwargs)
            max_mem = '0'

        if not praetor_settings.global_tracking:
            global_outputs = None
        else:
            global_variables = get_globals()
            global_outputs = find_dict_differences(glob_vars[0], global_variables)
            glob_vars.insert(0, global_variables)

        print('{} function_end: {}.{}'.format(praetor_settings.unique_string, module_loc, name))
        endTime = datetimestamp()
        outlist = [output]
        provcall(inlist, outlist, template, longname, startTime, endTime, max_mem, json_name, jsonDir=jsonDir,
                 module_name=module_loc, global_outputs=global_outputs, global_inputs=global_inputs)
        call_func_list.append(inspect.stack()[1].function)
        return output

    return wrap


def provWrapOpen(func):
    '''
    Wrapper alter pythons built-in open function so that it records provenance
    :param func: The open function object (typically just open)
    :return: Altered functionality open which also records provenance
    '''
    def wrapOpen(*args, **kwargs):
        filePath = praetor_settings.provenance_directory + os.environ['PRAETOR_pipeline_id'] + '/'
        provDests = ['/json/', '/prov/', '/templates/', '/big_entities/', '/function_store/']
        provPaths = [filePath + x for x in provDests]
        fileName = args[0]

        try:
            gate = [True for x in provPaths if x in fileName]
        except TypeError:
            gate = [False]

        if any(gate):
            output = func(*args, **kwargs)

        else:
            longname = 'pythonBuiltinFileAccess'
            template = longname + '_template.prov'
            json_name = longname
            jsonDir = filePath + '/json/'
            startTime = datetimestamp()
            if praetor_settings.memory:
                try:
                    mem_use, output = memory_usage((func, args, kwargs), retval=True)
                    max_mem = str(max(mem_use))
                except:
                    output = func(*args, **kwargs)
                    max_mem = '0'
            else:
                output = func(*args, **kwargs)
                max_mem = '0'
            endTime = datetimestamp()
            mode = output.mode
            metaData = os.stat(fileName)
            inlist = [fileName, mode]
            outlist = []
            inlist.extend([x for i, x in enumerate(metaData) if i in [4, 6]])
            hashvalue = md5(args[0])
            inlist.append(hashvalue)
            provcall(inlist, outlist, template, longname, startTime, endTime, max_mem, json_name, jsonDir=jsonDir)
            call_func_list.append(inspect.stack()[0][3])
        return output

    return wrapOpen


def for_all_methods(decorator):
    '''
    Applies a target decorator to a class, was used to apply the provWrap but is currently out of use
    :param decorator: Decorator to add to a class
    :return: Class with altered functionality to record provenance
    '''
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate

def for_all_methods_inherited(decorator):
    '''
    Applies a target decorator to a class, was used to apply the provWrap but is currently out of use
    :param decorator: Decorator to add to a class
    :return: Class with altered functionality to record provenance
    '''
    def decorate(cls):
        for attr in cls.__dict__:
            for name, fn in inspect.getmembers(cls, inspect.isroutine):
                setattr(cls, name, decorator(getattr(cls, fn)))
        return cls

    return decorate


def decorate_imported_function(func, decorator):
    '''
    Function to apply a decorator to an imported function
    :param func: Target function object
    :param decorator: Decorator to apply
    :return: Altered function which now records provenance
    '''
    func_type = type(func).__name__
    if isinstance(func, types.FunctionType):
        func = decorator(func)
    elif isinstance(func, types.BuiltinFunctionType):
        func = decorator(func)
    elif isinstance(func, types.ModuleType):
        func = decorate_all_in_module(func, decorator)
    else:
        print('function {} with type {} not supported by praetor and not wrapped'.format(func, func_type))
    return func


def decorate_all_in_module(module, decorator):
    '''
    Decorate the functions within imported modules
    :param module: Module to decorate
    :param decorator: decorator to apply
    :return: The function of the selected module is altered to record provenance
    '''
    mod_spec_blacklist = [x for x in praetor_settings.blacklist if module.__name__ in x]
    func_blacklist = [x[x.find('.')+1:] for x in mod_spec_blacklist]
    for name in dir(module):
        obj = getattr(module, name)
        try:
            obj_name = obj.__name__
        except:
            obj_name = obj
        if obj_name not in func_blacklist:
            if isinstance(obj, types.FunctionType):
                setattr(module, name, decorator(obj))
            elif isinstance(obj, types.BuiltinFunctionType):
                setattr(module, name, decorator(obj))
            elif isinstance(obj_name, types.ModuleType):
                for_all_methods(decorator(obj_name))
                # decorate_all_in_module(obj, decorator)
            else:
                pass


