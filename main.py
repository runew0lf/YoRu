import random

import requests
import streamlit as st
from streamlit_shortcuts import add_keyboard_shortcuts

from modules.settings import apply_style, load_styles, path_manager, resolutions, styles
from modules.utils import convert_bytes_to_PIL, load_workflow
from modules.websockets import WebSocketClient


# https://docs.streamlit.io/
# https://github.com/adriangalilea/streamlit-shortcuts

TEMP_PROMPT = "black and white pencil sketch, extreme side closeup of a wizards face with black tattoos, black background"
TEMP_MODEL = "crystalClearXL_ccxl.safetensors"
TEMP_SAMPLER = "dpmpp_3m_sde_gpu"
TEMP_SCHEDULER = "karras"

client = WebSocketClient()
client.connect()
st.set_page_config(layout="wide", page_title="YoRu", page_icon="🤖")

# The next bit can be used to hide all the headers and footers, but it also hides the streamlit menu

# st.markdown(
#     """
# <style>
#     #MainMenu, header, footer {visibility: hidden;}
# </style>
# """,
#     unsafe_allow_html=True,
# )

left_column, main_column, right_column = st.columns([2, 6, 2])

# left_column.write(st.session_state)

with main_column:
    _, indent, _ = st.columns([1, 3, 1])
    thisfile = indent.image("YoRu.png", use_column_width=True)
    my_bar = indent.progress(0)
    prompt_column, button_column = st.columns([6, 1])

    with prompt_column:
        prompt_text_area = st.text_area(
            "prompt", value=TEMP_PROMPT, label_visibility="hidden"
        )
        if st.checkbox("Hurt Me Plenty", value=True):
            steps = right_column.slider("Steps", 1, 100, 20)
            cfg = right_column.slider("Cfg", 1, 20, 7)
            samplers = client.object_info("KSampler", "sampler_name")[0]
            sampler = right_column.selectbox(
                "sampler",
                samplers,
                index=samplers.index(TEMP_SAMPLER),
            )
            schedulers = client.object_info("KSampler", "scheduler")[0]
            scheduler = right_column.selectbox(
                "scheduler",
                schedulers,
                index=schedulers.index(TEMP_SCHEDULER),
            )
            no_of_images = right_column.slider("Images", 1, 20, 1)
            resolution_picker = right_column.selectbox("Resolution", resolutions)
            styles = right_column.multiselect(
                "Styles", load_styles(), default="Style: sai-cinematic"
            )
            model = right_column.selectbox(
                "Model",
                path_manager.model_filenames,
                index=path_manager.model_filenames.index(TEMP_MODEL),
            )

    with button_column:
        st.write("#")
        if st.button(label="Generate", use_container_width=True):
            with WebSocketClient() as client:
                workflow = load_workflow("standard_sdxl.json")

                ksampler = workflow["3"]["inputs"]

                workflow["6"]["inputs"]["text"], _ = apply_style(
                    styles, prompt_text_area, ""
                )
                print(workflow["6"]["inputs"]["text"])
                ksampler["seed"] = random.randint(0, 1000000)  # random
                ksampler["steps"] = steps
                ksampler["cfg"] = cfg
                ksampler["sampler_name"] = sampler
                ksampler["scheduler"] = scheduler
                workflow["5"]["inputs"]["width"] = resolutions[resolution_picker][
                    "width"
                ]
                workflow["5"]["inputs"]["height"] = resolutions[resolution_picker][
                    "height"
                ]
                workflow["5"]["inputs"]["batch_size"] = no_of_images
                workflow["4"]["inputs"]["ckpt_name"] = model

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
        if st.button(label="Stop", use_container_width=True):
            requests.post(f"http://127.0.0.1:8188/interrupt", data="x")

add_keyboard_shortcuts(
    {
        "Ctrl+Enter": "Generate",
    }
)
