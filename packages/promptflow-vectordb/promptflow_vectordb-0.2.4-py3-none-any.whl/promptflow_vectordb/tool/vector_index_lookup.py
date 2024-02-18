import uuid
from typing import List, Union

from promptflow import tool, ToolProvider

from .contracts.telemetry import StoreToolEventNames, StoreToolEventCustomDimensions
from .contracts.ui_config import StoreType, VectorSearchToolUIConfig
from .adapter import AdapterFactory
from .utils.logging import ToolLoggingUtils
from .utils.pf_runtime_utils import PromptflowRuntimeUtils
from .utils.pf_exception_helpers import PromptflowExceptionConverter
from ..core.contracts import StoreStage, StoreOperation
from ..core.logging.utils import LoggingUtils


class VectorIndexLookup(ToolProvider):

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
                store_stage=StoreStage.INITIALIZATION,
                custom_dimensions={
                    StoreToolEventCustomDimensions.STORE_TYPE: StoreType.MLINDEX
                }
            )

            super().__init__()

            ui_config = VectorSearchToolUIConfig(
                store_type=StoreType.MLINDEX,
                path=path,
                logging_config=logging_config
            )

            self.__adapter = AdapterFactory.get_adapter(ui_config)
            self.__adapter.load()

            self.__logger.telemetry_event_completed(
                event_name=StoreToolEventNames.INIT,
            )
            self.__logger.flush()

        except Exception as e:
            raise PromptflowExceptionConverter.convert(e) from e

    @tool
    def search(
        self,
        query: Union[List[float], str],
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
            return self.__adapter.search(query, top_k)

        try:
            return _do_search()
        except Exception as e:
            raise PromptflowExceptionConverter.convert(e) from e
