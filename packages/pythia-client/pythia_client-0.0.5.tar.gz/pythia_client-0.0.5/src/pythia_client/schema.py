from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Union, Optional, Any, List

PrimitiveType = Union[str, int, float, bool]


class RequestBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class HaystackVersion(BaseModel):
    hs_version: str


class Usage(BaseModel):
    prompt_tokens: int
    total_tokens: int
    completion_tokens: Optional[int] = None


class Meta(BaseModel):
    model: str
    usage: Usage
    index: Optional[int] = None
    finish_reason: Optional[str] = None


class Embedder(BaseModel):
    meta: Meta


class Writer(BaseModel):
    documents_written: int


class FilterRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = {}


class FilterDocStoreReponse(BaseModel):
    id: str
    content: str
    dataframe: Optional[Union[str, Any]] = None
    blob: Optional[Union[str, Any]] = None
    meta: Dict[str, Any]
    score: float
    embedding: Union[List[float], Optional[str]] = None


class UploadFileResponse(RequestBaseModel):
    Embedder: Embedder
    Writter: Writer


class DocumentQueryReponse(BaseModel):
    id: str
    content: str
    dataframe: Optional[Union[str, Any]] = None
    blob: Optional[Union[str, Any]] = None
    meta: Dict[str, Any]
    score: float
    embedding: Union[List[float], Optional[str]] = None


class Answer(BaseModel):
    data: str
    query: str
    documents: List[DocumentQueryReponse]
    meta: Meta


class AnswerBuilder(BaseModel):
    answers: List[Answer]


class QueryRequest(RequestBaseModel):
    query: str
    params: Optional[dict] = None
    debug: Optional[bool] = False


class QueryResponse(RequestBaseModel):
    QueryEmbedder: Embedder
    AnswerBuilder: AnswerBuilder


class GetFileS3Reponse(RequestBaseModel):
    url: str


class DeleteDocResponse(RequestBaseModel):
    n_deleted_docstore: int
    n_deleted_s3: int
    deleted_s3_keys: List[str]


class RetrievedDoc(RequestBaseModel):
    original_file_name: str
    doc_id: str
    text: str
    score: Decimal


class LogQueryTable(RequestBaseModel):
    question_id: str
    source_app: str
    system_prompt: str
    user_query: str
    answer: str
    llm_model_name: str
    embedding_model_name: str
    retrieved_docs: List[RetrievedDoc]
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    timestamp: str = datetime.now().isoformat()
    start_time: str
    end_time: str
    time_taken: Decimal
    feedback: Optional[int] = -1


class LogIndexationTable(RequestBaseModel):
    indexation_id: str
    source_app: str
    embedding_model_name: str
    total_tokens: int
    timestamp: str = datetime.now().isoformat()
    start_time: str
    end_time: str
    time_taken: Decimal
    file_meta: List[Dict[str, Any]]
    s3_keys: List[str]
    indexation_mode: str
    n_files: int
    n_docs_written: int


class GeneratorJson(BaseModel):
    meta: List[Meta]


class EsrTicket(BaseModel):
    company_or_client_name: str
    ticket_category: str
    command_number: str


class OutputValidator(BaseModel):
    valid_replies: Optional[List[EsrTicket]] = None
    invalid_replies: Optional[List] = None
    error_message: Optional[str] = None


class DataExtractRequest(BaseModel):
    email_content: str


class DataExtractResponse(BaseModel):
    Generator_json: GeneratorJson
    OutputValidator: OutputValidator


class CPUUsage(BaseModel):
    used: float = Field(..., description="REST API average CPU usage in percentage")

    @field_validator("used")
    @classmethod
    def used_check(cls, v):
        return round(v, 2)


class MemoryUsage(BaseModel):
    used: float = Field(..., description="REST API used memory in percentage")

    @field_validator("used")
    @classmethod
    def used_check(cls, v):
        return round(v, 2)


class GPUUsage(BaseModel):
    kernel_usage: float = Field(..., description="GPU kernel usage in percentage")
    memory_total: int = Field(..., description="Total GPU memory in megabytes")
    memory_used: Optional[int] = Field(
        ..., description="REST API used GPU memory in megabytes"
    )

    @field_validator("kernel_usage")
    @classmethod
    def kernel_usage_check(cls, v):
        return round(v, 2)


class GPUInfo(BaseModel):
    index: int = Field(..., description="GPU index")
    usage: GPUUsage = Field(..., description="GPU usage details")


class HealthResponse(BaseModel):
    version: str = Field(..., description="Haystack version")
    cpu: CPUUsage = Field(..., description="CPU usage details")
    memory: MemoryUsage = Field(..., description="Memory usage details")
    gpus: List[GPUInfo] = Field(default_factory=list, description="GPU usage details")
