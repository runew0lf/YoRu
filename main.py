import random
from pathlib import Path


import requests
import streamlit as st
from streamlit_shortcuts import add_keyboard_shortcuts

from modules.settings import resolutions, styles
from modules.prompt_processing import process_prompt
from modules.utils import convert_bytes_to_PIL, load_workflow
from modules.websockets import WebSocketClient
import modules.args
import modules.civit
from PIL import Image


# https://docs.streamlit.io/
# https://github.com/adriangalilea/streamlit-shortcuts
# https://github.com/sqlinsights/streamlit-vertical-slider (could be interesting for the sliders)
# https://github.com/sqlinsights/streamlit-toggle-switch (interesting for the checkboxes)
# https://arnaudmiribel.github.io/streamlit-extras/ extra widgets
# pip install streamlit-tags (could be good for wildcards) https://share.streamlit.io/gagan3012/streamlit-tags/examples/app.py


TEMP_PROMPT = "black and white pencil sketch, extreme side closeup of a wizards face with black tattoos, black background"
TEMP_MODEL = "crystalClearXL_ccxl.safetensors"
TEMP_SAMPLER = "dpmpp_3m_sde_gpu"
TEMP_SCHEDULER = "karras"
TEMP_LORA = "None"

args = modules.args.parse_args()

client = WebSocketClient()
if not args.comfy is None:
    client.server_address = args.comfy
client.connect()
civit = modules.civit.Civit()
civit.update_folder(Path("models/checkpoints"))
civit.update_folder(Path("models/loras", isLora=True))
ico = Image.open("icon.png")
st.set_page_config(layout="wide", page_title="YoRu", page_icon=ico)

# The next bit can be used to hide all the headers and footers, but it also hides the streamlit menu
st.markdown(
    """
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
topbar = st.columns([1, 1, 1, 1, 1])
left_column, main_column = st.columns([2, 6])

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
            steps = left_column.slider("Steps", 1, 100, 20)
            cfg = left_column.slider("Cfg", 1, 20, 7)
            samplers = client.object_info("KSampler", "sampler_name")[0]
            sampler = topbar[1].selectbox(
                "sampler",
                samplers,
                index=samplers.index(TEMP_SAMPLER),
                label_visibility="hidden",
            )
            schedulers = client.object_info("KSampler", "scheduler")[0]
            scheduler = topbar[2].selectbox(
                "scheduler",
                schedulers,
                index=schedulers.index(TEMP_SCHEDULER),
                label_visibility="hidden",
            )
            no_of_images = left_column.slider("Images", 1, 20, 1)
            resolution_picker = left_column.selectbox("Resolution", resolutions)
            styles = left_column.multiselect(
                "Styles", styles, default="Style: sai-cinematic"
            )
            models = client.object_info("CheckpointLoaderSimple", "ckpt_name")[0]
            model = topbar[0].selectbox(
                "Model",
                models,
                index=models.index(TEMP_MODEL),
                label_visibility="hidden",
            )
            lora_col, strength_col = left_column.columns([1, 1])
            lora_models = client.object_info("LoraLoader", "lora_name")[0]
            lora_model = lora_col.selectbox(
                "Lora",
                ["None"] + lora_models,
                index=0,
            )
            lora_strength = strength_col.slider("Strength", 0.0, 2.0, 1.0, 0.1)

    with button_column:
        st.write("#")
        generate_button = st.button(label="Generate", use_container_width=True)
        stop_button = st.button(label="Stop", use_container_width=True)

### LOGIC ###

if generate_button:
    with WebSocketClient() as client:
        workflow = load_workflow("standard_sdxl.json")
        if lora_model != "None":
            workflow = load_workflow("sdxl_lora.json")
            workflow["10"]["inputs"]["lora_name"] = lora_model
            workflow["10"]["inputs"]["strength_model"] = lora_strength

        ksampler = workflow["3"]["inputs"]

        pos_prompt, neg_prompt = process_prompt(styles, prompt_text_area)

        workflow["6"]["inputs"]["text"] = pos_prompt
        workflow["7"]["inputs"]["text"] = neg_prompt

        print(workflow["6"]["inputs"]["text"])
        print(workflow["7"]["inputs"]["text"])

        ksampler["seed"] = random.randint(0, 1000000)  # random
        ksampler["steps"] = steps
        ksampler["cfg"] = cfg
        ksampler["sampler_name"] = sampler
        ksampler["scheduler"] = scheduler
        workflow["5"]["inputs"]["width"] = resolutions[resolution_picker]["width"]
        workflow["5"]["inputs"]["height"] = resolutions[resolution_picker]["height"]
        workflow["5"]["inputs"]["batch_size"] = no_of_images
        workflow["4"]["inputs"]["ckpt_name"] = model

        my_bar.progress(0, f"Loading Model...")
        for item in client.get_images(workflow):
            if client.status != "done":
                progress = int((100 / ksampler["steps"]) * item)
                my_bar.progress(progress, f"Generating... {item} / {ksampler['steps']}")
                print(client.status.upper())
                if client.status == "executing":  ##Doesnt quite work yet
                    my_bar.progress(progress, f"Current Node: {client.current_node}")

                if client.preview is not None:
                    image = convert_bytes_to_PIL(client.preview)
                    thisfile.image(image, use_column_width="always")

        for node_id, images in item.items():
            for image_data in images:
                thisfile.image(image_data, use_column_width="always")
    my_bar.progress(0)

if stop_button:
    requests.post(f"http://127.0.0.1:8188/interrupt", data="x")


add_keyboard_shortcuts(
    {
        "Ctrl+Enter": "Generate",
    }
)
