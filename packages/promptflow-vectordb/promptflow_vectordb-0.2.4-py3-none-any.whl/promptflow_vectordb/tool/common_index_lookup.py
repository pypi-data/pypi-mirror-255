from .utils.profiling import measure_execution_time
from .common_index_lookup_extensions import build_search_func

from azureml.rag.mlindex import MLIndex
from azureml.rag.utils.logging import enable_stdout_logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import logging
import os
from promptflow import tool
from ruamel.yaml import YAML
from typing import List, Union

yaml = YAML()

search_executor = ThreadPoolExecutor()

__LOG_LEVEL_ENV_KEY = 'PF_LOGGING_LEVEL'
try:
    __LOG_LEVEL_MAPPINGS = logging.getLevelNamesMapping()
except AttributeError:
    # logging.getLevelNamesMapping was only introduced in 3.11; fallback for older versions
    __LOG_LEVEL_MAPPINGS = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }


@lru_cache(maxsize=32)
def _get_search_func(mlindex_content: str, top_k: int, query_type: str):
    with measure_execution_time('search_function_construction'):
        mlindex_config = yaml.load(mlindex_content)
        index = MLIndex(mlindex_config=mlindex_config)
        return build_search_func(index, top_k, query_type)


@lru_cache(maxsize=1)
def _set_log_level(log_level):
    enable_stdout_logging(log_level)

    root = logging.getLogger()
    root.setLevel(log_level)


@tool
def search(
    mlindex_content: str,
    queries: Union[str, List[str]],
    top_k: int,
    query_type: str,
) -> List[List[dict]]:
    log_level = __LOG_LEVEL_MAPPINGS.get(os.getenv(__LOG_LEVEL_ENV_KEY), logging.INFO)
    _set_log_level(log_level)

    search_func = _get_search_func(mlindex_content, top_k, query_type)

    if isinstance(queries, str):
        queries = [queries]
        unwrap = True
    else:
        unwrap = False

    with measure_execution_time('search_function_execution'):
        search_results = search_executor.map(search_func, queries)
        results = [[
            {
                'text': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            } for doc, score in search_result] for search_result in search_results]

    if unwrap and len(results) == 1:
        return results[0]
    else:
        return results
