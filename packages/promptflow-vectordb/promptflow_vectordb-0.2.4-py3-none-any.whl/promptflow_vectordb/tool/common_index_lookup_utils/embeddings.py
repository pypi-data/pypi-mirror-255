from .constants import IndexTypes, EmbeddingTypes
from .utils import CallbackContext, tool_ui_callback
from promptflow.connections import AzureOpenAIConnection
from typing import Dict, List


def SentenceTransformerIsInstalled() -> bool:
    try:
        from sentence_transformers import SentenceTransformer  # noqa: F401
    except ImportError:
        return False

    return True


@tool_ui_callback
def list_available_embedding_types(context: CallbackContext, index_type: str) -> List[Dict[str, str]]:
    connections = context.ml_client.connections._operation.list(
        workspace_name=context.workspace_name,
        cls=lambda objs: objs,
        category=None,
        **context.ml_client.connections._scope_kwargs)

    workspace_contains_aoai_connection = False
    workspace_contains_oai_connection = False
    for connection in connections:
        if connection.properties.category == 'AzureOpenAI':
            workspace_contains_aoai_connection = True

        if workspace_contains_aoai_connection and workspace_contains_oai_connection:
            break

    embedding_types = []

    # This should be the set of index backends that support embedding-less querying (eg, Keyword).
    # At present, this includes only Azure Cog Search.
    if index_type in {IndexTypes.AzureCognitiveSearch}:
        embedding_types.append({'value': EmbeddingTypes.NoEmbedding, 'displayValue': EmbeddingTypes.NoEmbedding})

    if workspace_contains_aoai_connection:
        embedding_types.append({'value': EmbeddingTypes.AzureOpenAI, 'displayValue': EmbeddingTypes.AzureOpenAI})

    if workspace_contains_oai_connection:
        embedding_types.append({'value': EmbeddingTypes.OpenAI, 'displayValue': EmbeddingTypes.OpenAI})

    if SentenceTransformerIsInstalled():
        embedding_types.append({'value': EmbeddingTypes.HuggingFace, 'displayValue': EmbeddingTypes.HuggingFace})

    return embedding_types


@tool_ui_callback
def list_embedding_models(context: CallbackContext, embedding_type: str) -> List[Dict[str, str]]:
    if embedding_type == EmbeddingTypes.OpenAI:
        return [{'value': 'text-embedding-ada-002', 'display_value': 'text-embedding-ada-002'}]

    if embedding_type == EmbeddingTypes.HuggingFace:
        return [{
            'value': 'sentence-transformers/all-mpnet-base-v2',
            'display_value': 'sentence-transformers/all-mpnet-base-v2'}]

    raise ValueError(f'Unsupported embedding type: {embedding_type}.')


@tool_ui_callback
def list_aoai_embedding_deployments(
        context: CallbackContext,
        aoai_connection: AzureOpenAIConnection
) -> List[Dict[str, str]]:
    selected_connection = context.ml_client.connections._operation.get(
        workspace_name=context.workspace_name,
        connection_name=aoai_connection,
        **context.ml_client.connections._scope_kwargs)

    deployments_url = f'https://management.azure.com{selected_connection.properties.metadata.get("ResourceId")}' +\
        '/deployments?api-version=2023-05-01'
    models_url = f'https://management.azure.com{selected_connection.properties.metadata.get("ResourceId")}' +\
        '/models?api-version=2023-05-01'
    auth_header = f'Bearer {context.credential.get_token("https://management.azure.com/.default").token}'

    deployments_response = context.http.get(deployments_url, headers={'Authorization': auth_header}).json()
    models_response = context.http.get(models_url, headers={'Authorization': auth_header}).json()

    embedding_models =\
        set([f'{mdl.get("name")}:{mdl.get("version")}'
             for mdl in models_response.get('value')
             if mdl.get('capabilities', dict()).get('embeddings', 'false').lower() == 'true'])

    embedding_deployments =\
        [depl
         for depl in deployments_response.get('value')
         if f'{depl.get("properties", dict()).get("model", dict()).get("name")}:'
            f'{depl.get("properties", dict()).get("model", dict()).get("version")}'
         in embedding_models]

    return [{
        'value': depl.get('name'),
        'display_value': depl.get('name'),
    } for depl in embedding_deployments]
