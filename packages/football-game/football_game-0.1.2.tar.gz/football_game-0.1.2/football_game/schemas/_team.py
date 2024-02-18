from typing import TYPE_CHECKING
import uuid
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from ._player import Player
    from ._trainer import Trainer


class Team(SQLModel, table=True):
    team_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Unique identifier for the team"},
    )
    name: str
    presupuesto: float

    players: list["Player"] = Relationship(back_populates="team")
    trainer: "Trainer" = Relationship(back_populates="team")
