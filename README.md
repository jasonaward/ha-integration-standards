# Home Assistant integration standards

**These projects aim for enterprise quality but remain hobby projects: offered as is, to
be used at your own risk.**

A public, opt-in standard for jasonaward's hobby Home Assistant integrations: how they're
documented, versioned, released and presented. It builds on Home Assistant's and HACS's
own rules, adding only what they don't cover.

These are personal projects, built to learn when and how AI-assisted and AI-written code
can be applied well. The standard describes how the maintainer intends to build and
document them; it isn't a warranty, guarantee or commitment to any user.

## Contents

- [`STANDARD.md`](STANDARD.md): the standard.
- [`skills/ha-integration-standards/`](skills/ha-integration-standards/SKILL.md): a Claude
  skill that applies the standard when working on a project that has adopted it.
- [`CHANGELOG.md`](CHANGELOG.md): changes to the standard.

Planned: a template that creates and updates project repositories from the standard, and
the shared check each project's CI runs (section 8).

## Using it

1. A project adopts the standard by adding a `.standard-version` file with the version it
   follows. That file is the only record; projects without it aren't bound by the
   standard.
2. When the standard changes, its version changes (section 8), and projects adopt the new
   version through a reviewed update.

## License

[Apache License 2.0](LICENSE). Provided "as is", without warranty and without liability.
