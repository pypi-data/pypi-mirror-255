# Import from sibling directory ..\databricks_service
from cdh_lava_core.cdc_log_service import environment_tracing
from cdh_lava_core.cdc_log_service import environment_logging
import sys
import os

OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("posit_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("posit_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


__all__ = ["posit_connect", "posit_workbench"]
