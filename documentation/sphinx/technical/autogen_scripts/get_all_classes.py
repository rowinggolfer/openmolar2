#!/usr/bin/env python

'''
A module which pulls classes from all modules found walking
the directory (given as sys.argv[1])
'''

import inspect
import os, sys

KLASS_OUTDIR = "/home/neil/openmolar/hg_openmolar/documentation/sphinx/technical/classes"
KLASS_SUBDIR = os.path.join(KLASS_OUTDIR, "classes")

if not os.path.exists(KLASS_OUTDIR):
    os.mkdir(KLASS_OUTDIR)

if not os.path.exists(KLASS_SUBDIR):
    os.mkdir(KLASS_SUBDIR)

def klass_rst(module, klass):
    '''
    returns file contents understood by sphinx.
    eg.

    Advisor
    -------
    .. module:: lib_openmolar.common.widgets
        rst from the modules docstring
    .. autoclass:: lib_openmolar.common.widgets.Advisor
        :members:
        :undoc-members:
        :show-inheritance:

        .. automethod:: lib_openmolar.common.widgets.Advisor.__init__

    '''

    module_dir = os.path.dirname(module.__file__)
    module_path = module_dir + "." + module.__name__

    #remove the junk at the front of sys.argv[1]
    junk = os.path.dirname(os.path.abspath(sys.argv[1]))

    module_path = module_path.replace(junk, "", 1).strip(os.path.sep)
    module_path = module_path.replace(os.path.sep, ".")

    klass_path = module_path + "." +klass

    output = "%s\n%s\n\n"% (klass, "-"*len(klass))
    header_file = "technical/class_headings/%s.rst"% klass
    if not os.path.isfile(header_file):
        print "CREATING NEW CLASS HEADER FILE", header_file
        f = open(header_file, "w")
        f.close()

    f = open(header_file)
    contents = f.read()
    f.close()
    if contents != "":
        ## sometimes I need to ensure the path to the class is used!
        output += contents.replace("<KLASS>", klass_path)
    else:
        output += '''Incomplete documentation - sorry!

.. note::
    Neil - please put some data in %s'''% header_file

    output += '''

methods and attributes
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: %s
    :members:
    :undoc-members:
    :show-inheritance:

    .. automethod:: %s.__init__'''% (klass_path, klass_path)

    return output

def get_classes(module):
    '''
    Args:
        module (module object)

    examines the namespace of the module and
    Generates a list of classes which belong to this module.

    ignores 'private' classes
    '''

    for name in dir(module):
        obj = getattr(module, name)
        if (inspect.isclass(obj) and
        obj.__module__ == module.__name__ and
        obj.__name__[0] != "_"):
            yield obj

def get_class_names(module):
    '''
    returns the classes name (rather than the object itself)
    '''
    for klass in get_classes(module):
        yield klass.__name__

def get_modules(folder):
    '''
    Args:
        folder (string)

    returns a list of all python modules found under folder *folder*
    '''
    for root, dir_, files in os.walk(folder, followlinks=True):
        sys.path.insert(0, root)
        for file in files:
            if file.endswith(".py"):
                module = file.replace('.py','')
                if module in sys.modules.keys():
                    #print module, "already imported"
                    sys.modules.pop(module)
                mod = __import__(module)
                yield mod

def write_index(index_files):
    '''
    Args:
        index_files (list of strings)

    writes index.rst in the OUTDIR
    '''

    toc_text = "\n\n"

    start_char = ""

    f = open(os.path.join(KLASS_OUTDIR, "classindex.rst"), "w")
    f.write("Class Index\n")
    f.write("===========\n\n")
    f.write(".. toctree::\n")
    f.write("    :maxdepth: 1\n\n")

    for index in sorted(index_files):
        if index[0] != start_char:
            start_char = index[0]
            f.write("\n")
        f.write("    classes/%s\n"%index)

    f.close()

def main():
    '''
    entry point of the script

    creates a folder of rst_files with contents based on the TEMPLATE
    in location OUTDIR
    '''
    folder = os.path.abspath(sys.argv[1])

    index_files = []
    klass_no, warnings = 0,0
    for mod in get_modules(folder):
        if mod.__name__ == "__init__":
            continue
        for klass in get_class_names(mod):
            out_file = os.path.join(KLASS_SUBDIR, klass+".rst")
            if os.path.exists(out_file):
                if not klass in ("DemoGenerator","SchemaGenerator"):
                    warnings += 1
                    print "WARNING %s - file exists"% out_file
                continue
            klass_no +=1
            f = open(out_file, "w")
            f.write(klass_rst(mod, klass))
            f.close()

            index_files.append(klass + ".rst")

    print "%d Classes found %d WARNINGS"% (klass_no, warnings)
    write_index(index_files)

if __name__ == "__main__":
    import sys

    if len(sys.argv)<2:
        sys.exit('Usage: %s <folder>' % sys.argv[0])

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        sys.exit('%s is nota directory'% folder)

    main()
