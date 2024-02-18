import json

import numpy as np

from ..config.config_utils import ConfigWarning
from ..noise_models.utils import BaseNoiseComponent


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder for classes and data types that we use."""

    def default(self, obj):
        if isinstance(obj, complex):  # Complex numbers (not serializable by default)
            return {"__complex__": True, "real": obj.real, "imag": obj.imag}
        elif isinstance(obj, np.ndarray):  # Numpy arrays
            return {"__ndarray__": True, "data": obj.tolist(), "dtype": str(obj.dtype)}
        elif isinstance(obj, ConfigWarning):  # Config warnings
            return {
                "__ConfigWarning__": True,
                "loc": obj.loc,
                "type": obj.type,
                "msg": obj.msg,
            }
        elif isinstance(
            obj, BaseNoiseComponent
        ):  # Any objects derived from the BaseNoiseComponent class
            d = obj.to_dict()
            d["__BaseNoiseComponent__"] = True
            return d
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)

        return super().default(obj)


def jsonify(data):
    """Shorthand to convert data (possibly containing complex numbers or numpy arrays) to a json encodable dict with the custom encoder"""
    json_string = json.dumps(data, cls=CustomEncoder)
    return json.loads(json_string)
