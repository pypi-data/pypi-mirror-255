import pandas as pd
from sqlmodel import SQLModel, Session
from sqlalchemy import create_engine
from pathlib import Path

class PlayerCSVToDB(SQLModel, table=True):
    @staticmethod
    def create_csv(
        csv_name: str,
        header_1: str,
        header_2: str,
        header_3: str,
        header_4: str,
        header_5: str,
        header_6: str,
        header_7: str,
        header_8: str,
        header_9: str,
        header_10: str,
        header_11: str,
        header_12: str,
        header_13: str,
    ) -> None:
        """
        Create a .csv with the player's categories

        Args:
            csv_name: str: csv's name
            header: str: header's columns
        """
        headers = [
            header_1,
            header_2,
            header_3,
            header_4,
            header_5,
            header_6,
            header_7,
            header_8,
            header_9,
            header_10,
            header_11,
            header_12,
            header_13,
        ]

        df = pd.DataFrame(columns=headers)

        df.to_csv(csv_name, index=False)


    def create_player(df, player_data: dict, csv_file_path: str):
        """
        Create a player in a csv.

        Args:
            df (pd.DataFrame): DataFrame where we want to save the player.
            player_data (dict): DICT with the player's data.
            csv_file_path (str): csv path.
        """
        new_row = pd.DataFrame(player_data, index=[0])

        df = pd.concat([df, new_row], ignore_index=True)

        df.to_csv(csv_file_path, index=False)


    # New player data
    new_player_data = {
        "name": "Carlos",
        "age": 25,
        "weight": 70,
        "height": 1.75,
        "salary": 100000,
        "position": "Forward",
        "pac": 85,
        "sho": 90,
        "pas": 80,
        "dri": 85,
        "defe": 40,
        "phy": 75,
        "goalkeeping": 0,
    }

    # csv PATH
    csv_file_path = "football_game/schemas/test_player.csv"

    create_csv(
        csv_file_path,
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

    df = pd.read_csv(csv_file_path)
    create_player(df, player_data=new_player_data, csv_file_path=csv_file_path)
