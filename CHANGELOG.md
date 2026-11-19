# Changelog

## 0.2.0 (2026-11-19)

**Action needed:** projects on 0.1.0 update their README's install steps, changelog order,
tests, and `.standard-version` as below, and pin the check to this version.

- **Marketplace**: Home Assistant 2026.11 builds HACS in as the Marketplace. Projects
  follow its publishing guides as well as HACS's; the README's `### Marketplace or HACS`
  covers both, including how to get betas with the Marketplace's **Pre-release** switch.
- **Minimum Home Assistant version**: chosen for reach and upkeep, no older than about 12
  months and not under 3 months old, checking Home Assistant's analytics; code for older
  versions is kept small, labeled, and tested.
- **Deprecations**: tests fail when Home Assistant reports a deprecated use by the
  project's own code.
- **Changelog**: **Action needed:** comes first in its version's section, since it's
  shown as the update's release notes.
- **Shared check** (`check/check_standard.py`) and a reusable workflow that runs it in
  each project's CI, from the version in its `.standard-version`.
- **Copier template** that creates a project meeting the standard, with a minimal working
  integration and tests; `copier update` brings in later template changes.

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
