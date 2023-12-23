import streamlit as st
from modules.websockets import WebSocketClient
import random
from modules.utils import load_workflow, convert_bytes_to_PIL

# https://docs.streamlit.io/


client = WebSocketClient()

st.set_page_config(layout="wide", page_title="YoRu", page_icon="🤖")

_, main_column, right_column = st.columns([2, 6, 2])


steps = right_column.slider("Steps", 1, 100, 20)
cfg = right_column.slider("Cfg", 1, 20, 7)

with main_column:
    _, indent, _ = st.columns([1, 3, 1])
    thisfile = indent.image("YoRu.png", use_column_width=True)
    my_bar = indent.progress(0)
    prompt_column, button_column = st.columns([6, 1])

    with prompt_column:
        prompttext = st.text_area(
            "prompt", value="masterpiece, best quality, man", label_visibility="hidden"
        )
    with button_column:
        st.write("#")
        if st.button(label="Generate", use_container_width=True):
            with WebSocketClient() as client:
                workflow = load_workflow("standard_sdxl.json")

                ksampler = workflow["3"]["inputs"]

                workflow["6"]["inputs"]["text"] = prompttext
                ksampler["seed"] = random.randint(0, 1000000)  # random
                ksampler["steps"] = steps
                ksampler["cfg"] = cfg
                workflow["5"]["inputs"]["width"] = 1024
                workflow["5"]["inputs"]["height"] = 1024

                my_bar.progress(0, f"Loading Model...")
                for item in client.get_images(workflow):
                    if client.status != "done":
                        progress = int((100 / ksampler["steps"]) * item)
                        my_bar.progress(
                            progress, f"Generating... {item} / {ksampler['steps']}"
                        )
                        print(client.status.upper())
                        if client.status == "executing":  ##Doesnt quite work yet
                            my_bar.progress(
                                progress, f"Current Node: {client.current_node}"
                            )

                        if client.preview is not None:
                            image = convert_bytes_to_PIL(client.preview)
                            thisfile.image(image, use_column_width="always")

                for node_id, images in item.items():
                    for image_data in images:
                        thisfile.image(image_data, use_column_width="always")
            my_bar.progress(0)
        st.button(label="Stop", use_container_width=True)
