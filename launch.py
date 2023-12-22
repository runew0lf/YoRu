import subprocess
import streamlit.web.bootstrap
from streamlit import config as _config
import os

# _config.set_option("server.headless", True)
args = []


def main():
    command = [
        "..\python_embeded\python",
        "-s",
        "..\ComfyUI\main.py",
        "--windows-standalone-build",
        "--disable-auto-launch",
        "--preview-method",
        "auto",
    ]
    # Run the command in a new shell
    process = subprocess.Popen(command, shell=True)

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "main.py")
    streamlit.web.bootstrap.run(filename, "", args, flag_options={})


if __name__ == "__main__":
    main()
