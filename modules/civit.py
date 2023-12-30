import requests
import hashlib
from typing import Dict, Any
import time
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path
import concurrent.futures


class Civit:
    EXTENSIONS = {".pth", ".ckpt", ".bin", ".safetensors"}

    def __init__(self, base_url="https://civitai.com/api/v1/"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.Session()
        self.worker_folders = set()
        self.executor = ThreadPoolExecutor(max_workers=5)

    def update_folder(self, folder_path, isLora=False):
        self.executor.submit(self.update_worker, folder_path, isLora)

    def update_worker(self, folder_path, isLora=False):
        if folder_path in self.worker_folders:
            # Already working on this folder
            return
        self.worker_folders.add(folder_path)
        for path in Path(folder_path).rglob("*"):
            if path.suffix.lower() in self.EXTENSIONS:
                hash = self.model_hash(str(path))
                models = self.get_models_by_hash(hash)

                imgcheck = path.with_suffix(".jpeg")
                if not imgcheck.exists():
                    print(f"Downloading model preview for {path}")
                    try:
                        image_url = models.get("images", [{}])[0].get("url")
                        if image_url:
                            response = self.session.get(image_url)
                            response.raise_for_status()
                            with open(imgcheck, "wb") as file:
                                file.write(response.content)
                    except Exception as e:
                        logging.error(f"ERROR: failed downloading {imgcheck}\n    {e}")
                    time.sleep(1)

                txtcheck = path.with_suffix(".txt")
                if isLora and not txtcheck.exists():
                    print(f"Downloading LoRA keywords for {path}")
                    keywords = self.get_keywords(models)
                    with open(txtcheck, "w") as f:
                        f.write(", ".join(keywords))
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
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logging.error("Error: Model Not Found on civit.ai")
                return {}
            elif response.status_code == 503:
                logging.error("Error: Civit.ai Service Currently Unavailable")
                return {}
            else:
                logging.error(f"HTTP Error: {e}")
                return {}
        except requests.exceptions.RequestException as e:
            logging.error(f"Error: {e}")
            return {}

    def get_keywords(self, model):
        keywords = model.get("trainedWords", ["No Keywords for LoRA"])
        return keywords
