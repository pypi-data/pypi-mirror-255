import warnings
from typing import Sequence, Union

from ..io.observables import PauliObservable, PauliSumObservable
from ..utils.constants import MAX_QUBITS_PER_GATE_OR_CHANNEL
from ..utils.gate_maps import qiskit_gate_map
from .custom_types import (
    QiskitCircuit,
    QiskitCircuitOperation,
    QiskitQubit,
    QiskitSparsePauliOp,
)
from .utils import numpy_array_to_matrix_gate_dict, reorder_gate_matrix


def qiskit_circuit_to_native_python(
    circuit: QiskitCircuit,
) -> list[dict]:
    """Convert a Qiskit circuit to a JSON compatible object

    :param circuit: A circuit from Qiskit

    :returns:
        Serialized circuit
    """
    # Assign to each qubit a unique string identifier
    qubit_to_str_dict = {
        q: qiskit_qubit_to_str(q) for gate in circuit.data for q in gate.qubits
    }

    filtered_gates = filter_barriers_and_measurements(circuit.data)
    return [get_qiskit_gate_dict(gate, qubit_to_str_dict) for gate in filtered_gates]


def filter_barriers_and_measurements(
    instructions: Sequence[QiskitCircuitOperation],
) -> list[QiskitCircuitOperation]:
    """Filter out all barriers and measruements from a list of qiskit circuit instructions. Raise an error if the circuit contains intermediate measurements

    :param instructions: a Sequence of qiskit CircuitInstruction objects to filter

    :returns:
        A list with the instructions, from which barriers and measruements have been filtered.
    """
    indices_to_filter = []
    measurement_indices_qubits = []

    for instruction_index, instruction in enumerate(instructions):
        if instruction.operation.name == "barrier":
            indices_to_filter.append(instruction_index)

        elif instruction.operation.name == "measure":
            measurement_indices_qubits.append((instruction_index, instruction.qubits))

        else:
            for _, measurement_qubits in measurement_indices_qubits:
                if set(measurement_qubits) & set(instruction.qubits):
                    raise ValueError(
                        "The received qiskit circuit contains intermediate measurements. This is currently not supported. Stopping emulation"
                    )

    if measurement_indices_qubits:
        warnings.warn(
            "Encountered measurements at the end of the qiskit circuit. These are currently ignored. Please specify bitstring sampling in the config dictionary instead",
            stacklevel=2,
        )

    for measurement_index, _ in measurement_indices_qubits:
        indices_to_filter.append(measurement_index)

    return [ins for i, ins in enumerate(instructions) if i not in indices_to_filter]


