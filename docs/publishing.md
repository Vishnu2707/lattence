# Publish the local CLI

Phase 1 publishes the pre-v1 `0.5.2` distribution. The final `1.0.0`
version remains reserved for the completed milestone. The current PyPI name
must be checked again immediately before upload because another account can
claim it.

## Prepare isolated artifacts

Run these commands on `dev` at the reviewed release commit. Keep the staging
directory path for the upload and verification commands in the same shell.

```bash
publish_dir=$(mktemp -d /tmp/lattence-publish.XXXXXX)
uv build --out-dir "$publish_dir"
uv run twine check "$publish_dir"/*
```

The staging directory starts empty, so the upload cannot include an older
version left in `dist/`. Check that it contains exactly
`lattence-0.5.2-py3-none-any.whl` and `lattence-0.5.2.tar.gz`.

## Upload to PyPI

The first upload needs a PyPI account with a verified email address and an
account-scoped API token that can create the `lattence` project. Its value
starts with `pypi-`. Do not paste it into chat, commit it, or put it in shell
history. After the project exists, replace it with a project-scoped token or
configure trusted publishing. The token is unrelated to repository access.

In a Z shell, enter the token at the hidden prompt and upload only the two
staged archives:

```bash
export TWINE_USERNAME=__token__
read -rs "TWINE_PASSWORD?PyPI API token: "
export TWINE_PASSWORD
uv run twine upload --non-interactive --repository-url https://upload.pypi.org/legacy/ "$publish_dir"/*
unset TWINE_PASSWORD TWINE_USERNAME
```

Stop on any upload error. Do not use a local wheel as evidence of public
installation.

## Verify the public package

Use a new pipx home and bin directory, with the public index explicitly set.
The `pipx install lattence` package spec must resolve from PyPI, not from a
repository URL or local archive.

```bash
pipx_root=$(mktemp -d /tmp/lattence-pipx.XXXXXX)
PIPX_HOME="$pipx_root/home" PIPX_BIN_DIR="$pipx_root/bin" PIP_INDEX_URL=https://pypi.org/simple pipx install --python python3.12 lattence
"$pipx_root/bin/lattence" --version
"$pipx_root/bin/lattence" --help
.venv/bin/python tests/acceptance/check_distribution.py "$publish_dir/lattence-0.5.2-py3-none-any.whl" "$publish_dir/lattence-0.5.2.tar.gz" .venv/bin/lattence "$pipx_root/bin/lattence"
```

The last command compares the published installation's version, root help,
and every command help screen with the source build. Record the literal pipx
install output, not just its exit status. Run project acceptance separately
against `examples/vulnerable-agent` before closing the phase gate.
