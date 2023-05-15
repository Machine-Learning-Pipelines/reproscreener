# Installation

1. To use repro-screener, first clone the repository:

    ``` sh
    (.venv) $ git clone git@github.com:Machine-Learning-Pipelines/repro-screener.git
    ```

    [@bhaskaradhithyaReproScreenEnablingRobustness2022]

2. Install the python package manager [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer).

3. [Install pyenv and pyenv-virtualenv](https://github.com/pyenv/pyenv)

4. Create a virtual environment with the correct python version (3.9.13):

    ```  sh
    (.venv) $ pyenv install 3.9.13
    (.venv) $ pyenv virtualenv 3.9.13 repro-screener
    (.venv) $ pyenv local repro-screener
    ```

5. Install dependencies using poetry:

    ``` sh
    (.venv) $ poetry install
    ```