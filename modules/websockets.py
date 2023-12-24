import json
import urllib.parse
import urllib.request
import uuid
import websocket
from typing import Any, Dict, Generator, Optional, Union


class WebSocketClient:
    """
    A WebSocket client that communicates with a server.
    """

    def __init__(self, server_address: str = "127.0.0.1:8188") -> None:
        """
        Initialize the WebSocketClient with a server address and a unique client id.
        """
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.ws = websocket.WebSocket()
        self.preview = None
        self.status = None
        self.current_node = None

    def __enter__(self) -> "WebSocketClient":
        """
        Code to execute when entering the `with` block.
        For example, connect to the server.
        """
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Code to execute when exiting the `with` block.
        For example, disconnect from the server.
        """
        self.disconnect()

    def connect(self) -> None:
        """
        Connect to the websocket server.
        """
        self.ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")

    def disconnect(self) -> None:
        """
        Disconnect from the websocket server.
        """
        self.ws.close()

    def queue_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Queue a prompt to the server and return the server's response.
        """
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read().decode())

    def get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """
        Get an image from the server by providing filename, subfolder, and folder type.
        """
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            f"http://{self.server_address}/view?{url_values}"
        ) as response:
            return response.read()

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get the history of a prompt from the server by providing the prompt id.
        """
        with urllib.request.urlopen(
            f"http://{self.server_address}/history/{prompt_id}"
        ) as response:
            return json.loads(response.read().decode())

    def object_info(self, object_name: str) -> Dict[str, Any]:
        """
        Get object_info of object
        """
        with urllib.request.urlopen(
            f"http://{self.server_address}/object_info/{object_name}"
        ) as response:
            return json.loads(response.read().decode())

    def get_images(
        self, prompt: str
    ) -> Generator[Union[int, Dict[str, Any]], None, None]:
        """
        Get images related to a specific prompt from the server.
        """
        prompt_id = self.queue_prompt(prompt)["prompt_id"]
        self.status = "executing"
        output_images = {}

        while True:
            out = self.ws.recv()
            if not isinstance(out, str):
                self.preview = out
                continue

            message = json.loads(out)
            print(f"message: {message}")

            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break  # Execution is done
                if data["node"] is not None:
                    self.current_node = data["node"]

            if message["type"] == "progress":
                self.status = "generating preview"
                self.current_step = message["data"]["value"]
                yield self.current_step  # Yield progress immediately

        history = self.get_history(prompt_id)[prompt_id]
        for output in history["outputs"]:
            for node_id in history["outputs"]:
                node_output = history["outputs"][node_id]
                if "images" in node_output:
                    images_output = [
                        self.get_image(
                            image["filename"], image["subfolder"], image["type"]
                        )
                        for image in node_output["images"]
                    ]
                output_images[node_id] = images_output

        self.status = "done"
        yield output_images  # Yield the final output_images
