from typing import Union

from llama_index.vector_stores.types import BasePydanticVectorStore, VectorStore
from unstract.adapters.constants import Common
from unstract.adapters.vectordb import adapters
from unstract.adapters.vectordb.constants import VectorDbConstants
from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel, ToolSettingsKey
from unstract.sdk.tool.base import BaseTool


class ToolVectorDB:
    """Class to handle VectorDB for Unstract Tools."""

    def __init__(self, tool: BaseTool, tool_settings: dict[str, str] = {}):
        self.tool = tool
        self.vector_db_adapters = adapters
        self.vector_db_adapter_id = tool_settings.get(
            ToolSettingsKey.VECTOR_DB_ADAPTER_ID
        )

    def get_vector_db(
        self,
        adapter_instance_id: str,
        collection_name_prefix: str = None,
        embedding_type: str = None,
    ) -> Union[BasePydanticVectorStore, VectorStore, None]:
        adapter_instance_id = (
            adapter_instance_id
            if adapter_instance_id
            else self.vector_db_adapter_id
        )
        if adapter_instance_id is not None:
            try:
                vector_db_config = ToolAdapter.get_adapter_config(
                    self.tool, adapter_instance_id
                )
                vector_db_adapter_id = vector_db_config.get(Common.ADAPTER_ID)
                if vector_db_adapter_id in self.vector_db_adapters:
                    vector_db_adapter = self.vector_db_adapters[
                        vector_db_adapter_id
                    ][Common.METADATA][Common.ADAPTER]
                    vector_db_metadata = vector_db_config.get(
                        Common.ADAPTER_METADATA
                    )
                    # Adding the collection prefix and embedding type
                    # to the metadata
                    vector_db_metadata[
                        VectorDbConstants.VECTOR_DB_NAME_PREFIX
                    ] = collection_name_prefix
                    vector_db_metadata[
                        VectorDbConstants.EMBEDDING_TYPE
                    ] = embedding_type

                    vector_db_adapter_class = vector_db_adapter(
                        vector_db_metadata
                    )
                    return vector_db_adapter_class.get_vector_db_instance()
                else:
                    return None
            except Exception as e:
                self.tool.stream_log(
                    log=f"Unable to get vector_db instance: {e}",
                    level=LogLevel.ERROR,
                )
                return None
