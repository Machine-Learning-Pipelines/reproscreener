Usage
=====

Installation
------------

1. To use repro-screener, first clone the repository:

.. code-block:: console

    (.venv) $ git clone git@github.com:Machine-Learning-Pipelines/repro-screener.git

2. Install the python package manager `poetry <https://python-poetry.org/docs/#installing-with-the-official-installer>`_.

3. Install dependencies:

.. code-block:: console

    (.venv) $ poetry install

4. Run the ``run.sh`` bash script:

.. code-block:: console
    
    (.venv) $ ./run.sh

Project structure
-----------------

- ``run.sh`` is the script used to run ReproScreener
- ``case-studies`` contains the papers that ReproScreener is developed and tested on
- ``guidance`` contains the set of metrics that ReproScreener will check for 
- ``tests`` contains scripts and notebooks used during development
- ``src`` contains the main python scripts