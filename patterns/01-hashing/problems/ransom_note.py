"""
Ransom Note (Easy): https://leetcode.com/problems/ransom-note/
Pattern: 01 hashing | Variant: Frequency counting
Started: 2026-10-05

Answer these BEFORE coding (they are what makes the pattern stick):
  Brute force: Naive solution would be to convert them to lists and then check if the second list contains the first list. This is O(n) time and O(n) space.
  Signal that pointed to the pattern: We need to keep track of the frequency of each character in the ransom note and the magazine to see if we can construct the ransom note.
  State / invariant I maintain: fill the frequency dictionaries for the ransom note and the magazine. then check if the frequency of each character in the ransom note is less than or equal to the frequency of the same character in the magazine.
  Nearby pattern that almost works, and why it doesn't: Not sure
  Time / space:
"""
from typing import *


class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        freq_ransom = {}
        freq_magazine = {}
        for char in ransomNote:
            freq_ransom[char] = freq_ransom.get(char, 0) + 1
        for char in magazine:
            freq_magazine[char] = freq_magazine.get(char, 0) + 1
        for char in freq_ransom:
            if char not in freq_magazine or freq_ransom[char] > freq_magazine[char]:
                return False
        return True


if __name__ == "__main__":
    s = Solution()
    # Add at least 3 adversarial cases: empty / single element / duplicates / negatives / max size
    # assert s.method(...) == ...
    assert s.canConstruct("a", "b") == False
    assert s.canConstruct("a", "ab") == True
    assert s.canConstruct("aa", "aab") == True
    assert s.canConstruct("aa", "ab") == False
    assert s.canConstruct("aa", "a") == False
    assert s.canConstruct("aa", "aa") == True
    assert s.canConstruct("aa", "aaa") == True
    assert s.canConstruct("aa", "aaaa") == True
    print("ok")

# --- Follow-ups (from review, 2026-10-05) ---
# TODO 1: header: brute force = for each char in note, find & remove it from a list of magazine chars (O(n*m));
#         near miss = sort both + walk with two pointers (O(n log n), less memory); time/space = O(n+m) / O(1) (26 letters).
# TODO 2: add test: canConstruct("", "abc") == True (empty note).
# TODO 3 (optional): rewrite with ONE counter: build from magazine, decrement per note char, fail when it goes below 0.
