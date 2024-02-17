"""
protocols for typing only; They are useful to mock and patch stuff
"""

from typing import Protocol

from maus.edifact import EdifactFormatVersion

from transformerbeeclient.models.boneycomb import BOneyComb
from transformerbeeclient.models.marktnachricht import Marktnachricht


class CanConvertToBo4e(Protocol):  # pylint:disable=too-few-public-methods
    """
    Interface of all the things that can convert EDIFACT to BO4E
    """

    async def convert_to_bo4e(self, edifact: str, edifact_format_version: EdifactFormatVersion) -> list[Marktnachricht]:
        """convert the given edifact to a list of marktnachrichten"""


class CanConvertToEdifact(Protocol):  # pylint:disable=too-few-public-methods
    """
    Interface of all the things that can convert BO4E to EDIFACT
    """

    async def convert_to_edifact(self, boney_comb: BOneyComb, edifact_format_version: EdifactFormatVersion) -> str:
        """convert the given boney_comb to edifact assuming the format version is correct."""


class TransformerBeeClient(CanConvertToEdifact, CanConvertToBo4e):
    """
    Transformer.bee can convert to and from edifact
    """
