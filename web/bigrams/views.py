import logging
from django.shortcuts import render
from parsing.bigram_parser import count_bigrams, CountBigramOptions

logger = logging.getLogger(__name__)

TOP_N_DEFAULT = 50
TOP_N_MAX = 500
TEXT_MAX_CHARS = 200_000

OPTIONS = [
    ("ignore_all_punctuation", "Ignore punctuation"),
    ("letters_only", "Letters only"),
    ("case_sensitive", "Case sensitive"),
    ("include_apostrophes", "Include apostrophes"),
    ("include_hyphens", "Include hyphens"),
    ("sentence_sensitive", "Sentence sensitive"),
    ("line_separated", "Line separated"),
    ("valid_words", "Valid words"),
]

def index(request):
    ctx = {"options": OPTIONS, "checked_names": set(), "top_n": TOP_N_DEFAULT}
    if request.method != "POST":
        return render(request, "bigrams/index.html", ctx)

    text = (request.POST.get("text") or "").strip()
    if not text:
        ctx["error"] = "Paste text to find bigrams."
        return render(request, "bigrams/index.html", ctx)

    if len(text) > TEXT_MAX_CHARS:
        text = text[:TEXT_MAX_CHARS]

    checked = {name for name, _ in OPTIONS if request.POST.get(name)}
    ctx["checked_names"] = checked
    options = CountBigramOptions(**{name: (name in checked) for name, _ in OPTIONS})

    val = request.POST.get("top_n")
    if val and str(val).strip().isdigit():
        top_n = int(val)
        top_n = 1 if top_n < 1 else (TOP_N_MAX if top_n > TOP_N_MAX else top_n)
    else:
        top_n = TOP_N_DEFAULT
    ctx["top_n"] = top_n

    try:
        counter = count_bigrams(text.splitlines(), options)
    except Exception:
        logger.exception("count_bigrams failed")
        ctx["error"] = "Parsing failed. Try different options or smaller input."
        return render(request, "bigrams/index.html", ctx)

    items = counter.most_common(top_n)
    if items:
        ctx["pairs"] = items
        ctx["labels"] = [f"{a},{b}" for (a, b), _ in items]
        ctx["counts"] = [c for _, c in items]
    else:
        ctx["pairs"] = []
        ctx["notice"] = "No bigrams found."

    return render(request, "bigrams/index.html", ctx)

