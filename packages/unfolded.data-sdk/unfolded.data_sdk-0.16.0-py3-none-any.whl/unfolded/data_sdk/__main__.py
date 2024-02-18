"""Stub file to allow CLI use as an entry point

E.g.

```
python -m unfolded.data_sdk
```

instead of

```
uf-data-sdk
```

This can be useful to ensure that the CLI is using the same Python environment as the
active one. Otherwise in some circumstances, the PATH could be set up so that the
`uf-data-sdk` CLI and `python` are two different environments.
"""
from unfolded.data_sdk.cli import main

if __name__ == "__main__":
    main()
