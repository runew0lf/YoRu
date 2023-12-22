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

my_bar = st.progress(0)

col1, col2 = st.columns([3, 1])

with col1:
    prompttext = st.text_area(
        "prompt", value="masterpiece, best quality, man", label_visibility="visible"
    )
with col2:
    if st.button(label="Generate"):
        client.connect()
        with open("workflows\standard_sdxl.json", "r") as file:
            prompt = json.load(file)

        ksampler = prompt["3"]["inputs"]

        prompt["6"]["inputs"]["text"] = prompttext
        ksampler["seed"] = random.randint(0, 1000000)  # random
        ksampler["steps"] = 30
        prompt["5"]["inputs"]["width"] = 1024
        prompt["5"]["inputs"]["height"] = 1024

        my_bar.progress(0, f"Loading Model...")
        for item in client.get_images(prompt):
            if client.status != "done":
                progress = int((100 / ksampler["steps"]) * item)
                my_bar.progress(progress, f"Generating... {item} / {ksampler['steps']}")
                if client.status == "executing":  ##Doesnt quite work yet
                    my_bar.progress(progress, f"Current Node: {client.current_node}")

                if client.preview is not None:
                    image = Image.open(io.BytesIO(client.preview[8:]))
                    thisfile.image(image)

        for node_id, images in item.items():
            for image_data in images:
                thisfile.image(image_data, width=600)
        client.disconnect()
