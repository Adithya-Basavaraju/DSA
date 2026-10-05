"""01 · Hash lookup / frequency / grouping: core primitives.

Write these yourself once you understand the pattern. Later, reproduce them from a
BLANK file with `./dsa cold hashing` (no peeking at this file).

To write:
  - frequency counter (dict / Counter)
  - complement map (Two Sum style: check BEFORE insert)
  - group-by-signature (canonical key -> list)
"""

from collections import Counter, defaultdict


# --- 1. Frequency counter ---
def frequency(items):
    """value -> count. Two-pass: build, then query."""
    return Counter(items)
    # or:
    # freq = {}
    # for x in items:
    #     freq[x] = freq.get(x, 0) + 1
    # return freq


# --- 2. Complement map (Two Sum style) ---
def two_sum(nums, target):
    """Check BEFORE insert — never match an element with itself."""
    seen = {}  # value -> index
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i  # record AFTER the check
    return []


# --- 3. Group-by-signature ---
def _anagram_key(w: str) -> tuple:
    """26-count tuple: O(k) to build, vs O(k log k) for sorted(w)."""
    counts = [0] * 26
    for c in w:
        counts[ord(c) - ord("a")] += 1
    return tuple(counts)


def group_by_signature(words):
    """canonical key -> list. Key must be hashable (str/tuple, not list)."""
    groups = defaultdict(list)
    for w in words:
        groups[_anagram_key(w)].append(w)
    return list(groups.values())


# --- 4. Count pairs with difference k ---
def count_pairs_with_diff(nums, k):
    """Count pairs i < j with nums[j] - nums[i] == k.

    Same check-then-record skeleton as two_sum, but the map stores value -> COUNT
    seen so far (one left value can pair with many later rights).
    """
    seen = {}  # value -> count so far
    pairs = 0
    for x in nums:
        # look for earlier y where x - y == k  =>  y == x - k
        pairs += seen.get(x - k, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs


if __name__ == "__main__":
    # two_sum edge cases
    assert two_sum([5, 5], 10) == [0, 1]
    assert two_sum([], 1) == []
    assert two_sum([1, 2, 3], 100) == []

    # group_by_signature (26-count key)
    groups = group_by_signature(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert sorted(sorted(g) for g in groups) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]

    # count_pairs_with_diff
    assert count_pairs_with_diff([1, 5, 3, 5], 2) == 2
    assert count_pairs_with_diff([1, 2, 3, 4], 1) == 3  # (1,2),(2,3),(3,4)
    assert count_pairs_with_diff([1, 1, 1], 0) == 3  # C(3,2) via running counts

    print("ok")
