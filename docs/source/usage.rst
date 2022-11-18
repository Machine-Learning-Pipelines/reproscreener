Usage
=====

Installation
------------

1. To use repro-screener, first clone the repository:

.. code-block:: console

    (.venv) $ git clone git@github.com:Machine-Learning-Pipelines/repro-screener.git

2. Install the python package manager `poetry <https://python-poetry.org/docs/#installing-with-the-official-installer>`_.

3. Install pyenv and pyenv-virtualenv: `<https://github.com/pyenv/pyenv>`_.

4. Create a virtual environment with the correct python version (3.9.13):

.. code-block:: console

    (.venv) $ pyenv install 3.9.13
    (.venv) $ pyenv virtualenv 3.9.13 repro-screener
    (.venv) $ pyenv local repro-screener

3. Install dependencies using poetry:

.. code-block:: console

    (.venv) $ poetry install

4. Install grobid, grobid-service and grobid-python-client:

    - `<https://grobid.readthedocs.io/en/latest/Install-Grobid/>`_
    - `<https://grobid.readthedocs.io/en/latest/Grobid-service/>`_
    - `<https://github.com/kermitt2/grobid_client_python>`_

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