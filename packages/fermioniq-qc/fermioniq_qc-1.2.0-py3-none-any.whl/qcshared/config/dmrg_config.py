from typing import Optional

from pydantic import Field, validator

from .config_utils import BaseConfig
from .constants import MAX_BOND_DIM, MAX_CUT_DIM, MAX_SWEEPS


class DMRGConfig(BaseConfig):
    D: int | list[int] = Field(default=2, ge=1, le=MAX_BOND_DIM)
    init_mode: str = "ket"
    convergence_window_size: Optional[int] = Field(
        default=None,
        description="Number of fidelities to inspect for convergence",
        ge=2,
        le=1000,
    )
    convergence_threshold: float = Field(
        default=1e-5, description="Threshold for convergence", ge=0.0, le=1.0
    )
    target_fidelity: float = Field(
        default=1.0, description="Target fidelity to reach", ge=0.0, le=1.0
    )
    max_sweeps: int = Field(
        default=int(1e4), description="Maximum number of sweeps", ge=1, le=MAX_SWEEPS
    )
    max_subcircuit_rows: int = Field(default=1, ge=1, le=10)
    mpo_bond_dim: Optional[int] = Field(default=None, ge=4, le=1024)
    regular_grid: bool = True
    truncate_rows: bool = True

    @validator("init_mode")
    def validate_init_mode(cls, init_mode):
        if init_mode not in ["ket", "random", "tebd", "lowerD"]:
            raise ValueError(
                f"Unsupported / unrecognized initialization mode for dmrg ({init_mode})."
            )
        return init_mode

    @validator("mpo_bond_dim", always=True)
    def validate_mpo_bond_dim(cls, mpo_bond_dim, values):
        if "max_subcircuit_rows" not in values or mpo_bond_dim is None:
            return mpo_bond_dim

        # Check that this combination of mpo_bond_dim and max_subcircuit_rows doesn't go beyond
        #  the max_cut_dim that we allow
        max_cut = mpo_bond_dim ** values["max_subcircuit_rows"]

        if max_cut > MAX_CUT_DIM:
            raise ValueError(
                f"Product of mpo_bond_dim {mpo_bond_dim} and max_subcircuit_rows {values['max_subcircuit_rows']} exceeds the maximum of {MAX_CUT_DIM}."
            )
        return mpo_bond_dim
