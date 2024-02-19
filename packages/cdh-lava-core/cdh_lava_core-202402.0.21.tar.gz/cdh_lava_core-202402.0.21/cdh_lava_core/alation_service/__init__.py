"""Initialize the alation_service subpackage of cdh_lava_core package"""
# allow absolute import from the root folder
# whatever its name is.
# from cdh_lava_core.az_storage_service import az_storage_queue
import sys  # don't remove required for error handling
import os
from cdh_lava_core.cdc_log_service import environment_tracing
from cdh_lava_core.cdc_log_service import environment_logging


# Import from sibling directory ..\databricks_service
OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))

__all__ = [
    "custom_fields",
    "datasource",
    "db_column",
    "db_schema",
    "db_table",
    "endpoint",
    "excel_manifest",
    "execution_session",
    "id_finder",
    "json_manifest",
    "query",
    "tags",
    "token",
]
