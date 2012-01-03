import gettext
import logging
import os

logging.basicConfig(level = logging.INFO)

logging.debug("installing gettext and SETTINGS into __builtins__")
lang = os.environ.get("LANG")
if lang:
    try:
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        logging.debug("trying to install your environment language %s"% lang)
        logging.debug("%s not found, using default"% lang)
        gettext.install('openmolar', unicode=True)
else:
    logging.info("no language environment found")
    gettext.install('openmolar', unicode=True)

from classes import Plugin
import settings
settings.install()

import qrc_resources

__all__ = ["Plugin", "qrc_resources"]