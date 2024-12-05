# Installation

To install `reproscreener`, we recommend using a virtual environment such as [pyenv]( https://github.com/pyenv/pyenv-virtualenv) or [conda](https://docs.conda.io/en/latest/), or installing it using [pipx](https://pypa.github.io/pipx/). We recommend using python version {{ versions.python }}.

All you need is to pip install `reproscreener`! 

``` sh
pip install reproscreener
```

=== "pyenv"

    ``` bash
    pyenv install {{ versions.python }}
    pyenv virtualenv {{ versions.python }} reproscreener
    pyenv local reproscreener
    pip install reproscreener
    ```

=== "conda"

    ``` bash
    conda create -n reproscreener python={{ versions.python }}
    conda activate reproscreener
    pip install reproscreener
    ```

=== "pipx"

    ``` bash
    pipx install reproscreener
    ```
