# Home Assistant integration standards

**These projects aim for enterprise quality but remain hobby projects: offered as is, to
be used at your own risk.**

A public, opt-in standard for jasonaward's hobby Home Assistant integrations: how they're
documented, versioned, released and presented. It builds on Home Assistant's own rules,
including those of its Marketplace and of HACS, adding only what they don't cover.

These are personal projects, built to learn when and how AI-assisted and AI-written code
can be applied well. The standard describes how the maintainer intends to build and
document them; it isn't a warranty, guarantee or commitment to any user.

## Contents

- [`STANDARD.md`](STANDARD.md): the standard.
- [`skills/ha-integration-standards/`](skills/ha-integration-standards/SKILL.md): a Claude
  skill that applies the standard when working on a project that has adopted it.
- [`check/check_standard.py`](check/check_standard.py): the shared check (section 8).
  Errors are must rules that aren't met; warnings are _should_ rules.
- [`template/`](template) and [`copier.yml`](copier.yml): a
  [Copier](https://copier.readthedocs.io/) template that creates a project meeting the
  standard, with a minimal working integration and its tests.
- [`CHANGELOG.md`](CHANGELOG.md): changes to the standard.

## Using it

1. A project adopts the standard by adding a `.standard-version` file with the version it
   follows. That file is the only record; projects without it aren't bound by the
   standard.
2. When the standard changes, its version changes (section 8), and projects adopt the new
   version through a reviewed update.

### Starting a new project

```bash
pip install copier
copier copy --trust gh:jasonaward/ha-integration-standards ha-<domain>
```

Copier asks for the domain, the product, and the company (left empty for your own
product), and creates the repository. Then add the brand images, build the integration,
and fill in each README section marked TODO. To bring in later changes to the template,
run `copier update --trust` in the project and review the result.

### Running the check

In a project's CI, the template adds `.github/workflows/standard.yml`, which calls this
repository's reusable workflow, pinned to a commit:

```yaml
jobs:
  standard:
    uses: jasonaward/ha-integration-standards/.github/workflows/check.yml@<commit SHA>
```

It runs the check from the standard version in the project's `.standard-version`. To
run it locally, with Python 3.12 or later and nothing else to install:

```bash
python path/to/ha-integration-standards/check/check_standard.py path/to/project
```

## License

[Apache License 2.0](LICENSE). Provided "as is", without warranty and without liability.
