import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pytz

from llm_monitor.schema.transaction import TransactionRecord, TransactionRecordType
from llm_monitor.utils.aggregator import (
    add_records_to_batch,
    initialize_api_client,
    start_aggregator_job,
)


class LLMMonitor:
    timers: Dict[str, Dict[str, float]] = {}
    records: Dict[str, TransactionRecord] = {}
    version: Optional[str]

    def __init__(
        self,
        project_name: str,
        version: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initializes LLM Monitor

        Parameters
        ----------
        project_name : str
            The name of the project to log to
        version : Optional[str]
            A version identifier for this system so logs can be attributed
            to a specific configuration
        """
        self.version = version
        initialize_api_client(project_name=project_name)
        start_aggregator_job()

    def _start_new_node(self, node_id: str, chain_id: Optional[str]) -> str:
        if chain_id:
            # This check ensures we're actually logging the parent chain
            if self.records.get(chain_id):
                self.records[chain_id].has_children = True
                chain_root_id = self.records[chain_id].chain_root_id or node_id
            else:
                # We're not logging the parent chain, so this is the root
                chain_root_id = node_id
        else:
            # This node is the root if it doesn't have a parent
            chain_root_id = node_id

        self.timers[node_id] = {}
        self.timers[node_id]["start"] = time.perf_counter()

        return chain_root_id

    def _end_node(self, node_id: str) -> int:
        self.timers[node_id]["stop"] = time.perf_counter()
        latency_ms = round(
            (self.timers[node_id]["stop"] - self.timers[node_id]["start"]) * 1000
        )
        del self.timers[node_id]

        return latency_ms

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

    def log_node_start(
        self,
        node_type: TransactionRecordType,
        input_text: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        constructor: Optional[str] = None,
        chain_id: Optional[str] = None,
    ) -> str:
        """Log the start of a new node of any type

        Parameters
        ----------
        node_type : TransactionRecordType
            Type of node ("llm", "chat", "chain", "agent", "tool", "retriever")
        input_text : str
            Input to the node as a str or json dump, by default None
        model : Optional[str], optional
            Model name for llm or chat nodes, by default None
        temperature : Optional[float], optional
            Temperature setting for llm or chat nodes, by default None
        user_metadata : Optional[Dict[str, Any]], optional
            A dict of key-value metadata for identifying logs, by default None
        tags : Optional[List[str]], optional
            A list of string tags for identifying logs, by default None
        constructor : Optional[str], optional
            A class constructor name for the node (e.g. OpenAIChat), by default None
        chain_id : Optional[str], optional
            The ID of the chain this node belongs to, by default None

        Returns
        -------
        str
            The node_id used when calling log_node_completion() or log_node_error()
        """
        node_id = str(uuid4())

        chain_root_id = self._start_new_node(node_id, chain_id)

        self.timers[node_id] = {}
        self.timers[node_id]["start"] = time.perf_counter()

        self.records[node_id] = TransactionRecord(
            node_id=node_id,
            input_text=input_text,
            model=model,
            temperature=temperature,
            user_metadata=user_metadata,
            tags=tags,
            constructor=constructor,
            chain_id=chain_id,
            chain_root_id=chain_root_id,
            created_at=datetime.now(tz=pytz.utc).isoformat(),
            node_type=node_type,
            version=self.version,
        )
        return node_id

    def log_node_completion(
        self,
        node_id: str,
        output_text: str,
        num_input_tokens: Optional[int] = 0,
        num_output_tokens: Optional[int] = 0,
        num_total_tokens: Optional[int] = 0,
        finish_reason: Optional[str] = None,
        status_code: Optional[int] = 200,
    ) -> None:
        """_summary_

        Parameters
        ----------
        node_id : str
            Output value from log_node_start()
        output_text : str
            Ouput from the node as str or json dump (List[str] for retrievers)
        num_input_tokens : Optional[int], optional
            Number of input tokens for llm or chat nodes, by default 0
        num_output_tokens : Optional[int], optional
            Number of output tokens for llm or chat nodes, by default 0
        num_total_tokens : Optional[int], optional
            Total number of tokens for llm or chat nodes, by default 0
        finish_reason : Optional[str], optional
            Finish reason for node (e.g. "chain end" or "stop"), by default None
        status_code : Optional[int], optional
            HTTP status code for the node, by default 200
        """
        latency_ms = self._end_node(node_id)

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=output_text,
            num_input_tokens=num_input_tokens,
            num_output_tokens=num_output_tokens,
            num_total_tokens=num_total_tokens,
            finish_reason=finish_reason,
            latency_ms=latency_ms,
            status_code=status_code,
        )

        self._finalize_node(TransactionRecord(**model_dict))

    def log_node_error(
        self, node_id: str, error_message: str, status_code: Optional[int] = 500
    ) -> None:
        """Log an error encountered while processing a node

        Parameters
        ----------
        node_id : str
            Ouput from log_node_start()
        error_message : str
            The error message from the remote system or local application
        status_code : Optional[int], optional
            HTTP status code for the error, by default 500
        """
        latency_ms = self._end_node(node_id)

        model_dict = self.records[node_id].model_dump()
        model_dict.update(
            output_text=f"ERROR: {error_message}",
            num_input_tokens=0,
            num_output_tokens=0,
            num_total_tokens=0,
            latency_ms=latency_ms,
            status_code=status_code,
        )

        self._finalize_node(TransactionRecord(**model_dict))
