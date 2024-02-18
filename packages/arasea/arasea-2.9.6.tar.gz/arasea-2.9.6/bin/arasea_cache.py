#!/usr/bin/env python

import warnings

from arasea.bin.arasea_cache import *
from arasea.bin.arasea_cache import _logger

if __name__ == "__main__":
    warnings.warn(
        message= "Running 'arasea_cache.py' is deprecated. Use the arasea-cache "
        "script instead.",
        category=DeprecationWarning,
    )
    main()
