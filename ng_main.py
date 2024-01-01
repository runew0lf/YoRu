import random
from pathlib import Path


import requests

from nicegui import run, ui

from modules.settings import resolutions, styles
from modules.prompt_processing import process_prompt
from modules.utils import convert_bytes_to_PIL, load_workflow
from modules.websockets import WebSocketClient
import modules.args
import modules.civitai
from PIL import Image


# https://docs.streamlit.io/
# https://github.com/adriangalilea/streamlit-shortcuts
# https://github.com/sqlinsights/streamlit-vertical-slider (could be interesting for the sliders)
# https://github.com/sqlinsights/streamlit-toggle-switch (interesting for the checkboxes)
# https://arnaudmiribel.github.io/streamlit-extras/ extra widgets
# https://github.com/andfanilo/streamlit-drawable-canvas (The worlds best drawable canvas)
# https://github.com/DenizD/Streamlit-Image-Carousel (Better Gallery component)
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
#civitai = modules.civitai.Civitai()
#civitai.update_folder(Path("models/checkpoints"))
#civitai.update_folder(Path("models/loras"), isLora=True)

#st.set_page_config(layout="wide", page_title="YoRu", page_icon=ico)

# The next bit can be used to hide all the headers and footers, but it also hides the streamlit menu
#st.markdown(
#    """
#    <style>
#        #MainMenu, header, footer {visibility: hidden;}
#        .block-container {
#            padding-top: 1rem;
#            padding-bottom: 0rem;
#            padding-left: 5rem;
#            padding-right: 5rem;
#        }
#    </style>
#    """,
#    unsafe_allow_html=True,
#)

#left_column, main_column = st.columns([2, 6])

tab_names = ["Prompt", "Settings", "Model", "LoRAs"]
tab = {}
with ui.row():
    with ui.column():
        with ui.tabs().classes('w-full') as tabs:
            for name in tab_names:
                tab[name] = ui.tab(name)

        with ui.tab_panels(tabs, value=tab["Prompt"]).classes('w-full'):
            with ui.tab_panel(tab["Prompt"]):
                styles = ui.select(
                    styles,
                    label="Styles",
                    value="Style: sai-cinematic",
                    multiple=True,
                )
                prompt_text_area = ui.textarea(
                    label='Prompt',
                    placeholder='start typing',
                )
#            on_change=lambda e: result.set_text(e.value)
#    generate_button = st.button(label="Generate", use_container_width=True)
#    stop_button = st.button(label="Stop", use_container_width=True)


#    with ui.tab_panel(tab["Prompt"]):
#    with ui.tab_panel(two):
#        ui.label('Second tab')


            with ui.tab_panel(tab["Settings"]):
                with ui.row():
                    ui.label("Steps")
                    steps = ui.knob(
                        min=1,
                        max=100,
                        step=1,
                        value=20,
                        show_value=True,
                    )
                    ui.label("CFG")
                    cfg = ui.knob(
                        min=1,
                        max=20,
                        step=1,
                        value=7,
                        show_value=True,
                    )

                with ui.row():
                    samplers = client.object_info("KSampler", "sampler_name")[0]
                    sampler = ui.select(
                        samplers,
                        label="Sampler",
                        value=TEMP_SAMPLER,
                    )

                schedulers = client.object_info("KSampler", "scheduler")[0]
                scheduler = ui.select(
                    schedulers,
                    label="Scheduler",
                    value=TEMP_SCHEDULER,
                )
                no_of_images_label = ui.label("Images")
                no_of_images = ui.slider(
                    min=1,
                    max=50,
                    value=1,
                    step=1,
                    on_change=lambda e: no_of_images_label.set_text('Images: ' + str(e.value)),
                )

                ui.label("Resolution")
                resolution_picker = ui.select(
                    resolutions,
                )

