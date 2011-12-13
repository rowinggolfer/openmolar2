import gettext
import os

import settings

settings.install()

lang = os.environ.get("LANG")
if lang:
    try:
        AD_SETTINGS.log.debug(
            "trying to install %s as your environment language"% lang)

        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)

    except IOError:
        AD_SETTINGS.log.warning("%s not found, using default"% lang)
        gettext.install('openmolar', unicode=True)
else:
    AD_SETTINGS.log.warning(
        "no language environment found - this should not happen!")
    gettext.install('openmolar', unicode=True)
