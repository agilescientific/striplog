Changelog
=========

0.8.0
-----

- New point release because of breaking changes.
- Breaking change: `Striplog.prune()` and `Striplog.anneal()` now return copies, so you can chain them.
- `Striplog.bar()` makes a bar chart of the intervals, with optional sorting by thickness or any other key.
- Breaking change: `Striplog.hist()` (which `histogram()` now calls) now makes a plot as well and returns the bars (or the axis, if you pass one in).
- `Striplog.merge_neighbours()` performs a stepwise `Interval.union()` on all pairs of intervals, combining neighbours that have identical components. It is intended to be used after `Striplog.anneal()`.

0.7.0 to 0.7.3
--------------

- Improved test coverage
- Improved CSV writing
- Canstrat legend and ASCII file writing
- Striplog quality method


0.6.0 to 0.6.1
--------------

- Introduced `Position` object for expressing depths of intervals
- Custom string formatting for using with `format()`
- Lots of new built-in legends
- Random legends for when you're in a hurry
- Lots more superpowers for intervals, including intersect, merge and union
- Hatching in decors
- HTML repr for legends and intervals


0.5.0 to 0.5.6
--------------

- Rocks are now Components
- Python 3 support
- Many bug fixes
- Test coverage
- Continuous integration
- Updated documentation
- Histograms (buggy)
- Plot tests working


0.4.7 and earlier
-----------------

- First releases for client
