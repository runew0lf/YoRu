import requests
import hashlib
from typing import Dict, Any
import threading
import time
import urllib


class Civit:
    EXTENSIONS = [".pth", ".ckpt", ".bin", ".safetensors"]

    def __init__(self, base_url="https://civitai.com/api/v1/"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}

    def update_folder(self, folder_path, isLora=False):
        threading.Thread(
            target=self.update_worker,
            args=(
                folder_path,
                isLora,
            ),
            daemon=True,
        ).start()

    worker_folders = []
    def update_worker(self, folder_path, isLora=False):
        if folder_path in self.worker_folders:
            # Already working on this folder
            return
        self.worker_folders.append(folder_path)
        for path in folder_path.rglob("*"):
            if path.suffix.lower() in self.EXTENSIONS:
                hash = self.model_hash(str(path))
                models = self.get_models_by_hash(hash)

                imgcheck = path.with_suffix(".jpeg")
                if not imgcheck.exists():
                    print(f"Downloading model preview for {path}")
                    preview = self.get_preview(models)
                    # FIXME download and save somewhere
                    try:
                        if not preview is None:
                            urllib.request.urlretrieve(preview, imgcheck)
                    except Exception as e:
                        print(f"ERROR: failed downloading {preview}\n    {e}")
                    time.sleep(1)

                txtcheck = path.with_suffix(".txt")
                if isLora and not txtcheck.exists():
                    print(f"Downloading LoRA keywords for {path}")
                    keywords = self.get_keywords(models)
                    # FIXME save text somewhere
#                    with open(txtcheck, "w") as f:
#                        f.write(", ".join(keywords))
                    time.sleep(1)

        self.worker_folders.remove(folder_path)

    def _read_file(self, filename):
        try:
            with open(filename, "rb") as file:
                file.seek(0x100000)
                return file.read(0x10000)
        except FileNotFoundError:
            return b"NOFILE"
        except Exception:
            return b"NOHASH"

    def model_hash(self, filename):
        """old hash that only looks at a small part of the file and is prone to collisions"""
        file_content = self._read_file(filename)
        m = hashlib.sha256()
        m.update(file_content)
        shorthash = m.hexdigest()[0:8]
        return shorthash

    def get_models_by_hash(self, hash):
        url = f"{self.base_url}model-versions/by-hash/{hash}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print("Error: Model Not Found on civit.ai")
                return {}
            elif response.status_code == 503:
                print("Error: Civit.ai Service Currently Unavailable")
                return {}
            else:
                print(f"HTTP Error: {e}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {}

    def get_keywords(self, model):
        keywords = model.get("trainedWords", ["No Keywords for LoRA"])
        return keywords

    def get_preview(self, model):
        preview = model.get("images", [{"url": None}])[0]["url"]
        return preview
