from sqlalchemy.orm import Mapped, mapped_column

from bot.repositories.models.annotations import str_255
from bot.repositories.models.base_model import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str_255 | None]
    full_name: Mapped[str_255 | None]
    is_admin: Mapped[bool] = mapped_column(default=False)
