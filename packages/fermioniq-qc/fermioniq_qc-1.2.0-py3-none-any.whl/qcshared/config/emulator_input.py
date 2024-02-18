import logging
from typing import Any, Optional

from pydantic import ValidationError, validator

from ..json.decode import dejsonify
from ..json.encode import jsonify
from ..messaging.message import ConfigMessage
from ..noise_models import ANY, NoiseModel, QubitInternal
from .config_utils import BaseConfigWithWarning
from .constants import MPO_BOND_DIM_NO_NOISE, MPO_BOND_DIM_WITH_NOISE
from .emulator_config import EmulatorConfig


def validate_input(
    circuit: list[dict],
    config: dict[str, Any],
    noise_model: Optional[dict],
    print_warnings: bool = False,
) -> "EmulatorInput":
    """Validates the emulator input against the emulator config, and returns the validated input.

    :param circuit: The circuit
    :param config: The emulator config
    :param noise_model: The noise model
    :param print_warnings: Whether to print warnings or not

    :return: The validated emulator input
    """
    try:
        emulator_input = EmulatorInput(
            emulator_config=config, circuit=circuit, noise_model=noise_model  # type: ignore
        )
        if emulator_input._warnings:
            warnings = list(set(emulator_input._warnings))
            if print_warnings:
                logging.warning(ConfigMessage(warnings, []))

        return emulator_input
    except ValidationError as e:
        logging.error(ConfigMessage([], e.errors()))
        print(e.errors())
        raise e


def validate_input_batch(
    emulator_inputs: list[tuple[list[dict], dict[str, Any], Optional[dict]]]
) -> list["EmulatorInput"]:
    """Validates a batch of emulator inputs against the emulator config, and returns the validated inputs.

    Note that to use this function with multiprocessing, it can only take a single argument, which is why
    it does that, and as a first step unpacks that single argument into three below.
    """
    circuits = [emulator_input[0] for emulator_input in emulator_inputs]
    configs = [emulator_input[1] for emulator_input in emulator_inputs]
    noise_dicts = [emulator_input[2] for emulator_input in emulator_inputs]
    return list(map(validate_input, circuits, configs, noise_dicts))


