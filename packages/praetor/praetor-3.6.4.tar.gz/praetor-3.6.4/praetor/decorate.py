#!/usr/bin/env python33
# coding: utf-8

from io import BytesIO
import re
import sys
import tokenize

def findAll(inString,findx):
    '''
    Sub-routine used to find import locations
    :param inString: input string to search
    :param findx: substring to look for
    :return: all start locations of findx
    '''
    return [m.start() for m in re.finditer(findx, inString)]


def find_matching(importLines, modSearch):
    '''
    Find lines which import modules specified within the praetor settings file
    :param importLines: Lines where import substring is present
    :param modSearch: List of modules to search for
    :return: Lines of target file which import the modules in modSearch
    '''
    possible_start_values = [',', ' ']
    possible_end_values = [',', ' ', '\n']

    importLines = [x + '\n' for x in importLines]
    for x in importLines:
        hash_find = [i for i, letter in enumerate(x) if letter == '#']
        if len(hash_find) != 0:
            first_hash = min(hash_find)
            def_find = x.find('def')
            if first_hash < def_find:
                importLines.remove(x)
    period_index = modSearch.find('.')
    if period_index not in [-1, 0]:
        modSearch = modSearch[:modSearch.find('.')]

    mod_variations = []

    for start in possible_start_values:
        for end in possible_end_values:
            mod_variations.append(start + modSearch + end)

    matchingMod = [y for y in importLines if any(mod in y for mod in mod_variations)]
    matchingMod = [x[:-1] for x in matchingMod]
    return matchingMod


def module_string(mod):
    '''
    Creates the code to wrap imported modules and or functions
    :param mod: Module name
    :return: Python code to add to decorated file
    '''
    module = 'genBindings.decorate_all_in_module({},genBindings.provWrap)'.format(mod)
    function = '{0} = genBindings.decorate_imported_function({0},genBindings.provWrap)'.format(mod)

    conditional_string ='''
try:
    if isinstance({0}, types.FunctionType):
        {1}
        print("{3} is function" )
    elif isinstance({0}, types.BuiltinFunctionType):
        {1}
        print("{3} is built-in function" )
    else:
        {2}
        print("{3} is Module" )
except:
    print("Module or function {0} not found")
'''.format(mod, function, module, mod)

    return conditional_string


def extract_commented_code(line, py_ver):
    '''
    Function to extract all code hidden behind comments
    :param line: String line of code
    :return: String of comments code or None if there are none
    '''
    if py_ver == 2:
        try:
            tokens = tokenize.generate_tokens(BytesIO(line.encode('utf-8')).readline)
            if tokens is not None:
                for toktype, tok, start, end, line in tokens:
                    if toktype == tokenize.COMMENT:
                        commented_code = tok[1:].strip()
                        return commented_code
        except tokenize.TokenError:
            return 'None'
    else:
        try:
            tokens = tokenize.tokenize(BytesIO(line.encode('utf-8')).readline)
            if tokens is not None:
                for token in tokens:
                    if token.type == tokenize.COMMENT:
                        commented_code = token.string[1:].strip()
                        return commented_code
        except tokenize.TokenError:
            return 'None'

    return 'None'


def get_indentation(line):
    '''
    Function to return the indentation of any line of python code
    :param line: String of line to check
    :return: Numerical representation of indent
    '''
    stripped_line = line.lstrip()
    indentation = len(line) - len(stripped_line)
    return indentation


def add_fake_functions(exampleScript, loc_key='praetor_insert', loc_key_comment='praetor_comment'):
    '''
    Reads an input script, searches for commented keywords, generates and inserts fake functions into the
    decorated version of the script to record tailored provenance
    :param exampleScript: String of target python script
    :param loc_key: Keyword to trigger fake generation
    :return: original script with fake function additions as a string
    '''
    data = exampleScript.split('\n')
    py_ver = sys.version_info[0]
    to_comment = []
    for i, line in enumerate(data):
        line_comment = extract_commented_code(line, py_ver)
        if loc_key in line_comment:
            line_indent = get_indentation(line)
            com_items = line_comment.split(' ')
            input_names = [x[len('in_names='):] for x in com_items if 'in_names=' in x]
            input_values = [x[len('in_values='):] for x in com_items if 'in_values=' in x]
            outputs = [x[len('out='):] for x in com_items if 'out=' in x]
            name = [x[len('name='):] for x in com_items if 'name=' in x]
            function_string = '{0}def {1}({2}):\n    {0}return {3}\n{1}({4})'.format(' ' * line_indent, name[0],
                                                                                     input_names[0], outputs[0],
                                                                                     input_values[0])
            data[i] += '\n{0}'.format(function_string, ' ' * line_indent)

        if loc_key_comment in line_comment:
            com_items = line_comment.split(' ')
            to_comment = [x[len('comment='):] for x in com_items if 'comment=' in x]

    reformated_script = '\n'.join(data)
    return reformated_script, to_comment


