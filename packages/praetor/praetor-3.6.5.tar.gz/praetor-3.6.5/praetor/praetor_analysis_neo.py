import subprocess

from neo4j import GraphDatabase
import pandas as pd
from prov.model import ProvDocument
from prov2neo.client import Client
from neotime import DateTime

class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


def create_conn(prov_file, add="localhost:7687", usr='neo4j', password='admin', name='neo4j', scheme='bolt',
                uri="bolt://localhost:7687"):
    '''
    Uploads provenance file to neo4j database and establishes a connection to it
    :param prov_file: Provenance file to upload
    :param add: Address of neo4j database
    :param usr: username for neo4j
    :param password: password for neo4j
    :param name: name of database to upload to
    :param scheme: uri scheme
    :param uri: uri to connect to neo4j
    :return: Connection to neo4j database to be used for queries
    '''
    if prov_file[-5:] != '.json':
        extension = prov_file[prov_file.find('.'):]
        json_file = prov_file.replace(extension, '.json')
        subprocess.call(['provconvert', '-infile', prov_file, '-outfile', json_file])
    else:
        json_file = prov_file

    with open(json_file, 'r') as f:
        data = f.read()
    data = data.replace('"prov:starter":', '"prov:trigger":')
    with open(json_file, 'w') as f:
        f.write(data)

    graph = ProvDocument.deserialize(source=json_file, format="json")

    client = Client()
    client.connect(
        address=add,
        user=usr,
        password=password,
        name=name,
        scheme=scheme
    )
    client.import_graph(graph)
    conn = Neo4jConnection(uri=uri, user=usr, pwd=password)

    return conn


def query_handler(conn, query_string):
    '''
    Passes queries to Neo4j
    :param conn: Connection to Neo4j
    :param query_string: Query to pass
    :return: query results in a pandas dataframe
    '''
    result = conn.query(query_string, db='neo4j')
    return result


def clear_data(conn):
    '''
    Deletes all data from target neo4j graph database
    :param conn: connection to target graph
    :return:
    '''
    conn.query('MATCH (n) DETACH DELETE n', db='neo4j')


def activity_query(conn):
    query = "MATCH (n:Activity) RETURN n"
    result = query_handler(conn, query)
    df = pd.DataFrame([dict(r) for record in result for r in record])
    return df


def output_query(conn):
    query = "MATCH (n) - [r:wasGeneratedBy] -> (p) RETURN n"
    result = query_handler(conn, query)
    df = pd.DataFrame([dict(r) for record in result for r in record])
    return df


def input_query(conn):
    query = "MATCH (n) - [r:used] -> (p) RETURN p"
    result = query_handler(conn, query)
    df = pd.DataFrame([dict(r) for record in result for r in record])
    return df


def memory_query(conn):
    query = '''
    MATCH (n) WITH AVG(toFloat(n.`prtr:hadMemoryUsage`)) AS average 
    MATCH (n), (r)
    WHERE toFloat(r.`prtr:hadMemoryUsage`) > average
    RETURN r
    '''
    result = query_handler(conn, query)
    df = pd.DataFrame([dict(r) for record in result for r in record])
    return df


def source_query(conn):
    query = "MATCH (n:Activity) WHERE (n.`prtr:activitySource` = 'main') RETURN n"
    result = query_handler(conn, query)
    df = pd.DataFrame([dict(r) for record in result for r in record])
    return df
