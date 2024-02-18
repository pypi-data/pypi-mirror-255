import json
from hashlib import md5
from typing import Any


class ToolUtils:
    """Class containing utility methods."""

    @staticmethod
    def hash_str(string_to_hash: str, hash_method: str = "md5") -> str:
        """Computes the hash for a given input string.

        Useful to hash strings needed for caching and other purposes.
        Hash method defaults to "md5"

        Args:
            string_to_hash (str): String to be hashed
            hash_method (str): Hash hash_method to use, supported ones
                - "md5"

        Returns:
            str: Hashed string
        """
        if hash_method == "md5":
            return str(md5(string_to_hash.encode()).hexdigest())
        else:
            raise ValueError(f"Unsupported hash_method: {hash_method}")

    @staticmethod
    def load_json(file_to_load: str) -> dict[str, Any]:
        """Loads and returns a JSON from a file.

        Args:
            file_to_load (str): Path to the file containing JSON

        Returns:
            dict[str, Any]: The JSON loaded from file
        """
        with open(file_to_load, encoding="utf-8") as f:
            loaded_json: dict[str, Any] = json.load(f)
            return loaded_json

    @staticmethod
    def json_to_str(json_to_dump: dict[str, Any]) -> str:
        """Helps convert the JSON to a string. Useful for dumping the JSON to a
        file.

        Args:
            json_to_dump (dict[str, Any]): Input JSON to dump

        Returns:
            str: String representation of the JSON
        """
        compact_json = json.dumps(json_to_dump, separators=(",", ":"))
        return compact_json

    @staticmethod
    def generate_file_id(
        project_guid, file_name, vector_db, embedding, chunk_size, chunk_overlap
    ) -> str:
        """Generates a unique ID useful for identifying files during indexing.

        Args:
            project_guid (_type_): _description_
            file_name (_type_): _description_
            vector_db (_type_): _description_
            embedding (_type_): _description_
            chunk_size (_type_): _description_
            chunk_overlap (_type_): _description_

        Returns:
            _type_: _description_
        """
        return (
            f"{project_guid}|{vector_db}|"
            f"{embedding}|{chunk_size}|{chunk_overlap}"
            + "|"
            + ToolUtils.hash_str(file_name)
        )