def decorateFile(exampleScript, modules, wrap_open=False):
    '''
    Function to create a decorated version of a python script which wraps the desired imported modules/functions
    and the functions defined within the script in order to record provenance. It also adds imports to required
    modules and inserts fake functions based upon user input comment-hidden commands.
    :param exampleScript: Target script to decorate
    :param modules: List of target modules to decorate
    :param wrap_open: Whether to wrap pythons built-in open function
    :param global_tracking: Whether global variables should be tracked
    :return: Decorated version of exampleScript
    '''
    find1 = '.py'
    loc1 = exampleScript.index(find1)
    scriptShort = exampleScript[0:loc1]

    scriptNew = scriptShort + '_decorated.py'

    with open(exampleScript, 'r') as f:
        ogData = f.read()

    ogData, commented_globals = add_fake_functions(ogData)

    importRequired = '\nfrom praetor import genBindings\nimport types\ngenBindings.get_modules()\n'
    open_wrap = 'open = genBindings.provWrapOpen(open)\n'
    if wrap_open:
        importRequired += open_wrap

    end_of_script = '\ngenBindings.get_modules()'
    first_line_import = ogData[0:ogData.find('\n')]
    if len(first_line_import) != 0:
        if first_line_import[0:7] == 'import ':
            imports = [0]
            imports.extend([x + 1 for x in findAll(ogData, '\nimport ')])
        else:
            imports = [x + 1 for x in findAll(ogData, '\nimport ')]
    else:
        imports = findAll(ogData, '\nimport ')
        imports = [x + 1 for x in imports]
    importLines = [ogData[x:x + ogData[x:].index('\n')] for x in imports]

    if len(first_line_import) != 0:
        if first_line_import[0:5] == 'from ':
            from_imports = [0]
            from_imports.extend([x + 1 for x in findAll(ogData, '\nfrom ')])
        else:
            from_imports = [x + 1 for x in findAll(ogData, '\nfrom ')]
    else:
        from_imports = [x + 1 for x in findAll(ogData, '\nfrom ')]

    from_import_lines = [ogData[x:x + ogData[x:].index('\n')] for x in from_imports]

    ogData_lists = ogData.split('\n')
    first_line = ogData_lists[0]
    shebang_str = '#!/usr/bin/env python33'
    if shebang_str in first_line:
        first_import_loc = ogData.find(ogData_lists[1])
    else:
        first_import_loc = 0
    from_future = ogData.find('from __future__ import')
    future_import = ogData.find('import __future__')
    if from_future != -1 or future_import != -1:
        from_locs = [m.start() for m in re.finditer('from __future__ import', ogData)]
        im_locs = [im.start() for m in re.finditer('import __future__', ogData)]
        im_locs.extend(from_locs)
        final_loc = max(im_locs)
        first_import_loc = ogData[final_loc:].find('\n')

    ogData = ogData[:first_import_loc] + importRequired + ogData[first_import_loc:]

    ogData = ogData + end_of_script

    asString = ' as '
    for mod in modules:
        matchingMod = find_matching(importLines, mod)
        matchingFrom = find_matching(from_import_lines, mod)


        if len(matchingMod) != 0:
            if len(matchingMod) > 1:
                print('two imports matching the same naming convention for lines {} these have not been wrapped'.format(
                    matchingMod))
                continue
            if asString in matchingMod[0]:
                functName = matchingMod[0][matchingMod[0].index(asString) + len(asString):]
            else:
                functName = mod
            modifier = module_string(functName)
            ogData = ogData.replace(matchingMod[0], matchingMod[0] + '\n' + modifier)

        if len(matchingFrom) != 0:
            for line in matchingFrom:
                loc1 = line.find(' import ') + len(' import ')
                if loc1 != -1:
                    new_dec = module_string(mod)
                    ogData = ogData.replace(line, line + '\n' + new_dec)

    updatedData = ogData.replace('\ndef ', '\n@genBindings.provWrap\ndef ')

    with open(scriptNew, 'w') as f:
        f.write(updatedData)

    return scriptNew, commented_globals




