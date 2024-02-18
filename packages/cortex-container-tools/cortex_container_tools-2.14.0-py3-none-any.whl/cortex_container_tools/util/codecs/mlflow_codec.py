import pandas as pd
import numpy as np

from mlserver.types.dataplane import InferenceRequest as MLServerInferenceRequest
from mlserver.codecs import PandasCodec, NumpyCodec, StringCodec

from ._codec import Codec
from ..types import RequestInput, InferenceRequest, InferenceResponse, ResponseOutput
import json

class MLflowCodec(Codec):
    def decode(data) -> InferenceResponse:
        request = MLServerInferenceRequest(**json.loads(data))

        # Catch missing content type
        if request.parameters is None or request.parameters.content_type is None:
            raise ValueError("Missing content type in 'parameters' field.")

        content_type = request.parameters.content_type
        if content_type == 'pd':
            return PandasCodec.decode_request(request)
        elif content_type == 'np':
            return NumpyCodec.decode(request)
        elif content_type == 'str':
            return StringCodec.decode(RequestInput(**request.inputs[0]))
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

    def encode(data):
        input_type = type(data)
        if input_type == pd.DataFrame:
            encoded_pandas = PandasCodec.encode_outputs(data)
            inference_response = InferenceResponse(outputs=encoded_pandas)
            return inference_response
        elif input_type == np.ndarray:
            return NumpyCodec.encode_output('output-0', data)
        elif input_type == str:
            return StringCodec.encode(data)
        else:
            raise ValueError(f"Unsupported content type: {InferenceRequest.parameters.content_type}")
