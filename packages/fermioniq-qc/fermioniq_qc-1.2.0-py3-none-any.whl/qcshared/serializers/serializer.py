from typing import Any, Sequence

from ..observables.observables import Observable
from .cirq_serializer import (
    cirq_circuit_to_native_python,
    cirq_qubit_to_str,
    convert_cirq_pauli,
    default_qubits_cirq,
)
from .custom_types import (
    Circuit,
    CirqQubit,
    QiskitQubit,
    Qubit,
    is_cirq_circuit,
    is_cirq_pauli_string,
    is_cirq_pauli_sum,
    is_cirq_qubit,
    is_qiskit_circuit,
    is_qiskit_qubit,
    is_qiskit_sparse_pauli_op,
    is_sequence_of_cirq_qubit,
    is_sequence_of_qiskit_qubit,
)
from .qiskit_serializer import (
    convert_qiskit_sparse_pauli_op,
    default_qubits_qiskit,
    qiskit_circuit_to_native_python,
    qiskit_qubit_to_str,
)


def serialize_circuit(circuit) -> list[dict]:
    """Converts a circuit from a 3rd-party quantum programming framework to a serialized, native representation.
    Currently supported frameworks: Cirq, Qiskit.

    :param circuit: The circuit object.

    :returns:
        A serialization of the circuit (as a flat list of serialized gates).
        A dictionary mapping every qubit object in the circuit to a unique string identifier.

    """
    if is_qiskit_circuit(circuit):
        return qiskit_circuit_to_native_python(circuit)
    if is_cirq_circuit(circuit):
        return cirq_circuit_to_native_python(circuit)
    else:
        raise TypeError(f"Circuit type '{type(circuit)}' not recognized")


def serialize_qubits(
    qubits: Sequence[Qubit],
) -> tuple[str, ...]:
    """Given a sequence of qubit objects (e.g. Cirq Qid objects, Qiskit Qubit objects, etc.),
    convert to tuple of string labels representing the qubits.

    :param qubits: Sequence of qubit objects.

    :returns:
        Sequence of (str) qubit labels.

    """
    if is_sequence_of_qiskit_qubit(qubits):
        return tuple(qubit_to_str(q) for q in qubits)
    if is_sequence_of_cirq_qubit(qubits):
        return tuple(qubit_to_str(q) for q in qubits)
    else:
        raise ValueError(
            f"Qubit sequence not recognized, should be either tuple, list, or register containin cirq qubits or qiskit qubits"
        )


def get_default_qubit_objects(
    circuit: Circuit,
) -> list[QiskitQubit] | list[CirqQubit]:
    if is_cirq_circuit(circuit):
        return default_qubits_cirq(circuit)
    if is_qiskit_circuit(circuit):
        return default_qubits_qiskit(circuit)
    else:
        raise ValueError(f"Unrecognized circuit type {type(circuit)}.")


def qubit_to_str(qubit: Qubit) -> str:
    if is_cirq_qubit(qubit):
        return cirq_qubit_to_str(qubit)
    if is_qiskit_qubit(qubit):
        return qiskit_qubit_to_str(qubit)
    raise ValueError(f"Unrecognized qubit type {type(qubit)}.")


def serialize_observable(observable: Observable, qubits: list[str]) -> dict[str, Any]:
    """Serialize an observable to a dictionary.

    :param observable: The observable to serialize.
    :param qubits: The qubits (already serialized, i.e. as strings)

    :returns:
        A dictionary representation of the observable.
    """
    obs = observable.observable

    if is_qiskit_sparse_pauli_op(obs):
        return convert_qiskit_sparse_pauli_op(obs, qubits, observable.name).serialize()
    elif is_cirq_pauli_string(obs) or is_cirq_pauli_sum(obs):
        return convert_cirq_pauli(obs, observable.name).serialize()
    else:
        raise ValueError(f"Observable type {type(obs)} not recognized.")


def serialize_config(config_dict: dict[str, Any]) -> dict[str, Any]:
    """Fully serialize a config dict.

    Currently this involves:
    - Serializing the qubit order
    - Serializing the grouping (if present)
    - Serializing the observables (if present)

    :param config: The config dict to serialize.

    :returns:
        A fully serialized config dict.
    """
    # Make a shallow copy of the config
    conf_dict = config_dict.copy()

    # Serialize the qubits
    conf_dict["qubits"] = serialize_qubits(conf_dict["qubits"])

    # Serialize the grouping and the qubits
    grouping = conf_dict.get("grouping", None)
    if grouping is not None:
        if not all(isinstance(group, list) for group in conf_dict["grouping"]):
            raise ValueError("'grouping' should be a list of lists of qubits")

        conf_dict["grouping"] = [[qubit_to_str(q) for q in group] for group in grouping]

    if "expectation_values" in conf_dict["output"]:
        observables = conf_dict["output"]["expectation_values"].get("observables", None)
        if observables is not None:
            conf_dict["output"]["expectation_values"]["observables"] = [
                serialize_observable(obs, conf_dict["qubits"]) for obs in observables
            ]
    if "optimizer" in conf_dict:
        observable = conf_dict["optimizer"].get("observable", None)
        if observable is not None:
            conf_dict["optimizer"]["observable"] = serialize_observable(
                observable, conf_dict["qubits"]
            )

    return conf_dict
