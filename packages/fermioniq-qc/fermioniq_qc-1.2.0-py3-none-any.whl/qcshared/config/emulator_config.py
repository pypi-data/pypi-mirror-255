import re
import warnings
from typing import Optional

import numpy as np
from pydantic import Field, validator

from .config_utils import BaseConfig, ConfigWarning
from .constants import MAX_BITSTRINGS, MAX_QUBITS_FOR_FULL_OUTPUT
from .dmrg_config import DMRGConfig
from .noise_config import NoiseConfig
from .optimizer_config import OptimizerConfig
from .output_config import OutputConfig
from .tebd_config import TEBDConfig


class EmulatorConfig(BaseConfig):
    """This is a class for the emulator config.

    It does not know about the circuit or noise model.
    """

    qubits: list[str] = Field(description="Qubit objects", unique_items=True)
    grouping: Optional[list[list[str]]] = Field(
        default=None,
        description="Grouping of qubits as a list of lists. If None, groups will be generated"
        "automatically, with a group size given by group_size.",
    )
    group_size: Optional[int] = Field(
        default=None, description="Size of groups", ge=1, le=20
    )
    physical_dimensions: tuple[int, ...] = ()
    initial_state: int | list[int] = 0
    mode: str = Field(
        default="dmrg", description="Emulation mode. Supported: 'dmrg', 'tebd'"
    )
    noise: NoiseConfig = NoiseConfig()
    tebd: TEBDConfig = TEBDConfig()
    dmrg: DMRGConfig = DMRGConfig()
    output: OutputConfig = OutputConfig()
    optimizer: OptimizerConfig = OptimizerConfig()

    # TODO doesn't support physical dimensions beyond 2 yet
    @validator("initial_state", pre=True)
    def string_to_int_list(cls, initial_state, values):
        """If initial state is a string, check that it's a
        string of integers, and convert it to a list of
        integers.
        """
        if isinstance(initial_state, str):
            if not bool(re.match(r"^[01]+$", initial_state)):
                raise ValueError(
                    "initial_state is a string containing other characters than '0' and '1', this is currently not supported."
                )
            return [int(bit) for bit in initial_state]

        return initial_state

    @validator("physical_dimensions", pre=True)
    def list_to_tuple(cls, physical_dimensions, values):
        """
        Converts physical_dimensions to a tuple if it is a list.
        """
        if isinstance(physical_dimensions, list):
            return tuple(physical_dimensions)
        return physical_dimensions

    @validator("grouping", always=True)
    def validate_grouping(cls, grouping, values):
        """Validates grouping

        Check:
            - Qubit grouping includes all qubits in 'qubits'
            - There are no duplicate qubits in the grouping
        """
        if "qubits" not in values:
            # Avoid validation type error in 'qubits'
            return grouping

        if grouping is None:
            return grouping

        flat_grouping = [g for group in grouping for g in group]
        if any(g not in values.get("qubits") for group in grouping for g in group):
            raise ValueError("Qubit found in grouping that wasn't found in 'qubits'.")
        elif set(flat_grouping) != set(values.get("qubits")):
            raise ValueError("Qubit found in 'qubits' that wasn't found in grouping.")
        if len(set(flat_grouping)) != len(flat_grouping):
            raise ValueError("A qubit appears twice in the grouping.")

        return grouping

    @validator("group_size", always=True)
    def validate_group_size(cls, group_size, values):
        """Validates group_size."""
        if group_size is None:
            if not values.get("grouping"):
                raise ValueError("One of group_size or grouping must be given.")
            return None

        if "qubits" not in values:
            # Avoid validation type error in 'qubits'
            return group_size

        if values.get("grouping"):
            err_location = ["emulator_config", "grouping"]
            err_msg = (
                "Only one of grouping or group_size should be set at any one time. "
                "group_size will be overriden by grouping."
            )
            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Set to default value",
                    err_msg,
                )
            )
            return max(len(group) for group in values["grouping"])

        # If the group size was too big, make it small enough and raise a warning
        if group_size > len(values["qubits"]):
            err_location = ["emulator_config", "group_size"]
            err_msg = "Group_size requested is more than the number of qubits."
            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Set to valid value.",
                    err_msg,
                )
            )
            return len(values["qubits"])

        return group_size

    # Always is True so that this validator is applied, even if no 'dmrg' dict and default DMRGConfig is generated
    @validator("dmrg", always=True)
    def validate_dmrg(cls, dmrg, values):
        """
        Validates config for dmrg
        """
        if "mode" not in values or values["mode"] != "dmrg":
            return dmrg

        if dmrg.convergence_window_size is None:
            # If the grouping wasn't set, use the group_size to infer a window size
            if "grouping" not in values or values["grouping"] is None:
                # Quick exit if neither group_size or grouping is set (this will be caught earlier up)
                if values["group_size"] is None:
                    return dmrg
                window_size = 2 * len(values["qubits"]) // values["group_size"]
            else:
                window_size = 2 * len(values["grouping"])

            dmrg.convergence_window_size = window_size

            err_location = ["emulator_config", "dmrg", "convergence_window_size"]
            err_msg = (
                "convergence_window_size is None': set window_size to the number of qubit groups"
                f"\nResulting window size: {dmrg.convergence_window_size}."
            )

            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Set to default value",
                    err_msg,
                )
            )
        return dmrg

    # TODO doesn't support physical dimensions beyond 2 yet
    @validator("physical_dimensions", always=True)
    def validate_physical_dimensions(cls, physical_dims, values):
        """
        Check that physical_dims is empty, and fill with dimension 2.
        This function can be extended to allow for custom physical dimensions
        """
        if physical_dims and not all(dim == 2 for dim in physical_dims):
            raise ValueError("Custom physical dimensions are currently not supported")

        if "qubits" not in values:
            return ()

        return tuple(2 for _ in range(len(values["qubits"])))

    @validator("initial_state")
    def validate_initial_state(cls, initial_state, values):
        """Validates initial_state

        Check:
            - That the initial state is achievable (positive)
            - That the initial state matches the physical dimensions
        """
        if "physical_dimensions" not in values or not values["physical_dimensions"]:
            return None

        physical_dims = values["physical_dimensions"]
        n_qubits = len(physical_dims)

        if isinstance(initial_state, int):
            maximal_state = np.prod(physical_dims) - 1
            if initial_state < 0:
                raise ValueError(
                    f"Invalid initial state: {initial_state} (negative value)."
                )
            elif initial_state > 0 and initial_state > maximal_state:
                raise ValueError(
                    f"Invalid initial state: {initial_state} "
                    f"(not possible with {n_qubits} qubits) of dimensions {physical_dims})"
                )
        elif isinstance(initial_state, list):
            if len(initial_state) != n_qubits:
                raise ValueError(
                    f"Invalid initial state: {initial_state} "
                    f"(not possible with {n_qubits} qubits)."
                )
            elif any(
                s < 0 or s >= physical_dims[i] for i, s in enumerate(initial_state)
            ):
                raise ValueError(
                    f"Invalid physical value found in initial state: {initial_state} (for physical dimensions {physical_dims})"
                )
        else:
            return None

        return initial_state

    @validator("mode")
    def validate_mode(cls, mode, values):
        """Check:
        - Mode is supported
        - For mode 'dmrg', emulation must be performed on more than 1 group.
        - For mode 'tebd' a grouping must be given.
        """
        if "qubits" not in values:
            return mode

        supported_modes = ["tebd", "dmrg"]
        if mode not in supported_modes:
            raise ValueError(f"Invalid emulation mode provided ('{mode}').")

        if mode == "dmrg":
            if (
                "grouping" in values
                and values["grouping"] is not None
                and len(values["grouping"]) == 1
            ):
                raise ValueError(
                    "DMRG is not supported for a single group (MPS of length 1), use mode 'tebd' instead"
                )
            if (
                ("grouping" not in values or values["grouping"] is None)
                and "group_size" in values
                and values["group_size"] >= len(values["qubits"])
            ):
                raise ValueError(
                    "DMRG is not supported for a single group (MPS of length 1), but the maximum group size is larger or equal to the number of qubits"
                )

        if mode == "tebd" and "grouping" in values and values["grouping"] is None:
            raise ValueError(
                "Automatic grouping is not supported for emulation mode 'tebd'. Please set a grouping."
            )

        return mode

    @validator("output", always=True)
    def validate_output(cls, v, values, **kwargs):
        """Validates the output amplitudes agains 'qubits'

        This checks the following:
            - Number of qubits in each bitstring (int or string) match the number
                defined in ``qubits``
            - Number of bitstrings does not exceed ``MAX_BITSTRINGS``
            - Observables, if provided, act only on qubits existing in ``qubits``
            - Full MPS is only returned if bond dimensions <= 100, n_qubits <= 10.
        """
        # If amplitude output or observables output or mps output are not enabled, we don't do any checking
        if not (v.amplitudes.enabled or v.expectation_values.enabled or v.mps.enabled):
            return v

        # (try to) get 'qubits' and the number of qubits
        try:
            qubits = values["qubits"]
            n_qubits = len(set(qubits))
        except KeyError:
            return v

        # Validate amplitudes
        if v.amplitudes.enabled:
            bitstrings = v.amplitudes.bitstrings
            if isinstance(bitstrings, list):
                if all(isinstance(bs, str) for bs in bitstrings) and not all(
                    len(bs) == len(qubits) for bs in bitstrings
                ):
                    raise ValueError(
                        "The bitstrings for which amplitudes are to be computed do not "
                        f"match the number of qubits in 'qubits', given by: ({qubits})."
                    )
                elif all(isinstance(bs, int) for bs in bitstrings) and any(
                    bs > 0 and np.log2(bs) > len(qubits) for bs in bitstrings
                ):
                    raise ValueError(
                        "The basis state values for which amplitudes are to be computed are "
                        f"not compatible with the number of qubits in 'qubits', given by: ({qubits})."
                    )
            elif (
                isinstance(bitstrings, str)
                and bitstrings == "all"
                and n_qubits > MAX_QUBITS_FOR_FULL_OUTPUT
            ):
                raise ValueError(
                    f"Setting bitstrings to 'all' will generate {2**n_qubits} amplitudes, "
                    f"which is beyond the supported limit of {MAX_BITSTRINGS}. "
                    "The use of setting 'all' is only supported for up to "
                    f"{MAX_QUBITS_FOR_FULL_OUTPUT} qubits."
                )

        if v.expectation_values.enabled:
            # Check that each observable acts only on qubits in the qubit order
            for obs in v.expectation_values.observables:
                for pauli_obs in obs["serialized_observables"]:
                    if not all(q in qubits for q in pauli_obs["paulis"].keys()):
                        missing_qubits = [
                            q for q in pauli_obs["paulis"].keys() if q not in qubits
                        ]
                        raise ValueError(
                            f"Observable {obs['name']} acts on qubits ({missing_qubits}) not found in qubit order."
                        )

        if v.mps.enabled:
            if "mode" not in values:
                return v

            mode = values["mode"]

            if mode == "dmrg" or mode == "tebd":
                if mode == "dmrg":
                    bond_dims = values["dmrg"].D
                else:
                    bond_dims = values["tebd"].max_D

                if isinstance(bond_dims, int):
                    bond_dims = [bond_dims]

                if not (all(b <= 100 for b in bond_dims) and n_qubits <= 10):
                    raise ValueError(
                        "The full MPS can only be returned as output if bond dimension is less or equal than 100 and the number of qubits is less or equal than 10"
                    )

        return v
