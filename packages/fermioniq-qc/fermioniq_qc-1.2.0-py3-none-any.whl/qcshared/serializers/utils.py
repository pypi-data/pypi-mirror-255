from typing import Any

import numpy as np


def reorder_gate_matrix(big_endian_gate_matrix):
    """Reorder the gate matrix to get the little endian ordering
    Qiskit uses big endian ordering, so we need to reorder the qubits to get
    the little endian ordering that is used in our convention
    """
    # Check that the matrix has 2**N rows and columns
    n_qubits = np.log2(big_endian_gate_matrix.shape[0])
    if not np.isclose(n_qubits, int(n_qubits)) or (
        big_endian_gate_matrix.shape[0] != big_endian_gate_matrix.shape[1]
    ):
        raise ValueError(
            "Gate matrix must have shape (2**N, 2**N) with N being integer"
        )

    new_order = get_little_endian_reordering(int(n_qubits))
    new_gate_matrix = big_endian_gate_matrix[new_order, :][:, new_order]
    return new_gate_matrix


def get_little_endian_reordering(n_qubits):
    """Get the reordering of the qubits to get the little endian ordering
    Qiskit uses big endian ordering, so we need to reorder the qubits to get
    the little endian ordering that is used in our convention."""
    return [int(bin(i)[2:].zfill(n_qubits)[::-1], 2) for i in range(2**n_qubits)]


def numpy_array_to_matrix_gate_dict(numpy_matrix) -> dict:
    """Convert a numpy array to a matrix gate dictionary"""
    matrix_gate_dict = {}
    # If matrix is sparse
    if numpy_matrix.size > 2 * np.count_nonzero(numpy_matrix):
        non_zero_indices = np.nonzero(numpy_matrix)
        non_zero_values = numpy_matrix[non_zero_indices]
        sparse_representation = []
        for row, col, val in zip(*non_zero_indices, non_zero_values):
            sparse_representation.append(
                [int(row), int(col), float(val.real), float(val.imag)]
            )
        matrix_gate_dict["sparse_matrix"] = sparse_representation

    # If matrix is dense:
    else:
        real, imag = numpy_matrix.real, numpy_matrix.imag
        matrix_gate_dict["real_matrix"] = real.tolist()
        matrix_gate_dict["imag_matrix"] = imag.tolist()

    return matrix_gate_dict


def matrix_gate_dict_to_numpy_array(gate_dict: dict):
    """Convert a matrix gate dictionary to a numpy array"""
    matrix_gate_dict_params = gate_dict["params"]

    if "sparse_matrix" in matrix_gate_dict_params.keys():
        array = np.zeros(
            (2 ** len(gate_dict["qubits"]), 2 ** len(gate_dict["qubits"])),
            dtype=np.complex128,
        )
        for row, col, real, imag in matrix_gate_dict_params["sparse_matrix"]:
            array[row, col] = real + 1j * imag
    elif ("real_matrix" in matrix_gate_dict_params) and (
        "imag_matrix" in matrix_gate_dict_params
    ):
        real_matrix = np.array(matrix_gate_dict_params["real_matrix"])
        imag_matrix = np.array(matrix_gate_dict_params["imag_matrix"])
        array = real_matrix + 1j * imag_matrix
    else:
        raise ValueError(
            "Invalid matrix gate dictionary. a Gate must have either a sparse_matrix or a real_matrix and an imag_matrix."
        )

    return array
