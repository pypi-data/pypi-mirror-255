import json
import uuid

from shared_code import config_file_helper, app_utils, app_config, datalake_helper, workflow_state_store_helper


def process(data_source: str, delivery_date: str, workflow_id: str, file_name: str,vendor_delivery_location:str,triggerred_by:str):
    request_id = uuid.uuid4().hex

    config_file_name = f"{data_source}{app_config.DATAHUB_CONFIGS_FILE_SUFFIX}"
    config_json = datalake_helper.get_json_file(file_system=app_config.DATAHUB_CONFIGS_LOCATION,
                                                file_name=config_file_name)
    if config_json is None:
        raise ValueError(f"Unable to find file {file_name}.")

    delivery_type = config_json["delivery_type"]
    data_manager_email = config_json["data_manager_email"]
    target_database = ""
    if config_json.get("target_database") is not None:
        target_database = config_json["target_database"]

    # add audit entries
    config_json["workflow_id"] = workflow_id
    config_json["delivery_date"] = delivery_date
    config_json["triggerred_by"] = triggerred_by
    config_json["vendor_delivery_location"] = vendor_delivery_location
    config_json["tracking"] = {}
    config_json["tracking"]["status"] = app_config.WORKFLOW_STATUS_RUNNING
    config_json["tracking"]["start_utc"] = app_utils.utc_now_formatted()

    datalake_helper.save_file(data=json.dumps(config_json),
                              file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                              file_name=file_name)

    # get next service
    next_service = config_file_helper.get_next_unprocessed_service(config_json=config_json,
                                                                   request_id=request_id)

    config_file_helper.invoke_next_service(service=next_service,
                                           data_source=data_source,
                                           delivery_date=delivery_date,
                                           workflow_id=workflow_id,
                                           request_id=request_id,
                                           delivery_type=delivery_type,
                                           data_manager_email=data_manager_email,
                                           vendor_delivery_location=vendor_delivery_location,
                                           target_database=target_database)

    datalake_helper.save_file(data=json.dumps(config_json),
                              file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                              file_name=file_name)

    workflow_state_store_helper.upsert_workflow_status(data_source=data_source, workflow_id=workflow_id,
                                                            delivery_date=delivery_date,config_json=config_json)
