# Experiment Configuration Schema

This document describes every parameter accepted by the fault-injection experiment system.
Experiments are defined as JSON files (or sweep configs) consumed by `tools/lsf/generate_fi_jobs.py`
and executed by `tools/fault_injection.py`.

## Top-level structure

```json
{
  "encoder":          "<string>",
  "encoder_params":   { ... },
  "fi_env_params":    { ... },
  "fault_params":     { ... },
  "distribution_params": { ... },
  "header_params":    { ... },
  "dna_processing":   { ... },
  "sim_params":       { ... }
}
```

---

## `encoder`

Selects the pipeline architecture. Must match a key in `FileSystemFormats`
(`dnastorage/system/formats.py`).

| Value | Architecture |
|-------|-------------|
| `"ReedSolomon_Base4"` | RS outer + Base4 inner |
| `"BasicHedges"` | RS outer + HEDGES inner (handles indels) |
| `"Fountain_Base4"` | LT fountain outer + Base4 inner |
| `"Fountain_Hedges"` | LT fountain outer + HEDGES inner |
| `"ReedSolomon_Base4_FileLevelFountain"` | RS + Base4 + cross-block LT |
| `"Fountain_Base4_FileLevelFountain"` | LT + Base4 + cross-block LT |

---

## `encoder_params`

Parameters forwarded to the pipeline builder. Defaults differ by architecture.

### Common to all architectures

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `strand_length` | int | 32 | Payload nucleotides per strand |
| `index_bytes` | int | 2 | Bytes reserved for strand index |
| `rs_inner_distance` | int | 4 | Inner Reed-Solomon minimum Hamming distance |
| `crc_bytes` | int | 1 | CRC bytes appended per strand (`0` to disable) |
| `use_randomizer` | bool | true | XOR-randomize codewords to spread GC content |

### `ReedSolomon_Base4` / `ReedSolomon_Base4_FileLevelFountain`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `rs_outer_distance` | int | 8 | Outer RS minimum Hamming distance |
| `block_size` | int | 20 | Strands per RS outer block |

### `BasicHedges`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `hedges_rate` | float | 0.5 | Bits per nucleotide for HEDGES trellis |
| `hedges_prev_bits` | int | 8 | Context bits used in HEDGES trellis |
| `rs_outer_distance` | int | 8 | Outer RS minimum Hamming distance |
| `block_size` | int | 20 | Strands per outer block |

### `Fountain_Base4` / `Fountain_Base4_FileLevelFountain`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `fountain_redundancy` | float | 0.2 | Extra strands as fraction of source strands |
| `fountain_seed` | int | 0 | PRNG seed for LT code degree distribution |

### `Fountain_Hedges`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `hedges_rate` | float | 0.5 | Bits per nucleotide for HEDGES trellis |
| `hedges_prev_bits` | int | 8 | Context bits used in HEDGES trellis |
| `fountain_redundancy` | float | 0.2 | Extra strands as fraction of source strands |
| `fountain_seed` | int | 0 | PRNG seed for LT code degree distribution |

---

## `fi_env_params`

Controls the fault-injection environment loop.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `trials` | int | 1 | Number of independent Monte Carlo trials |
| `read_distribution` | string | `"bernoulli"` | Strand read-count distribution (see below) |
| `coverage` | float | 10.0 | Mean reads per strand |
| `synthesis_scale` | float | 1.0 | Multiply all synthesis error rates by this factor |
| `file` | string | *required* | Path to input file to encode |

---

## `fault_params`

Selects and configures the channel fault model. The `"fault_model"` key chooses
which model is instantiated; remaining keys are forwarded to that model.

### `fault_model`: `"fixed_rate"`

Uniform per-nucleotide error rate with equal substitution / deletion / insertion probability.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `error_rate` | float | 0.01 | Per-nucleotide error probability |

### `fault_model`: `"position_fixed_rate"`

Per-position error rates loaded from a pickle file.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `rate_file` | string | *required* | Path to pickle file mapping position → rate |

### `fault_model`: `"pattern_fixed_rate"`

Burst error patterns drawn from a distribution.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `pattern_file` | string | *required* | Path to pickle file of error patterns |
| `error_rate` | float | 0.01 | Overall burst trigger rate |

### `fault_model`: `"strand_fault_compressed"`

Introduces a fixed number of faulty strands regardless of pool size.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `num_faulty_strands` | int | 0 | Number of strands to corrupt |
| `error_rate` | float | 0.01 | Per-nucleotide error rate on faulty strands |

### `fault_model`: `"sequencing_experiment"`

Replays real nanopore FASTQ reads via a pre-computed strand mapping.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mapping_file` | string | *required* | Path to mapping pickle (strand → FASTQ reads) |

### `fault_model`: `"sequencing_experiment_downsample"`

Same as `sequencing_experiment` with random subsampling of reads.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mapping_file` | string | *required* | Path to mapping pickle |
| `downsample_fraction` | float | 1.0 | Fraction of reads to retain |

### `fault_model`: `"DNArSim"`

Calls the Julia DNArSim nanopore channel simulator. Requires Julia, the
`DNArSimPath` environment variable, and the conda environment.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `pore_model` | string | `"r9"` | Nanopore model (`"r9"`, `"r10"`) |
| `error_scale` | float | 1.0 | Scale factor for DNArSim error rates |

---

## `distribution_params`

Controls the read-count distribution (how many times each strand is sequenced).

### `read_distribution`: `"bernoulli"`

Each strand is either read (coverage copies) or missing.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `p_read` | float | 1.0 | Probability of reading each strand |

### `read_distribution`: `"poisson"`

Read count drawn from Poisson(λ = coverage).

*(No additional keys.)*

### `read_distribution`: `"negative_binomial"`

Read count drawn from NegBin(r, p) parameterized to match target coverage.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `dispersion` | float | 1.0 | Dispersion parameter r |

---

## `header_params`

Parameters for the file-header pipeline (always `BasicHedges`).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `header_strand_length` | int | 32 | Nucleotides per header strand |
| `header_index_bytes` | int | 2 | Index bytes in header strands |

---

## `dna_processing`

DNA-level post-processing filters applied after strand generation.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `min_length` | int | null | Drop strands shorter than this |
| `max_length` | int | null | Drop strands longer than this |
| `gc_min` | float | null | Drop strands below this GC fraction |
| `gc_max` | float | null | Drop strands above this GC fraction |
| `homopolymer_max` | int | null | Drop strands with homopolymer runs longer than this |

---

## `sim_params`

Miscellaneous simulation parameters.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `seed` | int | null | Global random seed (null = unseeded) |
| `verbose` | bool | false | Print progress during simulation |
| `output_dir` | string | `.` | Directory where `fi.pickle` / `fi.stats` are written |

---

## Sweep notation

`generate_fi_jobs.py` expands any parameter value that is a JSON array with a
special first element into a grid of experiments.

| Form | Expands to |
|------|-----------|
| `["value_list", v1, v2, ...]` | One experiment per value |
| `["range", start, stop, step]` | `range(start, stop, step)` — integers |
| `["dir_name", "/base/path", "regexp"]` | Matching subdirectory names under path |
| `["file_name", "/base/path", "regexp"]` | Matching file paths under path |

Sweeps over multiple parameters produce the Cartesian product.

### Example: sweep error rate and coverage

```json
{
  "encoder": "ReedSolomon_Base4",
  "encoder_params": { "strand_length": 32 },
  "fi_env_params": {
    "trials": 5,
    "coverage": ["value_list", 5.0, 10.0, 20.0],
    "file": "examples/small/test_image.png"
  },
  "fault_params": {
    "fault_model": "fixed_rate",
    "error_rate": ["range", 0.01, 0.11, 0.01]
  }
}
```

This generates 3 × 10 = 30 experiments, one directory per combination.
