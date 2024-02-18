import re
import ast
import codegen


def find(inString, findx):
    '''
    Find start locations of all instances of a substring within a string
    :param inString: String to search through
    :param findx: Substring to seach for
    :return: Start locations of all substring positions
    '''
    return [m.start() for m in re.finditer(findx, inString)]


def escape_forbidden_characters(in_string):
    '''
    Escape forbidden characters in input string in accordance with PROV-N
    :param in_string: input string to escape characters within
    :return: modified in_string with escaped characters
    '''
    forbidden = "\\(=)|,-:;[]+"
    allowed_special = '/._'
    in_string = [x if x.isalnum() else '\\'+x if x in forbidden else x if x in allowed_special else '' for x in in_string]
    final_string = ''.join(in_string)
    return final_string


def separateLists(inList):
    '''
    Similar to a ','.split(inList) function, but it also corrects for peculiarities in python parameter formatting
    :param inList: String representation of a list to separate
    :return: True list of separated variable names
    '''
    findC = ','
    sepLocs = find(inList,findC)
    sepLocs.insert(0,0)
    sepLocs.append(len(inList))
    
    inputList = [inList[x:y] for x, y in zip(sepLocs[0:-1], sepLocs[1:])]
    inputList = [x.replace(',','') for x in inputList]
    
    for x,inL in enumerate(inputList):
        if '=' in inL:
            loc1 = inL.find('=')
            inVal = inL[:loc1]
            inputList[x] = inVal
    
    return inputList


def separate_output(in_string):
    '''
    Walks the AST of a python function in order to separate outputs into distinct objects where applicable
    :param in_string: Function source code as string to walk
    :return: List of outputs from function
    '''
    answer = [(node.value) for node in ast.walk(ast.parse(in_string)) if isinstance(node, ast.Return)]

    possible_outputs = []
    for a in answer:
        try:
            outputlist = [codegen.to_source(a)]
        except (AttributeError, TypeError) as e:
            outputlist = ['None']
        if isinstance(a, tuple):
            outputlist = separateLists(outputlist)
        possible_outputs.append(outputlist)

    if len(possible_outputs) > 0:
        output_list = possible_outputs[-1]
    else:
        output_list = []

    return output_list


def variableSeparation(inString):
    '''
    Deconstructs function source code into key components such as name, inputs, and outputs
    :param inString: Function source code to separate
    :return: Dictionary of separated objects
    '''
    find1 = 'def '
    find2 = '('
    find3 = '):'
    find4 = 'return '
    find5 = '\n'
    
    functionDict = {}
    
    functionLocs = find(inString,find1)
    functionLocs.append(len(inString))

    for fNum in range(len(functionLocs)-1):
        searchString = inString[functionLocs[fNum]:functionLocs[fNum+1]]
        loc2 = searchString.index(find2)
        loc3 = searchString.index(find3)

        try:
            loc4s = find(searchString,find4)
        except:
            loc4s = []
        loc5s = [searchString[x:].index(find5) + x for x in loc4s]
        functName = searchString[len(find1):loc2]
        inputList = searchString[loc2+len(find2):loc3]
        if ',' in inputList:
            inputList = separateLists(inputList)
        else:
            inputList = [inputList]

        try:
            outputList = searchString[loc4s[-1]+len(find4):loc5s[-1]]
        except IndexError:
            outputList = 'empty'

        if ',' in outputList:
            outputList = separateLists(outputList)
        else:
            outputList = [outputList]

        if len(loc5s) != 0:
            function_string = searchString[:loc5s[-1]]
        else:
            function_string = searchString

        functionDict['funct_{0}'.format(fNum)] = [functName,inputList,outputList,function_string]
    return functionDict



bundleStart = """
document
prefix prov <http://www.w3.org/ns/prov#>
prefix var <http://openprovenance.org/var#>
prefix exe <http://example.org/>
prefix prtr <https://praetor.pages.mpcdf.de/praetor_provenance/>

bundle exe:bundle1"""

bundleEnd = '''
endBundle
endDocument'''


def createInputEntities(inputList, activity):
    '''
    Creates the input entity section of a PROV-N template specific to a python function
    :param inputList: List of names of the inputs to a function
    :param activity: Name of the function
    :param global_tracking: Whether global variables are being recorded
    :return: String defining the input entities and their relation to the function in PROV-N format
    '''
    activity = escape_forbidden_characters(activity)
    inputEntities = []
    inputList = [escape_forbidden_characters(x) for x in inputList]
    for i,inVal in enumerate(inputList):
        entityString = """
        entity(var:input{0}, [prov:value = 'var:input{0}value'])
        used(var:message, var:input{0}, -, [prov:role='exe:{2}_{1}'])""".format(i, inVal, activity)
        
        inputEntities.append(entityString)

    inputEntityString = '\n'.join(inputEntities)
    return inputEntityString


