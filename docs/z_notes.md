# reproscreener

```bash
https://arxiv.org/pdf/2306.00622
https://arxiv.org/pdf/2411.03417 
https://arxiv.org/abs/2106.07704

uv add requests pandas pathlib flashtext exrex rich gitpython urlextract feedparser watchdog docling streamlit

# Paper 2111.12673 from the gold standard dataset 
reproscreener --arxiv https://arxiv.org/e-print/2111.12673 --repo https://github.com/nicolinho/acc

# Paper 2106.07704 from the gold standard dataset
reproscreener --arxiv https://arxiv.org/e-print/2106.07704 --repo https://github.com/HanGuo97/soft-Q-learning-for-text-generation

# Paper 2203.06735 from the gold standard dataset
reproscreener --arxiv https://arxiv.org/e-print/2203.06735 --repo https://github.com/ghafeleb/Private-NonConvex-Federated-Learning-Without-a-Trusted-Server

# Run the tool with logging level set to debug
reproscreener --arxiv https://arxiv.org/e-print/2111.12673 --repo https://github.com/nicolinho/acc --log-level debug
```

## Notes

### June 4, 2025
- The `manual` evals for the abstracts were not used, the agreement was used instead. So the new derived/revised manual col is `manual_rev`.