import warnings
from typing import Any, Optional

from pydantic import StrictInt, StrictStr, root_validator, validator

from .config_utils import BaseConfig, ConfigWarning
from .constants import MAX_BITSTRINGS, MAX_QUBITS_FOR_FULL_OUTPUT, MAX_SHOTS


class ExpectationValuesOutputConfig(BaseConfig):
    enabled: bool = False
    observables: list[dict[str, Any]] = []

    @validator("observables")
    def validate_observables(cls, observables, values):
        if not values["enabled"]:
            return observables

        value_error_bad_format_pauli_sum = ValueError(
            "Observables must be provided as a list of dicts of the form {'name': <name>, 'serialized_observables': <serialized_observables>}."
        )
        value_error_bad_format_pauli_obs = ValueError(
            "Each serialized_observable must be a dict of the form {'paulis': <paulis>, 'coeff': <coeff>}."
        )

        for observable in observables:
            if set(observable.keys()) != {"serialized_observables", "name"}:
                raise value_error_bad_format_pauli_sum
            if not isinstance(observable["name"], str):
                raise value_error_bad_format_pauli_sum
            if not isinstance(observable["serialized_observables"], list):
                raise value_error_bad_format_pauli_sum

            for ob in observable["serialized_observables"]:
                if set(ob.keys()) != {"paulis", "coeff"}:
                    raise value_error_bad_format_pauli_obs
                if not isinstance(ob["paulis"], dict):
                    raise value_error_bad_format_pauli_obs
                if not isinstance(
                    ob["coeff"], (complex, float, int)
                ):  # int and float are acceptable
                    raise value_error_bad_format_pauli_obs

                if any([p not in ["X", "Y", "Z"] for p in ob["paulis"].values()]):
                    raise ValueError("Pauli operators must be 'X', 'Y', or 'Z'")

        return observables


class AmplitudesOutputConfig(BaseConfig):
    enabled: bool = False

    # Note the strict types to prevent coercion
    bitstrings: list[StrictStr] | list[StrictInt] | str = [0]

    @validator("bitstrings", pre=True)
    def validate_bitstrings_maxlen(cls, bitstrings, values):
        """Pre-check for too long list of bitstrings"""
        if len(set(bitstrings)) > MAX_BITSTRINGS:
            raise ValueError(
                f"The number of amplitudes requested is {len(bitstrings)}, which is "
                "beyond the supported limit of {MAX_BITSTRINGS}."
            )
        return bitstrings

    @validator("bitstrings")
    def validate_bitstrings(cls, bitstrings, values):
        """Validates bitstrings

        Check:
            - If provided as strings, each string contains only 0s and 1s
            - If provided as ints, each integer is positive
            - Bitstrings are indeed provided as a list of ints or a list of strs
                (this should already be checked by type-checking)
        """
        err_location = ["emulator_config", "output", "amplitudes", "bitstrings"]

        # Check that some bitstrings were provided
        if len(bitstrings) == 0:
            if values.get("enabled"):
                raise ValueError(
                    "You must provide at least one bitstring, or set bitstrings = 'all' "
                    "if computing amplitudes as output. "
                    f"Warning: Only do this for up to {MAX_QUBITS_FOR_FULL_OUTPUT} qubits."
                )
            else:
                err_msg = (
                    "You should provide at least one bitstring, or set bitstrings = 'all' "
                    "if computing amplitudes as output. "
                    "This will cause an error if computing amplitudes is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )

        # If bitstrings are given as strings, then check that there are no non-binary values in there
        if isinstance(bitstrings, list) and all(
            isinstance(bs, str) for bs in bitstrings
        ):
            if any(b not in ("0", "1") for bs in bitstrings for b in bs):
                if values.get("enabled"):
                    raise ValueError(
                        "Encountered non-binary value in bitstrings provided."
                    )
                else:
                    err_msg = (
                        "Encountered non-binary value in bitstrings provided."
                        "This will cause an error if computing amplitudes is enabled."
                    )
                    warnings.warn(
                        ConfigWarning(
                            err_location,
                            "Potential source of error",
                            err_msg,
                        )
                    )

        # If bitstrings is a list of ints, check that there are no negative values
        elif isinstance(bitstrings, list) and all(
            isinstance(bs, int) for bs in bitstrings
        ):
            if any(bs < 0 for bs in bitstrings):
                if values.get("enabled"):
                    raise ValueError("Encountered negative value in bitstrings.")
                else:
                    err_msg = (
                        "Encountered negative value in bitstrings."
                        "This will cause an error if computing amplitudes is enabled."
                    )
                    warnings.warn(
                        ConfigWarning(
                            err_location,
                            "Potential source of error",
                            err_msg,
                        )
                    )

        # If bitstrings is a string, check that it is "all" (the only valid setting in this case)
        elif isinstance(bitstrings, str) and bitstrings != "all":
            if values.get("enabled"):
                raise ValueError(
                    "Bitstrings must be one of: 'all', a list of integers, or a list of strings."
                )
            else:
                err_msg = (
                    "Bitstrings must be one of: 'all', a list of integers, or a list of strings."
                    "This will cause an error if computing amplitudes is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )

        # Check that bitstrings are unique, raising a warning if not (this won't cause errors).
        if isinstance(bitstrings, list) and len(set(bitstrings)) != len(bitstrings):
            bitstrings = [b for b in set(bitstrings)]
            err_msg = (
                "Bitstrings provided are not unique. Removed all duplicate bitstrings."
            )
            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Redundant input",
                    err_msg,
                )
            )
        return bitstrings


class SampleOutputConfig(BaseConfig):
    enabled: bool = True
    n_shots: Optional[int] = 1000
    return_probabilities: bool = False

    @validator("n_shots", pre=True)
    def validate_n_shots(cls, n_shots, values):
        err_location = ["emulator_config", "output", "sampling", "n_shots"]
        if values.get("enabled") and n_shots is None:
            raise ValueError(
                "You must provide a number of shots if using sampling as output."
            )
        if n_shots is not None and n_shots < 0:
            if values.get("enabled"):
                raise ValueError(f"Invalid number of shots {n_shots} (negative value).")
            else:
                err_msg = (
                    f"Invalid number of shots {n_shots} (negative value). "
                    "This will cause an error if sampling output is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )
        elif n_shots is not None and n_shots > MAX_SHOTS:
            if values.get("enabled"):
                raise ValueError(
                    f"Invalid number of shots {n_shots} (Surpasses limit of {MAX_SHOTS})."
                )
            else:
                err_msg = (
                    f"Invalid number of shots {n_shots} (Surpasses limit of {MAX_SHOTS}). "
                    "This will cause an error if sampling output is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )
        return n_shots


class MpsOutputConfig(BaseConfig):
    enabled: bool = False


class OutputConfig(BaseConfig):
    amplitudes: AmplitudesOutputConfig = AmplitudesOutputConfig()
    sampling: SampleOutputConfig = SampleOutputConfig()
    mps: MpsOutputConfig = MpsOutputConfig()
    expectation_values: ExpectationValuesOutputConfig = ExpectationValuesOutputConfig()

    @root_validator(pre=True)
    def validate_all2(cls, vals):
        return vals

    @root_validator(pre=False)
    def validate_all(cls, vals):
        amplitudes = vals.get("amplitudes")
        sampling = vals.get("sampling")
        mps = vals.get("mps")
        expvals = vals.get("expectation_values")

        if amplitudes is None or sampling is None or mps is None or expvals is None:
            return None

        if not any(
            [amplitudes.enabled, sampling.enabled, mps.enabled, expvals.enabled]
        ):
            raise ValueError("There are no output modes enabled.")
        return vals
