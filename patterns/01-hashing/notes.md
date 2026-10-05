# 01 · Hash lookup / frequency / grouping

> Write this in YOUR words during the learn phase. Claude checks it, not writes it.
> Reference: `./dsa show hashing` (variants + signals), reference/deep-research-report.md

## Core idea
A hash map makes lookup by key **O(1) on average**. It turns repeated linear searches ("have I seen X?",
O(n) each, O(n²) in total) into constant-time checks, so the whole scan becomes **O(n)**.

The real question before coding:
> **As I scan, what do I need to remember about what I've seen, and what question will I ask that memory?**

The answer decides the key and the value.

## Invariant
**One-pass (scan and remember):** when I'm at index `i`, the map summarises only the elements *before* `i`
(e.g. number → index, value → count). So at every step I **check the map first, then always record the current
element**. This guarantees I never match an element with itself, and duplicates still pair up correctly (`[5, 5]`).

**Two-pass (build then query):** fill the whole map first (counts, canonical key → group), then read it.
Here the invariant is just "the map is complete before I query it" (e.g. first unique char, group anagrams).

Keep only what can still matter: when a newer occurrence makes the old info useless, overwrite it
(nearby duplicates → latest index).

## Variants I identified
| Variant | Map shape | Question I ask it | Example |
|---|---|---|---|
| Seen / membership | `set` of values | "Have I seen x?" / "Is x's neighbour here?" | Contains Duplicate, Longest Consecutive Sequence |
| Complement lookup | value → index | "Have I seen `target - x`, and where?" | Two Sum |
| Value → latest index | value → most recent index | "How far back was the last x?" | Contains Duplicate II (`i - last[x] <= k`) |
| Frequency counting | value → count (`Counter`) | "How many times does x appear?" | First Unique Character (count, then 2nd pass over string) |
| Frequency comparison | two counters, or one counter +/- | "Do both have identical counts?" | Valid Anagram, Ransom Note |
| Canonical-key grouping | canonical key → list (`defaultdict(list)`) | "Which items are equivalent to this one?" | Group Anagrams (key = sorted word, or 26-count tuple) |

**Canonical key test:** two items are equivalent **if and only if** their keys are equal. The key must be hashable
(`"".join(sorted(w))` or `tuple(...)`, never a list).

## Recognition signals
- "Have I seen this before?" / duplicates / "appears more than once"
- Pair or complement condition on **unsorted** data (`a + b = target`, `a - b = k`)
- Counts matter, order doesn't: anagrams, "can X be built from Y", "appears exactly once"
- "Group together items that are equivalent"
- Need O(n) and sorting (O(n log n)) is ruled out or loses needed info (like original indices)

## Closest competing pattern
**Sorting (+ two pointers).** It also finds pairs and duplicates, and uses O(1) extra space, but costs O(n log n)
and destroys the original indices. Choose hashing when I need **original indices** or **O(n)**; choose sorting when
memory is tight or the input is already sorted. *(Two pointers is pattern 02: revisit this line then.)*

## Template
Canonical code goes in `primitive.py`, written by me. Moving parts:
- **One-pass:** `for i, x in enumerate(nums):` → query the map → record `x` (always, after the query)
- **Two-pass:** build `Counter(...)` or `defaultdict(list)` → second loop that reads it
- Choose the structure: `set` (seen) · `dict` (index) · `Counter` (count) · `defaultdict(list)` (group)

## Pitfalls / edge cases
- **Mutable keys:** keys must be immutable. If a key changed after insertion its hash would change and it could never
  be found again. Use `str` / `tuple`, never `list`.
- **Check before insert** in one-pass scans: `[5, 1, 2]`, target 10. Inserting first lets 5 match itself.
- **Iterate the set, not the list** in Longest Consecutive Sequence. Duplicate run-starts would recount the same
  run, which is O(n²) in the worst case.
- **Overwrite vs keep:** nearest-duplicate problems keep the *latest* index. Know which one the problem needs.
- Other inputs to test: empty input, a single element, all elements equal, negative numbers.

## Complexity
- Time: **O(n)** average (O(n·k log k) for group anagrams with sorted keys; O(n·k) with count keys)
- Space: **O(n)** for the map (O(1) if the key space is fixed, like 26 letters)
