# Striplog

Lithology and stratigraphic logs for wells and outcrop.

* [A blog post about striplog](http://www.agilegeoscience.com/blog/2015/4/15/striplog)
* [Another one, with a video](http://www.agilegeoscience.com/blog/2015/7/10/geophysics-at-scipy-2015)

## Docs

* Read striplog's documentation
* Check out the tutorial notebooks

## Dependencies

These are best installed with Anaconda, see **Install**, below.

* Numpy
* matplotlib

## Install

* `pip install striplog`

We recommend setting up a virtual environment:

* Install Anaconda if you don't have it already
* Then create an environment called `myenv` (or whatever you like), answering Yes to the confirmation question:

    conda create -n myenv python=3.9 numpy matplotlib
    conda activate myenv

* Then you can do:

    pip install striplog

## Development
### Setting up for testing

There are other requirements for testing, which you can install by navigating to the folder in which you cloned this repository. Then install `striplog` with

    pip install .[test]

The tests can be run with

    python run_tests.py

### Running the bleeding edge version

To run the latest version of striplog, you should be on the `develop` branch:

    git clone https://github.com/agile-geoscience/striplog.git
    cd striplog
    git checkout develop

We recommend working in a virtual environment (see above).

You can then install striplog by navigating to the `striplog` folder and running:

    pip install .

Remember to run `pip uninstall striplog` if you have already installed it.

## SciPy 2015

[Here's a presentation about Striplog](https://docs.google.com/presentation/d/16HJsJJQylb2_8D2NS1p2cjp1yzslqUl_51BN16J5Y2k/edit?usp=sharing)