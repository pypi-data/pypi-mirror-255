from typing import List
import uuid

from promptflow import tool, ToolProvider

from .contracts import StoreType
from .contracts.telemetry import StoreToolEventNames, StoreToolEventCustomDimensions
from .contracts.ui_config import VectorSearchToolUIConfig
from .adapter import AdapterFactory
from .utils.pf_runtime_utils import PromptflowRuntimeUtils
from .utils.logging import ToolLoggingUtils
from ..core.contracts import StoreStage, StoreOperation
from ..core.utils.path_utils import PathUtils
from ..core.logging.utils import LoggingUtils
from .utils.pf_exception_helpers import PromptflowExceptionConverter


class FaissIndexLookup(ToolProvider):

    def __init__(self, path: str):

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
                store_stage=StoreStage.INITIALIZATION
            )

            super().__init__()

            store_type = None

            if PathUtils.is_blob_storage_url(path):
                store_type = StoreType.BLOBFAISS
            elif PathUtils.is_data_store_url(path):
                store_type = StoreType.AMLDATASTOREFAISS
            elif PathUtils.is_github_url(path):
                store_type = StoreType.GITHUBFAISS
            elif PathUtils.is_http_url(path):
                store_type = StoreType.HTTPFAISS
            else:
                if PromptflowRuntimeUtils.is_running_in_aml():
                    store_type = StoreType.BLOBFAISS
                    path = PromptflowRuntimeUtils.get_url_for_relative_path_on_workspace_blob_store(path)
                else:
                    store_type = StoreType.LOCALFAISS

            self.__logger.telemetry(
                msg=f"{StoreToolEventNames.IDENTIFY_STORE_TYPE.value} : {store_type}",
                event_name=StoreToolEventNames.IDENTIFY_STORE_TYPE,
                custom_dimensions={
                    StoreToolEventCustomDimensions.STORE_TYPE: store_type
                }
            )

            ui_config = VectorSearchToolUIConfig(
                store_type=store_type,
                path=path,
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
    def search(
        self,
        vector: List[float],
        top_k: int = 3
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
            return self.__adapter.search(vector, top_k)

        try:
            return _do_search()
        except Exception as e:
            raise PromptflowExceptionConverter.convert(e) from e
