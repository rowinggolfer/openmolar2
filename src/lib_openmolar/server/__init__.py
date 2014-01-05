import gettext, os

lang = os.environ.get("LANG")
if lang:
    try:
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        gettext.install('openmolar', unicode=True)
else:
    gettext.install('openmolar', unicode=True)
