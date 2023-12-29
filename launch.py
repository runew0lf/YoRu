import subprocess
import streamlit.web.bootstrap
from streamlit import config as _config
import os
import sys
import modules.args

# _config.set_option("server.headless", True)
args = modules.args.parse_args()

_config.set_option("server.runOnSave", True)


def main():
    command = [
        "..\python_embeded\python",
        "-s",
        "..\ComfyUI\main.py",
        "--windows-standalone-build",
        "--disable-auto-launch",
        "--preview-method",
        "auto",
        "--output-directory",
        "..\YoRu\outputs",
    ]
    # Run the command in a new shell
    dirname = os.path.dirname(__file__)
    if dirname != "":
        os.chdir(dirname)

    if args.comfy is None:
        process = subprocess.Popen(command, shell=True)
    filename = os.path.join(dirname, "main.py")
    streamlit.web.bootstrap.run(filename, "", sys.argv[1:], flag_options={})


if __name__ == "__main__":
    main()
