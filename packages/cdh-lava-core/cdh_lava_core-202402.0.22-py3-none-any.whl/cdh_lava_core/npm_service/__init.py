"""Initialize the npm_service subpackage of cdh_lava_core package"""

import sys
import os

OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("npm_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("npm_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))

from cdh_lava_core.npm_service import npm_client

__all__ = ["npm_client"]
