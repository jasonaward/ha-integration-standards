# Home Assistant integration standard

**Version 0.2.0** · Owner: [@jasonaward](https://github.com/jasonaward)

How a hobby Home Assistant integration that adopts this standard is documented,
versioned, released and presented. It covers what users and contributors see, not how
the code is written.

This standard, throughout, describes how the maintainer intends to build and document
these projects. It isn't a warranty, guarantee or commitment to any user. The software is
provided under the Apache License 2.0, without warranty and without liability.

- Every rule is a **must**, enforced by the standard's checks where they can, unless it's
  marked _should_.
- A _should_ rule is expected; a project skips it only with the reason written in the
  repository (usually `quality_scale.yaml` or the README).
- Text marked _Standard text_ is used word for word, with only the `<placeholders>`
  filled in.

## 1. Why

**These projects aim for enterprise quality but remain hobby projects: offered as is, to
be used at your own risk.**

They're personal projects by a long-time software developer turned engineering leader,
built to learn when and how AI-assisted and AI-written code can be applied well, and to
keep evaluating it as the technology improves.

They aim for the bar of large-scale and critical systems: standards set and followed,
thorough testing, and security and privacy by design. Part of the purpose is to see
whether AI-written code can meet or exceed that bar, and what it takes to get there.

They're shared as custom repositories, installed through Home Assistant's Marketplace
(built in from Home Assistant 2026.11) or, on older versions, HACS. There's no plan to
submit them to Home Assistant or to the Marketplace's catalog; if that changes, a project
would go through their review process at the time.

**Opt-in.** The standard applies only to a project with a `.standard-version` file in its
repository, giving the version it follows. That file is the only record of adoption.
Other projects aren't bound by it and may borrow any part of it. A project stops
following it by removing the file and saying so in its README.

**Public**, so contributors can read the rules their changes are checked against, and so
public integration repositories can run its shared check.

## 2. Home Assistant, the Marketplace and HACS first

Home Assistant's own rules come first, including those of its Marketplace and of HACS,
which the Marketplace grew out of and shares its catalog, `hacs.json` and layout with.
This standard doesn't restate them and never contradicts them. Section 6 adds only what
they don't cover.

1. **Quality scale.** `custom_components/<domain>/quality_scale.yaml` lists every rule of
   Home Assistant's
   [integration quality scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules)
   as `done`, `todo` or `exempt`, with a comment for each `todo` and `exempt`.
   - Aim: **Platinum**. Floor: **Gold** for a release (a version without `b`); betas may
     have rules marked `todo`.
   - A Platinum rule may be `exempt` only when a library the project doesn't control
     prevents it; the comment names the library.
2. **Documentation.** READMEs follow Home Assistant's
   [integration page structure](https://developers.home-assistant.io/docs/documenting/integration-docs-examples)
   and [style guide](https://developers.home-assistant.io/docs/documenting/general-style-guide),
   as set out in section 5.
3. **Manifest.** `manifest.json` follows Home Assistant's
   [manifest rules](https://developers.home-assistant.io/docs/creating_integration_manifest),
   with: `codeowners` `["@jasonaward"]`; `documentation`
   `https://github.com/jasonaward/ha-<domain>`; `issue_tracker` the same with `/issues`;
   `loggers` naming the integration's own loggers; `requirements` pinned exactly, or `[]`.
4. **Marketplace and HACS.** The repository follows the Marketplace's
   [publishing guides](https://contributors.home-assistant.io/marketplace/) and HACS's
   [publishing requirements](https://hacs.xyz/docs/publish/start). In addition: topics
   include `home-assistant`, `hacs`, `home-assistant-integration` and the product;
   releases are zipped (`hacs.json`: `name`, `zip_release: true`,
   `filename: "<domain>.zip"`, `render_readme: true`, and `homeassistant` set to the
   minimum version, 7).
5. **Brand images** follow Home Assistant's
   [brand image rules](https://developers.home-assistant.io/docs/core/integration/brand_images),
   in `custom_components/<domain>/brand/`, with `dark_` versions. In addition: one flat
   style across all projects, no text in the icon, the logo's text in Inter, never another
   company's logo, wordmark, product photo or colors, and SVG sources in `docs/brand/`.
   The shared style and font are _should_.
6. **Tests and checks.** Home Assistant's `test-coverage` rule (above 95% per module),
   hassfest and HACS validation run in CI. In addition: tests on both the minimum and the
   latest Home Assistant, with branch coverage, that fail when Home Assistant reports a
   deprecated use by the project's own code; `ruff check` with its security rules and
   `ruff format --check`; `mypy --strict`; CodeQL; and this standard's check (section 8).
   _Should_: a weekly scheduled run against Home Assistant's upcoming beta, to catch
   breaking changes before users meet them.
7. **Minimum Home Assistant version.** Declared in `hacs.json` as `homeassistant`, where
   the Marketplace uses it to offer each user the newest release that supports their
   version, and in the README's Prerequisites. It's chosen for reach and upkeep:
   - _Should_: no older than about 12 months, and never a release less than 3 months old
     unless a needed feature requires it. The share of installations on each version, in
     [Home Assistant's analytics](https://analytics.home-assistant.io/), is checked when
     choosing.
   - Code that exists only for versions older than the latest is kept small, says in a
     comment which versions it's for, and is covered by the tests on the minimum version.
   - Raising it is a MINOR version with an **Action needed:** note.

## 3. Identity and naming

1. GitHub owner **`jasonaward`**; every link and install address uses it.
2. Author **Jason Ward**: in copyright lines (`Copyright <year> Jason Ward and
   contributors`), the commit author name and package metadata.
3. Email: commits use GitHub's private noreply address. The only public address is
   `opensource@` on the owner's domain (written `opensource@<owner domain>` here), used
   for the GitHub profile, package metadata and as a second option in `SECURITY.md`. No
   other email address appears in any file or commit.
4. Repository **`ha-<domain>`**, with hyphens in place of underscores: the domain
   `acme_heater` is in `ha-acme-heater`.
5. Integration name: the product's name as users know it, ending in **`(unofficial)`**
   when it's another company's product, for example "Acme Heater (unofficial)". The
   README title is that name followed by "for Home Assistant".
6. Other companies' names are used only to say what the integration works with.

## 4. Versions, changelog and releases

### 4.1 Versions

[Semantic Versioning 2.0.0](https://semver.org/), written in
[PEP 440](https://peps.python.org/pep-0440/) form, which Home Assistant, HACS and PyPI
all accept.

- Release `0.4.2`; beta `0.4.2b1`; git tag `v0.4.2b1`. Never `0.1.0-beta.1`; no alpha,
  release candidate, development or local versions.
- **Work in progress.** Projects stay at `0.x`, where Semantic Versioning allows anything
  to change; there's no `1.0.0`.
- **MINOR** (and PATCH back to 0): a new feature, entity, action, option or supported
  device; a raised minimum Home Assistant version; or anything users must act on, which
  the changelog marks **Action needed:**. **PATCH**: fixes, wording, translations,
  documentation.
- **Stages.** The first release is `0.1.0b1`. Each test build raises the beta number. A
  beta that worked is released unchanged without the suffix (`0.1.0b3` becomes `0.1.0`);
  the next beta starts from the next version (`0.2.0b1` or `0.1.1b1`).
- **One number.** `manifest.json` `version`, the bundled library's `__version__` and the
  changelog heading match; the tag adds `v`. Each project versions independently.
- A published version is never reused, changed or lowered.
- **Adopting the standard in an existing project.** One not yet published for others
  restarts as a new repository at `0.1.0b1`, from one commit that meets the standard; its
  old repository becomes a private archive (`ha-<domain>-archive`). Existing installs are
  removed in the Marketplace or HACS and installed again; config entries and entity IDs are kept as long as
  the domain doesn't change. A project already published adopts the standard with its
  next version instead.

### 4.2 Changelog

`CHANGELOG.md`, newest first, headed `## 0.1.0b1 (2026-11-19, beta)` or
`## 0.2.0 (2027-01-10)`, with an optional `## Unreleased` at the top. Written for users:
one bullet per change, starting with the bolded thing it affects. Anything users must act
on starts with **Action needed:**, says what to do, and comes first in its version's
section: the Marketplace and HACS show the section as the update's release notes.

### 4.3 Releases

1. Every release is a published GitHub release, built by CI from the tag, never uploaded
   by hand. The workflow checks that tag, manifest, library and changelog agree, runs the
   tests, builds `<domain>.zip`, attests its build provenance, and attaches it. The
   release notes are that version's changelog section.
2. Betas are marked **pre-release**, so the Marketplace offers them only to users who
   turned on the repository's **Pre-release** switch, and HACS only to users who turned on
   beta versions.
3. **A broken release** is fixed by a newer one as soon as possible. Until then, the
   changelog marks the broken version and says how to go back: choose the previous
   version from the repository's menu in the Marketplace, or **Redownload** in HACS.

## 5. README

### 5.1 Sections

Headings in this order. Those marked _if applicable_ may be left out; the rest must be
present. Where a heading carries out a quality-scale rule, the rule is in brackets.

1. `# <Integration name> for Home Assistant`, then an introduction: what the product is,
   what the integration does, and how it connects (`docs-high-level-description`).
2. Notices block (5.2).
3. `## Use cases`: concrete examples (`docs-use-cases`).
4. `## Supported devices`, with `### Tested` and `### Likely to work, not tested`, then
   `## Unsupported devices` (5.3; `docs-supported-devices`).
5. `## Prerequisites`: an account, the device set up in the vendor's app, the minimum
   Home Assistant version (`docs-installation-instructions`).
6. `## Installation`: `### Marketplace or HACS`, starting with the install buttons
   (5.7), then the steps for the Marketplace (Home Assistant 2026.11 and later) and for
   HACS (earlier versions), including how to get betas; then `### Manual`; _if
   applicable_ `### Switching from <other integration>`.
7. `## Configuration`: setup steps and the values asked for
   (`docs-installation-parameters`).
8. `## Configuration options`: each option, its default and effect, plus
   re-authentication and reconfiguration (`docs-configuration-parameters`).
9. `## Supported functionality`: entities by platform, attributes, the device page
   (`docs-supported-functions`).
10. `## Actions`, `## Triggers`, `## Conditions`, _if applicable_, each with its fields
    and an example (`docs-actions`).
11. `## Examples`: automations in YAML (`docs-examples`).
12. `## Data updates`: how often, what triggers a read, what users see when the service is
    down (`docs-data-update`).
13. `## Load on <service>` (5.5), for integrations that use a vendor's service.
14. `## Security and privacy` (5.4).
15. `## Safety` _if applicable_, named after the equipment, for example "Pool safety",
    for equipment that can cause damage or injury when misused.
16. `## Known limitations` (`docs-known-limitations`).
17. `## Troubleshooting`, ending with `### Reporting a problem`: ask for diagnostics and
    the device model, link the issue tracker and the reporting guide in `CONTRIBUTING.md`,
    and remind people to look over diagnostics before posting (`docs-troubleshooting`).
18. `## Removing the integration`: the steps, and what's left behind
    (`docs-removal-instructions`).
19. `## Development`: starting with how it's made and maintained (5.6), then how to run
    tests, lint and type checks.
20. `## Acknowledgments` _if applicable_.
21. `## License and disclaimer` (5.8).

### 5.2 Notices block

Under the introduction, as a quote block. The unofficial notice is left out for the
maintainer's own products; for a local device with no vendor service, its second and
third sentences are left out.

> _Standard text_
>
> ```markdown
> > **Hobby project, aiming for enterprise quality (<version>).** Built and tested to a
> > professional standard, but a personal project, offered as is: use it at your own risk.
> > It's a work in progress, and an update may change entities or settings; check the
> > changelog before updating. <What it's used with, for example "It's used with the
> > maintainer's own heater.">
> >
> > **Unofficial.** Not affiliated with, endorsed by, or supported by <Company>. It uses
> > <Company>'s service the way <Company>'s app does, not through an official or public
> > interface, so it can stop working whenever <Company> changes that service. Using it
> > may not be permitted by <Company>'s terms of service; you're responsible for your use
> > of your own account. <Trademarks> are trademarks of <Company>, used here only to say
> > which <device> this works with.
> >
> > **No warranty, no liability.** Provided "as is" under the Apache License 2.0. You use
> > it at your own risk; the authors aren't liable for any damage to equipment, property,
> > or anything else. See [License and disclaimer](#license-and-disclaimer).
> ```

### 5.3 Supported and unsupported devices

- `### Tested`: the exact models (and sizes or firmware where it matters) the maintainer
  uses.
- `### Likely to work, not tested`: each with the reason, for example "the same device
  type in the vendor's app", and an invitation to report results, linking the reporting
  guide in `CONTRIBUTING.md`.
- `## Unsupported devices`: what people might expect to work and doesn't, and what to
  use instead.

### 5.4 Security and privacy

Bullets with these bold leads, describing what the integration does. Where a statement
is checked by tests (for example, that passwords aren't logged), it's stated as fact;
otherwise it's stated as what the integration is designed to do.

- **What's stored**: credentials and where; what's kept only in memory; a reminder to
  protect backups.
- **Where data goes**: every service contacted, and that nothing is sent elsewhere (no
  analytics, no telemetry), if that's so. For a vendor's service, add: "What <Company>
  does with data it receives is governed by its own privacy policy, as when using its
  app; this integration doesn't control or know it."
- **What it can change**: every kind of change it can make, and what it doesn't change.
- **Effect on the vendor's app**, _if applicable_.
- **Logs** and **Diagnostics**: what's left out, and to look diagnostics over before
  posting them.
- **Code**: dependencies, how releases are built, and a link to `SECURITY.md`.

### 5.5 Load on the service

The project's own policy, chosen for its service: the default read interval and the range
users may set; what happens on errors; and limits on any heavier requests.

### 5.6 How it's made and maintained

The Development section starts with this statement. For a project where the maintainer
also writes code, its first sentence is "This integration is developed with AI
assistance, as part of learning when and how AI-assisted code can be applied well, and
of evaluating it as the technology improves."

> _Standard text_
>
> ```markdown
> All of the code in this integration is written by AI, as part of learning when and how
> AI-written code can be applied well, and of evaluating it as the technology improves.
> The maintainer directs the work and makes the design decisions. Changes go through a
> lengthy, iterative process of testing, verification, and validation, with real devices
> where applicable and with accounts and services the maintainer uses, and an
> AI-assisted security review against Home Assistant's integration quality scale, the
> maintainer's [integration standard](https://github.com/jasonaward/ha-integration-standards),
> and automated security scanning.
>
> It's maintained as well as possible while the maintainer uses these devices and
> services, and updated as needed to keep it working; if that changes, this README will
> say so. Contributions are welcome: bug reports, ideas, and pull requests in the
> [issue tracker](https://github.com/jasonaward/ha-<domain>/issues), and security
> concerns through [private reporting](SECURITY.md). All of the code is open for anyone
> to evaluate.
>
> This describes the maintainer's aims and process, not a guarantee; see
> [License and disclaimer](#license-and-disclaimer).
> ```

If the maintainer stops maintaining a project, the second paragraph is replaced with
"This integration is no longer actively maintained." and, if so, "Pull requests are still
reviewed." A project retired completely says so in its README, then its GitHub
repository is archived (read-only).

### 5.7 Install buttons

The Marketplace or HACS steps start with two [My Home Assistant](https://my.home-assistant.io/)
buttons, followed by numbered steps for users without them. The first button opens the
repository in the Marketplace or HACS, whichever the user has.
_Should_: no other badges.

> _Standard text_
>
> ```markdown
> [![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jasonaward&repository=ha-<domain>&category=integration)
>
> [![Open your Home Assistant instance and start setting up this integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=<domain>)
> ```

### 5.8 License and disclaimer

> _Standard text_
>
> ```markdown
> ## License and disclaimer
>
> Licensed under the [Apache License, Version 2.0](LICENSE). See [NOTICE](NOTICE) for
> attributions.
>
> **No warranty.** This software is provided "AS IS", without warranties or conditions of
> any kind, express or implied, including fitness for a particular purpose.
>
> **No liability.** In no event shall the authors or contributors be liable for any
> damages (including damage to <equipment>, property, or any other loss) arising from
> using or being unable to use this software, even if advised of the possibility of such
> damage. See sections 7 and 8 of the license.
>
> <Trademarks> are trademarks of <Company>. This project is not affiliated with,
> endorsed by, or supported by <Company>. Don't contact <Company> support about it.
> ```

The last paragraph is left out for the maintainer's own products.

### 5.9 Writing style

Home Assistant's style guide applies to the README, changelog, `docs/` and all
user-facing text. In particular: American English; serial comma; sentence-style
capitalization; UI elements in **bold** with `>` between menu steps; "select", not
"click"; `backticks` for file names, entity IDs and values; `-` for lists; lists over
tables; no "e.g."; no Liquid tags. Statements about quality, security or maintenance
describe aims and process, not guarantees. Examples use made-up values only.

## 6. Beyond Home Assistant's rules

### 6.1 Privacy

1. **Diagnostics** start with an `about` line saying what's left out and to look it over
   before posting, then include: the integration version; a health summary (status, last
   success, last error, failures in a row, update interval, timings); the options in use
   and which were changed; each device's entities with their state; raw values with
   unknown fields listed.
2. Diagnostics leave out email, usernames, passwords, tokens, keys, full device IDs (the
   last four characters are kept), serial numbers, MAC addresses, Wi-Fi names, account or
   owner names, addresses and coordinates, using an allowlist where possible.
3. **Logs** never contain passwords, tokens, keys or credentials at any level, checked by
   a test that runs sign-in and requests with debug logging on. Device IDs are shortened;
   emails aren't logged. _Should_: debug lines say what was requested, the result and how
   long it took.
4. **Repository and history** contain no real personal data: emails, device IDs, serial
   numbers, MAC addresses, Wi-Fi names, names, addresses or coordinates. Tests and
   examples use made-up values. No recordings of network traffic, and no instructions for
   intercepting a vendor's app. Before a repository goes public, its whole history passes
   the privacy check.
5. `.gitignore` excludes `answers.json`, `config_entry-*.json`, `*.har`, `*.flow`,
   `*.pcap`, `*.log`, `secrets.yaml` and `.env`.

### 6.2 Security

1. `SECURITY.md` says how to report a vulnerability privately (GitHub's **Report a
   vulnerability**), when to expect a reply, what's in and out of scope, and what never
   to post. Private vulnerability reporting is turned on. After a vulnerability is fixed,
   it's published as a GitHub security advisory and noted in the changelog.
2. Workflow actions are pinned to full commit SHAs, kept current by Dependabot version
   updates for actions and Python dependencies. Workflows have read-only permissions by
   default, with each job asking only for what it needs.
3. Repository settings: CodeQL scanning, Dependabot alerts, and secret scanning with push
   protection are on. `main` is protected: no force pushes or deletion, and pull requests
   must pass the required checks before merging.
4. **Dependencies:** none beyond Home Assistant's own where possible; any requirement is
   pinned exactly and checked for known vulnerabilities. A library written for a project
   lives in the same repository with the same version, bundled in the integration; it's
   published to PyPI only when something else needs it, and then only through trusted
   publishing. Reference libraries used only by tests go in `requirements_test.txt`.
5. **Vendors.** A project uses only what a vendor's own app already uses publicly
   (addresses, identifiers); it never includes a vendor's secret keys or bypasses
   protections. If a vendor objects to a project, the maintainer responds promptly and,
   if asked, stops publishing it.

### 6.3 Users' setups

1. Entity IDs never change on their own; a rename that changes one is opt-in, and says
   which automations and scripts use the old ID.
2. Entities removed on the device are removed after a grace period the README states.
3. _Should_: display precision of whole numbers for values set in whole units (a
   setting of 45 °F shows 45), one decimal for measured temperatures, and whole watts for
   power.
4. Config entry and option changes are migrated automatically, never by asking users to
   set up again. A removed option is still read, and dropped on migration.
5. **Vendor service changes.** For a cloud service, an unexpected response raises a repair
   issue or a single warning, not repeated errors, and the README's known limitations say
   the service may change without notice.

## 7. Repository files

| Path | Contents |
|---|---|
| `custom_components/<domain>/` | The integration (section 2), with `brand/`, `quality_scale.yaml`, `strings.json` and `translations/en.json`. |
| `README.md`, `CHANGELOG.md` | Sections 4.2 and 5. |
| `LICENSE` | The Apache License 2.0, unmodified. |
| `NOTICE` | The project name; `Copyright <year> Jason Ward and contributors`; the "AS IS" and no-liability lines; credit for adapted code (project, link, license, file); the trademark paragraph where it applies; and that the brand images are original. |
| `SECURITY.md` | Section 6.2. |
| `CONTRIBUTING.md` | A **Reporting** section (below); how to set up, test and lint; the rules that matter most (no secrets in logs, no new dependencies without discussion, be gentle with the service, text in `strings.json`, a changelog line); that contributions are licensed under the Apache License 2.0. |
| `hacs.json` | Section 2. |
| `CODE_OF_CONDUCT.md` | The [Contributor Covenant 3.0](https://www.contributor-covenant.org/), with `opensource@<owner domain>` as the reporting contact and its enforcement section set for a single maintainer. |
| `.github/pull_request_template.md` | A short checklist: tests added or updated, a changelog line, no secrets or personal data, AI assistance disclosed, the standard followed. |
| `.github/dependabot.yml` | Version updates for GitHub Actions and Python dependencies (section 6.2). |
| `.github/ISSUE_TEMPLATE/` | A bug report form (Home Assistant version, integration version, device model and firmware, a "new or untested model" checkbox, what happened, diagnostics, a privacy reminder) and `config.yml` turning off blank issues and linking to private security reporting. |
| `.github/workflows/` | Tests, validation, CodeQL and release (sections 2 and 4.3). |
| `docs/brand/` | SVG sources for the brand images. |
| `.gitignore` | Section 6.1. |
| `.standard-version` | The version of this standard the project follows. |

The **Reporting** section of `CONTRIBUTING.md` covers:

- **Bugs**: the bug report form, with diagnostics and, if asked, debug logs (how to turn
  them on and what to remove before posting).
- **A new or untested model**: the bug report form with the checkbox ticked, and the
  model and firmware; diagnostics; which entities show sensible values; which actions
  worked (for example start, stop and edit); and anything wrong or missing.
- **Security**: private reporting only (`SECURITY.md`), never a public issue.

It also states the policy on AI-assisted contributions: they're welcome; say so in the
pull request; the contributor is responsible for what they submit and must understand
it; and it gets the same review and tests as any other change.

Code adapted from other projects must have a compatible license and be credited in
`NOTICE`, the README's Acknowledgments and a comment at the top of the file.

## 8. Checks and changes

1. **The shared check**, run in each project's CI against the standard version it
   follows, fails when a **must** rule isn't met: required files, matching versions,
   README sections and standard text, manifest and `hacs.json` fields, license and
   `NOTICE`, privacy patterns, `.gitignore`, pinned actions and requirements, Dependabot
   configuration, the changelog's order, `quality_scale.yaml`, and brand images.
   **Should** rules produce warnings.
2. **This standard's version** follows section 4.1, without betas, and stays at `0.x`:
   MINOR for a new or stricter rule or new standard text, PATCH for wording.
3. The standard, its template, its check and its skill change together, with a changelog
   entry. Projects adopt a new version through a reviewed update, then change
   `.standard-version`; until then, their checks keep using the version they follow.

## 9. Sources

- Home Assistant:
  [integration quality scale rules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules),
  [documentation standards](https://developers.home-assistant.io/docs/documenting/standards),
  [style guide](https://developers.home-assistant.io/docs/documenting/general-style-guide),
  [integration page structure](https://developers.home-assistant.io/docs/documenting/integration-docs-examples),
  [manifest](https://developers.home-assistant.io/docs/creating_integration_manifest),
  [brand images](https://developers.home-assistant.io/docs/core/integration/brand_images).
- Marketplace: [publishing guides](https://contributors.home-assistant.io/marketplace/),
  [releases](https://contributors.home-assistant.io/marketplace/guides/releases/),
  [`hacs.json`](https://contributors.home-assistant.io/marketplace/reference/hacs-json/).
- HACS: [publishing requirements](https://hacs.xyz/docs/publish/start),
  [My Home Assistant links](https://hacs.xyz/docs/use/my/).
- Home Assistant [analytics](https://analytics.home-assistant.io/), for the share of
  installations on each version.
- Versions: [Semantic Versioning 2.0.0](https://semver.org/),
  [PEP 440](https://peps.python.org/pep-0440/).
- Sections 1, 3, 4.1 (work in progress), 5.2 to 5.8, 6 and 7 go beyond Home Assistant's,
  the Marketplace's and HACS's rules.
