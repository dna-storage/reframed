#!/bin/bash
# config/init.sh - optional environment setup for conda + MPI + Julia support.
#
# For the standard pip-only workflow you do NOT need this script; just run:
#
#   pip install -r requirements.txt && pip install -e .
#
# This script sets up the full conda environment with OpenMPI, Julia, and
# all optional dependencies.
set -e

# Resolve the repo root (two levels up from this script).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------
export DNASTORAGE_HOME="$REPO_ROOT"
export DNASTORAGE_TOOLS="$REPO_ROOT/tools"
export DNASTORAGE_LSF="$REPO_ROOT/tools/lsf"
export DNArSimPath="$REPO_ROOT/dnastorage/fi/DNArSim"
export FRAMED_CONFIGS="$REPO_ROOT/examples"
export FRAMED_CONDA="$REPO_ROOT/framed_conda"
export DNArSimData="$REPO_ROOT/probEdit"
export FRAMED_IMAGE_FILES="$REPO_ROOT/test_files"

# ---------------------------------------------------------------------------
# Clone DNArSim, apply patches, then remove the clone
# ---------------------------------------------------------------------------
git clone https://github.com/BHam-1/DNArSim/

rm -rf probEdit
mv DNArSim/simulator/probEdit "$REPO_ROOT"

for i in channel functions loadProb; do
    patch_file="${DNArSimPath}/${i}.patch"
    original_file="DNArSim/simulator/${i}.jl"
    output_file="${DNArSimPath}/${i}.jl"
    patch -o "$output_file" "$original_file" "$patch_file"
done

rm -rf DNArSim

if [ "${1:-}" = "-no-env" ]; then
    exit 0
fi

# ---------------------------------------------------------------------------
# Create the conda environment (includes OpenMPI and mpi4py)
# ---------------------------------------------------------------------------
conda env create --prefix "$FRAMED_CONDA" --file "$SCRIPT_DIR/dnastorage.yml"

# ---------------------------------------------------------------------------
# Install pip packages and the package itself inside the conda env.
# ---------------------------------------------------------------------------
conda run --live-stream --prefix "$FRAMED_CONDA" pip install -r "$REPO_ROOT/requirements.txt"
conda run --live-stream --prefix "$FRAMED_CONDA" pip install -e "$REPO_ROOT"
conda run --live-stream --prefix "$FRAMED_CONDA" python -c "import julia; julia.install()"
