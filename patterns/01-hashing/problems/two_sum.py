"""
Two Sum (Easy): https://leetcode.com/problems/two-sum/
Pattern: 01 hashing | Variant: Complement lookup
Started: 2026-10-06

Answer these BEFORE coding (they are what makes the pattern stick):
  Brute force: 
    - O(n^2) time, O(1) space
    - iterate through all pairs of numbers and check if they sum to the target
  Signal that pointed to the pattern: We can use a hasmap and check if the complement exists in the map.
  State / invariant I maintain: 
  Nearby pattern that almost works, and why it doesn't: We can use a two pointer approach to find the two numbers that sum to the target.
  Time / space: O(n) time, O(n) space
"""
from typing import *


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
      seen = {}
      for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
          return [seen[complement], i]
        seen[num] = i
      return []


if __name__ == "__main__":
    s = Solution()
    # Add at least 3 adversarial cases: empty / single element / duplicates / negatives / max size
    # assert s.twoSum(...) == ...
    assert s.twoSum([2,7,11,15], 9) == [0,1]
    assert s.twoSum([3,2,4], 6) == [1,2]
    assert s.twoSum([3,3], 6) == [0,1]
    assert s.twoSum([], 0) == []
    print("PASS")

# TODO (2026-10-06, review):
# TODO 1: fill in the invariant: what is true about `seen` at the moment you look at index i?
# TODO 2: rewrite the signal as words from the PROBLEM, not the solution. "Use a hashmap" is the approach;
#         the signal is what in the statement told you to use it.
# TODO 3: finish the near-miss line with the "why it doesn't". What does sorting do to the answer you must return?
# TODO 4: add a negatives/zero test, e.g. a pair that only exists using a negative number.
