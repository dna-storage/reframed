# Output Schema

This document describes every key written by `tools/fault_injection.py` into `fi.pickle`
and `fi.stats`, and the column naming conventions used by `tools/data_analysis/db_gen.py`
when building the aggregated Pandas DataFrame.

---

## Per-experiment output files

Each experiment leaf directory contains:

| File | Format | Description |
|------|--------|-------------|
| `fi.pickle` | Python `dict` (pickle) | All stats for this experiment |
| `fi.stats` | Plain text | Human-readable summary of same stats |
| `encoder.json` | JSON | Pipeline / encoder parameters |
| `fi_env.json` | JSON | Fault-injection environment parameters |
| `fault.json` | JSON | Fault model parameters |
| `distribution.json` | JSON | Read-distribution parameters |
| `header.json` | JSON | Header pipeline parameters |

---

## `fi.pickle` — core keys

These keys are written directly by `fault_injection.py`.

| Key | Type | Description |
|-----|------|-------------|
| `total_encoded_strands` | int | Number of strands produced by the encoder |
| `header_strand_length` | int | Nucleotides per header strand |
| `payload_strand_length` | int | Nucleotides per payload strand |
| `dead_header` | int | 1 if the header could not be decoded, else 0 |
| `file_size_bytes` | int | Size of the input file in bytes |
| `total_file_data_bytes` | int | Bytes successfully decoded |
| `total_strands_analyzed` | int | Strands passed to the decoder |
| `total_mismatch_bytes` | int | Bytes that differ between input and output |
| `file_size_difference_bytes` | int | `abs(decoded_size − original_size)` |
| `error` | int | 1 if any decoding error occurred, else 0 |

### Derived metrics

These can be computed from the core keys after loading `fi.pickle`:

| Metric | Formula |
|--------|---------|
| Bit error rate (BER) | `total_mismatch_bytes * 8 / (file_size_bytes * 8)` |
| Byte error rate | `total_mismatch_bytes / file_size_bytes` |
| Decoding success | `1 - error` |

---

## `fi.pickle` — probe keys

Probes are optional instrumentation components inserted into the pipeline.
Their keys follow the pattern `{probe_name}::{metric}`.

### `DNAErrorProbe` — per-position edit distance

| Key pattern | Description |
|-------------|-------------|
| `{name}::total_edit_errors` | Total edit distance across all strands |
| `{name}::insertion_edit_errors` | Edit distance attributed to insertions |
| `{name}::deletion_edit_errors` | Edit distance attributed to deletions |
| `{name}::substitution_edit_errors` | Edit distance attributed to substitutions |
| `{name}::total_strands` | Strands observed by this probe |

### `CodewordErrorRateProbe` — codeword-level accuracy

| Key pattern | Description |
|-------------|-------------|
| `{name}::total_strands` | Strands processed |
| `{name}::correct_strands` | Strands decoded without error |
| `{name}::incorrect_strands` | Strands with at least one error |
| `{name}::total_errors` | Aggregate error count across all strands |

### `IndexDistribution` — strand index histograms

| Key pattern | Description |
|-------------|-------------|
| `{name}::index_dist_encode` | Dict mapping index → encode count |
| `{name}::index_dist_decode` | Dict mapping index → decode count |
| `{name}::total_indexes_encode` | Total strands seen at encode |
| `{name}::total_indexes_decode` | Total strands seen at decode |

### `FilteredDNACounter` — dropped strands

| Key pattern | Description |
|-------------|-------------|
| `{name}::filtered_strand` | Number of strands dropped by this filter |

---

## DataFrame columns (`db_gen.py`)

`tools/data_analysis/db_gen.py` walks a results tree, loads every `fi.pickle`,
and merges it with its JSON config files into a single Pandas DataFrame.

### Column prefixes

| Prefix | Source |
|--------|--------|
| `encoder::` | `encoder.json` keys |
| `header::` | `header.json` keys |
| *(none)* | All `fi.pickle` keys (no prefix) |
| *(none)* | `fi_env.json`, `fault.json`, `distribution.json` keys (no prefix) |

### Example columns

```
encoder::encoder
encoder::strand_length
encoder::index_bytes
encoder::rs_outer_distance
fault_model
error_rate
coverage
total_encoded_strands
total_mismatch_bytes
file_size_bytes
error
```

### Loading the DataFrame

```python
import pickle, pandas as pd

with open("fault_injection_dataframe.pickle", "rb") as f:
    df = pickle.load(f)

# Bit error rate
df["ber"] = df["total_mismatch_bytes"] * 8 / (df["file_size_bytes"] * 8)

# Group by error rate, summarize
print(df.groupby("error_rate")[["ber", "error"]].mean())
```

### Using `quick_analyze.py`

For quick summaries without writing custom analysis code, use:

```bash
python tools/quick_analyze.py <results_dir> --group error_rate coverage
```

See `python tools/quick_analyze.py --help` for all options.
