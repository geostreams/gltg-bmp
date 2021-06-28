import datetime
import logging
import os
from typing import List

from dotenv import load_dotenv
from pyclowder.extractors import SimpleExtractor

from api.utils.db import Database

load_dotenv()

logger = logging.getLogger(__name__)


class PracticesExtractor(SimpleExtractor):
    extensions = ["xlsx"]

    def __init__(self):
        super(PracticesExtractor, self).__init__()

        self.database = {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "db_name": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
        }

    def process_dataset(self, input_files: List[str]):
        practice_files = []
        for input_file in input_files:
            parts = input_file.split(".")
            if len(parts) > 1 and parts[-1] in self.extensions:
                practice_files.append(input_file)

        if not practice_files:
            return {}

        db = Database(**self.database)
        db.import_practices(practice_files)
        return {
            "metadata": {
                "last_update": str(datetime.datetime.now()),
                "files": practice_files,
            }
        }


if __name__ == "__main__":
    extractor = PracticesExtractor()
    extractor.start()
