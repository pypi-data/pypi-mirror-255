#!/usr/bin/env python
# coding: utf-8

import sys
import os

try:
    prtr_path = os.environ['PRAETOR']
    sys.path.append(prtr_path)
    import praetor_settings_user as praetor_settings
    from praetor import praetorTemplates

except:
    from praetor import praetor_settings, praetorTemplates
    # from praetor import praetor_settings
    # import praetor_settings

sys.path.append(praetor_settings.provenance_directory + os.environ['PRAETOR_pipeline_id'] + '/')


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
     prtr:hadMemoryUsage = 'var:memoryUsage', prtr:activitySource = 'var:moduleName' ])
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
     prtr:hadMemoryUsage = 'var:memoryUsage', prtr:activitySource = 'var:moduleName' ])
    activity(var:message2, var:message2StartTime, var:message2EndTime)
    agent(var:lifeline, [prtr:modules = 'var:modules', prtr:python_version = 'var:python_version', prov:type='prtr:{1}'])

    wasAssociatedWith(var:message, var:lifeline, - , [])
    wasStartedBy(var:message2, -, var:message, -)
    """.format(activity, agent)

    return activityString


def generateBundle(function, bundleStart, bundleEnd):
    inEntities = praetorTemplates.createInputEntities(function[1], function[0])
    activity = createActivity(function[0], 'SoftwareAgent')
    activityStarted = createActivityStarted(function[0], 'SoftwareAgent')
    outEntities = praetorTemplates.createOutputEntities(function[2])


    bundleList = [bundleStart, inEntities, activity, outEntities, bundleEnd]
    bundle = '\n'.join(bundleList)

    bundleList2 = [bundleStart, inEntities, activityStarted, outEntities, bundleEnd]
    bundle2 = '\n'.join(bundleList2)

    return bundle, bundle2


def createOpenTemplate():
    fileFunc = """
    def fileAccess(fileName, mode, user_ID, size, hash_value):
        metadata = 'metadata'
        return fileName
    """
    func = praetorTemplates.variableSeparation(fileFunc)
    funcList = [x for x in func.values()]
    funcList = funcList[0]
    bundle, bundleStarted = generateBundle(funcList, praetorTemplates.bundleStart,
                                                            praetorTemplates.bundleEnd)

    with open(praetor_settings.provenance_directory + os.environ['PRAETOR_pipeline_id'] + '/' +
              'templates/pythonBuiltinFileAccess_template.provn', 'w') as f:
        f.write(bundle)

    with open(praetor_settings.provenance_directory + os.environ['PRAETOR_pipeline_id'] + '/' +
              'templates/pythonBuiltinFileAccessstarted_template.provn', 'w') as f:
        f.write(bundleStarted)
