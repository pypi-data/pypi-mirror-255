# def send_email(workflow_file_path: str):
import base64
from datetime import datetime, timedelta
import requests

from shared_code import email_templates, app_config


def send_workflow_status_email(config_json):
    # generate html
    html_template = email_templates.WORKFLOW_STATUS_EMAIL_TEMPLATE
    services = config_json["services"]
    data_source = config_json["datasource"]
    workflow_id = config_json["workflow_id"]
    delivery_date = config_json["delivery_date"]
    started_at = config_json["tracking"]["start_utc"]
    ended_at = config_json["tracking"]["end_utc"]
    wf_status = config_json["tracking"]["status"]
    # config_json["error"]["text"] = error_text
    html_body = ""
    stripe_row = False
    for service in services:
        display_name = service["display_name"]
        target_system = service["target_system"]
        target_resource_name = service["target_resource_name"]
        if service.get("tracking") is not None:
            tracking = service["tracking"]
            status = service["tracking"]["status"]
            start_utc = datetime.strptime(service["tracking"]["start_utc"], "%Y-%m-%dT%H:%M:%SZ")
            if tracking.get("end_utc") is not None:
                end_utc = datetime.strptime(service["tracking"]["end_utc"], "%Y-%m-%dT%H:%M:%SZ")
            else:
                end_utc = datetime.utcnow()

            delta_time = end_utc - start_utc
            total_time = str(timedelta(seconds=delta_time.total_seconds()))
        else:
            status = "UnProcessed"
            total_time = ""

        if stripe_row:
            css_style = "background-color: #f2f2f2;"
            stripe_row = False
        else:
            css_style = ""
            stripe_row = True

        html_body = html_body + f"""<tr style="{css_style}">
                                <td>{target_system}</td>
                                <td>{target_resource_name}</td>
                                <td>{display_name}</td>
                                <td>{total_time}</td>
                                <td>{status}</td>
                              </tr>"""

    email_subject = f"[{app_config.APP_ENVIRONMENT}] ETL completed for data source {data_source}  with status {wf_status}"
    email_body = html_template.replace("#BODY#", html_body) \
        .replace("#DATA_SOURCE#", data_source) \
        .replace("#DELIVERY_DATE#", delivery_date) \
        .replace("#WORKFLOW_ID#", workflow_id) \
        .replace("#LOAD_TYPE#", "TODO") \
        .replace("#STARTED_AT#", started_at) \
        .replace("#ENDED_AT#", ended_at)

    send_email(email_body=email_body, email_subject=email_subject, email_to=app_config.ORCHESTRATION_COMPLETE_EMAIL_TO)


def send_unhandled_error_email(error: str, data_source: str, workflow_id: str):
    email_subject = f"[{app_config.APP_ENVIRONMENT}] {data_source} ERROR - etl."
    email_body = f"<p>Workflow Id #{workflow_id}</p> <p>{error}</p>"
    if app_config.UNHANDLED_ERROR_EMAIL_TO is not None and app_config.UNHANDLED_ERROR_EMAIL_TO != "":
        send_email(email_body=email_body, email_subject=email_subject, email_to=app_config.UNHANDLED_ERROR_EMAIL_TO)


def send_workflow_start_email(data_source: str, workflow_id: str, delivery_date: str,vendor_delivery_location:str,triggerred_by:str):
    email_subject = f"[{app_config.APP_ENVIRONMENT}] ETL Started for data source {data_source}."
    email_body = f"""<p>Data Source: {data_source}</p> 
                     <p>Workflow Id: {workflow_id}</p> 
                     <p>Delivery Date: {delivery_date}</p>
                     <p>Vendor Delivery Location: {vendor_delivery_location}</p>
                     <p>Triggerred By: {triggerred_by}</p>
                     """
    send_email(email_body=email_body, email_subject=email_subject, email_to=app_config.ORCHESTRATION_COMPLETE_EMAIL_TO)


def send_looker_fail_email(file_name: str, error_text: str):
    email_subject = f"[{app_config.APP_ENVIRONMENT}] Looker Service failed to process ready file."
    email_body = f"<p>The file '{file_name}' failed to be processed because of error: {error_text}</p>"
    send_email(email_body=email_body, email_subject=email_subject, email_to=app_config.ORCHESTRATION_COMPLETE_EMAIL_TO)


def send_email(email_body: str, email_subject: str, email_to: str):
    # call logic apps helper
    url = app_config.EMAIL_NOTIFICATION_URL
    message_bytes = email_body.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    json = {
        "emailBody_Base64": base64_message,
        "emailTo": email_to,
        "emailSubject": email_subject
    }
    response = requests.post(url, json=json, headers={"Content-Type": "application/json"})
    if response.ok:
        return
    else:
        print(response.text)
        raise Exception(
            f"Error invoking url at {url}. \n Status_Code: {response.status_code}. Text: {response.text}")
