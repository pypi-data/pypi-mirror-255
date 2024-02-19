import json
import uuid

import cdc_azure.functions as func

import logging
from shared_code import datalake_helper, app_config, app_utils


def main(msg: func.QueueMessage) -> None:
    msg_body = msg.get_body().decode("utf-8")
    logging.info("[Logging Service] received event  %s", msg_body)
    try:
        process_message(msg_body)
    except Exception as ex:
        logging.error(f"Error processing message {msg_body}. \n \n error: " + str(ex))
        # raise the error so that it bubbles up and causes message to be sent to poison queue.
        # may need a better solution as to where to divert later
        raise


def process_message(msg_body: str):
    msg_json = json.loads(msg_body)

    if msg_json.get("workflow_id") is not None:
        workflow_id = msg_json["workflow_id"]
    else:
        workflow_id = "NO_WORKFLOW_ID"

    if msg_json.get("request_id") is not None:
        request_id = msg_json["request_id"]
    else:
        request_id = "workflow_start"

    if msg_json.get("data_source") is not None:
        data_source = msg_json["data_source"]
    else:
        data_source = "no_data_source"

    save_location = app_config.get_events_save_location(
        data_source, workflow_id=workflow_id
    )

    file_name = f"{request_id}.json"
    if datalake_helper.does_file_exist(file_system=save_location, file_name=file_name):
        datalake_helper.rename_file(
            file_system=save_location,
            file_name=file_name,
            new_name=f"{request_id}_{app_utils.utc_now_formatted_ymd_HMS()}.json",
        )

    datalake_helper.save_file(
        data=msg_body, file_system=save_location, file_name=file_name
    )


# if __name__ == "__main__":
# #     process_message(msg_body=json.dumps({
# #     "data_source": "premier",
# #     "delivery_date": "20221122",
# #     "workflow_id": "8100f73f35954fc4b42d2f3f87f2c1d7"
# # }))
#     msg_json = {
#     "data_source": "premier",
#     "delivery_date": "20221122",
#     "workflow_id": "8100f73f35954fc4b42d2f3f87f2c1d7"
# }
#     config_file_helper.add_event_message_and_save(config_file_name='premier_8100f73f35954fc4b42d2f3f87f2c1d7.json', event_msg_json=msg_json)
