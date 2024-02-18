import json

import numpy as np

from .. import noise_models
from ..config.config_utils import ConfigWarning
from ..messaging import message


class CustomDecoder(json.JSONDecoder):
    """Custom JSON decoder for classes and data types that we use. The main purpose of the decoder
    is to obtain back the various Message objects from their json string output."""

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "__ClientMessage__" in dct:
            class_name = dct["__ClientMessage__"]["name"]
            class_contents = dct["__ClientMessage__"]["content"]
            return getattr(message, class_name).from_dict(class_contents)
        # Complex numbers (not serializable by default)
        elif "__complex__" in dct:
            return complex(dct["real"], dct["imag"])
        # Numpy arrays
        elif "__ndarray__" in dct:
            return np.array(dct["data"], dtype=dct["dtype"])
        # Config warnings
        elif "__ConfigWarning__" in dct:
            return ConfigWarning(dct["loc"], dct["type"], dct["msg"])
        # BaseNoiseComponent and its subclasses (e.g. NoiseChannel, QubitNoise, GateNoise, NoiseModel)
        elif "__BaseNoiseComponent__" in dct:
            class_name = dct["type"]
            return getattr(noise_models, class_name).from_dict(dct)
        else:
            return dct


def dejsonify(data):
    """Shorthand to convert json encodable data to its original format with the custom decoder."""
    json_string = json.dumps(data)
    return json.loads(json_string, cls=CustomDecoder)
