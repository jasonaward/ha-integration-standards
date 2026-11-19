---
name: ha-integration-standards
description: Use when working on a jasonaward Home Assistant integration that has adopted the shared standard (a .standard-version file in the repository), so its README, changelog, versions, manifest, diagnostics, brand and repository files follow it.
---

# Home Assistant integration standard

**These projects aim for enterprise quality but remain hobby projects: offered as is, to
be used at your own risk.**

A public, opt-in standard for jasonaward's hobby Home Assistant integrations: projects by
a long-time software developer turned engineering leader, built to learn when and how
AI-assisted and AI-written code can be applied well, held to the bar of large-scale and
critical systems, and shared through HACS as custom repositories with no warranty. It
covers what users and contributors see, not how code is written. It describes the
maintainer's intended practices; it isn't a warranty or commitment to users.

The full text is `STANDARD.md` in `jasonaward/ha-integration-standards`. When it's
available, read it and follow it over this summary, which is for version **0.1.0**.

## When working on a project

1. Look for `.standard-version` in the repository.
   - Present: apply that version. If the standard is newer, say so and offer to update.
   - Absent: the project hasn't adopted it. Don't apply it or point out differences
     unless asked; you may offer once to adopt it or use a part of it.
2. Before finishing a change, check it against the rules below for what it touches, and
   fix or mention anything that doesn't meet them.
3. Work out version numbers from section 4; never invent one.
4. Never put real personal data in code, tests, docs, examples or commits. No traffic
   recordings or instructions for intercepting a vendor's app.
5. Public text describes aims and process, not guarantees ("designed to", "aims for"),
   unless a test checks the statement.

## Home Assistant and HACS first (section 2)

- `quality_scale.yaml`: every rule `done`, `todo` or `exempt` (with a comment). Aim
  Platinum; floor Gold for releases (betas may have `todo`); a Platinum rule is `exempt`
  only when an uncontrolled library prevents it, named in the comment.
- README follows Home Assistant's page structure and style guide (section 5).
- Manifest: `codeowners` `@jasonaward`; documentation and issue links to
  `github.com/jasonaward/ha-<domain>`; `loggers`; pinned `requirements` or `[]`.
- HACS: public repository with description and topics (`home-assistant`, `hacs`,
  `home-assistant-integration`, the product); GitHub releases; `hacs.json` with `name`,
  `homeassistant`, `render_readme`, `zip_release` and `<domain>.zip`.
- Brand images in `brand/`: PNG, trimmed, transparent; icon 256 and 512; logo shortest
  side 256 and 512; `dark_` versions; shared flat style; no other company's marks; SVG
  sources in `docs/brand/`.
- CI: tests on the minimum and latest Home Assistant, coverage above 95% per module,
  ruff (with security rules), `mypy --strict`, hassfest, HACS validation, CodeQL, the
  standard's check. Minimum Home Assistant version raised only in a MINOR, never to a
  release under 3 months old without need.

## Identity (section 3)

Owner `jasonaward`; author Jason Ward (`Copyright <year> Jason Ward and contributors`);
commits use GitHub's noreply address; the only public email is `opensource@` on the
owner's domain. Repository `ha-<domain>` with hyphens; name ends `(unofficial)` for
another company's product; README title "<name> for Home Assistant".

## Versions, changelog, releases (section 4)

- SemVer in PEP 440 form: `0.4.2`, beta `0.4.2b1`, tag `v0.4.2b1`. No hyphens, alphas,
  release candidates, dev or local versions. Work in progress: stay at `0.x`, no `1.0.0`.
- MINOR: feature, entity, option, device, raised minimum Home Assistant, or anything
  users must act on (changelog **Action needed:**). PATCH: fixes, wording, docs.
- First release `0.1.0b1`; betas raise `bN`; a good beta is released without the suffix.
  Same number in manifest, library `__version__`, changelog heading; tag adds `v`.
  Never reuse or lower a version.
- Changelog: newest first, `## 0.1.0b1 (2026-11-19, beta)`, user-facing bullets.
- Releases: GitHub releases built by CI from the tag, notes = the changelog section (versions checked, tests, zip,
  provenance attestation); betas marked pre-release. A retired project says so and its repository is archived. A broken release: fix
  forward fast;
  the changelog marks it and says how to go back with HACS **Redownload**.

## README (section 5)

Order: title and introduction; notices (hobby project aiming for enterprise quality,
use at your own risk, work in progress; unofficial, using the vendor's service the way
its app does, maybe not permitted by its terms, user responsible for their account; no
warranty or liability); Use cases; Supported devices (Tested, Likely to work) and Unsupported
devices; Prerequisites; Installation (HACS with the two My Home Assistant buttons,
Manual); Configuration; Configuration options; Supported functionality; Actions,
Triggers, Conditions if any; Examples; Data updates; Load on <service>; Security and
privacy; Safety if any; Known limitations; Troubleshooting (ending Reporting a problem);
Removing the integration (Troubleshooting and Likely to work link CONTRIBUTING's
Reporting guide); Development (starting with the how-it's-made statement);
Acknowledgments if any; License and disclaimer. Standard text for the notices, the
how-it's-made statement, the install buttons and the license section is in STANDARD.md
5.2, 5.6, 5.7 and 5.8. Style: Home Assistant's guide (American English, serial comma,
sentence case, bold UI with `>` between steps, "select", `-` lists, no "e.g.").

## Beyond Home Assistant's rules (section 6)

- Diagnostics: an `about` line, version, health summary, options in use and changed,
  entities with state, raw values; leave out credentials, tokens, full IDs (keep last
  four), serials, MACs, Wi-Fi names, owner names, locations; allowlist where possible.
- Logs: never secrets at any level (tested); IDs shortened; no emails.
- Repository and history: no real personal data; `.gitignore` excludes diagnostics
  downloads, traffic recordings, logs and secrets files.
- Rules are musts unless marked _should_.
- Security: `SECURITY.md` and private reporting on; fixed vulnerabilities published as
  GitHub security advisories; actions pinned to SHAs and kept current by Dependabot;
  read-only workflow permissions; CodeQL, Dependabot alerts, secret scanning with push
  protection; `main` protected with required checks; dependencies avoided or pinned and
  audited; libraries bundled, on PyPI only when needed and only via trusted publishing.
- Vendors: use only what the vendor's app already uses publicly; never vendor secret
  keys or bypassed protections; respond promptly to objections and stop publishing if
  asked. "Where data goes" notes the vendor's own privacy policy governs its data use.
- Users' setups: entity IDs change only by opt-in; removed entities go after a stated
  grace period; whole numbers for settings set in whole units, one decimal for measured
  temperatures; automatic migrations; vendor service changes raise one repair issue or
  warning.

## Repository files (section 7)

`custom_components/<domain>/`, `README.md`, `CHANGELOG.md`, `LICENSE` (Apache 2.0),
`NOTICE`, `SECURITY.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 3.0, contact
`opensource@`), `CONTRIBUTING.md` (Reporting section: bugs, new or untested models and
what to test, security privately; AI-assisted contributions welcome if disclosed, same
review), `.github/pull_request_template.md`, `.github/dependabot.yml`, `hacs.json`,
`.github/ISSUE_TEMPLATE/` (bug form with a "new or untested model" checkbox, blank
issues off), `.github/workflows/`, `docs/brand/`, `.gitignore`,
`.standard-version`.
