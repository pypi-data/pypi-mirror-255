from typing import Any, Literal, TypeGuard, Union

from pydantic import Field, PrivateAttr, validator

from ..serializers.custom_types import CirqQubit, QiskitQubit
from ..utils.constants import MAX_QUBITS_PER_GATE_OR_CHANNEL
from .channel import NoiseChannel
from .typing import Qubits, is_internal_qubit_list, qubits_to_internal_qubits
from .utils import BaseNoiseComponent, QubitInternal, tuples_to_lists


class QubitNoise(BaseNoiseComponent):
    """
    Base class for qubit noise, should not be initialised directly.

    QubitNoise objects contain lists of noise channels that are applied before/after a gate.
    The noise channels of a QubitNoise object are applied whenever a gate is encountered in the circuit that matches its parent GateNoise object,
    and when the qubits that it acts on matches those specified in the QubitNoise object.

    There are currently two subclasses of QubitNoise:
        - SpecificQubitNoise: Noise that is triggered by specific qubits.
        - GenericQubitNoise: Noise that is triggered by unspecified qubits. The number of qubits that trigger the noise can be specified, or set to 'any'.
    """

    # The channels applied before and after the gate that triggers the noise, in order of the list.
    # These are private fields, that should only be filled with the 'add' functions.
    _channels_pre: list[
        tuple[list[QubitInternal] | Literal["same"], NoiseChannel]
    ] = PrivateAttr(default=[])
    _channels_post: list[
        tuple[list[QubitInternal] | Literal["same"], NoiseChannel]
    ] = PrivateAttr(default=[])

    def _validate_channel(
        self,
        channel: NoiseChannel,
        target_qubits: list[QubitInternal] | Literal["same"],
    ) -> tuple[list[QubitInternal] | Literal["same"], NoiseChannel]:
        """
        Validate a single channel application against the QubitNoise object.
        """
        raise NotImplementedError(
            f"Method _validate_channel not implemented for class {self.__class__.__name__}."
        )

    @property
    def channels(
        self,
    ) -> dict[
        Literal["pre", "post"],
        list[tuple[list[QubitInternal] | Literal["same"], NoiseChannel]],
    ]:
        return {"pre": self._channels_pre, "post": self._channels_post}

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, self.__class__):
            return False
        # Equality between two QubitNoise objects is determined by their fields (but not the channels that they contain)
        try:
            for field_name in self.__fields__.keys():
                if getattr(self, field_name) != getattr(__value, field_name):
                    return False
        except AttributeError:
            return False
        return True

    def update(self, other: "QubitNoise"):
        """
        Update the QubitNoise object with the channels of another QubitNoise object. Duplicates are not checked.
        Note that all channels in this 'other' qubitnoise have already been validated w.r.t. the qubits, so no
        additional checks are needed.

        :param other: QubitNoise object of which all channels are applied.
        """
        self._channels_pre.extend(other._channels_pre)
        self._channels_post.extend(other._channels_post)

    def add(
        self,
        targets_channels: list[tuple[Qubits | Literal["same"], NoiseChannel]]
        | tuple[Qubits | Literal["same"], NoiseChannel],
        when: Literal["pre", "post"] = "post",
    ):
        """
        Add one or more noise channels to the QubitNoise object.

        :param channels: The noise channel(s) to add.
        :param targets: The qubits that the channel(s) act on. If ``channels`` is a list, these should be provided as a list of the same length. A target
        can be specified via a tuple of qubit labels, or by setting it to 'same' to indicate that the channel acts on the same qubits as the gate that triggered it.
        """
        if isinstance(targets_channels, tuple) and isinstance(
            targets_channels[1], NoiseChannel
        ):
            targets_channels = [targets_channels]

        to_add: list[tuple[list[QubitInternal] | Literal["same"], NoiseChannel]] = [
            self._validate_channel(channel, targets)
            if targets == "same"
            else self._validate_channel(channel, qubits_to_internal_qubits(targets))
            for targets, channel in targets_channels
        ]
        if when == "pre":
            self._channels_pre.extend(to_add)
        elif when == "post":
            self._channels_post.extend(to_add)
        else:
            raise ValueError(
                "Supported values for argument ``when`` are: 'pre', 'post'."
            )

    # to_dict and from_dict are overridden to allow for conversion between tuples and lists for the _channels_pre and _channels_post attributes
    def to_dict(self):
        """
        Convert the QubitNoise object to a dictionary representation.
        """
        all_field_names = self.__fields__.keys()

        # Collect fields
        fields = {
            field_name: getattr(self, field_name) for field_name in all_field_names
        }
        return {
            "type": self.__class__.__name__,
            "fields": fields,
            # Convert the _channels_pre and _channels_post from lists of tuples to lists of lists
            "_channels_pre": tuples_to_lists(self._channels_pre),
            "_channels_post": tuples_to_lists(self._channels_post),
        }

    @classmethod
    def from_dict(cls, d):
        # Create an instance of the class with the fields specified in the dictionary
        obj = cls(**d["fields"])

        # Manually add the channels (this avoids trying to set the private variables _channels_pre and _channels_post)
        for target_qubits, channel in d["_channels_pre"]:
            if isinstance(target_qubits, tuple):
                target_qubits = list(target_qubits)
            obj.add(
                [
                    (
                        target_qubits,
                        channel,
                    )
                ],
                "pre",
            )
        for target_qubits, channel in d["_channels_post"]:
            if isinstance(target_qubits, tuple):
                target_qubits = list(target_qubits)
            obj.add(
                [
                    (
                        target_qubits,
                        channel,
                    )
                ],
                "post",
            )
        return obj


