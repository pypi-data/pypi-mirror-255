WORKFLOW_STATUS_EMAIL_TEMPLATE = """
<div>
    <h2>#DATA_SOURCE# datasource</h2>
    <p>
        <ul>
        <li>Workflow: #WORKFLOW_ID#</li>
        <li>Delivery Date: #DELIVERY_DATE#</li>
        <li>Load Type: #LOAD_TYPE# </li>
        <li>Started At: #STARTED_AT# </li>
        <li>Ended At: #ENDED_AT# </li>
    </ul></p>

<table role="presentation" border="1" width="100%">
  <tr>
    <th>Type</th>
    <th>Resource</th>
    <th>Description</th>
    <th>Duration (HH:mm:ss)</th>
    <th>Status</th>
  </tr>
  #BODY#
</table>

</div>
"""
