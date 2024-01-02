import subprocess
import os
import sys
import modules.args

# _config.set_option("server.headless", True)
args = modules.args.parse_args()

#_config.set_option("server.runOnSave", True)


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

    if args.comfy is None and __name__ == "__main__":
        process = subprocess.Popen(command, shell=True)
    filename = os.path.join(dirname, "main.py")

    import ng_main

if __name__ in {"__main__"}:
    main()
