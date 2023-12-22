import streamlit as st
from modules.websockets import WebSocketClient
import json
from PIL import Image
import io
import random

client = WebSocketClient()


thisfile = st.image(
    "YoRu.png",
    width=600,
)
prompttext = st.text_area(
    "prompt", value="masterpiece, best quality, man", label_visibility="visible"
)

if st.button(label="Generate"):
    client.connect()
    with open("workflows\standard_sdxl.json", "r") as file:
        prompt = json.load(file)

    prompt["6"]["inputs"]["text"] = prompttext
    prompt["3"]["inputs"]["seed"] = random.randint(0, 1000000)  # random
    prompt["5"]["inputs"]["width"] = 1024
    prompt["5"]["inputs"]["height"] = 1024
    images_dict = client.get_images(prompt)
    for node_id, images in images_dict.items():
        for image_data in images:
            thisfile.image(image_data, width=600)
    # for image_data in client.get_images(prompt):
    #     image = Image.open(io.BytesIO(image_data))
    #     thisfile.image(image, width=600)
    client.disconnect()