def createActivity(activity, agent):
    '''
    Creates the activity and agent string for the PROV-N code and the relations between them, corresponding to the
    function and python code, respectively
    :param activity: Name of function
    :param agent: Type of agent (typically software agent)
    :return: PROV-N format string for agent, activity and relations
    '''
    activity = escape_forbidden_characters(activity)
    agent = escape_forbidden_characters(agent)
    activityString = """
    activity(var:message, var:messageStartTime, var:messageEndTime, [prtr:activityName = 'var:activityName',
     prtr:hadMemoryUsage = 'var:memoryUsage', prtr:activitySource = 'var:moduleName', prov:label="var:comment" ])
    agent(var:lifeline, [prtr:modules = 'var:modules', prtr:python_version = 'var:python_version', prov:type='prtr:{1}'])

    wasAssociatedWith(var:message, var:lifeline, - , [])
    """.format(activity, agent)
    
    return activityString


def createActivityStarted(activity, agent):
    '''
    Creates the activity and agent string for the PROV-N code and the relations between them, corresponding to the
    function and python code, respectively. For the case when a function was started by another
    :param activity: Name of function
    :param agent: Type of agent (typically software agent)
    :return: PROV-N format string for agent, activity and relations
    '''

    activity = escape_forbidden_characters(activity)
    agent = escape_forbidden_characters(agent)
    activityString = """
    activity(var:message, var:messageStartTime, var:messageEndTime, [prtr:activityName = 'var:activityName',
     prtr:hadMemoryUsage = 'var:memoryUsage', prtr:activitySource = 'var:moduleName', prov:label="var:comment" ])
    activity(var:message2, var:message2StartTime, var:message2EndTime)
    agent(var:lifeline, [prtr:modules = 'var:modules', prtr:python_version = 'var:python_version', prov:type='prtr:{1}'])

    wasAssociatedWith(var:message, var:lifeline, - , [])
    wasStartedBy(var:message2, -, var:message, -)
    """.format(activity, agent)
    
    return activityString


def createOutputEntities(outputList):
    '''
    Creates the output entity section of a PROV-N template specific to a python function
    :param outputList: List of names of the outputs to a function
    :param global_tracking: Whether global variables are being recorded
    :return: String defining the output entities and their relation to the function in PROV-N format
    '''
    outputEntities = []
    outputList = [escape_forbidden_characters(x) for x in outputList]

    for o in range(len(outputList)):
        outputString = """
        entity(var:output{0}, [prov:value = 'var:output{0}value'])
        wasGeneratedBy(var:output{0}, var:message, -)""".format(o)

        outputEntities.append(outputString)

    outputEntityString = '\n'.join(outputEntities)

    return outputEntityString


def generateBundle(function, bundleStart, bundleEnd):
    '''
    Combines the PROV-N strings created by the other functions in this file and generates the full PROV-N template in
    string format.
    :param function: List generated by praetor which includes the function name, inputs, outputs, etc.
    :param bundleStart: PROV-N format string which declares the start of the provenance document
    :param bundleEnd: PROV-N format string which declares the end of the provenance document
    :return: String format PROV-N template for target function
    '''
    inEntities = createInputEntities(function[1], function[0])
    activity = createActivity(function[0],'SoftwareAgent')
    activityStarted = createActivityStarted(function[0],'SoftwareAgent')
    outEntities = createOutputEntities(function[2])

    bundleList = [bundleStart,inEntities,activity,outEntities,bundleEnd]
    bundle = '\n'.join(bundleList)
    
    bundleList2 = [bundleStart,inEntities,activityStarted,outEntities,bundleEnd]
    bundle2 = '\n'.join(bundleList2)

    return bundle, bundle2


def globalBundle(parameter_key, parameter_value, parameterID, parameter_type, activityID):
    '''
    Function used only when global tracking is enabled. Takes the names, values, and IDs of global parameters and
    generates PROV-N entity definitions for them as well as relations to the intended object already present in the
    provenance
    :param parameter_key: List of keys of the parameters in the global dictionary
    :param parameter_value: List of values of the parameters in the global dictionary
    :param globalID: Prov ID generated for the collection of global parameters
    :param parameterID: List of Prov IDs generated for the global dictionary
    :param parameter_type: List of python types for objects in the global dictionary
    :return: String representation of the entity definitions and relations for global variables
    '''
    global_bundle_relation = ''
    for key, val, pid, ptype in zip(parameter_key, parameter_value, parameterID, parameter_type):
        global_bundle_relation += '''
        entity({0}, [prov:value = "{2}" %% {3}, prov:type = "prtr:global_variable"])
        used({4}, {0}, -, [prov:role = "{1}"])
        '''.format(pid, key, val, ptype, activityID)

    return global_bundle_relation
