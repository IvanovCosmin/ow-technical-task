from dataclasses import dataclass
from typing import Iterable
from pydantic import BaseModel
from src.repositories.usage_repo import MessageWithReport, UsageRepo
import re


class UsageResult(BaseModel):
    message_id: int
    timestamp: str
    report_name: str | None
    credits_used: float

def get_words_from_text(text: str):
    def _is_part_of_word(char: str):
       return char.isalpha() or char in ["'", "‘" "-"]

    start_of_word = None
    for idx, char in enumerate(text):
        # the backtick from notion is U+2018 which looks strange
        # I am going to go with the normal ' as well which is U+0027
        if _is_part_of_word(char):
            if start_of_word is None:
                start_of_word = idx
        else:
            if start_of_word is not None:
                yield text[start_of_word:idx]
                start_of_word = None
    if start_of_word is not None:
        yield text[start_of_word:]



# Scaling factor is used to get rid of all the floating point erorrs
SCALING_FACTOR = 100
class TextCreditsCalculator:
    BASE_COST = 1 * SCALING_FACTOR
    CHAR_COST = 0.05 * SCALING_FACTOR
    THIRD_VOWEL_COST = 0.3 * SCALING_FACTOR

    LEN_PENALTY = 5 * SCALING_FACTOR
    UNIQUE_WORD_BONUS = 2 * SCALING_FACTOR

    @dataclass
    class WordLenMultiplier:
        LESS_EQ_THAN_3 = 0.1 * SCALING_FACTOR
        LESS_EQ_THAN_7 = 0.2 * SCALING_FACTOR
        MORE_THAN_8 = 0.3 * SCALING_FACTOR

    @classmethod
    def compute(cls, text: str):
        words = list(get_words_from_text(text))
        cost = sum(
            [
                cls.BASE_COST,
                cls.CHAR_COST * len(text), # assuming spaces are chars,
                cls.LEN_PENALTY if len(text) > 100 else 0,
                *[cls.get_word_cost(word) for word in words],
                -1 * cls.UNIQUE_WORD_BONUS if cls.should_give_unique_word_bonus(words) else 0 
            ]
        )

        is_palindrome_multiplier = 2 if cls.is_palindrome(text) else 1

        return is_palindrome_multiplier * max(1, cost) / SCALING_FACTOR # the total cost should be >= 1 

    @staticmethod
    def is_palindrome(text: str):
        """
        If the entire message is a palindrome
        (that is to say, after converting all uppercase 
        letters into lowercase letters and removing all
        non-alphanumeric characters, it reads the same 
        forward and backward),
        """
        text_only_alpha_num = re.sub(r'[^a-zA-Z0-9]', '', text)
        text_only_alphnum_lowered = text_only_alpha_num.lower()
        if len(text) == 0:
            # decided not to give the bonus to empty texts, but will do for things such as "!!"
            # this may be pretty bad, as it opens a lot of cans of worms
            # at the same time, it would be weird to give cost 2 for empty string, and a lower cost
            # to "ab"
            return False 
        return text_only_alphnum_lowered[:] == text_only_alphnum_lowered[::-1]

    @staticmethod
    def should_give_unique_word_bonus(words: list[str]):
        # decided not to give empty word list the bonus
        return len(words) == len(set(words)) and len(words) > 0           

    @classmethod
    def get_word_length_multiplier(cls, word: str):
        word_len = len(word)
        if word_len <= 3:
            return cls.WordLenMultiplier.LESS_EQ_THAN_3
        if word_len <= 7:
            return cls.WordLenMultiplier.LESS_EQ_THAN_7
        return cls.WordLenMultiplier.MORE_THAN_8

    @classmethod
    def get_word_third_vowel_cost(cls, word: str):
        cost = 0
        # starting at 3rd and iterating every 3
        if len(word) < 3:
            return 0
        
        for char in word[2::3]:
            if char.lower() in ['a', 'e', 'i', 'o', 'u']:
                cost += cls.THIRD_VOWEL_COST
        return cost

    

    @classmethod
    def get_word_cost(cls, word: str):
        return sum(
            [
                # This multiplier is weird. It should multiply something, right?
                cls.get_word_length_multiplier(word),
                cls.get_word_third_vowel_cost(word),
            ]
        )

class UsageService():
    def __init__(self, usage_repo: UsageRepo) -> None:
        # here we are communicating with an external service
        # it is good to do dependency injection as in a real setting we
        # will need at least a way to run tests (such as creating a MockUsageRepo)
        self._usage_repo = usage_repo
    
    async def get_usage(self) -> Iterable[UsageResult]:
        messages = await self._usage_repo.get_current_period_with_reports()
        results: list[UsageResult] = []
        if messages is None:
            return []
        
        for message in messages:
            results.append(
                UsageResult(
                    message_id=message.id,
                    timestamp=message.timestamp,
                    report_name=message.report.name if message.report else None,
                    credits_used=self.compute_credits_for_message(message)
                )
            )

        return results

    @classmethod
    def compute_credits_for_message(cls, message: MessageWithReport):
        if message.report is not None:
            return message.report.credit_cost
        return cls.compute_credits_for_text(message.text)
    
    @staticmethod
    def compute_credits_for_text(text: str):
        return TextCreditsCalculator.compute(text)