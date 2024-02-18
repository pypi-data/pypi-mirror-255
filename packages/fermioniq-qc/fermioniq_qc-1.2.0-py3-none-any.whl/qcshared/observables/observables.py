from typing import Any, ClassVar

from pydantic import BaseModel, Extra, validator

from ..serializers.custom_types import (
    is_cirq_pauli_string,
    is_cirq_pauli_sum,
    is_qiskit_sparse_pauli_op,
)


class Observable(BaseModel):
    extra: ClassVar = Extra.forbid

    observable: Any
    name: str

    @validator("observable")
    def validate_observable(cls, v):
        if (
            is_cirq_pauli_string(v)
            or is_cirq_pauli_sum(v)
            or is_qiskit_sparse_pauli_op(v)
        ):
            return v
        else:
            raise TypeError(
                f"Observable type '{type(v)}' not recognized. Must be one of cirq.PauliString, cirq.PauliSum, or qiskit.SparsePauliOp."
            )
