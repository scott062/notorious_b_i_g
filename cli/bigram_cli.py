import sys
import shutil
import io
import typer

from collections import Counter
from typing import List

from parsing.bigram_parser import CountBigramOptions, count_bigrams


app = typer.Typer()

def ask_yes_no(prompt, default):
    while True:
        # TO-DO: Show defaults in prompt
        ans = input(f"{prompt} y/n: ").strip().lower()
        if ans == "":
            return default
        if ans == "y":
            return True
        if ans == "n":
            return False
        typer.echo("Please answer 'y' or 'n'.")

@app.command(help="Count bigrams from files or stdin. Use -i for interactive mode.")
def run(
    hist: bool = typer.Option(False, help="Show a bar chart of bigrams."),
    top: int = typer.Option(50, help="Show top # results."),

    # TO-DO: Clean up repeated options structure for typer and parser and interactive options
    # TO-DO: Re-think cascading relationships of punc
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive helper."),
    paths: List[typer.FileText] = typer.Argument(None, help="Files to read, or read from stdin."),
    letters_only: bool = typer.Option(True, help="Only letters."),
    ignore_all_punctuation: bool = typer.Option(True, help="Strip all punctuation."),
    include_apostrophes: bool = typer.Option(False, help="Keep apostrophes within words."),
    include_hyphens: bool = typer.Option(False, help="Keep hyphens within words."),
    sentence_sensitive: bool = typer.Option(False, help="Reset bigram sequence across sentences."),
    line_separated: bool = typer.Option(False, help="Reset bigram sequence at newline."),
):
    options = CountBigramOptions(
        letters_only=letters_only,
        ignore_all_punctuation=ignore_all_punctuation,
        include_apostrophes=include_apostrophes,
        include_hyphens=include_hyphens,
        sentence_sensitive=sentence_sensitive,
        line_separated=line_separated,
    )
    # TO-DO: Break out interactive from file inputs in code
    if interactive:
        typer.echo("Enter empty line to quit.")

        q_letters = ask_yes_no("Only letters?", letters_only)
        q_punctuation = ask_yes_no("Remove all punctuation?", ignore_all_punctuation)

        if q_punctuation:
            typer.echo("***punctuation removed*** apostrophes, hyphens, and sentence markings are ignored.")
            q_apostrophe = False
            q_hyphen = False
            q_sentence = False
        else:
            q_apostrophe = ask_yes_no("Keep apostrophes inside words ex. don't?", include_apostrophes)
            q_hyphen = ask_yes_no("Keep hyphens inside words ex. mother-in-law?", include_hyphens)
            q_sentence = ask_yes_no("Bigrams across sentences?", sentence_sensitive)

        options = CountBigramOptions(
            letters_only=q_letters,
            ignore_all_punctuation=q_punctuation,
            include_apostrophes=q_apostrophe,
            include_hyphens=q_hyphen,
            sentence_sensitive=q_sentence,
        )

        typer.echo("\nType a line of text to find bigrams.\n")
        while True:
            try:
                text = input("bigrams>> ")
            except EOFError:
                break
            if not text.strip():
                break
            counts = count_bigrams(io.StringIO(text), options)
            if not counts:
                typer.echo("**no data**")
                continue
            for (a, b), c in counts.most_common():
                typer.echo(f"({a}, {b}): {c}")
        raise typer.Exit(code=0)

    total: Counter = Counter()
    if not paths and sys.stdin.isatty():
        typer.echo("Use -i, or provide file input(s).", err=True)
        raise typer.Exit(code=2)

    if paths: # Maintain totals for multi files
        for f in paths:
            with f:
                total.update(count_bigrams(f, options))
    else:
        total.update(count_bigrams(sys.stdin, options))

    items = total.most_common(top or None)
    if hist:
        print_histogram(items)
    else:
        for (a, b), c in items:
            typer.echo(f"({a}, {b}): {c}")


# TO-DO: Migrate to rich dependency b/c this sucks, maybe another visualization file
def print_histogram(items, max_label=20):
    if not items:
        return typer.echo("*** no data ***")

    items.sort(key=lambda x: x[1], reverse=True)
    term_width = shutil.get_terminal_size(fallback=(80, 20)).columns
    label_width = min(max_label, max(len(f"{a},{b}") for (a, b), _ in items))
    bar_width = max(10, term_width - label_width - 6) # 6 is for the formatting and necessary counts (will break on very large counts > 5 digits)
    max_count = max(c for _, c in items) # Scaling factor - should be 100% of screen, everything else moves around this and 0 count of course

    for (a, b), c in items: # Counter dict -  c is counts
        label = f"{a},{b}"
        if len(label) > label_width:
            label = label[:label_width - 3] + "..." # Truncating long labels for clarity TO-DO: Alt solution for expanding labels
        n = bar_width if c == max_count else max(1 if c > 0 else 0, round(c / max_count * bar_width)) # Calc how many symbols
        typer.echo(f"{label.ljust(label_width)} | {'#' * n} {c}")

def main():
    app()

if __name__ == "__main__":
    main()

