import random

import numpy as np

from ..noise_models.channel import *
from ..noise_models.typing import Qubits


def random_unitary(d):
    """
    Random unitary of dimension d
    """
    A = np.random.random((d, d)) + 1j * np.random.random((d, d))
    U, _, _ = np.linalg.svd(A)
    return U


def random_target_channel_pair(
    qubit_labels: list[Qubits],
    strength: float = 0.2,
    max_n_qubits: int = 2,
    min_n_qubits: int = 1,
) -> tuple[list[Qubits], NoiseChannel]:
    """
    Make a random target-channel pair.

    :param qubit_labels: The labels of the qubits that the channel could act on
    :param strength: The strength of the channel. This is used to determine the strength of the noise.

    :return: A random target-channel pair
    """
    if min_n_qubits == max_n_qubits:
        n_qubits = min_n_qubits
    else:
        n_qubits = np.random.randint(1, min(max_n_qubits, len(qubit_labels)) + 1)

    # Choose a random channel compatible with the number of qubits
    if n_qubits == 1:
        channel_constructor = random.choice(
            [
                random_depolarizing_channel,
                random_bitflip_channel,
                random_phase_damping_channel,
                random_amplitude_damping_channel,
                random_phase_amplitude_damping_channel,
                random_pauli_channel,
                random_kraus_channel,
            ]
        )
        if channel_constructor in [
            random_depolarizing_channel,
            random_pauli_channel,
            random_kraus_channel,
        ]:
            targets, random_channel = channel_constructor(  # type: ignore
                n_qubits=n_qubits, qubit_labels=qubit_labels, strength=strength
            )
        else:
            targets, random_channel = channel_constructor(  # type: ignore
                qubit_labels=qubit_labels, strength=strength
            )
    else:
        channel_constructor = random.choice(
            [
                random_depolarizing_channel,
                random_pauli_channel,
                random_kraus_channel,
            ]
        )
        targets, random_channel = channel_constructor(  # type: ignore
            n_qubits=n_qubits, qubit_labels=qubit_labels, strength=strength
        )

    return targets, random_channel


def random_depolarizing_channel(
    n_qubits: int, qubit_labels: list[Qubits], strength: float = 0.2
) -> tuple[list[Qubits], DepolarizingChannel]:

    targets = random.sample(qubit_labels, n_qubits)
    return targets, DepolarizingChannel(
        p=np.random.uniform(0, strength), num_qubits=len(targets)
    )


def random_bitflip_channel(
    qubit_labels: list[Qubits], strength: float = 0.2
) -> tuple[list[Qubits], BitFlipChannel]:
    targets = random.sample(qubit_labels, 1)
    return targets, BitFlipChannel(
        p0=np.random.uniform(0, strength), p1=np.random.uniform(0, strength)
    )


def random_phase_damping_channel(
    qubit_labels: list[Qubits], strength: float = 0.2
) -> tuple[list[Qubits], PhaseDampingChannel]:
    targets = random.sample(qubit_labels, 1)
    return targets, PhaseDampingChannel(gamma_pd=np.random.uniform(0, strength))


def random_amplitude_damping_channel(
    qubit_labels: list[Qubits],
    strength: float = 0.2,
) -> tuple[list[Qubits], AmplitudeDampingChannel]:
    targets = random.sample(qubit_labels, 1)
    return targets, AmplitudeDampingChannel(
        gamma_ad=np.random.uniform(0, strength),
        excited_state_population=np.random.uniform(0, strength),
    )


def random_phase_amplitude_damping_channel(
    qubit_labels: list[Qubits],
    strength: float = 0.2,
) -> tuple[list[Qubits], PhaseAmplitudeDampingChannel]:
    gamma_ad = np.random.uniform(0, strength)
    gamma_pd = (1 - gamma_ad) * np.random.rand()
    targets = random.sample(qubit_labels, 1)
    return targets, PhaseAmplitudeDampingChannel(
        gamma_ad=gamma_ad,
        gamma_pd=gamma_pd,
        excited_state_population=np.random.uniform(0, strength),
    )


def random_pauli_channel(
    n_qubits: int, qubit_labels: list[Qubits], strength: float = 0.2
) -> tuple[list[Qubits], PauliChannel]:
    n_pauli_terms = np.random.randint(1, 4**n_qubits + 1)
    pauli_probs = {
        "".join(np.random.choice(["I", "X", "Y", "Z"], n_qubits)): np.random.uniform(
            0, strength
        )
        for _ in range(n_pauli_terms)
    }
    # Add the identity term with (unnormalized) probability 1
    pauli_probs["I" * n_qubits] = 1
    # Normalize the probabilities
    pauli_probs = {k: v / sum(pauli_probs.values()) for k, v in pauli_probs.items()}
    targets = random.sample(qubit_labels, n_qubits)
    return targets, PauliChannel(pauli_probs=pauli_probs)


def random_kraus_channel(
    n_qubits: int, qubit_labels: list[Qubits], strength: float = 0.2
) -> tuple[list[Qubits], KrausChannel]:
    random_kraus_op = random_unitary(2**n_qubits).reshape([2] * 2 * n_qubits)
    identity_kraus_op = np.eye(2**n_qubits).reshape([2] * 2 * n_qubits)
    random_kraus_op_coeff = np.sqrt(strength * 0.01)
    identity_kraus_op_coeff = np.sqrt(1 - random_kraus_op_coeff**2)
    kraus_ops = [random_kraus_op * random_kraus_op_coeff] + [
        identity_kraus_op * identity_kraus_op_coeff
    ]

    targets = random.sample(qubit_labels, n_qubits)

    return targets, KrausChannel(kraus_ops=kraus_ops)
