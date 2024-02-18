"""
Chroma DB required connection information
"""

from dataclasses import dataclass
from typing import Literal, TypedDict, Union


class HuggingFaceEFInputs(TypedDict):
    ef_type: Literal["hf"]
    api_key: str
    model_name: str


class OpenAIEFInputs(TypedDict):
    ef_type: Literal["openai"]
    api_key: str
    model_name: str


class OpenAIAzureEFInputs(TypedDict):
    ef_type: Literal["openai_azure"]
    api_key: str
    model_name: str
    api_base: str
    api_version: str


class SentenceTransformerEFInputs(TypedDict):
    ef_type: Literal["sentence_transformer"]
    model_name: str


@dataclass
class ChromaDB:
    """Class for storing chroma connection details"""

    def __post_init__(self):
        self.db_type = "chroma_db"

    host: str
    port: int
    collection: str
    ef_inputs: Union[
        HuggingFaceEFInputs, OpenAIEFInputs, OpenAIAzureEFInputs, SentenceTransformerEFInputs
    ]


@dataclass
class LlamaIndexDB:
    """Class for storing llama index remote connection details for AWS S3"""

    def __post_init__(self):
        self.db_type = "llamaindex_db"
        if self.aws_key == "" or self.aws_secret == "":
            raise ValueError("appropriate AWS credentials required.")
        if self.s3_bucket_name == "":
            raise ValueError("valid s3 bucket name is required.")
        if self.index_id == "":
            raise ValueError("non-empty index_id is required.")

    aws_key: str
    aws_secret: str
    s3_bucket_name: str
    ef_inputs: Union[
        HuggingFaceEFInputs, OpenAIEFInputs, OpenAIAzureEFInputs, SentenceTransformerEFInputs
    ]
    index_id: Union[str, None] = None


@dataclass
class LlamaIndexWithChromaDB:
    """Class for storing chroma connection details used with llama index"""

    def __post_init__(self):
        self.db_type = "llamaindex+chroma_db"

    host: str
    port: int
    collection: str
    ef_inputs: Union[
        HuggingFaceEFInputs, OpenAIEFInputs, OpenAIAzureEFInputs, SentenceTransformerEFInputs
    ]
