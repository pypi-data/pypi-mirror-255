import uuid
from typing import List, Optional, Union

from promptflow import tool, ToolProvider
from promptflow.connections import CognitiveSearchConnection

from .contracts.types import StoreType
from .contracts.telemetry import StoreToolEventNames, StoreToolEventCustomDimensions
from .contracts.ui_config import VectorSearchToolUIConfig
from ..core.utils.retry_utils import retry_and_handle_exceptions
from .adapter import AdapterFactory
from .utils.logging import ToolLoggingUtils
from .utils.pf_runtime_utils import PromptflowRuntimeUtils
from .utils.pf_exception_helpers import PromptflowExceptionConverter
from ..service.contracts.errors import EmbeddingSearchRetryableError
from ..core.contracts import StoreStage, StoreOperation
from ..core.logging.utils import LoggingUtils
from ..connections.pinecone import PineconeConnection
from ..connections.weaviate import WeaviateConnection
from ..connections.qdrant import QdrantConnection


class VectorDBLookup(ToolProvider):

    def __init__(
        self,
        connection: Union[CognitiveSearchConnection, PineconeConnection, WeaviateConnection, QdrantConnection]
    ):

        try:

            logging_config = ToolLoggingUtils.generate_config(
                tool_name=self.__class__.__name__
            )
            self.__logger = LoggingUtils.sdk_logger(__package__, logging_config)
            self.__logger.update_telemetry_context(
                {
                    StoreToolEventCustomDimensions.TOOL_INSTANCE_ID: str(uuid.uuid4())
                }
            )

            self.__logger.telemetry_event_started(
                event_name=StoreToolEventNames.INIT,
                store_stage=StoreStage.INITIALIZATION,
                custom_dimensions={
                    StoreToolEventCustomDimensions.STORE_TYPE: StoreType.DBSERVICE
                }
            )

            super().__init__()

            ui_config = VectorSearchToolUIConfig(
                store_type=StoreType.DBSERVICE,
                connection=connection,
                logging_config=logging_config
            )

            self.__adapter = AdapterFactory.get_adapter(ui_config)
            self.__adapter.load()

            self.__logger.telemetry_event_completed(
                event_name=StoreToolEventNames.INIT
            )
            self.__logger.flush()

        except Exception as e:
            raise PromptflowExceptionConverter.convert(e) from e

    @tool
    @retry_and_handle_exceptions(EmbeddingSearchRetryableError)
    def search(
        self,
        vector: List[float],
        top_k: int = 3,
        index_name: Optional[str] = None,  # for cognitive search
        class_name: Optional[str] = None,  # for weaviate search
        namespace: Optional[str] = None,  # for pinecone search
        collection_name: Optional[str] = None,  # for qdrant search
        text_field: Optional[str] = None,  # text field name in the response json from search engines
        vector_field: Optional[str] = None,  # vector field name in the response json from search engines
        search_params: Optional[dict] = None,  # additional params for making requests to search engines
        search_filters: Optional[dict] = None,  # additional filters for making requests to search engines
    ) -> List[dict]:

        try:
            pf_context = PromptflowRuntimeUtils.get_pf_context_info_for_telemetry()
        except Exception:
            pf_context = None

        @LoggingUtils.log_event(
            package_name=__package__,
            event_name=StoreToolEventNames.SEARCH,
            scope_context=pf_context,
            store_stage=StoreStage.SEARVING,
            store_operation=StoreOperation.SEARCH,
            logger=self.__logger,
            flush=True
        )
        def _do_search() -> List[dict]:
            return self.__adapter.search(
                query=vector,
                top_k=top_k,
                index_name=index_name,
                class_name=class_name,
                namespace=namespace,
                collection_name=collection_name,
                text_field=text_field,
                vector_field=vector_field,
                search_params=search_params,
                search_filters=search_filters
            )

        try:
            return _do_search()
        except Exception as e:
            raise PromptflowExceptionConverter.convert(e) from e
