from typing import Any as AnyType
from typing import Literal, TypeGuard, Union

from ..serializers.custom_types import (
    CirqQubit,
    QiskitQubit,
    is_sequence_of_cirq_qubit,
    is_sequence_of_qiskit_qubit,
)
from ..serializers.serializer import serialize_qubits
from .channel import NoiseChannel
from .utils import QubitInternal

# Type aliases
QubitsExternal = list[str] | list[CirqQubit] | list[QiskitQubit]
Qubits = Union[QubitsExternal, list[QubitInternal]]

NoiseEffect = list[tuple[Qubits | Literal["same"], NoiseChannel]]
Noise = dict[Literal["pre", "post"], NoiseEffect]
NoiseEffectInternal = list[tuple[QubitInternal | Literal["same"], NoiseChannel]]
NoiseInternal = dict[Literal["pre", "post"], NoiseEffectInternal]


def is_internal_qubit_list(qubits: AnyType) -> TypeGuard[list[QubitInternal]]:
    return isinstance(qubits, list) and all(
        isinstance(t, QubitInternal) for t in qubits
    )


def is_qubit_list(qubits: AnyType) -> TypeGuard[Qubits]:
    if isinstance(qubits, list):
        return (
            all(isinstance(x, str) for x in qubits)
            or is_sequence_of_cirq_qubit(qubits)
            or is_sequence_of_qiskit_qubit(qubits)
            or is_internal_qubit_list(qubits)
        )
    return False


def is_noise_effect_internal(obj: AnyType) -> TypeGuard[NoiseEffectInternal]:
    if not isinstance(obj, list):
        return False
    return all(
        isinstance(effect, tuple)
        and len(effect) == 2
        and (effect[0] == "same" or is_qubit_list(effect[0]))
        and isinstance(effect[1], NoiseChannel)
        for effect in obj
    )


def is_noise_internal(obj: AnyType) -> TypeGuard[NoiseInternal]:
    correct_dict_type = isinstance(obj, dict) and all(
        key in ["pre", "post"] for key in obj.keys()
    )
    correct_list_type = is_noise_effect_internal(
        obj["pre"]
    ) and is_noise_effect_internal(obj["post"])
    return correct_dict_type and correct_list_type


# Type conversions


def qubits_to_internal_qubits(qubits: Qubits) -> list[QubitInternal]:
    if is_internal_qubit_list(qubits):
        return qubits
    if (
        (isinstance(qubits, list) and all(isinstance(x, str) for x in qubits))
        or is_sequence_of_cirq_qubit(qubits)
        or is_sequence_of_qiskit_qubit(qubits)
    ):
        return [QubitInternal(object=t) for t in qubits]

    raise ValueError(
        f"Qubits {qubits} are of unrecognized type. They should be list of qubits (qiskit / cirq qubit objects or strings)"
    )


def qubits_to_strings(qubits: Qubits) -> list[str]:
    if isinstance(qubits, tuple):
        qubits = list(qubits)
    if isinstance(qubits, list) and all(isinstance(t, str) for t in qubits):
        # Extra conversion to string for Mypy
        return [str(t) for t in qubits]
    if is_internal_qubit_list(qubits):
        return [q._string for q in qubits]
    elif is_sequence_of_qiskit_qubit(qubits) or is_sequence_of_cirq_qubit(qubits):
        return list(serialize_qubits(qubits))
    raise ValueError(
        f"Qubits {qubits} are of unrecognized type. They should be list of qubits (qiskit / cirq qubit objects or strings)"
    )
