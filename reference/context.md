I have the full research report now. deep-research-report

It actually went further than we initially requested and produced a 30-day schedule too. **I suggest we ignore the schedule for the moment.** First, we should lock down the pattern taxonomy—because the quality of the eventual month depends on learning the *right* set of patterns rather than cramming arbitrary problems.

## The DSA Pattern Map

One important correction to the mental model: these aren't cleanly separated by data structure. **Patterns cross boundaries.** Two pointers appears in arrays and linked lists; BFS appears in trees and graphs; heaps power Dijkstra; hash maps combine with prefix sums and sliding windows; DFS underlies trees, graphs, and backtracking.

So I'd organize your knowledge as:

**Data structure → pattern → variant → invariant → recognition signals → implementation primitive.**

### 1. Arrays

| Pattern | Variants | Priority |
|---|---|---|
| **Two Pointers** | Opposite ends | 🔴 Core |
| | Same-direction / slow-fast | 🔴 Core |
| | Read/write / in-place compaction | 🔴 Core |
| | Sorted pair sum | 🔴 Core |
| | Sorted K-sum / 3Sum | 🔴 Core |
| **Sliding Window** | Fixed-size window | 🔴 Core |
| | Variable-size window | 🔴 Core |
| | Frequency-constrained window | 🔴 Core |
| | At-most / exactly-K transformations | 🟡 Important |
| **Prefix Aggregates** | Prefix sum | 🔴 Core |
| | Prefix + suffix | 🔴 Core |
| | Prefix state + hashmap | 🔴 Core |
| | Prefix modulo/remainder | 🟡 Important |
| **Binary Search** | Exact lookup | 🔴 Core |
| | Lower/upper bound | 🔴 Core |
| | First/last true | 🔴 Core |
| | Rotated sorted array | 🔴 Core |
| | Binary search on answer | 🔴 Core |
| **Intervals** | Merge intervals | 🔴 Core |
| | Insert interval | 🟡 Important |
| | Non-overlap / interval scheduling | 🟡 Important |
| | Meeting-room style problems | 🟡 Important |

The recognition distinctions here are extremely important.

**Contiguous + maintainable constraint → sliding window.**

**Contiguous + relation between cumulative states → prefix sums.**

**Sorted + boundary relationship → two pointers.**

**Monotone search space → binary search.**

---

## 2. Hash Maps / Hashing

Hash maps don't have as many independent patterns. They're more often a **supporting structure that makes another pattern possible**.

| Pattern | Variants | Priority |
|---|---|---|
| **Lookup** | Membership / seen set | 🔴 Core |
| | Complement lookup | 🔴 Core |
| | Value → index | 🔴 Core |
| **Frequency Counting** | Value → count | 🔴 Core |
| | Character frequency | 🔴 Core |
| | Frequency comparison | 🔴 Core |
| **Grouping** | Canonical key → group | 🔴 Core |
| | Sorted-key grouping | 🟡 |
| | Frequency-vector key | 🟡 |
| **State Indexing** | Prefix state → frequency | 🔴 Core |
| | Prefix state → earliest index | 🔴 Core |
| | Remainder/modulo → state | 🟡 Important |
| **Sliding-window state** | Character counts | 🔴 Core |
| | Required/formed counts | 🟡 Important |

This distinction needs to become automatic:

**Counting number of intervals → state → frequency.**

**Finding longest interval → state → earliest index.**

For example, `Subarray Sum Equals K` and `Contiguous Array` look different but belong to essentially the same **prefix-state + hash map** family. deep-research-report

---

## 3. Heaps / Priority Queues

There are really three major heap families worth mastering.

| Pattern | Variants | Priority |
|---|---|---|
| **Top-K / bounded heap** | Kth largest | 🔴 Core |
| | Kth smallest | 🔴 Core |
| | K closest | 🔴 Core |
| | Top-K frequent | 🔴 Core |
| **K-way merge** | Merge sorted arrays/lists | 🔴 Core |
| | Smallest among K streams | 🟡 |
| **Scheduling / dynamic priority** | Repeated best available candidate | 🔴 Core |
| | Task scheduling | 🟡 |
| | Event simulation | 🟡 |
| **Two heaps** | Running median | 🟡 Important |
| | Balanced lower/upper halves | 🟡 |
| **Lazy heap / stale entries** | Dijkstra stale entries | 🔴 Core for graphs |
| | Sliding-window heap deletion | 🟢 Stretch |

Recognition rule:

> **If the collection changes and you repeatedly need the current minimum/maximum/best candidate, investigate a heap.**

That distinguishes it from sorting. If you only need sorted order once, sorting may be simpler. If you need an extreme repeatedly while the candidate set changes, heap becomes much more attractive.

---

# 4. Trees

Trees should be learned primarily through **information flow**.

