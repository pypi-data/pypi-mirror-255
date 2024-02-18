import json
from dataclasses import asdict, is_dataclass
from typing import Iterator

from dacite import DaciteError, from_dict

from jldc.classes import Dataclass, JLDCDecoder, JLDCEncoder
from jldc.constants import _JLDC_DATACLASS, DEFAULT_ENCODING


def save_jsonl(
    file_path: str,
    data: list[Dataclass | dict] | dict,
    encoding: str = DEFAULT_ENCODING,
):
    """
    Save a list of dataclasses or dictionaries to a JSONLines file.

    Parameters
    ----------
    file_path: str
    data: list[Dataclass | dict] | dict
    encoding: str = DEFAULT_ENCODING
    """
    if not isinstance(data, list):
        data = [data]

    with open(file=file_path, mode="w", encoding=encoding) as file:
        for idx, item in enumerate(data):
            if is_dataclass(item) and not isinstance(item, type):
                item_dict = asdict(item)
                item_dict[_JLDC_DATACLASS] = str(item.__class__.__name__)
            elif isinstance(item, dict):
                item_dict = item
            else:
                raise TypeError(
                    "Can only write Dataclass or dict objects to file. Type %s unsupported",
                    type(item),
                )

            item_json = json.dumps(item_dict, cls=JLDCEncoder)
            file.write(item_json + "\n")


def _decode_json(
    _json: str,
    class_map: dict[str, Dataclass],
) -> Dataclass | dict:
    """
    Decode a JSON string into the original object, either a
    dataclass (from the map provided) or a dictionary.

    Parameters
    ----------
    _json: str
    class_map: dict[str, Dataclass]

    Returns
    -------
    Dataclass | dict
        The decoded JSON, as either a dataclass or dictionary.
    """
    line_dict = json.loads(_json, cls=JLDCDecoder)
    if (_cls := line_dict.get(_JLDC_DATACLASS)) and _cls in class_map:
        line_dict.pop(_JLDC_DATACLASS)
        try:
            return from_dict(data_class=class_map[_cls], data=line_dict)
        except DaciteError:
            pass

    return line_dict


def _get_class_map(
    classes: list[Dataclass] | Dataclass | None,
) -> dict[str, Dataclass]:
    """
    Convert the given class or classes, to a map necessary when
    decoding dataclasses from JSON.

    Parameters
    ----------
    classes: list[Dataclass] | Dataclass | None

    Returns
    -------
    dict[str, Dataclass]
        Mapping of dataclass names -> dataclass types.
    """
    classes = classes or []
    if not isinstance(classes, list):
        classes = [classes]

    return {_cl.__name__: _cl for _cl in classes}


def load_jsonl(
    file_path: str,
    classes: list[Dataclass] | Dataclass | None = None,
    encoding: str = DEFAULT_ENCODING,
) -> list[Dataclass | dict]:
    """
    Load a JSONLines file at once, decoding any dataclasses back to their original form.

    Parameters
    ----------
    file_path: str
    classes: list[Dataclass] | Dataclass | None = None
    encoding: str = DEFAULT_ENCODING

    Returns
    -------
    list[Dataclass | dict]
        List of data loaded from file.
    """
    class_map = _get_class_map(classes=classes)

    with open(file=file_path, mode="r", encoding=encoding) as file:
        return [
            _decode_json(
                _json=line,
                class_map=class_map,
            )
            for line in file
        ]


def iter_jsonl(
    file_path: str,
    classes: list[Dataclass] | Dataclass | None = None,
    encoding: str = DEFAULT_ENCODING,
) -> Iterator[Dataclass | dict]:
    """
    Load a JSONLines file line-by-line, decoding any dataclasses back to their original form.

    Parameters
    ----------
    file_path: str
    classes: list[Dataclass] | Dataclass | None = None
    encoding: str = DEFAULT_ENCODING

    Returns
    -------
    Iterator[Dataclass | dict]
        Iterator of data loaded from file.
    """
    class_map = _get_class_map(classes=classes)

    with open(file=file_path, mode="r", encoding=encoding) as file:
        for line in file:
            yield _decode_json(
                _json=line,
                class_map=class_map,
            )
