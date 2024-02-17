import time
from datetime import datetime
from http import HTTPStatus
from json import dumps
from typing import Any, Dict, List, Optional, Sequence, Union
from uuid import UUID

import pytz
import tiktoken
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts.chat import ChatPromptValue
from langchain.schema.agent import AgentAction, AgentFinish
from langchain.schema.messages import BaseMessage
from langchain.schema.messages import _message_to_dict as message_to_dict
from langchain.schema.output import LLMResult
from langchain_core.documents import Document
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1

from llm_monitor.schema.transaction import TransactionRecord, TransactionRecordType
from llm_monitor.utils.aggregator import (
    add_records_to_batch,
    initialize_api_client,
    start_aggregator_job,
)

Stringable = (str, int, float)

# The id field of the serialized response contains a list of identifiers
# that represent the structure of that call like
# ['langchain', 'chat_models', 'openai', 'ChatOpenAI'].
# We want to store the specific constructor being ChatOpenAI
IDX_OF_CONSTRUCTOR = 3


class MonitorHandler(BaseCallbackHandler):
    timers: Dict[str, Dict[str, float]] = {}
    records: Dict[str, TransactionRecord] = {}
    version: str

    def __init__(
        self, project_name: str, version: str, *args: Any, **kwargs: Any
    ) -> None:
        """LangChain callbackbander for LLM Monitoring

        Parameters
        ----------
        project_name : str
            Name of the project to log to
        version : str
            A version identifier for this system so logs can be attributed
            to a specific configuration
        """
        self.version = version
        initialize_api_client(project_name=project_name)
        start_aggregator_job()
        super().__init__(*args, **kwargs)

    def _start_new_node(
        self, run_id: UUID, parent_run_id: Optional[UUID]
    ) -> tuple[str, Optional[str], Optional[str]]:
        node_id = str(run_id)
        chain_id = str(parent_run_id) if parent_run_id else None
        if chain_id:
            # This check ensures we're actually logging the parent chain
            if self.records.get(chain_id):
                self.records[chain_id].has_children = True
                chain_root_id = self.records[chain_id].chain_root_id
            else:
                # We're not logging the parent chain, so this is the root
                chain_root_id = node_id
        else:
            # This node is the root if it doesn't have a parent
            chain_root_id = node_id

        self.timers[node_id] = {}
        self.timers[node_id]["start"] = time.perf_counter()

        return node_id, chain_root_id, chain_id

    def _end_node(self, run_id: UUID) -> tuple[str, int]:
        node_id = str(run_id)

        self.timers[node_id]["stop"] = time.perf_counter()
        latency_ms = round(
            (self.timers[node_id]["stop"] - self.timers[node_id]["start"]) * 1000
        )
        del self.timers[node_id]

        return node_id, latency_ms

    def _finalize_node(self, record: TransactionRecord) -> None:
        self.records[record.node_id] = record
        batch_records: List = []
        # If this record is closing out a root chain, then add all
        # records with that chain_root_id to the batch
        if record.node_id == record.chain_root_id:
            for k, v in self.records.copy().items():
                if v.chain_root_id == record.chain_root_id:
                    batch_records.append(v)
                    del self.records[k]

            add_records_to_batch(batch_records)

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when LLM starts running."""
        node_id, chain_root_id, chain_id = self._start_new_node(run_id, parent_run_id)
        input_text = prompts[0]
        tags = kwargs.get("tags")
        metadata = kwargs.get("metadata")
        constructor = serialized["id"][IDX_OF_CONSTRUCTOR]
        model = kwargs["invocation_params"]["model_name"]
        temperature = kwargs["invocation_params"].get("temperature")
        self.records[node_id] = TransactionRecord(
            node_id=node_id,
            chain_id=chain_id,
            chain_root_id=chain_root_id,
            input_text=input_text,
            model=model,
            created_at=datetime.now(tz=pytz.utc).isoformat(),
            temperature=temperature,
            tags=tags,
            user_metadata=metadata,
            constructor=constructor,
            node_type=TransactionRecordType.llm.value,
            version=self.version,
        )

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when Chat Model starts running."""
        node_id, chain_root_id, chain_id = self._start_new_node(run_id, parent_run_id)
        chat_messages = ChatPromptValue(messages=messages[0])
        tags = kwargs.get("tags")
        metadata = kwargs.get("metadata")
        constructor = serialized["id"][IDX_OF_CONSTRUCTOR]
        model = (
            kwargs["invocation_params"]["model"] or kwargs["invocation_params"]["_type"]
        )
        temperature = kwargs["invocation_params"].get("temperature")
        self.records[node_id] = TransactionRecord(
            node_id=node_id,
            chain_id=chain_id,
            chain_root_id=chain_root_id,
            input_text=chat_messages.to_string(),
            model=model,
            created_at=datetime.now(tz=pytz.utc).isoformat(),
            temperature=temperature,
            tags=tags,
            user_metadata=metadata,
            constructor=constructor,
            node_type=TransactionRecordType.chat.value,
            version=self.version,
        )

    def on_llm_end(self, response: LLMResult, run_id: UUID, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        node_id, latency_ms = self._end_node(run_id)

        generation = response.flatten()[0].generations[0][0]
        output_text = generation.text

        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            num_input_tokens = usage.get("prompt_tokens", None)
            num_output_tokens = usage.get("completion_tokens", None)
            num_total_tokens = usage.get("total_tokens", None)
        else:
            try:
                # This is because streaming requests don't provide `llm_output`
                # This only works for OpenAI models (or "" because typing)
                encoding = tiktoken.encoding_for_model(
                    self.records[node_id].model or ""
                )
                num_input_tokens = len(
                    encoding.encode(self.records[node_id].input_text)
                )
                num_output_tokens = len(encoding.encode(output_text))
                num_total_tokens = num_input_tokens + num_output_tokens
            except KeyError:
                num_input_tokens = 0
                num_output_tokens = 0
                num_total_tokens = 0

        if generation.generation_info:
            finish_reason = generation.generation_info.get("finish_reason", "")

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=output_text,
            num_input_tokens=num_input_tokens,
            num_output_tokens=num_output_tokens,
            num_total_tokens=num_total_tokens,
            finish_reason=finish_reason,
            latency_ms=latency_ms,
            status_code=HTTPStatus.OK,
        )

        self._finalize_node(TransactionRecord(**model_dict))

    def on_llm_error(self, error: BaseException, run_id: UUID, **kwargs: Any) -> Any:
        """Run when LLM errors."""
        node_id, latency_ms = self._end_node(run_id)

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=f"ERROR: {error}",
            num_input_tokens=0,
            num_output_tokens=0,
            num_total_tokens=0,
            latency_ms=latency_ms,
            status_code=getattr(error, "http_status", HTTPStatus.INTERNAL_SERVER_ERROR),
        )

        self._finalize_node(TransactionRecord(**model_dict))

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when chain starts running."""
        node_id, chain_root_id, chain_id = self._start_new_node(run_id, parent_run_id)
        tags = kwargs.get("tags")
        metadata = kwargs.get("metadata")
        constructor = serialized["id"][IDX_OF_CONSTRUCTOR]

        if isinstance(inputs, Stringable):
            node_input = {"input": inputs}
        elif isinstance(inputs, BaseMessage):
            node_input = message_to_dict(inputs)
        elif isinstance(inputs, dict):
            # We only support string inputs since those are the likely slots.
            node_input = inputs = {
                key: value
                for key, value in inputs.items()
                if value and isinstance(value, Stringable)
            }
        elif isinstance(inputs, list) and all(isinstance(v, Document) for v in inputs):
            node_input = {
                str(index): value.page_content for index, value in enumerate(inputs)
            }
        else:
            node_input = dict()

        self.records[node_id] = TransactionRecord(
            node_id=node_id,
            chain_id=chain_id,
            chain_root_id=chain_root_id,
            input_text=dumps(
                node_input,
                default=MonitorHandler.json_serializer,
            ),
            created_at=datetime.now(tz=pytz.utc).isoformat(),
            tags=tags,
            user_metadata=metadata,
            node_type=TransactionRecordType.chain.value,
            constructor=constructor,
            version=self.version,
        )

    def on_chain_end(
        self,
        outputs: Union[str, Dict[str, Any]],
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        """Run when chain ends running."""
        node_id, latency_ms = self._end_node(run_id)

        if isinstance(outputs, str):
            node_output = {"output": outputs}
        elif isinstance(outputs, dict):
            node_output = outputs
        elif isinstance(outputs, (AgentFinish, AgentAction)):
            node_output = outputs.dict()
        else:
            node_output = dict()

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=dumps(
                node_output,
                default=MonitorHandler.json_serializer,
            ),
            finish_reason="chain_end",
            latency_ms=latency_ms,
            status_code=HTTPStatus.OK,
        )

        self._finalize_node(TransactionRecord(**model_dict))

    def on_chain_error(self, error: BaseException, run_id: UUID, **kwargs: Any) -> Any:
        """Run when chain errors."""
        node_id, latency_ms = self._end_node(run_id)

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=f"ERROR: {error}",
            latency_ms=latency_ms,
            status_code=getattr(error, "http_status", HTTPStatus.INTERNAL_SERVER_ERROR),
        )

        self._finalize_node(TransactionRecord(**model_dict))

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        """Run on agent end."""
        node_id = str(run_id)
        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            node_type=TransactionRecordType.agent.value,
        )

        self.records[node_id] = TransactionRecord(**model_dict)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool starts running."""
        node_id, chain_root_id, chain_id = self._start_new_node(run_id, parent_run_id)
        tags = kwargs.get("tags")
        metadata = kwargs.get("metadata")
        constructor = serialized["name"]

        self.records[node_id] = TransactionRecord(
            node_id=node_id,
            chain_id=chain_id,
            chain_root_id=chain_root_id,
            input_text=input_str,
            created_at=datetime.now(tz=pytz.utc).isoformat(),
            tags=tags,
            user_metadata=metadata,
            node_type=TransactionRecordType.tool.value,
            constructor=constructor,
            version=self.version,
        )

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        """Run when tool ends running."""
        node_id, latency_ms = self._end_node(run_id)

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=output,
            latency_ms=latency_ms,
            status_code=HTTPStatus.OK,
        )

        self._finalize_node(TransactionRecord(**model_dict))

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        """Run when tool errors."""
        node_id, latency_ms = self._end_node(run_id)

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=f"ERROR: {error}",
            latency_ms=latency_ms,
            status_code=getattr(error, "http_status", HTTPStatus.INTERNAL_SERVER_ERROR),
        )

    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run on retriever start."""
        node_id, chain_root_id, chain_id = self._start_new_node(run_id, parent_run_id)
        constructor = serialized["id"][-1]

        self.records[node_id] = TransactionRecord(
            node_id=node_id,
            chain_id=chain_id,
            chain_root_id=chain_root_id,
            input_text=str(query),
            created_at=datetime.now(tz=pytz.utc).isoformat(),
            tags=tags,
            user_metadata=metadata,
            node_type=TransactionRecordType.retriever.value,
            constructor=constructor,
            version=self.version,
        )

    def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Run on retriever end."""
        node_id, latency_ms = self._end_node(run_id)

        model_dict = self.records[node_id].model_dump()

        docs = dumps(
            [
                {"page_content": document.page_content, "metadata": document.metadata}
                for document in documents
            ]
        )

        model_dict.update(
            output_text=str(docs),
            finish_reason="retriever_end",
            latency_ms=latency_ms,
            status_code=HTTPStatus.OK,
        )

        record = TransactionRecord(**model_dict)
        self._finalize_node(record)

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Run on retriever error."""
        node_id, latency_ms = self._end_node(run_id)

        model_dict = self.records[node_id].model_dump()

        model_dict.update(
            output_text=f"ERROR: {str(error)}",
            latency_ms=latency_ms,
            status_code=getattr(error, "http_status", HTTPStatus.INTERNAL_SERVER_ERROR),
        )

    @staticmethod
    def json_serializer(obj: Any) -> Union[str, Dict[Any, Any]]:
        """
        For serializing objects that cannot be serialized by default with json.dumps.

        Checks for certain methods to convert object to dict.
        """
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, BaseModelV1):
            return obj.dict()
        return str(type(obj))
