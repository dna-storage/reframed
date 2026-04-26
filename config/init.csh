#!/bin/csh
# config/init.csh - optional environment setup for conda + MPI + Julia support.
#
# For the standard pip-only workflow you do NOT need this script; just run:
#   pip install -r requirements.txt && pip install -e .
#
# This script sets up the full conda environment with OpenMPI, Julia, and
# all optional dependencies.

# Resolve repo root (one directory up from the config/ directory).
set SCRIPT_DIR = `dirname $0`
set REPO_ROOT = `cd $SCRIPT_DIR/.. && pwd`
cd $REPO_ROOT

setenv DNASTORAGE_HOME $REPO_ROOT
setenv DNASTORAGE_TOOLS $REPO_ROOT/tools
setenv DNASTORAGE_LSF $REPO_ROOT/tools/lsf
setenv DNArSimPath $REPO_ROOT/dnastorage/fi/DNArSim
setenv FRAMED_CONFIGS $REPO_ROOT/examples
setenv FRAMED_CONDA $REPO_ROOT/framed_conda
setenv DNArSimData $REPO_ROOT/probEdit
setenv FRAMED_IMAGE_FILES $REPO_ROOT/test_files

git clone https://github.com/BHam-1/DNArSim/

rm -rf probEdit

mv DNArSim/simulator/probEdit $REPO_ROOT

set patch_prefixes = ("channel" "functions" "loadProb")

foreach i ($patch_prefixes)
    set patch_file = "${DNArSimPath}/${i}.patch"
    set original_file = "DNArSim/simulator/${i}.jl"
    set output_file = "${DNArSimPath}/${i}.jl"
    patch -o $output_file $original_file $patch_file
end

rm -rf DNArSim

if ( $#argv > 0 && "$argv[1]" == "-no-env" ) then
    exit
endif

conda env create --prefix $FRAMED_CONDA --file $SCRIPT_DIR/dnastorage.yml

conda activate $FRAMED_CONDA

pip install -r $REPO_ROOT/requirements.txt
pip install -e $REPO_ROOT

python -c "import julia; julia.install()"
