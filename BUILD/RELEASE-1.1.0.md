# v1.1.0 release commands

These commands are prepared for manual execution after review. They were not
run during release preparation. Run them in order from a clean `dev` checkout.

## 1. Recheck the reviewed commit

```bash
git checkout dev
git pull --ff-only origin dev
./scripts/verify-release.sh
git status --short
git log origin/dev..dev --oneline
```

Both Git commands at the end must print nothing.

## 2. Create and push the annotated tag

```bash
git tag -a v1.1.0 -m "v1.1.0"
git push origin v1.1.0
```

## 3. Open the pull request to main

```bash
release_notes_file=$(mktemp /tmp/lattence-v1.1.0-notes.XXXXXX)
awk '/^## \[1\.1\.0\]/{copy=1; next} /^## \[1\.0\.0\]/{copy=0} copy' CHANGELOG.md > "$release_notes_file"
gh pr create --base main --head dev --title "Release v1.1.0" --body-file "$release_notes_file"
```

After review, merge through the pull request and synchronize `dev`:

```bash
gh pr merge --merge --delete-branch=false "$(gh pr view --json url --jq .url)"
git fetch origin
git checkout dev
git merge --ff-only origin/main
git push origin dev
```

## 4. Build and upload the PyPI distributions

Build from the tag in a detached worktree. The root distribution contains the
CLI, discovery, graph, governance, evidence, MCP, AI, crypto, and rule packs.
The API is a separate distribution required by `lattence[api]`.

```bash
publish_dir=$(mktemp -d /tmp/lattence-v1.1.0-publish.XXXXXX)
release_root=$(mktemp -d /tmp/lattence-v1.1.0-checkout.XXXXXX)
release_checkout="$release_root/repo"
git worktree add --detach "$release_checkout" v1.1.0
(
  cd "$release_checkout"
  uv build --package lattence --out-dir "$publish_dir"
  uv build --package lattence-api --out-dir "$publish_dir"
)
test -f "$publish_dir/lattence-1.1.0-py3-none-any.whl"
test -f "$publish_dir/lattence-1.1.0.tar.gz"
test -f "$publish_dir/lattence_api-1.1.0-py3-none-any.whl"
test -f "$publish_dir/lattence_api-1.1.0.tar.gz"
uv run twine check "$publish_dir"/*
export TWINE_USERNAME=__token__
read -rs "TWINE_PASSWORD?PyPI API token: "
export TWINE_PASSWORD
uv run twine upload --non-interactive --repository-url https://upload.pypi.org/legacy/ "$publish_dir"/*
unset TWINE_PASSWORD TWINE_USERNAME
```

## 5. Create the GitHub release

```bash
gh release create v1.1.0 "$publish_dir"/* --verify-tag --title "v1.1.0" --notes-file "$release_notes_file"
```

Remove the detached worktree after all public verification is complete:

```bash
git worktree remove "$release_checkout"
```
