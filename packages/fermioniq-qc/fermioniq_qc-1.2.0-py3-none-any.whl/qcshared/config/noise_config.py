from pydantic import Field, validator

from .config_utils import BaseConfig


class NoiseConfig(BaseConfig):
    # Is set to True in EmulatorInput if a noise model is given. No Pydantic checks should depend on this attribute
    enabled: bool = Field(
        description="Whether noise is turned on or not. Is set to True automatically if a noise model is given",
        default=False,
    )
    validate_model: bool = Field(
        description="Whether to validate the noise model against the circuit or not. "
        "This involves checking that every gate in the circuit triggers some noise channels,"
        "and that all qubits defined in the config (not necessarily the circuit) have "
        "some readout error defined. Default is True.",
        default=True,
    )
