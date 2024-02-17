"""
models used in the transformer.bee API
"""

from maus.edifact import EdifactFormatVersion
from pydantic import BaseModel, ConfigDict, Field


class EdifactToBo4eRequest(BaseModel):
    """
    The request to convert edifact to bo4e
    """

    model_config = ConfigDict(populate_by_name=True)
    edifact: str = Field(alias="EDI")  #: the edifact as plain string
    format_version: EdifactFormatVersion = Field(alias="FormatPackage")  #: the format version to use
    use_map: bool = Field(alias="UseMap", default=False)  #: legacy for MP. can be false by default


class EdifactToBo4eResponse(BaseModel):
    """
    The response to an EdifactToBo4eRequest
    """

    bo4e_json: str = Field(alias="BO4E")  #: the marktnachrichten as string
    edifact_format_version: EdifactFormatVersion = Field(alias="FormatPackage")  #: see maus.EdifactFormatVersion


class Bo4eTransactionToEdifactRequest(BaseModel):
    """
    The request to convert a single transaction/BOneyComb to edifact
    """

    model_config = ConfigDict(populate_by_name=True)
    bo4e_json_string: str = Field(alias="BO4E")  #: the BOneyComb as json string
    format_version: EdifactFormatVersion = Field(alias="FormatPackage")  #: the format version to use


class Bo4eTransactionToEdifactResponse(BaseModel):
    """
    The response to a Bo4eTransactionToEdifactRequest
    """

    edifact: str = Field(alias="EDI")  #: the edifact as plain string