class SpecificQubitNoise(QubitNoise):
    """
    Class to represent noise that is triggered by specific qubits.

    - Channels can be added to this object that act on specific qubits, or on the same qubits as the gate that triggered the noise.
    """

    qubits: list = Field(
        description="The qubits that trigger this particular QubitNoise as strings, qiskit or Cirq qubits, or QubitInternal objects (internal representation)"
    )

    _format: Literal["fermioniq"] | Literal["qiskit"] | Literal["cirq"] = PrivateAttr(
        default="fermioniq"
    )

    @property
    def qubit_strings(self) -> list[str]:
        return [q._string for q in self.qubits]

    @property
    def qubit_objects(self) -> list[str | QiskitQubit | CirqQubit]:
        return [q.object for q in self.qubits]

    @validator("qubits")
    def validate_qubits(cls, qubits, values):
        """
        - Check that qubits are a non-empty list of unique strings, qiskit qubits or cirq qubits.
        - Converts to a list of internal Qubit objects for storage
        """
        if not qubits:
            raise ValueError("The list of qubits given to the noise model is empty")

        if len(set(qubits)) != len(qubits):
            raise ValueError(
                f"Qubits do not occur uniquely in the list given to the QubitNoise object: {qubits}"
            )

        if not 1 <= len(qubits) <= MAX_QUBITS_PER_GATE_OR_CHANNEL:
            raise ValueError(
                f"Only gates on up to {MAX_QUBITS_PER_GATE_OR_CHANNEL} are currently supported, but found: {qubits}"
            )

        # this checks that qubits are a list, and creates qubit objects
        return qubits_to_internal_qubits(qubits)

    def _validate_channel(
        self,
        channel: NoiseChannel,
        target_qubits: list[QubitInternal] | Literal["same"],
    ) -> tuple[list[QubitInternal] | Literal["same"], NoiseChannel]:
        """
        Validate a single channel application against the QubitNoise object.
        Here 'target_qubits' should be internal Qubit objects, as they have been converted to internal objects by the 'add' function.
        """

        if not isinstance(channel, NoiseChannel):
            raise ValueError(
                f"Expected NoiseChannel object for argument `channel`, but got {type(channel)}."
            )

        # Case 1: The channel acts on target qubits that were specified.
        if is_internal_qubit_list(target_qubits):
            # Check that the number of target qubits matches the size of the channel
            if channel.n_qubits not in (1, len(target_qubits)):
                raise ValueError(
                    f"{len(target_qubits)} target qubits for the channel were specified, but the channel acts on {channel.n_qubits} qubits. "
                    f"The channel should act on either {len(target_qubits)} or 1 qubits to be applied to qubits {target_qubits}."
                )
            return (
                target_qubits,
                channel,
            )

        # Case 2: The channel acts on unspecified target qubits. "same"
        else:
            # Case 2.1: The channel acts on the same number of qubits as the QubitNoise is triggered by. Then a single copy of the channel is applied to the same qubits as the gate.
            if channel.n_qubits == len(self.qubits):
                return (
                    self.qubits,
                    channel,
                )
            # Case 2.2: The channel acts on single qubits. Then a copy of the channel is applied to each qubit that triggers the QubitNoise object. This will be performed at run-time.
            elif channel.n_qubits == 1:
                return (
                    "same",
                    channel,
                )
            else:
                raise ValueError(
                    f"Target qubits for the channel specified as {target_qubits}, but the channel acts on {channel.n_qubits} qubits. "
                    f"Note that the channel should act on either {len(self.qubits)} or 1 qubits to be applied to the same qubits as the gate that triggers it."
                )


