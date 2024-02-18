from pydantic import Field

from .config_utils import BaseConfig
from .constants import MAX_BOND_DIM


class TEBDConfig(BaseConfig):
    max_D: int | list[int] = Field(default=2, ge=1, le=MAX_BOND_DIM)
    svd_cutoff: float = Field(
        default=1e-8,
        description="Threshold below which singular values are truncated",
        gt=0.0,
        lt=1.0,
    )
