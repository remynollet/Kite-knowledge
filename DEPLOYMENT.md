# Deployment Guide — GitHub Pages

This guide covers the one-time setup and ongoing deployment of Kite-knowledge to GitHub Pages.

---

## Prerequisites

| Requirement | Minimum version |
|-------------|----------------|
| Python | 3.11+ |
| pip | Latest |
| Git | 2.x |
| GitHub account | Free tier |

---

## Part 1 — One-Time Repository Setup

### 1.1 Push the project to GitHub

```bash
cd Kite-knowledge/
git init
git remote add origin https://github.com/YOUR_USERNAME/Kite-knowledge.git
git add .
git commit -m "feat: initial project setup"
git push -u origin main
```

> Replace `YOUR_USERNAME` with your GitHub username. Update `repo_url` and `repo_name` in `mkdocs.yml` accordingly.

### 1.2 Update `mkdocs.yml` with your repository URL

Open `mkdocs.yml` and set:

```yaml
repo_url: https://github.com/YOUR_USERNAME/Kite-knowledge
repo_name: YOUR_USERNAME/Kite-knowledge
```

### 1.3 Configure Branch Protection

In GitHub: **Settings → Branches → Add branch protection rule**

- Branch name pattern: `main`
- ☑ Require a pull request before merging
- ☑ Require status checks to pass before merging
  - Required check: `Content Validation`
- ☑ Require branches to be up to date before merging
- ☑ Do not allow bypassing the above settings

This ensures no content bypasses the CI gate.

### 1.4 Enable GitHub Pages

After the first push to `main` (which triggers the deploy workflow and creates a `gh-pages` branch):

In GitHub: **Settings → Pages**

- Source: **Deploy from a branch**
- Branch: `gh-pages` / `/ (root)`
- Click **Save**

Your site will be live at:  
`https://YOUR_USERNAME.github.io/Kite-knowledge/`

---

## Part 2 — CI/CD Pipeline Overview

### CI Pipeline (`ci.yml`) — triggered on every PR to `main`

| Step | Check | Blocks merge if |
|------|-------|----------------|
| 1 | Frontmatter validation | Any required field missing or wrong type |
| 2 | AI draft gate | Any `ai_status: draft` found in `docs/` |
| 3 | Link check | Any broken internal link in `docs/` |
| 4 | MkDocs strict build | Any MkDocs warning or error |
| 5 (non-blocking) | Lighthouse accessibility audit | Informational only |

### Deploy Pipeline (`deploy.yml`) — triggered on every push to `main`

1. Checks out the repository
2. Installs Python dependencies from `requirements.txt`
3. Runs `mkdocs build`
4. Pushes the built site to the `gh-pages` branch via [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages)
5. GitHub Pages serves the `gh-pages` branch automatically

**End-to-end flow:**

```
PR opened → CI runs (4 gates) → PR approved → Merge to main → Deploy runs → Site updated
```

---

## Part 3 — Local Development

### Install dependencies

```bash
pip install -r requirements.txt
```

### Preview the site locally

```bash
mkdocs serve
```

Site available at: `http://127.0.0.1:8000`

### Validate before pushing

```bash
# Validate all frontmatter in docs/
python scripts/validate_frontmatter.py docs/

# Check for broken internal links
python scripts/check_links.py docs/

# Full strict build (same as CI)
mkdocs build --strict
```

All three commands must exit with code `0` before opening a PR.

---

## Part 4 — Deployment Troubleshooting

### Problem: Deploy workflow fails — `gh-pages` branch permission denied

**Cause:** The GitHub Actions workflow needs write access to the repository.

**Fix:** In GitHub: **Settings → Actions → General → Workflow permissions**  
→ Select **Read and write permissions** → Save.

### Problem: GitHub Pages shows a 404 after first deploy

**Cause:** GitHub Pages may not be activated yet, or the `gh-pages` branch was just created.

**Fix:**
1. Confirm the deploy workflow ran successfully (green checkmark in **Actions** tab)
2. Go to **Settings → Pages** and ensure source is set to `gh-pages` branch
3. Wait 2–3 minutes for GitHub CDN propagation

### Problem: CI Step 1 (frontmatter validation) fails on a file with no entity type

**Cause:** Index pages (`docs/*/index.md`) may have minimal or no frontmatter.  
**Expected behavior:** The validator skips files without a `type:` field — this is correct. If it fails, check that your file doesn't have a `type:` field with an unrecognized value.

### Problem: `mkdocs build --strict` fails with "WARNING"

**Cause:** MkDocs strict mode treats all warnings as errors. Common triggers:
- A page listed in `nav:` in `mkdocs.yml` but the `.md` file doesn't exist
- A `.md` file exists in `docs/` but is not listed in `nav:`

**Fix:** Ensure every file referenced in `mkdocs.yml` nav exists, and every file in `docs/` is listed in nav.

### Problem: Site content is outdated after a merge

**Cause:** The deploy workflow may have failed silently.

**Fix:** Check the **Actions** tab for the `Deploy — GitHub Pages` workflow. If it failed, inspect the logs. Common cause: `requirements.txt` package version conflict.

---

## Part 5 — Adding a New Entity Type (Advanced)

If you need to add a 9th entity type beyond the 8 currently supported:

1. Create `scripts/schemas/NEW_TYPE.yaml` following the pattern of `scripts/schemas/person.yaml`
2. Add `staging/NEW_TYPE/` and `docs/NEW_TYPE/` directories (with `.gitkeep`)
3. Add `docs/NEW_TYPE/index.md` section index
4. Add the new type to the `nav:` section in `mkdocs.yml`
5. Update `scripts/generate_entity.py` to include the new type in the `--type` choices

---

## Quick Reference

```bash
# Local preview
pip install -r requirements.txt
mkdocs serve

# Validate before PR
python scripts/validate_frontmatter.py docs/
python scripts/check_links.py docs/
mkdocs build --strict

# Deploy (automatic on merge to main)
# → triggered by GitHub Actions deploy.yml
```
