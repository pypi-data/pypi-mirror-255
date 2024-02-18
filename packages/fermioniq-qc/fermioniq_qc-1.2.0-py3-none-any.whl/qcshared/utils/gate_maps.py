from .constants import MAX_QUBITS_PER_GATE_OR_CHANNEL

# All currently supported gates, and the number of qubits that they act on
full_supported_gate_sizes = {
    "I": -1,
    "Gate": -1,
    "X": 1,
    "RX": 1,
    "S": 1,
    "SDG": 1,
    "T": 1,
    "TDG": 1,
    "Y": 1,
    "RY": 1,
    "Z": 1,
    "RZ": 1,
    "R": 1,
    "H": 1,
    "RH": 1,
    "P": 1,
    "PhasedXPOW": 1,
    "PhasedXZ": 1,
    "U": 1,
    "CX": 2,
    "CXPOW": 2,
    "CRX": 2,
    "CZ": 2,
    "CZPOW": 2,
    "CRZ": 2,
    "CY": 2,
    "CRY": 2,
    "RXX": 2,
    "RYY": 2,
    "RZZ": 2,
    "SWAP": 2,
    "SWAPPOW": 2,
    "ISWAP": 2,
    "ISWAPPOW": 2,
    "FSIM": 2,
    "PhasedFSIM": 2,
    "CU": 2,
    "CH": 2,
    "CCX": 3,
    "CCXPOW": 3,
    "RCCX": 3,
    "CSWAP": 3,
    "RCCCX": 4,
}

supported_gate_sizes = {
    k: v
    for k, v in full_supported_gate_sizes.items()
    if v <= MAX_QUBITS_PER_GATE_OR_CHANNEL
}

## Possibly add:
# Identity gate
# permutation gate
# DiaGonalGate

cirq_single_qubit_gates = {
    "_PauliX": "RX",
    "XPowGate": "RX",
    "Rx": "RX",
    "_PauliY": "RY",
    "YPowGate": "RY",
    "Ry": "RY",
    "_PauliZ": "RZ",
    "Rz": "RZ",
    "ZPowGate": "RZ",
    "T": "RZ",
    "S": "RZ",
    "HPowGate": "RH",
    "H": "RH",
    "PhasedXPowGate": "PhasedXPOW",
    "PhasedXZGate": "PhasedXZ",
}
cirq_two_qubit_gates = {
    "XXPowGate": "RXX",
    "YYPowGate": "RYY",
    "ZZPowGate": "RZZ",
    "CZ": "CZPOW",
    "CZPowGate": "CZPOW",
    "CXPowGate": "CXPOW",
    "CNOT": "CXPOW",
    "SwapPowGate": "SWAPPOW",
    "SWAP": "SWAPPOW",
    "ISwapPowGate": "ISWAPPOW",
    "ISWAP": "ISWAPPOW",
    "FSimGate": "FSIM",
    "PhasedFSimGate": "PhasedFSIM",
}
cirq_three_qubit_gates = {
    "CCX": "CCXPOW",
    "CCNOT": "CCXPOW",
    "TOFFOLI": "CCXPOW",
    "CCXPowGate": "CCXPOW",
}
cirq_n_qubit_gates = {
    "MatrixGate": "Gate",
}

cirq_gate_map = {}
for gate_dict in [
    cirq_single_qubit_gates,
    cirq_two_qubit_gates,
    cirq_three_qubit_gates,
    cirq_n_qubit_gates,
]:
    cirq_gate_map.update(gate_dict)

cirq_gate_map = {
    k: v
    for k, v in cirq_gate_map.items()
    if full_supported_gate_sizes[v] <= MAX_QUBITS_PER_GATE_OR_CHANNEL
}


qiskit_single_qubit_gates = {
    "x": "X",
    "y": "Y",
    "z": "Z",
    "h": "H",
    "s": "S",
    "sdg": "SDG",
    "t": "T",
    "tdg": "TDG",
    "rx": "RX",
    "ry": "RY",
    "rz": "RZ",
    "r": "R",
    "u": "U",
    "p": "P",
}
qiskit_two_qubit_gates = {
    "swap": "SWAP",
    "cx": "CX",
    "cz": "CZ",
    "ch": "CH",
    "crz": "CRZ",
    "crx": "CRX",
    "cry": "CRY",
    "cu": "CU",
    "rxx": "RXX",
    "ryy": "RYY",
    "rzz": "RZZ",
}
qiskit_three_qubit_gates = {
    "ccx": "CCX",
    "cswap": "CSWAP",
    "rccx": "RCCX",
    "rcccx": "RCCCX",
}
qiskit_n_qubit_gates = {
    "unitary": "Gate",
    "id": "I",
}

qiskit_gate_map = {}
for gate_dict in [
    qiskit_single_qubit_gates,
    qiskit_two_qubit_gates,
    qiskit_three_qubit_gates,
    qiskit_n_qubit_gates,
]:
    qiskit_gate_map.update(gate_dict)


qiskit_gate_map = {
    k: v
    for k, v in qiskit_gate_map.items()
    if full_supported_gate_sizes[v] <= MAX_QUBITS_PER_GATE_OR_CHANNEL
}
