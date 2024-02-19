import openai
import os

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import environment_file as cdc_env_file

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class TextCompletion:
    """
    A class used to represent a Text Completion mechanism using OpenAI's GPT-3.

    This class provides a method to generate a descriptive data dictionary for a database table
    using the OpenAI GPT-3 model. This is a static method, meaning it can be called without
    needing to create an instance of the class.

    ...

    Attributes
    ----------
    No class attributes.

    Methods
    -------
    create_data_dictionary_for_table(gpt_api_key, table_name, columns) -> str:
        Generates a descriptive data dictionary for a database table.

    """

    @staticmethod
    def create_docstring_for_table(
        gpt_api_key, table_name, columns, data_product_id, environment
    ):
        """
        Function to create a descriptive data dictionary for a table.

        Parameters:
        table_name (str): Name of the table.
        columns (list): List of column definitions (column name and type).

        Returns:
        str: Generated description of the data dictionary.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_docstring_for_table"):
            openai.api_key = gpt_api_key

            prompt = f"Create a descriptive docstring for a table named '{table_name}' with the following columns: {', '.join(columns)}.  Provide a table summary docstring in addition to individual columns. Include a user friendly title that displays the table name formatted for optimal readability labeled title in addittion to the table name labeled name."
            logger.info(f"Prompt: {prompt}")
            logger.info(f"api_key_length: {len(openai.api_key)}")

            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0.5,
                max_tokens=200,
            )

            prompt_response = response.choices[0].text.strip()
            return prompt_response
