"""
This module handles the system-specific function for 'jira_service'.

The module also includes environment tracing and logging from the 'cdc_log_service' package. Depending on the operating system (OS), it configures the paths to these directories differently, with specific paths for Windows (nt) and non-Windows systems.

The 'os' and 'sys' libraries are utilized to manage OS interactions and system-specific parameters.

Exports:
    - jira_client: A client interface for interaction with Jira.

Dependencies:
    - cdc_log_service: This sibling package provides environment tracing and logging capabilities.

Note: 
- The paths to the necessary resources and modules are added to the Python path at runtime, 
  using '\\' as a path delimiter for Windows and '/' for non-Windows systems.
- The term "nt" in Python identifies any Windows system and stands for "New Technology".

"""

from cdh_lava_core.cdc_log_service import environment_tracing
from cdh_lava_core.cdc_log_service import environment_logging
import sys
import os

OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("jira_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(
        os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("jira_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


__all__ = ["jira_client"]
