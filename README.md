# Notorious BIGram Parser

A small tool for counting bigrams from text inputs or file(s). Includes:
- **CLI** (Typer) with an ASCII histogram
- **Django UI** with a Chart.js bar chart
- tests for the core logic

### Requirements
- Python 3.11+
- Virtualenv (`uv` or `pip`)

### Setup
```bash
# from project root
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

## Project layout
```
Important Directories
cli/     # CLI app (Typer)
parsing/ # core logic
tests/   # pytest for parsing
web/     # Django UI
```

## CLI

### Run
Using Files:
```bash
uv run python -m cli.bigram_cli --hist file/path/here
```
or (interactive):
```bash
uv run python -m cli.bigram_cli --interactive
```
or (piped):
```bash
echo "YOUR TEXT HERE" | PYTHONPATH=. uv run python -m cli.bigram_cli --hist
```
ex (use any or all 3 possible samples):
```bash
uv run python -m cli.bigram_cli --hist ./samples/crime_and_punish.txt ./samples/pride_and_prej.txt ./samples/moby_dick.txt
```

**Inputs**
- `FILES` = one or more text files; counts are aggregated
- No files → reads from stdin
- No files and no stdin → exits

**Core options**
- `--hist` -> show a simple bar chart
- `--top INT` (default: 50) -> limit to top N
- `-i, --interactive` -> prompt to toggle parsing

**Parsing flags**
- `--letters-only / --no-letters-only` (default: **true**)
  keep only A–Z letters
- `--ignore-all-punctuation / --no-ignore-all-punctuation` (default: **true**)
  strip all punctuation
- `--include-apostrophes` (default: **false**)
  keep apostrophes inside words: `don't`
- `--include-hyphens` (default: **false**)
  keep hyphens inside words: `mother-in-law`
- `--sentence-sensitive` (default: **false**)
  reset bigram sequence at sentence end
- `--line-separated` (default: **false**)
  reset bigram sequence at each newline

### What the histogram does
- Fits to your terminal width.
- Long labels are condensed.
- The max count fills the bar; others are scaled proportionally.

## Django UI

### Run
```bash
cd web
python manage.py migrate
python manage.py runserver
# Accss at localhost -> http://127.0.0.1:8000/
```

### Features
- Paste text, parser options, choose **Top N** results.
- Chart.js bar chart + simple table.
- **Valid Words WIP**
<img width="2517" height="1252" alt="image" src="https://github.com/user-attachments/assets/37574765-8256-4eb6-80f8-637ad9c714a5" />

## Parser

`parsing/bigram_parser.py`

- `count_bigrams(lines, options)`
  Iterates per line (and per sentence, if enabled), forms `(prev, word)` bigrams.
- `CountBigramOptions` fields:
  - `ignore_all_punctuation`
  - `letters_only`
  - `case_sensitive`
  - `include_apostrophes`
  - `include_hyphens`
  - `sentence_sensitive`
  - `line_separated`
  - `valid_words` ***WIP***

Return shape is a `Counter`, the ui calls `.most_common()` and renders.

## Testing

```bash
pytest
```

## Limitations

- the CLI histogram truncates the count column visually if terminal is very narrow.
- UI is textarea-only (no file upload yet). Use CLI for file parsing.
- No DB models or caches; results aren’t saved between requests.

