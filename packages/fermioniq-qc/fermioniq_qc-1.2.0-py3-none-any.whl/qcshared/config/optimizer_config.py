from numbers import Number
from typing import Any, Literal, Optional

from pydantic import StrictStr, validator

from .config_utils import BaseConfig


class SPSAConfig(BaseConfig):
    learning_rate: float = 5
    learning_rate_exponent: float = 0.6
    perturbation: float = 1e-2
    perturbation_exponent: float = 0.1
    eps: float = 1e-14
    max_iter: int = 100
    params_tol: float = 1e-8
    fun_tol: float = 1e-7


class SerializedObservableConfig(BaseConfig):
    paulis: dict[str, Literal["X", "Y", "Z"]]
    coeff: Any  # (int | float | complex)

    @validator("coeff")
    def validate_coeff(cls, coeff):
        if not isinstance(coeff, Number):
            raise ValueError("Pauli operator coefficient should be a number")
        return coeff


class ObservableConfig(BaseConfig):
    name: StrictStr
    serialized_observables: list[SerializedObservableConfig]


class OptimizerConfig(BaseConfig):
    enabled: bool = False
    observable: Optional[ObservableConfig] = None
    optimizer: Literal["spsa"] = "spsa"
    evaluation_mode: Literal["contract"] = "contract"
    optimizer_name: Literal["spsa"] = "spsa"
    optimizer_settings: SPSAConfig = SPSAConfig()

    @validator("observable", always=True, pre=True)
    def validate_observable(cls, observable, values):
        if values["enabled"] and observable is None:
            raise ValueError("If optimizer is enabled, an observable must be specified")

        if not values["enabled"]:
            return None
        return observable
