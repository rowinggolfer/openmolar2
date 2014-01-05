import __builtin__
import gettext
import logging
import os

import settings

logging.basicConfig(level = logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s')

try:
    LOGGER.warning('''
        Abandoned a second attempt to install LOGGER into globals
        THIS SHOULD NOT HAPPEN!!
        perhaps code is being imported from both admin and client?''')
except NameError:
    LOGGER = logging.getLogger("openmolar-client")
    __builtin__.LOGGER = LOGGER

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

settings.install()

import qrc_resources

__all__ = ["Plugin", "qrc_resources"]