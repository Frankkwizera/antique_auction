__author__ = "Frank Kwizera"

import os

class Directories:
    @staticmethod
    def local_path() -> str:
        """
        Returns project root directory path
        """
        local_path: str = os.path.join("/", "var", "antique_auction")
        if not os.path.exists(local_path):
            os.mkdir(local_path)
        return local_path

    @staticmethod
    def database_root() -> str:
        """
        Returns database root directory path.
        """
        database_root: str = os.path.join(Directories.local_path(), "databases")
        if not os.path.exists(database_root):
            os.mkdir(database_root)
        return database_root

class GeneralConstants:
    PASSWORD_HASHING_METHOD: str = 'sha256'
    UUID_MAX_LENGTH: int = 64
    NAME_MAX_LENGTH: int = 64
    EMAIL_MAX_LENGTH: int = 64
    PASSWORD_HASH_MAX_LENGTH: int = 128
    DESCRIPTION_MAX_LENGTH: int = 128
