from ._codec import Codec
import json

class JSONCodec(Codec):
    def decode(data):
        return json.loads(data)

    def encode(data):
        return json.dumps(data)
