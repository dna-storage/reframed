# Configuration

This directory contains environment configuration files for optional setups.

## Files

| File | Purpose |
|------|---------|
| `dnastorage.yml` | Conda environment definition (optional; includes MPI/OpenMPI) |
| `Dockerfile` | Docker image with full environment including MPI and Julia |
| `init.sh` | Bash setup script for conda+MPI environment (Linux/macOS) |
| `init.csh` | C-shell setup script for conda+MPI environment |

## Default (pip-only) setup

For the standard Python-only workflow, just install from `requirements.txt`:

```bash
pip install -r requirements.txt
pip install -e .
```

MPI (`mpi4py`) and Julia (`julia`) support are **optional** extensions.

## Conda + MPI setup

If you need MPI-based parallelism or Julia fault-injection support:

```bash
conda env create -f config/dnastorage.yml
conda activate dnastorage
pip install -r requirements.txt
pip install -e .
```

For Julia / DNArSim support, run `config/init.sh` inside the activated environment.
