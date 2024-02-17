"""
contains the marktnachricht model class
"""

from pydantic import BaseModel, ConfigDict, Field, RootModel

from transformerbeeclient.models.boneycomb import BOneyComb, _BusinessObject


class Marktnachricht(BaseModel):
    """
    BOneyComb is a data structure that represents a "transaction" in the marktkommunikation.
    1 transaction is 1 "Geschäftsvorfall".
    """

    model_config = ConfigDict(populate_by_name=True)
    unh: str = Field(alias="UNH")  #: the UNH (interchange header) of the message
    transaktionen: list[BOneyComb] = Field(alias="transaktionen")
    """
    One marktnachricht contains at least 1 transaction aka BOneyComb
    """
    stammdaten: list[_BusinessObject] = Field(alias="stammdaten")
    """
    overall stammdaten of the marktnachricht
    """
    nachrichtendaten: dict[str, str] = Field(alias="nachrichtendaten")
    """
    Nachrichtendaten are similar to transaktionsdaten but not 100% identical
    """


_ListOfMarktnachricht = RootModel(list[Marktnachricht])
