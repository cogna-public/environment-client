# GitHub Workflows Documentation

## Automated Version Bumping and Publishing

This repository uses a fully automated two-stage workflow for releases:

### 1. `auto-version.yml` - Automatic Version Bumping

**Trigger:** Every push to `main` branch

**What it does:**
- Automatically bumps the **patch version** (e.g., 0.5.11 → 0.5.12)
- Runs `uv version --bump patch` to update `pyproject.toml` and `uv.lock`
- Commits the version change with message `publish: bump to vX.Y.Z`
- Creates a git tag `vX.Y.Z`
- Creates a GitHub release with auto-generated notes from commits

**Skip conditions:**
- Commit message starts with `publish:` (to avoid infinite loops from the bot's own commits)

**Authentication:**
- The workflow now prefers the repository secret `PAT_TOKEN` for all git pushes, tags, and release creation so the downstream publish workflow is triggered.
- If `PAT_TOKEN` is absent, it falls back to `GITHUB_TOKEN`; the release is still created, but GitHub suppresses release-triggered workflows such as `publish.yml`.

**No special requirements:**
- No conventional commit format needed
- No PR labels needed
- Just merge to main and it happens automatically

### 2. `publish.yml` - PyPI Publishing

**Trigger:** GitHub release published (automatically triggered by auto-version workflow)

**What it does:**
- Builds source distribution and wheel using `uv build`
- Publishes to PyPI using Trusted Publishing (OIDC)
- No API tokens required

## Usage

### Automatic Flow (Default)

Simply merge any PR to `main`:

1. Your PR gets merged to `main`
2. `auto-version.yml` automatically bumps patch version (0.5.11 → 0.5.12)
3. Bot commits the version bump and creates a tag
4. Bot creates a GitHub release
5. `publish.yml` is triggered and publishes to PyPI

**That's it! No manual steps required.**

### Manual Flow (For major/minor bumps)

For **minor** or **major** version bumps, use the manual approach:

```bash
just release minor        # bump minor (0.5.x → 0.6.0)
just release major "Msg"  # bump major (0.5.x → 1.0.0)
```

Or disable `auto-version.yml` and always use manual releases.

## Setup Requirements

### Personal Access Token (PAT) - REQUIRED

To allow the auto-version workflow to trigger the publish workflow, you need to create a **Personal Access Token**:

1. Go to GitHub Settings → Developer settings → Personal access tokens → **Fine-grained tokens**
2. Create a new token with:
   - **Repository access**: Only select `cogna-public/environment-client`
   - **Repository permissions**:
     - Contents: Read and write
     - Metadata: Read-only (automatically selected)
3. Copy the token
4. Go to your repository → Settings → Secrets and variables → Actions
5. Create a new secret named `PAT_TOKEN` with your token

**Why?** GitHub's `GITHUB_TOKEN` doesn't trigger other workflows (security feature). We need a PAT to trigger `publish.yml` after creating a release.

**Fallback:** If `PAT_TOKEN` is not set, the workflow still runs but won't trigger PyPI publishing automatically.

## Workflow Permissions

Both workflows require:
- `contents: write` - to push commits, tags, and create releases
- `id-token: write` - for PyPI Trusted Publishing (publish.yml only)

## Troubleshooting

**Version bump loop:**
- The workflow checks for `publish:` prefix to skip bot commits
- If looping occurs, check that the commit message format is correct

**No version bump:**
- Verify workflow ran (check Actions tab)
- Review workflow logs for errors

**PyPI publish doesn't trigger:**
- **Most common:** `PAT_TOKEN` secret is not configured (see Setup Requirements above)
- Verify the GitHub release was actually published (not a draft)
- Check that the publish workflow didn't error out (check Actions tab)

**PyPI publish fails:**
- Ensure Trusted Publishing is configured in PyPI project settings
- Verify the `pypi` environment exists in GitHub repository settings  
- Check that the release was actually published (not just created as draft)

**Manual workaround if PAT_TOKEN not set:**
- The auto-version workflow will still create the tag and release
- Manually trigger the publish workflow: Go to Actions → Publish → Run workflow → select the tag

## Testing Changes

To test workflow changes without affecting version:

1. Create a feature branch
2. Modify workflow files
3. Test using `workflow_dispatch` trigger or in a fork
4. Merge when confident

Or temporarily add `workflow_dispatch:` trigger to test manually.
