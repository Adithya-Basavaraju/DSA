"""
Valid Anagram (Easy): https://leetcode.com/problems/valid-anagram/
Pattern: 01 hashing | Variant: Frequency comparison
Started: 2026-10-05

Answer these BEFORE coding (they are what makes the pattern stick):
  Brute force: Naive solution would be to sort the strings and check if they are equal. This is O(n log n) time and O(n) space depending on the sorting algorithm. with a initial check for length equality.
  Signal that pointed to the pattern: We had to keep track of the frequency of each character in the strings to see if they are equal.
  State / invariant I maintain: fill the frequency dictionaries for s and t. then check if they are equal. if they are not, they are not anagrams. if they are, they are anagrams.
  Nearby pattern that almost works, and why it doesn't: We could have sorted the strings and then checked if they are equal. This is O(n log n) time and O(n) space. but it is not O(1) space.
  Time / space: O(n) time and O(n) space.
"""
from typing import *


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        freq_s = {}
        freq_t = {}
        for i in range(len(s)):
            freq_s[s[i]] = freq_s.get(s[i], 0) + 1
            freq_t[t[i]] = freq_t.get(t[i], 0) + 1
        return freq_s == freq_t


if __name__ == "__main__":
    s = Solution()
    # Add at least 3 adversarial cases: empty / single element / duplicates / negatives / max size
    assert s.isAnagram("", "") == True
    assert s.isAnagram("a", "a") == True
    assert s.isAnagram("ab", "ba") == True
    assert s.isAnagram("abc", "cba") == True
    assert s.isAnagram("abc", "abcd") == False
    assert s.isAnagram("abc", "ab") == False
    assert s.isAnagram("abc", "abcde") == False
    assert s.isAnagram("abc", "abcc") == False
    assert s.isAnagram("rat", "car") == False
    assert s.isAnagram("aab", "abb") == False
    print("ok")

# --- Follow-ups (from review, 2026-10-05) ---
# TODO: header brute force is still sorting; the true brute force is "for each char in s, find & remove it from t" (O(n^2)).
