import os
import sys
import subprocess
from subprocess import check_output, Popen, PIPE, CalledProcessError

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class PoetryClient:
    """
    A client for interacting with the Poetry library.

    This class provides methods for working with the Poetry library, such as printing the version of the library.

    Attributes:
        None
    """

    @classmethod
    def print_version(cls) -> str:
        """Prints version of library

        Returns:
            str: version of library
        """

        print_version_command = ["poetry", "version"]
        print_version_command_string = " ".join(print_version_command)
        print(print_version_command_string)
        current_working_dir = os.getcwd()
        print_version_result = f"current_working_dir:{current_working_dir}"
        try:
            print_version_result = check_output(print_version_command)
            print_version_result = (
                f"{str(print_version_result)}:{print_version_command_string} succeeded"
            )
        except subprocess.CalledProcessError as ex_called_process:
            error_string = ex_called_process.output
            print_version_result = str(print_version_result)
            if error_string is None:
                new_error_string = (
                    f": {print_version_command_string} succeeded with Exception"
                )
                print_version_result = print_version_result + new_error_string

            else:
                print_version_result = print_version_result + f"Error: {error_string}"

        print_version_result = str(print_version_result)
        print(print_version_result)
        return print_version_result
