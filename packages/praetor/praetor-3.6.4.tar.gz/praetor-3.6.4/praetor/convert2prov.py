import os
import json
from praetor import praetorTemplates


def template_from_json(json):

    template = '\nbundle exe:bundle1\n'

    entities = {key: value for key, value in json['var'].items() if 'input' in key}
    for x in range(int(len(entities) / 2)):
        ent_str = "\nentity(var:input{0}, [prov:value = 'var:input{0}value'])\nused(var:message, var:input{0}, -, [prov:role='exe:input_{0}'])\n".format(x)
        template += ent_str

    activity = '''\nactivity(var:message, var:messageStartTime, var:messageEndTime, [prtr:activityName = 'var:activityName',\nprtr:hadMemoryUsage = 'var:memoryUsage', prtr:activitySource = 'var:moduleName', prov:label="var:comment"  ])\n'''
    agent = "agent(var:lifeline, [prtr:modules = 'var:modules', prtr:python_version = 'var:python_version', prov:type='prtr:SoftwareAgent'])\nwasAssociatedWith(var:message, var:lifeline, - , [])\n"

    if 'message2' in list(json['var'].keys()):
        activity_2 = '\nactivity(var:message2, var:message2StartTime, var:message2EndTime)'
        started_relation = '\nwasStartedBy(var:message2, -, var:message, -)\n'
        template += activity
        template += activity_2
        template += agent
        template += started_relation
    else:
        template += activity
        template += agent

    entities = {key: value for key, value in json['var'].items() if 'output' in key}
    for x in range(int(len(entities) / 2)):
        ent_str = "\nentity(var:output{0}, [prov:value = 'var:output{0}value'])\nwasGeneratedBy(var:output{0}, var:message, -)\n".format(x)
        template += ent_str

    template += "\nendBundle"
    return template

def combine_prov(json_file, agent_json_file, template_dir, out_prov, commented_globals):
    '''
    Combines the output of praetor code to produce a singular provenance file.
    :param json_file: Bindings file name from praetor, usually named full_json.json
    :param agent_json_file: Bindings file name from praetor for agent data, usually named agent_json.json
    :param template_dir: Directory name where prov templates were generated
    :param out_prov: Name of the combined provenance file
    :return: One provenance file produced named out_prov which contains all information from the run
    '''
    template_list = os.listdir(template_dir)
    template_short = [x.replace('_template.provn', '') for x in template_list]
    template_dictionary = {}
    prefix_lines = []

    for name, temp in zip(template_short, template_list):
        with open(template_dir + temp, 'r') as f:
            data = f.readlines()
        template_string = [x for x in data if x not in ['document\n', 'endDocument']]
        prefix_lines.extend([item for item in template_string if item[0:7] == 'prefix '])
        refined_data = [item for item in template_string if item not in prefix_lines]
        big_string = ''.join(refined_data)
        template_dictionary[name] = big_string

    prefix_lines_set = list(set(prefix_lines))
    prefix_string = ''.join(prefix_lines_set)

    with open(agent_json_file, 'r') as f:
        for line in f:
            line = line.replace('\n', '')
            json_object = json.loads(line)
            agent_var = json_object['agent']['var']

    with open(out_prov, 'w') as f:
        f.write('document\n{}prefix urn_uuid <urn:uuid:>\nprefix run <http://example.org/>'.format(prefix_string))
    track_globals = False
    with open(json_file, 'r') as f:
        with open(out_prov, 'a') as out:
            for line in f:
                line = line.replace('\n', '')
                json_object = json.loads(line)
                name = next(iter(json_object))
                try:
                    template = template_dictionary[name]
                except KeyError:
                    template = template_from_json(json_object[name])
                    template_dictionary[name] = template
                field_names = json_object[name]['var'].keys()
                param_id = []
                param_value = []
                param_type = []
                param_label = []
                comment_labels = []
                comment_id = []
                for field_name in field_names:
                    if any([x in field_name for x in ['praetorglobalinput', 'praetorglobaloutput']]):
                        track_globals = True
                        if field_name in ['praetorglobalinput', 'praetorglobaloutput']:
                            glob_id = json_object[name]['var'][field_name][0]["@id"]
                        else:
                            param_label_single = json_object[name]['var'][field_name][0]['@label']
                            param_label_single = param_label_single[param_label_single.find(':')+1:]
                            if param_label_single in commented_globals:
                                comment_labels.append(json_object[name]['var'][field_name][0]['@value'])
                            else:
                                param_label.append(json_object[name]['var'][field_name][0]['@label'])
                                param_id.append(json_object[name]['var'][field_name][0]['@id'])
                                param_value.append(json_object[name]['var'][field_name][0]['@value'])
                                param_type.append(json_object[name]['var'][field_name][0]['@type'])

                    elif next(iter(json_object[name]['var'][field_name][0])) == '@id':
                        template = template.replace('var:{},'.format(field_name),
                                                    str(json_object[name]['var'][field_name][0]['@id']) + ',')

                    elif next(iter(json_object[name]['var'][field_name][0])) in ['@type', '@value']:
                        template = template.replace("'var:{}'".format(field_name),
                                                    '"{}" %% {}'.format(
                                                        json_object[name]['var'][field_name][0]['@value'].replace('\n', ''),
                                                        json_object[name]['var'][field_name][0]['@type']))
                        if field_name in ['messageStartTime', 'messageEndTime', 'message2StartTime', 'message2EndTime']:
                            template = template.replace("var:{}".format(field_name),
                                                        str(json_object[name]['var'][field_name][0]['@value']))
                if track_globals:
                    activity_id = json_object[name]['var']['message'][0]['@id']
                    glob_bund = praetorTemplates.globalBundle(param_label, param_value, param_id, param_type,
                                                              activity_id)
                    if len(comment_labels) == 0:
                        template = template.replace(', prov:label="var:comment"', '')
                    else:
                        comment_list = ['prov:label="{}" '.format(sing_com) for sing_com in comment_labels]
                        comment_string = ','.join(comment_list)
                        template = template.replace('prov:label="var:comment"', comment_string)
                    template = template.replace('endBundle', glob_bund + '\nendBundle')

                for field_name in agent_var.keys():
                    variable = str(agent_var[field_name][0]).replace('(', '')
                    variable = variable.replace(')', '')
                    if len(variable) > 0:
                        template = template.replace("'var:{}'".format(field_name), "'{}'".format(variable))
                    if field_name == 'lifeline':
                        template = template.replace("var:{},".format(field_name), "{},".format(variable))
                out.write(template)
            out.write('\nendDocument')




