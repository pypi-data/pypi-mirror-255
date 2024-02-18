import csv
from decouple import config
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel import Session

from schemas import *


def main():
    postgres_uri: str = config("POSTGRES_URI")
    engine = create_engine(postgres_uri)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        
        csv_name = "football_game/schemas/test_player.csv"

        PlayerCSVToDB().create_csv(
            csv_name, 
            "name",
            "age",
            "weight",
            "height",
            "salary",
            "position",
            "pac",
            "sho",
            "pas",
            "dri",
            "defe",
            "phy",
            "goalkeeping",
        )

        with open(csv_name, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row["name"] = str(row["name"])
                row["age"] = int(row["age"])
                row["weight"] = int(row["weight"])
                row["height"] = float(row["height"])
                row["salary"] = float(row["salary"])
                row["position"] = str(row["position"])
                row["pac"] = float(row["pac"])
                row["sho"] = float(row["sho"])
                row["pas"] = float(row["pas"])
                row["dri"] = float(row["dri"])
                row["defe"] = float(row["defe"])
                row["phy"] = float(row["phy"])
                row["goalkeeping"] = float(row["goalkeeping"])

                player = Player(**row)
                session.add(player)

        session.commit()
        print("Data inserted successfully!")


if __name__ == "__main__":
    main()