from datetime import datetime
from typing import Annotated

from sqlalchemy import text
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

str_255 = Annotated[str, 255]
