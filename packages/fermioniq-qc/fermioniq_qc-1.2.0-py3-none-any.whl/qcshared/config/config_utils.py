import warnings

from pydantic import Extra, PrivateAttr
from rich import box, print
from rich.panel import Panel
from rich.table import Table

from ..pydantic.models import BaseConfig


class ConfigWarning(Warning):
    def __init__(self, loc: list[str], type: str, msg: str):
        self.loc = loc
        self.type = type
        self.msg = msg

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        setattr(self, key, val)

    class Config:
        extra = Extra.forbid


class BaseConfigWithWarning(BaseConfig):
    """Class extending the BaseModel class of pydantic to capture and store warnings"""

    _warnings: list[str] = PrivateAttr()

    def __init__(self, **kwargs):
        with warnings.catch_warnings(record=True) as validation_warnings:
            # Only capture ConfigWarning instances, all other warnings are handled as usual
            warnings.simplefilter("always", category=ConfigWarning)
            # Continue with the initialization
            super().__init__(**kwargs)
            self._warnings = [
                vw.message
                for vw in validation_warnings
                if isinstance(vw, ConfigWarning)
            ]


def recursive_dict_update(d: dict, u: dict) -> dict:
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = recursive_dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def print_error_warning_table(
    title: str,
    errors_warnings: list,
    title_color: str = "green",
) -> None:
    type_lookup = {
        "value_error": "Bad Value",
        "value_error.configwarning": "Value Warning",
        "type_error": "Wrong Type",
    }

    table = Table(box=box.SIMPLE_HEAD, show_lines=True)
    table.add_column("", justify="right", style="blue", no_wrap=True)
    table.add_column("[blue]Location", justify="right", style="blue", no_wrap=True)
    table.add_column("[magenta]Type", style="magenta", width=20)
    table.add_column("[magenta]Description", style="magenta", width=100)

    for idx, e in enumerate(errors_warnings):
        location_without_root = [loc for loc in e["loc"] if loc != "__root__"]
        location_str = " -> ".join(location_without_root)
        e_type_str = type_lookup.get(e["type"], e["type"])
        table.add_row(f"{idx+1}. ", location_str, e_type_str, e["msg"])

    print(
        Panel(
            table,
            expand=False,
            title=f"[{title_color}][b]{title}",
        )
    )
