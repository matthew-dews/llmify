# llmify

To get started, run the following:

```
$ nix develop
$ poetry run llmify
Hello, world!
```

# Formating & type checking
```
poetry run black llmify
poetry run mypy llmify
```

# Building
Building can help troubleshoot packaging issues. Run `nix build` and then `results/bin/llmify`.