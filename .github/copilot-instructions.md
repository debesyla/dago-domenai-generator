# Dago Domain Generator - AI Coding Agent Instructions

## Project Purpose
Multi-strategy domain name generator for research and availability analysis. Produces `.txt` output files with domain lists that feed downstream analysis tools.

## Architecture Overview

**Core Principle**: Pluggable generator strategy pattern. Each generator implements the same interface but uses different algorithms:

```
main.py (CLI entry point)
├── markov_generator.py    → Character-level n-gram chains trained on corpus
├── brute_generator.py     → Exhaustive character combinations (itertools.product)
├── pattern_generator.py   → Regex-like pattern expansion
└── random_generator.py    → Weighted random combinations
```

**Data Flow**: Generator → output `.txt` file → external tools (WHOIS, availability checkers)

## Key Implementation Patterns

### 1. Generator Contract
Each generator should:
- Accept configurable parameters (e.g., `--order 3`, `--min 2 --max 4`)
- Implement a `generate()` method returning a generator/iterator (memory efficient)
- Support output to file via `generate_to_file(filepath)` for large result sets
- Include `estimate_count()` for progress tracking before generation starts
- Never load entire result set into memory

**Example**: Markov generator yields domains one-at-a-time; brute generator uses `itertools.product` with lazy evaluation.

### 2. Markov Chain Design (from `docs/MARKOV_IDEA.md`)
- **Order**: 3 (trigrams) is standard balance between randomness and pronounceability
- **Model Format**: Dict of dicts `{prefix_state: {next_char: count, ...}, ...}`
- **Scoring**: Log-likelihood per generated domain for quality filtering
- **Training**: Clean labels (lowercase, remove TLDs, validate length 2-63), add `^`/`$` boundary tokens
- **Deduplication**: Use Bloom filter for large sets (avoid loading full list into memory)

### 3. Brute Force Design (from `docs/BRUTE_FORCE_IDEA.md`)
- **Character Sets**: Letters, numbers, alphanumeric (stored in `CHARACTER_SETS` dict)
- **Hyphen Modes**: `'with'` (default, includes `-`), `'without'` (excludes), `'only'` (requires `-`)
- **Validation Rules**: Cannot start/end with hyphen, no `--` sequences, max 63 chars per label
- **Core Algorithm**: `itertools.product(charset, repeat=length)` for combinations
- **Count Estimation**: `len(charset) ** length` before generation begins

## Critical Files & Their Roles

| File | Responsibility |
|------|---|
| `src/main.py` | CLI dispatcher, argument parsing, generator selection |
| `src/generators/markov_generator.py` | Markov training & generation |
| `src/generators/brute_generator.py` | Exhaustive combinations |
| `src/utils/io_utils.py` | Batch file I/O to prevent memory overflow |
| `src/utils/progress_utils.py` | Console progress bars with ETA |
| `docs/OVERVIEW.md` | Full architecture & folder structure |
| `docs/MARKOV_IDEA.md` | Detailed Markov algorithm & training |
| `docs/BRUTE_FORCE_IDEA.md` | DNS validation rules & hyphen handling |

## Developer Workflows

### Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for testing & linting
```

### Testing
```bash
pytest tests/
flake8 src/
mypy src/
```

### Adding a New Generator
1. Create `src/generators/new_generator.py`
2. Implement: `generate()` (yields domains), `generate_to_file(path)`, `estimate_count()`
3. Add to generator registry in `main.py`
4. Create tests in `tests/test_new.py`

## Project-Specific Conventions

- **Output Format**: UTF-8 encoded `.txt` files, one domain per line (no TLD by default, unless specified in output file naming)
- **Generator Parameters**: Use consistent CLI flags (`--order`, `--min`, `--max`, `--count`, `--charset`, `--output`)
- **Memory Strategy**: Never load full result set; use generators/iterators and batch file writes
- **Error Handling**: Validate input corpus quality; warn on rejected domains during training
- **Progress Reporting**: Always show count estimates + progress bars for operations >1000 domains

## Integration Points

- **Input**: Domain corpus files in `/assets/input/` (145k real_domains.txt is primary training corpus)
- **Output**: Generated lists in `/assets/output/` (consumed by external analysis tools via `cat` / sort / uniq)
- **External Dependencies**: Only Python stdlib (collections, itertools, pickle, re) for core generation; pytest/flake8/mypy for dev

## Assumptions & Constraints

- Python 3.8+ required
- Single-threaded generation (for reproducibility and simplicity)
- Output files assumed to be relatively small enough for post-processing (`sort | uniq`)
- Domain analysis tools consume `.txt` input only
- No persistence of intermediate state (models can be retrained or regenerated)

## Common Pitfalls to Avoid

1. **Loading entire result set into memory** → Always use generators/batch writes
2. **Forgetting hyphen validation in brute mode** → DNS rules require checking start/end/consecutive hyphens
3. **Markov model not normalizing probabilities** → Use `Counter` for weighted random sampling
4. **Missing progress updates for long operations** → Use `progress_utils` for user feedback
5. **Assuming lowercase-only domains** → Numbers & hyphens allowed; validate per DNS spec
