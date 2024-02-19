import json
import logging

import cdc_azure.functions as func

from handlers import update_workflow_handler
from shared_code import (
    config_file_helper,
    app_config,
    datalake_helper,
    email_helper,
    app_utils,
    storage_queue_helper,
)


def main(msg: func.QueueMessage) -> None:
    msg_body = msg.get_body().decode("utf-8")
    logging.info("[Orchestrator Update] Service received event  %s", msg_body)
    process_message(msg_body)


def process_message(msg_body: str):
    msg_json = json.loads(msg_body)
    data_source = msg_json["data_source"]
    # delivery_date = msg_json['delivery_date']
    workflow_id = msg_json["workflow_id"]
    request_id = msg_json["request_id"]
    status = msg_json["status"]
    prev_service_output = None
    file_name = f"{data_source}_{workflow_id}.json"
    try:
        # does file exist?
        if not datalake_helper.does_file_exist(
            file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY, file_name=file_name
        ):
            fail_file_name = (
                f"{data_source}_{workflow_id}_{app_config.WORKFLOW_STATUS_FAILED}.json"
            )
            if datalake_helper.does_file_exist(
                file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                file_name=fail_file_name,
            ):
                datalake_helper.rename_file(
                    file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                    file_name=fail_file_name,
                    new_name=file_name,
                )
            else:
                fail_file_name = f"{data_source}_{workflow_id}_{app_config.WORKFLOW_STATUS_PENDING_APPROVAL}.json"
                if datalake_helper.does_file_exist(
                    file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                    file_name=fail_file_name,
                ):
                    datalake_helper.rename_file(
                        file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                        file_name=fail_file_name,
                        new_name=file_name,
                    )

        storage_queue_helper.send_message_to_queue(
            queue_name=app_config.QUEUE_OBSERVABILITY_LOGGING_NAME, message=msg_body
        )

        if msg_json.get("event_time_utc") is not None:
            event_time_utc: str = msg_json["event_time_utc"]
        else:
            event_time_utc = app_utils.utc_now_formatted()

        update_workflow_handler.process(
            data_source=data_source,
            workflow_id=workflow_id,
            request_id=request_id,
            status=status,
            file_name=file_name,
            event_time_utc=event_time_utc,
        )
    except Exception as ex:
        ex_formatted = app_utils.exception_to_string(ex)
        logging.error(
            f"Error processing message {msg_body}. \n \n error: " + ex_formatted
        )
        config_file_helper.add_error_message_and_save(
            config_file_name=file_name, error_text=ex_formatted
        )
        email_helper.send_unhandled_error_email(
            error=ex_formatted, data_source=data_source, workflow_id=workflow_id
        )


# if __name__ == "__main__":
#     file_name = f"premier_4f7967e62b194a2981f9fad588e85208.json"
#     process_message(
#         """
#      {
#     "data_source": "demo_integration_test",
#     "workflow_id": "faf3cd939e164336bcd4989cc8564544",
#     "request_id": "5e4395c03d0e4131b65d632aa040e54d",
#     "event_source": "looker-svc",
#     "event_time_utc": "2023-03-17T13:15:25Z",
#     "status": "Rerun"
# }
#         """)
# update_workflow_handler.process(data_source="premier",
#                                 workflow_id="4f7967e62b194a2981f9fad588e85208",
#                                 request_id="8be4ca369ac24f74a5705b14be327ede",
#                                 status="Success",
#                                 file_name=file_name,
#                                 event_time_utc="2022-12-16T03:05:30Z")