| Pattern | Variants | Priority |
|---|---|---|
| **DFS traversal** | Preorder | 🔴 Core |
| | Inorder | 🔴 Core |
| | Postorder | 🔴 Core |
| | Iterative DFS | 🔴 Core |
| **BFS** | Level-order | 🔴 Core |
| | Level aggregation | 🔴 Core |
| | Right/left-side view | 🟡 |
| **Path DFS** | Root → leaf state | 🔴 Core |
| | Path sum | 🔴 Core |
| | Ancestor state | 🟡 |
| **Subtree aggregation** | Height/depth | 🔴 Core |
| | Diameter | 🔴 Core |
| | Maximum path | 🔴 Core |
| | Subtree properties | 🔴 Core |
| **BST** | Search using ordering | 🔴 Core |
| | Validate BST | 🔴 Core |
| | Inorder sorted property | 🔴 Core |
| | Kth smallest/largest | 🔴 Core |
| **Tree relationships** | Lowest common ancestor | 🔴 Core |
| | Ancestor/descendant reasoning | 🟡 |

The most useful tree question isn't:

> “Should I use DFS?”

It's:

> **“What does my recursive function return?”**

For Diameter of Binary Tree, for example, the recursion returns information about **height**, while the global answer tracks the best **diameter**.

That's the kind of distinction we need to drill until it becomes natural.

---

# 5. Graphs

This is one of the biggest areas, but the report identifies a very manageable core.

| Pattern | Variants | Priority |
|---|---|---|
| **Graph DFS** | Reachability | 🔴 Core |
| | Connected components | 🔴 Core |
| | Cycle detection | 🔴 Core |
| **Graph BFS** | Reachability | 🔴 Core |
| | Unweighted shortest path | 🔴 Core |
| | Level/distance BFS | 🔴 Core |
| **Grid as graph** | Flood fill | 🔴 Core |
| | Islands/components | 🔴 Core |
| | Grid shortest path | 🔴 Core |
| **Multi-source BFS** | Multiple starting points | 🔴 Core |
| | Spreading processes | 🔴 Core |
| **Topological Sort** | Kahn's BFS | 🔴 Core |
| | DFS three-color | 🔴 Core |
| | Directed cycle detection | 🔴 Core |
| **Union-Find / DSU** | Connectivity | 🔴 Core |
| | Component merging | 🔴 Core |
| | Undirected cycle detection | 🔴 Core |
| | Component count | 🔴 Core |
| **Dijkstra** | Standard shortest path | 🔴 Core |
| | Grid weighted shortest path | 🟡 |
| | Modified state / path metric | 🟡 |
| **Other shortest paths** | 0-1 BFS | 🟢 Stretch |
| | Bellman-Ford | 🟢 Stretch |
| | Floyd-Warshall | 🟢 Stretch |
| **MST** | Kruskal + DSU | 🟡 |
| | Prim + heap | 🟡 |

Your high-speed recognition map eventually becomes:

**Connectivity → DFS/BFS/DSU**

**Unweighted shortest path → BFS**

**Multiple simultaneous sources → multi-source BFS**

**Dependencies → topological sort**

**Non-negative weighted shortest path → Dijkstra**

**Repeated component merging → DSU**

---

# 6. Dynamic Programming

This is where I would modify the report's organization slightly.

Don't think of DP as “memorize these 15 DP patterns.”

Think:

**State → transition → base cases → computation order → answer → optimization**

Then learn recurring **state shapes**.

| DP family | Variants | Priority |
|---|---|---|
| **1D DP** | Count ways | 🔴 Core |
| | Min/max cost | 🔴 Core |
| | Take/skip | 🔴 Core |
| | Prefix segmentation | 🔴 Core |
| **Knapsack** | 0/1 knapsack | 🔴 Core |
| | Unbounded knapsack | 🔴 Core |
| | Subset sum | 🔴 Core |
| | Target/count variants | 🟡 |
| **Grid DP** | Count paths | 🔴 Core |
| | Min/max path | 🔴 Core |
| | Obstacles | 🔴 Core |
| **Two-sequence DP** | LCS | 🔴 Core |
| | Edit distance | 🔴 Core |
| | Matching/alignment | 🟡 |
| **Subsequence DP** | LIS O(n²) DP | 🔴 Core |
| | LIS binary-search optimization | 🟡 |
| **String segmentation** | Word Break style | 🔴 Core |
| **Interval DP** | Solve `[l,r]` from smaller ranges | 🟢 Stretch |
| **Tree DP** | Combine child states | 🟡 Important |
| **State-machine DP** | Buy/sell/hold states | 🟡 |
| **Bitmask DP** | Subset-as-state | 🟢 Stretch |

There is one exercise I particularly want us to repeat:

```text
brute recursion
      ↓
identify repeated state
      ↓
memoization
      ↓
derive dependencies
      ↓
bottom-up DP
      ↓
space optimization
```

That will make DP much less mysterious.

---

# 7. Backtracking

