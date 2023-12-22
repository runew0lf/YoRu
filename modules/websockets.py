import websocket
import uuid
import json
import urllib.request
import urllib.parse


### https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/websockets_api_example.py


class WebSocketClient:
    # Initialize the WebSocketClient with a server address and a unique client id
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.ws = websocket.WebSocket()

    # Connect to the websocket server
    def connect(self):
        self.ws.connect(
            "ws://{}/ws?clientId={}".format(self.server_address, self.client_id)
        )

    # Disconnect from the websocket server
    def disconnect(self):
        self.ws.close()

    # Queue a prompt to the server and return the server's response
    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(
            "http://{}/prompt".format(self.server_address), data=data
        )
        return json.loads(urllib.request.urlopen(req).read())

    # Get an image from the server by providing filename, subfolder, and folder type
    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            "http://{}/view?{}".format(self.server_address, url_values)
        ) as response:
            return response.read()

    # Get the history of a prompt from the server by providing the prompt id
    def get_history(self, prompt_id):
        with urllib.request.urlopen(
            "http://{}/history/{}".format(self.server_address, prompt_id)
        ) as response:
            return json.loads(response.read())

    # get images related to a specific prompt from the server
    def get_images(self, prompt):
        # Queue the prompt and get the prompt_id from the response
        prompt_id = self.queue_prompt(prompt)["prompt_id"]
        output_images = {}
        # Keep receiving messages from the server until execution is done
        while True:
            out = self.ws.recv()
            # If the received message is a string, it's a JSON object
            if isinstance(out, str):
                message = json.loads(out)
                print(f"message: {message}")
                # If the type of the message is "executing", it means the server is still processing the prompt
                if message["type"] == "executing":
                    data = message["data"]
                    # If the node is None and the prompt_id matches, it means the execution is done
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break  # Execution is done
            else:
                # If the received message is not a string, it's binary data (an image)
                self.preview = out
                continue
                # yield out  # previews are binary data

        # Get the history of the prompt
        history = self.get_history(prompt_id)[prompt_id]
        # Iterate over the outputs in the history
        for o in history["outputs"]:
            # For each output, get the node_id and the corresponding output
            for node_id in history["outputs"]:
                node_output = history["outputs"][node_id]
                # If the output contains images, get the images
                if "images" in node_output:
                    images_output = []
                    for image in node_output["images"]:
                        # For each image, get the image data from the server
                        image_data = self.get_image(
                            image["filename"], image["subfolder"], image["type"]
                        )
                        # Add the image data to the images_output list
                        images_output.append(image_data)
                # Add the images_output list to the output_images dictionary with the node_id as the key
                output_images[node_id] = images_output

        # Return the output_images dictionary
        return output_images
