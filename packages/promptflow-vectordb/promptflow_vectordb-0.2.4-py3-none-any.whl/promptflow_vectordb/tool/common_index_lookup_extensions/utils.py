from .acs import simple_search_with_score, semantic_search_with_score

from ..common_index_lookup_utils.constants import QueryTypes

from azureml.rag import MLIndex
import functools
from langchain.docstore.document import Document
from langchain.vectorstores import AzureSearch
from typing import Callable, List, Tuple


def build_search_func(index: MLIndex, top_k: int, query_type: str) -> Callable[[str], List[Tuple[Document, float]]]:
    # Override the embeddings section if we're making keyword queries.
    if query_type in {QueryTypes.Simple, QueryTypes.Semantic}:
        index.embeddings_config = {
            'schema_version': '2',
            'kind': 'none'
        }

        # Temporary workaround for `as_langchain_vectorstore` throwing when field_mapping.embedding is None.
        if 'field_mapping' in index.index_config:
            index.index_config['field_mapping']['embedding'] = ''

    store = index.as_langchain_vectorstore()

    if query_type == QueryTypes.Simple:
        return functools.partial(simple_search_with_score, store=store, k=top_k)

    if query_type == QueryTypes.Semantic:
        return functools.partial(semantic_search_with_score, store=store, k=top_k, hybrid=False)

    if query_type == QueryTypes.Vector:
        if isinstance(store, AzureSearch):
            # AzureSearch doesn't implement similiarity_search_with_score
            return functools.partial(store.vector_search_with_score, k=top_k)
        else:
            return functools.partial(store.similarity_search_with_score, k=top_k)

    if query_type == QueryTypes.VectorSimpleHybrid:
        return functools.partial(store.hybrid_search_with_score, k=top_k)

    if query_type == QueryTypes.VectorSemanticHybrid:
        return functools.partial(semantic_search_with_score, store=store, k=top_k, hybrid=True)

    raise ValueError(f'Unsupported query type: {query_type}')
