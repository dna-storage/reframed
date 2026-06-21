# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**reFrameD** is a Python package (`dnastorage`) for modeling DNA-based information storage systems. It provides encoding, decoding, and simulation infrastructure for evaluating different codec architectures under realistic fault conditions.

## Commands

### Installation

For standard development (no conda or MPI):
```bash
pip install -r requirements.txt
pip install -e .
```

Full environment with MPI, Julia (for DNArSim), and conda:
```bash
source dnastorage.env   # set environment variables; repeat each session
make init               # runs config/init.sh: clones DNArSim, creates conda env
make develop            # pip install -e . inside conda env
```

The C++ extensions (`fasthedges`, `generate`) are compiled automatically during `pip install -e .`. If compilation fails, the package falls back to pure-Python equivalents automatically.

### Running Tests

```bash
python -m pytest tests/
```

Run a single test file:
```bash
python -m pytest tests/test_pipeline_roundtrip.py
```

Run a single test class or method:
```bash
python -m pytest tests/test_pipeline_roundtrip.py::TestReedSolomonBase4Roundtrip
python -m pytest tests/test_pipeline_roundtrip.py::TestReedSolomonBase4Roundtrip::test_erasure_recovery_within_capacity
```

### Fault Injection Experiments

```bash
cd $DNASTORAGE_HOME
tcsh examples/small/run_small.csh          # small non-HPC example, 12 cores
```

Larger experiments (LSF HPC only):
```bash
tcsh examples/iid/iid_experiment_script.csh
tcsh examples/DNArSim/DNArSim_experiment_script.csh
```

Compile results into a Pandas dataframe after experiments finish:
```bash
cd tools/data_analysis
python db_gen.py --path <top result path> --name fault_injection_dataframe
```

### Analysis Notebooks

```bash
conda activate framed_conda
cd notebooks
jupyter-lab framed.ipynb
```

## Architecture

### Codec Pipeline (the core abstraction)

The central data flow is: **file bytes → packets → DNA strands → (channel/fault injection) → DNA strands → packets → file bytes**.

`dnastorage/codec/PipeLine.py` — `PipeLine` class orchestrates the entire encode/decode pipeline. Components are classified by the type-tagging classes in `dnastorage/codec_types.py`:

| Tag class | Role |
|-----------|------|
| `BaseOuterCodec` | Block-level ECC across strands (e.g. Reed-Solomon, LT fountain) |
| `CWtoCW` | Codeword-to-codeword transformations (e.g. inner RS, CRC, randomize) |
| `CWtoDNA` | Codeword-to-DNA conversion (HEDGES, Base4 transcoding) |
| `DNAtoDNA` | DNA post-processing (primer prepend/append, length filters) |
| `Probe` | Instrumentation inserted for data collection during fault injection |

Encoding order when building the pipeline tuple: outer → inner → CW-to-DNA → DNA-to-DNA. `PipeLine.__init__` validates ordering and builds cascades via `cascade_build()`. During decode, each layer is peeled in reverse.

### Pipeline Builders (`dnastorage/arch/builder.py`)

Pre-assembled pipelines are created by builder functions. The four main ones:

- `ReedSolomon_Base4_Pipeline` — RS outer code, Base4 inner transcoding
- `Basic_Hedges_Pipeline` — RS outer code, HEDGES inner code (handles indels)
- `Fountain_Base4_Pipeline` — LT fountain outer code, Base4 inner transcoding
- `Fountain_Hedges_Pipeline` — LT fountain outer, HEDGES inner
- `*_FileLevelFountain_Pipeline` variants add a cross-block LT code on top

Builders accept a `packetizedfile` and `**kwargs` for all codec parameters. All kwargs have documented defaults inside each builder function.

### Format Registry (`dnastorage/system/formats.py`)

`FileSystemFormats` maps integer format IDs (e.g. `0x0704`) to pipeline builder functions. **Do not remove or alter existing entries** — backwards compatibility with encoded files depends on stable IDs. New pipelines are added as new entries.

### File-Level I/O (`dnastorage/system/pipeline_dnafile.py`)

`DNAFilePipeline.open("w", ...)` / `DNAFilePipeline.open("r", ...)` wraps encoding/decoding with file header management. The file header is itself DNA-encoded using the `BasicHedges` format and stores all pipeline parameters needed for decoding. A binary backup of the header pipeline config is also saved (`.header` file) in case the DNA header cannot be decoded.

