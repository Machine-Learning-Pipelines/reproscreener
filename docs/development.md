# Install for development

For a devlopment environment, first clone the repository `git@github.com:Machine-Learning-Pipelines/reproscreener.git`.

1. Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

[For installation methods, see the uv documentation](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

2. Create a virtual environment, activate it, and install the dependencies:

```bash
uv venv
source .venv/bin/activate
uv sync
```

3. Install the package in development mode: