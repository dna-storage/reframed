# Contributing to reFrameD

## Development Setup

For basic library development (no MPI or HPC tools required):

```bash
git clone https://github.com/dna-storage/reframed
cd reframed
pip install -r requirements.txt
pip install -e .
```

For the full simulation environment (conda + MPI + Julia), see [`config/README.md`](config/README.md) and use:

```bash
tcsh
source dnastorage.env
make init
make develop
```

## Running Tests

```bash
make test
# or equivalently:
python -m pytest tests
```

Use `pytest -v` for verbose output, or `pytest tests/test_pipeline_roundtrip.py` to run a specific file. The test suite does not require MPI.

## Adding a New Pipeline Format

1. **Create a builder function** in `dnastorage/arch/builder.py`. Follow the pattern of the existing builders (`ReedSolomon_Base4_Pipeline`, `Basic_Hedges_Pipeline`, etc.):
   - Call `check_required(required, **kwargs)` at the top with the list of kwargs your pipeline truly needs
   - Extract all other kwargs with `.get()` and sensible defaults
   - Assemble codec tuples: `out_pipeline`, `inner_pipeline`, `DNA_pipeline`
   - Return `pipeline.PipeLine(out_pipeline + inner_pipeline + DNA_pipeline, ...)`

2. **Register the format** in `dnastorage/system/formats.py` in the `FileSystemFormats` dict:
   ```python
   "MyNewFormat": FormatEntry(
       format_id=<unique_integer>,
       block_size=<bytes>,
       strand_size=<bytes>,
       abbreviation="MNF",
       description="Brief description",
       encoder=MyNewFormat_Pipeline,
       decoder=MyNewFormat_Pipeline,
   )
   ```
   **Warning:** Format IDs are stored in encoded DNA file headers. Once a format ID is assigned and used in real experiments, it must never be changed or reused.

3. **Add a roundtrip test** in `tests/test_pipeline_roundtrip.py` following the existing test pattern using the `_encode` / `_decode` helpers.

## Parameter Naming Convention

Builder kwargs use a legacy mixed naming convention that matches the JSON configuration files used by the fault injection and sequencing tools:

| Parameter | Style | Notes |
|-----------|-------|-------|
| `blockSizeInBytes`, `strandSizeInBytes` | camelCase-ish | Core sizing |
| `outerECCStrands`, `outerECCdivisor` | mixed | Outer error correction |
| `inner_ECC` | snake_case | Inner error correction |
| `hedges_rate`, `hedges_pad`, `hedge_prev_bits` | snake_case (inconsistent) | Hedges codec params |

**Do not rename these parameters.** JSON config files in `examples/` pass these names directly to the builder functions. Renaming them would silently break all existing experiment configurations.

## Code Style

No formatter is currently enforced. For new code, follow PEP 8 with a line length of 120. The wildcard imports (`from dnastorage.codec.phys import *`) in `builder.py` are intentional — the codec namespace is large and used heavily.

## Submitting Changes

1. Fork the repository and create a branch for your change
2. Make your changes and ensure `make test` passes
3. Open a pull request against `main` — the CI will run the test suite automatically

## Reporting Issues

Please open a GitHub issue at https://github.com/dna-storage/reframed/issues.
