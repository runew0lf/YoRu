import random
from pathlib import Path

import requests

from nicegui import run, ui
from nicegui.background_tasks import create

from fastapi import BackgroundTasks, FastAPI
import asyncio

from modules.settings import resolutions, styles
from modules.prompt_processing import process_prompt
from modules.utils import convert_bytes_to_PIL, load_workflow
from modules.paths import PathManager
from modules.websockets import WebSocketClient
import modules.args

import modules.civitai
from PIL import Image
import toml

# https://nicegui.io/documentation
# https://tailwind.build/classes

gen_data = {
    "cfg": 7,
    "lora": "None",
    "model": "crystalClearXL_ccxl.safetensors",
    "prompt": "black and white pencil sketch, extreme side closeup of a wizards face with black tattoos, black background",
    "styles": None,
    "sampler": "dpmpp_3m_sde_gpu",
    "scheduler": "karras",
    "steps": 20,
    "no_of_images": 1,
}

status = None
mainimage = None

args = modules.args.parse_args()

api = FastAPI()
client = WebSocketClient()
paths = PathManager()
if not args.comfy is None:
    client.server_address = args.comfy
client.connect()
models = client.object_info("CheckpointLoaderSimple", "ckpt_name")[0]


civitai = modules.civitai.Civitai()

civitai.update_cache(models, Path(paths.get_models_path()))
# civitai.update_cache(lora_models, Path(paths.get_loras_path()h), isLora=True)


# Functions and logic


def generate_clicked():
    ui.notify(f"DEBUG: Click!")
    create(call_comfy())


async def call_comfy():
    workflow = load_workflow("standard_sdxl.json")
    # FIXME use lora(s)
    #    if lora_model != "None":
    #        workflow = load_workflow("sdxl_lora.json")
    #        workflow["10"]["inputs"]["lora_name"] = lora_model
    #        workflow["10"]["inputs"]["strength_model"] = lora_strength

    ksampler = workflow["3"]["inputs"]

    pos_prompt, neg_prompt = process_prompt(gen_data["styles"], gen_data["prompt"])

    workflow["6"]["inputs"]["text"] = pos_prompt
    workflow["7"]["inputs"]["text"] = neg_prompt

    ksampler["seed"] = random.randint(0, 1000000)  # random
    ksampler["steps"] = gen_data["steps"]
    ksampler["cfg"] = gen_data["cfg"]
    ksampler["sampler_name"] = gen_data["sampler"]
    ksampler["scheduler"] = gen_data["scheduler"]

    # FIXME scale this according to the type of model?
    #    workflow["5"]["inputs"]["width"] = resolutions[resolution_picker]["width"]
    #    workflow["5"]["inputs"]["height"] = resolutions[resolution_picker]["height"]
    workflow["5"]["inputs"]["width"] = 1024
    workflow["5"]["inputs"]["height"] = 1024

    workflow["5"]["inputs"]["batch_size"] = gen_data["no_of_images"]
    workflow["4"]["inputs"]["ckpt_name"] = Path(
        gen_data["model"].replace(".jpeg", ".safetensors")
    ).name

    #    with st.spinner():
    if True:
        # FIXME
        #        my_bar.progress(0, f"Loading Model...")
        for item in client.get_images(workflow):
            await asyncio.sleep(0.1)
            if client.status != "done":
                progress = int((100 / ksampler["steps"]) * item)
                # FIXME
                #                my_bar.progress(
                #                    progress, f"Generating... {item} / {ksampler['steps']}"
                #                )
                print(client.status.upper())
                # FIXME
                if client.status == "executing":  ##Doesnt quite work yet
                    print(f"Thinking...")
                #                    my_bar.progress(
                #                        progress, f"Current Node: {client.current_node}"
                #                    )

                if client.preview is not None:
                    #                    st.session_state.image = convert_bytes_to_PIL(client.preview)
                    #                    mainimage.image(
                    #                        st.session_state.image, use_column_width="always"
                    #                    )
                    tmp_image = convert_bytes_to_PIL(client.preview)
                    mainimage.set_source(tmp_image)

        for node_id, images in item.items():
            for image_data in images:
                tmp_image = convert_bytes_to_PIL(client.preview)
                mainimage.set_source(tmp_image)
                # st.session_state.image = image_data
                # mainimage.image(st.session_state.image, use_column_width="always")


def stop_clicked():
    ui.notify(f"DEBUG: Stop!")
    requests.post(
        f"http://127.0.0.1:8188/interrupt", data="x"
    )  # FIXME connect to remote comfyui


# User interface

