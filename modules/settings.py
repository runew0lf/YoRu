import tomllib as toml
import shutil
from csv import DictReader
from pathlib import Path
from modules.paths import PathManager

DEFAULT_STYLES_FILE = Path("settings/styles.default")
STYLES_FILE = Path("settings/styles.csv")


def load_styles():
    styles = []

    if not STYLES_FILE.is_file():
        shutil.copy(DEFAULT_STYLES_FILE, STYLES_FILE)

    with STYLES_FILE.open("r") as f:
        reader = DictReader(f)
        styles = list(reader)

    default_style = {"name": "None", "prompt": "{prompt}", "negative_prompt": ""}
    random_style = {
        "name": "Style: Pick Random",
        "prompt": "{prompt}",
        "negative_prompt": "",
    }
    styles.insert(0, random_style)
    styles.insert(0, default_style)

    return {s["name"]: (s["prompt"], s["negative_prompt"]) for s in styles}


def load_resolutions():
    with open("settings/resolutions.toml", "rb") as f:
        resolutions = toml.load(f)
    return resolutions


styles = load_styles()
default_style = styles["None"]
allstyles = [x for x in load_styles() if x.startswith("Style")]
allstyles.remove("Style: Pick Random")
resolutions = load_resolutions()
path_manager = PathManager()
