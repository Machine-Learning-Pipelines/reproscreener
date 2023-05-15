# Usage

The tool has two primary arguments:

- `--arxiv`: This is the Arxiv URL to download and evaluate.
- `--repo`: This is the Git repository to evaluate.

You can also set the logging level using the `--log-level` argument.

## Examples

```bash
# Paper 2111.12673 from the gold standard dataset 
reproscreener --arxiv https://arxiv.org/e-print/2111.12673 --repo https://github.com/nicolinho/acc

# Paper 2106.07704 from the gold standard dataset
reproscreener --arxiv https://arxiv.org/e-print/2106.07704 --repo https://github.com/HanGuo97/soft-Q-learning-for-text-generation

# Paper 2203.06735 from the gold standard dataset
reproscreener --arxiv https://arxiv.org/e-print/2203.06735 --repo https://github.com/ghafeleb/Private-NonConvex-Federated-Learning-Without-a-Trusted-Server

# Run the tool with logging level set to debug
reproscreener --arxiv https://arxiv.org/e-print/2111.12673 --repo https://github.com/nicolinho/acc --log-level debug
```

By default, the logging level is set to `warning`. This means that only warnings, errors, and critical issues will be logged.

If you want to see more detailed logs, you can set the logging level to `debug`.

## Project structure

- `case-studies` contains the papers that ReproScreener is developed and tested on
- `guidance` contains the set of metrics that ReproScreener will check for
- `tests` contains scripts and notebooks used during development
- `src/reproscreener` contains the main python scripts
