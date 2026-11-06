from gen_stats import streaks

assert streaks([]) == (0, 0)
assert streaks([0, 0, 0]) == (0, 0)
assert streaks([1, 2, 0, 3, 1, 4]) == (3, 3)
assert streaks([1, 1, 1, 1, 0, 2, 2]) == (2, 4)
# today has nothing yet: streak through yesterday still counts
assert streaks([0, 5, 5, 0]) == (2, 2)
# yesterday empty too: streak is broken
assert streaks([5, 5, 0, 0]) == (0, 2)
print("ok")
