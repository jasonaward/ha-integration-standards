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
critical systems, and shared as custom repositories (Home Assistant's Marketplace from
2026.11, HACS before) with no warranty. It covers what users and contributors see, not
how code is written. It describes the maintainer's intended practices; it isn't a
warranty or commitment to users.

The full text is `STANDARD.md` in `jasonaward/ha-integration-standards`. When it's
available, read it and follow it over this summary, which is for version **0.2.0**.

## When working on a project

Every rule is a must unless marked _should_.

1. Look for `.standard-version` in the repository.
   - Present: apply that version. If the standard is newer, say so and offer to update.
   - Absent: the project hasn't adopted it. Don't apply it or point out differences
     unless asked; you may offer once to adopt it or use a part of it.
2. Before finishing a change, check it against the rules below for what it touches, and
   fix or mention anything that doesn't meet them. Run the shared check
   (`check/check_standard.py` in the standard's repository). Start new projects from its
   Copier template.
3. Read Home Assistant's rules in their current text before claiming one is met
   (contributors.home-assistant.io; the old developers site is frozen). Never mark a
   quality-scale rule `done` on a technicality, and back every statement of fact with
   code, a test or a source.
4. Work out version numbers from section 4; never invent one.
5. Never put real personal data in code, tests, docs, examples or commits. No traffic
   recordings or instructions for intercepting a vendor's app.
6. Commits: the maintainer's noreply address only; no co-author lines, session links or
   other email addresses in commit messages.
7. Public text describes aims and process, not guarantees ("designed to", "aims for"),
   unless a test checks the statement.

## Home Assistant, the Marketplace and HACS first (section 2)

- `quality_scale.yaml`: all 54 rules (November 2026, including `docs-triggers` and
  `docs-conditions`), each `done`, `todo` or `exempt`, with a comment for `todo` and
  `exempt`; `exempt` only under the rule's own exception. Aim Platinum; floor Gold for
  releases (betas may have `todo`).
- README follows Home Assistant's integration page structure and style guide, adapted for
  GitHub (section 5).
- Manifest: `codeowners` `@jasonaward`; documentation and issue links to
  `github.com/jasonaward/ha-<domain>`; `requirements` pinned with `==`; `loggers` naming
  the requirements' loggers (Home Assistant's definition).
- Marketplace and HACS (same catalog, `hacs.json` and layout): public repository with a
  description, issues on, topics (`home-assistant`, `hacs`, `home-assistant-integration`,
  the product); GitHub releases; `hacs.json` with `name`, `homeassistant` (the minimum),
  `zip_release` and `<domain>.zip` (no `render_readme`).
- Brand images in `custom_components/<domain>/brand/`: `icon.png` 256×256, `icon@2x.png`
  512×512, `dark_` versions; never Home Assistant's or another company's marks; SVG
  sources in `docs/brand/`. _Should_: logos, one flat style, logo text in Inter.
