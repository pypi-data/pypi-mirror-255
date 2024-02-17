import sys
from rich.console import Console
from argparse import ArgumentParser, Namespace
from pathlib import Path


def _validate_arguments(args: Namespace, console: Console):

    if not Path(args.trajectory_file).exists():
        console.print("[red]ERROR: Path to trajectory file does not exist!")
        sys.exit(1)

    if not Path(args.trajectory_file).is_file():
        console.print("[red]ERROR: Path to trajectory file is not a file!")
        sys.exit(1)

    if not args.trajectory_file.endswith(".xtc"):
        console.print("[red]ERROR: Trajectory file does not have an xtc extension!")
        sys.exit(1)

    if not Path(args.structure_file).exists():
        console.print("[red]ERROR: Path to structure file does not exist!")
        sys.exit(1)

    if not Path(args.structure_file).is_file():
        console.print("[red]ERROR: Path to structure file is not a file!")
        sys.exit(1)

    if not args.structure_file.endswith(".pdb"):
        console.print("[red]ERROR: Structure file does not have a pdb extension!")
        sys.exit(1)

    if args.index_file is not None and args.mode == "index":

        if not Path(args.index_file).exists():
            console.print("[red]ERROR: Path to index file does not exist!")
            sys.exit(1)

        if not Path(args.index_file).is_file():
            console.print("[red]ERROR: Path to index file is not a file!")
            sys.exit(1)

        if not args.index_file.endswith(".ndx"):
            console.print("[red]ERROR: Index file does not have an ndx extension!")
            sys.exit(1)

    if not args.output_file.endswith(".pdb"):
        args.output_file += ".pdb"


def parse_cli_args(console: Console) -> Namespace:

    arg_parser = ArgumentParser()

    arg_parser.add_argument(
        "-f", "--trajectory_file",
        type=str, required=True,
        help="The path to the trajectory file. It's extension should be xtc."
    )

    arg_parser.add_argument(
        "-s", "--structure_file",
        type=str, required=True,
        help="The path to the structure file. It's extension should be pdb."
    )

    arg_parser.add_argument(
        "-o", "--output_file",
        type=str, required=True,
        help="The b-labelled output pdb file."
    )

    arg_parser.add_argument(
        "-n", "--index_file",
        type=str, default=None,
        help="The index file containing the atoms for the RBS if mode is \"index\"."
    )

    arg_parser.add_argument(
        "-clr", "--cluster_radius",
        type=float, default=None,
        help="The epsilon value for the DBSCAN clustering algorithm given in nm."
    )

    arg_parser.add_argument(
        "-cln", "--cluster_neighbours",
        type=int, default=5,
        help="The min_samples value for the DBSCAN clustering algorithm."
    )

    arg_parser.add_argument(
        "-b", "--begin_time",
        type=int, default=0,
        help="The time (in ps) from the algorithm reads the trajectory."
    )

    arg_parser.add_argument(
        "-e", "--end_time",
        type=int, default=None,
        help="The time (in ps) until the algorithm reads the trajectory."
    )

    arg_parser.add_argument(
        "-dt", "--delta_time",
        type=int, default=None,
        help="The time (in ps) interval the algorithm reads the trajectory."
    )

    arg_parser.add_argument(
        "-m", "--mode",
        type=str, default="CA", choices=["CA", "CB", "index"],
        help="Either \"CA\", \"CB\", or \"index\"."
    )

    args: Namespace = arg_parser.parse_args()
    _validate_arguments(args, console)

    return args
