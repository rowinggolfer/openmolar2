import gettext, os

lang = os.environ.get("LANG")
if lang:
    try:
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        print "trying to install your environment language", lang
        print "%s not found, using default"% lang
        gettext.install('openmolar', unicode=True)
else:
    print "no language environment found"
    gettext.install('openmolar', unicode=True)
