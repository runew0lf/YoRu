import toml


def load_resolutions():
    with open("settings/resolutions.toml", "r") as f:
        resolutions = toml.load(f)
    return resolutions


resolutions = load_resolutions()
