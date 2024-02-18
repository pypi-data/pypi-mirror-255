from typing import Sequence, cast

from pydantic import Field, PrivateAttr

from .qubit import GenericQubitNoise, QubitNoise, SpecificQubitNoise
from .typing import Qubits, qubits_to_internal_qubits
from .utils import ANY, BaseNoiseComponent


class GateNoise(BaseNoiseComponent):
    """
    Base class for gate noise, should not be initialised directly.

    GateNoise objects collect QubitNoise objects, which contain lists of noise channels that are applied before/after a gate.
    The noise channels of a QubitNoise object are applied whenever a gate is encountered in the circuit that matches a GateNoise object,
    and when the qubits that it acts on matches one of its QubitNoise objects.

    There are currently two subclasses of GateNoise:
        - SpecificGateNoise: Noise that is triggered by a gate with a specified name.
        - GenericGateNoise: Noise that is triggered by an unspecified gate. The number of qubits that the gate acts on should be specified.
    """

    # The QubitNoise objects that are contained within this GateNoise object
    _generic_qubit_noise: list[GenericQubitNoise] = PrivateAttr(default=[])
    _specific_qubit_noise: list[SpecificQubitNoise] = PrivateAttr(default=[])

    @property
    def generic_qubit_noise(self):
        return self._generic_qubit_noise

    @property
    def specific_qubit_noise(self):
        return self._specific_qubit_noise

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, self.__class__):
            return False
        # Equality between two GateNoise objects is determined by their fields (but not the QubitNoise objects that they contain).
        # Note: private attributes do not count as fields.
        try:
            for field_name in self.__fields__.keys():
                if getattr(self, field_name) != getattr(__value, field_name):
                    return False
        except AttributeError:
            return False
        return True

    def update(self, other: "GateNoise"):
        """
        Update the GateNoise object with the QubitNoise objects of another GateNoise object.
        Duplicates are identified and merged by the add method.
        """
        self.add([*other._generic_qubit_noise, *other._specific_qubit_noise])

    def _validate_qubit_noise(self, qubit_noise: QubitNoise) -> QubitNoise:
        raise NotImplementedError(
            f"{self.__class__.__name__} class should not be initialised directly."
        )

    def add(self, qubit_noises: Sequence[QubitNoise] | QubitNoise):
        """
        Add one or more QubitNoise objects to the GateNoise object, in the order specified.

        :param qubit_noises: QubitNoise objects to apply in conjunction with the gate
        """
        if isinstance(qubit_noises, QubitNoise):
            qubit_noises = [qubit_noises]

        # Validate first. If there's an error then none of the QubitNoise objects will be added.
        to_add_specific: list[SpecificQubitNoise] = [
            cast(SpecificQubitNoise, self._validate_qubit_noise(qubit_noise))
            for qubit_noise in qubit_noises
            if isinstance(qubit_noise, SpecificQubitNoise)
        ]
        to_add_generic: list[GenericQubitNoise] = [
            cast(GenericQubitNoise, self._validate_qubit_noise(qubit_noise))
            for qubit_noise in qubit_noises
            if isinstance(qubit_noise, GenericQubitNoise)
        ]
        # Add the QubitNoise objects, adding to existing ones if duplicates are found
        # Start with specific qubit noise
        for qubit_noise_specific in to_add_specific:
            # If there is not already a QubitNoise object with the same triggers, add it
            if qubit_noise_specific not in self._specific_qubit_noise:
                self._specific_qubit_noise.append(qubit_noise_specific)
            # Otherwise update the existing QubitNoise object using the new one
            else:
                self._specific_qubit_noise[
                    self._specific_qubit_noise.index(qubit_noise_specific)
                ].update(qubit_noise_specific)

        # Repeat the process for generic qubit noise
        for qubit_noise_generic in to_add_generic:
            # If there is not already a QubitNoise object with the same triggers, add it
            if qubit_noise_generic not in self._generic_qubit_noise:
                self._generic_qubit_noise.append(qubit_noise_generic)
            # Otherwise update the existing QubitNoise object using the new one
            else:
                self._generic_qubit_noise[
                    self._generic_qubit_noise.index(qubit_noise_generic)
                ].update(qubit_noise_generic)

    def specific_qubit_noise_lookup(self, gate_qubits: Qubits) -> QubitNoise | None:
        """
        Attempt to find a SpecificQubitNoise object that matches the given qubit labels.

        :param gate_qubits: List of qubit labels, QubitInternal objects, Qiskit qubit objects or Cirq qubit objects that the gate acts on.

        :return: QubitNoise object that matches the given qubit labels, or None if no match was found.
        """
        # Checks that gate qubits are a list of target objects (str, Qiskit qubit, Cirq qubit or internal Qubit)
        gate_qubits_internal = qubits_to_internal_qubits(gate_qubits)

        # Search for a specific noise entry with matching gate_qubits. Note that QubitNoise objects have internal qubit objects
        # as labels.
        for qubit_noise in self._specific_qubit_noise:
            if qubit_noise.qubits == gate_qubits_internal:
                return qubit_noise

        return None

    def generic_qubit_noise_lookup(self, n_gate_qubits: int) -> QubitNoise | None:
        """
        Attempt to find a GenericQubitNoise object that matches the given number of qubits.

        :param n_gate_qubits: Number of qubits that the gate acts on.

        :return: QubitNoise object that matches the given number of qubits, or None if no match was found.
        """
        if not isinstance(n_gate_qubits, int):
            raise ValueError(f"n_gate_qubits must be an integer. Got {n_gate_qubits}")

        # Search for a generic noise entry with the right number of qubits
        for qubit_noise in self._generic_qubit_noise:
            if n_gate_qubits == qubit_noise.n_qubits:
                return qubit_noise

        return None

    def get_noise_channels(self, gate_qubits: Qubits, trace: bool = False):
        """
        Get all noise channels (pre and post) that are triggered by the application of some gate (associated to this GateNoise object) to ``gate_qubits``.

        The lookup uses the following decision process:
            - A QubitNoise object is searched for that matches the qubits that the gate acts on (SpecificQubitNoise object).
            - If no match is found, a QubitNoise object is searched for that matches the number of qubits that the gate acts on (GenericQubitNoise object).

            If a QubitNoise object is found, its channels are returned. If nothing is found, None is returned.

        :param gate_qubits: List of qubit labels, QubitInternal objects, Qiskit qubit objects or Cirq qubit objects that the gate acts on.
        :param trace: If True, return the trace of the lookup process instead of the channels.

        :return: A dictionary with keys 'pre' and 'post', where each maps to a list of (target, channel) pairs,
                where the target is a tuple of qubit labels that the channel acts on, and the channel a NoiseChannel object.
                If no match was found, None is returned.
                If trace is True, the trace of the lookup process is returned as well.
        """
        trace_dict: dict[str, dict | None] = {}
        found_generic = False
        channels = None

        # First try to find a specific qubit noise object
        qubit_noise = self.specific_qubit_noise_lookup(gate_qubits)
        found_specific = qubit_noise is not None

        # Failing that, try to find a generic qubit noise object matching the number of qubits acted upon
        if qubit_noise is None:
            qubit_noise = self.generic_qubit_noise_lookup(len(gate_qubits))

        # If a match was found and it wasn't specific, then we found a generic match
        if qubit_noise is not None and not found_specific:
            found_generic = True

        # Record the trace of the lookup
        if found_specific:
            trace_dict["specific_qubit"] = {"qubits": list(gate_qubits)}
        else:
            trace_dict["specific_qubit"] = None

        if found_generic and qubit_noise is not None:
            trace_dict["generic_qubit"] = {"qubits": qubit_noise.n_qubits}
        else:
            trace_dict["generic_qubit"] = None

        # If we found a match, get the channels
        if (found_specific or found_generic) and qubit_noise is not None:
            channels = qubit_noise.channels

        # If tracing is on, return the channels and trace
        if trace:
            return channels, trace_dict
        # Otherwise return just the channels
        else:
            return channels