class GenericQubitNoise(QubitNoise):
    """
    Class to represent noise that is triggered by unspecified qubits. The number of qubits that trigger the noise must be
    provided, although this can be set to 'any' to specify that the noise can be triggered by any number of qubits.

    - Channels can be added to this object that act on specific qubits, or on the same qubits as the gate that triggered the noise.
    """

    n_qubits: int = Field(
        description="The number of qubits that trigger this particular QubitNoise.",
        ge=1,
        le=MAX_QUBITS_PER_GATE_OR_CHANNEL,
    )

    def _validate_channel(
        self,
        channel: NoiseChannel,
        target_qubits: list[QubitInternal] | Literal["same"],
    ) -> tuple[list[QubitInternal] | Literal["same"], NoiseChannel]:
        """
        Validate a single channel application against the QubitNoise object.
        Here 'target_qubits' should be internal Qubit objects, as they have been converted to internal objects by the 'add' function.
        """
        if not isinstance(channel, NoiseChannel):
            raise ValueError(
                f"Expected NoiseChannel object for argument `channel`, but got {type(channel)}."
            )

        # Case 1: The channel acts on target qubits that were specified.
        # if isinstance(target_qubits, tuple):
        if is_internal_qubit_list(target_qubits):
            # Check that the number of target qubits matches the size of the channel
            if channel.n_qubits not in (1, len(target_qubits)):
                raise ValueError(
                    f"{len(target_qubits)} target qubits for the channel were specified, but the channel acts on {channel.n_qubits} qubits. "
                    f"The channel should act on either {len(target_qubits)} or 1 qubits to be applied to qubits {target_qubits}."
                )
            return (
                target_qubits,
                channel,
            )

        # Case 2: The channel acts on the same number of qubits as the QubitNoise is triggered by, or on single qubits.
        # Then the particular qubits that this channel is applied to will be determined at run-time.
        elif channel.n_qubits in (
            1,
            self.n_qubits,
        ):
            return "same", channel

        # If we made it this far, it means that an error occured. Precisely, the target qubits for the channel weren't specified,
        # and the channel acts on an inappropriate number of qubits given this QubitNoise object.
        else:
            if self.n_qubits == 1:
                raise ValueError(
                    f"Target qubits for channel specified as 'same' as gate qubits, but the channel acts on {channel.n_qubits} qubits. "
                    f"The channel should act on 1 qubit in order to be applied to the same qubits as the gate that triggers it."
                )
            else:
                raise ValueError(
                    f"Target qubits for channel specified as 'same' as gate qubits, but the channel acts on {channel.n_qubits} qubits. "
                    f"The channel should act on either {self.n_qubits} or 1 qubits to be applied to the same qubits as the gate that triggers it."
                )
