#!/usr/bin/env python3
import agxOSG
import agxSDK
import agx
import os
import sys
import signal
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Action, SUPPRESS
from brickbundles import bundle_path
from rebrick import validate_brickfile, __version__, ClickAdapter

class VersionAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(__version__)
        exit(0)


def parse_args():
    parser = ArgumentParser(description="View brick models", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("brickfile", help="the .brick file to load")
    parser.add_argument("--bundle-path", help="list of path to bundle dependencies if any. Overrides environment variable BRICK_BUNDLE_PATH.", 
                        metavar="<bundle_path>", default=bundle_path())
    parser.add_argument("--debug-render-tnc", help="Path to .obj file to use to debug render mate connector frames (tangent, normal, cross)",
                        metavar="<objpath>", default="")
    parser.add_argument("--loglevel", choices=["trace", "debug", "info", "warn", "error", "critical", "off"], help="Set log level", default="warn")
    parser.add_argument("--modelname", help="The model to load (defaults to last model in file)", metavar="<name>", default="")
    parser.add_argument("--version", help="Show version", action=VersionAction, nargs=0, default=SUPPRESS)
    return parser.parse_args()

class AllowCtrlBreakListener(agxOSG.ExampleApplicationListener):
    pass

def validate():

    args = parse_args()
    ClickAdapter.set_log_level(args.loglevel)

    _ = agx.init()
    simulation = agxSDK.Simulation()

    if validate_brickfile(simulation, args.brickfile, args.bundle_path, args.modelname, args.debug_render_tnc):
        exit(0)
    else:
        exit(255)

def handler(signum, frame):
    os._exit(0)

def run():
    signal.signal(signal.SIGINT, handler)
    validate()

if __name__ == '__main__':
    run()
