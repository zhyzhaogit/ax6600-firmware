# Bootstrap Guide

## Goal

Turn the scaffold into your real GitHub-backed AX6600 firmware workspace with minimal manual editing.

## Repositories

Create two GitHub repositories:

- `ax6600-firmware`
- `ax6600-source`

You can rename them, but the default scripts and docs assume these names.

## Local Bootstrap

From `ax6600-firmware`:

```powershell
python scripts/bootstrap_identity.py --github-user <your-github-user>
```

Optional flags:

- `--source-repo-name <name>` if your source repository is not named `ax6600-source`
- `--firmware-repo-name <name>` if your firmware repository is not named `ax6600-firmware`
- `--enable-source-primary` to mark the personal source repository as the preferred enabled source immediately

## After Bootstrap

1. Review `targets/ax6600/upstreams.yml`.
2. Add Git remotes.
3. Push both repositories.
4. Enable GitHub Actions.
5. Run `control-plane-check`.
6. Run `sync-watch`, then `config-diff`, then `canary-build`.

## Suggested Remote Commands

Firmware repository:

```powershell
git remote add origin https://github.com/<your-github-user>/ax6600-firmware.git
git push -u origin main
```

Source repository:

```powershell
git remote add origin https://github.com/<your-github-user>/ax6600-source.git
git push -u origin main
```

## Notes

- `source-primary` is disabled by default until you point it at a real repository.
- The source repository should eventually grow `ax6600-dev` and `ax6600-stable` branches after your first upstream import and validation cycle.
