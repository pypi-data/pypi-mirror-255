import json
import logging
import uuid

import cdc_azure.functions as func

from handlers import start_workflow_handler
from shared_code import (
    datalake_helper,
    config_file_helper,
    app_config,
    app_utils,
    email_helper,
    storage_queue_helper,
)


def main(msg: func.QueueMessage) -> None:
    msg_body = msg.get_body().decode("utf-8")
    logging.info("[Orchestrator Start] Service received event  %s", msg_body)
    try:
        process_message(msg_body)
    except Exception as ex:
        logging.error(f"Error processing message {msg_body}. \n \n error: " + str(ex))
        file_name = f"unknown_error_{app_utils.utc_now_formatted_ymd_HMS()}.txt"
        config_file_helper.add_error_message_and_save(
            config_file_name=file_name, error_text=str(ex)
        )


def process_message(msg_body: str):
    msg_json = json.loads(msg_body)
    data_source = msg_json["data_source"]
    delivery_date = msg_json["delivery_date"]
    workflow_id = uuid.uuid4().hex
    vendor_delivery_location = ""
    triggerred_by = ""

    if msg_json.get("vendor_delivery_location") is None:
        msg_json["vendor_delivery_location"] = ""
    else:
        vendor_delivery_location = msg_json["vendor_delivery_location"]

    if msg_json.get("workflow_id") is not None:
        workflow_id = msg_json["workflow_id"]
    else:
        msg_json["workflow_id"] = workflow_id

    if msg_json.get("triggerred_by") is not None:
        triggerred_by = msg_json["triggerred_by"]

    file_name = f"{data_source}_{workflow_id}.json"

    storage_queue_helper.send_message_to_queue(
        queue_name=app_config.QUEUE_OBSERVABILITY_LOGGING_NAME,
        message=json.dumps(msg_json),
    )

    try:
        email_helper.send_workflow_start_email(
            data_source=data_source,
            workflow_id=workflow_id,
            delivery_date=delivery_date,
            vendor_delivery_location=vendor_delivery_location,
            triggerred_by=triggerred_by,
        )

        start_workflow_handler.process(
            data_source=data_source,
            delivery_date=delivery_date,
            workflow_id=workflow_id,
            file_name=file_name,
            vendor_delivery_location=vendor_delivery_location,
            triggerred_by=triggerred_by,
        )

    except Exception as ex:
        logging.error(f"Error processing message {msg_body}. \n \n error: " + str(ex))
        config_file_helper.add_error_message_and_save(
            config_file_name=file_name, error_text=str(ex)
        )
        email_helper.send_unhandled_error_email(
            error=str(ex), data_source=data_source, workflow_id=workflow_id
        )


# if __name__ == "__main__":
#     workflow_id = uuid.uuid4().hex
#     process_message(msg_body=json.dumps({
#         "data_source": "demo_integration_test",
#         "delivery_date": "20221122",
#         "workflow_id": workflow_id
#     }))
#     msg_json = {
#     "data_source": "premier",
#     "delivery_date": "20221122",
#     "workflow_id": "8100f73f35954fc4b42d2f3f87f2c1d7"
# }
#     config_file_helper.add_event_message_and_save(config_file_name='premier_8100f73f35954fc4b42d2f3f87f2c1d7.json', event_msg_json=msg_json)
