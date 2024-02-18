from setuptools import setup

setup(name='praetor',
      version='3.6.4',
      python_requires='>=3.7',
      description='Automatic Generation of Provenance from Python3 Scripts',
      url='https://gitlab.mpcdf.mpg.de/PRAETOR/prov-PRAETOR_public/',
      author='Michael Johnson',
      author_email='michael.johnson0100@gmail.com',
      license='MIT',
      packages=['praetor'],
      install_requires=['codegen', 'matplotlib', 'memory_profiler', 'pymongo', 'rdflib', 'pandas', 'prov', 'requests'],
      scripts=['bin/praetor_run.py', 'bin/add_quality.py'],
      zip_safe=False)

