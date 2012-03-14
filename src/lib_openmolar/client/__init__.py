import __builtin__
import gettext
import logging
import os

logging.basicConfig(level = logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s')

LOGGER = logging.getLogger("openmolar-client")
__builtin__.__dict__["LOGGER"] = LOGGER

LOGGER.debug("installing gettext and SETTINGS into __builtins__")

lang = os.environ.get("LANG")
if lang:
    try:
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        LOGGER.debug("trying to install your environment language %s"% lang)
        LOGGER.debug("%s not found, using default"% lang)
        gettext.install('openmolar', unicode=True)
else:
    LOGGER.info("no language environment found")
    gettext.install('openmolar', unicode=True)

import settings
settings.install()

import qrc_resources

__all__ = ["Plugin", "qrc_resources"]