- Translations: a complete `translations/en.json`; no `strings.json` (Home Assistant
  doesn't use it for custom integrations).
- No polling-interval option (`appropriate-polling`): the project fixes the interval;
  users who want less or more use an automation with **Update entity**.
- CI: tests with Home Assistant's own `pytest-homeassistant` on the latest stable release
  (and, _should_, weekly on the latest beta); on the minimum version, with the retired
  `pytest-homeassistant-custom-component` build if the minimum is before 2026.11, helpers
  imported through `tests/ha_test.py`; above 95% line coverage in every module; an
  autouse fixture failing tests when Home Assistant reports a deprecated use by the
  project's code; ruff (with security rules), `mypy --strict`, hassfest, HACS validation,
  CodeQL, the standard's check. The README claims only the versions CI tested.
- Minimum Home Assistant version (`hacs.json` and Prerequisites): chosen for reach and
  upkeep, _should_ be no older than about 12 months and not under 3 months old unless a
  needed feature requires it (check Home Assistant's analytics); code for older versions
  kept small, labeled with the versions it's for, and tested; raising it is a MINOR with
  **Action needed:**.

## Identity (section 3)

Owner `jasonaward`; author Jason Ward (`Copyright <year> Jason Ward and contributors`);
commits use GitHub's noreply address, with no co-author lines; the only public email is
`opensource@` on the owner's domain. Repository `ha-<domain>` with hyphens; name ends
`(unofficial)` for another company's product; README title "<name> for Home Assistant".

## Versions, changelog, releases (section 4)

- SemVer in PEP 440 form: `0.4.2`, beta `0.4.2b1`, tag `v0.4.2b1`. No hyphens, alphas,
  release candidates, dev or local versions. Work in progress: stay at `0.x`, no `1.0.0`.
- MINOR: feature, entity, option, device, raised minimum Home Assistant, or anything
  users must act on (**Action needed:**). PATCH: fixes, wording, docs.
- First release `0.1.0b1`; betas raise `bN`; a good beta is released without the suffix.
  Manifest version and changelog heading match; tag adds `v`. A version is published when
  its tag exists, and is never reused, changed or lowered.
- Changelog: newest first, `## 0.1.0b1 (2026-11-19, beta)`, bullets only, each starting
  with the bolded thing it affects; an **Action needed:** bullet comes first (it's shown
  as the update's release notes).
- Releases: started by the maintainer from the Actions tab with the version; CI runs the
  standard's release check, the tests, builds and attests the zip, and creates the tag
  and the release, with that version's changelog section as notes; betas marked
  pre-release. Before every release, betas included, an audit by a reviewer independent
  of the author checks every quality-scale rule and every rule of the standard against
  their current text, with evidence; the report is `docs/audits/<version>.md`.
- Betas reach Marketplace users who turn on pre-releases for the repository (**Include
  pre-releases** in its menu or its **Pre-release** switch, by Home Assistant version) or
  pick one under **Install another version**; HACS users through the repository's
  pre-release switch. A broken release: fix forward fast; the changelog says how to go
  back (Marketplace: restore a backup, or **Install another version**; HACS:
  **Redownload**). A retired project says so in its README and is archived.

## README (section 5)

Order: title and introduction (with a link to the manufacturer's or service's website);
notices (hobby project aiming for enterprise quality, use at your own risk, work in
progress; unofficial, using the vendor's service the way its app does, maybe not
permitted by its terms, user responsible for their account; no warranty or liability);
Use cases; Supported devices (Tested, Likely to work, not tested) and Unsupported
devices; Prerequisites; Installation (Marketplace or HACS, with the two My Home Assistant
buttons and steps for both, then Manual); Configuration; Configuration options;
Supported functionality; Triggers, Conditions, Actions if any (a `###` per item); Examples;
Data updates; Load on <service> (fixed read interval, minimum time between reads, how to
read less often); Security and privacy; Safety if any; Known limitations; Troubleshooting
(`### Symptom: ...` with cause and fix, then diagnostics and logs, ending Reporting a
problem); Removing the integration; Development (starting with the how-it's-made
statement); Acknowledgments if any; License and disclaimer. Troubleshooting and Likely to
work link CONTRIBUTING's Reporting guide. Standard text for the notices, the how-it's-made
statement, the install buttons and the license section is in STANDARD.md 5.2, 5.6, 5.7
and 5.8. Style: Home Assistant's guide (American English, serial comma, sentence case,
bold UI with `>` between steps, "select", `-` lists, no "e.g."); for GitHub, no Liquid
tags.

## Beyond Home Assistant's rules (section 6)

- Diagnostics: an `about` line, version, health summary, options in use and changed,
  entities with state, raw values; leave out credentials, tokens, full IDs (keep last
  four), serials, MACs, Wi-Fi names, owner names, locations; allowlist where possible.
- Logs: never secrets at any level (tested); IDs shortened; no emails.
- Repository and history: no real personal data; earlier private history never pushed;
  `.gitignore` excludes diagnostics downloads, traffic recordings, logs and secrets files.
- Security: `SECURITY.md` and private reporting on; fixed vulnerabilities published as
  GitHub security advisories; actions pinned to SHAs and kept current by Dependabot;
  read-only workflow permissions; CodeQL, Dependabot alerts, secret scanning with push
  protection; `main` protected with required checks; requirements and test requirements
  pinned exactly.
- Client libraries (6.4): code that talks to a device or service lives in `py<name>`, its
  own public repository, Apache 2.0, no Home Assistant imports, async with the caller's
  `aiohttp` session, fully typed (`py.typed`), its own changelog and tests, released to
  PyPI by CI with trusted publishing and attestations; the integration pins it with `==`
  and lists its logger; a library change is released before the integration that needs
  it.
- Vendors: use only what the vendor's app already uses publicly; never vendor secret
  keys or bypassed protections; respond promptly to objections and stop publishing if
  asked; _should_ enforce a minimum time between requests whatever users or automations
  ask, stated in the README. "Where data goes" notes the vendor's own privacy policy
  governs its data use.
- Users' setups: entity IDs change only by opt-in; removed entities go after a stated
  grace period; whole numbers for settings set in whole units, one decimal for measured
  temperatures, whole watts; automatic migrations; vendor service changes raise one
  repair issue or warning; device pages show only identifiers known to be right.

## Repository files (section 7)

`custom_components/<domain>/` (with `brand/`, `quality_scale.yaml`,
`translations/en.json`), `README.md`, `CHANGELOG.md`, `LICENSE` (Apache 2.0), `NOTICE`,
`SECURITY.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 3.0, contact `opensource@`),
`CONTRIBUTING.md` (Reporting section: bugs, new or untested models and what to test,
security privately; AI-assisted contributions welcome if disclosed, same review),
`.github/pull_request_template.md`, `.github/dependabot.yml`, `hacs.json`,
`.github/ISSUE_TEMPLATE/` (bug form with a "new or untested model" checkbox, blank issues
off), `.github/workflows/` (tests, validation, CodeQL, the standard's check, release),
`requirements_test.txt` (pinned), `docs/audits/`, `docs/brand/`, `.gitignore`,
`.standard-version`.
