from decouple import config
from sqlalchemy.engine import Engine
from sqlmodel import create_engine, SQLModel, Session

from schemas import *


def main():
    postgres_uri: str = config("POSTGRES_URI")
    engine: Engine = create_engine(postgres_uri)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        team = Team(name="Real Madrid", presupuesto=99999999999)
        kepa = Player(
            name="Kepa Arrizabalaga",
            age=28,
            weight=88,
            height=1.88,
            salary=9000000,
            posicion="Goalkeeper",
            team=team,
            pac=33.5,
            sho=24.33,
            pas=41.67,
            dri=43.83,
            defe=18.4,
            phy=41,
            goalkeeping=85,
        )

        session.add_all([team, kepa])
        session.commit()


if __name__ == "__main__":
    main()
