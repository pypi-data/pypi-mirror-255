import sys
import warnings
import numpy as np

from argparse import Namespace
from rich.console import Console
from rich.progress import Progress
from MDAnalysis import Universe, AtomGroup
from MDAnalysis.coordinates.base import Timestep, ReaderBase
from sklearn.cluster import DBSCAN

from .cli_args import parse_cli_args
from .ndx_file import read_ndx_file

console = Console()


def get_ref_selection(universe: Universe, args: Namespace) -> AtomGroup:

    ref_selection: AtomGroup
    if args.mode == "CA":
        ref_selection = universe.select_atoms("name CA")
    elif args.mode == "CB":
        ref_selection = universe.select_atoms("name CB or (name CA and resname GLY)")
    elif args.mode == "index":
        ref_selection = read_ndx_file(args.index_file, universe, console)
    else:
        raise Exception(f"Mode error! Mode was \"{args.mode}\", which is unexpected!")

    console.print(f"Number of selected residues: {ref_selection.n_residues}")
    console.print(f"Number of selected atoms: {ref_selection.n_atoms}")

    return ref_selection


def get_trajectory_slice(universe: Universe, args: Namespace) -> ReaderBase:

    begin_frame = int(args.begin_time / universe.trajectory.dt)

    console.print(f"Start frame is {begin_frame} at time {args.begin_time} ps.")

    if args.end_time is None:
        end_frame: int = len(universe.trajectory)
        args.end_time = end_frame * universe.trajectory.dt
    else:
        end_frame = int(args.end_time / universe.trajectory.dt)

    console.print(f"End frame is {end_frame} at time {args.end_time} ps.")

    if args.delta_time is None:
        delta_frame: int = 1
        args.delta_time = universe.trajectory.dt
    else:
        delta_frame = int(args.delta_time / universe.trajectory.dt)

    if delta_frame == 0:
        console.print(
            f"[red]ERROR: "
            f"The delta time for the analysis ({args.delta_time} ps) "
            f"is smaller than the delta time of the trajectory ({universe.trajectory.dt} ps)!"
        )
        sys.exit(1)

    console.print(f"Delta frame is {delta_frame} with a delta time of {args.delta_time} ps.")

    trajectory = universe.trajectory[begin_frame:end_frame:delta_frame]

    return trajectory


def get_distance_std_mx(
    trajectory: ReaderBase,
    ref_selection: AtomGroup,
    args: Namespace
) -> np.ndarray:

    dmx_mean = None
    dmx_variance = None

    with Progress(console=console) as progress:

        task = progress.add_task("Calculating matrices...", total=len(trajectory))

        frame: Timestep
        for frame_idx, frame in enumerate(trajectory):

            ca_positions: np.ndarray = ref_selection.positions
            dmx = ca_positions[:, np.newaxis, :] - ca_positions[np.newaxis, :, :]
            dmx = np.sqrt(np.sum(dmx ** 2, axis=2))

            if dmx_mean is None:
                dmx_mean = np.copy(dmx)
                dmx_variance = np.zeros(dmx.shape)
            else:
                new_dmx_mean = dmx_mean + (dmx - dmx_mean) / (frame_idx + 1)
                dmx_variance += (dmx - dmx_mean) * (dmx - new_dmx_mean)
                dmx_mean = np.copy(new_dmx_mean)

            current_time = args.begin_time + frame_idx * args.delta_time
            progress.update(task, advance=1)  # , description=f"Sim. time: {current_time} ps")

    return np.sqrt(dmx_variance / len(trajectory))


def show_dist_std_mx_stat(distance_std_mx: np.ndarray, args: Namespace) -> None:

    console.print(f"Distance standard deviation matrix constructed with shape: {distance_std_mx.shape}.")

    console.print(f"\tMin: {np.min(distance_std_mx):.3f} nm")
    console.print(f"\tMax: {np.max(distance_std_mx):.3f} nm")
    console.print(f"\tAvg: {np.mean(distance_std_mx):.3f} nm")
    console.print(f"\tMedian: {np.median(distance_std_mx):.3f} nm")
    console.print(f"\tStd: {np.std(distance_std_mx):.3f} nm")

    nth_closest_neigh_med_value = np.median(np.sort(distance_std_mx, axis=1)[:, args.cluster_neighbours])
    console.print(f"\tMedian of {args.cluster_neighbours}th closest neighbour: {nth_closest_neigh_med_value:.3f} nm")

    if args.cluster_radius is None:
        console.print("[yellow]No clustering radius was given! Using the previous median value as a radius.")
        args.cluster_radius = nth_closest_neigh_med_value


def perform_segmentation(distance_std_mx: np.ndarray, args: Namespace) -> np.ndarray:

    segmentation_labels: np.ndarray = DBSCAN(
        eps=args.cluster_radius,
        min_samples=args.cluster_neighbours,
        metric="precomputed"
    ).fit(distance_std_mx).labels_

    console.print(f"Segmentation done! Found {len(np.unique(segmentation_labels))} segments.")

    for idx in np.sort(np.unique(segmentation_labels)):
        current_size = np.sum(segmentation_labels == idx)
        console.print(f"\tSize of segment {idx}: {current_size}")

    return segmentation_labels


def blabel(
    universe: Universe,
    ref_selection: AtomGroup,
    segmentation_labels: np.ndarray,
    args: Namespace
):

    console.print("Resetting atom bfactors...")
    universe.add_TopologyAttr("tempfactors")  # needed to set the tempfactors of the atoms
    for atom in universe.atoms:
        atom.tempfactor = -1.

    if args.mode == "index":
        for idx, atom in enumerate(ref_selection.atoms):
            atom.tempfactor = segmentation_labels[idx]
    else:
        for idx, atom in enumerate(ref_selection.atoms):
            tempfactor_array = segmentation_labels[idx] * np.ones(len(atom.residue.atoms))
            atom.residue.atoms.tempfactors = tempfactor_array

    # Without "catch_warnings" we would get "Found no information for attr: 'formalcharges'".
    with warnings.catch_warnings(action="ignore"):
        universe.select_atoms("all").write(args.output_file)

    console.print(f"B-labelled pdb file saved as {args.output_file}")


def main():

    console.print("[green](main) Parsing CLI arguments...")
    args = parse_cli_args(console)

    console.print("[green](main) Reading trajectory and structure files...")
    universe = Universe(args.structure_file, args.trajectory_file)

    console.print("[green](main) Getting the reference selection...")
    ref_selection = get_ref_selection(universe, args)

    console.print("[green](main) Getting the analyzable trajectory interval...")
    trajectory = get_trajectory_slice(universe, args)

    console.print("[green](main) Calculating the distance standard deviation matrix...")
    distance_std_mx = get_distance_std_mx(trajectory, ref_selection, args)

    console.print("[green](main) Displaying statistics about the distance standard deviation matrix...")
    show_dist_std_mx_stat(distance_std_mx, args)

    console.print("[green](main) Performing segmentation...")
    segmentation_labels = perform_segmentation(distance_std_mx, args)

    console.print("[green](main) Saving the b-labelled structure...")
    blabel(universe, ref_selection, segmentation_labels, args)

    console.print("[green](main) Program terminated with success!")


if __name__ == "__main__":
    main()
