from typing import Optional

from llama_index.embeddings.base import BaseEmbedding
from unstract.adapters.constants import Common
from unstract.adapters.embedding import adapters
from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel, ToolSettingsKey
from unstract.sdk.tool.base import BaseTool


class ToolEmbedding:
    def __init__(self, tool: BaseTool, tool_settings: dict[str, str] = {}):
        self.tool = tool
        self.max_tokens = 1024 * 16
        self.embedding_adapters = adapters
        self.embedding_adapter_id = tool_settings.get(
            ToolSettingsKey.EMBEDDING_ADAPTER_ID
        )

    def get_embedding(
        self, adapter_instance_id: str
    ) -> Optional[BaseEmbedding]:
        adapter_instance_id = (
            adapter_instance_id
            if adapter_instance_id
            else self.embedding_adapter_id
        )
        if adapter_instance_id is not None:
            try:
                embedding_config_data = ToolAdapter.get_adapter_config(
                    self.tool, adapter_instance_id
                )
                embedding_adapter_id = embedding_config_data.get(
                    Common.ADAPTER_ID
                )
                if embedding_adapter_id in self.embedding_adapters:
                    embedding_adapter = self.embedding_adapters[
                        embedding_adapter_id
                    ][Common.METADATA][Common.ADAPTER]
                    embedding_metadata = embedding_config_data.get(
                        Common.ADAPTER_METADATA
                    )
                    embedding_adapter_class = embedding_adapter(
                        embedding_metadata
                    )
                    return embedding_adapter_class.get_embedding_instance()
                else:
                    return None
            except Exception as e:
                self.tool.stream_log(
                    log=f"Error getting embedding: {e}", level=LogLevel.ERROR
                )
                return None
        else:
            return None
