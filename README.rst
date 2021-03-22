striplog
========

.. image:: https://img.shields.io/travis/agile-geoscience/striplog.svg
    :target: https://travis-ci.org/agile-geoscience/striplog
    :alt: Travis build status
    
.. image:: https://readthedocs.org/projects/striplog/badge/?version=latest
    :target: https://striplog.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
    
.. image:: https://img.shields.io/pypi/status/striplog.svg
    :target: https://pypi.python.org/pypi/striplog/
    :alt: Development status

.. image:: https://img.shields.io/pypi/v/striplog.svg
    :target: https://pypi.python.org/pypi/striplog/
    :alt: Latest version
    
.. image:: https://img.shields.io/pypi/pyversions/striplog.svg
    :target: https://pypi.python.org/pypi/striplog/
    :alt: Python version

.. image:: https://img.shields.io/pypi/l/striplog.svg
    :target: http://www.apache.org/licenses/LICENSE-2.0
    :alt: License

Lithology and stratigraphic logs for wells and outcrop. 

* `A blog post about striplog <http://www.agilegeoscience.com/blog/2015/4/15/striplog>`_
* `Another one, with a video <http://www.agilegeoscience.com/blog/2015/7/10/geophysics-at-scipy-2015>`_


Docs
----

* `Read The Docs <https://striplog.readthedocs.org/>`_
* Check out `the tutorial </tutorial>`_ notebooks.


Installation
------------

.. code-block:: shell

    pip install striplog

I recommend setting up a virtual environment:

* Install `Anaconda <http://docs.continuum.io/anaconda/install>`_ if you don't have it already
* Then do this to create an environment called ``myenv`` (or whatever you like), answering Yes to the confirmation question::

.. code-block:: shell

    conda create -n myenv python=3.5 numpy matplotlib
    source activate myenv

* Then you can do ``pip install striplog``.


Getting started
---------------

.. code-block:: python

    from striplog import Striplog
    s = Striplog.from_log


Development: setting up for testing
-----------

There are other requirements for testing, as listed in ``setup.py``. They should install with

.. code-block:: shell

    python setup.py test

But I had better luck doing ``conda install pytest`` first.

The tests can be run with

.. code-block:: shell

    python run_tests.py


Development: running the bleeding edge
-----------

To run the latest version of the code, you should be on the `develop` branch:

.. code-block:: python

    git clone https://github.com/agile-geoscience/striplog.git
    cd striplog
    git checkout develop
    
You probably want to continue in your virtual environment (see above).

Then I use these commands, which you can join with `;` if you like, to keep the software up to date:

.. code-block:: python

    /usr/bin/yes | pip uninstall striplog     # Of course you don't need this one if you didn't install it yet.
    python setup.py sdist
    pip install dist/striplog-0.6.1.tar.gz    # Or whatever was the last version to build.
