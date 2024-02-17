import sys
import numpy as np

from rich.console import Console
from collections import OrderedDict
from MDAnalysis import AtomGroup, Universe


def read_ndx_file(ndx_file_path: str, universe: Universe, console: Console) -> AtomGroup:

    ndx_content = OrderedDict()

    # Reading the ndx file
    with open(ndx_file_path, "r") as f:
        ndx_file = f.read()
    ndx_file = ndx_file.split("\n")

    # Parsing the ndx file content
    current_key = None
    for line in ndx_file:

        if line.startswith("[ "):
            current_key = line[2:-2]
            ndx_content[current_key] = list()
        elif line.startswith(";"):
            pass
        else:
            ndx_content[current_key] += list(map(int, line.split()))

    # Printing the groups in GROMACS style
    max_name_length = max(map(len, ndx_content.keys()))
    max_len_length = max(map(lambda x: len(str(len(x))), ndx_content.values()))

    console.print("Select group for rigid body analysis")
    for group_idx, group_name in enumerate(ndx_content):

        str_len = str(len(ndx_content[group_name]))

        current_line = "Group"
        current_line += str(group_idx).rjust(6)
        current_line += f" ( {group_name.ljust(max_name_length)} ) has "
        current_line += f"{str_len.ljust(max_len_length)} elements"

        console.print(current_line)

    selected_idx = int(console.input("Select a group: "))

    # Getting the selected atom IDs
    ndx_content = list(ndx_content.values())
    if selected_idx >= len(ndx_content) or selected_idx < 0:
        console.print(
            f"[red]ERROR: Invalid group index: {selected_idx}!"
        )
        sys.exit(1)

    atom_ids = ndx_content[selected_idx]

    # Getting the selected atoms.
    # This is highly inefficient, but will do for now...
    atom_indices = list()
    for current_id in atom_ids:

        current_idx = np.argwhere(universe.atoms.ids == current_id)
        if len(current_idx) != 1:
            console.print(
                f"[red]ERROR: Atom ID not found: {current_id}! "
                f"Maybe the given structure does not have atoms that are specified in the selected group?"
            )
            sys.exit(1)
        current_idx = current_idx[0, 0]
        atom_indices.append(current_idx)

    atom_indices = np.array(atom_indices)
    atom_group = universe.atoms[atom_indices]

    return atom_group
