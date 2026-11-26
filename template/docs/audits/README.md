# Audit reports

Every release, betas included, follows an audit by a reviewer independent of the author:
a person, or an AI agent working without the author's context. The audit checks the
project against every rule of Home Assistant's integration quality scale and of the
[integration standard](https://github.com/jasonaward/ha-integration-standards) (4.3.4),
each against its current text, with evidence for every verdict.

The report for a version is `<version>.md` in this folder, for example `0.1.0b1.md`. The
release workflow refuses to release a version without one.
