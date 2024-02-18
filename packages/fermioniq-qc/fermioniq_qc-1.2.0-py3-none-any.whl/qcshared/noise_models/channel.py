import numpy as np
from pydantic import Field, validator

from ..utils.constants import MAX_QUBITS_PER_GATE_OR_CHANNEL
from .utils import BaseNoiseComponent


class NoiseChannel(BaseNoiseComponent):
    """
    Base class for noise channels
    """

    # This property should be overriden by derived classes.
    @property
    def n_qubits(self):
        raise NotImplementedError(
            f"n_qubits property not implemented for {self.__class__.__name__}"
        )

    @property
    def params(self):
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__fields__.keys()
        }


class SingleQubitChannel(NoiseChannel):
    """
    Base class for single qubit noise channels.
    """

    # Used to report how many qubits this class acts on. This is *not* a parameter (field) of the channel.
    @property
    def n_qubits(self):
        return 1


class DepolarizingChannel(NoiseChannel):
    """
    Noise model for depolarizing noise
    Maps the density matrix rho -> (1-p)rho + p * I / d where d is the dimension of the Hilbert space

    The depolarizing parameter p must be between 0 and 1
    """

    p: float = Field(description="Depolarizing parameter", ge=0, le=1)
    num_qubits: int = Field(
        description="Number of qubits for depolarizing noise",
        ge=1,
        le=MAX_QUBITS_PER_GATE_OR_CHANNEL,
    )

    @property
    def n_qubits(self):
        return self.num_qubits


class BitFlipChannel(SingleQubitChannel):
    """
    A bit flip channel with probabilities p0 and p1 for flipping 0 to 1 and 1 to 0 respectively.
    """

    p0: float = Field(description="Probability of flipping 0 to 1", ge=0, le=1)
    p1: float = Field(description="Probability of flipping 1 to 0", ge=0, le=1)


class PhaseDampingChannel(SingleQubitChannel):
    """Noise model for phase damping noise

    This channel is only defined for single qubits
    Uses the Nielsen and Chuang definition of phase damping
    Maps the density matrix rho = [[rho_00, rho_01], [rho_10, rho_11]] ->
    -> [[rho_00, sqrt(1-gamma) * rho_01], [sqrt(1-gamma) * rho_10, gamma * rho_11]]

    This is done by applying the Kraus operators:
    K_0 = [[1, 0], [0, sqrt(1-gamma_pd)]]
    K_1 = [[0,0], [0, sqrt(gamma_pd)]]

    """

    gamma_pd: float = Field(description="Phase damping parameter", ge=0, le=1)


class AmplitudeDampingChannel(SingleQubitChannel):
    """Noise model for amplitude damping. This channel is only defined for a single qubit.

    Applies the Kraus operators:
        K0 = sqrt(1 - p1) * [[1, 0], [0, sqrt(1 - a)]]
        K1 = sqrt(1 - p1) * [[0, sqrt(a)], [0, 0]]
        K2 = sqrt(p1) * [[sqrt(1 - a), 0], [0, 1]]
        K3 = sqrt(p1) * [[0, 0], [sqrt(a), 0]]

    """

    gamma_ad: float = Field(description="Amplitude damping parameter", ge=0, le=1)
    excited_state_population: float = Field(
        description="Excited state population", ge=0, le=1
    )


class PhaseAmplitudeDampingChannel(SingleQubitChannel):
    """Noise model for phase and amplitude damping noise. This channel is only defined for a single qubit.

    Applies the Kraus operators:
    A0 = sqrt(1 - p1) * [[1, 0], [0, sqrt(1 - a - b)]]
    A1 = sqrt(1 - p1) * [[0, sqrt(a)], [0, 0]]
    A2 = sqrt(1 - p1) * [[0, 0], [0, sqrt(b)]]
    B0 = sqrt(p1) * [[sqrt(1 - a - b), 0], [0, 1]]
    B1 = sqrt(p1) * [[0, 0], [sqrt(a), 0]]
    B2 = sqrt(p1) * [[sqrt(b), 0], [0, 0]]

    where a = gamma_ad, b = gamma_pd and p1 = excited_state_population

    """

    gamma_ad: float = Field(description="Amplitude damping parameter", ge=0, le=1)
    gamma_pd: float = Field(description="Phase damping parameter", ge=0, le=1)
    excited_state_population: float = Field(
        description="Excited state population", ge=0, le=1
    )

    @validator("gamma_pd")
    def validate_gamma_ad_pd(cls, gamma_pd, values):
        """
        Checks:
            gamma_ad + gamma_pd is between 0 and 1
        """
        if "gamma_ad" not in values:
            return gamma_pd

        if not (0 <= gamma_pd + values["gamma_ad"] <= 1):
            raise ValueError("Sum of gamma_ad and gamma_pd must be between 0 and 1")
        return gamma_pd


