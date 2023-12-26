from pathlib import Path
import json


class PathManager:
    DEFAULT_PATHS = {
        "path_checkpoints": "../models/checkpoints/",
        "path_loras": "../models/loras/",
    }

    EXTENSIONS = [".pth", ".ckpt", ".bin", ".safetensors"]

    def __init__(self):
        self.paths = self.load_paths()
        self.model_paths = self.get_model_paths()
        self.update_all_model_names()

    def load_paths(self):
        paths = self.DEFAULT_PATHS.copy()
        settings_path = Path("settings/paths.json")
        if settings_path.exists():
            with settings_path.open() as f:
                paths.update(json.load(f))
        for key in self.DEFAULT_PATHS:
            if key not in paths:
                paths[key] = self.DEFAULT_PATHS[key]
        with settings_path.open("w") as f:
            json.dump(paths, f, indent=2)
        return paths

    def get_model_paths(self):
        return {
            "modelfile_path": self.get_abspath_folder(self.paths["path_checkpoints"]),
            "lorafile_path": self.get_abspath_folder(self.paths["path_loras"]),
        }

    def get_abspath_folder(self, path):
        folder = self.get_abspath(path)
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def get_abspath(self, path):
        return Path(path) if Path(path).is_absolute() else Path(__file__).parent / path

    def update_all_model_names(self):
        self.model_filenames = self.get_model_filenames(
            self.model_paths["modelfile_path"]
        )
        self.lora_filenames = self.get_model_filenames(
            self.model_paths["lorafile_path"], True
        )

    def get_model_filenames(self, folder_path, isLora=False):
        folder_path = Path(folder_path)
        if not folder_path.is_dir():
            raise ValueError("Folder path is not a valid directory.")
        filenames = []
        for path in folder_path.rglob("*"):
            if path.suffix.lower() in self.EXTENSIONS:
                filenames.append(str(path.relative_to(folder_path)))
        # Return a sorted list, prepend names with 0 if they are in a folder or 1
        # if it is a plain file. This will sort folders above files in the dropdown
        return sorted(
            filenames,
            key=lambda x: f"0{x.casefold()}"
            if not str(Path(x).parent) == "."
            else f"1{x.casefold()}",
        )
