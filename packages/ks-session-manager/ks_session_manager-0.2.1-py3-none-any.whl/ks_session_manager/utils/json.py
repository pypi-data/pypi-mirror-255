import json
from pathlib import Path


def read_json_file(file: str | Path) -> dict:
    """
    Reads and parses a JSON file.

    Parameters:
        file (str or Path): The path to the JSON file.

    Returns:
        dict: The parsed JSON data as dictionary.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the specified file is not a valid JSON file.

    """
    file = Path(file)

    if not file.is_file():
        raise FileNotFoundError(f'{file} does not exist')

    try:
        return json.loads(file.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        raise ValueError(f'{file} is not a valid JSON file')
