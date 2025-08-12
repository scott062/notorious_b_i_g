import io
import re
import string
from collections import Counter
from dataclasses import dataclass

SENTENCE_SPLIT_REGEX = re.compile(r"[.!?]+") # TO-DO: Enhance with actual NLP tokenization to better determine false positives like: Mr., Mrs., etc., .com
WHITE_SPACE_REGEX = re.compile(r"\s+")
PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation) # Covers all ASCII punctuation

@dataclass
class CountBigramOptions:
    letters_only: bool = True # a-z only - ignore other chars like numbers
    ignore_all_punctuation: bool = True # Remove all punctuation from text
    case_sensitive: bool = False # Distinguish bigrams as uppercase and lowercase; A-Z vs a-z
    include_apostrophes: bool = False # dont vs don't
    include_hyphens: bool = False # Parse hyphenated word as single word
    sentence_sensitive: bool = False # Whether to include bigrams as beginning of one sentence and the end of the last sentence
    line_separated: bool = False # Whether a new line resets the bigram count (extensibility with csv)
    valid_words: bool = False # Check chars against English dictionary

    def __post_init__(self):
        if self.ignore_all_punctuation:
            self.include_apostrophes = False
            self.include_hyphens = False
            self.sentence_sensitive = False


def preprocess(text, options):
    if not options.case_sensitive:
        text = text.lower()
    if options.ignore_all_punctuation:
        text = _remove_punctuation(text)
    text = _remove_whitespace(text)
    return text


def count_bigrams(lines, options):
    counts = Counter()
    re_pattern = build_regex(options)
    previous_word = None # Keep track of latest word

    for line in lines:
        if options.line_separated: # Reset bigram with new line
            previous_word = None

        line = preprocess(line, options)
        if options.sentence_sensitive:
            sentences = SENTENCE_SPLIT_REGEX.split(line)
        else:
            sentences = [line]

        for sentence in sentences:
            for match in re_pattern.finditer(sentence):
                word = match.group(0)
                if previous_word is not None:
                    counts[(previous_word, word)] += 1
                previous_word = word

            if options.sentence_sensitive:
                previous_word = None

    return counts


def build_regex(options):
    pattern = ""
    if options.letters_only:
        pattern = "[A-Za-z]" if options.case_sensitive else "[a-z]" # Only letters
    else:
        pattern = "[A-Za-z0-9]" if options.case_sensitive else "[a-z0-9]" # Only letters & numbers

    word_pattern = ""
    if options.include_apostrophes: # Include match for apostrophe ex. don't
        word_pattern += "'"
    if options.include_hyphens: # Include match for hyphenated word ex. mother-in-law
        word_pattern += "-"

    if word_pattern:
        final = fr"{pattern}+(?:[{word_pattern}]{pattern}+)*"
    else:
        final = fr"{pattern}+"

    return re.compile(final)


def _remove_punctuation(text_input):
    return text_input.translate(PUNCTUATION_TABLE)

def _remove_whitespace(text_input):
    return WHITE_SPACE_REGEX.sub(" ", text_input).strip()

