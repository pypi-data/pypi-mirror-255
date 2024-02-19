# Import from sibling directory ..\databricks_service

import sys
import os

OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("github_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("github_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))

import cdh_lava_core.github_service.github_secret
import cdh_lava_core.github_service.github_release
import cdh_lava_core.github_service.github_issue


__all__ = ["github_secret", "github_release", "github_issue"]
