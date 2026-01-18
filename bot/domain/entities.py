from dataclasses import dataclass


@dataclass
class UserMeta:
    tg_id: int
    username: str | None
    full_name: str | None

    @property
    def allow_name(self):
        return self.full_name if self.full_name is not None else self.username or "Anonymous"
