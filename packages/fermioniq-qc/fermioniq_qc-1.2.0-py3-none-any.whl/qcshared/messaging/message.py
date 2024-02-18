import json
from typing import Any, Optional

from ..json.encode import CustomEncoder


class ClientMessage:
    """Base class for messages to be sent / displayed by the client."""

    def __init__(self, content_dict: dict[str, Any]):
        assert isinstance(content_dict, dict)
        self.content_dict = content_dict

    @classmethod
    def from_dict(cls, content_dict: dict[str, Any]):
        return cls(content_dict)

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except:
            return self.content_dict[__name]

    def __setattr__(self, __name: str, __value: Any) -> None:
        try:
            super().__setattr__(__name, __value)
        except:
            self.content_dict[__name] = __value

    def __str__(self):
        return json.dumps(
            {
                "__ClientMessage__": {
                    "name": str(self.__class__.__name__),
                    "content": self.content_dict,
                }
            },
            cls=CustomEncoder,
        )


class StringMessage(ClientMessage):
    """Class for generic messages."""

    def __init__(self, message: str):
        assert isinstance(message, str)
        super().__init__({"message": message})

    @classmethod
    def from_dict(cls, content_dict: dict[str, Any]):
        return cls(content_dict["message"])


class ProgressMessage(ClientMessage):
    """Class for progress update messages. The ``progress_step`` is a float between 0 and 1."""

    def __init__(
        self,
        progress_step: float,
        abs_progress: float,
        label: Optional[str] = None,
        finished: bool = False,
    ):
        assert isinstance(progress_step, float)
        assert label is None or isinstance(label, str)
        if not (0.0 <= progress_step <= 1.0):
            raise ValueError(
                f"Parameter for ProgressMessage: progress_step should be a float between 0 and 1 (got {progress_step})."
            )
        if not (0.0 <= abs_progress <= 1.0):
            raise ValueError(
                f"Parameter for ProgressMessage: abs_progress should be a float between 0 and 1 (got {abs_progress})."
            )
        super().__init__(
            {
                "progress_step": progress_step,
                "abs_progress": abs_progress,
                "label": label,
                "finished": finished,
            }
        )

    @classmethod
    def from_dict(cls, content_dict: dict[str, Any]) -> "ProgressMessage":
        return cls(
            content_dict["progress_step"],
            content_dict["abs_progress"],
            content_dict.get("label", None),
            content_dict.get("finished", False),
        )


class ConfigMessage(ClientMessage):
    """Class for config warnings, errors, and successes."""

    def __init__(self, warnings: list, errors: list):
        assert isinstance(warnings, list) and isinstance(errors, list)
        super().__init__({"warnings": warnings, "errors": errors})

    @classmethod
    def from_dict(cls, content_dict: dict[str, Any]):
        return cls(content_dict["warnings"], content_dict["errors"])


class ErrorMessage(ClientMessage):
    """Class for (generic) errors."""

    def __init__(self, message: str, error_type: Optional[str] = None):
        assert isinstance(message, str)
        assert error_type is None or isinstance(error_type, str)
        super().__init__({"message": message, "error_type": error_type})

    @classmethod
    def from_dict(cls, content_dict: dict[str, Any]):
        return cls(content_dict["message"], content_dict.get("error_type", None))
