#!/usr/bin/env python
# coding: utf-8

from collections import Counter
from datetime import datetime
import logging
import os
import requests

import matplotlib.pyplot as plt
import pandas as pd
try:
    from pandas.io.json import json_normalize
except:
    from pandas import json_normalize


DATABASE_HOST_URL = os.environ.get('DATABASE_HOST_URL', 'http://127.0.0.1:3030/')
REPOSITORY_ID = os.environ.get('REPOSITORY_ID', 'ds')
SPARQL_REST_URL = DATABASE_HOST_URL + REPOSITORY_ID

prefixes = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX run: <http://example.org/>
        PREFIX exe: <http://example.org/>
        PREFIX prtr: <https://praetor.pages.mpcdf.de/praetor_provenance/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
'''

prefix_dict = {'http://www.w3.org/ns/prov#': 'prov:',
               'http://example.org/': 'run:',
               'https://praetor.pages.mpcdf.de/praetor_provenance/': 'prtr:',
               'http://www.w3.org/2000/01/rdf-schema#': 'rdfs:'}

def remove_name_spaces(string, name_spaces):
    '''
    Remove namespaces from values in the provenance
    :param string: Input string to remove prefixes from
    :param name_spaces: Namespaces to remove
    :return: input string minus namespaces
    '''
    for x in name_spaces:
        try:
            string = string.replace(x, '')
        except AttributeError:
            for i, val in enumerate(string):
                string[i] = val.replace(x, '')
    return string


def clear_response(arr):
    logging.debug('StaticUtils: clearing given array')
    unwanted_strings = ['s', '', ' ', 's,p', 's,p,o', 'p,o', 'o', 'p', 'g', 'g,s,p,o', 's,p,o,r',
                        'activity,entity,p,dt,value,role,startTime,endTime', 's,s_count', 's,s_count,graphs', 's_count',
                        's,s_count,p,o,o_count', 'uuid,s,p,o', 's,g,s_count', 's,s_count,roles', 's,ts,te', 's,u']

    for string in unwanted_strings:
        if string in arr:
            arr.remove(string)

    logging.debug('StaticUtils: cleared list: ' + str(arr))

    return arr


def query_handler(query):
    '''
    Sends query to triple store
    :param query:
    :return: response of query
    '''
    response = requests.post(SPARQL_REST_URL,
                             data={'query': query},
                             timeout=86400)

    return response


def query_handler_histograms(query):
    '''
    Sends query to triple store
    :param query:
    :return: response of query
    '''
    response = requests.post(SPARQL_REST_URL,
                             data={'query': query},
                             headers={'Accept': 'text/csv'},
                             timeout=86400)

    return response

def upload_provenance(file_name):
    '''
    Function for uploading provenance files to the database
    :param file_name: name of provenance file to upload
    :return: Name of the graph in the database
    '''
    file_name_short = file_name.split('/')[-1]
    pipeline = 'http://' + file_name_short.replace('.ttl', '')
    data = open(file_name).read()
    headers = {'Content-Type': 'text/turtle;charset=utf-8'}
    url = SPARQL_REST_URL + '/data'
    requests.post(url, params={'graph': pipeline}, data=data, headers=headers)
    return pipeline


def convert_to_datetime(datetime_str):
    datetime_str = datetime_str[:-6]
    time = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    return time


def convert_to_datetime_exception(datetime_str):
    '''
    Converts a string representation of datetime to a datetime object - temperamental
    :param datetime_str:
    :return: datetime object
    '''
    try:
        time = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        try:
            time = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            time = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')

    return time


def result_to_df(response, pre_dict=prefix_dict):
    '''
    Converts a response from the database to a pandas dataframe
    :param response: response to convert
    :return: pandas dataframe format response
    '''
    df = json_normalize(response.json()['results']['bindings'], meta='value')
    cols = [c for c in df.columns if c[-6:] == '.value']
    df2 = df[cols]
    col_names = [x for x in cols]

    if 'startTime.value' in col_names and 'endTime.value' in col_names:
        start_strs = df['startTime.value'].tolist()
        end_strs = df['endTime.value'].tolist()

        start_str = [x for x in start_strs]
        datetime_start = [convert_to_datetime_exception(x) for x in start_str]

        end_str = [x for x in end_strs]
        datetime_end = [convert_to_datetime_exception(x) for x in end_str]

        durations = [(x - y).total_seconds() for x, y in zip(datetime_end, datetime_start)]

        df2.insert(1, 'duration (s)', durations)

    df2 = df2.drop_duplicates()
    for key, value in pre_dict.items():
        df2 = df2.replace(key, value, regex=True)
    return df2


def user_defined_query(query):
    '''
    Function to pass a SPARQL query to the database
    :param query: string SPARQL query
    :return: dataframe of the results
    '''
    res = query_handler(query)
    response_as_string = clear_response(res.text.split("\r\n"))
    print(response_as_string)
    df = result_to_df(res)
    return df


def object_histogram(pipeline_list, object_name, object_type, prefixes=prefixes):
    '''
    Creates a histogram for the potential values for parameters or runtime metrics within one or more provenance datasets
    :param pipeline_list: list of provenance files to upload and query
    :param object_name: Name (role) of the parameter or name of the function to investigate
    :param object_type: can be 'entity' or 'activity'
    :param prefixes: prefixes required for the query
    :return: Data frame of the results and histogram plots
    '''
    res_string = ''
    frames = []
    for pipeline in pipeline_list:
        pipeline_name = upload_provenance(pipeline)

        if object_type == 'entity':
            query = prefixes + '''
            SELECT ?value
            FROM NAMED <''' + pipeline_name + '''>
            WHERE {
            GRAPH ?g {
            ?be a prov:Usage .
            ?be prov:hadRole ''' + object_name + ''' .
            ?be prov:entity ?entity .
            ?entity prov:value ?value .
            }
            }
            '''
        if object_type == 'activity':
            query = prefixes + '''
            SELECT ?startTime ?endTime ?memory ?output
            FROM NAMED  <''' + pipeline_name + '''>
            WHERE {
            GRAPH ?g {
            ?a a prov:Activity .
            ?a prtr:activityName  "''' + object_name + '''" . 
            ?a prov:startedAtTime ?startTime . 
            ?a prov:endedAtTime ?endTime .
            ?a prtr:hadMemoryUsage ?memory . 
            ?o prov:wasGeneratedBy ?a .
            ?o prov:value ?output .
            }
            }
            '''

        res = query_handler(query)
        df = result_to_df(res)
        df.to_csv('{}.csv'.format(pipeline))
        frames.append(df)
    final_df = pd.concat(frames)
    time_d = {}
    for col in final_df.columns:
        if col in ['startTime.value', 'endTime.value']:
            time_d[col] = final_df[col].values.tolist()

        else:
            if col != 'duration (s)':
                values = final_df[col].values.tolist()
                letter_counts = Counter(values)
                df = pd.DataFrame.from_dict(letter_counts, orient='index')
                ax = df.plot(kind='bar')
                ax.set_xlabel(col[:col.find('.')])
                ax.set_ylabel('Occurence')
                plt.show()

    if time_d != {}:
        duration = [(convert_to_datetime(x) - convert_to_datetime(y)).total_seconds() for x, y in
                    zip(time_d['endTime.value'], time_d['startTime.value'])]
        plt.hist(duration)
        plt.ylabel('Occurence')
        plt.xlabel('Duration')
        plt.xticks(rotation=90)
        plt.show()


    return final_df


def query_activity(pipeline, prefixes=prefixes):
    '''
    Queries the database for all activities within it and returns their names, ID, start/end times and memory usage
    :param pipeline: the name of the graph to query
    :param prefixes: prefixes required for the query
    :return: results from the query
    '''
    query = prefixes + '''

         SELECT ?activityID ?functionName ?startTime ?endTime ?memory ?functionSource 
         FROM NAMED <''' + pipeline + '''>                      

         WHERE {
         GRAPH ?g {
         
         ?activityID a prov:Activity .
         ?activityID prtr:activityName ?functionName.
         ?activityID prov:startedAtTime ?startTime.
         ?activityID prov:endedAtTime ?endTime.
         ?activityID prtr:hadMemoryUsage ?memory.
         ?activityID prtr:activitySource ?functionSource.
         }
         }

         '''

    res = query_handler(query)
    df = result_to_df(res)
    return df



def query_started_individual(pipeline, activity, prefixes=prefixes):
    '''
    A query to return all functions that were started by a target function
    :param pipeline: name of the graph to query
    :param activity: name of the activity
    :param prefixes: prefixes required for query
    :return: The identifier of each function started by the target activity
    '''

    if 'uuid:' in activity:
        activity = activity[activity.find('uuid:')+len('uuid:'):]

    query = prefixes + '''

         SELECT ?a
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?a2 prov:qualifiedStart ?b .
         ?b prov:hadActivity ?a .
        FILTER(CONTAINS(str(?a2), "''' + activity + '''"))
         }
         }
         '''
    res = query_handler(query)
    response_as_string = clear_response(res.text.split("\r\n"))
    df = result_to_df(res)
    return df


def query_was_started_by_individual(pipeline, activity, prefixes=prefixes):
    '''
    A query to return all functions that started the target function
    :param pipeline: name of the graph to query
    :param activity: name of the activity
    :param prefixes: prefixes required for query
    :return: The identifier of each function that started the target activity
    '''
    query = prefixes + '''

         SELECT ?a
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?a prov:qualifiedStart ?b .
         ?b prov:hadActivity ?a2 .
         FILTER(CONTAINS(str(?a2), "''' + activity + '''"))

         }
         }
         '''
    res = query_handler(query)
    df = result_to_df(res)
    return df


def query_started(pipeline, prefixes=prefixes):
    '''
    A query to return all functions that were started by another
    :param pipeline: name of the graph to query
    :param prefixes: prefixes required for query
    :return: The identifier of each function started by another
    '''
    query = prefixes + '''

         SELECT ?startedBy ?started
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {
        
         ?startedBy prov:qualifiedStart ?awsb .
         ?awsb prov:hadActivity ?started.

         }
         }
         '''
    res = query_handler(query)
    df = result_to_df(res)
    return df


def query_input(pipeline, prefixes=prefixes):
    '''
    A query to find all inputs within a provenance dataset, the results show their ID, role, and value
    :param pipeline: the name of the graph to query
    :param prefixes: prefixes required for query
    :return: The identifier, role, and value of every entity used as an input
    '''
    query = prefixes + '''
         
         SELECT ?activityID ?entityID ?objectName ?value
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?activityID prov:qualifiedUsage ?ni .
         ?ni prov:entity ?entityID .
         ?ni prov:hadRole ?objectName .
         ?entityID prov:value ?value .

         }
         }
         '''
    res = query_handler(query)
    df = result_to_df(res)
    return df


def query_output(pipeline, prefixes=prefixes):
    '''
    A query to find all outputs within a provenance dataset, the results show their ID, role, and value
    :param pipeline: the name of the graph to query
    :param prefixes: prefixes required for the query
    :return: The identifier, role, and value of every entity used as an output
    '''
    query = prefixes + '''
         SELECT ?activityID ?value ?objectName 
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?objectName prov:wasGeneratedBy ?activityID .
         ?objectName prov:value ?value. 

         }
         }
         '''
    res = query_handler(query)
    df = result_to_df(res)
    return df


def query_output_individual(pipeline, activity, prefixes=prefixes):
    '''
     A query to find all outputs for a target function within a provenance dataset, the results show their ID, role,
      and value
    :param pipeline: name of the graph to query
    :param activity: name of the activity
    :param prefixes: prefixes required for query
    :return: The identifier, role, and value of every entity used as an output in target function
    '''
    query = prefixes + '''

         SELECT ?activityID ?entityID ?value
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?entityID prov:wasGeneratedBy ?activityID .
         ?activityID prtr:activityName ''' + activity + ''' .
         ?entityID prov:value ?value . 
         

         }
         }
         '''

    res = query_handler(query)
    df = result_to_df(res)
    return df


def query_input_individual(pipeline, entity, prefixes=prefixes):
    '''
    A query to find all of a specific input within a provenance dataset, the results show their ID, role, and value
    :param pipeline: the name of the graph to query
    :param entity: role of an entity to search (name of the entity in python)
    :param prefixes: prefixes required for the query
    :return: The identifier, role, and value of every entity used as an input
    '''
    query = prefixes + '''

         SELECT ?activityID ?entityID ?value
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?activityID prov:qualifiedUsage ?ni .
         ?ni prov:entity ?entityID .
         ?ni prov:hadRole ''' + entity + ''' .
         ?entityID prov:value ?value .

         }
         }
         '''

    res = query_handler(query)
    df = result_to_df(res)
    return df

def query_quality(pipeline, prefixes=prefixes):
    '''
    A query to extract quality metrics from provenance datasets
    :param pipeline: the name of the graph to query
    :param prefixes: prefixes required for the query
    :return: All values and metrics of quality contained within the provenance and what they are attached to
    '''

    query = prefixes + '''
    SELECT ?qualityMetric ?qualityValue ?qualityID 
    FROM NAMED <''' + pipeline + '''>
    
    WHERE {
    GRAPH ?g {

    ?qid a prov:Entity ;
        rdfs:label ?qualityMetric ;
        rdfs:subClassOf "prtr:QualityMeasure" .
        
    ?qualityID a prov:Entity ;
        prov:value ?qualityValue ;
        a ?qq .
    
    FILTER(CONTAINS(STR(?qq), ":quality_measure_"))
    
    }
    }
    '''

    query_2 = prefixes + '''
    SELECT ?qualityID ?objectID
    FROM NAMED <''' + pipeline + '''>
    
    WHERE {
    GRAPH ?g {

    ?objectID prtr:hadQuality ?qualityID .
    
    }
    }
    
    '''

    res = query_handler(query)
    df = result_to_df(res)
    res = query_handler(query_2)
    df2 = result_to_df(res)
    df_comb = df.merge(df2, how='outer', on='qualityID.value')
    df_comb = df_comb.dropna()
    return df_comb


def query_resources_used(pipeline, activity=None, prefixes=prefixes):
    '''
    Calculates the total memory and time for a function or a pipeline as a whole
    :param pipeline: name of the graph to query
    :param activity: name of the activity
    :param prefixes: prefixes required for query
    :return: total time (s) and memory (MB)
    '''
    query = prefixes + '''
    
    
         SELECT ?activityID ?startTime ?endTime ?memory 
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {
         ?activityID a prov:Activity .
         ?activityID prov:startedAtTime ?startTime.
         ?activityID prov:endedAtTime ?endTime.
         ?activityID prtr:hadMemoryUsage ?memory
         }
         }
    
    '''
    res = query_handler(query)
    results = result_to_df(res)

    if activity != None:
        sorted_df = results.sort_values(by=['startTime'], ascending=True)
        sorted_df = sorted_df.reset_index(drop=True)
        start = sorted_df.loc[sorted_df['activityID'] == activity].index.tolist()
        results = results[:start[0]]

    func_times = results['duration (s)'].tolist()

    memory = results['memory.value'].tolist()
    mem_vals = [float(x) for x in memory]

    tot_time = sum(func_times)
    func_mem = [(x * y) for x, y in zip(func_times, mem_vals)]
    tot_mem = sum(func_mem)

    return {'total_time_s': tot_time, 'total_memory_MB': tot_mem}


def query_av_mem(pipeline, prefixes=prefixes):
    '''
    Determine all function which had a greater than average memory consumption
    :param pipeline: Name of pipeline to query
    :param prefixes: Prefixes  required for query
    :return: Names of all functions with greater than average memory usage
    '''
    query = prefixes + '''

         SELECT ?n 
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?a a prov:Activity .
         ?a prtr:activityName ?n . 
         ?a prtr:hadMemoryUsage ?mem.
         FILTER( ?mem > AVG(?mem))
         
         }
         }
         GROUP BY ?a
         '''

    res = query_handler(query)
    return res



def query_activity_source(pipeline, module, prefixes=prefixes):
    '''
    Query to find all activities belonging to a particular source, typically either main or a module name
    :param pipeline: pipeline name to query
    :param module: name of module
    :param prefixes: prefixes required for query
    :return: All activities that belong to the target module
    '''
    query = prefixes + '''

         SELECT ?a ?an
         FROM NAMED <''' + pipeline + '''>

         WHERE {
         GRAPH ?g {

         ?a a prov:Activity .
         ?a prtr:activityName ?an .
         ?a prtr:activitySource ''' + module + ''' .
         }
         }

         '''

    res = query_handler(query)

    return res


def forward_search(pipeline, object_id, n_itter, prefixes=prefixes):
    '''
    Function to find the n next objects in the provenance that are connected to object_id
    :param pipeline: name of provenance graph to query over
    :param object_id: id of object for the start of the search
    :param n_itter: number of connections from initial object to explore
    :param prefixes: prefixes required for the query
    :return: dataframe of all objects connected to the object_id over n connections
    '''
    activity_id = False
    structure_1 = '''
    FROM NAMED <''' + pipeline + '''>
    
    WHERE {
    GRAPH ?g {
    
    '''

    structure_2 = '''
    }
    }
    '''
    if 'uuid:' in object_id:
        object_id_search = object_id[object_id.find('uuid:')+len('uuid:'):]
        activity_id = True
    selects = ['?node{0}'.format(x) for x in range(n_itter+1)]
    sel_str = 'SELECT ' + ' '.join(selects)
    if activity_id:
        main_con = '?a ?relation0 ?node0 .'
    else:
        main_con = '{} ?relation0 ?node0 .'.format(object_id)
    connections = ['?node{0} ?relation{1} ?node{1} .'.format(x, x+1) for x in range(n_itter)]
    con_str = '\n'.join(connections)
    query =  main_con + '\n' + con_str
    filter_start = 'FILTER('
    filter_str = ['?relation{} != prov:wasAssociatedWith'.format(x) for x in range(n_itter)]
    filter_string = ' && '.join(filter_str)
    if activity_id:
        query += '\n' + filter_start + filter_string + ' && CONTAINS(STR(?a), "{}")'.format(object_id_search) + ') .\n'
    else:
        query += '\n' + filter_start + filter_string +') .\n'
    final_query = prefixes + sel_str + structure_1 + query + structure_2
    res = query_handler(final_query)
    df = result_to_df(res)
    df = df.drop_duplicates()
    return df


def backward_search(pipeline, object_id, n_itter, prefixes=prefixes):
    '''
    Function to find the n previous objects in the provenance that are connected to object_id
    :param pipeline: name of provenance graph to query over
    :param object_id: id of object for the start of the search
    :param n_itter: number of connections from initial object to explore
    :param prefixes: prefixes required for the query
    :return: dataframe of all objects connected to the object_id over n connections
    '''
    activity_id = False
    structure_1 = '''
    FROM NAMED <''' + pipeline + '''>

    WHERE {
    GRAPH ?g {

    '''

    structure_2 = '''
    }
    }
    '''
    if 'uuid:' in object_id:
        object_id_search = object_id[object_id.find('uuid:') + len('uuid:'):]
        activity_id = True
    selects = ['?node{0}'.format(x) for x in range(n_itter)]
    sel_str = 'SELECT ' + ' '.join(selects)
    if activity_id:
        main_con = '?node0 ?relation0 ?a'
    else:
        main_con = '?node0 ?relation0 {} .'.format(object_id)
    connections = ['?node{1} ?relation{1} ?node{0} .'.format(x, x + 1) for x in list(reversed(range(n_itter)))[1:]]
    con_str = '\n'.join(connections)
    query = con_str + '\n' + main_con
    filter_start = 'FILTER('
    filter_str = ['?relation{} != prov:wasAssociatedWith'.format(x) for x in range(n_itter)]
    filter_string = ' && '.join(filter_str)
    if activity_id:
        '\n' + filter_start + filter_string + ' && CONTAINS(STR(?a), "{}")'.format(object_id_search) + ') .\n'
    else:
        query += '\n' + filter_start + filter_string + ') .\n'

    final_query = prefixes + sel_str + structure_1 + query + structure_2
    res = query_handler(final_query)
    df = result_to_df(res)
    df = df.drop_duplicates()
    return df
