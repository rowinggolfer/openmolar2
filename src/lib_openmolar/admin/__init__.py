import gettext
import os

import settings
import admin_logger

admin_logger.install()
settings.install()

lang = os.environ.get("LANG")
if lang:
    try:
        LOGGER.debug(
            "trying to install %s as your environment language"% lang)

        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)

    except IOError:
        LOGGER.warning("%s not found, using default"% lang)
        gettext.install('openmolar', unicode=True)
else:
    LOGGER.warning(
        "no language environment found - this should not happen!")
    gettext.install('openmolar', unicode=True)
