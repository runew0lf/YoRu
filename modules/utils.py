import json
from PIL import Image
from io import BytesIO
from pathlib import Path
from typing import Dict


def load_workflow(name: str) -> Dict:
    """
    Load a workflow from a JSON file.

    Parameters:
    name (str): The name of the workflow file.

    Returns:
    dict: The loaded workflow.
    """
    with open(Path("workflows") / name, "r") as file:
        prompt = json.load(file)
    return prompt


def convert_bytes_to_PIL(bytes: bytes) -> Image:
    """
    Convert bytes to a PIL Image object.

    Parameters:
    bytes (bytes): The bytes to convert.

    Returns:
    PIL.Image.Image: The converted image.
    """
    return Image.open(BytesIO(bytes[8:]))
