# DSA, pattern-first

26 pattern families, learned one at a time. Each one goes through **learn → variants → solve → cold → edge cases**,
with spaced reviews at D+1, D+3, D+7 and D+14. Progress is in [roadmap.md](roadmap.md).

## Daily loop

```sh
./dsa today                     # what to do now: current step, suggested problems, reviews due
```

1. **Reviews first** (if any are due): `./dsa cold <pattern>`, write the primitive from memory, then `./dsa review <pattern> pass|fail`
2. **Learn** a new pattern with Claude: "teach me sliding window". Write `notes.md` yourself, then `./dsa gate <p> invariant`
3. **Drill**: "give me a recognition drill on <pattern>", then `./dsa drill <p> 8/10 --confused prefix-state:sliding-window`
4. **Solve**: `./dsa new two-sum` (creates the file and starts a timer), solve it, then
   `./dsa log two-sum clean|hint|peeked|unsolved --errors RC --note "what went wrong"`
5. **Insights**: `./dsa stats`, or run `./dsa dashboard` for the visual overview

## Dashboard

Run `./dsa dashboard` and open `dashboard/index.html`. The page is generated from
`tools/dashboard_template.html` and local tracker data, so the design is retained
whenever you regenerate it. It follows your system appearance by default; the
light/dark control remembers your choice in the browser.

Error tags: **R** recognition · **I** invariant · **C** coding · **E** edge case · **X** complexity

## Layout

```
reference/     the research report + pattern taxonomy
patterns/      one folder per started pattern: notes.md, primitive.py, problems/, cold/
tracker/       curriculum.json + your logs (csv/json)
tools/         the dsa CLI and dashboard template
dashboard/     generated dashboard
```
