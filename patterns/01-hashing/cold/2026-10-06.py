"""
COLD IMPLEMENTATION: 01 · Hash lookup / frequency / grouping  (2026-10-06)
No notes, no autocomplete, no looking at primitive.py or old solutions.

Write from scratch:
  - frequency counter (dict / Counter)
  - complement map (Two Sum style: check BEFORE insert)
  - group-by-signature (canonical key -> list)

Then add tests below, run it, and record the result:
  ./dsa gate hashing cold            (first time: passes the cold gate)
  ./dsa review hashing pass|fail     (when a spaced review is due)
"""

from collections import Counter, defaultdict

# --- 1. Frequency counter ---
def frequency(items):
  return Counter(items)
  # or:
  # freq = {}
  # for x in items:
  #   freq[x] = freq.get(x, 0) + 1
  # return freq

def frequency_manual(items):
  freq = {}
  for x in items:
    freq[x] = freq.get(x, 0) + 1
  return freq

# --- 2. Complement map (Two Sum style) ---
def two_sum(nums, target):
  seen = {}
  for i,n in enumerate(nums):
    complement = target - n
    if complement in seen:
      return [seen[complement], i]
    seen[n] = i
  return []

# --- 3. Group-by-signature (canonical key -> list) ---
def _anagram_key(word: str) -> tuple:
  """
  valid input: a-z
  """
  counts = [0]*26
  for char in word:
      counts[ord(char)-ord('a')]+=1
  return tuple(counts)
    
def group_anagrams(words):
    groups = defaultdict(list)
    for word in words:
        groups[_anagram_key(word)].append(word)
    return list(groups.values())


if __name__ == "__main__":
    failures = []

    def check(name, actual, expected):
        """Record a failure instead of stopping at the first one."""
        if actual != expected:
            failures.append(name)
            print(f"  x {name}\n      expected {expected!r}\n      got      {actual!r}")

    def same_groups(groups):
        """Order-insensitive form of a list of groups, so [[b, a], [c]] == [[c], [a, b]]."""
        return sorted(sorted(g) for g in groups)

    # Usage:
    #   check("short name", frequency([...]), Counter({...}))
    #   check("short name", same_groups(group_anagrams([...])), same_groups([[...], [...]]))
    #
    # For each function, aim for one test per question. Delete the questions you've answered.

    # Each test names the bug it would catch. If you can't name one, the test is probably redundant.

    # --- frequency ---
    check("frequency: mixed repeats and singles", frequency([3, 1, 3, 2, 3, 1]), Counter({3: 3, 1: 2, 2: 1}))  # counting at all
    check("frequency: empty", frequency([]), Counter())                       # crashes on empty input
    check("frequency: all identical", frequency([7, 7, 7]), Counter({7: 3}))  # overwrite (=1) instead of increment
    check("frequency: negatives repeat", frequency([-1, 2, -1]), Counter({-1: 2, 2: 1}))  # array-index counting breaks on negatives

    # frequency_manual must agree with Counter on every input above.
    for case in ([3, 1, 3, 2, 3, 1], [], [7, 7, 7], [-1, 2, -1], "hello"):
        check(f"frequency_manual matches Counter: {case!r}", frequency_manual(case), frequency(case))

    # --- two_sum ---
    check("two_sum: classic", two_sum([2, 7, 11, 15], 9), [0, 1])
    check("two_sum: self-match trap", two_sum([3, 2, 4], 6), [1, 2])     # insert-before-check returns [0, 0]
    check("two_sum: duplicates pair up", two_sum([3, 3], 6), [0, 1])     # a set (no index) or a "skip duplicates" rule
    check("two_sum: single element", two_sum([5], 10), [])                # self-match with nothing else around
    check("two_sum: empty", two_sum([], 0), [])                           # crashes on empty input
    check("two_sum: no valid pair", two_sum([1, 2, 3], 100), [])          # returns garbage instead of []
    check("two_sum: negatives and zero", two_sum([-3, 4, 0, 3], 0), [0, 3])  # assumes positives (e.g. "skip if x > target")

    # --- _anagram_key: compare keys with each other, not with hand-written 26-tuples ---
    check("key: anagrams share a key", _anagram_key("eat") == _anagram_key("tea"), True)  # order-sensitive key
    check("key: same letters, different counts", _anagram_key("aab") == _anagram_key("abb"), False)  # set-of-letters key
    check("key: different lengths", _anagram_key("a") == _anagram_key("aa"), False)  # set-of-letters key, again
    check("key: hashable", hash(_anagram_key("abc")) == hash(_anagram_key("cab")), True)  # returning a list -> TypeError

    # --- group_anagrams: always compare through same_groups (group order is not part of the contract) ---
    check("group: classic",
          same_groups(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])),
          same_groups([["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]))
    check("group: empty", group_anagrams([]), [])                         # crashes on empty input
    check("group: nothing groups", same_groups(group_anagrams(["abc", "def"])), same_groups([["abc"], ["def"]]))  # key too coarse
    check("group: everything groups", same_groups(group_anagrams(["abc", "bca", "cab"])), [["abc", "bca", "cab"]])  # key too fine
    check("group: duplicate words kept", same_groups(group_anagrams(["ab", "ba", "ab"])), [["ab", "ab", "ba"]])  # dedupes with a set
    check("group: different lengths split", same_groups(group_anagrams(["a", "aa"])), [["a"], ["aa"]])  # set-of-letters key

    print("PASS" if not failures else f"FAIL ({len(failures)})")