class SpecificGateNoise(GateNoise):
    """
    Class to represent noise that is triggered by specific gates. The gate name must be specified (and supported).

    - Supported gates are defined in 'gate_sizes'. TODO
    - QubitNoise objects can be added to this class that are triggered by specific qubits (SpecifcQubitNoise), or by any qubits (GenericQubitNoise).
    """

    # String representing the gate. A gate name (e.g. 'CX').
    gate_name: str = Field(
        description="Name of gate that triggers this particular GateNoise. E.g. 'CX', 'Z', 'Fsim'."
    )

    def _validate_qubit_noise(self, qubit_noise: QubitNoise) -> QubitNoise:
        """Validate a QubitNoise object against this GateNoise object, returning the object if it is valid."""
        if not isinstance(qubit_noise, QubitNoise):
            raise ValueError(f"Unrecognised QubitNoise object: {qubit_noise}")

        return qubit_noise


class GenericGateNoise(GateNoise):
    """
    Class to represent noise that is triggered by any gate.

    - QubitNoise objects can be added to this class that are triggered by specific qubits (SpecifcQubitNoise), or by any number of qubits (GenericQubitNoise).
    """

    def _validate_qubit_noise(self, qubit_noise: QubitNoise) -> QubitNoise:
        """Validate a QubitNoise object against this GateNoise object, returning the object if it is valid."""
        if not isinstance(qubit_noise, QubitNoise):
            raise ValueError(f"Unrecognised QubitNoise object: {qubit_noise}")

        # No validation needs to be performed here (generic gate noise is compatible with any qubit noise)

        return qubit_noise
