---
name: publish-rendercv-typst-package
description: Create a PR to publish a new version of RenderCV's Typst package (typst/, @preview/rendercv) to the Typst Universe (typst/packages repository). Validates package integrity, forks/clones the repo, copies files, and opens a PR.
disable-model-invocation: true
---

# Publish RenderCV's Typst package to Typst Universe

Create a pull request to `typst/packages` to publish the current version of RenderCV's Typst package, which lives in `typst/` at the repository root (`@preview/rendercv`).

The clone location for the typst/packages fork is `$HOME/.cache/rendercv/typst-packages`.

## Step 1: Read package metadata

Read `typst/typst.toml` to get the version and all metadata fields.

## Step 2: Validate package integrity

Run ALL checks below. Collect ALL failures and report them together. Do NOT proceed to Step 3 if any check fails.

### 2a: Required files

Verify these exist in `typst/`:
- `lib.typ` (the entrypoint)
- `typst.toml`
- `README.md` (Typst Universe requires it; it documents the package for standalone Typst users)
- `LICENSE`
- `src/`, `entries/`, and `designs/` (imported by `lib.typ`)

If `typst.toml` has a `[template]` section, also verify its `path` folder, its `entrypoint` file, and its `thumbnail` exist.

### 2b: Manifest completeness

Parse `typst.toml` and verify it has:
- Required: `name`, `version`, `entrypoint`, `authors`, `license`, `description`
- `compiler`: the minimum Typst version, matching the `typst` Python dependency's version in `pyproject.toml`
- `exclude`: excludes PDFs and anything not needed at runtime

### 2c: Version consistency

Check that the version string in `typst/typst.toml` matches `version` in `pyproject.toml` (RenderCV and its Typst package share a version), and appears correctly in:
- `typst/README.md` import statements (`@preview/rendercv:X.Y.Z`)
- The template's entrypoint, if there is a template
- Any example files in `typst/examples/*.typ` (if they have import statements)

If ANY file references an old version, stop and report which files need updating. (The docs in `docs/` also show `@preview/rendercv:X.Y.Z` imports; report stale ones as warnings.)

### 2d: Changelog entry

Read `docs/changelog.md` and verify there is an entry for the version being published.

### 2e: The package compiles on its own

The package must not import anything outside `typst/` with relative paths (`../`), and every `@preview/...` package it imports must exist on Typst Universe. Check with:

```bash
grep -rn '#import' typst/lib.typ typst/src typst/entries typst/designs
```

Relative imports may only point inside `typst/`. External imports (like `@preview/fontawesome:X.Y.Z`) must match the versions pinned in `hatch_build.py`'s `external_typst_packages`.

### 2f: No stale or broken links

Check that `typst/README.md` does not reference nonexistent files within the package (e.g., broken relative links).

### 2g: Import style in the template

If there is a template, verify its entrypoint uses the absolute package import (`@preview/rendercv:{version}`) and NOT a relative import like `../lib.typ`. The Typst packages repository requires absolute imports.

## Step 3: Handle previous work

1. Check for existing open PRs for rendercv in `typst/packages`:
   ```
   gh pr list --repo typst/packages --author @me --search "rendercv" --state all
   ```

2. If an existing PR is **open**, ask the user what to do:
   - Update the existing PR?
   - Close it and create a new one?
   - Abort?

3. If the clone directory `$HOME/.cache/rendercv/typst-packages` already exists:
   - If there are old branches for previous versions that have been merged/closed, delete them.
   - Reset to upstream/main before proceeding.

## Step 4: Set up fork and clone

### If clone does NOT exist:

```bash
mkdir -p $HOME/.cache/rendercv
# Fork if not already forked (idempotent)
gh repo fork typst/packages --clone=false
# Clone with sparse checkout
gh repo clone $(gh api user --jq .login)/packages $HOME/.cache/rendercv/typst-packages -- --filter=blob:none --sparse
cd $HOME/.cache/rendercv/typst-packages
git sparse-checkout set packages/preview/rendercv
git remote add upstream https://github.com/typst/packages.git 2>/dev/null || true
git fetch upstream main
```

### If clone ALREADY exists:

```bash
cd $HOME/.cache/rendercv/typst-packages
git fetch upstream main
git checkout main
git reset --hard upstream/main
```

## Step 5: Create the package version directory

1. Read the version from `typst/typst.toml` (e.g., `3.0.0`).
2. Create a new branch: `git checkout -b rendercv-{version}`
3. Create the target directory: `packages/preview/rendercv/{version}/`
4. Copy files from `typst/` into the target:

**Files to copy:**
- `lib.typ`
- `typst.toml`
- `README.md`
- `LICENSE`
- `src/`, `entries/`, and `designs/` (entire directories)
- The template folder and thumbnail, if `typst.toml` has a `[template]` section
- `examples/` (if it has any files, but exclude any `.pdf` files)

**Do NOT copy:**
- `.git/` or `.gitignore`
- Any `.pdf` files
- Anything matched by `exclude` in `typst.toml`

5. Verify no PDF files ended up in the target directory.

## Step 6: Determine previous version

Look at existing directories in `packages/preview/rendercv/` to find the most recent previous version. This is needed for the PR description. If no previous version exists (first submission), note that this is a new package.

## Step 7: Build PR description

Read `docs/changelog.md` and extract the changes for the current version that concern the Typst package (entry types, designs, the renderer, and the Typst API).

**PR title:** `rendercv:{version}`

**PR body for updates:**
```
I am submitting
  - [ ] a new package
  - [x] an update for a package

Description: {Brief description of the package}. {Summary of what changed in this version}.

### Changes from {previous_version}

{Bullet list of changes extracted from docs/changelog.md}
```

**PR body for new packages** (if no previous version exists, include the full checklist):
```
I am submitting
  - [x] a new package
  - [ ] an update for a package

Description: {Description from typst.toml}

I have read and followed the submission guidelines and, in particular, I
- [x] selected a name that isn't the most obvious or canonical name for what the package does
- [x] added a `typst.toml` file with all required keys
- [x] added a `README.md` with documentation for my package
- [x] have chosen a license and added a `LICENSE` file or linked one in my `README.md`
- [x] tested my package locally on my system and it worked
- [x] `exclude`d PDFs or README images, if any, but not the LICENSE
- [x] ensured that my package is licensed such that users can use and distribute the contents of its template directory without restriction, after modifying them through normal use.
```

## Step 8: Commit, push, and create PR

```bash
cd $HOME/.cache/rendercv/typst-packages
git add packages/preview/rendercv/{version}/
git commit -m "rendercv:{version}"
git push -u origin rendercv-{version}
```

Create the PR:
```bash
gh pr create \
  --repo typst/packages \
  --base main \
  --title "rendercv:{version}" \
  --body "..." # Use the body from Step 7
```

## Step 9: Report results

Tell the user:
1. The PR URL (clickable)
2. The clone location (`$HOME/.cache/rendercv/typst-packages`)
3. The branch name (`rendercv-{version}`)
4. Any warnings noticed during validation (even if they didn't block the PR)
