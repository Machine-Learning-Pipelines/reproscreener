# Installation

1. To use reproscreener [@bhaskaradhithyaReproScreenEnablingRobustness2022], first create a virtual environment and activate it:

   1. Install the python package manager [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer).

   2. [Install pyenv and pyenv-virtualenv](https://github.com/pyenv/pyenv)

   3. Create a virtual environment with the correct python version (3.9.13):

    ```  sh
    (.venv) $ pyenv install 3.9.13
    (.venv) $ pyenv virtualenv 3.9.13 reproscreener
    (.venv) $ pyenv local reproscreener
    ```

2. Install `reproscreener` from pip

    ``` sh
    (.venv) $ pip install reproscreener
    ```