tab_names = ["Prompt", "Settings", "Model", "LoRAs"]
tab = {}
with ui.row().classes("w-full no-wrap"):
    with ui.column().classes("w-1/4 h-screen"):
        with ui.tabs().classes("w-full") as tabs:
            for name in tab_names:
                tab[name] = ui.tab(name)

        with ui.tab_panels(tabs, value=tab["Prompt"]).classes("w-full"):
            with ui.tab_panel(tab["Prompt"]):
                # build styles list from styles using .keys()
                stylelist = list(styles.keys())
                stylescomponent = ui.select(
                    stylelist,
                    label="Styles",
                    value="Style: sai-cinematic",
                    multiple=True,
                )
                prompt_text_area = ui.textarea(
                    label="Prompt",
                    placeholder="start typing",
                    value=gen_data["prompt"],
                )
                with ui.row():
                    generate_button = ui.button(
                        "Generate",
                        on_click=lambda: generate_clicked(),
                    )
                    stop_button = ui.button(
                        "Stop",
                        on_click=lambda: stop_clicked(),
                    )

            with ui.tab_panel(tab["Settings"]):
                with ui.row():
                    ui.label("Steps")
                    steps = ui.knob(
                        min=1,
                        max=50,
                        step=1,
                        value=gen_data["steps"],
                        show_value=True,
                    )
                    ui.label("CFG")
                    cfg = ui.knob(
                        min=0,
                        max=20,
                        step=0.01,
                        value=gen_data["cfg"],
                        show_value=True,
                    )

                with ui.row():
                    samplers = client.object_info("KSampler", "sampler_name")[0]
                    sampler = ui.select(
                        samplers,
                        label="Sampler",
                        value=gen_data["sampler"],
                    )

                schedulers = client.object_info("KSampler", "scheduler")[0]
                scheduler = ui.select(
                    schedulers,
                    label="Scheduler",
                    value=gen_data["scheduler"],
                )
                no_of_images_label = ui.label("Images")
                no_of_images = ui.slider(
                    min=1,
                    max=50,
                    value=1,
                    step=1,
                    on_change=lambda e: no_of_images_label.set_text(
                        "Images: " + str(e.value)
                    ),
                )

                ui.label("Resolution")
                resolution_picker = ui.select(
                    resolutions,
                )

            def model_select(modelname):
                global status
                status.set_text(f"Selected {modelname} model")
                ui.notify(f"Click")

            with ui.tab_panel(tab["Model"]):
                cachepath = Path(".cache/civitai")
                with ui.scroll_area().classes("w-full").style("height: 80vh"):
                    with ui.row().classes("full flex items-center"):
                        for modelname in models:
                            with ui.card().tight():
                                modelimage = Path.joinpath(
                                    cachepath,
                                    modelname.replace(".safetensors", ".jpeg"),
                                )
                                # create button with image
                                # scale image to fit button
                                with ui.button(
                                    color="transparent",
                                    on_click=lambda modelname=modelname: model_select(
                                        modelname
                                    ),
                                ).style("width: 150px; aspect-ratio: 1"):
                                    ui.image(
                                        str(modelimage),
                                    ).style("fit: cover; aspect-ratio: 1")
                                    ui.label(
                                        modelname.replace(".safetensors", "")
                                    ).classes(
                                        "absolute-bottom text-subtitle2 text-center"
                                    ).style(
                                        "white-space: nowrap; overflow: hidden; text-overflow: ellipsis"
                                    )

    # with tabs[tab_names.index("Model")]:
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
    # with tabs[tab_names.index("LoRAs")]:
    #    # lora_col, strength_col = left_column.columns([1, 1])
    #    lora_models = client.object_info("LoraLoader", "lora_name")[0]
    #    lora_model = st.selectbox(
    #        "Lora",
    #        ["None"] + lora_models,
    #        index=0,
    #    )
    #    lora_strength = st.slider("Strength", 0.0, 2.0, 1.0, 0.1)

    with ui.column().classes("w-3/4"):
        with ui.row().classes("w-full"):
            status = ui.label("").style("position: absolute")
        with ui.row().classes("w-full"):
            mainimage = ui.image("resources/YoRu.png").props(
                "fit=scale-down height=90vh"
            )

#    _, indent, _ = st.columns([1, 3, 1])
#    if "image" not in st.session_state:
#        st.session_state.image = "YoRu.png"
#    thisfile = indent.image(st.session_state.image, use_column_width=True)
#    my_bar = indent.progress(0)
#    prompt_column, button_column = st.columns([6, 1])

### LOGIC ###

# if generate_button:
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
# if stop_button:
#    requests.post(f"http://127.0.0.1:8188/interrupt", data="x")
#
#
# add_keyboard_shortcuts(
#    {
#        "Ctrl+Enter": "Generate",
#    }
# )

ui.run(favicon="resources/icon.png", dark=True, show=False, reload=False)
print("DEBUG: start")
