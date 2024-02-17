from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TransactionRecordType(str, Enum):
    llm = "llm"
    chat = "chat"
    chain = "chain"
    tool = "tool"
    agent = "agent"
    retriever = "retriever"


class TransactionRecord(BaseModel):
    latency_ms: Optional[int] = None
    status_code: Optional[int] = None
    input_text: str
    output_text: Optional[str] = None
    model: Optional[str] = None
    num_input_tokens: Optional[int] = None
    num_output_tokens: Optional[int] = None
    num_total_tokens: Optional[int] = None
    finish_reason: Optional[str] = None
    node_id: str
    chain_id: Optional[str] = None
    chain_root_id: Optional[str] = None
    output_logprobs: Optional[Dict] = None
    created_at: str
    tags: Optional[List[str]] = None
    user_metadata: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    constructor: Optional[str] = None
    node_type: TransactionRecordType
    has_children: bool = False
    version: str


class TransactionRecordBatch(BaseModel):
    records: List[TransactionRecord]
