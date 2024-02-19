import pandas as pd
import os
import sys
import re
import json
from datetime import time
from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton
from datetime import datetime


from cdh_lava_core.cdc_tech_environment_service import (
    environment_file as cdc_env_file,
)

# Default request time out
REQUEST_TIMEOUT = 180
# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
# Default limit item number of items to retrieve
LIMIT = 500


class SequenceDiagram:
    @staticmethod
    def format_log_entry(log_entry):
        # Convert timestamp to American date-time format
        timestamp = datetime.fromtimestamp(log_entry["Local time"] / 1000).strftime(
            "%Y-%m-%d %I:%M:%S %p"
        )

        # Create the formatted string based on the type of log entry
        if log_entry["type"] == "event":
            return f"{log_entry['ename']}, Duration: {log_entry['duration']} s, Timestamp: {timestamp}"
        else:
            return f"Severity level: {log_entry['severity']}, Message: {log_entry['message']}, Timestamp: {timestamp}"

    @staticmethod
    def extract_name_json(details):
        # Implement your logic to extract name from details
        return details.get("name", "Unknown")

    @staticmethod
    def extract_severity_and_message_and_duration_json(details):
        # Dummy implementation - adjust according to your data structure
        severity = details.get("status", "Unknown")
        start_time = details.get("start_time", "0")
        end_time = details.get("end_time", "0")
        # Convert start_time and end_time from nanoseconds to seconds
        start_time_ns = int(start_time)
        end_time_ns = int(end_time)
        # Divide by 1e9 to convert nanoseconds to seconds
        start_time_seconds = start_time_ns / 1e9
        end_time_seconds = end_time_ns / 1e9
        # Convert seconds to datetime objects
        start_time_human_readable = datetime.fromtimestamp(start_time_seconds)
        end_time_human_readable = datetime.fromtimestamp(end_time_seconds)
        # Calculate duration
        duration = end_time_human_readable - start_time_human_readable

        message = details.get("kind", "No message")
        duration = details.get("duration", 0)  # Example, needs to be defined
        return (
            severity,
            message,
            duration,
            start_time_human_readable,
            end_time_human_readable,
        )

    @staticmethod
    def extract_name(detail):
        """
        Extracts the name from the given detail string.

        Args:
            detail (str): The detail string containing the name.

        Returns:
            str: The extracted name, or an empty string if no match is found.
        """
        match = re.search(r"Name: (\w+),", detail)
        return match.group(1) if match else ""

    @staticmethod
    def extract_severity_and_message_and_duration(detail):
        """
        Extracts the severity, message, and duration from the given detail string.

        Args:
            detail (str): The detail string containing severity, message, and duration information.

        Returns:
            tuple: A tuple containing the severity, message, and duration extracted from the detail string.
        """
        severity_match = re.search(r"Severity level: (\w+)", detail)
        message_match = re.search(r"Message: (.+)", detail)
        duration_match = re.search(r"Duration: (.+)", detail)

        severity = severity_match.group(1) if severity_match else ""
        message = message_match.group(1) if message_match else ""
        duration = duration_match.group(1) if duration_match else ""

        return severity, message, duration

    @staticmethod
    def calculate_duration(current_time, previous_time):
        """
        Calculate the duration between two time values.

        Args:
            current_time (datetime.time): The current time.
            previous_time (datetime.time): The previous time.

        Returns:
            float: The duration in seconds.

        """
        # Handle None inputs
        if current_time is None or previous_time is None:
            return 0.0

        # Convert datetime.time to total seconds since midnight
        current_seconds = (
            current_time.hour * 3600
            + current_time.minute * 60
            + current_time.second
            + current_time.microsecond / 1e6
        )

        prev_seconds = (
            previous_time.hour * 3600
            + previous_time.minute * 60
            + previous_time.second
            + previous_time.microsecond / 1e6
        )

        duration = current_seconds - prev_seconds
        return round(duration, 1)

    @staticmethod
    def convert_time(time_str):
        """
        Converts a time string or numeric value to a `time` object.

        Args:
            time_str (str, float, int): The time string or numeric value to be converted.

        Returns:
            time: The converted `time` object.

        Raises:
            ValueError: If the input `time_str` is of an unsupported type.

        """
        # Handle float or integer inputs
        if isinstance(time_str, (float, int)):
            total_seconds = float(time_str)
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            seconds, microseconds = divmod(seconds, 1)
            microseconds *= 1e6  # Convert fractional seconds to microseconds
            return time(int(hours), int(minutes), int(seconds), int(microseconds))

        # Handle the "0" string case
        if isinstance(time_str, time):
            return time_str
        if time_str == "0":
            return time(0, 0, 0)
        if isinstance(time_str, str):
            return datetime.strptime(time_str, "%M:%S.%f").time()
        else:
            raise ValueError(f"Unsupported type {type(time_str)} for time_str")

    @staticmethod
    def parse_span_data(data_product_id, environment, line):
        """
        Parse the span data from a given line.

        Args:
            line (str): The line containing the span data.

        Returns:
            dict: A dictionary representing the parsed span data.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("parse_span_data"):
            try:
                # Extracting the JSON-like part from each line
                json_str = str(line.split("Span Data: ")[1].strip())

                # Replacing single quotes with double quotes for valid JSON
                json_str = json_str.replace("'", '"')

                # Debugging: print the string being loaded
                logger.info("JSON string being loaded: %s", json_str)

                # Convert the JSON string to a dictionary
                logger.info(f"json_str: {json_str}")
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")
                logger.error(f"Offending string: {json_str}")
                return None  # or raise an error

    @classmethod
    def read_span_data_from_file(cls, data_product_id, environment, file_path):
        """
        Reads span data from a file and returns a list of parsed data.

        Args:
            file_path (str): The path to the file containing the span data.

        Returns:
            list: A list of parsed span data.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("read_span_data_from_file"):
            try:
                parsed_data = []
                line_count = 0
                max_lines = 10000

                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        if line.startswith("Span Data:"):
                            line = line.replace("'", '"')
                            parsed_data.append(
                                cls.parse_span_data(data_product_id, environment, line)
                            )
                            line_count += 1

                            if line_count >= max_lines:
                                logger.warning(
                                    "Warning: File size exceeded 500 lines limit."
                                )
                                break

                parsed_data = [item for item in parsed_data if item is not None]

                return parsed_data

            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Trace Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def read_log_json_txt(cls, data_product_id, environment):
        """
        Read and process log data from a JSON text file.

        Args:
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the log data is collected.

        Returns:
            pandas.DataFrame: A DataFrame containing the processed log data.

        Raises:
            Exception: If an error occurs while reading or processing the log data.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("read_log_json_txt"):
            try:
                log_path = LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).get_log_file_path()
                log_path = str(log_path).replace("logging", "tracing")

                # Split the input into lines and process each line
                data = cls.read_span_data_from_file(
                    data_product_id, environment, log_path
                )

                # Convert the list of dictionaries to a Pandas DataFrame
                df_log_trace = pd.DataFrame(data)
                df_log_trace["name"] = df_log_trace["name"].str.strip()

                # Replace with the actual names you want to exclude
                names_to_exclude = [
                    "parse_span_data",
                    "read_span_data_from_file",
                    "read_log_json_txt",
                    "convert_to_current_os_dir",
                    "convert_to_windows_dir",
                    "convert_to_unix_dir",
                    "get_api_token_from_config",
                    "validate_api_token",
                    "get_api_token",
                    "get",
                    "__init__",
                    "",
                ]
                logger.info(f"names_to_exclude: {names_to_exclude}")
                df_log_trace = df_log_trace[
                    ~df_log_trace["name"].isin(names_to_exclude)
                ]

                # Apply the function to the 'Local time' column
                # records  = df_log_trace.copy().to_dict("records")

                line_count = 0
                max_lines = 1000

                # Assuming df_log_trace is already a DataFrame created from your 'Span Data'
                for index, record in df_log_trace.iterrows():
                    df_log_trace.at[index, "Name"] = cls.extract_name_json(record)
                    (
                        severity,
                        message,
                        duration,
                        start_time_human_readable,
                        end_time_human_readable,
                    ) = cls.extract_severity_and_message_and_duration_json(record)
                    df_log_trace.at[index, "Severity"] = severity
                    df_log_trace.at[index, "Message"] = message
                    df_log_trace.at[index, "Duration"] = duration
                    df_log_trace.at[index, "Start"] = start_time_human_readable
                    df_log_trace.at[index, "End"] = end_time_human_readable
                    line_count += 1

                    if line_count >= max_lines:
                        logger.warning(
                            f"Warning: df_log_trace size exceeded {max_lines} row limit."
                        )
                        break

                df_log_trace = pd.DataFrame(df_log_trace)

                # Drop columns if needed (check if they exist first)
                if "Type" in df_log_trace.columns:
                    df_log_trace.drop(columns=["Type"], inplace=True)

                logger.info(f"df_log_trace: {df_log_trace}")
                return df_log_trace

            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Trace Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def read_log_trace_excel(
        cls,
        data_product_id,
        environment,
        log_path=None,
        file_name="download_manifest_excel.xlsx",
    ):
        """
        Reads a log trace from an Excel file, processes the data, and returns a DataFrame with log traces.

        Args:
            log_path (str, optional): The path to the directory where the Excel log file is located. If not provided,
                                    a default path based on the executing script's directory and the environment
                                    parameter will be constructed.
            environment (str, optional): Specifies the environment under which the log trace file is located.
                                        Default is "dev".
            file_name (str, optional): Name of the Excel file containing the log traces.
                                    Default is "download_manifest_excel.xlsx".

        Returns:
            pd.DataFrame: A DataFrame containing the processed log traces, sorted by 'Local time' and with a
                        computed 'Duration' column in seconds.

        Raises:
            Exception: If an error occurs during the reading or processing of the Excel file.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("read_log_trace"):
            try:
                if log_path is None:
                    # Get the directory of the currently executing script (i.e., the 'tests' folder)
                    tests_directory = os.path.dirname(os.path.abspath(__file__))
                    # Get the parent directory (i.e., the project root)
                    log_path = os.path.dirname(tests_directory)
                    log_path = log_path + "/" + environment + "_log_trace_sequence/"

                obj_file = cdc_env_file.EnvironmentFile()

                right_most_150_chars = file_name[-80:]
                file_name = right_most_150_chars

                log_path = obj_file.convert_to_current_os_dir(
                    log_path, data_product_id, environment
                )

                logger.info("variable: " + log_path)

                log_excel_file = log_path + file_name
                logger.info("log_excel_file: " + log_excel_file)

                # Read the Excel file into a DataFrame from the first sheet
                df_log_trace = pd.read_excel(log_excel_file, sheet_name=0)

                # Apply the function to the 'Local time' column
                df_log_trace["Local time"] = df_log_trace["Local time"].apply(
                    cls.convert_time
                )

                # Sort by 'Local time'
                df_log_trace = df_log_trace.sort_values(by="Local time")

                # Extract name from details
                df_log_trace["Name"] = df_log_trace["Details"].apply(cls.extract_name)

                # Extract severity and messages from details
                (
                    df_log_trace["Severity"],
                    df_log_trace["Message"],
                    df_log_trace["Duration"],
                ) = zip(
                    *df_log_trace["Details"].apply(
                        cls.extract_severity_and_message_and_duration
                    )
                )

                # Drop the 'Type' column
                df_log_trace.drop(columns=["Type"], inplace=True)

                return df_log_trace

            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Excel Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def create_filename_with_timestamp(base_name):
        """
        Creates a filename with a timestamp appended to the base name.

        Args:
            base_name (str): The base name of the file.

        Returns:
            str: The filename with the timestamp appended.
        """
        # Get the current date and time
        now = datetime.now()
        # Format the date and time in a filename-friendly format (e.g., YYYYMMDD_HHMMSS)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        # Append the timestamp to the base filename
        prefix = "cdh_lava_core"
        return f"{prefix}_{base_name}_{timestamp}.txt"  # or another appropriate file extension

    @staticmethod
    def get_first_word(text):
        """
        Returns the first word from a given text string.

        Args:
            text (str): The input text string.

        Returns:
            str or None: The first word from the text string, or None if the text is empty.
        """
        # Split the string into words
        words = text.split()

        # Check if there is at least one word
        if words:
            return words[0]
        else:
            return None  # or some other appropriate value or action

    @classmethod
    def generate_timeline_from_trace_log_json(cls, data_product_id, environment):
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("generate_timeline_from_trace_log_json"):
            try:
                log_path = LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).get_log_file_path()

                log_path = str(log_path).replace("logging", "tracing")
                # Variables to control the call stack level and indentation
                stack = []
                indentation = "  "
                previous_name = None

                # List to store the lines of the timeline
                timeline = []

                df_timeline = cls.read_log_json_txt(data_product_id, environment)
                logger.info(f"df_timeline.columns: {df_timeline.columns}")

                for _, row in df_timeline.iterrows():
                    name = row["Name"]
                    duration = row["Duration"]
                    severity = row["Severity"]
                    message = row["Message"]

                    # Update stack based on call name
                    if name == "__init__":
                        stack.append(name)
                    elif previous_name == "__init__":
                        stack[-1] = name
                    elif name in stack:
                        # If the name is already in the stack, pop names until we find it
                        while stack and stack[-1] != name:
                            stack.pop()
                    else:
                        # If the name is not in the stack, simply add it
                        stack.append(name)

                    # Create the timeline entry
                    indents = len(stack) - 1

                    line = f"{indentation * indents}{name} [{duration}]"
                    if severity and message:
                        line += f" | {severity}: {message}"
                    timeline.append(line)

                    # Update previous name for the next iteration
                    previous_name = name

                content = "\n".join(timeline)
                # Normalize the path to remove any trailing slash
                directory_path = os.path.dirname(log_path)

                base_name = cls.get_first_word(content)
                new_file_name = cls.create_filename_with_timestamp(base_name)
                full_path = os.path.join(directory_path, new_file_name)

                # Open the file at full_path in write mode with utf-8 encoding
                with open(full_path, "w", encoding="utf-8") as file:
                    file.write(content)

                logger.info(f"content: {content}")
                return content

            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Excel Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def generate_timeline_from_excel(
        cls,
        data_product_id,
        environment,
        log_path=None,
        file_name="download_manifest_excel.xlsx",
    ):
        """
        Generates a timeline string based on log trace data from an Excel file.

        This method reads log trace data from an Excel file, sorts it based on the 'Local time' field, and then
        formats each log entry to generate a detailed timeline of events.

        Args:
            log_path (str, optional): The path to the directory where the Excel log file is located. If not provided,
                                    a default path based on the executing script's directory and the environment
                                    parameter will be constructed.
            environment (str, optional): Specifies the environment under which the log trace file is located.
                                        Default is "dev".
            file_name (str, optional): Name of the Excel file containing the log traces.
                                    Default is "download_manifest_excel.xlsx".

        Returns:
            str: A detailed timeline of events based on the log trace data.

        Raises:
            Exception: If an error occurs during the reading or processing of the Excel file or the generation
                    of the timeline.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("generate_timeline_from_excel"):
            try:
                # Variables to control the call stack level and indentation
                stack = []
                indentation = "  "
                previous_name = None

                # List to store the lines of the timeline
                timeline = []

                df_timeline = cls.read_log_trace_excel(
                    data_product_id, environment, log_path, file_name
                )

                # Filter out empty names
                df_timeline = df_timeline[df_timeline["Name"].str.strip().ne("")]

                # Filter out __init__ names
                df_timeline = df_timeline[df_timeline["Name"] != "__init__"]

                # Filter out get names and redundant functions
                df_timeline = df_timeline[df_timeline["Name"] != "get"]
                df_timeline = df_timeline[df_timeline["Name"] != "get_api_token"]
                df_timeline = df_timeline[df_timeline["Name"] != "validate_api_token"]
                df_timeline = df_timeline[
                    df_timeline["Name"] != "get_api_token_from_config"
                ]
                df_timeline = df_timeline[
                    df_timeline["Name"] != "convert_to_windows_dir"
                ]
                df_timeline = df_timeline[
                    df_timeline["Name"] != "convert_to_current_os_dir"
                ]
                df_timeline = df_timeline[df_timeline["Name"] != "convert_to_unix_dir"]
                for _, row in df_timeline.iterrows():
                    name = row["Name"]
                    duration = row["Duration"]
                    severity = row["Severity"]
                    message = row["Message"]

                    # Update stack based on call name
                    if name == "__init__":
                        stack.append(name)
                    elif previous_name == "__init__":
                        stack[-1] = name
                    elif name in stack:
                        # If the name is already in the stack, pop names until we find it
                        while stack and stack[-1] != name:
                            stack.pop()
                    else:
                        # If the name is not in the stack, simply add it
                        stack.append(name)

                    # Create the timeline entry
                    indents = len(stack) - 1

                    line = f"{indentation * indents}{name} [{duration}]"
                    if severity and message:
                        line += f" | {severity}: {message}"
                    timeline.append(line)

                    # Update previous name for the next iteration
                    previous_name = name

                content = "\n".join(timeline)

                new_file_name = file_name.rsplit(".", 1)[0] + ".txt"
                full_path = os.path.join(log_path, new_file_name)

                # Open the file at full_path in write mode with utf-8 encoding
                with open(full_path, "w", encoding="utf-8") as file:
                    file.write(content)

                logger.info(f"content: {content}")
                return content

            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Excel Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def generate_diagram_from_excel(
        cls, data_product_id, environment, log_path, file_name
    ):
        """
        Generates a sequence diagram in Mermaid notation based on log trace data from an Excel file.

        Args:
            log_path (str, optional): The path to the directory where the Excel log file is located. If not provided,
                                    a default path based on the executing script's directory and the environment
                                    parameter will be constructed.
            environment (str, optional): Specifies the environment under which the log trace file is located.
                                        Default is "dev".
            file_name (str, optional): Name of the Excel file containing the log traces.
                                    Default is "download_manifest_excel.xlsx".

        Returns:
            str: A sequence diagram in Mermaid notation based on the log trace data.

        Raises:
            Exception: If an error occurs during the reading or processing of the Excel file or the generation
                    of the diagram.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("generate_diagram_from_excel"):
            try:
                df = cls.read_log_trace_excel(
                    data_product_id, environment, log_path, file_name
                )

                # Process the data to generate Mermaid notation
                participants = df["Name"].unique()
                mermaid_code = "sequenceDiagram\n"
                for participant in participants:
                    mermaid_code += f"participant {participant}\n"

                previous_name = None
                for index, row in df.iterrows():
                    logger.info(f"index:{index}, row: {row}")
                    if previous_name:
                        mermaid_code += f"{previous_name}-->>{row['Name']}: {row['Details'].split(',')[0]}\n"
                        mermaid_code += f"Note right of {row['Name']}: Duration: {row['Duration']} s\n"
                    previous_name = row["Name"]

                logger.info(f"mermaid_code: {mermaid_code}")
                return mermaid_code

            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Excel Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
