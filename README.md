# llmify

To get started, run the following:

```
$ nix develop
$ poetry run python -m sample_package
Hello, world!
```

# Formating & type checking
Run `lint.sh`, which will setup a venv and then run the formatter and type checker.

# Building
Building can help troubleshoot packaging issues. Run `nix build` and then `results/bin/llmify`.