### Strand Representation (`dnastorage/strand_representation.py`)

`BaseDNA` is the universal strand container used throughout the pipeline:
- `dna_strand` — string of ACGT characters
- `codewords` — list of byte integers (before/after DNA conversion)
- `index_ints` — tuple of integers encoding the strand's position in the block hierarchy
- `index_bytes` — how many bytes in `codewords` are reserved for the index

### Packetized File I/O (`dnastorage/util/packetizedfile.py`)

`ReadPacketizedFilestream` reads a byte stream in fixed-size blocks. `WritePacketizedFilestream` accepts out-of-order packets by index and assembles the final file when all packets arrive.

### Fault Injection (`dnastorage/fi/`)

`BaseFI.open(fault_injector_name, **kwargs)` returns a fault model. Available models:

- `fixed_rate` — uniform per-nucleotide error rate (sub/del/ins equally probable)
- `position_fixed_rate` — per-position rates from a pickle file
- `pattern_fixed_rate` — burst patterns drawn from a distribution
- `strand_fault_compressed` — fixed number of faulty strands
- `sequencing_experiment` — replays real nanopore FASTQ reads via a mapping file
- `sequencing_experiment_downsample` — same, with random subsampling
- `DNArSim` — calls the Julia DNArSim nanopore channel simulator (requires Julia + the env var `DNArSimPath`)

The top-level experiment driver is `tools/fault_injection.py`, which is invoked by the LSF job generators (`tools/lsf/`). Experiment parameters are passed as JSON config files.

### Clustering & Consolidation (`dnastorage/cluster/`, `dnastorage/codec/consolidation.py`)

After decoding the DNA layer, multiple noisy copies of the same strand are consolidated before inner decoding:
- `LocalitySensitiveHashCluster` (LSH) — groups similar strands via minhash signatures
- `IdealCluster` — oracle clustering using ground-truth index (for simulation only)
- `BasicDNAClusterModel` — runs cluster → `MuscleAlign` → `SimpleMajorityVote`
- `SimpleMajorityVote` — consolidates aligned codeword copies by majority

### HEDGES Inner Code (`dnastorage/codec/hedges.py`, `dnastorage/codec/fasthedges/`)

HEDGES is a trellis-based insertion/deletion-correcting code. The Python wrapper in `hedges.py` calls the C++ extension `fasthedges` (compiled from `dnastorage/codec/fasthedges/`). The C++ implementation is the performance-critical path.

### Environment Variables

Set by `dnastorage.env` or `config/init.sh`:

| Variable | Purpose |
|----------|---------|
| `DNASTORAGE_HOME` | Repo root |
| `DNASTORAGE_TOOLS` | `tools/` directory |
| `DNArSimPath` | Path to Julia DNArSim files (required for DNArSim fault model) |
| `DNArSimData` | Path to `probEdit/` probability tables for DNArSim |
| `FRAMED_CONDA` | Conda environment prefix |

## Key Conventions

### Adding a New Pipeline

1. Implement a builder function in `dnastorage/arch/builder.py` following the existing pattern (accepts `pf, **kwargs`, returns a `PipeLine`).
2. Register it in `FileSystemFormats` in `dnastorage/system/formats.py` with a new format ID. Never modify existing IDs.
3. Add roundtrip tests in `tests/test_pipeline_roundtrip.py`.

### Header Serialization

Every codec component that must preserve state across encode/decode sessions implements `encode_header()` / `decode_header(buf)`. The `buf` is a raw byte list; `decode_header` consumes its bytes and returns the remainder. This chain propagates through the entire cascade via `BaseCodec.encode_header()` / `decode_header()`.

### MPI Parallelism

Decoding supports optional MPI parallelism. Attach a communicator via `pipeline.mpi = comm`. The pipeline scatters strands across ranks for inner decoding, then gathers results at rank 0 for outer decoding. MPI is an optional dependency (`mpi4py`); the package works without it.

### Test Fixtures

`tests/conftest.py` provides an `autouse` fixture (`fi_test_data`) that generates synthetic `test_dna.txt` and `test_rate.csv` in a `tmp_path` and `chdir`s into it, so fault-injection tests that open these files by name work without any manual setup.
