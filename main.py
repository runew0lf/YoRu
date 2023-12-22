import streamlit as st
from modules.websockets import WebSocketClient
import json
from PIL import Image
import io
import random

client = WebSocketClient()

##test to see if notifications works
thisfile = st.image(
    "YoRu.png",
    width=600,
)

col1, col2 = st.columns([3, 1])

progress_text = "Operation in progress. Please wait."
my_bar = st.progress(0, text=progress_text)

with col1:
    prompttext = st.text_area(
        "prompt", value="masterpiece, best quality, man", label_visibility="visible"
    )
with col2:
    if st.button(label="Generate"):
        client.connect()
        with open("workflows\standard_sdxl.json", "r") as file:
            prompt = json.load(file)

        prompt["6"]["inputs"]["text"] = prompttext
        prompt["3"]["inputs"]["seed"] = random.randint(0, 1000000)  # random
        prompt["5"]["inputs"]["width"] = 1024
        prompt["5"]["inputs"]["height"] = 1024

        ## We need to grab value while this is processing as excecution pauses
        images_dict = client.get_images(prompt)

        for node_id, images in images_dict.items():
            for image_data in images:
                thisfile.image(image_data, width=600)
        # for image_data in client.get_images(prompt):
        #     image = Image.open(io.BytesIO(image_data))
        #     thisfile.image(image, width=600)
        client.disconnect()
