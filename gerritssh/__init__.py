__author__ = 'Keith Derrick'
__email__ = 'kderrick_public@att.net'
__version__ = '0.1.0'


class GerritsshException(Exception):
    '''
        Base class for each of the package's exceptions.
    '''
    pass

import logging

# Add a NullHandler to the root logger for the package so that submodules
# can simply use getLogger(__name__). If the logging module does not contain
# a NullHandler, create a dummy one per the documentation.

if 'NullHandler' not in dir(logging):  # pragma: no cover
    # logging.ullHandler does not exist before v2.6 of Python
    class __NullHandler(logging.Handler):  # noqa - inhibit N801
        def emit(self, record):
            pass
    __nullh = __NullHandler()
else:
    __nullh = logging.NullHandler()

logging.getLogger(__name__).addHandler(__nullh)

# Import all the submodules so that their contents are available as
# gerritssh.* rather than gerritssh.<module>.*
#
# All modules define the __all__ attribute making them safe for import *
# but flake8 does not like this construct, so we inhibit qa checking on these
# lines.

from .gerritsite import *  # noqa - inhibit F403
from .query import *  # noqa - inhibit F403
from .review import *  # noqa - inhibit F403
from .lsprojects import *  # noqa - inhibit F403
from .lsgroups import *  # noqa - inhibit F403
from .bancommit import *  # noqa - inhibit F403
