# Rigid Body Segmentation (RiBoSe)

[![PyPI](https://img.shields.io/pypi/v/rigid-body-segmentation)](https://pypi.org/project/rigid-body-segmentation)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)

![Rigid Body Segmentation of The Mutant ab8 Nanobody in Complex with the SARS-CoV-2 S-RBD](
 https://github.com/fazekaszs/rigid_body_segmentation/tree/master/imgs/ab8_rbd_test_compressed.gif
)

## About

_RiBoSe_ is a tool for the analysis of MD trajectories.
It segments the simulated protein (or other stuff) into approximately rigid parts.
Within the parts, each atom has at least one other atomic partner whose distance's
 standard deviation is below a certain threshold.
The resulting segmentation should be helpful to reduce the number of degrees of 
 freedom to analyze, since each segment can be thought of as a single rigid body
 without an internal structure.
The result of _RiBoSe_ is a pdb file, which can be visualized (for eg. with [PyMol](https://pymol.org/2/)).
The atoms in the pdb file will have integer B-factor fields denoting the index of the
 segment they belong to.
Index -1 means that the atom does not belong to any segments, while 0 and above are the
 segment indices.

## Installation

The script bundle can be installed from PyPI:

```bash
pip install rigid-body-segmentation
```

## Dependencies

The following packages are used by _RiBoSe_:
- NumPy (tested with version 1.26.3)
- MDAnalysis (tested with version 2.7.0)
- scikit-learn (tested with version 1.4.0)
- rich (tested with version 13.7.0)

## Running _RiBoSe_

The following command runs the analysis:

```bash
python -m rigid_body_segmentation [OPTIONS]
```

The following flags are available:
- `-f` sets the trajectory file (xtc format, obligatory flag).
- `-s` sets the structure file (pdb format, obligatory flag).
- `-o` sets the output file (pdb format, obligatory flag).
- `-n` sets the index file (ndx format). Only needed if `-mode` is `"index"`.
- `-clr` and `-cln` set the cluster radius and cluster number parameters
 for the internal DBSCAN algorithm. By default, `-clr` is calculated from the
 distance standard deviation matrix, while `-cln` is set to 5.
- `-b`, `-e` and `-dt` set the beginning-, end- and step-times for the analysis.
 These values are given in ps dimensions.
- `-m` sets the mode, which defines what atoms should be included in the analysis.
 By default, it is set to `"CA"`, meaning that only the C&alpha; are used. Other
 possible values are `"CB"` and `"index"`.

## The algorithm

_RiBoSe_ creates two matrices for the selected atom set. 
The first matrix is the pairwise average distance matrix between the atoms, which
 is used to calculate the second matrix, which is the pairwise distance standard
 deviation matrix between the atoms.
Then, this latter matrix is used as a precalculated metric matrix for the DBSCAN 
 clustering algorithm.
These calculations utilize the 
 [Welford online algorithm](https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online).
The clustering algorithm groups atoms together that have small distance standard deviations.

## References

If you use _RiBoSe_, please cite one (or, even better, some) of the following articles:

```bibtex
@article{Fazekas2022,
  title = {Omicron Binding Mode: Contact Analysis and Dynamics of the Omicron Receptor-Binding Domain in Complex with ACE2},
  volume = {62},
  ISSN = {1549-960X},
  url = {http://dx.doi.org/10.1021/acs.jcim.2c00397},
  DOI = {10.1021/acs.jcim.2c00397},
  number = {16},
  journal = {Journal of Chemical Information and Modeling},
  publisher = {American Chemical Society (ACS)},
  author = {Fazekas,  Zsolt and Menyhárd,  Dóra K. and Perczel,  András},
  year = {2022},
  month = jul,
  pages = {3844–3853}
}
```
```bibtex
@article{NagyFazekas2023,
  title = {Inhibitor Design Strategy for Myostatin: Dynamics and Interaction Networks Define the Affinity and Release Mechanisms of the Inhibited Complexes},
  volume = {28},
  ISSN = {1420-3049},
  url = {http://dx.doi.org/10.3390/molecules28155655},
  DOI = {10.3390/molecules28155655},
  number = {15},
  journal = {Molecules},
  publisher = {MDPI AG},
  author = {Nagy-Fazekas,  Dóra and Fazekas,  Zsolt and Taricska,  Nóra and Stráner,  Pál and Karancsiné Menyhárd,  Dóra and Perczel,  András},
  year = {2023},
  month = jul,
  pages = {5655}
}
```