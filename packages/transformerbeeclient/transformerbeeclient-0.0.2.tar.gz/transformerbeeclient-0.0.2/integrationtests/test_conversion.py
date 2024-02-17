import json
from pathlib import Path

from maus.edifact import EdifactFormatVersion

from transformerbeeclient.client import TransformerBeeClient
from transformerbeeclient.models.boneycomb import BOneyComb


class TestConversion:
    """
    tests, that we can convert bo4e/edifact and vice versa
    """

    async def test_edifact_to_bo4e_without_authentication(self, unauthenticated_client: TransformerBeeClient):
        with open(Path(__file__).parent / "TestEdifact" / "FV2310" / "55001.edi", "r", encoding="utf-8") as edifile:
            edifact = edifile.read()
        actual = await unauthenticated_client.convert_to_bo4e(edifact, EdifactFormatVersion.FV2310)
        assert isinstance(actual, list)
        assert all(isinstance(x, BOneyComb) for x in actual[0].transaktionen)

    async def test_bo4e_to_edifact_without_authentication(self, unauthenticated_client: TransformerBeeClient):
        with open(Path(__file__).parent / "TestEdifact" / "FV2310" / "55001.json", "r", encoding="utf-8") as edifile:
            boneycomb = BOneyComb.model_validate(json.load(edifile))
        actual = await unauthenticated_client.convert_to_edifact(boneycomb, EdifactFormatVersion.FV2310)
        assert isinstance(actual, str)
        assert actual.startswith("UNA:+.? 'UNB+UNOC:")

    async def test_edifact_to_bo4e_with_authentication(self, oauthenticated_client: TransformerBeeClient):
        with open(Path(__file__).parent / "TestEdifact" / "FV2310" / "55001.edi", "r", encoding="utf-8") as edifile:
            edifact = edifile.read()
        actual = await oauthenticated_client.convert_to_bo4e(edifact, EdifactFormatVersion.FV2310)
        assert isinstance(actual, list)
        assert all(isinstance(x, BOneyComb) for x in actual[0].transaktionen)

    async def test_bo4e_to_edifact_with_authentication(self, oauthenticated_client: TransformerBeeClient):
        with open(Path(__file__).parent / "TestEdifact" / "FV2310" / "55001.json", "r", encoding="utf-8") as edifile:
            boneycomb = BOneyComb.model_validate(json.load(edifile))
        actual = await oauthenticated_client.convert_to_edifact(boneycomb, EdifactFormatVersion.FV2310)
        assert isinstance(actual, str)
        assert actual.startswith("UNA:+.? 'UNB+UNOC:")
