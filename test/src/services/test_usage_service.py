import pytest

from src.services.usage_service import TextCreditsCalculator, get_words_from_text, SCALING_FACTOR

@pytest.mark.parametrize("text,expected", [
    ("Abc abc abc'", ["Abc", "abc", "abc'"]),
    ("1234 1123", []),
    ("Abc1234abc", ["Abc", "abc"]),
    ("What are the landlord's obligations in the event of property damage due to fire or other disasters?", [
        "What", "are", "the", "landlord's", "obligations", "in", "the", "event", "of", "property", "damage", "due", "to", "fire", "or", "other", "disasters"
    ])
])
def test_get_words_from_text(text: str, expected: list[str]):
    words_generator = get_words_from_text(text)
    assert list(words_generator) == expected

@pytest.mark.parametrize("text,expected", [
    ("abc cba", True),
    ("abccba", True),
    ("1234abccba4321", True),
    ("", False),
    ("!a!b!ccba", True),
    ("!!!!!!!!", True),
    ("ab", False)
])
def test_is_palindrome(text: str, expected: bool):
    assert TextCreditsCalculator.is_palindrome(text) == expected

@pytest.mark.parametrize("text,expected",[
        ("This is a test", True),
        ("This is a test test", False),
        ("", False)
    ]
)
def test_should_give_word_bonus(text: str, expected: bool):
    words = list(get_words_from_text(text))
    assert TextCreditsCalculator.should_give_unique_word_bonus(words) == expected

@pytest.mark.parametrize("word,expected",[
        ("aa", 0),
        ("aaa", 30),
        ("aab", 0),
        ("bbb", 0),
        ("aaaaaa", 60)
    ]
)
def test_get_word_third_vowel_cost(word: str, expected: float):
    assert TextCreditsCalculator.get_word_third_vowel_cost(word) == expected

@pytest.mark.parametrize("word,expected", [
    ("abc", 10),
    ("aba", 40),
    ("abcde", 20),
    ("bbbbbbbb", 30)
])
def test_get_word_cost(word: str, expected: float):
    assert TextCreditsCalculator.get_word_cost(word) == expected


def test_compute_text_is_palindrome():
    """
        The palindrome one should cost twice the amount that the non palindrome one costs
    """
    text_palindrome = "bbbbbbccccccbbbbbb"
    text_non_palindrome = "bbbbbbccccccbbbbbc"
    assert TextCreditsCalculator.compute(text_non_palindrome) * 2 == TextCreditsCalculator.compute(text_palindrome)

    text_palindrome = "aaa bbb aaa"
    text_non_palindrome = "aaa cbb aaa"
    assert TextCreditsCalculator.compute(text_non_palindrome) * 2 == TextCreditsCalculator.compute(text_palindrome)
 

def test_compute_len_penalty():
    word_not_exceeding = "a" * 100
    word_exceeding = "a" * 101

    difference = TextCreditsCalculator.compute(word_exceeding) - TextCreditsCalculator.compute(word_not_exceeding)
    assert difference >= TextCreditsCalculator.LEN_PENALTY / SCALING_FACTOR

def test_unique_words_bonus():
    non_unique = "aaa bbb aaa ccc " + "e" * 100
    unique = "aaa bbb eee ccc " + "e" * 100

    diff = TextCreditsCalculator.compute(non_unique) - TextCreditsCalculator.compute(unique)
    assert diff == TextCreditsCalculator.UNIQUE_WORD_BONUS / SCALING_FACTOR

def test_base_cost():
    assert TextCreditsCalculator.compute("") == 1, "Should be the base cost"