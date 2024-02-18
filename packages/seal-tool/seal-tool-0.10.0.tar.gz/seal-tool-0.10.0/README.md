# seal

Perform richness-extent-grain analyses inspired by Palmer & White
([doi:10.1086/285704](https://doi.org/10.1086/285704), [doi:10.17615/n84a-pd17](https://doi.org/10.17615/n84a-pd17))

## Setup

### Installation

Simply download `seal` from Codeberg [releases](https://codeberg.org/mmatous/seal)
or clone the repository using git.

### First run

Done only when installing and running the tool for the first time.

Open the project directory in your
command-line interface.

#### Linux

In POSIX-compatible shell run:
```bash
source ./src/firstrun.sh
```

#### Windows

In PowerShell Run:
```
./src/firstrun.ps1
```

If you encounter an error such as `./src/firstrun.ps1 cannot be loaded because running scripts is disabled on this system`
on Windows, it means the script was blocked by your
security settings. In that case either unblock
the script e.g. using the [`Unblock-File` or `Set-ExecutionPolicy` cmdlets](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.4#example-7-unblock-a-script-to-run-it-without-changing-the-execution-policy) or run the
necessary commands manually.

```
python -m venv ./venv
./venv/Scripts/Activate.ps1
pip install .[dev]
```


You should see `(venv)` before your shell prompt now and `seal --help`
should run the tool without errors. Continue with [Usage](#Usage).

### Subsequent runs

Done when running the tool any time after the first initial installation.

Linux:
```
source ./venv/bin/activate
seal <subcommand>
```

Windows PowerShell:
```
./venv/Scripts/activate.ps1
seal <subcommand>
```

## Usage

One would generally want to use `preprocess`, `analyse` and `plot` subcommands in this order.
`misc` subcommand contains several scripts that
may be useful while converting or modifying either datasets or quadrat
lists for analysis.

More detailed help can be accesed by `seal --help`
or `seal <subcommand> --help`.

### Preprocess

Preprocess will ensure given dataset is fit to be processed
by the `analyse` command by e.g. sanitizing strings,
warning for missing values or
checking whether species column remains consistent with
name, morph and phase.

Example:
```
seal preprocess --dataset ./datasets/raw.csv --output ./datasets/clean.csv
```


### Analysis

`analyse` subcommand ingests [taskfile](./tasks/example-task.conf)
to perform analyses requested therein.

Example:
```
seal analyse --taskfile ./tasks/example-task.conf
```

Currently supported analyses are:

#### a1 - Overview

This analysis calculates per-quadrat species number
and number of encountered individuals for each level.

The additional data contain general description of given dataset and various smaller statistics for each level.
Such statistics include, for example, the most common value, mean, median, min and such for each data column.

This helps familiarize oneself with the data and serves as a basic check of the levels-creating strategy.

#### a2 - Species-area relationship

This analysis shows relationship between species richness and area sampled.

Species-area curve is calculated for each level by accumulating quadrats
and tallying the number of species. Since this method is sensitive to order of the
quadrats, number of permutations must be specified and their arithmetic mean is plotted.

The additional data contain statistics of the calculated results.

#### a3 - Distance-dependent species difference

This analysis creates pairwise difference of sets of encountered species
in two quadrats.

Result is the difference as a function of distance of the quadrats.

#### a4 - Radius richness

This analysis calculates the number of species within various distance intervals (interval's width is set by
the `interval-step` parameter)
from each quadrat. The radius forms a belt of sorts with a specified width.

We recommend using the size of the smallest quadrat as the smallest possible step.

#### a5 - Ratio of observed and expected species

This analysis calculates the ratio of observed and expected number of species for each
quadrat. The expected value is calculated as $$\sum_{}P_i * (1 - P_i)$$  where P<sub>i</sub> is the proportion
of quadrats occupied by species _i_ and the summation is over all the species in the study grid.

#### a6 - Ratio of shared and unique species

This analysis calculates several ratios for pairs of quadrats based on their distance.
1) Ratio of shared species among the quadrats and exclusive species among the quadrats.
2) Ratio of shared species among the quadrats and all
the species in the dataset.
3) Ratio of shared species among the quadrats and
all the species in the study grid.


#### a7 - Jaccard dissimilarity

This analysis calculates Jaccard dissimilarity with regards to species between
all possible pairs of quadrats.

Result is plotted as dissimilarity against the distance
of the quadrats.

Jaccard dissimilarity between quadrats _a_ and _b_ is calculated as:
$$J(a, b) = 1 - \frac{intersect_{ab}}{intersect_{ab} + exclusive_a + exclusive_b}$$



### Ploting

`plot` subcommand ingests [taskfile](./tasks/example-task.conf) to detect results of previous analyses
and present them as graphs.

Generated graphs will be saved to the same directory as
analysis results.

Example:
```
seal plot --taskfile ./tasks/example-task.conf
```

### Misc

`misc` subcommand is a kitchen sink of opinionated
convenience tools.

## Development

For unit tests run `python -m doctest ./src/seal/<file>`.

For functional tests run `pytest`.

### License
The source code—including the tests and documentation—is licensed under [GPLv3](./LICENSE)

`./datasets/data-bmd-sl.csv` is licensed under [CC-BY-SA-4.0](./datasets/LICENSE)

[aopk-fish.csv](./datasets/aopk-fish.csv) was provided under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
by AOPK ČR, Nálezová databáze ochrany přírody, on-line database portal.nature.cz. Downloaded 2024-02-05.
