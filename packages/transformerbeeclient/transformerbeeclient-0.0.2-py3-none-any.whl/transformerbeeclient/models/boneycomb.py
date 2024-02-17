"""
contains the BOneyComb model class
"""

from typing import Any

from pydantic import BaseModel

_BusinessObject = dict[str, Any]  # because transformer.bee uses BO4E.net ⚡ bo4e-python


class BOneyComb(BaseModel):
    """
    BOneyComb is a data structure that represents a "transaction" in the marktkommunikation.
    1 transaction is 1 "Geschäftsvorfall".
    """

    stammdaten: list[_BusinessObject]  #: the business objects
    transaktionsdaten: dict[str, str]
    """
    Transaktionsdaten are metadata related to the Marktprozess and are not related to a specific Business object.
    """
    links: dict[str, list[str]] | None = None