Backtracking has fewer core templates than people think.

The universal primitive is:

```text
choose
explore
undo
```

The variants come from **what choices are legal at each recursion level**.

| Pattern | Variants | Priority |
|---|---|---|
| **Subsets** | Include/exclude | 🔴 Core |
| | Start-index enumeration | 🔴 Core |
| **Combinations** | Choose K | 🔴 Core |
| | Reusable candidates | 🔴 Core |
| | Non-reusable candidates | 🔴 Core |
| **Permutations** | `used[]` | 🔴 Core |
| | Swap-based permutation | 🟡 |
| **Duplicate handling** | Sort + skip duplicates | 🔴 Core |
| **Partitioning** | String partition | 🔴 Core |
| | Segment validation | 🔴 Core |
| **Grid backtracking** | Mark → explore → restore | 🔴 Core |
| **Constraint satisfaction** | N-Queens | 🟡 Important |
| | Sudoku | 🟢 Stretch |
| **Pruning** | Invalid-state pruning | 🔴 Core |
| | Bound-based pruning | 🟡 |

The key recognition distinction:

**Need one path/reachability → DFS.**

**Need all valid choices/configurations → backtracking.**

**Same states repeatedly recomputed → investigate DP.**

---

# 8. Linked Lists

Linked lists are mostly about **pointer invariants and rewiring**.

| Pattern | Variants | Priority |
|---|---|---|
| **Reversal** | Full reversal | 🔴 Core |
| | Recursive reversal | 🟡 |
| | Reverse sublist | 🔴 Core |
| | Reverse K-group | 🟡 |
| **Slow/Fast pointers** | Find middle | 🔴 Core |
| | Cycle detection | 🔴 Core |
| | Cycle entry | 🟡 |
| **Fixed-gap pointers** | Nth node from end | 🔴 Core |
| **Dummy node** | Head-safe deletion | 🔴 Core |
| | Construction/merge | 🔴 Core |
| **Merge** | Two sorted lists | 🔴 Core |
| | K sorted lists + heap | 🔴 Cross-pattern |
| **List partitioning** | Build separate chains | 🟡 |
| **Reordering** | Middle + reverse + merge | 🟡 Important |

There are really four primitives I want to become unconscious:

```text
prev / curr / next reversal
slow / fast
fixed gap
dummy head
```

Most linked-list interview problems are compositions of those.

---

# 9. Stacks

Stacks split cleanly into ordinary LIFO problems and monotonic-stack problems.

| Pattern | Variants | Priority |
|---|---|---|
| **Matching** | Parentheses/brackets | 🔴 Core |
| | Nested structures | 🔴 Core |
| **Expression processing** | Postfix evaluation | 🔴 Core |
| | Infix parsing | 🟡 |
| | Calculator problems | 🟡 |
| **Monotonic Stack** | Next greater | 🔴 Core |
| | Next smaller | 🔴 Core |
| | Previous greater | 🔴 Core |
| | Previous smaller | 🔴 Core |
| **Boundary computation** | Left/right smaller boundaries | 🔴 Core |
| | Histogram | 🔴 Core |
| | Span/distance | 🔴 Core |
| **Stack simulation** | Undo/history | 🟡 |
| | Collision-type simulation | 🟡 |

For monotonic stacks, don't memorize Daily Temperatures.

Memorize this idea:

> **The stack contains candidates whose answer has not been found yet. The current element either becomes another unresolved candidate or resolves candidates from the top.**

That's the invariant.

---

# The actual core curriculum

After going through the research, I'd compress everything above into roughly **25 pattern families** rather than treating every row as an independent thing:

**Hash lookup/frequency → Two pointers → Sliding window → Prefix state → Binary search → Intervals → Linked-list rewiring → Fast/slow pointers → Stack → Monotonic stack → Top-K heap → Heap orchestration → Tree DFS → Tree BFS → Tree postorder/subtree aggregation → BST → Graph DFS/BFS → Multi-source BFS → Topological sort → Union-Find → Dijkstra → Backtracking → 1D DP → Knapsack DP → Grid DP → Sequence/String DP.**

That is the vocabulary I want you to own.

And there are a few things I'd deliberately **deprioritize during the first month**: Bellman-Ford, Floyd-Warshall, advanced interval DP, bitmask DP, sophisticated heap deletion, Sudoku-level backtracking, advanced tree structures, tries, segment trees, Fenwick trees, and specialized graph algorithms. They're useful, but adding them now would work against your stated goal of making the highest-frequency machinery automatic. This prioritization follows the report's own core-vs-stretch distinction. deep-research-report

The next step should **not** be jumping directly into that generated 30-day calendar. Now that we have the taxonomy, we should design the month around **mastery gates and dependencies**—including exactly which variants you implement from scratch, which problems represent each variant, recognition-only drills, and when each primitive reappears for spaced recall. That's where we can make this substantially better than a generic LeetCode roadmap.