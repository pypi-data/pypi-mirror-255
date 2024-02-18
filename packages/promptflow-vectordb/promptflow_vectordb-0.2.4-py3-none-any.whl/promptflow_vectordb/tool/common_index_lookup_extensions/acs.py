import json
from langchain.docstore.document import Document
from langchain.vectorstores import AzureSearch
from typing import Dict, List, Optional, Tuple


def simple_search_with_score(
        query: str,
        store: AzureSearch,
        k: int = 4,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    from langchain.vectorstores.azuresearch import (
        FIELDS_CONTENT,
        FIELDS_CONTENT_VECTOR,
        FIELDS_METADATA,
    )

    results = store.client.search(
        search_text=query,
        query_type='simple',
        filter=filters,
        top=k,
    )

    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=result.pop(FIELDS_CONTENT),
                metadata=json.loads(result[FIELDS_METADATA])
                if FIELDS_METADATA in result
                else {
                    k: v for k, v in result.items() if k != FIELDS_CONTENT_VECTOR
                },
            ),
            float(result['@search.score']),
        )
        for result in results
    ]

    return docs


def semantic_search_with_score(
        query: str, store:
        AzureSearch,
        k: int = 4,
        hybrid: bool = False,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    from langchain.vectorstores.azuresearch import (
        FIELDS_CONTENT,
        FIELDS_CONTENT_VECTOR,
        FIELDS_METADATA,
    )

    if hybrid:
        from azure.search.documents.models import Vector
        import numpy as np
        results = store.client.search(
            search_text=query,
            vectors=[
                Vector(
                    value=np.array(
                        store.embedding_function(query), dtype=np.float32
                    ).tolist(),
                    k=50,
                    fields=FIELDS_CONTENT_VECTOR,
                )
            ],
            filter=filters,
            query_type='semantic',
            query_language=store.semantic_query_language,
            semantic_configuration_name=store.semantic_configuration_name,
            query_caption='extractive',
            query_answer='extractive',
            top=k,
        )
    else:
        results = store.client.search(
            search_text=query,
            filter=filters,
            query_type='semantic',
            query_language=store.semantic_query_language,
            semantic_configuration_name=store.semantic_configuration_name,
            query_caption='extractive',
            query_answer='extractive',
            top=k,
        )

    # Get Semantic Answers
    semantic_answers = results.get_answers() or []
    semantic_answers_dict: Dict = {}
    for semantic_answer in semantic_answers:
        semantic_answers_dict[semantic_answer.key] = {
            'text': semantic_answer.text,
            'highlights': semantic_answer.highlights,
        }

    docs = [
        (
            Document(
                page_content=result.pop(FIELDS_CONTENT),
                metadata={
                    **(
                        json.loads(result[FIELDS_METADATA])
                        if FIELDS_METADATA in result
                        else {
                            k: v
                            for k, v in result.items()
                            if k != FIELDS_CONTENT_VECTOR
                        }
                    ),
                    **{
                        'captions': {
                            'text': result.get('@search.captions', [{}])[0].text,
                            'highlights': result.get('@search.captions', [{}])[
                                0
                            ].highlights,
                        }
                        if result.get('@search.captions')
                        else {},
                        'answers': semantic_answers_dict.get(
                            json.loads(result['metadata']).get('key'), ''
                        )
                        if result.get('metadata')
                        else {},
                    },
                },
            ),
            float(result['@search.score']),
        )
        for result in results
    ]

    return docs
