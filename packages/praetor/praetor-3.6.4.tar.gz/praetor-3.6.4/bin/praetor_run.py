#!/usr/bin/env python3
import os
import subprocess
import sys
import uuid
import time

t_start = time.time()

try:
    prtr_path = os.environ['PRAETOR']
    sys.path.append(prtr_path)
    import praetor_settings_user as praetor_settings

except:
    from praetor import praetor_settings
    # import praetor_settings
    pass

def generate_pipeline_id():
    '''
    Creates a unique id for a pipeline run which includes the praetor version
    :return: Unique id
    '''
    proc1 = subprocess.Popen(['pip3', 'show', 'praetor'], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', 'Version'], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc1.stdout.close()
    out, err = proc2.communicate()
    out = out.decode("utf-8")
    praetor_version = out[out.find(': ') + 2: -1]

    pipeline_id = "praetor_{}_{}".format(praetor_version, uuid.uuid4())
    return pipeline_id


def escape_forbidden_characters(in_string):
    '''
    Escapes special characters from an input string to fit PROV-N
    :param in_string: String to escape characters within
    :return: Original string with escaped characters
    '''
    forbidden = "\\(=)|,:;[]"
    allowed_special = '/._-'
    no_forbidden = [x if x.isalnum() else '\\' + x if x in forbidden else x if x in allowed_special else '' for x in in_string]
    final_string = ''.join(no_forbidden)
    return final_string


pipeline_id = generate_pipeline_id()
os.environ['PRAETOR_pipeline_id'] = pipeline_id
currentDir = praetor_settings.provenance_directory + '{}/'.format(pipeline_id)
subprocess.call(['mkdir', currentDir])

with open(currentDir+'templateDictionary.py','w') as f:
    f.write('tempDict = {}')


from praetor import convert2prov, decorate, genBindings, praetorTemplates
from praetor.python_builtin_wrap_templateGen import createOpenTemplate

# import convert2prov, decorate, praetorTemplates
# from python_builtin_wrap_templateGen import createOpenTemplate

newDirectories = ['prov', 'json', 'templates', 'big_entities', 'function_store']
for name in newDirectories:
    try:
        subprocess.call(['mkdir', currentDir+name])
    except:
        print('Directory {} already exists'.format(name))

with open(currentDir+'json/'+praetor_settings.json_file,'w') as f:
    f.write("")

if __name__ == '__main__':
    exampleScript = sys.argv[1]

    with open(exampleScript,'r') as f:
        script = f.read()

    newName, commented_globals = decorate.decorateFile(exampleScript, modules=praetor_settings.modules,
                                                       wrap_open=praetor_settings.wrap_open)

    functionCommands = ['python3', newName]

    if len(sys.argv) > 2:
        stringCommands = [str(x) for x in sys.argv[2:]]
        functionCommands.extend(stringCommands)

    if praetor_settings.wrap_open:
        createOpenTemplate()

    time_setup = time.time() - t_start
    t_se = time.time()

    with open(currentDir+'/console_output.log', 'wb') as f:
        process = subprocess.Popen(functionCommands, stdout=subprocess.PIPE)
        for c in iter(lambda: process.stdout.read(1), b""):
            try:
                sys.stdout.write(c.decode("utf-8"))
                f.write(c)
            except UnicodeDecodeError:
                try:
                    sys.stdout.reconfigure(encoding="utf-8")
                    f.write(c)
                except UnicodeDecodeError:
                    f.write('Console log line not recorded, unicode error')

    example_sep = praetorTemplates.variableSeparation(script)
    tot_sep_dict = {x[0]:[x[1],x[2]] for x in example_sep.values()}
    function_code = [x[3] for x in example_sep.values()]

    for counter,key in enumerate(example_sep.keys()):
        template_no_special = praetorTemplates.escape_forbidden_characters(example_sep[key][0])
        if not os.path.isfile(currentDir+'/templates/{}_template.provn'.format(template_no_special)):
            bundle, bundleStarted = praetorTemplates.generateBundle(example_sep[key], praetorTemplates.bundleStart,
                                                                    praetorTemplates.bundleEnd)
            with open(currentDir+'/templates/{}_template.provn'.format(template_no_special),'w') as f:
                f.write(bundle)

            with open(currentDir+'/templates/{}started_template.provn'.format(template_no_special),'w') as f:
                f.write(bundleStarted)

            with open(currentDir+'/function_store/{}_function.txt'.format(template_no_special),'w') as f:
                f.write(function_code[counter])

    subprocess.call(['mv', newName, currentDir])

    make_string = """
ts := $(shell /bin/date "+%Y%m%d%H%M%S")

build:
\tmvn clean install

merge:
\tfind ./prov/*.provn | sed "s/^/file, /; s/$$/, provn/" | provconvert -merge - -outfile mergey.provn

flatten:
\tprovconvert -infile mergey.provn -index -flatten -outfile flatten_file.provn

flattensvg:
\tprovconvert -infile mergey.provn -index -flatten -outfile flatten_file.svg
  
flattenpng:
\tprovconvert -infile mergey.provn -index -flatten -outfile flatten_file.png

flattenrdf:
\tprovconvert -infile mergey.provn -index -flatten -outfile flatten_file.rdf

flattenttl:
\tprovconvert -infile mergey.provn -index -flatten -outfile flatten_file.ttl    
    """

    t_run = time.time() - t_se
    t_r = time.time()
    if praetor_settings.build_prov:

        convert2prov.combine_prov(currentDir+'json/full_json.json', currentDir+'json/agent_json.json',
                                  currentDir+'templates/', currentDir+'mergey.provn', commented_globals)

        with open(currentDir+'Makefile', 'w') as f:
            f.write(make_string)

        if praetor_settings.flatten_prov:
            os.chdir(currentDir)
            subprocess.call(['make','flatten'])

    t_build = time.time() - t_r

timing_string = "set_up_time = {0}\nrun_time = {1}\nbuild_time = {2}".format(time_setup, t_run, t_build)

with open(currentDir+'prtr_timing_'+pipeline_id+'.txt', 'w') as f:
    f.write(timing_string)
