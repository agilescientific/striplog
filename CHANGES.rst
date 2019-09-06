Changelog
=========

0.8.3 (July 2019)
----

- Minor release. Updated tutorials and fixed some bugs.

0.8.2 (July 2019)
-----

- Added ``Striplog.shift()`` to allow you to shift all the tops and bases by some ``delta`` or by setting a new ``start``.
- Added ``striplog.markov.Markov_chain()``. See the ``Markov_chain.ipynb`` notebook in ``tutorial`` to see how to use it. This is an experimental module. There might be an elegant way to add the Markov chain as an attribute/methods on ``Striplog`` objects, but I couldn't think of it.
- Fixed a bug in ``Striplog.hist()`` which produced the wrong colours and labels for the bars.


0.8.1 (June 2019)
-----

- Added ``append``, ``extend`` and ``pop`` methods to ``Striplog`` objects.
- Breaking change: Changed the name of ``Striplog.__insert()`` to ``Striplog.insert()`` to match ``append()``, ``extend()`` and ``pop()``.
- Added binary morphology filters to ``Striplog`` object. These offer another way to filter intervals, and thus to simplify a binary striplog (one in which an attribute of the components contains only a single binary 'flag'). Operations include ``dilation``, ``erosion``, ``opening``, and ``closing``.
- Fixed a bug in ``plot``: it assumed the first interval in a striplog was the 'shallowest' and the last the deepest. But if intervals can overlap (which they can), then this is not a safe assumption. Now uses ``Striplog.start`` and ``Striplog.stop`` to decide.
- Added ``mode`` keyword arg to anneal, allowing user to choose whether the gaps in the log are filled in by flooding upwards (that is, extend the interval below the gap upwards), flooding downwards (extend the upper interval), or flooding symmetrically into the middle from both above and below, meeting in the middle. (Note, you can also fill gaps with another component, using the ``fill()`` method.)
- Added ``merge`` method to the ``Striplog``. This allows you to merge overlapping intervals by precedence (rather than by blending the contents of the intervals). For example, you can choose to keep the thickest interval in all overlaps. If intervals have a date, you could keep the latest interval.
- Added ``net_to_gross`` method to ``Striplog`` object. Give it a binary attribute and it will compute the ratio of intervals having that attribute as ``True`` to the total thickness.
- Added a couple of notebooks to ``/tutorial``.
- Fixed a bug that allowed lists of intervals used to instantiate striplogs to be mutated.


0.8.0 (March 2019)
-----

- New point release because of breaking changes.
- Breaking change: ``Striplog.prune()`` and ``Striplog.anneal()`` now return copies, so you can chain them.
- ``Striplog.bar()`` makes a bar chart of the intervals, with optional sorting by thickness or any other key.
- Breaking change: ``Striplog.hist()`` (which ``histogram()`` now calls) now makes a plot as well and returns the bars (or the axis, if you pass one in).
- ``Striplog.merge_neighbours()`` performs a stepwise ``Interval.union()`` on all pairs of intervals, combining neighbours that have identical components. It is intended to be used after ``Striplog.anneal()``.


0.7.0 to 0.7.3
--------------

- Improved test coverage.
- Improved CSV writing.
- Canstrat legend and ASCII file writing.
- Striplog quality method.


0.6.0 to 0.6.1
--------------

- Introduced ``Position`` object for expressing depths of intervals.
- Custom string formatting for using with ``format()``.
- Lots of new built-in legends.
- Random legends for when you're in a hurry.
- Lots more superpowers for intervals, including intersect, merge and union.
- Hatching in decors.
- HTML repr for legends and intervals.


0.5.0 to 0.5.6
--------------

- Rocks are now Components.
- Python 3 support.
- Many bug fixes.
- Test coverage.
- Continuous integration.
- Updated documentation.
- Histograms (buggy).
- Plot tests working.


0.4.7 and earlier
-----------------

- First releases for client.
