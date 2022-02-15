Changelog
=========

0.9.0 (coming February 2022)
----------------------------

- We are no longer supporting versions of Python before 3.6 (because I like f-strings).
- You can now pass format string labels to ``striplog.plot()``, e.g. ``'{colour} {lithology}'``. These are passed to the Component summary method.
- The Striplog constructor now creates Components if it is given miscellaneous data. If there are not components (e.g. "comp" fields in the CSV), then the description and either the provided Lexicon or the default one will be passed to the Interval constructor.
- Reorganized and moved ``the documentation <https://code.agilescientific.com/striplog>``_ to make it a bit easier to follow.
- You can plot Striplog's logo with ``striplog.logo.plot()``.


0.8.8 (January 2021)
--------------------

- Added ``Striplog.from_dict()`` to create a striplog from a dictionary with items like ``name: depth``.
- When reading a Petrel 'tops' file, you can pass a single function to apply to every quantity, not just a mapping of field names to functions. (You might do this to replace all ``-999.25`` with ``np.nan``, for example.) There's no way to do both at present, but if there's a need, please file an issue.
- Updated the default lexicon with some 'modifiers' like 'silty', 'sandy', etc.
- ``Lexicon._parse_description()`` is now a private static method (it was previously mangled which was a mistake). It can be called without instantiating a class to parse a piece of text. See the notebook, ``Parsing_a_description.ipynb``.
- Fixed a bug causing the default Lexicon to be a shallow copy, which was annoying.


0.8.7 (November 2020)
---------------------

- Breaking change: ``Striplog.extract()`` now returns a copy of the striplog instead of changing the striplog in place.
- Added option to send actual data to ``Striplog.to_log()`` instead of index from lookup table.
- Added a tutorial, ``Blocking_curves_with_striplog.ipynb``.


0.8.6 (October 2020)
--------------------

- Multi-step Markov chains now work properly, respecting 'self-transitions'.
- Added ``include_self`` property to the repr of a Markov chain object.
- Added ``match_only`` argument to ``Legend.random()``` to allow you to keep only certain properties in the components.
- ``Component.from_text()`` will now use ``Lexicon.default()`` if you don't pass one in.

We started adding an experimental new feature; feedback welcome! Added ``Striplog.from_macrostrat()`` which takes a lat/lon location and returns a striplog in geological time or in depth below the surface at that location.


0.8.5 (May 2020)
----------------

- Fixed sphinx documentation.
- Documentation now includes all tutorial notebooks.


0.8.4 (April 2020)
------------------

- Added ``label`` kwarg to ``striplog.plot()``. Give it the name of a field in the ``primary`` component and it will be added to the plot as text. Experimental feature; might break with some sizes of striplog. Feedback welcome.
- Fixed a bug in ``Striplog.hist()`` which produced the wrong colours and labels for the bars.


0.8.3 (July 2019)
-----------------

- Minor release. Updated tutorials and fixed some bugs.


0.8.2 (July 2019)
-----------------

- Added ``Striplog.shift()`` to allow you to shift all the tops and bases by some ``delta`` or by setting a new ``start``.
- Added ``striplog.markov.Markov_chain()``. See the ``Markov_chain.ipynb`` notebook in ``tutorial`` to see how to use it. This is an experimental module. There might be an elegant way to add the Markov chain as an attribute/methods on ``Striplog`` objects, but I couldn't think of it.
- Fixed a bug in ``Striplog.hist()`` which produced the wrong colours and labels for the bars.


0.8.1 (June 2019)
-----------------

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
------------------

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
