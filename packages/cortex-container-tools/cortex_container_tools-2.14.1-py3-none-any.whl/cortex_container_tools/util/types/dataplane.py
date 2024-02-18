from pydantic import Field
from typing import List, Any, Optional, Dict

from . import BaseModel

class Parameters(BaseModel):
    class Config:
        extra = 'allow'

    content_type: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None


class TensorData(BaseModel):
    __root__: Any = Field(..., title="TensorData")

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, idx):
        return self.__root__[idx]

    def __len__(self):
        return len(self.__root__)

class RequestInput(BaseModel):
    name: str
    shape: List[int]
    datatype: str
    parameters: Optional["Parameters"] = None
    data: "TensorData"

class ResponseOutput(BaseModel):
    name: str
    shape: List[int]
    datatype: str
    parameters: Optional["Parameters"] = None
    data: "TensorData"

class RequestOutput(BaseModel):
    name: str
    parameters: Optional["Parameters"] = None

class InferenceRequest(BaseModel):
    parameters: Optional["Parameters"] = None
    inputs: List["RequestInput"]

class InferenceResponse(BaseModel):
    outputs: List[Any]
