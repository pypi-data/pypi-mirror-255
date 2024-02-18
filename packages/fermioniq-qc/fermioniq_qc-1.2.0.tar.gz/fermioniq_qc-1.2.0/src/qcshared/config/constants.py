""" Constants """
MAX_SHOTS = 1e9
"""Maximum number of shots (samples) that can be asked for when sampling from a \
        circuit"""

MAX_QUBITS_FOR_FULL_OUTPUT = 10
"""Maximum number of qubits that we support for 'full' output \
        (e.g. all amplitudes, statevector output, etc."""

BOND_DIM_THRESHOLD_FOR_GRID_COMPILATION = 64

MAX_BITSTRINGS = 2**MAX_QUBITS_FOR_FULL_OUTPUT
"""Maximum number of bitstrings for which we will compute amplitudes)"""

MAX_BOND_DIM = 2**13
"""Maximum bond dimension allowed (no guarantee that this will work)"""

MAX_EASY_BOND_DIM = 128
"""Maximum bond dimension that will always be allowed despite the setting of the effort parameter"""

MAX_SWEEPS = 1e6

MAX_ELEMENTS = 60 * 2**30 / 16
NUM_ROWS = 1
MPO_BOND_DIM_NO_NOISE = 4
MPO_BOND_DIM_WITH_NOISE = 16

MAX_CUT_DIM = 1024
"""Maximum cut size through a compiled dmrg circuit (grid or split)"""

MAX_JOB_SIZE = 50
"""Max number of allowed circuits per job"""
