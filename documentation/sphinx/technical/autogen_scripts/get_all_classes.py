#!/usr/bin/env python

'''
A module which pulls classes from all modules found walking
the directory (given as sys.argv[1])
'''

import inspect
import os, sys

def determine_path ():
    """Borrowed from wxglade.py"""
    root = __file__
    if os.path.islink (root):
        root = os.path.realpath (root)
    retarg = os.path.dirname (os.path.abspath (root))
    return retarg

path_ = determine_path()

technical_path = os.path.split(path_)[0]
KLASS_OUTDIR = os.path.join(technical_path, "classes")
KLASS_SUBDIR = os.path.join(KLASS_OUTDIR, "classes")

if not os.path.exists(KLASS_OUTDIR):
    os.mkdir(KLASS_OUTDIR)

if not os.path.exists(KLASS_SUBDIR):
    os.mkdir(KLASS_SUBDIR)

def remove_null_klass_rst_files():
    print "REMOVING ALL NULL rst files from class_headings directory"
    headings_path = os.path.join(technical_path, "class_headings")
    for root, dir_, files in os.walk(technical_path):
        for file_ in files:
            filepath = os.path.abspath(os.path.join(root, file_))
            if os.stat(filepath).st_size == 0:
                print "removing %s"% filepath
                os.remove(filepath)
    print "Done\n"

def klass_rst(module, klass):
    '''
    returns file contents understood by sphinx.
    eg.

    Advisor
    -------
    .. module:: lib_openmolar.common.qt4.widgets
        rst from the modules docstring
    .. autoclass:: lib_openmolar.common.qt4.widgets.Advisor
        :members:
        :undoc-members:
        :show-inheritance:

        .. automethod:: lib_openmolar.common.qt4.widgets.Advisor.__init__

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

def get_class_names(module):
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
        (obj.__module__ == module.__name__ and obj.__name__[0] != "_")):
            yield name

def get_modules(folder):
    '''
    Args:
        folder (string)

    returns a list of all python modules found under folder *folder*
    '''
    for root, dir_, files in os.walk(folder, followlinks=True):
        sys.path.insert(0, root)
        for file_ in files:
            if file_.endswith(".py"):
                module = file_.replace('.py','')
                if module == "__init__":
                    continue
                if module in sys.modules.keys():
                    #print module, "already imported"
                    sys.modules.pop(module)
                #print "importing", module, "from", root
                mod = __import__(module)
                yield mod

def write_index(rst_files):
    '''
    Args:
        index_files (list of strings)

    writes index.rst in the OUTDIR
    '''

    f = open(os.path.join(KLASS_OUTDIR, "classindex.rst"), "w")
    f.write('''Classes
=======

..note ::
    Openmolar is almost entirely Object orientated, and so it makes sense to
    structure this documentation by classes, not modules.

If you are looking for a full list of classes in alphabetical order::
    - :doc:`all_classes`

Otherwise, for the sake of readability of the documentation, classes are gathered into packages::
    - Common
    - Client
    - Admin
    - Server

.. toctree::
    :maxdepth: 2

    common_classes
    client_classes
    admin_classes
    server_classes\n\n''')
    f.close()

    f = open(os.path.join(KLASS_OUTDIR, "all_classes.rst"), "w")
    f.write("Complete Class Index\n")
    f.write("====================\n\n")
    f.write(".. toctree::\n")
    f.write("    :maxdepth: 1\n\n")

    start_char = ""

    for rst_file, module in sorted(rst_files):
        link = "    classes/%s\n"% rst_file
        if rst_file[0] != start_char:
            start_char = rst_file[0]
            f.write("\n")

        f.write(link)
    f.close()

    for package in ["admin", "common", "client", "server"]:
        f = open(os.path.join(KLASS_OUTDIR, "%s_classes.rst"% package), "w")
        header = "%s%s Classes"% (package[0].upper(), package[1:])
        f.write("%s\n"% header)
        f.write("%s\n\n"% ("="*len(header)))
        f.write(".. toctree::\n")
        f.write("    :maxdepth: 1\n\n")

        for rst_file, module in sorted(rst_files):
            if "lib_openmolar/%s"% package in module:
                link = "    classes/%s\n"% rst_file
                f.write(link)

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
        for klass in get_class_names(mod):
            out_file = os.path.join(KLASS_SUBDIR, klass+".rst")
            if os.path.exists(out_file):
                if not klass in ("DemoGenerator"):
                    warnings += 1
                    print "WARNING %s - file exists"% out_file
                continue
            klass_no +=1
            f = open(out_file, "w")
            f.write(klass_rst(mod, klass))
            f.close()

            index_files.append((klass + ".rst", mod.__file__))

    print "%d Classes found %d WARNINGS"% (klass_no, warnings)
    write_index(index_files)

if __name__ == "__main__":

    remove_null_klass_rst_files()
    if len(sys.argv)<2:
        sys.exit('Usage: %s <folder>' % sys.argv[0])

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        sys.exit('%s is not a directory'% folder)

    main()
