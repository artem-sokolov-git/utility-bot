from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import Numeric, text
from sqlalchemy.orm import mapped_column

int_pk = Annotated[
    int,
    mapped_column(primary_key=True),
]
created_at = Annotated[
    datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())")),
]
updated_at = Annotated[
    datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=lambda: datetime.now()),
]

uah = Annotated[Decimal, mapped_column(Numeric(10, 2))]

str_255 = Annotated[str, 255]
