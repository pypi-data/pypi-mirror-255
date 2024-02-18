from .constants import IndexTypes
from .mlindex_client import MLIndexClient
from .utils import CallbackContext, tool_ui_callback
from typing import Dict, List


@tool_ui_callback
def list_available_index_types(context: CallbackContext) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs)

    mlindex_client = MLIndexClient(context)
    registered_indices = mlindex_client.list_indices()

    workspace_contains_acs_connection = False
    workspace_contains_pinecone_connection = False

    for connection in connections:
        if connection.properties.category == "CognitiveSearch":
            workspace_contains_acs_connection = True
        if connection.properties.category == "CustomKeys" and \
                'environment' in connection.properties.metadata and 'project_id' in connection.properties.metadata:
            workspace_contains_pinecone_connection = True

        if workspace_contains_acs_connection and workspace_contains_pinecone_connection:
            break

    index_options = []

    if len([index for index in registered_indices if index.status == 'Ready']) > 0:
        index_options.append({
            'value': IndexTypes.MLIndexAsset,
        })

    if workspace_contains_acs_connection:
        index_options.append({
            'value': IndexTypes.AzureCognitiveSearch,
        })

    index_options.append({
        'value': IndexTypes.FAISS,
    })

    if workspace_contains_pinecone_connection:
        index_options.append({
            'value': IndexTypes.Pinecone,
        })

    index_options.append({
        'value': IndexTypes.MLIndexPath,
    })

    return index_options
