#!/usr/bin/env python3

import sys
from sigProfilerPlotting import sigProfilerPlotting
from sigProfilerPlotting.controllers import cli_controller


def main_function():
    commands = {
        "plotSBS": "Plot Single Base Substitutions.",
        "plotID": "Plot Small Insertions and Deletions.",
        "plotDBS": "Plot Doublet Base Substitutions.",
        "plotSV": "Plot Structural Variations.",
        "plotCNV": "Plot Copy Number Variations.",
    }

    if len(sys.argv) < 2 or sys.argv[1].lower() not in commands:
        print_usage(commands)
        sys.exit(1)

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    controller = cli_controller.CliController()

    if command == "plotsbs":
        controller.dispatch(args)
    elif command == "plotid":
        controller.dispatch(args)
    elif command == "plotdbs":
        controller.dispatch(args)
    elif command == "plotsv":
        controller.dispatch(args)
    elif command == "plotcnv":
        controller.dispatch(args)
    else:
        print_usage(commands)
        sys.exit(1)


def print_usage(commands):
    """Prints the usage message."""
    print("Usage: sigProfilerPlotting <command> [<args>]\n")
    print("Commands:")
    for cmd, desc in commands.items():
        print(f"  {cmd}: {desc}")
    print(
        "\nUse 'sigProfilerPlotting <command> --help' for more information on a specific command."
    )


if __name__ == "__main__":
    main_function()
