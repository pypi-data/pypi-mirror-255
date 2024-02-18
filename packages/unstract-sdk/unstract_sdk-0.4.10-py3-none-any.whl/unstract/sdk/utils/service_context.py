from typing import Any, Optional

from llama_index import ServiceContext
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.llms.utils import LLMType
from unstract.sdk.llm import ToolLLM
from unstract.sdk.utils.usage_handler import UsageHandler


class UNServiceContext:
    """Class representing the UNServiceContext.

    Use this over the default service context of llama index

    This class provides a static method to get the service context for
    UNstract Tools. The service context includes a tokenizer, token counter,
    usage handler, and  callback manager.

    Attributes:
        None

    Methods:
        get_service_context: Returns the service context for UNstract Tools.

    Example:
        service_context = UNServiceContext.
                            get_service_context(
                                workflow_id="123",
                                execution_id="456",
                                llm="default",
                                embed_model="default")
    """

    @staticmethod
    def get_service_context(
        workflow_id: str = "",
        execution_id: str = "",
        llm: Optional[LLMType] = None,
        embed_model: Optional[Any] = None,
    ) -> ServiceContext:
        """Returns the service context for UNstract Tools.

        Parameters:
            workflow_id (str): The workflow ID. Default is an empty string.
            execution_id (str): The execution ID. Default is an empty string.
            llm (Optional[LLMType]): The LLM type. Default is None.
            embed_model (Optional[Any]): The embedding model. Default is None.

        Returns:
            ServiceContext: The service context for UNstract Tools.

        Example:
            service_context = UNServiceContext.get_service_context(
                workflow_id="123",
                execution_id="456",
                llm="default",
                embed_model="default"
            )
        """
        tokenizer = ToolLLM.get_tokenizer(llm)
        token_counter = TokenCountingHandler(tokenizer=tokenizer, verbose=True)
        usage_handler = UsageHandler(
            token_counter=token_counter,
            llm_model=llm,
            embed_model=embed_model,
            workflow_id=workflow_id,
            execution_id=execution_id,
        )

        callback_manager = CallbackManager(
            handlers=[token_counter, usage_handler]
        )
        return ServiceContext.from_defaults(
            llm=llm, embed_model=embed_model, callback_manager=callback_manager
        )
