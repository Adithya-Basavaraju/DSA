"""
Contains Duplicate (Easy): https://leetcode.com/problems/contains-duplicate/
Pattern: 01 hashing | Variant: Membership / seen set
Started: 2026-10-05

Answer these BEFORE coding (they are what makes the pattern stick):
  Brute force: A naive solution would be for every element, check whether the remaining array contains the same element. This is O(n^2) time and O(1) space. stop when we find a duplicate.
  Signal that pointed to the pattern: We had to keep track of the elements we've seen so far to see if we've seen this element before.
  State / invariant I maintain: We maintain a set of seen elements.
  Nearby pattern that almost works, and why it doesn't: we can sort the array and then check if the adjacent elements are the same. This is O(n log n) time and O(1) space. but it is not O(n) space.
  Time / space: O(n) time and O(n) space.
"""
from typing import *


class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        seen = set()
        for num in nums:
            if num in seen:
                return True
            seen.add(num)
        return False


if __name__ == "__main__":
    s = Solution()
    # Add at least 3 adversarial cases: empty / single element / duplicates / negatives / max size
    assert s.containsDuplicate([1, 2, 3, 4, 5]) == False
    assert s.containsDuplicate([1, 2, 3, 4, 5, 1]) == True
    assert s.containsDuplicate([1, 1, 1, 1, 1]) == True
    assert s.containsDuplicate([-1, -2, -3, -4, -5]) == False
    assert s.containsDuplicate([1000000000, 1000000000]) == True
    assert s.containsDuplicate([]) == False
    assert s.containsDuplicate([7]) == False
    print("ok")

# --- Follow-ups (from review, 2026-10-05) ---
# TODO: header: brute force = for each element, check if the remaining array contains the same element (O(n^2));
#       near miss = sort + walk with two pointers (O(n log n), less memory); time/space = O(n log n) / O(1) (if stable sort).