def get_qiskit_gate_dict(
    gate: QiskitCircuitOperation,
    qubit_to_str_dict: dict[QiskitQubit, str],
) -> dict[str, Union[str, dict, tuple]]:
    """Get a dictionary representation of a qiskit gate

    :param gate: The Qiskit gate to convert

    :param qubit_to_str_dict: dictionary mapping qiskit qubits to strings (as returned by qiskit_qubit_to_str)

    :returns:
        Serialization of the gate.
    """
    gate_dict: dict[str, str | dict[str, float] | dict[str, str] | tuple] = {}
    qiskit_gate_name = gate.operation.name

    try:
        gate_dict["name"] = qiskit_gate_map[qiskit_gate_name]
        gate_dict["label"] = qiskit_gate_name
    except KeyError:
        raise NotImplementedError(
            f"Qiskit gate {qiskit_gate_name} not supported yet, please use a unitary gate with the corresponding numpy array instead"
        )

    gate_dict["qubits"] = tuple(qubit_to_str_dict[qubit] for qubit in gate.qubits)

    n_gate_qubits = len(gate_dict["qubits"])
    if n_gate_qubits > MAX_QUBITS_PER_GATE_OR_CHANNEL:
        raise NotImplementedError(
            f"Gates on more than {MAX_QUBITS_PER_GATE_OR_CHANNEL} qubits are currently not supported; gate {qiskit_gate_name} acts on {n_gate_qubits} qubits"
        )

    param_dict: dict[str, float] = {}
    variable_param_dict: dict[str, str] = {}

    def _update_param_dicts(_name, _value):
        """Update one or both dicts depending on whether the gate contains variable params"""
        if hasattr(_value, "parameters") and hasattr(_value, "name"):
            # Qiskit Parameter object
            param_dict[_name] = 0.0
            variable_param_dict[_name] = _value.name
        elif hasattr(_value, "parameters"):
            # Expression containing one or more parameters
            # e.g. param1 * 2, or param1 + param2
            raise ValueError("Gate parameters should not contain expressions")
        else:
            param_dict[_name] = float(_value)

    if gate_dict["name"] in (
        "P",
        "RX",
        "RY",
        "RZ",
        "CRZ",
        "CRX",
        "CRY",
        "RXX",
        "RYY",
        "RZZ",
    ):
        _update_param_dicts("rads", gate.operation.params[0])

    elif gate_dict["name"] == "R":
        _update_param_dicts("theta", gate.operation.params[0])
        _update_param_dicts("phi", gate.operation.params[1])

    elif gate_dict["name"] in ("U", "CU"):
        _update_param_dicts("theta", gate.operation.params[0])
        _update_param_dicts("phi", gate.operation.params[1])
        _update_param_dicts("lam", gate.operation.params[2])

        if gate_dict["name"] == "CU":
            _update_param_dicts("gamma", gate.operation.params[3])

    elif gate_dict["name"] == "Gate":
        matrix = gate.operation.to_matrix()
        re_ordered_matrix = reorder_gate_matrix(matrix)
        param_dict = numpy_array_to_matrix_gate_dict(re_ordered_matrix)

        # Use the label of the gate (if given) as the label of the serialized gate
        if gate.operation.label is not None:
            gate_dict["label"] = gate.operation.label

    gate_dict["params"] = param_dict
    if variable_param_dict:
        gate_dict["variable_params"] = variable_param_dict

    return gate_dict


def default_qubits_qiskit(circuit: QiskitCircuit) -> list[QiskitQubit]:
    return circuit.qubits


def qiskit_qubit_to_str(qubit: QiskitQubit) -> str:
    return f"{qubit.register.name}_{qubit.register.index(qubit)}"


def convert_qiskit_sparse_pauli_op(
    qiskit_obs: QiskitSparsePauliOp, qubits: list[str], name: str
) -> PauliSumObservable:
    """Constructs an instance of the PauliObservable class from a
    qiskit SparsePauliOp.

    Since the qiskit SparsePauliOp does not contain information about the qubits that
    it acts on, we assume that it acts on all qubits given in ``qubits``.

    :param qiskit_obs: qiskit SparsePauliOp
    :param qubits: list of qubit labels (as strings, i.e. already serialized)
    :param name: str specifying the name of the operator

    :returns:
        an PauliObservable class instance representing the input SparsePauliOp
    """
    if qiskit_obs.num_qubits != len(qubits):
        raise ValueError(
            f"""Number of qubits ({qiskit_obs.num_qubits}) in qiskit operator does not
            match number of qubits ({len(qubits)}) in 'qubits'."""
        )

    # Store operator term-by-term
    observables = []
    for coeff, pauli_string in zip(qiskit_obs.coeffs, qiskit_obs.paulis):
        # Dictionary from qubit labels to Pauli operators (as strings)
        qubit_to_pauli: dict[str, str] = {}

        # read string from right to left
        for idx, pauli in enumerate(pauli_string):
            qubit_label = qubits[idx]

            # Only store non-identity Pauli's
            if str(pauli) != "I":
                if qubit_label not in qubit_to_pauli:
                    qubit_to_pauli[qubit_label] = str(pauli)
                else:
                    raise ValueError(
                        f"Qubit {qubit_label} already has a Pauli {qubit_to_pauli[qubit_label]} acting on it."
                    )
        observables.append(PauliObservable(qubit_to_pauli, coeff))

    return PauliSumObservable(observables, name)
