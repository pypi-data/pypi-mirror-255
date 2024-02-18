from typing import Any, Sequence, TypeGuard, TypeVar


# Concrete classes for type-checking
class Qubit:
    ...


class QiskitQubit(Qubit):
    __slots__ = ("index",)
    ...


class CirqQubit(Qubit):
    __slots__ = ("x", "row", "col", "name")
    ...


class Circuit:
    ...


class QiskitCircuit(Circuit):
    @property
    def qubits(self) -> list[QiskitQubit]:
        ...

    ...


class CirqCircuit(Circuit):
    __slots__ = ("moments",)

    def all_qubits(self) -> set[CirqQubit]:
        ...

    ...


class Observable:
    ...


class QiskitSparsePauliOp(Observable):
    __slots__ = ("paulis", "coeffs", "num_qubits")


class CirqPauliString(Observable):
    __slots__ = ("coefficient", "qubits", "gate")


CirqPauliSum = list[CirqPauliString]


# TypeVars for type-checking
# Custom types for qiskit
QiskitCircuitOperation = TypeVar("QiskitCircuitOperation")

# Custom types for cirq
CirqGateOperation = TypeVar("CirqGateOperation")
CirqMeasurement = TypeVar("CirqMeasurement")
CirqLineQubit = TypeVar("CirqLineQubit")
CirqGridQubit = TypeVar("CirqGridQubit")
CirqNamedQubit = TypeVar("CirqNamedQubit")

# Qiskit typeguards
# Qiskit circuit
def is_qiskit_circuit(val: object) -> TypeGuard[QiskitCircuit]:
    str_type = str(type(val))
    return "qiskit" in str_type and "circuit" in str_type


# Qiskit qubit
def is_qiskit_qubit(val: object) -> TypeGuard[QiskitQubit]:
    str_type = str(type(val))
    return "qiskit" in str_type and "Qubit" in str_type


# Qiskit circuit operation
def is_qiskit_circuit_instruction(val: object) -> TypeGuard[QiskitCircuitOperation]:
    str_type = str(type(val))
    return "qiskit" in str_type and "CircuitInstruction" in str_type


# Qiskit sequence checks
def is_sequence_of_qiskit_qubit(obj: Sequence[Any]) -> TypeGuard[Sequence[QiskitQubit]]:
    return isinstance(obj, Sequence) and all(is_qiskit_qubit(q) for q in obj)


# Qiskit observable checks
def is_qiskit_sparse_pauli_op(val: object) -> TypeGuard[QiskitSparsePauliOp]:
    str_type = str(type(val))
    return "qiskit" in str_type and "SparsePauliOp" in str_type


# Cirq typeguards
# Cirq circuit
def is_cirq_circuit(val: object) -> TypeGuard[CirqCircuit]:
    str_type = str(type(val))
    return "cirq" in str_type and "circuit" in str_type


# Cirq qubit
def is_cirq_qubit(val: object) -> TypeGuard[CirqQubit]:
    str_type = str(type(val))
    return "cirq" in str_type and ("Qid" in str_type or "Qubit" in str_type)


# Cirq gate operation
def is_cirq_gate_operation(val: object) -> TypeGuard[CirqGateOperation]:
    str_type = str(type(val))
    return "cirq" in str_type and "GateOperation" in str_type


def is_cirq_measurement(val: object) -> TypeGuard[CirqMeasurement]:
    str_type = str(type(val))
    return "cirq" in str_type and "MeasurementGate" in str_type


# Cirq qubit types
def is_cirq_line_qubit(val: object) -> TypeGuard[CirqLineQubit]:
    str_type = str(type(val))
    return "cirq" in str_type and "LineQubit" in str_type


def is_cirq_grid_qubit(val: object) -> TypeGuard[CirqGridQubit]:
    str_type = str(type(val))
    return "cirq" in str_type and "GridQubit" in str_type


def is_cirq_named_qubit(val: object) -> TypeGuard[CirqNamedQubit]:
    str_type = str(type(val))
    return "cirq" in str_type and "NamedQubit" in str_type


# Cirq sequence checks
def is_list_of_cirq_qubit(obj: list[Any]) -> TypeGuard[list[CirqQubit]]:
    return isinstance(obj, list) and all(is_cirq_qubit(q) for q in obj)


def is_sequence_of_cirq_qubit(obj: Sequence[Any]) -> TypeGuard[Sequence[CirqQubit]]:
    return isinstance(obj, Sequence) and all(is_cirq_qubit(q) for q in obj)


def is_cirq_pauli_sum(val: object) -> TypeGuard[CirqPauliSum]:
    str_type = str(type(val))
    return "cirq" in str_type and "PauliSum" in str_type


def is_cirq_pauli_string(val: object) -> TypeGuard[CirqPauliString]:
    str_type = str(type(val))
    return "cirq" in str_type and "PauliString" in str_type
