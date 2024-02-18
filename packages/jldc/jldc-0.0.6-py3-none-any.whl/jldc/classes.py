from datetime import datetime
from json import JSONDecoder, JSONEncoder
from typing import Any, Callable, ClassVar, Protocol

from jldc.constants import _JLDC_NDARRAY, _JLDC_NDARRAY_DTYPE, _JLDC_NDARRAY_SHAPE


class Dataclass(Protocol):
    """Approximation of a dataclass object, for typing."""

    __dataclass_fields__: ClassVar[dict]
    __name__: ClassVar[str]
    __call__: ClassVar[Callable]


class JLDCEncoder(JSONEncoder):
    """Custom encoder, to handle non-default types when converting to JSON."""

    def default(self, obj: Any):
        if isinstance(obj, datetime):
            return obj.isoformat()

        try:
            import numpy as np

            if isinstance(obj, np.ndarray):
                return {
                    _JLDC_NDARRAY: obj.tolist(),
                    _JLDC_NDARRAY_DTYPE: str(obj.dtype),
                    _JLDC_NDARRAY_SHAPE: obj.shape,
                }

        except ImportError:
            # numpy isn't installed => no arrays to encode!
            pass

        return super().default(obj)


class JLDCDecoder(JSONDecoder):
    """Custom decoder, to handle non-default types when converting from JSON."""

    def __init__(self, **kwargs):
        """Updated init, adding a custom object hook."""
        kwargs["object_hook"] = self.object_hook
        super().__init__(**kwargs)

    @staticmethod
    def object_hook(obj: Any):
        if isinstance(obj, dict) and _JLDC_NDARRAY in obj:
            try:
                import numpy as np
            except ImportError as err:
                raise RuntimeError(
                    "You must install numpy to decode JSON with ndarray types."
                ) from err

            return np.array(obj[_JLDC_NDARRAY], obj[_JLDC_NDARRAY_DTYPE]).reshape(
                obj[_JLDC_NDARRAY_SHAPE]
            )

        for key, val in obj.items():
            if isinstance(val, str):
                try:
                    obj[key] = datetime.fromisoformat(val)
                except ValueError:
                    # string incorrect date format, leave it
                    pass

        return obj
