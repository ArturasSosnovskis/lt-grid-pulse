from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass
from datetime import date

# Sanity limits for electricity prices in Lithuania, manual choice.
# Records with prices outside the range go to quarantine.
# Change limits if valid readings end in quarantine.
ELERING_PRICE_LOWER_BOUND = -500
ELERING_PRICE_UPPER_BOUND = 4000
# UNIX time start boundary, to catch negative time values.
ELERING_TS_LOWER_BOUND = 0


class EleringRawRow(BaseModel):
    model_config = ConfigDict(strict=True)

    timestamp: int = Field(ge=ELERING_TS_LOWER_BOUND)
    price: float = Field(ge=ELERING_PRICE_LOWER_BOUND, le=ELERING_PRICE_UPPER_BOUND)


@dataclass
class QuarantinedRow:
    day: date
    raw: str
    reason: str
