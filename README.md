
<h2 align="center">Industrial Ecology Ontology DB</h2>

<p align="center">
<a href="https://github.com/ciraig/IndustrialEcologyOntologyDB/actions"><img alt="Actions Status" src="https://github.com/ciraig/IndustrialEcologyOntologyDB/workflows/Test/badge.svg"></a>
<a href="https://github.com/psf/black/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>


### Environment setup

Copy the template and edit values for your machine:

```bash
cp .env.example .env
```

`.env` is ignored by git on purpose.

**Never commit it. Use `.env.example` as the reference template.**

## How to contribute

The expected workflow is as follow:
 - Make your changes
 - Run make fmt (or the Docker Black command)
 - Commit and push to a branch
 - Open a Pull Request to 'main'
 - Wait for CI validation
 - Merge your Pull Request

---

## Branch protection

The default branch is protected with the following rules:

 - Direct pushes are not allowed
 - Pull requests are required

All required CI checks (including Black) must pass

This prevents unformatted code and unit test regression from landing in the repository, even if someone tries to bypass local tooling.

If you are used to pushing directly to the repository: **this is no longer possible by design**.

---

## Code formatting (Black)

This project enforces **Black** as the single source of truth for Python formatting.

We intentionally **do not rely on local virtualenvs**.  
All formatting and checks are executed **via Docker**, to ensure identical behavior across all machines.

### Why this exists

- Avoid style debates and diffs noise
- Guarantee consistent formatting across contributors
- Prevent unformatted code from reaching the main branch
- Keep the toolchain simple and reproducible

### How to format code locally

You do not need a local virtualenv.

```
# Format all Python code
docker compose run --rm api black /app

Check formatting (same as CI)
docker compose run --rm api black --check /app
```

If you prefer shorter commands, a Makefile is provided:

```
make fmt    # auto-format code
make lint   # check formatting (CI equivalent)
```