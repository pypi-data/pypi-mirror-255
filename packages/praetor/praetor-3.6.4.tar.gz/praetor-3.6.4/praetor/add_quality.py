#!/usr/bin/env python
# coding: utf-8

import argparse
import hashlib
import re
import subprocess
import uuid

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


def find_all_locs(string, substring):
    locs = [m.start() for m in re.finditer(substring, string)]
    return locs


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def find_identifier(entity_name, prov_file):
    hash_value = None

    if entity_name[:4] != 'run:':
        try:
            hash_value = md5(entity_name)
        except:
            print('entity_name is un-hashable')

    ID = []

    with open(prov_file, 'r') as f:
        for line in f:
            if hash_value is not None:
                is_there_hash = line.find(hash_value)
                if is_there_hash != -1:
                    loc1 = line.find('(')
                    loc2 = line.find(',')
                    ID.append(line[loc1 + 1:loc2])
            entity_loc = line.find(entity_name)
            if entity_loc != -1:
                loc1 = line.find('(')
                loc2 = line.find(',')
                ID.append(line[loc1 + 1:loc2])

    id_set = list(set(ID))

    return id_set


def find_activity_id(prov_file_name):
    with open(prov_file_name, 'r') as f:
        for line in f:
            if line[:22] == 'agent(urn_uuid:praetor':
                agent_id = line[line.find('(') + 1:line.find(',')]
                return agent_id


def escape_forbidden_characters(in_string):
    forbidden = "\\(=)|,:;[]"
    allowed_special = '/._-'
    no_forbidden = [x if x.isalnum() else '\\' + x if x in forbidden else x if x in allowed_special else '' for x in
                    in_string]
    final_string = ''.join(no_forbidden)
    return final_string


def add_quality_prov_prtr(input_prov_file, prov_ID, obj_type, name, value, quality_file='quality.provn',
                          temp_listing='listing.txt', preserve=None, other_prov=None, other_prov_id=None):
    ID = 'run:' + str(uuid.uuid4())
    val_type = type(value).__name__
    prov_val_type = dtypes[val_type]

    if not preserve:
        name = escape_forbidden_characters(name)
        value = escape_forbidden_characters(value)

    Q_ID = 'run:quality_measure_' + name

    prefixes = '''
    prefix urn_uuid <urn:uuid:>
    prefix run <http://example.org/>
    prefix var <http://openprovenance.org/var#>
    prefix rdf <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs <http://www.w3.org/2000/01/rdf-schema#>
    prefix prtr <https://praetor.pages.mpcdf.de/praetor_provenance/>
    '''
    qm_string = 'entity({0}, [prov:value="{1}" %% xsd:{2}, rdf:type="{3}"])'.format(ID, value, prov_val_type, Q_ID)
    quality_label = 'entity({0}, [prov:label="{1}", rdfs:subClassOf="prtr:QualityMeasure"])'.format(Q_ID, name)
    if obj_type == 'entity':
        quality_entity = 'entity({0},[prtr:hadQuality="{1}"])'.format(prov_ID, ID)
    elif obj_type == 'activity':
        quality_entity = 'activity({0},[prtr:hadQuality="{1}"])'.format(prov_ID, ID)
    elif obj_type == 'agent':
        quality_entity = 'agent({0},[prtr:hadQuality="{1}"])'.format(prov_ID, ID)
    else:
        raise ValueError(
            'Allowed values for the type of object to attach quality to are (--type, -t) are entity, activity, or agent')

    if other_prov is None:
        prov_file_string = 'document\n{}\n{}\n{}\n{}\nendDocument'.format(prefixes, qm_string, quality_label,
                                                                          quality_entity)
    else:
        if other_prov_id is None:
            other_prov_id = find_activity_id(other_prov)
        file_relations = 'wasGeneratedBy({0},{1},-)'.format(ID, other_prov_id)
        prov_file_string = 'document\n{0}\n{1}\n{2}\n{3}\n{4}\nendDocument'.format(prefixes, qm_string,
                                                                                   quality_label, quality_entity,
                                                                                   file_relations)

    with open(quality_file, 'w') as f:
        f.write(prov_file_string)

    listing_text = 'file, {0}, provn\nfile, ./{1}, provn'.format(input_prov_file, quality_file)

    with open(temp_listing, 'w') as f:
        f.write(listing_text)

    outfile = input_prov_file.replace('.provn', '_quality.provn')

    subprocess.call(['provconvert', '-merge', temp_listing, '-outfile', outfile])

    if other_prov is not None:
        listing_text = 'file, {0}, provn\nfile, ./{1}, provn'.format(outfile, other_prov)
        with open(temp_listing, 'w') as f:
            f.write(listing_text)
        subprocess.call(['provconvert', '-merge', temp_listing, '-outfile', outfile])

if __name__ == "__main__":

    parser = argparse.ArgumentParser('My program')
    parser.add_argument('-f', '--provfile')
    parser.add_argument('-i', '--provid')
    parser.add_argument('-q', '--quality')
    parser.add_argument('-v', '--value')
    parser.add_argument('-e', '--entity')
    parser.add_argument('-p', '--preserve')
    parser.add_argument('-w', '--workflow')
    parser.add_argument('-t', '--type')

    args = parser.parse_args()

    prov_file = args.provfile
    prov_id = args.provid
    quality_name = args.quality
    quality_value = args.value
    object_value = args.entity
    preserve_gate = args.preserve
    creation_prov_file = args.workflow
    object_type = args.type

    if prov_id is None and object_value is None:
        lifeline_ID = find_activity_id(prov_file)
        object_type = 'agent'
        add_quality_prov_prtr(prov_file, lifeline_ID, object_type, quality_name, quality_value, preserve=preserve_gate,
                              other_prov=creation_prov_file)
    elif object_value == None:
        add_quality_prov_prtr(prov_file, prov_id, object_type, quality_name, quality_value, preserve=preserve_gate,
                              other_prov=creation_prov_file)
    elif prov_id == None:
        ID = find_identifier(object_value, prov_file)
        if len(ID) == 0:
            print('specified value and hash value not found in provenance')
        else:
            object_type = 'entity'
            for identifier in ID:
                add_quality_prov_prtr(prov_file, identifier, object_type, quality_name, quality_value,
                                      preserve=preserve_gate, other_prov=creation_prov_file)
    else:
        print('Please use either a prov ID or entity, not both')
