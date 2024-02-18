#===============================================================================
# Manitoba Hydro International / Power Technology Center
# Enerplot Automation Library
#===============================================================================
"""
Manitoba Hydro International

Enerplot Python Automation Library

Connect to already running application::

   import mhi.enerplot
   enerplot = mhi.enerplot.connect()
   enerplot.load_files('myproject')

Launch and connect to new application instance::

   import mhi.enerplot
   enerplot = mhi.enerplot.launch()
   enerplot.load_files('myproject')

Connect to application, launching a new instance if necessary::

   import mhi.enerplot
   enerplot = mhi.enerplot.application()
   enerplot.load_files('myproject')
"""

#===============================================================================
# Version Identifiers
#===============================================================================

VERSION = '2.5.3'
VERSION_HEX = 0x020503f0


#===============================================================================
# Imports
#===============================================================================

import os, sys, logging
from typing import List, Tuple

# Enerplot 1.0 compatibility:
import mhi.common
sys.modules['mhi.enerplot.common'] = sys.modules['mhi.common']


#-------------------------------------------------------------------------------
# Submodules
#-------------------------------------------------------------------------------

from mhi.common.remote import Context #, Remotable #, deprecated
from mhi.common import config

from .application import Enerplot
from .progress import Progress
from .trace import Trace
from .component import Component
from .book import Book, Sheet
from .annotation import Line, TextArea, GroupBox
from .graph import GraphFrame, PlotFrame, FFTFrame, GraphPanel, Curve
from .datafile import DataFile, MutableDataFile, Channel


#===============================================================================
# Logging
#===============================================================================

_LOG = logging.getLogger(__name__)


#===============================================================================
# Options
#===============================================================================

OPTIONS = config.fetch("~/.mhi.enerplot.py")


#===============================================================================
# Connection and Application Start
#===============================================================================

def application():
    """
    This method will find try to find a currently running Enerplot application,
    and connect to it.  If no running Enerplot application can be found, or
    if it is unable to connect to that application, a new Enerplot application
    will be launched and a connection will be made to it.

    If running inside a Python environment embedded within an Enerplot
    application, the containing application instance is always returned.

    Returns:
        Enerplot: The Enerplot application proxy object

    Example::

        import mhi.enerplot
        enerplot = mhi.enerplot.application()
        enerplot.load_files('myproject')
    """

    return Context._application(connect, launch, 'Enerplot%.exe')

def connect(host='localhost', port=None, timeout=5):

    """
    This method will find try to find a currently running Enerplot application,
    and connect to it.

    Parameters:
        host (str): The host the Enerplot application is running on
            (defaults to the local host)

        port (int): The port to connect to.  Required if running multiple
            Enerplot instances.

        timeout (float): Seconds to wait for the connection to be accepted.

    Returns:
        Enerplot: The Enerplot application proxy object

    Example::

        import mhi.enerplot
        enerplot = mhi.enerplot.application()
        enerplot.load_files('myproject')
    """

    if host == 'localhost':
        if not port:
            from mhi.common import process # pylint: disable=import-outside-toplevel

            ports = process.listener_ports_by_name('Enerplot%')
            if not ports:
                raise ProcessLookupError("No availiable Enerplot process")

            addr, port, pid, app = ports[0]
            _LOG.info("%s [%d] listening on %s:%d", app, pid, addr, port)

    _LOG.info("Connecting to %s:%d", host, port)

    return Context._connect(host=host, port=port, timeout=timeout)


def launch(port=None, silence=True, timeout=5, version=None,
           minimum='1.0', maximum=None, allow_alpha=False, allow_beta=False,
           x64=True, **options):

    """
    Launch a new Enerplot instance and return a connection to it.

    Parameters:
        port (int): The port to connect to.  Required if running multiple
            Enerplot instances.

        silence (bool): Suppresses dialogs which can block automation.

        timeout (float): Time (seconds) to wait for the connection to be
            accepted.

        version (str): Specific version to launch if multiple versions present.

        minimum (str): Minimum allowed version to run (default '1.0')

        maximum (str): Maximum allowed  version to run (default: unlimited)

        allow_alpha (bool): Allow launching an "alpha" version of PSCAD.

        allow_beta (bool): Allow launching a "beta" version of PSCAD.

        **options: Additional keyword=value options

    Returns:
        Enerplot: The Enerplot application proxy object

    Example::

        import mhi.enerplot
        enerplot = mhi.enerplot.launch()
        enerplot.load_files('myproject')

    .. versionchanged:: 2.2.1
        added `minimum`, `maximum`, `allow_alpha`, `allow_beta`,
        `x64` parameters.
    """

    from mhi.common import process # pylint: disable=import-outside-toplevel

    options = dict(OPTIONS, **options) if OPTIONS else options

    args = ["{exe}", "/nologo", "/port:{port}"]

    if not options.get('exe', None):
        options['exe'] = process.find_exe('Enerplot', version, x64,
                                          minimum, maximum,
                                          allow_alpha, allow_beta)
        if not options['exe']:
            raise ValueError("Unable to find required version")

    if not port:
        port = process.unused_tcp_port()
        _LOG.info("Automation server port: %d", port)

    process.launch(*args, port=port, **options)

    app = connect(port=port, timeout=timeout)

    if app and silence:
        app.silence = True

    return app

def versions() -> List[Tuple[str, bool]]:
    """
    Find the installed versions of Enerplot

    Returns:
        List[Tuple[str, bool]]: List of tuples of version string and 64-bit flag
    """

    from mhi.common import process # pylint: disable=import-outside-toplevel

    return process.versions('Enerplot')


