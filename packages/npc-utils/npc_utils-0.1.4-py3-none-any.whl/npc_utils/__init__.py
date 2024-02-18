"""
    Collection of MindScope Neuropixels packages, simplifying installation and keeping versions updated.
"""

import doctest
import importlib.metadata
import logging

# import functions from other packages here:
from npc_ephys import *
from npc_io import *
from npc_lims import *
from npc_mvr import *
from npc_samstim import *
from npc_session import *
from npc_stim import *
from npc_sync import *

logger = logging.getLogger(__name__)

__version__ = importlib.metadata.version("npc_utils")
logger.debug(f"{__name__}.{__version__ = }")


def testmod(**testmod_kwargs) -> doctest.TestResults:  # type: ignore[no-redef]
    """
    Run doctests for the module, configured to ignore exception details and
    normalize whitespace.

    Accepts kwargs to pass to doctest.testmod().

    Add to modules to run doctests when run as a script:
    .. code-block:: text
        if __name__ == "__main__":
            from npc_io import testmod
            testmod()

    """
    _ = testmod_kwargs.setdefault(
        "optionflags", doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    )
    return doctest.testmod(**testmod_kwargs)


if __name__ == "__main__":
    testmod()
