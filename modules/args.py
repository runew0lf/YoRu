import argparse

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=None, help="Set the listen port.")
    parser.add_argument("--comfy", type=str, default=None, help="Set eternal comfy host:port.")
    #parser.add_argument("--auth", type=str, help="Set credentials username/password.")
    #parser.add_argument(
    #    "--listen",
    #    type=str,
    #    default=None,
    #    metavar="IP",
    #    nargs="?",
    #    const="0.0.0.0",
    #    help="Set the listen interface.",
    #)
    #parser.add_argument(
    #    "--nobrowser", action="store_true", help="Do not launch in browser."
    #)
    return parser

def parse_args():
    parser = get_parser()
    return parser.parse_args()

