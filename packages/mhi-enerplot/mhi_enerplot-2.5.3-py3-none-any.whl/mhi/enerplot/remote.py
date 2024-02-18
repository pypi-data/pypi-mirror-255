#===============================================================================
# Enerplot Remotable objects
#===============================================================================

"""
Enerplot Remote Proxy
"""


#===============================================================================
# Imports
#===============================================================================

# Allow modules to import rmi, rmi_property and deprecated from here.
# pylint: disable=unused-import
from mhi.common.remote import Remotable as _Remotable
from mhi.common.remote import rmi, rmi_property, deprecated, requires
# pylint: enable=unused-import


#===============================================================================
# PSCAD Remotable
#===============================================================================

class Remotable(_Remotable):            # pylint: disable=too-few-public-methods
    """
    The Remote Proxy
    """
    
    # Treat all derived classes as being in the mhi.pscad module
    _MODULE = "mhi.enerplot"

    @property
    def _enerplot(self) -> "Enerplot":
        return self._context._main            # pylint: disable=protected-access


#===============================================================================
# Typing requires complete types at the end of the module
#===============================================================================

# pylint: disable=wrong-import-order, wrong-import-position, ungrouped-imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .application import Enerplot