#with tabs[tab_names.index("Model")]:
#    models = client.object_info("CheckpointLoaderSimple", "ckpt_name")[0]
#    #model = st.selectbox(
#    #    "Model",
#    #    models,
#    #    index=models.index(TEMP_MODEL),
#    #    label_visibility="hidden",
#    #)
#
#    arr_images = []
#    arr_captions = []
#    cachepath = Path(".cache/civitai")
#    for model in models:
#        arr_images.append(
#            str(
#                Path.joinpath(
#                    cachepath, model.replace(".safetensors", ".jpeg")
#                ).absolute()
#            )
#        )
#        arr_captions.append(model.replace(".safetensors", ""))
#
#    st.markdown(
#        """
#        <style>
#            .element-container {
#                max-height: 600px;
#                overflow-x: hidden;
#                overflow-y: scroll;
#            }
#        </style>
#        """,
#        unsafe_allow_html=True,
#    )
#    model = image_select(
#        label="Model",
#        images=arr_images,
#        captions=arr_captions,
#    )
#
#with tabs[tab_names.index("LoRAs")]:
#    # lora_col, strength_col = left_column.columns([1, 1])
#    lora_models = client.object_info("LoraLoader", "lora_name")[0]
#    lora_model = st.selectbox(
#        "Lora",
#        ["None"] + lora_models,
#        index=0,
#    )
#    lora_strength = st.slider("Strength", 0.0, 2.0, 1.0, 0.1)

    with ui.column():
        ui.label("wtf?")
        thisfile = ui.image("YoRu.png")
#    _, indent, _ = st.columns([1, 3, 1])
#    if "image" not in st.session_state:
#        st.session_state.image = "YoRu.png"
#    thisfile = indent.image(st.session_state.image, use_column_width=True)
#    my_bar = indent.progress(0)
#    prompt_column, button_column = st.columns([6, 1])

### LOGIC ###

#if generate_button:
#    with WebSocketClient() as client:
#        workflow = load_workflow("standard_sdxl.json")
#        if lora_model != "None":
#            workflow = load_workflow("sdxl_lora.json")
#            workflow["10"]["inputs"]["lora_name"] = lora_model
#            workflow["10"]["inputs"]["strength_model"] = lora_strength
#
#        ksampler = workflow["3"]["inputs"]
#
#        pos_prompt, neg_prompt = process_prompt(styles, prompt_text_area)
#
#        workflow["6"]["inputs"]["text"] = pos_prompt
#        workflow["7"]["inputs"]["text"] = neg_prompt
#
#        print(workflow["6"]["inputs"]["text"])
#        print(workflow["7"]["inputs"]["text"])
#
#        ksampler["seed"] = random.randint(0, 1000000)  # random
#        ksampler["steps"] = steps
#        ksampler["cfg"] = cfg
#        ksampler["sampler_name"] = sampler
#        ksampler["scheduler"] = scheduler
#        workflow["5"]["inputs"]["width"] = resolutions[resolution_picker]["width"]
#        workflow["5"]["inputs"]["height"] = resolutions[resolution_picker]["height"]
#        workflow["5"]["inputs"]["batch_size"] = no_of_images
#        workflow["4"]["inputs"]["ckpt_name"] = Path(model.replace(".jpeg", ".safetensors")).name
#
#        with st.spinner():
#            my_bar.progress(0, f"Loading Model...")
#            for item in client.get_images(workflow):
#                if client.status != "done":
#                    progress = int((100 / ksampler["steps"]) * item)
#                    my_bar.progress(
#                        progress, f"Generating... {item} / {ksampler['steps']}"
#                    )
#                    print(client.status.upper())
#                    if client.status == "executing":  ##Doesnt quite work yet
#                        my_bar.progress(
#                            progress, f"Current Node: {client.current_node}"
#                        )
#
#                    if client.preview is not None:
#                        st.session_state.image = convert_bytes_to_PIL(client.preview)
#                        thisfile.image(
#                            st.session_state.image, use_column_width="always"
#                        )
#
#            for node_id, images in item.items():
#                for image_data in images:
#                    st.session_state.image = image_data
#                    thisfile.image(st.session_state.image, use_column_width="always")
#    my_bar.progress(0)
#
#if stop_button:
#    requests.post(f"http://127.0.0.1:8188/interrupt", data="x")
#
#
#add_keyboard_shortcuts(
#    {
#        "Ctrl+Enter": "Generate",
#    }
#)

ui.run(
    favicon="icon.png",
    dark=True,
    show=False,
)
