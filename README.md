# Optimization

Small collection of optimization models and example notebooks.

## Project layout
- `src/electricity/base.py`: abstract `OptimizationModel` base class.
- `src/electricity/unit_commitment.py`: `GeneratorCommitment` unit-commitment model.
- `notebooks/electricity_markets.ipynb`: example notebook using the electricity models.
- `data/`, `docs/`, `tests/`: placeholders for inputs, docs, and tests.

## Setup
1) Create and activate the conda env:
```bash
conda env create -f environment.yml
conda activate opt_env
```

## Using the code in notebooks
Because this isn’t installed as a package, make sure Python can see the project root:
- Easiest: start Jupyter from the project root after activating the env:
  ```bash
  conda activate opt_env
  jupyter lab
  ```
- If a notebook kernel still can’t find `src`, add one line at the top of the notebook:
  ```python
  import sys, pathlib
  sys.path.append(str(pathlib.Path.cwd().parent))  # assumes notebook is in notebooks/
  ```
Then you can import:
```python
from src import GeneratorCommitment
# or: from src.electricity import GeneratorCommitment
```

## Notes
- You need a solver available to Pyomo (CBC, GLPK, HiGHS, etc.); `environment.yml` includes them.
- Add new domain code under `src/<domain>/` and optionally re-export it in `src/__init__.py` for simple imports.