class KrausChannel(NoiseChannel):
    """Noise model for general Kraus noise on qudits

    Maps the density matrix rho -> sum_i K_i rho K_i^dagger.

    Defined by a list of Kraus operators K_i with shape (d_0, d_1, ..., d_n, d_0, d_1, ..., d_n),
    where n is the number of qudits and d_j the physical dimension of qudit j.
    """

    kraus_ops: list[np.ndarray] = Field(
        description="List of Kraus operators, each with shape (d_0, d_1, ..., d_n, d_0, d_1, ..., d_n), "
        "where n is the number of qudits and d_j the physical dimension of qudit j.",
        min_items=1,
    )

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, self.__class__):
            return False
        try:
            for field_name in self.__fields__.keys():
                if field_name == "kraus_ops":
                    if not all(
                        np.allclose(kraus_op, kraus_op_2)
                        for kraus_op, kraus_op_2 in zip(
                            getattr(self, field_name),
                            getattr(__value, field_name),
                            strict=True,
                        )
                    ):
                        return False

                elif getattr(self, field_name) != getattr(__value, field_name):
                    return False
        except AttributeError:
            return False
        return True

    @property
    def n_qubits(self):
        return len(self.kraus_ops[0].shape) // 2

    @validator("kraus_ops")
    def validate_kraus_ops(cls, kraus_ops):
        """
        Checks:
            - All kraus operators are of shape (d_0, d_1, ..., d_n, d_0, d_1, ..., d_n)
            - Kraus operators sum up to the Identity matrix
        """
        # Check that each Kraus operator has an even number of indices, and that the shapes of each operator are the same
        if not all(len(k.shape) % 2 == 0 for k in kraus_ops) or not all(
            k.shape == kraus_ops[0].shape for k in kraus_ops
        ):
            raise ValueError(
                "All Kraus operators must be matrices of dimension (d_0, d_1, ..., d_n, d_0, d_1, ..., d_n) for n qudits, "
                "where d_j is the physical dimension of qudit j."
            )

        n_qudits = len(kraus_ops[0].shape) // 2

        if n_qudits > MAX_QUBITS_PER_GATE_OR_CHANNEL:
            raise ValueError(
                f"Kraus channels can currently only be defined on up to {MAX_QUBITS_PER_GATE_OR_CHANNEL} qubits; found {n_qudits}"
            )

        # Check that the kraus operators are 'square'
        if not all(
            k.shape[0:n_qudits] == k.shape[n_qudits : 2 * n_qudits] for k in kraus_ops
        ):
            raise ValueError(
                "All Kraus operators must be matrices of dimension (d_0, d_1, ..., d_n, d_0, d_1, ..., d_n) for n qudits, "
                "where d_j is the physical dimension of qudit j."
            )

        total_phys_dim = np.prod(kraus_ops[0].shape[:n_qudits])

        # Check that the sum of the Kraus operators multiplied with their dagger is equal to the identity
        sum_of_k_dagger_k = np.zeros(
            (total_phys_dim, total_phys_dim), dtype=np.complex128
        )
        for kraus_op in kraus_ops:
            reshaped_kraus_op = kraus_op.reshape((total_phys_dim, total_phys_dim))
            sum_of_k_dagger_k += reshaped_kraus_op.conj().T @ reshaped_kraus_op

        if not np.allclose(sum_of_k_dagger_k, np.eye(total_phys_dim)):
            raise ValueError(
                "The sum of the Kraus operators multiplied with their dagger must be equal to identity."
            )

        return kraus_ops


class PauliChannel(NoiseChannel):
    """
    Noise model for Pauli noise on qubits, in which each Pauli string is applied to the qubits with a given probability.
    These probabilities are specified via a dictionary.

    For example, for a 2 qubit system, if one wants to do nothing with probability 0.5, or otherwise apply XX (0.25 prob)
    or YY (0.25 prob), the dictionary would be:
    {"II": 0.5, "XX": 0.25, "YY": 0.25}

    The probabilities must sum to 1. Operators which are not specified are assumed to have probability 0
    """

    pauli_probs: dict[str, float | int] = Field(
        description="Dictionary of Pauli operators and their probabilities",
    )

    @property
    def n_qubits(self):
        # Assume that the number of qubits is given by the length of the Pauli strings
        return len(list(self.pauli_probs.keys())[0])

    @validator("pauli_probs")
    def validate_pauli_probs(cls, pauli_probs):
        """
        Checks:
            - All probabilities are between 0 and 1
            - Probabilities sum up to 1
            - Pauli strings only contain 'X', 'Y', 'Z', 'I' and are of length n_qubits
        """
        # Assume that the number of qubits is given by the length of the Pauli strings
        n_qubits = len(list(pauli_probs.keys())[0])

        if n_qubits > MAX_QUBITS_PER_GATE_OR_CHANNEL:
            raise ValueError(
                f"Pauli channels can currently only be defined on up to {MAX_QUBITS_PER_GATE_OR_CHANNEL} qubits; found {n_qubits}"
            )

        total_prob = 0.0
        for pauli_string, prob in pauli_probs.items():
            if not (0 < prob <= 1):
                raise ValueError(
                    "Probabilities must be between 0 (exclusive) and 1 (inclusive)"
                )
            if not (
                len(pauli_string) == n_qubits
                and all(char in "IXYZ" for char in pauli_string)
            ):
                raise ValueError(
                    f"Pauli string {pauli_string} not valid, must be a combination of X, Y, Z and I with length equal to the number of qubits = {n_qubits}"
                )
            total_prob += prob

        if not np.isclose(total_prob, 1):
            raise ValueError("Probabilities must sum to 1")

        return pauli_probs
