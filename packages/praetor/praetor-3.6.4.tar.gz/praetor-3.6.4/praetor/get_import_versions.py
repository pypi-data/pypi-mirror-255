import subprocess

import importlib
import sys

# try:
prtr_path = os.environ['PRAETOR']
sys.path.append(prtr_path)
import praetor_settings
# except:
#     # from praetor import praetor_settings
#     # import praetor_settings
#     sys.path.append(praetor_settings.dynamic_file_dir)


import python_modules


def get_agent_string():
    versions = []
    procPy = subprocess.Popen(['python','--version'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    pythonVersion = procPy.stderr.read().decode('utf-8')
    # print(pythonVersion)
    loc = 'Python '
    pyVer = pythonVersion[pythonVersion.find(loc)+len(loc):]
    pyVer = pyVer.strip()
    pyVer = ''.join(e for e in pyVer if e.isalnum() or e == '.' or e == '-')

    importlib.reload(python_modules)
    modules = python_modules.modules

    for mod in modules:
        proc1 = subprocess.Popen(['pip','show',mod],stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['grep','Version'],stdin=proc1.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        proc1.stdout.close()

        out, err = proc2.communicate()
        versions.append(out.decode('utf-8'))

    versions = [x.replace('\n','') for x in versions]
    versions = [x[x.find(': ')+2:] for x in versions]

    modString = ["exe:{}='u2p:{}'".format(x,y) for x,y in zip(modules,versions)]
    modString.insert(0,"exe:python='u2p:{}'".format(pyVer))

    agentString = ', '.join(modString)

    return agentString
