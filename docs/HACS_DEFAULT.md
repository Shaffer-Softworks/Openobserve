# HACS default repository checklist

Target: **Shaffer-Softworks/Openobserve** in [hacs/default](https://github.com/hacs/default) `integration` list.

## Repo requirements

| Item | Status |
|------|--------|
| Single integration under `custom_components/openobserve/` | Done |
| `manifest.json`, `hacs.json`, `info.md` | Done |
| Brand assets in `custom_components/openobserve/brand/` | Done |
| GitHub Actions: hassfest + HACS (no `ignore: brands`) | Done |
| GitHub releases | v0.2.0 tag exists; publish v0.2.2+ when ready |
| Description, topics, issues | Done |

## hacs/default PR

**Open:** https://github.com/hacs/default/pull/7820

- Fork: `sickkick/HACS`, branch `add-openobserve`
- List entry: `"Shaffer-Softworks/Openobserve"` (casefold sort: after `hyperhdr-ha`, before `shaiu/technicolor`)
- PR body: [checklist + 3 links](https://github.com/hacs/default/blob/master/.github/PULL_REQUEST_TEMPLATE.md) (release, HACS action, hassfest)
- CI: was all green (2026-05-20)
- **Next:** mark **Ready for review** when re-validated (do not request review early)

**Validate run:** https://github.com/Shaffer-Softworks/Openobserve/actions/runs/26174295004

## After merge

OpenObserve appears in the default HACS Integrations store after the next scheduled scan.

## Install until then

HACS → Custom repositories → `https://github.com/Shaffer-Softworks/Openobserve`

Update to **0.2.2+** for thread-safety fixes (async bus listeners).
