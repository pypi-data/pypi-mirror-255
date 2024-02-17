#!/usr/bin/env python3
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Action, SUPPRESS
import agx
import agxIO
import agxSDK
from rebrick import AgxToBrickMapper

init = agx.AutoInit()

class VersionAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(__version__)
        exit(0)


def parse_args():
    parser = ArgumentParser(description="Convert .agx files to .brick", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("agxfile", help="the .agx file to load")
    parser.add_argument("--root-system-name", help="Override the name of the root system model", metavar="<root system name>")
    parser.add_argument("--version", help="Show version", action=VersionAction, nargs=0, default=SUPPRESS)
    return parser.parse_known_args()


def run():
    args, _ = parse_args()
    simulation = agxSDK.Simulation()
    assembly = agxSDK.AssemblyRef(agxSDK.Assembly())
    if args.root_system_name is not None:
        assembly.setName(args.root_system_name)
    agxIO.readFile(args.agxfile, simulation, assembly.get())
    mapper = AgxToBrickMapper(os.path.dirname(args.agxfile), True)
    print(mapper.assemblyToBrick(assembly))

if __name__ == '__main__':
    run()
