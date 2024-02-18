from typing import Literal, Sequence, overload

from pydantic import Field, PrivateAttr, validator

from ..serializers.custom_types import (
    Circuit,
    CirqQubit,
    QiskitQubit,
    is_cirq_circuit,
    is_cirq_qubit,
    is_qiskit_circuit,
    is_qiskit_qubit,
)
from ..serializers.serializer import serialize_circuit
from ..utils import gate_maps
from ..utils.constants import MAX_QUBITS_PER_GATE_OR_CHANNEL
from ..utils.gate_maps import cirq_gate_map, qiskit_gate_map
from . import utils
from .channel import BitFlipChannel, NoiseChannel
from .gate import GateNoise, GenericGateNoise, SpecificGateNoise
from .qubit import GenericQubitNoise, SpecificQubitNoise
from .typing import (
    Noise,
    Qubits,
    is_qubit_list,
    qubits_to_internal_qubits,
    qubits_to_strings,
)
from .utils import ANY, Any, BaseNoiseComponent, QubitInternal


class NoiseModel(BaseNoiseComponent):
    """
    Class for storing the full noise model of a quantum device.

    A NoiseModel consists of a set of GateNoise objects, each of which contains a set of QubitNoise objects, each of which
    contains a list of (target, NoiseChannel) pairs, where the target is a tuple of qubit labels that the channel acts on.

    A NoiseModel is applied to a circuit in the following way:
        - For each gate in the circuit, the NoiseModel is searched for a GateNoise object that matches the name of that gate.
        - If a matching GateNoise object is found, its QubitNoise objects are searched for one that matches the qubits that the gate acts on.
        - If found, then the NoiseChannels of that QubitNoise object are applied to their target qubits, either before or after the gate (depending on where they were targeted).

    At each point, if no matching object is found, then the model falls back to a 'generic' one, in this order:
        - If no GateNoise object matching the name of the gate is found, the model instead searches through its GateNoise objects for one that is triggered by the
            number of qubits that the gate acts on (a GenericGateNoise object). Failing that, a GateNoise object with 'any' as the number of triggering qubits is used.
        - When searching the QubitNoise objects of a GateNoise object, if none are found that match the qubits that the gate acts on, then the model instead searches for one that
            is triggered by the number of qubits as the gate acts on (a GenericQubitNoise object). Failing that, a QubitNoise object with 'any' as the number of triggering qubits is used.
    """

    name: str = Field(
        description="The name of the device noise model. Can only consist of letters, digits spaces, underscores, and hyphens",
        regex=r"^[A-Za-z\d_-]*$",
        default="",
    )

    qubits: list = Field(
        description="The qubits in the device as strings, qiskit or Cirq qubits, or QubitInternal objects (internal representation). Noise channels and operators should all act on subsets of these qubits",
    )

    description: str = Field(
        description="A description of the noise model. E.g. Applies single-qubit depolarizing noise after every gate to the same qubits that the gate acts on.",
        regex=r"^[A-Za-z0-9\s\d_-]*$",
        default="",
    )

    # TODO: check type error
    supported_gate_sizes: dict[str, int] = Field(  # type: ignore
        description="A dictionary of supported gates and the number of qubits that they act on. A -1 can be used to denote gates that can act on any number of qubits (e.g. an identity gate). Default is common.utils.supported_gate_sizes. Note: these should not be the names of qiskit or cirq gates.",
        default=None,
    )

    _gate_noise_specific: list[SpecificGateNoise] = PrivateAttr(default=[])
    _gate_noise_general: list[GenericGateNoise] = PrivateAttr(default=[])
    _readout_errors: list[tuple[QubitInternal | Any, BitFlipChannel]] = PrivateAttr(
        default=[]
    )
    _type: Literal["fermioniq"] | Literal["cirq"] | Literal["qiskit"] = PrivateAttr(
        default="fermioniq"
    )

    @property
    def qubit_strings(self) -> list[str]:
        return [q._string for q in self.qubits]

    @property
    def qubit_objects(self) -> list[str | QiskitQubit | CirqQubit]:
        return [q.object for q in self.qubits]

    @property
    def readout_errors(self):
        return self._readout_errors

    def get_supported_gate_size(self, gate_name: str) -> int:
        """
        Return the number of qubits that the given gate acts on, or -1 if the gate acts on any number of qubits.

        :param gate_name: The name of the gate.

        :return: The number of qubits that the gate acts on, or -1 if the gate acts on any number of qubits.
        """
        return self.supported_gate_sizes[gate_name]

    @validator("qubits")
    def validate_qubits(cls, qubits, values):
        """
        Checks:
            - qubits is a non empty list of unique qubit objects (strings, Cirq qubits, Qiskit qubits or internal qubit objects)
        """
        if not qubits:
            raise ValueError("The list of qubits given to the noise model is empty")

        if len(set(qubits)) != len(qubits):
            raise ValueError(
                f"Qubits do not occur uniquely in the list given to the noise model: {qubits}"
            )
        # This raises an error if qubits is not a list of qubit objects or strings
        qubits = qubits_to_internal_qubits(qubits)
        return qubits

    @validator("supported_gate_sizes", always=True)
    def validate_supported_gate_sizes(cls, supported_gate_sizes, values):
        """
        Validates the supported gate sizes provided. If any are provided, then it checks:
        - At least one supported gate is provided
        - All gate sizes are positive integers or -1
        - If cirq is being used, that any gates that conflict with cirq match the cirq gate sizes
        - If qiskit is being used, that any gates that conflict with qiskit match the qiskit gate sizes
        """
        # Test whether qiskit or cirq are being used, in order to check whether the gate names conflict
        using_qiskit = using_cirq = False
        if "qubits" in values:
            using_qiskit = any(is_qiskit_qubit(q.object) for q in values["qubits"])
            using_cirq = any(is_cirq_qubit(q.object) for q in values["qubits"])

        # If no supported gate sizes are provided, then return the default (from cirq / qiskit if appropriate)
        if supported_gate_sizes is None:
            if using_cirq:
                return {
                    g: gate_maps.supported_gate_sizes[cirq_gate_map[g]]
                    for g in cirq_gate_map.keys()
                }
            elif using_qiskit:
                return {
                    g: gate_maps.supported_gate_sizes[qiskit_gate_map[g]]
                    for g in qiskit_gate_map.keys()
                }
            else:
                return gate_maps.supported_gate_sizes.copy()

        # If some custom supported gate sizes are provided, then validate them
        if len(supported_gate_sizes) == 0:
            raise ValueError("At least one supported gate must be provided.")
        if any(
            n != -1 and not (1 <= n <= MAX_QUBITS_PER_GATE_OR_CHANNEL)
            for n in supported_gate_sizes.values()
        ):
            raise ValueError(
                f"Gate sizes must be a positive integer <= {MAX_QUBITS_PER_GATE_OR_CHANNEL}, or -1. Got {supported_gate_sizes}."
            )

        # Check conflicts with qiskit:
        # If there is a gate with the same name as a qiskit gate, but with a different number of qubits, then raise an error
        if using_qiskit and any(
            g in qiskit_gate_map
            and supported_gate_sizes[g]
            != gate_maps.supported_gate_sizes[qiskit_gate_map[g]]
            for g in supported_gate_sizes.keys()
        ):
            bad_names = [
                g
                for g in supported_gate_sizes.keys()
                if g in qiskit_gate_map
                and supported_gate_sizes[g]
                != gate_maps.supported_gate_sizes[qiskit_gate_map[g]]
            ]
            raise ValueError(
                f"Gate names {bad_names} match names of qiskit gates, but the specified number of qubits that they act on differs from the qiskit definition. Either give these gates a unique name, or provide the correct number of qubits."
            )

        # Check conflicts with cirq:
        # If there is a gate with the same name as a cirq gate, but with a different number of qubits, then raise an error
        if using_cirq and any(
            g in cirq_gate_map
            and supported_gate_sizes[g]
            != gate_maps.supported_gate_sizes[cirq_gate_map[g]]
            for g in supported_gate_sizes.keys()
        ):
            bad_names = [g for g in supported_gate_sizes.keys() if g in cirq_gate_map]
            raise ValueError(
                f"Gate names {bad_names} match names of cirq gates, but the specified number of qubits that they act on differs from the cirq definition. Either give these gates a unique name, or provide the correct number of qubits."
            )

        return supported_gate_sizes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the type of the model (qiskit, cirq, or fermioniq)
        if all(is_cirq_qubit(qo) for qo in self.qubit_objects):
            self._type = "cirq"
        elif all(is_qiskit_qubit(qo) for qo in self.qubit_objects):
            self._type = "qiskit"
        elif not (
            all(isinstance(qo, str) for qo in self.qubit_objects)
            or all(isinstance(qo, QubitInternal) for qo in self.qubit_objects)
        ):
            if any(
                isinstance(qo, (str, QubitInternal))
                or is_cirq_qubit(qo)
                or is_qiskit_qubit(qo)
                for qo in self.qubit_objects
            ):
                raise ValueError(
                    f"Using a mixture of qubit types in the noise model. Please use only a single type. Current types are {[type(qo) for qo in self.qubit_objects]}."
                )
            else:
                raise ValueError(
                    "Unrecognized qubit types in the noise model. Please use only qiskit / cirq / string qubits (or instances of QubitInternal)."
                )

    def add_supported_gate(
        self, gate_name: str, n_qubits: int, overwrite: bool = False
    ):
        """
        Add a new gate / gates to the list of supported gates, with the number of qubits that it acts on. A -1 can be used
        for a gate that is allowed to act on any number of qubits.

        :param gate_name: Name of the gate. If using qiskit/cirq, it should not conflict with the name of a qiskit/cirq gate.
        :param n_qubits: Number of qubits that the gate acts on. Use -1 to denote any number.
        :param overwrite: Overwrite existing gate entries. Default is False.
        """
        if not isinstance(gate_name, str):
            raise ValueError(f"Gate name must be a string. Got {type(gate_name)}.")
        if not isinstance(n_qubits, int) or (
            n_qubits != -1 and not (1 <= n_qubits <= MAX_QUBITS_PER_GATE_OR_CHANNEL)
        ):
            raise ValueError(
                f"Gate size must be a positive integer <= {MAX_QUBITS_PER_GATE_OR_CHANNEL}, or -1. Got {n_qubits}."
            )

        if gate_name in self.supported_gate_sizes and not overwrite:
            raise ValueError(
                f"Gate name {gate_name} conflicts with an existing supported gate (of size {self.supported_gate_sizes[gate_name]}). To overwrite, ensure that the `overwrite` argument is set to True."
            )
        self.supported_gate_sizes[gate_name] = n_qubits

    def update(self, other: "NoiseModel"):
        """
        Update the NoiseModel object with the GateNoise objects of another NoiseModel object.
        Duplicates are identified and merged by the add_gate_noise method.
        """
        map(
            self.add_gate_noise,  # type: ignore
            [
                *other._gate_noise_general,
                *other._gate_noise_specific,
            ],
        )

    def specific_gate_noise_lookup(self, gate_name: str) -> GateNoise | None:
        """
        Find a SpecificGateNoise object that is triggered by the given gate name. If no GateNoise object is found, returns None.
        """
        # Search for a specific gate noise entry with matching gate_name
        for gate_noise in self._gate_noise_specific:
            if gate_noise.gate_name == gate_name:
                return gate_noise

        return None

    def generic_gate_noise_lookup(self) -> GateNoise | None:
        """
        Find a GenericGateNoise object. If no GateNoise object is found, returns None.

        :return: A GenericGateNoise object, or None if no match is found.
        """
        # TODO: This function is a bit redundant at this point, but it might be useful in the future
        # Search for a generic gate noise entry with the right number of qubits or matching 'any'
        if self._gate_noise_general:
            return self._gate_noise_general[0]
        else:
            return None

    def _validate_gate_noise_qubits_with_model(self, gate_noise: GateNoise):
        for qubit_noise in gate_noise.specific_qubit_noise:
            assert set(qubit_noise.qubit_strings).issubset(
                set(self.qubit_strings)
            ), f"Added gate noise object has qubits {qubit_noise.qubit_objects} that do not match noise model {self.qubit_objects}"

        for qubit_noise in (
            gate_noise.specific_qubit_noise + gate_noise.generic_qubit_noise
        ):
            for qubits, _ in qubit_noise.channels["pre"] + qubit_noise.channels["post"]:
                if qubits != "same":
                    assert set([q._string for q in qubits]).issubset(
                        set(self.qubit_strings)
                    ), f"Added gate noise object has qubits {[q.object for q in qubits]} that do not match noise model {self.qubit_objects}"

    def _validate_specific_gate_noise_with_model(self, gate_noise: SpecificGateNoise):
        if gate_noise.gate_name not in self.supported_gate_sizes:
            raise ValueError(
                f"Gate noise object has gate name {gate_noise.gate_name}, which is not in the supported gate names."
            )
        required_n_qubits = self.supported_gate_sizes[gate_noise.gate_name]

        if required_n_qubits != -1:
            for qubit_noise in gate_noise.specific_qubit_noise:
                if isinstance(qubit_noise, SpecificQubitNoise):
                    if len(qubit_noise.qubits) != required_n_qubits:
                        raise ValueError(
                            f"Added gate noise object has qubit noise object {qubit_noise} with {len(qubit_noise.qubits)} qubits, but the gate acts on {required_n_qubits} qubits."
                        )
                elif isinstance(qubit_noise, GenericQubitNoise):
                    if (
                        isinstance(qubit_noise.n_qubits, int)
                        and qubit_noise.n_qubits != required_n_qubits
                    ):
                        raise ValueError(
                            f"Added gate noise object has qubit noise object {qubit_noise} with {qubit_noise.n_qubits} qubits, but the gate acts on {required_n_qubits} qubits."
                        )

    def add_gate_noise(self, gate_noise: GateNoise):
        """
        Adds a GateNoise object to the noise model.
        If a GateNoise object with the same triggering conditions already exists, it is updated instead.
        """
        self._validate_gate_noise_qubits_with_model(gate_noise)

        if isinstance(gate_noise, SpecificGateNoise):
            # Validate this gate noise against the supported gate sizes dict
            self._validate_specific_gate_noise_with_model(gate_noise)
            # If the gate noise is not already present (meaning: same triggers at the GateNoise level), add it
            if gate_noise not in self._gate_noise_specific:
                self._gate_noise_specific.append(gate_noise)
            # Otherwise, update the existing gate noise with the new one (which might mean updating the QubitNoise
            # objects it contains, or the channels of its QubitNoise objects, if they already exist)
            else:
                self._gate_noise_specific[
                    self._gate_noise_specific.index(gate_noise)
                ].update(gate_noise)
        elif isinstance(gate_noise, GenericGateNoise):
            if gate_noise not in self._gate_noise_general:
                self._gate_noise_general.append(gate_noise)
            else:
                self._gate_noise_general[
                    self._gate_noise_general.index(gate_noise)
                ].update(gate_noise)
        else:
            raise ValueError(
                f"Unrecognized gate_noise object {gate_noise} of type {type(gate_noise)}"
            )

    def get_readout_error(self, qubit: QubitInternal | str) -> BitFlipChannel | None:
        """
        Return the readout error for qubit ``qubit``. If there is no specific entry for the qubit,
        then the readout error for the 'any' qubit is returned. If there is no entry for the 'any' qubit,
        then None is returned.
        """
        any_channel = None
        for other_qubit, channel in self._readout_errors:
            if str(qubit) == str(other_qubit):
                return channel
            if other_qubit == ANY:
                any_channel = channel
        return any_channel

    # Overloads for typing purposes
    @overload
    def get_noise_channels(
        self,
        gate_name: str,
        gate_qubits: Sequence[str] | Sequence[QiskitQubit] | Sequence[CirqQubit],
        trace: Literal[False],
    ) -> Noise | None:
        ...

    @overload
    def get_noise_channels(
        self,
        gate_name: str,
        gate_qubits: Sequence[str] | Sequence[QiskitQubit] | Sequence[CirqQubit],
        trace: Literal[True],
    ) -> tuple[Noise | None, dict]:
        ...

    @overload
    def get_noise_channels(
        self,
        gate_name: str,
        gate_qubits: Sequence[str] | Sequence[QiskitQubit] | Sequence[CirqQubit],
    ) -> Noise | None:
        ...

    def get_noise_channels(
        self,
        gate_name: str,
        gate_qubits: Sequence[str] | Sequence[QiskitQubit] | Sequence[CirqQubit],
        trace: bool = False,
    ) -> Noise | None | tuple[Noise | None, dict]:
        """
        Get all noise channels (pre and post) that are triggered by the application of gate ``gate_name`` to qubits ``gate_qubits``.

        The lookup process uses the following decision process:
            First, a GateNoise object is obtained, via the following:
                - A GateNoise object is searched for that matches the gate name (SpecificGateNoise object).
                - If no match is found, a GateNoise object is searched for that matches the number of qubits that the gate acts on (GenericGateNoise object).
                - If no match is found, a GateNoise object is searched for that matches 'any' number of qubits (GenericGateNoise object).

            Once a GateNoise object is found, the following process is used to find a QubitNoise object:
                - A QubitNoise object is searched for that matches the qubits that the gate acts on (SpecificQubitNoise object).
                - If no match is found, a QubitNoise object is searched for that matches the number of qubits that the gate acts on (GenericQubitNoise object).
                - If no match is found, a QubitNoise object is searched for that matches 'any' number of qubits (GenericQubitNoise object).

            If a QubitNoise object is found, its channels are returned. If nothing is found, None is returned.

        The process follows a 'as specific as possible, falling back to generics' approach, with the order of precedence being:
            1. Gate noise: name > n_qubits > 'any'
            2. Qubit noise: qubits > n_qubits > 'any'

        I.e. emphasis is put on finding as specific a gate noise object as possible, and then as specific as possible qubit noise object.

        :param gate_name: The name of the gate that triggers the channel.
        :param gate_qubits: The qubits that the gate acts on.
        :param trace: If True, returns the trace of the lookup process as well as the channels.

        :return: A dictionary with keys 'pre' and 'post', where each maps to a list of (target, channel) pairs,
                where the target is a tuple of qubit labels that the channel acts on, and the channel a NoiseChannel object.
                If no noise channels are found, returns None.
                If trace is True, returns a tuple of the channels and the trace of the lookup process (the latter is a dictionary).
        """

        # Convert gate_qubits to a list if they are a tuple. Throw an error if gate_qubits is not a tuple or list
        if isinstance(gate_qubits, tuple):
            gate_qubits = list(gate_qubits)

        if not is_qubit_list(gate_qubits):
            raise ValueError(
                f"gate_qubits should be a list or tuple of qubit objects (string, Qiskit qubit or Cirq qubit)."
            )

        # If the gate acts on qubits that are not included in the model, return None
        if not set(qubits_to_strings(gate_qubits)).issubset(set(self.qubit_strings)):
            if trace:
                return None, {"Error": "Gate acts on qubits not included in the model"}
            return None

        # Check that the gate is supported
        if gate_name not in self.supported_gate_sizes:
            raise ValueError(
                f"Gate {gate_name} is not supported by the noise model. You can add the gate to the list of supported gates by calling the add_supported_gate method."
            )
        if (
            self.supported_gate_sizes[gate_name] != -1
            and len(gate_qubits) != self.supported_gate_sizes[gate_name]
        ):
            raise ValueError(
                f"Gate {gate_name} acts on {len(gate_qubits)} qubits, but the gate is specified to act on {self.supported_gate_sizes[gate_name]} qubits."
            )

        trace_dict = {}
        specific_trace = None
        generic_trace = None

        channels: dict | None = None

        # First try to find a specific gate noise object
        gate_noise_object = self.specific_gate_noise_lookup(gate_name)

        # If we found one, try to find find matching noise channels
        if gate_noise_object is not None:
            channels, gate_noise_trace = gate_noise_object.get_noise_channels(
                gate_qubits, trace=True
            )
            specific_trace = {"name": gate_name, "trace": gate_noise_trace}

        # If no gate noise object or channels were found, try to find a generic noise object using the number of qubits
        if gate_noise_object is None or channels is None:
            gate_noise_object = self.generic_gate_noise_lookup()
            # If we found one, try to find find matching noise channels
            if gate_noise_object is not None:
                channels, gate_noise_trace = gate_noise_object.get_noise_channels(
                    gate_qubits, trace=True
                )
                generic_trace = {"name": "any", "trace": gate_noise_trace}

        trace_dict["specific_gate"] = specific_trace
        trace_dict["generic_gate"] = generic_trace

        # If tracing is turned on, return the channels and the trace
        if trace:
            return channels, trace_dict
        # Otherwise, just return the channels
        else:
            return channels

    def add(
        self,
        gate_name: str | Any,
        gate_qubits: Qubits | int,
        channel: NoiseChannel,
        channel_qubits: Qubits | Literal["same"],
        when: Literal["post"] | Literal["pre"] = "post",
    ):
        """
        Add a noise channel to the noise model. I.e. one which is triggered by the combination of ``gate_name`` applied to ``gate_qubits``,
        and acts on ``channel_qubits``.

        The channel will be applied either before or after the gate, depending on the value of ``when``.

        Special cases to consider:
            Triggering conditions:
                - ``gate_name`` is ANY: The channel will be triggered by any gate for which a more specific (with a named gate) entry has not been found.
                - ``gate_qubits`` is an integer: The channel will be triggered by the given gate when it acts on ``gate_qubits`` qubits for which a more specific (with specified qubits) entry has not been found.

            Channel application:
                - ``channel_qubits`` is 'same': The channel will be applied to the same qubits as the gate that triggered it. In this case the channel should act on the same number
                    of qubits, or on single qubits (and then one copy of the channel will be applied to each qubit).

        :param gate_name: The name of the gate that triggers the channel. Can be ANY (or any instance of Any) to match any gate.
        :param gate_qubits: The qubits that the gate acts on. Either a sequence of qubits, or an integer to match a specific number of qubits.
        :param channel: The channel to apply when the triggering conditions are met.
        :param channel_qubits: The qubits that the channel acts on. Can be 'same' to match the qubits that the gate acts on. If these qubits are not known ahead of time, they are determined
        at 'run-time' (i.e. once a circuit has been provided).

        """
        # Checks on the gate name and gate qubits, and supported gate sizes
        if not isinstance(gate_name, Any):
            # Check that the gate is supported
            if gate_name not in self.supported_gate_sizes:
                raise ValueError(
                    f"Error adding noise rule: Gate {gate_name} is not supported by the noise model. You can add the gate to the list of supported gates by calling the add_supported_gate method."
                )

            # Check that the number of gates matches the supported gate size
            supported_gate_size = self.supported_gate_sizes[gate_name]
            if isinstance(gate_qubits, Sequence):
                gate_size = len(gate_qubits)
            elif isinstance(gate_qubits, int):
                gate_size = gate_qubits
            else:
                raise ValueError(
                    "Gate qubits must be specified as a sequence of qubits, or an integer."
                )

            if supported_gate_size != -1 and gate_size != supported_gate_size:
                raise ValueError(
                    f"Error adding noise rule: Gate {gate_name} is combined with {gate_size} qubits, but the gate acts on {supported_gate_size} qubits."
                )

        if not isinstance(gate_qubits, int):
            # Check that the gate qubits are a list or tuple
            if not isinstance(gate_qubits, Sequence):
                raise ValueError(
                    f"Error adding noise rule: Gate qubits are of unrecognized type. They should be list of qubits (qiskit / cirq qubit objects or strings), or int."
                )
            # Check that the gate qubits are included in the model
            # (Note: this conversion checks internally that gate_qubits is a list of qubit objects)
            if not set(qubits_to_strings(gate_qubits)).issubset(self.qubit_strings):
                raise ValueError(
                    f"Error adding noise rule: The noise channel is triggered by qubits {gate_qubits}, which are not all included in the model qubits {self.qubit_objects}."
                )

        # Convert gate qubits to a list if they were given as a tuple
        if isinstance(gate_qubits, tuple):
            gate_qubits = list(gate_qubits)
        # Convert channel qubits to a list if they were given as a tuple
        if isinstance(channel_qubits, tuple):
            channel_qubits = list(channel_qubits)

        # Checks on the channel qubits
        if channel_qubits != "same":
            # Check that the channel qubits are included in the model
            if not set(qubits_to_strings(channel_qubits)).issubset(self.qubit_strings):
                raise ValueError(
                    f"Error adding noise rule: The channel {channel} acts on qubits {channel_qubits}, which are not all included in the model qubits {self.qubit_objects}."
                )

        # Case 1: Specific GateNoise object
        if gate_name != ANY and isinstance(gate_name, str):
            gate_noise_object = self.specific_gate_noise_lookup(gate_name)
            # If no SpecificGateNoise object was found, create a new one
            if gate_noise_object is None:
                gate_noise_object = SpecificGateNoise(gate_name=gate_name)
                self._gate_noise_specific.append(gate_noise_object)

        # Case 2: Generic GateNoise object
        else:
            gate_noise_object = self.generic_gate_noise_lookup()
            # If no GenericGateNoise object was found, create a new one
            if gate_noise_object is None:
                gate_noise_object = GenericGateNoise()
                self._gate_noise_general.append(gate_noise_object)

        # Attempt to find the QubitNoise object that matches the gate_qubits
        # Case 1: Specific QubitNoise object (gate_qubits are a list of qubit objects, not an integer)
        if is_qubit_list(gate_qubits):
            qubit_noise_object = gate_noise_object.specific_qubit_noise_lookup(
                gate_qubits
            )
            # If no SpecificQubitNoise object was found, create a new one
            if qubit_noise_object is None:
                qubit_noise_object = SpecificQubitNoise(qubits=gate_qubits)
                gate_noise_object.add(qubit_noise_object)

        # Case 2: Generic QubitNoise object, gate_qubits is an integer
        elif isinstance(gate_qubits, int):
            qubit_noise_object = gate_noise_object.generic_qubit_noise_lookup(
                gate_qubits
            )
            # If no GenericQubitNoise object was found, create a new one
            if qubit_noise_object is None:
                qubit_noise_object = GenericQubitNoise(n_qubits=gate_qubits)
                gate_noise_object.add(qubit_noise_object)

        # Vacuous else for mypy
        else:
            raise ValueError(
                "Gate qubits are not sequences of qubit object or int as required."
            )

        # Add the channel to the QubitNoise object
        qubit_noise_object.add((channel_qubits, channel), when)

    # TODO not tested yet
    def add_readout_error(
        self,
        qubit: str | Any | CirqQubit | QiskitQubit | QubitInternal,
        p0: float,
        p1: float,
    ):
        """
        Add readout error to the noise model, acting on either a particular qubit or all qubits (for which a
        particular readout error has not been added).

        :param qubit: The qubit that the readout error acts on. Can be ANY (or any instance of Any) to match any qubit.
        :param p0: The probability of a 0 being read out as a 1.
        :param p1: The probability of a 1 being read out as a 0.
        """

        internal_qubit: QubitInternal | Any
        if isinstance(qubit, Any):
            internal_qubit = ANY
        elif isinstance(qubit, QubitInternal):
            internal_qubit = qubit
        else:
            internal_qubit = QubitInternal(object=qubit)

        if (
            not isinstance(internal_qubit, Any)
            and internal_qubit._string not in self.qubit_strings
        ):
            raise ValueError(
                f"The readout error acts on qubit {qubit}, which is not included in the model."
            )
        if not (0 <= p0 <= 1 and 0 <= p1 <= 1):
            raise ValueError(
                f"The readout error probabilities must be between 0 and 1, but are {p0} and {p1}."
            )

        # Make the bitflip channel and add it to the readout errors, replacing existing channels
        bitflip_channel = BitFlipChannel(p0=p0, p1=p1)

        # Find any existing readout error for this qubit, and replace it
        for idx, (existing_qubit, _) in enumerate(self._readout_errors):
            if existing_qubit == internal_qubit:
                self._readout_errors[idx] = (internal_qubit, bitflip_channel)
                return

        self._readout_errors.append(
            (
                internal_qubit,
                bitflip_channel,
            )
        )

    def on_circuit(self, circuit: list[dict] | Circuit):
        """
        Apply the noise model to a circuit (in serialized form).

        :param serialized_circuit: A serialized circuit, i.e. a list of dictionaries, each of which represents a gate in the circuit.

        :return: A dictionary with two keys:
            - 'noise_by_gate': A list of dictionaries, one for each gate in the circuit, giving the gate and the noise channels that are applied before and after the gate.
            - 'missing_noise': A list of dictionaries, one for each gate in the circuit for which no noise channels were found, giving the gate, the position in the circuit, and the trace of the lookup process (useful for debugging).
        """
        # Serialize the circuit if it is not already
        if is_qiskit_circuit(circuit) or is_cirq_circuit(circuit):
            serialized_circuit = serialize_circuit(circuit)
        elif isinstance(circuit, list):
            serialized_circuit = circuit
        else:
            raise ValueError(f"Unrecognized circuit type for circuit {circuit}.")

        noise_info = []
        missed_gates = []
        for idx, gate in enumerate(serialized_circuit):
            # Use the label if possible (for custom gates), otherwise the gate name itself
            gate_name = gate["label"]

            gate_qubits = gate["qubits"]

            noise_channels, trace = self.get_noise_channels(
                gate_name, gate_qubits, trace=True
            )

            if noise_channels is None:
                # Add the gate to the list of missed gates, and give the trace of the lookup
                missed_gates.append(
                    {
                        "position": idx,
                        "gate": gate,
                        "trace": trace,
                    }
                )
            noise_info.append({"gate": gate, "noise": noise_channels})

        return {
            "noise_by_gate": noise_info,
            "readout_error": self.readout_errors,
            "missing_noise": missed_gates,
        }
