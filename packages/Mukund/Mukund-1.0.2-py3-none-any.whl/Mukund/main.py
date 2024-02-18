import zipfile
from pathlib import Path
from Mukund.core.database import *

class Mukund:
    def __init__(self, Name: str = "Storage") -> None:
        """
        Initialize the Mukund class with a specified database name.

        Parameters:
        - Name: Name of the Storage.
        """
        self.db_name = Name
        self.db_path = Path(Name)
        self.db_path.mkdir(exist_ok=True)
        print(
            """
                        █▀▄▀█ █░█ █▄▀ █░█ █▄░█ █▀▄
                        █░▀░█ █▄█ █░█ █▄█ █░▀█ █▄▀

                Visit @ItzMukund for updates!! (Telegram)
"""
        )

    def database(self, collection_name: str) -> Base:
        """
        Create or access a database collection.

        Parameters:
        - collection_name: Name of the collection within the database.

        Returns:
        - Base: An instance of the Base class representing the specified collection.
        """
        collection_path = self.db_path / f"{collection_name}.json"
        return Base(collection_path)
    
    def backup(self, path) -> None:
        """
        Create a backup of the entire Mukund database by zipping all collection files.

        Parameters:
        - path: Path to the backup zip file e.g Mukund.zip .

        Returns:
        - A zip file 
        """
        with zipfile.ZipFile(Path(path), 'w') as zip_file:
            zip_file.write(self.db_path, arcname=self.db_path.name)
            for collection_file in self.db_path.glob("*.json"):
                arcname = f"{self.db_path.name}/{collection_file.name}"
                zip_file.write(collection_file, arcname=arcname)