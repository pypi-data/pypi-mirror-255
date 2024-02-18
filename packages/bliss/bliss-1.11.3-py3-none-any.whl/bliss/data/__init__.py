import sys
from bliss.common import deprecation
import blissdata.data as _data

sys.modules["bliss.data"] = _data

deprecation.deprecated_warning(
    "Module",
    "bliss.data",
    replacement="blissdata.data",
    since_version="1.11",
    skip_backtrace_count=100,
)
