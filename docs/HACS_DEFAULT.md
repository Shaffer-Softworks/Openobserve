# HACS default repository checklist

Target: include **Shaffer-Softworks/Openobserve** in [hacs/default](https://github.com/hacs/default) `integration` list.

## Repo requirements (this repository)

| Item | Status |
|------|--------|
| Single integration under `custom_components/openobserve/` | Done |
| `manifest.json` (domain, version, docs, issues, codeowners) | Done |
| `hacs.json` with `name` | Done |
| `info.md` or README (`render_readme: true`) | Done |
| Brand assets in `custom_components/openobserve/brand/` | Done |
| GitHub Actions: hassfest + HACS action | `.github/workflows/validate.yaml` |
| GitHub releases | v0.2.0+ |
| Repo description, topics, issues enabled | Set via `gh repo edit` |

## Before opening the hacs/default PR

1. Confirm **Validate** workflow is green on `main`.
2. Submitter must be **repo owner** or major contributor; PR must come from a **personal fork** (not org).
3. Optional but recommended: add domain to [home-assistant/brands](https://github.com/home-assistant/brands) if the default-repo brands check does not yet accept in-integration `brand/` (HA 2026.3+).

## hacs/default PR

**Open:** https://github.com/hacs/default/pull/7820 (from `sickkick/HACS` branch `add-openobserve`)

1. Fork `hacs/default` to a personal account (e.g. `sickkick/HACS`).
2. Branch from `master`.
3. Add `"Shaffer-Softworks/Openobserve"` to `integration` sorted with `key=str.casefold` (after `hyperhdr-ha`, before `shaiu/technicolor`).
4. PR body must include the [checklist and three action/release links](https://github.com/hacs/default/blob/master/.github/PULL_REQUEST_TEMPLATE.md).
5. Mark **ready for review** after CI passes (do not request review early).

## After merge

Default store updates on the next HACS scheduled scan. Users find **OpenObserve** under Integrations without adding a custom repository.
