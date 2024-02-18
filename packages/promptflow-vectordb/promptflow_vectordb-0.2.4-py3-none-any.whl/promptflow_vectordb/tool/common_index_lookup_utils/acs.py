from .utils import CallbackContext, tool_ui_callback
from promptflow.connections import CognitiveSearchConnection
from typing import Dict, List


@tool_ui_callback
def list_acs_indices(context: CallbackContext, acs_connection: CognitiveSearchConnection) -> List[Dict[str, str]]:
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=acs_connection,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{context.arm_id}' +\
        f'/connections/{selected_connection.name}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token("https://management.azure.com/.default").token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
    api_key = secrets_response.get('properties', dict()).get('credentials', dict()).get('key')

    api_version = selected_connection.properties.metadata.get('ApiVersion', '2023-03-15-preview')
    indexes_response = context.http.get(
        f'{selected_connection.properties.target}/indexes?api-version={api_version}',
        headers={'api-key': api_key}).json()

    return [{
        'value': index.get('name'),
        'display_value': index.get('name')} for index in indexes_response.get('value', [])]


@tool_ui_callback
def list_acs_index_fields(
        context: CallbackContext,
        acs_connection: CognitiveSearchConnection,
        acs_index_name: str,
        field_data_type: str
) -> List[Dict[str, str]]:
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=acs_connection,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{context.arm_id}' +\
        f'/connections/{selected_connection.name}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token("https://management.azure.com/.default").token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
    api_key = secrets_response.get('properties', dict()).get('credentials', dict()).get('key')

    api_version = selected_connection.properties.metadata.get('ApiVersion', '2023-03-15-preview')
    selected_index = context.http.get(
        f'{selected_connection.properties.target}/indexes/{acs_index_name}?api-version={api_version}',
        headers={'api-key': api_key}).json()

    return [{
        'value': field.get('name'),
        'display_value': field.get('name')}
        for field in selected_index.get('fields', []) if field.get('type') == field_data_type]


@tool_ui_callback
def list_acs_index_semantic_configurations(
        context: CallbackContext,
        acs_connection: CognitiveSearchConnection,
        acs_index_name: str
) -> List[Dict[str, str]]:
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=acs_connection,
        **context.ml_client.connections._scope_kwargs)

    url = f'https://management.azure.com{context.arm_id}' +\
        f'/connections/{selected_connection.name}/listSecrets?api-version=2022-01-01-preview'
    auth_header = f'Bearer {context.credential.get_token("https://management.azure.com/.default").token}'

    secrets_response = context.http.post(url, headers={'Authorization': auth_header}).json()
    api_key = secrets_response.get('properties', dict()).get('credentials', dict()).get('key')

    api_version = selected_connection.properties.metadata.get('ApiVersion', '2023-03-15-preview')
    selected_index = context.http.get(
        f'{selected_connection.properties.target}/indexes/{acs_index_name}?api-version={api_version}',
        headers={'api-key': api_key}).json()

    configurations = selected_index.get('semantic', {}).get('configurations', [])
    return [{'value': configuration.get('name')} for configuration in configurations]
