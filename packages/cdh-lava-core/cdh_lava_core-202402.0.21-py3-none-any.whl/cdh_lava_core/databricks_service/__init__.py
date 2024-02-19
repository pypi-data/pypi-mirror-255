"""Initialize the alation_service subpackage of cdh_lava_core package"""

# allow absolute import from the root folder
# whatever its name is.
# from cdh_lava_core.az_storage_service import az_storage_queue


import sys  # don't remove required for error handling
import os


# Import from sibling directory ..\databricks_service
OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("cdc_metadata_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("cdc_metadata_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))

__all__ = [
    "database",
    "dataset_convert",
    "dataset_core",
    "dataset_crud",
    "dataset_extract",
    "notebook",
    "repo_core",
    "dbx_secret_scope",
    "cluster",
    "sql",
    "dbx_db_rest",
    "dbx_rest",
    "dbx_workspace",
]
