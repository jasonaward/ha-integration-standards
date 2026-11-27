# Changelog

## 0.2.0 (2026-11-27)

- **Action needed:** projects made with 0.1.0 update to the rules below: move client code
  into a library on PyPI, drop `strings.json` and any polling-interval option, set the
  minimum Home Assistant version to 2026.3.0 or later, adopt the new test tools,
  `requirements_ci.txt`, `hacs.json` keys, changelog format, README text and sections and
  release workflow, list the two new quality-scale rules, and pin the check to this
  version. (0.1.0 was never tagged, so no project runs its check.)
- **Home Assistant's rules first, read as written**: quality-scale claims hold against the
  rule's current text, not by a technicality, and `exempt` only under the rule's own
  exception; a rule a third-party library blocks stays `todo`. The few rules written for
  integrations in Home Assistant itself (`brands`, `strict-typing`, the documentation
  pages, coverage) are mapped to their custom-integration equivalents. Links point to
  Home Assistant's new contributor documentation.
- **Quality scale**: 54 rules, adding `docs-triggers` and `docs-conditions`.
- **Client libraries**: code that talks to a device or service lives in its own public
  `py<name>` repository, released to PyPI by CI with trusted publishing, as Home
  Assistant requires (`dependency-transparency`). This replaces 0.1.0's bundled libraries,
  which contradicted Home Assistant.
- **Manifest**: `loggers` names the requirements' loggers, as Home Assistant defines it.
- **Translations**: a complete `translations/en.json`; no `strings.json`, which Home
  Assistant doesn't use for custom integrations.
- **Polling**: no polling-interval option; _should_: a minimum time between requests to a
  vendor's cloud, whatever users or automations ask, stated in the README.
- **Marketplace**: Home Assistant 2026.11 builds HACS in as the Marketplace. Projects
  follow its publishing guides as well as HACS's; `render_readme` is dropped;
  `hide_default_branch` keeps unreleased code from being offered; _should_: manifest
  `categories`. The README's `### Marketplace or HACS` covers both, including betas and
  going back a version, with the Marketplace's labels taken from Home Assistant's
  frontend; the installation section is marked for the Marketplace to leave out.
- **Domain**: never one of Home Assistant's own integrations, checked by a test.
- **Tests**: Home Assistant's own `pytest-homeassistant` replaces the retired
  `pytest-homeassistant-custom-component` (kept only for minimum versions before 2026.11);
  the latest stable release is really tested, and _should_, the latest beta weekly;
  tests fail when Home Assistant reports a deprecated use by the project's code, through
  its frame helper or a deprecated constant's logger; CI tools and test requirements
  pinned, never alongside a package Home Assistant pins; above 95% line coverage per
  module on the minimum and the latest version, with only marked version code excluded.
- **Minimum Home Assistant version**: 2026.3.0 or later, which shows the `brand/` images;
  chosen for reach and upkeep, no older than about 12 months and not under 3 months old
  unless a needed feature requires it, checking Home Assistant's analytics; code for older
  versions kept small, labeled and tested.
- **Releases**: started from the Actions tab, on the default branch only, one at a time,
  with a version newer than every earlier tag; every test, lint, type check, hassfest
  and HACS validation runs first; the release job runs in a protected `release`
  environment, and CI creates the tag and the release. Every release, betas included,
  follows an independent audit, kept in `docs/audits/<version>.md` with a fixed header
  and a verdict for every rule, and required by the release check, along with no `TODO`.
- **Repository settings**: protected `v*` tags, immutable releases and the `release`
  environment; hassfest and the HACS action, which have no current tags, pinned to dated
  commits and refreshed before each release.
- **Changelog**: bullets only; **Action needed:** is the first bullet, since it's shown as
  the update's release notes.
- **README**: the introduction links the manufacturer's or service's website; the notices
  describe aims rather than claims, and the unofficial notice fits a service used like
  the app, a public interface, or a local device; the load section only for integrations
  that use a service; the minimum version in Prerequisites; triggers, conditions and
  actions in Home Assistant's order; troubleshooting as symptom, cause and fix; the
  statement on how it's made covers the maintainer's code, so contributors' code can be
  merged; deliberate differences from Home Assistant's page structure and style guide
  stated; no "e.g.", "i.e." or "etc.".
- **Commits**: the maintainer's noreply address only, with no co-author lines;
  contributors' and bots' commits keep their own.
- **Published means tagged**: a version, of a project or of this standard, is published
  when its tag exists, and can't change after that.
- **Device pages** show only identifiers known to be right.
- **Third audit**: a one-word trademark passes ("is a trademark"), with or without a
  connection sentence; the deprecation fixture listens from setup to teardown; the
  pull-request version check works in private repositories; hassfest is pinned to its
  release tag; the minimum-version job tests the exact minimum; build provenance uses
  `actions/attest`; the check requires read-only workflow permissions, the Marketplace
  markers, the same standard commit in both workflows, and an audit verdict for every
  rule by whole name and every section; UI wording sourced for both pre-release
  switches and the 48-hour updates of repositories added from a link.
- **Shared check** (`check/check_standard.py`) and a reusable workflow that runs it in
  each project's CI, from the same commit as the workflow, covering the maintainer's
  commits on the branch and, when releasing, the audit report. A pull request can't
  lower `.standard-version`.
- **Copier template** that creates a project meeting the standard, with a minimal working
  integration and tests; `copier update` brings in later template changes. This
  repository's CI checks that every test job of a generated project can install, and
  that a generated project's tests pass and catch a deprecated constant.

## 0.1.0 (2026-11-19)

- **First version** of the standard, in nine sections: why; Home Assistant and HACS
  first; identity and naming; versions, changelog and releases; README; beyond Home
  Assistant's rules (privacy, security, users' setups); repository files; checks and
  changes; sources.
- **Enterprise-quality aim, hobby terms**: stated first in the standard and in every
  README's notices: offered as is, used at your own risk.
- **Unofficial notice** says projects use a vendor's service the way its app does, may
  stop working, and may not be permitted by the vendor's terms; vendor objections are
  answered promptly.
- **Reporting guide** in `CONTRIBUTING.md` for bugs, new or untested models, and
  security.
- **Musts by default**: every rule is a must unless marked _should_.
- **Security**: Dependabot updates and alerts, secret scanning with push protection,
  required checks, security advisories for fixed vulnerabilities, weekly run against
  Home Assistant's beta.
- **Community**: Contributor Covenant 3.0, a pull request template, and a policy on
  AI-assisted contributions.
- **Opt-in and public**: applies only to projects with a `.standard-version` file.
- **Not a warranty**: the standard describes intended practices; public statements about
  quality, security and maintenance describe aims and process, not guarantees.
- **Home Assistant and HACS first**: their rules by reference, not restated. Quality
  scale aim Platinum, floor Gold for releases; coverage above 95% per module.
- **Versions**: Semantic Versioning in PEP 440 form; first release `0.1.0b1`; projects
  stay at `0.x` as work in progress.
- **README**: Home Assistant's integration page structure, standard text for notices,
  how it's made and maintained, install buttons, and license and disclaimer.
- **Broken releases and vendor service changes**: how each is handled.
- **Skill** `ha-integration-standards` summarizing the standard.