class EmulatorInput(BaseConfigWithWarning):
    """This is a class for the emulator input.

    It knows about the emulator config, the circuit, and the noise model, and can validate
    these against each other.
    """

    circuit: list[dict]
    emulator_config: EmulatorConfig
    noise_model: Optional[NoiseModel]

    # TODO: should validate more
    @validator("circuit", always=True)
    def validate_payload(cls, v, values):
        """Validation of the payload structure, and conversion to tuple"""
        for gate_dict in v:
            try:
                qubits = gate_dict["qubits"]
                assert isinstance(qubits, list) or isinstance(qubits, tuple)
                gate_dict["qubits"] = tuple(qubits)
            except:
                raise ValueError(
                    "Not all items in the payload have a 'qubits' field containing a list or tuple of labels"
                )
            if "name" not in gate_dict or "label" not in gate_dict:
                raise ValueError(
                    "Not all items in the payload have a 'name' and 'label' field"
                )
        return v

    @validator("emulator_config")
    def validate_config_circuit(cls, v, values, **kwargs):
        """Post-validation on circuit + config"""
        try:
            circuit = values["circuit"]
        except KeyError:
            return v
        circuit_qubits = qubits_in_circuit(circuit)

        if any(q not in v.qubits for q in circuit_qubits):
            erronous_qubits = (q for q in circuit_qubits if q not in v.qubits)
            raise ValueError(
                "The circuit acts on one or more erronous qubits that are not contained in "
                f"'qubits'. Erronous qubits: {','.join(erronous_qubits)}"
            )

        if v.mode == "tebd" and long_range_gates(circuit, v.grouping):
            raise ValueError(
                "Emulation mode tebd cannot be used when there are long-range gates in "
                "the circuit. Please adjust the grouping or use a different emulation "
                "mode (e.g. dmrg)."
            )
        return v

    @validator("noise_model", always=True)
    def validate_noise_model(cls, v, values, **kwargs):
        """
        Validates the noise model against the config and circuit.

        Checks:
        - If no mpo_bond_dim has been specified for 'dmrg', this is filled with a default, depending on the existence
            of a noise model.
        - If a noise model is given, the noise 'enabled' flag is set to true, for later output processing.
        - If a noise model is given, the mpo_bond_dim must be >= 16. otherwise it should be >= 4.
        - If the noise config specifies to validate the noise model, then the noise model must be valid, which means:
            - Every gate in the circuit must trigger some noise channels
            - All qubits defined in the config (not necessarily the circuit) must have some readout error defined

        """
        # Exit early if the circuit and/or emulator config already failed to validate
        if not ("circuit" in values and "emulator_config" in values):
            return v

        # No noise model given
        if v is None:
            if values["emulator_config"].mode == "dmrg":
                if values["emulator_config"].dmrg.mpo_bond_dim is None:
                    values["emulator_config"].dmrg.mpo_bond_dim = MPO_BOND_DIM_NO_NOISE
                elif values["emulator_config"].dmrg.mpo_bond_dim < 4:
                    raise ValueError(
                        "MPO bond dim. should be at least 4 for noiseless emulation."
                    )

        # A noise model is given
        else:
            # Set private noise flag in config
            values["emulator_config"].noise.enabled = True

            # Set MPO bond dim to noisy default, or check that the given value >=16
            if values["emulator_config"].mode == "dmrg":
                if values["emulator_config"].dmrg.mpo_bond_dim is None:
                    values[
                        "emulator_config"
                    ].dmrg.mpo_bond_dim = MPO_BOND_DIM_WITH_NOISE

                elif values["emulator_config"].dmrg.mpo_bond_dim < 16:
                    raise ValueError(
                        "MPO bond dim. should be at least 16 for noisy emulation."
                    )

            # If validation is turned on (default), validate the noise model
            if values["emulator_config"].noise.validate_model:
                validate_noise_model_against_qubits(
                    noise_model=v, qubits=values["emulator_config"].qubits
                )
                validate_noise_model_against_circuit(
                    noise_model=v, circuit=values["circuit"]
                )

        return v


def validate_noise_model_against_qubits(noise_model: NoiseModel, qubits: list[str]):
    """Check that all qubits exist in the noise model, and that there exists readout error for all qubits."""

    noise_model_qubit_strings = noise_model.qubit_strings
    for q in qubits:
        if q not in noise_model_qubit_strings:
            raise ValueError(
                f"Qubit {q} is listed in the config, but is not contained in the noise model."
            )

    remaining_qubits = set(qubits)
    for q, _ in noise_model.readout_errors:
        if q in remaining_qubits:
            remaining_qubits.remove(q)
        if q == ANY:
            remaining_qubits.clear()

    if len(remaining_qubits) > 0:
        raise ValueError(
            f"Readout error for qubits {remaining_qubits} are not defined in the noise model, and there is no generic entry (with ANY)."
        )


def validate_noise_model_against_circuit(noise_model: NoiseModel, circuit: list[dict]):
    """Check that there exists a noise trigger for every gate in the circuit."""
    noise = noise_model.on_circuit(circuit)
    # If there was any missing noise, return an error
    if len(noise["missing_noise"]) > 0:
        raise ValueError(
            f"The following gates in the circuit do not trigger any noise channels: {noise['missing_noise']}"
        )


def long_range_gates(gatelist: list[dict], grouping: list[list[str]]) -> bool:
    """Checks if there are any long-range gates in a list

    Given a gatelist (as a dict) and a qubit grouping, detect any long-range gates,
    where long-range means acting over any non-adjacent groups
    """
    for gate in gatelist:
        gate_qubits = gate["qubits"]
        if len(gate_qubits) == 1:
            continue
        groups_involved = [
            i for i, g in enumerate(grouping) for q in gate_qubits if q in g
        ]
        long_range = any(
            (abs(i - j) > 1 for i in groups_involved for j in groups_involved)
        )
        if long_range:
            return True
    return False


def qubits_in_circuit(gatelist: list[dict]) -> set[str]:
    return {q for gate in gatelist for q in gate["qubits"]}
