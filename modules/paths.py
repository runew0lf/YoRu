from pathlib import Path
import toml

# Load paths from TOML file


class PathManager:
    def __init__(self):
        self.config = toml.load("settings/paths.toml")

    def get_abspath_folder(self, path):
        folder = self.get_abspath(path)
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def get_abspath(self, path):
        return Path(path) if Path(path).is_absolute() else Path(__file__).parent / path

    def get_models_path(self):
        models_path = self.config["Paths"]["models"]
        return self.get_abspath_folder(models_path)

    def get_loras_path(self):
        loras_path = self.config["Paths"]["loras"]
        return self.get_abspath_folder(loras_path)
