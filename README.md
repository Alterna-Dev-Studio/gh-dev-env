# gh-dev-env

A [GitHub CLI](https://cli.github.com/) extension that creates your private copy of [dev-env-template](https://github.com/Alterna-Dev-Studio/dev-env-template), clones it, and runs its setup.

```bash
gh extension install Alterna-Dev-Studio/gh-dev-env
gh dev-env my-dev-env
```

`gh dev-env <name>` runs `gh repo create <name> --template Alterna-Dev-Studio/dev-env-template --private --clone`, pulls until GitHub has finished copying the template files, then runs `cd <name> && ./scripts/setup`. The name defaults to `my-dev-env`. Give `owner/name` to create the repository under an organization. Options after the name, such as `--skip-taiga-mcp`, are passed to setup. It refuses to run if `./<name>` already exists.

Set `DEV_ENV_TEMPLATE=owner/repo` to start from a fork of the template instead.

## Testing

`python3 -m unittest discover -s tests -v` runs the tests against a fake `gh` and `git`, with no network access.
