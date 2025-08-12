import io
import pytest
from collections import Counter
from parsing.bigram_parser import CountBigramOptions, count_bigrams, build_regex

def test_post_init_ignore_all_punctuation():
    options = CountBigramOptions(ignore_all_punctuation=True, include_apostrophes=True, include_hyphens=True, sentence_sensitive=True)
    assert options.include_apostrophes is False
    assert options.include_hyphens is False
    assert options.sentence_sensitive is False

def test_letters_only():
    only_letters = count_bigrams(io.StringIO("a1 b2 c3 123"), CountBigramOptions(letters_only=True))
    assert only_letters == {("a","b"): 1, ("b","c"): 1}

    not_only_letters = count_bigrams(io.StringIO("a1 b2 c3 123"), CountBigramOptions(letters_only=False))
    assert not_only_letters == {("a1","b2"): 1, ("b2","c3"): 1, ("c3", "123"): 1}

def test_case_sensitive():
    insensitive = count_bigrams(io.StringIO("apple Apple apple"), CountBigramOptions(case_sensitive=False))
    assert insensitive == {("apple","apple"): 2}

    sensitive = count_bigrams(io.StringIO("Apple apple Apple"), CountBigramOptions(case_sensitive=True))
    assert sensitive == {("Apple","apple"): 1, ("apple","Apple"): 1}

def test_apostrophes():
    no_apostrophes = count_bigrams(io.StringIO("don't hello couldn't"), CountBigramOptions(ignore_all_punctuation=True, include_apostrophes=True))
    assert ("don't","hello") not in no_apostrophes

    yes_apostrophes = count_bigrams(io.StringIO("don't hello couldn't"), CountBigramOptions(ignore_all_punctuation=False, include_apostrophes=True))
    assert yes_apostrophes == {("don't","hello"): 1, ("hello","couldn't"): 1}

def test_hyphens():
    no_hyphens = count_bigrams(io.StringIO("mother-in-law visits"), CountBigramOptions(ignore_all_punctuation=True, include_hyphens=True))
    assert ("mother-in-law","visits") not in no_hyphens

    yes_hyphens = count_bigrams(io.StringIO("mother-in-law visits"), CountBigramOptions(ignore_all_punctuation=False, include_hyphens=True))
    assert ("mother-in-law","visits") in yes_hyphens

def test_whitespace():
    tabs_whitespace_newlines = count_bigrams(io.StringIO(" a   b\t\tc  \n d \n        e"), CountBigramOptions())
    assert {("a","b"):1, ("b","c"):1, ("c","d"):1, ("d", "e"): 1} == tabs_whitespace_newlines

def test_line_separated():
    text = "a b\nc d"
    no_separation = count_bigrams(io.StringIO(text), CountBigramOptions(ignore_all_punctuation=True, line_separated=False))
    assert ("b","c") in no_separation

    yes_separation = count_bigrams(io.StringIO(text), CountBigramOptions(ignore_all_punctuation=True, line_separated=True))
    assert ("b","c") not in yes_separation
    assert ("a","b") in yes_separation
    assert ("c","d") in yes_separation

def test_no_bigram():
    one_word = count_bigrams(io.StringIO("alone"), CountBigramOptions())
    assert one_word == Counter()

def test_repeated():
    repeating = count_bigrams(io.StringIO("a b a b a"), CountBigramOptions())
    assert repeating == {("a","b"): 2, ("b","a"): 2}

def test_regex_letters_digits(): # Testing config not regex
    options_1 = CountBigramOptions(letters_only=True, case_sensitive=False, ignore_all_punctuation=True)
    r_only_letters = build_regex(options_1)
    assert r_only_letters.fullmatch("abcdef")
    assert not r_only_letters.fullmatch("abcdef1")

    options_2 = CountBigramOptions(letters_only=False, case_sensitive=False, ignore_all_punctuation=True)
    r_letters_digits= build_regex(options_2)
    assert r_letters_digits.fullmatch("abcdef12345")
    assert r_letters_digits.fullmatch("1a1")

