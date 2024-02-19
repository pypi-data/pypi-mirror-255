"""Initialize the cdc_log_service subpackage of cdh_lava_core package"""
# allow absolute import from the root folder
# whatever its name is.
import sys  # don't remove required for error handling
import os
import cdh_lava_core.cdc_log_service.environment_tracing
import cdh_lava_core.cdc_log_service.environment_logging
import cdh_lava_core.cdc_log_service.sequence_diagram

# Import from sibling directory ..\databricks_service
OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("cdc_log_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("cdc_log_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


__all__ = ["environment_logging", "environment_tracing", "sequence_diagram"]
